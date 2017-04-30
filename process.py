# coding: utf-8
import json, threading
from register import register
from login import login
from recv_message import recv_message
from send_message import send_message
from sendMsg import sendMsg
from connectionlist import connectionlist

from WXBizDataCrypt import WXBizDataCrypt

def decrypt(encryptedData, iv):
    appId = 'wx2bd3ca4f04e83411'
    sessionKey = 'tiihtNczf5v6AKRyjwEUhQ=='

    pc = WXBizDataCrypt(appId, sessionKey)

    print pc.decryptData(encryptedData, iv)

def token_data(server, sjson):
    import struct
    from urllib import unquote
    try:
        username = unquote(server.users[address])
    except:
        username = 'anonymity user'
    token = "\x81"
    # struct为Python中处理二进制数的模块，二进制流为C，或网络流的形式。
    length = len(sjson)
    if length < 126:
        token += struct.pack("B", length)
    elif length <= 0xFFFF:
        token += struct.pack("!BH", 126, length)
    else:
        token += struct.pack("!BQ", 127, length)
    #print(type(sjson))
    sjson = '%s%s' % (token, sjson)
    return sjson
def process_data(server, data, address):
    jdata = json.loads(data)
    state = jdata['state']
    if state == 1:
        encryptedData = jdata['encInfo']
        iv = jdata['iv']
        decrypt(encryptedDatass, iv)
        #username = jdata['name']
        flag=0
        if flag:
            res = "success"
            #connectionlist[username]=address
        else:
            res = "fail"
        reply = {'res':res}
        sjson = json.dumps(reply)

        sjson = token_data(server,sjson)
        t1 = threading.Thread(target=sendMsg, args=[server, sjson, address])
        t1.start()
    # """
    # elif state == 1:
    #     flag = login(jdata)
    #     username = jdata['acc']
    #     if flag:
    #         res = "success"
    #         connectionlist[username]=address
    #     else:
    #         res="fail"
    #     reply = {'reply':res}
    #     sjson = json.dumps(reply)
    #     sjson = token_data(server,sjson)
    #     #print res
    #     t1 = threading.Thread(target=sendMsg, args=[server, sjson, address])
    #     t1.start()
    # """
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
