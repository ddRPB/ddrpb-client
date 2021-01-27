#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# PyQT
from PyQt4 import QtGui, QtCore

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class DicomBrowserDialogUI(object):
    """DICOM browser dialog
    """

    def setupUi(self, parent):
        """Prepare graphical user interface elements
        """
        QtGui.QDialog.__init__(self, parent)
        
        # Dialog dimensions
        width = 600
        height = 450

        # Title and icon
        self.setWindowTitle("Selected DICOM data")
        appIconPath = ':/images/rpb-icon'
        appIcon = QtGui.QIcon()
        appIcon.addPixmap(QtGui.QPixmap(appIconPath))
        self.setWindowIcon(appIcon)
        self.resize(width, height)

        # Dialog layout root
        rootLayout = QtGui.QVBoxLayout(self)

        # Instructions
        msg = "Instructions: you can select one STUDY (mandatory) and SERIES from other STUDIES (if necessary)."
        lblInstructions = QtGui.QLabel(msg)

        rootLayout.addWidget(lblInstructions)

        # DicomData
        rootLayout.addWidget(self.setupDicomDir())

        # Dialog buttons
        rootLayout.addWidget(self.setupButtons())

        # self.retranslateUi(Form)
        # QtCore.QMetaObject.connectSlotsByName(Form)

    def setupDicomDir(self):
        """Setup DICOM patient UI
        """
        dicomDataLayout = QtGui.QVBoxLayout()
        dicomDataLayout.setSpacing(10)

        # Group
        dicomDataGroup = QtGui.QGroupBox("DICOM data structure: ")
        dicomDataGroup.setLayout(dicomDataLayout)

        # DICOM data
        self.treeDicomData = QtGui.QTreeView()

        # Add to layout
        dicomDataLayout.addWidget(self.treeDicomData)

        return dicomDataGroup

    def setupButtons(self):
        """Setup dialog buttons
        """
        self.btnOk = QtGui.QPushButton("Ok")
        return self.btnOk
