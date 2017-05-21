# coding: utf-8
import json, threading
from register import register
from login import login
from recv_message import recv_message
from send_message import send_message
from sendMsg import sendMsg
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
                sqlu = "update session set third_session = %s where openid = %s;"
                cur.execute(sqlu, [_3rd_session, openid])
                conn.commit()
            except:
                print "error"
        else:
            sqli = "insert into session(third_session,session_key,openid) values(%s,%s,%s);"
            cur.execute(sqli,[_3rd_session,session_key,openid])
            conn.commit()
            try:
                sqli = "insert into session(third_session,session_key,openid) values(%s,%s,%s);"
                cur.execute(sqli,[_3rd_session,session_key,openid])
                conn.commit()
            except:
                print "error"
    except:
        print "error"

def process_data(server, data, address):
    jdata = json.loads(data)
    state = jdata['state']
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
        reply = {'reply':_3rd_session}
        sjson = json.dumps(reply)
        sjson = token_data(server, sjson)
        t1 = threading.Thread(target=sendMsg, args=[server, sjson, address])
    elif state == 2:
        chatlog = send_message(jdata)
        log=[]
        for i in chatlog:
            contain = i[1]
            friendName = i[2]
            fromstr = 'recv'
            sendJson = {'text':contain,'from':fromstr,'friendName':friendName}
            send = json.dumps(sendJson)
            log.append(send)
        data = {'state':1, 'log':log}
        data = json.dumps(data)
        t1 = threading.Thread(target=sendMsg, args=[server, data, address])
    elif state == 3:
        recv_message(jdata)
    else:
        data_error()