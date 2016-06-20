#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# PyQt
from PyQt4 import QtGui, QtCore

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class DicomDownloadModuleUI(object):
    """DICOM Download Module UI definition
    """

    def setupUi(self, module):
        """Setup UI
        """
        self.centralwidget = QtGui.QWidget(module)
        self.centralwidget.setObjectName(_fromUtf8("dicomDownloadModule"))
        self.rootLayout = QtGui.QVBoxLayout(self.parent)

        newIconRes = ':/images/new.png'
        saveIconRes = ':/images/save.png'
        detailsIconRes = ':/images/details.png'
        deleteIconRes = ':/images/delete.png'
        reloadIconRes = ':/images/reload.png'

        self.reloadIcon = QtGui.QIcon()
        self.reloadIcon.addPixmap(QtGui.QPixmap(reloadIconRes))

        self.newIcon = QtGui.QIcon()
        self.newIcon.addPixmap(QtGui.QPixmap(newIconRes))

        self.saveIcon = QtGui.QIcon()
        self.saveIcon.addPixmap(QtGui.QPixmap(saveIconRes))

        self.deleteIcon = QtGui.QIcon()
        self.deleteIcon.addPixmap(QtGui.QPixmap(deleteIconRes))

        self.detailsIcon = QtGui.QIcon()
        self.detailsIcon.addPixmap(QtGui.QPixmap(detailsIconRes))

        self.setupOcConnectionBar()

        # Main Tab Widget
        self.tabWidget = QtGui.QTabWidget()

        # Create tabs
        self.setupSites()

        tab5 = QtGui.QWidget()
        
        self.tabWidget.addTab(tab5, "Summary")

        self.textBrowserProgress = QtGui.QTextBrowser()
        self.textBrowserProgress.setObjectName(_fromUtf8("textBrowserProgress"))

        toolBarButtonSize = 20
        self.btnDownload = QtGui.QPushButton()
        downloadIconPath = ":/images/download.png"
        downloadIcon = QtGui.QIcon()
        downloadIcon.addPixmap(QtGui.QPixmap(downloadIconPath))

        self.btnDownload.setIcon(downloadIcon)
        self.btnDownload.setIconSize(QtCore.QSize(toolBarButtonSize, toolBarButtonSize))
        self.btnDownload.setToolTip("Download DICOM data")
        self.btnDownload.setDisabled(True)

        self.progressBar = QtGui.QProgressBar()

        layoutTab5 = QtGui.QVBoxLayout(tab5)

        # Last step
        layoutTab5.addWidget(self.textBrowserProgress)
        layoutTab5.addWidget(self.progressBar)
        layoutTab5.addWidget(self.btnDownload)

        self.rootLayout.addWidget(self.tabWidget)

        # Put defined central widget into ManWindow central widget
        self.retranslateUi(module)
        QtCore.QMetaObject.connectSlotsByName(module)

    def setupOcConnectionBar(self):
        # Connection info
        connectionLayout = QtGui.QGridLayout()
        connectionLayout.setSpacing(10)
        self.rootLayout.addLayout(connectionLayout)

        # OC connection SOAP web services
        ocSOAPConnection= QtGui.QLabel("OC connection (SOAP):")
        self.lblOcConnection = QtGui.QLabel()

        # Add to connection layout
        connectionLayout.addWidget(ocSOAPConnection, 1, 0)
        connectionLayout.addWidget(self.lblOcConnection, 1, 1, 1, 8)

        # OC study
        study = QtGui.QLabel("Study: ")
        self.cmbStudy = QtGui.QComboBox()

        # Add to layout
        connectionLayout.addWidget(study, 2, 0)
        connectionLayout.addWidget(self.cmbStudy, 2, 1, 2, 8)

    def setupSites(self):
        """
        """
        tabStudySites = QtGui.QWidget()

        self.tabWidget.addTab(tabStudySites, "Study/Sites")

        self.txtStudyFilter = QtGui.QLineEdit()
        self.tvStudies = QtGui.QTableView()

        self.tvStudies.setAlternatingRowColors(True)
        self.tvStudies.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tvStudies.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tvStudies.setSortingEnabled(True)

        layoutStudySites = QtGui.QVBoxLayout(tabStudySites)
        layoutStudySitesToolbar = QtGui.QGridLayout()

        lblFilter = QtGui.QLabel("Filter:")
        layoutStudySitesToolbar.addWidget(lblFilter, 1, 0)
        layoutStudySitesToolbar.addWidget(self.txtStudyFilter, 1, 1)

        layoutStudySites.addLayout(layoutStudySitesToolbar)
        layoutStudySites.addWidget(self.tvStudies)

####    ##    #######  ##    ## 
 ##   ####   ##     ## ###   ## 
 ##     ##   ##     ## ####  ## 
 ##     ##    #######  ## ## ## 
 ##     ##   ##     ## ##  #### 
 ##     ##   ##     ## ##   ### 
####  ######  #######  ##    ##

    def retranslateUi(self, module):
        """
        """
        #self.btnDownload.setText(QtGui.QApplication.translate("MainWindow", "Download DICOM data", None, QtGui.QApplication.UnicodeUTF8))
