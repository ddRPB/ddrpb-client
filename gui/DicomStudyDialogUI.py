#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# PyQt
from PyQt4 import QtGui, QtCore

# UI
import gui.colours

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class DicomStudyDialogUI(object):
    """DICOM study overview dialog
    """

    def setupUi(self, parent):
        """Prepare graphical user interface elements
        """
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("Selected DICOM Study")
        appIconPath =':/images/rpb-icon.jpg'
        appIcon = QtGui.QIcon()
        appIcon.addPixmap(QtGui.QPixmap(appIconPath))
        self.setWindowIcon(appIcon)
        self.resize(600, 600)

        # Colour styles
        self.redStyle = "QWidget { background-color:" + gui.colours.RED + ";}"
        self.greenStyle = "QWidget { background-color:" + gui.colours.GREEN + ";}"

        # Dialog layout root
        rootLayout = QtGui.QVBoxLayout(self)

        # Instructions
        msg = "Instructions: you can use '->' buttons to retain patient identity free STUDY/SERIE descriptions."
        lblInstructions = QtGui.QLabel(msg)

        rootLayout.addWidget(lblInstructions)

        # Patient
        rootLayout.addWidget(self.setupPatient())

        # Study
        rootLayout.addWidget(self.setupStudy())

        # Tab
        self.tabWidget = QtGui.QTabWidget()
        rootLayout.addWidget(self.tabWidget)

        self.tabWidget.addTab(self.setupDicomSeries(), "DICOM study series")
        
        self.tabWidget.addTab(self.setupStructuredReporting(), "Structured reporting")

        rootLayout.addWidget(self.setupButtons())

        # Disable SR tab by default (enabled when SR serie modality is selected)
        self.tabWidget.setTabEnabled(1, False)

        # self.retranslateUi(Form)
        # QtCore.QMetaObject.connectSlotsByName(Form)

    def setupPatient(self):
        """Setup DICOM patient UI
        """
        # Patient Grid
        patientLayout = QtGui.QGridLayout()
        patientLayout.setSpacing(10)

        # Group
        patientGroup = QtGui.QGroupBox("DICOM patient: ")
        patientGroup.setLayout(patientLayout)

        # Patient ID
        lblPatientId = QtGui.QLabel("ID:")
        self.txtPatientId = QtGui.QLineEdit()
        self.txtPatientId.setReadOnly(True)
        self.txtPatientId.setStyleSheet(self.redStyle)
        self.txtPatientId.setToolTip("Original PatientID")

        lblNewPatientId = QtGui.QLabel("->")
        lblNewPatientId.setToolTip("Is going to be replaced with...")
        
        self.txtNewPatientId = QtGui.QLineEdit()
        self.txtNewPatientId.setReadOnly(True)
        self.txtNewPatientId.setStyleSheet(self.greenStyle)
        self.txtNewPatientId.setToolTip("Pseudonymised PatientID")

        # Patient Name
        lblPatientName = QtGui.QLabel("Name:")
        self.txtPatientName = QtGui.QLineEdit()
        self.txtPatientName.setReadOnly(True)
        self.txtPatientName.setStyleSheet(self.redStyle)
        self.txtPatientName.setToolTip("Original PatientName")

        lblNewPatientName = QtGui.QLabel("->")
        lblNewPatientName.setToolTip("Is going to be replaced with...")
        
        self.txtNewPatientName = QtGui.QLineEdit()
        self.txtNewPatientName.setReadOnly(True)
        self.txtNewPatientName.setStyleSheet(self.greenStyle)
        self.txtNewPatientName.setToolTip("Pseudonymised PatientName")

        # Patient Gender
        lblPatientGender = QtGui.QLabel("Gender:")
        self.txtPatientGender = QtGui.QLineEdit()
        self.txtPatientGender.setReadOnly(True)
        self.txtPatientGender.setStyleSheet(self.redStyle)
        self.txtPatientGender.setToolTip("Original PatientGender")

        lblNewPatientGender = QtGui.QLabel("->")
        lblNewPatientGender.setToolTip("Is going to be replaced with...")

        self.txtNewPatientGender = QtGui.QLineEdit()
        self.txtNewPatientGender.setReadOnly(True)
        self.txtNewPatientGender.setStyleSheet(self.greenStyle)
        self.txtNewPatientGender.setToolTip("Pseudonymised PatientGender")

        # Patient DOB
        lblPatientDOB = QtGui.QLabel("DOB:")
        self.txtPatientDOB = QtGui.QLineEdit()
        self.txtPatientDOB.setReadOnly(True)
        self.txtPatientDOB.setStyleSheet(self.redStyle)
        self.txtPatientDOB.setToolTip("Original PatientDOB")

        lblNewPatientDOB = QtGui.QLabel("->")
        lblNewPatientDOB.setToolTip("Is going to be replaced with...")

        self.txtNewPatientDOB = QtGui.QLineEdit()
        self.txtNewPatientDOB.setReadOnly(True)
        self.txtNewPatientDOB.setStyleSheet(self.greenStyle)
        self.txtNewPatientDOB.setToolTip("Pseudonymised PatientDOB")

        # Add to connection layout
        patientLayout.addWidget(lblPatientId, 0, 0)
        patientLayout.addWidget(self.txtPatientId, 0, 1)
        patientLayout.addWidget(lblNewPatientId, 0, 2)
        patientLayout.addWidget(self.txtNewPatientId, 0, 3)

        patientLayout.addWidget(lblPatientName, 1, 0)
        patientLayout.addWidget(self.txtPatientName, 1, 1)
        patientLayout.addWidget(lblNewPatientName, 1, 2)
        patientLayout.addWidget(self.txtNewPatientName, 1, 3)

        patientLayout.addWidget(lblPatientGender, 2, 0)
        patientLayout.addWidget(self.txtPatientGender, 2, 1)
        patientLayout.addWidget(lblNewPatientGender, 2, 2)
        patientLayout.addWidget(self.txtNewPatientGender, 2, 3)

        patientLayout.addWidget(lblPatientDOB, 3, 0)
        patientLayout.addWidget(self.txtPatientDOB, 3, 1)
        patientLayout.addWidget(lblNewPatientDOB, 3, 2)
        patientLayout.addWidget(self.txtNewPatientDOB, 3, 3)

        return patientGroup

    def setupStudy(self):
        """Setup DICOM study UI
        """
        # Patient Grid
        studyLayout = QtGui.QGridLayout()
        studyLayout.setSpacing(10)

        # Group
        studyGroup = QtGui.QGroupBox("DICOM study: ")
        studyGroup.setLayout(studyLayout)

        # Study type
        lblStudyType = QtGui.QLabel("Study type:")
        self.cmbStudyType = QtGui.QComboBox()
        self.cmbStudyType.setToolTip("Detected DICOM study type")

        # Study description
        lblStudyDescription = QtGui.QLabel("Description:")
        self.txtStudyDescription = QtGui.QLineEdit()
        self.txtStudyDescription.setReadOnly(True)
        self.txtStudyDescription.setStyleSheet(self.redStyle)
        self.txtStudyDescription.setToolTip("Original StudyDescription")

        self.copyStudyDescButton = QtGui.QPushButton("->")
        self.copyStudyDescButton.setToolTip("Copy description")

        self.txtNewStudyDescription = QtGui.QLineEdit()
        self.txtNewStudyDescription.setStyleSheet(self.greenStyle)
        self.txtNewStudyDescription.setToolTip("Pseudonymised StudyDescription")

        # Add to connection layout
        studyLayout.addWidget(lblStudyType, 0, 0)
        studyLayout.addWidget(self.cmbStudyType, 0, 1)
        studyLayout.addWidget(lblStudyDescription, 1, 0)
        studyLayout.addWidget(self.txtStudyDescription, 1, 1)
        studyLayout.addWidget(self.copyStudyDescButton, 1, 2)
        studyLayout.addWidget(self.txtNewStudyDescription, 1, 3)

        return studyGroup

    def setupDicomSeries(self):
        """Setup DICOM study series tab
        """
        # Tab
        tabSeries = QtGui.QWidget()

        # Layout
        layoutSeries = QtGui.QVBoxLayout(tabSeries)
        layoutSeriesToolbar = QtGui.QGridLayout()

        # Data table view
        self.tvSeries = QtGui.QTableView()
        self.tvSeries.setAlternatingRowColors(True)
        self.tvSeries.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.tvSeries.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

        self.btnCopySeriesDesc = QtGui.QPushButton("->")
        self.btnCopySeriesDesc.setToolTip("Copy descriptions")

        # Filter for the table
        txtFilter = QtGui.QLabel("Filter:")
        self.txtSeriesFilter = QtGui.QLineEdit()

        # Fill the layout with elemets
        layoutSeriesToolbar.addWidget(txtFilter, 1, 0)
        layoutSeriesToolbar.addWidget(self.txtSeriesFilter, 1, 1)
        layoutSeriesToolbar.addWidget(self.btnCopySeriesDesc, 1, 2)

        layoutSeries.addLayout(layoutSeriesToolbar)
        layoutSeries.addWidget(self.tvSeries)

        # Final GUI element
        return tabSeries

    def setupStructuredReporting(self):
        """Setup DICOM SR structured reporting tab
        """
        # Tab
        tabSr = QtGui.QWidget()

        # Layout
        layoutSr = QtGui.QVBoxLayout(tabSr)
        layoutSrToolbar = QtGui.QGridLayout()

        # Text Edit
        self.teReport = QtGui.QTextEdit()
        self.teReport.setStyleSheet(self.redStyle)
        self.teReport.setEnabled(False)

        # Label
        self.lblFreeLength = QtGui.QLabel()

        # Buttons
        self.btnApprove = QtGui.QPushButton("Approve")
        self.btnApprove.setToolTip("Approve structured report")
        self.btnApprove.setEnabled(False)

        # Fill the layout with elemets
        layoutSrToolbar.addWidget(self.btnApprove, 0, 0, 1, 6)
        layoutSrToolbar.addWidget(self.lblFreeLength, 0, 7, 1, 1)

        layoutSr.addLayout(layoutSrToolbar)
        layoutSr.addWidget(self.teReport)

        # Final GUI element
        return tabSr

    def setupButtons(self):
        """Setup dialog OK button
        """
        self.btnOk = QtGui.QPushButton("Ok")
        return self.btnOk
