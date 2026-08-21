import pymysql
conn = pymysql.connect(host='localhost', port=6033, user='root', password='5745', charset='utf8mb4', database='mcp')   # 連結資料庫


with conn.cursor() as cursor:
    sql = """
    CREATE TABLE IF NOT EXISTS scores (
        ID int NOT NULL AUTO_INCREMENT PRIMARY KEY,
        Name varchar(20),
        Chinese int(3),
        English int(3),
        Math int(3)
    );
    """
    cursor.execute(sql)      # 執行 SQL 指令
    conn.commit()            # 提交資料庫

    conn.close()