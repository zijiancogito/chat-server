import mysql.connector
conn= mysql.connector.connect(
        host='localhost',
        port = 3306,
        user='root',
        passwd='19960209',
        db ='chat',
        )
cur = conn.cursor()