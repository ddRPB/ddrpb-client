#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# PyQt
from PyQt4 import QtGui

# Encoding RFC 3548
import base64

########  ####    ###    ##        #######   ######
##     ##  ##    ## ##   ##       ##     ## ##    ##
##     ##  ##   ##   ##  ##       ##     ## ##
##     ##  ##  ##     ## ##       ##     ## ##   ####
##     ##  ##  ######### ##       ##     ## ##    ##
##     ##  ##  ##     ## ##       ##     ## ##    ##
########  #### ##     ## ########  #######   ######


class KeyDialog(QtGui.QDialog):
    """Key Dialog Class
    """

    def __init__(self, key, parent=None):
        """Default Constructor
        """
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("Key")
        self.resize(500, 250)

        # Dialog layout root
        rootLayout = QtGui.QVBoxLayout(self)

        # Key Text
        txtKey = QtGui.QTextEdit()
        txtKey.setReadOnly(True)
        txtKey.setText(base64.b64encode(key))

        # Layout
        rootLayout.addWidget(txtKey)
