#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# Coding Scheme Designator (0008,0102) 
# Code Value (0008,0100) 
# Code Meaning (0008,0104)

class DeidentMethod(object):
    """De-identification method
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
        """De-identify
        """
        result = False

        # Lookup if element is specified in attributes defined in this de-identification method
        for attribute in self._attributes:

            # Lowercase tag comparision in string form (gggg, eeee)
            if (str(attribute)).lower() == (str(element.tag)).lower():

                # Perform the action specified for the attribute within this de-identification method
                attribute.Action.PerformDeident(element, deidentConfig, idat)

                # Report that de-identification action was performed and close the lookup
                result = True
                break

        return result

    def Reidentificate(self):
        """Not Implemented
        """
        pass
