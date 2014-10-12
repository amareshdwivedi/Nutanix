__author__ = 'subashatreya'


import paramiko
from base_checker import *
from prettytable import PrettyTable
import sys





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



    def run_checks(self, args):

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.config['cvm_ip'], username=self.config['cvm_user'], password=self.config['cvm_pwd'])

        ntnx_env = "source /etc/profile.d/zookeeper_env.sh && source /usr/local/nutanix/profile.d/nutanix_env.sh && "

        cmd = len(args) > 0 and self.config['ncc_path'] + " " + " ".join(args) or self.config['ncc_path']
        cmd = ntnx_env + cmd

        stdin, stdout, stderr =  ssh.exec_command(cmd)


        for line in stdout:
            print line.strip('\n')


        ssh.close()

        return CheckerResult("ncc")

    
    def usage(self):
        x = PrettyTable(["Name", "Short help"])
        x.align["Name"] = "l"
        x.align["Short help"] = "l" # Left align city names
        x.padding_width = 1 # One space between column edges and contents (default)
        x.add_row(["run_all", "Run all checks."])           
        print x
        exit_with_message("")
    
