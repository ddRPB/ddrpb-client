
class MainzellisteConnectInfo():
    """Connection detail for Mainzelliste REST services

    Create tha basis conection ant authentication infromation for use with Mainzelliste REST interface
    """

    def __init__(self, baseUrl, userName, password, apiKey):
        """Constructor

        Create complete connection info
        """
        # Initialise members
        self.baseUrl = baseUrl
        self.userName = userName
        self.password = password
        self.apiKey = apiKey

        # When the URL does not end with '/', add the character to URL
        if baseUrl[-1] != '/' : self.baseUrl = baseUrl + "/"


    def __str__(self):
        """ToString

        Print the class itself
        """
        print "MainzellisteConnectInfo:\n baseUrl: " + self.baseUrl + "\nuserName: " + self.userName + "\npassword: " + self.password + "\nappiKey: " + self.apiKey

