from database import conn,cur
from const import connectionlist
def recv_message(messageJson):
    target = messageJson['target']
    message = messageJson['message']
    name = messageJson['name']
    import time
    sendtime = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
    sql="select id from session natural join userid where third_session = %s"
    sqls="select openid,third_session from userid natural join session where id = %s"
    try:
        cur.execute(sql,[name])
        temp=cur.fetchall()
        cur.execute(sqls,[target])
        temp1=cur.fetchall()
        if  temp and temp1:
            src=temp[0][0]
            des=temp1[0][0]
            return des,sendtime,message,src,trd
        else:
            pass
    except:
        print "sql error"
    return

def offline(des,sendtime,message,src):
    sqli = "insert into log(openid,sendtime,content,sendid) values(%s,%s,%s,%s);"
    cur.execute(sqli,(des,sendtime,message,src))
    conn.commit()


