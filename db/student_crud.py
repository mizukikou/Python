"""
學生資料維護系統 (Student CRUD)

以 tkinter 建立圖形介面，透過 mysql-connector-python 連線 MySQL，
對 `class` 資料庫中的 `students` 資料表進行
Create（新增）、Retrieve（查詢）、Update（修改）、Delete（刪除）。

程式架構分為兩層：
1. 資料層（DB layer）：get_connection() + 各 CRUD 方法中的 SQL 執行邏輯，
   全部使用參數化查詢（%s 佔位符），避免 SQL Injection。
2. 介面層（UI layer）：StudentApp 類別，用 tkinter/ttk 元件組成表單、
   按鈕列、清單（Treeview），並用事件（按鈕 command、Treeview 選取事件）
   把使用者操作串接到資料層。

兩層之間沒有額外的中介物件（例如 ORM Model），因為資料表欄位單純、
規模小，直接讀寫資料庫在此已經足夠清楚，不需要額外抽象。
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

import mysql.connector

# 資料庫連線設定：對應 Readme.md 中提供的帳密與資料庫名稱。
# 正式專案應改用環境變數或設定檔管理帳密，這裡為教學/練習用途直接寫死。
DB_CONFIG = {
    'host': 'localhost',
    'port': 6033,
    'user': 'root',
    'password': '1qaz@wsx',
    'database': 'class',
}


def get_connection():
    """建立並回傳一個新的 MySQL 連線。

    採「每次操作都開新連線、用完即關」的做法（而非全域共用一條連線），
    好處是不用擔心連線逾時或跨執行緒共用的問題，缺點是效能較差；
    對於單機、低頻率操作的桌面工具來說，這個取捨是合理的。
    """
    return mysql.connector.connect(**DB_CONFIG)


class StudentApp:
    """學生資料維護視窗。

    畫面由上到下分成三塊：
        1. 表單（Entry / Combobox）：輸入或顯示單筆學生資料。
        2. 按鈕列：新增 / 修改 / 刪除 / 清除表單 / 重新整理。
        3. 清單（Treeview）：顯示資料表所有列，點選某列會把該列資料
           帶入上方表單，供修改或刪除使用。

    self.selected_id 用來記錄目前表單對應到資料庫哪一筆 cID：
        - None：表單是「新增模式」，按下「新增」會新增一筆資料。
        - 有值：表單是「編輯模式」（來自使用者在清單中點選某列），
          按下「修改」或「刪除」會作用在這個 cID 上。
    """

    def __init__(self, root):
        self.root = root
        self.selected_id = None  # 目前選取的學生編號（cID），None 代表新增模式

        root.title('學生資料維護系統')
        root.geometry('820x520')

        # 依序建立畫面元件：表單 -> 按鈕 -> 清單
        self._build_form()
        self._build_buttons()
        self._build_tree()

        # 一開始就從資料庫載入現有資料，填入清單
        self.refresh()

    def _build_form(self):
        """建立上方輸入表單。

        每個欄位都用一個 tk.StringVar 綁定 Entry/Combobox，
        之後可以用 var.get() 讀取使用者輸入、var.set() 寫入資料
        （例如把清單選取列的資料帶回表單）。
        """
        frame = ttk.LabelFrame(self.root, text='學生資料')
        frame.pack(fill='x', padx=10, pady=5)

        # 第一列：姓名、性別、生日
        row0 = ttk.Frame(frame)
        row0.pack(fill='x', padx=5, pady=3)
        ttk.Label(row0, text='姓名:', width=8).pack(side='left')
        self.var_name = tk.StringVar()
        ttk.Entry(row0, textvariable=self.var_name, width=20).pack(side='left', padx=5)

        ttk.Label(row0, text='性別:', width=6).pack(side='left')
        self.var_sex = tk.StringVar(value='F')
        # 性別限定只能從 F/M 選擇（對應資料表 cSex 為 ENUM('F','M')），
        # state='readonly' 讓使用者只能選不能自行輸入其他字串。
        ttk.Combobox(row0, textvariable=self.var_sex, values=['F', 'M'], width=5, state='readonly').pack(side='left', padx=5)

        ttk.Label(row0, text='生日:', width=6).pack(side='left')
        self.var_birthday = tk.StringVar()
        ttk.Entry(row0, textvariable=self.var_birthday, width=14).pack(side='left', padx=5)
        ttk.Label(row0, text='(YYYY-MM-DD)').pack(side='left')

        # 第二列：Email、電話
        row1 = ttk.Frame(frame)
        row1.pack(fill='x', padx=5, pady=3)
        ttk.Label(row1, text='Email:', width=8).pack(side='left')
        self.var_email = tk.StringVar()
        ttk.Entry(row1, textvariable=self.var_email, width=28).pack(side='left', padx=5)

        ttk.Label(row1, text='電話:', width=6).pack(side='left')
        self.var_phone = tk.StringVar()
        ttk.Entry(row1, textvariable=self.var_phone, width=16).pack(side='left', padx=5)

        # 第三列：地址
        row2 = ttk.Frame(frame)
        row2.pack(fill='x', padx=5, pady=3)
        ttk.Label(row2, text='地址:', width=8).pack(side='left')
        self.var_addr = tk.StringVar()
        ttk.Entry(row2, textvariable=self.var_addr, width=55).pack(side='left', padx=5)

    def _build_buttons(self):
        """建立操作按鈕列，每個按鈕綁定對應的處理方法（command）。"""
        frame = ttk.Frame(self.root)
        frame.pack(fill='x', padx=10, pady=5)
        ttk.Button(frame, text='新增', command=self.create).pack(side='left', padx=3)
        ttk.Button(frame, text='修改', command=self.update).pack(side='left', padx=3)
        ttk.Button(frame, text='刪除', command=self.delete).pack(side='left', padx=3)
        ttk.Button(frame, text='清除表單', command=self.clear_form).pack(side='left', padx=3)
        ttk.Button(frame, text='重新整理', command=self.refresh).pack(side='left', padx=3)

    def _build_tree(self):
        """建立下方的 Treeview 清單，用來顯示資料表所有列。

        Treeview 每一列（item）都存放一組 values，順序對應 columns，
        因此讀取／寫入時要保持欄位順序一致：
        (cID, cName, cSex, cBirthday, cEmail, cPhone, cAddr)。
        """
        columns = ('cID', 'cName', 'cSex', 'cBirthday', 'cEmail', 'cPhone', 'cAddr')
        headings = {'cID': '編號', 'cName': '姓名', 'cSex': '性別', 'cBirthday': '生日',
                    'cEmail': 'Email', 'cPhone': '電話', 'cAddr': '地址'}
        widths = {'cID': 50, 'cName': 80, 'cSex': 40, 'cBirthday': 90,
                  'cEmail': 170, 'cPhone': 100, 'cAddr': 220}

        self.tree = ttk.Treeview(self.root, columns=columns, show='headings', height=14)
        for col in columns:
            self.tree.heading(col, text=headings[col])
            anchor = 'center' if col in ('cID', 'cSex', 'cBirthday') else 'w'
            self.tree.column(col, width=widths[col], anchor=anchor)
        self.tree.pack(fill='both', expand=True, padx=10, pady=5)

        # 使用者點選某一列時觸發 on_select，把該列資料帶回上方表單
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

    # ------------------------------------------------------------------
    # Retrieve（查詢）
    # ------------------------------------------------------------------
    def refresh(self):
        """從資料庫重新查詢所有學生資料，並重繪清單。

        每次呼叫都先清空 Treeview 現有內容，避免重複顯示舊資料，
        再依 cID 排序重新插入，確保清單順序穩定。
        """
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('SELECT cID, cName, cSex, cBirthday, cEmail, cPhone, cAddr FROM students ORDER BY cID')
            for cid, name, sex, birthday, email, phone, addr in cur.fetchall():
                # email/phone/addr 允許 NULL，顯示時轉成空字串避免顯示 None
                self.tree.insert('', 'end', values=(cid, name, sex, birthday, email or '', phone or '', addr or ''))
            cur.close()
            conn.close()
        except mysql.connector.Error as e:
            messagebox.showerror('資料庫錯誤', str(e))

    def on_select(self, event):
        """當使用者在清單中點選某一列時，把該列資料填回表單。

        同時記錄 self.selected_id，讓後續按「修改」或「刪除」
        知道要作用在哪一筆資料。
        """
        selected = self.tree.selection()
        if not selected:
            return
        cid, name, sex, birthday, email, phone, addr = self.tree.item(selected[0], 'values')
        self.selected_id = cid
        self.var_name.set(name)
        self.var_sex.set(sex)
        self.var_birthday.set(birthday)
        self.var_email.set(email)
        self.var_phone.set(phone)
        self.var_addr.set(addr)

    def clear_form(self):
        """清空表單並取消清單選取，回到「新增模式」。"""
        self.selected_id = None
        self.var_name.set('')
        self.var_sex.set('F')
        self.var_birthday.set('')
        self.var_email.set('')
        self.var_phone.set('')
        self.var_addr.set('')
        self.tree.selection_remove(self.tree.selection())

    def _validate(self):
        """新增／修改前的欄位檢查，回傳是否通過驗證。

        只檢查資料表中標示 NOT NULL 的欄位（cName、cBirthday），
        並確認生日字串符合 YYYY-MM-DD 格式，避免寫入資料庫時報錯。
        """
        if not self.var_name.get().strip():
            messagebox.showwarning('輸入錯誤', '姓名為必填欄位')
            return False
        birthday = self.var_birthday.get().strip()
        if not birthday:
            messagebox.showwarning('輸入錯誤', '生日為必填欄位')
            return False
        try:
            date.fromisoformat(birthday)
        except ValueError:
            messagebox.showwarning('輸入錯誤', '生日格式須為 YYYY-MM-DD')
            return False
        return True

    def _form_values(self):
        """把表單目前的內容整理成一個 tuple，供 INSERT/UPDATE 使用。

        Email、電話、地址若使用者留空，轉成 None，
        寫入資料庫時會存成 NULL（對應資料表這三欄允許 NULL 的設計）。
        """
        return (
            self.var_name.get().strip(),
            self.var_sex.get(),
            self.var_birthday.get().strip(),
            self.var_email.get().strip() or None,
            self.var_phone.get().strip() or None,
            self.var_addr.get().strip() or None,
        )

    # ------------------------------------------------------------------
    # Create（新增）
    # ------------------------------------------------------------------
    def create(self):
        """新增一筆學生資料。

        cID 是 auto_increment，不需要也不應該由程式指定，
        所以 INSERT 語句只填其餘六個欄位。
        """
        if not self._validate():
            return
        try:
            conn = get_connection()
            cur = conn.cursor()
            # 使用 %s 佔位符搭配參數 tuple，由驅動程式負責跳脫特殊字元，
            # 避免直接字串拼接造成 SQL Injection。
            cur.execute(
                'INSERT INTO students (cName, cSex, cBirthday, cEmail, cPhone, cAddr) '
                'VALUES (%s, %s, %s, %s, %s, %s)',
                self._form_values(),
            )
            conn.commit()  # INSERT/UPDATE/DELETE 都要 commit 才會真正寫入資料庫
            cur.close()
            conn.close()
            messagebox.showinfo('成功', '新增成功')
            self.clear_form()
            self.refresh()  # 新增後重新查詢，讓清單顯示最新資料（含新的 cID）
        except mysql.connector.Error as e:
            messagebox.showerror('資料庫錯誤', str(e))

    # ------------------------------------------------------------------
    # Update（修改）
    # ------------------------------------------------------------------
    def update(self):
        """修改 self.selected_id 對應的那筆資料。

        必須先在清單中選取一列（selected_id 才會有值），
        否則無法判斷要修改哪一筆，因此先檢查 selected_id 是否為 None。
        """
        if self.selected_id is None:
            messagebox.showwarning('提示', '請先在清單中選擇一筆資料')
            return
        if not self._validate():
            return
        try:
            conn = get_connection()
            cur = conn.cursor()
            # _form_values() 回傳的 tuple 對應 SET 子句的六個 %s，
            # 最後再補上 WHERE 用的 cID，組成完整的參數 tuple。
            cur.execute(
                'UPDATE students SET cName=%s, cSex=%s, cBirthday=%s, cEmail=%s, cPhone=%s, cAddr=%s '
                'WHERE cID=%s',
                self._form_values() + (self.selected_id,),
            )
            conn.commit()
            cur.close()
            conn.close()
            messagebox.showinfo('成功', '修改成功')
            self.clear_form()
            self.refresh()
        except mysql.connector.Error as e:
            messagebox.showerror('資料庫錯誤', str(e))

    # ------------------------------------------------------------------
    # Delete（刪除）
    # ------------------------------------------------------------------
    def delete(self):
        """刪除 self.selected_id 對應的那筆資料。

        刪除是不可逆操作，因此先用 askyesno 跳出確認對話框，
        使用者按「否」則直接 return，不執行任何資料庫操作。
        """
        if self.selected_id is None:
            messagebox.showwarning('提示', '請先在清單中選擇一筆資料')
            return
        if not messagebox.askyesno('確認刪除', f'確定要刪除編號 {self.selected_id} 的資料嗎？'):
            return
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('DELETE FROM students WHERE cID=%s', (self.selected_id,))
            conn.commit()
            cur.close()
            conn.close()
            messagebox.showinfo('成功', '刪除成功')
            self.clear_form()
            self.refresh()
        except mysql.connector.Error as e:
            messagebox.showerror('資料庫錯誤', str(e))


if __name__ == '__main__':
    # 程式進入點：建立主視窗、掛上 StudentApp、進入 tkinter 事件迴圈。
    root = tk.Tk()
    app = StudentApp(root)
    root.mainloop()
