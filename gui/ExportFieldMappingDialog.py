#----------------------------------------------------------------------
#------------------------------ Modules -------------------------------
# PyQt
import sys

from PyQt4 import QtGui, QtCore, uic

from converters.DateConverter import DateConverter
from converters.FloatConverter import FloatConverter
from utils import first


# Standard
# Utils
# Converters
#----------------------------------------------------------------------
class ExportFieldMappingDialog(QtGui.QDialog):
    """Export Field Mapping dialog
    """

    #----------------------------------------------------------------------
    #--------------------------- Constructors -----------------------------

    def __init__(self, parent = None):
        """
        """
        QtGui.QDialog.__init__(self, parent)

        #------------------------------------------------------
        #-------------------- GUI -----------------------------
        self.width = 700
        self.height = 600
        self.setFixedSize(self.width, self.height);
        self.setWindowTitle("Map data field to metadata field for export")

        # Dialog layout root
        rootLayout = QtGui.QVBoxLayout(self)

        # Metadata field for mapping UI
        rootLayout.addWidget(self.__setupMetadataFieldUI())
        # Date Tranformation UI
        rootLayout.addWidget(self.__setupDateTransformationGroupUI())
        # Float Transformation UI
        rootLayout.addWidget(self.__setupFloatTransformationGroupUI())
        # Code List Transformation UI
        rootLayout.addWidget(self.__setupCodeListTransformationGroupUI())
        # Data mapping preview UI
        rootLayout.addWidget(self.__setupDataMappingPreviewUI())

        # Dialog buttons
        btnLayout = QtGui.QGridLayout()
        btnLayout.setSpacing(10)
        rootLayout.addLayout(btnLayout)

        self.btnOk = QtGui.QPushButton("Ok")
        self.btnCancel = QtGui.QPushButton("Cancel")

        btnLayout.addWidget(self.btnOk, 1, 0)
        btnLayout.addWidget(self.btnCancel, 1, 1)

        #----------------------------------------------------------
        #----------------- Event handlers -------------------------

        self.btnOk.clicked.connect(self.handleOk)
        self.btnCancel.clicked.connect(self.handleCancel)

        #-----------------------------------------------------------
        #------------------ View Models ----------------------------
        self.dataHeaders = []
        self.dataMapping = None
        self.dataService = None

    #----------------------------------------------------------------------
    #--------------------------- Setup UI  --------------------------------

    def __setupMetadataFieldUI(self):
        """
        """
        # Dialog grid
        layout = QtGui.QGridLayout()
        self.metadataFieldGroup = QtGui.QGroupBox('Metadata field:')
        self.metadataFieldGroup.setLayout(layout)

        lblMetadataFieldText = QtGui.QLabel("Study metadata field: ")
        self.lblMetadataField = QtGui.QLabel()

        lblMetadataDataFormat = QtGui.QLabel("Study metadata format:")
        self.lblMetadataFieldFormat = QtGui.QLabel()

        lblDataFieldText = QtGui.QLabel("Assign to data field: ")
        self.cmbDataFields = QtGui.QComboBox()

        # Add to layout
        layout.addWidget(lblMetadataFieldText, 0, 0)
        layout.addWidget(self.lblMetadataField, 0, 1)

        layout.addWidget(lblMetadataDataFormat, 1, 0)
        layout.addWidget(self.lblMetadataFieldFormat, 1, 1)

        layout.addWidget(lblDataFieldText, 2, 0)
        layout.addWidget(self.cmbDataFields, 2, 1)

        self.cmbDataFields.currentIndexChanged['QString'].connect(self.cmbDataFieldsChanged)

        return self.metadataFieldGroup


    def __setupDateTransformationGroupUI(self):
        """
        """
        # Date transformation UI
        dateTransformationLayout = QtGui.QGridLayout()
        self.dateTransformationGroup = QtGui.QGroupBox("Date format transformation:")
        self.dateTransformationGroup.setLayout(dateTransformationLayout)

        self.chbYear = QtGui.QCheckBox("year")
        self.chbMonth = QtGui.QCheckBox("month")
        self.chbDay = QtGui.QCheckBox("day")
        dateStructureGroup = QtGui.QGroupBox("Raw data date consists of: ")
        dateStructureBox = QtGui.QVBoxLayout()
        dateStructureGroup.setLayout(dateStructureBox)
        dateStructureBox.addWidget(self.chbYear)
        dateStructureBox.addWidget(self.chbMonth)
        dateStructureBox.addWidget(self.chbDay)
        dateStructureBox.addStretch(1)

        self.rbtnDash = QtGui.QRadioButton("-")
        self.rbtnDot = QtGui.QRadioButton(".")
        self.rbtnSlash = QtGui.QRadioButton("/")
        dateSeparatorGroup = QtGui.QGroupBox("Date separator is: ")
        dateSeparatorBox= QtGui.QVBoxLayout();
        dateSeparatorGroup.setLayout(dateSeparatorBox)
        dateSeparatorBox.addWidget(self.rbtnDash)
        dateSeparatorBox.addWidget(self.rbtnDot)
        dateSeparatorBox.addWidget(self.rbtnSlash)
        dateSeparatorBox.addStretch(1)

        self.rbtnDayYear = QtGui.QRadioButton("day-month-year")
        self.rbtnYearDay = QtGui.QRadioButton("year-month-day")
        dateOrderGroup = QtGui.QGroupBox("Date order is: ")
        dateOrderBox= QtGui.QVBoxLayout()
        dateOrderGroup.setLayout(dateOrderBox)
        dateOrderBox.addWidget(self.rbtnDayYear)
        dateOrderBox.addWidget(self.rbtnYearDay)
        dateOrderBox.addStretch(1)

        dateTransformationLayout.addWidget(dateStructureGroup, 0, 0)
        dateTransformationLayout.addWidget(dateSeparatorGroup, 0, 1)
        dateTransformationLayout.addWidget(dateOrderGroup, 0, 2)

        self.chbYear.stateChanged.connect(self.chbYearStateChanged)
        self.chbMonth.stateChanged.connect(self.chbMonthStateChanged)
        self.chbDay.stateChanged.connect(self.chbDayStateChanged)

        self.rbtnDash.toggled.connect(self.rbtnDashToggled)
        self.rbtnDot.toggled.connect(self.rbtnDotToggled)
        self.rbtnSlash.toggled.connect(self.rbtnSlashToggled)

        self.rbtnDayYear.toggled.connect(self.rbtnDayYearToggled)
        self.rbtnYearDay.toggled.connect(self.rbtnYearDayToggled)

        return self.dateTransformationGroup


    def __setupFloatTransformationGroupUI(self):
        """
        """
        # Float transformation UI
        floatTransformationLayout = QtGui.QGridLayout()
        self.floatTransformationGroup = QtGui.QGroupBox("Float format transformation: ")
        self.floatTransformationGroup.setLayout(floatTransformationLayout)

        self.rbtnFloatComma = QtGui.QRadioButton(",")
        self.rbtnFloatDot = QtGui.QRadioButton(".")
        floatSeparatorGroup = QtGui.QGroupBox("Floating number delimiter is: ")
        # TODO: GroupBox seems to add a margin which does not look nice in GUI
        floatSeparatorBox= QtGui.QHBoxLayout();
        floatSeparatorGroup.setLayout(floatSeparatorBox)
        floatSeparatorBox.addWidget(self.rbtnFloatComma)
        floatSeparatorBox.addWidget(self.rbtnFloatDot)
        floatSeparatorBox.addStretch(1)

        floatTransformationLayout.addWidget(floatSeparatorGroup, 0, 0)

        self.rbtnFloatComma.toggled.connect(self.rbtnFloatCommaToggled)
        self.rbtnFloatDot.toggled.connect(self.rbtnFloatDotToggled)

        return self.floatTransformationGroup


    def __setupCodeListTransformationGroupUI(self):
        """
        """
        # Code transformation UI
        codeListTransformationLayout = QtGui.QGridLayout()

        self.codeListTransformationGroup = QtGui.QGroupBox('Code list format transformation:')
        self.codeListTransformationGroup.setLayout(codeListTransformationLayout)

        lblUseCodeListText = QtGui.QLabel("Use metadata defined code list to encode data:\n (Raw data is not coded according to list)")
        chbUseCodeList = QtGui.QCheckBox()

        lblCodeListText = QtGui.QLabel("Defined code list for this data item: ")
        self.tvCodeList = QtGui.QTableView()

        codeListTransformationLayout.addWidget(lblUseCodeListText, 0, 0)
        codeListTransformationLayout.addWidget(chbUseCodeList, 0, 1)

        codeListTransformationLayout.addWidget(lblCodeListText, 1, 0)
        codeListTransformationLayout.addWidget(self.tvCodeList, 1, 1)

        chbUseCodeList.stateChanged.connect(self.chbUseCodeListChanged)

        return self.codeListTransformationGroup


    def __setupDataMappingPreviewUI(self):
        """
        """
        # Data mapping preview UI
        previewLayout = QtGui.QGridLayout()
        self.previewGroup = QtGui.QGroupBox('Data mapping preview:')
        self.previewGroup.setLayout(previewLayout)

        btnValidateMapping = QtGui.QPushButton("Validate mapping")

        self.tvDataMappingPreview = QtGui.QTableView()

        previewLayout.addWidget(btnValidateMapping, 1, 0)
        previewLayout.addWidget(self.tvDataMappingPreview, 2, 0, 2, 1)

        btnValidateMapping.clicked.connect(self.btnValidateMappingClicked)

        return self.previewGroup

    #----------------------------------------------------------------------
    #--------------------------- Set View Model ---------------------------

    def setData(self, dataMapping, dataHeaders):
        """
        """
        # Data bidned to dialog UI
        self.dataHeaders = dataHeaders
        self.dataMapping = dataMapping

        self.lblMetadataField.setText(dataMapping.metadata)
        self.lblMetadataFieldFormat.setText(dataMapping.dataType)

        self.cmbDataFields.addItems(self.dataHeaders)

        # Visibility of UI depended on type dataFormat of metadata element
        # Date format
        if dataMapping.dataType == "partialDate" or dataMapping.dataType == "date":
            self.dateConverter = DateConverter()

            self.dataMapping.setConverter(self.dateConverter)

            self.dateTransformationGroup.setVisible(True)
            self.floatTransformationGroup.setVisible(False)
            self.codeListTransformationGroup.setVisible(False)
        # Float format
        elif dataMapping.dataType == "float":
            self.floatConverter = FloatConverter()

            self.dataMapping.setConverter(self.floatConverter)

            self.floatTransformationGroup.setVisible(True)
            self.dateTransformationGroup.setVisible(False)
            self.codeListTransformationGroup.setVisible(False)
        # Integer format - needed for coded list
        elif dataMapping.dataType == "integer" and dataMapping.codeList is not None:
            self.codeListTransformationGroup.setVisible(True)
            self.dateTransformationGroup.setVisible(False)
            self.floatTransformationGroup.setVisible(False)

            codeListModel = QtGui.QStandardItemModel()
            codeListModel.setHorizontalHeaderLabels(["Metadata values", "Meaning"])

            if self.dataMapping.codeList is not None:
                row = 0
                for itm in self.dataMapping.codeList.listItems:
                    iCodedValue = QtGui.QStandardItem(itm.codedValue)
                    iDecodedValue = QtGui.QStandardItem(itm.decodedValue)
                    codeListModel.setItem(row, 0, iCodedValue)
                    codeListModel.setItem(row, 1, iDecodedValue)
                    row = row + 1

            self.tvCodeList.setModel(codeListModel)
            self.tvCodeList.resizeColumnsToContents()

        #If neccessary also for text, URI
        else:
            self.dateTransformationGroup.setVisible(False)
            self.floatTransformationGroup.setVisible(False)
            self.codeListTransformationGroup.setVisible(False)

    #----------------------------------------------------------------------
    #------------------- Code List Form Event Handlers -------------------------

    def chbUseCodeListChanged(self, state):
        """
        """
        if state == QtCore.Qt.Checked:
            self.dataMapping.setUseCodeListToEncodeData(True)
        else:
            self.dataMapping.setUseCodeListToEncodeData(False)

    #----------------------------------------------------------------------
    #------------------- Date Form Event Handlers -------------------------

    def chbYearStateChanged(self, state):
        """
        """
        if state == QtCore.Qt.Checked:
            self.dateConverter.setHasYearComponet(True)
        else:
            self.dateConverter.setHasYearComponet(False)


    def chbMonthStateChanged(self, state):
        """
        """
        if state == QtCore.Qt.Checked:
            self.dateConverter.setHasMonthComponet(True)
        else:
            self.dateConverter.setHasMonthComponet(False)


    def chbDayStateChanged(self, state):
        """
        """
        if state == QtCore.Qt.Checked:
            self.dateConverter.setHasDayComponet(True)
        else:
            self.dateConverter.setHasDayComponet(False)


    def rbtnDashToggled(self, enabled):
        if enabled:
            self.dateConverter.setDateSeparator("-")


    def rbtnDotToggled(self, enabled):
        if enabled:
            self.dateConverter.setDateSeparator(".")


    def rbtnSlashToggled(self, enabled):
        if enabled:
            self.dateConverter.setDateSeparator("/")


    def rbtnDayYearToggled(self, enabled):
        if enabled:
            self.dateConverter.setIsIsoOrdered(False)


    def rbtnYearDayToggled(self, enabled):
        if enabled:
            self.dateConverter.setIsIsoOrdered(False)

    #----------------------------------------------------------------------
    #------------------- Float Form Event Handlers ------------------------

    def rbtnFloatCommaToggled(self, enabled):
        if enabled:
            self.floatConverter.setFloatingNumberDelimiter(",")


    def rbtnFloatDotToggled(self, enabled):
        if enabled:
            self.floatConverter.setFloatingNumberDelimiter(".")

    #----------------------------------------------------------------------
    #------------------- Preview Form Event Handlers ------------------------

    def btnValidateMappingClicked(self):
        """
        """
        errors = []

        row = 0
        for data in self.dataValues:
            try:
                transformedData = self.dataMapping.map(data)
                itemTransformedData = QtGui.QStandardItem(transformedData)

                #TODO: if it has code list check if itemTransformedData has a value from coded list

                self.model.setItem(row, 1, itemTransformedData)
                row = row + 1
            except ValueError as detail:
                errors.append("Conversion error on line " + str(row + 1) + " details: " + detail)
                row = row + 1

        self.tvDataMappingPreview.setModel(self.model)
        self.tvDataMappingPreview.resizeColumnsToContents()

        if errors is not []:
            pass
            # TODO: show dialog vith list of errors occured during mapping


    def cmbDataFieldsChanged(self, text):
        """
        """
        # Selected data to map to metadata
        self.dataMapping.data = first.first(dataHeader for dataHeader in self.dataHeaders if dataHeader == text)

        # Now extract data values from data file according to selection
        self.dataValues = []

        # Load data values from data file according to selection
        for i in range (1, self.dataService.size()):
            dataRow = self.dataService.getRow(i)
            dataIndex = self.dataService.headers.index(self.dataMapping.data)
            dataValue = dataRow[dataIndex]

            self.dataValues.append(dataValue)

        # Create view model for preview table view
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Raw Data", "Mapping transformed data"])

        row = 0
        for data in self.dataValues:
            itemDataField = QtGui.QStandardItem(data)
            itemTransformedData = QtGui.QStandardItem("")
            self.model.setItem(row, 0, itemDataField)
            self.model.setItem(row, 1, itemTransformedData)
            row = row + 1

        self.tvDataMappingPreview.setModel(self.model)
        self.tvDataMappingPreview.resizeColumnsToContents()


    #----------------------------------------------------------------------
    #------------------- Dialog Buttons Handlers --------------------------

    def handleOk(self):
        """OK Button Click
        """
        if (self.dataMapping.isComplete()):
            self.accept()
        else:
            QtGui.QMessageBox.warning(self, 'Error', 'Specified data mapping for this metadata field is not complete.')


    def handleCancel(self):
        """Cancel Button Click
        """
        self.reject()

