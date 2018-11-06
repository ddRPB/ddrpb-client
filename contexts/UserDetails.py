#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# Singleton
from utils.SingletonType import SingletonType

# Python 2 and 3
from six import with_metaclass


class UserDetails(with_metaclass(SingletonType)):
    """Logged user details
    """

    def __init__(self):
        """Default Constructor
        """
        self.username = ""
        self.password = ""
        self.clearpass = ""
