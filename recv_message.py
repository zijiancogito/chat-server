from database import conn,cur
from const import connectionlist
def recv_message(messageJson):
    target = messageJson['friendID']
    message = messageJson['messageEnc']
    sessionid=messageJson['sessionid']
    import time
    sendtime = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
    #sql="select id from session natural join userid where third_session = %s"
    sqls="select openid,third_session from userid natural join session where id = %s"
    try:
        #cur.execute(sql,[name])
        #temp=cur.fetchall()
        cur.execute(sqls,[target])
        temp1=cur.fetchall()
        if temp1:
            des=temp1[0][0]
            trd=temp1[0][1]
            return des,sendtime,message,trd,sessionid
        else:
            pass
    except:
        print "sql error"
    return

def offline(des,sendtime,message,src,sessionid):
    sqli = "insert into log(openid,sendtime,content,sessionid) values(%s,%s,%s);"
    cur.execute(sqli,[des,sendtime,message,sessionid])
    conn.commit()


