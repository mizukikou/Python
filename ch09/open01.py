import os
pName = 'c:/data/'
if not os.path.exists(pName):
    os.makedirs(pName)  # 上層資料夾不存在時；makedirs：會自動全部建好。makedir：會直接報錯。
    print('Path created')
else:
    print('Path exists')
    fName = open(pName + 'test.txt', 'a')  # 於檔案末尾追加內容
    fName.write('Hello, world!\n')
    fName.close()