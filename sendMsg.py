# coding: utf-8
def sendMsg(self, data, address):
    try:
        client = self.clients[address]
        try:
            client.send(data)
        except:
            self.close_client(address)
    except:
        pass
