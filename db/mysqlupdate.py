import pymysql
conn = pymysql.connect(host='localhost', port=6033, user='root', password='5745', charset='utf8mb4', database='pythondb')

with conn.cursor() as cursor:
    sql = "update scores set Chinese = 98 where ID = 4"
    cursor.execute(sql)
    conn.commit()

    sql = "select * from scores where ID = 4"
    cursor.execute(sql)
    data = cursor.fetchone()
    print(data)

    conn.close()