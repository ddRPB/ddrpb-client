#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# Standard
import os
import sys
import tempfile
import shutil
import time

# Pickle
if sys.version < "3":
    import cPickle as pickle
else:
    import _pickle as pickle

# Logging
import logging
import logging.config

# DICOM
if sys.version < "3":
    import dicom

    from dicom.dataset import Dataset
    from dicom.multival import MultiValue
    from dicom.sequence import Sequence
else:
    from pydicom import dicomio as dicom

    from pydicom.dataset import Dataset
    from pydicom.multival import MultiValue
    from pydicom.sequence import Sequence

# List
from blist import blist

# PyQt
from PyQt4 import QtCore

# Services
from services.AnonymisationService import AnonymisationService
from services.DicomDirectoryService import DicomDirectoryService

# GUI Messages
import gui.messages

# Context
from contexts.ConfigDetails import ConfigDetails

 ######  ######## ########  ##     ## ####  ######  ########
##    ## ##       ##     ## ##     ##  ##  ##    ## ##
##       ##       ##     ## ##     ##  ##  ##       ##
 ######  ######   ########  ##     ##  ##  ##       ######
      ## ##       ##   ##    ##   ##   ##  ##       ##
##    ## ##       ##    ##    ## ##    ##  ##    ## ##
 ######  ######## ##     ##    ###    ####  ######  ########


class DicomService(object):
    """Class which takes care about anonymisation and upload of chosen files
    """
 ######   #######  ##    ##  ######  ######## ########  ##     ##  ######  ######## 
##    ## ##     ## ###   ## ##    ##    ##    ##     ## ##     ## ##    ##    ##    
##       ##     ## ####  ## ##          ##    ##     ## ##     ## ##          ##    
##       ##     ## ## ## ##  ######     ##    ########  ##     ## ##          ##    
##       ##     ## ##  ####       ##    ##    ##   ##   ##     ## ##          ##    
##    ## ##     ## ##   ### ##    ##    ##    ##    ##  ##     ## ##    ##    ##    
 ######   #######  ##    ##  ######     ##    ##     ##  #######   ######     ##  

    def __init__(self):
        """Default constructor
        """
        self._logger = logging.getLogger(__name__)
        logging.config.fileConfig("logging.ini", disable_existing_loggers=False)

        self.StudyUID = ""
        self.li_UID = blist([])
        self.li_UID_anonym = blist([])
      
        # Init members
        self.dicomData = None
        self._patientID = ""
        self._patientCount = 0
        self._studyCount = 0
        self._instanceCount = 0
        self._doseSumType = ""
        self._summNumberOfBeams = 0
        self._planCount = 0
        self._doseCount = 0

        # Path to temporary folder for anonymised DICOM data
        self._directory_tmp = ""

########  ########   #######  ########  ######## ########  ######## #### ########  ######
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##    ##
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##
########  ########  ##     ## ########  ######   ########     ##     ##  ######    ######
##        ##   ##   ##     ## ##        ##       ##   ##      ##     ##  ##             ##
##        ##    ##  ##     ## ##        ##       ##    ##     ##     ##  ##       ##    ##
##        ##     ##  #######  ##        ######## ##     ##    ##    #### ########  ######

    @property
    def dataRoot(self):
        """DICOM data root Getter
        """
        return self.dicomData.dataRoot

    @property
    def dataDescriptorCount(self):
        """Number of DICOM data descriptors
        """
        return self.dicomData.descriptorSize

    @property
    def hasOnePatient(self):
        """Patient number validation Getter
        """
        return self._patientCount == 1

    @property
    def patientCount(self):
        """Number of patients
        """
        return self._patientCount

    @property
    def hasOneStudy(self):
        """Study number validation Getter
        """
        return self._studyCount == 1

    @property
    def studyCount(self):
        """Number of selected studies
        """
        return self._studyCount

    @property
    def hasUniqueInstances(self):
        """SOPInstanceUIDs number validation Getter
        """
        return self._instanceCount == self.dicomData.descriptorSize

    @property
    def instanceCount(self):
        """Instance number validation Getter
        """
        return self._instanceCount

    @property
    def plansHaveAllDoses(self):
        """Verify the completeness of treatment plan according to dose summation type
        """
        # FRACTION_SESSION = dose calculated for a single session (fraction) of a single Fraction Group within RT Plan
        # BEAM_SESSION = dose calculated for a single session (fraction) of one or more Beams within RT Plan
        # BRACHY_SESSION = dose calculated for a single session (fraction) of one or more Brachy Application Setups
        # within RT Plan
        # CONTROL_POINT = dose calculated for one or more Control Points within a Beam for a single fraction.

        # Dose calculated for entire delivery of all fraction groups of RT Plan
        if self._doseSumType == "PLAN":
            return self._planCount == self._doseCount
        # Dose calculated for entire delivery of 2 or more RT Plans
        elif self._doseSumType == "MULTI_PLAN":
            pass
        # Dose calculated for entire delivery of a single Fraction Group within RT Plan
        elif self._doseSumType == "FRACTION":
            pass
        # Dose calculated for entire delivery of one or more Beams within RT Plan
        elif self._doseSumType == "BEAM":
            return self._summNumberOfBeams <= self._doseCount or self._doseCount == 1
        # Dose calculated for entire delivery of one or more Brachy Application
        elif self._doseSumType == "BRACHY":
            pass 
        elif self._doseSumType == "FRACTION_SESSION":
            pass
        elif self._doseSumType == "BEAM_SESSION":
            pass
        elif self._doseSumType == "BRACHY_SESSION":
            pass
        elif self._doseSumType == "CONTROL_POINT":
            pass

        return True
      
    @property
    def doseSumType(self):
        """Dose summation type Getter
        """
        return self._doseSumType

    @property
    def planBeamNumber(self):
        """Summ of number of beams Getter
        """
        return self._summNumberOfBeams

    @property
    def planCount(self):
        """Number of detected plan instances Getter
        """
        return self._planCount

    @property
    def doseCount(self):
        """Number of detected dose instances Getter
        """
        return self._doseCount

    @property
    def directory_tmp(self):
        """Temporary DICOM study directory path Getter
        """
        return self._directory_tmp

    @directory_tmp.setter
    def directory_tmp(self, value):
        """Temporary DICOM study directory path Setter
        """
        self._directory_tmp = value

    @property
    def PatientID(self):
        """Pseudonymised patient ID (PID) Getter
        """
        return self._patientID

    @PatientID.setter
    def PatientID(self, value):
        """Pseudonymised patient ID (PID) Setter
        """
        self._patientID = value

##     ## ######## ######## ##     ##  #######  ########   ######
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ##
#### #### ##          ##    ##     ## ##     ## ##     ## ##
## ### ## ######      ##    ######### ##     ## ##     ##  ######
##     ## ##          ##    ##     ## ##     ## ##     ##       ##
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ##
##     ## ########    ##    ##     ##  #######  ########   ######

    def prepareDicomData(self, path, thread):
        """Prepare DICOM directory representation
        """
        thread.emit(QtCore.SIGNAL("log(QString)"), gui.messages.LOG_DICOM_SCAN)

        # Prepare the DICOM data service
        self.dicomData = DicomDirectoryService(path)
        result = self.dicomData.setup(thread)

        # Finished
        thread.emit(QtCore.SIGNAL("log(QString)"), gui.messages.LOG_DICOM_DATA)

        if result:
            thread.emit(QtCore.SIGNAL("finished(QString)"), "True")
        else:
            self._logger.error("Error when reading DICOM data.")
            thread.emit(QtCore.SIGNAL("finished(QString)"), "False")
        return None

    def analyseDicomStudyType(self, data, thread):
        """Basic analysis about conformity of provided DICOM data

        It detects most probable study type depending on DICOM modalities
        present in the study
        """
        if self.dicomData is None:
            return False

        thread.emit(QtCore.SIGNAL("log(QString)"), "Analysing provided DICOM Study...")
        self.dicomData.reload(thread)
        thread.emit(QtCore.SIGNAL("log(QString)"), "DICOM data dictionary reloaded...")
        thread.emit(QtCore.SIGNAL("log(QString)"), "Checking list of patients...")
        self._patientCount = self.dicomData.determineNumberOfPatientIDs()
        thread.emit(QtCore.SIGNAL("log(QString)"), "Checking list of studies...")
        self._studyCount = self.dicomData.determineNumberOfStudyUIDs()
        thread.emit(QtCore.SIGNAL("log(QString)"), "Checking list of instances...")
        self._instanceCount = self.dicomData.determineNumberOfInstanceUIDs()
        thread.emit(QtCore.SIGNAL("log(QString)"), "Checking list of modalities...")
        dicomStudyType = self.dicomData.determineStudyType()

        if dicomStudyType == "TreatmentPlan":
            if not self.checkTreatmentPlanData(thread):
                return False

            # Treatment plan data should share the same frame of reference
            thread.emit(QtCore.SIGNAL("log(QString)"), "Checking list of frame of references...")
            if not self.dicomData.isFrameOfReferenceUnique():
                errorMessage = "Provided DICOM treatment plan study has multiple frame of references. "
                errorMessage += "Please provide DICOM study which has the unique frame of reference "
                errorMessage += "for all DICOM-RT modalities."
                thread.emit(QtCore.SIGNAL("message(QString)"), errorMessage)
                return False
        elif dicomStudyType == "Contouring":
            if not self.checkContouringStudyData(thread):
                return False

            # Contouring study data should share the same frame of reference
            thread.emit(QtCore.SIGNAL("log(QString)"), "Checking list of frame of references...")
            if not self.dicomData.isFrameOfReferenceUnique():
                errorMessage = "Provided DICOM contouring study has multiple frame of references. "
                errorMessage += "Please provide DICOM study which has the unique frame of reference "
                errorMessage += "for all DICOM-RT modalities."
                thread.emit(QtCore.SIGNAL("message(QString)"), errorMessage)
                return False

        # Inform about the DICOM study type
        thread.emit(QtCore.SIGNAL("finished(QString)"), dicomStudyType)
        return None

    def getPatient(self):
        # Augment with Patient PID
        self.dicomData.patient.newId = self.PatientID

        if ConfigDetails().replacePatientNameWith == "pid":
            self.dicomData.patient.newName = self.PatientID
        elif ConfigDetails().replacePatientNameWith == "const":
            self.dicomData.patient.newName = ConfigDetails().constPatientName

        return self.dicomData.patient

    def getStudy(self):
        # I am giving back whole data root because also series out of the main
        # selected DICOM study have to be considered
        return self.dicomData.dataRoot

    def getReportSerieText(self):
        """Get text from all structured series documents
        """
        text = ""
        for study in self.dicomData.dataRoot.children:
            for serie in study.children:
                if serie.isChecked and serie.modality == "SR":
                    if text == "":
                        text = serie.approvedReportText
                    else:
                        text += "\n\n" + serie.approvedReportText
        
        # We usually store this into one textarea, OC has a size limit there
        if len(text) > 4000:
            text = text[:4000]
            self._logger.error("Shortening complete report text to 4000 characters in order to fit into OC text-area.")
        
        return text

    def getRoiNameDict(self):
        """Get dictionary of ROI names in DICOM study

        Only applicable when the study is treatment plan or contouring study with RTSTRUCT seires
        """
        return self.dicomData.ROIs

    def checkTreatmentPlanData(self, thread=None):
        """Checks the completeness of DICOM study data (treatment plan)
        """
        modalities = self.dicomData.getModalities()

        if "CT" in modalities and \
           "RTSTRUCT" in modalities and \
           "RTPLAN" in modalities and \
           "RTDOSE" in modalities:

            ct_dicomData = self.dicomData.belongingTo("Modality", "CT")
            li_SOPInstanceUID_CT = []
            for elem in ct_dicomData:
                li_SOPInstanceUID_CT.append(elem["SOPInstanceUID"])

            # Check how many RTSTRUCT is in the folder
            rtstruct_dicomData = self.dicomData.belongingTo("Modality", "RTSTRUCT")
            if len(rtstruct_dicomData) > 1:
                thread.emit(QtCore.SIGNAL("message(QString)"), gui.messages.ERR_MULTIPLE_RTSTRUCT)
                return False

            rtstruct_dicomData = rtstruct_dicomData[0]

            if "FrameOfReferenceUID" not in rtstruct_dicomData:
                msg = "Structure set is not defined on top of CT data. "
                msg += "Upload of inconsistent treatment plan is not possible!"
                thread.emit(QtCore.SIGNAL("message(QString)"), msg)
                return False

            # Check whether all CT images to where RTSTRUCT refers are provided
            missingCT = False
            missingCT_UID = []
            for elem in rtstruct_dicomData["ContourImageSequence"]:
                if elem not in li_SOPInstanceUID_CT:
                    missingCT = True
                    missingCT_UID.append(elem)
            if missingCT:
                msg = "Structure set (RTSTRUCT) is referencing CT images which are not within the provided data set: "
                msg += str(missingCT_UID)
                thread.emit(QtCore.SIGNAL("message(QString)"), msg)
                return False

            rtplan_dicomData = self.dicomData.belongingTo("Modality", "RTPLAN")

            # SOP instance UID of RTSTRUCT
            rtstruct_SOPInstanceUID = rtstruct_dicomData["SOPInstanceUID"]
            
            # Collect SOP instance UID from RTPLAN (one or more)
            rtplan_SOPInstanceUID = []
            # Each plan should refer max 1 RTSTRUCT
            planRefStructUID = []

            for elem in rtplan_dicomData:
                rtplan_SOPInstanceUID.append(elem["SOPInstanceUID"])
                planRefStructUID.append(elem["ReferencedSOPInstanceUID_RTSTRUCT"])
            
            # Collect SOP instance UID from RTDOSE referencing to RTPLAN
            # Collect SOP instance UID from RTDOSE referencing to RTSTRUCT
            rtdose_dicomData = self.dicomData.belongingTo("Modality", "RTDOSE")
            self._doseCount = len(rtdose_dicomData)

            doseRefPlanUID = []
            doseRefStructUID = []
            for elem in rtdose_dicomData:
                doseRefPlanUID.append(elem["ReferencedSOPInstanceUID_RTPLAN"])
                # Is not mandatory so it does not have to be there
                if "ReferencedSOPInstanceUID_RTSTRUCT" in elem:
                    doseRefStructUID.append(elem["ReferencedSOPInstanceUID_RTSTRUCT"])
            
            # Remove duplicate values
            doseRefStructUID = list(set(doseRefStructUID))
            doseRefPlanUID = list(set(doseRefPlanUID))

            # Check whether the all RTPLANs referenced from RTDOSEs exists
            for refRtPlanUID in doseRefPlanUID:
                if refRtPlanUID not in rtplan_SOPInstanceUID:
                    msg = "One of RTDOSE is referencing to unknown RTPLAN. "
                    msg += "Upload of inconsistent treatment plan is not possible!"
                    thread.emit(QtCore.SIGNAL("message(QString)"), msg)
                    return False            

            # Check whether the RTSTRUCT referenced from RTDOSEs exists
            if not ConfigDetails().autoRTStructRef:
                for refRtStructUID in doseRefStructUID:
                    if refRtStructUID != rtstruct_SOPInstanceUID:
                        msg = "One of RTDOSE is referencing to unknown RTSTRUCT. "
                        msg += "Upload of inconsistent treatment plan is not possible!"
                        thread.emit(QtCore.SIGNAL("message(QString)"), msg)
                        return False

            # How many RTPLAN and RTDOSE SOP instances have been detected
            if rtplan_dicomData is not None:
                self._planCount = len(rtplan_dicomData)
            if rtdose_dicomData is not None:
                self._doseCount = len(rtdose_dicomData)

            # RTDOSE DoseSummationType should be uniform across treatment planning data
            self._summNumberOfBeams = 0
            if len(self.dicomData.unique("DoseSummationType")) == 1:
                self._doseSumType = self.dicomData.unique("DoseSummationType")[0]

                if self._doseSumType == "BEAM":
                    for i in xrange(self._planCount):
                        # Summ number of beams from each plan
                        if "BeamNumbers" in rtplan_dicomData[i]:
                            self._summNumberOfBeams += rtplan_dicomData[i]["BeamNumbers"]

            # Check whether the RTSTRUCT is referenced from all RTPLANs
            if not ConfigDetails().autoRTStructRef:
                for refRtStructUID in planRefStructUID:
                    if refRtStructUID != rtstruct_SOPInstanceUID:
                        msg = "One of RTPLAN is referencing to unknown RTSTRUCT. "
                        msg += "Upload of inconsistent treatment plan is not possible!"
                        thread.emit(QtCore.SIGNAL("message(QString)"), msg)
                        return False

            return True

        else:
            missingModality = ""
            li_ModalityFull = ["RTSTRUCT", "RTPLAN", "CT", "RTDOSE"]
            for elem in li_ModalityFull:
                if elem not in modalities: 
                    missingModality = elem

            msg = "Treatment plan data is not complete. "
            msg += missingModality + " modality is missing. "
            msg += "Upload of none complete treatment plan is not possible. "
            msg += "Please correct your treatment plan and try it again."
            thread.emit(QtCore.SIGNAL("message(QString)"), msg)
            
            return False

    def checkContouringStudyData(self, thread=None):
        """Checks the completeness of DICOM study data (contouring study)
        """
        modalities = self.dicomData.getModalities()

        if "CT" in modalities and \
           "RTSTRUCT" in modalities:

            ct_dicomData = self.dicomData.belongingTo("Modality", "CT")
            li_SOPInstanceUID_CT = []
            for elem in ct_dicomData:
                li_SOPInstanceUID_CT.append(elem["SOPInstanceUID"])

            # Check how many RTSTRUCT is in the folder
            rtstruct_dicomData = self.dicomData.belongingTo("Modality", "RTSTRUCT")
            if len(rtstruct_dicomData) > 1:
                thread.emit(QtCore.SIGNAL("message(QString)"), gui.messages.ERR_MULTIPLE_RTSTRUCT)
                return False

            rtstruct_dicomData = rtstruct_dicomData[0]

            if "FrameOfReferenceUID" not in rtstruct_dicomData:
                msg = "Structure set is not defined on top of CT data. "
                msg += "Upload of inconsistent contouring study is not possible!"
                thread.emit(QtCore.SIGNAL("message(QString)"), msg)
                return False

            # Check whether all CT images to where RTSTRUCT refers are provided
            missingCT = False
            missingCT_UID = []
            for elem in rtstruct_dicomData["ContourImageSequence"]:
                if elem not in li_SOPInstanceUID_CT:
                    missingCT = True
                    missingCT_UID.append(elem)
            if missingCT:
                msg = "Structure set (RTSTRUCT) is referencing CT images which are not within the provided data set: "
                msg += str(missingCT_UID)
                thread.emit(QtCore.SIGNAL("message(QString)"), msg)
                return False

            return True

        else:
            missingModality = ""
            li_ModalityFull = ["RTSTRUCT", "CT"]
            for elem in li_ModalityFull:
                if elem not in modalities:
                    missingModality = elem

            msg = "Contouring study data is not complete. "
            msg += missingModality + " modality is missing. "
            msg += "Upload of none complete contouring study is not possible. "
            msg += "Please correct your contouring study and try it again."
            thread.emit(QtCore.SIGNAL("message(QString)"), msg)

            return False

    def anonymiseDicomData(self, data, thread=None):
        """Anonymise DICOM data, use new Patient ID and DICOM ROI mapping

        Also checks if plan is complete and anonymises the plan.
        """
        patient = data[0]
        dicomDataRoot = data[1]
        mappingRoiDic = data[2]

        thread.emit(QtCore.SIGNAL("taskUpdated"), 0)
        thread.emit(QtCore.SIGNAL("log(QString)"), "DICOM study pseudonymisation...")

        # Anonymize plan in temporary directory (and use the ROI mapping)
        self._directory_tmp = tempfile.mkdtemp()
        svcAnonymise = AnonymisationService(self.directory_tmp, patient, dicomDataRoot, mappingRoiDic)

        # Provide optional setting for anonymisation (use PID)
        svcAnonymise.GeneratePatientID = False
        svcAnonymise.PatientID = self.PatientID
        svcAnonymise.makeAnonymous(thread)

        thread.emit(QtCore.SIGNAL("taskUpdated"), 0)

        self.StudyUID = svcAnonymise.StudyInstanceUID
        self.li_UID_anonym = svcAnonymise.li_UID_anonym
        self.li_UID = svcAnonymise.li_UID

        if not self.StudyUID:
            shutil.rmtree(self.directory_tmp)
            thread.emit(QtCore.SIGNAL('message(QString)'), svcAnonymise.errorMessage)
            thread.emit(QtCore.SIGNAL('finished(QString)'), 'False')
            return None

        thread.emit(QtCore.SIGNAL('finished(QString)'), 'True')

    def uploadDicomData(self, data, thread):
        """Sends the files to the server
        """
        result = "True"
        resultLogMessage = "Upload finished..."

        # Logging message to UI
        thread.emit(QtCore.SIGNAL("log(QString)"), "DICOM study upload...")

        # Upload files from temporary directory
        # obtain and sort filenames
        files = os.listdir(self.directory_tmp)
        files.sort()

        # Upload each file separately (due to memory conservation)
        sourceSize = len(files)
        uploaded = 0
        for i in xrange(len(files)):
            dict_data = {}
            try:
                # Load i-th file, append to dictionary and close
                filepath = os.path.join(self.directory_tmp, files[i])
                f = open(filepath, 'rb')
                dict_data[files[i]] = f.read()
                f.close()
                # for the last file set FINISH=True, otherwise False
                if i < len(files) - 1:
                    dict_data["FINISH"] = False
                else:
                    thread.emit(QtCore.SIGNAL("log(QString)"), "Last file sent...")
                    dict_data["FINISH"] = True

                self._logger.info("Uploading: " + files[i] + " Last file: " + str(dict_data["FINISH"]))

                # Save as string with pickle (https allows for sending strings only)
                dict_data = pickle.dumps(dict_data, protocol=pickle.HIGHEST_PROTOCOL)

                # Sent string to server
                svcHttp = data
                status = svcHttp.uploadDicomData(dict_data)
                self._logger.info(status)

                # Error handling concerning status
                if status == "URL":
                    result = "False"
                    resultLogMessage = "Upload failed!"
                    thread.emit(QtCore.SIGNAL("message(QString)"), "URL unknown.")
                    if os.path.exists(self.directory_tmp):
                        shutil.rmtree(self.directory_tmp)
                    break
                elif status == "datalength":
                    result = "False"
                    resultLogMessage = "Upload failed!"
                    thread.emit(QtCore.SIGNAL("message(QString)"), "Data length does not agree.")
                    if os.path.exists(self.directory_tmp):
                        shutil.rmtree(self.directory_tmp)
                    break
                elif status == "PACS":
                    result = "False"
                    resultLogMessage = "Upload failed!"
                    thread.emit(QtCore.SIGNAL("message(QString)"), "PACS cannot import the DICOM data.")
                    if os.path.exists(self.directory_tmp):
                        shutil.rmtree(self.directory_tmp)
                    break
                elif status:
                    pass
                else:
                    result = "False"
                    resultLogMessage = "Upload failed!"
                    thread.emit(QtCore.SIGNAL("message(QString)"), "Unknown error during data upload.")
                    if os.path.exists(self.directory_tmp):
                        shutil.rmtree(self.directory_tmp)
                    break
            except Exception as err:
               result = "False"
               resultLogMessage = "Upload failed!"
               self._logger.error(err)
               thread.emit(QtCore.SIGNAL("message(QString)"), "Cannot read the data, cannot send them.")
               if os.path.exists(self.directory_tmp):
                   shutil.rmtree(self.directory_tmp)
               break

            # Report progress
            if thread:
                uploaded += 1
                thread.emit(QtCore.SIGNAL("taskUpdated"), [uploaded, sourceSize])

        # Remove temporary directory if still exists
        if os.path.exists(self.directory_tmp):
            shutil.rmtree(self.directory_tmp)

        thread.emit(QtCore.SIGNAL('log(QString)'), resultLogMessage)
        thread.emit(QtCore.SIGNAL('finished(QString)'), result)

    def verifyUploadedDicomData(self, data, thread):
        """Verify availability of sent files in research PACS
        """
        success = True

        dicomDataRoot = data[0]
        svcHttp = data[1]

        sourceSize = 0
        verified = 0
        for study in dicomDataRoot.children:
            for series in study.children:
                if series.isChecked:
                    sourceSize += series.size

        # Consider all selected series from dataRoot
        for study in dicomDataRoot.children:

            for series in study.children:
                if series.isChecked:
                    # New series instance UID
                    seriesInstanceUID = self.li_UID_anonym[self.li_UID.index(series.suid)]

                    # Retrieve series details from research PACS
                    dicomVerifyImportRepeat = 300  # repeat the verification multiple times
                    dicomVerifyImportSleep = 1  # wait a second between repeats
                    seriesImportSuccess = True
                    importedFiles = 0

                    # There is a queue for import so it may take some time until the data are shown in PACS
                    for i in range(0, dicomVerifyImportRepeat):
                        importedSeries = svcHttp.getDicomSeriesData(self._patientID, self.StudyUID, seriesInstanceUID)
                        if importedSeries is None or importedSeries.size != series.size:
                            seriesImportSuccess = False
                            time.sleep(dicomVerifyImportSleep)
                        else:
                            seriesImportSuccess = True
                            importedFiles += importedSeries.size
                            break

                    if not seriesImportSuccess:
                        thread.emit(QtCore.SIGNAL("log(QString)"),
                                    "DICOM Series: " + series.description + " verification failed!")
                        thread.emit(QtCore.SIGNAL("log(QString)"),
                                    "Sent: " + str(series.size) + "; Imported: " + str(importedFiles))

                    success = success and seriesImportSuccess

                    if thread:
                        verified += importedFiles
                        thread.emit(QtCore.SIGNAL("taskUpdated"), [verified, sourceSize])

        if success:
            thread.emit(QtCore.SIGNAL("log(QString)"),
                        "DICOM data import [" + str(verified) + "/" + str(sourceSize) + "] successfully finished!")
            thread.emit(QtCore.SIGNAL('message(QString)'), "Data transfer was successful!")
            return True
        else:
            thread.emit(QtCore.SIGNAL("message(QString)"), "PACS data import failed.")
            return False

    def storeInstances(self, data, thread):
        """Stores DICOM instances
        """
        result = "True"
        resultLogMessage = "Upload finished..."

        # Logging message to UI
        thread.emit(QtCore.SIGNAL("log(QString)"), "DICOM study upload...")

        svcHttp = data

        # Upload files from temporary directory
        # obtain and sort filenames
        files = os.listdir(self.directory_tmp)
        files.sort()

        # Upload each file separately (due to memory conservation)
        sourceSize = len(files)
        uploaded = 0

        for i in xrange(len(files)):

            try:
                if i == len(files) - 1:
                    thread.emit(QtCore.SIGNAL("log(QString)"), "Last file sent...")

                # Load i-th file for sending into list
                encoded_datasets = list()
                filepath = os.path.join(self.directory_tmp, files[i])
                with open(filepath, 'rb') as dataset:
                    encoded_ds = dataset.read()
                    encoded_datasets.append(encoded_ds)

                svcHttp.httpPostMultipartApplicationDicom(encoded_datasets)

            except Exception as err:
                result = "False"
                resultLogMessage = "Upload failed!"
                self._logger.error(err)
                thread.emit(QtCore.SIGNAL("message(QString)"), "Cannot read the data, cannot send them.")
                if os.path.exists(self.directory_tmp):
                    shutil.rmtree(self.directory_tmp)
                break

            # Report progress
            if thread:
                uploaded += 1
                thread.emit(QtCore.SIGNAL("taskUpdated"), [uploaded, sourceSize])

        # Remove temporary directory
        if os.path.exists(self.directory_tmp):
            shutil.rmtree(self.directory_tmp)

        thread.emit(QtCore.SIGNAL('log(QString)'), resultLogMessage)
        thread.emit(QtCore.SIGNAL('finished(QString)'), result)
