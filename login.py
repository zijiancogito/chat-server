from database import conn,cur
def login(userid):

    sqls = "select password from user where iduser=%s;"
    try:
        cur.execute(sqls,[userid])
        temp = cur.fetchall()
        return 1
    except:
        register(userid)
    return 0
