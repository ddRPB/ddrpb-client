#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# Logging
import logging
import logging.config

# SOAP
import pysimplesoap.client
from pysimplesoap.client import SoapClient
from pysimplesoap.simplexml import SimpleXMLElement
from pysimplesoap.transport import get_http_wrapper, set_http_wrapper

STUDYNAMESPACE = "http://openclinica.org/ws/data/v1"
STUDYACTION = "http://openclinica.org/ws/data/v1/"

 ######  ######## ########  ##     ## ####  ######  ########
##    ## ##       ##     ## ##     ##  ##  ##    ## ##
##       ##       ##     ## ##     ##  ##  ##       ##
 ######  ######   ########  ##     ##  ##  ##       ######
      ## ##       ##   ##    ##   ##   ##  ##       ##
##    ## ##       ##    ##    ## ##    ##  ##    ## ##
 ######  ######## ##     ##    ###    ####  ######  ########


class OCDataWsService:
    """SOAP import data web service to OpenClinica
    """

    def __init__(self, studyLocation, proxyStr, proxyUsr, proxyPass, isTrace):
        """Default Constructor
        """
        self._logger = logging.getLogger(__name__)
        logging.config.fileConfig("logging.ini", disable_existing_loggers=False)

        proxies = None

        if proxyStr:
            proxies = pysimplesoap.client.parse_proxy(proxyStr)
            self._logger.info("OC Data SOAP services with proxies: " + str(proxies))

        self._logger.info("OC Data SOAP services with auth: " + str(proxyUsr))

        if proxies:
            self.client = SoapClient(location=studyLocation,
                                     namespace=STUDYNAMESPACE,
                                     action=STUDYACTION,
                                     soap_ns='soapenv',
                                     ns="v1",
                                     trace=isTrace,
                                     proxy=proxies,
                                     username=proxyUsr,
                                     password=proxyPass)
        else:
            self.client = SoapClient(location=studyLocation,
                                     namespace=STUDYNAMESPACE,
                                     action=STUDYACTION,
                                     soap_ns='soapenv',
                                     ns="v1",
                                     trace=isTrace,
                                     username=proxyUsr,
                                     password=proxyPass)

        self._logger.info("OC Data SOAP services successfully initialised.")

##     ## ######## ######## ##     ##  #######  ########   ######  
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ## 
#### #### ##          ##    ##     ## ##     ## ##     ## ##       
## ### ## ######      ##    ######### ##     ## ##     ##  ######  
##     ## ##          ##    ##     ## ##     ## ##     ##       ## 
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ## 
##     ## ########    ##    ##     ##  #######  ########   ######  

    def wsse(self, userName, passwordHash):
        """Setup WSSE security
        """
        self.client['wsse:Security'] = {
            'wsse:UsernameToken': {
                'wsse:Username': userName,
                'wsse:Password': passwordHash,
            }
        }

    def importData(self, odm):
        """Import ODM XML formatted study data
        """
        odmXml = u"""<?xml version="1.0" encoding="UTF-8"?><importRequest>%s</importRequest>""" % odm.decode("utf-8")

        params = SimpleXMLElement(odmXml.encode('utf-8'))
        response = self.client.call("importRequest", params)

        return str(response.result)
