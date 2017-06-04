import MySQLdb
conn= MySQLdb.connect(
        host='10.66.230.56',
        port = 3306,
        user='root',
        passwd='caoying123',
        db ='test',
        )
cur = conn.cursor()
