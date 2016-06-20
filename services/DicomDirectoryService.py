#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# Standard
import os

# Logging
import logging
import logging.config

# PyQt - for running in a separate thread
from PyQt4 import QtCore

# DICOM
import dicom

# Domain
from domain.Node import Node

# DICOM domain
from dcm.DicomPatient import DicomPatient
from dcm.DicomStudy import DicomStudy
from dcm.DicomSeries import DicomSeries

# DICOM De-identification
from dicomdeident.DeidentConfig import DeidentConfig

# Context
from contexts.ConfigDetails import ConfigDetails

 ######  ######## ########  ##     ## ####  ######  ########
##    ## ##       ##     ## ##     ##  ##  ##    ## ##
##       ##       ##     ## ##     ##  ##  ##       ##
 ######  ######   ########  ##     ##  ##  ##       ######
      ## ##       ##   ##    ##   ##   ##  ##       ##
##    ## ##       ##    ##    ## ##    ##  ##    ## ##
 ######  ######## ##     ##    ###    ####  ######  ########


class DicomDirectoryService:
    """DICOM directory lookup service
    This service is responsible for working with DICOM files. 
    It provides hierarchical access to DICOM elements within the files.

    directory: source DICOM data directory
    """

    def __init__(self, directory):
        """Default constructor
        """
        # Setup logger - use logging config file
        self._logger = logging.getLogger(__name__)
        logging.config.fileConfig("logging.ini", disable_existing_loggers=False)

        # Path to source DICOM directory
        self._directory = directory
        # List of DICOM files in a source directory
        self._files = []

        # The list of descriptors describing DICOM files (used for search)
        self.dicomDescriptors = []

        # Data root holds hierarchy structure of underlying DICOM data
        self._rootNode = None
        # DICOM studies detected in the source data
        self._studies = []
        # DICOM series detected in the source data
        self._series = []

        # Initialised file list
        self._loadFileNames()

        # Selected patient, study, rois which will be uploaded
        self._selectedStudy = None
        self._rois = {} # Dictionary (key = ROINumber, value = ROIName)

        self._patient = None

        self._burnedInAnnotations = False

        # Configuration of deidentification
        self._deidentConfig = DeidentConfig()

        # Searching results over DICOM tree (have to be members because searching function is recursive)
        # TODO: refactor this and make it work more transparently
        self.dataValue = ""
        self.dataList = []

        # Parsing errors
        self._errors = []

########  ########   #######  ########  ######## ########  ######## #### ########  ######
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##    ##
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##
########  ########  ##     ## ########  ######   ########     ##     ##  ######    ######
##        ##   ##   ##     ## ##        ##       ##   ##      ##     ##  ##             ##
##        ##    ##  ##     ## ##        ##       ##    ##     ##     ##  ##       ##    ##
##        ##     ##  #######  ##        ######## ##     ##    ##    #### ########  ######

    @property
    def isReadable(self):
        """Verify whether the source directory path is readable
        """
        return os.access(self._directory, os.R_OK)

    @property
    def size(self):
        """Get the number of files in source directory
        """
        if self._files is not None:
            return len(self._files)
        else:
            return 0

    @property
    def dataRoot(self):
        """DICOM data root Getter
        All detected DICOM studies will be served as children of root node
        """
        if self._rootNode is not None:
            return self._rootNode
        else:
            self._rootNode = Node("DICOM data root node")
            for study in self._studies:
                self._rootNode.addChild(study)

        return self._rootNode

    @property
    def patient(self):
        """DICOM Patient Getter
        """
        if self._patient is None:
            patientIdList = self.unique("PatientID")
            if len(patientIdList) == 1:
                self._patient = DicomPatient()
                self._patient.id = patientIdList[0]
                if len(self.unique("PatientName")) == 1:
                    self._patient.name = self.unique("PatientName")[0]
                if len(self.unique("PatientSex")) == 1:
                    self._patient.gender = self.unique("PatientSex")[0]
                if len(self.unique("PatientBirthDate")) == 1:
                    self._patient.dob = self.unique("PatientBirthDate")[0]

                self._patient.newName = self._deidentConfig.ReplacePatientNameWith
                if ConfigDetails().retainPatientCharacteristicsOption:
                    self._patient.newGender = self._patient.gender
                else:
                    self._patient.newGender = self._deidentConfig.ReplaceDefaultWith
                self._patient.newDob = self._deidentConfig.ReplaceDateWith
            elif len(patientIdList) > 1:
                # More patients use the first which is detected
                self._patient = DicomPatient()
                self._patient.id = patientIdList[0]
                self._patient.name = self.unique("PatientName")[0]
                self._patient.gender = self.unique("PatientSex")[0]
                self._patient.dob = self.unique("PatientBirthDate")[0]

                self._patient.newName = self._deidentConfig.ReplacePatientNameWith
                if ConfigDetails().retainPatientCharacteristicsOption:
                    self._patient.newGender = self._patient.gender
                else:
                    self._patient.newGender = self._deidentConfig.ReplaceDefaultWith
                self._patient.newDob = self._deidentConfig.ReplaceDateWith

        return self._patient

    @property
    def study(self):
        """DICOM Study Getter
        Only one DICOM study (main - selected) is considered for further work
        """
        if self._selectedStudy is None:
            if self._rootNode is not None:
                for study in self._rootNode.children:
                    if study.isChecked:
                        self._selectedStudy = study
                        break

        return self._selectedStudy

    @property
    def ROIs(self):
        """DICOM RTSTRUCT Region Of Interest Dictionary Getter
        """
        return self._rois

##     ## ######## ######## ##     ##  #######  ########   ######
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ##
#### #### ##          ##    ##     ## ##     ## ##     ## ##
## ### ## ######      ##    ######### ##     ## ##     ##  ######
##     ## ##          ##    ##     ## ##     ## ##     ##       ##
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ##
##     ## ########    ##    ##     ##  #######  ########   ######

    def setup(self, thread=None):
        """Setup the dicomDirectory to make it possible to lookup what DICOM data have been provided
        DICOM study descriptor dictionary for easier search
        """
        self._errors = []

        # File reading progress checking
        processed = 0

        # Gather file DICOM study data and put into DicomStudies
        tempStudies = {}
        # Gather file DICOM series data and put into DicomSeries
        tempSeries = {}

        # Only process DICOM files
        for f in self._files:
            if self._invalidFile(f):
                continue

            try:
                descriptor = None
                dcmFile = dicom.read_file(f, force=True)
                self._logger.debug("Reading DICOM file: " + f)

                # Construct DICOM file descriptor
                descriptor = {
                    "Filename": f
                }

                # PatientID
                if "PatientID" in dcmFile:
                    descriptor["PatientID"] = dcmFile.PatientID
                else:
                    self._logger.error("PatientID tag is missing in " + f + "!")
                    self._errors.append("PatientID tag is missing in " + f + "!")

                # StudyInstanceUID
                if "StudyInstanceUID" in dcmFile:
                    studyInstanceUid = dcmFile.StudyInstanceUID
                    descriptor["StudyInstanceUID"] = dcmFile.StudyInstanceUID

                    # Get SUID and prepare study objects
                    if studyInstanceUid not in tempStudies:
                        tempStudies[str(studyInstanceUid)] = DicomStudy(studyInstanceUid)
                else:
                    self._logger.error("StudyInstanceUID tag is missing in " + f + "!")
                    self._errors.append("StudyInstanceUID tag is missing in " + f + "!")

                # Is it a DICOM serie (SeriesInstanceUID)
                if "SeriesInstanceUID" in dcmFile:
                    seriesInstanceUID = dcmFile.SeriesInstanceUID
                    descriptor["SeriesInstanceUID"] = dcmFile.SeriesInstanceUID

                    # Get SUID and register the file with an existing or new series object
                    if seriesInstanceUID not in tempSeries:
                        tempSeries[str(seriesInstanceUID)] = DicomSeries(seriesInstanceUID)

                    # Lower memory consumption by saving only paths
                    tempSeries[str(seriesInstanceUID)].appendFile(f)
                else:
                    self._logger.error("SeriesInstanceUID tag is missing in " + f + "!")
                    self._errors.append("SeriesInstanceUID tag is missing in " + f + "!")


                # SOPInstanceUID
                if "SOPInstanceUID" in dcmFile:
                    descriptor["SOPInstanceUID"] = dcmFile.SOPInstanceUID
                else:
                    self._logger.error("SOPInstanceUID tag is missing in " + f + "!")
                    self._errors.append("SOPInstanceUID tag is missing in " + f + "!")

                # PatientName in descriptor
                if "PatientName" in dcmFile:
                    descriptor["PatientName"] = dcmFile.PatientName
                else:
                    self._logger.info("PatientName tag is missing in " + f + ". Replacing with default: " + self._deidentConfig.ReplacePatientNameWith + ".")
                    descriptor["PatientName"] = self._deidentConfig.ReplacePatientNameWith

                # PatientBirthDate in descriptor
                if "PatientBirthDate" in dcmFile:
                    descriptor["PatientBirthDate"] = dcmFile.PatientBirthDate
                else:
                    self._logger.info("PatientBirthDate tag is missing in " + f + ". Replacing with default: " + self._deidentConfig.ReplaceDateWith + ".")
                    descriptor["PatientBirthDate"] = self._deidentConfig.ReplaceDateWith

                # PatientSex in descriptor
                if "PatientSex" in dcmFile:
                    descriptor["PatientSex"] = dcmFile.PatientSex
                else:
                    self._logger.info("PatientSex tag is missing in " + f + ". Replacing with default: O.")
                    descriptor["PatientSex"] = "O"  # Other, if not present

                # Save StudyDescription in descriptor
                if "StudyDescription" in dcmFile:
                    descriptor["StudyDescription"] = dcmFile.StudyDescription
                    tempStudies[str(studyInstanceUid)].name = dcmFile.StudyDescription
                    tempStudies[str(studyInstanceUid)].description = dcmFile.StudyDescription
                    if "StudyDate" in dcmFile:
                        tempStudies[str(studyInstanceUid)].date = dcmFile.StudyDate

                # Save IntanceNumber in descriptor
                if "InstanceNumber" in dcmFile:
                    descriptor["InstanceNumber"] = dcmFile.InstanceNumber
                else:
                    descriptor["InstanceNumber"] = 0

                # Save PatientsAge in descriptor
                if "PatientsAge" in dcmFile:
                    descriptor["PatientsAge"] = dcmFile.PatientsAge
                else:
                    descriptor["PatientsAge"] = "OOOY"

                # Save FrameOfReferenceUID in descriptor
                self.getValue(dcmFile, "Frame of Reference UID")
                if self.dataValue != "":
                    descriptor["FrameOfReferenceUID"] = self.dataValue

                self.dataValue = ""
                self.dataList = []

                # Save ReferencedSOPInstanceUID_RTPLAN in descriptor
                self.getValue(dcmFile, "Referenced SOP Instance UID", reference="Referenced Structure Set Sequence")
                if self.dataValue != "":
                    descriptor["ReferencedSOPInstanceUID_RTSTRUCT"] = self.dataValue

                self.dataValue = ""
                self.dataList = []

                # Save ReferencedSOPInstanceUID_RTPLAN in descriptor
                self.getValue(dcmFile,  "Referenced SOP Instance UID", reference="Referenced RT Plan Sequence")
                if self.dataValue != "":
                    descriptor["ReferencedSOPInstanceUID_RTPLAN"] = self.dataValue

                self.dataValue = ""
                self.dataList = []

                # Save Countour Image Sequence
                self.getValue(dcmFile,  "Contour Image Sequence")
                if self.dataList  != []:
                    descriptor["ContourImageSequence"] = list(set(self.dataList))

                self.dataValue = ""
                self.dataList = []

                # According to modality save
                if "Modality" in dcmFile:
                    descriptor["Modality"] = dcmFile.Modality,

                    # For RTPLAN
                    if dcmFile.Modality == "RTPLAN":

                        # Save RTPlanLabel in descriptor
                        if "RTPlanLabel" in dcmFile:
                            descriptor["RTPlanLabel"] = dcmFile.RTPlanLabel

                        # Save BeamNumbers
                        if "Beams" in dcmFile:
                            descriptor["BeamNumbers"] = len(dcmFile.Beams)

                        # Save RadiationType
                        self.getValue(dcmFile, "Radiation Type")
                        if self.dataValue != "":
                            descriptor["RadiationType"] = self.dataValue

                        self.dataValue = ""
                        self.dataList = []

                    # Save DoseSummationType for RTDOSE
                    elif dcmFile.Modality == "RTDOSE" and \
                        "DoseSummationType" in dcmFile:
                        descriptor["DoseSummationType"] = dcmFile.DoseSummationType

                    # For RTSTRUCT prepare ROIs dictionary
                    elif dcmFile.Modality == "RTSTRUCT":
                        # Oncentra MasterPlan case exports RTSTRUCT with this point we should store this info
                        if "ReferencedFrameOfReferenceSequence" in dcmFile:
                            for element in dcmFile.ReferencedFrameOfReferenceSequence:
                                if "FrameOfReferenceRelationshipSequence" in element:
                                    for secElem in element.FrameOfReferenceRelationshipSequence:
                                        if "FrameOfReferenceTransformationType" in secElem:
                                            descriptor["TreatmentPlanningReferencePoint"] = "Yes"
                                            break

                        for element in dcmFile:
                            if element.VR == "SQ":
                                if element.name == "Structure Set ROI Sequence":
                                    for subElem in element:
                                        self._rois[subElem.ROINumber] = [subElem.ROIName]

                        self._logger.info("Number of RTSTRUCT ROIs: " + str(len(self._rois)))

            except Exception, err:
                msg = "Unexpected error during DICOM data parsing:" + f + "!"
                self._logger.exception(msg)
                self._errors.append(msg)

            # Add descriptor for DICOM file
            if descriptor is not None:
                self.dicomDescriptors.append(descriptor)

            # Progress
            if thread:
                processed += 1
                thread.emit(QtCore.SIGNAL("taskUpdated"), [processed, self.size])

        # Make a series list and sort, so that the order is deterministic
        tempSeries = tempSeries.values()
        tempSeries.sort(key=lambda x: x.suid)

        # Prepare real series objects and put it into property
        for i in range(len(tempSeries)):
            try:
                tempSeries[i]._finish()
                self._series.append(tempSeries[i])
            except Exception:
                # Finish was not successful but I do not want to
                # skip the serie (probably report-like file without pixels)
                self._series.append(tempSeries[i])

        # Assign series to temp studies
        for series in self._series:
            tempStudies[series.studyInstanceUid].addChild(series)

        # Prepare real studies objects
        tempStudies = tempStudies.values()
        tempStudies.sort(key=lambda x: x.suid)
        for i in range(len(tempStudies)):
            self._studies.append(tempStudies[i])

        # Report reading errors
        resultError = ""
        for errMsg in self._errors:
            resultError = resultError + errMsg + "\n"
        if resultError != "" and thread:
            if len(self._errors) > 40:
                resultError = "Cannot process DICOM data, because there are too many parsing errors. Please check the log file for detailed information."
            thread.emit(QtCore.SIGNAL("message(QString)"), resultError)

        # Successful reading of data or not
        if resultError != "":
            return False
        else:
            return True

    def reload(self, thread=None):
        """Setup the dicomDirectory to make it possible to lookup what DICOM data have been provided
        DICOM study descriptor (on top of selected study) for easier search
        """
        self._errors = []

        # Reset lookup variables
        self._rois = {}  # Dictionary (key = ROINumber, value = ROIName)
        self.dicomDescriptors = []

        # Searching results over DICOM tree (have to be members because searching function is recursive)
        self._burnedInAnnotations = False
        self.dataValue = ""
        self.dataList = []

        # File reading progress checking
        processed = 0

        # Build descriptors for elements in selected study
        # and also for selected series (even if there are not in selected study)
        # for such series the descriptor will be holding selected study instance UID
        # this is important to pass the DICOM study upload consistency check
        if self._rootNode is not None:
            for study in self._rootNode.children:
                for serie in study.children:
                    # Even if series is not in a selected study
                    if serie.isChecked:
                        for f in serie.files:
                            try:
                                dcmFile = dicom.read_file(f, force=True)

                                # Determine whether there is any data with burned in annotations
                                if not self._burnedInAnnotations:
                                    if "BurnedInAnnotation" in dcmFile:
                                        if (str(dcmFile.BurnedInAnnotation)).upper() == "TRUE":
                                            self._burnedInAnnotations = True
                                            self._logger.info("Burned in annotation found in: " + f)

                                # Construct DICOM file descriptor
                                descriptor = {
                                    "PatientID": dcmFile.PatientID,
                                    "SeriesInstanceUID": dcmFile.SeriesInstanceUID,
                                    "SOPInstanceUID": dcmFile.SOPInstanceUID,
                                    "Modality": dcmFile.Modality,
                                    "Filename": dcmFile.filename
                                }

                                # PatientName in descriptor
                                if "PatientName" in dcmFile:
                                    descriptor["PatientName"] = dcmFile.PatientName
                                else:
                                    descriptor["PatientName"] = self._deidentConfig.ReplacePatientNameWith

                                # PatientBirthDate in descriptor
                                if "PatientBirthDate" in dcmFile:
                                    descriptor["PatientBirthDate"] = dcmFile.PatientBirthDate
                                else:
                                    descriptor["PatientBirthDate"] = self._deidentConfig.ReplaceDateWith

                                # PatientSex in descriptor
                                if "PatientSex" in dcmFile:
                                    descriptor["PatientSex"] = dcmFile.PatientSex
                                else:
                                    descriptor["PatientSex"] = "O" # Other, if not present

                                # StudyInctanceUID in descriptor
                                # Depends on the fact that the file belong to series in selected study
                                if "StudyInstanceUID" in dcmFile:
                                    if dcmFile.StudyInstanceUID != self.study.suid:
                                        dcmFile.StudyInstanceUID = self.study.suid
                                    descriptor["StudyInstanceUID"] = self.study.suid

                                # StudyDescription in descriptor
                                # Depends on the fact that the file belong to series in selected study
                                if "StudyDescription" in dcmFile:
                                    if dcmFile.StudyDescription != self.study.description:
                                        dcmFile.StudyDescription = self.study.description
                                    descriptor["StudyDescription"] = self.study.description

                                # Save InstanceNumber in descriptor
                                if "InstanceNumber" in dcmFile:
                                    descriptor["InstanceNumber"] = dcmFile.InstanceNumber
                                else:
                                    descriptor["InstanceNumber"] = 0

                                # Save PatientsAge in descriptor
                                if "PatientsAge" in dcmFile:
                                    descriptor["PatientsAge"] = dcmFile.PatientsAge
                                else:
                                    descriptor["PatientsAge"] = "OOOY"

                                # Save FrameOfReferenceUID in descriptor
                                self.getValue(dcmFile, "Frame of Reference UID")
                                if self.dataValue != "":
                                    descriptor["FrameOfReferenceUID"] = self.dataValue

                                self.dataValue = ""
                                self.dataList = []

                                # Save ReferencedSOPInstanceUID_RTPLAN in descriptor
                                self.getValue(dcmFile, "Referenced SOP Instance UID", reference="Referenced Structure Set Sequence")
                                if self.dataValue != "":
                                    descriptor["ReferencedSOPInstanceUID_RTSTRUCT"] = self.dataValue

                                self.dataValue = ""

                                self.dataList = []

                                # Save ReferencedSOPInstanceUID_RTPLAN in descriptor
                                self.getValue(dcmFile, "Referenced SOP Instance UID", reference="Referenced RT Plan Sequence")
                                if self.dataValue != "":
                                    descriptor["ReferencedSOPInstanceUID_RTPLAN"] = self.dataValue

                                self.dataValue = ""
                                self.dataList = []

                                # Save Contour Image Sequence
                                self.getValue(dcmFile, "Contour Image Sequence")
                                if self.dataList != []:
                                    descriptor["ContourImageSequence"] = list(set(self.dataList))

                                self.dataValue = ""
                                self.dataList = []

                                # According to modality save
                                if "Modality" in dcmFile:

                                    # For RTPLAN
                                    if dcmFile.Modality == "RTPLAN":

                                        # Save RTPlanLabel in descriptor
                                        if "RTPlanLabel" in dcmFile:
                                            descriptor["RTPlanLabel"] = dcmFile.RTPlanLabel

                                        # Save BeamNumbers
                                        if "Beams" in dcmFile:
                                            descriptor["BeamNumbers"] = len(dcmFile.Beams)

                                        # Save RadiationType
                                        self.getValue(dcmFile, "Radiation Type")
                                        if self.dataValue != "":
                                            descriptor["RadiationType"] = self.dataValue

                                        self.dataValue = ""
                                        self.dataList = []

                                    # Save DoseSummationType for RTDOSE
                                    elif dcmFile.Modality == "RTDOSE" and \
                                        "DoseSummationType" in dcmFile:
                                        descriptor["DoseSummationType"] = dcmFile.DoseSummationType

                                    # For RTSTRUCT prepare ROIs dictionary
                                    elif dcmFile.Modality == "RTSTRUCT":
                                        # Oncentra MasterPlan case exports RTSTRUCT with this point we should store this info
                                        if "ReferencedFrameOfReferenceSequence" in dcmFile:
                                            for element in dcmFile.ReferencedFrameOfReferenceSequence:
                                                if "FrameOfReferenceRelationshipSequence" in element:
                                                    for secElem in element.FrameOfReferenceRelationshipSequence:
                                                        if "FrameOfReferenceTransformationType" in secElem:
                                                            descriptor["TreatmentPlanningReferencePoint"] = "Yes"
                                                            break

                                        for element in dcmFile:
                                            if element.VR == "SQ":
                                                if element.name == "Structure Set ROI Sequence":
                                                    for subElem in element:
                                                        self._rois[subElem.ROINumber] = [subElem.ROIName]

                            except Exception, err:
                                self._logger.exception("Unexpected error in dicom file reading.")

                            # Add descriptor for DICOM file
                            self.dicomDescriptors.append(descriptor)

                            # Progress
                            size = 0
                            for progressStudy in self._rootNode.children:
                                for progressSeries in progressStudy.children:
                                    if progressSeries.isChecked:
                                        size += progressSeries.size

                            if thread:
                                processed += 1
                                thread.emit(QtCore.SIGNAL("taskUpdated"), [processed, size])

    def unique(self, tagname):
        """Lookup whether specific tag has unique value within DICOM study
        """
        # Initialise return list
        resList = []

        # Search within descriptors dictionary
        for entry in self.dicomDescriptors:
            if tagname in entry:
                resList.append(entry[tagname])

        # Return created list
        return list(set(resList))

    def isFrameOfReferenceUnique(self):
        """For treatment plan the frame of reference has to be the same
        """
        frameOfReferenceUids = []

        for entry in self.dicomDescriptors:
            if "Modality" in entry:
                if entry["Modality"] in ["CT", "RTPLAN", "RTDOSE", "RTSTRUCT"]:
                    if "FrameOfReferenceUID" in entry:
                        if entry["FrameOfReferenceUID"] not in frameOfReferenceUids:
                            if entry["Modality"] == "RTSTRUCT":
                                if "TreatmentPlanningReferencePoint" in entry:
                                    # TreatmentPanningReferencePoint can have a different frame of refferences (multicase export from Oncentra)
                                    if entry["TreatmentPlanningReferencePoint"] == "Yes":
                                        self._logger.info("Skipping frame of reference because it is treatment plan reference point.")
                                        continue
                                    frameOfReferenceUids.append(entry["FrameOfReferenceUID"])
                            frameOfReferenceUids.append(entry["FrameOfReferenceUID"])
                            self._logger.debug(entry)

        self._logger.info("FrameOfReferences: " + str(len(list(set(frameOfReferenceUids)))))

        return len(list(set(frameOfReferenceUids))) == 1

    def belongingTo(self, tagname, tagValue):
        """
        """
        # Initialise return list
        resList = []

        # Search within descriptors dictionary
        for entry in self.dicomDescriptors:
            if tagname in entry:
                if entry[tagname] == tagValue:
                    resList.append(entry)

        # Return created list
        return resList

    def getValue(self, dcmFile, dataName, reference=None):
        """Read value of specified DICOM element for the DICOM file

        dcmFile: DICOM file
        dataName: DICOM tag element name
        reference: element is referenced by other element (name)

        return: value of found dicom tag
        """
        # Search in all elements within DICOM file
        for data_element in dcmFile:

            if data_element.name == "Contour Image Sequence":
                for elem in data_element.value:
                    self.dataList.append(elem.ReferencedSOPInstanceUID)

            # For sequences
            if data_element.VR == "SQ":
                if reference is not None and \
                   data_element.name != reference: continue
                for dataset in data_element.value:
                    self.getValue(dataset, dataName, reference)

            # For normal elements
            else:
                if data_element.name == dataName:
                    self.dataValue = data_element.value

        return 0

    def determineNumberOfPatientIDs(self):
        """Detect the number of patient IDs
        """
        patientIdList = self.unique("PatientID")
        return len(patientIdList)

    def determineNumberOfStudyUIDs(self):
        """Detect the number of sutdy instace UIDs
        """
        studyInstanceUidList = self.unique("StudyInstanceUID")
        return len(studyInstanceUidList)

    def determineStudyType(self):
        """Choose type of dicom study acording to present modalities
        """
        result = ""

        modalityList = self.unique("Modality")
        modalityList = list(set(modalityList))

        # What DICOM study type it can be depends on present modalities
        if "RTSTRUCT" in modalityList or \
           "RTPLAN" in modalityList or \
           "RTDOSE" in modalityList:
            result = "TreatmentPlan"

        elif "PT" in modalityList and \
             "CT" in modalityList:
             result = "PET-CT"
        elif "PT" in modalityList and \
             "MR" in modalityList:
             result = "PET-MRI"
        elif "MR" in modalityList:
            result = "MRI"
        elif "CT" in modalityList:
            result = "CT"
        elif "US" in modalityList:
            result = "US"
        elif "ST" in modalityList:
            result = "SPECT"
        else:
            result = "Other"

        return result

    def getModalities(self):
        """Return list of modalities in DICOM study
        """
        modalityList = self.unique("Modality")
        modalityList = list(set(modalityList))
        return modalityList

    def hasBurnedInAnnotations(self):
        """Burned in annotations
        """
        return self._burnedInAnnotations

########  ########  #### ##     ##    ###    ######## ########
##     ## ##     ##  ##  ##     ##   ## ##      ##    ##
##     ## ##     ##  ##  ##     ##  ##   ##     ##    ##
########  ########   ##  ##     ## ##     ##    ##    ######
##        ##   ##    ##   ##   ##  #########    ##    ##
##        ##    ##   ##    ## ##   ##     ##    ##    ##
##        ##     ## ####    ###    ##     ##    ##    ########

    def _loadFileNames(self):
        """Recursively search for all files withing source data dictionary
        """
        if self.isReadable:
            for path, subdirs, files in os.walk(self._directory):
                for name in files:
                    self._files.append(os.path.join(path, name))

            self._files.sort()

    def _invalidFile(self, path):
        """Check whether the file should be ignored
        """
        isInvalid = False
        baseName = os.path.basename(path)

        if baseName == "DICOMDIR":
            isInvalid = True
        elif baseName == "DIRFILE":
            isInvalid = True
        elif baseName.lower().endswith(".txt"):
            isInvalid = True
        elif baseName.lower().endswith(".gsession"):  # Geisterr 3D file
            isInvalid = True
        elif baseName.lower().endswith(".gstk"):  # Geisterr 3D file
            isInvalid = True
        elif baseName.lower().endswith(".genv"):  # Geisterr 3D file
            isInvalid = True
        elif baseName.lower().endswith(".rdf"):  # Rover file
            isInvalid = True

        return isInvalid
