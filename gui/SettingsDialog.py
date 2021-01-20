#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# System
import sys
import platform

# Logging
import logging
import logging.config

# PyQt
from PyQt4 import QtGui, QtCore

# Contexts
from contexts.ConfigDetails import ConfigDetails

# Utils
from utils import first

# Services
from services.AppConfigurationService import AppConfigurationService
from services.DiagnosticService import DiagnosticService

########  ####    ###    ##        #######   ######
##     ##  ##    ## ##   ##       ##     ## ##    ##
##     ##  ##   ##   ##  ##       ##     ## ##
##     ##  ##  ##     ## ##       ##     ## ##   ####
##     ##  ##  ######### ##       ##     ## ##    ##
##     ##  ##  ##     ## ##       ##     ## ##    ##
########  #### ##     ## ########  #######   ######


class SettingsDialog(QtGui.QDialog):
    """Settings Dialog Class
    """

    def __init__(self, parent=None):
        """Default Constructor
        """
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("Settings")

        # Setup logger - use config file
        self._logger = logging.getLogger(__name__)
        logging.config.fileConfig('logging.ini', disable_existing_loggers=False)

        # Resources
        reloadIconRes = ":/images/reload.png"
        newIconRes = ":/images/new.png"
        editIconRes = ":/images/edit.png"
        deleteIconRes = ":/images/delete.png"
        saveIconRes = ":/images/save.png"
        cancelIconRes = ":/images/cancel.png"
        connectionIconRes = ":/images/connection.png"

        self.reloadIcon = QtGui.QIcon()
        self.reloadIcon.addPixmap(QtGui.QPixmap(reloadIconRes))

        self.newIcon = QtGui.QIcon()
        self.newIcon.addPixmap(QtGui.QPixmap(newIconRes))

        self.editIcon = QtGui.QIcon()
        self.editIcon.addPixmap(QtGui.QPixmap(editIconRes))

        self.saveIcon = QtGui.QIcon()
        self.saveIcon.addPixmap(QtGui.QPixmap(saveIconRes))

        self.cancelIcon = QtGui.QIcon()
        self.cancelIcon.addPixmap(QtGui.QPixmap(cancelIconRes))

        self.deleteIcon = QtGui.QIcon()
        self.deleteIcon.addPixmap(QtGui.QPixmap(deleteIconRes))

        self.connectionIcon = QtGui.QIcon()
        self.connectionIcon.addPixmap(QtGui.QPixmap(connectionIconRes))

        self._toolBarButtonSize = 25

        # Dialog layout root
        rootLayout = QtGui.QVBoxLayout(self)

        # Settings tab view
        self.tabSettings = QtGui.QTabWidget()
        rootLayout.addWidget(self.tabSettings)

        self.tabSettings.addTab(self._initGeneral(), "General")
        self.tabSettings.addTab(self._initGui(), "GUI")
        self.tabSettings.addTab(self._initDicom(), "DICOM")
        self.tabSettings.addTab(self._initSanityTests(), "Sanity Tests")

        # Command buttons
        rootLayout.addWidget(self._initButtons())

##     ##    ###    ##    ## ########  ##       ######## ########   ######
##     ##   ## ##   ###   ## ##     ## ##       ##       ##     ## ##    ##
##     ##  ##   ##  ####  ## ##     ## ##       ##       ##     ## ##
######### ##     ## ## ## ## ##     ## ##       ######   ########   ######
##     ## ######### ##  #### ##     ## ##       ##       ##   ##         ##
##     ## ##     ## ##   ### ##     ## ##       ##       ##    ##  ##    ##
##     ## ##     ## ##    ## ########  ######## ######## ##     ##  ######

    def btnOkClicked(self):
        """Ok button clicked
        """
        self._applySettings()
        self.close()

    def btnApplyClicked(self):
        """Apply button clicked
        """
        self._applySettings()

    def btnCancelClicked(self):
        """Cancel button clicked
        """
        self.close()

    def cbProxyEnabledChanged(self, state):
        """Visibility of proxy GUI settings changed
        """
        if state == QtCore.Qt.Checked:
            self.ddlProxyConfiguration.setDisabled(False)
            self._initProxyUiVisibility()
        else:
            self.ddlProxyConfiguration.setDisabled(True)
            self.txtProxyServer.setDisabled(True)
            self.txtProxyPort.setDisabled(True)
            self.txtNoProxy.setDisabled(True)

    def ddlProxyConfigurationChanged(self, index):
        """Visibility of proxy GUI settings changed
        """
        self._initProxyUiVisibility()

    def cbProxyAuthChanged(self, state):
        """Visibility of proxy auth GUI settings changed
        """
        if state == QtCore.Qt.Checked:
            self.txtProxyAuthLogin.setDisabled(False)
            self.txtProxyAuthPass.setDisabled(False)
        else:
            self.txtProxyAuthLogin.setDisabled(True)
            self.txtProxyAuthPass.setDisabled(True)

    def ddlPatNameReplaceChanged(self, index):
        """Visibility of const patient name GUI settings changed
        """
        if sys.version < "3":
            self.txtConstPatientName.setDisabled(
                str(self.ddlPatNameReplace.itemData(self.ddlPatNameReplace.currentIndex()).toString()) != "const"
            )
        else:
            self.txtConstPatientName.setDisabled(
                self.ddlPatNameReplace.itemData(self.ddlPatNameReplace.currentIndex()) != "const"
            )

########  ########  #### ##     ##    ###    ######## ########
##     ## ##     ##  ##  ##     ##   ## ##      ##    ##
##     ## ##     ##  ##  ##     ##  ##   ##     ##    ##
########  ########   ##  ##     ## ##     ##    ##    ######
##        ##   ##    ##   ##   ##  #########    ##    ##
##        ##    ##   ##    ## ##   ##     ##    ##    ##
##        ##     ## ####    ###    ##     ##    ##    ########

    def _initGeneral(self):
        """Initialise General UI tab
        """
        tabGeneral = QtGui.QWidget()
        layoutGeneral = QtGui.QVBoxLayout(tabGeneral)

        # Config file
        self.txtConfigFile = QtGui.QLineEdit()
        self.txtConfigFile.setText(str(ConfigDetails().configFileName))
        self.txtConfigFile.setDisabled(True)

        # Networking
        self.txtServer = QtGui.QLineEdit()
        self.txtServer.setMinimumWidth(250)
        self.txtServer.setText(str(ConfigDetails().rpbHost))

        self.txtPort = QtGui.QLineEdit()
        self.txtPort.setValidator(QtGui.QIntValidator(self.txtPort))
        self.txtPort.setText(str(ConfigDetails().rpbHostPort))

        self.txtServerApp = QtGui.QLineEdit()
        self.txtServerApp.setText(str(ConfigDetails().rpbApplication))

        # Startup Update
        self.cbStartupUpdateCheck = QtGui.QCheckBox()
        self.cbStartupUpdateCheck.setChecked(ConfigDetails().startupUpdateCheck)

        rpbGeneralLayout = QtGui.QFormLayout()
        rpbGeneralLayout.addRow("Configuration:", self.txtConfigFile)
        rpbGeneralLayout.addRow("Server:", self.txtServer)
        rpbGeneralLayout.addRow("Port:", self.txtPort)
        rpbGeneralLayout.addRow("Application:", self.txtServerApp)
        rpbGeneralLayout.addRow("Check for updates at startup:", self.cbStartupUpdateCheck)

        rpbGeneralGroup = QtGui.QGroupBox("RPB general")
        rpbGeneralGroup.setLayout(rpbGeneralLayout)

        # Proxy
        self.cbProxyEnabled = QtGui.QCheckBox()
        self.cbProxyEnabled.setChecked(ConfigDetails().proxyEnabled)
        self.cbProxyEnabled.stateChanged.connect(self.cbProxyEnabledChanged)

        options = []
        self.ddlProxyConfiguration = QtGui.QComboBox()

        if platform.system() != "Windows":
            self.ddlProxyConfiguration.addItem("Auto-detect", "auto")
            options.append("auto")

        self.ddlProxyConfiguration.addItem("Manual", "manual")
        options.append("manual")

        i = options.index(ConfigDetails().proxyConfiguration)
        self.ddlProxyConfiguration.setCurrentIndex(i)
        self.ddlProxyConfiguration.currentIndexChanged.connect(self.ddlProxyConfigurationChanged)

        self.txtProxyServer = QtGui.QLineEdit()
        self.txtProxyServer.setText(str(ConfigDetails().proxyHost))

        self.txtProxyPort = QtGui.QLineEdit()
        self.txtProxyPort.setValidator(QtGui.QIntValidator(self.txtProxyPort))
        self.txtProxyPort.setText(str(ConfigDetails().proxyPort))

        self.txtNoProxy = QtGui.QLineEdit() 
        self.txtNoProxy.setText(str(ConfigDetails().noProxy))

        proxyLayout = QtGui.QFormLayout()
        proxyLayout.addRow("Proxy enabled:", self.cbProxyEnabled)
        proxyLayout.addRow("Proxy configuration:", self.ddlProxyConfiguration)
        proxyLayout.addRow("Proxy server:", self.txtProxyServer)
        proxyLayout.addRow("Proxy port:", self.txtProxyPort)
        proxyLayout.addRow("No proxy:", self.txtNoProxy)

        proxyGroup = QtGui.QGroupBox("Proxy")
        proxyGroup.setLayout(proxyLayout)

        # Proxy auth
        self.cbProxyAuth = QtGui.QCheckBox()
        self.cbProxyAuth.setChecked(ConfigDetails().proxyAuthEnabled)
        self.cbProxyAuth.stateChanged.connect(self.cbProxyAuthChanged)

        self.txtProxyAuthLogin = QtGui.QLineEdit()
        self.txtProxyAuthLogin.setMinimumWidth(250)
        self.txtProxyAuthLogin.setText(str(ConfigDetails().proxyAuthLogin))

        self.txtProxyAuthPass = QtGui.QLineEdit()
        self.txtProxyAuthPass.setEchoMode(QtGui.QLineEdit.Password)
        self.txtProxyAuthPass.setText(str(ConfigDetails().proxyAuthPassword))

        proxyAuthLayout = QtGui.QFormLayout()
        proxyAuthLayout.addRow("Proxy auth enabled:", self.cbProxyAuth)
        proxyAuthLayout.addRow("Proxy auth login:", self.txtProxyAuthLogin)
        proxyAuthLayout.addRow("Proxy auth password:", self.txtProxyAuthPass)

        proxyAuthGroup = QtGui.QGroupBox("Proxy authentication")
        proxyAuthGroup.setLayout(proxyAuthLayout)

        # Layouting
        layoutGeneral.addWidget(rpbGeneralGroup)
        layoutGeneral.addWidget(proxyGroup)
        layoutGeneral.addWidget(proxyAuthGroup)

        # GUI elements activation/deactivation
        if self.cbProxyEnabled.isChecked():
            self.txtProxyServer.setDisabled(False)
            self.txtProxyPort.setDisabled(False)
            self.txtNoProxy.setDisabled(False)
        else:
            self.txtProxyServer.setDisabled(True)
            self.txtProxyPort.setDisabled(True)
            self.txtNoProxy.setDisabled(True)

        if self.cbProxyAuth.isChecked():
            self.txtProxyAuthLogin.setDisabled(False)
            self.txtProxyAuthPass.setDisabled(False)
        else:
            self.txtProxyAuthLogin.setDisabled(True)
            self.txtProxyAuthPass.setDisabled(True)

        self._initProxyUiVisibility()

        return tabGeneral

    def _initGui(self):
        """Initialise GUI UI tab
        """
        tabGui = QtGui.QWidget()
        layoutGui = QtGui.QFormLayout(tabGui)

        # GUI
        self.txtGuiWidth = QtGui.QLineEdit()
        self.txtGuiWidth.setValidator(QtGui.QIntValidator(self.txtGuiWidth))
        self.txtGuiWidth.setText(str(ConfigDetails().width))

        self.txtGuiHeight = QtGui.QLineEdit()
        self.txtGuiHeight.setValidator(QtGui.QIntValidator(self.txtGuiHeight))
        self.txtGuiHeight.setText(str(ConfigDetails().height))

        layoutGui.addRow("Window width:", self.txtGuiWidth)
        layoutGui.addRow("Window height:", self.txtGuiHeight)

        return tabGui

    def _initDicom(self):
        """Initialise DICOM UI tab
        """
        tabDicom = QtGui.QWidget()
        layoutDicom = QtGui.QVBoxLayout(tabDicom)

        # Replace patient name with
        options = []
        self.ddlPatNameReplace = QtGui.QComboBox()
        self.ddlPatNameReplace.addItem("pseudonym", "pid")
        self.ddlPatNameReplace.addItem("constant", "const")
        options.append("pid")
        options.append("const")
        i = options.index(ConfigDetails().replacePatientNameWith)
        self.ddlPatNameReplace.setCurrentIndex(i)
        self.ddlPatNameReplace.currentIndexChanged.connect(self.ddlPatNameReplaceChanged)

        # Anonymous constant patient name
        self.txtConstPatientName = QtGui.QLineEdit()
        self.txtConstPatientName.setText(str(ConfigDetails().constPatientName))

        # Multiple Patient IDs
        self.cbMultiPat = QtGui.QCheckBox()
        self.cbMultiPat.setChecked(ConfigDetails().allowMultiplePatientIDs)

        # Application confidentiality profile
        self.cbApplicationConfidentialityProfile = QtGui.QCheckBox()
        self.cbApplicationConfidentialityProfile.setChecked(ConfigDetails().applicationConfidentialityProfile)
        self.cbApplicationConfidentialityProfile.setDisabled(True)

        # Retain Patient Characteristic during de-identification
        self.cbRetainPatChar = QtGui.QCheckBox()
        self.cbRetainPatChar.setChecked(ConfigDetails().retainPatientCharacteristicsOption)

        # Retain Dates and Times during de-identification
        self.cbRetainFullDates = QtGui.QCheckBox()
        self.cbRetainFullDates.setChecked(ConfigDetails().retainLongFullDatesOption)

        # Retain Device Identity during de-identification
        self.cbRetainDeviceIdentity = QtGui.QCheckBox()
        self.cbRetainDeviceIdentity.setChecked(ConfigDetails().retainDeviceIdentityOption)

        # Clean Structured Content Option during de-identification
        self.cbCleanSc = QtGui.QCheckBox()
        self.cbCleanSc.setChecked(ConfigDetails().cleanStructuredContentOption)
        self.cbCleanSc.setDisabled(True)

        # Clean Descriptors Option during de-identification
        self.cbCleanDescs = QtGui.QCheckBox()
        self.cbCleanDescs.setChecked(ConfigDetails().cleanDescriptorsOption)
        self.cbCleanDescs.setDisabled(True)

        # Retain Study and Series Descriptions during de-identification
        self.cbRetainStudySeriesDescs = QtGui.QCheckBox()
        self.cbRetainStudySeriesDescs.setChecked(ConfigDetails().retainStudySeriesDescriptions)

        dicomDeidentificationLayout = QtGui.QFormLayout()
        dicomDeidentificationLayout.addRow("Replace patient name with:", self.ddlPatNameReplace)
        dicomDeidentificationLayout.addRow("Const anonymous patient name:", self.txtConstPatientName)
        dicomDeidentificationLayout.addRow("Allow multiple patient IDs:", self.cbMultiPat)
        dicomDeidentificationLayout.addRow("Application confidentiality profile:", self.cbApplicationConfidentialityProfile)
        dicomDeidentificationLayout.addRow("Clean structured content option:", self.cbCleanSc)
        dicomDeidentificationLayout.addRow("Clean descriptors option:", self.cbCleanDescs)
        dicomDeidentificationLayout.addRow("Retain study and series descriptions:", self.cbRetainStudySeriesDescs)
        dicomDeidentificationLayout.addRow("Retain log. full dates option:", self.cbRetainFullDates)
        dicomDeidentificationLayout.addRow("Retain patient characteristics option:", self.cbRetainPatChar)
        dicomDeidentificationLayout.addRow("Retain device identity option:", self.cbRetainDeviceIdentity)

        dicomDeidentificationGroup = QtGui.QGroupBox("DICOM de-identification")
        dicomDeidentificationGroup.setLayout(dicomDeidentificationLayout)

        # Automatic mapping of RT-Struct names
        self.cbAutoRTStructMatch = QtGui.QCheckBox()
        self.cbAutoRTStructMatch.setChecked(ConfigDetails().autoRTStructMatch)

        # Automatic referencing of RT-Struct in all RTPlans
        self.cbAutoRTStructRef = QtGui.QCheckBox()
        self.cbAutoRTStructRef.setChecked(ConfigDetails().autoRTStructRef)

        dicomHarmonisationLayout = QtGui.QFormLayout()
        dicomHarmonisationLayout.addRow("Auto mapping of RTSTRUCT ROI names:", self.cbAutoRTStructMatch)
        dicomHarmonisationLayout.addRow("Auto re-referencing of RTSTRUCT SOPInstanceUID:", self. cbAutoRTStructRef)

        dicomHarmonisationGroup = QtGui.QGroupBox("DICOM harmonisation")
        dicomHarmonisationGroup.setLayout(dicomHarmonisationLayout)

        # Layout
        layoutDicom.addWidget(dicomDeidentificationGroup)
        layoutDicom.addWidget(dicomHarmonisationGroup)

        # GUI elements activation/deactivation
        if sys.version < "3":
            self.txtConstPatientName.setDisabled(
                str(self.ddlPatNameReplace.itemData(self.ddlPatNameReplace.currentIndex()).toString()) != "const"
            )
        else:
            self.txtConstPatientName.setDisabled(
                self.ddlPatNameReplace.itemData(self.ddlPatNameReplace.currentIndex()) != "const"
            )

        return tabDicom

    def _initSanityTests(self):
        """Initialise Data sanity tests UI tab
        """
        tabSanityTests = QtGui.QWidget()
        layoutSanityTests = QtGui.QFormLayout(tabSanityTests)

        # Patient gender match
        self.cbPatientGenderMatch = QtGui.QCheckBox()
        self.cbPatientGenderMatch.setChecked(ConfigDetails().patientGenderMatch)

        # Patient dob match
        self.cbPatientDobMatch = QtGui.QCheckBox()
        self.cbPatientDobMatch.setChecked(ConfigDetails().patientDobMatch)

        # Layout
        layoutSanityTests.addRow("Check patient gender match:", self.cbPatientGenderMatch)
        layoutSanityTests.addRow("Check patient date of birth match:", self.cbPatientDobMatch)

        return tabSanityTests

    def _initButtons(self):
        """Initialise Buttons
        """
        buttons = QtGui.QWidget()
        commandLayout = QtGui.QHBoxLayout(buttons)

        self.btnOk = QtGui.QPushButton("Ok")
        self.btnApply = QtGui.QPushButton("Apply")
        self.btnCancel = QtGui.QPushButton("Cancel")

        self.btnOk.clicked.connect(self.btnOkClicked)
        self.btnApply.clicked.connect(self.btnApplyClicked)
        self.btnCancel.clicked.connect(self.btnCancelClicked)

        commandLayout.addWidget(self.btnOk)
        commandLayout.addWidget(self.btnApply)
        commandLayout.addWidget(self.btnCancel)

        return buttons

    def _initProxyUiVisibility(self):
        if sys.version < "3":
            if str(self.ddlProxyConfiguration.itemData(self.ddlProxyConfiguration.currentIndex()).toString()) == "auto":
                self.txtProxyServer.setDisabled(True)
                self.txtProxyPort.setDisabled(True)
                self.txtNoProxy.setDisabled(True)
            else:
                self.txtProxyServer.setDisabled(False)
                self.txtProxyPort.setDisabled(False)
                self.txtNoProxy.setDisabled(False)
        else:
            if self.ddlProxyConfiguration.itemData(self.ddlProxyConfiguration.currentIndex()) == "auto":
                self.txtProxyServer.setDisabled(True)
                self.txtProxyPort.setDisabled(True)
                self.txtNoProxy.setDisabled(True)
            else:
                self.txtProxyServer.setDisabled(False)
                self.txtProxyPort.setDisabled(False)
                self.txtNoProxy.setDisabled(False)

    def _applySettings(self):
        """Apply changes and save them to in memory app context as well as to persistent config file
        """
        section = "RadPlanBioServer"
        if not AppConfigurationService().hasSection(section):
            AppConfigurationService().add(section)

        option = "host"
        value = self.txtServer.text()
        ConfigDetails().rpbHost = str(value)
        AppConfigurationService().set(section, option, str(value))

        option = "port"
        value = self.txtPort.text()
        ConfigDetails().rpbHostPort = int(value)
        AppConfigurationService().set(section, option, str(value))

        option = "application"
        value = self.txtServerApp.text()
        ConfigDetails().rpbApplication = str(value)
        AppConfigurationService().set(section, option, str(value))

        ###########################################################

        section = "Proxy"
        if not AppConfigurationService().hasSection(section):
            AppConfigurationService().add(section)

        option = "enabled"
        value = self.cbProxyEnabled.isChecked()
        ConfigDetails().proxyEnabled = value
        AppConfigurationService().set(section, option, str(value))

        option = "configuration"
        value = str(self.ddlProxyConfiguration.itemData(self.ddlProxyConfiguration.currentIndex()).toString())
        ConfigDetails().proxyConfiguration = value
        AppConfigurationService().set(section, option, str(value))

        # Automatic proxy detection
        if ConfigDetails().proxyConfiguration == "auto":

            # Detect proxy
            proxies = DiagnosticService().wpadProxyDiagnostic()

            # Proxies detected
            if proxies:
                host_port = proxies[0].split(":")
                ConfigDetails().proxyHost = str(host_port[0])
                ConfigDetails().proxyPort = int(host_port[1])
                self._logger.info(
                    "Automatically detected proxy stored in context: " +
                    ConfigDetails().proxyHost +
                    ":" +
                    str(ConfigDetails().proxyPort)
                )

        elif ConfigDetails().proxyConfiguration == "manual":
            option = "host"
            value = self.txtProxyServer.text()
            ConfigDetails().proxyHost = str(value)
            AppConfigurationService().set(section, option, str(value))

            option = "port"
            value = self.txtProxyPort.text()
            ConfigDetails().proxyPort = int(value)
            AppConfigurationService().set(section, option, str(value))

            option = "noproxy"
            value = self.txtNoProxy.text()
            ConfigDetails().noProxy = str(value)
            AppConfigurationService().set(section, option, str(value))

        ############################################################

        section = "Proxy-auth"
        if not AppConfigurationService().hasSection(section):
            AppConfigurationService().add(section)

        option = "enabled"
        value = self.cbProxyAuth.isChecked()
        ConfigDetails().proxyAuthEnabled = value
        AppConfigurationService().set(section, option, str(value))

        option = "login"
        value = self.txtProxyAuthLogin.text()
        ConfigDetails().proxyAuthLogin = str(value)
        AppConfigurationService().set(section, option, str(value))

        option = "password"
        value = self.txtProxyAuthPass.text()
        ConfigDetails().proxyAuthPassword = str(value)
        AppConfigurationService().set(section, option, str(value))

        ############################################################

        section = "General"
        if not AppConfigurationService().hasSection(section):
            AppConfigurationService().add(section)

        option = "startupupdatecheck"
        value = self.cbStartupUpdateCheck.isChecked()
        ConfigDetails().startupUpdateCheck = value
        AppConfigurationService().set(section, option, str(value))

        ############################################################

        section = "GUI"
        if not AppConfigurationService().hasSection(section):
            AppConfigurationService().add(section)

        option = "main.width"
        value = self.txtGuiWidth.text()
        ConfigDetails().width = int(value)
        AppConfigurationService().set(section, option, str(value))

        option = "main.height"
        value = self.txtGuiHeight.text()
        ConfigDetails().height = int(value)
        AppConfigurationService().set(section, option, str(value))

        #############################################################

        section = "DICOM"
        if not AppConfigurationService().hasSection(section):
            AppConfigurationService().add(section)

        option = "replacepatientnamewith"
        value = str(self.ddlPatNameReplace.itemData(self.ddlPatNameReplace.currentIndex()).toString())
        ConfigDetails().replacePatientNameWith = value
        AppConfigurationService().set(section, option, str(value))

        option = "constpatientname"
        value = self.txtConstPatientName.text()
        ConfigDetails().constPatientName = str(value)
        AppConfigurationService().set(section, option, str(value))

        option = "retainstudyseriesdescriptions"
        value = self.cbRetainStudySeriesDescs.isChecked()
        ConfigDetails().retainStudySeriesDescriptions = value
        AppConfigurationService().set(section, option, str(value))

        option = "allowmultiplepatientids"
        value = self.cbMultiPat.isChecked()
        ConfigDetails().allowMultiplePatientIDs = value
        AppConfigurationService().set(section, option, str(value))

        option = "retainpatientcharacteristicsoption"
        value = self.cbRetainPatChar.isChecked()
        ConfigDetails().retainPatientCharacteristicsOption = value
        AppConfigurationService().set(section, option, str(value))

        option = "retaindeviceidentityoption"
        value = self.cbRetainDeviceIdentity.isChecked()
        ConfigDetails().retainDeviceIdentityOption = value
        AppConfigurationService().set(section, option, str(value))

        option = "retainlongfulldatesoption"
        value = self.cbRetainFullDates.isChecked()
        ConfigDetails().retainLongFullDatesOption = value
        AppConfigurationService().set(section, option, str(value))

        option = "autortstructmatch"
        value = self.cbAutoRTStructMatch.isChecked()
        ConfigDetails().autoRTStructMatch = value
        AppConfigurationService().set(section, option, str(value))

        option = "autortstructref"
        value = self.cbAutoRTStructRef.isChecked()
        ConfigDetails().autoRTStructRef = value
        AppConfigurationService().set(section, option, str(value))

        ############################################################

        section = "SanityTests"
        if not AppConfigurationService().hasSection(section):
            AppConfigurationService().add(section)

        option = "patientgendermatch"
        value = self.cbPatientGenderMatch.isChecked()
        ConfigDetails().patientGenderMatch = value
        AppConfigurationService().set(section, option, str(value))

        option = "patientdobmatch"
        value = self.cbPatientDobMatch.isChecked()
        ConfigDetails().patientDobMatch = value
        AppConfigurationService().set(section, option, str(value))

        ############################################################

        AppConfigurationService().saveConfiguration()
