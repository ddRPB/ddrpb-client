#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# Standard
import os
import shutil
import errno
import re

# Logging
import logging
import logging.config

# PyQt - threading
from PyQt4 import QtCore

# Zip
import zipfile

# Services
from services.AppConfigurationService import AppConfigurationService


class Error(EnvironmentError):
    pass

try:
    WindowsError
except NameError:
    WindowsError = None

 ######  ######## ########  ##     ## ####  ######  ########
##    ## ##       ##     ## ##     ##  ##  ##    ## ##
##       ##       ##     ## ##     ##  ##  ##       ##
 ######  ######   ########  ##     ##  ##  ##       ######
      ## ##       ##   ##    ##   ##   ##  ##       ##
##    ## ##       ##    ##    ## ##    ##  ##    ## ##
 ######  ######## ##     ##    ###    ####  ######  ########


class UpgradeService(object):
    """RadPlanBio upgrade client service
    """

    def __init__(self):
        """Default constructor
        """
        self._logger = logging.getLogger(__name__)
        logging.config.fileConfig("logging.ini", disable_existing_loggers=False)

        self._updaterDir = "update"
        self._newzip = "RadPlanBio-client-x64.zip"
        self._backupDir = "client-backup"
        self._newDir = "RadPlanBio-client"

    def preUpgrade(self, data=None, thread=None):
        """Preparation before upgrade
        """
        self._backupCurrentClient("./", self._backupDir)
        self._unzipNewClient()
        self._enableUpgradeFlag()

        if thread:
            thread.emit(QtCore.SIGNAL("finished(QVariant)"), None)
            return None

    def upgrade(self, thread=None):
        """During upgrade (executed when isUpgrading is setup to true)
        """
        self._logger.info("Client upgrade started.")
        try:
            self._logger.info(os.listdir("./"))

            # If running from source
            if os.path.isdir("contexts"):
                shutil.rmtree("contexts")
            if os.path.isdir("converters"):
                shutil.rmtree("converters")
            if os.path.isdir("dcm"):
                shutil.rmtree("dcm")
            if os.path.isdir("domain"):
                shutil.rmtree("domain")
            if os.path.isdir("gui"):
                shutil.rmtree("gui")
            if os.path.isdir("resources"):
                shutil.rmtree("resources")
            if os.path.isdir("services"):
                shutil.rmtree("services")
            if os.path.isdir("test"):
                shutil.rmtree("test")
            if os.path.isdir("utils"):
                shutil.rmtree("utils")
            if os.path.isdir("viewModels"):
                shutil.rmtree("viewModels")
            if os.path.isdir("workers"):
                shutil.rmtree("workers")
            if os.path.isdir("xsl"):
                shutil.rmtree("xsl")
            if os.path.exists("__init__.py"):
                os.remove("__init__.py")
            if os.path.exists("__init__.pyc"):
                os.remove("__init__.pyc")
            if os.path.exists("license.txt"):
                os.remove("license.txt")
            if os.path.exists("mainClient.py"):
                os.remove("mainClient.py")
            if os.path.exists("run-client.sh"):
                os.remove("run-client.sh")

            # If packed to executable
            if os.path.isdir("eggs"):
                shutil.rmtree("eggs")
                self._logger.info("eggs directory removed.")
            if os.path.isdir("include"):
                shutil.rmtree("include")
                self._logger.info("include directory removed.")
            if os.path.isdir("qt4_plugins"):
                shutil.rmtree("qt4_plugins")
                self._logger.info("qt4_plugins directory removed.")

            directory = "./"

            pattern = "^.*\.(dll|pyd|manifest|so)$"
            self._purge(directory, pattern)

            if os.path.exists("RadPlanBio-client.exe"):
                os.remove("RadPlanBio-client.exe")
                self._logger.info("RadPlanBio-client.exe removed.")
            
            # Copy the new version
            self._copytree(
                "RadPlanBio-client",
                "./",
                ignore=shutil.ignore_patterns(self._updaterDir, "client.log", "key.pem", "key.pkl", "logging.ini", "radplanbio-client.cfg")
            )
            self._logger.info("New client dir copied.")
        except Exception as err:
            self._logger.error("Error during update: " + str(err))

        self._enableUpgradeFinishedFlag()
        self._logger.info("Client upgrade finished.")

    def cleanup(self, thread=None):
        """Cleanup after upgrade
        """
        try:
            shutil.rmtree(self._updaterDir)
        except OSError:
            self._logger.info("Cannot cleanup old updater.")

        try:
            shutil.copytree("RadPlanBio-client/update", "./update")
        except OSError:
            self._logger.info("Cannot copy new updater.")

        try:
            shutil.rmtree(self._backupDir)
        except OSError:
            self._logger.info("Cannot cleanup client backup.")

        try:
            os.remove(self._newzip)
        except OSError:
            self._logger.info("Zip not removed because does not exists.")

        try:
            shutil.rmtree(self._newDir)
        except OSError:
            self._logger.info("Cannot cleanup new client dir.")

        self._disableUpgradeFlag() 
 
########  ########  #### ##     ##    ###    ######## ######## 
##     ## ##     ##  ##  ##     ##   ## ##      ##    ##       
##     ## ##     ##  ##  ##     ##  ##   ##     ##    ##       
########  ########   ##  ##     ## ##     ##    ##    ######   
##        ##   ##    ##   ##   ##  #########    ##    ##       
##        ##    ##   ##    ## ##   ##     ##    ##    ##       
##        ##     ## ####    ###    ##     ##    ##    ######## 

    def _backupCurrentClient(self, src, dest):
        """Backup corrent working client installation
        """
        try:
            shutil.copytree(src, dest, ignore=shutil.ignore_patterns(self._backupDir, self._newzip))
        except OSError as e:
            # If the error was caused because the source wasn't a directory
            if e.errno == errno.ENOTDIR:
                shutil.copy(src, dest)
            else:
                self._logger.error("Directory not copied. Error: %s" % e)

    def _unzipNewClient(self):
        """Extract new cient
        """
        zfile = zipfile.ZipFile(self._newzip)
        zfile.extractall("./")

    def _enableUpgradeFlag(self):
        """Setup upgrade flag to application config
        """
        AppConfigurationService().add("Temp")
        AppConfigurationService().set("Temp", "isUpgrading", str(True))
        AppConfigurationService().set("Temp", "upgradeFinished", str(False))
        AppConfigurationService().saveConfiguration()

    def _enableUpgradeFinishedFlag(self):
        """
        """
        AppConfigurationService().set("Temp", "isUpgrading", str(False))
        AppConfigurationService().set("Temp", "upgradeFinished", str(True))
        AppConfigurationService().saveConfiguration()

    def _disableUpgradeFlag(self):
        """Remove upgrade flag from application config
        """
        AppConfigurationService().remove("Temp")
        AppConfigurationService().saveConfiguration()

    def _purge(self, directory, pattern):
        """
        """
        for f in os.listdir(directory):
            if re.search(pattern, f):
                self._logger.info("dir: " + directory + " file: " + f + " will be removed.")
                os.remove(os.path.join(directory, f))

    def _copytree(self, src, dst, symlinks=False, ignore=None):
        """Used to copy into current folder (tweek without folder creation)
        """
        if not os.path.exists(dst):
            os.makedirs(dst)

        names = os.listdir(src)
        if ignore is not None:
            ignored_names = ignore(src, names)
        else:
            ignored_names = set()
 
        errors = []
        for name in names:
            if name in ignored_names:
                self._logger.info("Ignored: " + str(name))
                continue
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            try:
                if symlinks and os.path.islink(srcname):
                    linkto = os.readlink(srcname)
                    os.symlink(linkto, dstname)
                elif os.path.isdir(srcname):
                    self._copytree(srcname, dstname, symlinks, ignore)
                else:
                    shutil.copy2(srcname, dstname)
            except IOError as why:
                errors.append((srcname, dstname, str(why)))
            except Error as err:
                errors.extend(err.args[0])
        try:
            shutil.copystat(src, dst)
        except OSError as why:
            if WindowsError is not None and isinstance(why, WindowsError):
                # Copying file access times may fail on Windows
                pass
            else:
                errors.extend((src, dst, str(why)))
        if errors:
            raise Error(errors)
