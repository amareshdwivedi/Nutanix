__author__ = 'subash atreya'

import string
import warnings
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
from base_checker import *
from prettytable import PrettyTable
import sys
import fnmatch
import datetime

def exit_with_message(message):
    print message
    sys.exit(1)


def checkgroup(group_name, description):
    def outer(func):
        def inner(*args, **kwargs):
            args[0].reporter.notify_progress(args[0].reporter.notify_checkName, description)
            return func(*args, **kwargs)
        inner.group = group_name
        return inner
    return outer

class VCChecker(CheckerBase):

    _NAME_ = "vc"


    def __init__(self):
        super(VCChecker, self).__init__(VCChecker._NAME_)
        self.si = None

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
            x.add_row([checks,"Run "+checks])
        x.add_row(["run_all", "Run all VC checks."])

        message = message is None and str(x) or "\nERROR : "+ message + "\n\n" + str(x)
        exit_with_message(message)


    def execute(self, args):

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


        self.reporter.notify_progress(self.reporter.notify_info,"Starting VC Checks")
        self.result = CheckerResult("vc")
        warnings.simplefilter('ignore')


        check_functions = {}
        for func in dir(self):
            func_obj = getattr(self, func)
            if callable(func_obj) and func.startswith("check_") and hasattr(func_obj, 'group'):
                group_name = func_obj.group
                group_functions = check_functions.get(group_name)
                if group_functions:
                    group_functions.append(func_obj)
                else:
                    check_functions[group_name] = [func_obj]

        self.si = SmartConnect(host=self.config['vc_ip'], user=self.config['vc_user'], pwd=self.config['vc_pwd'], port=self.config['vc_port'])

        passed_all = True


        for check_group in check_groups_run:
            self.reporter.notify_progress(self.reporter.notify_checkGroup,check_group)
            for check in self.config[check_group]:
                self.reporter.notify_progress(self.reporter.notify_checkName,check['name'])
                passed, message = self.validate_vc_property(check['path'], check['operator'], check['ref-value'])
                self.result.add_check_result(CheckerResult(check['name'], passed, message))
                passed_all = passed_all and passed

            if check_group in check_functions:
                for check_function in check_functions[check_group]:
                    passed, message = check_function()
                    self.result.add_check_result(CheckerResult(check['name'], passed, message))
                    passed_all = passed_all and passed

        Disconnect(self.si)
        self.result.passed = passed_all
        self.result.message = "VC Checks completed with " + (passed_all and "success" or "failure")
        self.reporter.notify_progress(self.reporter.notify_info,"VC Checks complete")

        return self.result


    def validate_vc_property(self, path, operator, expected):

        props = self.get_vc_property(path)
        if props == None:
            message = path + "=" + "None" + " (Expected: " + operator + expected + ") "
            passed =  VCChecker.apply_operator(props, expected, operator)
            self.reporter.notify_progress(self.reporter.notify_checkLog, message, passed and "PASS" or "FAIL")
            return False, message
        
        if expected.startswith("content"):
            # Reference to another object
            expected_props = self.get_vc_property(expected)

        passed_all = True
        message_all = ""

        for path,property in props.iteritems():
            expected_val = expected
            if expected.startswith("content"):
                expected_val = str(expected_props[path])

            passed =  VCChecker.apply_operator(property, expected_val, operator)
            passed_all = passed_all and passed
            message = path + "=" + str(property) + " (Expected: " + operator + expected_val + ") "
            if not passed:
                message_all += ("," + message)
            self.reporter.notify_progress(self.reporter.notify_checkLog,message, passed and "PASS" or "FAIL")

        if passed_all:
            return True, None
        else:
            return False, message_all


    @staticmethod
    def apply_operator(actual, expected, operator):

        if operator == "=":
            return expected == str(actual)

        elif operator == "<":
            return int(actual) < int(expected)

        elif operator == "<=":
            return int(actual) <= int(expected)
        elif operator == "!=":
            return expected != str(actual)

        # Handle others operators as needed
        else:
            raise RuntimeError("Unexpected operator " + operator)



    def matches_filter(self, xpath, cur_obj, expected, filter_names,filter_operator):
        attr = getattr(cur_obj, xpath[0])

        if hasattr(cur_obj, "name"):
            filter_names.append(cur_obj.name)

        if len(xpath) == 1:
            if filter_operator == '=':
                return fnmatch.fnmatch(attr, expected)
            elif filter_operator == '!=':
                return not fnmatch.fnmatch(attr, expected)

        if isinstance(attr, list):
            matches = True
            for item in attr:
                matches = matches and self.matches_filter(xpath[1:], item, expected, filter_names,filter_operator)
            return matches
        else:
            return self.matches_filter(xpath[1:], attr, expected, filter_names,filter_operator)

    def apply_filter(self, cur_obj, filter, filter_names):
        if filter is None:
            return True
        if'!=' in filter:
            filter_prop, filter_val = filter.split("!=")
            filter_operator = '!='
        elif '=' in filter:    
            filter_prop, filter_val = filter.split("=")
            filter_operator = '=' 
        filter_prop_xpath = string.split(filter_prop, '-')

        return self.matches_filter(filter_prop_xpath, cur_obj, filter_val, filter_names, filter_operator)


    def retrieve_vc_property(self, xpath, cur_obj, name):
        if "[" in xpath[0]:
            node,filter = xpath[0].split("[")
            filter = filter[:-1]
        else:
            node = xpath[0]
            filter = None
    
        try:
            attr = getattr(cur_obj, node)
        except AttributeError:
            return {}
        except:
            print "Unknow error"     
        

        name_added = False
        if hasattr(cur_obj, "name"):
            name.append(cur_obj.name)
            name_added = True


        if len(xpath) == 1:
            return {".".join(name): attr}

        if isinstance(attr, list):
            vals = {}

            for item in attr:
                filter_names = []
                filter_pass = self.apply_filter(item, filter, filter_names)

                if filter_pass:
                    attr_val = self.retrieve_vc_property(xpath[1:], item, name + filter_names)
                    if attr_val:
                        vals.update(attr_val)

            if name_added:
                name.pop()

            return vals

        else:
            filter_names = []
            filter_pass = self.apply_filter(attr, filter, filter_names)
            result = filter_pass and self.retrieve_vc_property(xpath[1:], attr, name + filter_names) or None
            if name_added:
                name.pop()

            return result


    def get_vc_property(self, path):
        return self.retrieve_vc_property(string.split(path, '.'), self.si, [])


    # Manual checks
    @checkgroup("cluster_checks", "Validate datastore heartbeat")
    def check_datastore_heartbeat(self):

        datastores = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.datastore')
        heartbeat_datastores = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.configuration.dasConfig.heartbeatDatastore')

        message = ""
        for cluster, cluster_datastores in datastores.iteritems():
            cluster_heartbeat_datastores = [ds.name for ds in heartbeat_datastores[cluster]]
            for ds in cluster_datastores:
                if not fnmatch.fnmatch(ds.name, 'NTNX-*'):
                    is_heartbeating = ds.name in cluster_heartbeat_datastores
                    self.reporter.notify_progress(self.reporter.notify_checkLog,cluster+"."+ds.name+"="+str(is_heartbeating) + " (Expected: =True) " , (is_heartbeating and "PASS" or "FAIL"))
                    if not is_heartbeating:
                        message += ", " +cluster+"."+ds.name+"is not heartbeating"

        if len(message) > 0:
            return True, None
        else:
            return False, message
    
    @checkgroup("cluster_checks", "VSphere Cluster Nodes in Same Version")
    def check_vSphere_cluster_nodes_in_same_version(self):
        #content.rootFolder.childEntity.hostFolder.childEntity.datastore.host.key.config.product.version
        datastores = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.datastore')
        
        message = ""
        
        for cluster, cluster_datastores in datastores.iteritems():
            mult_vers_flag, version = False, ''
            for datastore in cluster_datastores:
                for host in datastore.host:
                    if version == '':
                        version = host.key.config.product.version
                    else:
                        if host.key.config.product.version != version:
                            mult_vers_flag = True
                            break
            self.reporter.notify_progress(self.reporter.notify_checkLog, cluster + " (Expected multiple Version: =No) " , (not mult_vers_flag and "PASS" or "FAIL"))
            if mult_vers_flag:
                message += ", " +cluster+" nodes have multiple versions avilable."        
        if len(message) > 0:
            return True, None
        else:
            return False, message

    @checkgroup("esxi_checks", "Validate the Directory Services Configuration is set to Active Directory")
    def check_directory_service_set_to_active_directory(self):
        authenticationStoreInfo = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.host.config.authenticationManagerInfo.authConfig')
       
        message = ""
        for hostname,store in authenticationStoreInfo.iteritems():
            for item in store :
                if isinstance(item,vim.host.ActiveDirectoryInfo):
                    if hasattr(item,"enabled"):
                        is_active_dir_enabled=item.enabled
                        self.reporter.notify_progress(self.reporter.notify_checkLog, hostname+"="+str(is_active_dir_enabled) + " (Expected: =True) " , (is_active_dir_enabled and "PASS" or "FAIL"))
                        if not is_active_dir_enabled:
                            message += ", " +hostname+" ActiveDirectoryInfo not enabled"
       
        if len(message) > 0:
            return True, None
        else:
            return False, message

    @checkgroup("vcenter_server_checks", "Validate vCenter Server license expiration date")
    def check_vcenter_server_license_expiry(self):
        expirationDate = self.get_vc_property('content.licenseManager.evaluation.properties[key=expirationDate].value')
        
        message = ""
        for item, expiry_date in expirationDate.iteritems():
            #Currently timezone is not considered for the date difference / Need to add
            xexpiry = datetime.datetime(expiry_date.year,expiry_date.month, expiry_date.day)
            
            valid_60_days = (xexpiry - (datetime.datetime.today() + datetime.timedelta(60))).days > 60 or (xexpiry - (datetime.datetime.today() + datetime.timedelta(60))).days < 0
            self.reporter.notify_progress(self.reporter.notify_checkLog,"License Expiration Validation date " + str(expiry_date) + " days (Expected: > 60 days or always valid) " , (valid_60_days and "PASS" or "FAIL"))
            if not valid_60_days:
                message += ", License valid for less than 60 days"
        if len(message) > 0:
            return True, message
        else:
            return False, message
