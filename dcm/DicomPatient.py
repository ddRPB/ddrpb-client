#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# Domain
from domain.Node import Node


class DicomPatient(Node):
    """DicomPatient entity
    """

    def __init__(self, parent=None):
        """Default constructor
        """
        super(DicomPatient, self).__init__("", parent)

        # Init properties
        self._id = ""
        self._name = ""
        self._gender = ""
        self._dob = ""

########  ########   #######  ########  ######## ########  ######## #### ########  ######
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##    ##
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##
########  ########  ##     ## ########  ######   ########     ##     ##  ######    ######
##        ##   ##   ##     ## ##        ##       ##   ##      ##     ##  ##             ##
##        ##    ##  ##     ## ##        ##       ##    ##     ##     ##  ##       ##    ##
##        ##     ##  #######  ##        ######## ##     ##    ##    #### ########  ######

    @property
    def id(self):
        """ DICOM Patient ID Getter
        """
        return self._id

    @id.setter
    def id(self, value):
        """DICOM Patient ID Setter
        """
        self._id = value

    @property
    def name(self):
        """ The DICOM Patient name Getter
        """
        return self._name

    @name.setter
    def name(self, value):
        """DICOM Patient name Setter
        """
        self._name = value

    @property
    def gender(self):
        """ The DICOM Patient gender Getter
        """
        return self._gender

    @gender.setter
    def gender(self, value):
        """DICOM Patient gender Setter
        """
        self._gender = value

    @property
    def dob(self):
        """ The DICOM Patient dob Getter
        """
        return self._dob

    @dob.setter
    def dob(self, value):
        """DICOM Patient dob Setter
        """
        self._dob = value

##     ## ######## ######## ##     ##  #######  ########   ######
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ##
#### #### ##          ##    ##     ## ##     ## ##     ## ##
## ### ## ######      ##    ######### ##     ## ##     ##  ######
##     ## ##          ##    ##     ## ##     ## ##     ##       ##
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ##
##     ## ########    ##    ##     ##  #######  ########   ######

    def typeInfo(self):
        """Display information about DICOM study as hierarchy node type
        """
        return "PATIENT"

    def __repr__(self):
        """Object representation of DICOM patient
        """
        adr = hex(id(self)).upper()
        return "<DicomPatient %s>" % adr
