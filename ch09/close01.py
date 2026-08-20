import os
pName = 'c:/data/'
if not os.path.exists(pName):
    os.makedirs(pName)  # 上層資料夾不存在時；makedirs：會自動全部建好。makedir：會直接報錯。
    print('Path created')
else:
    print('Path exists')
    with open(pName + 'test.txt', 'a') as fName:  # 於檔案末尾追加內容
        fName.write('Whole new world!\n')
    # fName.close()  # 不需要，with語句會自動關閉文件