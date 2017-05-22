#!/usr/bin/python
from Crypto.PublicKey import RSA
def encrypt(message):
    externKey="PublicKey.pem"
    privatekey = open(externKey, "r")
    encryptor = RSA.importKey(privatekey)
    encriptedData=encryptor.encrypt(message, 0)
    file = open("cryptThingy.txt", "wb")
    file.write(encriptedData[0])
    file.close()
if __name__ == "__main__":
    encryptedThingy=encrypt("Loren ipsum")