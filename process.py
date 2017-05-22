# coding: utf-8
import json, threading
from register import register
from login import login
from recv_message import recv_message,offline
from send_message import send_message
from error import data_error
from const import connectionlist
from database import conn,cur
from WXBizDataCrypt import WXBizDataCrypt

def decrypt(encryptedData, iv, session_key):
    appId = 'wx2bd3ca4f04e83411'

    pc = WXBizDataCrypt(appId, session_key)

    print pc.decryptData(encryptedData, iv)

def token_data(server, sjson):
    import struct
    from urllib import unquote
    try:
        username = unquote(server.users[address])
    except:
        username = 'anonymity user'
    token = "\x81"
    length = len(sjson)
    if length < 126:
        token += struct.pack("B", length)
    elif length <= 0xFFFF:
        token += struct.pack("!BH", 126, length)
    else:
        token += struct.pack("!BQ", 127, length)
    sjson = '%s%s' % (token, sjson)
    return sjson

def get_session(code):
    import urllib
    appid = "wx2bd3ca4f04e83411"
    secret = "e267808c0e7f6e89b3d51cecc9799216"
    url = "https://api.weixin.qq.com/sns/jscode2session?appid="+appid+"&secret="+secret+"&js_code="+code+"&grant_type=authorization_code"
    page = urllib.urlopen(url)
    html = page.read()
    data = json.loads(html)
    return data

def save_session(_3rd_session, session_key, openid):
    try:
        sql = "select openid from session where openid=%s;"
        cur.execute(sql, [openid])
        temp = cur.fetchall()
        if len(temp):
            try:
                sqlu = "update session set third_session = %s,sequence=0 where openid = %s;"
                cur.execute(sqlu, [_3rd_session, openid])
                conn.commit()
            except:
                print "error"
        else:
            try:
                sqli = "insert into session(third_session,session_key,openid,sequence) values(%s,%s,%s,0);"
                cur.execute(sqli,[_3rd_session,session_key,openid])
                conn.commit()
            except:
                print "error"
    except:
        print "error"

def getpubkey():
    keyfile=open("PublicKey.pem","r")
    text=keyfile.readlines()
    pubkey=""
    for line in text[1:len(text)-1]:
        pubkey=pubkey+line[0:len(line)-1]
    return pubkey

from Crypto.PublicKey import RSA
def decrypt(ciphertext):
    externKey="PrivateKey.pem"
    publickey = open(externKey, "r")
    decryptor = RSA.importKey(publickey, passphrase="f00bar")
    retval=None
    retval = decryptor.decrypt(ciphertext)
    return retval

def process_data(server, data, address):
    jdata = json.loads(data)
    state = jdata['state']
    jmsg = None
    if state != 1:
        text = jdata['text']
        message = decrypt(text)
        jmsg = json.loads(message)
    if state == 1:
        code = jdata['code']
        data = get_session(code)
        session_key = data['session_key']
        openid = data['openid']
        from os import urandom
        import binhex
        import binascii
        _3rd_session = binascii.hexlify(urandom(16)).decode()
        save_session(_3rd_session, session_key, openid)
        pubkey=getpubkey()
        reply = {'reply':_3rd_session,'pubkey':pubkey}
        sjson = json.dumps(reply)
        sjson = token_data(server, sjson)
        connectionlist[_3rd_session]=address
        try:
            client = server.clients[address]
            try:
                client.send(sjson)
            except:
                server.close_client(address)
        except:
            pass
    elif state == 2:
        chatlog = send_message(jmsg)
        log=[]
        if chatlog:
            for i in chatlog:
                fromstr = 'recv'
                sendJson = {'text':i[2],'from':i[0],'time':i[1]}
                send = json.dumps(sendJson)
                log.append(send)
        data = {'state':1, 'log':log}
        data = json.dumps(data)
        sjson = token_data(server, data)
        try:
            client = server.clients[address]
            try:
                client.send(sjson)
            except:
                server.close_client(address)
        except:
            pass
    elif state == 3:
        data=recv_message(jdata)
        if data:
            des=data[0]
            sendtime=data[1]
            message=data[2]
            src=data[3]
            trd=data[4]
            if trd not in connectionlist:
                offline(des,sendtime,message,src)
            else:
                sendJson={'state':3,'text':message,'from':src,'time':sendtime}
                send=json.dumps(sendJson)
                sjson=token_data(server,send)
                address=connectionlist[trd]
                try:
                    client = server.clients[address]
                    try:
                        client.send(sjson)
                    except:
                        server.close_client(address)
                except:
                    pass
        else:
            pass
    else:
        data_error()