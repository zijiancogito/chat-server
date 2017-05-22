from database import conn,cur
def send_message(messageJson):
    third = messageJson['myName']
    sqli = "select openid from session where third_session=%s;"
    sql="select id,sendtime,content from log natural join userid where openid=%s;"
    sqld="delete from log where openid=%s;"
    try:
        cur.execute(sqli,[third])
        temp = cur.fetchall()
        if temp:
            openid=temp[0][0]
            cur.execute(sql,[openid])
            log=cur.fetchall()
            cur.execute(sqld,[openid])
            conn.commit()
            return log
        else:
            return
    except:
        return

