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

# PyQt
from PyQt4 import QtGui, QtCore, QtNetwork

# Contexts
from contexts.ConfigDetails import ConfigDetails

# Services
from services.ApplicationEntityService import ApplicationEntityService

# Utils
from utils import first

# Services
from services.AppConfigurationService import AppConfigurationService

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

        # Init members
        self._isNewAe = False
        self._remoteAEs = []
        self._selectedRemoteAE = None

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
        self.tabSettings.addTab(self._initApplicationEntity(), "Application Entity")

        # Command buttons
        rootLayout.addWidget(self._initButtons())

        # Load data
        self.reloadRemoteAEs()

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
            self.txtProxyServer.setDisabled(False)
            self.txtProxyPort.setDisabled(False)
            self.txtNoProxy.setDisabled(False)
        else:
            self.txtProxyServer.setDisabled(True)
            self.txtProxyPort.setDisabled(True)
            self.txtNoProxy.setDisabled(True) 

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
        if str(self.ddlPatNameReplace.itemData(index).toString()) == "const":
            self.txtConstPatientName.setDisabled(False)
        else:
            self.txtConstPatientName.setDisabled(True)

    def ddlRpbAetSuffixChanged(self, index):
        """Cient AE title suffix generation changed
        """
        aetSuffix =  str(self.ddlRpbAetSuffix.itemData(index).toString())

        # Consider AET suffix option when creating AE for client
        AET = str(self.txtRpbAE.text())

        if aetSuffix == "host":
            AET += str(QtNetwork.QHostInfo.localHostName())
        elif aetSuffix == "fqdn":
            AET += str(QtNetwork.QHostInfo.localHostName()) + "."  + str(QtNetwork.QHostInfo.localDomainName())

        self.ddlRpbAetSuffix.setToolTip(AET)

    def tvRemoteAEChanged(self, current, previous):
        """
        """
        # Take the first column of selected row from table view
        index = self.raeModel.index(current.row(), 0)
        self._selectedRemoteAE = first.first(
            rae for rae in self._remoteAEs if rae["AET"].encode("utf-8") == index.data().toPyObject().toUtf8()
        )

        self._logger.debug("Selected remote AE: " + self._selectedRemoteAE["AET"])

        if self._selectedRemoteAE is not None:
            self.txtRemoteAeTitle.setText(self._selectedRemoteAE["AET"])
            self.txtRemoteAeHost.setText(self._selectedRemoteAE["Address"])
            self.txtRemoteAePort.setText(str(self._selectedRemoteAE["Port"]))

            self.btnRemoveAE.setDisabled(False)
            self.btnEditAE.setDisabled(False)
            self.btnConnectionAETest.setDisabled(False)

    def btnReloadClicked(self):
        """
        """
        self.reloadRemoteAEs()

    def btnNewRemoteAEClicked(self):
        """
        """
        self.txtRemoteAeTitle.setDisabled(False)
        self.txtRemoteAeHost.setDisabled(False)
        self.txtRemoteAePort.setDisabled(False)

        self.txtRemoteAeTitle.setText("")
        self.txtRemoteAeHost.setText("")
        self.txtRemoteAePort.setText("")

        self.btnReloadAE.setDisabled(True)
        self.btnNewAE.setDisabled(True)
        self.btnEditAE.setDisabled(True)
        self.btnRemoveAE.setDisabled(True)
        self.btnConnectionAETest.setDisabled(True)
        self.btnOk.setDisabled(True)
        self.btnApply.setDisabled(True)
        self.btnCancel.setDisabled(True)

        self.btnSaveAE.setDisabled(False)
        self.btnCancelAE.setDisabled(False)

        self._isNewAe = True

    def btnEditRemoteAEClicked(self):
        """
        """
        self.txtRemoteAeTitle.setDisabled(False)
        self.txtRemoteAeHost.setDisabled(False)
        self.txtRemoteAePort.setDisabled(False)

        self.btnReloadAE.setDisabled(True)
        self.btnNewAE.setDisabled(True)
        self.btnEditAE.setDisabled(True)
        self.btnRemoveAE.setDisabled(True)
        self.btnConnectionAETest.setDisabled(True)
        self.btnOk.setDisabled(True)
        self.btnApply.setDisabled(True)
        self.btnCancel.setDisabled(True)

        self.btnSaveAE.setDisabled(False)
        self.btnCancelAE.setDisabled(False)

    def btnRemoveRemoteAEClicked(self):
        """
        """
        for ae in self._remoteAEs:
            if ae["AET"] == self._selectedRemoteAE["AET"]:
                self._remoteAEs.remove(ae)
                self._selectedRemoteAE = None
                break

        self.refreshRemoteAEs()

    def btnSaveRemoteAEClicked(self):
        """
        """
        # Save new or edit existing AE
        if self._isNewAe:
            value = self.txtRemoteAeTitle.text()
            aet = str(value)
            value = self.txtRemoteAeHost.text()
            address = str(value)
            value = self.txtRemoteAePort.text()
            port = int(value)

            newAe = dict(Address=address, Port=port, AET=aet)
            self._remoteAEs.append(newAe)
            self._isNewAe = False
        else:
            for ae in self._remoteAEs:
                if ae["AET"] == self._selectedRemoteAE["AET"]:
                    value = self.txtRemoteAeTitle.text()
                    ae["AET"] = str(value)
                    value = self.txtRemoteAeHost.text()
                    ae["Address"] = str(value)
                    value = self.txtRemoteAePort.text()
                    ae["Port"] = int(value)

                    self._selectedRemoteAE = ae
                    break

        self.refreshRemoteAEs()

        self.txtRemoteAeTitle.setDisabled(True)
        self.txtRemoteAeHost.setDisabled(True)
        self.txtRemoteAePort.setDisabled(True)

        self.btnReloadAE.setDisabled(False)
        self.btnNewAE.setDisabled(False)
        self.btnEditAE.setDisabled(False)
        self.btnRemoveAE.setDisabled(False)
        self.btnConnectionAETest.setDisabled(False)
        self.btnOk.setDisabled(False)
        self.btnApply.setDisabled(False)
        self.btnCancel.setDisabled(False)

        self.btnSaveAE.setDisabled(True)
        self.btnCancelAE.setDisabled(True)        

    def btnCancelRemoteAEClicked(self):
        """
        """
        self.txtRemoteAeTitle.setDisabled(True)
        self.txtRemoteAeHost.setDisabled(True)
        self.txtRemoteAePort.setDisabled(True)

        self.btnReloadAE.setDisabled(False)
        self.btnNewAE.setDisabled(False)
        self.btnEditAE.setDisabled(False)
        self.btnRemoveAE.setDisabled(False)
        self.btnOk.setDisabled(False)
        self.btnApply.setDisabled(False)
        self.btnCancel.setDisabled(False)

        self.btnSaveAE.setDisabled(True)
        self.btnCancelAE.setDisabled(True)

    def btnConnectionRemoteAETestClicked(self):
        """Test connection to Remote AE clicked
        """
        try:
            if not ApplicationEntityService().isReady:
                if ConfigDetails().rpbAE is not None and ConfigDetails().rpbAE != "":

                    # Consider AET suffix option when creating AE for client
                    AET = str(self.txtRpbAE.text())

                    if ConfigDetails().rpbAETsuffix == "host":
                        AET += str(QtNetwork.QHostInfo.localHostName())
                    elif ConfigDetails().rpbAETsuffix == "fqdn":
                        AET += str(QtNetwork.QHostInfo.localHostName()) + "." +\
                               str(QtNetwork.QHostInfo.localDomainName())

                    ApplicationEntityService().init(
                        AET,
                        int(self.txtRpbAEport.text())
                    )

            association = ApplicationEntityService().requestAssociation(self._selectedRemoteAE)
            status = ApplicationEntityService().echo(association)
            QtGui.QMessageBox.information(
                self, 
                "Remote AE connection test", 
                "Result: " + str(status)
            )

            association.Release(0)
        except Exception, err:
            self._logger.error(str(err))

 ######   #######  ##     ## ##     ##    ###    ##    ## ########   ######
##    ## ##     ## ###   ### ###   ###   ## ##   ###   ## ##     ## ##    ##
##       ##     ## #### #### #### ####  ##   ##  ####  ## ##     ## ##
##       ##     ## ## ### ## ## ### ## ##     ## ## ## ## ##     ##  ######
##       ##     ## ##     ## ##     ## ######### ##  #### ##     ##       ##
##    ## ##     ## ##     ## ##     ## ##     ## ##   ### ##     ## ##    ##
 ######   #######  ##     ## ##     ## ##     ## ##    ## ########   ######

    def reloadRemoteAEs(self):
        """
        """
        self._remoteAEs = ConfigDetails().remoteAEs
        self.refreshRemoteAEs()

    def refreshRemoteAEs(self):
        """
        """
        # Model
        self.raeModel = QtGui.QStandardItemModel(self.tvRemoteAe)
        self.raeModel.setHorizontalHeaderLabels(["AET", "Host", "Port"])

        row = 0
        for ae in self._remoteAEs:
            aetItem = QtGui.QStandardItem(ae["AET"])
            hostItem = QtGui.QStandardItem(ae["Address"])
            portItem = QtGui.QStandardItem(str(ae["Port"]))

            self.raeModel.setItem(row, 0, aetItem)
            self.raeModel.setItem(row, 1, hostItem)
            self.raeModel.setItem(row, 2, portItem)

            row = row + 1

        # Set the models Views
        self.tvRemoteAe.setModel(self.raeModel)

        # Resize the width of columns to fit the content
        self.tvRemoteAe.resizeColumnsToContents()

        # After the view has model, set currentChanged behaviour
        self.tvRemoteAe.selectionModel().currentChanged.connect(self.tvRemoteAEChanged)

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

        self.txtProxyServer = QtGui.QLineEdit()
        self.txtProxyServer.setText(str(ConfigDetails().proxyHost))

        self.txtProxyPort = QtGui.QLineEdit()
        self.txtProxyPort.setValidator(QtGui.QIntValidator(self.txtProxyPort))
        self.txtProxyPort.setText(str(ConfigDetails().proxyPort))

        self.txtNoProxy = QtGui.QLineEdit() 
        self.txtNoProxy.setText(str(ConfigDetails().noProxy))

        proxyLayout = QtGui.QFormLayout()
        proxyLayout.addRow("Proxy enabled:", self.cbProxyEnabled)
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

        # Anonymouse constant patient name
        self.txtConstPatientName = QtGui.QLineEdit()
        self.txtConstPatientName.setText(str(ConfigDetails().constPatientName))

        # Multiple patient IDs
        self.cbMultiPat = QtGui.QCheckBox()
        self.cbMultiPat.setChecked(ConfigDetails().allowMultiplePatientIDs)

        # Application confidentality profile
        self.cbApplicationConfidentialityProfile = QtGui.QCheckBox()
        self.cbApplicationConfidentialityProfile.setChecked(ConfigDetails().applicationConfidentialityProfile)
        self.cbApplicationConfidentialityProfile.setDisabled(True)

        # Retain Patient Characteristic during anonymisation
        self.cbRetainPatChar = QtGui.QCheckBox()
        self.cbRetainPatChar.setChecked(ConfigDetails().retainPatientCharacteristicsOption)

        # Clean Descriptors Option during anonymisation
        self.cbCleanDescs = QtGui.QCheckBox()
        self.cbCleanDescs.setChecked(ConfigDetails().cleanDescriptorsOption)
        self.cbCleanDescs.setDisabled(True)

        # Retain Study Date during anonymisation
        self.cbRetainStudyDate = QtGui.QCheckBox()
        self.cbRetainStudyDate.setChecked(ConfigDetails().retainStudyDate)

        # Retain Study Time during anonymisation
        self.cbRetainStudyTime = QtGui.QCheckBox()
        self.cbRetainStudyTime.setChecked(ConfigDetails().retainStudyTime)

        # Retain Series Date during anonymisation
        self.cbRetainSeriesDate = QtGui.QCheckBox()
        self.cbRetainSeriesDate.setChecked(ConfigDetails().retainSeriesDate)

        # Retain Series Time during anonymisation
        self.cbRetainSeriesTime = QtGui.QCheckBox()
        self.cbRetainSeriesTime.setChecked(ConfigDetails().retainSeriesTime)

        # Retaion Study and Series Descriptions during anonymisation
        self.cbRetaionStudySeriesDescs = QtGui.QCheckBox()
        self.cbRetaionStudySeriesDescs.setChecked(ConfigDetails().retainStudySeriesDescriptions)

        dicomDeidentificationLayout = QtGui.QFormLayout()
        dicomDeidentificationLayout.addRow("Replace patient name with:", self.ddlPatNameReplace)
        dicomDeidentificationLayout.addRow("Const anonymous patient name:", self.txtConstPatientName)
        dicomDeidentificationLayout.addRow("Allow multiple patient IDs:", self.cbMultiPat)
        dicomDeidentificationLayout.addRow("Application confidentiality profile:", self.cbApplicationConfidentialityProfile)
        dicomDeidentificationLayout.addRow("Clean descriptors option:", self.cbCleanDescs)
        dicomDeidentificationLayout.addRow("Retain study and series descriptions:", self.cbRetaionStudySeriesDescs)
        dicomDeidentificationLayout.addRow("Retain patient characteristics option:", self.cbRetainPatChar)
        dicomDeidentificationLayout.addRow("Retain study date:", self.cbRetainStudyDate)        
        dicomDeidentificationLayout.addRow("Retain study time:", self.cbRetainStudyTime)
        dicomDeidentificationLayout.addRow("Retain series date:", self.cbRetainSeriesDate)
        dicomDeidentificationLayout.addRow("Retain series time:", self.cbRetainSeriesTime)

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

        # Replace DICOM patient folder name with
        dicomPatienFolderOptions = []
        self.ddlPatientFolderName = QtGui.QComboBox()
        self.ddlPatientFolderName.addItem("pseudonym", "pid")
        self.ddlPatientFolderName.addItem("StudySubjectID", "ssid")
        dicomPatienFolderOptions.append("pid")
        dicomPatienFolderOptions.append("ssid")
        i = dicomPatienFolderOptions.index(ConfigDetails().downloadDicomPatientFolderName)
        self.ddlPatientFolderName.setCurrentIndex(i)

        # Replace DICOM study folder name with
        dicomFolderOptions = []
        self.ddlStudyFolderName = QtGui.QComboBox()
        self.ddlStudyFolderName.addItem("item OID", "oid")
        self.ddlStudyFolderName.addItem("item label", "label")
        dicomFolderOptions.append("oid")
        dicomFolderOptions.append("label")
        i = dicomFolderOptions.index(ConfigDetails().downloadDicomStudyFolderName)
        self.ddlStudyFolderName.setCurrentIndex(i)

        dicomDownloadLayout = QtGui.QFormLayout()
        dicomDownloadLayout.addRow("Download DICOM patient folder name:", self.ddlPatientFolderName)
        dicomDownloadLayout.addRow("Download DICOM study folder name:", self.ddlStudyFolderName)

        dicomDownloadGroup = QtGui.QGroupBox("DICOM download")
        dicomDownloadGroup.setLayout(dicomDownloadLayout)

        # Layout
        layoutDicom.addWidget(dicomDeidentificationGroup)
        layoutDicom.addWidget(dicomHarmonisationGroup)
        layoutDicom.addWidget(dicomDownloadGroup)

        # GUI elements activation/deactivation
        if str(self.ddlPatNameReplace.itemData(self.ddlPatNameReplace.currentIndex()).toString()) == "const":
            self.txtConstPatientName.setDisabled(False)
        else:
            self.txtConstPatientName.setDisabled(True)

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

    def _initApplicationEntity(self):
        """Initialise AE tab
        """
        tabAe = QtGui.QWidget()
        layoutAe = QtGui.QVBoxLayout(tabAe)

        # Client DICOM AE title
        self.txtRpbAE = QtGui.QLineEdit()
        self.txtRpbAE.setToolTip("AET")
        self.txtRpbAE.setMinimumWidth(250)
        self.txtRpbAE.setText(str(ConfigDetails().rpbAE))

        # Client DICOM AE port
        self.txtRpbAEport = QtGui.QLineEdit()
        self.txtRpbAEport.setValidator(QtGui.QIntValidator(self.txtRpbAEport))
        self.txtRpbAEport.setText(str(ConfigDetails().rpbAEport))

        # Client DICOM AET suffix
        rpbAetSuffixOptions = []
        self.ddlRpbAetSuffix = QtGui.QComboBox()
        
        if ApplicationEntityService().ae != None:
            self.ddlRpbAetSuffix.setToolTip(ApplicationEntityService().ae.name)
            
        self.ddlRpbAetSuffix.addItem("No", "no")
        self.ddlRpbAetSuffix.addItem("Hostname", "host")
        self.ddlRpbAetSuffix.addItem("Fully qualified domain name", "fqdn")
        self.ddlRpbAetSuffix.currentIndexChanged.connect(self.ddlRpbAetSuffixChanged)
        rpbAetSuffixOptions.append("no")
        rpbAetSuffixOptions.append("host")
        rpbAetSuffixOptions.append("fqdn")
        i = rpbAetSuffixOptions.index(ConfigDetails().rpbAETsuffix)
        self.ddlRpbAetSuffix.setCurrentIndex(i)

        # Layout
        clienAeLayout = QtGui.QFormLayout()
        clienAeLayout.addRow("AE name:", self.txtRpbAE)
        clienAeLayout.addRow("Port:", self.txtRpbAEport)
        clienAeLayout.addRow("AET suffix:", self.ddlRpbAetSuffix)

        # Group
        clientAeGroup = QtGui.QGroupBox("Client AE")
        clientAeGroup.setLayout(clienAeLayout)

        # Adding/Editing AE node
        self.txtRemoteAeTitle = QtGui.QLineEdit()
        self.txtRemoteAeTitle.setToolTip("AET")
        self.txtRemoteAeTitle.setMinimumWidth(250)
        self.txtRemoteAeTitle.setDisabled(True)

        self.txtRemoteAeHost = QtGui.QLineEdit()
        self.txtRemoteAeHost.setMinimumWidth(250)
        self.txtRemoteAeHost.setDisabled(True)

        self.txtRemoteAePort = QtGui.QLineEdit()
        self.txtRemoteAePort.setValidator(QtGui.QIntValidator(self.txtRemoteAePort))
        self.txtRemoteAePort.setDisabled(True)

        self.tvRemoteAe = QtGui.QTableView()

        # Buttons row
        self.btnReloadAE = QtGui.QPushButton()
        self.btnReloadAE.setToolTip("Reload configured remote AEs")
        self.btnReloadAE.setMaximumWidth(self._toolBarButtonSize)
        self.btnReloadAE.setMaximumHeight(self._toolBarButtonSize)
        self.btnReloadAE.setIcon(self.reloadIcon)
        self.btnReloadAE.setIconSize(QtCore.QSize(self._toolBarButtonSize - 7, self._toolBarButtonSize - 7))

        self.btnReloadAE.clicked.connect(self.btnReloadClicked)

        self.btnNewAE = QtGui.QPushButton()
        self.btnNewAE.setToolTip("Create a new remote AE")
        self.btnNewAE.setMaximumWidth(self._toolBarButtonSize)
        self.btnNewAE.setMaximumHeight(self._toolBarButtonSize)
        self.btnNewAE.setIcon(self.newIcon)
        self.btnNewAE.setIconSize(QtCore.QSize(self._toolBarButtonSize - 7, self._toolBarButtonSize - 7))

        self.btnNewAE.clicked.connect(self.btnNewRemoteAEClicked)

        self.btnEditAE = QtGui.QPushButton()
        self.btnEditAE.setToolTip("Edit an existing remote AE")
        self.btnEditAE.setMaximumWidth(self._toolBarButtonSize)
        self.btnEditAE.setMaximumHeight(self._toolBarButtonSize)
        self.btnEditAE.setIcon(self.editIcon)
        self.btnEditAE.setIconSize(QtCore.QSize(self._toolBarButtonSize - 7, self._toolBarButtonSize - 7))

        self.btnEditAE.clicked.connect(self.btnEditRemoteAEClicked)

        self.btnRemoveAE = QtGui.QPushButton()
        self.btnRemoveAE.setToolTip("Remove selected remote AE")
        self.btnRemoveAE.setMaximumWidth(self._toolBarButtonSize)
        self.btnRemoveAE.setMaximumHeight(self._toolBarButtonSize)
        self.btnRemoveAE.setIcon(self.deleteIcon)
        self.btnRemoveAE.setIconSize(QtCore.QSize(self._toolBarButtonSize - 7, self._toolBarButtonSize - 7))
        self.btnRemoveAE.setDisabled(True)

        self.btnRemoveAE.clicked.connect(self.btnRemoveRemoteAEClicked)

        self.btnSaveAE = QtGui.QPushButton()
        self.btnSaveAE.setToolTip("Save modification of remote AE")
        self.btnSaveAE.setMaximumWidth(self._toolBarButtonSize)
        self.btnSaveAE.setMaximumHeight(self._toolBarButtonSize)
        self.btnSaveAE.setIcon(self.saveIcon)
        self.btnSaveAE.setIconSize(QtCore.QSize(self._toolBarButtonSize - 7, self._toolBarButtonSize - 7))
        self.btnSaveAE.setDisabled(True)

        self.btnSaveAE.clicked.connect(self.btnSaveRemoteAEClicked)

        self.btnCancelAE = QtGui.QPushButton()
        self.btnCancelAE.setToolTip("Cancel modification of remote AE")
        self.btnCancelAE.setMaximumWidth(self._toolBarButtonSize)
        self.btnCancelAE.setMaximumHeight(self._toolBarButtonSize)
        self.btnCancelAE.setIcon(self.cancelIcon)
        self.btnCancelAE.setIconSize(QtCore.QSize(self._toolBarButtonSize - 7, self._toolBarButtonSize - 7))
        self.btnCancelAE.setDisabled(True)

        self.btnCancelAE.clicked.connect(self.btnCancelRemoteAEClicked)

        self.btnConnectionAETest = QtGui.QPushButton()
        self.btnConnectionAETest.setToolTip("Test connection to remote AE (C-Echo)")
        self.btnConnectionAETest.setMaximumWidth(self._toolBarButtonSize)
        self.btnConnectionAETest.setMaximumHeight(self._toolBarButtonSize)
        self.btnConnectionAETest.setIcon(self.connectionIcon)
        self.btnConnectionAETest.setIconSize(QtCore.QSize(self._toolBarButtonSize - 7, self._toolBarButtonSize - 7))
        self.btnConnectionAETest.setDisabled(True)

        self.btnConnectionAETest.clicked.connect(self.btnConnectionRemoteAETestClicked)

        remoteAeButtonsLayout = QtGui.QHBoxLayout()
        remoteAeButtonsLayout.addWidget(self.btnReloadAE)
        remoteAeButtonsLayout.addWidget(self.btnNewAE)
        remoteAeButtonsLayout.addWidget(self.btnEditAE)
        remoteAeButtonsLayout.addWidget(self.btnRemoveAE)
        remoteAeButtonsLayout.addWidget(self.btnSaveAE)
        remoteAeButtonsLayout.addWidget(self.btnCancelAE)
        remoteAeButtonsLayout.addStretch(1)
        remoteAeButtonsLayout.addWidget(self.btnConnectionAETest)

        # Layout
        remoteAeLayout = QtGui.QFormLayout()
        remoteAeLayout.addRow("Remote AE name:", self.txtRemoteAeTitle)
        remoteAeLayout.addRow("Remote AE host:", self.txtRemoteAeHost)
        remoteAeLayout.addRow("Remote AE port:", self.txtRemoteAePort)

        # Group
        remoteAeGroup = QtGui.QGroupBox("Remote AE")
        remoteAeGroup.setLayout(remoteAeLayout)

        layoutAe.addWidget(clientAeGroup)
        layoutAe.addWidget(remoteAeGroup)
        layoutAe.addLayout(remoteAeButtonsLayout)
        layoutAe.addWidget(self.tvRemoteAe)

        return tabAe

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
            AppConfigurationService.add(section)

        option = "enabled"
        value = self.cbProxyEnabled.isChecked()
        ConfigDetails().proxyEnabled = value
        AppConfigurationService().set(section, option, str(value))

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
            AppConfigurationService.add(section)

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
            AppConfigurationService.add(section)

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
        value = self.cbRetaionStudySeriesDescs.isChecked()
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

        option = "retainstudydate"
        value = self.cbRetainStudyDate.isChecked()
        ConfigDetails().retainStudyDate = value
        AppConfigurationService().set(section, option, str(value))

        option = "retainstudytime"
        value = self.cbRetainStudyTime.isChecked()
        ConfigDetails().retainStudyTime = value
        AppConfigurationService().set(section, option, str(value))

        option = "retainseriesdate"
        value = self.cbRetainSeriesDate.isChecked()
        ConfigDetails().retainSeriesDate = value
        AppConfigurationService().set(section, option, str(value))

        option = "retainseriestime"
        value = self.cbRetainSeriesTime.isChecked()
        ConfigDetails().retainSeriesTime = value
        AppConfigurationService().set(section, option, str(value))

        option = "autortstructmatch"
        value = self.cbAutoRTStructMatch.isChecked()
        ConfigDetails().autoRTStructMatch = value
        AppConfigurationService().set(section, option, str(value))

        option = "autortstructref"
        value = self.cbAutoRTStructRef.isChecked()
        ConfigDetails().autoRTStructRef = value
        AppConfigurationService().set(section, option, str(value))
        
        option = "downloaddicomstudyfoldername"
        value = str(self.ddlStudyFolderName.itemData(self.ddlStudyFolderName.currentIndex()).toString())
        ConfigDetails().downloadDicomStudyFolderName = value
        AppConfigurationService().set(section, option, str(value))

        option = "downloaddicompatientfoldername"
        value = str(self.ddlPatientFolderName.itemData(self.ddlPatientFolderName.currentIndex()).toString())
        ConfigDetails().downloadDicomPatientFolderName = value
        AppConfigurationService().set(section, option, str(value))

        ############################################################

        section = "SanityTests"
        if not AppConfigurationService().hasSection(section):
            AppConfigurationService().add(section)

        option = "patientGenderMatch"
        value = self.cbPatientGenderMatch.isChecked()
        ConfigDetails().patientGenderMatch = value
        AppConfigurationService().set(section, option, str(value))

        option = "patientDobMatch"
        value = self.cbPatientDobMatch.isChecked()
        ConfigDetails().patientDobMatch = value
        AppConfigurationService().set(section, option, str(value))

        ############################################################

        section = "AE"
        if not AppConfigurationService().hasSection(section):
            AppConfigurationService().add(section)

        option = "name"
        value = self.txtRpbAE.text()
        ConfigDetails().rpbAE = str(value)
        AppConfigurationService().set(section, option, str(value))

        option = "port"
        value = self.txtRpbAEport.text()
        ConfigDetails().rpbAEport = int(value)
        AppConfigurationService().set(section, option, int(value))

        option = "aetsuffix"
        value = str(self.ddlRpbAetSuffix.itemData(self.ddlRpbAetSuffix.currentIndex()).toString())
        ConfigDetails().rpbAETsuffix = value
        AppConfigurationService().set(section, option, str(value))

        ############################################################

        section = "RemoteAEs"
        if not AppConfigurationService().hasSection(section):
            AppConfigurationService().add(section)

        option = "count"
        value = len(self._remoteAEs)
        AppConfigurationService().set(section, option, value)
        
        i = 0
        for rae in self._remoteAEs:
            section = "RemoteAE" + str(i)
            if not AppConfigurationService().hasSection(section):
                AppConfigurationService().add(section)

            option = "address"
            value = rae["Address"]
            AppConfigurationService().set(section, option, value)

            option = "port"
            value = rae["Port"]
            AppConfigurationService().set(section, option, value)

            option = "aet"
            value = rae["AET"]
            AppConfigurationService().set(section, option, value)

            i = i + 1

        ConfigDetails().remoteAEs = self._remoteAEs

        ############################################################

        AppConfigurationService().saveConfiguration()
