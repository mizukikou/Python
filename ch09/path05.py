import os
import shutil
print(os.getcwd()) # 取得目前工作目錄
#os.makedirs('c:/data/')
#print('directory created')
#os.rmdir('c:/test/')
shutil.rmtree('c:/test/')
print('directory removed')
