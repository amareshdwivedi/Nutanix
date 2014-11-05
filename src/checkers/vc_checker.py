__author__ = 'subash atreya'
from requests.exceptions import ConnectionError
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
from colorama import Fore
import web
from web import form

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
        self.config_form =  form.Form( 
                form.Textbox("Server",value=self.authconfig['vc_ip']),
                form.Textbox("Port",value=self.authconfig['vc_port']),
                form.Textbox("User",value=self.authconfig['vc_user']),
                form.Password("Password",value=Security.decrypt(self.authconfig['vc_pwd'])),
                form.Password("Retype_Password",value=Security.decrypt(self.authconfig['vc_pwd'])), 
                form.Textbox("Cluster",value=self.authconfig['cluster']),
                form.Textbox("Host",value=self.authconfig['host']))() 

        self.si = None

    def get_name(self):
        return VCChecker._NAME_

    def get_desc(self):
        return "Performs vCenter Server health checks"

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
        x.add_row(["run_all", "Run all VC checks"])
        x.add_row(["setup", "Set vCenter Server Configuration"])
        message = message is None and str(x) or "\nERROR: "+ message + "\n\n" + str(x)
        exit_with_message(message)

    def setup(self):
        print "\nConfiguring vCenter Server:\n"
        
#         print "Current configuration for vCenter Server is:\n vCenter Server IP: %s \n vCenter User Name: %s \n VCenter Port: %d\n Clusters: %s \n hosts: %s"%\
#               (self.authconfig['vc_ip'], self.authconfig['vc_user'], self.authconfig['vc_port'],self.authconfig['cluster'],self.authconfig['host'] )
        current_vc_ip = self.authconfig['vc_ip'] if ('vc_ip' in self.authconfig.keys()) else "Not Set"
        vc_ip=raw_input("Enter vCenter Server IP [default: "+current_vc_ip+"]: ")
        vc_ip=vc_ip.strip()
        if vc_ip == "":
            if(current_vc_ip == "Not Set"):
                exit_with_message("Error: Set vCenter Server IP.")
            vc_ip=current_vc_ip
        
        if Validate.valid_ip(vc_ip) == False:
            exit_with_message("\nError: Invalid vCenter Server IP address")
                
        current_vc_user=self.authconfig['vc_user'] if ('vc_user' in self.authconfig.keys()) else "Not Set"
        vc_user=raw_input("Enter vCenter Server User Name [default: "+current_vc_user+"]: ")
        vc_user=vc_user.strip()
        if vc_user == "":
            if(current_vc_user == "Not Set"):
                exit_with_message("Error: Set vCenter Server User Name.")
            vc_user=current_vc_user
            
            
        current_pwd=self.authconfig['vc_pwd'] if  ('vc_pwd' in self.authconfig.keys()) else "Not Set"
        new_vc_pwd=getpass.getpass('Enter vCenter Server Password [Press enter to use previous password]: ')
        
        if new_vc_pwd == "":
            if(current_pwd == "Not Set"):
                exit_with_message("Error: Set vCenter Server Password.")
            vc_pwd = current_pwd
        else:
            confirm_pass=getpass.getpass('Re-Enter vCenter Server Password: ')
            if new_vc_pwd !=confirm_pass :
                exit_with_message("\nError: Password miss-match.Please run \"vc setup\" command again")
            vc_pwd=Security.encrypt(new_vc_pwd)
        
        current_vc_port=self.authconfig['vc_port'] if  ('vc_port' in self.authconfig.keys()) else "Not Set"
        vc_port=raw_input("Enter vCenter Server Port [default: "+str(current_vc_port)+"]: ")
        #vc_port=vc_port.strip()
        if vc_port == "":
            if(current_vc_port == "Not Set"):
                exit_with_message("Error: Set vCenter Server Port.")
            vc_port=int(current_vc_port)
        else:
            vc_port=int(vc_port)
        if isinstance(vc_port, int ) == False:
            exit_with_message("\nError: Port number is not a numeric value")
        
        current_cluster=self.authconfig['cluster'] if ('cluster' in self.authconfig.keys()) else "Not Set"
        cluster=raw_input("Enter Cluster Name [default: "+current_cluster+"] {multiple names separated by comma(,); blank to include all clusters}: ")
        cluster=cluster.strip()
        
        current_host=self.authconfig['host'] if ('host' in self.authconfig.keys()) else "Not Set"
        hosts=raw_input("Enter Host IP [default: "+current_host+"] {multiple names separated by comma(,); blank to include all hosts}: ")
        
        #Test Connection Status
        print "Checking vCenter Server Connection Status:",
        status, message = self.check_connectivity(vc_ip, vc_user, vc_pwd, vc_port)
        if status == True:
            print Fore.GREEN+" Connection successful"+Fore.RESET
        else:
           print Fore.RED+" Connection failure"+Fore.RESET
           exit_with_message(message)
           
        #print "vc_ip :"+vc_ip+" vc_user :"+vc_user+" vc_pwd : "+vc_pwd+ " vc_port:"+str(vc_port)+" cluster : "+cluster+" host : "+hosts
 
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
    
    def check_connectivity(self,vc_ip,vc_user,vc_pwd,vc_port):
        si=None
        warnings.simplefilter('ignore')
        try:
            si = SmartConnect(host=vc_ip, user=vc_user, pwd=Security.decrypt(vc_pwd), port=vc_port)
            return True,None
        except vim.fault.InvalidLogin:
            return False,"Error : Invalid vCenter Server Username or password\n\nPlease run \"vc setup\" command again!!"
        except ConnectionError as e:
            return False,"Error : Connection Error"+"\n\nPlease run \"vc setup\" command again!!"
        finally:
            Disconnect(si)
    
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
        self.result = CheckerResult("vc",self.authconfig)
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
        
        try:
            self.si = SmartConnect(host=self.authconfig['vc_ip'], user=self.authconfig['vc_user'], pwd=Security.decrypt(self.authconfig['vc_pwd']), port=self.authconfig['vc_port'])
        except vim.fault.InvalidLogin:
            exit_with_message("Error : Invalid vCenter Server Username or password\n\nPlease run \"vc setup\" command to configure vc")
        except ConnectionError as e:
            exit_with_message("Error : Connection Error"+"\n\nPlease run \"vc setup\" command to configure vc")
        
        passed_all = True
        #self.realtime_results['vc'] = []
        for check_group in check_groups_run:
            self.reporter.notify_progress(self.reporter.notify_checkGroup,check_group)
            for check in self.config[check_group]:
                self.reporter.notify_progress(self.reporter.notify_checkName,check['name'])
                passed, message = self.validate_vc_property(check['path'], check['operator'], check['ref-value'])
                try:
                    self.realtime_results = json.load(open("test.json","r"))
                    all_prop,props = [ x for x in message.split(', ') if x != ''], []
                    for xprop in all_prop:
                        xprop,xstatus = xprop.split("#")
                        
                        xprop_msg, xprop_actual, xprop_exp = xprop.split("=")
                        if xprop_msg == "":
                            xprop_msg = check['name']
                        xprop_actual = xprop_actual.split(' ')[0]
                        
                        if check['operator'] == "=": 
                            xprop_exp = check['ref-value']
                        else:
                            xprop_exp = "not "+check['ref-value']  
                        props.append({"Message":xprop_msg,"Status":xstatus,"Expected":xprop_exp , "Actual":xprop_actual })
                
                    self.realtime_results['vc']['checks'].append({'Message':check['name'] ,'Status': (passed and "PASS" or "FAIL"),"Properties": props})
                    with open("test.json", "w") as myfile:
                        json.dump(self.realtime_results, myfile)
                except:
                    # Need to handle temp-file case for command line
                    pass
                self.result.add_check_result(CheckerResult(check['name'], None, passed, message, check['severity']))
                passed_all = passed_all and passed
            
            if check_group in check_functions:
                for check_function in check_functions[check_group]:
                    passed, message = check_function()
                    try:
                        self.realtime_results = json.load(open("test.json","r"))
                        all_prop,props = [ x for x in message.split(', ') if x != ''], []
                        for xprop in all_prop:
                            xprop,xstatus = xprop.split("#")
                            xprop_msg, xprop_actual, xprop_exp = xprop.split("=")
                            xprop_actual = xprop_actual.split(' ')[0]
                            xprop_exp = xprop_exp.split(")")[0]
                            props.append({"Message":xprop_msg,"Status":xstatus,"Expected":xprop_exp , "Actual":xprop_actual })
                        
                        self.realtime_results['vc']['checks'].append({'Message':check_function.descr ,'Status': (passed and "PASS" or "FAIL"),"Properties": props})
                        with open("test.json", "w") as myfile:
                            json.dump(self.realtime_results, myfile)
                    except:
                        pass
                    self.result.add_check_result(CheckerResult(check_function.descr, None, passed, message, check_function.severity))
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
            if isinstance(property, list):
                property = ','.join(property)
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
        if hasattr(cur_obj, "name")  and cur_obj.name not in name:
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
        passed = True
        message = ""
        message_all = ""
        for cluster, cluster_datastores in datastores.iteritems():
            try:
                cluster_heartbeat_datastores = [ds.name for ds in heartbeat_datastores[cluster]]
            except KeyError:
                cluster_heartbeat_datastores = []
            except:
                print "Unknown error"   
            for ds in cluster_datastores:
                if not fnmatch.fnmatch(ds.name, 'NTNX-*'):
                    is_heartbeating = ds.name in cluster_heartbeat_datastores
                    self.reporter.notify_progress(self.reporter.notify_checkLog,cluster+"."+ds.name+"="+str(is_heartbeating) + " (Expected: =True) " , (is_heartbeating and "PASS" or "FAIL"))
                    passed = passed and is_heartbeating
                    message += ", " +cluster+"."+ds.name+"="+str(is_heartbeating) + " (Expected: =True) "+"#"+((is_heartbeating) and "PASS" or "FAIL")
 
        return passed, message
    
    @checkgroup("cluster_checks", "VSphere Cluster Nodes in Same Version", 1)
    def check_vSphere_cluster_nodes_in_same_version(self):
        #content.rootFolder.childEntity.hostFolder.childEntity.datastore.host.key.config.product.version
        datastores = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.datastore')
         
        message = ""
        passed = True
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
            passed = passed and (not mult_vers_flag)
            message += ", " +cluster+" Nodes have Multiple Versions Available"+"#"+(( not mult_vers_flag) and "PASS" or "FAIL")   
        return passed, message
    
    @checkgroup("cluster_checks", "Cluster Advance Settings das.isolationaddress1",1)
    def check_cluster_das_isolationaddress1(self):
        all_isolation_address1 = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.configuration.dasConfig.option[key=das*isolationaddress1].value')
        all_cvm_ips = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.configurationEx.dasVmConfig.key[name=NTNX*CVM].guest.net.ipAddress')
        all_ips = []
        for item in all_cvm_ips.values():
            all_ips.extend(item)
        
        message = ""
        isolation_address_present=True
        passed = True
        try:
            for cluster, isolation_address1 in all_isolation_address1.iteritems():
                isolation_address_present = isolation_address1 in all_ips
                
                self.reporter.notify_progress(self.reporter.notify_checkLog,   cluster + "=CVM IP:"+str(isolation_address_present)+" (Expected: =CVM IP: True)" , (isolation_address_present and "PASS" or "FAIL"))
                passed = passed and isolation_address_present 
                message += ", " + cluster + "=CVM-IP:"+str(isolation_address_present)+" (Expected: =CVM-IP:True) " +"#"+((isolation_address_present) and "PASS" or "FAIL")      
        except AttributeError:
            self.reporter.notify_progress(self.reporter.notify_checkLog," isolationaddress1 not configured (Expected : = Should be Cluster IP)"  , (not isolation_address_present and "PASS" or "FAIL"))
            passed = False
            message += ", " +"=isolationaddress1 not configured (Expected : = Should be Cluster IP) "+"#"+("FAIL") 
            return False, message
        return passed, message
    
    @checkgroup("cluster_checks", "Cluster Advance Settings das.isolationaddress2",1)
    def check_cluster_das_isolationaddress2(self):
        all_isolation_address2 = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.configuration.dasConfig.option[key=das*isolationaddress2].value')
        all_cvm_ips = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.configurationEx.dasVmConfig.key[name=NTNX*CVM].guest.ipAddress')
        message = ""
        isolation_address_present=True
        passed = False
        try:
            for cluster, isolation_address2 in all_isolation_address2.iteritems():
                isolation_address_present = isolation_address2 in all_cvm_ips.values()
                self.reporter.notify_progress(self.reporter.notify_checkLog,  cluster + "=CVM IP:"+str(isolation_address_present)+" (Expected: =CVM IP: True) "  , (isolation_address_present and "PASS" or "FAIL"))
                passed = passed and isolation_address_present  
                message += ", " + cluster + "=CVM-IP:"+str(isolation_address_present)+" (Expected: =CVM-IP:True) " +"#"+(( isolation_address_present) and "PASS" or "FAIL")        
        except AttributeError:
            self.reporter.notify_progress(self.reporter.notify_checkLog," isolationaddress2 not configured (Expected : = Should be any one of the CVM IP)"  , (not isolation_address_present and "PASS" or "FAIL"))
            passed = False
            message += ", " +"=isolationaddress2 not configured (Expected : = Should be any one of the CVM IP)"+"#"+("FAIL")
            return False, message
        return passed, message
                
    @checkgroup("cluster_checks", "Cluster Advance Settings das.isolationaddress3",1)
    def check_cluster_das_isolationaddress3(self):
        all_isolation_address3 = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.configuration.dasConfig.option[key=das*isolationaddress3].value')
        all_cvm_ips = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.configurationEx.dasVmConfig.key[name=NTNX*CVM].guest.ipAddress')
        message = ""
        isolation_address_present=True
        passed = True
        try:
            for cluster, isolation_address3 in all_isolation_address3.iteritems():
                isolation_address_present = isolation_address3 in all_cvm_ips.values()
                self.reporter.notify_progress(self.reporter.notify_checkLog,  cluster + "=CVM IP:"+str(isolation_address_present)+" (Expected: =CVM IP: True) " , (isolation_address_present and "PASS" or "FAIL"))
                passed = passed and isolation_address_present
                message += ", " +cluster+"=CVM-IP:"+str(isolation_address_present)+" (Expected: =CVM-IP:True) "+"#" +((isolation_address_present) and "PASS" or "FAIL")         
        except AttributeError:
            self.reporter.notify_progress(self.reporter.notify_checkLog," isolationaddress2 not configured (Expected: = Should be any one of the CVM IP)"  , (not isolation_address_present and "PASS" or "FAIL"))
            passed = False
            message += ", " +"=isolationaddress3 not configured(Expected : = Should be any one of the CVM IP)"+"#"+("FAIL")
        return passed, message  
    
    @checkgroup("esxi_checks", "Validate the Directory Services Configuration is set to Active Directory",3)
    def check_directory_service_set_to_active_directory(self):
        authenticationStoreInfo = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.host.config.authenticationManagerInfo.authConfig')
       
        message = ""
        passed = True
        for hostname,store in authenticationStoreInfo.iteritems():
            for item in store :
                if isinstance(item,vim.host.ActiveDirectoryInfo):
                    if hasattr(item,"enabled"):
                        is_active_dir_enabled=item.enabled
                        self.reporter.notify_progress(self.reporter.notify_checkLog, hostname+"="+str(is_active_dir_enabled) + " (Expected: =True) " , (is_active_dir_enabled and "PASS" or "FAIL"))
                        passed = passed and (is_active_dir_enabled and True or False)
                        message += ", " +hostname+"="+str(is_active_dir_enabled) + " (Expected: =True) "+"#"+((is_active_dir_enabled) and "PASS" or "FAIL") 
       
        return passed, message
    
    @checkgroup("esxi_checks", "Validate NTP client is set to Enabled and is in the running state",1)
    def check_ntp_client_enable_running(self):
        datacenter_hosts =self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.host')
        message = ""
        passed = False
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
                    passed = passed and ((ruleset_enable and service_running) and "PASS" or "FAIL") 
                    message += ", " +datacenter+"."+host.name+" = NTP Client Status Enabled:"+str(ruleset_enable) + " and is running:"+str(service_running)+" (Expected: ="+" NTP Client Enable : True and running : True "+") "+"#"+ ((ruleset_enable and service_running) and "PASS" or "FAIL")
                except AttributeError:
                    self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter+"."+host.name+" = NTP Client not configured" , ((ruleset_enable and service_running) and "PASS" or "FAIL"))
                    passed = False
                    message += ", " +datacenter+"."+host.name+" = NTP Client not configured"+" (Expected: ="+" NTP Client Enable : True and running : True "+") "+"#"+ ((ruleset_enable and service_running) and "PASS" or "FAIL")
        return passed, message

    @checkgroup("vcenter_server_checks", "Validate vCenter Server license expiration date",1)
    def check_vcenter_server_license_expiry(self):
        expirationDate = self.get_vc_property('content.licenseManager.evaluation.properties[key=expirationDate].value')
        
        message = ""
        passed = False
        for item, expiry_date in expirationDate.iteritems():
            #Currently timezone is not considered for the date difference / Need to add
            xexpiry = datetime.datetime(expiry_date.year,expiry_date.month, expiry_date.day)
            
            valid_60_days = (xexpiry - (datetime.datetime.today() + datetime.timedelta(60))).days > 60 or (xexpiry - (datetime.datetime.today() + datetime.timedelta(60))).days < 0
            self.reporter.notify_progress(self.reporter.notify_checkLog,"License Expiration Validation date " + str(expiry_date) + " days (Expected: => 60 days or always valid) " , (valid_60_days and "PASS" or "FAIL"))
            passed = passed and valid_60_days
            message += ", "+"License Expiration Validation date " + str(expiry_date) + " days (Expected: => 60 days or always valid) "+"#"+((not valid_60_days) and "PASS" or "FAIL")
        return passed, message
    
    @checkgroup("vcenter_server_checks", "Validate vCenter Server has VMware Tools installed and is up to date.",3)
    def check_vcenter_server_tool_status(self):
        vcenter_ipv4 = self.get_vc_property('content.setting.setting[key=VirtualCenter*AutoManagedIPV4].value')
        vcenter_ip=vcenter_ipv4[""]
        vms = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.host.vm.guest')
        
        message = ""
        passed = True
        for vm in vms.keys():
            guest_info=vms[vm]
            if guest_info.ipAddress == vcenter_ip:
                toolsStatus=guest_info.toolsStatus
                toolsStatus_expected="toolsOk"
                if toolsStatus == toolsStatus_expected :
                    self.reporter.notify_progress(self.reporter.notify_checkLog, "vCenter Server VMware Tools installed Status="+toolsStatus  + " (Expected: ="+toolsStatus_expected+") " , (True and "PASS" or "FAIL"))
                else:
                    passed = False
                    self.reporter.notify_progress(self.reporter.notify_checkLog, "vCenter Server VMware Tools installed Status="+toolsStatus  + " (Expected: ="+toolsStatus_expected+") " , (False and "PASS" or "FAIL"))
                message += ", "+"vCenter Server VMware Tools installed Status="+toolsStatus  + " (Expected: ="+toolsStatus_expected+") " +"#"+((toolsStatus == toolsStatus_expected) and "PASS" or "FAIL")
                break
        
        return passed,message
    
    @checkgroup("network_and_switch_checks", "Virtual Distributed Switch - Network IO Control",1)
    def check_virtual_distributed_switch_networ_io_control(self):
        datacenter_networks = self.get_vc_property('content.rootFolder.childEntity.networkFolder.childEntity')
       
        message = ""
        passed = True
        for datacenter in datacenter_networks.keys():
            network_list = datacenter_networks.get(datacenter)
            for network in network_list:
                if isinstance(network,vim.dvs.VmwareDistributedVirtualSwitch):
                    nioc_enabled=network.config.networkResourceManagementEnabled
                    self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter+"."+network.name+"="+str(nioc_enabled) + " (Expected: =True) " , (nioc_enabled and "PASS" or "FAIL"))
                    message += ", " +datacenter+"."+network.name+"="+str(nioc_enabled) + " (Expected: =True) "+"#"+((nioc_enabled) and "PASS" or "FAIL")
                    passed = passed and nioc_enabled
        return passed, message
        
    @checkgroup("network_and_switch_checks", "Virtual Distributed Switch - MTU",2)
    def check_virtual_distributed_switch_mtu(self):
        datacenter_networks = self.get_vc_property('content.rootFolder.childEntity.networkFolder.childEntity')
       
        message = ""
        pass_all=True
        for datacenter in datacenter_networks.keys():
            network_list = datacenter_networks.get(datacenter)
            for network in network_list:
                if isinstance(network,vim.dvs.VmwareDistributedVirtualSwitch):
                    maxMtu=network.config.maxMtu
                    # default value for maxMtu is 1500. Sometime MOB returns None value. So setting maxMtu value to 1500 as default
                    if maxMtu is None: 
                        maxMtu=1500
                    maxMtu_expected=1500
                    if maxMtu == maxMtu_expected:
                        message += ", " +datacenter+"."+network.name+"="+str(maxMtu) + " (Expected: ="+str(maxMtu_expected)+")"+"#"+(True and "PASS" or "FAIL")
                        self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter+"."+network.name+"="+str(maxMtu) + " (Expected: ="+str(maxMtu_expected)+") " , ( True and "PASS" or "FAIL"))
                    else:
                        pass_all=False
                        self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter+"."+network.name+"="+str(maxMtu) + " (Expected: ="+str(maxMtu_expected)+") " , ( False and "PASS" or "FAIL"))
                        message += ", " +datacenter+"."+network.name+"="+str(maxMtu) + " (Expected: ="+str(maxMtu_expected)+")"+"#"+(False and "PASS" or "FAIL")
       
        return pass_all, message
    
    @checkgroup("storage_and_vm_checks", "Confirm the states of vStorage hardware acceleration support for datastore.",1)
    def check_vStorageSupport(self):
        datacenter_host = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity')
        message = ""
        pass_all=True
        for host_domain in datacenter_host.keys():      
            for ClusterComputeRrc in datacenter_host[host_domain]:
                # print "\n*******************\nClusterComputeRrc : "+str(ClusterComputeRrc)
                expected_vStorageSupported="vStorageSupported"
                try:
                    datastores=ClusterComputeRrc.environmentBrowser.QueryConfigTarget().datastore
                    for datastore in datastores:
                        vStorageSupport=datastore.vStorageSupport
                        
                        if fnmatch.fnmatch(datastore.name,"NTNX-local-ds*") :
                            continue
                        else:
                            if (vStorageSupport == expected_vStorageSupported):
                                message += ", " +host_domain+"."+ClusterComputeRrc.name+"."+datastore.name+"="+vStorageSupport+ " (Expected: ="+expected_vStorageSupported+")"+"#"+(True and "PASS" or "FAIL")
                                self.reporter.notify_progress(self.reporter.notify_checkLog, host_domain+"."+ClusterComputeRrc.name+"."+datastore.name+"="+vStorageSupport+ " (Expected: ="+expected_vStorageSupported+")" , ( True and "PASS" or "FAIL"))
                            else:
                                pass_all=False
                                # To handle None Value
                                new_vStorageSupport= vStorageSupport if vStorageSupport else "None"
                                message += ", " +host_domain+"."+ClusterComputeRrc.name+"."+datastore.name+"="+new_vStorageSupport + " (Expected: ="+expected_vStorageSupported+")"+"#"+(False and "PASS" or "FAIL")
                                self.reporter.notify_progress(self.reporter.notify_checkLog, host_domain+"."+ClusterComputeRrc.name+"."+datastore.name+"="+new_vStorageSupport+ " (Expected: ="+expected_vStorageSupported+")" , ( False and "PASS" or "FAIL"))
            
                except AttributeError:
                    pass_all=False 
                    message += ", " + host_domain+"."+ClusterComputeRrc.name+"="+ "DataStore not attached"+ " (Expected: ="+expected_vStorageSupported+")"+"#"+(False and "PASS" or "FAIL")
                    self.reporter.notify_progress(self.reporter.notify_checkLog, host_domain+"."+ClusterComputeRrc.name+"="+ "DataStore not attached"+ " (Expected: ="+expected_vStorageSupported+")", ( False and "PASS" or "FAIL"))
                     
        return pass_all, message
