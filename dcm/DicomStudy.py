#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# Domain
from domain.Node import Node


class DicomStudy(Node):
    """DICOM object which can be part of DICOM hierarchy tree (as a Node)
    """

    def __init__(self, suid, parent=None):
        """Default constructor
        """
        super(DicomStudy, self).__init__(suid, parent)

        # Init members
        self._suid = suid
        self._description = ""
        self._newDescription = ""
        self._date = ""
        self._modalities = ""

########  ########   #######  ########  ######## ########  ######## #### ########  ######
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##    ##
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##
########  ########  ##     ## ########  ######   ########     ##     ##  ######    ######
##        ##   ##   ##     ## ##        ##       ##   ##      ##     ##  ##             ##
##        ##    ##  ##     ## ##        ##       ##    ##     ##     ##  ##       ##    ##
##        ##     ##  #######  ##        ######## ##     ##    ##    #### ########  ######

    @property
    def name(self):
        """Overwrite name to display reasonable info about the DICOM study
        """
        return "[" + self.studyType() + "] " + self.description + "<SERIES=" + str(self.childCount()) + ">"

    @property
    def suid(self):
        """ DICOM study instance UID Getter"""
        return self._suid

    @suid.setter
    def suid(self, suid):
        """DICOM study instance UID Setter
        """
        self._suid = suid

    @property
    def description(self):
        """ The DICOM study description Getter
        """
        return self._description

    @description.setter
    def description(self, value):
        """DICOM study description Setter
        """
        self._description = value

    @property
    def newDescription(self):
        """ The DICOM study new description Getter
        """
        return self._newDescription

    @newDescription.setter
    def newDescription(self, value):
        """New DICOM study description Setter
        """
        self._newDescription = value

    @property
    def date(self):
        """The DICOM study date Getter
        """
        return self._date 

    @date.setter
    def date(self, value):
        """The DICOM study date Setter
        """
        self._date = value

    @property
    def modalities(self):
        """The DICOM modalities in study Getter
        """
        return self._modalities

    @modalities.setter
    def modalities(self, value):
        """The DICOM modalities in study Setter
        """
        self._modalities = value

    @property
    def isChecked(self):
        """Node isChecked Getter
        """
        return self._isChecked

    @isChecked.setter
    def isChecked(self, isChecked):
        """Node isChecked Setter
        """
        self._isChecked = isChecked

        # Distribute the option to all children
        if self._children is not None:
            for child in self._children:
                child.isChecked = isChecked

        # print("Running is checked on Dicom Study")

        # Only one selected DICOM study possible
        if isChecked:
            if self.parent is not None:
                for child in self.parent.children:
                    if child._suid != self._suid:
                        child.isChecked = False

##     ## ######## ######## ##     ##  #######  ########   ######
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ##
#### #### ##          ##    ##     ## ##     ## ##     ## ##
## ### ## ######      ##    ######### ##     ## ##     ##  ######
##     ## ##          ##    ##     ## ##     ## ##     ##       ##
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ##
##     ## ########    ##    ##     ##  #######  ########   ######

    def studyType(self):
        """Determine DICOM study type depending on it series 
        """
        modalityList = []

        if self._children is not None:
            for child in self._children:
                modalityList.append(child.modality)

        list(set(modalityList))

        if "CT" in modalityList and \
           "RTSTRUCT" in modalityList and \
           "RTPLAN" not in modalityList and \
           "RTDOSE" not in modalityList:
            result = "Contouring"
        elif "RTSTRUCT" in modalityList or \
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

    def hasStructuredReport(self):
        """Determine whether study has any SR modality series
        """
        if self._children is not None:
            for child in self._children:
                if child.modality == "SR":
                    return True

        return False

    def typeInfo(self):
        """Display information about DICOM study as hierarchy node type
        """
        return "STUDY"

    def typeDate(self):
        """Display information about DICOM study date
        """
        return self._date

    def __repr__(self):
        """Object representation of DICOM study
        """
        adr = hex(id(self)).upper()
        return "<DicomStudy %s>" % adr
