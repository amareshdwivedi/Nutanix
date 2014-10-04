__author__ = 'subashatreya'

import time
from reporters import CheckerResult


class NCCChecker:

    _NAME_ = "ncc"

    def __init__(self):
        self.result = None
        self.config = {}

    def get_name(self):
        return NCCChecker._NAME_

    def configure(self, config):
        self.config['cvm_ip'] = config['cvm_ip']
        self.config['cvm_user'] = config['cvm_user']

    def run_checks(self, listener):
        listener.notify_progress("Starting NCC Checks")
        self.result = CheckerResult("ncc", "PASS", "NCC Checks Passed")
        self.check1(listener)
        self.check2(listener)
        listener.notify_progress("Check complete")
        return self.result

    def check1(self, listener):
        time.sleep(1)
        listener.notify_progress("Check1 ............ PASS")
        self.result.add_step_result(CheckerResult("Check1", "PASS", "Check 1 passed"))

    def check2(self, listener):
        time.sleep(1)
        listener.notify_progress("Check2 ............ PASS")
        self.result.add_step_result(CheckerResult("Check2", "PASS", "Check 2 passed"))