import re

class Validate:
    
    @staticmethod
    def valid_ip(address):
        ip_pattern = "^([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])$"
        pat=re.compile(ip_pattern)
        is_valid_ip = pat.match(str(address))
        if is_valid_ip : 
            return True
        return False
