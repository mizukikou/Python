import pymysql
conn = pymysql.connect(host='localhost', port=6033, user='root', password='1qaz@wsx', 
charset='utf8mb4', database='pythondb') # 連結資料庫
 
with conn.cursor() as cursor:
    sql = "delete from scores where ID = 4"
    cursor.execute(sql)
    conn.commit()
 
    sql = "select * from scores"
    cursor.execute(sql)
    data = cursor.fetchall()
    print(data)

    conn.close()