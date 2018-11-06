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

# Datetime
from datetime import datetime

# PyQt
from PyQt4 import QtGui, QtCore

# GUI
from gui.DicomStudyDialogUI import DicomStudyDialogUI

# ViewModels
from viewModels.DicomStudySeriesTableModel import DicomStudySeriesTableModel

# Context
from contexts.ConfigDetails import ConfigDetails

# DICOM de-identification
from dicomdeident.DeidentConfig import DeidentConfig

# Utils
from utils import first

########  ####    ###    ##        #######   ######
##     ##  ##    ## ##   ##       ##     ## ##    ##
##     ##  ##   ##   ##  ##       ##     ## ##
##     ##  ##  ##     ## ##       ##     ## ##   ####
##     ##  ##  ######### ##       ##     ## ##    ##
##     ##  ##  ##     ## ##       ##     ## ##    ##
########  #### ##     ## ########  #######   ######


class DicomStudyDialog(QtGui.QDialog, DicomStudyDialogUI):
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
        self._logger = logging.getLogger(__name__)
        logging.config.fileConfig('logging.ini', disable_existing_loggers=False)


        self._patient = None
        self._study = None
        self._studySeries = []

        self._selectedSeries = None
        self._seriesProxyModel = None

        self._reportMaxLength = 3999
        self._reportLength = 0
        self.lblFreeLength.setText(str(self._reportLength) + "/" + str(self._reportMaxLength))

        # Configuration of de-identification
        self._deidentConfig = DeidentConfig()

        # Handlers
        self.connect(
            self.txtNewStudyDescription,
            QtCore.SIGNAL("textChanged(QString)"),
            self.newStudyDescriptionChanged
        )
        self.teReport.textChanged.connect(self.teReportChanged)

        self.copyStudyDescButton.clicked.connect(self.copyStudyDescButtonClicked)
        self.btnCopySeriesDesc.clicked.connect(self.btnCopySeriesDescClicked)

        self.btnApprove.clicked.connect(self.btnApproveClicked)
        self.btnOk.clicked.connect(self.btnOkClicked)

########  ########   #######  ########  ######## ########  ######## #### ########  ######
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##    ##
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##
########  ########  ##     ## ########  ######   ########     ##     ##  ######    ######
##        ##   ##   ##     ## ##        ##       ##   ##      ##     ##  ##             ##
##        ##    ##  ##     ## ##        ##       ##    ##     ##     ##  ##       ##    ##
##        ##     ##  #######  ##        ######## ##     ##    ##    #### ########  ######

    @property
    def descsProvided(self):
        """New descriptions provided Getter
        """
        studyDescProvided = True
        if self._study.description != "" and self._study.newDescription == "":
            studyDescProvided = False

        seriesDescProvided = True
        for s in self._studySeries:
            if s.description != "" and s.newDescription == "":
                seriesDescProvided = False
                break

        return studyDescProvided and seriesDescProvided

    @property
    def studySeries(self):
        """Study series Getter
        """
        return self._studySeries

    @studySeries.setter
    def studySeries(self, value):
        """Study series Setter
        """
        self._studySeries = value

##     ## ######## ######## ##     ##  #######  ########   ######
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ##
#### #### ##          ##    ##     ## ##     ## ##     ## ##
## ### ## ######      ##    ######### ##     ## ##     ##  ######
##     ## ##          ##    ##     ## ##     ## ##     ##       ##
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ##
##     ## ########    ##    ##     ##  #######  ########   ######

    def setModel(self, patient, dicomDataRoot, studyType):
        """Prepare view models for this dialog
        """
        self._patient = patient

        if dicomDataRoot is not None:

            # Take the main selected study from dataRoot
            for study in dicomDataRoot.children:
                if study.isChecked:
                    self._study = study
                    break

            # Consider all selected series from dataRoot
            for study in dicomDataRoot.children:
                for serie in study.children:
                    if serie.isChecked:
                        self._studySeries.append(serie)

        # View model for DICOM patient
        self.txtPatientId.setText(self._patient.id)
        self.txtNewPatientId.setText(self._patient.newId)
        self.txtPatientName.setText(self._patient.name)
        self.txtNewPatientName.setText(self._patient.newName)
        self.txtPatientGender.setText(self._patient.gender)
        self.txtNewPatientGender.setText(self._patient.newGender)
        self.txtPatientDOB.setText(self._patient.dob)
        self.txtNewPatientDOB.setText(self._patient.newDob)

        # View model for DICOM study
        self.txtStudyDate.setText(self._study.date)
        if ConfigDetails().retainLongFullDatesOption:
            self.txtNewStudyDate.setText(self._study.date)
        else:
            self.txtNewStudyDate.setText(ConfigDetails().replaceDateWith)

        self.txtStudyType.setText(studyType)

        self.txtStudyDescription.setText(self._study.description)
        if self._study.description == "":
            self.txtNewStudyDescription.setReadOnly(True)

        # View model for DICOM study series
        seriesModel = DicomStudySeriesTableModel(self._studySeries)

        self._seriesProxyModel = QtGui.QSortFilterProxyModel()
        self._seriesProxyModel.setSourceModel(seriesModel)
        self._seriesProxyModel.setDynamicSortFilter(True)
        self._seriesProxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        # Filtering
        QtCore.QObject.connect(
            self.txtSeriesFilter,
            QtCore.SIGNAL("textChanged(QString)"),
            self._seriesProxyModel.setFilterRegExp
        )

        # Assign to TableView
        self.tvSeries.setModel(self._seriesProxyModel)
        self.tvSeries.resizeColumnsToContents()

        # Selection changed
        self.tvSeries.selectionModel().currentChanged.connect(self.tblSeriesItemChanged)

        # Automatically copy descriptions: save user some clicks
        if ConfigDetails().retainStudySeriesDescriptions:
            self.copyStudyDescButtonClicked()
            self.btnCopySeriesDescClicked()

    def passSanityCheck(self, rpbStudySubject):
        """Check whether the main subject characteristics of DICOM data is matching chosen RPB subject
        """
        genderPass = False
        dobPass = False

        if rpbStudySubject.subject is not None and self._patient is not None:

            # Gender match is enabled and RPB subject has gender and DICOM patient has gender
            if ConfigDetails().patientGenderMatch and \
               rpbStudySubject.subject.gender is not None and rpbStudySubject.subject.gender != "" and \
               self._patient.gender is not None and self._patient.gender != "" and self._patient.gender != "O":

                    # Gender is the same
                    if rpbStudySubject.subject.gender.lower() == self._patient.gender.lower():
                        genderPass = True
                        self._logger.info("Gender sanity check passed.")
                    else:
                        self._logger.error("RPB subject gender: " + rpbStudySubject.subject.gender.lower())
                        self._logger.error("DICOM patient gender: " + self._patient.gender.lower())

            # Gender is not provided so pass the test
            else:
                genderPass = True
                self._logger.info("Gender sanity check was skipped.")

            # DOB match is enabled and full date of birth collected and RPB subject has DOB and DICOM patient has DOB
            if ConfigDetails().patientDobMatch and\
               rpbStudySubject.subject.dateOfBirth is not None and rpbStudySubject.subject.dateOfBirth != "" and\
               self._patient.dob is not None and self._patient.dob != "":
                    
                    # Convert from strings dates
                    format = "%Y%m%d"
                    dicomdob = datetime.strptime(self._patient.dob, format)
                    deidentdob = datetime.strptime(self._deidentConfig.ReplaceDateWith, format)
                    format = "%Y-%m-%d"
                    edcdob = datetime.strptime(rpbStudySubject.subject.dateOfBirth, format)

                    # DOB is the same
                    if edcdob == dicomdob:
                        dobPass = True
                        self._logger.info("Full DOB sanity check passed.")
                    # DICOM DOB was de-identified before
                    elif dicomdob == deidentdob:
                        dobPass = True
                        self._logger.info("DOB sanity chack was skipped, because provided DICOM DOB is already de-identifed.")
                    else:
                        self._logger.error("RPB subject date of birth: " + str(edcdob))
                        self._logger.error("DICOM patient date of birth: " + str(dicomdob))
            
            # DOB match is enabled and only year of birth collected and RPB subject has year of birth and DICOM patient has DOB
            elif ConfigDetails().patientDobMatch and\
                 rpbStudySubject.subject.yearOfBirth is not None and rpbStudySubject.subject.yearOfBirth != "" and\
                 self._patient.dob is not None and self._patient.dob != "":
                    
                    # Year of birth is the same
                    if rpbStudySubject.subject.yearOfBirth == self._patient[:4]:
                        dobPass = True
                        self._logger.info("Year of birth sanity check passed.")
                    else:
                       self._logger.error("RPB subject year of birth: " + rpbStudySubject.subject.yearOfBirth)
                       self._logger.error("DICOM patient year of birth: " + self._patient[:4])
            
            # DOB is not provided so pass the test
            else:
                dobPass = True
                self._logger.info("DOB sanity check was skipped.")

        return genderPass and dobPass

##     ##    ###    ##    ## ########  ##       ######## ########   ######
##     ##   ## ##   ###   ## ##     ## ##       ##       ##     ## ##    ##
##     ##  ##   ##  ####  ## ##     ## ##       ##       ##     ## ##
######### ##     ## ## ## ## ##     ## ##       ######   ########   ######
##     ## ######### ##  #### ##     ## ##       ##       ##   ##         ##
##     ## ##     ## ##   ### ##     ## ##       ##       ##    ##  ##    ##
##     ## ##     ## ##    ## ########  ######## ######## ##     ##  ######

    def tblSeriesItemChanged(self, current, previous):
        """On selected DICOM series changed
        """
        self.teReport.clear()

        # Take the 4th column (UID) of selected row from table view
        index = self._seriesProxyModel.index(current.row(), 3)
        if index.data().toPyObject(): 
            self._selectedSeries = first.first(
                serie for serie in self._studySeries if str(serie.suid) == index.data().toPyObject()
            )

            if self._selectedSeries.modality == "SR":
                self.tabWidget.setTabEnabled(1, True)
                self.teReport.setEnabled(True)
                self.btnApprove.setEnabled(True)

                if self._selectedSeries.isApproved:
                    self.teReport.clear()
                    self.teReport.insertPlainText(self._selectedSeries.approvedReportText)
                    self.teReport.setStyleSheet(self.greenStyle)
                else:
                    self.teReport.setStyleSheet(self.redStyle)
                    for doc in self._selectedSeries.dsrDocuments:
                        self.teReport.insertPlainText(doc.renderText())
            else:
                self.tabWidget.setTabEnabled(1, False)
                self.teReport.setEnabled(False)
                self.btnApprove.setEnabled(False)

    def newStudyDescriptionChanged(self, value):
        """Changing a combobox activates this method, changing the mapping of the corresponding entry in self.dict_ROIName
        """
        self._study.newDescription = value

    def copyStudyDescButtonClicked(self):
        """Copy the original DICOM study description to new
        """
        self.txtNewStudyDescription.setText(self.txtStudyDescription.text())

    def btnCopySeriesDescClicked(self):
        """Copy the original DICOM study description to new
        """
        for serie in self._studySeries:
            serie.newDescription = serie.description

        # View model for DICOM study series
        seriesModel = DicomStudySeriesTableModel(self._studySeries)

        self._seriesProxyModel = QtGui.QSortFilterProxyModel()
        self._seriesProxyModel.setSourceModel(seriesModel)
        self._seriesProxyModel.setDynamicSortFilter(True)
        self._seriesProxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        # Assign to TableView
        self.tvSeries.setModel(self._seriesProxyModel)
        self.tvSeries.resizeColumnsToContents()

        self.tvSeries.selectionModel().currentChanged.connect(self.tblSeriesItemChanged)

    def btnApproveClicked(self):
        """Approve the text in within SR serie
        """
        # Green color for approved text
        self.teReport.setStyleSheet(self.greenStyle)

        # Store the approved text of reports
        self._selectedSeries.approvedReportText = unicode(self.teReport.toPlainText().toUtf8(), "utf-8")
        self._selectedSeries.isApproved = True

    def teReportChanged(self):
        """On change (editing) in text editor of SR text
        """
        self.teReport.setStyleSheet(self.redStyle)

        self._reportLength = self.teReport.toPlainText().length()
        self.lblFreeLength.setText(str(self._reportLength) + "/" + str(self._reportMaxLength))

        if self.teReport.toPlainText().length() > self._reportMaxLength:
            # Cut the text to max number of characters
            text = self.teReport.toPlainText()
            text.chop(text.length() - self._reportMaxLength)
            self.teReport.setPlainText(text)
            # Move the cursor to the end
            cursor = self.teReport.textCursor()
            cursor.setPosition(self.teReport.document().characterCount() - 1)
            self.teReport.setTextCursor(cursor)

    def btnOkClicked(self):
        """Ask user one more time if the information is correct.
        """
        if self.descsProvided:
            question = "Are you sure that you provided proper\nstudy/series descriptions and removed\npatient identity data from them?\n\nThe DICOM files will be pseudonymised\n but study/series descriptions will be retained!"
            response = QtGui.QMessageBox.question(
                self,
                "Question",
                question,
                QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Yes).__or__(QtGui.QMessageBox.No), QtGui.QMessageBox.No
            )
        else:
            question = "Original DICOM study/series descriptions will be deleted\nduring pseudonymisation and you did not provided the\nalternative descriptions!\n\nAny research important data you have in descriptions\nwill be lost!\n\nDo you want to continue?"
            response = QtGui.QMessageBox.question(
                self,
                "Question",
                question,
                QtGui.QMessageBox.StandardButtons(QtGui.QMessageBox.Yes).__or__(QtGui.QMessageBox.No), QtGui.QMessageBox.No
            )

        if response == QtGui.QMessageBox.Yes:
            self.accept()
        elif QtGui.QMessageBox.No:
            QtGui.QMessageBox.information(self, "Information", "Provide data in order to upload the DICOM files.")
