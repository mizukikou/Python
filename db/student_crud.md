# 學生資料維護系統 教學文件

以 tkinter 建立圖形介面，透過 MySQL 對 `class` 資料庫的 `students` 資料表
進行 Create（新增）、Retrieve（查詢）、Update（修改）、Delete（刪除）。

程式檔案：[student_crud.py](student_crud.py)

---

## 一、環境準備

### 1. 安裝 MySQL 並建立資料庫

需要一個本機可連線的 MySQL Server（例如 XAMPP、MySQL Installer 皆可）。
啟動服務後，用 MySQL 用戶端（Workbench、命令列、phpMyAdmin 等）
執行 [Readme.md](Readme.md) 中提供的 SQL，建立資料庫與資料表：

```sql
CREATE TABLE IF NOT EXISTS `students` (
  `cID` tinyint(2) unsigned zerofill NOT NULL auto_increment,
  `cName` varchar(20) collate utf8_unicode_ci NOT NULL,
  `cSex` enum('F','M') collate utf8_unicode_ci NOT NULL default 'F',
  `cBirthday` date NOT NULL,
  `cEmail` varchar(100) collate utf8_unicode_ci default NULL,
  `cPhone` varchar(50) collate utf8_unicode_ci default NULL,
  `cAddr` varchar(255) collate utf8_unicode_ci default NULL,
  PRIMARY KEY  (`cID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
```

連線資訊（對應程式中的 `DB_CONFIG`）：

| 項目     | 值          |
|----------|-------------|
| 主機     | localhost   |
| 帳號     | root        |
| 密碼     | 1qaz@wsx    |
| 資料庫名 | class       |
| 資料表名 | students    |

> 這組帳密僅供本機練習使用。正式環境不應把密碼寫死在程式碼中，
> 應改用環境變數或設定檔（並將該檔案排除在版本控制之外）。

### 2. 安裝 Python 套件

tkinter 是 Python 內建模組，不需另外安裝；但需要安裝 MySQL 驅動程式：

```bash
pip install mysql-connector-python
```

可用以下指令確認安裝成功：

```bash
python -c "import mysql.connector; print('OK')"
```

### 3. 確認可以連線

```bash
python -c "
import mysql.connector
conn = mysql.connector.connect(host='localhost', user='root', password='1qaz@wsx', database='class')
print('連線成功')
conn.close()
"
```

若出現 `Can't connect to MySQL server` 之類的錯誤，代表 MySQL 服務尚未啟動，
需先啟動服務（例如在 XAMPP 控制台點選 Start）再重試。

---

## 二、設計方法

### 1. 分層設計：資料層 / 介面層

程式沒有使用額外的 ORM 或 Model 類別，而是分成兩個部分：

- **資料層**：`get_connection()` 負責建立資料庫連線；每個 CRUD 方法
  （`create` / `refresh` / `update` / `delete`）自行開連線、執行 SQL、
  commit、關閉連線。
- **介面層**：`StudentApp` 類別負責畫面（表單、按鈕、清單）與事件處理，
  呼叫資料層完成實際的資料庫操作。

因為資料表欄位單純、操作情境單機且低頻率，這樣「輕量分層、不過度抽象」
的做法已足夠清楚維護，不需要再拉出 Repository、DAO 等額外物件。

### 2. 連線策略：每次操作開新連線

`get_connection()` 每次呼叫都建立一條新連線，操作完立即關閉，
而不是讓整個程式共用一條全域連線。

- 優點：不用處理連線逾時、多執行緒共用連線等複雜問題。
- 代價：每次操作多了建立連線的開銷。

對於單機桌面工具、操作頻率不高的情境，這個取捨是合理的。

### 3. 表單與清單的資料同步機制

- 表單欄位使用 `tk.StringVar` 綁定 `Entry` / `Combobox`，
  讀取用 `var.get()`，寫入用 `var.set()`。
- 清單使用 `ttk.Treeview`，每一列存放固定順序的 values：
  `(cID, cName, cSex, cBirthday, cEmail, cPhone, cAddr)`。
- 使用者點選清單某一列時，觸發 `<<TreeviewSelect>>` 事件呼叫
  `on_select`，把該列資料寫回表單，同時記錄 `self.selected_id`。
- `self.selected_id` 是「目前模式」的關鍵狀態：
  - `None`：新增模式，按「新增」會新增一筆。
  - 有值：編輯模式，按「修改」／「刪除」作用在這個 `cID` 上。

### 4. 安全性：參數化查詢

所有 SQL 都使用 `%s` 佔位符搭配參數 tuple，例如：

```python
cur.execute(
    'INSERT INTO students (cName, cSex, cBirthday, cEmail, cPhone, cAddr) '
    'VALUES (%s, %s, %s, %s, %s, %s)',
    self._form_values(),
)
```

而不是用字串拼接組出 SQL 字串。這樣可以讓驅動程式負責跳脫特殊字元，
避免 SQL Injection。

### 5. 資料驗證

`_validate()` 只檢查資料表中標示 `NOT NULL` 的欄位（姓名、生日），
並確認生日符合 `YYYY-MM-DD` 格式（用 `datetime.date.fromisoformat` 驗證），
避免把不合法的資料送進資料庫觸發例外。Email、電話、地址允許留空，
留空時會轉成 `None`，寫入資料庫變成 `NULL`。

### 6. 錯誤處理

所有資料庫操作都包在 `try / except mysql.connector.Error` 中，
發生錯誤時用 `messagebox.showerror` 顯示錯誤訊息，
不會讓整個程式當掉，也不會讓使用者看到 Python 例外堆疊。

---

## 三、程式架構總覽

```
student_crud.py
├── DB_CONFIG                  資料庫連線設定
├── get_connection()           建立一條新的 MySQL 連線
└── class StudentApp
    ├── __init__               初始化視窗，依序建立表單/按鈕/清單，並載入資料
    ├── _build_form             建立姓名/性別/生日/Email/電話/地址輸入欄位
    ├── _build_buttons          建立新增/修改/刪除/清除表單/重新整理按鈕
    ├── _build_tree             建立 Treeview 清單並綁定選取事件
    ├── refresh                 [R] 查詢所有資料，重繪清單
    ├── on_select                清單選取事件：把該列資料帶回表單
    ├── clear_form               清空表單，回到新增模式
    ├── _validate                 表單驗證（姓名、生日必填與格式）
    ├── _form_values              把表單內容整理成 SQL 參數 tuple
    ├── create                  [C] 新增一筆資料
    ├── update                  [U] 修改 selected_id 對應的那筆資料
    └── delete                  [D] 刪除 selected_id 對應的那筆資料
```

---

## 四、執行方式

確認 MySQL 服務已啟動、資料表已建立後，執行：

```bash
python student_crud.py
```

操作流程：

1. **新增**：填寫表單（姓名、生日必填），按「新增」。
2. **查詢**：畫面下方清單會自動顯示所有資料；也可按「重新整理」手動刷新。
3. **修改**：在清單中點選一列，資料會帶入表單，修改後按「修改」。
4. **刪除**：在清單中點選一列，按「刪除」，跳出確認對話框後執行刪除。
5. **清除表單**：清空表單內容並取消清單選取，回到新增模式。

---

## 五、常見問題

| 問題 | 原因 / 解法 |
|------|-------------|
| `Can't connect to MySQL server on 'localhost:3306'` | MySQL 服務未啟動，請先啟動服務 |
| `Access denied for user 'root'@'localhost'` | 帳號密碼錯誤，確認與 `DB_CONFIG` 一致 |
| `Unknown database 'class'` | 尚未建立 `class` 資料庫，需先執行建立資料庫的 SQL |
| 生日輸入後跳出格式錯誤 | 需輸入 `YYYY-MM-DD` 格式，例如 `1990-01-01` |
