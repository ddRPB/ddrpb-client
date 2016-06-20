#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# Standard
import os

# DICOM
import dicom

# Pickle
import cPickle as pickle

# Services
from services.CryptoService import CryptoService

 ######  ######## ########  ##     ## ####  ######  ########
##    ## ##       ##     ## ##     ##  ##  ##    ## ##
##       ##       ##     ## ##     ##  ##  ##       ##
 ######  ######   ########  ##     ##  ##  ##       ######
      ## ##       ##   ##    ##   ##   ##  ##       ##
##    ## ##       ##    ##    ## ##    ##  ##    ## ##
 ######  ######## ##     ##    ###    ####  ######  ########


class DeanonymisationService():
    """DICOM deanonymisation service class

    This service performs the deanonymisation/depseudonymisation of DICOM data
    depending on specified configuration.

    The service is developed in conformance with DICOM supplement 142 (Clinical Trial De-identification Profiles)
    """

    def __init__(self, directory):
        """Default constructor
        """
        self.__svcCrypto = CryptoService()
        self.__directory = directory

########  ########   #######  ########  ######## ########  ######## #### ########  ######
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##    ##
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##
########  ########  ##     ## ########  ######   ########     ##     ##  ######    ######
##        ##   ##   ##     ## ##        ##       ##   ##      ##     ##  ##             ##
##        ##    ##  ##     ## ##        ##       ##    ##     ##     ##  ##       ##    ##
##        ##     ##  #######  ##        ######## ##     ##    ##    #### ########  ######

    @property
    def directory(self):
        """DICOM directory to deanonymise Getter
        """
        return self.__directory

    @directory.setter
    def directory(self, value):
        """DICOM directory to deanonymise Setter
        """
        if self.__directory != value:
            self.__directory = value

##     ## ######## ######## ##     ##  #######  ########   ######
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ##
#### #### ##          ##    ##     ## ##     ## ##     ## ##
## ### ## ######      ##    ######### ##     ## ##     ##  ######
##     ## ##          ##    ##     ## ##     ## ##     ##       ##
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ##
##     ## ########    ##    ##     ##  #######  ########   ######

    def makeDeanonymous(self):
        """Deanonymise the data
        """
        # Directory readable?
        accessOK = os.access(self.__directory,  os.R_OK)
        if accessOK == False:
            print "Could not read directory ",  self.__directory, " check existence and reading rights"
            sys.exit()

        for f in os.listdir(self.__directory):
            # Read
            dcmFile = dicom.read_file(self.__directory + os.sep + f)

            # Deanonymise
            print "Decryption and reverting original DICOM identity data"
            self.__reverseIdentity(dcmFile)

            # Special case for SOP instance UID to put into Referenced
            if dcmFile.file_meta.MediaStorageSOPClassUID == 'RT Plan Storage':
                dcmFile.ReferencedStructureSets[0].ReferencedSOPInstanceUID = self.__sopInstanceUid

            # Save
            dcmFile.save_as(self.__directory + os.sep + f)

########  ########  #### ##     ##    ###    ######## ########
##     ## ##     ##  ##  ##     ##   ## ##      ##    ##
##     ## ##     ##  ##  ##     ##  ##   ##     ##    ##
########  ########   ##  ##     ## ##     ##    ##    ######
##        ##   ##    ##   ##   ##  #########    ##    ##
##        ##    ##   ##    ## ##   ##     ##    ##    ##
##        ##     ## ####    ###    ##     ##    ##    ########

    def __reverseIdentity(self, dcmFile):
        """Reverse the dcmFile identity
        """
        # Check if the attribute Patient Identity Removed (0012,0062) is YES
        t = dicom.tag.Tag((0x12, 0x62))
        if "PatientIdentityRemoved" in dcmFile and dcmFile[t].value == "YES":
            # Get the attribute Encrypted Attributes Sequence (0400,0500)
            t = dicom.tag.Tag((0x400, 0x500))
            encryptedAttributesSequence = dcmFile[t]

            # Get the atribute Encrypted Content (0400,0520) from sequence
            encryptedContent = encryptedAttributesSequence[0].EncryptedContent

            # Get decripted dicom dataset
            decryptedData = self.__svcCrypto.decrypt(encryptedContent)

            # Deserialize these original DICOM data from string
            encryptedAttributesDs = pickle.loads(decryptedData)

            # Get the attribute De-identification method code sequence (0012,0064)
            # to know codes of profiles and options used for deanonymisation
            t = dicom.tag.Tag((0x0012, 0x0064))
            dcmFile[t]

            # Get the Modified Attributes Sequence (0400,0550) from
            # encryptedAttributesDs and set them to origin
            t = dicom.tag.Tag((0x400, 0x550))

            for encryptedAttributeDs in encryptedAttributesDs[t]:
                # Ignore SOAP Instance UID
                if "SOPInstanceUID" in encryptedAttributeDs:
                    # There is just one data element in dta set and I want to know the name
                    elementName =  encryptedAttributeDs.dir()[0]
                    element = encryptedAttributeDs.data_element(elementName)

                    print dcmFile[element.tag]

                    self.__sopInstanceUid = element.value

                    print self.__sopInstanceUid
                else:
                    # There is just one data element in dta set and I want to know the name
                    elementName =  encryptedAttributeDs.dir()[0]
                    element = encryptedAttributeDs.data_element(elementName)

                    print dcmFile[element.tag]

                    dcmFile[element.tag].value = element.value

                    print dcmFile[element.tag]


            # Remove the Modified Attributes Sequence (0400,0550)
            if "ModifiedAttributesSequence" in dcmFile:
                t = dicom.tag.Tag((0x400, 0x550))
                del dcmFile[t]

            # Set the attribute Patient Identity Removed (0012,0062) to NO
            if "PatientIdentityRemoved" in dcmFile:
                t = dicom.tag.Tag((0x12, 0x62))
                dcmFile[t] = dicom.dataelem.DataElement(t, "CS", "NO")

            # Remove the attribute De-identification Method (0012, 0063)
            if "De-identificationMethod" in dcmFile:
                t = dicom.tag.Tag(0x0012, 0x0063)
                del dcmFile[t]

            # Remove the attribute De-identification method code sequence (0012,0064)
            t = dicom.tag.Tag((0x0012, 0x0064))
            del dcmFile[t]
