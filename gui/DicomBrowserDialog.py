#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# PyQt
from PyQt4 import QtGui, QtCore

# Dialog UI 
from gui.DicomBrowserDialogUI import DicomBrowserDialogUI

# ViewModels
from viewModels.DicomDataItemModel import DicomDataItemModel

########  ####    ###    ##        #######   ######
##     ##  ##    ## ##   ##       ##     ## ##    ##
##     ##  ##   ##   ##  ##       ##     ## ##
##     ##  ##  ##     ## ##       ##     ## ##   ####
##     ##  ##  ######### ##       ##     ## ##    ##
##     ##  ##  ##     ## ##       ##     ## ##    ##
########  #### ##     ## ########  #######   ######


class DicomBrowserDialog(QtGui.QDialog, DicomBrowserDialogUI):
    """Dialog which allows to select what studies/series from provided DICOM data should
    be considered further for verification of correctness and upload.
    """

    def __init__(self, parent=None):
        """ Setup UI
        """
        # Setup UI
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(parent)

        self._rootNode = None
        self._dicomDataModel = None

        # Handlers
        self.btnOk.clicked.connect(self.btnOkClicked)

##     ## ######## ######## ##     ##  #######  ########   ######
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ##
#### #### ##          ##    ##     ## ##     ## ##     ## ##
## ### ## ######      ##    ######### ##     ## ##     ##  ######
##     ## ##          ##    ##     ## ##     ## ##     ##       ##
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ##
##     ## ########    ##    ##     ##  #######  ########   ######

    def setModel(self, dicomData):
        """Prepare view models for this dialog
        """
        self._rootNode = dicomData

        # View model for DICOM data tree
        self._dicomDataModel = DicomDataItemModel(dicomData)

        dicomDataProxyModel = QtGui.QSortFilterProxyModel()
        dicomDataProxyModel.setSourceModel(self._dicomDataModel)
        dicomDataProxyModel.setDynamicSortFilter(True)
        dicomDataProxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        # Filtering
        # QtCore.QObject.connect(
        #   self.txtSeriesFilter,
        #   QtCore.SIGNAL("textChanged(QString)"),
        #   self.seriesProxyModel.setFilterRegExp
        # )

        # Assign view model to the view
        self.treeDicomData.setModel(dicomDataProxyModel)
        self.treeDicomData.resizeColumnToContents(0)
        self.treeDicomData.expandAll()

        # Resize the column of tree view to see the series description
        self.treeDicomData.setColumnWidth(0, 400)

        # self.dicomDataModel.dataChanged.connect(self.treeDataChanged)
        # QtCore.QObject.connect(
        #   self.dicomDataModel,
        #   QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
        #   self.treeDataChanged
        # )

##     ##    ###    ##    ## ########  ##       ######## ########   ######
##     ##   ## ##   ###   ## ##     ## ##       ##       ##     ## ##    ##
##     ##  ##   ##  ####  ## ##     ## ##       ##       ##     ## ##
######### ##     ## ## ## ## ##     ## ##       ######   ########   ######
##     ## ######### ##  #### ##     ## ##       ##       ##   ##         ##
##     ## ##     ## ##   ### ##     ## ##       ##       ##    ##  ##    ##
##     ## ##     ## ##    ## ########  ######## ######## ##     ##  ######

    def treeDataChanged(self):
        """Selection in tree view changed
        """
        self.treeDicomData.expandAll()

    def btnOkClicked(self):
        """OK button clicked handler
        """
        studySelected = False

        if self._rootNode is not None:
            for study in self._rootNode.children:
                if study.isChecked:
                    studySelected = True
                    break

        if studySelected:
            self.accept()
        else:
            QtGui.QMessageBox.information(
                self,
                "No DICOM study selected",
                "Please check the DICOM study that you would like to upload."
            )
