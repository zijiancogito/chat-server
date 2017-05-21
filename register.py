from database import conn,cur
def register(userid):
    sqli = "insert into user(iduser) values(%s);"
    try:
        cur.execute(sqli,(userid))
        conn.commit()
        return 1
    except:
        return 0
