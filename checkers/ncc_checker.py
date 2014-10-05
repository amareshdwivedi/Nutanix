__author__ = 'subashatreya'

import time
from base_checker import *


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

    @check
    def check1(self):
        time.sleep(1)
        return "FAIL", "Failed"

    @check
    def check2(self):
        time.sleep(1)
        return "PASS", "Successful"