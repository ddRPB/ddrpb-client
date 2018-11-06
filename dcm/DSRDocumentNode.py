#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# Domain
from domain.Node import Node


class DSRDocumentNode(Node):
    """
    """

    def __init__(self, parent=None):
        """Default constructor
        """
        super (DSRDocumentNode, self).__init__("name", parent)

        self._conceptName = ""
        self._valueType = "" # CONTAINER,CODE, TEXT, NUM, PNAME, DATE, TIME, DATETIME, UIDREF, COMPOSITE, IMAGE, WAVEFORM, SCOORD, TCOORD
        self._relationshipType = "" # CONTAINS, HAS OBS CONTEXT
        self._continuityOfContent = "" # SEPARATE
        
        self._nameCodeValue = ""
        self._nameCodingSchemeDesignator = "" # DCM
        self._nameCodeMeaning = ""
        
        self._codeValue = ""
        self._codingSchemeDesignator = ""
        self._codeMeaning = ""

        self._textValue = "" # if value type is text
        self._uid = "" # if value type is uidref
        self._personName = "" # if value type is pname

        #concept code sequence when valueType is code

########  ########   #######  ########  ######## ########  ######## #### ########  ######
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##    ##
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##
########  ########  ##     ## ########  ######   ########     ##     ##  ######    ######
##        ##   ##   ##     ## ##        ##       ##   ##      ##     ##  ##             ##
##        ##    ##  ##     ## ##        ##       ##    ##     ##     ##  ##       ##    ##
##        ##     ##  #######  ##        ######## ##     ##    ##    #### ########  ######

    @property
    def conceptName(self):
        return self._conceptName

    @conceptName.setter
    def conceptName(self, value):
        self._conceptName = value

    @property
    def valueType(self):
        return self._valueType

    @valueType.setter
    def valueType(self, value):
        self._valueType = value

    @property
    def relationshipType(self):
        return self._relationshipType

    @relationshipType.setter
    def relationshipType(self, value):
        self._relationshipType = value

    @property
    def continuityOfContent(self):
        return self._continuityOfContent

    @continuityOfContent.setter
    def continuityOfContent(self, value):
        self._continuityOfContent = value

    @property
    def codeValue(self):
        return self._codeValue

    @codeValue.setter
    def codeValue(self, value):
        self._codeValue = value

    @property
    def codingSchemeDesignator(self):
        return self._codingSchemeDesignator

    @codingSchemeDesignator.setter
    def codingSchemeDesignator(self, value):
        self._codingSchemeDesignator = value

    @property
    def codeMeaning(self):
        return self._codeMeaning

    @codeMeaning.setter
    def codeMeaning(self, value):
        self._codeMeaning = value


    @property
    def nameCodeValue(self):
        return self._nameCodeValue

    @nameCodeValue.setter
    def nameCodeValue(self, value):
        self._nameCodeValue = value

    @property
    def nameCodingSchemeDesignator(self):
        return self._nameCodingSchemeDesignator

    @nameCodingSchemeDesignator.setter
    def nameCodingSchemeDesignator(self, value):
        self._nameCodingSchemeDesignator = value

    @property
    def nameCodeMeaning(self):
        return self._nameCodeMeaning

    @nameCodeMeaning.setter
    def nameCodeMeaning(self, value):
        self._nameCodeMeaning = value
    
    @property
    def textValue(self):
        return self._textValue

    @textValue.setter
    def textValue(self, value):
        self._textValue = value

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, value):
        self._uid = value

    @property
    def personName(self):
        return self._personName

    @personName.setter
    def personName(self, value):
        self._personName = value

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

        if self._valueType == "CONTAINER":
            result += "\n" + "[" + self._nameCodeMeaning + "]" + "\n"
        elif self._valueType == "CODE":
            if self._relationshipType == "HAS OBS CONTEXT":
                result += "\n" + "Observation Context: " + self._nameCodeMeaning + " = " + self._codeMeaning + "\n"
        elif self._valueType == "TEXT":
            result += "\n" + "[" + self._nameCodeMeaning + "]" + "\n"
            result += self._textValue + "\n"
        #elif self._valueType == "NUM":
        elif self._valueType == "PNAME":
            if self._relationshipType == "HAS OBS CONTEXT":
                result += "\n" + "Observation Context: " + self._nameCodeMeaning + " = " + self._personName + "\n"
        #elif self._valueType == "DATE":
        #elif self._valueType == "TIME":
        #elif self._valueType == "DATETIME"
        elif self.valueType == "UIDREF":
            if self.relationshipType == "HAS OBS CONTEXT":
                result += "\n" + "Observation Context: " + self._nameCodeMeaning + " = " + self._uid + "\n"
        #elif self._valueType == "COMPOSITE"
        #elif self._valueType == "IMAGE"
        #elif self._valueType == "WAVEFORM"
        #elif self._valueType == "SCOORD"
        #elif self._valueType == "TCOORD"

        if len(self._children) > 0:
            for node in self._children:
                result += node.renderText()

        return result

    def typeInfo(self):
        """
        """
        return "SRNODE"
