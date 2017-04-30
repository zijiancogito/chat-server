from database import conn,cur
def register(registerJson):
    username = registerJson['name']
    password = registerJson['psw']
    phonenum = registerJson['phone']
    sqli = "insert into user(username,password,phonenum) values(%s,%s,%s);"
    try:
        cur.execute(sqli,(username,password,phonenum))
        conn.commit()
        return 1
    except:
        return 0
