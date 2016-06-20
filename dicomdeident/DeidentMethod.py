#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

import DeidentMethodType

# Coding Scheme Designator (0008,0102) 
# Code Value (0008,0100) 
# Code Meaning (0008,0104)

# DCM 113100 Basic Application Confidentiality Profile
# DCM 113101 Clean Pixel Data Option
# DCM 113102 Clean Recognizable Visual Features Option
# DCM 113103 Clean Graphics Option
# DCM 113104 Clean Structured Content Option
# DCM 113105 Clean Descriptors Option
# DCM 113106 Retain Longitudinal Temporal Information With Full Dates Option
# DCM 113107 Retain Longitudinal Temporal Information With Modified Dates Option
# DCM 113108 Retain Patient Characteristics Option
# DCM 113109 Retain Device Identity Option
# DCM 113110 Retain UIDs OptionSupplement 
# DCM 113111 Retain Safe Private Option

class DeidentMethod(object):
    """Deidentification method
    """

    def __init__(self, name, description, code, methodType):
        """Default constructor
        """
        self._name = name
        self._description = description
        self._code = code
        self._methodType = methodType

        self._attributes = []

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
    def Code(self):
        """Code Getter
        """
        return self._code

    @property
    def MethodType(self):
        """MethodType Getter
        """
        return self._methodType

    @property
    def Attributes(self):
        """Attributes Getter
        """
        return self._attributes

##     ## ######## ######## ##     ##  #######  ########   ######
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ##
#### #### ##          ##    ##     ## ##     ## ##     ## ##
## ### ## ######      ##    ######### ##     ## ##     ##  ######
##     ## ##          ##    ##     ## ##     ## ##     ##       ##
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ##
##     ## ########    ##    ##     ##  #######  ########   ######

    def Deidentificate(self, element, deidentConfig, idat):
        """Deidentify
        """
        result = False

        for attribute in self._attributes:
            if str(attribute) == str(element.tag):
                attribute.Action.PerformDeident(element, deidentConfig, idat)
                result = True
                break

        return result

    def Reidentificate(self):
        """Not Implemented
        """
        pass