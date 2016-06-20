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

# Contexts
from contexts.ConfigDetails import ConfigDetails

# Utils
from difflib import get_close_matches

# PyQt
from PyQt4 import QtGui, QtCore

# GUI
from gui.DicomMappingDialogUI import DicomMappingDialogUI
from gui.ExtendedCombo import ExtendedCombo
import gui.colours

########  ####    ###    ##        #######   ######
##     ##  ##    ## ##   ##       ##     ## ##    ##
##     ##  ##   ##   ##  ##       ##     ## ##
##     ##  ##  ##     ## ##       ##     ## ##   ####
##     ##  ##  ######### ##       ##     ## ##    ##
##     ##  ##  ##     ## ##       ##     ## ##    ##
########  #### ##     ## ########  #######   ######


class DicomMappingDialog(QtGui.QDialog, DicomMappingDialogUI):
    """
    Widget showing the original Roi names which lets the user connect them
    to default names (useful for modeling)
    """
    def __init__(self, parent=None):
        """ Setup Ui, and load default names from file
        """
        # Setup UI
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(parent)

        # Setup logger - use config file
        self.logger = logging.getLogger(__name__)
        logging.config.fileConfig('logging.ini', disable_existing_loggers=False)

        self.greenStyle = "QWidget { background-color:" + gui.colours.GREEN + ";}"
        self.orangeStyle = "QWidget { background-color:" + gui.colours.ORANGE + ";}"

        # Extra naming conventions
        self._extraTextDelimiter = "___"
        self._leftRightModel = [("", ""), ("left", "_L"), ("right", "_R")]
        self._oarMarginModel = [("0", ""), ("nonuniform", "_PRV")]
        self._tvMultipleModel = [("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5"), ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9")]

        # Prepare data for UI
        self.initializeData()

        # Handlers
        self.pushButton.clicked.connect(self.pushButtonClicked)

########  ########   #######  ########  ######## ########  ######## #### ########  ######
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##    ##
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##
########  ########  ##     ## ########  ######   ########     ##     ##  ######    ######
##        ##   ##   ##     ## ##        ##       ##   ##      ##     ##  ##             ##
##        ##    ##  ##     ## ##        ##       ##    ##     ##     ##  ##       ##    ##
##        ##     ##  #######  ##        ######## ##     ##    ##    #### ########  ######

    @property
    def originalRoiNameDict(self):
        """OriginalRoiNameDict Getter
        """
        return self.__originalRoiNameDict

    @originalRoiNameDict.setter
    def originalRoiNameDict(self, value):
        """OriginalRoiNameDict Setter
        """
        self.__originalRoiNameDict = value
        self.__originalRoiNumberList = value.keys()

    @property
    def formalizedRTStructs(self):
        """FormalizedRTStructs Getter
        """
        return self.__formalizedRTStructs

    @formalizedRTStructs.setter
    def formalizedRTStructs(self, value):
        """FormalizedRTStructs Setter
        """
        self.__formalizedRTStructs = value

##     ## ######## ######## ##     ##  #######  ########   ######
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ##
#### #### ##          ##    ##     ## ##     ## ##     ## ##
## ### ## ######      ##    ######### ##     ## ##     ##  ######
##     ## ##          ##    ##     ## ##     ## ##     ##       ##
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ##
##     ## ########    ##    ##     ##  #######  ########   ######

    def setModel(self, originalRoiNameDict, formalizedRTStructs, leftRightContours, extraTextContours, oarContours, tvContours, tvMultipleContours):
        """Fills the entries of the table with the ROI names and checkboxes for the default names
        """
        self.__originalRoiNameDict = originalRoiNameDict
        self.__originalRoiNumberList = originalRoiNameDict.keys()
        self.__formalizedRTStructs = formalizedRTStructs

        self._extraTextContours = extraTextContours
        self._leftRightContours = leftRightContours
        self._oarContours = oarContours
        self._tvContours = tvContours
        self._tvMultipleContours = tvMultipleContours

        # Each ROI will be presented on separate row
        Nrows = len(self.__originalRoiNameDict.values())
        Ncols = 6

        # Set number of rows and columns and set widths and titles of rows
        self.tableWidget.setRowCount(Nrows)
        self.tableWidget.setColumnCount(Ncols)
        self.tableWidget.setColumnWidth(0, 200)
        self.tableWidget.setColumnWidth(1, 200)
        self.tableWidget.setColumnWidth(2, 200)
        self.tableWidget.setColumnWidth(3, 120)
        self.tableWidget.setColumnWidth(4, 120)
        self.tableWidget.setColumnWidth(5, 200)
        self.tableWidget.setHorizontalHeaderLabels(["Original Name", "Replace Name" ,"Assigned Name", "Additional Info", "Margin (mm)", "Prescription dose (cGy)"])

        # Full table: standardised combined string
        self.txtStandardisedList = []
        # Fill table: original ROI name on the left, default name comboboxes on the right
        self.comboBoxList = []
        # Fill the table: additional info txt box
        self.cmbExtraList = []
        # Fill the table: margin txt box
        self.cmbMarginList = []
        # Fill the table: dose txt box
        self.cmbDoseList = []

        # Create rows
        for i in xrange(Nrows):

            # Key for Original ROI Name dictionary - it is the number of original ROI in DCM
            key = self.__originalRoiNumberList[i]

            # Standard
            txtStandard = QtGui.QLabel()
            txtStandard.setStyleSheet(self.greenStyle)

            # Assigned name
            combobox = ExtendedCombo()
            combobox.setStyleSheet(self.orangeStyle)

            # Organ laterality and extra
            cmbExtra = QtGui.QComboBox()
            cmbExtra.setStyleSheet(self.orangeStyle)
            cmbExtra.setEnabled(False)
            cmbExtra.setEditable(False)

            # Margin
            cmbMargin = QtGui.QComboBox()
            cmbMargin.setStyleSheet(self.orangeStyle)
            cmbMargin.setEnabled(False)
            cmbMargin.setEditable(False)

            # Dose
            cmbDose = QtGui.QComboBox()
            cmbDose.setStyleSheet(self.orangeStyle)
            cmbDose.setEnabled(False)
            cmbDose.setEditable(False)

            # Use formalized RTStructs as data set for combobox
            rtsNames = []
            for item in self.__formalizedRTStructs:
                combobox.addItem(item.name, item.identifier)
                rtsNames.append(item.name)

            # Put original ROI name into first column
            self.tableWidget.setItem(
                i,
                0,
                QtGui.QTableWidgetItem(
                    self.__originalRoiNameDict[key][0])
                )
            # Original name is not editable
            self.tableWidget.item(i, 0).setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled)
            self.tableWidget.item(i, 0).setBackgroundColor(QtGui.QColor(gui.colours.RED))

            # Put combo boxes to extra columns
            self.tableWidget.setCellWidget(i, 1, txtStandard)
            self.tableWidget.setCellWidget(i, 2, combobox)
            self.tableWidget.setCellWidget(i, 3, cmbExtra)
            self.tableWidget.setCellWidget(i, 4, cmbMargin)
            self.tableWidget.setCellWidget(i, 5, cmbDose)

            # Automatic matching of RTStructs names is configurable
            j = 0 # Select first otherwise
            if ConfigDetails().autoRTStructMatch:
                # Find most promising agreement (first) to ROIName in default_values
                closest = get_close_matches(\
                    self.__originalRoiNameDict[key][0],\
                    rtsNames, 1, 0)[0]

                # Find position of closest name in
                j = rtsNames.index(closest)
            
            combobox.setCurrentIndex(j)

            self.logger.debug(self.__originalRoiNameDict[key][0] + \
                " initally mapped to: " + \
                self.formalizedRTStructs[j].identifier.encode("utf-8"))

            # Save presselected options to RoiNameDic
            self.__originalRoiNameDict[self.__originalRoiNumberList[i]].\
                append(self.formalizedRTStructs[j].identifier)

            # Show initial mapping in GUI
            txtStandard.setText(self.formalizedRTStructs[j].identifier.encode("utf-8"))

            # Enable additional info for L/R
            if self.__formalizedRTStructs[j].name in self._leftRightContours:
                cmbExtra.setEnabled(True)
                cmbExtra.setEditable(False)
                cmbExtra.clear()
                for lrItem in self._leftRightModel:
                    cmbExtra.addItem(lrItem[0], lrItem[1])
            # Enable additional info form multiple TV
            elif self.__formalizedRTStructs[j].name in self._tvMultipleContours:
                cmbExtra.setEnabled(True)
                cmbExtra.setEditable(False)
                cmbExtra.clear()
                for multiItem in self._tvMultipleModel:
                    cmbExtra.addItem(multiItem[0], multiItem[1])

            # Enable non standard additional info for contours of common type
            elif self.__formalizedRTStructs[j].name in self._extraTextContours:
                cmbExtra.setEnabled(True)
                cmbExtra.setEditable(True)
                cmbExtra.clear()
            else:
                cmbExtra.setEnabled(False)
                cmbExtra.setEditable(False)
                cmbExtra.clear()

            # Enable margin info for organ at risk OAR as well as TV
            if self.__formalizedRTStructs[j].name in self._oarContours:
                cmbMargin.setEnabled(True)
                cmbMargin.setEditable(True)
                cmbMargin.setValidator(QtGui.QIntValidator(0, 99, cmbMargin))
                cmbMargin.clear()
                for marginItem in self._oarMarginModel:
                    cmbMargin.addItem(marginItem[0], marginItem[1])
            elif self.__formalizedRTStructs[j].name in self._tvContours:
                cmbMargin.setEnabled(True)
                cmbMargin.setEditable(True)
                cmbMargin.setValidator(QtGui.QIntValidator(0, 99, cmbMargin))
                cmbMargin.clear()
            else:
                cmbMargin.setEnabled(False)
                cmbMargin.setEditable(False)
                cmbMargin.clear()

            # Enable dose info for target volume TV
            if self.__formalizedRTStructs[j].name in self._tvContours:
                cmbDose.setEnabled(True)
                cmbDose.setEditable(True)
                cmbDose.setValidator(QtGui.QIntValidator(0, 90000, cmbDose))
                cmbDose.clear()
            else:
                cmbDose.setEnabled(False)
                cmbDose.setEditable(False)
                cmbDose.clear()

            # Handler
            self.connect(combobox, QtCore.SIGNAL("currentIndexChanged(QString)"), self.updateMapping)
            self.connect(cmbExtra, QtCore.SIGNAL("editTextChanged(QString)"), self.updateDetailsMappingText)
            self.connect(cmbExtra, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateDetailsMappingCombo)
            self.connect(cmbMargin, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateMarginMappingCombo)
            self.connect(cmbMargin, QtCore.SIGNAL("editTextChanged(QString)"), self.updateMarginMappingText)
            self.connect(cmbDose, QtCore.SIGNAL("editTextChanged(QString)"), self.updateDoseMappingText)

            # Append combobox to list
            self.txtStandardisedList.append(txtStandard)
            self.comboBoxList.append(combobox)
            self.cmbExtraList.append(cmbExtra)
            self.cmbMarginList.append(cmbMargin)
            self.cmbDoseList.append(cmbDose)

##     ##    ###    ##    ## ########  ##       ######## ########   ######
##     ##   ## ##   ###   ## ##     ## ##       ##       ##     ## ##    ##
##     ##  ##   ##  ####  ## ##     ## ##       ##       ##     ## ##
######### ##     ## ## ## ## ##     ## ##       ######   ########   ######
##     ## ######### ##  #### ##     ## ##       ##       ##   ##         ##
##     ## ##     ## ##   ### ##     ## ##       ##       ##    ##  ##    ##
##     ## ##     ## ##    ## ########  ######## ######## ##     ##  ######

    def pushButtonClicked(self):
        """Ask user one more time if the mapping is correct, accept if Yes
        Remind him to provide a mapping if No.
        """

        question = "Are you sure about the mapping which you specified?\nThe DICOM RT structures will be renamed according to the mapping!"
        response = QtGui.QMessageBox.question(self, "Question",
                                              question,
                                              QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Yes).__or__(QtGui.QMessageBox.No), QtGui.QMessageBox.No)

        if response == QtGui.QMessageBox.Yes:
            super(DicomMappingDialog, self).accept()
        elif QtGui.QMessageBox.No:
            QtGui.QMessageBox.information(self, "Information", "Provide a propper mapping, in order to upload the files.")

    def updateMapping(self, value):
        """Changing a combobox activates this method, changing the mapping of the corresponding entry in self.dict_ROIName
        """
        # Which ROI (which row of combobox)
        row = self.comboBoxList.index(self.sender())
        # Get the key (key is original number of ROI)
        key = self.__originalRoiNumberList[row]
        # The index of formalized ROI
        index = self.sender().currentIndex()

        self.logger.debug("Original: " + self.__originalRoiNameDict[key][0])
        self.logger.debug("Previously selected: " + self.__originalRoiNameDict[key][1].encode("utf-8"))
        self.logger.debug("Selected index: " +  str(index) + " = " + value + " [" + str(self.__formalizedRTStructs[index].identifier) + "]")

        # Keep the original key and name but assign new name (1 index)
        self.__originalRoiNameDict[key][1] = str(self.__formalizedRTStructs[index].identifier)

        # Re-initialise extra column
        if self.__formalizedRTStructs[index].name in self._leftRightContours:
            self.cmbExtraList[row].setEnabled(True)
            self.cmbExtraList[row].setEditable(False)
            self.cmbExtraList[row].clear()
            self.cmbExtraList[row].clearEditText()
            for lrItem in self._leftRightModel:
                self.cmbExtraList[row].addItem(lrItem[0], lrItem[1])
        elif self.__formalizedRTStructs[index].name in self._tvMultipleContours:
            self.cmbExtraList[row].setEnabled(True)
            self.cmbExtraList[row].setEditable(False)
            self.cmbExtraList[row].clear()
            self.cmbExtraList[row].clearEditText()
            for multiItem in self._tvMultipleModel:
                self.cmbExtraList[row].addItem(multiItem[0], multiItem[1])

        elif self.__formalizedRTStructs[index].name in self._extraTextContours:
            self.cmbExtraList[row].setEnabled(True)
            self.cmbExtraList[row].setEditable(True)
            self.cmbExtraList[row].clear()
            self.cmbExtraList[row].clearEditText()
        else:
            self.cmbExtraList[row].setEnabled(False)
            self.cmbExtraList[row].clear()
            self.cmbExtraList[row].clearEditText()

        # Re-initialise margin column
        if self.__formalizedRTStructs[index].name in self._oarContours:
            self.cmbMarginList[row].setEnabled(True)
            self.cmbMarginList[row].setEditable(True)
            self.cmbMarginList[row].setValidator(QtGui.QIntValidator(0, 99, self.cmbMarginList[row]))
            self.cmbMarginList[row].clear()
            self.cmbMarginList[row].clearEditText()
            for marginItem in self._oarMarginModel:
                self.cmbMarginList[row].addItem(marginItem[0], marginItem[1])
        elif self.__formalizedRTStructs[index].name in self._tvContours:
            self.cmbMarginList[row].setEnabled(True)
            self.cmbMarginList[row].setEditable(True)
            self.cmbMarginList[row].setValidator(QtGui.QIntValidator(0, 99, self.cmbMarginList[row]))
            self.cmbMarginList[row].clear()
            self.cmbMarginList[row].clearEditText()
        else:
            self.cmbMarginList[row].setEnabled(False)
            self.cmbMarginList[row].clear()
            self.cmbMarginList[row].clearEditText()

        # Re-initialise dose column
        if self.__formalizedRTStructs[index].name in self._tvContours:
            self.cmbDoseList[row].setEnabled(True)
            self.cmbDoseList[row].setEditable(True)
            self.cmbDoseList[row].setValidator(QtGui.QIntValidator(0, 90000, self.cmbDoseList[row]))
            self.cmbDoseList[row].clear()
            self.cmbDoseList[row].clearEditText()
        else:
            self.cmbDoseList[row].setEnabled(False)
            self.cmbDoseList[row].setEditable(False)
            self.cmbDoseList[row].clear()
            self.cmbDoseList[row].clearEditText()

        # Show result
        self.txtStandardisedList[row].setText(self.__originalRoiNameDict[key][1])

        self.logger.info("Mapping details changed.")
        self.logger.info("Original: " + self.__originalRoiNameDict[key][0])
        self.logger.info("Newly selected: " + self.__originalRoiNameDict[key][1])

    def updateDetailsMappingText(self):
        """Changing a text box with details mapping
        """
        # Which ROI (which row of line edit)
        row = self.cmbExtraList.index(self.sender())
        # Get the key (key is original number of ROI)
        key = self.__originalRoiNumberList[row]

        # Assigned identifier
        identifier = str(self.comboBoxList[row].itemData(self.comboBoxList[row].currentIndex()).toString())
        label = str(self.comboBoxList[row].currentText().toUtf8()).decode("utf-8")

        # Re-initialise margin column
        if label in self._oarContours:
            self.cmbMarginList[row].setEnabled(True)
            self.cmbMarginList[row].setEditable(True)
            self.cmbMarginList[row].setValidator(QtGui.QIntValidator(0, 99, self.cmbMarginList[row]))
            self.cmbMarginList[row].clear()
            self.cmbMarginList[row].clearEditText()
            for marginItem in self._oarMarginModel:
                self.cmbMarginList[row].addItem(marginItem[0], marginItem[1])
        elif label in self._tvContours:
            self.cmbMarginList[row].setEnabled(True)
            self.cmbMarginList[row].setEditable(True)
            self.cmbMarginList[row].setValidator(QtGui.QIntValidator(0, 99, self.cmbMarginList[row]))
            self.cmbMarginList[row].clear()
            self.cmbMarginList[row].clearEditText()
        else:
            self.cmbMarginList[row].setEnabled(False)
            self.cmbMarginList[row].clear()
            self.cmbMarginList[row].clearEditText()

        # Re-initialise dose column
        if label in self._tvContours:
            self.cmbDoseList[row].setEnabled(True)
            self.cmbDoseList[row].setEditable(True)
            self.cmbDoseList[row].setValidator(QtGui.QIntValidator(0, 90000, self.cmbDoseList[row]))
            self.cmbDoseList[row].clear()
            self.cmbDoseList[row].clearEditText()
        else:
            self.cmbDoseList[row].setEnabled(False)
            self.cmbDoseList[row].setEditable(False)
            self.cmbDoseList[row].clear()
            self.cmbDoseList[row].clearEditText()

        # Extra text 
        extraText = ""
        if str(self.cmbExtraList[row].currentText().toUtf8()).decode("utf-8") is not "":
            extraText += str(self.cmbExtraList[row].currentText().toUtf8()).decode("utf-8")

        if extraText == "":
            self.__originalRoiNameDict[key][1] = identifier
        else:
            self.__originalRoiNameDict[key][1] = identifier + self._extraTextDelimiter + extraText

        # Show result
        self.txtStandardisedList[row].setText(self.__originalRoiNameDict[key][1])

        self.logger.info("Update mapping details text: " + self.__originalRoiNameDict[key][1])

    def updateDetailsMappingCombo(self, index):
        """Changing a combobox item with details mapping
        """
        # Which ROI (which row of line edit)
        row = self.cmbExtraList.index(self.sender())
        # Get the key (key is original number of ROI)
        key = self.__originalRoiNumberList[row]

        # Assigned identifier
        identifier = str(self.comboBoxList[row].itemData(self.comboBoxList[row].currentIndex()).toString())
        label = str(self.comboBoxList[row].currentText().toUtf8()).decode("utf-8")

        # Re-initialise margin column
        if label in self._oarContours:
            self.cmbMarginList[row].setEnabled(True)
            self.cmbMarginList[row].setEditable(True)
            self.cmbMarginList[row].setValidator(QtGui.QIntValidator(0, 99, self.cmbMarginList[row]))
            self.cmbMarginList[row].clear()
            self.cmbMarginList[row].clearEditText()
            for marginItem in self._oarMarginModel:
                self.cmbMarginList[row].addItem(marginItem[0], marginItem[1])
        elif label in self._tvContours:
            self.cmbMarginList[row].setEnabled(True)
            self.cmbMarginList[row].setEditable(True)
            self.cmbMarginList[row].setValidator(QtGui.QIntValidator(0, 99, self.cmbMarginList[row]))
            self.cmbMarginList[row].clear()
            self.cmbMarginList[row].clearEditText()
        else:
            self.cmbMarginList[row].setEnabled(False)
            self.cmbMarginList[row].clear()
            self.cmbMarginList[row].clearEditText()

         # Re-initialise dose column
        if label in self._tvContours:
            self.cmbDoseList[row].setEnabled(True)
            self.cmbDoseList[row].setEditable(True)
            self.cmbDoseList[row].setValidator(QtGui.QIntValidator(0, 90000, self.cmbDoseList[row]))
            self.cmbDoseList[row].clear()
            self.cmbDoseList[row].clearEditText()
        else:
            self.cmbDoseList[row].setEnabled(False)
            self.cmbDoseList[row].setEditable(False)
            self.cmbDoseList[row].clear()
            self.cmbDoseList[row].clearEditText()

        # Laterality (L, R) option or description
        extraText = ""
        if str(self.cmbExtraList[row].currentText().toUtf8()).decode("utf-8") is not "":
            # L, R options
            if str(self.cmbExtraList[row].currentText().toUtf8()).decode("utf-8") in ["left", "right"]:

                extraText = str(self.cmbExtraList[row].itemData(index).toPyObject())
            # Description
            else:
                extraText += str(self.cmbExtraList[row].currentText().toUtf8()).decode("utf-8")

        self.__originalRoiNameDict[key][1] = identifier + extraText

        # Show result
        self.txtStandardisedList[row].setText(self.__originalRoiNameDict[key][1])

        self.logger.info("Update mapping details combo box: " + self.__originalRoiNameDict[key][1])

    def updateMarginMappingCombo(self, index):
        """Changing a combobox item with the OAR margin mapping
        """
        # Which ROI (which row of line edit)
        row = self.cmbMarginList.index(self.sender())
        # Get the key (key is original number of ROI)
        key = self.__originalRoiNumberList[row]

        # Assigned identifier
        identifier = str(self.comboBoxList[row].itemData(self.comboBoxList[row].currentIndex()).toString())
        # Laterality (L, R) option
        extraText = str(self.cmbExtraList[row].itemData(self.cmbExtraList[row].currentIndex()).toString())
        # Margin for OAR
        marginText = str(self.cmbMarginList[row].itemData(self.cmbMarginList[row].currentIndex()).toString())

        self.__originalRoiNameDict[key][1] = identifier + extraText + marginText

        # Show result
        self.txtStandardisedList[row].setText(self.__originalRoiNameDict[key][1])

        self.logger.info("Update mapping margin combo box: " + self.__originalRoiNameDict[key][1])

    def updateMarginMappingText(self):
        """Changing a text box with the OAR or TV margin mapping
        """
        # Which ROI (which row of line edit)
        row = self.cmbMarginList.index(self.sender())
        # Get the key (key is original number of ROI)
        key = self.__originalRoiNumberList[row]

        # Assigned identifier
        identifier = str(self.comboBoxList[row].itemData(self.comboBoxList[row].currentIndex()).toString())
        
        # Laterality (L, R) option
        extraText = str(self.cmbExtraList[row].itemData(self.cmbExtraList[row].currentIndex()).toString())
        isNonStandard = False
        if str(self.cmbExtraList[row].currentText().toUtf8()).decode("utf-8") is not "":
            # L/R options
            if str(self.cmbExtraList[row].currentText().toUtf8()).decode("utf-8") in ["left", "right"]:
                extraText = str(self.cmbExtraList[row].itemData(self.cmbExtraList[row].currentIndex()).toPyObject())
            # Index options
            elif str(self.cmbExtraList[row].currentText().toUtf8()).decode("utf-8") in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                extraText = str(self.cmbExtraList[row].itemData(self.cmbExtraList[row].currentIndex()).toPyObject())
            # Non standard Description
            else:
                extraText += str(self.cmbExtraList[row].currentText().toUtf8()).decode("utf-8")
                isNonStandard = True

        # Add special delimiter for non standard extra text
        if isNonStandard and extraText != "":
            extraText = self._extraTextDelimiter + extraText

        # Margin for OAR
        marginText = ""
        if str(self.cmbMarginList[row].currentText().toUtf8()).decode("utf-8") is not "":
            # 0 or nonuniform options are handled in different handler
            if (str(self.cmbMarginList[row].currentText().toUtf8()).decode("utf-8") == "0" or
                str(self.cmbMarginList[row].currentText().toUtf8()).decode("utf-8") == "nonuniform"):
                return
            # Integer value in mm
            else:
                marginText += str(self.cmbMarginList[row].currentText().toUtf8()).decode("utf-8")

        # Format for int with one leading 0
        if marginText != "" and marginText != "+":
            marginText = "%02d" % (int(marginText))

        # Dose for TV
        doseText = ""
        if str(self.cmbDoseList[row].currentText().toUtf8()).decode("utf-8") is not "":

            # Integer value in cGy
            doseText += str(self.cmbDoseList[row].currentText().toUtf8()).decode("utf-8")

        # Reformat int to string
        if doseText != "" and doseText != "+":
            doseText = str(int(doseText))

        if marginText == "" and doseText == "":
            self.__originalRoiNameDict[key][1] = identifier + extraText
        elif marginText == "":
            if isNonStandard:
                self.__originalRoiNameDict[key][1] = identifier + "_" + doseText + extraText
            else:
                self.__originalRoiNameDict[key][1] = identifier + extraText + "_" + doseText
        elif doseText == "":
            if isNonStandard:
                self.__originalRoiNameDict[key][1] = identifier + "_" + marginText + extraText 
            else:
                self.__originalRoiNameDict[key][1] = identifier + extraText + "_" + marginText
        else:
            if isNonStandard:
                self.__originalRoiNameDict[key][1] = identifier + "_" + marginText + "_" + doseText + extraText
            else:
                self.__originalRoiNameDict[key][1] = identifier + extraText + "_" + marginText + "_" + doseText

        # Show result
        self.txtStandardisedList[row].setText(self.__originalRoiNameDict[key][1])

        self.logger.info("Update mapping margin text: " + self.__originalRoiNameDict[key][1])

    def updateDoseMappingText(self):
        """Changing a text box with the TV dose mapping
        """
        # Which ROI (which row of line edit)
        row = self.cmbDoseList.index(self.sender())
        # Get the key (key is original number of ROI)
        key = self.__originalRoiNumberList[row]

        # Assigned identifier
        identifier = str(self.comboBoxList[row].itemData(self.comboBoxList[row].currentIndex()).toString())
        # Extra or number of TV option
        extraText = str(self.cmbExtraList[row].itemData(self.cmbExtraList[row].currentIndex()).toString())
        isNonStandard = False
        if str(self.cmbExtraList[row].currentText().toUtf8()).decode("utf-8") is not "":
            # Index options
            if (str(self.cmbExtraList[row].currentText().toUtf8()).decode("utf-8") in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]):
                extraText = str(self.cmbExtraList[row].itemData(self.cmbExtraList[row].currentIndex()).toPyObject())
            # Non standard Description
            else:
                extraText += str(self.cmbExtraList[row].currentText().toUtf8()).decode("utf-8")
                isNonStandard = True

        # Add special delimiter for non standard extra text
        if isNonStandard and extraText != "":
            extraText = self._extraTextDelimiter + extraText

        # Margin from previous TV
        marginText = ""
        if str(self.cmbMarginList[row].currentText().toUtf8()).decode("utf-8") is not "":
 
            # Integer value in mm from previous TV    
            marginText += str(self.cmbMarginList[row].currentText().toUtf8()).decode("utf-8")

        # Format for int with one leading 0
        if marginText != "" and marginText != "+":
            marginText = "%02d" % (int(marginText))

        # Dose for TV
        doseText = ""
        if str(self.cmbDoseList[row].currentText().toUtf8()).decode("utf-8") is not "":

            # Integer value in cGy
            doseText += str(self.cmbDoseList[row].currentText().toUtf8()).decode("utf-8")

        # Reformat int to string
        if doseText != "" and doseText != "+":
            doseText = str(int(doseText))

        if marginText == "" and doseText == "":
            self.__originalRoiNameDict[key][1] = identifier + extraText
        elif marginText == "":
            if isNonStandard:
                self.__originalRoiNameDict[key][1] = identifier + "_" + doseText + extraText
            else:
                self.__originalRoiNameDict[key][1] = identifier + extraText + "_" + doseText
        elif doseText == "":
            if isNonStandard:
                self.__originalRoiNameDict[key][1] = identifier + "_" + marginText + extraText 
            else:
                self.__originalRoiNameDict[key][1] = identifier + extraText + "_" + marginText
        else:
            if isNonStandard:
                self.__originalRoiNameDict[key][1] = identifier + "_" + marginText + "_" + doseText + extraText
            else:
                self.__originalRoiNameDict[key][1] = identifier + extraText + "_" + marginText + "_" + doseText 

        # Show result
        self.txtStandardisedList[row].setText(self.__originalRoiNameDict[key][1])

        self.logger.info("Update mapping dose text: " + self.__originalRoiNameDict[key][1])

 ######   #######  ##     ## ##     ##    ###    ##    ## ########   ######
##    ## ##     ## ###   ### ###   ###   ## ##   ###   ## ##     ## ##    ##
##       ##     ## #### #### #### ####  ##   ##  ####  ## ##     ## ##
##       ##     ## ## ### ## ## ### ## ##     ## ## ## ## ##     ##  ######
##       ##     ## ##     ## ##     ## ######### ##  #### ##     ##       ##
##    ## ##     ## ##     ## ##     ## ##     ## ##   ### ##     ## ##    ##
 ######   #######  ##     ## ##     ## ##     ## ##    ## ########   ######

    def initializeData(self):
        """Initialize data properties for UI
        """
        # Dictionary, key is the original number of ROI,
        # value is a list where 0 element is original name and 1 element is choosen name
        self.__originalRoiNameDict = {}
        # The keys are stored also here
        self.__originalRoiNumberList = []
        # Formalized RTStructures loaded from DB
        self.__formalizedRTStructs = []
