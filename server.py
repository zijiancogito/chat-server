# coding: utf-8

from socket import *
import json, time, threading

from config import config
from readMsg import readMsg

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
            address = addr[0]# + ':' + str(addr[1])  # ip:port

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
            self.thrs[address] = threading.Thread(target=readMsg, args=[self,address])
            self.thrs[address].start()

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
