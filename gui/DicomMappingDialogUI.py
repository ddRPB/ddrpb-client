#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# PyQt
from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class DicomMappingDialogUI(object):
    """DICOM mapping dialog
    """

    def setupUi(self, parent):
        """Prepare graphical user interface elements
        """
        QtGui.QDialog.__init__(self, parent)

        # Dialog dimensions
        width = 1000
        height = 450

        # Title and icon
        self.setWindowTitle("DICOM RTSTRUCT contour names mapping")
        appIconPath = ':/images/rpb-icon.jpg'
        appIcon = QtGui.QIcon()
        appIcon.addPixmap(QtGui.QPixmap(appIconPath))
        self.setWindowIcon(appIcon)
        self.resize(width, height)

        # Dialog layout root
        rootLayout = QtGui.QVBoxLayout(self)

        # Instructions
        msg = "Instructions: you have to map delineated contours to standardised names\n" \
              "(OAR can have laterality, TV can have identifier index and prescription dose. " \
              "Both OAR and TV can have margin details)."
        lblInstructions = QtGui.QLabel(msg)

        rootLayout.addWidget(lblInstructions)

        self.tableWidget = QtGui.QTableWidget()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)

        rootLayout.addWidget(self.tableWidget)

        self.pushButton = QtGui.QPushButton("Ok")

        rootLayout.addWidget(self.pushButton)
    
        self.retranslateUi(parent)
        QtCore.QMetaObject.connectSlotsByName(parent)

    def retranslateUi(self, parent):
        self.pushButton.setText(QtGui.QApplication.translate("Form", "Ok", None, QtGui.QApplication.UnicodeUTF8))
