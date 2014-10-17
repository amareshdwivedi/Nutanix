__author__ = 'subashatreya'

import abc
import json
import os
from reporters import CheckerResult

def check(func):
    def wrapper(*args, **kwargs):
        args[0].reporter.notify_progress("Running " + func.__name__)
        result = func(*args, **kwargs)

        checker_result = CheckerResult(func.__name__, result[0], result[1])
        args[0].reporter.notify_progress("Completed " + func.__name__ + " ....... " + str(result[0]))
        args[0].result.add_check_result(checker_result)
    return wrapper

class CheckerBase:

    __metaclass__ = abc.ABCMeta

    def __init__(self, name):
        self.config = {}
        auth={}
        try:
            auth=CheckerBase.get_auth_config(self.get_name())
        except ValueError:
            print self.get_name()+ " not configured"
            self.setup()
        except KeyError:
            print self.get_name()+ " not configured"
            self.setup()
        self.authconfig=auth
        self.reporter = None
        self.checks=[]
        self.result = CheckerResult(name)

    @abc.abstractmethod
    def get_name(self):
        return

    @abc.abstractmethod
    def get_desc(self):
        return

    @abc.abstractmethod
    def configure(self, config, reporter):
        return

    @abc.abstractmethod
    def execute(self, args):
        return
    
    @abc.abstractmethod
    def usage(self):
        return
       
    @abc.abstractmethod
    def setup(self):
        return

    @staticmethod
    def validate_config(config, prop):
        if not prop in config:
            raise RuntimeError(prop + " not in config")
    
    @staticmethod
    def get_auth_config(checker):
        fp = open("conf" + os.path.sep + "auth.conf", 'r')
        authconfig = json.load(fp)
        fp.close()
        return authconfig[checker]
 
    @staticmethod
    def save_auth_into_auth_config(checker_name, data):
        authconfig={}
        try:
            fp = open("conf" + os.path.sep + "auth.conf", 'r')
            authconfig = json.load(fp)
            fp.close()
            
        except ValueError:
            "do nothing"
        authconfig[checker_name]=data
        fp = open("conf" + os.path.sep + "auth.conf", 'w')
        json.dump(authconfig, fp, indent=2)
        fp.close()
    
