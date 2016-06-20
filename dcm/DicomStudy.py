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
        super (DicomStudy, self).__init__(suid, parent)

        # Init members
        self._suid = suid
        self._studyType = ""
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
    def suid(self):
        """ DICOM study instance UID Getter"""
        return self._suid

    @suid.setter
    def suid(self, suid):
        """DICOM study instance UID Setter
        """
        self._suid = suid

    @property
    def studyType(self):
        """ The DICOM study type Getter
        """
        return self._studyType

    @studyType.setter
    def studyType(self, value):
        """DICOM study type Setter
        """
        self._studyType = value

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

        #print("Running is checked on Dicom Study")

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

    def hasStructuredReport(self):
        """Determine whether study has any SR modality serie
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
