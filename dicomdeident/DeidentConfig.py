#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

class DeidentConfig(object):
    """Deidentification configuration
    """

    def __init__(self, replaceDefaultWith="", replaceDateWith="19000101", replaceTimeWith="000000.000000", replaceDateTimeWith="000000.00", replacePatientNameWith="XXX"):
        """Default constructor
        """
        self._replaceDefaultWith = replaceDefaultWith
        self._replaceDateWith = replaceDateWith
        self._replaceTimeWith = replaceTimeWith
        self._replaceDateTimeWith = replaceDateTimeWith
        self._replacePatientNameWith = replacePatientNameWith

        self._basicApplicationConfidentialityProfile = True
        self._cleanDescriptorsOption = True
        self._retainPatientCharacteristicsOption = True

########  ########   #######  ########  ######## ########  ######## #### ########  ######
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##    ##
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##
########  ########  ##     ## ########  ######   ########     ##     ##  ######    ######
##        ##   ##   ##     ## ##        ##       ##   ##      ##     ##  ##             ##
##        ##    ##  ##     ## ##        ##       ##    ##     ##     ##  ##       ##    ##
##        ##     ##  #######  ##        ######## ##     ##    ##    #### ########  ######

    @property
    def ReplaceDefaultWith(self):
        """ReplaceDefault Getter
        """
        return self._replaceDefaultWith

    @property
    def ReplaceDateWith(self):
        """ReplaceDateWith Getter
        """
        return self._replaceDateWith

    @property
    def ReplaceTimeWith(self):
        """ReplaceTimeWith Getter
        """
        return self._replaceTimeWith

    @property
    def ReplaceDateTimeWith(self):
    	"""ReplaceDateTimeWith Getter
    	"""
    	return self._replaceDateTimeWith

    @property
    def ReplacePatientNameWith(self):
        """ReplacePatientNameWith Getter
        """
        return self._replacePatientNameWith

    @ReplacePatientNameWith.setter
    def ReplacePatientNameWith(self, value):
        """ReplacePatientNameWith Setter
        """
        self._replacePatientNameWith = value

    @property
    def RetainPatientCharacteristicsOption(self):
        """RetainPatientCharacteristicsOption Getter
        """
        return self._retainPatientCharacteristicsOption

    @RetainPatientCharacteristicsOption.setter
    def RetainPatientCharacteristicsOption(self, value):
        """RetainPatientCharacteristicsOption Setter
        """
        self._retainPatientCharacteristicsOption = value

##     ## ######## ######## ##     ##  #######  ########   ######
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ##
#### #### ##          ##    ##     ## ##     ## ##     ## ##
## ### ## ######      ##    ######### ##     ## ##     ##  ######
##     ## ##          ##    ##     ## ##     ## ##     ##       ##
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ##
##     ## ########    ##    ##     ##  #######  ########   ######

    def GetAppliedMethodCodes(self):
        """Return list of applied deident methods codes 
        """
        methods = []
        if self._basicApplicationConfidentialityProfile:
            methods.append("113100")
        if self._cleanDescriptorsOption:
            methods.append("113105")
        if self._retainPatientCharacteristicsOption:
            methods.append("113108")

        return methods