#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# Standard
import sys
import os
import platform

# Logging
import logging
import logging.config

# Services
from services.DiagnosticService import DiagnosticService

# PyQt
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import QT_VERSION_STR
from PyQt4.Qt import PYQT_VERSION_STR

# Contexts
from contexts.ConfigDetails import ConfigDetails
from contexts.OCUserDetails import OCUserDetails
from contexts.UserDetails import UserDetails

# Version numbers comparison
from distutils.version import LooseVersion

# UI
import gui.messages
from gui.LoginDialog import LoginDialog
from gui.mainClientUI import MainWindowUI

# Services
from services.AppConfigurationService import AppConfigurationService
from services.HttpConnectionService import HttpConnectionService
from services.UpgradeService import UpgradeService
from services.OCConnectInfo import OCConnectInfo
from services.OCWebServices import OCWebServices

##      ## #### ##    ## ########   #######  ##      ##
##  ##  ##  ##  ###   ## ##     ## ##     ## ##  ##  ##
##  ##  ##  ##  ####  ## ##     ## ##     ## ##  ##  ##
##  ##  ##  ##  ## ## ## ##     ## ##     ## ##  ##  ##
##  ##  ##  ##  ##  #### ##     ## ##     ## ##  ##  ##
##  ##  ##  ##  ##   ### ##     ## ##     ## ##  ##  ##
 ###  ###  #### ##    ## ########   #######   ###  ###

EXIT_CODE_RESTART = -123456789  # Any value


class MainWindow(QMainWindow, MainWindowUI):
    """Main window view shell
    Main view shell where the other modules views are registered
    """

    def __init__(self, parent=None):
        """Constructor of main application window
        """
        QMainWindow.__init__(self, parent)

        self._logger = logging.getLogger(__name__)
        logging.config.fileConfig("logging.ini", disable_existing_loggers=False)

        self.setupUi(self)
        self.statusBar.showMessage("Ready")

        self._logger.info("RadPlanBio host: %s:%s" % (ConfigDetails().rpbHost, str(ConfigDetails().rpbHostPort)))
        self._logger.info("Partner site proxy: %s:%s [%s]" % (ConfigDetails().proxyHost, str(ConfigDetails().proxyPort), str(ConfigDetails().proxyEnabled)))

        self.svcHttp = HttpConnectionService(ConfigDetails().rpbProtocol, ConfigDetails().rpbHost, ConfigDetails().rpbHostPort, UserDetails())
        self.svcHttp.application = ConfigDetails().rpbApplication
        if ConfigDetails().proxyEnabled:
            self.svcHttp.setupProxy(ConfigDetails().proxyHost, ConfigDetails().proxyPort, ConfigDetails().noProxy)
        if ConfigDetails().proxyAuthEnabled:
            self.svcHttp.setupProxyAuth(ConfigDetails().proxyAuthLogin, ConfigDetails().proxyAuthPassword)

        self.lblRPBConnection.setText("[%s]@%s/%s:%s" % (UserDetails().username, ConfigDetails().rpbHost, ConfigDetails().rpbApplication, str(ConfigDetails().rpbHostPort)))

        defaultAccount = None
        try:
            defaultAccount = self.svcHttp.getMyDefaultAccount()
        except Exception as err:
            self._logger.info("HTTP communication failed: %s" % str(err))

        if defaultAccount is not None and defaultAccount.ocusername and defaultAccount.ocusername != "":
            ocUsername = defaultAccount.ocusername

            # TODO: deprecate loading from getOCAccountPasswordHash - old python server style
            ocPasswordHash = self.svcHttp.getOCAccountPasswordHash()
            if ocPasswordHash is None:
                ocPasswordHash = defaultAccount.ocpasswordhash

            ocSoapPublicUrl = defaultAccount.partnersite.edc.soappublicurl

            successful = False
            try:
                # Create connection artifact to OC
                self.ocConnectInfo = OCConnectInfo(ocSoapPublicUrl, ocUsername)
                self.ocConnectInfo.setPasswordHash(ocPasswordHash)

                if ConfigDetails().proxyEnabled:
                    self.ocWebServices = OCWebServices(
                        self.ocConnectInfo,
                        ConfigDetails().proxyHost,
                        ConfigDetails().proxyPort,
                        ConfigDetails().noProxy,
                        ConfigDetails().proxyAuthLogin,
                        ConfigDetails().proxyAuthPassword
                    )
                else:
                    self.ocWebServices = OCWebServices(self.ocConnectInfo)
                
                successful, studies = self.ocWebServices.listAllStudies()
            except:
                self._logger.info("HTTP OC communication failed.", exc_info=True)

            if successful:
                ocUserDetails = OCUserDetails()
                ocUserDetails.username = ocUsername
                ocUserDetails.passwordHash = ocPasswordHash
                ocUserDetails.connected = True
            else:
                QtGui.QMessageBox.warning(self, "Error", "Wrong username or password!")

    def closeEvent(self, event):
        """Cleaning up
        """
        self._logger.debug("Destroying the application.")

    def quit(self):
        """Quit (exit) event handler
        """
        reply = QtGui.QMessageBox.question(
            self,
            "Question",
            gui.messages.QUE_EXIT,
            QtGui.QMessageBox.Yes,
            QtGui.QMessageBox.No
        )

        if reply == QtGui.QMessageBox.Yes:
            self._logger.debug("Destroying the application.")
            QtGui.qApp.quit()

##     ## ######## ######## ##     ##  #######  ########   ######  
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ## 
#### #### ##          ##    ##     ## ##     ## ##     ## ##       
## ### ## ######      ##    ######### ##     ## ##     ##  ######  
##     ## ##          ##    ##     ## ##     ## ##     ##       ## 
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ## 
##     ## ########    ##    ##     ##  #######  ########   ######  

    def connectToOpenClinica(self):
        """Connection to OpenClinica SOAP web services
        """
        if not OCUserDetails().connected:
            QtGui.QMessageBox.warning(self, "Error", "Cannot connect to RadPlanBio - OpenClinica SOAP services!")
        else:
            return True

##     ##    ###    #### ##    ##
###   ###   ## ##    ##  ###   ##
#### ####  ##   ##   ##  ####  ##
## ### ## ##     ##  ##  ## ## ##
##     ## #########  ##  ##  ####
##     ## ##     ##  ##  ##   ###
##     ## ##     ## #### ##    ##


def startup():
    """Start the client/upgrade
    """
    logger = logging.getLogger(__name__)
    logging.config.fileConfig("logging.ini", disable_existing_loggers=False)

    # Apply app configuration according the config file
    configure()
    # Internationalisation
    # translate()

    # Log the version of client (useful for remote debugging)
    logger.info("RPB desktop client version: %s" % ConfigDetails().version)
    logger.info("RPB protocol: %s" % ConfigDetails().rpbProtocol)
    logger.info("RPB upload service: %s" % ConfigDetails().rpbUploadService)
    logger.info("Qt version: %s" % QT_VERSION_STR)
    logger.info("PyQt version: %s" % PYQT_VERSION_STR)

    # Client is compiled with stow-rs switch on adapt the configuration connection info
    if ConfigDetails().rpbUploadService == "stow-rs":

        # Only remove rpbApplication string when it is set and it is not testing installation (without reverse proxy)
        if ConfigDetails().rpbApplication != "" and ConfigDetails().rpbHostPort != "9000":

            logger.info("Configuration connection info will be adapted to RPB-portal as backend.")

            # Wipe the application statement (not necessary when portal is backend)
            section = "RadPlanBioServer"
            option = "application"
            ConfigDetails().rpbApplication = ""
            AppConfigurationService().set(section, option, "")

            # Save and reconfigure
            AppConfigurationService().saveConfiguration()
            configure()
        else:
            logger.info("Configuration connection info already adapted for RPB-portal as backend.")
    else:
        logger.info("Configuration connection info points to legacy RPB-server backend.")

    # Basic services
    DiagnosticService().systemProxyDiagnostic()

    svcHttp = HttpConnectionService(ConfigDetails().rpbProtocol, ConfigDetails().rpbHost, ConfigDetails().rpbHostPort, UserDetails())
    svcHttp.application = ConfigDetails().rpbApplication

    if ConfigDetails().proxyEnabled:
        svcHttp.setupProxy(ConfigDetails().proxyHost, ConfigDetails().proxyPort, ConfigDetails().noProxy)
    if ConfigDetails().proxyAuthEnabled:
        svcHttp.setupProxyAuth(ConfigDetails().proxyAuthLogin, ConfigDetails().proxyAuthPassword)

    # App log    
    app = QtGui.QApplication(sys.argv)
    ConfigDetails().logFilePath = "%s%sclient.log" % (os.getcwd() , os.path.sep)
    ConfigDetails().keyFilePath = "%s%skey.pkl" % (os.getcwd() , os.path.sep)

    # Startup
    if ConfigDetails().isUpgrading is None or ConfigDetails().isUpgrading == "False":
        # Check whether upgrade was done
        showNotify = False
        if ConfigDetails().upgradeFinished is not None and ConfigDetails().upgradeFinished == "True":
            # Start upgrade procedure
            svcUpgrade = UpgradeService()
            svcUpgrade.cleanup()
            msg = "RadPlanBio client has been successfully upgraded"
            showNotify = True

        # Continue with standard login dialog
        loginDialog = LoginDialog(svcHttp)
        if loginDialog.exec_() == QtGui.QDialog.Accepted:

            # Main application window
            ui = MainWindow()
            ui.show()

            # Upgrade completed notification
            if showNotify:
                reply = QtGui.QMessageBox.information(ui, "Upgrade completed", msg, QtGui.QMessageBox.Ok)
                if reply == QtGui.QMessageBox.Ok:
                    showNotify = False

            # Automatic update check at startup
            if ConfigDetails().startupUpdateCheck:
                
                # Load version from server, user details updated in login dialog
                latestSoftware = svcHttp.getLatestSoftware(ConfigDetails().identifier)
                
                if latestSoftware is not None:
                    latestVersion = str(latestSoftware.version)
                else:
                    latestVersion = ConfigDetails().version

                if sys.version < "3":
                    cmp = lambda x, y: LooseVersion(x).__cmp__(y)
                else:
                    cmp = lambda x, y: LooseVersion(x)._cmp(y)

                canUpgrade = cmp(ConfigDetails().version, latestVersion)
                if canUpgrade < 0:
                    ui.upgradePopup()
                    
            currentExitCode = app.exec_()
            return currentExitCode
        else:
            QtGui.qApp.quit()
    else:
        # Start updater (RadPlanBio-update.exe)
        if platform.system() == "Windows":
            if os.path.isfile("./update/RadPlanBio-update.exe"):
                QtCore.QProcess.startDetached("./update/RadPlanBio-update.exe")
            else:
                QtCore.QProcess.startDetached("python ./update/mainUpdate.py")
        elif platform.system() == "Linux":
            if os.path.isfile("./update/RadPlanBio-update"):
                QtCore.QProcess.startDetached("./update/RadPlanBio-update")
            else:
                QtCore.QProcess.startDetached("python ./update/mainUpdate.py")
        else:
            QtCore.QProcess.startDetached("python ./update/mainUpdate.py")

        # Close this one
        QtGui.qApp.quit()


def main():
    """Main function
    """
    currentExitCode = EXIT_CODE_RESTART

    while currentExitCode == EXIT_CODE_RESTART:
        currentExitCode = 0
        currentExitCode = startup()

 ######   #######  ##    ## ######## ####  ######   
##    ## ##     ## ###   ## ##        ##  ##    ##  
##       ##     ## ####  ## ##        ##  ##        
##       ##     ## ## ## ## ######    ##  ##   #### 
##       ##     ## ##  #### ##        ##  ##    ##  
##    ## ##     ## ##   ### ##        ##  ##    ##  
 ######   #######  ##    ## ##       ####  ######   


def configure():
    """Read configuration settings from config file
    """
    appConfig = AppConfigurationService(ConfigDetails().configFileName)
    
    section = "RadPlanBioServer"
    if appConfig.hasSection(section):
        if appConfig.hasOption(section, "host"):
            ConfigDetails().rpbHost = appConfig.get(section)["host"]
        if appConfig.hasOption(section, "port"):
            ConfigDetails().rpbHostPort = appConfig.get(section)["port"]
        if appConfig.hasOption(section, "application"):
            ConfigDetails().rpbApplication = appConfig.get(section)["application"]

    section = "Proxy"
    if appConfig.hasSection(section):
        if appConfig.hasOption(section, "enabled"):
            ConfigDetails().proxyEnabled = appConfig.getboolean(section, "enabled")
        if appConfig.hasOption(section, "configuration"):
            ConfigDetails().proxyConfiguration = appConfig.get(section)["configuration"]

        # Automatic proxy detection
        if ConfigDetails().proxyConfiguration == "auto":
            # Detect proxy
            proxies = DiagnosticService().wpadProxyDiagnostic()
            # Proxies detected
            if proxies:
                host_port = proxies[0].split(":")
                ConfigDetails().proxyHost = str(host_port[0])
                ConfigDetails().proxyPort = int(host_port[1])

        # Manual proxy settings
        elif ConfigDetails().proxyConfiguration == "manual":
            if appConfig.hasOption(section, "host"):
                ConfigDetails().proxyHost = appConfig.get(section)["host"]
            if appConfig.hasOption(section, "port"):
                ConfigDetails().proxyPort = appConfig.get(section)["port"]
            if appConfig.hasOption(section, "noproxy"):
                ConfigDetails().noProxy = appConfig.get(section)["noproxy"]

    section = "Proxy-auth"
    if appConfig.hasSection(section):
        if appConfig.hasOption(section, "enabled"):
            ConfigDetails().proxyAuthEnabled = appConfig.getboolean(section, "enabled")
        if appConfig.hasOption(section, "login"):
            ConfigDetails().proxyAuthLogin = appConfig.get(section)["login"]
        if appConfig.hasOption(section, "password"):
            ConfigDetails().proxyAuthPassword = appConfig.get(section)["password"]

    section = "GUI"
    if appConfig.hasSection(section):
        if appConfig.hasOption(section, "main.width"):
            ConfigDetails().width = int(appConfig.get(section)["main.width"])
        if appConfig.hasOption(section, "main.height"):
            ConfigDetails().height = int(appConfig.get(section)["main.height"])

    section = "DICOM"
    if appConfig.hasSection(section):
        if appConfig.hasOption(section, "replacepatientnamewith"):
            ConfigDetails().replacePatientNameWith = appConfig.get(section)["replacepatientnamewith"]
        if appConfig.hasOption(section, "constpatientname"):
            ConfigDetails().constPatientName = appConfig.get(section)["constpatientname"]
        if appConfig.hasOption(section, "allowmultiplepatientids"):
            ConfigDetails().allowMultiplePatientIDs = appConfig.getboolean(section, "allowmultiplepatientids")
        if appConfig.hasOption(section, "retainpatientcharacteristicsoption"):
            ConfigDetails().retainPatientCharacteristicsOption = appConfig.getboolean(section, "retainpatientcharacteristicsoption")
        if appConfig.hasOption(section, "retaindeviceidentityoption"):
            ConfigDetails().retainDeviceIdentityOption = appConfig.getboolean(section, "retaindeviceidentityoption")
        if appConfig.hasOption(section, "retainlongfulldatesoption"):
            ConfigDetails().retainLongFullDatesOption = appConfig.getboolean(section, "retainlongfulldatesoption")
        if appConfig.hasOption(section, "retainstudyseriesdescriptions"):
            ConfigDetails().retainStudySeriesDescriptions = appConfig.getboolean(section, "retainstudyseriesdescriptions")
        if appConfig.hasOption(section, "autortstructmatch"):
            ConfigDetails().autoRTStructMatch = appConfig.getboolean(section, "autortstructmatch")
        if appConfig.hasOption(section, "autortstructref"):
            ConfigDetails().autoRTStructRef = appConfig.getboolean(section, "autortstructref")

    section = "SanityTests"
    if appConfig.hasSection(section):
        if appConfig.hasOption(section, "patientgendermatch"):
            ConfigDetails().patientGenderMatch = appConfig.getboolean(section, "patientgendermatch")
        if appConfig.hasOption(section, "patientdobmatch"):
            ConfigDetails().patientDobMatch = appConfig.getboolean(section, "patientdobmatch")

    section = "General"
    if appConfig.hasSection(section):
        if appConfig.hasOption(section, "startupupdatecheck"):
            ConfigDetails().startupUpdateCheck = appConfig.getboolean(section, "startupupdatecheck")

    section = "Temp"
    if appConfig.hasSection(section):
        if appConfig.hasOption(section, "isupgrading"):
            ConfigDetails().isUpgrading = appConfig.get(section)["isupgrading"]
        if appConfig.hasOption(section, "upgradefinished"):
            ConfigDetails().upgradeFinished = appConfig.get(section)["upgradefinished"]

####    ##    #######  ##    ## 
 ##   ####   ##     ## ###   ## 
 ##     ##   ##     ## ####  ## 
 ##     ##    #######  ## ## ## 
 ##     ##   ##     ## ##  #### 
 ##     ##   ##     ## ##   ### 
####  ######  #######  ##    ## 

# def translate():
    # """Internationalisation
    # """
    # translator = QtCore.QTranslator()
    # translator.load("qt_ru", QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    # app.installTranslator(translator)


if __name__ == '__main__':
    main()
