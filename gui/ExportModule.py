#----------------------------------------------------------------------
#------------------------------ Modules -------------------------------
# PyQt
import logging
import logging.config
import sys, os, shutil, time

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtGui import QMainWindow, QWidget

from UserDetails import UserDetails
from domain.ExportMapping import ExportMapping
from gui.ExportFieldMappingDialog import ExportFieldMappingDialog
from gui.ExportModuleUI import ExportModuleUI
from services.AppConfigurationService import AppConfigurationService
from services.CsvFileDataService import CsvFileDataService
from services.HttpConnectionService import HttpConnectionService
from services.MainzellisteConnectInfo import MainzellisteConnectInfo
from services.OdmFileDataService import OdmFileDataService
from services.PseudonymisationService import PseudonymisationService
from utils import first
from viewModels.ExportMappingTableModel import ExportMappingTableModel


# Standard
# Logging
# Utils
# GUI
# View Models
# Domain
# Services
#----------------------------------------------------------------------
class ExportModule(QWidget, ExportModuleUI):
    """Export Module view class

    Export Module is class inerited from ExportModuleUI. There the GUI layout
    and elements are defined. In this class the handlers aka View application
    logic is defined. Handler are invoking functionality which is provided in
    bussiness layer of the application (services, domain).
    """

    #----------------------------------------------------------------------
    #--------------------------- Constructors -----------------------------

    def __init__(self, parent = None):
        """Constructor of ExportModule View
        """
        QWidget.__init__(self, parent)
        self.parent = parent

        #-----------------------------------------------------------------------
        #----------------------- Logger ----------------------------------------
        self.logger = logging.getLogger(__name__)
        logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
        #-----------------------------------------------------------------------
        #---------------------- App config --------------------------------------
        self.appConfig = AppConfigurationService()
        #-----------------------------------------------------------------------
        #--------------------- Create Module UI --------------------------------
        self.setupUi(self)
        #-----------------------------------------------------------------------
        #---------- Load modules buttons - events definitions ------------------
        self.btnReload.clicked.connect(self.btnReloadClicked)

        self.btnMapExportField.clicked.connect(self.btnMapExportFieldClicked)

        self.btnLocateDataFilename.clicked.connect(self.btnLocateDataFilenameClicked)
        self.btnLocateMetaDataFilename.clicked.connect(self.btnLocateMetaDataFilenameClicked)
        self.btnValidateMapping.clicked.connect(self.btnValidateDataTransformationClicked)
        self.btnLoadMapping.clicked.connect(self.btnLoadMappingClicked)

        self.cmbStudyEvent.currentIndexChanged['QString'].connect(self.cmbStudyEventChanged)
        self.cmbEventForm.currentIndexChanged['QString'].connect(self.cmbEventFormChanged)
        #-----------------------------------------------------------------------
        # Domain model
        self.__study = None
        self.__studyEvents = []
        self.__selectedStudyEvent = None
        self.__studyEventCrfs = []
        self.__selectedEventCrf = None

        #-----------------------------------------------------------------------
        #----------------------- Services --------------------------------------
        # There are two http services, one for communicating with my own
        # site server/database
        section = "MySiteServer"
        hostname = self.appConfig.get(section)["host"]
        port = self.appConfig.get(section)["port"]
        self.svcHttp = HttpConnectionService(hostname, port, UserDetails())

        self.reload()

        #-----------------------------------------------------------------------
        # TODO: make it a Stragety desing pattern later
        self.fileDataService = CsvFileDataService()
        self.fileMetaDataService = OdmFileDataService()
        self.exportMapping = []

        # Just for testing to have guick access to files
        self.dataFilename = "/mnt/edv/skripcakt/ulice/branches/radplanbio/data/radiochemotherapy.csv"
        self.metaDataFilename = "/mnt/edv/skripcakt/ulice/branches/radplanbio/data/HNSCCStudyMetadata.xml"

        #-----------------------------------------------------------------------
        # Create REST mainzellieste
        userName = "admin"
        password = "admin"
        baseUrl = "http://g89rtpsrv.med.tu-dresden.de:8080/mainzelliste-1.1-SNAPSHOT/"
        apiKey = "mdatdd"

        connectInfo = MainzellisteConnectInfo(baseUrl, userName, password, apiKey)
        self.svcPseudonymisation = PseudonymisationService(connectInfo)

        # # Retrive all pids
        # allPids = self.svcPseudonymisation.getAllPatients()

        # # Start reading session (I know the PID and I want to gat patient data)
        # sessionId, uri1 = self.svcPseudonymisation.newSession()
        # tokenId, url2 = self.svcPseudonymisation.readPatientToken(sessionId, allPids[0].idString)
        # self.svcPseudonymisation.getPatient(tokenId)

        #tokenId, uri2 = self.svcPseudonymisation.newPatientToken(sessionId)
        #self.svcPseudonymisation.createPatientJson(tokenId)
        #self.svcPseudonymisation.resolveTempIds(tokenId)


    def loadModuleData(self, selectedIndex):
        if selectedIndex == 0:
            pass


    def reload(self):
        requests = []

        # TODO: read from users data
        # It is not Heidelberg I have it here just for testing to simulate on one database
        mySite = "DKTK-HEIDELBERG"
        site = self.svcHttp.getPartnerSiteByName(mySite)
        if site is not None:
            requests = self.svcHttp.getAllPullDataRequestsToSite(site.sitename)

        pullDataRequestModel = QtGui.QStandardItemModel()
        pullDataRequestModel.setHorizontalHeaderLabels(["Request sent from", "Subject", "Created"])

        row = 0
        for itm in requests:
            fromValue = QtGui.QStandardItem(itm.sentFromSite.sitename)
            subjectValue = QtGui.QStandardItem(itm.subject)
            createdValue = QtGui.QStandardItem(str(itm.created))

            pullDataRequestModel.setItem(row, 0, fromValue)
            pullDataRequestModel.setItem(row, 1, subjectValue)
            pullDataRequestModel.setItem(row, 2, createdValue)

            row = row + 1

        self.tvPullDataRequests.setModel(pullDataRequestModel)
        self.tvPullDataRequests.resizeColumnsToContents()

    #----------------------------------------------------------------------
    #------------------- Browse Buttons Handlers -------------------------

    def btnLocateDataFilenameClicked(self):
        """User selects a file to export
        """
        # Get a data file name
        fileName = QtGui.QFileDialog.getOpenFileName(self, "Locate data file", QtCore.QDir.currentPath(), "csv files(*.csv)")

        # Check read access to the file
        ok = os.access(fileName, os.R_OK)

        # If access is OK
        if ok:
            self.dataFilename = str(fileName);
            self.txtDataFilename.setText(self.dataFilename)


    def btnLocateMetaDataFilenameClicked(self):
        """Open a file open dialog where user selects a study metadata XML file

        """
        # Get a metadata file name
        fileName = QtGui.QFileDialog.getOpenFileName(self, "Locate metadata file", QtCore.QDir.currentPath(), "xml files(*.xml)")

        # Check read access to the file
        ok = os.access(fileName, os.R_OK)

        # If access is OK
        if ok:
            # Get file path as string
            self.metaDataFilename = str(fileName)
            # Set the path to GUI
            self.txtMetaDataFilename.setText(self.metaDataFilename)
            # Prepare service for reading XML ODM files
            self.fileMetaDataService.setFilename(self.metaDataFilename)

            # Load the Study domain object
            self.__study = self.fileMetaDataService.loadStudy()
            # And inform the GUI
            self.lblStudy.setText(self.__study.name())

            # Load list of Study Event Definition domain objects
            self.__studyEvents = self.fileMetaDataService.loadStudyEvents()

            # And prepare ViewModel for the GUI
            seModel = QtGui.QStandardItemModel()

            for studyEventDef in self.__studyEvents:
               text = QtGui.QStandardItem(studyEventDef.name())
               seModel.appendRow([text])

            self.cmbStudyEvent.setModel(seModel)

    #----------------------------------------------------------------------
    #------------------- Command Buttons Handlers -------------------------

    def btnReloadClicked(self):
        self.reload()


    def btnLoadMappingClicked(self):
        """Load mapping into table view
        """
        if self.dataFilename == "":
            if self.txtDataFileName.text() == "":
                # error
                pass
            else :
                ok = os.access(self.txtDataFilename.text(), os.R_OK)
                if ok:
                    self.dataFilename = self.txtDataFilename.text()
                else:
                    #error
                    pass

        if self.metaDataFilename == "":
            if self.txtMetaDataFilename.text() == "":
                # error
                pass
            else :
                ok = os.access(self.txtMetaDataFilename.text(), os.R_OK)
                if ok:
                    self.metaDataFilename = self.txtMetaDataFilename.text()
                else:
                    #error
                    pass


        # Accumulate data headers
        self.fileDataService.setFilename(self.dataFilename)
        self.fileDataService.loadHeaders()

        # Accumulate metadata headers
        self.fileMetaDataService.setFilename(self.metaDataFilename)
        self.fileMetaDataService.loadHeaders()

        # Create a exportMaping list for table ViewModel
        self.exportMapping = self.fileMetaDataService.loadExportMapping(self.__selectedEventCrf)

        # Create a tableView model
        self.exportMappingModel = ExportMappingTableModel(self.exportMapping)
        self.tvExportDataMapping.setModel(self.exportMappingModel)

        # Make tableView editable
        self.tvExportDataMapping.setEditTriggers(QtGui.QAbstractItemView.CurrentChanged)

        # Create combo box delegate to display in teableView
        #dataComboBoxDelegate = ComboBoxDelegate(self, self.fileDataService.headers)
        #actionButtonDelegate = PushButtonDelegate(self)

        # Assign delegates to columns
        #self.tvExportDataMapping.setItemDelegateForColumn(2, dataComboBoxDelegate)
        #self.tvExportDataMapping.setItemDelegateForColumn(4, actionButtonDelegate)

        # Make cobobox always displayed
        #for i in range(0, len(self.fileMetaDataService.headers)):
            #self.tvExportDataMapping.openPersistentEditor(self.exportMappingModel.index(i, 2));
            #self.tvExportDataMapping.openPersistentEditor(self.exportMappingModel.index(i, 4));

        # Resize table columns to content
        self.tvExportDataMapping.resizeColumnsToContents()

        self.tvExportDataMapping.selectionModel().currentChanged.connect(self.tblExportDataMappingItemChanged)


    def btnMapExportFieldClicked(self):
        """Map metadata to datafiled from provided CSV data
        """
        # Initialize dialog
        dialog = ExportFieldMappingDialog(self)
        dialog.dataService = self.fileDataService
        dialog.setData(self.selectedDataMapping, self.fileDataService.headers)

        # Show dialog
        dialogResult = dialog.exec_()

        if dialogResult == QtGui.QDialog.Accepted:
            # Take data from dialog
            self.exportMappingModel.dataItems[self.selectedRow].data = dialog.dataMapping.data
            self.exportMappingModel.dataItems[self.selectedRow].setConverter = dialog.dataMapping.converter

            # Resize table columns to content
            self.tvExportDataMapping.resizeColumnsToContents()


    def btnMapExportFieldConstantClicked(self):
        pass


    def btnValidateMappingClicked(self):
        """
        """
        mappingErrors =  []
        for i in range(0, len(self.fileMetaDataService.headers)):
            print self.exportMappingModel.dataItems[i].metadata + " -> " + self.exportMappingModel.dataItems[i].data

        # Error: All mandatory columns are mapped
        # Warning: one column is mapped to several metadata


    def btnValidateDataTransformationClicked(self):
        """
        """
        dataSize = self.fileDataService.size()

        validationErrors =  []
        # Try to convert all data (from 1 ignore the header)
        for i in range (1, dataSize):
            # For every row of input data set
            dataRow = self.fileDataService.getRow(i)
            # Go through specified export mapping
            for j in range(0, len(self.fileMetaDataService.headers)):
                # And locate data in csv which corresponds to mapping
                metadataHeader = self.exportMappingModel.dataItems[j].metadata

                dataHeader = self.exportMappingModel.dataItems[j].data
                dataIndex = self.fileDataService.headers.index(dataHeader)
                dataValue = dataRow[dataIndex]

                print "metadata: " + metadataHeader + " -> " + dataHeader + " = " + dataValue

                # Check if the data conform
                #self.exportMappingModel.dataItems[j].checkDataType(dataValue)
                if (self.exportMappingModel.dataItems[j].validate(dataValue) == False):
                    errorMessage = "Input file row: " + i + ". " +  dataHeader + " = " + dataValue + "does not conform metadata codelist for: " + metadataHeader
                    validationErrors.append(errorMessage)

        # Show errors if appiers

        # Show confirmation of valid in no errors

    #----------------------------------------------------------------------
    #------------------- ComboBox Handlers --------------------------------

    def cmbStudyEventChanged(self, text):
        """
        """
        # I need to find StudyEvent object according to name (text)
        self.__selectedStudyEvent = first.first(event for event in self.__studyEvents if event.name() == text)

        # When selected event found search CRFs for the event
        if self.__selectedStudyEvent is not None:
            # Load list of Study Event Form Definition domain objects
            self.__studyEventCrfs = self.fileMetaDataService.loadEventCrfs(self.__selectedStudyEvent)

            # And prepare ViewModel for the GUI
            sefModel = QtGui.QStandardItemModel()

            for studyEventCrf in self.__studyEventCrfs:
               text = QtGui.QStandardItem(studyEventCrf.name())
               sefModel.appendRow([text])

            self.cmbEventForm.setModel(sefModel)


    def cmbEventFormChanged(self, text):
        """
        """
        self.__selectedEventCrf = first.first(crf for crf in self.__studyEventCrfs if crf.name() == text)

    #----------------------------------------------------------------------
    #------------------- TableView Handlers -------------------------------

    def tblExportDataMappingItemChanged(self, current, previous):
        self.selectedDataMapping = self.exportMappingModel.dataItems[current.row()]
        self.selectedRow = current.row()
