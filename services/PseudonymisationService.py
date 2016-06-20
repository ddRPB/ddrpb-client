#----------------------------------------------------------------------
#------------------------------ Modules -------------------------------
# Logging
from datetime import datetime
import json
import logging
import logging.config
import webbrowser

from domain.Identificator import Identificator
from domain.Person import Person
import requests
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth


# JSON
# Date
# Web browser
# HTTP
# Domain
#----------------------------------------------------------------------
class PseudonymisationService():
    """Service ussing REST mainzelliste pseudonymisation interface
    """

    #----------------------------------------------------------------------
    #--------------------------- Constructors -----------------------------

    def __init__(self, connectInfo):
        """Default construtor

        """
        # Logger
        self.logger = logging.getLogger(__name__)
        logging.config.fileConfig('logging.ini', disable_existing_loggers=False)

        self.connectInfo = connectInfo;

    #----------------------------------------------------------------------
    #----------------------------- Methods --------------------------------
    #----------------------------------------------------------------------
    #----------------------------- Sessions -------------------------------

    def newSession(self):
        """Obtain session id
        """
        endpoint = "sessions"
        headers = {'mainzellisteApiKey': self.connectInfo.apiKey }

        r = requests.post(self.connectInfo.baseUrl + endpoint, headers=headers)

        sessionId = r.json()["sessionId"]
        uri = r.json()["uri"]

        self.logger.debug("session id = " + sessionId)
        self.logger.debug("uri = " + uri)

        return sessionId, uri


    def deleteSession(self, sessionId):
        """Delete session with specified session id
        """
        endpoint = "sessions/"
        headers = {'mainzellisteApiKey': self.connectInfo.apiKey }

        r = requests.delete(self.connectInfo.baseUrl + endpoint + sessionId, headers=headers)

        print r.status_code

    #----------------------------------------------------------------------
    #----------------------------- Patient Tokens -------------------------

    def newPatientToken(self, sessionId):
        """Obtain token id for creation of a new patient
        """
        endpoint = "sessions/"
        method = "addPatient"

        # TODO: maybe I have to load this
        callback = "http://g89rtpsrv.med.tu-dresden.de:8080/radplanbio-1.0.0-SNAPSHOT/"

        data = { 'type': method, 'data': { 'callback': callback } }

        s = requests.Session()
        s.headers.update({ 'Content-Type': 'application/json' })
        s.headers.update({ 'mainzellisteApiKey': self.connectInfo.apiKey })

        r = s.post(self.connectInfo.baseUrl + endpoint + sessionId + "/tokens", data=json.dumps(data))

        tokenId = r.json()["tokenId"]
        uri = r.json()["uri"]

        self.logger.debug("token id = " + tokenId)
        self.logger.debug("uri = " + uri)

        return tokenId, uri


    def readPatientToken(self, sessionId, pid):
        """
        """
        endpoint = "sessions/"
        method = "readPatient"

        # TODO: maybe I have to load this
        callback = "http://g89rtpsrv.med.tu-dresden.de:8080/radplanbio-1.0.0-SNAPSHOT/"

        data = { 'type': method, 'data': { 'callback': callback, 'id' : pid } }

        s = requests.Session()
        s.headers.update({ 'Content-Type': 'application/json' })
        s.headers.update({ 'Accept': 'application/json' })
        s.headers.update({ 'mainzellisteApiKey': self.connectInfo.apiKey })

        r = s.post(self.connectInfo.baseUrl + endpoint + sessionId + "/tokens", data=json.dumps(data))

        tokenId = r.json()["tokenId"]
        uri = r.json()["uri"]

        self.logger.debug("token id = " + tokenId)
        self.logger.debug("uri = " + uri)

        return tokenId, uri

    #----------------------------------------------------------------------
    #----------------------------- Create Patient PIDs --------------------

    def createPatientForm(self, tokenId):
        """Open form for entering new patient in the web viewer (did now work for my case)
        """
        endpoint = "html/createPatient"
        queryString = "?tokenId="
        webbrowser.open_new(self.connectInfo.baseUrl +  endpoint + queryString + tokenId)


    def createPatientJson(self, tokenId, person):
        """Create new patient PID accroding to data
        """
        endpoint = "patients"

        # Create a HTML form data
        # mandatory vorname, nachname, geburtstag, geburtsmonat, geburtsjahr,
        # optional geburtsname, plz, ort

        params = { 'tokenId' : tokenId }
        data = { 'vorname': person.firstname, 'nachname': person.surname, 'geburtstag' : '{:02d}'.format(person.birthdate.day), 'geburtsmonat' : '{:02d}'.format(person.birthdate.month), 'geburtsjahr' : '{:0d}'.format(person.birthdate.year), 'geburtsname' : person.birthname, 'plz' : person.zipcode, 'ort' : person.city }

        print str(data)

        s = requests.Session()
        s.headers.update({ 'Content-Type': 'application/x-www-form-urlencoded' })
        s.headers.update({ 'Accept': 'application/json'} )

        r = s.post(self.connectInfo.baseUrl + endpoint, params=params, data=data)

        print r.status_code
        print r.text

        try:
            newId = r.json()["newId"]
            tentative = r.json()["tentative"]
            uri = r.json()["uri"]

            self.logger.debug("new id = " + newId)
            self.logger.debug("tentative = " + str(tentative))
            self.logger.debug("uri = " + uri)
        except:
            newId = ""
            tentative = False

        return newId, tentative


    def createSurePatientJson(self, tokenId, person):
        """Create patient PID according to data

        In this case you are sure about a data so new patient is created
        If possible match is found
        """
        endpoint = "patients"

        # Create a HTML form data
        # mandatory vorname, nachname, geburtstag, geburtsmonat, geburtsjahr,
        # optional geburtsname, plz, ort

        # Provide this field to confirm patient
        # sureness

        params = { 'tokenId' : tokenId }
        data = { 'vorname': person.firstname, 'nachname': person.surname, 'geburtstag' : '{:02d}'.format(person.birthdate.day), 'geburtsmonat' : '{:02d}'.format(person.birthdate.month), 'geburtsjahr' : '{:0d}'.format(person.birthdate.year), 'geburtsname' : person.birthname, 'plz' : person.zipcode, 'ort' : person.city, 'sureness' : 'True' }

        print str(data)

        s = requests.Session()
        s.headers.update({ 'Content-Type': 'application/x-www-form-urlencoded' })
        s.headers.update({ 'Accept': 'application/json'} )

        r = s.post(self.connectInfo.baseUrl + endpoint, params=params, data=data)

        print r.status_code
        print r.text

        try:
            newId = r.json()["newId"]
            tentative = r.json()["tentative"]
            uri = r.json()["uri"]

            self.logger.debug("new id = " + newId)
            self.logger.debug("tentative = " + str(tentative))
            self.logger.debug("uri = " + uri)
        except:
            newId = ""
            tentative = False

        return newId, tentative


    def resolveTempIds(self, tid):
        """Not finished

        """
        endpoint = "patients/tempid"
        callback = "http://g89rtpsrv.med.tu-dresden.de:8080/radplanbio-1.0.0-SNAPSHOT/"
        params = { 'callback' : callback, 'data' : {'subjects' : { 'ids' : [  tid ] } } }

        s = requests.Session()
        s.headers.update({ 'Content-Type': 'application/json' })
        s.headers.update({ 'Accept': 'application/json'})

        r = s.get(self.connectInfo.baseUrl + endpoint + "?callback=localhost&data=%7B%27subjects%27%20%3A%20%7B%20%27ids%27%20%3A%20%5B%20%20%22" + tid + "%22%20%5D%20%7D%20%7D")

        self.logger.debug(r.url)
        self.logger.debug(r.text)

    #----------------------------------------------------------------------
    #-------------------------------- Get Patients ------------------------

    def getPatient(self, tid):
        """Get patient by token ID
        """
        endpoint = "patients/tempid/" + tid

        s = requests.Session()
        s.headers.update({ 'Accept': 'application/json'})

        r = s.get(self.connectInfo.baseUrl + endpoint)

        resultCode = r.status_code

        print r.json()

        person = None

        person = Person()
        person.firstname = r.json()['vorname']['value']
        person.surename = r.json()['nachname']['value']
        day = int(r.json()['geburtstag']['value'])
        month = int(r.json()['geburtsmonat']['value'])
        year = int(r.json()['geburtsjahr']['value'])
        person.birthdate = datetime(year, month, day)
        person.city = r.json()['ort']['value']
        person.zipcode = r.json()['plz']['value']

        return person


    def getAllPatients(self):
        """Get list of all patients IDs

        Has to have an admin access to tomcat
        """

        endpoint = "patients"
        callback = "http://g89rtpsrv.med.tu-dresden.de:8080/radplanbio-1.0.0-SNAPSHOT/"

        s = requests.Session()
        s.headers.update({ 'Accept': 'application/json'})

        auth = HTTPDigestAuth(self.connectInfo.userName, self.connectInfo.password)

        r = s.get(self.connectInfo.baseUrl + endpoint, auth=auth)

        ids = r.json()

        # Create an object representation for PIDs
        identificators = []
        for patientsIds in ids :
            for ident in patientsIds :
                idString =  ident["idString"]
                idType = ident["type"]
                isTentative = ident["tentative"]

                if (idType == "pid") :
                    identificator = Identificator(idString, idType, isTentative)
                    identificators.append(identificator)

        for pid in identificators:
            print pid.idString

        return identificators

    #----------------------------------------------------------------------
    #-------------------------------- Self methods ------------------------

    def __str__(self):
        """ToString

        Print the class itself
        """
        #TODO: print connect info
        return "PseudonymisationService: "

