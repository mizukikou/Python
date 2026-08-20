import os
pName =  'c:/data/'
if not os.path.exists(pName):
    print('Path does not exist')
    os.makedirs(pName)  # 建立資料夾
    print('Path created')
with open(pName + 'test.txt', 'a',encoding='utf-8') as fName:  # 建立檔案
    fName.write('王一心,85,90,95\n')
    fName.write('李小龍,75,80,85\n')
    fName.write('張三,65,70,75\n')
    # fName.flush()  # 將 Python 內部緩衝區裡的資料，「沖洗」到作業系統的快取記憶體中。
    os.fsync(fName.fileno())  # 會自動在幕後先幫你執行一次 flush()。強制作業系統把快取記憶體中的資料，立馬寫入真正的實體硬碟。
    
fw = open(pName + 'test.txt', 'a', encoding='utf-8')  # 開啟檔案
fw.write('新的一行\n')
# 必須在關閉檔案前執行，否則關閉後 fName.fileno() 就失效了
os.fsync(fw.fileno())  # 必須在關閉檔案前執行，否則關閉後 fw.fileno() 就失效了
fw.close()  # close() 會在Python 內部會自動先幫你執行一次 flush()，然後再關閉檔案。