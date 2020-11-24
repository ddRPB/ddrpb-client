#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# PyQt
from PyQt4 import QtCore


class WorkerThread(QtCore.QThread):
    """General purpose thread class, takes function and function arguments as parameters
    """

 ######   #######  ##    ##  ######  ######## ########  ##     ##  ######  ########  #######  ########   ######
##    ## ##     ## ###   ## ##    ##    ##    ##     ## ##     ## ##    ##    ##    ##     ## ##     ## ##    ##
##       ##     ## ####  ## ##          ##    ##     ## ##     ## ##          ##    ##     ## ##     ## ##
##       ##     ## ## ## ##  ######     ##    ########  ##     ## ##          ##    ##     ## ########   ######
##       ##     ## ##  ####       ##    ##    ##   ##   ##     ## ##          ##    ##     ## ##   ##         ##
##    ## ##     ## ##   ### ##    ##    ##    ##    ##  ##     ## ##    ##    ##    ##     ## ##    ##  ##    ##
 ######   #######  ##    ##  ######     ##    ##     ##  #######   ######     ##     #######  ##     ##  ######

    def __init__(self, function, args=None):
        """Default constructor
        @param function function to run on start
        @param args args to pass to function
        """
        QtCore.QThread.__init__(self)

        self.function = function
        self.args = args

    def __del__(self):
        """Overwrite __del__ method to ensure that thread stops processing before it gets destroyed
        """
        self.wait()

##     ## ######## ######## ##     ##  #######  ########   ######
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ##
#### #### ##          ##    ##     ## ##     ## ##     ## ##
## ### ## ######      ##    ######### ##     ## ##     ##  ######
##     ## ##          ##    ##     ## ##     ## ##     ##       ##
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ##
##     ## ########    ##    ##     ##  #######  ########   ######

    def run(self):
        """Runs the function with arguments
        """
        self.function(self.args, self)

    def stop(self):
        """Terminates the thread
        """
        self.terminate()
