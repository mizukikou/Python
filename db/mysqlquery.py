import pymysql
# 修正 1：確保最後一項有指定 database='pythondb'
conn = pymysql.connect(host='localhost', port=6033, user='root', password='5745', charset='utf8mb4', database='pythondb')

with conn.cursor() as cursor:
    # 修正 2：將 scores 改為 students
    sql = "select * from students"
    cursor.execute(sql)
    datas = cursor.fetchall()        # 取出所有資料
    print(datas)
    print('-' * 30)                 # 分隔線
    
    # 修正 3：這裡同樣改為 students
    sql = "select * from students"
    cursor.execute(sql)
    data = cursor.fetchone()        # 取出第一筆資料
    print(data)

conn.close()
