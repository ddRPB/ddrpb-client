#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# Standard
import sys
import os

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

# Domain
from domain.CrfDicomField import CrfDicomField

# Module UI
from gui.DicomUploadModuleUI import DicomUploadModuleUI

# Dialogs
from gui.DicomBrowserDialog import DicomBrowserDialog
from gui.DicomStudyDialog import DicomStudyDialog
from gui.DicomMappingDialog import DicomMappingDialog

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

# Version numbers comparison
from distutils.version import LooseVersion

# Workers
from workers.WorkerThread import WorkerThread

 ######   #######  ##    ##  ######  ########  ######  
##    ## ##     ## ###   ## ##    ##    ##    ##    ## 
##       ##     ## ####  ## ##          ##    ##       
##       ##     ## ## ## ##  ######     ##     ######  
##       ##     ## ##  ####       ##    ##          ## 
##    ## ##     ## ##   ### ##    ##    ##    ##    ## 
 ######   #######  ##    ##  ######     ##     ######

# DICOM CRF annotation names
DICOM_PATIENT_ID = "DICOM_PATIENT_ID"
DICOM_STUDY_INSTANCE_UID = "DICOM_STUDY_INSTANCE_UID"
DICOM_SERIES_INSTANCE_UID = "DICOM_SERIES_INSTANCE_UID"
DICOM_SR_TEXT = "DICOM_SR_TEXT"

# RTSTRUCT types
COMMON = "COMMON"
ORGAN = "ORGAN"
ORGANLR = "ORGANLR"

##     ##  #######  ########  ##     ## ##       ########
###   ### ##     ## ##     ## ##     ## ##       ##
#### #### ##     ## ##     ## ##     ## ##       ##
## ### ## ##     ## ##     ## ##     ## ##       ######
##     ## ##     ## ##     ## ##     ## ##       ##
##     ## ##     ## ##     ## ##     ## ##       ##
##     ##  #######  ########   #######  ######## ########


class DicomUploadModule(QWidget, DicomUploadModuleUI):
    """This module is responsible for assigning DICOM data to existing Study/Subject/eCRF.
    It takes local folder with DICOM study use existing Patient PID as PatientID tag for
    newly generated pseudonymised DICOM files. Afterwards the pseudonymised files are uploaded
    to RadPlanBio import/export server, to the location which is mapped to automatically
    import incoming data into PACS ConQuest. Also the existing eCRF study in OpenClinica
    is modified to have the data about DICOM PatientID and StudyInstanceUID in order to
    be able to make a connection between PACS and eCRF.
    """

    def __init__(self, parent=None):
        """Constructor of DicomUploadModule
        """
        # Setup GUI
        QWidget.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)

        # Hide summary of XML for importing data to OC (for user not necessary)
        self.lblSummary.hide()

        # Setup logger - use config file
        self.logger = logging.getLogger(__name__)
        logging.config.fileConfig('logging.ini', disable_existing_loggers=False)

        # List of worker threads
        self._threadPool = []

        # Initialise main data members
        self._mySite = None
        # Prepares services and main data for this ViewModel
        self.prepareServices()

        self.studySubjectProxyModel = None

        # Initialize data structures for UI
        self._studies = []
        self._studySubjects = []
        self._crfFieldsAnnotation = []
        self._crfDicomFields = []
        self._crfFieldsDicomPatientAnnotation = []
        self._crfFieldDicomReportAnnotation = []

        self._selectedStudy = None
        self._studyMetadata = None
        self._selectedStudySite = None
        self._selectedStudySubject = None
        self._selectedStudyEvent = None
        self._selectedCrfDicomField = None
        self._selectedCrfDicomPatientField = None
        self._selectedCrfSRTextField = None

        self.reloadData()

        # Finish UI setup
        self.lblOcConnection.setText("[" + OCUserDetails().username + "] " + self._mySite.edc.soappublicurl)

        # Register handlers
        self.btnUpload.clicked.connect(self.btnUploadClicked)
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
        self.tvStudySubjects.setModel(None)
        self.tvStudyEvents.setModel(None)
        self.tvDicomStudies.setModel(None)
        self.textBrowserProgress.clear()

        # Set selected study and reload sites
        if sys.version < "3":
            self._selectedStudy = first.first(
                study for study in self._studies if study.name().encode("utf-8") == text.toUtf8()
            )
        else:
            self._selectedStudy = first.first(
                study for study in self._studies if study.name() == text
            )
        
        # Reload CRF fields annotation
        self.reloadCrfFieldsAnnotations()

        # Reload study sites
        self.reloadStudySites()

    def tblStudyItemChanged(self, current, previous):
        """Event handler which is triggered when selectedStudy change

        When the study is selected I have to clean all the other data elements
        Which depends on study. It means: StudySubjects, StudyEventDefinitions, StudyEventCRFs
        """
        # Clean the model before loading the new one
        self.tvStudySubjects.setModel(None)
        self.tvStudyEvents.setModel(None)
        self.tvDicomStudies.setModel(None)   
        self.textBrowserProgress.clear()  

        # Take the first column of selected row from table view (study identifier)
        index = self.studyProxyModel.index(current.row(), 0)

        # Multicentre
        if len(self._selectedStudy.sites) > 0:
            if sys.version < "3":
                self._selectedStudySite = first.first(
                    studySite for studySite in self._selectedStudy.sites if
                    studySite.identifier.encode("utf-8") == index.data().toPyObject().toUtf8()
                )
            else:
                self._selectedStudySite = first.first(
                    studySite for studySite in self._selectedStudy.sites if
                    studySite.identifier == index.data()
                )

        # Get the study metadata
        self.reloadStudyMetadata()

    def tblStudySubjectItemChanged(self, current, previous):
        """Event handler which is triggered when selectedStudySubject change
        """
        self.tvStudyEvents.setModel(None)
        self.tvDicomStudies.setModel(None)
        self.textBrowserProgress.clear()

        # Take the first column of selected row from table view (StudySubjectID)
        index = self.studySubjectProxyModel.index(current.row(), 0)

        if sys.version < "3":
            if index.data().toPyObject():
                self._selectedStudySubject = (
                    first.first(
                        subject for subject in self._studySubjects if subject.label().encode("utf-8") == index.data().toPyObject().toUtf8()
                    )
                )
        else:
            if index.data():
                self._selectedStudySubject = (
                    first.first(
                        subject for subject in self._studySubjects if subject.label() == index.data()
                    )
                )

        if self._selectedStudySubject is not None:
            if self._selectedStudySubject.subject.uniqueIdentifier is None or self._selectedStudySubject.subject.uniqueIdentifier == "":
                errMsg = "Selected study subject (" + self._selectedStudySubject.label() + ") "
                errMsg += "has no pseudonym and no DICOM data can be associated with subject without pseudonym. "
                errMsg += "Please correct the subject record in RPB first."
                self.Error(errMsg)
            else:
                # TODO: I don't like this approach, refactor it!!!
                # Propagate PatientID into service
                self.svcDicom.PatientID = self._selectedStudySubject.subject.uniqueIdentifier

                # Load scheduled events for selected subject
                self.reloadEvents()
            
    def tblStudyEventItemChanged(self, current, previous):
        """Event handler which is triggered when selectedStudyEventDefinition change
        """
        self.tvDicomStudies.setModel(None)
        self.textBrowserProgress.clear()

        # Selected studyEventDefinitions
        # Take the first column of selected row from table view (Event Name with repeat key if the event is repeating)
        index = self.studyEventProxyModel.index(current.row(), 0)

        if sys.version < "3":
            if index.data().toPyObject():
                self._selectedStudyEvent = (
                    first.first(
                        e for e in self._selectedStudySubject.events if (e.name.encode("utf-8") == index.data().toPyObject().toUtf8()) or
                         (e.name + " [" + e.studyEventRepeatKey + "]").encode("utf-8") == index.data().toPyObject().toUtf8()
                    )
                )
        else:
            if index.data():
                self._selectedStudyEvent = (
                    first.first(
                        e for e in self._selectedStudySubject.events if (e.name == index.data()) or
                         (e.name + " [" + e.studyEventRepeatKey + "]") == index.data()
                    )
                )

        if self._selectedStudyEvent is not None:
            # Determine whether the upload is allowed based on event status
            if self._selectedStudyEvent.status is not None:
                if self._selectedStudyEvent.status in ["stopped", "skipped", "locked"]:
                    self.Error("Selected study event is %s, you cannot upload DICOM data for this event unless the status of the event changes in EDC." % self._selectedStudyEvent.status)
                else:
                    self.reloadDicomFields()
            else:
                self.Error("Failed to load status data of selected study event")

    def tblDicomStudiesItemChanged(self, current, previous):
        """Event handler which is triggered when DICOM study item change
        """
        self.textBrowserProgress.clear()

        # Take the fifth column (OID) of selected row from table view
        index = self.dicomFieldsProxyModel.index(current.row(), 5)

        if sys.version < "3":
            if index.data().toPyObject():
                self._selectedCrfDicomField = first.first(field for field in self._crfDicomFields if field.oid.encode("utf-8") == index.data().toPyObject().toUtf8())
        else:
            if index.data():
                self._selectedCrfDicomField = first.first(field for field in self._crfDicomFields if field.oid == index.data())

        if self._selectedCrfDicomField is not None and self._selectedCrfDicomField.value != "":
            msg = "DICOM study was already uploaded for " + self._selectedCrfDicomField.label + " DICOM field. "
            msg += "If you continue with upload the existing data will not be removed from research PACS, "
            msg += "however the newly uploaded DICOM study will replace the association with selected "
            msg += "study subject DICOM field."
            self.Message(msg)

        if self._selectedCrfDicomField is not None:
            # Get the appropriate DICOM patient CRF field depending on selected study
            for patientField in self._crfFieldsDicomPatientAnnotation:
                if (patientField.eventdefinitionoid == self._selectedCrfDicomField.eventOid and
                        patientField.formoid == self._selectedCrfDicomField.formOid):
                    self._selectedCrfDicomPatientField = patientField
                    break

            # Naming conventions item OID ends with
            #
            # SRTEXT - report
            # DCM - DICOM study instance

            # Report should be associated to study (max one report for one study)
            for reportField in self._crfFieldDicomReportAnnotation:
                if (reportField.eventdefinitionoid == self._selectedCrfDicomField.eventOid and
                    reportField.formoid == self._selectedCrfDicomField.formOid and
                    reportField.groupoid == self._selectedCrfDicomField.groupOid):

                    if self._selectedCrfDicomField.oid.endswith("DCM"):
                        dcmBaseOid = self._selectedCrfDicomField.oid[0: len(self._selectedCrfDicomField.oid) - 3]
                    else:
                        continue

                    if reportField.crfitemoid.endswith("SRTEXT"):
                        srBaseOid = reportField.crfitemoid[0: len(reportField.crfitemoid) - 6]
                    else:
                        continue

                    if dcmBaseOid == srBaseOid:
                        self._selectedCrfSRTextField = reportField
                        break

                    # Fix for PETra Follow-Up DICOM eCRF because I used wrong item name conventions there
                    if self._selectedStudy.identifier() == "STR-PETra-2013" and self._selectedStudyEvent.eventDefinitionOID == "SE_PRFOLLOWUP":
                        dcmBaseOid = dcmBaseOid.replace("UID", "")
                        if dcmBaseOid == srBaseOid:
                            self._selectedCrfSRTextField = reportField
                            break

            reportText = ""

            # Generate ODM XML for selection
            odm = self.fileMetaDataService.generateOdmXmlForStudy(
                self.getStudyOid(),
                self._selectedStudySubject,
                self._selectedStudyEvent,
                reportText,
                self._selectedCrfDicomPatientField,
                self._selectedCrfDicomField,
                self._selectedCrfSRTextField
            )

            self.logger.debug(odm)

            # Show the preliminary XML (without DICOM study UID - will be generated)
            self.lblSummary.setText(odm)
            self.lblSummary.setWordWrap(True)

            # Show the selected upload target
            msg = "Selected upload target: "
            msg += self._selectedStudy.name() + "/"
            if len(self._selectedStudy.sites) > 0:
                msg += self._selectedStudySite.name + "/"
            msg += self._selectedStudySubject.label() + " ["
            msg += self._selectedStudySubject.subject.uniqueIdentifier + "]" + "/"
            if self._selectedStudyEvent.isRepeating:
                msg += self._selectedStudyEvent.name + " [" + self._selectedStudyEvent.studyEventRepeatKey + "]/"
            else:
                msg += self._selectedStudyEvent.name + "/"
            msg += self._selectedCrfDicomField.label

            self.textBrowserProgress.append(msg)

    def btnUploadClicked(self):
        """Upload button pressed (DICOM upload workflow started)
        """
        if self.selectionIsComplete():
            QtGui.qApp.processEvents(QtCore.QEventLoop.AllEvents, 1000)

            self.progressBar.setRange(0, 100)
            self.progressBar.setValue(0)

            self.directory = self.selectFolderDialog()
            
            if self.directory is not None:
                # Make textBrowser visible
                self.textBrowserProgress.setVisible(True)
                self.textBrowserProgress.append('Wait please:')

                # Disable upload button for now but better is to desable whole UI
                self.btnUpload.setEnabled(False)

                # Start the workflow: analyse the type of DICOM
                self.performDicomDataPreparation()
        else:
            errMsg = "Selection of upload destination is not complete. "
            errMsg += "Please select site, subject, event and DICOM study and only than click on upload."
            self.Error(errMsg)

    def handleTaskUpdated(self, data):
        """Move progress bar percentage
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
        self.logger.debug("Destroying DICOM upload module")
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

 ######   #######  ##     ## ##     ##    ###    ##    ## ########   ######
##    ## ##     ## ###   ### ###   ###   ## ##   ###   ## ##     ## ##    ##
##       ##     ## #### #### #### ####  ##   ##  ####  ## ##     ## ##
##       ##     ## ## ### ## ## ### ## ##     ## ## ## ## ##     ##  ######
##       ##     ## ##     ## ##     ## ######### ##  #### ##     ##       ##
##    ## ##     ## ##     ## ##     ## ##     ## ##   ### ##     ## ##    ##
 ######   #######  ##     ## ##     ## ##     ## ##    ## ########   ######

    def selectionIsComplete(self):
        """Verify whether selection is complete and the upload procedure can start
        """
        return self._selectedStudy is not None and self._selectedStudySubject is not None and self._selectedStudyEvent is not None and self._selectedCrfDicomField is not None 

    def prepareServices(self):
        """Prepare services for this module
        """
        # HTTP connection to RadPlanBio server (Database)
        self.svcHttp = HttpConnectionService(ConfigDetails().rpbHost, ConfigDetails().rpbHostPort, UserDetails())
        self.svcHttp.application = ConfigDetails().rpbApplication

        if ConfigDetails().proxyEnabled:
            self.svcHttp.setupProxy(ConfigDetails().proxyHost, ConfigDetails().proxyPort, ConfigDetails().noProxy)
        if ConfigDetails().proxyAuthEnabled:
            self.svcHttp.setupProxyAuth(ConfigDetails().proxyAuthLogin, ConfigDetails().proxyAuthPassword)

        # Read partner site of logged user
        self._mySite = self.svcHttp.getMyDefaultAccount().partnersite

        # Condition logic depending on EDC version (OC)
        # OC has new web services starting from 3.7
        if self._mySite.edc.version is not None:
            self.logger.debug("EDC version: %s" % self._mySite.edc.version)

            if sys.version < "3":
                cmp = lambda x, y: LooseVersion(x).__cmp__(y)
            else:
                cmp = lambda x, y: LooseVersion(x)._cmp(y)

            isNewerVersion = cmp(str(self._mySite.edc.version), "3.7")
            self.logger.debug("Is newer OC version: " + str(isNewerVersion))
            if isNewerVersion >= 0:
                self._canUseSSIDinREST = True
            else:
                self._canUseSSIDinREST = False
        else:
            self._canUseSSIDinREST = False    

        # Create connection artifact to users main OpenClinica SOAP
        baseUrl = self._mySite.edc.soappublicurl
        self.ocConnectInfo = OCConnectInfo(baseUrl, OCUserDetails().username)
        self.ocConnectInfo.setPasswordHash(OCUserDetails().passwordHash)

        if ConfigDetails().proxyEnabled:
            self.ocWebServices = OCWebServices(self.ocConnectInfo, ConfigDetails().proxyHost, ConfigDetails().proxyPort, ConfigDetails().noProxy, ConfigDetails().proxyAuthLogin, ConfigDetails().proxyAuthPassword)
        else:
            self.ocWebServices = OCWebServices(self.ocConnectInfo)

        # ODM XML metadata processing
        self.fileMetaDataService = OdmFileDataService()
        # DICOM PROCESSING SERVICE
        self.svcDicom = DicomService()

        self.__mappingRoiDic = None

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

        # Selected sheduled studye event for subject
        self._selectedStudyEvent = None

        # CRF fields annotations
        del self._crfFieldsAnnotation[:]
        self._crfFieldsAnnotation = []
        del self._crfFieldsDicomPatientAnnotation[:]
        self._crfFieldsDicomPatientAnnotation = []
        del self._crfDicomFields[:]
        self._crfDicomFields = []
        del self._crfFieldDicomReportAnnotation[:]
        self._crfFieldDicomReportAnnotation = []

        self._selectedCrfDicomField = None
        self._selectedCrfDicomPatientField = None
        self._selectedCrfSRTextField = None

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

    def reloadCrfFieldsAnnotations(self):
        """Reload CRF fields annotation for study (in working thread)
        """
        # Setup loading UI
        self.window().statusBar.showMessage("Loading list of CRF fields annotations...")

        # Get RadPlanBio study and its CRF fields annotation
        s = self.svcHttp.getStudyByOcIdentifier(self._selectedStudy.identifier())

        # Create data loading thread
        if s:
            self._threadPool.append(
                WorkerThread(
                    self.svcHttp.getCrfFieldsAnnotationForStudy,
                    s.id
                )
            )
        else:
            QtGui.QMessageBox.warning(self, "Warning", "Selected study is not defined as RadPlanBio study.")

        # Connect slots
        self.connect(
            self._threadPool[len(self._threadPool) - 1],
            QtCore.SIGNAL("finished(QVariant)"),
            self.loadFieldsCrfFieldsAnnotationsFinished
        )

        # Start thread
        self._threadPool[len(self._threadPool) - 1].start()

    def reloadStudySites(self):
        """Reload sites for selected OpenClinica sutdy (in memory processing)
        (If it is mono centre study show one default site)
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

                row += 1
        else:
            studyIdentifierValue = QtGui.QStandardItem(self._selectedStudy.identifier())
            studyNameValue = QtGui.QStandardItem(self._selectedStudy.name())

            self.studySitesModel.setItem(row, 0, studyIdentifierValue)
            self.studySitesModel.setItem(row, 2, studyNameValue)

            row += 1

        # Create a proxy model to enable Sorting and filtering
        self.studyProxyModel = QtGui.QSortFilterProxyModel()
        self.studyProxyModel.setSourceModel(self.studySitesModel)
        self.studyProxyModel.setDynamicSortFilter(True)
        self.studyProxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        # Connect to filtering UI element
        QtCore.QObject.connect(
            self.txtStudyFilter,
            QtCore.SIGNAL("textChanged(QString)"),
            self.studyProxyModel.setFilterRegExp
        )

        self.tvStudies.setModel(self.studyProxyModel)
        self.tvStudies.resizeColumnsToContents()

        # After the view has model, set currentChanged behaviour
        self.tvStudies.selectionModel().currentChanged.connect(self.tblStudyItemChanged)

    def reloadSubjects(self):
        """Reload OpenClinica study subjects enrolled into selected study/site in working thread
        """
        # Clear study subjects
        del self._studySubjects[:]
        self._studySubjects = []
        self._selectedStudySubject = None
        self._studySubjects = None
        self._subjectsREST = None

        # Setup loading UI
        self.window().statusBar.showMessage("Loading list of study subjects...")
        self.window().enableIndefiniteProgess()
        self.tabWidget.setEnabled(False)

        # Load subject for whole study or only site if it is multicentre study
        if self._selectedStudy and self._selectedStudy.isMulticentre:
            self._threadPool.append(
                WorkerThread(
                    self.ocWebServices.listAllStudySubjectsByStudySite,
                    [self._selectedStudy, self._selectedStudySite, self._studyMetadata]
                )
            )
        else:
            self._threadPool.append(
                WorkerThread(
                    self.ocWebServices.listAllStudySubjectsByStudy,
                    [self._selectedStudy, self._studyMetadata]
                )
            )

        # Connect slots
        self.connect(
            self._threadPool[len(self._threadPool) - 1],
            QtCore.SIGNAL("finished(QVariant)"),
            self.loadSubjectsFinished
        )

        # Start thread
        self._threadPool[len(self._threadPool) - 1].start()

        # Need to get OIDs of all subjects
        if not self._canUseSSIDinREST:  
            self.logger.debug("Continuing with RESTfull URL to get OIDs for all study subjects")

            self._threadPool.append(
                WorkerThread(
                    self.svcHttp.getStudyCasebookSubjects,
                    [self._mySite.edc.edcpublicurl, self.getStudyOid()]
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

    def reloadEvents(self):
        """Reload OpenClinica events scheduled for selected study subject
        """
        # Setup loading UI
        self.window().statusBar.showMessage("Loading subject scheduled events...")
        self.window().enableIndefiniteProgess()
        self.tabWidget.setEnabled(False)
            
        if not self._canUseSSIDinREST:

            studySubjectIdentifier = self._selectedStudySubject.oid
            # Define a job
            # Need to get EventRepeatKeys
            self._threadPool.append(
                WorkerThread(
                    self.svcHttp.getStudyCasebookEvents,
                    [self._mySite.edc.edcpublicurl, self.getStudyOid(), studySubjectIdentifier]
                )
            )
        else:

            studySubjectIdentifier = self._selectedStudySubject.label()
            # Define a job
            # Need to get EventRepeatKeys
            self._threadPool.append(
                WorkerThread(
                    self.svcHttp.getStudyCasebookSubjectWithEvents,
                    [self._mySite.edc.edcpublicurl, self.getStudyOid(), studySubjectIdentifier]
                )
            )

        # Connect slots
        self.connect(
            self._threadPool[len(self._threadPool) - 1],
            QtCore.SIGNAL("finished(QVariant)"),
            self.loadEventsFinished
        )

        # Start thread
        self._threadPool[len(self._threadPool) - 1].start()
        
    def reloadDicomFields(self):
        """Reload annotations for OpenClinica eCRF fields
        """
        # Prerequisites for DICOM annotations loading
        if self._selectedStudySubject and self._selectedStudyEvent:

            # Setup loading UI
            self.window().statusBar.showMessage("Loading list of DICOM field values...")
            self.window().enableIndefiniteProgess()
            self.tabWidget.setEnabled(False)

            studyoid = self.getStudyOid()
            sspid = self._selectedStudySubject.subject.uniqueIdentifier
            
            eventDefOid = self._selectedStudyEvent.eventDefinitionOID
            studyEventRepeatKey = self._selectedStudyEvent.studyEventRepeatKey

            # Get annotation for selected event and non-hidden eCRFs which you want to retrieve values for
            annotations = []
            for crfAnnotation in self._crfFieldsAnnotation:
                # Only annotation in event
                if crfAnnotation.eventdefinitionoid == self._selectedStudyEvent.eventDefinitionOID:
                    # Only form (versions) which are scheduled (default versions are scheduled automatically)
                    if self._selectedStudyEvent.hasScheduledCrf(crfAnnotation.formoid):
                        annotations.append(crfAnnotation)

            # Create data loading thread
            self._threadPool.append(
                WorkerThread(
                    self.svcHttp.getCrfItemsValues,
                    [studyoid, sspid, eventDefOid, studyEventRepeatKey, annotations]
                )
            )

            # Connect slots
            self.connect(
                self._threadPool[len(self._threadPool) - 1],
                QtCore.SIGNAL("finished(QVariant)"),
                self.loadDicomFieldsFinished
            )

            # Start thread
            self._threadPool[len(self._threadPool) - 1].start()

    def performDicomDataPreparation(self):
        """Extract the structure from DICOM data
        """
        # Create thread, and pass the DICOM folder as parameter
        self._threadPool.append(WorkerThread(self.svcDicom.prepareDicomData, self.directory))

        # Connect message events (error-message, log, finished)
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
        self.connect(
            self._threadPool[len(self._threadPool) - 1],
            QtCore.SIGNAL("taskUpdated"),
            self.handleTaskUpdated
        )
        self.connect(
            self._threadPool[len(self._threadPool) - 1],
            QtCore.SIGNAL("finished(QString)"),
            self.DicomPrepareFinished
        )

        # Start thread
        self._threadPool[len(self._threadPool) - 1].start()
        return

    def performDicomAnalysis(self):
        """Perform initial DICOM data analysis in a separate thread
        """
        # Create thread, and pass the DICOM folder as parameter
        self._threadPool.append(WorkerThread(self.svcDicom.analyseDicomStudyType, self.directory))

        # Connect message events (error-message, log, finished)
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
        self.connect(
            self._threadPool[len(self._threadPool) - 1],
            QtCore.SIGNAL("taskUpdated"),
            self.handleTaskUpdated
        )
        self.connect(
            self._threadPool[len(self._threadPool) - 1],
            QtCore.SIGNAL("finished(QString)"),
            self.DicomAnalyseFinished
        )

        # Start thread
        self._threadPool[len(self._threadPool) - 1].start()
        return

    def performDicomStudyOverview(self, dicomStudyType):
        """Shows DICOM study overview dialog
        """
        # View
        self.studyDialog = DicomStudyDialog(self)

        # View Model
        self.__patient = self.svcDicom.getPatient()
        self._selectedDicomStudy = self.svcDicom.getStudy()
        self.studyDialog.setModel(self.__patient, self._selectedDicomStudy, dicomStudyType)

        # RPB and DICOM data correspond
        if self.studyDialog.passSanityCheck(self._selectedStudySubject):
            # Show dialog
            if self.studyDialog.exec_():
                # Mapping will be passed to DICOM service via worker parameters
                return True
            else:
                return False
        else:
            errMsg = "There is a mismatch of gender or date of birth between selected RPB study subject and DICOM data."
            self.Error(errMsg)
            self.logger.error(errMsg)
            return False

    def performDicomMapping(self, dicomStudyType):
        """Shows DICOM region of interest mapping dialog
        """
        # Map DICOM ROIs - it is mandatory for Treatment Plan
        if dicomStudyType == "TreatmentPlan" or dicomStudyType == "Contouring":
            # Setup loading UI
            self.window().statusBar.showMessage("Loading formalised RTSTRUCT names...")
            self.window().enableIndefiniteProgess()
            self.tabWidget.setEnabled(False)

            # Define a job
            self._threadPool.append(
                WorkerThread(
                    self.svcHttp.getAllRTStructs, []
                )
            )

            # Connect slots
            self.connect(
                self._threadPool[len(self._threadPool) - 1],
                QtCore.SIGNAL("finished(QVariant)"),
                self.loadRTStructsFinished
            )

            # Start thread
            self._threadPool[len(self._threadPool) - 1].start()
        else:
            self.performDicomDeidentification()

    def performDicomDeidentification(self):
        """De-identify DICOM study
        """
        # Create thread - Anonymise data and use ROI mapping
        self._threadPool.append(
            WorkerThread(
                self.svcDicom.anonymiseDicomData, 
                [self.__patient, self._selectedDicomStudy, self.__mappingRoiDic]
            )
        )

        # Connect message events (message, log, finised)
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
        self.connect(
            self._threadPool[len(self._threadPool) - 1],
            QtCore.SIGNAL("finished(QString)"),
            self.DicomAnonymiseFinishedMessage
        )
        self.connect(
            self._threadPool[len(self._threadPool) - 1],
            QtCore.SIGNAL("taskUpdated"),
            self.handleTaskUpdated
        )

        # Start thread
        self._threadPool[len(self._threadPool) - 1].start()

    def selectFolderDialog(self):
        """User selects a directory with the DICOM study files
        """
        try:
            dirPath = QtGui.QFileDialog.getExistingDirectory(
                None,
                "Please select the folder with patient DICOM study files"
            )
            if dirPath == "":
                return None

            isReadable = os.access(str(dirPath), os.R_OK)
            QtGui.qApp.processEvents(QtCore.QEventLoop.AllEvents, 1000)
            
            if not isReadable:
                errMsg = "The client is not allowed to read data from the selected folder!"
                self.Error(errMsg)
                self.logger.error(errMsg)
                return None
        except UnicodeEncodeError:
            errMsg = "The path to the selected folder contains unsupported special characters, "
            errMsg += "please use only ASCII characters in names of folders!"
            self.Error(errMsg)
            self.logger.error(errMsg)
            return None    

        return str(dirPath)

    def performDicomUpload(self):
        """Perform upload of anonymised DICOM data and import of DICOM Patient ID, and Study Instance UID into OC
        Called after after annonymise is finished
        """
        self.textBrowserProgress.append("Importing pseudonymised data into EDC eCRF...")

        self._selectedCrfDicomField.value = self.svcDicom.StudyUID
        reportText = self.svcDicom.getReportSerieText()

        # Generate ODM XML for selection
        odm = self.fileMetaDataService.generateOdmXmlForStudy(
            self.getStudyOid(),
            self._selectedStudySubject,
            self._selectedStudyEvent,
            reportText,
            self._selectedCrfDicomPatientField,
            self._selectedCrfDicomField,
            self._selectedCrfSRTextField
        )

        self.logger.debug(odm)

        # Show the preliminary XML (without DICOM study UID - will be generated)
        self.lblSummary.setText(odm)
        self.lblSummary.setWordWrap(True)

        importSuccessful = self.ocWebServices.importODM(odm)
        if importSuccessful:
            self.textBrowserProgress.append("Import to OpenClinica EDC successful...")

            # Start uploading DICOM data
            # Create thread
            self._threadPool.append(WorkerThread(self.svcDicom.uploadDicomData, self.svcHttp))
            # Connect finish event
            self._threadPool[len(self._threadPool) - 1].finished.connect(self.DicomUploadFinishedMessage)
            # Connect message events
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
        else:
            self.textBrowserProgress.append("Import Error. Cannot continue.")
            return

        return

    def loadStudiesFinished(self, studies):
        """Finished loading studies from server
        """
        if sys.version < "3":
            self._studies = studies.toPyObject()
            self._studies.sort(cmp=lambda x, y: cmp(x.name(), y.name()))
        else:
            self._studies = studies
            self._studies = sorted(self._studies, key=lambda st: st.name())

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

        # Load annotation for selected study
        self.reloadCrfFieldsAnnotations()

    def loadStudyMetadataFinished(self, metadata):
        """Finished loading metadata from server
        """
        if sys.version < "3":
            self._studyMetadata = metadata.toPyObject()
        else:
            self._studyMetadata = metadata

        # Update status bar
        self.tabWidget.setEnabled(False)
        self.window().statusBar.showMessage("Ready")
        self.window().disableIndefiniteProgess()

        if self._selectedStudy:
            # TODO: one could in theory retrieve status of the selected study from metadata for further logic

            # Set the OC active study according to the selection
            # in order to make sure that RESTfull calls are executed properly
            if self._selectedStudy.isMulticentre:
                ocStudy = self.svcHttp.getOCStudyByIdentifier(self._selectedStudySite.identifier)
            else:
                ocStudy = self.svcHttp.getOCStudyByIdentifier(self._selectedStudy.identifier())

            # Change active study in EDC
            updateResult = self.svcHttp.changeUserActiveStudy(UserDetails().username, ocStudy.id)

        # Reload study subjects with scheduled events (extend them with metadata)
        self.reloadSubjects()

    def loadSubjectsFinished(self, subjects):
        """Finished loading of SOAP subject data
        """
        if sys.version < "3":
            self._studySubjects = subjects.toPyObject()
        else:
            self._studySubjects = subjects

        # Need synchronise OIDs
        if not self._canUseSSIDinREST: 
            self.syncSubjectAndRESTSubjects()
        elif self._studySubjects is not None:
            # Create the ViewModels for Views
            self.subjectsModel = QtGui.QStandardItemModel()
            self.subjectsModel.setHorizontalHeaderLabels(
                ["StudySubjectID", "PID", "SecondaryID", "Gender", "Enrollment date"]
            )

            row = 0
            for studySubject in self._studySubjects:
                # Always mandatory
                labelItem = QtGui.QStandardItem(studySubject.label())
                enrollmentDateItem = QtGui.QStandardItem(studySubject.enrollmentDate)

                # Optional
                secondaryLabelItem = QtGui.QStandardItem("")
                if studySubject.secondaryLabel() is not None:
                    secondaryLabelItem = QtGui.QStandardItem(studySubject.secondaryLabel())

                # Not everything has to be collected (depend on study setup)
                pidItem = QtGui.QStandardItem("")
                genderItem = QtGui.QStandardItem("")
                if studySubject.subject is not None:
                    if studySubject.subject.uniqueIdentifier is not None:
                        pidItem = QtGui.QStandardItem(studySubject.subject.uniqueIdentifier)
                    if studySubject.subject.gender is not None:
                        genderItem = QtGui.QStandardItem(studySubject.subject.gender)

                self.subjectsModel.setItem(row, 0, labelItem)
                self.subjectsModel.setItem(row, 1, pidItem)
                self.subjectsModel.setItem(row, 2, secondaryLabelItem)
                self.subjectsModel.setItem(row, 3, genderItem)
                self.subjectsModel.setItem(row, 4, enrollmentDateItem)
                row += 1

            # Create a proxy model to enable Sorting and filtering
            self.studySubjectProxyModel = QtGui.QSortFilterProxyModel()
            self.studySubjectProxyModel.setSourceModel(self.subjectsModel)
            # Sorting
            self.studySubjectProxyModel.setDynamicSortFilter(True)
            self.studySubjectProxyModel.sort(0, QtCore.Qt.AscendingOrder)
            # Filtering
            self.studySubjectProxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

            # Connect to filtering UI element
            QtCore.QObject.connect(
                self.txtStudySubjectFilter,
                QtCore.SIGNAL("textChanged(QString)"),
                self.studySubjectProxyModel.setFilterRegExp
            )

            # Set the models Views
            self.tvStudySubjects.setModel(self.studySubjectProxyModel)

            # Resize the width of columns to fit the content
            self.tvStudySubjects.resizeColumnsToContents()

            # After the view has model, set currentChanged behaviour
            self.tvStudySubjects.selectionModel().currentChanged.connect(self.tblStudySubjectItemChanged)

            self.tabWidget.setEnabled(True)
            self.window().statusBar.showMessage("Ready")
            self.window().disableIndefiniteProgess()

    def loadSubjectsRESTFinished(self, subjects):
        """Finished loading of REST subject data
        """
        if sys.version < "3":
            self._subjectsREST = subjects.toPyObject()
        else:
            self._subjectsREST = subjects

        self.syncSubjectAndRESTSubjects()

    def syncSubjectAndRESTSubjects(self):
        """Synchronise results from SOAP and REST subject loading
        """
        self.logger.debug("Synchronising SOAP and REST subjects")

        # In case the REST worker finished sooner than the SOAP worker
        if self._studySubjects is not None and self._subjectsREST is not None:

            # Create the ViewModels for Views
            self.subjectsModel = QtGui.QStandardItemModel()
            self.subjectsModel.setHorizontalHeaderLabels(
                ["StudySubjectID", "PID", "SecondaryID", "Gender", "Enrollment date", "OID"]
            )

            row = 0
            for studySubject in self._studySubjects:
                # Always mandatory
                labelItem = QtGui.QStandardItem(studySubject.label())
                enrollmentDateItem = QtGui.QStandardItem(studySubject.enrollmentDate)

                # Optional
                secondaryLabelItem = QtGui.QStandardItem("")
                if studySubject.secondaryLabel() is not None:
                    secondaryLabelItem = QtGui.QStandardItem(studySubject.secondaryLabel())

                # Not everything has to be collected (depend on study setup)
                pidItem = QtGui.QStandardItem("")
                genderItem = QtGui.QStandardItem("")
                if studySubject.subject is not None:
                    if studySubject.subject.uniqueIdentifier is not None:
                        pidItem = QtGui.QStandardItem(studySubject.subject.uniqueIdentifier)
                    if studySubject.subject.gender is not None:
                        genderItem = QtGui.QStandardItem(studySubject.subject.gender)

                oidItem = QtGui.QStandardItem("")
                for sREST in self._subjectsREST:
                    if sREST.studySubjectId == studySubject.label():
                        oidItem = QtGui.QStandardItem(sREST.oid)
                        studySubject.oid = sREST.oid
                        break

                self.subjectsModel.setItem(row, 0, labelItem)
                self.subjectsModel.setItem(row, 1, pidItem)

                row += 1


            # Create a proxy model to enable Sorting and filtering
            self.studySubjectProxyModel = QtGui.QSortFilterProxyModel()
            self.studySubjectProxyModel.setSourceModel(self.subjectsModel)
            # Sorting
            self.studySubjectProxyModel.setDynamicSortFilter(True)
            self.studySubjectProxyModel.sort(0, QtCore.Qt.AscendingOrder)
            # Filtering
            self.studySubjectProxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

            # Connect to filtering UI element
            QtCore.QObject.connect(
                self.txtStudySubjectFilter,
                QtCore.SIGNAL("textChanged(QString)"),
                self.studySubjectProxyModel.setFilterRegExp
            )

            # Set the models Views
            self.tvStudySubjects.setModel(self.studySubjectProxyModel)

            # Resize the width of columns to fit the content
            self.tvStudySubjects.resizeColumnsToContents()

            # After the view has model, set currentChanged behaviour
            self.tvStudySubjects.selectionModel().currentChanged.connect(self.tblStudySubjectItemChanged)

            self.tabWidget.setEnabled(True)
            self.window().statusBar.showMessage("Ready")
            self.window().disableIndefiniteProgess()

    def loadEventsFinished(self, result):
        """Finished loading events data
        """
        if sys.version < "3":
            resultREST = result.toPyObject()
        else:
            resultREST = result

        if type(resultREST) is list:
            eventsREST = resultREST
        else:
            eventsREST = resultREST.studyEventData

        if self._canUseSSIDinREST:
            self._selectedStudySubject.oid = resultREST.oid
            self._selectedStudySubject.status = resultREST.status

            self.logger.debug("Loaded subject key: " + self._selectedStudySubject.oid)
            self.logger.debug("Loaded subject status: " + self._selectedStudySubject.status)

        # Only show events for available subjects
        if self._selectedStudySubject.status not in ["removed"]:

            # Quick way of crating simple view model
            self.eventsModel = QtGui.QStandardItemModel()
            self.eventsModel.setHorizontalHeaderLabels(
                ["Name", "Description", "Category", "Type", "Repeating", "Start date", "Status"]
            )

            row = 0
            for event in self._selectedStudySubject.events:

                # Show only events that have DICOM study UID annotations
                eventHasDicomCrf = False
                for crfAnnotation in self._crfFieldsAnnotation:
                    if crfAnnotation.eventdefinitionoid == event.eventDefinitionOID:
                        eventHasDicomCrf = True
                        break

                if eventHasDicomCrf:
                    nameItem = QtGui.QStandardItem(event.name)
                    descriptionItem = QtGui.QStandardItem(event.description)
                    categoryItem = QtGui.QStandardItem(event.category)
                    typeItem = QtGui.QStandardItem(event.eventType)
                    isRepeatingItem = QtGui.QStandardItem(str(event.isRepeating))
                    startDateItem = QtGui.QStandardItem("{:%d-%m-%Y}".format(event.startDate))

                    # Enhance with information from REST
                    statusItem = QtGui.QStandardItem()
                    for e in eventsREST:

                        soapEventStartDate = "{:%d-%m-%Y}".format(event.startDate)
                        restEventStartDate = "{:%d-%m-%Y}".format(e.startDate)

                        # Ugly workaround for the stupidity how OC handles missing times when using SOAP (issues with 12/24 hours)
                        if ((e.eventDefinitionOID == event.eventDefinitionOID and e.startDate.isoformat() == event.startDate.isoformat()) or
                            (e.eventDefinitionOID == event.eventDefinitionOID and restEventStartDate == soapEventStartDate and "T12:" in e.startDate.isoformat())):

                            # REST event for sync found according to OID and date,
                            # Add data from REST if it was not already added to domain model before
                            if not self._selectedStudySubject.scheduledEventOccurrenceExists(e):
                                event.status = e.status
                                event.studyEventRepeatKey = e.studyEventRepeatKey
                                event.setForms(e.forms)

                            # Set the attributes for view model
                            if event.isRepeating:
                                nameItem = QtGui.QStandardItem(event.name + " [" + event.studyEventRepeatKey + "]")
                            statusItem = QtGui.QStandardItem(event.status)

                            break

                    self.eventsModel.setItem(row, 0, nameItem)
                    self.eventsModel.setItem(row, 1, descriptionItem)
                    self.eventsModel.setItem(row, 2, categoryItem)
                    self.eventsModel.setItem(row, 3, typeItem)
                    self.eventsModel.setItem(row, 4, isRepeatingItem)
                    self.eventsModel.setItem(row, 5, startDateItem)
                    self.eventsModel.setItem(row, 6, statusItem)

                    row += 1

            self.studyEventProxyModel = QtGui.QSortFilterProxyModel()
            self.studyEventProxyModel.setSourceModel(self.eventsModel)
            self.studyEventProxyModel.setDynamicSortFilter(True)
            self.studyEventProxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

            QtCore.QObject.connect(
                self.txtStudyEventFilter,
                QtCore.SIGNAL("textChanged(QString)"),
                self.studyEventProxyModel.setFilterRegExp
            )

            self.tvStudyEvents.setModel(self.studyEventProxyModel)

            self.tvStudyEvents.resizeColumnsToContents()
            self.tvStudyEvents.selectionModel().currentChanged.connect(self.tblStudyEventItemChanged)

            # Update status bar
            self.tabWidget.setEnabled(True)
            self.window().statusBar.showMessage("Ready")
            self.window().disableIndefiniteProgess()
        else:
            # Update status bar
            self.tabWidget.setEnabled(True)
            self.window().statusBar.showMessage("Ready")
            self.window().disableIndefiniteProgess()

            self.Error("Selected study subject is %s, you cannot upload DICOM data for this study subject unless the status of the study subject changes in EDC." % self._selectedStudySubject.status)

    def loadRTStructsFinished(self, rtStructs):
        """Finished loading formalised RTSTRUCT contour names
        """
        if sys.version < "3":
            formalizedRTStructs = rtStructs.toPyObject()
        else:
            formalizedRTStructs = rtStructs

        # Update status bar
        self.tabWidget.setEnabled(True)
        self.window().statusBar.showMessage("Ready")
        self.window().disableIndefiniteProgess()

        self.textBrowserProgress.append('Enter DICOM ROIs mapping...')
        self.mappingDialog = DicomMappingDialog(self)

        # Load the dictionary of original ROIs in DICOM study
        originalRoiNameDict = self.svcDicom.getRoiNameDict()

        leftRightContours = []
        extraTextContours = []
        oarContours = []
        tvContours = []
        tvMultipleContours = []
        for struct in formalizedRTStructs:
            if struct.structType.name == ORGANLR:
                leftRightContours.append(struct.name)
                oarContours.append(struct.name)
            elif struct.structType.name == ORGAN:
                oarContours.append(struct.name)
            elif struct.structType.name == COMMON:
                extraTextContours.append(struct.name)
                if struct.identifier in ["TBV", "CTV", "GTV", "PTV", "CTVp", "CTVn", "GTVp", "GTVn", "PTVp", "PTVn", "CTVn_L1", "CTVn_L2", "CTVn_L3", "CTVn_L4", "CTVn_IMN", "CTVn_interpect", "CTVp_breast", "CTVp_chestwall", "CTVp_tumourbed", "PTVp_breast", "PTVp_chestwall", "PTVp_tumourbed"]:
                    tvContours.append(struct.name)
                if struct.identifier in ["CTVp", "CTVn", "GTVp", "GTVn", "PTVp", "PTVn"]:
                    tvMultipleContours.append(struct.name)

        # Setup view model for dialog
        self.mappingDialog.setModel(
            originalRoiNameDict,
            formalizedRTStructs,
            leftRightContours,
            extraTextContours,
            oarContours,
            tvContours,
            tvMultipleContours
        )

        # Show RTSTRUCT contour mapping dialog
        if self.mappingDialog.exec_():
            # Mapping will be passed to DICOM service via worker parameters
            self.__mappingRoiDic = self.mappingDialog.originalRoiNameDict
            # Continue with de-identification
            self.performDicomDeidentification()
        else:
            self.DicomUploadFinishedMessage()       

    def loadFieldsCrfFieldsAnnotationsFinished(self, annotations):
        """Finished loading study CRFs annotations from server (sort them)
        """
        # Reset lists
        del self._crfFieldsAnnotation[:]
        self._crfFieldsAnnotation = []
        del self._crfFieldsDicomPatientAnnotation[:]
        self._crfFieldsDicomPatientAnnotation = []
        del self._crfFieldDicomReportAnnotation[:]
        self._crfFieldDicomReportAnnotation = []

        if sys.version < "3":
            annots = annotations.toPyObject()
        else:
            annots = annotations

        # Sort them to proper lists and filter only DICOM upload related
        for annotation in annots:
            if annotation.annotationtype.name == DICOM_PATIENT_ID:
                self._crfFieldsDicomPatientAnnotation.append(annotation)
            elif annotation.annotationtype.name == DICOM_STUDY_INSTANCE_UID:
                self._crfFieldsAnnotation.append(annotation)
            elif annotation.annotationtype.name == DICOM_SR_TEXT:  
                self._crfFieldDicomReportAnnotation.append(annotation)

        # Update status bar
        self.window().statusBar.showMessage("Ready")

    def loadDicomFieldsFinished(self, crfFieldValues):
        """Finished loading DICOM field CRFs values from server
        """
        if sys.version < "3":
            retrievedValue = crfFieldValues.toPyObject()
        else:
            retrievedValue = crfFieldValues

        # Get annotation for selected event
        row = 0
        dicomFieldsModel = QtGui.QStandardItemModel()
        dicomFieldsModel.setHorizontalHeaderLabels(
            ["Label", "Description", "Data type", "Field value", "Annotation", "OID"]
        )
        self._crfDicomFields = []

        for crfAnnotation in self._crfFieldsAnnotation:
            # Only annotation in event
            if crfAnnotation.eventdefinitionoid == self._selectedStudyEvent.eventDefinitionOID:

                # Only form (versions) which are scheduled (default versions are scheduled automatically)
                if self._selectedStudyEvent.hasScheduledCrf(crfAnnotation.formoid):

                    value = str(retrievedValue[row])

                    field = CrfDicomField(
                        crfAnnotation.crfitemoid,
                        value,
                        crfAnnotation.annotationtype.name,
                        crfAnnotation.eventdefinitionoid,
                        crfAnnotation.formoid,
                        crfAnnotation.groupoid
                    )

                    self._crfDicomFields.append(field)

                    i = self.fileMetaDataService.loadCrfItem(
                        crfAnnotation.formoid,
                        crfAnnotation.crfitemoid,
                        self._studyMetadata
                    )
                    if i is not None:
                        field.label = i.label
                        itemLabelValue = QtGui.QStandardItem(i.label)
                        itemDescriptionValue = QtGui.QStandardItem(i.description)
                        itemDataTypeValue = QtGui.QStandardItem(i.dataType)
                        itemValueValue = QtGui.QStandardItem(value)
                        itemAnnotationType = QtGui.QStandardItem(crfAnnotation.annotationtype.name)
                        itemCrfFieldOid = QtGui.QStandardItem(field.oid)

                        dicomFieldsModel.setItem(row, 0, itemLabelValue)
                        dicomFieldsModel.setItem(row, 1, itemDescriptionValue)
                        dicomFieldsModel.setItem(row, 2, itemDataTypeValue)
                        dicomFieldsModel.setItem(row, 3, itemValueValue)
                        dicomFieldsModel.setItem(row, 4, itemAnnotationType)
                        dicomFieldsModel.setItem(row, 5, itemCrfFieldOid)

                        row += 1

        # Create a proxy model to enable Sorting and filtering
        self.dicomFieldsProxyModel = QtGui.QSortFilterProxyModel()
        self.dicomFieldsProxyModel.setSourceModel(dicomFieldsModel)
        self.dicomFieldsProxyModel.setDynamicSortFilter(True)
        self.dicomFieldsProxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        # Connect to filtering UI element
        QtCore.QObject.connect(
            self.txtDicomStudiesFilter,
            QtCore.SIGNAL("textChanged(QString)"),
            self.dicomFieldsProxyModel.setFilterRegExp
        )

        # Set model to View
        self.tvDicomStudies.setModel(self.dicomFieldsProxyModel)

        # Resize the width of columns to fit the content
        self.tvDicomStudies.resizeColumnsToContents()

        # After the view has model, set currentChanged behaviour
        self.tvDicomStudies.selectionModel().currentChanged.connect(self.tblDicomStudiesItemChanged)

        # Update status bar
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
            self.btnUpload.setEnabled(False)
        else:
            self.btnUpload.setEnabled(True)

    def Error(self, string):
        """Error message box
        """
        QtGui.QMessageBox.critical(self, "Error", string)
        self.btnUpload.setEnabled(True)

    def Warning(self, string):
        """Warning message box
        """
        QtGui.QMessageBox.warning(self, "Warning", string)
        self.btnUpload.setEnabled(True)

    def Message(self, string):
        """Called from message event, opens a small window with the message
        """
        QtGui.QMessageBox.about(self, "Info", string)
        self.btnUpload.setEnabled(True)

    def LogMessage(self, string):
        """Called from log event in thread and adds log into textbrowser UI
        """
        self.textBrowserProgress.append(string)

    def DicomPrepareFinished(self, result):
        """Preparation finished show DICOM browser
        """
        # DICOM parsing successful
        if result == "True":
            # Collect DICOM data hierarchy
            rootNode = self.svcDicom.dataRoot

            # Provide the possibility to sub select what DICOM data to include
            self.dicomBrowserDialog = DicomBrowserDialog(self)
            self.dicomBrowserDialog.setModel(rootNode)

            if self.dicomBrowserDialog.exec_():
                self.performDicomAnalysis()
            else:
                self.DicomUploadFinishedMessage()
        # DICOM parsing was not successful
        else:
            self.DicomUploadFinishedMessage()

    def DicomAnalyseFinished(self, dicomStudyType):
        """Initial analysis of provided dicom data finished
        """
        ready = False

        # Check the analysis results
        if not self.svcDicom.hasOnePatient:
            if ConfigDetails().allowMultiplePatientIDs:
                msg = "Multiple patients were found in provided DICOM study [" + str(self.svcDicom.patientCount) + "]. "
                msg += "If you continue the client will deal with provided data as if it belong to one patient. "
                msg += "Do you want to continue?"
                reply = QtGui.QMessageBox.question(self, "Question", msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

                if reply != QtGui.QMessageBox.Yes:
                    self.DicomUploadFinishedMessage()
                    return False
            else:
                errMsg = "Multiple patients were found in provided DICOM study ["
                errMsg += str(self.svcDicom.patientCount) + "]. "
                errMsg += "Please provide DICOM study with exactly for one patient."
                self.Error(errMsg)
                self.DicomUploadFinishedMessage()
                return False

        if not self.svcDicom.hasOneStudy:
            errMsg = "Multiple or no DICOM study detected [" + str(self.svcDicom.studyCount) + "]. "
            errMsg += "Please provide data belonging to exactly one DICOM study."
            self.Error(errMsg)
            self.DicomUploadFinishedMessage()
            return False

        # Careful there is a burned in data
        if self.svcDicom.dicomData.hasBurnedInAnnotations():
            reply = QtGui.QMessageBox.question(
                self,
                "Question",
                gui.messages.QUE_BURNED_IN_ANNOTATIONS,
                QtGui.QMessageBox.Yes,
                QtGui.QMessageBox.No
            )
            if reply != QtGui.QMessageBox.Yes:
                self.DicomUploadFinishedMessage()
                return False

        # Check additional attributes for TreatmentPlan
        if dicomStudyType == "TreatmentPlan" and not self.svcDicom.plansHaveAllDoses:

            msg = ""
            if self.svcDicom.doseSumType == "PLAN":
                msg = "RT-Dose summation type is PLAN and "
                msg += "[" + str(self.svcDicom.planCount) + "] RTPLANs "
                msg += "and [" + str(self.svcDicom.doseCount) + "] RTDOSE objects detected.\n"
            elif self.svcDicom.doseSumType == "BEAM":
                msg = "RT-Dose summation type is BEAM and " 
                msg += "more beam numbers [" + str(self.svcDicom.planBeamNumber) + "] in RTPLANs "
                msg += "than RTDOSE objects [" + str(self.svcDicom.doseCount) + "] detected.\n"
                
            msg += "Do you want to continue?"
            reply = QtGui.QMessageBox.question(self, "Question", msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

            if reply != QtGui.QMessageBox.Yes:
                self.DicomUploadFinishedMessage()
                return False

        # Prepare DICOM study/series descriptions
        if self.performDicomStudyOverview(dicomStudyType):
            # Continue with DICOM mapping and de-identification
            self.performDicomMapping(dicomStudyType)
        else:
            self.DicomUploadFinishedMessage()        

    def DicomAnonymiseFinishedMessage(self, result):
        """
        """
        # Anonymisation was successful
        if result == "True":
            self.performDicomUpload()
        else:
            self.DicomUploadFinishedMessage()

    def DicomUploadFinishedMessage(self):
        """ Called after uploadDataThread finished, after the data were uploaded to the RadPlanBio server
        """
        # Enable upload button
        self.btnUpload.setEnabled(True)
        self.window().statusBar.showMessage("Ready")
