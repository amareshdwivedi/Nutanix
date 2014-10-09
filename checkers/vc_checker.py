__author__ = 'subash atreya'

import string
import warnings
import argparse
from pyVim.connect import SmartConnect, Disconnect

from base_checker import *

class VCChecker(CheckerBase):

    _NAME_ = "vc"

    def __init__(self):
        super(VCChecker, self).__init__(VCChecker._NAME_)

    def get_name(self):
        return VCChecker._NAME_

    def configure(self, config, reporter):
        self.config = config
        self.reporter = reporter

        # Only for validation to fail early
        a = config['vc_ip']
        a = config['vc_user']
        a = config['vc_pwd']
        a = config['vc_port']
        checks_list = [k for k,v in config.items() if k.endswith('checks')]
        #print checks_list
        for checks in checks_list:
            metrics = config[checks]
            if len(metrics) == 0:
                raise RuntimeError("At least one metric must be specified in "+ checks + "configuration file");

    def parse_vc_args(self,check_list):
        checks_list = [k for k,v in self.config.items() if k.endswith('checks')]
        print checks_list
        parser = argparse.ArgumentParser(description='Nutanix HealthCheck Tool : VCenter Checks')
        for checks in check_list : 
            parser.add_argument(checks, help="Checks you want to run")
        args = parser.parse_args()
        return args

    def run_checks(self):
        self.reporter.notify_progress("+++ Starting VC Checks")
        self.result = CheckerResult("vc")
        warnings.simplefilter('ignore')
        si = SmartConnect(host=self.config['vc_ip'], user=self.config['vc_user'], pwd=self.config['vc_pwd'], port=self.config['vc_port'])

        passed_all = True 
        #checks_list = [k for k,v in self.config.items() if k.endswith('checks')]
        if len(self.checks)==0:
            checks_list = [k for k,v in self.config.items() if k.endswith('checks')]
        else:
            checks_list =self.checks
            
        for checks in checks_list:
            for check in self.config[checks]:
                name, xpath_str, expected = string.split(check, ',')
                name = name.strip()
                xpath_str = xpath_str.strip()
                expected = expected.strip()
    
                xpath = string.split(xpath_str, '.')
                self.reporter.notify_progress("Check - " + name)
                passed, message = self.validate_vc_property(xpath, si, None, expected)
                self.result.add_check_result(CheckerResult(name, passed, message))
                passed_all = passed_all and passed

        Disconnect(si)
        self.result.passed = passed_all
        self.result.message = "VC Checks completed with " + (passed_all and "success" or "failure")
        self.reporter.notify_progress("+++ VC Checks complete\n")

        return self.result


    def validate_vc_property(self, xpath, cur_obj, name, expected):
        attr = getattr(cur_obj, xpath[0])

        if hasattr(cur_obj, "name"):
            name = cur_obj.name

        if len(xpath) == 1:
            if expected == str(attr):
                passed = True
                message = name + "." + xpath[0] + "=" + expected
            else:
                passed = False
                message = name + "." + xpath[0] + "=" + str(attr) + "(Expected = " + expected + ")"

            self.reporter.notify_progress("   " +message + (passed and " .... PASS" or " .... FAIL"))

            return passed, message

        if isinstance(attr, list):
            passed_all = True
            message_all = ""
            for item in attr:
                passed, message = self.validate_vc_property(xpath[1:], item, name, expected)
                passed_all = passed_all and passed
                message_all = len(message_all) > 0 and (message_all + " , " + message) or message
            return passed_all, message_all

        else:
            return self.validate_vc_property(xpath[1:], attr, name, expected)
