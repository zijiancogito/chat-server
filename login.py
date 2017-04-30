from database import conn,cur
def login(loginJson):
    username = loginJson['acc']
    #print(username)
    password = loginJson['psw']
    sqli = "select password from user where username=%s;"
    try:
        cur.execute(sqli,[username])
        temp = cur.fetchall()
        #print(temp)
        psw = temp[0][0]
        if psw == password:
            #connectionlist.append(username)
            return 1
        else:
            return 0
    except:
        return 0
    return 0
