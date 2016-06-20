# Create deployment .spec files
python ../../../programming/pyinstaller-2.0/pyinstaller.py --noconsole --debug --strip -n RadPlanBio-client ./client/mainClient.py

# Build distibution
../../../programming/pyinstaller-2.0/pyinstaller.py RadPlanBio-client.spec

# Copy configuration files
cp ./client/logging.ini ./dist/RadPlanBio-client/
cp ./client/radplanbio-client.cfg ./dist/RadPlanBio-client/
~                                                   
