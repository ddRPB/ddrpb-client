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

# JSON
import json

# PyQt - threading
from PyQt4 import QtCore

# Data model
from services.DataPersistanceService import CrfFieldAnnotationSerializer
from services.DataPersistanceService import DefaultAccountSerializer
from services.DataPersistanceService import PartnerSiteSerializer
from services.DataPersistanceService import PullDataRequestSerializer
from services.DataPersistanceService import RTStructTypeSerializer
from services.DataPersistanceService import RTStructSerializer
from services.DataPersistanceService import StudySerializer
from services.DataPersistanceService import OCStudySerializer
from services.DataPersistanceService import SoftwareSerializer

# Domain
from domain.Subject import Subject
from domain.Event import Event
from domain.Crf import Crf
from domain.CrfDicomField import CrfDicomField

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

    def __init__(self, ip, port, userDetails):
        """Default constructor
        """
        self._logger = logging.getLogger(__name__)
        logging.config.fileConfig("logging.ini", disable_existing_loggers=False)

        # Server IP and port as members
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
        self._pullDataRequestSerializer = PullDataRequestSerializer()
        self._partnerSiteSerializer = PartnerSiteSerializer()
        self._defaultAccountSerializer = DefaultAccountSerializer()
        self._studySerializer = StudySerializer()
        self._ocStudySerializer = OCStudySerializer()
        self._crfFieldAnnotationSerializer = CrfFieldAnnotationSerializer()
        self._rtStructTypeSerializer = RTStructTypeSerializer()
        self._rtStructSerializer = RTStructSerializer()
        self._softwareSerializer = SoftwareSerializer()

########  ########   #######  ########  ######## ########  ######## #### ########  ######
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##    ##
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##
########  ########  ##     ## ########  ######   ########     ##     ##  ######    ######
##        ##   ##   ##     ## ##        ##       ##   ##      ##     ##  ##             ##
##        ##    ##  ##     ## ##        ##       ##    ##     ##     ##  ##       ##    ##
##        ##     ##  #######  ##        ######## ##     ##    ##    #### ########  ######

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

    def authenticateUser(self, username, password):
        method = "/api/v1/authenticateUser/"
        result = None

        site = "MySiteForAuthorisation"

        s = requests.Session()
        s.headers.update({
            "Content-Type": "application/json",
            "Site": site,
            "Username": username,
            "Password": password
        })

        auth = None
        if self._proxyAuthEnabled:
            auth = HTTPBasicAuth(self._proxyAuthLogin, self._proxyAuthPassword)
            self._logger.info("Connecting with authentication: " + str(self._proxyAuthLogin))

        # Application proxy enabled
        if self._proxyEnabled:
            if self._noProxy != "" and self._noProxy is not whitespace and self._noProxy in "https://" + self.__ip:
                self._logger.info("Connecting without proxy because of no proxy: " + self._noProxy)
                r = s.get(
                    "https://" + self.__ip + ":" + self.__port + self.__application + method,
                    auth=auth,
                    verify=False,
                    proxies={}
                )
            else:
                proxies = {"http": "http://" + self._proxyHost + ":" + self._proxyPort, "https": "https://" + self._proxyHost + ":" + self._proxyPort}
                self._logger.info("Connecting with application defined proxy: " + str(proxies))
                r = s.get(
                    "https://" + self.__ip + ":" + self.__port + self.__application + method,
                    auth=auth,
                    verify=False,
                    proxies=proxies
                )
        # Use system proxy
        else:
            proxies = requests.utils.get_environ_proxies("https://" + self.__ip)
            self._logger.info("Using system proxy variables (no proxy applied): " + str(proxies))
            r = s.get(
                "https://" + self.__ip + ":" + self.__port + self.__application + method,
                auth=auth,
                verify=False,
                proxies=proxies
            )

        if r.status_code == 200:
            result = self._defaultAccountSerializer.deserialize(r.json())

        if result is not None:
            return result.isenabled
        else:
            return False

    def getMyDefaultAccount(self):
        """
        """
        method = "/api/v1/getMyDefaultAccount/"
        result = None

        r = self._sentRequest(method)

        if r.status_code == 200:
            result = self._defaultAccountSerializer.deserialize(r.json())
        else:
            self._logger.info("Cound not retrieve RPB default account entity.")

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

    def getDicomStudyCrfAnnotationsForStudy(self, studyid):
        method = "/api/v1/getDicomStudyCrfAnnotationsForStudy/" + str(studyid)
        results = []

        r = self._sentRequest(method)

        if r.status_code == 200:
            listOfDicst = r.json()
            for dic in listOfDicst:
                obj = self._crfFieldAnnotationSerializer.deserialize(dic)
                results.append(obj) 

        return results

    def getDicomPatientCrfAnnotationsForStudy(self, studyid):
        method = "/api/v1/getDicomPatientCrfAnnotationsForStudy/" + str(studyid)
        results = []

        r = self._sentRequest(method)

        if r.status_code == 200:
            listOfDicst = r.json()
            for dic in listOfDicst:
                obj = self._crfFieldAnnotationSerializer.deserialize(dic)
                results.append(obj)

        return results

    def getDicomReportCrfAnnotationsForStudy(self, studyid):
        """
        """
        method = "/api/v1/getDicomReportCrfAnnotationsForStudy/" + str(studyid)
        results = []

        r = self._sentRequest(method)

        if r.status_code == 200:
            listOfDicst = r.json()
            for dic in listOfDicst:
                obj = self._crfFieldAnnotationSerializer.deserialize(dic)
                results.append(obj)

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

########     ###    ########  ######## ##    ## ######## ########      ######  #### ######## ########  ######
##     ##   ## ##   ##     ##    ##    ###   ## ##       ##     ##    ##    ##  ##     ##    ##       ##    ##
##     ##  ##   ##  ##     ##    ##    ####  ## ##       ##     ##    ##        ##     ##    ##       ##
########  ##     ## ########     ##    ## ## ## ######   ########      ######   ##     ##    ######    ######
##        ######### ##   ##      ##    ##  #### ##       ##   ##            ##  ##     ##    ##             ##
##        ##     ## ##    ##     ##    ##   ### ##       ##    ##     ##    ##  ##     ##    ##       ##    ##
##        ##     ## ##     ##    ##    ##    ## ######## ##     ##     ######  ####    ##    ########  ######

    def getAllPartnerSites(self):
        """
        """
        method = "/api/v1/getAllPartnerSites/"
        results = []

        r = self._sentRequest(method)

        if r.status_code == 200:
            listOfDicst = r.json()
            for dic in listOfDicst:
                obj = self._partnerSiteSerializer.deserialize(dic)
                results.append(obj)

        return results

    def getAllPartnerExceptName(self, sitename):
        method = "/api/v1/getAllPartnerExceptName/" + sitename
        results = []

        r = self._sentRequest(method)

        if r.status_code == 200:
            listOfDicst = r.json()
            for dic in listOfDicst:
                obj = self._partnerSiteSerializer.deserialize(dic)
                results.append(obj)

        return results

    def getPartnerSiteByName(self, sitename):
        method = "/api/v1/getPartnerSiteByName/" + sitename
        result = None

        r = self._sentRequest(method)

        if r.status_code == 200:
            result = self._partnerSiteSerializer.deserialize(r.json())

        return result

########  ##     ## ##       ##          ########     ###    ########    ###    
##     ## ##     ## ##       ##          ##     ##   ## ##      ##      ## ##   
##     ## ##     ## ##       ##          ##     ##  ##   ##     ##     ##   ##  
########  ##     ## ##       ##          ##     ## ##     ##    ##    ##     ## 
##        ##     ## ##       ##          ##     ## #########    ##    ######### 
##        ##     ## ##       ##          ##     ## ##     ##    ##    ##     ## 
##         #######  ######## ########    ########  ##     ##    ##    ##     ## 

    def getAllPullDataRequestsFromSite(self, sitename):
        method = "/api/v1/getAllPullDataRequestsFromSite/" + sitename
        results = []

        r = self._sentRequest(method)

        if r.status_code == 200:
            listOfDicst = r.json()
            for dic in listOfDicst:
                obj = self._pullDataRequestSerializer.deserialize(dic)
                results.append(obj)

        return results

    def getAllPullDataRequestsToSite(self, sitename):
        method = "/api/v1/getAllPullDataRequestsToSite/" + sitename
        results = []

        r = self._sentRequest(method)

        if r.status_code == 200:
            listOfDicst = r.json()
            for dic in listOfDicst:
                obj = self._pullDataRequestSerializer.deserialize(dic)
                results.append(obj)

        return results

 #######  ########  ######## ##    ##     ######  ##       #### ##    ## ####  ######     ###
##     ## ##     ## ##       ###   ##    ##    ## ##        ##  ###   ##  ##  ##    ##   ## ##
##     ## ##     ## ##       ####  ##    ##       ##        ##  ####  ##  ##  ##        ##   ##
##     ## ########  ######   ## ## ##    ##       ##        ##  ## ## ##  ##  ##       ##     ##
##     ## ##        ##       ##  ####    ##       ##        ##  ##  ####  ##  ##       #########
##     ## ##        ##       ##   ###    ##    ## ##        ##  ##   ###  ##  ##    ## ##     ##
 #######  ##        ######## ##    ##     ######  ######## #### ##    ## ####  ######  ##     ##

    #TODO: deprecate, load this directly from OC rest service
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

    #TODO: deprecate, load this directly from OC rest service
    def getCrfItemValue(self, studyid, subjectPid, studyEventOid, studyEventRepeatKey, formOid, itemOid):
        """
        """
        method = "/api/v2/getCrfItemValue/" + studyid + "/" + subjectPid + "/" + studyEventOid + "/" + studyEventRepeatKey + "/" + formOid + "/" + itemOid

        r = self._sentRequest(method)

        if r.status_code == 200:
            value = r.json()["itemValue"]

        return value

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

        return ocPasswordHash

    def getOCStudyByIdentifier(self, identifier):
        """Get OC study by its identifier
        """
        method = "/api/v1/getOCStudyByIdentifier/" + identifier 
        result = None

        r = self._sentRequest(method)

        if r.status_code == 200:
            result = self._ocStudySerializer.deserialize(r.json())

        return result

    def getUserActiveStudy(self, username):
        """Load user active OC study
        """
        method = "/api/v1/getUserActiveStudy/" + username 
        result = None

        r = self._sentRequest(method)

        if r.status_code == 200:
            result = self._ocStudySerializer.deserialize(r.json())

        return result

    def changeUserActiveStudy(self, username, activeStudyId):
        """Change user active OC study
        """
        method = "/api/v1/changeUserActiveStudy/" + username + "/" + str(activeStudyId)
        result = None

        r = self._sentRequest(method)

        if r.status_code == 200:
            dic = r.json()
            result = dic["result"]
            if result == "true":
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

    def getAllSubjectsDicomData(self, studyIdentifier):
        """Get an overview of patients with their DICOM studies beloging to specific trial
        """
        method = "/api/v1/studies/" + studyIdentifier + "/dicomStudies"

        results = []

        r = self._sentRequest(method)

        if r.status_code == 200:
            if "Patients" in r.json():
                patientsData = r.json()["Patients"]
                if type(patientsData) is list:
                    for p in patientsData:
                        subject = Subject()
                        subject.oid = p["SubjectKey"]
                        subject.studySubjectId = p["StudySubjectID"]
                        subject.uniqueIdentifier = p["UniqueIdentifier"]

                        if "Studies" in p:
                            dicomData = p["Studies"]
                            if type(dicomData) is list:
                                for dcm in dicomData:
                                    studyItem = CrfDicomField()
                                    studyItem.eventOid = dcm["StudyEventOid"]
                                    studyItem.oid = dcm["ItemOid"]
                                    studyItem.label = dcm["Label"]
                                    studyItem.value = dcm["StudyInstanceUid"]
                                    studyItem.webApiUrl = dcm["WebApiUrl"]

                                    subject.dicomData.append(studyItem)

                        results.append(subject)

        return results

    def unzipDicomData(self, url):
        """Get an overview of files withing specific DICOM study
        """
        method = "/unzip"

        results = []

        r = self._requestUrlGet(url + method)

        if r.status_code == 200:
            if "Patients" in r.json():
                patientsData = r.json()["Patients"]
                if type(patientsData) is list:
                    for p in patientsData:
                        subject = Subject()
                        subject.uniqueIdentifier = p["UniqueIdentifier"]

                        if "Studies" in p:
                            dicomData = p["Studies"]
                            if type(dicomData) is list:
                                for dcm in dicomData:
                                    studyItem = CrfDicomField()
                                    studyItem.value = dcm["StudyInstanceUid"]

                                    if "Files" in dcm:
                                        filesData = dcm["Files"]
                                        if type(filesData) is list:
                                            for f in filesData:
                                                studyItem.fileUrls.append(f["WebApiUrl"])

                                    subject.dicomData.append(studyItem)

                        results.append(subject)

        return results

    def clearDicomData(self, url):
        """Clean up unzipped DICOM study data from server
        """
        method = "/clean"

        result = False

        r = self._requestUrlGet(url + method)

        if r.status_code == 200:
            dic = r.json()
            result = dic["result"]
            if result == "true":
                result = True
            else:
                result = False

        return result

    def downloadDicomData(self, fileUrl, downloadDir):
        """Download DICOM file
        """
        r = self._requestUrlGet(fileUrl)

        index = fileUrl.find("/dcm/")
        localFilename = fileUrl[index+5:]
        try:
            os.remove(downloadDir + os.sep + localFilename)
        except OSError:
            pass

        with open(downloadDir + os.sep + localFilename, "wb") as handle:
            for block in r.iter_content(1024):
                if not block:
                    break

                handle.write(block)

        result = downloadDir + os.sep + localFilename

        return result

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

        r = self._postRequest(method, dcmFile, "application/octet-stream")
        self._logger.info(str(r.status_code))
        result = pickle.loads(r.content)

        return result

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
            "Username": self.__userDetails.username,
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
            url = "https://%s:%s%s%s" % (self.__ip, str(self.__port), self.__application, method.encode("utf-8"))
        else:
            url = "https://%s:%s%s%s" % (self.__ip, str(self.__port), self.__application, method)

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

    def _requestUrlGet(self, url):
        """Generic GET request to URL (not necessarily the the main server URL, can be URL of different site)
        """
        # TODO: in this case the user should be RPB platform user
        # one platform DD is contacting WebAPI of different platform e.g. FR
        s = requests.Session()
        s.headers.update({
            "Content-Type": "application/json",
            "Username": self.__userDetails.username,
            "Password": self.__userDetails.password,
            "Clearpass": self.__userDetails.clearpass
        })

        auth = None
        if self._proxyAuthEnabled:
            auth = HTTPBasicAuth(self._proxyAuthLogin, self._proxyAuthPassword)
            self._logger.info("Connecting with authentication: " + str(self._proxyAuthLogin))

        # Ensure that URL ends with /
        if not url.endswith("/"):
            url += "/"

        # Prevent duplicate https:// in url
        if url.startswith("https://"):
            url = url.replace("https://", "")

        # TODO there is something wrong with URL that server is providing so I am fixing it here
        url = url.replace("//", "/")

        # Application proxy enabled
        if self._proxyEnabled:
            if self._noProxy != "" and self._noProxy is not whitespace and self._noProxy in "https://" + self.__ip:
                self._logger.info("Connecting without proxy because of no proxy: " + self._noProxy)
                self._logger.debug("https://" + url)
                r = s.get("https://" + url, auth=auth, verify=False, proxies={})
            else:
                proxies = {"http": "http://" + self._proxyHost + ":" + self._proxyPort, "https": "https://" + self._proxyHost + ":" + self._proxyPort}
                self._logger.info("Connecting with application defined proxy: " + str(proxies))
                self._logger.debug("https://" + url)
                r = s.get("https://" + url, auth=auth, verify=False, proxies=proxies)
        # Use system proxy
        else:
            proxies = requests.utils.get_environ_proxies("https://" + self.__ip)
            self._logger.info("Using system proxy variables (no proxy applied): " + str(proxies))
            self._logger.debug("https://" + url)
            r = s.get("https://" + url, auth=auth, verify=False, proxies=proxies)

        return r

    def _postRequest(self, method, body, contentType):
        """Generic POST request to RadPlanBio server
        """
        s = requests.Session()
        s.headers.update({
                "Content-Type": contentType,
                "Content-Length": str(len(body)),
                "Site": "MySiteForAuthorisation",
                "Username": self.__userDetails.username,
                "Password": self.__userDetails.password
            }
        )

        auth = None
        if self._proxyAuthEnabled:
            auth = HTTPBasicAuth(self._proxyAuthLogin, self._proxyAuthPassword)
            self._logger.info("Connecting with authentication: %s" % str(self._proxyAuthLogin))

        # Unicode for URL depends on python version
        if sys.version < "3":
            url = "https://%s:%s%s" % (self.__ip, str(self.__port), self.__application + method.encode("utf-8"))
        else:
            url = "https://%s:%s%s" % (self.__ip, str(self.__port), self.__application + method)

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

    def _ocRequest(self, ocUrl, method):
        """Generic OpenClinica (RESTfull URL) GET request
        """
         # xml, html
        dataFormat = "json"

        s = requests.Session()
        loginCredentials = {"j_username": self.__userDetails.username, "j_password": self.__userDetails.clearpass}

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
