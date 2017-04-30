# coding: utf-8
from socket import *
import threading

from process import process_data
from config import config
def readMsg(server, address):
    if address not in server.clients:
        return False

    client = server.clients[address]

    import select
    time_out = 0
    while 1:
        if address in server.stops:
            server.close_client(address)
            print(address + 'logout')
            break

        # 检测超时
        if time_out >= config['TIME_OUT']:
            server.close_client(address)
            break

        time_out += 5

        infds, outfds, errfds = select.select([client, ], [], [], 5)
        if len(infds) == 0:
            continue

        time_out = 0
        try:
            info = client.recv(1024)
        except:
            server.close_client(address)
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

        # 开启线程记录
        if raw_str:
            print(raw_str)
            t1 = threading.Thread(target=process_data, args=[server,raw_str, address])
            t1.start()
