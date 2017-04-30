# coding: utf-8

from socket import *
import json, time, threading
from process import ProcessData
from config import config
from database import conn,cur
from array import *
connectionlist={}

def recv_message(messageJson):
    targetName = messageJson['targetName']
    message = messageJson['message']
    name = messageJson['name']
    if target not in connectionlist:
        sqli = "insert into chatlog values(%s,%s,%s);"
        cur.execute(sqli,(targetName,message,name))
    return 0
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
def register(registerJson):
    username = registerJson['name']
    password = registerJson['psw']
    phonenum = registerJson['phone']
    sqli = "insert into user(username,password,phonenum) values(%s,%s,%s);"
    try:
        cur.execute(sqli,(username,password,phonenum))
        conn.commit()
        connectionlist.append(username)
        return 1
    except:
        return 0
    return 0
def send_message(messageJson):
    name = messageJson['myName']
    #friendName = messageJson['friendName']
    print(name)
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
def data_error():
    return 0
class Server():
    def __init__(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((config['HOST'], config['PORT']))  # 监听端口
        self.sock.listen(config['LISTEN_CLIENT'])  # 监听客户端数量
        print("start!!!")
        # 所有监听的客户端
        self.clients = {}
        self.thrs = {}
        self.users = {}
        self.stops = []

    # 监听客户端连接
    def listen_client(self):
        while 1:
            # 循环监听
            tcpClientSock, addr = self.sock.accept()
            address = addr[0] # + ':' + str(addr[1])  # ip:port

            # 握手
            topInfo = tcpClientSock.recv(1024)
            headers = {}
            if not topInfo:
                tcpClientSock.close()
                continue

            header, data = topInfo.split('\r\n\r\n', 1)

            try:
                getInfo = header.split('\r\n')[0].split(' ')[1].split('/')[1:]
                if getInfo[0] == 'name':
                    self.users[address] = str(getInfo[1])
                else:
                    self.users[address] = 'anonymity user'
            except:
                self.users[address] = 'anonymity user'


            for line in header.split('\r\n')[1:]:
                key, val = line.split(': ', 1)
                headers[key] = val

            if 'Sec-WebSocket-Key' not in headers:
                tcpClientSock.close()
                continue

            import hashlib, base64
            sec_key = headers['Sec-WebSocket-Key']
            res_key = base64.b64encode(hashlib.sha1(sec_key + config['MAGIC_STRING']).digest())

            str_handshake = config['HANDSHAKE_STRING'].replace('{1}', res_key).replace('{2}', config['HOST'] + ':' + str(config['PORT']))
            tcpClientSock.send(str_handshake)

            # 握手成功 分配线程进行监听
            print(address+'login')

            self.clients[address] = tcpClientSock
            self.thrs[address] = threading.Thread(target=self.readMsg, args=[address])
            self.thrs[address].start()

    def readMsg(self, address):
        if address not in self.clients:
            return False

        client = self.clients[address]

        import select
        time_out = 0
        while 1:
            if address in self.stops:
                self.close_client(address)
                print(address + 'logout')
                break

            # 检测超时
            if time_out >= config['TIME_OUT']:
                self.close_client(address)
                break

            time_out += 5

            infds, outfds, errfds = select.select([client, ], [], [], 5)
            if len(infds) == 0:
                continue

            time_out = 0
            try:
                info = client.recv(1024)
            except:
                self.close_client(address)
                break
            if not info:
                continue

            #if info == 'quit':
            #    self.close_client(address)
            #    break
            code_len = ord(info[1]) & 127
            if code_len == 126:
                masks = info[4:8]
                data = info[8:]
            elif code_len == 127:
                masks = info[10:14]
                data = info[14:]
            else:
                masks = info[2:6]
                data = info[6:]
            i = 0
            raw_str = ""
            for d in data:
                raw_str += chr(ord(d) ^ ord(masks[i % 4]))
                i += 1

            # 获取到输入的数据 向所有的客户端发送
            # 开启线程记录
            if raw_str:
                print(raw_str)
                t1 = threading.Thread(target=self.process_data, args=[raw_str, address])
                t1.start()
    def process_data(self, data, address):
        import json
        jdata = json.loads(data)
        state = jdata['state']
        if state == 0:
            flag = register(jdata)
            if flag:
                res = "success"
            else:
                res = "fail"
            #print res
            t1 = threading.Thread(target=self.register_data, args=[res, address])
            t1.start()
        elif state == 1:
            username = jdata['acc']
            flag = login(jdata)
            if flag:
                res = "success"
                connectionlist[username]=address
            else:
                res="fail"
            #print res
            t1 = threading.Thread(target=self.login_data, args=[res, address])
            t1.start()

        elif state == 2:
            print(jdata)
            chatlog = send_message(jdata)
            state = 1
            log=[]
            for i in chatlog:
                contain = i[1]
                friendName = i[2]
                fromstr = 'recv'
                cur_thread = threading.current_thread()
                sendJson = [{'text':contain,'from':fromstr,'friendName':friendName}]
                send = json.dumps(sendJson)
                self.request.sendall(send)
                rec_cmd = "proccess "+rec_src+" -o "+rec_dst
                print "CMD '%r'" % (rec_cmd)
                os.system(rec_cmd)
        elif state == 3:
            recv_message(jdata)
        else:
            data_error()

    def login_data(self, data, address):
        import struct
        from urllib import unquote
        try:
            username = unquote(self.users[address])
        except:
            username = 'anonymity user'
        token = "\x81"


        # struct为Python中处理二进制数的模块，二进制流为C，或网络流的形式。
        reply = {'reply':data}
        sjson = json.dumps(reply)
        length = len(sjson)
        if length < 126:
            token += struct.pack("B", length)
        elif length <= 0xFFFF:
            token += struct.pack("!BH", 126, length)
        else:
            token += struct.pack("!BQ", 127, length)
        #print(type(sjson))
        sjson = '%s%s' % (token, sjson)
        #print sjson
        try:
            #for key, val in self.clients.iteritems():
            #    print("key="),
            #    print(key)
            #    client = val
            client = self.clients[address]
            try:
                client.send(sjson)
            except:
                self.close_client(key)
        except:
            pass
    def register_data(self, data, address):
        import struct
        from urllib import unquote
        try:
            username = unquote(self.users[address])
        except:
            username = 'anonymity user'
        token = "\x81"


        # struct为Python中处理二进制数的模块，二进制流为C，或网络流的形式。
        reply = {'res':data}
        sjson = json.dumps(reply)
        length = len(sjson)
        if length < 126:
            token += struct.pack("B", length)
        elif length <= 0xFFFF:
            token += struct.pack("!BH", 126, length)
        else:
            token += struct.pack("!BQ", 127, length)
        #print(type(sjson))
        sjson = '%s%s' % (token, sjson)
        #print sjson
        try:
            #for key, val in self.clients.iteritems():
            client = self.clients[address]
            try:
                client.send(sjson)
            except:
                self.close_client(address)
        except:
            pass

    def close_client(self, address):
        try:
            client = self.clients.pop(address)
            self.stops.append(address)
            client.close()
            del self.users[address]
        except:
            pass

        print(address+u'logout')

if __name__ == '__main__':
    c = Server()
    c.listen_client()
