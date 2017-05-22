#!/usr/bin/python
from Crypto.PublicKey import RSA
def decrypt():
    externKey="PrivateKey.pem"
    publickey = open(externKey, "r")
    decryptor = RSA.importKey(publickey, passphrase="f00bar")
    retval=None
    file = open("cryptThingy.txt", "rb")
    retval = decryptor.decrypt(file.read())
    file.close()
    return retval
if __name__ == "__main__":
    decryptedThingy=decrypt()
    print "Decrypted: %s" % decryptedThingy