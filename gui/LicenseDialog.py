#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# PyQt
from PyQt4 import QtGui, QtCore

########  ####    ###    ##        #######   ######
##     ##  ##    ## ##   ##       ##     ## ##    ##
##     ##  ##   ##   ##  ##       ##     ## ##
##     ##  ##  ##     ## ##       ##     ## ##   ####
##     ##  ##  ######### ##       ##     ## ##    ##
##     ##  ##  ##     ## ##       ##     ## ##    ##
########  #### ##     ## ########  #######   ######

class LicenseDialog(QtGui.QDialog):
    """License Dialog Class
    """

    def __init__(self, parent=None):
        """Default Constructor
        """
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("License")
        self.resize(500, 250)

        # Dialog layout root
        rootLayout = QtGui.QVBoxLayout(self)

        # License Text
        txtLicense = QtGui.QTextEdit()
        txtLicense.setReadOnly(True)

        txtFile = QtCore.QFile('license.txt')
        if not txtFile.open(QtCore.QIODevice.ReadOnly):
            QtGui.QMessageBox.information(None, "info", file.errorString())

        stream = QtCore.QTextStream(txtFile)
        txtLicense.setText(stream.readAll())

        # Layouting
        rootLayout.addWidget(txtLicense)
