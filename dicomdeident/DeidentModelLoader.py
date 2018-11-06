#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

from dicomdeident.DeidentMethodType import DeidentMethodType
from dicomdeident.DeidentMethod import DeidentMethod
from dicomdeident.Attribute import Attribute
from dicomdeident.KeepAttributeAction import KeepAttributeAction


class DeidentModelLoader(object):
    """Loader for de-identification Model
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
        """Return de-identification profile from loaded options (has to be only one)
        """
        for method in self._methods:
            if method.MethodType == DeidentMethodType.PROFILE:
                return method

        return None

    def GetOptions(self):
        """Return de-identification options which should be applied in addition to profile
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
        """Initialise de-identification methods
        """

        if config.RetainLongFullDatesOption:
            # TODO: later this will be replaced with real loading (e.g. from DB or config)
            method = DeidentMethod("Retain Longitudinal Temporal Information With Full Dates Option",
                                   "Retention of information that would otherwise be removed during de-identification according to an option defined in PS 3.15 that requires that any dates and times be retained.",
                                   "113106",
                                   DeidentMethodType.OPTION)

            method.Attributes.append(Attribute("Acquisition Date", "0008", "0022", KeepAttributeAction()))
            method.Attributes.append(Attribute("Acquisition DateTime", "0008", "002A", KeepAttributeAction()))
            method.Attributes.append(Attribute("Acquisition Time", "0008", "0032", KeepAttributeAction()))
            method.Attributes.append(Attribute("Admitting Date", "0038", "0020", KeepAttributeAction()))
            method.Attributes.append(Attribute("Admitting Time", "0038", "0021", KeepAttributeAction()))
            method.Attributes.append(Attribute("Content Date", "0008", "0023", KeepAttributeAction()))
            method.Attributes.append(Attribute("Content Time", "0008", "0033", KeepAttributeAction()))
            method.Attributes.append(Attribute("Curve Date", "0008", "0025", KeepAttributeAction()))
            method.Attributes.append(Attribute("Curve Time", "0008", "0035", KeepAttributeAction()))
            method.Attributes.append(Attribute("Last Menstrual Date", "0010", "21D0", KeepAttributeAction()))
            method.Attributes.append(Attribute("Overlay Date", "0008", "0024", KeepAttributeAction()))
            method.Attributes.append(Attribute("Overlay Time", "0008", "0034", KeepAttributeAction()))
            method.Attributes.append(Attribute("Performed Procedure Step Start Date", "0040", "0244", KeepAttributeAction()))
            method.Attributes.append(Attribute("Performed Procedure Step Start Time", "0040", "0245", KeepAttributeAction()))
            method.Attributes.append(Attribute("Scheduled Procedure Step End Date", "0040", "0004", KeepAttributeAction()))
            method.Attributes.append(Attribute("Scheduled Procedure Step End Time", "0040", "0005", KeepAttributeAction()))
            method.Attributes.append(Attribute("Scheduled Procedure Step Start Date", "0040", "0002", KeepAttributeAction()))
            method.Attributes.append(Attribute("Scheduled Procedure Step Start Time", "0040", "0003", KeepAttributeAction()))
            method.Attributes.append(Attribute("Series Date", "0008", "0021", KeepAttributeAction()))
            method.Attributes.append(Attribute("Series Time", "0008", "0031", KeepAttributeAction()))
            method.Attributes.append(Attribute("Study Date", "0008", "0020", KeepAttributeAction()))
            method.Attributes.append(Attribute("Study Time", "0008", "0030", KeepAttributeAction()))
            method.Attributes.append(Attribute("Timezone Offset From UTC", "0008", "0201", KeepAttributeAction()))

            self._methods.append(method)

        if config.RetainPatientCharacteristicsOption:
            # TODO: later this will be replaced with real loading (e.g. from DB or config)
            method = DeidentMethod("Retain Patient Characteristics Option",
                                   "Retention of information that would otherwise be removed during de-identification according to an option defined in PS 3.15 that requires that any physical characteristics of the patient, which are descriptive rather than identifying information per se, be retained. E.g., Patient's Age, Sex, Size (height) and Weight.",
                                   "113108",
                                   DeidentMethodType.OPTION)

            method.Attributes.append(Attribute("Ethnic Group", "0010", "2160", KeepAttributeAction()))
            method.Attributes.append(Attribute("Patient Sex Neutered", "0010", "2203", KeepAttributeAction()))
            method.Attributes.append(Attribute("Patient's Age", "0010", "1010", KeepAttributeAction()))
            method.Attributes.append(Attribute("Patient's Sex", "0010", "0040", KeepAttributeAction()))
            method.Attributes.append(Attribute("Patient's Size", "0010", "1020", KeepAttributeAction()))
            method.Attributes.append(Attribute("Patient's Weight", "0010", "1030", KeepAttributeAction()))
            method.Attributes.append(Attribute("Pregnancy Status", "0010", "21C0", KeepAttributeAction()))
            method.Attributes.append(Attribute("Smoking Status", "0010", "21A0", KeepAttributeAction()))

            self._methods.append(method)

        if config.RetainDeviceIdentityOption:
            # TODO: later this will be replaced with real loading (e.g. from DB or config)
            method = DeidentMethod("Retain Device Identity Option",
                                   "Retention of information that would otherwise be removed during de-identification according to an option defined in PS 3.15 that requires that any information that identifies a device be retained. E.g., Device Serial Number.",
                                   "113109",
                                   DeidentMethodType.OPTION)

            method.Attributes.append(Attribute("Cassette ID", "0018", "1007", KeepAttributeAction()))
            method.Attributes.append(Attribute("Detector ID", "0018", "700A", KeepAttributeAction()))
            method.Attributes.append(Attribute("Device Serial Number", "0018", "1000", KeepAttributeAction()))

            # I commented this, we replace this UID as we do with the rest => I am going to deviate from standard here
            # method.Attributes.append(Attribute("Device UID", "0018", "1002", KeepAttributeAction()))

            method.Attributes.append(Attribute("Gantry ID", "0018", "1008", KeepAttributeAction()))
            method.Attributes.append(Attribute("Generator ID", "0018", "1005", KeepAttributeAction()))
            method.Attributes.append(Attribute("Performed Station AE Title", "0040", "0241", KeepAttributeAction()))
            method.Attributes.append(Attribute("Performed Station Geographic Location Code Sequence", "0040", "4030", KeepAttributeAction()))
            method.Attributes.append(Attribute("Performed Station Name", "0040", "0242", KeepAttributeAction()))
            method.Attributes.append(Attribute("Performed Station Name Code Sequence", "0040", "0248", KeepAttributeAction()))
            method.Attributes.append(Attribute("Plate ID", "0018", "1004", KeepAttributeAction()))
            method.Attributes.append(Attribute("Scheduled Procedure Step Location", "0040", "0011", KeepAttributeAction()))
            method.Attributes.append(Attribute("Scheduled Station AE Title", "0040", "0001", KeepAttributeAction()))
            method.Attributes.append(Attribute("Scheduled Station Geographic Location Code Sequence", "0040", "4027", KeepAttributeAction()))
            method.Attributes.append(Attribute("Scheduled Station Name", "0040", "0010", KeepAttributeAction()))
            method.Attributes.append(Attribute("Scheduled Station Name Code Sequence", "0040", "4025", KeepAttributeAction()))
            method.Attributes.append(Attribute("Scheduled Study Location", "0032", "1020", KeepAttributeAction()))
            method.Attributes.append(Attribute("Scheduled Study Location AE Title", "0032", "1021", KeepAttributeAction()))
            method.Attributes.append(Attribute("Station Name", "0008", "1010", KeepAttributeAction()))

            self._methods.append(method)
