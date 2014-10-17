import socket
import abc

class Validate:
    
    @staticmethod
    def valid_ip(address):
        try: 
            socket.inet_aton(address)
            return True
        except:
            return False
  
