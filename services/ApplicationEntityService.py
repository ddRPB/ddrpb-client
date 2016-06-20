#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# Standard
import os

# PyQt
from PyQt4 import QtCore

# DICOM
from netdicom.applicationentity import AE
from netdicom.SOPclass import *
from dicom.dataset import Dataset, FileDataset

# Singleton
from utils.SingletonType import SingletonType

# Logging
import logging
import logging.config

 ######  ######## ########  ##     ## ####  ######  ########
##    ## ##       ##     ## ##     ##  ##  ##    ## ##
##       ##       ##     ## ##     ##  ##  ##       ##
 ######  ######   ########  ##     ##  ##  ##       ######
      ## ##       ##   ##    ##   ##   ##  ##       ##
##    ## ##       ##    ##    ## ##    ##  ##    ## ##
 ######  ######## ##     ##    ###    ####  ######  ########


class ApplicationEntityService(object):
    """DICOM application entity service
    """

    __metaclass__ = SingletonType

    def __init__(self):
        """Default constructor
        """
        # Setup logger - use config file
        self._logger = logging.getLogger(__name__)
        logging.config.fileConfig('logging.ini', disable_existing_loggers=False)

        self._ae = None
        self._downloadDir = ""
        self._guiThread = None
        self._fileCounter = 0

    def __del__(self):
        """Default destructor
        """
        if self.isReady:
            self.quit()

########  ########   #######  ########  ######## ########  ######## #### ########  ######  
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##    ## 
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##       
########  ########  ##     ## ########  ######   ########     ##     ##  ######    ######  
##        ##   ##   ##     ## ##        ##       ##   ##      ##     ##  ##             ## 
##        ##    ##  ##     ## ##        ##       ##    ##     ##     ##  ##       ##    ## 
##        ##     ##  #######  ##        ######## ##     ##    ##    #### ########  ###### 

    @property   
    def ae(self):
        """AE Getter
        """
        return self._ae

    @property
    def isReady(self):
        """Is ready Getter
        """
        return self._ae is not None

    @property
    def downloadDir(self):
        """Download directory Getter
        """
        return self._downloadDir

    @downloadDir.setter
    def downloadDir(self, value):
        """Download directory Setter
        """
        self._downloadDir = value

##     ## ######## ######## ##     ##  #######  ########   ######
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ##
#### #### ##          ##    ##     ## ##     ## ##     ## ##
## ### ## ######      ##    ######### ##     ## ##     ##  ######
##     ## ##          ##    ##     ## ##     ## ##     ##       ##
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ##
##     ## ########    ##    ##     ##  #######  ########   ######

    def init(self, name, port):
        """Initialize and start AE
        """
        # setup AE
        self._ae = AE(name, port, [PatientRootFindSOPClass,
                                   StudyRootFindSOPClass,
                                   PatientRootMoveSOPClass,
                                   StudyRootMoveSOPClass,
                                   VerificationSOPClass], [StorageSOPClass,
                                                           VerificationSOPClass])

        self._ae.OnAssociateRequest = self.onAssociateRequest
        self._ae.OnAssociateResponse = self.onAssociateResponse
        self._ae.OnReceiveStore = self.onReceiveStore
        self._ae.OnReceiveEcho = self.onReceiveEcho

        self._ae.start()

        self._logger.info("AE created: " + name + ":" + str(port))

    def quit(self):
        """Quite AE
        """
        self._ae.Quit()

    def requestAssociation(self, remoteAe):
        """Create association with remote AE
        """
        self._logger.debug("Request association")
        
        return self._ae.RequestAssociation(remoteAe)

    def echo(self, association):
        """Perform a DICOM echo
        """
        status = association.VerificationSOPClass.SCU(1)
        self._logger.debug("Echo done with status: " + str(status))
        return status

    def find(self, data, thread=None):
        """Perform DICOM find
        """
        association = data[0]
        queryLvl = data[1] 

        arguments = len(data)

        patientNameFilter = ""
        patientIdFilter = "*" 
        studyUidFilter = "*"
        seriesUidFilter = "*"

        d = Dataset()

        if (arguments >= 3):
            patientNameFilter = data[2]
        if (arguments >= 4):
            patientIdFilter = data[3]
            d.ModalitiesInStudy = ""
        if (arguments >= 5):
            studyUidFilter = data[4]
        if (arguments >= 6):
            seriesUidFilter = data[5]

        d.QueryRetrieveLevel = queryLvl
        d.PatientsName = patientNameFilter
        d.PatientID = patientIdFilter
        d.PatientSex = ""
        d.PatientBirthDate = ""

        d.StudyInstanceUID = studyUidFilter
        d.AccessionNumber = ""
        d.StudyDescription = ""
        d.StudyDate = ""
        
        d.SeriesInstanceUID = seriesUidFilter
        d.SeriesDate = ""
        d.SeriesTime = ""
        d.SeriesDescription = ""
        d.Modality = ""

        status = association.PatientRootFindSOPClass.SCU(d, 1)
        
        self._logger.debug("Find done with status: " + str(status))

        if thread:
            thread.emit(QtCore.SIGNAL("finished(QVariant)"), status)
            return None
        else:    
            return status

    def findPatient(self, data, thread=None):
        """Perform DICOM patient find
        """
        association = data[0]
        queryLvl = data[1]

        d = Dataset()
        d.QueryRetrieveLevel = queryLvl

        status = association.PatientRootFindSOPClass.SCU(d, 1)
        
        self._logger.debug("Find DICOM patinet done with status: " + str(status))

        if thread:
            thread.emit(QtCore.SIGNAL("finished(QVariant)"), status)
            return None
        else:    
            return status

    def findStudy(self, data, thread=None):
        """Perform DICOM study find
        """
        association = data[0]
        queryLvl = data[1]

        d = Dataset()
        d.QueryRetrieveLevel = queryLvl

        status = association.StudyRootFindSOPClass.SCU(d, 1)
        
        self._logger.debug("Find DICOM study done with status: " + str(status))

        if thread:
            thread.emit(QtCore.SIGNAL("finished(QVariant)"), status)
            return None
        else:    
            return status

    def queryRetrieveTree(self, data, thread=None):
        """
        """
        rootNode = data[0] # rootNode
        remoteAe = data[1] # remoteAe

        self._guiThread = thread
        self._fileCounter = 0

        count = len(rootNode.children)
        downloaded = 0

        thread.emit(QtCore.SIGNAL("log(QString)"), "Retrieving DICOM data can take some time please wait...")

        for patient in rootNode.children:
            if patient.isChecked:
                thread.emit(QtCore.SIGNAL("log(QString)"), "Processing DICOM patient: " + patient.name + " (" + patient.id + ")")
                self.queryRetrievePatient(patient.id, patient.name, remoteAe, thread)
            else:
                for study in patient.children:
                    if study.isChecked:
                        thread.emit(QtCore.SIGNAL("log(QString)"), "Processing DICOM study: " + study.suid)
                        self.queryRetrieveStudy()
                    else:
                        for series in study.children:
                            if series.isChecked:
                                thread.emit(QtCore.SIGNAL("log(QString)"), "Processing DICOM study: " + series.suid)
                                self.queryRetrieveSeries()

            downloaded = downloaded + 1
            thread.emit(QtCore.SIGNAL("taskUpdated"), [downloaded, count])

        thread.emit(QtCore.SIGNAL('log(QString)'), 'Finished!')
        thread.emit(QtCore.SIGNAL('message(QString)'),"Retrieve job was successful.")

    def queryRetrievePatient(self, patientId, patientName, remoteAe, thread=None):
        """
        """
        queryLvl = "PATIENT"
        association = self._ae.RequestAssociation(remoteAe)
        result = self.find([association, queryLvl, patientName, patientId])

        for entity in result:
            if not entity[1]: continue

            d = Dataset()
            try:
                d.PatientID = entity[1].PatientID
            except Exception, err:
                self._logger.error(str(err))
                continue

            subAssociation = self._ae.RequestAssociation(remoteAe)
            generator = subAssociation.PatientRootMoveSOPClass.SCU(
                d, 
                self._ae.name, 
                1
            )

            for subentity in generator:
                self._logger.info(subentity)

            subAssociation.Release(0)

        association.Release(0)

    def queryRetrieveStudy(self, studyUid, remoteAe, thread=None):
        """
        """
        queryLvl = "STUDY"
        association = self._ae.RequestAssociation(remoteAe)
        result = self.find([association, queryLvl, patientName, patientId])

        for entity in result:
            if not entity[1]: continue

            d = Dataset()
            association = self._ae.RequestAssociation(remoteAe)

            gen = association.StudyRootMoveSOPClass.SCU(
                d, 
                self._ae.name, 
                1
            )

            for gg in gen:
                self._logger.info(gg)

            association.Release(0)

    def queryRetrieveSeries(self, seriesUid, remoteAe, thread=None):
        """
        """
        queryLvl = "SERIES"
        association = self._ae.RequestAssociation(remoteAe)
        result = self.find([association, queryLvl, patientName, patientId])

        for entity in result:
            if not entity[1]: continue

            d = Dataset()
            association = self._ae.RequestAssociation(remoteAe)

            generator = association.SeriesRootMoveSOPClass.SCU(
                d, 
                self._ae.name, 
                1
            )

            for entity in generator:
                self._logger.info(entity)

            association.Release(0)

########  ########  #### ##     ##    ###    ######## ########
##     ## ##     ##  ##  ##     ##   ## ##      ##    ##
##     ## ##     ##  ##  ##     ##  ##   ##     ##    ##
########  ########   ##  ##     ## ##     ##    ##    ######
##        ##   ##    ##   ##   ##  #########    ##    ##
##        ##    ##   ##    ## ##   ##     ##    ##    ##
##        ##     ## ####    ###    ##     ##    ##    ########

    def onAssociateRequest(self, association):
        """
        """
        self._logger.debug("Association requested")
        self._logger.debug(association)

    def onAssociateResponse(self, association):
        """
        """
        self._logger.debug("Association response received")

    def onReceiveEcho(self):
        """
        """
        self._logger.debug("Echo received")
        
        return True
 
    def onReceiveStore(self, sopClass, receivedDs):
        """
        """
        self._logger.debug("Received C-STORE: " + receivedDs.PatientName)

        try:
            # DICOM header (metadata)
            file_meta = Dataset()
            file_meta.MediaStorageSOPClassUID = receivedDs.SOPClassUID
            file_meta.MediaStorageSOPInstanceUID = receivedDs.SOPInstanceUID
            # TransferSyntaxUID

            # pydicom root UID + 1
            file_meta.ImplementationClassUID = "1.2.826.0.1.3680043.8.498.1"

            path = self.downloadDir + os.sep + receivedDs.PatientID

            # Patient ID is the root folder
            if os.path.isdir(path) == False:
                os.mkdir(path)

            path = path + os.sep + receivedDs.StudyInstanceUID

            # DICOM study separated to subfolder under patient
            if os.path.isdir(path) == False:
                os.mkdir(path)

            filename = path + os.sep + receivedDs.Modality + "."  + receivedDs.SOPInstanceUID + ".dcm"

            # Create a DICOM file
            ds = FileDataset(filename, {}, file_meta=file_meta, preamble="\0" * 128)
            ds.update(receivedDs)
            ds.save_as(filename)

            self._fileCounter = self._fileCounter + 1
            
            self._logger.debug("File written to: " +  filename)
            
            if self._guiThread:
                self._guiThread.emit(QtCore.SIGNAL("log(QString)"), "File written to: " +  filename)
                self._guiThread.emit(QtCore.SIGNAL("taskUpdated"), self._fileCounter)

        except Exception, err:
            self._logger.error(str(err))

        # Have to return appropriate status
        return sopClass.Success
