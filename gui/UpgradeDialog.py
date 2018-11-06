#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# System
import sys

# Logging
import logging
import logging.config

# PyQt
from PyQt4 import QtGui, QtCore

# Version numbers comparison
from distutils.version import LooseVersion

# Services
from services.HttpConnectionService import HttpConnectionService
from services.UpgradeService import UpgradeService

# Contexts
from contexts.ConfigDetails import ConfigDetails
from contexts.UserDetails import UserDetails

# Workers
from workers.WorkerThread import WorkerThread

########  ####    ###    ##        #######   ######
##     ##  ##    ## ##   ##       ##     ## ##    ##
##     ##  ##   ##   ##  ##       ##     ## ##
##     ##  ##  ##     ## ##       ##     ## ##   ####
##     ##  ##  ######### ##       ##     ## ##    ##
##     ##  ##  ##     ## ##       ##     ## ##    ##
########  #### ##     ## ########  #######   ######


class UpgradeDialog(QtGui.QDialog):
    """Upgrade Dialog Class
    """

    def __init__(self, parent=None):
        """Default Constructor
        """
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("Upgrade")

        # Setup logger - use config file
        self.logger = logging.getLogger(__name__)
        logging.config.fileConfig("logging.ini", disable_existing_loggers=False)

        toolBarButtonSize = 15

        upgradeIconPath = ":/images/upgrade.png"
        upgradeIcon = QtGui.QIcon()
        upgradeIcon.addPixmap(QtGui.QPixmap(upgradeIconPath))

        # List of worker threads
        self._threadPool = []

        # Dialog layout root
        rootLayout = QtGui.QVBoxLayout(self)

        # Init services
        self.prepareServices()

        # Load version from server
        self._latestSoftware = self.svcHttp.getLatestSoftware(ConfigDetails().identifier)
        if self._latestSoftware != None:
            latestVersion = str(self._latestSoftware.version)
        else:
            latestVersion = ConfigDetails().version

        # Client current versions
        lblCurrentVersion = QtGui.QLabel("Installed client version: %s" % ConfigDetails().version)
        lblLatestVersion = QtGui.QLabel("Latest client version: %s" % latestVersion)

        if sys.version < "3":
            cmp = lambda x, y: LooseVersion(x).__cmp__(y)
        else:
            cmp = lambda x, y: LooseVersion(x)._cmp(y)

        canUpgrade = cmp(ConfigDetails().version, latestVersion)

        self.btnUpgrade = QtGui.QPushButton("Upgrade")
        self.btnUpgrade.setIcon(upgradeIcon)
        self.btnUpgrade.setToolTip("Upgrade")
        if canUpgrade >= 0:
            self.btnUpgrade.setDisabled(True)
        self.btnUpgrade.setIconSize(QtCore.QSize(toolBarButtonSize, toolBarButtonSize))
        self.btnUpgrade.clicked.connect(self.upgradeClicked)

        self.textBrowserProgress = QtGui.QTextBrowser()

        # Layouting
        rootLayout.addWidget(lblCurrentVersion)
        rootLayout.addWidget(lblLatestVersion)
        rootLayout.addWidget(self.textBrowserProgress)
        rootLayout.addWidget(self.btnUpgrade)

##     ##    ###    ##    ## ########  ##       ######## ########   ######  
##     ##   ## ##   ###   ## ##     ## ##       ##       ##     ## ##    ## 
##     ##  ##   ##  ####  ## ##     ## ##       ##       ##     ## ##       
######### ##     ## ## ## ## ##     ## ##       ######   ########   ######  
##     ## ######### ##  #### ##     ## ##       ##       ##   ##         ## 
##     ## ##     ## ##   ### ##     ## ##       ##       ##    ##  ##    ## 
##     ## ##     ## ##    ## ########  ######## ######## ##     ##  ###### 

    def handleDestroyed(self):
        """Kill runnign threads
        """
        self.logger.debug("Destroying Upload dialog")
        for thread in self._threadPool:
            thread.terminate()
            thread.wait()
            self._logger.debug("Thread killed.")
    
    def upgradeClicked(self):
        """Upgrade button clicked handler
        """
        self.btnUpgrade.setDisabled(True)
        self.textBrowserProgress.clear()
        self.textBrowserProgress.append("Wait please:")
        self.textBrowserProgress.append("downloading new client...")

        self._threadPool.append(WorkerThread(self.svcHttp.downloadRadPlanBioClient, self._latestSoftware))

        # Connect slots
        self.connect(
            self._threadPool[len(self._threadPool) - 1],
            QtCore.SIGNAL("finished(QVariant)"),
            self.downloadFinished
        )

        # Start thread
        self._threadPool[len(self._threadPool) - 1].start()

 ######   #######  ##     ## ##     ##    ###    ##    ## ########   ######
##    ## ##     ## ###   ### ###   ###   ## ##   ###   ## ##     ## ##    ##
##       ##     ## #### #### #### ####  ##   ##  ####  ## ##     ## ##
##       ##     ## ## ### ## ## ### ## ##     ## ## ## ## ##     ##  ######
##       ##     ## ##     ## ##     ## ######### ##  #### ##     ##       ##
##    ## ##     ## ##     ## ##     ## ##     ## ##   ### ##     ## ##    ##
 ######   #######  ##     ## ##     ## ##     ## ##    ## ########   ######

    def downloadFinished(self, data):
        """Download thread finished
        """
        self.textBrowserProgress.append("upgrade preparation...")
        self._threadPool.append(WorkerThread(self.svcUpgrade.preUpgrade))

        # Connect slots
        self.connect(
            self._threadPool[len(self._threadPool) - 1],
            QtCore.SIGNAL("finished(QVariant)"),
            self.prepareFinished
        )

        # Start thread
        self._threadPool[len(self._threadPool) - 1].start()

    def prepareFinished(self, data):
        """Prepare download thread finished
        """
        self.textBrowserProgress.append("upgrade will continue after restart...")        

        msg = "RadPlaBio client need to be restarted to continue the upgrade! (if not automatically please restart the client manually)"
        reply = QtGui.QMessageBox.information(self, "Restart", msg, QtGui.QMessageBox.Ok)

        if reply == QtGui.QMessageBox.Ok:
            self.parent().restart()

    def prepareServices(self):
        """Prepare services for this module
        """
        # HTTP connection to RadPlanBio server (Database)
        self.svcHttp = HttpConnectionService(ConfigDetails().rpbHost, ConfigDetails().rpbHostPort, UserDetails())
        self.svcHttp.application = ConfigDetails().rpbApplication

        if ConfigDetails().proxyEnabled:
            self.svcHttp.setupProxy(ConfigDetails().proxyHost, ConfigDetails().proxyPort, ConfigDetails().noProxy)
        if ConfigDetails().proxyAuthEnabled:
            self.svcHttp.setupProxyAuth(ConfigDetails().proxyAuthLogin, ConfigDetails().proxyAuthPassword)

        self.svcUpgrade = UpgradeService()

        # Read partner site of logged user
        self.mySite = self.svcHttp.getMyDefaultAccount().partnersite
