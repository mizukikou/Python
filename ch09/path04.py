import os
pName =  'c:/data/'
if os.path.exists(pName):
    print('Path exists')
    os.rmdir(pName)  # 內容需是空(沒檔案)的
    print('Path removed')
else:
    print('Path does not exist')
