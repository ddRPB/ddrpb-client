#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######


class DeidentConfig(object):
    """De-identification configuration
    """

    def __init__(self, replaceDefaultWith="", replaceDateWith="19000101", replaceTimeWith="000000.000000", replaceDateTimeWith="000000.00", replacePatientNameWith="XXX", replacePersonNameWith="PN"):
        """Default constructor
        """
        self._replaceDefaultWith = replaceDefaultWith
        self._replaceDateWith = replaceDateWith
        self._replaceTimeWith = replaceTimeWith
        self._replaceDateTimeWith = replaceDateTimeWith
        self._replacePatientNameWith = replacePatientNameWith
        self._replacePersonNameWith = replacePersonNameWith

        # default profile
        self._basicApplicationConfidentialityProfile = True

        # not implemented
        self._cleanPixelDataOption = False
        # not implemented
        self._cleanRecognizableVisualFeaturesOption = False
        # not implemented
        self._cleanGraphicsOption = False

        # partially implemented with basic profile
        self._cleanStructuredContentOption = True
        # partially implemented with basic profile
        self._cleanDescriptorsOption = True

        # TODO: these two should be mutually exclusive
        self._retainLongFullDatesOption = True
        # not implemented
        self._retainLongModifiedDatesOption = False

        self._retainPatientCharacteristicsOption = True
        self._retainDeviceIdentityOption = True

        # not implemented
        self._retainUIDsOption = False
        # not implemented
        self._retainSafePrivateOption = False


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
    def ReplacePersonNameWith(self):
        """ReplacePersonNameWith Getter
        """
        return self._replacePersonNameWith

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
    def RetainLongFullDatesOption(self):
        """RetainLongFullDatesOption Getter
        """
        return self._retainLongFullDatesOption

    @RetainLongFullDatesOption.setter
    def RetainLongFullDatesOption(self, value):
        """RetainLongFullDatesOption Setter
        """
        self._retainLongFullDatesOption = value

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

    @property
    def RetainDeviceIdentityOption(self):
        """RetainDeviceIdentityOption Getter
        """
        return self._retainDeviceIdentityOption

    @RetainDeviceIdentityOption.setter
    def RetainDeviceIdentityOption(self, value):
        """RetainDeviceIdentityOption Setter
        """
        self._retainDeviceIdentityOption = value


##     ## ######## ######## ##     ##  #######  ########   ######
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ##
#### #### ##          ##    ##     ## ##     ## ##     ## ##
## ### ## ######      ##    ######### ##     ## ##     ##  ######
##     ## ##          ##    ##     ## ##     ## ##     ##       ##
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ##
##     ## ########    ##    ##     ##  #######  ########   ######

    def GetAppliedMethodCodes(self):
        """Return list of applied de-identification methods codes
        """
        methods = []
        if self._basicApplicationConfidentialityProfile:
            methods.append("113100")
        if self._cleanPixelDataOption:
            methods.append("113101")
        if self._cleanRecognizableVisualFeaturesOption:
            methods.append("113102")
        if self._cleanGraphicsOption:
            methods.append("113103")
        if self._cleanStructuredContentOption:
            methods.append("113104")
        if self._cleanDescriptorsOption:
            methods.append("113105")
        if self._retainLongFullDatesOption:
            methods.append("113106")
        if self._retainLongModifiedDatesOption:
            methods.append("113107")
        if self._retainPatientCharacteristicsOption:
            methods.append("113108")
        if self._retainDeviceIdentityOption:
            methods.append("113109")
        if self._retainUIDsOption:
            methods.append("113110")
        if self._retainSafePrivateOption:
            methods.append("113111")

        return methods
