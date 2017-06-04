from database import conn,cur
def send_message(messageJson):
    third = messageJson['trd']
    seq = messageJson['seq']
    sqli = "select openid,sequence from session where third_session=%s;"
    sql="select sendtime,content,sessionid from log natural join userid where openid=%s;"
    sqld="delete from log where openid=%s;"
    try:
        cur.execute(sqli,[third])
        temp = cur.fetchall()
        if temp:
            openid=temp[0][0]
            seqs=temp[0][1]
            if seq!=seqs:
                print seq," ",seqs
                return [],0
            else:
                seq=seq+1
                seqs=seqs+2
                sqls="update session set sequence=%s where third_session=%s"
                cur.execute(sqls,[seqs,third])
                conn.commit() 
            cur.execute(sql,[openid])
            log=cur.fetchall()
            cur.execute(sqld,[openid])
            conn.commit()
            if log:
            	return log,seq
            else:
                return [],seq
        else:
            print "no user"
            return [],0
    except:
            print "sql error"
            return [],0

