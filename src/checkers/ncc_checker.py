__author__ = 'subashatreya'


import paramiko
from base_checker import *
from prettytable import PrettyTable
import sys
import ast




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

        CheckerBase.validate_config(config, "cvm_ip")
        CheckerBase.validate_config(config, "cvm_user")
        CheckerBase.validate_config(config, "cvm_pwd")
        CheckerBase.validate_config(config, "ncc_path")



    def execute(self, args):
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.config['cvm_ip'], username=self.config['cvm_user'], password=self.config['cvm_pwd'])

        self.reporter.notify_progress(self.reporter.notify_info,"Starting NCC Checks")
        self.result = CheckerResult("ncc")
        
        ntnx_env = "source /etc/profile.d/zookeeper_env.sh && source /usr/local/nutanix/profile.d/nutanix_env.sh && "
        cmd = len(args) > 0 and self.config['ncc_path'] + " --ncc_interactive=false " + " ".join(args) or self.config['ncc_path']
        cmd = ntnx_env + cmd

        status_text = {0 : "Done", 3 : "Pass",1 : "Done", 7: "Err"}
        stdin, stdout, stderr =  ssh.exec_command(cmd)
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
        self.reporter.notify_progress(self.reporter.notify_info,"NCC Checks complete")
        ssh.close()
        
        return self.result
        
    
    def usage(self):
        x = PrettyTable(["Name", "Short help"])
        x.align["Name"] = "l"
        x.align["Short help"] = "l" # Left align city names
        x.padding_width = 1 # One space between column edges and contents (default)
        x.add_row(["run_all", "Run all checks."])           
        print x
        exit_with_message("")
    
