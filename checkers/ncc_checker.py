__author__ = 'subashatreya'

import time
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

    def configure(self, config, reporter):
        self.config['cvm_ip'] = config['cvm_ip']
        self.config['cvm_user'] = config['cvm_user']
        self.reporter = reporter


    def run_checks(self):
        self.reporter.notify_progress("++++ Starting NCC Checks ++++")
        self.result = CheckerResult("ncc")

        self.check1()
        self.check2()

        self.result.status = "PASS"
        self.result.message = "NCC Checks Successful"
        self.reporter.notify_progress("++++ NCC Checks Completed ..... PASS ++++\n")

        return self.result
    
    def usage(self):
        x = PrettyTable(["Name", "Short help"])
        x.align["Name"] = "l"
        x.align["Short help"] = "l" # Left align city names
        x.padding_width = 1 # One space between column edges and contents (default)
        x.add_row(["run_all", "Run all checks."])           
        print x
        exit_with_message("")
    
    def parse_args(self,options):
        if len(options)==0:
            self.usage()
        option=options[0]
        if option == 'help' :
            self.usage()
        if option != "run_all":
            self.usage() 
        return

    @check
    def check1(self):
        time.sleep(1)
        return "FAIL", "Failed"

    @check
    def check2(self):
        time.sleep(1)
        return "PASS", "Successful"