import pymysql

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='rown-roastery',
        cursorclass=pymysql.cursors.DictCursor
    )
