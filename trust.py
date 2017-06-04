from database import cur,conn
def getuserid(trd):
    sql="select id from session natural join userid where third_session=%s"
    try:
        cur.execute(sql,[trd])
        temp=cur.fetchall()
        userid=temp[0][0]
        return userid
    except:
        pass
    return 

def saveInvite(inviteCode,trd,userid):
    sql="insert into invite values(%s,%s,%s)"
    try:
        cur.execute(sql,[inviteCode,trd,userid])
        conn.commit()
    except:
        pass
    return

def searchInvite(inviteCode):
    sql="select trd,userid from invite where inviteCode=%s"
    try:
        cur.execute(sql,[inviteCode])
        temp=cur.fetchall()
        return temp[0][0],temp[0][1]
    except:
        pass
    return None,None

def deleteInvite(inviteCode):
    sql="delete from invite where inviteCode=%s"
    try:
        cur.execute(sql,[inviteCode])
        conn.commit()
    except:
        pass
    return
