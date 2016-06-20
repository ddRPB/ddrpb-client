#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

from DeidentMethodType import DeidentMethodType
from DeidentMethod import DeidentMethod
from Attribute import Attribute
from KeepAttributeAction import KeepAttributeAction

class DeidentModelLoader(object):
    """Loader for Deidentification Model
    """

    def __init__(self, config):
        """Default constructor
        """
        self._methods = []
        self._load(config)

########  ########   #######  ########  ######## ########  ######## #### ########  ######
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##    ##
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##
########  ########  ##     ## ########  ######   ########     ##     ##  ######    ######
##        ##   ##   ##     ## ##        ##       ##   ##      ##     ##  ##             ##
##        ##    ##  ##     ## ##        ##       ##    ##     ##     ##  ##       ##    ##
##        ##     ##  #######  ##        ######## ##     ##    ##    #### ########  ######

##     ## ######## ######## ##     ##  #######  ########   ######
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ##
#### #### ##          ##    ##     ## ##     ## ##     ## ##
## ### ## ######      ##    ######### ##     ## ##     ##  ######
##     ## ##          ##    ##     ## ##     ## ##     ##       ##
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ##
##     ## ########    ##    ##     ##  #######  ########   ######

    def GetProfile(self):
        """Return dedident profile from loaded options (has to be only one)
        """
        for method in self._methods:
            if method.MethodType == DeidentMethodType.PROFILE:
                return method

        return None

    def GetOptions(self):
        """Return deident options which should be applied in addition to profile
        """
        options = []
        for method in self._methods:
            if method.MethodType == DeidentMethodType.OPTION:
                options.append(method)

        return options

########  ########  #### ##     ##    ###    ######## ########
##     ## ##     ##  ##  ##     ##   ## ##      ##    ##
##     ## ##     ##  ##  ##     ##  ##   ##     ##    ##
########  ########   ##  ##     ## ##     ##    ##    ######
##        ##   ##    ##   ##   ##  #########    ##    ##
##        ##    ##   ##    ## ##   ##     ##    ##    ##
##        ##     ## ####    ###    ##     ##    ##    ########

    def _load(self, config):
        """Initialise deidentification methods
        """
        if config.RetainPatientCharacteristicsOption:
            # TODO: later this will be replaced with real loading
            method = DeidentMethod("Retain Patient Characteristics Option", "Retention of information that would otherwise be removed during de-identification according to an option defined in PS 3.15 that requires that any physical characteristics of the patient, which are descriptive rather than identifying information per se, be retained. E.g., Patient's Age, Sex, Size (height) and Weight.", "113108", DeidentMethodType.OPTION)
            method.Attributes.append(Attribute("Ethnic Group", "0010", "2160", KeepAttributeAction()))
            method.Attributes.append(Attribute("Patient Sex Neutered", "0010", "2203", KeepAttributeAction()))
            method.Attributes.append(Attribute("Patient's Age", "0010", "1010", KeepAttributeAction()))
            method.Attributes.append(Attribute("Patient's Sex", "0010", "0040", KeepAttributeAction()))
            method.Attributes.append(Attribute("Patient's Size", "0010", "1020", KeepAttributeAction()))
            method.Attributes.append(Attribute("Patient's Weight", "0010", "1030", KeepAttributeAction()))
            method.Attributes.append(Attribute("Pregnancy Status", "0010", "21C0", KeepAttributeAction()))
            method.Attributes.append(Attribute("Smoking Status", "0010", "21A0", KeepAttributeAction()))

            self._methods.append(method)
