__author__ = 'subashatreya'
from prettytable import PrettyTable
from colorama import Fore, Back, Style
from colorama import init
init()

MSG_WIDTH = 120
class CheckerResult:
    def __init__(self, name, passed=None, message=None, severity=1):
        self.name = name
        self.passed = passed
        if str(self.passed) in ("True","False"):
            self.passed = passed and "PASS" or "FAIL"
        self.message = message
        self.severity = severity
        self.steps = []

    def add_check_result(self, step):
        self.steps.append(step)

    def set_status(self, status):
        self.status = status
    
    def set_message(self, message):
        self.message = message
        
    def set_severity(self, severity):
        self.severity = severity
        
    def prop_dict(self):
        props  = []
        all_prop = [ x for x in self.message.split(', ') if x != '']
        for xprop in all_prop:
            xprop,xstatus = xprop.split("#")
            props.append({"Message":xprop,"Status":xstatus})
        return props
        
    def to_dict(self):
        if self.message is None:
            dict_obj = {"Name": self.name, "Status": self.passed} 
        elif ',' in self.message:
            self.props = self.prop_dict()
            dict_obj = {"Name": self.name, "Status": self.passed, "Properties": self.props, "Severity": self.severity}
        else:
            dict_obj = {"Name": self.name, "Status": self.passed, "Properties": self.message, "Severity": self.severity}
            
        if len(self.steps) > 0:
            steps_dict = []
            for step in self.steps:
                steps_dict.append(step.to_dict())
            dict_obj["checks"] = steps_dict

        return dict_obj


class DefaultConsoleReporter:

    def __init__(self, name):
        self.name = name
        self.row_count = 0
        self.x = PrettyTable(["message", "Status"])
        
    def notify_progress(self, fname,*args):
        fname(*args)
        
        
    def notify_info(self, message):
        print self.name + " : " + "+++ "+message+" +++"
    
    def notify_checkGroup(self,message):
        print self.name + " : " + "\n++++ Running check group - "+message+" ++++"
        
    def notify_checkName(self,message):
        if self.row_count > 0:
            print str(self.x)
            
        if message == "":
            return
        
        self.x = PrettyTable([message, "Status"])
        self.x.align[message] = "l"
        self.x.align["Status"] = "l"
        self.x.padding_width = 1
        self.row_count = 0
        
        
    def notify_checkLog(self,message, status):
        if status == "FAIL":
            status = Fore.RED+status+Fore.RESET
        else:
            status = Fore.GREEN+status+Fore.RESET
        
        self.x.add_row(['\n'.join([message[x:x+MSG_WIDTH] for x in range(0,len(message),MSG_WIDTH)]).ljust(MSG_WIDTH),status])
        self.row_count += 1
    
    def notify_one_line(self,message, status):
        print "+"+"-"*MSG_WIDTH+"-"*10+"+"
        if status == "FAIL":
            status = Fore.RED+"[ "+status+" ]"+Fore.RESET
        elif status == "Err":
            status = Fore.YELLOW+"[ "+status+" ]"+Fore.RESET
        elif status == "Warn":
            status = Fore.MAGENTA+"[ "+status+" ]"+Fore.RESET
        else:
            status = Fore.GREEN+"[ "+status+" ]"+Fore.RESET
        print '\n'.join([message[x:x+MSG_WIDTH] for x in range(0,len(message),MSG_WIDTH)]).ljust(MSG_WIDTH),status
        self.row_count += 1
        

