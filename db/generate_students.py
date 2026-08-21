# -*- coding: utf-8 -*-
"""
產生學生假資料並寫入 MySQL 的 students 資料表。
根據現有資料的格式與風格，生成具有台灣風格的假資料。
新增資料前會檢查資料庫中已存在的 Email、手機、姓名，確保不會產生重複資料。

使用方式：
    python generate_students.py              # 預設新增 100 筆
    python generate_students.py -n 50        # 指定新增 50 筆
    python generate_students.py --count 200  # 指定新增 200 筆
"""

import sys
import io
import argparse

# 強制 stdout 使用 utf-8 編碼，避免 Windows cp950 問題
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import mysql.connector
import random
import string
from datetime import date, timedelta

# ============================================================
# 資料庫連線設定
# ============================================================
DB_CONFIG = {
    "host": "localhost",
    "port": 6033,
    "user": "root",
    "password": "5745",
    "database": "pythondb",
    "charset": "utf8mb4",
}

# ============================================================
# 假資料素材（台灣風格）
# ============================================================

# 常見中文姓氏
LAST_NAMES = [
    "陳", "林", "黃", "張", "李", "王", "吳", "劉", "蔡", "楊",
    "許", "鄭", "謝", "洪", "郭", "邱", "曾", "廖", "賴", "徐",
    "周", "葉", "蘇", "莊", "江", "呂", "何", "羅", "高", "蕭",
    "潘", "朱", "簡", "鍾", "彭", "游", "詹", "胡", "施", "沈",
    "余", "趙", "盧", "梁", "顏", "柯", "孫", "魏", "翁", "戴",
]

# 常見中文名字用字（男性偏好）
MALE_NAME_CHARS = [
    "志", "明", "建", "國", "文", "偉", "宏", "俊", "傑", "信",
    "廷", "翰", "銘", "哲", "瑋", "智", "宇", "承", "恩", "軒",
    "博", "勝", "賢", "德", "豪", "仁", "嘉", "裕", "維", "政",
    "聖", "穎", "霖", "鴻", "佑", "宸", "睿", "皓", "煜", "楷",
]

# 常見中文名字用字（女性偏好）
FEMALE_NAME_CHARS = [
    "怡", "雅", "婷", "惠", "玲", "淑", "芳", "美", "嘉", "佳",
    "欣", "宜", "蓉", "珊", "筠", "琪", "萱", "涵", "詩", "庭",
    "儀", "潔", "柔", "妍", "彤", "心", "靜", "慧", "瑩", "君",
    "雯", "媗", "螢", "楚", "寧", "晴", "瑜", "琳", "薇", "羽",
]

# 台北市常見路名
ROADS = [
    "忠孝東路", "忠孝西路", "仁愛路", "信義路", "和平東路", "和平西路",
    "敦化南路", "敦化北路", "復興南路", "復興北路", "建國南路", "建國北路",
    "中山北路", "中山南路", "民生東路", "民生西路", "民權東路", "民權西路",
    "南京東路", "南京西路", "八德路", "延吉街", "光復南路", "光復北路",
    "松江路", "新生南路", "新生北路", "羅斯福路", "長安東路", "長安西路",
    "市民大道", "基隆路", "辛亥路", "永康街", "濟南路", "重慶南路",
    "三民路", "民族路", "中正路", "中華路", "北環路", "中央路",
]

# 縣市區域
CITIES = [
    "台北市", "新北市", "桃園市", "台中市", "台南市", "高雄市",
    "基隆市", "新竹市", "嘉義市",
]

# 英文名字（用於 email）
ENGLISH_NAMES_MALE = [
    "james", "john", "robert", "michael", "david", "william", "richard",
    "joseph", "thomas", "charles", "daniel", "matthew", "anthony", "mark",
    "steven", "paul", "andrew", "kevin", "brian", "george", "edward",
    "jason", "ryan", "jacob", "gary", "nicholas", "eric", "jonathan",
    "stephen", "larry", "justin", "scott", "brandon", "benjamin", "samuel",
    "raymond", "henry", "jack", "dennis", "peter", "alex", "patrick",
    "frank", "sean", "aaron", "vincent", "martin", "bruce", "alan", "tyler",
]

ENGLISH_NAMES_FEMALE = [
    "mary", "patricia", "jennifer", "linda", "barbara", "elizabeth",
    "susan", "jessica", "sarah", "karen", "lisa", "nancy", "betty",
    "margaret", "sandra", "ashley", "emily", "donna", "michelle", "carol",
    "amanda", "melissa", "deborah", "stephanie", "rebecca", "sharon",
    "laura", "cynthia", "kathleen", "amy", "angela", "shirley", "anna",
    "brenda", "pamela", "emma", "nicole", "helen", "samantha", "katherine",
    "christine", "debra", "rachel", "carolyn", "janet", "catherine",
    "maria", "heather", "diane", "ruth", "julie", "olivia", "joyce",
    "virginia", "victoria", "kelly", "lauren", "christina", "joan", "evelyn",
]

# Email 域名
EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com.tw", "hotmail.com", "outlook.com",
    "mail.com", "student.edu.tw", "campus.tw", "mymail.com",
]

# 每筆資料產生的最大重試次數，避免無窮迴圈
MAX_RETRIES = 1000


# ============================================================
# 資料產生函式
# ============================================================

def generate_chinese_name(sex: str) -> str:
    """產生一個隨機中文姓名"""
    last_name = random.choice(LAST_NAMES)
    name_chars = MALE_NAME_CHARS if sex == "M" else FEMALE_NAME_CHARS
    # 名字 1~2 個字
    name_len = random.choice([1, 2, 2, 2])  # 2 個字的機率較高
    first_name = "".join(random.sample(name_chars, name_len))
    return last_name + first_name


def generate_birthday() -> date:
    """產生 1984~1995 年間的隨機生日"""
    start_date = date(1984, 1, 1)
    end_date = date(1995, 12, 31)
    delta = (end_date - start_date).days
    random_days = random.randint(0, delta)
    return start_date + timedelta(days=random_days)


def generate_email(sex: str) -> str:
    """產生一個隨機 email"""
    names = ENGLISH_NAMES_MALE if sex == "M" else ENGLISH_NAMES_FEMALE
    name = random.choice(names)
    # 有機率加上數字後綴
    suffix = ""
    if random.random() > 0.4:
        suffix = str(random.randint(1, 999))
    domain = random.choice(EMAIL_DOMAINS)
    return f"{name}{suffix}@{domain}"


def generate_phone() -> str:
    """產生台灣手機號碼格式（09XXXXXXXX）"""
    prefixes = ["0910", "0911", "0912", "0916", "0918", "0920",
                "0921", "0922", "0928", "0930", "0932", "0935",
                "0937", "0938", "0939", "0952", "0955", "0956",
                "0958", "0960", "0963", "0965", "0968", "0970",
                "0972", "0975", "0978", "0905", "0906", "0907"]
    prefix = random.choice(prefixes)
    remaining = "".join([str(random.randint(0, 9)) for _ in range(6)])
    return prefix + remaining


def generate_address() -> str:
    """產生隨機台灣地址"""
    city = random.choice(CITIES)
    road = random.choice(ROADS)
    number = random.randint(1, 500)

    # 隨機決定是否加上巷弄、樓層
    addr = f"{city}{road}{number}號"
    if random.random() > 0.7:
        lane = random.randint(1, 30)
        addr = f"{city}{road}{lane}巷{number}號"
    if random.random() > 0.6:
        floor = random.randint(2, 15)
        addr += f"{floor}樓"

    return addr


def generate_height(sex: str) -> int:
    """產生合理的身高（公分）"""
    if sex == "M":
        return random.randint(165, 185)
    else:
        return random.randint(150, 170)


def generate_weight(sex: str, height: int) -> int:
    """根據身高產生合理的體重（公斤）"""
    # BMI 18.5 ~ 27 的合理範圍
    bmi = random.uniform(18.5, 27.0)
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
    產生指定數量的學生假資料，確保與資料庫已有資料不重複。

    重複檢查欄位：
    - cName（姓名）：不可與已有姓名重複
    - cEmail（Email）：不可與已有 Email 重複
    - cPhone（手機）：不可與已有手機重複
    """
    students = []

    # 複製一份，在生成過程中同步更新，避免新資料之間也重複
    used_names = set(existing["names"])
    used_emails = set(existing["emails"])
    used_phones = set(existing["phones"])

    generated = 0
    total_retries = 0

    while generated < count:
        retries = 0
        sex = random.choice(["M", "F"])

        # --- 產生不重複的姓名 ---
        name = generate_chinese_name(sex)
        while name in used_names:
            name = generate_chinese_name(sex)
            retries += 1
            if retries > MAX_RETRIES:
                print(f"⚠️  姓名組合已接近上限，已成功產生 {generated} 筆（目標 {count} 筆）")
                return students
        used_names.add(name)

        # --- 產生不重複的 Email ---
        retries = 0
        email = generate_email(sex)
        while email.lower() in used_emails:
            email = generate_email(sex)
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

        # --- 其他欄位（不需要唯一性檢查）---
        birthday = generate_birthday()
        height = generate_height(sex)
        weight = generate_weight(sex, height)
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
    """將學生資料寫入 MySQL"""
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
        description="學生假資料產生器 - 產生台灣風格的學生假資料並寫入 MySQL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例：
  python generate_students.py              # 預設新增 100 筆
  python generate_students.py -n 50        # 新增 50 筆
  python generate_students.py --count 200  # 新增 200 筆
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
    print(f"  學生假資料產生器（本次新增 {count} 筆）")
    print("=" * 55)
    print()

    # Step 1: 從資料庫讀取已有資料，建立重複檢查集合
    print("【Step 1】讀取資料庫現有資料...\n")
    existing = load_existing_data()

    # Step 2: 產生不重複的假資料
    print(f"【Step 2】產生 {count} 筆不重複的假資料...\n")
    students = generate_students(count, existing)

    if not students:
        print("❌ 無法產生任何不重複的資料，請檢查資料素材的組合數量是否足夠。")
        sys.exit(1)

    # 預覽前 5 筆
    preview_count = min(5, len(students))
    print(f"📋 預覽前 {preview_count} 筆資料：\n")
    print(f"{'姓名':<6} {'性別':<4} {'生日':<12} {'Email':<30} {'手機':<14} {'身高':<6} {'體重':<6}")
    print("-" * 90)
    for s in students[:preview_count]:
        print(f"{s['cName']:<6} {s['cSex']:<4} {s['cBirthday']:<12} "
              f"{s['cEmail']:<30} {s['cPhone']:<14} {s['cHeight']:<6} {s['cWeight']:<6}")
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
    print(f"【Step 3】寫入資料庫...\n")
    insert_students(students)

    # Step 4: 驗證結果
    print()
    verify_result()


if __name__ == "__main__":
    main()
