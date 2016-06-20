#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# System
import sys

# PyQT
from PyQt4 import QtGui, QtCore, uic

# Contexts
from contexts.ConfigDetails import ConfigDetails

# Resource images for buttons
from gui import images_rc

# Application Dialogs
from gui.AboutDialog import AboutDialog
from gui.SettingsDialog import SettingsDialog
from gui.UpgradeDialog import UpgradeDialog

# GUI Messages
import gui.messages

# Application modules GUI
from gui.DicomUploadModule import DicomUploadModule
from gui.DicomDownloadModule import DicomDownloadModule
from gui.DicomLookupModule import DicomLookupModule

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

##      ## #### ##    ## ########   #######  ##      ## 
##  ##  ##  ##  ###   ## ##     ## ##     ## ##  ##  ## 
##  ##  ##  ##  ####  ## ##     ## ##     ## ##  ##  ## 
##  ##  ##  ##  ## ## ## ##     ## ##     ## ##  ##  ## 
##  ##  ##  ##  ##  #### ##     ## ##     ## ##  ##  ## 
##  ##  ##  ##  ##   ### ##     ## ##     ## ##  ##  ## 
 ###  ###  #### ##    ## ########   #######   ###  ### 

EXIT_CODE_RESTART = -123456789 # any value

class MainWindowUI(object):
    """Main Window UI defintion
    """

    def setupUi(self, MainWindow):
        """ Prepare complete GUI for application main window
        """
        # Main window size
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(ConfigDetails().width, ConfigDetails().height)

        appIconPath =":/images/rpb-icon.jpg"
        appIcon = QtGui.QIcon()
        appIcon.addPixmap(QtGui.QPixmap(appIconPath))
        MainWindow.setWindowIcon(appIcon)

        # Central widget is main window in this case
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))

        # Prepare menu bar UI
        self._setupMenuBar(MainWindow)

        # Root layout manager for main window is stack panel
        rootLayout = QtGui.QVBoxLayout(self.centralwidget)

        # Prepare tool bar UI
        rootLayout.addLayout(self._setupToolBar())

        # Prepare main tab for modules UI
        rootLayout.addWidget(self._setupModulesTab())

        self._setupWelcomeModule()
        self._setupStatusBar(MainWindow)

        # Put defined central widget into ManWindow central widget
        self.retranslateUi(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Event handlers
        QtCore.QObject.connect(self, QtCore.SIGNAL("RESTARTREQUIRED"), self.restart)

##     ## ######## ##    ## ##     ## 
###   ### ##       ###   ## ##     ## 
#### #### ##       ####  ## ##     ## 
## ### ## ######   ## ## ## ##     ## 
##     ## ##       ##  #### ##     ## 
##     ## ##       ##   ### ##     ## 
##     ## ######## ##    ##  #######  

    def _setupMenuBar(self, MainWindow):
        """Create application menu bar
        """
        self.menuBar = QtGui.QMenuBar(MainWindow)
        self.menuBar.setObjectName(_fromUtf8("menuBar"))
        
        restartAction = QtGui.QAction(QtGui.QIcon(), "&Restart", self)
        restartAction.setShortcut("Ctrl+R")
        restartAction.setStatusTip("Restart application")
        restartAction.triggered.connect(self.restart)

        exitAction = QtGui.QAction(QtGui.QIcon("exit.png"), "&Exit", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.setStatusTip("Exit application")
        exitAction.triggered.connect(self.quit)

        fileMenu = self.menuBar.addMenu("&File")
        fileMenu.addAction(restartAction)
        fileMenu.addAction(exitAction)
        
        uploadAction = QtGui.QAction(QtGui.QIcon(), "&Upload", self)
        uploadAction.setShortcut("Ctrl+U")
        uploadAction.setStatusTip("Upload DICOM subject data")
        uploadAction.triggered.connect(self.loadUploadModule)

        downloadAction = QtGui.QAction(QtGui.QIcon(), "&Download", self)
        downloadAction.setShortcut("Ctrl+D")
        downloadAction.setStatusTip("Download DICOM subject data")
        downloadAction.triggered.connect(self.loadDownloadModule)

        queryAction = QtGui.QAction(QtGui.QIcon(), "&Lookup", self)
        queryAction.setShortcut("Ctrl+L")
        queryAction.setStatusTip("Lookup local DICOM data")
        queryAction.triggered.connect(self.loadQueryModule)

        deidentifyAction = QtGui.QAction(QtGui.QIcon(), "&Deidentify (offline)", self)
        deidentifyAction.setShortcut("Ctrl+A")
        deidentifyAction.setStatusTip("Deidentify DICOM data and save locally")
        #deidentifyAction.triggered.connect(self.loadDeidentifyModule)
        deidentifyAction.setDisabled(True)

        reidentifyAction = QtGui.QAction(QtGui.QIcon(), "R&eidentify (offline)", self)
        reidentifyAction.setShortcut("Ctrl+E")
        reidentifyAction.setStatusTip("Reidentify locally stored DICOM data")
        #reidentifyAction.triggered.connect()
        reidentifyAction.setDisabled(True)

        modulesMenu = self.menuBar.addMenu("&Modules")
        modulesMenu.addAction(uploadAction)
        modulesMenu.addAction(downloadAction)
        modulesMenu.addAction(queryAction)
        modulesMenu.addAction(deidentifyAction)
        modulesMenu.addAction(reidentifyAction)
        
        settingsAction = QtGui.QAction(QtGui.QIcon(), "&Settings", self)
        settingsAction.setShortcut("Ctrl+S")
        settingsAction.setStatusTip("Application settings")
        settingsAction.triggered.connect(self.settingsPopup)

        preferencesMenu = self.menuBar.addMenu("&Preferences")
        preferencesMenu.addAction(settingsAction)

        upgradeAction = QtGui.QAction(QtGui.QIcon(), "Up&grade", self)
        upgradeAction.setShortcut("Ctrl+G")
        upgradeAction.setStatusTip("Download application upgrade")
        upgradeAction.triggered.connect(self.upgradePopup)

        toolsMenu = self.menuBar.addMenu("&Tools")
        toolsMenu.addAction(upgradeAction)

        helpAction = QtGui.QAction(QtGui.QIcon(), "&Help Contents", self)
        helpAction.setShortcut("F1")
        helpAction.setStatusTip("Display RadPlanBio client user manual")
        helpAction.triggered.connect(self.helpPopup)

        aboutAction = QtGui.QAction(QtGui.QIcon(), "&About", self)
        aboutAction.setStatusTip("Display information about application")
        aboutAction.triggered.connect(self.aboutPopup)

        helpMenu = self.menuBar.addMenu("&Help")
        helpMenu.addAction(helpAction)
        helpMenu.addAction(aboutAction)

        MainWindow.setMenuBar(self.menuBar)

########  #######   #######  ##       ########     ###    ########  
   ##    ##     ## ##     ## ##       ##     ##   ## ##   ##     ## 
   ##    ##     ## ##     ## ##       ##     ##  ##   ##  ##     ## 
   ##    ##     ## ##     ## ##       ########  ##     ## ########  
   ##    ##     ## ##     ## ##       ##     ## ######### ##   ##   
   ##    ##     ## ##     ## ##       ##     ## ##     ## ##    ##  
   ##     #######   #######  ######## ########  ##     ## ##     ## 

    def _setupToolBar(self):
        """Create main window toolbar
        """
        toolBarButtonSize = 25

        modulesButtonsToolbar = QtGui.QHBoxLayout()

        # RadPlanBio connection
        connection = QtGui.QLabel("Connection:")
        self.lblRPBConnection = QtGui.QLabel("not implemented")

        # Module close button
        self.btnCloseModule = QtGui.QPushButton()
        self.btnCloseModule.setDisabled(True)
        self.btnCloseModule.setMaximumWidth(toolBarButtonSize)
        self.btnCloseModule.setMaximumHeight(toolBarButtonSize)
        self.btnCloseModule.clicked.connect(self.btnCloseModuleClicked)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+W"), self, self.btnCloseModuleClicked)

        closeModuleIconPath =":/images/x-mark.png"
        closeIcon = QtGui.QIcon()
        closeIcon.addPixmap(QtGui.QPixmap(closeModuleIconPath))

        self.btnCloseModule.setIcon(closeIcon)
        self.btnCloseModule.setToolTip("Close module [Ctrl+W]")
        self.btnCloseModule.setIconSize(QtCore.QSize(toolBarButtonSize, toolBarButtonSize))

        self.btnHelp = QtGui.QPushButton()
        self.btnHelp.setMaximumWidth(toolBarButtonSize)
        self.btnHelp.setMaximumHeight(toolBarButtonSize)
        self.btnHelp.clicked.connect(self.helpPopup)

        helpIconPath = ":/images/help.png"
        helpIcon = QtGui.QIcon()
        helpIcon.addPixmap(QtGui.QPixmap(helpIconPath))

        self.btnHelp.setIcon(helpIcon)
        self.btnHelp.setToolTip("Display RadPlanBio client user manual [F1]")
        self.btnHelp.setIconSize(QtCore.QSize(toolBarButtonSize, toolBarButtonSize))

        space = QtGui.QSpacerItem(200, 25)

        # Add all to layout
        modulesButtonsToolbar.addWidget(connection)
        modulesButtonsToolbar.addWidget(self.lblRPBConnection)
        modulesButtonsToolbar.addStretch(1)
        modulesButtonsToolbar.addWidget(self.btnHelp)
        modulesButtonsToolbar.addWidget(self.btnCloseModule)

        return modulesButtonsToolbar

##     ##  #######  ########  ##     ## ##       ########  ######  
###   ### ##     ## ##     ## ##     ## ##       ##       ##    ## 
#### #### ##     ## ##     ## ##     ## ##       ##       ##       
## ### ## ##     ## ##     ## ##     ## ##       ######    ######  
##     ## ##     ## ##     ## ##     ## ##       ##             ## 
##     ## ##     ## ##     ## ##     ## ##       ##       ##    ## 
##     ##  #######  ########   #######  ######## ########  ###### 
    
    def _setupModulesTab(self):
        """Create welcome module selection module
        """
        # Main Modules tab widget
        self.tabModules = QtGui.QTabWidget()
        self.tabModules.setTabPosition(QtGui.QTabWidget.South)

        # Create module tabs
        tabWelcomeModule = QtGui.QWidget()

        # Add tabs to widget
        self.tabModules.addTab(tabWelcomeModule, "Welcome")

        # Tab modules layout
        self.layoutWelcomeModule = QtGui.QVBoxLayout(tabWelcomeModule)

        return self.tabModules

##      ## ######## ##        ######   #######  ##     ## ######## 
##  ##  ## ##       ##       ##    ## ##     ## ###   ### ##       
##  ##  ## ##       ##       ##       ##     ## #### #### ##       
##  ##  ## ######   ##       ##       ##     ## ## ### ## ######   
##  ##  ## ##       ##       ##       ##     ## ##     ## ##       
##  ##  ## ##       ##       ##    ## ##     ## ##     ## ##       
 ###  ###  ######## ########  ######   #######  ##     ## ######## 
 
    def _setupWelcomeModule(self):
        """Create welcome module for application module loading
        """
        # Grid layout
        welcomeGrid = QtGui.QGridLayout()
        self.layoutWelcomeModule.addLayout(welcomeGrid)

        moduleButtonWidth = 100
        moduleButtonHeight = 200
        moduleButtonIconSize = 200

        # Upload
        self.btnLoadAssignDicomModule = QtGui.QPushButton()
        self.btnLoadAssignDicomModule.setObjectName("LoadAssignDicomModule")
        self.btnLoadAssignDicomModule.setMinimumWidth(moduleButtonWidth/3)
        self.btnLoadAssignDicomModule.setMinimumHeight(moduleButtonHeight)
        self.btnLoadAssignDicomModule.clicked.connect(self.btnLoadModuleClicked)

        loadAssignDicomModuleIconPath = ":/images/localDicomUpload.png"
        assignDicomIcon = QtGui.QIcon()
        assignDicomIcon.addPixmap(QtGui.QPixmap(loadAssignDicomModuleIconPath))
        self.btnLoadAssignDicomModule.setIcon(assignDicomIcon)
        self.btnLoadAssignDicomModule.setIconSize(QtCore.QSize(moduleButtonIconSize, moduleButtonIconSize))

        # Download
        self.btnLoadDownloadModule = QtGui.QPushButton()
        self.btnLoadDownloadModule.setObjectName("DownloadDicomModule")
        self.btnLoadDownloadModule.setMinimumWidth(moduleButtonWidth/3)
        self.btnLoadDownloadModule.setMinimumHeight(moduleButtonHeight)
        self.btnLoadDownloadModule.clicked.connect(self.btnLoadModuleClicked)

        loadDownloadModuleIconPath = ":/images/download.png"
        downloadIcon = QtGui.QIcon()
        downloadIcon.addPixmap(QtGui.QPixmap(loadDownloadModuleIconPath))
        self.btnLoadDownloadModule.setIcon(downloadIcon)
        self.btnLoadDownloadModule.setIconSize(QtCore.QSize(moduleButtonIconSize, moduleButtonIconSize))

        # DICOM node Query/Retrieve
        self.btnLoadQueryModule = QtGui.QPushButton()
        self.btnLoadQueryModule.setObjectName("QueryDicomModule")
        self.btnLoadQueryModule.setMinimumWidth(moduleButtonWidth/3)
        self.btnLoadQueryModule.setMinimumHeight(moduleButtonHeight)
        self.btnLoadQueryModule.clicked.connect(self.btnLoadModuleClicked)

        loadQueryModuleIconPath = ":/images/lookup.png"
        queryIcon = QtGui.QIcon()
        queryIcon.addPixmap(QtGui.QPixmap(loadQueryModuleIconPath))
        self.btnLoadQueryModule.setIcon(queryIcon)
        self.btnLoadQueryModule.setIconSize(QtCore.QSize(moduleButtonIconSize, moduleButtonIconSize))

        # Add to grid layout
        welcomeGrid.addWidget(self.btnLoadAssignDicomModule, 0, 0)
        welcomeGrid.addWidget(self.btnLoadDownloadModule, 1, 0)
        welcomeGrid.addWidget(self.btnLoadQueryModule, 0, 1)

 ######  ########    ###    ######## ##     ##  ######  
##    ##    ##      ## ##      ##    ##     ## ##    ## 
##          ##     ##   ##     ##    ##     ## ##       
 ######     ##    ##     ##    ##    ##     ##  ######  
      ##    ##    #########    ##    ##     ##       ## 
##    ##    ##    ##     ##    ##    ##     ## ##    ## 
 ######     ##    ##     ##    ##     #######   ###### 

    def _setupStatusBar(self, MainWindow):
        """Create status bar
        """
        self.statusBar = QtGui.QStatusBar(MainWindow)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))

        MainWindow.setStatusBar(self.statusBar)

    def enableIndefiniteProgess(self):
        """Show indefinite progress right in status bar
        """
        self.progressBar = QtGui.QProgressBar()
        self.progressBar.setMaximumHeight(16)
        self.progressBar.setMaximumWidth(200)
        self.progressBar.setTextVisible(False)
        self.statusBar.addPermanentWidget(self.progressBar, 0)

        self.progressBar.setValue(0)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(0)

    def disableIndefiniteProgess(self):
        """Hide indefinite progress from status bar
        """
        self.statusBar.removeWidget(self.progressBar);

##     ##    ###    ##    ## ########  ##       ######## ########   ######  
##     ##   ## ##   ###   ## ##     ## ##       ##       ##     ## ##    ## 
##     ##  ##   ##  ####  ## ##     ## ##       ##       ##     ## ##       
######### ##     ## ## ## ## ##     ## ##       ######   ########   ######  
##     ## ######### ##  #### ##     ## ##       ##       ##   ##         ## 
##     ## ##     ## ##   ### ##     ## ##       ##       ##    ##  ##    ## 
##     ## ##     ## ##    ## ########  ######## ######## ##     ##  ###### 

    def restart(self):
        """Restart event handler
        """
        QtGui.qApp.exit(EXIT_CODE_RESTART)

    def btnLoadModuleClicked(self):
        """ Load module handler
        """
        name = str(self.sender().objectName())
        self.btnCloseModule.setDisabled(False)

        if name == "LoadAssignDicomModule":
            self.loadUploadModule()
        elif name == "DownloadDicomModule":
            self.loadDownloadModule()
        elif name == "QueryDicomModule":
            self.loadQueryModule()

    def loadUploadModule(self):
        """Load DICOM data upload module
        """
        if self.connectToOpenClinica():
            self.tabDicomUploadModule = QtGui.QWidget()
            self.tabModules.addTab(self.tabDicomUploadModule, "Upload DICOM")
            self.layoutDicomUploadModule = QtGui.QVBoxLayout(self.tabDicomUploadModule)

            self.dicomUploadModule = DicomUploadModule(self.tabDicomUploadModule)
            self.layoutDicomUploadModule.addLayout(self.dicomUploadModule.rootLayout)

            self.tabModules.setCurrentIndex(self.tabModules.count() - 1)

            self.btnCloseModule.setDisabled(False)

    def loadDownloadModule(self):
        """Load DICOM data download module
        """
        if self.connectToOpenClinica():
            self.tabDicomDownloadModule = QtGui.QWidget()
            self.tabModules.addTab(self.tabDicomDownloadModule, "Download DICOM")
            self.layoutDicomDownloadModule = QtGui.QVBoxLayout(self.tabDicomDownloadModule)

            self.dicomDownloadModule = DicomDownloadModule(self.tabDicomDownloadModule)
            self.layoutDicomDownloadModule.addLayout(self.dicomDownloadModule.rootLayout)

            self.tabModules.setCurrentIndex(self.tabModules.count() - 1)

            self.btnCloseModule.setDisabled(False)

    def loadQueryModule(self):
        """Lookup DICOM data module
        """
        self.tabDicomLookupModule = QtGui.QWidget()
        self.tabModules.addTab(self.tabDicomLookupModule, "Lookup DICOM")
        self.layoutDicomLookupModule = QtGui.QVBoxLayout(self.tabDicomLookupModule)

        self.dicomLookupModule = DicomLookupModule(self.tabDicomLookupModule)
        self.layoutDicomLookupModule.addLayout(self.dicomLookupModule.rootLayout)

        self.tabModules.setCurrentIndex(self.tabModules.count() - 1)

        self.btnCloseModule.setDisabled(False)

    def btnCloseModuleClicked(self):
        """Close module handler
        """
        # Currently selected tab module
        index = self.tabModules.currentIndex()

        # Always keep welcome tab module
        if (index != 0):
            self.tabModules.widget(index).deleteLater()
            self.tabModules.widget(index).close()
            self.tabModules.removeTab(index)
        
        if self.tabModules.count() == 1:
            self.btnCloseModule.setDisabled(True)

        self.tabModules.setCurrentIndex(0)
        self.tabModules.setTabEnabled(0, True)

    def helpPopup(self):
        """Show online user manual
        """
        link = "https://radplanbio.uniklinikum-dresden.de/help/client/clientmanual.html"
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(link))

    def aboutPopup(self):
        """Show about dialog
        """
        self.dialog = AboutDialog(self)
        self.dialog.exec_()

    def settingsPopup(self):
        """Show settings dialog
        """
        self.dialog = SettingsDialog(self)
        self.dialog.exec_()

    def upgradePopup(self):
        """Show settings dialog
        """
        self.dialog = UpgradeDialog(self)
        self.dialog.exec_()

####    ##    #######  ##    ## 
 ##   ####   ##     ## ###   ## 
 ##     ##   ##     ## ####  ## 
 ##     ##    #######  ## ## ## 
 ##     ##   ##     ## ##  #### 
 ##     ##   ##     ## ##   ### 
####  ######  #######  ##    ##

    def retranslateUi(self, MainWindow):
        """UI text localisation
        """
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "RadPlanBio - Desktop Client", None, QtGui.QApplication.UnicodeUTF8))
        self.btnLoadAssignDicomModule.setText(QtGui.QApplication.translate("MainWindow", "Upload DICOM\ndata for existing\nstudy subject\nin RadPlanBio", None, QtGui.QApplication.UnicodeUTF8))
        self.btnLoadDownloadModule.setText(QtGui.QApplication.translate("MainWindow", "Download DICOM\ndata of existing\nstudy subjects\nin RadPlanBio", None, QtGui.QApplication.UnicodeUTF8))
        self.btnLoadQueryModule.setText(QtGui.QApplication.translate("MainWindow", "Lookup DICOM\ndata withing a\nDICOM node", None, QtGui.QApplication.UnicodeUTF8))