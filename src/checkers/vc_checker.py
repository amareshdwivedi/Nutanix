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
import getpass
from validation import Validate
from security import Security

def exit_with_message(message):
    print message
    sys.exit(1)


def checkgroup(group_name, description, severity):
    def outer(func):
        def inner(*args, **kwargs):
            args[0].reporter.notify_progress(args[0].reporter.notify_checkName, description)
            return func(*args, **kwargs)
        inner.group = group_name
        inner.descr = description
        inner.severity = severity
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
        self.authconfig=self.get_auth_config(self.get_name())
        CheckerBase.validate_config(self.authconfig, "vc_ip")
        CheckerBase.validate_config(self.authconfig, "vc_user")
        CheckerBase.validate_config(self.authconfig, "vc_pwd")
        CheckerBase.validate_config(self.authconfig, "vc_port")

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
        x.add_row(["setup", "Set vCenter Server Configuration"])
        message = message is None and str(x) or "\nERROR : "+ message + "\n\n" + str(x)
        exit_with_message(message)

    def setup(self):
        print "\nConfiguring vCenter Server :\n"
        vc_ip=raw_input("Enter vCenter Server IP : ")
        if Validate.valid_ip(vc_ip) == False:
            exit_with_message("\nError : Invalid vCenter Server IP address")
        vc_user=raw_input("Enter vCenter Server User Name : ")
        new_pass=getpass.getpass('Please Enter vCenter Server Password : ')
        confirm_pass=getpass.getpass('Please Re-Enter vCenter Server Password : ')
        if new_pass !=confirm_pass :
            exit_with_message("\nError :Password miss-match. Please try setup command again")
        vc_pwd=Security.encrypt(new_pass)
        
        vc_port=int(raw_input("Enter vCenter Server Port : "))
    
        if isinstance(vc_port, int ) == False:
            exit_with_message("\nError : Port number is not a numeric value")
        #print "vc_ip :"+vc_ip+" vc_user :"+vc_user+" vc_pwd : "+vc_pwd+ " vc_port:"+vc_port
        cluster=raw_input("Enter Cluster Name[multiple names separated by comma(,); blank to include all clusters] : ")
        hosts=raw_input("Enter Host IP[multiple names separated by comma(,); blank to include all host] : ")
        vc_auth = dict()
        vc_auth["vc_ip"]=vc_ip;
        vc_auth["vc_user"]=vc_user;
        vc_auth["vc_pwd"]=vc_pwd;
        vc_auth["vc_port"]=vc_port;
        vc_auth["cluster"]=cluster;
        vc_auth["host"]=hosts;
        CheckerBase.save_auth_into_auth_config(self.get_name(),vc_auth)
        exit_with_message("vCenter Server is configured Successfully ")
        return
    
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
        elif args[0] == 'setup':
            self.setup()
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

        self.si = SmartConnect(host=self.authconfig['vc_ip'], user=self.authconfig['vc_user'], pwd=Security.decrypt(self.authconfig['vc_pwd']), port=self.authconfig['vc_port'])

        passed_all = True


        for check_group in check_groups_run:
            self.reporter.notify_progress(self.reporter.notify_checkGroup,check_group)
            for check in self.config[check_group]:
                self.reporter.notify_progress(self.reporter.notify_checkName,check['name'])
                passed, message = self.validate_vc_property(check['path'], check['operator'], check['ref-value'])
                self.result.add_check_result(CheckerResult(check['name'], passed, message, check['severity']))
                passed_all = passed_all and passed
            self.reporter.notify_progress(self.reporter.notify_checkName,"")

            if check_group in check_functions:
                for check_function in check_functions[check_group]:
                    passed, message = check_function()
                    self.result.add_check_result(CheckerResult(check_function.descr, passed, message, check_function.severity))
                    passed_all = passed_all and passed
                self.reporter.notify_progress(self.reporter.notify_checkName,"")

        Disconnect(self.si)
        self.result.passed = ( passed_all and "PASS" or "FAIL" )
        self.result.message = "VC Checks completed with " + (passed_all and "success" or "failure")
        self.reporter.notify_progress(self.reporter.notify_info,"VC Checks complete")

        return self.result


    def validate_vc_property(self, path, operator, expected):

        props = self.get_vc_property(path)
        message_all = ""
        passed_all = True
        
        if props == None:
            passed =  VCChecker.apply_operator(props, expected, operator)
            message = path + "=" + "None" + " (Expected: " + operator + expected + ") "
            message_all += (", "+message+"#"+(passed and "PASS" or "FAIL")) 
            passed_all = passed_all and passed
            self.reporter.notify_progress(self.reporter.notify_checkLog, message, passed and "PASS" or "FAIL")
            return False, message_all
        
        if expected.startswith("content"):
            # Reference to another object
            expected_props = self.get_vc_property(expected)

        
        

        for path,property in props.iteritems():
            expected_val = expected
            if expected.startswith("content"):
                expected_val = str(expected_props[path])

            passed =  VCChecker.apply_operator(property, expected_val, operator)
            passed_all = passed_all and passed
            message = path + "=" + str(property) + " (Expected: " + operator + expected_val + ") "
            #if not passed:
            #    message_all += ("," + message)
            self.reporter.notify_progress(self.reporter.notify_checkLog,message, passed and "PASS" or "FAIL")
            message_all += (", "+message+"#"+(passed and "PASS" or "FAIL")) 
        if passed_all:
            return True, message_all
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
        try:
            attr = getattr(cur_obj, xpath[0])
        except AttributeError:
            return {}
        except:
            print "Unknow error"   
        
        if hasattr(cur_obj, "name"):
            filter_names.append(cur_obj.name)

        if len(xpath) == 1:
            if filter_operator == '=':
                for expected_val in expected.split(','):
                    if fnmatch.fnmatch(attr, expected_val):
                        return True
                return False
            elif filter_operator == '!=':
                for expected_val in expected.split(','):
                    if not fnmatch.fnmatch(attr, expected_val):
                        return True
                return False

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


    def retrieve_vc_property(self, xpath, cur_obj, name, cluster_level_entity=False):
        if "[" in xpath[0]:
            node,filter = xpath[0].split("[")
            filter = filter[:-1]
        else:
            node = xpath[0]
            filter = None
          
        if node == "hostFolder":
            cluster_level_entity = True
            
        if node == "childEntity" and cluster_level_entity:
            if self.authconfig['cluster'] != "":
                filter = "name="+self.authconfig['cluster']
        if node == "host":
            if self.authconfig['host'] != "":
                filter = "name="+self.authconfig['host']
                
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
                    attr_val = self.retrieve_vc_property(xpath[1:], item, name + filter_names,cluster_level_entity)
                    if attr_val:
                        vals.update(attr_val)

            if name_added:
                name.pop()

            return vals

        else:
            filter_names = []
            filter_pass = self.apply_filter(attr, filter, filter_names)
            result = filter_pass and self.retrieve_vc_property(xpath[1:], attr, name + filter_names,cluster_level_entity) or None
            if name_added:
                name.pop()

            return result


    def get_vc_property(self, path):
        return self.retrieve_vc_property(string.split(path, '.'), self.si, [])


    # Manual checks
    @checkgroup("cluster_checks", "Validate datastore heartbeat", 1)
    def check_datastore_heartbeat(self):

        datastores = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.datastore')
        heartbeat_datastores = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.configuration.dasConfig.heartbeatDatastore')

        message = ""
        message_all = ""
        for cluster, cluster_datastores in datastores.iteritems():
            cluster_heartbeat_datastores = [ds.name for ds in heartbeat_datastores[cluster]]
            for ds in cluster_datastores:
                if not fnmatch.fnmatch(ds.name, 'NTNX-*'):
                    is_heartbeating = ds.name in cluster_heartbeat_datastores
                    self.reporter.notify_progress(self.reporter.notify_checkLog,cluster+"."+ds.name+"="+str(is_heartbeating) + " (Expected: =True) " , (is_heartbeating and "PASS" or "FAIL"))
                    '''
                    if not is_heartbeating:
                    '''
                    message += ", " +cluster+"."+ds.name+"is not heartbeating"+"#"+((not is_heartbeating) and "PASS" or "FAIL")

        if len(message) > 0:
            return True, message
        else:
            return False, message
    
    @checkgroup("cluster_checks", "VSphere Cluster Nodes in Same Version", 1)
    def check_vSphere_cluster_nodes_in_same_version(self):
        #content.rootFolder.childEntity.hostFolder.childEntity.datastore.host.key.config.product.version
        datastores = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.datastore')
        
        message = ""
        for cluster, cluster_datastores in datastores.iteritems():
            mult_vers_flag, versions = False, [] 
            for datastore in cluster_datastores:
                for host in datastore.host:
                    if len(versions) == 0:
                        versions.append(host.key.config.product.version)
                    else:
                        if host.key.config.product.version not in versions:
                            versions.append(host.key.config.product.version)
                            mult_vers_flag = True
                            break
                if mult_vers_flag:
                    break
            self.reporter.notify_progress(self.reporter.notify_checkLog, cluster + " (Expected multiple Version: =No ( found:"+str(versions)+") ) " , (not mult_vers_flag and "PASS" or "FAIL"))
            '''
            if mult_vers_flag:
            '''
            message += ", " +cluster+" Nodes have Multiple Versions Available"+"#"+(( not mult_vers_flag) and "PASS" or "FAIL")   
        if len(message) > 0:
            return True, message
        else:
            return False, message

    @checkgroup("cluster_checks", "Cluster Advance Settings das.isolationaddress1",1)
    def check_cluster_das_isolationaddress1(self):
        all_isolation_address1 = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.configuration.dasConfig.option[key=das*isolationaddress1].value')
        all_cvm_ips = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.configurationEx.dasVmConfig.key[name=NTNX*CVM].guest.net.ipAddress')
        all_ips = []
        for item in all_cvm_ips.values():
            all_ips.extend(item)
        
        message = ""
        for cluster, isolation_address1 in all_isolation_address1.iteritems():
            isolation_address_present = isolation_address1 in all_ips
            
            self.reporter.notify_progress(self.reporter.notify_checkLog,  cluster + " (Expected : =Cluster configuration option IsolationAddress1(Value) is some CVM's ipAddress ) " , (isolation_address_present and "PASS" or "FAIL"))
            '''
            if not isolation_address_present:
            '''
            message += ", " +cluster+" isolationaddress1 value is not CVM ipAddress."+"#"+((not isolation_address_present) and "PASS" or "FAIL")      
        if len(message) > 0:
            return True, message
        else:
            return False, message
    
    @checkgroup("cluster_checks", "Cluster Advance Settings das.isolationaddress2",1)
    def check_cluster_das_isolationaddress2(self):
        all_isolation_address2 = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.configuration.dasConfig.option[key=das*isolationaddress2].value')
        all_cvm_ips = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.configurationEx.dasVmConfig.key[name=NTNX*CVM].guest.ipAddress')
        message = ""
        for cluster, isolation_address2 in all_isolation_address2.iteritems():
            isolation_address_present = isolation_address2 in all_cvm_ips.values()
            self.reporter.notify_progress(self.reporter.notify_checkLog,  cluster + " (Expected : =Cluster configuration option IsolationAddress2(Value) is some CVM's ipAddress ) " , (isolation_address_present and "PASS" or "FAIL"))
            '''
            if not isolation_address_present:
            '''
            message += ", " +cluster+" isolationaddress2 value is not CVM ipAddress."+"#"+((not isolation_address_present) and "PASS" or "FAIL")        
        if len(message) > 0:
            return True, message
        else:
            return False, message
                
    @checkgroup("cluster_checks", "Cluster Advance Settings das.isolationaddress3",1)
    def check_cluster_das_isolationaddress3(self):
        all_isolation_address3 = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.configuration.dasConfig.option[key=das*isolationaddress3].value')
        all_cvm_ips = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.configurationEx.dasVmConfig.key[name=NTNX*CVM].guest.ipAddress')
        message = ""
        for cluster, isolation_address3 in all_isolation_address3.iteritems():
            isolation_address_present = isolation_address3 in all_cvm_ips.values()
            self.reporter.notify_progress(self.reporter.notify_checkLog,  cluster + " (Expected : =Cluster configuration option IsolationAddress3(Value) is some CVM's ipAddress ) " , (isolation_address_present and "PASS" or "FAIL"))
            '''
            if not isolation_address_present:
            '''
            message += ", " +cluster+" isolationaddress3 value is not CVM ipAddress."+"#" +((not isolation_address_present) and "PASS" or "FAIL")         
        if len(message) > 0:
            return True, message
        else:
            return False, message  
    
    @checkgroup("esxi_checks", "Validate the Directory Services Configuration is set to Active Directory",3)
    def check_directory_service_set_to_active_directory(self):
        authenticationStoreInfo = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.host.config.authenticationManagerInfo.authConfig')
       
        message = ""
        for hostname,store in authenticationStoreInfo.iteritems():
            for item in store :
                if isinstance(item,vim.host.ActiveDirectoryInfo):
                    if hasattr(item,"enabled"):
                        is_active_dir_enabled=item.enabled
                        self.reporter.notify_progress(self.reporter.notify_checkLog, hostname+"="+str(is_active_dir_enabled) + " (Expected: =True) " , (is_active_dir_enabled and "PASS" or "FAIL"))
                        '''
                        if not is_active_dir_enabled:
                        '''
                        message += ", " +hostname+" ActiveDirectoryInfo not enabled"+"#"+(( not is_active_dir_enabled) and "PASS" or "FAIL") 
       
        if len(message) > 0:
            return True, message
        else:
            return False, message
    
    @checkgroup("esxi_checks", "Validate NTP client is set to Enabled and is in the running state",1)
    def check_ntp_client_enable_running(self):
        datacenter_hosts =self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.host')
        message = ""
        for datacenter in datacenter_hosts.keys():
            for host in datacenter_hosts[datacenter]:
                try:
                    ruleset_enable =False
                    service_running = False
                    rulesets=host.configManager.firewallSystem.firewallInfo.ruleset
                    host_services =host.config.service.service
                    for ruleset in rulesets:
                        if ruleset.key=="ntpClient":
                            ruleset_enable=ruleset.enabled
                             
                            for service in host_services:
                                if service.key == "ntpd":
                                    service_running=service.running
                    self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter+"."+host.name+" = NTP Client Status Enabled:"+str(ruleset_enable) + " and is running:"+str(service_running)+" (Expected: ="+" NTP Client Enable : True and running : True "+") " , ((ruleset_enable and service_running) and "PASS" or "FAIL"))
                    message += ", " +datacenter+"."+host.name+" = NTP Client Status Enabled:"+str(ruleset_enable) + " and is running:"+str(service_running)+" (Expected: ="+" NTP Client Enable : True and running : True "+") "+"#"+ ((ruleset_enable and service_running) and "PASS" or "FAIL")
                except AttributeError:
                    self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter+"."+host.name+" = NTP Client not configured" , ((ruleset_enable and service_running) and "PASS" or "FAIL"))
                    message += ", " +datacenter+"."+host.name+" = NTP Client not configured"+"#"+((ruleset_enable and service_running) and "PASS" or "FAIL")
                                    
        if len(message) > 0:
            return True, message
        else:
            return False, message

    @checkgroup("vcenter_server_checks", "Validate vCenter Server license expiration date",1)
    def check_vcenter_server_license_expiry(self):
        expirationDate = self.get_vc_property('content.licenseManager.evaluation.properties[key=expirationDate].value')
        
        message = ""
        for item, expiry_date in expirationDate.iteritems():
            #Currently timezone is not considered for the date difference / Need to add
            xexpiry = datetime.datetime(expiry_date.year,expiry_date.month, expiry_date.day)
            
            valid_60_days = (xexpiry - (datetime.datetime.today() + datetime.timedelta(60))).days > 60 or (xexpiry - (datetime.datetime.today() + datetime.timedelta(60))).days < 0
            self.reporter.notify_progress(self.reporter.notify_checkLog,"License Expiration Validation date " + str(expiry_date) + " days (Expected: > 60 days or always valid) " , (valid_60_days and "PASS" or "FAIL"))
            message += ", "+"License valid for less than 60 days"+"#"+((not valid_60_days) and "PASS" or "FAIL")
        if len(message) > 0:
            return True, message
        else:
            return False, message
    
    @checkgroup("vcenter_server_checks", "Validate vCenter Server has VMware Tools installed and is up to date.",3)
    def check_vcenter_server_tool_status(self):
        vcenter_ipv4 = self.get_vc_property('content.setting.setting[key=VirtualCenter*AutoManagedIPV4].value')
        vcenter_ip=vcenter_ipv4[""]
        vms = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.host.vm.guest')
        
        message = ""
        for vm in vms.keys():
            guest_info=vms[vm]
            if guest_info.ipAddress == vcenter_ip:
                toolsStatus=guest_info.toolsStatus
                toolsStatus_expected="toolsOk"
                if toolsStatus == toolsStatus_expected :
                    self.reporter.notify_progress(self.reporter.notify_checkLog, "vCenter Server VMware Tools installed Status="+toolsStatus  + " (Expected: ="+toolsStatus_expected+") " , (True and "PASS" or "FAIL"))
                else:
                    self.reporter.notify_progress(self.reporter.notify_checkLog, "vCenter Server VMware Tools installed Status="+toolsStatus  + " (Expected: ="+toolsStatus_expected+") " , (False and "PASS" or "FAIL"))
                message += "vCenter Server VMware Tools installed Status="+toolsStatus  + " (Expected: ="+toolsStatus_expected+") " +"#"+((toolsStatus == toolsStatus_expected) and "PASS" or "FAIL")
                break
        
        if len(message) > 0:
            return True, message
        else:
            return False, message
    
    @checkgroup("network_and_switch_checks", "Virtual Distributed Switch - Network IO Control",1)
    def check_virtual_distributed_switch_networ_io_control(self):
        datacenter_networks = self.get_vc_property('content.rootFolder.childEntity.networkFolder.childEntity')
       
        message = ""
        for datacenter in datacenter_networks.keys():
            network_list = datacenter_networks.get(datacenter)
            for network in network_list:
                if isinstance(network,vim.dvs.VmwareDistributedVirtualSwitch):
                    nioc_enabled=network.config.networkResourceManagementEnabled
                    self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter+"."+network.name+"="+str(nioc_enabled) + " (Expected: =True) " , (nioc_enabled and "PASS" or "FAIL"))
                    message += ", " +datacenter+"."+network.name+"  Network IO Control not enabled"+"#"+((not nioc_enabled) and "PASS" or "FAIL")
       
        if len(message) > 0:
            return True, message
        else:
            return False, message
        
    @checkgroup("network_and_switch_checks", "Virtual Distributed Switch - MTU",2)
    def check_virtual_distributed_switch_mtu(self):
        datacenter_networks = self.get_vc_property('content.rootFolder.childEntity.networkFolder.childEntity')
       
        message = ""
        for datacenter in datacenter_networks.keys():
            network_list = datacenter_networks.get(datacenter)
            for network in network_list:
                if isinstance(network,vim.dvs.VmwareDistributedVirtualSwitch):
                    maxMtu=network.config.maxMtu
                    # default value for maxMtu is 1500. Sometime MOB returns None value. So setting maxMtu value to 1500 as default
                    if maxMtu=="None": 
                        maxMtu=1500
                    maxMtu_expected=1500
                    if maxMtu == maxMtu_expected:
                        message += ", " +datacenter+"."+network.name+"="+str(maxMtu) + " (Expected: ="+str(maxMtu_expected)+")"+"#"+(True and "PASS" or "FAIL")
                        self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter+"."+network.name+"="+str(maxMtu) + " (Expected: ="+str(maxMtu_expected)+") " , ( True and "PASS" or "FAIL"))
                    else:
                        message += ", " +datacenter+"."+network.name+"="+str(maxMtu) + " (Expected: ="+str(maxMtu_expected)+")"+"#"+(False and "PASS" or "FAIL")
       
        if len(message) > 0:
            return True, message
        else:
            return False, message
