#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# Standard
import os
import sys

# Logging
import logging
import logging.config

# HTTP
import binascii
import requests
from requests.auth import HTTPBasicAuth

# Disable insecure connection warnings
#import urllib3
#urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# String
from string import whitespace

# Datetime
from datetime import datetime

# Pickle
if sys.version < "3":
    import cPickle as pickle
else:
    import _pickle as pickle

# PyQt - threading
from PyQt4 import QtCore

# Data model
from services.DataPersistanceService import CrfFieldAnnotationSerializer
from services.DataPersistanceService import DefaultAccountSerializer
from services.DataPersistanceService import PartnerSiteSerializer
from services.DataPersistanceService import RTStructTypeSerializer
from services.DataPersistanceService import RTStructSerializer
from services.DataPersistanceService import StudySerializer
from services.DataPersistanceService import OCStudySerializer
from services.DataPersistanceService import SoftwareSerializer

# Domain
from domain.Subject import Subject
from domain.Event import Event
from domain.Crf import Crf
from dcm.DicomSeries import DicomSeries

 ######  ######## ########  ##     ## ####  ######  ########
##    ## ##       ##     ## ##     ##  ##  ##    ## ##
##       ##       ##     ## ##     ##  ##  ##       ##
 ######  ######   ########  ##     ##  ##  ##       ######
      ## ##       ##   ##    ##   ##   ##  ##       ##
##    ## ##       ##    ##    ## ##    ##  ##    ## ##
 ######  ######## ##     ##    ###    ####  ######  ########


class HttpConnectionService(object):
    """HTTP connection service
    """

    def __init__(self, protocol, ip, port, userDetails):
        """Default constructor
        """
        self._logger = logging.getLogger(__name__)
        logging.config.fileConfig("logging.ini", disable_existing_loggers=False)

        # Server IP and port as members
        self.__protocol = protocol
        self.__ip = ip
        self.__port = port
        self.__userDetails = userDetails
        self.__application = ""

        # Proxy settings
        self._proxyEnabled = False
        self._proxyHost = ""
        self._proxyPort = ""
        self._noProxy = ""

        # Proxy authentication
        self._proxyAuthEnabled = False
        self._proxyAuthLogin = ""
        self._proxyAuthPassword = ""

        # JSON serialization/deserialization
        self._partnerSiteSerializer = PartnerSiteSerializer()
        self._defaultAccountSerializer = DefaultAccountSerializer()
        self._studySerializer = StudySerializer()
        self._ocStudySerializer = OCStudySerializer()
        self._crfFieldAnnotationSerializer = CrfFieldAnnotationSerializer()
        self._rtStructTypeSerializer = RTStructTypeSerializer()
        self._rtStructSerializer = RTStructSerializer()
        self._softwareSerializer = SoftwareSerializer()

        # chunk_size: int, optional
        #             maximum number of bytes per data chunk using chunked transfer
        #             encoding (helpful for storing and retrieving large objects or large
        #             collections of objects such as studies or series)
        self._chunk_size = None

########  ########   #######  ########  ######## ########  ######## #### ########  ######
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##    ##
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##
########  ########  ##     ## ########  ######   ########     ##     ##  ######    ######
##        ##   ##   ##     ## ##        ##       ##   ##      ##     ##  ##             ##
##        ##    ##  ##     ## ##        ##       ##    ##     ##     ##  ##       ##    ##
##        ##     ##  #######  ##        ######## ##     ##    ##    #### ########  ######

    @property
    def protocol(self):
        """Protocol Getter
        """
        return self.__protocol

    @protocol.setter
    def protocol(self, value):
        """Protocol Setter
        """
        if self.__protocol != value:
            self.__protocol = value

    @property
    def ip(self):
        """IP Getter
        """
        return self.__ip

    @ip.setter
    def ip(self, value):
        """IP Setter
        """
        if self.__ip != value:
            self.__ip = value

    @property
    def port(self):
        """Port Getter
        """
        return self.__port

    @port.setter
    def port(self, value):
        """Port Setter
        """
        if self.__port != value:
            self.__port = value

    @property
    def application(self):
        """Application Getter
        """
        return self.__application

    @application.setter
    def application(self, value):
        """Application Setter
        """
        if self.__application != value:
            self.__application = "/" + value

##     ## ######## ######## ##     ##  #######  ########   ######  
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ## 
#### #### ##          ##    ##     ## ##     ## ##     ## ##       
## ### ## ######      ##    ######### ##     ## ##     ##  ######  
##     ## ##          ##    ##     ## ##     ## ##     ##       ## 
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ## 
##     ## ########    ##    ##     ##  #######  ########   ######  

    def setupProxy(self, host, port, noProxy):
        """Enable communication over proxy
        """
        if (host is not None and host != "") and (port is not None and port != ""):
            self._proxyHost = host
            self._proxyPort = port
            self._noProxy = noProxy

            self._proxyEnabled = True

    def setupProxyAuth(self, login, password):
        """Enable proxy authentication
        """
        self._proxyAuthLogin = login
        self._proxyAuthPassword = password

        self._proxyAuthEnabled = True

 ######   ######## ########
##    ##  ##          ##
##        ##          ##
##   #### ######      ##
##    ##  ##          ##
##    ##  ##          ##
 ######   ########    ##

   ###    ##     ## ######## ##     ## 
  ## ##   ##     ##    ##    ##     ## 
 ##   ##  ##     ##    ##    ##     ## 
##     ## ##     ##    ##    ######### 
######### ##     ##    ##    ##     ## 
##     ## ##     ##    ##    ##     ## 
##     ##  #######     ##    ##     ##

    def getMyDefaultAccount(self):
        """
        """
        method = "/api/v1/getMyDefaultAccount/"
        result = None

        r = self._sentRequest(method)

        if r.status_code == 200:
            result = self._defaultAccountSerializer.deserialize(r.json())
        else:
            self._logger.info("Could not retrieve RPB default account entity.")

        return result

 ######  ######## ##     ## ########  ##    ##
##    ##    ##    ##     ## ##     ##  ##  ##
##          ##    ##     ## ##     ##   ####
 ######     ##    ##     ## ##     ##    ##
      ##    ##    ##     ## ##     ##    ##
##    ##    ##    ##     ## ##     ##    ##
 ######     ##     #######  ########     ##

    def getStudyByOcIdentifier(self, ocidentifier):
        method = u"/api/v1/getStudyByOcIdentifier/" + ocidentifier
        result = None

        r = self._sentRequest(method)

        if r.status_code == 200:
            result = self._studySerializer.deserialize(r.json())

        return result

########  ########  ######  ######## ########  ##     ##  ######  ########
##     ##    ##    ##    ##    ##    ##     ## ##     ## ##    ##    ##
##     ##    ##    ##          ##    ##     ## ##     ## ##          ##
########     ##     ######     ##    ########  ##     ## ##          ##
##   ##      ##          ##    ##    ##   ##   ##     ## ##          ##
##    ##     ##    ##    ##    ##    ##    ##  ##     ## ##    ##    ##
##     ##    ##     ######     ##    ##     ##  #######   ######     ##

    def getAllRTStructs(self, data, thread=None):
        """Get all formalised RTSTRUCT contour names
        """
        method = "/api/v1/getAllRTStructs/"
        results = []

        r = self._sentRequest(method)

        if r.status_code == 200:
            listOfDicst = r.json()
            for dic in listOfDicst:
                obj = self._rtStructSerializer.deserialize(dic)
                results.append(obj)

        if thread:
            thread.emit(QtCore.SIGNAL("finished(QVariant)"), results)
            return None
        else:
            return results

 ######  ########  ########       ###    ##    ## ##    ##  #######  ########    ###    ######## ####  #######  ##    ##  ######
##    ## ##     ## ##            ## ##   ###   ## ###   ## ##     ##    ##      ## ##      ##     ##  ##     ## ###   ## ##    ##
##       ##     ## ##           ##   ##  ####  ## ####  ## ##     ##    ##     ##   ##     ##     ##  ##     ## ####  ## ##
##       ########  ######      ##     ## ## ## ## ## ## ## ##     ##    ##    ##     ##    ##     ##  ##     ## ## ## ##  ######
##       ##   ##   ##          ######### ##  #### ##  #### ##     ##    ##    #########    ##     ##  ##     ## ##  ####       ##
##    ## ##    ##  ##          ##     ## ##   ### ##   ### ##     ##    ##    ##     ##    ##     ##  ##     ## ##   ### ##    ##
 ######  ##     ## ##          ##     ## ##    ## ##    ##  #######     ##    ##     ##    ##    ####  #######  ##    ##  ######

    def getCrfFieldsAnnotationForStudy(self, studyid, thread=None):
        """Get all CRF fields annotation for given study
        """
        method = "/api/v1/getCrfFieldsAnnotationForStudy/" + str(studyid)
        results = []

        r = self._sentRequest(method)

        if r.status_code == 200:
            listOfDicst = r.json()
            for dic in listOfDicst:
                obj = self._crfFieldAnnotationSerializer.deserialize(dic)
                results.append(obj)

        if thread:
            thread.emit(QtCore.SIGNAL("finished(QVariant)"), results)
            return None
        else:
            return results

 ######   #######  ######## ######## ##      ##    ###    ########  ######## 
##    ## ##     ## ##          ##    ##  ##  ##   ## ##   ##     ## ##       
##       ##     ## ##          ##    ##  ##  ##  ##   ##  ##     ## ##       
 ######  ##     ## ######      ##    ##  ##  ## ##     ## ########  ######   
      ## ##     ## ##          ##    ##  ##  ## ######### ##   ##   ##       
##    ## ##     ## ##          ##    ##  ##  ## ##     ## ##    ##  ##       
 ######   #######  ##          ##     ###  ###  ##     ## ##     ## ######## 

    def getLatestSoftware(self, softwareName):
        """Get latest version of specific software from portal
        """
        method = "/api/v1/getLatestSoftware/" + str(softwareName)
        result = None

        r = self._sentRequest(method)

        if r.status_code == 200:
            result = self._softwareSerializer.deserialize(r.json())

        return result

 #######  ########  ######## ##    ##     ######  ##       #### ##    ## ####  ######     ###
##     ## ##     ## ##       ###   ##    ##    ## ##        ##  ###   ##  ##  ##    ##   ## ##
##     ## ##     ## ##       ####  ##    ##       ##        ##  ####  ##  ##  ##        ##   ##
##     ## ########  ######   ## ## ##    ##       ##        ##  ## ## ##  ##  ##       ##     ##
##     ## ##        ##       ##  ####    ##       ##        ##  ##  ####  ##  ##       #########
##     ## ##        ##       ##   ###    ##    ## ##        ##  ##   ###  ##  ##    ## ##     ##
 #######  ##        ######## ##    ##     ######  ######## #### ##    ## ####  ######  ##     ##

    # TODO: deprecate, load this directly from OC rest service
    def getCrfItemsValues(self, data, thread=None):
        """Get values of specified items fields from OpenClinica
        within one study event for multiple data item fields
        """
        results = []

        if data:
            studyid = data[0]
            subjectPid = data[1]      
            studyEventOid = data[2]
            studyEventRepeatKey = data[3]
            annotations = data[4]

        for a in annotations:
            method = "/api/v2/getCrfItemValue/" + studyid + "/" + subjectPid + "/" + studyEventOid + "/" + studyEventRepeatKey + "/" + a.formoid + "/" + a.crfitemoid

            r = self._sentRequest(method)

            if r.status_code == 200:
                value = r.json()["itemValue"]

                if value is None:
                    value = ""

                results.append(value)

        if thread:
            thread.emit(QtCore.SIGNAL("finished(QVariant)"), results)
            return None
        else:
            return results

    # TODO: deprecate, when portal provides new API for defaultAccount with OC password hash loading
    def getOCAccountPasswordHash(self):
        """Read user account password hash
        """
        method = "/api/v1/getOCAccoutPasswordHash/"
        result = None

        r = self._sentRequest(method)

        if r.status_code == 200:
            dic = r.json()
            ocPasswordHash = dic["ocPasswordHash"]
            result = ocPasswordHash

        return result

    def getOCStudyByIdentifier(self, identifier):
        """Get OC study by its identifier
        """
        method = "/api/v1/getOCStudyByIdentifier/" + identifier
        methodPortal = "/api/v1/edcstudies/" + identifier
        result = None

        r = self._sentRequest(method)

        if r.status_code == 200:
            result = self._ocStudySerializer.deserialize(r.json())
        else:
            r = self._sentPortalRequest(methodPortal)
            if r.status_code == 200:
                result = self._ocStudySerializer.deserialize(r.json())

        return result

    def changeUserActiveStudy(self, username, activeStudyId):
        """Change user active OC study
        """
        method = "/api/v1/changeUserActiveStudy/" + username + "/" + str(activeStudyId)
        methodPortal = "/api/v1/defaultaccounts/" + username + "/activestudy/" + str(activeStudyId)
        result = None

        r = self._sentRequest(method)

        if r.status_code == 200:
            dic = r.json()
            result = dic["result"]
            if result == "true":
                return True
            else:
                return False
        else:
            r = self._putPortalRequest(methodPortal)
            if r.status_code == 204:
                return True
            else:
                return False


 #######   ######      ######  ##     ## ########        ## ########  ######  ######## 
##     ## ##    ##    ##    ## ##     ## ##     ##       ## ##       ##    ##    ##    
##     ## ##          ##       ##     ## ##     ##       ## ##       ##          ##    
##     ## ##           ######  ##     ## ########        ## ######   ##          ##    
##     ## ##                ## ##     ## ##     ## ##    ## ##       ##          ##    
##     ## ##    ##    ##    ## ##     ## ##     ## ##    ## ##       ##    ##    ##    
 #######   ######      ######   #######  ########   ######  ########  ######     ##    

    def getStudyCasebookSubjects(self, data, thread=None):
        """Get study casebook of all subjects
        """
        if data:
            ocUrl = data[0]
            studyOid = data[1]

        method = studyOid + "/*/*/*"
        results = []

        r = self._ocRequest(ocUrl, method)

        if r.status_code == 200:
            if "ClinicalData" in r.json():
                subjectData = r.json()["ClinicalData"]["SubjectData"]

                # Multiple subjects
                if type(subjectData) is list:
                    for subj in subjectData:

                        subject = Subject()
                        subject.oid = subj["@SubjectKey"]
                        subject.studySubjectId = subj["@OpenClinica:StudySubjectID"]
                        subject.status = subj["@OpenClinica:Status"]

                        if "@OpenClinica:UniqueIdentifier" in subj:
                            subject.uniqueIdentifier = subj["@OpenClinica:UniqueIdentifier"]
                        results.append(subject)
                # Only one subject reported
                elif type(subjectData) is dict:
                    subj = subjectData

                    subject = Subject()
                    subject.oid = subj["@SubjectKey"]
                    subject.studySubjectId = subj["@OpenClinica:StudySubjectID"]
                    subject.status = subj["@OpenClinica:Status"]

                    if "@OpenClinica:UniqueIdentifier" in subj:
                        subject.uniqueIdentifier = subj["@OpenClinica:UniqueIdentifier"]
                    results.append(subject)

        if thread:
            thread.emit(QtCore.SIGNAL("finished(QVariant)"), results)
            return None
        else:
            return results

    def getStudyCasebookSubject(self, ocUrl, studyOid, subjectId):
        """Get casebook of one subject
        SubjectId can be StudySubjectOID (SS_) or StudySubjectID (in new version of OC)
        """
        method = studyOid + "/" + subjectId + "/*/*"
        results = None

        r = self._ocRequest(ocUrl, method)

        if r.status_code == 200:
            if "ClinicalData" in r.json():
                subjectData = r.json()["ClinicalData"]["SubjectData"]
                # Exactly one subject should be reported
                if type(subjectData) is dict:
                    subj = subjectData

                    subject = Subject()
                    subject.oid = subj["@SubjectKey"]
                    subject.studySubjectId = subj["@OpenClinica:StudySubjectID"]
                    subject.status = subj["@OpenClinica:Status"]

                    if "@OpenClinica:UniqueIdentifier" in subj:
                        subject.uniqueIdentifier = subj["@OpenClinica:UniqueIdentifier"]
                    results.append(subject)

        return results

 #######   ######     ######## ##     ## ######## ##    ## ######## 
##     ## ##    ##    ##       ##     ## ##       ###   ##    ##    
##     ## ##          ##       ##     ## ##       ####  ##    ##    
##     ## ##          ######   ##     ## ######   ## ## ##    ##    
##     ## ##          ##        ##   ##  ##       ##  ####    ##    
##     ## ##    ##    ##         ## ##   ##       ##   ###    ##    
 #######   ######     ########    ###    ######## ##    ##    ##    

    def getStudyCasebookEvents(self, data, thread=None):
        """Get study casebook subject events
        """
        if data:
            ocUrl = data[0]
            studyOid = data[1]
            studySubjectIdentifier = data[2]

        method = studyOid + "/" + studySubjectIdentifier + "/*/*"
        results = []
        
        r = self._ocRequest(ocUrl, method)

        if r.status_code == 200:
            if "ClinicalData" in r.json():
                if "SubjectData" in r.json()["ClinicalData"]:
                    if "StudyEventData" in r.json()["ClinicalData"]["SubjectData"]:
                        
                        eventData = r.json()["ClinicalData"]["SubjectData"]["StudyEventData"]

                        # Multiple events
                        if type(eventData) is list:
                            for ed in eventData:
                                event = Event()
                                event.eventDefinitionOID = ed["@StudyEventOID"]
                                event.status = ed["@OpenClinica:Status"]

                                dateString = ed["@OpenClinica:StartDate"]
                                format = ""
                                # Is it only date or datetime (in json the date format looks like this)
                                if len(dateString) == 11:
                                    format = "%d-%b-%Y"
                                elif len(dateString) == 20:
                                    format = "%d-%b-%Y %H:%M:%S"

                                event.startDate = datetime.strptime(dateString, format)
                                event.studyEventRepeatKey = ed["@StudyEventRepeatKey"]

                                # Subject Age At Event is optional (because collect birth date is optional)
                                if "OpenClinica:SubjectAgeAtEvent" in ed:
                                    event.subjectAgeAtEvent = ed["OpenClinica:SubjectAgeAtEvent"]

                                # Resulting eCRFs
                                if "FormData" in ed:
                                    formData = ed["FormData"]

                                    # Multiple forms
                                    if type(formData) is list:
                                        for frm in formData:
                                            crf = Crf()
                                            crf.oid = frm["@FormOID"]
                                            crf.version = frm["@OpenClinica:Version"]
                                            crf.status = frm["@OpenClinica:Status"]
                                            event.addCrf(crf)
                                    # Only one form in event
                                    elif type(formData) is dict:
                                        frm  = formData
                                        crf = Crf()
                                        crf.oid = frm["@FormOID"]
                                        crf.version = frm["@OpenClinica:Version"]
                                        crf.status = frm["@OpenClinica:Status"]
                                        event.addCrf(crf)
                                
                                # + automatically schedule default version only (if it is not)
                                eventFormOids = []

                                eventDefinition = r.json()["Study"]["MetaDataVersion"]["StudyEventDef"]
                                if type(eventDefinition) is list:
                                    for ed in eventDefinition:
                                        formRef = ed["FormRef"]
                                        if type(formRef) is list:
                                            for fr in formRef:
                                                eventFormOids.append(fr["@FormOID"])
                                        elif type(formRef) is dict:
                                            eventFormOids.append(formRef["@FormOID"])
                                elif type(eventDefinition) is dict:
                                    ed = eventDefinition
                                    formRef = ed["FormRef"]
                                    if type(formRef) is list:
                                        for fr in formRef:
                                            eventFormOids.append(fr["@FormOID"])
                                    elif type(formRef) is dict:
                                        eventFormOids.append(formRef["@FormOID"])

                                formDefinition = r.json()["Study"]["MetaDataVersion"]["FormDef"]
                                if type(formDefinition) is list:
                                    for fd in formDefinition:
                                        if fd["@OID"] in eventFormOids:
                                            if not event.hasScheduledCrf(fd["@OID"]):

                                                presentInEventDefinition = fd["OpenClinica:FormDetails"]["OpenClinica:PresentInEventDefinition"]

                                                # Form used in multiple Events
                                                if type(presentInEventDefinition) is list:
                                                    for pied in presentInEventDefinition:
                                                        # Only default version forms
                                                        if pied["@IsDefaultVersion"] == "Yes":
                                                            # Only the form that belong to the current event
                                                            if pied["@StudyEventOID"] == event.eventDefinitionOID:
                                                                crf = Crf()
                                                                crf.oid = fd["@OID"]
                                                                event.addCrf(crf)
                                                                break

                                                # Form used in one Event
                                                elif type(presentInEventDefinition) is dict:
                                                    # Only default version forms
                                                    if presentInEventDefinition["@IsDefaultVersion"] == "Yes":
                                                        crf = Crf()
                                                        crf.oid = fd["@OID"]
                                                        event.addCrf(crf)

                                elif type(formDefinition) is dict:
                                    fd = formDefinition
                                    if fd["@OID"] in eventFormOids:
                                        if not event.hasScheduledCrf(fd["@OID"]):

                                            presentInEventDefinition = fd["OpenClinica:FormDetails"]["OpenClinica:PresentInEventDefinition"]

                                            # Form used in multiple Events
                                            if type(presentInEventDefinition) is list:
                                                for pied in presentInEventDefinition:
                                                    # Only default version forms
                                                    if pied["@IsDefaultVersion"] == "Yes":
                                                        # Only the form that belong to the current event
                                                        if pied["@StudyEventOID"] == event.eventDefinitionOID:
                                                            crf = Crf()
                                                            crf.oid = fd["@OID"]
                                                            event.addCrf(crf)
                                                            break

                                            # Form used in one Event
                                            elif type(presentInEventDefinition) is dict:
                                                # Only default version forms
                                                if presentInEventDefinition["@IsDefaultVersion"] == "Yes":
                                                    crf = Crf()
                                                    crf.oid = fd["@OID"]
                                                    event.addCrf(crf)

                                results.append(event)
                        # Only one event reported
                        elif type(eventData) is dict:
                            ed = eventData

                            event = Event()
                            event.eventDefinitionOID = ed["@StudyEventOID"]
                            event.status = ed["@OpenClinica:Status"]
                            dateString = ed["@OpenClinica:StartDate"]

                            format = ""
                            # Is it only date or datetime (in json the date format looks like this)
                            if len(dateString) == 11:
                                format = "%d-%b-%Y"
                            elif len(dateString) == 20:
                                format = "%d-%b-%Y %H:%M:%S"

                            event.startDate = datetime.strptime(dateString, format)
                            event.studyEventRepeatKey = ed["@StudyEventRepeatKey"]

                            # Subject Age At Event is optional (because collect birth date is optional)
                            if "OpenClinica:SubjectAgeAtEvent" in ed:
                                event.subjectAgeAtEvent = ed["OpenClinica:SubjectAgeAtEvent"]

                            # Resulting eCRFs
                            if "FormData" in ed:
                                formData = ed["FormData"]

                                # Multiple forms
                                if type(formData) is list:
                                    for frm in formData:
                                        crf = Crf()
                                        crf.oid = frm["@FormOID"]
                                        crf.version = frm["@OpenClinica:Version"]
                                        crf.status = frm["@OpenClinica:Status"]
                                        event.addCrf(crf)
                                # Only one form in event
                                elif type(formData) is dict:
                                    frm  = formData
                                    crf = Crf()
                                    crf.oid = frm["@FormOID"]
                                    crf.version = frm["@OpenClinica:Version"]
                                    crf.status = frm["@OpenClinica:Status"]
                                    event.addCrf(crf)
                            # + automatically schedule default version (if it is not)
                            eventFormOids = []

                            eventDefinition = r.json()["Study"]["MetaDataVersion"]["StudyEventDef"]
                            if type(eventDefinition) is list:
                                for ed in eventDefinition:
                                    formRef = ed["FormRef"]
                                    if type(formRef) is list:
                                        for fr in formRef:
                                            eventFormOids.append(fr["@FormOID"])
                                    elif type(formRef) is dict:
                                        eventFormOids.append(formRef["@FormOID"])
                            elif type(eventDefinition) is dict:
                                ed = eventDefinition
                                formRef = ed["FormRef"]
                                if type(formRef) is list:
                                    for fr in formRef:
                                        eventFormOids.append(fr["@FormOID"])
                                elif type(formRef) is dict:
                                    eventFormOids.append(formRef["@FormOID"])

                            formDefinition = r.json()["Study"]["MetaDataVersion"]["FormDef"]
                            if type(formDefinition) is list:
                                for fd in formDefinition:
                                    if fd["@OID"] in eventFormOids:
                                        if not event.hasScheduledCrf(fd["@OID"]):

                                            presentInEventDefinition = fd["OpenClinica:FormDetails"]["OpenClinica:PresentInEventDefinition"]

                                            # Form used in multiple Events
                                            if type(presentInEventDefinition) is list:
                                                for pied in presentInEventDefinition:
                                                    # Only default version forms
                                                    if pied["@IsDefaultVersion"] == "Yes":
                                                        # Only the form that belong to the current event
                                                        if pied["@StudyEventOID"] == event.eventDefinitionOID:
                                                            crf = Crf()
                                                            crf.oid = fd["@OID"]
                                                            event.addCrf(crf)
                                                            break

                                            # Form used in one Event
                                            elif type(presentInEventDefinition) is dict:
                                                # Only default version forms
                                                if presentInEventDefinition["@IsDefaultVersion"] == "Yes":
                                                    crf = Crf()
                                                    crf.oid = fd["@OID"]
                                                    event.addCrf(crf)

                            elif type(formDefinition) is dict:
                                fd = formDefinition
                                if fd["@OID"] in eventFormOids:
                                    if not event.hasScheduledCrf(fd["@OID"]):

                                        presentInEventDefinition = fd["OpenClinica:FormDetails"]["OpenClinica:PresentInEventDefinition"]

                                        # Form used in multiple Events
                                        if type(presentInEventDefinition) is list:
                                            for pied in presentInEventDefinition:
                                                # Only default version forms
                                                if pied["@IsDefaultVersion"] == "Yes":
                                                    # Only the form that belong to the current event
                                                    if pied["@StudyEventOID"] == event.eventDefinitionOID:
                                                        crf = Crf()
                                                        crf.oid = fd["@OID"]
                                                        event.addCrf(crf)
                                                        break

                                        # Form used in one Event
                                        elif type(presentInEventDefinition) is dict:
                                            # Only default version forms
                                            if presentInEventDefinition["@IsDefaultVersion"] == "Yes":
                                                crf = Crf()
                                                crf.oid = fd["@OID"]
                                                event.addCrf(crf)

                            results.append(event)

        if thread:
            thread.emit(QtCore.SIGNAL("finished(QVariant)"), results)
            return None
        else:
            return results

    def getStudyCasebookSubjectWithEvents(self, data, thread=None):
        """Get study casebook subject with events
        """
        if data:
            ocUrl = data[0]
            studyOid = data[1]
            studySubjectIdentifier = data[2]

        method = studyOid + "/" + studySubjectIdentifier + "/*/*"
        result = None
        
        r = self._ocRequest(ocUrl, method)

        if r.status_code == 200:
            if "ClinicalData" in r.json():
                if "SubjectData" in r.json()["ClinicalData"]:
                    
                    subjectData = r.json()["ClinicalData"]["SubjectData"]
                    # Exactly one subject should be reported
                    if type(subjectData) is dict:
                        subj = subjectData

                        subject = Subject()
                        subject.oid = subj["@SubjectKey"]
                        subject.studySubjectId = subj["@OpenClinica:StudySubjectID"]
                        subject.status = subj["@OpenClinica:Status"]

                        if "@OpenClinica:UniqueIdentifier" in subj:
                            subject.uniqueIdentifier = subj["@OpenClinica:UniqueIdentifier"]
                        result = subject

                    if "StudyEventData" in r.json()["ClinicalData"]["SubjectData"]:
                        
                        eventData = r.json()["ClinicalData"]["SubjectData"]["StudyEventData"]

                        # Multiple events
                        if type(eventData) is list:
                            for ed in eventData:
                                event = Event()
                                event.eventDefinitionOID = ed["@StudyEventOID"]
                                event.status = ed["@OpenClinica:Status"]

                                dateString = ed["@OpenClinica:StartDate"]
                                format = ""
                                # Is it only date or datetime (in json the date format looks like this)
                                if len(dateString) == 11:
                                    format = "%d-%b-%Y"
                                elif len(dateString) == 20:
                                    format = "%d-%b-%Y %H:%M:%S"

                                event.startDate = datetime.strptime(dateString, format)
                                event.studyEventRepeatKey = ed["@StudyEventRepeatKey"]

                                # Subject Age At Event is optional (because collect birth date is optional)
                                if "OpenClinica:SubjectAgeAtEvent" in ed:
                                    event.subjectAgeAtEvent = ed["OpenClinica:SubjectAgeAtEvent"]

                                # Resulting eCRFs
                                if "FormData" in ed:
                                    formData = ed["FormData"]

                                    # Multiple forms
                                    if type(formData) is list:
                                        for frm in formData:
                                            crf = Crf()
                                            crf.oid = frm["@FormOID"]
                                            crf.version = frm["@OpenClinica:Version"]
                                            crf.status = frm["@OpenClinica:Status"]
                                            event.addCrf(crf)
                                    # Only one form in event
                                    elif type(formData) is dict:
                                        frm = formData
                                        crf = Crf()
                                        crf.oid = frm["@FormOID"]
                                        crf.version = frm["@OpenClinica:Version"]
                                        crf.status = frm["@OpenClinica:Status"]
                                        event.addCrf(crf)
                                
                                # + automatically schedule default version only (if it is not)
                                eventFormOids = []

                                eventDefinition = r.json()["Study"]["MetaDataVersion"]["StudyEventDef"]
                                if type(eventDefinition) is list:
                                    for ed in eventDefinition:
                                        formRef = ed["FormRef"]
                                        if type(formRef) is list:
                                            for fr in formRef:
                                                eventFormOids.append(fr["@FormOID"])
                                        elif type(formRef) is dict:
                                            eventFormOids.append(formRef["@FormOID"])
                                elif type(eventDefinition) is dict:
                                    ed = eventDefinition
                                    formRef = ed["FormRef"]
                                    if type(formRef) is list:
                                        for fr in formRef:
                                            eventFormOids.append(fr["@FormOID"])
                                    elif type(formRef) is dict:
                                        eventFormOids.append(formRef["@FormOID"])

                                formDefinition = r.json()["Study"]["MetaDataVersion"]["FormDef"]
                                if type(formDefinition) is list:
                                    for fd in formDefinition:
                                        if fd["@OID"] in eventFormOids:
                                            if not event.hasScheduledCrf(fd["@OID"]):
                                                
                                                presentInEventDefinition = fd["OpenClinica:FormDetails"]["OpenClinica:PresentInEventDefinition"]

                                                # Form used in multiple Events
                                                if type(presentInEventDefinition) is list:
                                                    for pied in presentInEventDefinition:
                                                        # Only default version of non-hidden forms
                                                        if pied["@IsDefaultVersion"] == "Yes" and pied["@HideCRF"] == "No":
                                                            # Only the form that belong to the current event
                                                            if pied["@StudyEventOID"] == event.eventDefinitionOID:
                                                                crf = Crf()
                                                                crf.oid = fd["@OID"]
                                                                event.addCrf(crf)
                                                                break

                                                # Form used in one Event
                                                elif type(presentInEventDefinition) is dict:
                                                    # Only default version of non-hidden forms
                                                    if presentInEventDefinition["@IsDefaultVersion"] == "Yes" and presentInEventDefinition["@HideCRF"] == "No":
                                                        crf = Crf()
                                                        crf.oid = fd["@OID"]
                                                        event.addCrf(crf)
                                elif type(formDefinition) is dict:
                                    fd = formDefinition
                                    if fd["@OID"] in eventFormOids:
                                        if not event.hasScheduledCrf(fd["@OID"]):

                                            presentInEventDefinition = fd["OpenClinica:FormDetails"]["OpenClinica:PresentInEventDefinition"]

                                            # Form used in multiple Events
                                            if type(presentInEventDefinition) is list:
                                                for pied in presentInEventDefinition:
                                                    # Only default version of non-hidden forms
                                                    if pied["@IsDefaultVersion"] == "Yes" and pied["@HideCRF"] == "No":
                                                        # Only the form that belong to the current event
                                                        if pied["@StudyEventOID"] == event.eventDefinitionOID:
                                                            crf = Crf()
                                                            crf.oid = fd["@OID"]
                                                            event.addCrf(crf)
                                                            break

                                            # Form used in one Event
                                            elif type(presentInEventDefinition) is dict:
                                                # Only default version of non-hidden forms
                                                if presentInEventDefinition["@IsDefaultVersion"] == "Yes" and presentInEventDefinition["@HideCRF"] == "No":
                                                    crf = Crf()
                                                    crf.oid = fd["@OID"]
                                                    event.addCrf(crf)

                                result.studyEventData.append(event)
                        
                        # Only one event reported
                        elif type(eventData) is dict:
                            ed = eventData

                            event = Event()
                            event.eventDefinitionOID = ed["@StudyEventOID"]
                            event.status = ed["@OpenClinica:Status"]
                            dateString = ed["@OpenClinica:StartDate"]

                            format = ""
                            # Is it only date or datetime (in json the date format looks like this)
                            if len(dateString) == 11:
                                format = "%d-%b-%Y"
                            elif len(dateString) == 20:
                                format = "%d-%b-%Y %H:%M:%S"

                            event.startDate = datetime.strptime(dateString, format)
                            event.studyEventRepeatKey = ed["@StudyEventRepeatKey"]

                            # Subject Age At Event is optional (because collect birth date is optional)
                            if "OpenClinica:SubjectAgeAtEvent" in ed:
                                event.subjectAgeAtEvent = ed["OpenClinica:SubjectAgeAtEvent"]

                            # Resulting eCRFs
                            if "FormData" in ed:
                                formData = ed["FormData"]

                                # Multiple forms
                                if type(formData) is list:
                                    for frm in formData:
                                        crf = Crf()
                                        crf.oid = frm["@FormOID"]
                                        crf.version = frm["@OpenClinica:Version"]
                                        crf.status = frm["@OpenClinica:Status"]
                                        event.addCrf(crf)
                                # Only one form in event
                                elif type(formData) is dict:
                                    frm  = formData
                                    crf = Crf()
                                    crf.oid = frm["@FormOID"]
                                    crf.version = frm["@OpenClinica:Version"]
                                    crf.status = frm["@OpenClinica:Status"]
                                    event.addCrf(crf)
                            # + automatically schedule default version (if it is not)
                            eventFormOids = []

                            eventDefinition = r.json()["Study"]["MetaDataVersion"]["StudyEventDef"]
                            if type(eventDefinition) is list:
                                for ed in eventDefinition:
                                    formRef = ed["FormRef"]
                                    if type(formRef) is list:
                                        for fr in formRef:
                                            eventFormOids.append(fr["@FormOID"])
                                    elif type(formRef) is dict:
                                        eventFormOids.append(formRef["@FormOID"])
                            elif type(eventDefinition) is dict:
                                ed = eventDefinition
                                formRef = ed["FormRef"]
                                if type(formRef) is list:
                                    for fr in formRef:
                                        eventFormOids.append(fr["@FormOID"])
                                elif type(formRef) is dict:
                                    eventFormOids.append(formRef["@FormOID"])

                            formDefinition = r.json()["Study"]["MetaDataVersion"]["FormDef"]
                            if type(formDefinition) is list:
                                for fd in formDefinition:
                                    if fd["@OID"] in eventFormOids:
                                        if not event.hasScheduledCrf(fd["@OID"]):

                                            presentInEventDefinition = fd["OpenClinica:FormDetails"]["OpenClinica:PresentInEventDefinition"]

                                            # Form used in multiple Events
                                            if type(presentInEventDefinition) is list:
                                                for pied in presentInEventDefinition:
                                                    # Only default version of non-hidden forms
                                                    if pied["@IsDefaultVersion"] == "Yes" and pied["@HideCRF"] == "No":
                                                        # Only the form that belong to the current event
                                                        if pied["@StudyEventOID"] == event.eventDefinitionOID:
                                                            crf = Crf()
                                                            crf.oid = fd["@OID"]
                                                            event.addCrf(crf)
                                                            break

                                            # Form used in one Event
                                            elif type(presentInEventDefinition) is dict:
                                                # Only default version of non-hidden forms
                                                if presentInEventDefinition["@IsDefaultVersion"] == "Yes" and presentInEventDefinition["@HideCRF"] == "No":
                                                    crf = Crf()
                                                    crf.oid = fd["@OID"]
                                                    event.addCrf(crf)

                            elif type(formDefinition) is dict:
                                fd = formDefinition
                                if fd["@OID"] in eventFormOids:
                                    if not event.hasScheduledCrf(fd["@OID"]):

                                        presentInEventDefinition = fd["OpenClinica:FormDetails"]["OpenClinica:PresentInEventDefinition"]

                                        # Form used in multiple Events
                                        if type(presentInEventDefinition) is list:
                                            for pied in presentInEventDefinition:
                                                # Only default version of non-hidden forms
                                                if pied["@IsDefaultVersion"] == "Yes" and pied["@HideCRF"] == "No":
                                                    # Only the form that belong to the current event
                                                    if pied["@StudyEventOID"] == event.eventDefinitionOID:
                                                        crf = Crf()
                                                        crf.oid = fd["@OID"]
                                                        event.addCrf(crf)
                                                        break

                                        # Form used in one Event
                                        elif type(presentInEventDefinition) is dict:
                                            # Only default version of non-hidden forms
                                            if presentInEventDefinition["@IsDefaultVersion"] == "Yes" and presentInEventDefinition["@HideCRF"] == "No":
                                                crf = Crf()
                                                crf.oid = fd["@OID"]
                                                event.addCrf(crf)

                            result.studyEventData.append(event)

        if thread:
            thread.emit(QtCore.SIGNAL("finished(QVariant)"), result)
            return None
        else:
            return result

########  ########  ########      ######  ##       #### ######## ##    ## ######## 
##     ## ##     ## ##     ##    ##    ## ##        ##  ##       ###   ##    ##    
##     ## ##     ## ##     ##    ##       ##        ##  ##       ####  ##    ##    
########  ########  ########     ##       ##        ##  ######   ## ## ##    ##    
##   ##   ##        ##     ##    ##       ##        ##  ##       ##  ####    ##    
##    ##  ##        ##     ##    ##    ## ##        ##  ##       ##   ###    ##    
##     ## ##        ########      ######  ######## #### ######## ##    ##    ##    

    def downloadRadPlanBioClient(self, software, thread=None):
        """Download latest version of the RadPlanBio client
        """
        method = "software/"

        portalUrl = str(software.portal.publicurl)
        remoteFilename = str(software.filename)

        # Ensure that URL ends with /
        if not portalUrl.endswith("/"):
            portalUrl += "/"

        localFilename = "RadPlanBio-client-x64.zip"

        try:
            os.remove(localFilename)
        except OSError:
            self._logger.info("Zip not removed because does not exists.")

        with open(localFilename, "wb") as handle:
            url = portalUrl + method + remoteFilename
            self._logger.info("Downloading from: %s" % url)

            s = requests.Session()

            auth = None
            if self._proxyAuthEnabled:
                auth = HTTPBasicAuth(self._proxyAuthLogin, self._proxyAuthPassword)
                self._logger.info("Connecting with authentication: %s" % str(self._proxyAuthLogin))

            # Application proxy enabled
            if self._proxyEnabled:
                # No proxy
                if self._noProxy != "" and self._noProxy is not whitespace and self._noProxy in "https://" + self.__ip:
                    proxies = {}
                    self._logger.info("Connecting without proxy because of no proxy: %s" % self._noProxy)
                # RPB client defined proxy
                else:
                    proxies = {"http": "http://" + self._proxyHost + ":" + self._proxyPort, "https": "https://" + self._proxyHost + ":" + self._proxyPort}
                    self._logger.info("Connecting with application defined proxy: %s" % str(proxies))
            # Use system proxy
            else:
                proxies = requests.utils.get_environ_proxies("https://" + self.__ip)
                self._logger.info("Using system proxy variables (no proxy applied): " + str(proxies))

            response = s.get(url, stream=True, auth=auth, verify=False, proxies=proxies)

            if not response.ok:
                self._logger.error("Error during new RadPlanBio client download.")

            for block in response.iter_content(1024):
                if not block:
                    break

                handle.write(block)

        if thread:
            thread.emit(QtCore.SIGNAL("finished(QVariant)"), None)
            return None

########  ####  ######   #######  ##     ##
##     ##  ##  ##    ## ##     ## ###   ###
##     ##  ##  ##       ##     ## #### ####
##     ##  ##  ##       ##     ## ## ### ##
##     ##  ##  ##       ##     ## ##     ##
##     ##  ##  ##    ## ##     ## ##     ##
########  ####  ######   #######  ##     ##

    def getDicomSeriesData(self, patientID, studyInstanceUID, seriesInstanceUID):
        """
        """
        method = "/api/v1/getDicomSeriesData/" + patientID + "/" + studyInstanceUID + "/" + seriesInstanceUID
        dicomSeries = None

        r = self._sentRequest(method)

        if r.status_code == 200:

            if "Series" in r.json():
                jsonSeries = r.json()["Series"]
                if type(jsonSeries) is list:
                    for js in jsonSeries:
                        dicomSeries = DicomSeries(js["SeriesInstanceUID"])
                        dicomSeries.modality = js["Modality"]

                        jsonImages = js["Images"]
                        if type(jsonImages) is list:
                            for ji in jsonImages:
                                dicomSeries.appendFile(ji["SOPInstanceUID"])

        return dicomSeries

########   #######   ######  ########
##     ## ##     ## ##    ##    ##
##     ## ##     ## ##          ##
########  ##     ##  ######     ##
##        ##     ##       ##    ##
##        ##     ## ##    ##    ##
##         #######   ######     ##

########  ####  ######   #######  ##     ## 
##     ##  ##  ##    ## ##     ## ###   ### 
##     ##  ##  ##       ##     ## #### #### 
##     ##  ##  ##       ##     ## ## ### ## 
##     ##  ##  ##       ##     ## ##     ## 
##     ##  ##  ##    ## ##     ## ##     ## 
########  ####  ######   #######  ##     ## 

    def uploadDicomData(self, dcmFile):
        """
        """
        method = "/api/v1/uploadDicomData/"
        result = None

        response = self._postRequest(method, dcmFile, "application/octet-stream")

        self._logger.info(str(response.status_code))
        result = pickle.loads(response.content)

        return result

    def httpPost(self, data, headers):
        """Performs a HTTP POST request.
        Parameters
        ----------
        data: bytes
            HTTP request message payload
        headers: Dict[str, str]
            HTTP request message headers
        """

        method = "/api/v1/dicomweb/studies/"

        def serveDataChunks(data):
            for i, offset in enumerate(range(0, len(data), self._chunk_size)):
                self._logger.debug("Serve data chunk #{i}")
                end = offset + self._chunk_size
                yield data[offset:end]

        if self._chunk_size is not None and len(data) > self._chunk_size:
            self._logger.info("Store data in chunks using chunked transfer encoding")
            chunked_headers = dict(headers)
            chunked_headers['Transfer-Encoding'] = 'chunked'
            chunked_headers['Cache-Control'] = 'no-cache'
            chunked_headers['Connection'] = 'Keep-Alive'
            data_chunks = serveDataChunks(data)
            response = self._postPortalRequest(method, data_chunks, chunked_headers)
        else:
            response = self._postPortalRequest(method, data, headers)
        self._logger.debug("Request status code: {}".format(response.status_code))
        response.raise_for_status()
        if not response.ok:
            self._logger.warning("Storage was not successful for all instances")
            payload = response.content
            content_type = response.headers['Content-Type']
            # TODO: check what is the server responding.... maybe we can process the error messages - for now commented
            # if content_type in ('application/dicom+json', 'application/json',):
            #     dataset = load_json_dataset(payload)
            # elif content_type in ('application/dicom+xml', 'application/xml',):
            #     tree = fromstring(payload)
            #     dataset = _load_xml_dataset(tree)
            # else:
            #     raise ValueError('Response message has unexpected media type.')
            # failed_sop_sequence = getattr(dataset, 'FailedSOPSequence', [])
            # for failed_sop_item in failed_sop_sequence:
            #    self._logger.error(
            #        'storage of instance {} failed: "{}"'.format(
            #            failed_sop_item.ReferencedSOPInstanceUID,
            #            failed_sop_item.FailureReason
            #        )
            #    )
        return response

    def httpPostMultipartApplicationDicom(self, data):
        """Performs a HTTP POST request with a multipart payload with
        "application/dicom" media type.
        Parameters
        ----------
        data: Sequence[bytes]
            DICOM data sets that should be posted
        Returns
        -------
        String
            empty string; maybe we can add status to propagate to UI
        """

        # Generate random boundary value
        boundary = binascii.hexlify(os.urandom(16)).decode('ascii')
        content_type = (
            'multipart/related; '
            'type="application/dicom"; '
            'boundary=' + boundary
        )
        content = self.encodeMultipartMessage(data, content_type)
        response = self.httpPost(
            content,
            headers={'Content-Type': content_type}
        )
        if response.content:
            content_type = response.headers['Content-Type']

            # TODO: currently there is no need for sending dicom+json or dicom+xml
            # if content_type in ('application/dicom+json', 'application/json',):
            #    return load_json_dataset(response.json())
            # elif content_type in ('application/dicom+xml', 'application/xml',):
            #    tree = fromstring(response.content)
            #    return _load_xml_dataset(tree)

        # return dicom.Dataset()
        # TODO: maybe here return status
        return ""

    def encodeMultipartMessage(self, data, content_type):
        """Encodes the payload of a HTTP multipart response message.
        Parameters
        ----------
        data: Sequence[bytes]
            data
        content_type: str
            content type of the multipart HTTP request message
        Returns
        -------
        bytes
            HTTP request message body
        """
        multipart, content_type_field, boundary_field = content_type.split(';')
        content_type = content_type_field.split('=')[1].strip('"')
        boundary = boundary_field.split('=')[1]
        body = b''
        for payload in data:
            body += (
                '\r\n--{boundary}'
                '\r\nContent-Type: {content_type}\r\n\r\n'.format(
                    boundary=boundary,
                    content_type=content_type
                ).encode('utf-8')
            )
            body += payload
        body += '\r\n--{boundary}--'.format(boundary=boundary).encode('utf-8')
        return body

########  ########  #### ##     ##    ###    ######## ######## 
##     ## ##     ##  ##  ##     ##   ## ##      ##    ##       
##     ## ##     ##  ##  ##     ##  ##   ##     ##    ##       
########  ########   ##  ##     ## ##     ##    ##    ######   
##        ##   ##    ##   ##   ##  #########    ##    ##       
##        ##    ##   ##    ## ##   ##     ##    ##    ##       
##        ##     ## ####    ###    ##     ##    ##    ######## 

    def _sentRequest(self, method):
        """Generic GET request to RadPlanBio server
        """
        # Standard header
        s = requests.Session()
        s.headers.update({
            "Content-Type": "application/json",
            "Username": self.__userDetails.username.lower(),
            "Password": self.__userDetails.password,
            "Clearpass": self.__userDetails.clearpass
        })

        # Proxy authentication
        auth = None
        if self._proxyAuthEnabled:
            auth = HTTPBasicAuth(self._proxyAuthLogin, self._proxyAuthPassword)
            self._logger.info("Connecting with authentication: %s" % str(self._proxyAuthLogin))

        # Unicode for URL depends on python version
        if sys.version < "3":
            url = "%s://%s:%s%s%s" % (self.__protocol, self.__ip, str(self.__port), self.__application, method.encode("utf-8"))
        else:
            url = "%s://%s:%s%s%s" % (self.__protocol, self.__ip, str(self.__port), self.__application, method)

        # Application proxy enabled
        if self._proxyEnabled:
            # No proxy
            if self._noProxy != "" and self._noProxy is not whitespace and self._noProxy in "https://" + self.__ip:
                proxies = {}
                self._logger.info("Connecting without proxy because of no proxy: %s" % self._noProxy)
            # RPB client defined proxy
            else:
                proxies = {"http": "http://" + self._proxyHost + ":" + self._proxyPort, "https": "https://" + self._proxyHost + ":" + self._proxyPort}
                self._logger.info("Connecting with application defined proxy: %s" % str(proxies))
        # Use system proxy
        else:
            proxies = requests.utils.get_environ_proxies("https://" + self.__ip)
            self._logger.info("Using system proxy variables (no proxy applied): %s" % str(proxies))

        r = s.get(url, auth=auth, verify=False, proxies=proxies)

        return r

    def _postRequest(self, method, body, contentType):
        """Generic POST request to RadPlanBio server
        """
        s = requests.Session()
        s.headers.update({
                "Content-Type": contentType,
                "Content-Length": str(len(body)),
                "Username": self.__userDetails.username.lower(),
                "Password": self.__userDetails.password,
                "Clearpass": self.__userDetails.clearpass
            }
        )

        auth = None
        if self._proxyAuthEnabled:
            auth = HTTPBasicAuth(self._proxyAuthLogin, self._proxyAuthPassword)
            self._logger.info("Connecting with authentication: %s" % str(self._proxyAuthLogin))

        # Unicode for URL depends on python version
        if sys.version < "3":
            url = "%s://%s:%s%s" % (self.__protocol, self.__ip, str(self.__port), self.__application + method.encode("utf-8"))
        else:
            url = "%s://%s:%s%s" % (self.__protocol, self.__ip, str(self.__port), self.__application + method)

        # Application proxy enabled
        if self._proxyEnabled:
            # No proxy
            if self._noProxy != "" and self._noProxy is not whitespace and self._noProxy in "https://" + self.__ip:
                proxies = {}
                self._logger.info("Connecting without proxy because of no proxy: %s" % self._noProxy)
            # RPB client defined proxy
            else:
                proxies = {"http": "http://" + self._proxyHost + ":" + self._proxyPort, "https": "https://" + self._proxyHost + ":" + self._proxyPort}
                self._logger.info("Connecting with application defined proxy: %s" % str(proxies))
        # Use system proxy
        else:
            proxies = requests.utils.get_environ_proxies("https://" + self.__ip)
            self._logger.info("Using system proxy variables (no proxy applied): %s" % str(proxies))

        r = s.post(url, auth=auth, data=body, verify=False, proxies=proxies)

        return r

    def _sentPortalRequest(self, method):
        """Generic GET request to RadPlanBio portal server
        """
        # Standard header
        s = requests.Session()
        s.headers.update({
            "Content-Type": "application/json",
            "X-Api-Key": self.__userDetails.apikey
        })

        # Proxy authentication
        auth = None
        if self._proxyAuthEnabled:
            auth = HTTPBasicAuth(self._proxyAuthLogin, self._proxyAuthPassword)
            self._logger.info("Connecting with authentication: %s" % str(self._proxyAuthLogin))

        # Unicode for URL depends on python version
        if sys.version < "3":
            url = "%s://%s:%s%s%s" % (self.__protocol, self.__ip, str(self.__port), self.__application, method.encode("utf-8"))
        else:
            url = "%s://%s:%s%s%s" % (self.__protocol, self.__ip, str(self.__port), self.__application, method)

        # Application proxy enabled
        if self._proxyEnabled:
            # No proxy
            if self._noProxy != "" and self._noProxy is not whitespace and self._noProxy in "https://" + self.__ip:
                proxies = {}
                self._logger.info("Connecting without proxy because of no proxy: %s" % self._noProxy)
            # RPB client defined proxy
            else:
                proxies = {"http": "http://" + self._proxyHost + ":" + self._proxyPort, "https": "https://" + self._proxyHost + ":" + self._proxyPort}
                self._logger.info("Connecting with application defined proxy: %s" % str(proxies))
        # Use system proxy
        else:
            proxies = requests.utils.get_environ_proxies("https://" + self.__ip)
            self._logger.info("Using system proxy variables (no proxy applied): %s" % str(proxies))

        r = s.get(url, auth=auth, verify=False, proxies=proxies)

        return r

    def _putPortalRequest(self, method):
        """Generic PUT request to RadPlanBio portal server
        """
        # Standard header
        s = requests.Session()
        s.headers.update({
            "Content-Type": "application/json",
            "X-Api-Key": self.__userDetails.apikey
        })

        # Proxy authentication
        auth = None
        if self._proxyAuthEnabled:
            auth = HTTPBasicAuth(self._proxyAuthLogin, self._proxyAuthPassword)
            self._logger.info("Connecting with authentication: %s" % str(self._proxyAuthLogin))

        # Unicode for URL depends on python version
        if sys.version < "3":
            url = "%s://%s:%s%s%s" % (self.__protocol, self.__ip, str(self.__port), self.__application, method.encode("utf-8"))
        else:
            url = "%s://%s:%s%s%s" % (self.__protocol, self.__ip, str(self.__port), self.__application, method)

        # Application proxy enabled
        if self._proxyEnabled:
            # No proxy
            if self._noProxy != "" and self._noProxy is not whitespace and self._noProxy in "https://" + self.__ip:
                proxies = {}
                self._logger.info("Connecting without proxy because of no proxy: %s" % self._noProxy)
            # RPB client defined proxy
            else:
                proxies = {"http": "http://" + self._proxyHost + ":" + self._proxyPort, "https": "https://" + self._proxyHost + ":" + self._proxyPort}
                self._logger.info("Connecting with application defined proxy: %s" % str(proxies))
        # Use system proxy
        else:
            proxies = requests.utils.get_environ_proxies("https://" + self.__ip)
            self._logger.info("Using system proxy variables (no proxy applied): %s" % str(proxies))

        r = s.put(url, auth=auth, verify=False, proxies=proxies)

        return r

    def _postPortalRequest(self, method, data, headers):
        """Generic POST request to RadPlanBio portal server
        """

        # Standard header
        s = requests.Session()
        s.headers.update(headers)
        s.headers.update({
            "X-Api-Key": self.__userDetails.apikey
        })

        # Proxy authentication
        auth = None
        if self._proxyAuthEnabled:
            auth = HTTPBasicAuth(self._proxyAuthLogin, self._proxyAuthPassword)
            self._logger.info("Connecting with authentication: %s" % str(self._proxyAuthLogin))

        # Unicode for URL depends on python version
        if sys.version < "3":
            url = "%s://%s:%s%s%s" % (
            self.__protocol, self.__ip, str(self.__port), self.__application, method.encode("utf-8"))
        else:
            url = "%s://%s:%s%s%s" % (self.__protocol, self.__ip, str(self.__port), self.__application, method)

        # Application proxy enabled
        if self._proxyEnabled:
            # No proxy
            if self._noProxy != "" and self._noProxy is not whitespace and self._noProxy in "https://" + self.__ip:
                proxies = {}
                self._logger.info("Connecting without proxy because of no proxy: %s" % self._noProxy)
            # RPB client defined proxy
            else:
                proxies = {"http": "http://" + self._proxyHost + ":" + self._proxyPort,
                           "https": "https://" + self._proxyHost + ":" + self._proxyPort}
                self._logger.info("Connecting with application defined proxy: %s" % str(proxies))
        # Use system proxy
        else:
            proxies = requests.utils.get_environ_proxies("https://" + self.__ip)
            self._logger.info("Using system proxy variables (no proxy applied): %s" % str(proxies))

        r = s.post(url, data=data, auth=auth, verify=False, proxies=proxies)

        return r

    def _ocRequest(self, ocUrl, method):
        """Generic OpenClinica (RESTfull URL) GET request
        """
         # xml, html
        dataFormat = "json"

        s = requests.Session()
        loginCredentials = {"j_username": self.__userDetails.username.lower(), "j_password": self.__userDetails.clearpass}

        auth = None
        if self._proxyAuthEnabled:
            auth = HTTPBasicAuth(self._proxyAuthLogin, self._proxyAuthPassword)
            self._logger.info("Connecting with authentication: " + str(self._proxyAuthLogin))

        # Ensure that URL ends with /
        if not ocUrl.endswith("/"):
            ocUrl += "/"

        # Application proxy enabled
        if self._proxyEnabled:
            if self._noProxy != "" and self._noProxy is not whitespace and self._noProxy in "https://" + self.__ip:
                self._logger.info("Connecting without proxy because of no proxy: " + self._noProxy)
                r = s.post(
                    ocUrl + "j_spring_security_check",
                    loginCredentials,
                    auth=auth,
                    verify=False,
                    proxies={}
                )
                r = s.get(
                    ocUrl + "rest/clinicaldata/" + dataFormat + "/view/" + method,
                    auth=auth,
                    verify=False,
                    proxies={}
                )
            else:
                proxies = {"http": "http://" + self._proxyHost + ":" + self._proxyPort, "https": "https://" + self._proxyHost + ":" + self._proxyPort}
                self._logger.info("Connecting with application defined proxy: " + str(proxies))
                r = s.post(
                    ocUrl + "j_spring_security_check",
                    loginCredentials,
                    auth=auth,
                    verify=False,
                    proxies=proxies
                )
                r = s.get(
                    ocUrl + "rest/clinicaldata/" + dataFormat + "/view/" + method,
                    auth=auth,
                    verify=False,
                    proxies=proxies
                )
        # Use system proxy
        else:
            proxies = requests.utils.get_environ_proxies("https://" + self.__ip)
            self._logger.info("Using system proxy variables (no proxy applied): " + str(proxies))
            r = s.post(
                ocUrl + "j_spring_security_check",
                loginCredentials,
                auth=auth,
                verify=False,
                proxies=proxies
            )
            r = s.get(
                ocUrl + "rest/clinicaldata/" + dataFormat + "/view/" + method,
                auth=auth,
                verify=False,
                proxies=proxies
            )

        return r
