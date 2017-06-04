# coding: utf-8
import json, threading
from register import register
from login import login
from recv_message import recv_message,offline
from send_message import send_message
from error import data_error
from const import connectionlist,templist
from database import conn,cur
from WXBizDataCrypt import WXBizDataCrypt
from trust import getuserid,saveInvite,searchInvite,deleteInvite
from sendMsg import sendMsg
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
    if not data:
        print "invalid code"
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
            try:
                sqli = "insert into session(third_session,session_key,openid,sequence) values(%s,%s,%s,0);"
                sql1="insert into userid(openid,id) values(%s,%s);"
                import hashlib
                userid=hashlib.sha256()
                userid.update(openid)
                temp=userid.hexdigest()
                cur.execute(sqli,[_3rd_session,session_key,openid])
                conn.commit()
                cur.execute(sql1,[openid,temp])
                conn.commit()
                return temp 
            except:
                print "error"
    except:
        print "error"
    return 

def getpubkey():
    f=open("key.pem","rb")
    key=""
    for byte in f.read():
        hexstr="%s" % byte.encode('hex')
        #print hexstr
        key=key+hexstr
    f.close()
    n=key[64:578]
    e=key[582:]
    pubkey=n+"|"+e
    return pubkey

from Crypto.PublicKey import RSA
from binascii import a2b_hex,b2a_hex
def pubdecrypt(ciphertext):
    externKey="PrivateKey.pem"
    privatekey = open(externKey, "r")
    decryptor = RSA.importKey(privatekey, passphrase="f00bar")
    retval=None
    retval = decryptor.decrypt(ciphertext)
    temp=retval[158:222]
    temp2=retval[223:]
    key = a2b_hex(temp)
    iv=a2b_hex(temp2)
    return key,iv
from Crypto.Cipher import AES
def datadecrypt(ciphertext,key,iv):
    cryptor = AES.new(key,AES.MODE_CBC,iv)
    plain_text = cryptor.decrypt(a2b_hex(ciphertext))
    pos = plain_text.rindex('}')
    return plain_text[:pos+1]
def dataencrypt(message,key,iv):
    crypto = AES.new(key,AES.MODE_CBC,iv)
    length=16
    count=len(message)
    add=length-(count % length)
    message=message+('\0'*add)
    cipher=crypto.encrypt(message)
    import base64
    text=base64.b64encode(cipher)
    return text
def process_data(server, data, address):
    print "raw_data: ",data
    state=-1
    try:
	jdata = json.loads(data)
    	state = jdata['state']
    except:
	pass
    jmsg = None
    if state > 1:
        text = jdata['aeskeyEnc']
        text2 = jdata['aesEncText']
        import base64
        text1=base64.b64decode(text)
        key,iv = pubdecrypt(text1)
        msg = datadecrypt(text2,key,iv)
        jmsg = json.loads(msg)
        #print "decrypt data:" , jmsg
    if state == 1:
        code = jdata['code']
        data = get_session(code)
        if data:  
            session_key = data['session_key']
            openid = data['openid']
            from os import urandom
            import binhex
            import binascii
            _3rd_session = binascii.hexlify(urandom(16)).decode()
            userid=save_session(_3rd_session, session_key, openid)
            print userid
            pubkey=getpubkey()
            reply = {'reply':_3rd_session,'pubkey':pubkey,'id':userid}
            sjson = json.dumps(reply)
            sjson = token_data(server, sjson)
            connectionlist[_3rd_session]=address
            t1 = threading.Thread(target=sendMsg, args=[server,sjson, address])
            t1.start()
    elif state == 2:
        chatlog,seq = send_message(jmsg)
        log=[]
        if chatlog:
            for i in chatlog:
                fromstr = 'recv'
                sendJson = {'text':i[1],'time':i[0],'sessionid':i[2]}
                send = json.dumps(sendJson)
                log.append(send)
        #plain ={'seq':seq,'log':log}
        data ={'state':1, 'log':log, 'seq':seq}
        data = json.dumps(data)
        sjson = token_data(server, data)
        t1 = threading.Thread(target=sendMsg, args=[server,sjson, address])
        t1.start()
    elif state == 3:
        print jmsg
        print connectionlist
        data=recv_message(jmsg)
        if data:
            des=data[0]
            sendtime=data[1]
            message=data[2]
            trd=data[3]
            sessionid=data[4]
            if trd not in connectionlist:
                offline(des,sendtime,message,sessionid)
            else:
                sendJson={'state':3,'text':message,'time':sendtime,'sessionid':sessionid}
                send=json.dumps(sendJson)
                sjson=token_data(server,send)
                addr=connectionlist[trd]
                t1 = threading.Thread(target=sendMsg, args=[server,sjson,addr])
                t1.start()
        else:
            pass
    elif state==4:
        tempid=jmsg['inviteCode']
        trd=jmsg['trd']
        userid=getuserid(trd)
        saveInvite(tempid,trd,userid)
    elif state==6:  #refuse
	print "not agree"
        tempid=jmsg['inviteCode']
        thd,userid=searchInvite(tempid)
        if thd in connectionlist:
            sendJson={'state':6,'accept':0,'result':0,'inviteCode':tempid,'friendId':None}
            send=json.dumps(sendJson)
            sjson=token_data(server,send)
            addr=connectionlist[thd]
            t1 = threading.Thread(target=sendMsg, args=[server,sjson, addr])
            t1.start()
        deleteInvite(tempid)
    elif state==7:  #agree
	print "agree"
        tempid=jmsg['inviteCode']
        flag=jmsg['result']
        trd=jmsg['trd']
        thrd,userid=searchInvite(tempid)
        uid=getuserid(trd)
        if flag:
            if trd in connectionlist:
                sendJson={'state':4,'inviteCode':tempid,'friendId':userid}
                send=json.dumps(sendJson)
                sjson=token_data(server,send)
                addr=connectionlist[trd]
                t1 = threading.Thread(target=sendMsg, args=[server,sjson,addr])
                t1.start()
            else:
                pass
            if thrd in connectionlist:
                sendJson={'state':6,'accept':1,'result':1,'inviteCode':tempid,'friendId':uid}
                send=json.dumps(sendJson)
                sjson=token_data(server,send)
                addr=connectionlist[thrd]
                t1 = threading.Thread(target=sendMsg, args=[server,sjson,addr])
          
        else:
            sendJson={'state':6,'accept':1,'result':0,'inviteCode':tempid,'friendId':None}
            send=json.dumps(sendJson)
            sjson=token_data(server,send)
            #addr1=connectionlist[trd]
            addr2=connectionlist[thrd]
            #t1 = threading.Thread(target=sendMsg, args=[server,sjson, addr1])
            #t1.start()
            t2 = threading.Thread(target=sendMsg, args=[server,sjson, addr2])
            t2.start()
        deleteInvite(tempid)
    else:
        data_error()
