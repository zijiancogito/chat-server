from database import conn,cur
def recv_message(messageJson):
    targetName = messageJson['targetName']
    message = messageJson['message']
    name = messageJson['name']
    if target not in connectionlist:
        sqli = "insert into chatlog values(%s,%s,%s);"
        cur.execute(sqli,(targetName,message,name))
    return 0
