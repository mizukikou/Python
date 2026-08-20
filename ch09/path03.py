import os
pName =  'c:/data/'
if os.path.exists(pName):
    print('Path exists')
else:
    print('Path does not exist')
    os.makedirs(pName) # 上層資料夾不存在時；makedirs：會自動全部建好。makedir：會直接報錯。
    print('Path created')