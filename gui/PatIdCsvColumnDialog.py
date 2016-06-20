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
from PyQt4 import QtGui
from PyQt4.QtCore import Qt

# Utils
from utils import first

########  ####    ###    ##        #######   ######
##     ##  ##    ## ##   ##       ##     ## ##    ##
##     ##  ##   ##   ##  ##       ##     ## ##
##     ##  ##  ##     ## ##       ##     ## ##   ####
##     ##  ##  ######### ##       ##     ## ##    ##
##     ##  ##  ##     ## ##       ##     ## ##    ##
########  #### ##     ## ########  #######   ######


class PatIdCsvColumnDialog(QtGui.QDialog):
    """CSV file loading dialog Class
    """

    def __init__(self, parent=None):
        """Default Constructor
        """
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("Select Patient ID column")

        # Setup logger - use config file
        self.logger = logging.getLogger(__name__)
        logging.config.fileConfig('logging.ini', disable_existing_loggers=False)

        upgradeIconPath =':/images/upgrade.png'
        upgradeIcon = QtGui.QIcon(upgradeIconPath)
        upgradeIcon.addPixmap(QtGui.QPixmap(upgradeIcon))

        # Dialog layout root
        rootLayout = QtGui.QVBoxLayout(self)

        formLayout = QtGui.QFormLayout()
        self.cmbPatIdColumn = QtGui.QComboBox()

        formLayout.addRow("Patient ID column:", self.cmbPatIdColumn)

        self.btnOk = QtGui.QPushButton("Ok")
        self.btnOk.setDisabled(True)

        # OK and Cancel buttons
        self.buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        # Init members
        self._columns = []
        self._selectedPatIdColumn = None

        # Layouting
        rootLayout.addLayout(formLayout)
        rootLayout.addWidget(self.buttons)

        # Register handlers
        self.cmbPatIdColumn.currentIndexChanged["QString"].connect(self.cmbPatIdColumnChanged)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

##     ##    ###    ##    ## ########  ##       ######## ########   ######  
##     ##   ## ##   ###   ## ##     ## ##       ##       ##     ## ##    ## 
##     ##  ##   ##  ####  ## ##     ## ##       ##       ##     ## ##       
######### ##     ## ## ## ## ##     ## ##       ######   ########   ######  
##     ## ######### ##  #### ##     ## ##       ##       ##   ##         ## 
##     ## ##     ## ##   ### ##     ## ##       ##       ##    ##  ##    ## 
##     ## ##     ## ##    ## ########  ######## ######## ##     ##  ###### 
    
    def cmbPatIdColumnChanged(self, text):
        """PatientID column changed
        """
        # Set selected study and reload sites
        self._selectedPatIdColumn = first.first(
            col for col in self._columns if col.encode("utf-8") == text.toUtf8()
        )

        # Enable ok button
        if self._selectedPatIdColumn:
            self.btnOk.setDisabled(False)
        else:
            self.btnOk.setDisabled(True)

 ######   #######  ##     ## ##     ##    ###    ##    ## ########   ######
##    ## ##     ## ###   ### ###   ###   ## ##   ###   ## ##     ## ##    ##
##       ##     ## #### #### #### ####  ##   ##  ####  ## ##     ## ##
##       ##     ## ## ### ## ## ### ## ##     ## ## ## ## ##     ##  ######
##       ##     ## ##     ## ##     ## ######### ##  #### ##     ##       ##
##    ## ##     ## ##     ## ##     ## ##     ## ##   ### ##     ## ##    ##
 ######   #######  ##     ## ##     ## ##     ## ##    ## ########   ######

    def setModel(self, columns):
        """Set dialog viewModel
        """
        self._columns = columns

        # And prepare ViewModel for the GUI
        columnsModel = QtGui.QStandardItemModel()
        for column in self._columns:
            text = QtGui.QStandardItem(column)
            columnsModel.appendRow([text])

        self.cmbPatIdColumn.setModel(columnsModel)
