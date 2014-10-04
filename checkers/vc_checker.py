__author__ = 'subash atreya'

import time
from reporters import CheckerResult


class VCChecker:

    _NAME_ = "vc"

    def __init__(self):
        self.result = None
        self.config = {}

    def get_name(self):
        return VCChecker._NAME_

    def configure(self, config):
        self.config['vc_ip'] = config['vc_ip']
        self.config['vc_user'] = config['vc_user']

    def run_checks(self, listener):
        listener.notify_progress("Starting VC Checks")
        time.sleep(2)
        self.result = CheckerResult("vc", "PASS", "NCC Checks Passed")
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