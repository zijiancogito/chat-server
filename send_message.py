from database import conn,cur
def send_message(messageJson):
    third = messageJson['third']
    
    #print(friendName)
    sqli = "select * from chatlog where targetName=%s;"
    #sqld = "delete from chatlog where targetName=%s and scrName=%s"
    try:
        cur.execute(sqli,[name])
        chatlog = cur.fetchall()
        print(chatlog)
        #cur.execute(sqld,(name,friendName))
        return chatlog
    except:
        return []
