#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# System
import sys

# Hashing
import hashlib

# PyQt
from PyQt4 import QtGui, QtCore

# Dialogs
from gui.SettingsDialog import SettingsDialog

# Contexts
from contexts.UserDetails import UserDetails
from contexts.ConfigDetails import ConfigDetails

# Resource images for buttons
if sys.version < "3":
    from gui import images_rc

########  ####    ###    ##        #######   ######
##     ##  ##    ## ##   ##       ##     ## ##    ##
##     ##  ##   ##   ##  ##       ##     ## ##
##     ##  ##  ##     ## ##       ##     ## ##   ####
##     ##  ##  ######### ##       ##     ## ##    ##
##     ##  ##  ##     ## ##       ##     ## ##    ##
########  #### ##     ## ########  #######   ######


class LoginDialog(QtGui.QDialog):
    """Login Dialog Class
    """

    def __init__(self, svcHttp):
        """Default constructor
        """
        # Setup GUI
        QtGui.QDialog.__init__(self)
        self.setWindowTitle("RadPlanBio - Login")
        appIconPath = ":/images/rpb-icon.jpg"
        appIcon = QtGui.QIcon()
        appIcon.addPixmap(QtGui.QPixmap(appIconPath))
        self.setWindowIcon(appIcon)

        toolBarButtonSize = 15

        configIconPath = ':/images/config.png'
        configIcon = QtGui.QIcon(configIconPath)
        configIcon.addPixmap(QtGui.QPixmap(configIconPath))

        # Config button
        self.btnConfig = QtGui.QPushButton()
        self.btnConfig.setIcon(configIcon)
        self.btnConfig.setToolTip("Configuration")
        self.btnConfig.setIconSize(QtCore.QSize(toolBarButtonSize, toolBarButtonSize))
        self.btnConfig.setMinimumWidth(toolBarButtonSize)
        self.btnConfig.clicked.connect(self.settingsPopup)

        # Dialog layout root
        rootLayout = QtGui.QVBoxLayout(self)

        # Login grid
        loginLayout = QtGui.QGridLayout()
        loginLayout.setSpacing(10)
        rootLayout.addLayout(loginLayout)

        # Connection
        lblConnection = QtGui.QLabel("Connection:")
        self.txtConnection = QtGui.QLineEdit()
        self.txtConnection.setText(ConfigDetails().rpbHost + "/" + ConfigDetails().rpbApplication)
        self.txtConnection.setMinimumWidth(300)
        self.txtConnection.setDisabled(True)

        # User label
        lblUsername = QtGui.QLabel("Username:")
        self.txtUsername = QtGui.QLineEdit()

        # Password label
        lblPassword = QtGui.QLabel("Password:")
        self.txtPassword = QtGui.QLineEdit()
        self.txtPassword.setEchoMode(QtGui.QLineEdit.Password)

        # Login button
        loginIconPath = ':/images/login.png'
        loginIcon = QtGui.QIcon()
        loginIcon.addPixmap(QtGui.QPixmap(loginIconPath))

        self.btnLogin = QtGui.QPushButton("Login")
        self.btnLogin.setIcon(loginIcon)
        self.btnLogin.setToolTip("Login")
        self.btnLogin.setIconSize(QtCore.QSize(toolBarButtonSize, toolBarButtonSize))
        self.btnLogin.clicked.connect(self.handleLogin)

        # Add to connection layout
        loginLayout.addWidget(lblConnection, 0, 0)
        loginLayout.addWidget(self.txtConnection, 0, 1)
        loginLayout.addWidget(self.btnConfig, 0, 2)

        loginLayout.addWidget(lblUsername, 1, 0)
        loginLayout.addWidget(self.txtUsername, 1, 1, 1, 2)

        loginLayout.addWidget(lblPassword, 2, 0)
        loginLayout.addWidget(self.txtPassword, 2, 1, 1, 2)

        loginLayout.addWidget(self.btnLogin, 3, 1, 1, 2)

        self.txtUsername.setFocus()

        # Services
        self.svcHttp = svcHttp

        # ViewModel
        self.userName = ""
        self.password = ""

##     ##    ###    ##    ## ########  ##       ######## ########   ######  
##     ##   ## ##   ###   ## ##     ## ##       ##       ##     ## ##    ## 
##     ##  ##   ##  ####  ## ##     ## ##       ##       ##     ## ##       
######### ##     ## ## ## ## ##     ## ##       ######   ########   ######  
##     ## ######### ##  #### ##     ## ##       ##       ##   ##         ## 
##     ## ##     ## ##   ### ##     ## ##       ##       ##    ##  ##    ## 
##     ## ##     ## ##    ## ########  ######## ######## ##     ##  ###### 
    
    def handleLogin(self):
        """Send authenticate user message to site server
        """
        username = str(self.txtUsername.text())
        password = str(self.txtPassword.text())
        passwordHash = hashlib.sha1(password.encode("utf-8")).hexdigest()

        try:
            UserDetails().username = username
            UserDetails().clearpass = password
            UserDetails().password = passwordHash

            defaultAccount = self.svcHttp.getMyDefaultAccount()
            successful = defaultAccount is not None and defaultAccount.isenabled

            if successful:
                UserDetails().apikey = defaultAccount.apikey
                self.accept()
            else:
                QtGui.QMessageBox.warning(self, "Error", "Wrong username or password.")
        except:
            QtGui.QMessageBox.warning(
                self, "Error", "Cannot communicate with the server, no network connection or the server is not running."
            )


    def settingsPopup(self):
        """Show settings dialog
        """
        self.dialog = SettingsDialog(self)
        self.dialog.exec_()
