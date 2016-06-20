#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# Domain
from domain.Node import Node


class DicomRtStructure(Node):
    """DICOM-RT object which can be part of DICOM hierarchy tree (as a Node)
    """

    def __init__(self, roiNumber, roiName, parent=None):
        """Default constructor
        """
        super (DicomRtStructure, self).__init__(roiNumber, parent)

        # Init members
        self._roiNumber = roiNumber
        self._roiName = roiName

        # Observation details
        self._roiObservationNumber = -1
        self._roiObservationLabel = ""
        self._rtRoiInterpretedType = ""


########  ########   #######  ########  ######## ########  ######## #### ########  ######
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##    ##
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##
########  ########  ##     ## ########  ######   ########     ##     ##  ######    ######
##        ##   ##   ##     ## ##        ##       ##   ##      ##     ##  ##             ##
##        ##    ##  ##     ## ##        ##       ##    ##     ##     ##  ##       ##    ##
##        ##     ##  #######  ##        ######## ##     ##    ##    #### ########  ######

    @property
    def name(self):
        """Overwrite name to display reasonable info about the DICOM ROI
        """
        if self.rtRoiInterpretedType is not None and self.rtRoiInterpretedType != "":
            if self.roiObservationLabel is not None and self.roiObservationLabel != "":
                return "[ROI] " + str(self.roiNumber) + ": " + self.roiName + \
                       " (" + self.roiObservationLabel + " - " + self.rtRoiInterpretedType + ")"
            else:
                return "[ROI] " + str(self.roiNumber) + ": " + self.roiName + " (" + self.rtRoiInterpretedType + ")"
        else:
            return "[ROI] " + str(self.roiNumber) + ": " + self.roiName

    @property
    def roiNumber(self):
        """ROI Number Getter
        """
        return self._roiNumber

    @roiNumber.setter
    def roiNumber(self, value):
        """ROI Number Setter
        """
        self._roiNumber = value

    @property
    def roiName(self):
        """ROI Name Getter
        """
        return self._roiName

    @roiName.setter
    def roiName(self, value):
        """ROI Name Setter
        """
        self._roiName = value

    @property
    def roiObservationLabel(self):
        """ROI Observation label Getter
        """
        return self._roiObservationLabel

    @roiObservationLabel.setter
    def roiObservationLabel(self, value):
        """ROI  Observation labe Setter
        """
        self._roiObservationLabel = value

    @property
    def rtRoiInterpretedType(self):
        """ROI Name Getter
        """
        return self._rtRoiInterpretedType

    @rtRoiInterpretedType.setter
    def rtRoiInterpretedType(self, value):
        """ROI Name Setter
        """
        self._rtRoiInterpretedType = value

##     ## ######## ######## ##     ##  #######  ########   ######
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ##
#### #### ##          ##    ##     ## ##     ## ##     ## ##
## ### ## ######      ##    ######### ##     ## ##     ##  ######
##     ## ##          ##    ##     ## ##     ## ##     ##       ##
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ##
##     ## ########    ##    ##     ##  #######  ########   ######

    def typeInfo(self):
        """Display information about DICOM data as hierarchy node type
        """
        return "ROI"

    def typeDate(self):
        """Display information about DICOM ROI date
        """
        return ""

    def __repr__(self):
        """Object representation of DICOM ROI
        """
        adr = hex(id(self)).upper()
        return "<ROI %s>" % adr
