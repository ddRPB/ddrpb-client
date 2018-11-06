#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######


class AbstractAttributeAction(object):
    """Abstract Action which should be performed on DICOM attribute
    """

    def __init__(self, name="", description="", code=""):
        """Default constructor
        """
        self._name = name
        self._description = description
        self._code = code

        self._attribute = None

########  ########   #######  ########  ######## ########  ######## #### ########  ######
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##    ##
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##
########  ########  ##     ## ########  ######   ########     ##     ##  ######    ######
##        ##   ##   ##     ## ##        ##       ##   ##      ##     ##  ##             ##
##        ##    ##  ##     ## ##        ##       ##    ##     ##     ##  ##       ##    ##
##        ##     ##  #######  ##        ######## ##     ##    ##    #### ########  ######

    @property
    def Name(self):
        """Name Getter
        """
        return self._name

    @property
    def Description(self):
        """Description Getter
        """
        return self._description

    @property
    def Code(self):
        """Code Getter
        """
        return self._code

    @property
    def Attribute(self):
        """Attribute Getter
        """
        return self._attribute

    @Attribute.setter
    def Attribute(self, attribute):
        """Attribute Setter
        """
        self._attribute = attribute

##     ## ######## ######## ##     ##  #######  ########   ######
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ##
#### #### ##          ##    ##     ## ##     ## ##     ## ##
## ### ## ######      ##    ######### ##     ## ##     ##  ######
##     ## ##          ##    ##     ## ##     ## ##     ##       ##
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ##
##     ## ########    ##    ##     ##  #######  ########   ######

    def PerformDeident(self, element, deidentConfig, idat):
        """Do Not Implement - Abstract
        """
        pass

    def PerformReident(self):
        """Do Not Implement - Abstract
        """
        pass
