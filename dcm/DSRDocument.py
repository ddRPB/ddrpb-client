#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# Domain
from dcm.DSRDocumentNode import DSRDocumentNode


class DSRDocument(object):
    """DICOM Structured Report document
    """

    def __init__(self, dcmFile):
        """Default constructor
        """
        self._completionFlag = None 
        self._verificationFlag = None

        # Completion Flag (0040, a491)
        if "CompletionFlag" in dcmFile:
            self._completionFlag = dcmFile.CompletionFlag
        # Verification Flag (0040, a493)
        if "VefificationFlag" in dcmFile:
            self._verificationFlag = dcmFile.VerificationFlag

        self._docTree = self._generateDocTree(dcmFile)

########  ########   #######  ########  ######## ########  ######## #### ########  ######
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##    ##
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##
########  ########  ##     ## ########  ######   ########     ##     ##  ######    ######
##        ##   ##   ##     ## ##        ##       ##   ##      ##     ##  ##             ##
##        ##    ##  ##     ## ##        ##       ##    ##     ##     ##  ##       ##    ##
##        ##     ##  #######  ##        ######## ##     ##    ##    #### ########  ######

    @property
    def completionFlag(self):
        return self._completionFlag

    @property
    def verificationFlag(self):
        return self._verificationFlag

    @property
    def docTree(self):
        return self._docTree

##     ## ######## ######## ##     ##  #######  ########   ######
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ##
#### #### ##          ##    ##     ## ##     ## ##     ## ##
## ### ## ######      ##    ######### ##     ## ##     ##  ######
##     ## ##          ##    ##     ## ##     ## ##     ##       ##
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ##
##     ## ########    ##    ##     ##  #######  ########   ######

    def renderText(self):
        """
        """
        result = ""

        if self._docTree is not None:
            result += self._docTree.renderText()

        return result

    def _generateDocTree(self, dcmFile):
        """
        """      
        rootNode = DSRDocumentNode()


        if "ContentSequence" in dcmFile:
            contents = dcmFile.ContentSequence
            for item in contents:
                node = self._generateContentSequenceNode(item, rootNode)

        return rootNode

    def _generateContentSequenceNode(self, dataset, parent):
        """
        """
        node = DSRDocumentNode(parent)

        # Node basic data
        if "RelationshipType" in dataset:
            node.relationshipType = dataset.RelationshipType
        if "ValueType" in dataset:
            node.valueType = dataset.ValueType

        # Concept sequences
        if "ConceptNameCodeSequence" in dataset:
            seq = dataset.ConceptNameCodeSequence
            if len(seq) == 1:
                for elem in seq:
                    if "CodeValue" in elem:
                        node.nameCodeValue = elem.CodeValue
                    if "CodingSchemeDesignator" in elem:
                        node.nameCodingSchemeDesignator = elem.CodingSchemeDesignator
                    if "CodeMeaning" in elem:
                        node.nameCodeMeaning = elem.CodeMeaning

        if "ConceptCodeSequence" in dataset:
            seq = dataset.ConceptCodeSequence
            if len(seq) == 1:
                for elem in seq:
                    if "CodeValue" in elem:
                        node.codeValue = elem.CodeValue
                    if "CodingSchemeDesignator" in elem:
                        node.codingSchemeDesignator = elem.CodingSchemeDesignator
                    if "CodeMeaning" in elem:
                        node.codeMeaning = elem.CodeMeaning

        # Additional attributes
        if "ContinuityOfContent" in dataset:
            node.continuityOfContent = dataset.ContinuityOfContent

        # According to type store the value
        if "TextValue" in dataset:
            node.textValue = dataset.TextValue
        if "UID" in dataset:
            node.uid = dataset.UID
        if "PersonName" in dataset:
            node.personName = dataset.PersonName

        # Recursive
        if "ContentSequence" in dataset:
            contents = dataset.ContentSequence
            for item in contents:
                subNode = self._generateContentSequenceNode(item, node)           
            
        return node
