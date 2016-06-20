#----------------------------------------------------------------------
#------------------------------ Modules -------------------------------
# PyQt
import sys

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import pyqtSlot, SIGNAL, SLOT


# Standard
# UTF 8
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

#----------------------------------------------------------------------

class ExportModuleUI(object):
    """Export Module UI definition
    """

    #-------------------------------------------------------------------
    #-------------------- UI -------------------------------------------

    def setupUi(self, Module):
        """
        """
        #----------------------------------------------------------------------
        #--------------------------- Module -----------------------------------
        self.centralwidget = QtGui.QWidget(Module)
        self.centralwidget.setObjectName(_fromUtf8("exportModule"))
        self.rootLayout = QtGui.QVBoxLayout(self.parent)
        #----------------------------------------------------------------------
        #---------------------------- Icons -----------------------------------
        newIconRes = ':/images/new.png'
        reloadIconRes = ':/images/reload.png'
        saveIconRes = ':/images/save.png'
        detailsIconRes = ':/images/details.png'
        deleteIconRes = ':/images/delete.png'
        reloadIconRes = ':/images/reload.png'

        self.reloadIcon = QtGui.QIcon()
        self.reloadIcon.addPixmap(QtGui.QPixmap(reloadIconRes));

        self.newIcon = QtGui.QIcon()
        self.newIcon.addPixmap(QtGui.QPixmap(newIconRes))

        self.saveIcon = QtGui.QIcon()
        self.saveIcon.addPixmap(QtGui.QPixmap(saveIconRes))

        self.deleteIcon = QtGui.QIcon()
        self.deleteIcon.addPixmap(QtGui.QPixmap(deleteIconRes))

        self.detailsIcon = QtGui.QIcon()
        self.detailsIcon.addPixmap(QtGui.QPixmap(detailsIconRes))

        #----------------------------------------------------------------------
        #--------------------- Setup UI----------------------------------------
        self.rootLayout.addLayout(self.__setupToolbarButtonsUI())
        self.rootLayout.addWidget(self.__setupModuleTabs())

        # Module tabs UI
        self.__setupPullDataRequestUI()
        self.__setupDataMappingUI()
        self.__setupStudyDataUI()
        self.__setupSubjectsUI()
        self.__setupDicomMappingUI()
        self.__setupPushResponseUI()

        self.rootLayout.addLayout(self.__setupWizzardButtonsUI())

        #----------------------------------------------------------------------
        #---- Put defined central widget into ManWindow central widget --------
        self.retranslateUi(Module)
        QtCore.QMetaObject.connectSlotsByName(Module)


    #-------------------------------------------------------------------
    #-------------------- Setup Module UI ------------------------------

    def __setupToolbarButtonsUI(self):
        """
        """
        # Buttons toolbar
        # TODO: encapsulate this to global application UI settings
        toolbarButtonSize = 25

        toolbarGrid = QtGui.QHBoxLayout()

        self.btnReload = QtGui.QPushButton()
        self.btnReload.setIcon(self.reloadIcon)
        self.btnReload.setToolTip("reload")
        self.btnReload.setIconSize(QtCore.QSize(toolbarButtonSize, toolbarButtonSize))

        self.btnNew = QtGui.QPushButton()
        self.btnNew.setIcon(self.newIcon)
        self.btnNew.setToolTip("new")
        self.btnNew.setIconSize(QtCore.QSize(toolbarButtonSize, toolbarButtonSize))

        self.btnDetails = QtGui.QPushButton()
        self.btnDetails.setIcon(self.detailsIcon)
        self.btnDetails.setToolTip("edit details")
        self.btnDetails.setIconSize(QtCore.QSize(toolbarButtonSize, toolbarButtonSize))

        self.btnSave = QtGui.QPushButton()
        self.btnSave.setIcon(self.saveIcon)
        self.btnSave.setToolTip("save")
        self.btnSave.setIconSize(QtCore.QSize(toolbarButtonSize, toolbarButtonSize))

        self.btnDelete = QtGui.QPushButton()
        self.btnDelete.setIcon(self.deleteIcon)
        self.btnDelete.setToolTip("delete")
        self.btnDelete.setIconSize(QtCore.QSize(toolbarButtonSize, toolbarButtonSize))

        self.btnGeneratePID = QtGui.QPushButton()

        self.btnMapExportField = QtGui.QPushButton()

        space = QtGui.QSpacerItem(1000, 0)

        toolbarGrid.addWidget(self.btnReload,)
        toolbarGrid.addWidget(self.btnNew,)
        toolbarGrid.addWidget(self.btnDetails)
        toolbarGrid.addWidget(self.btnSave)
        toolbarGrid.addWidget(self.btnDelete)
        toolbarGrid.addWidget(self.btnMapExportField)

        # The rest of toolbar button row
        toolbarGrid.addItem(space)

        return toolbarGrid


    def __setupModuleTabs(self):
        """
        """
        self.tabExportModule = QtGui.QTabWidget()
        self.connect(self.tabExportModule, SIGNAL('currentChanged(int)'), self.moduleTabChanged)

        # Create tabs
        tabPullRequests = QtGui.QWidget()
        tabStudyData = QtGui.QWidget()
        tabSubjects = QtGui.QWidget()
        tabDicomMapping = QtGui.QWidget()
        tabDataMapping = QtGui.QWidget()
        tabPushResponse = QtGui.QWidget()

        # Add tabs to widget
        self.tabExportModule.addTab(tabPullRequests, "Data pull requests")
        self.tabExportModule.addTab(tabStudyData, "Study data")
        self.tabExportModule.addTab(tabSubjects, "Study subjects")
        self.tabExportModule.addTab(tabDicomMapping, "DICOM mapping")
        self.tabExportModule.addTab(tabDataMapping, "Export data mapping")
        self.tabExportModule.addTab(tabPushResponse, "Data push response")

        # Enable the first tab
        for i in range (1, self.tabExportModule.count()):
            self.tabExportModule.setTabEnabled(i, False)

        # Define layout for tabs
        self.layoutPullRequests = QtGui.QVBoxLayout(tabPullRequests)
        self.layoutStudyData = QtGui.QVBoxLayout(tabStudyData)
        self.layoutSubjects = QtGui.QVBoxLayout(tabSubjects)
        self.layoutDicomMapping = QtGui.QVBoxLayout(tabDicomMapping)
        self.layoutExport = QtGui.QVBoxLayout(tabDataMapping)
        self.layoutPushResponse = QtGui.QVBoxLayout(tabPushResponse)

        return self.tabExportModule


    def __setupPullDataRequestUI(self):
        """
        """
        # Table View
        self.tvPullDataRequests = QtGui.QTableView()
        self.layoutPullRequests.addWidget(self.tvPullDataRequests)

        # Behaviour for the table views - select single row
        self.tvPullDataRequests.setAlternatingRowColors(True)
        self.tvPullDataRequests.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tvPullDataRequests.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)


    def __setupStudyDataUI(self):
        """
        """
        studyDataGrid = QtGui.QGridLayout()
        studyDataGrid.setSpacing(10)

        self.layoutStudyData.addLayout(studyDataGrid)

        # Study metadata file .xml
        lblMetaDataFilename = QtGui.QLabel("Study metadata file (*.xml): ")
        self.txtMetaDataFilename = QtGui.QLineEdit()
        self.btnLocateMetaDataFilename = QtGui.QPushButton()

        # Study
        lblStudyText = QtGui.QLabel("Study: ")
        self.lblStudy = QtGui.QLabel()

        # Study event to export
        lblStudyEventText = QtGui.QLabel("Study event: ")
        self.cmbStudyEvent = QtGui.QComboBox()

        # Event for to export
        lblFormText = QtGui.QLabel("CRF Form: ")
        self.cmbEventForm = QtGui.QComboBox()

        # Study data file, could be .csv or .odm or zipped .odm files
        lblDataFilename = QtGui.QLabel("Study data file (*.csv): ")
        self.txtDataFilename = QtGui.QLineEdit()
        self.btnLocateDataFilename = QtGui.QPushButton()

        # Load mapping
        self.btnLoadMapping = QtGui.QPushButton()
        self.btnLoadMapping.setMinimumHeight(160)

         # Add to connection layout
        studyDataGrid.addWidget(lblMetaDataFilename, 0, 0)
        studyDataGrid.addWidget(self.txtMetaDataFilename, 0, 1, 1, 8)
        studyDataGrid.addWidget(self.btnLocateMetaDataFilename, 0, 9)

        studyDataGrid.addWidget(lblStudyText, 1, 0)
        studyDataGrid.addWidget(self.lblStudy, 1, 1, 1, 8)

        studyDataGrid.addWidget(lblStudyEventText, 2, 0)
        studyDataGrid.addWidget(self.cmbStudyEvent, 2, 1, 1, 8)

        studyDataGrid.addWidget(lblFormText, 3, 0)
        studyDataGrid.addWidget(self.cmbEventForm, 3, 1, 1, 8)

        studyDataGrid.addWidget(lblDataFilename, 4, 0)
        studyDataGrid.addWidget(self.txtDataFilename, 4, 1, 1, 8)
        studyDataGrid.addWidget(self.btnLocateDataFilename, 4, 9)

        studyDataGrid.addWidget(self.btnLoadMapping, 0, 10, 4, 1)


    def __setupSubjectsUI(self):
        subjectsGrid = QtGui.QGridLayout()
        subjectsGrid.setSpacing(10)

        self.layoutSubjects.addLayout(subjectsGrid)

        lblSubjectID = QtGui.QLabel("Choose field from you data file which contains subject id:")
        self.cmbSubjectID = QtGui.QComboBox()

        # TODO: no such id field in data every line is unique subject

        lblNrOfSubjects = QtGui.QLabel("Count of subjects in your data file:")
        self.lblSubjectsCount = QtGui.QLabel()

        lblIsIdPid = QtGui.QLabel("Can the choosen ID be used as PID:")
        self.chbIsIdPid = QtGui.QCheckBox()

        lblPidGenerator = QtGui.QLabel("PID generator: ")
        self.lblSelectedPidGenerator = QtGui.QLabel()

        # Root path to dicom data
        lblPatientsDicomRoot = QtGui.QLabel("")

        subjectsGrid.addWidget(lblSubjectID, 0, 0)
        subjectsGrid.addWidget(self.cmbSubjectID, 0, 1)

        subjectsGrid.addWidget(lblIsIdPid, 1, 0)
        subjectsGrid.addWidget(self.chbIsIdPid, 1, 1)

        subjectsGrid.addWidget(lblPidGenerator, 2, 0)
        subjectsGrid.addWidget(self.lblSelectedPidGenerator, 2, 1)

        self.tvSubjects = QtGui.QTableView()
        self.layoutSubjects.addWidget(self.tvSubjects)

         # Behaviour for the table views - select single row
        self.tvSubjects.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tvSubjects.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)


    def __setupDicomMappingUI(self):
        pass


    def __setupDataMappingUI(self):
        """
        """
        # exportGrid = QtGui.QGridLayout()
        # exportGrid.setSpacing(10)

        # self.layoutExport.addLayout(exportGrid)

        # # Study metadata file .xml
        # lblMetaDataFilename = QtGui.QLabel("Study metadata file (*.xml): ")
        # self.txtMetaDataFilename = QtGui.QLineEdit()
        # self.btnLocateMetaDataFilename = QtGui.QPushButton()

        # # Study
        # lblStudyText = QtGui.QLabel("Study: ")
        # self.lblStudy = QtGui.QLabel()

        # # Study event to export
        # lblStudyEventText = QtGui.QLabel("Study event: ")
        # self.cmbStudyEvent = QtGui.QComboBox()

        # # Event for to export
        # lblFormText = QtGui.QLabel("CRF Form: ")
        # self.cmbEventForm = QtGui.QComboBox()

        # # Study data file, could be .csv or .odm or zipped .odm files
        # lblDataFilename = QtGui.QLabel("Study data file (*.csv): ")
        # self.txtDataFilename = QtGui.QLineEdit()
        # self.btnLocateDataFilename = QtGui.QPushButton()

        # # Load mapping
        # self.btnLoadMapping = QtGui.QPushButton()
        # exportGrid.addWidget(self.btnLoadMapping, 1, 10, 5, 1)
        # self.btnLoadMapping.setMinimumHeight(160)

        # # Add to connection layout
        # exportGrid.addWidget(lblMetaDataFilename, 1, 0)
        # exportGrid.addWidget(self.txtMetaDataFilename, 1, 1, 1, 8)
        # exportGrid.addWidget(self.btnLocateMetaDataFilename, 1, 9)

        # exportGrid.addWidget(lblStudyText, 2, 0)
        # exportGrid.addWidget(self.lblStudy, 2, 1, 1, 8)

        # exportGrid.addWidget(lblStudyEventText, 3, 0)
        # exportGrid.addWidget(self.cmbStudyEvent, 3, 1, 1, 8)

        # exportGrid.addWidget(lblFormText, 4, 0)
        # exportGrid.addWidget(self.cmbEventForm, 4, 1, 1, 8)

        # exportGrid.addWidget(lblDataFilename, 5, 0)
        # exportGrid.addWidget(self.txtDataFilename, 5, 1, 1, 8)
        # exportGrid.addWidget(self.btnLocateDataFilename, 5, 9)

        # Table View
        self.tvExportDataMapping = QtGui.QTableView()
        self.layoutExport.addWidget(self.tvExportDataMapping)

        # Behaviour for the table views - select single row
        self.tvExportDataMapping.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tvExportDataMapping.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

        # Validate mapping buton
        self.btnValidateMapping = QtGui.QPushButton()
        self.layoutExport.addWidget(self.btnValidateMapping)


    def __setupPushResponseUI(self):
        pass


    def __setupWizzardButtonsUI(self):
        """
        """
        buttonGrid = QtGui.QGridLayout()

        self.btnNext = QtGui.QPushButton()
        self.btnNext.setText("Next step")
        self.btnNext.setToolTip("next step")
        self.btnNext.clicked.connect(self.btnNextClicked)

        self.btnPrevious = QtGui.QPushButton()
        self.btnPrevious.setText("Previous step")
        self.btnPrevious.setToolTip("previous step")
        self.btnPrevious.setEnabled(False)
        self.btnPrevious.clicked.connect(self.btnPreviousClicked)

        self.btnFinish = QtGui.QPushButton()
        self.btnFinish.setText("Finish")
        self.btnFinish.setToolTip("finish")
        self.btnFinish.setVisible(False)

        buttonGrid.addWidget(self.btnPrevious, 0, 0)
        buttonGrid.addWidget(self.btnNext, 0, 1)
        buttonGrid.addWidget(self.btnFinish, 0, 1)

        return buttonGrid

    #-------------------------------------------------------------------
    #-------------------- Module Event Handlers ------------------------

    def moduleTabChanged(self, selectedIndex):
        """According to selected index of tab setup the toolbar buttons
        """
        self.setupToolBarButtons(selectedIndex)
        self.setupWizzardButtons(selectedIndex)
        self.loadModuleData(selectedIndex)


    def btnNextClicked(self):
        """
        """
        currentIndex = self.tabExportModule.currentIndex()

        for i in range (0, self.tabExportModule.count()):
            self.tabExportModule.setTabEnabled(i, False)

        self.tabExportModule.setTabEnabled(currentIndex + 1, True)
        self.tabExportModule.setCurrentIndex(currentIndex + 1)


    def btnPreviousClicked(self):
        currentIndex = self.tabExportModule.currentIndex()

        for i in range (0, self.tabExportModule.count()):
            self.tabExportModule.setTabEnabled(i, False)

        self.tabExportModule.setTabEnabled(currentIndex - 1, True)
        self.tabExportModule.setCurrentIndex(currentIndex - 1)

    #-------------------------------------------------------------------
    #------------------------ Button Commands --------------------------

    def setupToolBarButtons(self, selectedTabIndex):
        """
        """
        # Data pull reqests
        if selectedTabIndex == 0:
            self.btnReload.setVisible(True)
            self.btnNew.setVisible(False)
            self.btnDetails.setVisible(False)
            self.btnSave.setVisible(False)
            self.btnDelete.setVisible(False)
            self.btnMapExportField.setVisible(False)
        # Study data
        elif selectedTabIndex == 1:
            self.btnReload.setVisible(True)
            self.btnNew.setVisible(False)
            self.btnDetails.setVisible(False)
            self.btnSave.setVisible(False)
            self.btnDelete.setVisible(False)
            self.btnMapExportField.setVisible(False)
        # Subjects
        elif selectedTabIndex == 2:
            self.btnReload.setVisible(True)
            self.btnNew.setVisible(False)
            self.btnDetails.setVisible(False)
            self.btnSave.setVisible(False)
            self.btnDelete.setVisible(False)
            self.btnMapExportField.setVisible(False)
        # DICOM structure mapping
        elif selectedTabIndex == 3:
            pass
        # Data export mapping
        elif selectedTabIndex == 4:
            self.btnReload.setVisible(True)
            self.btnNew.setVisible(True)
            self.btnDetails.setVisible(False)
            self.btnSave.setVisible(False)
            self.btnDelete.setVisible(False)
            self.btnMapExportField.setVisible(True)
        # Puss response
        elif selectedTabIndex == 5:
            pass
        else:
            self.btnReload.setVisible(False)
            self.btnNew.setVisible(False)
            self.btnDetails.setVisible(False)
            self.btnSave.setVisible(False)
            self.btnDelete.setVisible(False)
            self.btnMapExportField.setVisible(False)


    def setupWizzardButtons(self, selectedTabIndex):
        """When first tab, disable previous
        When last tab, make next text finish
        """
        # First tab
        if selectedTabIndex == 0:
            self.btnFinish.setVisible(False)
            self.btnPrevious.setEnabled(False)
        # Last tab
        elif selectedTabIndex == 5:
            self.btnFinish.setVisible(True)
            self.btnPrevious.setEnabled(True)
        else:
            self.btnFinish.setVisible(False)
            self.btnPrevious.setEnabled(True)

    #-------------------------------------------------------------------
    #-------------------- Internationalisation -------------------------

    def retranslateUi(self, Module):
        """
        """
        # Export toolbar buttons
        self.btnMapExportField.setText(QtGui.QApplication.translate("ExportModule", "map field", None, QtGui.QApplication.UnicodeUTF8))

        self.btnLocateDataFilename.setText(QtGui.QApplication.translate("ExportModule", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.btnLocateMetaDataFilename.setText(QtGui.QApplication.translate("ExportModule", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.btnValidateMapping.setText(QtGui.QApplication.translate("ExportModule", "Validate mapping", None, QtGui.QApplication.UnicodeUTF8))
        self.btnLoadMapping.setText(QtGui.QApplication.translate("ExportModule", "Load", None, QtGui.QApplication.UnicodeUTF8))
