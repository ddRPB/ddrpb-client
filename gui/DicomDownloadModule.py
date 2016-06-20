#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# Standard
import os
import time

# Logging
import logging
import logging.config

# PyQt
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QWidget

# Contexts
from contexts.ConfigDetails import ConfigDetails
from contexts.OCUserDetails import OCUserDetails
from contexts.UserDetails import UserDetails

# Module UI
from gui.DicomDownloadModuleUI import DicomDownloadModuleUI

# GUI Messages
import gui.messages

# Services
from services.DicomService import DicomService
from services.HttpConnectionService import HttpConnectionService
from services.OCConnectInfo import OCConnectInfo
from services.OCWebServices import OCWebServices
from services.OdmFileDataService import OdmFileDataService

# Utils
from utils import first

# Workers
from workers.WorkerThread import WorkerThread

##     ##  #######  ########  ##     ## ##       ########
###   ### ##     ## ##     ## ##     ## ##       ##
#### #### ##     ## ##     ## ##     ## ##       ##
## ### ## ##     ## ##     ## ##     ## ##       ######
##     ## ##     ## ##     ## ##     ## ##       ##
##     ## ##     ## ##     ## ##     ## ##       ##
##     ##  #######  ########   #######  ######## ########

class DicomDownloadModule(QWidget, DicomDownloadModuleUI):
    """Bulk download of DICOM data withing specific clinical trial
    """

    def __init__(self, parent = None):
        """Constructor of DicomUploadModule
        """
        # Setup GUI
        QWidget.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)

        # Setup logger - use config file
        self.logger = logging.getLogger(__name__)
        logging.config.fileConfig('logging.ini', disable_existing_loggers=False)

        # List of worker threads
        self._threadPool = []

        # Initialise main data members
        self._mySite = None;
        # Prepares services and main data for this ViewModel
        self.prepareServices()

        # Initialize data structures for UI
        self._downloadDir = None
        self._studies = []
        self._studySubjects = []

        # Initial data load
        self.reloadData()

        # Finish UI setup
        self.lblOcConnection.setText("[" + OCUserDetails().username + "] " + self._mySite.edc.soapbaseurl)

        # Register handlers
        self.btnDownload.clicked.connect(self.btnDownloadClicked)
        self.cmbStudy.currentIndexChanged['QString'].connect(self.cmbStudyChanged)
        self.destroyed.connect(self.handleDestroyed)

    def __del__(self):
        """Default Destructor
        """
        self.handleDestroyed()

##     ##    ###    ##    ## ########  ##       ######## ########   ######
##     ##   ## ##   ###   ## ##     ## ##       ##       ##     ## ##    ##
##     ##  ##   ##  ####  ## ##     ## ##       ##       ##     ## ##
######### ##     ## ## ## ## ##     ## ##       ######   ########   ######
##     ## ######### ##  #### ##     ## ##       ##       ##   ##         ##
##     ## ##     ## ##   ### ##     ## ##       ##       ##    ##  ##    ##
##     ## ##     ## ##    ## ########  ######## ######## ##     ##  ######

    def cmbStudyChanged(self, text):
        """Executed when the concrete study is selected from studies combobox
        """
        # Reset table views
        self.tvStudies.setModel(None)
        self.textBrowserProgress.clear()

        # Set selected study and reload sites
        self._selectedStudy = first.first(study for study in self._studies if study.name().encode("utf-8") == text.toUtf8())

        # Disable download button
        self._selectedStudySite = None
        self.btnDownload.setDisabled(True)

        # Reload study sites
        self.reloadStudySites()

    def tblStudyItemChanged(self, current, previous):
        """Event handler which is triggered when selectedStudy change

        When the study is selected I have to clean all the other data elements
        Which depends on study. It means: StudySubjects, StudyEventDefinitions, StudyEventCRFs
        """
        self.textBrowserProgress.clear()

        # Take the first column of selected row from table view
        index = self.studyProxyModel.index(current.row(), 0); 

        # Multicentric
        if len(self._selectedStudy.sites) > 0:
            self._selectedStudySite = first.first(studySite for studySite in self._selectedStudy.sites if studySite.identifier.encode("utf-8") == index.data().toPyObject().toUtf8())
            # Enabled download button
            if (self._selectedStudySite is not None):
                self.btnDownload.setDisabled(False)
        else:
            if (self._selectedStudy is not None):
                self.btnDownload.setDisabled(False)

        # Get the study metadata
        self.reloadStudyMetadata()

         # Show the selected upload target
        msg = "Selected study for download: "
        msg += self._selectedStudy.name() + "/"
        if len(self._selectedStudy.sites) > 0:
            msg += self._selectedStudySite.name + "/"

        self.textBrowserProgress.append(msg)

    def tblStudySubjectItemChanged(self, current, previous):
        """Event handler which is triggered when selectedStudySubject change
        """
        self.tvStudyEvents.setModel(None)
        self.tvDicomStudies.setModel(None)
        self.textBrowserProgress.clear()

        # Take the first column of selected row from table view
        index = self.studySubjectProxyModel.index(current.row(), 1);
        if index.data().toPyObject(): 
            self._selectedStudySubject = (
                first.first(
                    subject for subject in self._studySubjects if subject.label().encode("utf-8") == index.data().toPyObject().toUtf8()
                    )
                )

            # TODO: enable this when you migrate to a new version of OC
            # I need to load a SubjectKey
            # ssREST = self._svcHttp.getStudyCasebookSubject(
            #         self._mySite.edc.edcbaseurl, 
            #         self.getStudyOid(), 
            #         self._selectedStudySubject.label()
            #     )
            # if ssREST != None:
            #     self._selectedStudySubject.oid = ssREST.oid
            #     self.logger.debug("Loaded subject key: " + self._selectedStudySubject.oid)

            # TODO: I dont like it, get rid of it ()
            # Propagate PatientID into service
            self._svcDicom.PatientID = self._selectedStudySubject.subject.uniqueIdentifier

    def btnDownloadClicked(self):
        """Upload button pressed (DICOM upload workflow started)
        """
        QtGui.qApp.processEvents(QtCore.QEventLoop.AllEvents, 1000)

        #self.progressBar.setRange(0, 100)
        #self.progressBar.setValue(0)

        self._downloadDir = self.selectFolderDialog()
        
        if self._downloadDir is not None:

            # Disable upload button for now but better is to disable whole UI
            self.btnDownload.setEnabled(False)


            # Start download DICOM data
            # Create thread
            self._threadPool.append(WorkerThread(self._svcDicom.downloadDicomData, [self._downloadDir, self.getStudyIdentifier(), self._svcHttp]))
            # Connect finish event
            self._threadPool[len(self._threadPool) - 1].finished.connect(self.DicomDownloadFinishedMessage)
            # Connect message eventscd
            self.connect(
                self._threadPool[len(self._threadPool) - 1],
                QtCore.SIGNAL("message(QString)"),
                self.Message
            )
            self.connect(
                self._threadPool[len(self._threadPool) - 1],
                QtCore.SIGNAL("log(QString)"),
                self.LogMessage
            )
            # Progress
            self.connect(
                    self._threadPool[len(self._threadPool) - 1],
                    QtCore.SIGNAL("taskUpdated"),
                    self.handleTaskUpdated
            )
            # Start thread
            self._threadPool[len(self._threadPool) - 1].start()

    def handleTaskUpdated(self, data):
        """Move progress bar precento by precento
        """
        if type(data) is list:
            if data[0]:
                processed = data[0]
            if data[1]:
                size = data[1]

            progress = processed * 100 / size
            self.window().statusBar.showMessage("Processed files: [" + str(processed) + "/" + str(size) + "]")
            self.progressBar.setValue(progress)

    def handleDestroyed(self):
        """Kill running threads
        """
        self.logger.debug("Destroying DICOM download module")
        for thread in self._threadPool:
            thread.terminate()
            thread.wait()
            self.logger.debug("Thread killed.")

    def getStudyOid(self):
        """Return study or site OID depending on mono/multi centre configuration
        """
        # Multicentre
        if len(self._selectedStudy.sites) > 0:
            return self._selectedStudySite.oid
        # Monocentre
        else:
            return self._selectedStudy.oid()

    def getStudyIdentifier(self):
        """Return study or site OID depending on mono/multi centre configuration
        """
        # Multicentre
        if len(self._selectedStudy.sites) > 0:
            return self._selectedStudySite.identifier
        # Monocentre
        else:
            return self._selectedStudy.identifier()

 ######   #######  ##     ## ##     ##    ###    ##    ## ########   ######
##    ## ##     ## ###   ### ###   ###   ## ##   ###   ## ##     ## ##    ##
##       ##     ## #### #### #### ####  ##   ##  ####  ## ##     ## ##
##       ##     ## ## ### ## ## ### ## ##     ## ## ## ## ##     ##  ######
##       ##     ## ##     ## ##     ## ######### ##  #### ##     ##       ##
##    ## ##     ## ##     ## ##     ## ##     ## ##   ### ##     ## ##    ##
 ######   #######  ##     ## ##     ## ##     ## ##    ## ########   ######

    def prepareServices(self):
        """Prepare services for this module
        """
        # HTTP connection to RadPlanBio server (Database)
        self._svcHttp = HttpConnectionService(ConfigDetails().rpbHost, ConfigDetails().rpbHostPort, UserDetails())
        self._svcHttp.application = ConfigDetails().rpbApplication

        if ConfigDetails().proxyEnabled:
            self._svcHttp.setupProxy(ConfigDetails().proxyHost, ConfigDetails().proxyPort, ConfigDetails().noProxy)
        if ConfigDetails().proxyAuthEnabled:
            self._svcHttp.setupProxyAuth(ConfigDetails().proxyAuthLogin, ConfigDetails().proxyAuthPassword)

        # Read partner site of logged user
        self._mySite = self._svcHttp.getMyDefaultAccount().partnersite

        # Create connection artefact to users main OpenClinica SOAP
        baseUrl = self._mySite.edc.soapbaseurl
        self.ocConnectInfo = OCConnectInfo(baseUrl, OCUserDetails().username)
        self.ocConnectInfo.setPasswordHash(OCUserDetails().passwordHash)

        if ConfigDetails().proxyEnabled:
            self.ocWebServices = OCWebServices(self.ocConnectInfo, ConfigDetails().proxyHost, ConfigDetails().proxyPort, ConfigDetails().noProxy, ConfigDetails().proxyAuthLogin, ConfigDetails().proxyAuthPassword)
        else:
            self.ocWebServices = OCWebServices(self.ocConnectInfo)

        # ODM XML metadata processing
        self.fileMetaDataService = OdmFileDataService()
        # DICOM PROCESSING SERVICE
        self._svcDicom = DicomService()

    def reloadData(self):
        """Initialization of data for UI
        """
        # OpenClinica study
        del self._studies[:]
        self._studies = []
        self._selectedStudy = None
        self._studyMetadata = None

        # OpenClinica study site
        self._selectedStudySite = None

        # OpenClinica study subjects
        del self._studySubjects[:]
        self._studySubjects = []
        self._selectedStudySubject = None

        # Load studies
        self.reloadStudies()

    def reloadStudies(self):
        """Reload OpenClinica studies (in working thread)
        """
        # Setup loading UI
        self.window().statusBar.showMessage("Loading list of clinical studies...")
        self.window().enableIndefiniteProgess()
        self.tabWidget.setEnabled(False)

        # Create data loading thread
        self._threadPool.append(WorkerThread(self.ocWebServices.listAllStudies))

        # Connect slots
        self.connect(
            self._threadPool[len(self._threadPool) - 1],
            QtCore.SIGNAL("finished(QVariant)"),
            self.loadStudiesFinished
        )

        # Start thread
        self._threadPool[len(self._threadPool) - 1].start()

    def reloadStudyMetadata(self):
        """Reload study metadata for selected study
        """
        # Setup loading UI
        self.window().statusBar.showMessage("Loading study metadata...")
        self.window().enableIndefiniteProgess()
        self.tabWidget.setEnabled(False)

        # Create data loading thread
        self._threadPool.append(WorkerThread(self.ocWebServices.getStudyMetadata, self._selectedStudy))

        # Connect slots
        self.connect(
            self._threadPool[len(self._threadPool) - 1],
            QtCore.SIGNAL("finished(QVariant)"),
            self.loadStudyMetadataFinished
        )

        # Start thread
        self._threadPool[len(self._threadPool) - 1].start()

    def reloadStudySites(self):
        """Reload sites for selected OpenClinica sutdy (in memory processing)
        (If it is monocentric study show one default site)
        """
        # Quick way of crating simple viewModel
        self.studySitesModel = QtGui.QStandardItemModel()
        self.studySitesModel.setHorizontalHeaderLabels(["Identifier", "Partner Site", "Study"])

        row = 0
        if len(self._selectedStudy.sites) > 0:
            for site in self._selectedStudy.sites:
                siteIdentifierValue = QtGui.QStandardItem(site.identifier)
                siteNameValue = QtGui.QStandardItem(site.name)
                studyNameValue = QtGui.QStandardItem(self._selectedStudy.name())

                self.studySitesModel.setItem(row, 0, siteIdentifierValue)
                self.studySitesModel.setItem(row, 1, siteNameValue)
                self.studySitesModel.setItem(row, 2, studyNameValue)

                row = row + 1
        else:
            studyIdentifierValue = QtGui.QStandardItem(self._selectedStudy.identifier())
            studyNameValue = QtGui.QStandardItem(self._selectedStudy.name())

            self.studySitesModel.setItem(row, 0, studyIdentifierValue)
            self.studySitesModel.setItem(row, 2, studyNameValue)

            row = row + 1

        # Create a proxy model to enable Sorting and filtering
        self.studyProxyModel = QtGui.QSortFilterProxyModel()
        self.studyProxyModel.setSourceModel(self.studySitesModel)
        self.studyProxyModel.setDynamicSortFilter(True)
        self.studyProxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        # Connect to filtering UI element
        QtCore.QObject.connect(self.txtStudyFilter, QtCore.SIGNAL("textChanged(QString)"), self.studyProxyModel.setFilterRegExp)

        self.tvStudies.setModel(self.studyProxyModel)
        self.tvStudies.resizeColumnsToContents()

        # After the view has model, set currentChanged behaviour
        self.tvStudies.selectionModel().currentChanged.connect(self.tblStudyItemChanged)

    def reloadSubjects(self):
        """Reload OpenClinica study subects enrolled into selected study/site in working thread
        """
        # Setup loading UI
        self.window().statusBar.showMessage("Loading list of study subjects...")
        self.window().enableIndefiniteProgess()
        self.tabWidget.setEnabled(False)
        self._subjectsLoaded = False

        # Load subject for whole study or only site if it is multicentre study
        if self._selectedStudy and self._selectedStudy.isMulticentre:
            self._threadPool.append(WorkerThread(self.ocWebServices.listAllStudySubjectsByStudySite, [self._selectedStudy, self._selectedStudySite, self._studyMetadata]))
        else:
            self._threadPool.append(WorkerThread(self.ocWebServices.listAllStudySubjectsByStudy, [self._selectedStudy, self._studyMetadata]))

        # Connect slots
        self.connect(
            self._threadPool[len(self._threadPool) - 1],
            QtCore.SIGNAL("finished(QVariant)"),
            self.loadSubjectsFinished
        )

        # Start thread
        self._threadPool[len(self._threadPool) - 1].start()

        # TODO: it would be much faster if I request REST subject only for the selected one
        # TODO: however we have to migrate to a new version of OC first
        # Need to get OIDs of subjects
        self._threadPool.append(
                WorkerThread(
                    self._svcHttp.getStudyCasebookSubjects, [self._mySite.edc.edcbaseurl, self.getStudyOid()]
                )
            )

        # Connect slots
        self.connect(
            self._threadPool[len(self._threadPool) - 1],
            QtCore.SIGNAL("finished(QVariant)"),
            self.loadSubjectsRESTFinished
        )

        # Start thread
        self._threadPool[len(self._threadPool) - 1].start()

    def selectFolderDialog(self):
        """User selects a directory for DICOM study files
        """
        try:
            dirPath = QtGui.QFileDialog.getExistingDirectory(None, "Please select the DICOM download destination folder")
            if dirPath == "":
                return None

            isReadable = os.access(str(dirPath),  os.R_OK)
            QtGui.qApp.processEvents(QtCore.QEventLoop.AllEvents, 1000)
            
            if isReadable == False:
                self.Error("The client is not allowed to read data from the selected folder!")
                self.logger.error("No read access to selected folder.")
                return None
        except UnicodeEncodeError:
            self.Error("The path to the selected folder contains unsupported characters (unicode), please use only ascii characters in names of folders!")
            self.logger.error("Unsupported unicode folder path selected.")
            return None    

        return str(dirPath)

    def loadStudiesFinished(self, studies):
        """Finished loading studies from server
        """
        self._studies = studies.toPyObject()
        self._studies .sort(cmp = lambda x, y: cmp(x.name(), y.name()))

        # And prepare ViewModel for the GUI
        studiesModel = QtGui.QStandardItemModel()
        for study in self._studies:
           text = QtGui.QStandardItem(study.name())
           studiesModel.appendRow([text])
        self.cmbStudy.setModel(studiesModel)

        # Select the first study
        self._selectedStudy = self._studies[0]

        # Update status bar
        self.tabWidget.setEnabled(True)
        self.window().statusBar.showMessage("Ready")
        self.window().disableIndefiniteProgess()

    def loadStudyMetadataFinished(self, metadata):
        """Finished loading metadata from server
        """
        self._studyMetadata = metadata.toPyObject()

        # Update status bar
        self.tabWidget.setEnabled(False)
        self.window().statusBar.showMessage("Ready")
        self.window().disableIndefiniteProgess()

        # Set the OC active study according to the selection (in order to make sure that RESTfull calls are executed)
        if self._selectedStudy and self._selectedStudy.isMulticentre:
            ocStudy = self._svcHttp.getOCStudyByIdentifier(self._selectedStudySite.identifier)
        else:
            ocStudy = self._svcHttp.getOCStudyByIdentifier(self._selectedStudy.identifier())
        
        updateResult = self._svcHttp.changeUserActiveStudy(UserDetails().username, ocStudy.id) 

        self.tabWidget.setEnabled(True)
        self.window().statusBar.showMessage("Ready")
        self.window().disableIndefiniteProgess()

    def loadSubjectsFinished(self, subjects):
        """Finished loading of subject data
        """
        self._studySubjects = subjects.toPyObject()
        self._subjectsLoaded = True

    def loadSubjectsRESTFinished(self, subjects):
        """
        """ 
        # In case the REST worker finished sooner than the SOAP worker
        while self._subjectsLoaded != True:
            time.sleep(1)

        subjectsREST = subjects.toPyObject()

        # Create the ViewModels for Views
        # Quick way of crating simple viewModel
        self.subjectsModel = QtGui.QStandardItemModel()
        self.subjectsModel.setHorizontalHeaderLabels(["PersonID", "StudySubjectID", "SecondaryID", "Gender", "Enrollment date", "OID"])

        row = 0
        for studySubject in self._studySubjects:
            # Always mandatory
            labelItem = QtGui.QStandardItem(studySubject.label())
            enrollmentDateItem = QtGui.QStandardItem(studySubject.enrollmentDate)

            # Optional
            secondaryLabelItem = QtGui.QStandardItem("")
            if studySubject.secondaryLabel() != None:
                secondaryLabelItem = QtGui.QStandardItem(studySubject.secondaryLabel())

            # Not everything has to be collected (depend on study setup)
            pidItem = QtGui.QStandardItem("")
            genderItem = QtGui.QStandardItem("")
            if studySubject.subject != None:
                if studySubject.subject.uniqueIdentifier != None:
                    pidItem = QtGui.QStandardItem(studySubject.subject.uniqueIdentifier)
                if studySubject.subject.gender != None:
                    genderItem = QtGui.QStandardItem(studySubject.subject.gender)

            oidItem = QtGui.QStandardItem("")
            for sREST in subjectsREST:
                if sREST.studySubjectId == studySubject.label():
                    oidItem = QtGui.QStandardItem(sREST.oid)
                    studySubject.oid = sREST.oid

            self.subjectsModel.setItem(row, 0, pidItem)
            self.subjectsModel.setItem(row, 1, labelItem)
            self.subjectsModel.setItem(row, 2, secondaryLabelItem)
            self.subjectsModel.setItem(row, 3, genderItem)
            self.subjectsModel.setItem(row, 4, enrollmentDateItem)
            self.subjectsModel.setItem(row, 5, oidItem)

            row = row + 1

        # Create a proxy model to enable Sorting and filtering
        self.studySubjectProxyModel = QtGui.QSortFilterProxyModel()
        self.studySubjectProxyModel.setSourceModel(self.subjectsModel)
        self.studySubjectProxyModel.setDynamicSortFilter(True)
        self.studySubjectProxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        # Connect to filtering UI element
        QtCore.QObject.connect(self.txtStudySubjectFilter, QtCore.SIGNAL("textChanged(QString)"), self.studySubjectProxyModel.setFilterRegExp)

        # Set the models Views
        self.tvStudySubjects.setModel(self.studySubjectProxyModel)

        # Resize the width of columns to fit the content
        self.tvStudySubjects.resizeColumnsToContents()

        # After the view has model, set currentChanged behaviour
        self.tvStudySubjects.selectionModel().currentChanged.connect(self.tblStudySubjectItemChanged)

        self.tabWidget.setEnabled(True)
        self.window().statusBar.showMessage("Ready")
        self.window().disableIndefiniteProgess()

##     ## ########  ######   ######     ###     ######   ########  ######
###   ### ##       ##    ## ##    ##   ## ##   ##    ##  ##       ##    ##
#### #### ##       ##       ##        ##   ##  ##        ##       ##
## ### ## ######    ######   ######  ##     ## ##   #### ######    ######
##     ## ##             ##       ## ######### ##    ##  ##             ##
##     ## ##       ##    ## ##    ## ##     ## ##    ##  ##       ##    ##
##     ## ########  ######   ######  ##     ##  ######   ########  ######

    def Question(self, string):
        """Question message box
        """
        reply = QtGui.QMessageBox.question(self, "Question", string, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            self.btnDownload.setEnabled(False)
        else:
            self.btnDownload.setEnabled(True)

    def Error(self, string):
        """Error message box
        """
        QtGui.QMessageBox.critical(self, "Error", string)
        self.btnDownload.setEnabled(True)

    def Warning(self, string):
        """Warning message box
        """
        QtGui.QMessageBox.warning(self, "Warning", string)
        self.btnDownload.setEnabled(True)

    def Message(self, string):
        """Called from message event, opens a small window with the message
        """
        QtGui.QMessageBox.about(self, "Info", string)
        self.btnDownload.setEnabled(True)

    def LogMessage(self, string):
        """Called from log event in thread and adds log into textbrowser UI
        """
        self.textBrowserProgress.append(string)

    def DicomDownloadFinishedMessage(self):
        """ Called after uploadDataThread finished, after the data were uploaded to
        the RadPlanBio server
        """
        # Enable upload button
        self.btnDownload.setEnabled(True)
        self.window().statusBar.showMessage("Ready")
