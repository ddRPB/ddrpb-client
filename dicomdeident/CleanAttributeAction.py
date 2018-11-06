#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

from dicomdeident.AbstractAttributeAction import AbstractAttributeAction


class CleanAttributeAction(AbstractAttributeAction):
    """C - clean means replace with value of similar meaning known not to 
    contain identifying information and consisten with VR
    """

    def __init__(self):
        """Default constructor
        """
        super (CleanAttributeAction, self).__init__("Clear", "Clean, means replace with values of similar meaning known not to contain identifying information and consistent with the VR", "C")

##     ## ######## ######## ##     ##  #######  ########   ######
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ##
#### #### ##          ##    ##     ## ##     ## ##     ## ##
## ### ## ######      ##    ######### ##     ## ##     ##  ######
##     ## ##          ##    ##     ## ##     ## ##     ##       ##
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ##
##     ## ########    ##    ##     ##  #######  ########   ######
    
    def PerformDeident(self, element, deidentConfig, idat):
        """Deidentify
        """
        if element.VR == "SQ":
            for sequence in element.value:
                self._clean(sequence, idat)
        else:
            self._clean(element, idat)

    def PerformReident(self):
        """Not Implemented
        """
        pass

########  ########  #### ##     ##    ###    ######## ########
##     ## ##     ##  ##  ##     ##   ## ##      ##    ##
##     ## ##     ##  ##  ##     ##  ##   ##     ##    ##
########  ########   ##  ##     ## ##     ##    ##    ######
##        ##   ##    ##   ##   ##  #########    ##    ##
##        ##    ##   ##    ## ##   ##     ##    ##    ##
##        ##     ## ####    ###    ##     ##    ##    ########

    def _clean(self, element, idat):
        """Means replace with values of similar meaning known not to 
        contain identifying information and consistent with the VR
        """
        if element.VR == "SQ":
            for sequence in element.value:
                self._clean(sequence, idat)
        # TODO: need to specify branches for each DICOM VR type
        else:
            # Search for IDAT in values
            for identifying in idat:
                if identifying in element.value:
                    element.value.replace(identifying, "")
