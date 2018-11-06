#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# Standard
import os, sys

# Logging
import logging
import logging.config

# PyQt
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QWidget

# DICOM
if sys.version < "3":
    import dicom
else:
    from pydicom import dicomio as dicom

# Contexts
from contexts.ConfigDetails import ConfigDetails

# Module UI
from gui.DicomLookupModuleUI import DicomLookupModuleUI

# Dialogs
from gui.PatIdCsvColumnDialog import PatIdCsvColumnDialog

# ViewModels
from viewModels.DicomDataItemModel import DicomDataItemModel

# Services
if sys.version < "3":
    from services.ApplicationEntityService import ApplicationEntityService

from services.CsvFileDataService import CsvFileDataService

# DCM
from dcm.DicomPatient import DicomPatient
from dcm.DicomStudy import DicomStudy
from dcm.DicomSeries import DicomSeries
from domain.Node import Node

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


class DicomLookupModule(QWidget, DicomLookupModuleUI):
    """Bulk download of DICOM data withing specific clinical trial
    """

    def __init__(self, parent=None):
        """Constructor of DicomUploadModule
        """
        # Setup GUI
        QWidget.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)

        # Setup logger - use config file
        self._logger = logging.getLogger(__name__)
        logging.config.fileConfig('logging.ini', disable_existing_loggers=False)

        # List of worker threads
        self._threadPool = []

        # Prepares services and main data for this ViewModel
        self.prepareServices()

        # Initialize data structures for UI
        self._dicomNodes = []
        self._patientIds = []
        self._patients = []
        self._studies = []
        self._series = []
        self._retrieveRootNode = Node("RetrieveRootNode")

        self._selectedNode = None
        self._selectedPatient = None
        self._selectedStudy = None
        self._selectedSeries = None

        # Initial data load
        self.reloadData()

        # Register handlers
        self.cmbDicomNode.currentIndexChanged["QString"].connect(self.cmbDicomNodeChanged)

        self.btnLoadPatIds.clicked.connect(self.btnLoadPatIdsClicked)
        self.btnCancelSearchCriteria.clicked.connect(self.btnCancelSearchCriteriaClicked)
        self.btnSearch.clicked.connect(self.btnSearchClicked)

        self.btnPlusPatient.clicked.connect(self.btnAddPatientClicked)
        self.btnPlusAllPatients.clicked.connect(self.btnAddAllPatientsClicked)
        self.btnMinusPatient.clicked.connect(self.btnRemovePatientClicked)
        self.btnMinusAllPatients.clicked.connect(self.btnRemoveAllPatientsClicked)

        self.btnDownload.clicked.connect(self.btnDownloadClicked)
        
        self.destroyed.connect(self.handleDestroyed)

    def __del__(self):
        """Default destructor
        """
        self.handleDestroyed()

##     ##    ###    ##    ## ########  ##       ######## ########   ######
##     ##   ## ##   ###   ## ##     ## ##       ##       ##     ## ##    ##
##     ##  ##   ##  ####  ## ##     ## ##       ##       ##     ## ##
######### ##     ## ## ## ## ##     ## ##       ######   ########   ######
##     ## ######### ##  #### ##     ## ##       ##       ##   ##         ##
##     ## ##     ## ##   ### ##     ## ##       ##       ##    ##  ##    ##
##     ## ##     ## ##    ## ########  ######## ######## ##     ##  ######

    def cmbDicomNodeChanged(self, text):
        """DICOM node selection changed
        """
        # Reset
        self.textBrowserProgress.clear()

        # Set selected study and reload sites
        self._selectedNode = first.first(node for node in self._dicomNodes if node["AET"].encode("utf-8") == text.toUtf8())

        # Disable download button
        self.btnDownload.setDisabled(True)

    def tblPatientChanged(self, current, previous):
        """DICOM patient selection changed
        """
        # Take the first column of selected row from table view
        index = self._patientsProxyModel.index(current.row(), 0)

        if index.data().toPyObject():    
            self._selectedPatient = first.first(
                patient for patient in self._patients if patient.id.encode("utf-8") == index.data().toPyObject().toUtf8()
            )

            self._logger.debug("Selected DICOM patient: " + self._selectedPatient.id)

            self.reloadDicomStudies()       

    def tblPatientDoubleClicked(self, index):
        """DICOM patient double clicked
        """
        # Take the first column of selected row from table view
        index = self._patientsProxyModel.index(index.row(), 0)

        if index.data().toPyObject():
            pat = first.first(
                patient for patient in self._patients if patient.id.encode("utf-8") == index.data().toPyObject().toUtf8()
            )

            if pat.isChecked == True:
                pat.isChecked = False
            else:
                pat.isChecked = True

            if pat.isChecked == True:
                if self._retrieveRootNode.containsChild(pat) == False:
                    self._retrieveRootNode.addChild(pat)
            else:
                if self._retrieveRootNode.containsChild(pat) == True:
                    self._retrieveRootNode.removeChild(pat)

            if (len(self._retrieveRootNode.children) > 0):
                self.btnDownload.setDisabled(False)
            else:
                self.btnDownload.setDisabled(True)

            self.reloadDicomPatientsModel()
            self.reloadSelectedTreeModel()

    def tblStudyChanged(self, current, previous):
        """DICOM study selection changed
        """
        # Take the fourth column of selected row from table view
        index = self._studyProxyModel.index(current.row(), 3)

        if index.data().toPyObject():  
            self._selectedStudy = first.first(
                study for study in self._studies if study.suid.encode("utf-8") == index.data().toPyObject().toUtf8()
            )

            self._logger.debug("Selected DICOM study: " + self._selectedStudy.suid)

            self.reloadDicomSeries()

    def tblSeriesChanged(self, current, previous):
        """DICOM series selection changed
        """
        # Take the fith column of selected row from table view
        index = self._seriesProxyModel.index(current.row(), 4)

        if index.data().toPyObject(): 
            self._selectedSeries = first.first(
                series for series in self._series if series.suid.encode("utf-8") == index.data().toPyObject().toUtf8()
            )

            self._logger.debug("Selected DICOM series: " + self._selectedSeries.suid)

    def btnLoadPatIdsClicked(self):
        """
        """
        # Show select file dialog
        filePath = self.selectCsvFileDialog()
        if filePath:
            self._logger.info("Scaning file for PatientIDs: " + filePath)

            self.txtPatientIdFilter.setText("")
            self.txtPatientNameFilter.setText("")

            # Sep character
            sepChar = ","

            # Load csv file and detect header
            self._svcCSV.setFilename(filePath)
            self._svcCSV.delimiter = sepChar
            self._svcCSV.loadHeaders()

            self.dialog = PatIdCsvColumnDialog(self)
            self.dialog.setModel(self._svcCSV.headers)

            patIdColumn = None
            if self.dialog.exec_():
                patIdColumn = self.dialog._selectedPatIdColumn

            del self._patientIds[:]
            self._patientIds = []

            if patIdColumn:
                for i in range(1, self._svcCSV.size()):
                    index = self._svcCSV.getRow(0).index(patIdColumn)
                    patId = self._svcCSV.getRow(i)[index]
                    self._patientIds.append(patId)
            
                # Disable Patient ID filter textBox
                self.txtPatientIdFilter.setText(str(self._patientIds))
                self.txtPatientIdFilter.setDisabled(True)

    def btnCancelSearchCriteriaClicked(self):
        """
        """
        self.txtPatientIdFilter.setText("")
        self.txtPatientNameFilter.setText("")
        self.txtPatientIdFilter.setDisabled(False)
        self.txtPatientNameFilter.setDisabled(False)

        del self._patientIds[:]
        self._patientIds = []

    def btnSearchClicked(self):
        """Search DICOM patients clicked
        """
        # Clean up patinest
        del self._patients[:]
        self._patients = []

        # Clean up patient studies
        del self._studies[:]
        self._studies = []

        # Clea up series
        del self._series[:]
        self._series = []

        # Setup loading UI
        self.window().statusBar.showMessage("Loading DICOM patients...")
        self.window().enableIndefiniteProgess()
        self.tabWidget.setEnabled(False)

        # Prepare search
        selectedQueryLvl = "PATIENT"
        self._association = self._svcAE.requestAssociation(self._selectedNode)
        self._svcAE.echo(self._association)

        if self.txtPatientIdFilter.isEnabled():
            patIdFilter = str(self.txtPatientIdFilter.text())
        else:
            patIdFilter = "*"

        patNameFilter = str(self.txtPatientNameFilter.text().toUtf8())

        # Create data loading thread
        self._threadPool.append(WorkerThread(self._svcAE.find, [self._association, selectedQueryLvl, patNameFilter, patIdFilter]))

        # Connect slots
        self.connect(
            self._threadPool[len(self._threadPool) - 1],
            QtCore.SIGNAL("finished(QVariant)"),
            self.dicomFindPatientsFinised
        )

        # Start thread
        self._threadPool[len(self._threadPool) - 1].start()

    def btnAddPatientClicked(self):
        """Add patient to receieve cart button clicked
        """
        self._selectedPatient.isChecked = True
        if self._retrieveRootNode.containsChild(self._selectedPatient) == False:
            self._retrieveRootNode.addChild(self._selectedPatient)

        if (len(self._retrieveRootNode.children) > 0):
            self.btnDownload.setDisabled(False)
        else:
            self.btnDownload.setDisabled(True)

        self.reloadDicomPatientsModel()
        self.reloadSelectedTreeModel()

    def btnAddAllPatientsClicked(self):
        """Add all patients to receive cart button clicked
        """
        # Add only filtered patients
        for row in xrange(self._patientsProxyModel.rowCount()):
            index = self._patientsProxyModel.index(row, 0)
            patient = first.first(
                patient for patient in self._patients if patient.id.encode("utf-8") == index.data().toPyObject().toUtf8()
            )

            patient.isChecked = True
            if self._retrieveRootNode.containsChild(patient) == False:
                self._retrieveRootNode.addChild(patient)

        if (len(self._retrieveRootNode.children) > 0):
            self.btnDownload.setDisabled(False)
        else:
            self.btnDownload.setDisabled(True)

        self.reloadDicomPatientsModel()
        self.reloadSelectedTreeModel()

    def btnRemovePatientClicked(self):
        """Remove patient from receive cart button clicked
        """
        self._selectedPatient.isChecked = False
        if self._retrieveRootNode.containsChild(self._selectedPatient) == True:
            self._retrieveRootNode.removeChild(self._selectedPatient)

        if (len(self._retrieveRootNode.children) > 0):
            self.btnDownload.setDisabled(False)
        else:
            self.btnDownload.setDisabled(True)

        self.reloadDicomPatientsModel()
        self.reloadSelectedTreeModel()

    def btnRemoveAllPatientsClicked(self):
        """Remove all patients from retrieve cart button clicked
        """
        for patient in self._patients:
            patient.isChecked = False
            if self._retrieveRootNode.containsChild(patient) == True:
                self._retrieveRootNode.removeChild(patient)

        if (len(self._retrieveRootNode.children) > 0):
            self.btnDownload.setDisabled(False)
        else:
            self.btnDownload.setDisabled(True)

        self.reloadDicomPatientsModel()
        self.reloadSelectedTreeModel()

    def btnDownloadClicked(self):
        """Download button pressed (DICOM download workflow started)
        """
        QtGui.qApp.processEvents(QtCore.QEventLoop.AllEvents, 1000)

        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)

        downloadDir = self.selectFolderDialog()
        
        if downloadDir is not None:

            # Disable upload button for now but better is to disable whole UI
            self.btnDownload.setEnabled(False)

            self._svcAE.downloadDir = downloadDir

            # Start download DICOM data
            # Create thread
            self._threadPool.append(WorkerThread(self._svcAE.queryRetrieveTree, [self._retrieveRootNode, self._selectedNode]))
            # Connect finish event
            self._threadPool[len(self._threadPool) - 1].finished.connect(self.dicomDownloadFinishedMessage)
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
            self.progressBar.setValue(progress)
        else:
            received = data
            self.window().statusBar.showMessage("Received files: [" + str(received) + "]")

    def handleDestroyed(self):
        """Kill running threads
        """
        self._logger.debug("Destroying DICOM lookup module")
        self._svcAE.quit()
        for thread in self._threadPool:
            thread.terminate()
            thread.wait()
            self._logger.debug("Thread killed.")

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
        try:
            if sys.version < "3":
                self._svcAE = ApplicationEntityService()
            self._svcCSV = CsvFileDataService()
        except Exception as err:
            self._logger.error(str(err))

    def reloadData(self):
        """Initialization of data for UI
        """
        # DICOM server nodes
        del self._dicomNodes[:]
        self._dicomNodes = []

        # DICOM patients
        del self._patients[:]
        self._patients = []

        # DICOM studies
        del self._studies[:]
        self._studies = []

        # DICOM series
        del self._series[:]
        self._series= []

        # Load DICOM nodes
        self.reloadDicomNodes()

    def reloadDicomNodes(self):
        """Reload DicomNodes
        """
        # Setup loading UI
        self.window().statusBar.showMessage("Loading list of configured DICOM nodes...")
        self.window().enableIndefiniteProgess()
        self.tabWidget.setEnabled(False)

        self._dicomNodes = ConfigDetails().remoteAEs

        # And prepare ViewModel for the GUI
        nodesModel = QtGui.QStandardItemModel()
        for node in self._dicomNodes:
           text = QtGui.QStandardItem(node["AET"])
           text.setToolTip(node["Address"])
           nodesModel.appendRow([text])
        self.cmbDicomNode.setModel(nodesModel)

        # Update status bar
        self.tabWidget.setEnabled(True)
        self.window().statusBar.showMessage("Ready")
        self.window().disableIndefiniteProgess()

        # Select the first study
        if len(self._dicomNodes) > 0:
            self._selectedNode = self._dicomNodes[0]
        else:
            self.Error("No remote DICOM servers configured!")

    def reloadDicomPatientsModel(self):
        """Reload DICOM patients table ViemModel
        """
        # View model for DICOM patients table
        patientsModel = QtGui.QStandardItemModel()
        patientsModel.setHorizontalHeaderLabels(["PatientID", "Patient Name", "Gender", "Birth Date", "Retrieve"])

        row = 0
        for patient in self._patients:
            patientIdItem = QtGui.QStandardItem(patient.id)
            patientNameItem = QtGui.QStandardItem(patient.name)
            patientGenderItem = QtGui.QStandardItem(patient.gender)
            patientBirthDateItem = QtGui.QStandardItem(patient.dob)
            patientIsSelectedItem = QtGui.QStandardItem(str(patient.isChecked))

            patientsModel.setItem(row, 0, patientIdItem)
            patientsModel.setItem(row, 1, patientNameItem)
            patientsModel.setItem(row, 2, patientGenderItem)
            patientsModel.setItem(row, 3, patientBirthDateItem)
            patientsModel.setItem(row, 4, patientIsSelectedItem)

            row = row + 1

        # Create a proxy model to enable Sorting and filtering
        self._patientsProxyModel = QtGui.QSortFilterProxyModel()
        self._patientsProxyModel.setSourceModel(patientsModel)
        self._patientsProxyModel.setDynamicSortFilter(True)
        self._patientsProxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        # Connect to filtering UI element
        QtCore.QObject.connect(
            self.txtPatientFilter, 
            QtCore.SIGNAL("textChanged(QString)"), 
            self._patientsProxyModel.setFilterRegExp
        )

        # Set the models Views
        self.tvPatients.setModel(self._patientsProxyModel)

        # Resize the width of columns to fit the content
        self.tvPatients.resizeColumnsToContents()

        # After the view has model, set currentChanged behaviour
        self.tvPatients.selectionModel().currentChanged.connect(self.tblPatientChanged)
        self.tvPatients.doubleClicked.connect(self.tblPatientDoubleClicked)

    def reloadDicomStudiesModel(self):
        """Reload DICOM studies table ViewModel
        """
        # View model for DICOM studies table
        studyModel = QtGui.QStandardItemModel()
        studyModel.setHorizontalHeaderLabels(["Modalities", "Description", "Date", "UID"])

        row = 0

        for study in self._studies:

            modalitiesString = ""
            if type(study.modalities) is dicom.multival.MultiValue:
                modalitiesString = ",".join(study.modalities)
            else:
                modalitiesString = str(study.modalities)

            studyModalitiesItem = QtGui.QStandardItem(modalitiesString)
            studyDateItem = QtGui.QStandardItem(study.date)
            studyDescriptionItem = QtGui.QStandardItem(study.description)
            studyUidItem = QtGui.QStandardItem(study.suid)

            studyModel.setItem(row, 0, studyModalitiesItem)
            studyModel.setItem(row, 1, studyDescriptionItem)
            studyModel.setItem(row, 2, studyDateItem)
            studyModel.setItem(row, 3, studyUidItem)

            row = row + 1

        # Create a proxy model to enable Sorting and filtering
        self._studyProxyModel = QtGui.QSortFilterProxyModel()
        self._studyProxyModel.setSourceModel(studyModel)
        self._studyProxyModel.setDynamicSortFilter(True)
        self._studyProxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        # Connect to filtering UI element
        QtCore.QObject.connect(self.txtStudyFilter, QtCore.SIGNAL("textChanged(QString)"), self._studyProxyModel.setFilterRegExp)

        # Set the models Views
        self.tvStudies.setModel(self._studyProxyModel)

        # Resize the width of columns to fit the content
        self.tvStudies.resizeColumnsToContents()

        # After the view has model, set currentChanged behaviour
        self.tvStudies.selectionModel().currentChanged.connect(self.tblStudyChanged)

    def reloadDicomSeriesModel(self):
        """Reload DICOM series table ViewModel
        """
        seriesModel = QtGui.QStandardItemModel()
        seriesModel.setHorizontalHeaderLabels(["Modality", "Description", "Date", "Time", "UID"])

        row = 0

        for series in self._series:
            seriesModalityLabel = QtGui.QStandardItem(series.modality)
            seriesDescriptionLabel = QtGui.QStandardItem(series.description)
            seriesDateLabel = QtGui.QStandardItem(series.date)
            seriesTimeLabel = QtGui.QStandardItem(series.time)
            seriesUidLabel = QtGui.QStandardItem(series.suid)

            seriesModel.setItem(row, 0, seriesModalityLabel)
            seriesModel.setItem(row, 1, seriesDescriptionLabel)
            seriesModel.setItem(row, 2, seriesDateLabel)
            seriesModel.setItem(row, 3, seriesTimeLabel)
            seriesModel.setItem(row, 4, seriesUidLabel)

            row += 1

        # Create a proxy model to enable Sorting and filtering
        self._seriesProxyModel = QtGui.QSortFilterProxyModel()
        self._seriesProxyModel.setSourceModel(seriesModel)
        self._seriesProxyModel.setDynamicSortFilter(True)
        self._seriesProxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        # Connect to filtering UI element
        QtCore.QObject.connect(
            self.txtSeriesFilter,
            QtCore.SIGNAL("textChanged(QString)"),
            self._seriesProxyModel.setFilterRegExp
        )

        # Set the models Views
        self.tvSeries.setModel(self._seriesProxyModel)

        # Resize the width of columns to fit the content
        self.tvSeries.resizeColumnsToContents()

        # After the view has model, set currentChanged behaviour
        self.tvSeries.selectionModel().currentChanged.connect(self.tblSeriesChanged)

    def reloadDicomStudies(self):
        """Search DICOM patient studies
        """
        # Cean studies
        del self._studies[:]
        self._studies = []
        # Clean study series
        del self._series[:]
        self._series = []

        # Setup loading UI
        self.window().statusBar.showMessage("Loading DICOM studies...")
        self.window().enableIndefiniteProgess()
        self.tabWidget.setEnabled(False)

        # Prepare search
        selectedQueryLvl = "STUDY"
        self._association = self._svcAE.requestAssociation(self._selectedNode)

        # Create data loading thread
        self._threadPool.append(WorkerThread(
            self._svcAE.find, 
            [self._association, selectedQueryLvl, self._selectedPatient.name, self._selectedPatient.id])
        )

        # Connect slots
        self.connect(
            self._threadPool[len(self._threadPool) - 1],
            QtCore.SIGNAL("finished(QVariant)"),
            self.dicomFindStudiesFinished
        )

        # Start thread
        self._threadPool[len(self._threadPool) - 1].start()      

    def reloadDicomSeries(self):
        """Search DICOM study series
        """
        # Clean series
        del self._series[:]
        self._series = []

        # Setup loading UI
        self.window().statusBar.showMessage("Loading DICOM series...")
        self.window().enableIndefiniteProgess()
        self.tabWidget.setEnabled(False)

        # Prepare search
        selectedQueryLvl = "SERIES"
        self._association = self._svcAE.requestAssociation(self._selectedNode)

        # Create data loading thread
        self._threadPool.append(WorkerThread(
            self._svcAE.find, 
            [self._association, selectedQueryLvl, self._selectedPatient.name, self._selectedPatient.id, self._selectedStudy.suid])
        )

        # Connect slots
        self.connect(
            self._threadPool[len(self._threadPool) - 1],
            QtCore.SIGNAL("finished(QVariant)"),
            self.dicomFindSeriesFinished
        )

        # Start thread
        self._threadPool[len(self._threadPool) - 1].start()

    def reloadSelectedTreeModel(self):
        """Reload recieve cart tree ViewModel
        """
        # View model for DICOM data tree
        self.dicomDataModel = DicomDataItemModel(self._retrieveRootNode)

        self.dicomDataProxyModel = QtGui.QSortFilterProxyModel()
        self.dicomDataProxyModel.setSourceModel(self.dicomDataModel)
        self.dicomDataProxyModel.setDynamicSortFilter(True)
        self.dicomDataProxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        # Filtering
        # QtCore.QObject.connect(self.txtSeriesFilter, QtCore.SIGNAL("textChanged(QString)"), self.seriesProxyModel.setFilterRegExp)

        # Assign view model to the view
        self.treeDicomData.setModel(self.dicomDataProxyModel)
        self.treeDicomData.resizeColumnToContents(0)
        self.treeDicomData.expandAll()

        # Resize the column of tree view to see the series description
        self.treeDicomData.setColumnWidth(0, 200)

    def selectCsvFileDialog(self):
        """Open file dialog
        """
        try:
            filePath = QtGui.QFileDialog.getOpenFileName(None, "Please select the CSV file with patient IDs")
            if filePath == "":
                return None

            isReadable = os.access(str(filePath),  os.R_OK)
            QtGui.qApp.processEvents(QtCore.QEventLoop.AllEvents, 1000)
            
            if isReadable == False:
                self.Error("The client is not allowed to read data from the selected path!")
                self._logger.error("No read access to selected path.")
                return None
        except UnicodeEncodeError:
            self.Error("The path to the selected folder contains unsupported characters (unicode), please use only ascii characters in names of folders!")
            self._logger.error("Unsupported unicode folder path selected.")
            return None    

        return str(filePath)

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
                self._logger.error("No read access to selected folder.")
                return None
        except UnicodeEncodeError:
            self.Error("The path to the selected folder contains unsupported characters (unicode), please use only ascii characters in names of folders!")
            self._logger.error("Unsupported unicode folder path selected.")
            return None    

        return str(dirPath)

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

    def dicomFindPatientsFinised(self, dicomPatients):
        """Populate patients table after the reload finished
        """
        result = dicomPatients.toPyObject()

        for entity in result:
            if not entity[1]: continue
            try:
                patient = DicomPatient()
                patient.id = entity[1].PatientID
                patient.name = entity[1].PatientName
                patient.gender = entity[1].PatientSex
                patient.dob = entity[1].PatientBirthDate

                # Apply post query patient IDs list filter (from CSV file)
                if len(self._patientIds) > 0:
                    for patId in self._patientIds:
                        # TODO: maybe support for ignore case
                        if patId == patient.id:
                            self._patients.append(patient)
                            break
                else:
                    self._patients.append(patient)

            except Exception as err:
                self._logger.error(str(err))
                continue

        self._association.Release(0)

        self.reloadDicomPatientsModel()
        self.reloadDicomStudiesModel()
        self.reloadDicomSeriesModel()

        # Update status bar
        self.tabWidget.setEnabled(True)
        self.window().statusBar.showMessage("Ready")
        self.window().disableIndefiniteProgess()

    def dicomFindStudiesFinished(self, dicomStudies):
        """Populate studies table after the reload finished
        """
        result = dicomStudies.toPyObject()

        for entity in result:
            if not entity[1]: continue
            try:
                study = DicomStudy(entity[1].StudyInstanceUID, None)
                study.description = entity[1].StudyDescription
                study.date = entity[1].StudyDate
                study.modalities = entity[1].ModalitiesInStudy

                self._studies.append(study)
            except Exception as err:
                self._logger.error(str(err))
                continue

        self._association.Release(0)

        self.reloadDicomStudiesModel()
        self.reloadDicomSeriesModel()

        # Update status bar
        self.tabWidget.setEnabled(True)
        self.window().statusBar.showMessage("Ready")
        self.window().disableIndefiniteProgess()

    def dicomFindSeriesFinished(self, dicomSeries):
        """Populate series table after reload of series finished
        """
        result = dicomSeries.toPyObject()

        for entity in result:
            if not entity[1]: continue
            try:
                series = DicomSeries(entity[1].SeriesInstanceUID, False, None)
                series.modality = entity[1].Modality
                series.description = entity[1].SeriesDescription
                series.date = entity[1].SeriesDate
                series.time = entity[1].SeriesTime

                self._series.append(series)
            except Exception as err:
                self._logger.error(str(err))
                continue

        self._association.Release(0)

        self.reloadDicomSeriesModel()

        # Update status bar
        self.tabWidget.setEnabled(True)
        self.window().statusBar.showMessage("Ready")
        self.window().disableIndefiniteProgess()

    def dicomDownloadFinishedMessage(self):
        """ Called after uploadDataThread finished, after the data were uploaded to the RadPlanBio server
        """
        # Enable upload button
        self.btnDownload.setEnabled(True)
        self.window().statusBar.showMessage("Ready")
