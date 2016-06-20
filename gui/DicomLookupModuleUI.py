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


class DicomLookupModuleUI(object):
    """DICOM Lookup Module UI definition
    """

    def setupUi(self, module):
        """Setup UI
        """
        self.centralwidget = QtGui.QWidget(module)
        self.centralwidget.setObjectName(_fromUtf8("dicomLookupModule"))
        self.rootLayout = QtGui.QVBoxLayout(self.parent)

        newIconRes = ":/images/new.png"
        reloadIconRes = ":/images/reload.png"
        saveIconRes = ":/images/save.png"
        detailsIconRes = ":/images/details.png"
        deleteIconRes = ":/images/delete.png"
        reloadIconRes = ":/images/reload.png"
        fromFileIconRes = ":/images/search-all.png"
        plusIconRes = ":/images/plus.png"
        plusAllIconRes = ":/images/plus-all.png"
        minusIconRes = ":/images/minus.png"
        minusAllIconRes = ":/images/minus-all.png"
        searchIconPath = ":/images/search.png"
        cancelIconRes = ":/images/cancel.png"

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

        self.searchIcon = QtGui.QIcon()
        self.searchIcon.addPixmap(QtGui.QPixmap(searchIconPath))

        self.fromFileIcon = QtGui.QIcon()
        self.fromFileIcon.addPixmap(QtGui.QPixmap(fromFileIconRes))

        self.plusIcon = QtGui.QIcon()
        self.plusIcon.addPixmap(QtGui.QPixmap(plusIconRes))

        self.plusAllIcon = QtGui.QIcon()
        self.plusAllIcon.addPixmap(QtGui.QPixmap(plusAllIconRes))

        self.minusIcon = QtGui.QIcon()
        self.minusIcon.addPixmap(QtGui.QPixmap(minusIconRes))

        self.minusAllIcon = QtGui.QIcon()
        self.minusAllIcon.addPixmap(QtGui.QPixmap(minusAllIconRes))

        self.cancelIcon = QtGui.QIcon()
        self.cancelIcon.addPixmap(QtGui.QPixmap(cancelIconRes))

        self._toolBarButtonSize = 25

        self.setupDicomServerConnectionBar()

        # Main Tab Widget
        self.tabWidget = QtGui.QTabWidget()

        # Create tabs
        self.setupPatients()
        self.setupStudies()
        self.setupSeries()
        self.setupSummary()

        self.rootLayout.addWidget(self.tabWidget)

        # Put defined central widget into ManWindow central widget
        self.retranslateUi(module)
        QtCore.QMetaObject.connectSlotsByName(module)

    def setupDicomServerConnectionBar(self):
        """
        """
        # Connection info
        connectionLayout = QtGui.QVBoxLayout()
        self.rootLayout.addLayout(connectionLayout)

        # DICOM node
        self.cmbDicomNode= QtGui.QComboBox()
        dicomServerLayout = QtGui.QFormLayout()
        dicomServerLayout.addRow("DICOM server:", self.cmbDicomNode)

        # Patient search
        lblPatientId = QtGui.QLabel("Patient ID:")
        self.txtPatientIdFilter = QtGui.QLineEdit()
        lblPatientName = QtGui.QLabel("Patient Name:")
        self.txtPatientNameFilter = QtGui.QLineEdit()

        self.btnSearch = QtGui.QPushButton()
        self.btnSearch.setToolTip("Find DICOM data")
        self.btnSearch.setMaximumWidth(self._toolBarButtonSize)
        self.btnSearch.setMaximumHeight(self._toolBarButtonSize)
        self.btnSearch.setIcon(self.searchIcon)
        self.btnSearch.setIconSize(QtCore.QSize(self._toolBarButtonSize - 7, self._toolBarButtonSize - 7))

        self.btnLoadPatIds = QtGui.QPushButton()
        self.btnLoadPatIds.setToolTip("Load set of Patient IDs from CSV file")
        self.btnLoadPatIds.setMaximumWidth(self._toolBarButtonSize)
        self.btnLoadPatIds.setMaximumHeight(self._toolBarButtonSize)
        self.btnLoadPatIds.setIcon(self.fromFileIcon)
        self.btnLoadPatIds.setIconSize(QtCore.QSize(self._toolBarButtonSize - 7, self._toolBarButtonSize - 7))

        self.btnCancelSearchCriteria = QtGui.QPushButton()
        self.btnCancelSearchCriteria.setToolTip("Cancel search criteria")
        self.btnCancelSearchCriteria.setMaximumWidth(self._toolBarButtonSize)
        self.btnCancelSearchCriteria.setMaximumHeight(self._toolBarButtonSize)
        self.btnCancelSearchCriteria.setIcon(self.cancelIcon)
        self.btnCancelSearchCriteria.setIconSize(QtCore.QSize(self._toolBarButtonSize - 7, self._toolBarButtonSize - 7))

        patientSearchLayout = QtGui.QHBoxLayout()
        patientSearchLayout.addWidget(lblPatientId)
        patientSearchLayout.addWidget(self.txtPatientIdFilter)
        patientSearchLayout.addWidget(lblPatientName)
        patientSearchLayout.addWidget(self.txtPatientNameFilter)
        patientSearchLayout.addWidget(self.btnLoadPatIds)
        patientSearchLayout.addWidget(self.btnCancelSearchCriteria)
        patientSearchLayout.addWidget(self.btnSearch)

        searchGroup = QtGui.QGroupBox("Query (C-Find)")
        searchGroup.setLayout(patientSearchLayout)

        # Connection layout
        connectionLayout.addLayout(dicomServerLayout)
        connectionLayout.addWidget(searchGroup)

    def setupPatients(self):
        """DICOM patients tab
        """
        tabPatients = QtGui.QWidget()

        self.tabWidget.addTab(tabPatients, "DICOM Patients")

        self.tvPatients = QtGui.QTableView()

        self.tvPatients.setAlternatingRowColors(True)
        self.tvPatients.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tvPatients.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tvPatients.setSortingEnabled(True)

        layoutPatients = QtGui.QVBoxLayout(tabPatients)

        layoutPatientsFilter = QtGui.QFormLayout()
        self.txtPatientFilter = QtGui.QLineEdit()
        layoutPatientsFilter.addRow("Filter:", self.txtPatientFilter)

        self.btnPlusAllPatients = QtGui.QPushButton()
        self.btnPlusAllPatients.setToolTip("Add all patients to retrieve cart")
        self.btnPlusAllPatients.setMaximumWidth(self._toolBarButtonSize)
        self.btnPlusAllPatients.setMaximumHeight(self._toolBarButtonSize)
        self.btnPlusAllPatients.setIcon(self.plusAllIcon)
        self.btnPlusAllPatients.setIconSize(QtCore.QSize(self._toolBarButtonSize - 7, self._toolBarButtonSize - 7))

        self.btnPlusPatient = QtGui.QPushButton()
        self.btnPlusPatient.setToolTip("Add patient to retrieve cart")
        self.btnPlusPatient.setMaximumWidth(self._toolBarButtonSize)
        self.btnPlusPatient.setMaximumHeight(self._toolBarButtonSize)
        self.btnPlusPatient.setIcon(self.plusIcon)
        self.btnPlusPatient.setIconSize(QtCore.QSize(self._toolBarButtonSize - 7, self._toolBarButtonSize - 7))

        self.btnMinusAllPatients = QtGui.QPushButton()
        self.btnMinusAllPatients.setToolTip("Remove all patients from retrieve cart")
        self.btnMinusAllPatients.setMaximumWidth(self._toolBarButtonSize)
        self.btnMinusAllPatients.setMaximumHeight(self._toolBarButtonSize)
        self.btnMinusAllPatients.setIcon(self.minusAllIcon)
        self.btnMinusAllPatients.setIconSize(QtCore.QSize(self._toolBarButtonSize - 7, self._toolBarButtonSize - 7))

        self.btnMinusPatient = QtGui.QPushButton()
        self.btnMinusPatient.setToolTip("Remove patient from retrieve cart")
        self.btnMinusPatient.setMaximumWidth(self._toolBarButtonSize)
        self.btnMinusPatient.setMaximumHeight(self._toolBarButtonSize)
        self.btnMinusPatient.setIcon(self.minusIcon)
        self.btnMinusPatient.setIconSize(QtCore.QSize(self._toolBarButtonSize - 7, self._toolBarButtonSize - 7))

        layoutPatientsToolbar = QtGui.QHBoxLayout()
        layoutPatientsToolbar.addWidget(self.btnPlusAllPatients)
        layoutPatientsToolbar.addWidget(self.btnMinusAllPatients)
        layoutPatientsToolbar.addWidget(self.btnPlusPatient)
        layoutPatientsToolbar.addWidget(self.btnMinusPatient)
        layoutPatientsToolbar.addStretch(1)

        layoutPatients.addLayout(layoutPatientsFilter)
        layoutPatients.addLayout(layoutPatientsToolbar)
        layoutPatients.addWidget(self.tvPatients)

    def setupStudies(self):
        """DICOM studies tab
        """
        tabStudies = QtGui.QWidget()

        self.tabWidget.addTab(tabStudies, "DICOM Studies")

        self.txtStudyFilter = QtGui.QLineEdit()
        self.tvStudies = QtGui.QTableView()

        self.tvStudies.setAlternatingRowColors(True)
        self.tvStudies.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tvStudies.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tvStudies.setSortingEnabled(True)

        layoutStudies = QtGui.QVBoxLayout(tabStudies)
        layoutStudiesToolbar = QtGui.QGridLayout()

        txtFilter = QtGui.QLabel("Filter:")
        layoutStudiesToolbar.addWidget(txtFilter, 2, 0)
        layoutStudiesToolbar.addWidget(self.txtStudyFilter, 2, 1)

        layoutStudies.addLayout(layoutStudiesToolbar)
        layoutStudies.addWidget(self.tvStudies)

    def setupSeries(self):
        """DICOM series tab
        """
        tabSeries= QtGui.QWidget()

        self.tabWidget.addTab(tabSeries, "DICOM Series")

        self.txtSeriesFilter = QtGui.QLineEdit()
        self.tvSeries= QtGui.QTableView()

        self.tvSeries.setAlternatingRowColors(True)
        self.tvSeries.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tvSeries.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tvSeries.setSortingEnabled(True)

        layoutSeries = QtGui.QVBoxLayout(tabSeries)
        layoutSeriesToolbar = QtGui.QGridLayout()

        txtFilter = QtGui.QLabel("Filter:")
        layoutSeriesToolbar.addWidget(txtFilter, 2, 0)
        layoutSeriesToolbar.addWidget(self.txtSeriesFilter, 2, 1)

        layoutSeries.addLayout(layoutSeriesToolbar)
        layoutSeries.addWidget(self.tvSeries)

    def setupSummary(self):
        """DICOM retrieve summary tab
        """
        tabSummary = QtGui.QWidget()
        
        self.tabWidget.addTab(tabSummary, "Summary")

        self.textBrowserProgress = QtGui.QTextBrowser()
        self.textBrowserProgress.setObjectName(_fromUtf8("textBrowserProgress"))

        self.btnDownload = QtGui.QPushButton()
        downloadIconPath = ":/images/download.png"
        downloadIcon = QtGui.QIcon()
        downloadIcon.addPixmap(QtGui.QPixmap(downloadIconPath))

        self.btnDownload.setIcon(downloadIcon)
        self.btnDownload.setIconSize(QtCore.QSize(self._toolBarButtonSize, self._toolBarButtonSize))
        self.btnDownload.setToolTip("Retrieve DICOM data")
        self.btnDownload.setDisabled(True)

        self.progressBar = QtGui.QProgressBar()

        # Group
        dicomDataLayout = QtGui.QVBoxLayout()
        dicomDataLayout.setSpacing(10)
        
        dicomDataGroup = QtGui.QGroupBox("DICOM data in cart for retrieve: ")
        dicomDataGroup.setLayout(dicomDataLayout)
        
        self.treeDicomData = QtGui.QTreeView()
        
        dicomDataLayout.addWidget(self.treeDicomData)

        layoutDownload = QtGui.QVBoxLayout()
        layoutDownload.addWidget(self.textBrowserProgress)
        layoutDownload.addWidget(self.progressBar)
        layoutDownload.addWidget(self.btnDownload)

        layoutSummary = QtGui.QHBoxLayout(tabSummary)
        layoutSummary.addWidget(dicomDataGroup)
        layoutSummary.addLayout(layoutDownload)

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
        self.btnDownload.setText(QtGui.QApplication.translate("MainWindow", "Retrieve DICOM data", None, QtGui.QApplication.UnicodeUTF8))