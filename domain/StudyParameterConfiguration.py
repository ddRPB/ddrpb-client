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


class StudyParameterConfiguration(object):
    """StudyParameterConfiguration - wrapper around OpenClinica study parameters configuration
    """

######   #######  ##    ##  ######  ######## ########  ##     ##  ######  ########
##    ## ##     ## ###   ## ##    ##    ##    ##     ## ##     ## ##    ##    ##
##       ##     ## ####  ## ##          ##    ##     ## ##     ## ##          ##
##       ##     ## ## ## ##  ######     ##    ########  ##     ## ##          ##
##       ##     ## ##  ####       ##    ##    ##   ##   ##     ## ##          ##
##    ## ##     ## ##   ### ##    ##    ##    ##    ##  ##     ## ##    ##    ##
######   #######  ##    ##  ######     ##    ##     ##  #######   ######     ##

    def __init__(self, logger=None):
        """Constructor
        """
        # Logger
        self._logger = logger or logging.getLogger(__name__)

        # Init members
        self._sexRequired = None
        self._collectSubjectDob = None

########  ########   #######  ########  ######## ########  ######## #### ########  ######
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##    ##
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##
########  ########  ##     ## ########  ######   ########     ##     ##  ######    ######
##        ##   ##   ##     ## ##        ##       ##   ##      ##     ##  ##             ##
##        ##    ##  ##     ## ##        ##       ##    ##     ##     ##  ##       ##    ##
##        ##     ##  #######  ##        ######## ##     ##    ##    #### ########  ######

    @property
    def sexRequired(self):
        """Sex Required Getter
        """
        return self._sexRequired

    @sexRequired.setter
    def sexRequired(self, sexRequired):
        """"Sex Required Setter
        """
        if self._sexRequired != sexRequired:
            self._sexRequired = sexRequired

    @property
    def collectSubjectDob(self):
        """Collect Subject DOB Getter
        """
        return self._collectSubjectDob

    @collectSubjectDob.setter
    def collectSubjectDob(self, collectSubjectDob):
        """"Collect Subject DOB Setter
        """
        if self._collectSubjectDob != collectSubjectDob:
            self._collectSubjectDob = collectSubjectDob
