#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

from dicomdeident.AbstractAttributeAction import AbstractAttributeAction


class KeepAttributeAction(AbstractAttributeAction):
    """K - keep (unchanged for non-sequences attributes, cleaned for sequences)
    """

    def __init__(self):
        """Default constructor
        """
        super(KeepAttributeAction, self).__init__("Keep",
                                                  "Keep (unchanged for non-sequences attributes, cleaned for sequences)",
                                                  "K")

##     ## ######## ######## ##     ##  #######  ########   ######
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ##
#### #### ##          ##    ##     ## ##     ## ##     ## ##
## ### ## ######      ##    ######### ##     ## ##     ##  ######
##     ## ##          ##    ##     ## ##     ## ##     ##       ##
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ##
##     ## ########    ##    ##     ##  #######  ########   ######
    
    def PerformDeident(self, element, deidentConfig, idat):
        """De-identify
        """
        if element.VR == "SQ":
            for sequence in element.value:
                self._clean(sequence, idat)
        else:
            pass

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
        """Means replace with values of similar meaning known not to contain identifying information and consistent with the VR
        """
        if element.VR == "SQ":
            for sequence in element.value:
                self._clean(sequence, idat)
        else:
            # Search for IDAT in values
            for identifying in idat:
                if identifying in element.value:
                    element.value.replace(identifying, "")
