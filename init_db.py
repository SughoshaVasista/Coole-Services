import pymysql

try:
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='sughosha',
        password='sughosha_12'
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS coole_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print("Database coole_db initialized successfully.")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error connecting to MySQL: {str(e)}")
