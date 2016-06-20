#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

class CrfDicomField():
    """Representation of RPB data collection field documenting DICOM data
    
    In RPB collected DICOM data element is a more specific case of standard
    CRF data field. In addition to basic information about its belonging (study event,
    form, group), it holds the WebAPI URI reference that point to DICOM study data
    """

 ######   #######  ##    ##  ######  ######## ########  ##     ##  ######  ########  #######  ########   ######
##    ## ##     ## ###   ## ##    ##    ##    ##     ## ##     ## ##    ##    ##    ##     ## ##     ## ##    ##
##       ##     ## ####  ## ##          ##    ##     ## ##     ## ##          ##    ##     ## ##     ## ##
##       ##     ## ## ## ##  ######     ##    ########  ##     ## ##          ##    ##     ## ########   ######
##       ##     ## ##  ####       ##    ##    ##   ##   ##     ## ##          ##    ##     ## ##   ##         ##
##    ## ##     ## ##   ### ##    ##    ##    ##    ##  ##     ## ##    ##    ##    ##     ## ##    ##  ##    ##
 ######   #######  ##    ##  ######     ##    ##     ##  #######   ######     ##     #######  ##     ##  ######

    def __init__(self, oid = None, value= None, annotationType= None, eventOid= None, formOid= None, groupOid= None):
        """Default constructor
        """
        # Init members
        self._oid = oid
        self._label = ""
        self._description = ""
        self._value = value
        self._annotationType = annotationType
        self._eventOid = eventOid
        self._formOid = formOid
        self._groupOid = groupOid
        self._webApiUrl = ""
        self._fileUrls = []

########  ########   #######  ########  ######## ########  ######## #### ########  ######
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##    ##
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##
########  ########  ##     ## ########  ######   ########     ##     ##  ######    ######
##        ##   ##   ##     ## ##        ##       ##   ##      ##     ##  ##             ##
##        ##    ##  ##     ## ##        ##       ##    ##     ##     ##  ##       ##    ##
##        ##     ##  #######  ##        ######## ##     ##    ##    #### ########  ######

    @property
    def oid(self):
        """OID Getter
        """
        return self._oid

    @oid.setter
    def oid(self, oidValue):
        """OID Setter
        """
        self._oid = oidValue

    @property
    def label(self):
        """Label Getter
        """
        return self._label

    @label.setter
    def label(self, value):
        """Label Setter
        """
        self._label = value
    
    @property
    def value(self):
        """Value Getter
        """
        return self._value

    @value.setter
    def value(self, value):
        """Value Setter
        """
        self._value = value

    @property
    def annotationType(self):
        """Annotation type Getter
        """
        return self._annotationType

    @annotationType.setter
    def annotationType(self, value):
        """Annotation type Setter
        """
        self._annotationType = value

    @property
    def eventOid(self):
        """EventOid Getter
        """
        return self._eventOid

    @eventOid.setter
    def eventOid(self, eventOid):
        """EventOid Setter
        """
        self._eventOid = eventOid

    @property
    def formOid(self):
        """FormOid Getter
        """
        return self._formOid

    @formOid.setter
    def formOid(self, formOid):
        """FormOid Setter
        """
        self._formOid = formOid

    @property
    def groupOid(self):
        """GroupOid Getter
        """
        return self._groupOid

    @groupOid.setter
    def groupOid(self, groupOid):
        """Group Setter
        """
        self._groupOid = groupOid

    @property
    def webApiUrl(self):
        """WebAPI URL Getter
        """
        return self._webApiUrl

    @webApiUrl.setter
    def webApiUrl(self, value):
        """WebAPI URL Setter
        """
        self._webApiUrl = value

    @property
    def fileUrls(self):
        """File URLs Getter
        """
        return self._fileUrls

    @fileUrls.setter
    def fileUrls(self, urls):
        """File URLs Setter
        """
        self._fileUrls = urls
