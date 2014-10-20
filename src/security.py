import binascii
from Crypto.Cipher import ARC4

class Security :
    @staticmethod
    def encrypt(data):
        arc=ARC4.new('01234567')
        cipher_text=binascii.hexlify(arc.encrypt(data))
        return cipher_text
    
    @staticmethod
    def decrypt(cipher_text):
        arc = ARC4.new('01234567')
        data=arc.decrypt(binascii.unhexlify(cipher_text))
        return data