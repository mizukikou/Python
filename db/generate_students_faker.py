# -*- coding: utf-8 -*-
"""
使用 Faker 套件產生學生假資料並寫入 MySQL 的 students 資料表。
利用 Faker 的 zh_TW（台灣）本地化提供者，產生貼近真實的台灣風格假資料。
新增資料前會檢查資料庫中已存在的 Email、手機、姓名，確保不會產生重複資料。

使用方式：
    python generate_students_faker.py              # 預設新增 100 筆
    python generate_students_faker.py -n 50        # 指定新增 50 筆
    python generate_students_faker.py --count 200  # 指定新增 200 筆

前置安裝：
    pip install faker mysql-connector-python
"""

import sys
import io
import argparse

# 強制 stdout 使用 utf-8 編碼，避免 Windows cp950 問題
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import mysql.connector
import random
from datetime import date
from faker import Faker

# ============================================================
# 初始化 Faker（使用台灣本地化）
# ============================================================
fake = Faker("zh_TW")

# 設定隨機種子（可選，設定後每次執行結果一致，方便測試）
# Faker.seed(42)
# random.seed(42)

# ============================================================
# 資料庫連線設定
# ============================================================
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "1qaz@wsx",
    "database": "class",
    "charset": "utf8mb4",
}

# ============================================================
# 資料產生設定
# ============================================================

# 生日範圍
BIRTHDAY_START = date(1984, 1, 1)
BIRTHDAY_END = date(1995, 12, 31)

# 身高範圍（公分）
HEIGHT_RANGE = {
    "M": (165, 185),
    "F": (150, 170),
}

# BMI 範圍（用於計算體重）
BMI_MIN = 18.5
BMI_MAX = 27.0

# Email 域名列表（Faker 預設域名較少，自訂增加多樣性）
EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com.tw", "hotmail.com", "outlook.com",
    "mail.com", "student.edu.tw", "campus.tw", "mymail.com",
]

# 每筆資料產生的最大重試次數，避免無窮迴圈
MAX_RETRIES = 1000


# ============================================================
# 資料產生函式
# ============================================================

def generate_name(sex: str) -> str:
    """使用 Faker 產生台灣風格中文姓名"""
    if sex == "M":
        return fake.name_male()
    else:
        return fake.name_female()


def generate_birthday() -> date:
    """產生指定範圍內的隨機生日"""
    return fake.date_between(start_date=BIRTHDAY_START, end_date=BIRTHDAY_END)


def generate_email(name: str) -> str:
    """
    產生隨機 Email。
    使用 Faker 產生使用者名稱部分，搭配自訂域名列表。
    """
    username = fake.user_name()
    # 有機率加上數字後綴，增加唯一性
    if random.random() > 0.3:
        username += str(random.randint(1, 9999))
    domain = random.choice(EMAIL_DOMAINS)
    return f"{username}@{domain}"


def generate_phone() -> str:
    """
    產生台灣手機號碼格式（09XXXXXXXX）。
    使用 Faker 的 zh_TW phone_number 或自訂格式。
    """
    # Faker zh_TW 的 phone_number 可能包含市話，這裡確保只產生手機
    prefixes = [
        "0910", "0911", "0912", "0916", "0918", "0920",
        "0921", "0922", "0928", "0930", "0932", "0935",
        "0937", "0938", "0939", "0952", "0955", "0956",
        "0958", "0960", "0963", "0965", "0968", "0970",
        "0972", "0975", "0978", "0905", "0906", "0907",
    ]
    prefix = random.choice(prefixes)
    remaining = fake.numerify("######")  # 產生 6 位隨機數字
    return prefix + remaining


def generate_address() -> str:
    """使用 Faker 產生台灣風格地址"""
    return fake.address().replace("\n", "")


def generate_height(sex: str) -> int:
    """產生合理的身高（公分）"""
    low, high = HEIGHT_RANGE[sex]
    return random.randint(low, high)


def generate_weight(height: int) -> int:
    """根據身高和隨機 BMI 計算合理體重（公斤）"""
    bmi = random.uniform(BMI_MIN, BMI_MAX)
    height_m = height / 100
    weight = bmi * (height_m ** 2)
    return round(weight)


# ============================================================
# 資料庫操作函式
# ============================================================

def load_existing_data() -> dict:
    """
    從資料庫讀取已存在的學生資料，回傳各欄位的集合，用於重複檢查。
    檢查欄位：cName（姓名）、cEmail（Email）、cPhone（手機）
    """
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    existing = {
        "names": set(),
        "emails": set(),
        "phones": set(),
    }

    try:
        cursor.execute("SELECT cName, cEmail, cPhone FROM students;")
        rows = cursor.fetchall()
        for row in rows:
            if row[0]:
                existing["names"].add(row[0])
            if row[1]:
                existing["emails"].add(row[1].lower())
            if row[2]:
                existing["phones"].add(row[2])

        print(f"📂 資料庫現有 {len(rows)} 筆學生資料")
        print(f"   已有姓名 {len(existing['names'])} 個、"
              f"Email {len(existing['emails'])} 個、"
              f"手機 {len(existing['phones'])} 個\n")

    except mysql.connector.Error as err:
        print(f"❌ 讀取現有資料失敗：{err}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

    return existing


def generate_students(count: int, existing: dict) -> list:
    """
    使用 Faker 產生指定數量的學生假資料，確保與資料庫已有資料不重複。

    重複檢查欄位：
    - cName（姓名）：不可與已有姓名重複
    - cEmail（Email）：不可與已有 Email 重複（不區分大小寫）
    - cPhone（手機）：不可與已有手機重複
    """
    students = []

    # 複製一份，在生成過程中同步更新，避免新資料之間也重複
    used_names = set(existing["names"])
    used_emails = set(existing["emails"])
    used_phones = set(existing["phones"])

    generated = 0

    while generated < count:
        sex = random.choice(["M", "F"])

        # --- 產生不重複的姓名 ---
        retries = 0
        name = generate_name(sex)
        while name in used_names:
            name = generate_name(sex)
            retries += 1
            if retries > MAX_RETRIES:
                print(f"⚠️  姓名組合已接近上限，已成功產生 {generated} 筆（目標 {count} 筆）")
                return students
        used_names.add(name)

        # --- 產生不重複的 Email ---
        retries = 0
        email = generate_email(name)
        while email.lower() in used_emails:
            email = generate_email(name)
            retries += 1
            if retries > MAX_RETRIES:
                print(f"⚠️  Email 組合已接近上限，已成功產生 {generated} 筆（目標 {count} 筆）")
                return students
        used_emails.add(email.lower())

        # --- 產生不重複的手機號碼 ---
        retries = 0
        phone = generate_phone()
        while phone in used_phones:
            phone = generate_phone()
            retries += 1
            if retries > MAX_RETRIES:
                print(f"⚠️  手機號碼組合已接近上限，已成功產生 {generated} 筆（目標 {count} 筆）")
                return students
        used_phones.add(phone)

        # --- 其他欄位 ---
        birthday = generate_birthday()
        height = generate_height(sex)
        weight = generate_weight(height)
        addr = generate_address()

        students.append({
            "cName": name,
            "cSex": sex,
            "cBirthday": birthday.strftime("%Y-%m-%d"),
            "cEmail": email,
            "cPhone": phone,
            "cAddr": addr,
            "cHeight": height,
            "cWeight": weight,
        })

        generated += 1

    return students


def insert_students(students: list):
    """將學生資料批次寫入 MySQL"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    sql = """
        INSERT INTO students (cName, cSex, cBirthday, cEmail, cPhone, cAddr, cHeight, cWeight)
        VALUES (%(cName)s, %(cSex)s, %(cBirthday)s, %(cEmail)s, %(cPhone)s, %(cAddr)s, %(cHeight)s, %(cWeight)s)
    """

    try:
        cursor.executemany(sql, students)
        conn.commit()
        print(f"✅ 成功新增 {cursor.rowcount} 筆學生資料！")
    except mysql.connector.Error as err:
        conn.rollback()
        print(f"❌ 新增資料失敗：{err}")
    finally:
        cursor.close()
        conn.close()


def verify_result():
    """驗證寫入後的資料庫總筆數"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM students;")
        total = cursor.fetchone()[0]
        print(f"📊 資料庫目前共有 {total} 筆學生資料")
    except mysql.connector.Error as err:
        print(f"❌ 驗證失敗：{err}")
    finally:
        cursor.close()
        conn.close()


# ============================================================
# 主程式
# ============================================================

def parse_args():
    """解析命令列參數"""
    parser = argparse.ArgumentParser(
        description="學生假資料產生器（Faker 版）- 產生台灣風格的學生假資料並寫入 MySQL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例：
  python generate_students_faker.py              # 預設新增 100 筆
  python generate_students_faker.py -n 50        # 新增 50 筆
  python generate_students_faker.py --count 200  # 新增 200 筆
        """,
    )
    parser.add_argument(
        "-n", "--count",
        type=int,
        default=100,
        help="要新增的學生資料筆數（預設：100）",
    )
    return parser.parse_args()


def main():
    """主程式"""
    args = parse_args()
    count = args.count

    print("=" * 55)
    print(f"  學生假資料產生器 - Faker 版（本次新增 {count} 筆）")
    print("=" * 55)
    print()

    # Step 1: 從資料庫讀取已有資料，建立重複檢查集合
    print("【Step 1】讀取資料庫現有資料...\n")
    existing = load_existing_data()

    # Step 2: 使用 Faker 產生不重複的假資料
    print(f"【Step 2】使用 Faker 產生 {count} 筆不重複的假資料...\n")
    students = generate_students(count, existing)

    if not students:
        print("❌ 無法產生任何不重複的資料，請檢查 Faker 的組合數量是否足夠。")
        sys.exit(1)

    # 預覽前 5 筆
    preview_count = min(5, len(students))
    print(f"📋 預覽前 {preview_count} 筆資料：\n")
    print(f"{'姓名':<6} {'性別':<4} {'生日':<12} {'Email':<35} {'手機':<14} {'身高':<6} {'體重':<6}")
    print("-" * 95)
    for s in students[:preview_count]:
        print(f"{s['cName']:<6} {s['cSex']:<4} {s['cBirthday']:<12} "
              f"{s['cEmail']:<35} {s['cPhone']:<14} {s['cHeight']:<6} {s['cWeight']:<6}")
    if len(students) > preview_count:
        print(f"... 還有 {len(students) - preview_count} 筆\n")
    else:
        print()

    # 統計
    male_count = sum(1 for s in students if s["cSex"] == "M")
    female_count = sum(1 for s in students if s["cSex"] == "F")
    avg_height = sum(s["cHeight"] for s in students) / len(students)
    avg_weight = sum(s["cWeight"] for s in students) / len(students)
    print(f"📊 新增資料統計：男生 {male_count} 人、女生 {female_count} 人")
    print(f"   平均身高 {avg_height:.1f} cm、平均體重 {avg_weight:.1f} kg\n")

    # Step 3: 寫入資料庫
    print("【Step 3】寫入資料庫...\n")
    insert_students(students)

    # Step 4: 驗證結果
    print()
    verify_result()


if __name__ == "__main__":
    main()
