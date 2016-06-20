python C:\Users\toskrip\Desktop\packing-machine\PyInstaller-2.1\PyInstaller-2.1\pyinstaller.py --icon=favicon.ico --noconsole -n RadPlanBio-client .\client\mainClient.py
python C:\Users\toskrip\Desktop\packing-machine\PyInstaller-2.1\PyInstaller-2.1\pyinstaller.py --icon=favicon.ico --noconsole RadPlanBio-client.spec

copy .\client\logging.ini .\dist\RadPlanBio-client\
copy .\client\radplanbio-client.cfg .\dist\RadPlanBio-client\
copy .\client\license.txt .\dist\RadPlanBio-client\

python C:\Users\toskrip\Desktop\packing-machine\PyInstaller-2.1\PyInstaller-2.1\pyinstaller.py --noconsole -n RadPlanBio-update .\client\update\mainUpdate.py
python C:\Users\toskrip\Desktop\packing-machine\PyInstaller-2.1\PyInstaller-2.1\pyinstaller.py --noconsole RadPlanBio-update.spec

copy .\client\logging.ini .\dist\RadPlanBio-update\
mkdir .\dist\RadPlanBio-client\RadPlanBio-update
xcopy .\dist\RadPlanBio-update .\dist\RadPlanBio-client\RadPlanBio-update /e
rename .\dist\RadPlanBio-client\RadPlanBio-update\ update