# coding: utf-8
def sendMsg(self, data, address):
    print "send msg" 
    try:
        print("client")
        client = self.clients[address]
        try:
            client.send(data)
            print("send")
        except:
            print("fail")
            self.close_client(address)
    except:
        print("fail")
        pass
