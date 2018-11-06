#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

import hashlib


class OCConnectInfo(object):
    """Connection detail for OC SOAP web services

    Create tha basis connection ant authentication information for use with OC web services
    """

    def __init__(self, baseUrl, userName, passwordHash=None):
        """Constructor

        Create complete connection info
        """
        # Initialise members
        self.baseUrl = baseUrl
        self.userName = userName
        self.passwordHash = passwordHash

        # When the URL does not end with '/', add the character to URL
        if baseUrl[-1] != '/':
            self.baseUrl = baseUrl + "/"

    def setPassword(self, password):
        """ Perform sha1 hash
        """
        if not password:
            print("[Error]: can generate sha1, because no password provided.")
        else:
            try:
                self.passwordHash = hashlib.sha1(password).hexdigest()
            except Exception as err:
                print("[Exception]: during generation of sha1 password hash.")

    def setPasswordHash(self, passwordHash):
        self.passwordHash = passwordHash

    def __str__(self):
        """ToString

        Print the class itself
        """
        print("OCConnectInfo:\n baseUrl: " + self.baseUrl + "\nuserName: " + self.userName + "\npasswordHash: " + self.passwordHash)
