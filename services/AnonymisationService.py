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
from string import whitespace

# Crypto
import uuid
import hashlib
import random

# PyQt
from PyQt4 import QtCore

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

# Pickle
if sys.version < "3":
    import cPickle as pickle
else:
    import _pickle as pickle

# Services
from services.CryptoService import CryptoService

# Contexts
from contexts.ConfigDetails import ConfigDetails

# Generic library for DICOM de-identification
from dicomdeident.DeidentConfig import DeidentConfig
from dicomdeident.DeidentModelLoader import DeidentModelLoader

 ######  ######## ########  ##     ## ####  ######  ########
##    ## ##       ##     ## ##     ##  ##  ##    ## ##
##       ##       ##     ## ##     ##  ##  ##       ##
 ######  ######   ########  ##     ##  ##  ##       ######
      ## ##       ##   ##    ##   ##   ##  ##       ##
##    ## ##       ##    ##    ## ##    ##  ##    ## ##
 ######  ######## ##     ##    ###    ####  ######  ########


class AnonymisationService(object):
    """DICOM pseudonymisation service class

    This service performs the de-identification of DICOM data
    depending on specified configuration.

    The service is developed in conformance with DICOM supplement 142 (Clinical Trial De-identification Profiles)
    """

    def __init__(self, destination, patient, dicomDataRoot, mappingRoiDic):
        """Default constructor
        """
        self._svcCrypto = CryptoService()

        # Configuration of de-identification
        self._deidentConfig = DeidentConfig()
        self._deidentConfig.ReplacePatientNameWith = patient.newName
        self._deidentConfig.RetainPatientCharacteristicsOption = ConfigDetails().retainPatientCharacteristicsOption
        self._deidentConfig.RetainLongFullDatesOption = ConfigDetails().retainLongFullDatesOption
        self._deidentConfig.RetainDeviceIdentityOption = ConfigDetails().retainDeviceIdentityOption

        # Load the de-identification model according to configuration
        self._modelLoader = DeidentModelLoader(self._deidentConfig)

        # Get profile and options from loaded model
        self._profile = self._modelLoader.GetProfile()
        self._options = self._modelLoader.GetOptions()

        self._destination = destination
        self._lastGeneratedUid = None
        
        self._errorMessage = ""
        self._sourceSize = 0
           
        # List of original DICOM UID for elements with name in li_NameUID
        self.li_UID = blist([])
        # List of anonymised DICOM UID for element with name in li_NameUID
        self.li_UID_anonym = blist([])

        self.__patient = patient
        
        if dicomDataRoot is not None:
          self._dicomDataRoot = dicomDataRoot
          self.__series = []

          # Take the main selected study from dataRoot
          for study in dicomDataRoot.children:
            if study.isChecked:
              self.__study = study
              break

          # Consider all selected series from dataRoot
          for study in dicomDataRoot.children:
            for serie in study.children:
              if serie.isChecked:
                self.__series.append(serie)

        self.__mappingRoiDic = mappingRoiDic

        # These list for now define the Basic Profile

        # Which fields are UIDs and should be replaced by randomly generated UID
        self.li_NameUID = ['Concatenation UID',
                       'Context Group Extension Creator UID',
                       'Creator Version UID',
                       'Creator-Version UID',
                       'Device UID',
                       'Dimension Organization UID',
                       'Dose Reference UID',
                       'Failed SOP Instance UID List',
                       'Fiducial UID',
                       'Frame of Reference UID',
                       'Instance Creator UID',
                       'Irradiation Event UID',
                       'Large Palette Color Lookup Table UID',
                       'Media Storage SOP Instance UID',
                       'Palette Color Lookup Table UID',
                       'Referenced Frame of Reference UID',
                       'Referenced General Purpose Scheduled Procedure Step Transaction UID',
                       'Referenced SOP Instance UID',
                       'Referenced SOP Instance UID in File',
                       'Related Frame of Reference UID',
                       'Requested SOP Instance UID',
                       'Series Instance UID',
                       'SOP Instance UID',
                       'Storage Media File-set UID',
                       'Synchronization Frame of Reference UID',
                       'Template Extension Creator UID',
                       'Template Extension Organization UID',
                       'Transaction UID',
                       'UID']

        # Which fields should be removed
        self.li_NameRemove = ['Acquisition Comments',
                          'Acquisition Context Sequence',
                          'Acquisition Protocol Description',
                          'Actual Human Performers Sequence',
                          "Additional Patient's History",
                          "Additional Patient History",
                          'Admission ID',
                          'Admitting Date',
                          'Admitting Diagnoses Code Sequence',
                          'Admitting Diagnoses Description',
                          'Admitting Time',
                          'Affected SOP Instance UID',
                          'Allergies',
                          'Arbitrary',
                          'Author Observer Sequence',
                          'Branch of Service',
                          'Cassette ID',
                          'Comments on Performed Procedure Step',
                          'Comments on the Performed Procedure Step',
                          'Confidentiality Constraint on Patient Data Description',
                          "Content Creator's Identification Code",
                          "Content Creator's Identification Code Sequence",
                          'Content Sequence',
                          'Contribution Description',
                          'Country of Residence',
                          'Current Patient Location',
                          'Curve Data',
                          'Curve Date',
                          'Curve Time',
                          'Custodial Organization Sequence',
                          'Data Set Trailing Padding',
                          'Derivation Description',
                          'Detector ID',
                          'Digital Signature UID',
                          'Digital Signatures Sequence',
                          'Discharge Diagnosis Description',
                          'Distribution Address',
                          'Distribution Address',
                          'Ethnic Group',
                          'Frame Comments',
                          'Gantry ID',
                          'Generator ID',
                          'Human Performers Name',
                          "Human Performer's Name",
                          'Human Performers Organization',
                          "Human Performer's Organization",
                          'Icon Image Sequence',
                          'Identifying Comments',
                          'Image Comments',
                          'Image Presentation Comments',
                          'Image Service Request Comments',
                          "Imaging Service Request Comments",
                          'Impressions',
                          'Institution Address',
                          'Institutional Department Name',
                          'Insurance Plan Identification',
                          'Intended Recipients of Results Identification Sequence',
                          'Interpretation Approver Sequence',
                          'Interpretation Author',
                          'Interpretation Diagnosis Description',
                          'Interpretation ID Issuer',
                          'Interpretation Recorder',
                          'Interpretation Text',
                          'Interpretation Transcriber',
                          'Issuer of Admission ID',
                          'Issuer of Patient ID',
                          'Issuer of Service Episode ID',
                          'Last Menstrual Date',
                          'MAC',
                          'Medical Alerts',
                          'Medical Record Locator',
                          'Military Rank',
                          'Modified Attributes Sequence',
                          'Modified Image Description',
                          'Modifying Device ID',
                          'Modifying Device Manufacturer',
                          'Name of Physician(s) Reading Study',
                          'Names of Intended Recipients of Results',
                          'Occupation',
                          'Original Attributes Sequence',
                          'Order Callback Phone Number',
                          'Order Entered By',
                          'Order Enterer Location',
                          "Order Enterer's Location",
                          'Other Patient IDs',
                          'Other Patient IDs Sequence',
                          'Other Patient Names',
                          'Overlay Comments',
                          'Overlay Data',
                          'Overlay Date',
                          'Overlay Time',
                          'Participant Sequence',
                          'Patient Address',
                          "Patient's Address",
                          "Patient's Age",
                          'Patient Comments',
                          'Patient State',
                          'Patient Transport Arrangements',
                          "Patient's Birth Name",
                          "Patient's Birth Time",
                          "Patient's Institution Residence",
                          "Patient's Insurance Plan Code Sequence",
                          "Patient's Mother's Birth Name",
                          "Patient's Primary Language Code Sequence",
                          "Patient's Primary Language Modifier Code Sequence",
                          "Patient's Religious Preference",
                          "Patient's Size",
                          "Patient's Telephone Numbers",
                          "Patient's Weight",
                          'Performed Location',
                          'Performed Procedure Step Description',
                          'Performed Procedure Step ID',
                          'Performed Procedure Step Start Date',
                          'Performed Procedure Step Start Time',
                          'Performed Station AE Title',
                          'Performed Station Geographic Location Code Sequence',
                          'Performed Station Name',
                          'Performed Station Name Code Sequence',
                          "Performing Physicians' Identification Sequence",
                          "Performing Physician Identification Sequence",
                          "Performing Physicians' Name",
                          "Performing Physician's Name",
                          'Person Address',
                          "Person's Address",
                          'Person Telephone Numbers',
                          "Person's Telephone Numbers",
                          'Physician Approving Interpretation',
                          'Physician Reading Study Identification Sequence',
                          "Physician(s) Reading Study Identification Sequence",
                          'Physician(s) of Record',
                          'Physician(s) of Record Identification Sequence',
                          'Plate ID',
                          'Procedure Code Sequence',
                          'Pre-Medication',
                          'Pregnancy Status',
                          'Reason for Imaging Service Request',
                          'Reason for the Imaging Service Request',
                          'Reason for Study',
                          'Referenced Digital Signature Sequence',
                          'Referenced Patient Alias Sequence',
                          'Referenced Patient Sequence',
                          'Referenced Performed Procedure Step Sequence',
                          'Referenced SOP Instance MAC Sequence',
                          'Referenced Study Sequence',
                          "Referring Physician's Address",
                          "Referring Physician's Identification Sequence",
                          "Referring Physician Identification Sequence",
                          "Referring Physician's Telephone Numbers",
                          'Region of Residence',
                          'Request Attributes Sequence',
                          'Requested Contrast Agent',
                          'Requested Procedure Comments',
                          'Requested Procedure ID',
                          'Requested Procedure Code Sequence',
                          'Requested Procedure Location',
                          'Requesting Physician',
                          'Requesting Service',
                          'Responsible Person',
                          'Results Comments',
                          'Results Distribution List Sequence',
                          'Results ID Issuer',
                          'Scheduled Human Performers Sequence',
                          'Scheduled Patient Institution Residence',
                          'Scheduled Performing Physician Identification Sequence',
                          'Scheduled Performing Physician Name',
                          "Scheduled Performing Physician's Name",
                          'Scheduled Procedure Step End Date',
                          'Scheduled Procedure Step End Time',
                          'Scheduled Procedure Step Description',
                          'Scheduled Procedure Step Location',
                          'Scheduled Procedure Step Start Date',
                          'Scheduled Procedure Step Start Time',
                          'Scheduled Station AE Title',
                          'Scheduled Station Geographic Location Code Sequence',
                          'Scheduled Station Name',
                          'Scheduled Station Name Code Sequence',
                          'Scheduled Study Location',
                          'Scheduled Study Location AE Title',
                          'Service Episode Description',
                          'Service Episode ID',
                          'Smoking Status',
                          'Source Image Sequence',
                          'Special Needs',
                          'Study Comments',
                          'Study ID',
                          'Study ID Issuer',
                          'Text Comments',
                          'Text String',
                          'Timezone Offset From UTC',
                          'Topic Author',
                          'Topic Key Words',
                          "Topic Keywords",
                          'Topic Subject',
                          'Topic Title',
                          'Verifying Organization',
                          'Visit Comments']

        # Which fields should be replaces by default value
        self.li_NameReplace = ['Accession Number',
                           'Acquisition Date',
                           'Acquisition Date Time',
                           "Acquisition DateTime",
                           'Acquisition Device Processing Description',
                           'Acquisition Time',
                           "Content Creator's Name",
                           'Content Date',
                           'Content Time',
                           'Contrast Bolus Agent',
                           "Contrast/Bolus Agent",
                           'Device Serial Number',
                           'Filler Order Number of Imaging Service Request',
                           "Filler Order Number / Imaging Service Request",
                           'Graphic Annotation Sequence',
                           'Institution Code Sequence',
                           'Institution Name',
                           "Operators' Identification Sequence",
                           "Operator Identification Sequence",
                           "Operators' Name",
                           "Patient's Sex",
                           'Patient Sex Neutered',
                           "Patient's Sex Neutered",
                           "Patient's Birth Date",
                           'Person Identification Code Sequence',
                           'Placer Order Number of Imaging Service Request',
                           "Placer Order Number / Imaging Service Request",
                           'Protocol Name',
                           "Referring Physician's Name",
                           'Requested Procedure Description',
                           'Reviewer Name',
                           "Series Date",
                           "Series Time",
                           'Station Name',
                           "Study Date",
                           'Study ID',
                           "Study Time",
                           'Verifying Observer Identification Code Sequence',
                           'Verifying Observer Name',
                           'Verifying Observer Sequence']

########  ########   #######  ########  ######## ########  ######## #### ########  ######
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##    ##
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##
########  ########  ##     ## ########  ######   ########     ##     ##  ######    ######
##        ##   ##   ##     ## ##        ##       ##   ##      ##     ##  ##             ##
##        ##    ##  ##     ## ##        ##       ##    ##     ##     ##  ##       ##    ##
##        ##     ##  #######  ##        ######## ##     ##    ##    #### ########  ######

    @property
    def mappingRoiDic(self):
        """Mapping ROI dictionary Getter

        Mapping ROI dictionary is providing assignment between original names
        of DICOM RTSTRUCT ROIs and formalised names. It should help to keep the
        anonymised data consistent with formal language for region definition.
        """
        return self.__mappingRoiDic

    @mappingRoiDic.setter
    def mappingRoiDic(self, value):
        """Mapping ROI dictionary Setter

        Mapping ROI dictionary is providing assignment between original names
        of DICOM RTSTRUCT ROIs and formalised names. It should help to keep the
        anonymised data consistent with formal language for region definition.
        """
        self.__mappingRoiDic = value

    @property
    def PatientID(self):
        """Pseudonymised patient ID Getter
        """
        return self._patientID

    @PatientID.setter
    def PatientID(self, value):
        """Pseudonymised patient ID Setter
        """
        self._patientID = value

    @property
    def errorMessage(self):
        """Error message Getter
        """
        return self._errorMessage

##     ## ######## ######## ##     ##  #######  ########   ######
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ##
#### #### ##          ##    ##     ## ##     ## ##     ## ##
## ### ## ######      ##    ######### ##     ## ##     ##  ######
##     ## ##          ##    ##     ## ##     ## ##     ##       ##
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ##
##     ## ########    ##    ##     ##  #######  ########   ######

    def makeAnonymous(self, thread=None):
        """Anonymise DICOM folder
        """
        # Check if the path to new dictionary exists
        if not os.path.exists(self._destination):
            self._errorMessage = "Folder for saving anonymised data does not exists"
            return None

        # Init the size of files to anonymise
        filenames = self._getFileNames()
        self._sourceSize = len(filenames)

        # Get original SOP instance UID of selected RTSTRUCT for referencing in RTPLANs
        originalStructUid = self._getOriginalStructSopUid()

        # As a study UID I will use randomly generated UID
        self.StudyInstanceUID = str(self._generateDicomUid())
        self.PatientsName = self._deidentConfig.ReplacePatientNameWith

        # Prepare all UIDs with randomly generated replacements 
        self._prepareUIDs(filenames, thread)

        anonymised = 0
        
        # Now anonymise/pseudonymise whole selected original DICOM hierarchy
        for filename in filenames:
          dcmFile = dicom.read_file(filename, force=True)
                  
          # Keep list of IDAT (PatientID, PatientsName)
          # TODO: this should be extended about more values also from tags with different VR type
          idat = []         
          if self._isValidValue(dcmFile.PatientID):
            idat.append(dcmFile.PatientID)
          if self._isValidValue(dcmFile.PatientsName):
            idat.append(dcmFile.PatientsName)

          # De-identify
          # print "Replacing study and series descriptions"
          self._rewriteDicomDescriptions(dcmFile)
          # print "Encrypting and storing DICOM identity data"
          self._storeIdentity(dcmFile)
          # print "De-identification of dcmFile"
          self._anonymizeDicomUID(dcmFile)
          # print "Remove private tags"
          self._removePrivateTags(dcmFile)
          # print "De-identification of metadata"
          self._anonymizeDicomUID(dcmFile.file_meta)
          # print "De-identification of data"
          self._anonymizeDicomData(dcmFile, idat)
          # print "Map ROI contours"
          self._formalizeDicomROIs(dcmFile)
          # print "Correct RTPlans to point to exactly one RTSTRUCT"
          self._fixPlanToStructReference(dcmFile, originalStructUid)
          # print "Correct RTDose to point to exactly one RTSTRUCT"
          self._fixDoseToStructReference(dcmFile, originalStructUid)

          # Assign pseudonymised PatientID, PatientsName and StudyInstanceUID
          dcmFile.PatientID = self.PatientID
          dcmFile.PatientsName = self.PatientsName
          dcmFile.StudyInstanceUID = self.StudyInstanceUID

          # Save newly de-identified file (filename: modality_randomUID.dcm)
          dicomExtension = ".dcm"
          separator = "_"
          if self._isValidValue(dcmFile.Modality):
            anonymisedFileName = dcmFile.Modality + separator + str(self._generateDicomUid()) + dicomExtension
          else:
            anonymisedFileName = str(self._generateDicomUid()) + dicomExtension            
          dcmFile.save_as(self._destination + os.sep + anonymisedFileName)

          # Progress
          if thread:
              anonymised += 1
              thread.emit(QtCore.SIGNAL("taskUpdated"), [anonymised, self._sourceSize])

########  ########  #### ##     ##    ###    ######## ########
##     ## ##     ##  ##  ##     ##   ## ##      ##    ##
##     ## ##     ##  ##  ##     ##  ##   ##     ##    ##
########  ########   ##  ##     ## ##     ##    ##    ######
##        ##   ##    ##   ##   ##  #########    ##    ##
##        ##    ##   ##    ## ##   ##     ##    ##    ##
##        ##     ## ####    ###    ##     ##    ##    ########

    def _getFileNames(self):
        """Get file names of set to anonymise
        """
        filenames = []

        for study in self._dicomDataRoot.children:
            for serie in study.children:
                if serie.isChecked:
                    for filename in serie.files:
                        filenames.append(filename)

        return filenames

    def _getOriginalStructSopUid(self):
        """Get original SOPInstanceUID of selected RTSTRUCT (for referencing)
        """
        for study in self._dicomDataRoot.children:
            for series in study.children:
              if series.isChecked and series.modality == "RTSTRUCT":
                return series.sopInstanceUid

    def _prepareUIDs(self, filenames, thread=None):
        """Collect original UIDs and prepare the randomly generated ones
        """
        processed = 0
        for filename in filenames:
          dcmFile = dicom.read_file(filename, force=True)
           
          # Collect all original UIDs li_UID  from main dataset as well as meta
          self._getDicomUID(dcmFile)
          self._getDicomUID(dcmFile.file_meta)
 
          # Progress
          if thread:
              processed += 1
              thread.emit(QtCore.SIGNAL("taskUpdated"), [processed, self._sourceSize])
 
        # Remove duplicates from li_UID lists
        self.li_UID = blist(set(self.li_UID))
        self.li_UID.sort()
 
        # Create li_UID_anonym list filled with randomly generated UID
        # The list will have the same size as li_UID (mirroring each other)
        for i in range(len(self.li_UID)):
            self.li_UID_anonym.append(str(self._generateDicomUid()))

    def _getDicomUID(self, dataset):
      """Collect list of all DICOM UIDs for elements with names in li_NameUID
      param dataset: DICOM file or SQ (Sequence of items)
      """
      for element in dataset:
          # When the element is sequence run it recursively
          if element.VR == "SQ":
              for sequence in element.value:
                  self._getDicomUID(sequence)
          # When the element is unique identifier
          elif element.VR == "UI":
              if element.name in self.li_NameUID:
                  if self._isValidValue(element.value):
                      self.li_UID.append(element.value)

    def _rewriteDicomDescriptions(self, dataset):
        """Apply new study and series descriptions
        """
        if type(self.__study.newDescription) is not str and str(self.__study.newDescription.toUtf8()).decode("utf-8") != "":
          if "StudyDescription" in dataset:
            dataset.StudyDescription = str(self.__study.newDescription.toUtf8())
        else:
          if "StudyDescription" in dataset:
            del dataset.StudyDescription

        # Try to replace according to series instance UID 
        if "SeriesInstanceUID" in dataset:
          found = False
          for serie in self.__series:
            if serie.suid == dataset.SeriesInstanceUID:
              if "SeriesDescription" in dataset:
                dataset.SeriesDescription = str(serie.newDescription)
                found = True
                break

        # If no new series description than delete
        if found == False:
          if "SeriesDescription" in dataset:
            del dataset.SeriesDescription

    def _anonymizeDicomUID(self, dataset):
        """Anonymise DICOM UID elements
        UID values are replaced with randomly generated UID
        """
        for element in dataset:
            # When the element is sequence of zero or more items, recursive anonymise
            if element.VR == "SQ":
                for sequence in element.value:
                    self._anonymizeDicomUID(sequence)
            # When the element is unique identifier assign the randomly generated one
            elif element.VR == "UI":
                if element.name in self.li_NameUID:
                    if self._isValidValue(element.value):
                        element.value = self.li_UID_anonym[self.li_UID.index(element.value)]  

    def _anonymizeDicomData(self, dataset, idat):
        """Apply de-identification rules for tags in DICOM dataset
        """
        for element in dataset:
            # First check whether an option is defined which overrides the basic profile
            if self._optionApplied(element, idat):
                continue

            # Otherwise continue with basic profile
            # Remove element
            if element.name in self.li_NameRemove:
                del dataset[element.tag]
            # Replace element with default value
            elif element.name in self.li_NameReplace:
                # When element is person name
                if element.VR == "PN":
                    element.value = self._deidentConfig.ReplacePersonNameWith
                # When element is date yyyymmdd
                elif element.VR == "DA":
                    element.value = self._deidentConfig.ReplaceDateWith
                # When element is time hhmmss.frac
                elif element.VR == "TM":
                    element.value = self._deidentConfig.ReplaceTimeWith
                # When element is datetime
                elif element.VR == "DT":
                    element.value = self._deidentConfig.ReplaceDateTimeWith
                # When element is sequence
                elif element.VR == "SQ":
                    element.value = dicom.sequence.Sequence([dicom.dataset.Dataset()])
                # The rest replace with empty string
                else:
                    element.value = self._deidentConfig.ReplaceDefaultWith
            # For inner sequences run the anonymise recursive
            # this should be always the last condition branch
            elif element.VR == "SQ":
                for sequence in element.value:
                    self._anonymizeDicomData(sequence, idat)

    def _optionApplied(self, dataset, idat):
        """Try to apply defined de-identification options
        """
        wasApplied = False
        for option in self._options:
            if not wasApplied:
                wasApplied = option.Deidentificate(dataset, self._deidentConfig, idat)
            else:
                break

        return wasApplied

    def _removePrivateTags(self, dataset):
        """Remove private tags from DICOM dataset if there is not special exception defined
        """
        # Philips Gemini PET/CT scanner (compressed files with private syntax UID) should not remove private tags
        # because it will be not possible to decompress the imaging data
        if "TransferSyntaxUID" in dataset.file_meta:
            # Keep private tags
            if dataset.file_meta.TransferSyntaxUID == "1.3.46.670589.33.1.4.1":
                return

        # PT modality do not remove privateTags (for specified systems only)
        if dataset.Modality == "PT" or dataset.Modality == "MR":
            if "Manufacturer" in dataset and "ManufacturerModelName" in dataset:
                # Keep private tags
                if dataset.Manufacturer == "Philips Medical Systems" and dataset.ManufacturerModelName == "Ingenuity TF PET/MR":
                    return

        # MR modality do not remove privateTags (for specified systems only)
        if dataset.Modality == "MR":
            if "Manufacturer" in dataset and "ManufacturerModelName" in dataset:
                # Keep private tags
                if dataset.Manufacturer == "Philips Medical Systems" and dataset.ManufacturerModelName == "Ingenuity":
                    return

        # RTDOSE modality do not remove privateTags (for specified systems only)
        if dataset.Modality == "RTDOSE":
            if "Manufacturer" in dataset and "ManufacturerModelName" in dataset:
                # Keep private tags
                if dataset.Manufacturer == "Nucletron" and dataset.ManufacturerModelName == "Oncentra":
                    return
                # Keep private tags
                elif dataset.Manufacturer == "TomoTherapy Incorporated" and dataset.ManufacturerModelName == "Hi-Art":
                    return
                # Remove private tags
                elif dataset.Manufacturer == "Varian Medical Systems" and dataset.ManufacturerModelName == "ARIA RadOnc":
                    pass

        # RTPLAN modality do not remove privateTags (for specified systems only)
        if dataset.Modality == "RTPLAN":
            if "Manufacturer" in dataset and "ManufacturerModelName" in dataset:
                # Keep private tags
                if dataset.Manufacturer == "Nucletron" and dataset.ManufacturerModelName == "Oncentra":
                    return
                # Keep private tags
                elif dataset.Manufacturer == "TomoTherapy Incorporated" and dataset.ManufacturerModelName == "Hi-Art":
                    return
                # Remove private tags
                elif dataset.Manufacturer == "Varian Medical Systems" and dataset.ManufacturerModelName == "ARIA RadOnc":
                    pass

        dataset.remove_private_tags()

    def _formalizeDicomROIs(self, dataset):
        """Change names of original ROIs according to defined mapping
        """
        if dataset.Modality == "RTSTRUCT":
            for element in dataset:
                if element.VR == "SQ":
                    if element.name == "Structure Set ROI Sequence":
                        for subElem in element:
                            # Make sure that key exists
                            if subElem.ROINumber in self.__mappingRoiDic:
                                # Make sure you have a mapping for original ROI name
                                if subElem.ROIName == self.__mappingRoiDic[subElem.ROINumber][0]:
                                    subElem.ROIName = self.__mappingRoiDic[subElem.ROINumber][1]

    def _fixPlanToStructReference(self, dataset, originalStructUid):
        """Make all RTPLANs to refer to one RTSTRUCT that was selected before and harmonised
        """
        if dataset.Modality == "RTPLAN":
            if "ReferencedStructureSetSequence" in dataset:
                for seqItem in dataset.ReferencedStructureSetSequence:
                    if "ReferencedSOPInstanceUID" in seqItem:
                        if seqItem.ReferencedSOPInstanceUID != self.li_UID_anonym[self.li_UID.index(originalStructUid)]:
                            seqItem.ReferencedSOPInstanceUID = self.li_UID_anonym[self.li_UID.index(originalStructUid)]

    def _fixDoseToStructReference(self, dataset, originalStructUid):
        """Make all RTDOSEs to refer to one RTSTRUCT that was selected before and harmonised
        """
        if dataset.Modality == "RTDOSE":
            if "ReferencedStructureSetSequence" in dataset:
                for seqItem in dataset.ReferencedStructureSetSequence:
                    if "ReferencedSOPInstanceUID" in seqItem:
                        if seqItem.ReferencedSOPInstanceUID != self.li_UID_anonym[self.li_UID.index(originalStructUid)]:
                            seqItem.ReferencedSOPInstanceUID = self.li_UID_anonym[self.li_UID.index(originalStructUid)]
    
    def _storeIdentity(self, dcmFile):
        """
        """
        # Collect attributes I want to keep and encrypt
        protectedAttributes = []

        # Frame Of Reference UID
        if "FrameOfReferenceUID" in dcmFile:
          ds1 = Dataset()
          ds1[0x0020,0x0052] = dcmFile[0x0020,0x0052]
          protectedAttributes.append(ds1)
        # Patient ID
        if "PatientID" in dcmFile:
          ds2 = Dataset()
          ds2[0x0010,0x0020] = dcmFile[0x0010,0x0020]
          protectedAttributes.append(ds2)
        # Patient name
        if "PatientName" in dcmFile:
          ds3 = Dataset()
          ds3[0x0010,0x0010] = dcmFile[0x0010,0x0010]
          protectedAttributes.append(ds3)
        # Patient birth date
        if "PatientBirthDate" in dcmFile:
          ds4 = Dataset()
          ds4[0x0010,0x0030] = dcmFile[0x0010,0x0030]
          protectedAttributes.append(ds4)
        # SOP Instance UID
        if "SOPInstanceUID" in dcmFile:
          ds5 = Dataset()
          ds5[0x0008,0x0018] = dcmFile[0x0008,0x0018]
          protectedAttributes.append(ds5)
        # StudyInstance UID
        if "StudyInstanceUID" in dcmFile:
          ds6 = Dataset()
          ds6[0x0020,0x000D] = dcmFile[0x0020,0x000D]
          protectedAttributes.append(ds6)

        # Instance of Encrypted Attributes Data Set
        encryptedAttributesDs = Dataset()

        # Set the Modified Attributes Sequence (0400,0550) to
        # the Attributes to be protected
        t = dicom.tag.Tag((0x400, 0x550))
        encryptedAttributesDs[t] = dicom.dataelem.DataElement(t, "SQ", Sequence(protectedAttributes))

        # Serialize these original DICOM data to string
        encryptedDicomAttributes = pickle.dumps(encryptedAttributesDs)

        # Encrypt
        encryptedData = self._svcCrypto.encrypt(encryptedDicomAttributes)

        # Encrypted Attributes Sequence item with two attributes
        item = Dataset()

        # Set the attribute Encrypted Content Transfer Syntax UID (0400,0510) to
        # the UID of the Transfer Syntax used to encode the instance of the Encrypted Attributes Data Set
        t = dicom.tag.Tag((0x400, 0x510))
        item[t] = dicom.dataelem.DataElement(t, "UI", dcmFile.file_meta[0x0002, 0x0010].value)

        # Set the atribute Encrypted Content (0400,0520) to
        # the data resulting from the encryption of the Encrypted Attributes Data Set instance
        t = dicom.tag.Tag((0x400, 0x520))
        item[t] = dicom.dataelem.DataElement(t, "OB", encryptedData)

        # Set the attribute Encrypted Attributes Sequence (0400,0500)
        # each item consists of two attributes ( (0400,0510); (0400,0520) )
        t = dicom.tag.Tag((0x400, 0x500))
        dcmFile[t] = dicom.dataelem.DataElement(t, "SQ", Sequence([item]))

        # Set the attribute Patient Identity Removed (0012,0062) to YES
        t = dicom.tag.Tag((0x12, 0x62))
        dcmFile[t] = dicom.dataelem.DataElement(t, "CS", "YES")

        # Codes of corresponding profiles and options as a dataset
        profilesOptionsDs = Dataset()

        # De-identification Method Coding Scheme Designator (0008,0102)
        t = dicom.tag.Tag((0x8, 0x102))

        profilesOptionsDs[t] = dicom.dataelem.DataElement(t, "DS", MultiValue(dicom.valuerep.DS, self._deidentConfig.GetAppliedMethodCodes()))

        # Set the attribute De-identification method code sequence (0012,0064)
        # to the created dataset of codes for profiles and options
        t = dicom.tag.Tag((0x12, 0x64))
        dcmFile[t] = dicom.dataelem.DataElement(t, "SQ", Sequence([profilesOptionsDs]))

        # A string describing the method used may also be inserted in or added to De-identification Method (0012,0063), but is not required

    def _isValidValue(self, value):
        """Proof whether the value is valid for further use
        """
        return value != "" and value is not whitespace

    def _generateDicomUid(self):
        """Generate unique UID for DICOM element
        """
        while True:
            uid = self._makeUid()
            if uid != self._lastGeneratedUid:
                self._lastGeneratedUid = uid
                break

        return uid

    def _makeUid(self, entropySrcs=None, prefix="2.25."):
        """Generate a DICOM UID value.
        Follows the advice given at: http://www.dclunie.com/medical-image-faq/html/part2.html#UID

        :entropySrcs : list of str or None
            List of strings providing the entropy used to generate the UID.
            If None these will be collected from a combination of HW address, time, process ID, and randomness.
            Otherwise the result is deterministic (providing the same values will result in the same UID).
        """
        maxUidSize = 64
        availDigits = maxUidSize - len(prefix)

        # Combine all the entropy sources with a hashing algorithm
        if entropySrcs is None:
            entropySrcs = [str(uuid.uuid1()),  # 128-bit from MAC/time/randomness
                           str(os.getpid()),  # Current process ID
                           hex(random.getrandbits(64))]  # 64-bit randomness

        hashVal = hashlib.sha512("".join(entropySrcs).encode('utf-8'))

        # Convert this to an int with the maximum available digits
        return prefix + str(int(hashVal.hexdigest(), 16))[:availDigits]
