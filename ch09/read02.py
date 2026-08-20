import os
pName =  'c:/data/'
if os.path.exists(pName):
    print('Path exists')
    with open(pName + 'stu.txt', 'r',encoding='utf-8') as fr:  # 於檔案末尾追加內容
        str1 = fr.readline() 
        print(str1, end='')
        print('=' * 20)
        str2 = fr.readline(7)  # 
        print(str2)
        print('=' * 20)
        for line in fr:
            print(line, end ='')
else:
    print('Path does not exist')
    
# fr.readline() 或 for line in fr 時，Python 讀出來的字串末尾，本來就包含檔案內建的換行符號 \n。
# 另外 print() 它預設的行為就是印完所有東西後，自動在結尾補上一個 \n。
# 所以加上 end='' 參數，讓 print() 不要再自動補上 \n，這樣就不會出現多餘的空行了。