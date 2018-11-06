######## ##     ## ######## ##    ## ######## 
##       ##     ## ##       ###   ##    ##    
##       ##     ## ##       ####  ##    ##    
######   ##     ## ######   ## ## ##    ##    
##        ##   ##  ##       ##  ####    ##    
##         ## ##   ##       ##   ###    ##    
########    ###    ######## ##    ##    ##  


class Event:
    """Study Event
    This is study event scheduled for specific study subject
    """

    def __init__(self, eventDefinitionOID="", startDate=None, startTime=None):
        """Default constructor
        """
        self._eventDefinitionOID = eventDefinitionOID
        self._name = ""
        self._description = ""
        self._status = ""
        self._category = ""
        self._startDate = startDate
        self._startTime = startTime
        self._isRepeating = False
        self._studyEventRepeatKey = ""
        self._eventType = ""
        self._subjectAgeAtEvent = ""

        self._forms = []

########  ########   #######  ########  ######## ########  ######## #### ########  ######  
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##    ## 
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##       
########  ########  ##     ## ########  ######   ########     ##     ##  ######    ######  
##        ##   ##   ##     ## ##        ##       ##   ##      ##     ##  ##             ## 
##        ##    ##  ##     ## ##        ##       ##    ##     ##     ##  ##       ##    ## 
##        ##     ##  #######  ##        ######## ##     ##    ##    #### ########  ###### 

    @property
    def eventDefinitionOID(self):
        """Event definition OID Getter
        """
        return self._eventDefinitionOID

    @eventDefinitionOID.setter
    def eventDefinitionOID(self, value):
        """Event definition OID Setter
        """
        self._eventDefinitionOID = value

    @property 
    def name(self):
        """Event name Getter
        """
        return self._name

    @name.setter
    def name(self, value):
        """Event name Setter
        """
        self._name = value

    @property
    def description(self):
        """Description Getter
        """
        return self._description

    @description.setter
    def description(self, value):
        """Description Setter
        """
        self._description = value

    @property
    def status(self):
        """Status Getter
        """
        return self._status

    @status.setter
    def status(self, value):
        """Status Setter
        """
        self._status = value

    @property
    def category(self):
        """Category Getter
        """
        return self._category

    @category.setter
    def category(self, value):
        """Category Setter
        """
        self._category = value

    @property
    def startDate(self):
        """Study event start date Getter
        """
        return self._startDate

    @startDate.setter
    def startDate(self, value):
        """Study event start date Setter
        """
        self._startDate = value

    @property
    def startTime(self):
        """Study event start time Getter
        """
        return self._startTime

    @startTime.setter
    def startTime(self, value):
        """Study event start time Setter
        """
        self._startTime = value

    @property
    def isRepeating(self):
        """Is repeating Getter
        """
        return self._isRepeating

    @isRepeating.setter
    def isRepeating(self, value):
        """Is repeating Setter
        """
        self._isRepeating = value

    @property
    def studyEventRepeatKey(self):
        """StudyEventRepeatKey Getter
        """
        return self._studyEventRepeatKey

    @studyEventRepeatKey.setter
    def studyEventRepeatKey(self, value):
        """StudyEvent RepeatKey Setter
        """
        self._studyEventRepeatKey = value

    @property
    def eventType(self):
        """Event type Getter
        """
        return self._eventType

    @eventType.setter
    def eventType(self, value):
        """Event type Setter
        """
        self._eventType = value

    @property
    def subjectAgeAtEvent(self):
        """Subject age at event Getter
        """
        return self._subjectAgeAtEvent

    @subjectAgeAtEvent.setter
    def subjectAgeAtEvent(self, value):
        """Subject age at event Setter
        """
        self._subjectAgeAtEvent = value

    @property
    def forms(self):
        """eCRFs Getter
        """
        return self._forms

##     ## ######## ######## ##     ##  #######  ########   ######  
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ## 
#### #### ##          ##    ##     ## ##     ## ##     ## ##       
## ### ## ######      ##    ######### ##     ## ##     ##  ######  
##     ## ##          ##    ##     ## ##     ## ##     ##       ## 
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ## 
##     ## ########    ##    ##     ##  #######  ########   ######  

    def addCrf(self, form):
        """Add eCRF form to the event
        """
        self._forms.append(form)

    def setForms(self, value):
        """eCRFs Setter
        """
        self._forms = value

    def hasScheduledCrf(self, formOid):
        """Verify whether the event has specific CRF scheduled
        """
        result = False

        for crf in self._forms:
            if crf.oid == formOid:
                result = True
                break

        return result
