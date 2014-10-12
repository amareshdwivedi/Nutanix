__author__ = 'subash atreya'

import string
import warnings
from pyVim.connect import SmartConnect, Disconnect
from base_checker import *
from prettytable import PrettyTable
import sys
import re

def exit_with_message(message):
    print message
    sys.exit(1)




class VCChecker(CheckerBase):

    _NAME_ = "vc"

    def __init__(self):
        super(VCChecker, self).__init__(VCChecker._NAME_)

    def get_name(self):
        return VCChecker._NAME_

    def get_desc(self):
        return "This module is used to run VCenter Server checks"

    def configure(self, config, reporter):
        self.config = config
        self.reporter = reporter

        CheckerBase.validate_config(config, "vc_ip")
        CheckerBase.validate_config(config, "vc_user")
        CheckerBase.validate_config(config, "vc_pwd")
        CheckerBase.validate_config(config, "vc_port")

        checks_list = [k for k in config.keys() if k.endswith('checks')]
        #print checks_list
        for checks in checks_list:
            metrics = config[checks]
            if len(metrics) == 0:
                raise RuntimeError("At least one metric must be specified in "+ checks + "configuration file");

    def usage(self, message=None):
        x = PrettyTable(["Name", "Short help"])
        x.align["Name"] = "l"
        x.align["Short help"] = "l" # Left align city names
        x.padding_width = 1 # One space between column edges and contents (default)
        checks_list = [k for k in self.config.keys() if k.endswith('checks')]

        for checks in checks_list:
            x.add_row([checks,"Run "+checks+" checks"])
        x.add_row(["run_all", "Run all VC checks."])

        message = message is None and str(x) or "\nERROR : "+ message + "\n\n" + str(x)
        exit_with_message(message)


    def run_checks(self, args):

        if len(args) == 0:
            self.usage()

        check_groups = [k for k,v in self.config.items() if k.endswith('checks')]
        check_groups_run = []

        if args[0] == "help":
            self.usage()

        elif args[0] == "run_all":
            check_groups_run = check_groups
            if len(args) > 1:
                self.usage("Parameter not expected after run_all")

        else:
            for group in args:
                if group not in check_groups:
                    self.usage("Group " + group + " is not a valid check group")
                check_groups_run.append(group)


        self.reporter.notify_progress("+++ Starting VC Checks")
        self.result = CheckerResult("vc")
        warnings.simplefilter('ignore')
        si = SmartConnect(host=self.config['vc_ip'], user=self.config['vc_user'], pwd=self.config['vc_pwd'], port=self.config['vc_port'])

        passed_all = True

        #print si.content.rootFolder.childEntity[0].hostFolder.childEntity[0].configuration.drsVmConfig[0].key.name

        for check_group in check_groups_run:

            for check in self.config[check_group]:
                xpath = string.split(check['path'], '.')
                self.reporter.notify_progress("Check - " + check['name'])
                passed, message = self.validate_vc_property(xpath, si, check['name'], check['operator'], check['ref-value'])
                self.result.add_check_result(CheckerResult(check['name'], passed, message))
                passed_all = passed_all and passed

        Disconnect(si)
        self.result.passed = passed_all
        self.result.message = "VC Checks completed with " + (passed_all and "success" or "failure")
        self.reporter.notify_progress("+++ VC Checks complete\n")

        return self.result

    @staticmethod
    def apply_operator(actual, expected, operator):
        if operator == "=":
            return expected == str(actual)
        # Handle others operators as needed
        else:
            raise RuntimeError("Unexpected operator " + operator)



    def matches_filter(self, xpath, cur_obj, expected):
        attr = getattr(cur_obj, xpath[0])
        if len(xpath) == 1:
            return re.match(expected, attr) is not None

        if isinstance(attr, list):
            matches = True
            for item in attr:
                matches = matches and self.matches_filter(xpath[1:], item, expected)
            return matches
        else:
            return self.matches_filter(xpath[1:], attr, expected)

    def apply_filter(self, cur_obj, filter):
        if filter is None:
            return True

        filter_prop, filter_val = filter.split("=")
        filter_prop_xpath = string.split(filter_prop, '.')

        return self.matches_filter(filter_prop_xpath, cur_obj, filter_val)


    def validate_vc_property(self, xpath, cur_obj, name, operator, expected):

        if "[" in xpath[0]:
            node,filter = xpath[0].split("[")
            filter = filter[:-1]
        else:
            node = xpath[0]
            filter = None

        attr = getattr(cur_obj, node)

        if hasattr(cur_obj, "name"):
            name = cur_obj.name

        if len(xpath) == 1:
            if VCChecker.apply_operator(attr, expected, operator):
                passed = True
                message = name + "." + node + operator + expected
            else:
                passed = False
                message = name + "." + node + "=" + str(attr) + "(Expected: " + operator + expected + ")"

            self.reporter.notify_progress("   " +message + (passed and " .... PASS" or " .... FAIL"))

            return passed, message

        if isinstance(attr, list):
            passed_all = True
            message_all = ""

            for item in attr:
                if self.apply_filter(item, filter):
                    passed, message = self.validate_vc_property(xpath[1:], item, name, operator, expected)
                    passed_all = passed_all and passed
                    message_all = len(message_all) > 0 and (message_all + " , " + message) or message

            return passed_all, message_all

        else:
            return self.apply_filter(attr, filter) and self.validate_vc_property(xpath[1:], attr, name, operator, expected) or (True, "")
