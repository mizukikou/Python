# 學生假資料產生器 - 教學文件

## 概述

[generate_students.py](generate_students.py) 是一個 **Python** 命令列工具，能夠自動產生符合台灣風格的學生假資料，並直接寫入 `MySQL` 資料庫的 `students` 資料表中。

### 核心功能

- 🎯 **指定筆數**：透過命令列參數 `-n` 指定要新增的資料筆數（預設 100 筆）
- 🔍 **重複檢查**：新增前自動讀取資料庫現有資料，確保**姓名、Email、手機**三個欄位不會出現重複
- 🇹🇼 **台灣風格**：產生的資料包含中文姓名、台灣地址、台灣手機號碼等
- 📊 **即時統計**：執行後顯示預覽、統計摘要與驗證結果

---

## 前置需求

### 1. Python 環境

- Python 3.8 以上版本

### 2. 安裝相依套件

```bash
pip install mysql-connector-python
```

### 3. 資料庫環境

確保 `MySQL` 伺服器正在運行，且 `class` 資料庫中已建立 `students` 資料表：

```sql
CREATE TABLE IF NOT EXISTS students (
    cID       SMALLINT UNSIGNED ZEROFILL NOT NULL AUTO_INCREMENT PRIMARY KEY,
    cName     VARCHAR(20)     NOT NULL,
    cSex      ENUM('F','M')   NOT NULL DEFAULT 'F',
    cBirthday DATE            NOT NULL,
    cEmail    VARCHAR(100)    DEFAULT NULL,
    cPhone    VARCHAR(50)     DEFAULT NULL,
    cAddr     VARCHAR(255)    DEFAULT NULL,
    cHeight   TINYINT(3) UNSIGNED DEFAULT NULL,
    cWeight   TINYINT(3) UNSIGNED DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8_unicode_ci;
```

> **注意**：若預期資料總筆數超過 255 筆，請將 `cID` 型態設為 `SMALLINT`（最大 65,535）或 `INT`（最大 ~21 億），避免 `Out of range` 錯誤。

---

## 使用方式

### 基本用法

```bash
# 預設新增 100 筆
python generate_students.py

# 指定新增 50 筆
python generate_students.py -n 50

# 指定新增 200 筆
python generate_students.py --count 200

# 查看說明
python generate_students.py --help
```

### 命令列參數

參數|簡寫|預設值|說明
---|---|---|---
`--count`|`-n`|`100`|要新增的學生資料筆數

---

## 執行流程

程式執行時會依序進行以下四個步驟：

```
┌─────────────────────────────────────────────────┐
│  Step 1：讀取資料庫現有資料                        │
│  ↓ 從 students 表讀取所有 cName, cEmail, cPhone   │
│  ↓ 建立重複檢查用的集合（Set）                      │
├─────────────────────────────────────────────────┤
│  Step 2：產生 N 筆不重複的假資料                    │
│  ↓ 逐筆產生，每筆都與已有資料比對                    │
│  ↓ 若重複則重新產生（最多重試 1000 次）              │
├─────────────────────────────────────────────────┤
│  Step 3：寫入資料庫                               │
│  ↓ 使用 executemany 批次寫入                      │
│  ↓ 失敗時自動 rollback                           │
├─────────────────────────────────────────────────┤
│  Step 4：驗證結果                                 │
│  ↓ 查詢資料庫總筆數並顯示                          │
└─────────────────────────────────────────────────┘
```

### 執行範例輸出

```
=======================================================
  學生假資料產生器（本次新增 50 筆）
=======================================================

【Step 1】讀取資料庫現有資料...

📂 資料庫現有 130 筆學生資料
   已有姓名 130 個、Email 130 個、手機 130 個

【Step 2】產生 50 筆不重複的假資料...

📋 預覽前 5 筆資料：

姓名     性別   生日           Email                          手機             身高     體重
------------------------------------------------------------------------------------------
張賢仁    M    1992-06-15   john510@outlook.com            0928251692     176    78
盧瑋勝    M    1984-09-28   alex193@hotmail.com            0965334527     181    61
羅嘉信    M    1995-08-20   william105@yahoo.com.tw        0952055557     176    78
江涵彤    F    1989-12-12   barbara62@yahoo.com.tw         0935430198     154    45
余薇儀    F    1985-08-02   jessica400@yahoo.com.tw        0960952735     164    69
... 還有 45 筆

📊 新增資料統計：男生 24 人、女生 26 人
   平均身高 167.1 cm、平均體重 63.7 kg

【Step 3】寫入資料庫...

✅ 成功新增 50 筆學生資料！

📊 資料庫目前共有 180 筆學生資料
```

---

## 資料庫連線設定

程式中的連線設定位於 `DB_CONFIG` 字典（第 28~35 行）：

```python
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "1qaz@wsx",
    "database": "class",
    "charset": "utf8mb4",
}
```

> 如需連接其他資料庫，請修改上述設定值。

---

## 重複檢查機制

程式會檢查以下三個欄位，確保新增的資料不與資料庫中已存在的資料重複：

欄位|用途|說明
---|---|---
`cName`（姓名）|唯一性檢查|新產生的中文姓名不可與已有紀錄重複
`cEmail`（Email）|唯一性檢查|比對時不區分大小寫（統一轉為小寫比較）
`cPhone`（手機）|唯一性檢查|10 位數手機號碼不可重複

### 防護機制

- **即時同步**：每產生一筆資料，立即加入已使用集合，避免新資料之間也出現重複
- **重試上限**：每個欄位最多重試 `1000` 次，超過則自動停止並提示，避免無窮迴圈
- **交易保護**：寫入失敗時自動 `ROLLBACK`，不會留下不完整的資料

---

## 假資料素材一覽

程式內建豐富的台灣風格素材，以下列出各類別的數量與範圍：

### 姓名

類別|數量|範例
---|---|---
中文姓氏|50 個|陳、林、黃、張、李、王...
男性名字用字|40 個|志、明、建、國、文、偉...
女性名字用字|40 個|怡、雅、婷、惠、玲、淑...

- 名字長度：1~2 個字（2 個字機率 75%）
- 男性姓名理論組合：50 × (40 + 40×39) = 50 × 1,600 = **80,000** 種
- 女性姓名理論組合：同上 **80,000** 種

### 生日

- 範圍：`1984-01-01` ~ `1995-12-31`
- 天數跨度：約 4,383 天

### Email

類別|數量|說明
---|---|---
男性英文名|50 個|james, john, robert...
女性英文名|60 個|mary, patricia, jennifer...
Email 域名|8 個|gmail.com, yahoo.com.tw...
數字後綴|0~999|60% 機率加上數字後綴

### 手機號碼

- 格式：`09XXXXXXXX`（10 位數）
- 前 4 碼有 30 種選擇，後 6 碼為隨機數字
- 理論組合：30 × 10^6 = **3,000 萬**種

### 地址

類別|數量|範例
---|---|---
縣市|9 個|台北市、新北市、桃園市...
路名|42 條|忠孝東路、仁愛路、信義路...
門牌號碼|1~500|隨機
巷弄|30% 機率加上|1~30 巷
樓層|40% 機率加上|2~15 樓

### 身高 & 體重

項目|男性|女性|說明
---|---|---|---
身高（cm）|165~185|150~170|隨機整數
體重（kg）|依 BMI 計算|依 BMI 計算|BMI 範圍 18.5~27.0

---

## 程式架構

```
generate_students.py
│
├── DB_CONFIG              # 資料庫連線設定
├── 假資料素材常數           # LAST_NAMES, MALE_NAME_CHARS, ROADS, CITIES 等
│
├── 資料產生函式
│   ├── generate_chinese_name(sex)    # 產生中文姓名
│   ├── generate_birthday()           # 產生隨機生日
│   ├── generate_email(sex)           # 產生隨機 Email
│   ├── generate_phone()              # 產生台灣手機號碼
│   ├── generate_address()            # 產生隨機地址
│   ├── generate_height(sex)          # 產生身高
│   └── generate_weight(sex, height)  # 產生體重（依 BMI）
│
├── 資料庫操作函式
│   ├── load_existing_data()          # 讀取現有資料（用於重複檢查）
│   ├── generate_students(count, existing)  # 產生不重複的假資料
│   ├── insert_students(students)     # 批次寫入資料庫
│   └── verify_result()               # 驗證寫入結果
│
└── 主程式
    ├── parse_args()                  # 解析命令列參數
    └── main()                        # 主流程控制
```

---

## 函式說明

### `load_existing_data() → dict`

從資料庫讀取現有的 `cName`、`cEmail`、`cPhone` 三個欄位，回傳一個包含三個 `set` 的字典，用於後續的重複比對。

### `generate_students(count, existing) → list`

核心產生函式。接收目標筆數和已存在資料集合，逐筆產生不重複的學生資料。每產生一筆即同步更新已使用集合，確保新資料之間也不重複。

### `generate_chinese_name(sex) → str`

根據性別從不同的名字用字列表中隨機抽取，組合為「姓 + 名」的中文全名。名字長度以 2 個字為主（75% 機率）。

### `generate_weight(sex, height) → int`

根據身高和隨機 BMI（18.5~27.0）計算出合理體重，而非完全隨機，使資料更貼近真實。

### `insert_students(students) → None`

使用 `executemany` 進行批次寫入。寫入失敗時會自動 `ROLLBACK`，確保資料完整性。

---

## 已知限制與注意事項

> [!WARNING]
> `cID` 欄位型態若為 `TINYINT`（最大 255），資料超過 255 筆時會報 `Out of range` 錯誤。
> 請在使用前將 `cID` 改為 `SMALLINT` 或 `INT`：
> ```sql
> ALTER TABLE students MODIFY COLUMN cID SMALLINT UNSIGNED ZEROFILL NOT NULL AUTO_INCREMENT;
> ```

> [!NOTE]
> - 姓名的理論組合約 80,000 種，但實際可用組合會隨已有資料增加而減少
> - 當要求的筆數接近素材組合上限時，程式會自動停止並回報已產生的筆數
> - Windows 環境下，程式已處理 `cp950` 編碼問題，可正常顯示中文與 Emoji

---

## 常見問題

### Q1：如何修改產生的假資料風格？

修改程式頂部的常數即可：

```python
# 修改姓氏列表
LAST_NAMES = ["陳", "林", "黃", ...]

# 修改生日範圍（在 generate_birthday 函式中）
start_date = date(1990, 1, 1)  # 改為 1990 年起
end_date = date(2005, 12, 31)  # 改為 2005 年止

# 修改身高範圍（在 generate_height 函式中）
return random.randint(170, 190)  # 男性身高範圍
```

### Q2：如何連接不同的資料庫？

修改 `DB_CONFIG` 設定：

```python
DB_CONFIG = {
    "host": "192.168.1.100",     # 遠端伺服器 IP
    "port": 3306,
    "user": "your_user",
    "password": "your_password",
    "database": "your_database",
    "charset": "utf8mb4",
}
```

### Q3：執行時出現 `UnicodeEncodeError` 怎麼辦？

程式已內建解決方案。若仍有問題，可在執行前設定環境變數：

```bash
# Windows PowerShell
$env:PYTHONIOENCODING="utf-8"
python generate_students.py
```

### Q4：可以產生多少筆不重複的資料？

取決於素材的組合數量。以目前的素材計算：

欄位|理論上限|說明
---|---|---
姓名|~80,000|50 姓 × (40 + 40×39) 名
Email|~880,000|110 名 × 8 域名 × 1000 數字
手機|~30,000,000|30 前綴 × 10^6

**姓名是瓶頸**，實務上建議單次產生不超過 **5,000** 筆，以避免重試次數過多導致效率下降。
