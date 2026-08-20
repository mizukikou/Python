import os
pName =  'c:/data/'
if os.path.exists(pName):
    print(pName + ' is a directory')
elif os.path.exists(pName):
    print(pName + ' is a file')
else:
    print(pName + ' is not a directory or a file')
    
fName = 'c:/windows/system.ini'
if os.path.exists(fName):
    print(fName + ' is a file')
else:
    print(fName + ' is not a file')