import pymysql
conn = pymysql.connect(host='localhost', port=6033, user='root', password='1qaz@wsx', 
charset='utf8mb4', database='pythondb') # 連結資料庫

with conn.cursor() as cursor:
    sql = """
    insert into scores (Name, Chinese, English, Math) values
    ('李大毛',95,92,80),
    ('林小明',82,83,61),
    ('黃小英',74,53,71),
    ('劉大樹',86,87,89),
    ('何美麗',89,73,95)
    """
    cursor.execute(sql)
    conn.commit()      # 提交資料庫

    conn.close()