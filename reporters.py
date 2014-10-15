__author__ = 'subashatreya'
from prettytable import PrettyTable

class CheckerResult:
    def __init__(self, name, passed=None, message=None):
        self.name = name
        self.passed = passed
        self.message = message
        self.steps = []
        
    def add_check_result(self, step):
        self.steps.append(step)

    def set_status(self, status):
        self.status = status

    def set_message(self, message):
        self.message = message

    def to_dict(self):
        dict_obj = {"name": self.name, "pass:": self.passed, "message:": self.message}

        if len(self.steps) > 0:
            steps_dict = []
            for step in self.steps:
                steps_dict.append(step.to_dict())
            dict_obj["checks"] = steps_dict

        return dict_obj


class DefaultConsoleReporter:

    def __init__(self, name):
        self.name = name
        #self.x = PrettyTable(["Check Property", "Status"])
        #self.x.align["Check Property"] = "l"
        #self.x.align["Status"] = "l" # Left align city names
        #self.x.padding_width = 1 # One space between column edges and contents (default)



    def notify_progress(self, fname,*args):
        fname(*args)
        
        
    def notify_info(self, message):
        print self.name + " : " + "+++ "+message+" +++"
    
    def notify_checkGroup(self,message):
        print self.name + " : " + "\n++++ Running check group - "+message+" ++++"
    
    def notify_checkName(self,message):
        #print self.name + " : " + "Check - ",message
        self.x = PrettyTable([message, "Status"])
        self.x.align[message] = "l"
        self.x.align["Status"] = "l" # Left align city names
        self.x.padding_width = 1 # One space between column edges and contents (default)
        
        
    
    
    def notify_checkLog(self,message,status):
        #print self.name + " :     "+message + ('[ '+status+' ]').rjust(110-len(message))+''
        msg = " :     "+message + ('[ '+status+' ]').rjust(110-len(message))+''
        self.x.add_row([message,status])
        print str(self.x)
        
    

