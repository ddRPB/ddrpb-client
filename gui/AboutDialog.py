#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# Standard
import platform

# PyQt
from PyQt4 import QtGui
from PyQt4.QtCore import Qt

# Dialogs
from gui.LicenseDialog import LicenseDialog
from gui.KeyDialog import KeyDialog

# Contexts
from contexts.ConfigDetails import ConfigDetails

# Services
from services.CryptoService import CryptoService

########  ####    ###    ##        #######   ######
##     ##  ##    ## ##   ##       ##     ## ##    ##
##     ##  ##   ##   ##  ##       ##     ## ##
##     ##  ##  ##     ## ##       ##     ## ##   ####
##     ##  ##  ######### ##       ##     ## ##    ##
##     ##  ##  ##     ## ##       ##     ## ##    ##
########  #### ##     ## ########  #######   ######


class AboutDialog(QtGui.QDialog):
    """About Dialog Class
    """

    def __init__(self, parent=None):
        """Default Constructor
        """
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("About")

        size = 100
        lblIcon = QtGui.QLabel()
        appIconPath = ":/images/rpb-icon"
        myPixmap = QtGui.QPixmap(appIconPath)
        myScaledPixmap = myPixmap.scaled(size, size, Qt.KeepAspectRatio)
        lblIcon.setPixmap(myScaledPixmap)

        copyright = u"\u00A9"

        self.svcCrypto = CryptoService()

        # Dialog layout root
        rootLayout = QtGui.QVBoxLayout(self)

        # About Text
        lblAppName = QtGui.QLabel(ConfigDetails().name)
        lblAppVersion = QtGui.QLabel("version: " + ConfigDetails().version)
        lblPlatform = QtGui.QLabel("system: " + platform.system())
        lblLogFile = QtGui.QLabel("log: " + ConfigDetails().logFilePath)
        lblKeyFile = QtGui.QLabel("key: " + ConfigDetails().keyFilePath)
        lblEmptyLine = QtGui.QLabel("")
        lblAppCopyright = QtGui.QLabel(copyright + " " + ConfigDetails().copyright)

        # Show encryption key
        # 32 bytes long key for AES-256
        self.btnKey = QtGui.QPushButton("Encryption Key")
        if self.svcCrypto.keyExists():
            self.btnKey.setToolTip("Show base64 encoded 32 bytes long key used for AES-256 encryption")
            self.btnKey.setDisabled(False)
        else:
            self.btnKey.setToolTip("Encryption key does not exist")
            self.btnKey.setDisabled(True)
        self.btnKey.clicked.connect(self.btnKeyClicked)

        # Show Licence
        self.btnLicense = QtGui.QPushButton("License")
        self.btnLicense.setToolTip("Show software license")
        self.btnLicense.clicked.connect(self.btnLicenseClicked)

        # Layout
        rootLayout.addWidget(lblIcon)
        rootLayout.addWidget(lblAppName)
        rootLayout.addWidget(lblAppVersion)
        rootLayout.addWidget(lblPlatform)
        rootLayout.addWidget(lblLogFile)
        rootLayout.addWidget(lblKeyFile)
        rootLayout.addWidget(self.btnKey)
        rootLayout.addWidget(self.btnLicense)
        rootLayout.addWidget(lblEmptyLine)
        rootLayout.addWidget(lblAppCopyright)

##     ##    ###    ##    ## ########  ##       ######## ########   ######  
##     ##   ## ##   ###   ## ##     ## ##       ##       ##     ## ##    ## 
##     ##  ##   ##  ####  ## ##     ## ##       ##       ##     ## ##       
######### ##     ## ## ## ## ##     ## ##       ######   ########   ######  
##     ## ######### ##  #### ##     ## ##       ##       ##   ##         ## 
##     ## ##     ## ##   ### ##     ## ##       ##       ##    ##  ##    ## 
##     ## ##     ## ##    ## ########  ######## ######## ##     ##  ###### 

    def btnLicenseClicked(self):
        """Show license dialog
        """
        self.dialog = LicenseDialog(self)
        self.dialog.exec_()

    def btnKeyClicked(self):
        """Show encryption key dialog
        """
        self.dialog = KeyDialog(self.svcCrypto.key, self)
        self.dialog.exec_()
