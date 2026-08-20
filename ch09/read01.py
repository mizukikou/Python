import os
pName =  'c:/data/'
if os.path.exists(pName):
    print('Path exists')
    fr = open(pName + 'test.txt', 'r')  # 讀取檔案內容
    str1 = fr.read(7)  # 讀取前7個字元
    print(str1)
    print('=' * 20)
    print(fr.read())
    fr.close()  # 關閉檔案
    print('=' * 20)
else:
    print('Path does not exist')
    
with open(pName + 'test.txt', 'r') as fr:  # 讀取檔案內容
    str1 = fr.readline()  # 
    print(str1)
    print('=' * 20)
    print(fr.read())