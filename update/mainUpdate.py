#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# Standard
import sys
import os
import platform

# Logging
import logging
import logging.config

# PyQt
from PyQt4 import QtGui, QtCore

# Services
from services.AppConfigurationService import AppConfigurationService
from services.UpgradeService import UpgradeService

##     ##    ###    #### ##    ##
###   ###   ## ##    ##  ###   ##
#### ####  ##   ##   ##  ####  ##
## ### ## ##     ##  ##  ## ## ##
##     ## #########  ##  ##  ####
##     ## ##     ##  ##  ##   ###
##     ## ##     ## #### ##    ##


def startup():
    """Start the updater
    """
    logger = logging.getLogger(__name__)
    logging.config.fileConfig("logging.ini", disable_existing_loggers=False)

    logger.info("Updater folder contains: ")
    logger.info(os.listdir("./"))

    appConfig = None
    # Running from source or packed executable
    if (os.path.isfile("mainClient.py") or os.path.isfile("RadPlanBio-client.exe")):
        appConfig = AppConfigurationService("radplanbio-client.cfg")
    else:
        appConfig = AppConfigurationService("../radplanbio-client.cfg")

    section = "Temp"
    if appConfig.hasSection(section):
        isUpgrading = appConfig.get(section)["isupgrading"]
        upgradeFinished = appConfig.get(section)["upgradefinished"]

        app = QtGui.QApplication(sys.argv)

        # Startup
        if isUpgrading == "False":
            # Exit updater
            app.quit()
        else:
            # Start upgrade procedure
            svcUpgrade = UpgradeService()
            svcUpgrade.upgrade()

            # Start client (RadPlanBio-client.exe)
            if platform.system() == "Windows":
                if os.path.isfile("../RadPlanBio-client.exe"):
                    QtCore.QProcess.startDetached("../RadPlanBio-client.exe")
                elif os.path.isfile("RadPlanBio-client.exe"):
                    QtCore.QProcess.startDetached("RadPlanBio-client.exe")
                else:
                    QtCore.QProcess.startDetached("python mainClient.py")
            elif platform.system() == "Linux":
                if os.path.isfile("../RadPlanBio-client"):
                    QtCore.QProcess.startDetached("../RadPlanBio-client")
                else:
                    QtCore.QProcess.startDetached("python mainClient.py")
            else:
                QtCore.QProcess.startDetached("python mainClient.py")

            # Exit updater
            app.quit()

def main():
    """Main function
    """
    currentExitCode = startup()

if __name__ == '__main__':
    main()
