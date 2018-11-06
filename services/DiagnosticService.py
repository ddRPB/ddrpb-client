#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# Sys
import sys
import os
import platform

# Requests
import requests
import socket

# Logging
import logging
import logging.config

# Context
from contexts.ConfigDetails import ConfigDetails

# PAC - there is no 64bit version available
if platform.system() != "Windows":
    import pacparser

# HTTP
if sys.version < "3":
    import urllib2
else:
    import urllib

# Disable insecure connection warnings
#import urllib3
#urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Singleton
from utils.SingletonType import SingletonType

 ######  ######## ########  ##     ## ####  ######  ########
##    ## ##       ##     ## ##     ##  ##  ##    ## ##
##       ##       ##     ## ##     ##  ##  ##       ##
 ######  ######   ########  ##     ##  ##  ##       ######
      ## ##       ##   ##    ##   ##   ##  ##       ##
##    ## ##       ##    ##    ## ##    ##  ##    ## ##
 ######  ######## ##     ##    ###    ####  ######  ########


class DiagnosticService:
    """This service is providing connection diagnostic features
    """

    __metaclass__ = SingletonType

    def __init__(self):
        """Default constructor
        """
        # Setup logger - use logging config file
        self._logger = logging.getLogger(__name__)
        logging.config.fileConfig("logging.ini", disable_existing_loggers=False)

    def systemProxyDiagnostic(self):
        """Diagnose network info and store in the log
        """
        self._logger.info("Checking proxy setting within environment.")

        if sys.version < "3":
            self._logger.info("Proxies detected within urllib2:")
            proxies = urllib2.getproxies()
            self._logger.info(proxies)
        else:
            self._logger.info("Proxies detected within urllib:")
            proxies = urllib.request.getproxies()
            self._logger.info(proxies)


        self._logger.info("Proxies detected within requests:")
        proxies = requests.utils.get_environ_proxies("")
        self._logger.info(proxies)

    def wpadProxyDiagnostic(self):
        """Diagnose WPAD/PAC and store in the log         
        """
        # I don't support windows for this
        if platform.system() != "Windows":

            self._logger.info("Auto detection of proxy settings WPAD/PAC.")

            # Create a list of wpadURLs to lookup
            wpadUrls = []
            tempUrl = socket.getfqdn()
            hasDot = tempUrl.find(".") > 0
            while hasDot:
                index = tempUrl.find(".")
                tempUrl = tempUrl[index + 1:]
                wpadUrls.append("http://wpad." + tempUrl + "/wpad.dat")

                hasDot = tempUrl.find(".") > 0

            # Remove the last url -> it is national domain
            wpadUrls.pop()

            self._logger.info("WPAD URLs to try: " + str(wpadUrls))

            for wpadUrl in wpadUrls:
                try:
                    wpadRequest = requests.get(wpadUrl)

                    if wpadRequest.status_code == 200:

                        if wpadRequest.text is not None:
                            wpadFile = open("wpad.dat", "w")
                            wpadFile.write(wpadRequest.text)
                            wpadFile.close()

                            pacparser.init()
                            pacparser.parse_pac("wpad.dat")
                            os.remove("wpad.dat")

                            try:
                                proxyString = pacparser.find_proxy("https://" + ConfigDetails().rpbHost)
                                self._logger.info("Proxies detected with WPAD: " + proxyString)

                                proxylist = proxyString.split(";")
                                proxies = []

                                while proxylist:
                                    proxy = proxylist.pop(0).strip()
                                    if proxy[0:5].upper() == "PROXY":
                                        proxy = proxy[6:].strip()
                                        if self.isProxyAlive(proxy):
                                            proxies.append(proxy)
                                    return proxies
                                break
                            except:
                                self._logger.error("Could not determine proxy using PAC")
                        else:
                            self._logger.error("wpad.dat not found")

                    else:
                        self._logger.error(wpadUrl + " does not exists")
                except:
                    self._logger.error("Request for WPAD failed: " + wpadUrl)

    def isProxyAlive(self, proxy):
        """Test whether the connection with proxy can be established
        """
        host_port = proxy.split(":")
        if len(host_port) != 2:
            self._logger.error("Proxy host is not defined as host:port")
            return False

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        try:
            s.connect((host_port[0], int(host_port[1])))
        except Exception as e:
            self._logger.error("Proxy %s is not accessible" % proxy)
            self._logger.error(str(e))
            return False

        s.close()
        return True
