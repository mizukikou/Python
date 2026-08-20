import os
pName = 'c:/data/'
if os.path.exists(pName):
    print('Path exists')
    fr = open(pName + 'stu.txt', 'r', encoding='utf-8')  # 開啟檔案
    # lst = fr.readlines()  # 讀取檔案內容
    # for line in lst:
    for line in fr:
        print(line.strip())  # strip()：去掉字串前後的空白字元
    fr.close()  # 關閉檔案
else:
    print('Path does not exist')
    
# strip() 函數會自動切除字串最前端與最尾端的所有空白字元，包含空格、縮排（Tab）以及最關鍵的「換行符號（\n）