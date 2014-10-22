__author__ = 'subashatreya'


import paramiko
from base_checker import *
from prettytable import PrettyTable
import sys
import ast
import getpass
from validation import Validate
from security import Security


def exit_with_message(message):
    print message
    sys.exit(1)


class NCCChecker(CheckerBase):

    _NAME_ = "ncc"

    def __init__(self):
        super(NCCChecker, self).__init__(NCCChecker._NAME_)

    def get_name(self):
        return NCCChecker._NAME_

    def get_desc(self):
        return "This module is used to run NCC checks"

    def configure(self, config, reporter):
        self.config = config
        self.reporter = reporter
        self.authconfig=self.get_auth_config(self.get_name())
        CheckerBase.validate_config(self.authconfig, "cvm_ip")
        CheckerBase.validate_config(self.authconfig, "cvm_user")
        CheckerBase.validate_config(self.authconfig, "cvm_pwd")
        CheckerBase.validate_config(self.config, "ncc_path")
        
    def usage(self, message=None):
        x = PrettyTable(["Name", "Short help"])
        x.align["Name"] = "l"
        x.align["Short help"] = "l" # Left align city names
        x.padding_width = 1 # One space between column edges and contents (default)
        x.add_row(["ncc", "Run NCC checks."])
        x.add_row(["ncc setup", "Set Nutanix Cluster Check Configuration"])
        message = message is None and str(x) or "\nERROR : "+ message + "\n\n" + str(x)
        exit_with_message(message)

    def execute(self, args):
        
        if len(args) != 0:
            if args[0] == 'setup':
                self.setup()
                exit_with_message("Nutanix Cluster is configured.")
            
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.authconfig['cvm_ip'], username=self.authconfig['cvm_user'], password=Security.decrypt(self.authconfig['cvm_pwd']))

        self.reporter.notify_progress(self.reporter.notify_info,"Starting NCC Checks")
        self.result = CheckerResult("ncc")
        
        ntnx_env = "source /etc/profile.d/zookeeper_env.sh && source /usr/local/nutanix/profile.d/nutanix_env.sh && "
        cmd = len(args) > 0 and self.config['ncc_path'] + " --ncc_interactive=false " + " ".join(args) or self.config['ncc_path']
        cmd = ntnx_env + cmd

        status_text = {0 : "Done",1 : "Done", 3 : "Pass",4: "Pass",5: "Warn",6: "Fail", 7: "Err"}
        stdin, stdout, stderr =  ssh.exec_command(cmd)
        passed_all = True
        for line in stdout:
            try :
                t = ast.literal_eval(line.strip('\n').replace("null","'null'").replace("true","'true'").replace("false","'false'"))
            except :
                print line.strip('\n')
                continue

            check_name = t["output holder list"][0]["message"]            
            status = t["status"]
            message = ""
            if status in [7]:
                message = t["detail canvas"]["output holder list"] [0]["message list"][0]
                
            self.result.add_check_result(CheckerResult(check_name, status_text[status], message))
            self.reporter.notify_one_line(check_name, status_text[status])
            if status not in [0,1,3,4]:
                passed_all = False
        self.result.passed = (passed_all and "PASS" or "FAIL")
        self.reporter.notify_progress(self.reporter.notify_info,"NCC Checks complete")
        ssh.close()
        
        return self.result
 
    
    def setup(self):
        print "\nConfiguring NCC :\n"
        cvm_ip=raw_input("Enter CVM IP : ")
        
        if Validate.valid_ip(cvm_ip) == False:
            exit_with_message("\nError : Invalid CVM IP address")
        
        cvm_user=raw_input("Enter CVM User Name : ")
        new_pass=getpass.getpass('Please Enter a  CVM Password: ')
        confirm_pass=getpass.getpass('Please Re-Enter a CVM Password: ')
        if new_pass !=confirm_pass :
            exit_with_message("\nError :Password miss-match. Please try setup command again")
        cvm_pwd=Security.encrypt(new_pass)
        
        #print "cvm_ip :"+cvm_ip+" cvm_user :"+cvm_user+" cvm_pwd : "+cvm_pwd
        
        ncc_auth = dict()
        ncc_auth["cvm_ip"]=cvm_ip;
        ncc_auth["cvm_user"]=cvm_user;
        ncc_auth["cvm_pwd"]=cvm_pwd;
     
        CheckerBase.save_auth_into_auth_config(self.get_name(),ncc_auth)
        exit_with_message("NCC is configured Successfully ")
        return