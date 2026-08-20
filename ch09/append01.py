import os

pName = 'c:/data/'
file_path = pName + 'stu.txt'

# 1. 確保資料夾存在
if not os.path.exists(pName):
    os.mkdir(pName)

# 2. 追加資料區塊（全面指定 utf-8）
with open(file_path, 'a', encoding='utf-8') as fa:
    fa.write('\n趙七海, 66, 87')
    fa.write('\n陳九東, 83, 88')
    print("✍️ 兩筆資料已成功附加到檔案末尾。")

print("==============================")
print("📖 以下為目前 stu.txt 的完整內容：")
print("==============================")

# 3. 讀取並列印區塊（全面指定 utf-8）
with open(file_path, 'r', encoding='utf-8') as fr:
    lst = fr.readlines()  # 一口氣讀取所有行
    for line in lst:
        print(line.strip())  # 完美剃除換行符號
