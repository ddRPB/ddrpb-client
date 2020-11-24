#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# System
import sys

# Logging
import logging
import logging.config

# Domain
from domain.EventDefinitionCrf import EventDefinitionCrf
from domain.Item import Item
from domain.Study import Study
from domain.StudyEventDefinition import StudyEventDefinition
from domain.StudyParameterConfiguration import StudyParameterConfiguration

# Prefer C accelerated version of ElementTree for XML parsing
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

 ######  ######## ########  ##     ## ####  ######  ########
##    ## ##       ##     ## ##     ##  ##  ##    ## ##
##       ##       ##     ## ##     ##  ##  ##       ##
 ######  ######   ########  ##     ##  ##  ##       ######
      ## ##       ##   ##    ##   ##   ##  ##       ##
##    ## ##       ##    ##    ## ##    ##  ##    ## ##
 ######  ######## ##     ##    ###    ####  ######  ########

# Namespace maps for reading of XML
nsmaps = {
    'odm': 'http://www.cdisc.org/ns/odm/v1.3',
    'cdisc': 'http://www.cdisc.org/ns/odm/v1.3',
    'OpenClinica': 'http://www.openclinica.org/ns/odm_ext_v130/v3.1'
}
# ("xsl", "http://www.w3.org/1999/XSL/Transform")
# ("beans", "http://openclinica.org/ws/beans")
# ("studysubject", "http://openclinica.org/ws/studySubject/v1")
# ("OpenClinica", "http://www.openclinica.org/ns/odm_ext_v130/v3.1")

# TODO: theoretically I can use xslt to transform xml metadata into import xml
# TODO: I should check if the loaded XML data conform XML schema for ODM


class OdmFileDataService(object):
    """File data service dedicated to work with XML files according to ODM schema
    """
    def __init__(self, logger=None):
        """Constructor
        """
        # Logger
        self.logger = logger or logging.getLogger(__name__)

        # Init members
        self.filename = ""

        # Header columns are holding the names of data elements
        self.headers = []

##     ## ######## ######## ##     ##  #######  ########   ######
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ##
#### #### ##          ##    ##     ## ##     ## ##     ## ##
## ### ## ######      ##    ######### ##     ## ##     ##  ######
##     ## ##          ##    ##     ## ##     ## ##     ##       ##
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ##
##     ## ########    ##    ##     ##  #######  ########   ######

    def isFileLoaded(self):
        """Determine whether the filename is provided to the service
        """
        return self.filename != ""

    def setFilename(self, filename):
        """Setup data filename for the service
        """
        if self.filename != filename:
            self.filename = filename

    def getFilename(self):
        """Get the name of the data fila
        """
        return str(self.filename)

    def loadHeaders(self):
        """Load items headers from xml metadata
        """
        if self.isFileLoaded:
            documentTree = ET.ElementTree(file=self.filename)

            for element in documentTree.iterfind('.//odm:ItemDef', namespaces=nsmaps):
                self.headers.append(element.attrib['Comment'])

    def loadStudy(self):
        """Extract Study domain object according to ODM from metadata XML
        """
        study = None

        # Check if file path is setup
        if self.isFileLoaded:
            documentTree = ET.ElementTree(file=self.filename)

            # Locate Study data in XML file via XPath
            for element in documentTree.iterfind('.//odm:Study', namespaces=nsmaps):
                study = Study()
                study.setOid(element.attrib['OID'])

                for studyName in documentTree.iterfind('.//odm:Study[@OID="' + study.oid() + '"]/odm:GlobalVariables/odm:StudyName', namespaces=nsmaps):
                    study.setName(studyName.text)

                for studyDescription in documentTree.iterfind('.//odm:Study[@OID="' + study.oid() + '"]/odm:GlobalVariables/odm:StudyDescription', namespaces=nsmaps):
                    study.setDescription(studyDescription.text)

                # In case I need this information later
                # for studyProtocolName in documentTree.iterfind('.//odm:Study[@OID="' + study.oid() + '"]/odm:GlobalVariables/odm:ProtocolName', namespaces=nsmaps):
                #     print studyProtocolName.text

        # The resulting study element
        return study

    def loadStudyEvents(self):
        """Extract a list of Study Event domain objects according to ODM from metadata XML
        """
        studyEvents = []

        # Check if file path is setup
        if self.isFileLoaded:
            documentTree = ET.ElementTree(file=self.filename)

            # First obtain list of references (OIDs) to study events defined in ODM -> Study -> MetaDataVersion -> Protocol
            studyEventRefs = []

            for studyEventRef in documentTree.iterfind('.//odm:StudyEventRef', namespaces=nsmaps):
                studyEventRefs.append(studyEventRef.attrib['StudyEventOID'])

                # In case I need this information later
                # print studyEventRef.attrib['Mandatory']
                # print studyEventRef.attrib['OrderNumber']

            # Now for each study event reference find study event definition
            for eventRef in studyEventRefs:
                for element in documentTree.iterfind('.//odm:StudyEventDef[@OID="' + eventRef + '"]', namespaces=nsmaps):
                    studyEvent = StudyEventDefinition()

                    studyEvent.setOid(element.attrib['OID'])
                    studyEvent.setName(element.attrib['Name'])
                    studyEvent.setRepeating(element.attrib['Repeating'])
                    studyEvent.setType(element.attrib['Type'])

                    studyEvents.append(studyEvent)

        # Return resulting study event defintion elements
        return studyEvents

    def loadEventCrfs(self, studyEventDef):
        """Extract a list of EventDefinitionCrf domain objects according to ODM from metadata XML
        """
        eventCrfs = []

        # Check if file path is setup
        if self.isFileLoaded:
            documentTree = ET.ElementTree(file=self.filename)

            # First collect ForRef elements as a childrens of selected Study Event Definition
            formRefs = []

            for formRef in  documentTree.iterfind('.//odm:StudyEventDef[@OID="' + studyEventDef.oid() + '"]/odm:FormRef', namespaces=nsmaps):
                formRefs.append(formRef.attrib['FormOID'])

                # # If this information needed later
                # formRef.attrib['Mandatory']

            # Now search FormDefs according to FormRefs
            for formRef in formRefs:
                for form in documentTree.iterfind('.//odm:FormDef[@OID="' + formRef + '"]', namespaces=nsmaps):
                    eventCrf = EventDefinitionCrf()

                    eventCrf.setOid(form.attrib['OID'])
                    eventCrf.setName(form.attrib['Name'])
                    eventCrf.setRepeating(form.attrib['Repeating'])

                    eventCrfs.append(eventCrf)

        # Return resulting study event crf forms
        return eventCrfs

    def loadCrfItem(self, formOid, itemOid, metadata):
        """Load CRF item details from ODM metadata
        """
        item = None

        self.logger.info("CRF form OID: " + formOid)
        self.logger.info("CRF item OID: " + itemOid)

        # Check if file path is setup
        if metadata:
            documentTree = ET.ElementTree((ET.fromstring(str(metadata))))

            # Locate ItemDefs data in XML file via XPath
            for itemElement in documentTree.iterfind('.//odm:ItemDef[@OID="' + itemOid + '"]', namespaces=nsmaps):
                # Check FormOID, normally I would do it in XPath but python does not support contains wildcard
                if itemElement.attrib["{http://www.openclinica.org/ns/odm_ext_v130/v3.1}FormOIDs"].find(formOid) != -1:
                    item = Item()
                    item.oid = itemElement.attrib['OID']
                    item.name = itemElement.attrib['Name']
                    item.description = itemElement.attrib['Comment']
                    item.dataType = itemElement.attrib['DataType']

                    for itemDetails in itemElement:
                        if (str(itemDetails.tag)).strip() == "{http://www.openclinica.org/ns/odm_ext_v130/v3.1}ItemDetails":
                            for detailsElement in itemDetails:
                                if (str(detailsElement.tag)).strip() == "{http://www.openclinica.org/ns/odm_ext_v130/v3.1}ItemPresentInForm":
                                    for presentForm in detailsElement:
                                        if (str(presentForm.tag)).strip() == "{http://www.openclinica.org/ns/odm_ext_v130/v3.1}LeftItemText":
                                            item.label = presentForm.text

        # Return resulting CRT item
        return item

    def printData(self):
        """Print the content of file to the console
        """
        if self.isFileLoaded:
            documentTree = ET.ElementTree(file=self.filename)

            for element in documentTree.iter():
                print(element.tag, element.attrib)

    def generateOdmXmlForStudy(self, studyOid, subject, event, reportText, crfDicomPatientField, crfDicomStudyField, crfSRTextField=None):
        """
        Create the XML ODM structured data string for import
        :param studyOid: Study OID
        :param subject: subject
        :param event: event
        :param reportText: reportText
        :param crfDicomPatientField: crfDicomPatientField
        :param crfDicomStudyField: crfDicomStudyField
        :param crfSRTextField: crfDicomSRTextField
        :return: void
        """
        odm = ET.Element("ODM")

        # Study - Study OID
        clinicalData = ET.SubElement(odm, "ClinicalData")
        clinicalData.set("StudyOID", studyOid)
        clinicalData.set("MetaDataVersionOID", 'v1.0.0')

        # Subject - Study Subject ID
        subjectData = ET.SubElement(clinicalData, "SubjectData")
        subjectData.set("SubjectKey", subject.oid)

        # Event
        studyEventData = ET.SubElement(subjectData, "StudyEventData")
        studyEventData.set("StudyEventOID", event.eventDefinitionOID)
        studyEventData.set("StudyEventRepeatKey", event.studyEventRepeatKey)

        # CRF form
        formData = ET.SubElement(studyEventData, "FormData")
        formData.set("FormOID", crfDicomStudyField.formOid)

        # Item group - DICOM Patient ID
        patientItemGroupData = ET.SubElement(formData, "ItemGroupData")
        patientItemGroupData.set("ItemGroupOID", crfDicomPatientField.groupoid)
        patientItemGroupData.set("TransactionType", "Insert")

        # DICOM Patient ID - PID
        itemData = ET.SubElement(patientItemGroupData, "ItemData")
        itemData.set("ItemOID", crfDicomPatientField.crfitemoid)
        itemData.set("Value", subject.subject.uniqueIdentifier)

        if crfDicomStudyField.groupOid == crfDicomPatientField.groupoid:
            # DICOM Study UID
            itemData = ET.SubElement(patientItemGroupData, "ItemData")
            itemData.set("ItemOID", crfDicomStudyField.oid)
            itemData.set("Value", crfDicomStudyField.value)

            # DICOM SR text
            if crfSRTextField:
                if crfSRTextField.groupoid == crfDicomPatientField.groupoid:
                    itemData = ET.SubElement(patientItemGroupData, "ItemData")
                    itemData.set("ItemOID", crfSRTextField.crfitemoid)
                    itemData.set("Value", reportText)
        else:
            # Item group - DICOM Study UID
            dcmItemGroupData = ET.SubElement(formData, "ItemGroupData")
            dcmItemGroupData.set("ItemGroupOID", crfDicomStudyField.groupOid)
            dcmItemGroupData.set("TransactionType", "Insert")

            # DICOM Study UID
            itemData = ET.SubElement(dcmItemGroupData, "ItemData")
            itemData.set("ItemOID", crfDicomStudyField.oid)
            itemData.set("Value", crfDicomStudyField.value)

            # DICOM SR text
            if crfSRTextField:
                if crfSRTextField.groupoid == crfDicomStudyField.groupOid:
                    itemData = ET.SubElement(dcmItemGroupData, "ItemData")
                    itemData.set("ItemOID", crfSRTextField.crfitemoid)
                    itemData.set("Value", reportText)

        documentTree = ET.ElementTree(odm)

        if sys.version < "3":
            xmlString = ET.tostring(odm, encoding="UTF-8")
            xmlString = xmlString.replace("<?xml version='1.0' encoding='UTF-8'?>", "")
        else:
            xmlString = str(ET.tostring(odm))
            xmlString = xmlString.replace("<?xml version='1.0' encoding='UTF-8'?>", "")

        return xmlString

    def getItemOidFromMetadata(self, metadata, formOid, itemName):
        """Get item OID from metadata when form and itemName are known

        Param metadata study metadata
        Param formOid specify which form to search in metadata
        Param itemName specify which item to search
        Return string OID value of specified itemName from metadata or None
        """
        documentTree = ET.ElementTree((ET.fromstring(str(metadata))))

        itemOids = []

        # Locate ItemDefs data in XML file via XPath
        for item in documentTree.iterfind('.//odm:ItemDef[@OpenClinica:FormOIDs="' + formOid + '"]' + '[@Name="' + itemName + '"]', namespaces=nsmaps):
            itemOids.append(item.attrib['OID'])

        if len(itemOids) == 1:
            return itemOids[0]
        else:
            return None

    def getItemGroupOidFromMetadata(self, metadata, itemOid):
        """
        Param metadata study metadata
        Param itemOid specifies the oid of item which group we are searching
        Return string OID value of found ItemGroupDef or None
        """
        documentTree = ET.ElementTree((ET.fromstring(str(metadata))))

        itemGroupOids = []

        groupFound = False
        # Locate ItemGroupDefs data in XML file via XPath
        for group in documentTree.iterfind('.//odm:ItemGroupDef', namespaces=nsmaps):
            for element in group:
                if (str(element.tag)).strip() == "{http://www.cdisc.org/ns/odm/v1.3}ItemRef":
                    if element.attrib['ItemOID'] == itemOid:
                        itemGroupOids.append(group.attrib['OID'])
                        groupFound = True
                        break

            if groupFound:
                break

        if len(itemGroupOids) == 1:
            return itemGroupOids[0]
        else:
            return None

    def getStudyParameterConfigurationFromMetadata(self, metadata):
        """
        Param metadata study metadata
        Return StudyParameterConfiguration
        """

        studyParameterConfiguration = None
        documentTree = ET.ElementTree((ET.fromstring(str(metadata))))

        # Locate EDC StudyParameterConfiguration element in XML file via XPath
        for configuration in documentTree.iterfind('.//OpenClinica:StudyParameterConfiguration', namespaces=nsmaps):

            studyParameterConfiguration = StudyParameterConfiguration()

            # Locate parameters of interest
            for parameter in configuration:

                if (str(parameter.tag)).strip() == "{http://www.openclinica.org/ns/odm_ext_v130/v3.1}StudyParameterListRef":

                    # Collect Subject DOB
                    if parameter.attrib['StudyParameterListID'] == "SPL_collectDob":
                        if parameter.attrib['Value'] == "1":
                            studyParameterConfiguration.collectSubjectDob = "YES"
                        elif parameter.attrib['Value'] == "2":
                            studyParameterConfiguration.collectSubjectDob = "ONLY_YEAR"
                        elif parameter.attrib['Value'] == "3":
                            studyParameterConfiguration.collectSubjectDob = "NO"

                    # Sex required
                    elif parameter.attrib['StudyParameterListID'] == "SPL_genderRequired":
                        if parameter.attrib['Value'] == "true":
                            studyParameterConfiguration.sexRequired = True
                        elif parameter.attrib['Value'] == "false":
                            studyParameterConfiguration.sexRequired = False

            break

        self.logger.info("Study configuration - CollectSubjectDOB: " + studyParameterConfiguration.collectSubjectDob)
        self.logger.info("Study configuration - SexRequired: " + str(studyParameterConfiguration.sexRequired))

        return studyParameterConfiguration
