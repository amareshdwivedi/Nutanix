__author__ = 'subashatreya'
from prettytable import PrettyTable
from colorama import Fore, Back, Style
from colorama import init
init()

class CheckerResult:
    def __init__(self, name, passed=None, message=None):
        self.name = name
        self.passed = passed
        
        if self.passed != '':
            self.passed = passed and "PASS" or "FAIL"
        
        self.message = message
        self.steps = []

    def add_check_result(self, step):
        self.steps.append(step)

    def set_status(self, status):
        self.status = status
    
    def set_message(self, message):
        self.message = message
        
    def prop_dict(self):
        props  = []
        all_prop = [ x for x in self.message.split(', ') if x != '']
        for xprop in all_prop:
            xprop,xstatus = xprop.split("#")
            props.append({"Message":xprop,"Status":xstatus})
        return props
        
    def to_dict(self):
        if self.message == None:
            return None
        elif ',' in self.message:
            self.props = self.prop_dict()
            dict_obj = {"Name": self.name, "Status": self.passed, "Properties": self.props}
        else:
            dict_obj = {"Name": self.name, "Status": self.passed, "Properties": self.message}
            
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
        self.x.add_row([message.ljust(120),status])
        self.row_count += 1
    
    def notify_one_line(self,message, status):
        print "+"+"-"*130+"+"
        if status == "FAIL":
            status = Fore.RED+"[ "+status+" ]"+Fore.RESET
        elif status == "Err":
            status = Fore.YELLOW+"[ "+status+" ]"+Fore.RESET
        else:
            status = Fore.GREEN+"[ "+status+" ]"+Fore.RESET
        print message.ljust(120),status
        self.row_count += 1
        

