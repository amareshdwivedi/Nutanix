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


def checkgroup(group_name, description, category,expected_result):
    def outer(func):
        def inner(*args, **kwargs):
            args[0].reporter.notify_progress(args[0].reporter.notify_checkName, description)
            return func(*args, **kwargs)
        inner.group = group_name
        inner.descr = description
        inner.category = category
        inner.expected_result = expected_result
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
                #form.Password("Retype_Password",value=Security.decrypt(self.authconfig['vc_pwd'])), 
                form.Textbox("Cluster",value=self.authconfig['cluster']),
                form.Textbox("Host",value=self.authconfig['host']))() 

        self.si = None
        self.categories=['security','performance','availability','manageability','recoverability','reliability','post-install']
        self.category=None

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
        
        for category in self.categories:
            x.add_row([category,"Run "+category+' category'])
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
        elif args[0] in self.categories:
            self.category=args[0]
            check_groups_run = check_groups
            if len(args) > 1:
                self.usage("Parameter not expected after categories")
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
        
        for check_group in check_groups_run:
            
            self.reporter.notify_progress(self.reporter.notify_checkGroup,check_group)
            
            for check in self.config[check_group]:
                self.reporter.notify_progress(self.reporter.notify_checkName,check['name'])              
                if self.category!=None: #condition for category 
                    if self.category not in check['category']:
                        continue
                          
                self.reporter.notify_progress(self.reporter.notify_checkName,check['name'])
                passed, message = self.validate_vc_property(check['path'], check['operator'], check['ref-value'])
                try:
                    self.realtime_results = json.load(open("display_json.json","r"))
                    all_prop,props = [ x for x in message.split(', ') if x != ''], []
                    for xprop in all_prop:
                        xprop,xstatus = xprop.split("#")
                        
                        xprop_msg, xprop_actual, xprop_exp = xprop.split("=")
                        if xprop_msg == "":
                            xprop_msg = check['name']
                        xprop_actual = xprop_actual.split(' (')[0] or xprop_actual.split(' ')[0] or "None"
                        
                        if check['operator'] == "=": 
                            
                            xprop_exp = check['ref-value'] or "None"
                        elif check['operator'] == "!=":
                            xprop_exp = "Not equal to "+(check['ref-value']  or "None")
                        elif check['operator'] == "<=":
                            if check['ref-value'].startswith("content."):
                                xprop_exp = xprop_exp.split(')')[0] or xprop_exp.split(') ')[0] or "None"
                                xprop_exp = "Less than or Equal to "+xprop_exp
                            else:
                                xprop_exp = "Less than or Equal to "+( check['ref-value'] or "None" )
                        
                        if xprop_exp == "none":
                            xprop_exp = "None"
                        if xprop_actual == "none":
                            xprop_actual = "None"
                            
                        #props.append({"Message":xprop_msg,"Status":xstatus,"Expected":xprop_exp , "Actual":xprop_actual })
                        xporp_act_msg = xprop_msg.replace('NoName@','').replace("NoName",'').replace('@','.')    
                        props.append({"Message":xporp_act_msg,"Status":xstatus,"Expected":xprop_exp , "Actual":xprop_actual })

                    self.realtime_results['vc']['checks'].append({'Message':check['name'] ,'Status': (passed and "PASS" or "FAIL"),"Properties": props})
                    with open("display_json.json", "w") as myfile:
                        json.dump(self.realtime_results, myfile)
                except:
                    # Need to handle temp-file case for command line
                    pass
                self.result.add_check_result(CheckerResult(check['name'], None, passed, message, check['category'],check['path'],check['expectedresult']))
                passed_all = passed_all and passed
            
            if check_group in check_functions:
                for check_function in check_functions[check_group]:
                    
                    if self.category!=None:#condition for category for custom checks 
                        if self.category not in check_function.category:
                            continue
                             
                    passed, message,path = check_function()
                    try:
                        self.realtime_results = json.load(open("display_json.json","r"))
                        all_prop,props = [ x for x in message.split(', ') if x != ''], []
                        for xprop in all_prop:
                            xprop,xstatus = xprop.split("#")
                            xprop_msg, xprop_actual, xprop_exp = xprop.split("=")
                            xprop_actual = xprop_actual.split('(')[0] or  xprop_actual.split(' (')[0] or xprop_actual.split(' ')[0] or "None"
                            xprop_exp = xprop_exp.split(")")[0] or xprop_exp.split(" )")[0] or "None"
                             
                            if xprop_exp == "none":
                                xprop_exp = "None"
                            if xprop_actual == "none":
                                xprop_actual = "None"
                             
                            #props.append({"Message":xprop_msg,"Status":xstatus,"Expected":xprop_exp , "Actual":xprop_actual })
                            xporp_act_msg = xprop_msg.replace('NoName@','').replace("NoName",'').replace('@','.')
                            props.append({"Message":xporp_act_msg,"Status":xstatus,"Expected":xprop_exp , "Actual":xprop_actual })
                         
                        self.realtime_results['vc']['checks'].append({'Message':check_function.descr ,'Status': (passed and "PASS" or "FAIL"),"Properties": props})
                        with open("display_json.json", "w") as myfile:
                            json.dump(self.realtime_results, myfile)
                    except:
                        pass
                    self.result.add_check_result(CheckerResult(check_function.descr, None, passed, message, check_function.category, path,check_function.expected_result))
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
        
#         if props == None:
#             passed =  VCChecker.apply_operator(props, expected, operator)
#             message = path + "=" + "None" + " (Expected: " + operator + expected + ") "
#             message_all += (", "+message+"#"+(passed and "PASS" or "FAIL")) 
#             passed_all = passed_all and passed
#             self.reporter.notify_progress(self.reporter.notify_checkLog, message, passed and "PASS" or "FAIL")
#             return False, message_all
        
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
        
        if actual == 'Not-Configured' or expected  == 'Not-Configured':
            return  False
        
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
            return {"@".join(name): "Not-Configured"}
        except:
            print "Unknow error"     
        

        name_added = False
        if hasattr(cur_obj, "name"):  #and cur_obj.name not in name:
            name.append(cur_obj.name)
            name_added = True
        else:
            name.append("NoName")

        if len(xpath) == 1:
            return {"@".join(name): attr}

        if isinstance(attr, list):
            vals = {}

            for item in attr:
                filter_names = []
                filter_pass = self.apply_filter(item, filter, filter_names)

                if filter_pass:
                    attr_val = self.retrieve_vc_property(xpath[1:], item, name + filter_names,cluster_level_entity)
                    if attr_val:
                        vals.update(attr_val)

#             if name_added:
#                 name.pop()

            if vals == {}:
                vals={"@".join(name): "Not-Configured"}
            
            return vals

        else:
            filter_names = []
            filter_pass = self.apply_filter(attr, filter, filter_names)
            result = filter_pass and self.retrieve_vc_property(xpath[1:], attr, name + filter_names,cluster_level_entity) or None
#             if name_added:
#                 name.pop()
                        
            return result


    def get_vc_property(self, path):
        return self.retrieve_vc_property(string.split(path, '.'), self.si, [])


        # Manual checks
    
    @checkgroup("cluster_checks", "Validate datastore heartbeat", ["availability"],"Heatbeat Datastore Name")
    def check_datastore_heartbeat(self):
        path='content.rootFolder.childEntity.hostFolder.childEntity.datastore'
        datastores = self.get_vc_property(path)
        heartbeat_datastores = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.configuration.dasConfig.heartbeatDatastore')
        passed = False
        message = ""
        message_all = ""
        for cluster, cluster_datastores in datastores.iteritems():
            if cluster_datastores == 'Not-Configured':
                passed = False
                self.reporter.notify_progress(self.reporter.notify_checkLog,cluster+"="+"Datastore-Not-Configured (Expected: =True) " , (False and "PASS" or "FAIL"))
                message += ", " +cluster+"=Datastore-Not-Configured (Expected: =True) "+"#"+((False) and "PASS" or "FAIL")
                continue
            
            try:
                cluster_heartbeat_datastores = [ds.name for ds in heartbeat_datastores[cluster]]
            except KeyError:
                cluster_heartbeat_datastores = []
               
            for ds in cluster_datastores:
                if not fnmatch.fnmatch(ds.name, 'NTNX-*'):
                    is_heartbeating = ds.name in cluster_heartbeat_datastores
                    self.reporter.notify_progress(self.reporter.notify_checkLog,cluster+"."+ds.name+"="+str(is_heartbeating) + " (Expected: =True) " , (is_heartbeating and "PASS" or "FAIL"))
                    passed = passed and is_heartbeating
                    message += ", " +cluster+"@"+ds.name+"="+str(is_heartbeating) + " (Expected: =True) "+"#"+((is_heartbeating) and "PASS" or "FAIL")
 
        return passed, message,path
    
    @checkgroup("cluster_checks", "VSphere Cluster Nodes in Same Version", ["availability"],"All Nodes in Same Version")
    def check_vSphere_cluster_nodes_in_same_version(self):
            path='content.rootFolder.childEntity'
            root = self.get_vc_property(path) or {}
            message = ""
            passed_all = True
    
            for dc, dcInfo in root.iteritems():
                for xdc in dcInfo:
                    for xcluster in xdc.hostFolder.childEntity:
                        passed = True
                        mult_vers_flag, versions = False, [] 
                        hosts = xcluster.host
                                                   
                        for xhost in hosts:
                            nodeInfo = xhost.config.product 
                            if len(versions) == 0:
                                versions.append(nodeInfo.version)
                            else:
                                if nodeInfo.version not in versions:
                                    passed = False
                                    versions.append(nodeInfo.version)
                                    mult_vers_flag = True
                        
                        if len(versions) == 0: # to test weather any HOST configured to cluster
                            mult_vers_flag = True
                            versions = "Not-Configured"
                        
                        self.reporter.notify_progress(self.reporter.notify_checkLog,"Datacenters."+xdc.name+"."+xcluster.name + "=" + str(versions) + " (Expected: =Multiple versions not present) " , (not mult_vers_flag and "PASS" or "FAIL"))
                        message += ", "+"@Datacenters@"+xdc.name+"@"+xcluster.name + "="+str(versions)+" (Expected: =Multiple versions not present)#"+(not mult_vers_flag and "PASS" or "FAIL")   
                        passed_all = passed_all and passed    
            return passed_all, message,path
    
    @checkgroup("cluster_checks", "Cluster Advance Settings das.isolationaddress1",["availability"],"IP Address of any Nutanix CVM")
    def check_cluster_das_isolationaddress1(self):
        path='content.rootFolder.childEntity.hostFolder.childEntity'
        all_cluster = self.get_vc_property(path) or {}
        message = ""
        passed_all = True
        passed = False
        for datacenter, clusters in all_cluster.iteritems():
            try:
                if len(clusters)==0:
                    raise AttributeError
                
                for cluster in clusters:
                    passed = False
                    cluster_name=cluster.name
                    
                    nics = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity[name='+cluster_name+'].configurationEx.dasVmConfig.key[name=NTNX*CVM].guest.net')
                    cluster_all_ips = []
                    cluster_str = ''
                    for nic, nicInfo in nics.iteritems():
                        if nicInfo != 'Not-Configured': 
                            cluster_all_ips.extend(nicInfo[0].ipAddress)
                    for item in cluster_all_ips:
                        cluster_str += item + " "
                    
                    options=cluster.configuration.dasConfig.option
                    if len(options)!=0:
                        has_isolationaddress1=False
                        isolationaddress1=None
                        for option in options:
                            if option.key=='das.isolationaddress1':
                                has_isolationaddress1=True
                                #print cluster_name, option.key, option.value
                                isolationaddress1=option.value
                                passed = isolationaddress1 in cluster_all_ips
                                self.reporter.notify_progress(self.reporter.notify_checkLog,  datacenter +"@"+cluster_name+ "=" + str(isolationaddress1) + "(Expected: =Among:"+str(cluster_all_ips)+")", (passed and "PASS" or "FAIL"))
                                message += ", "+datacenter +"@"+cluster_name+"="+str(isolationaddress1)+" (Expected: =Among:["+cluster_str+"])#"+(passed and "PASS" or "FAIL")
                            if has_isolationaddress1==True:
                                if option.key=='das.isolationaddress2' or option.key=='das.isolationaddress3':
                                    if isolationaddress1 == option.value:
                                        passed_all=False
                                        self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter +"@"+cluster_name+ "=Advance setting has duplicated value with das.isolationaddress2 or das.isolationaddress3  (Expected: =Among:"+str(cluster_all_ips)+")", (False and "PASS" or "FAIL"))
                                        message += ", "+datacenter +"@"+cluster_name+"=Advance setting has duplicated value with das.isolationaddress2 or das.isolationaddress3 (Expected: =Among:["+cluster_str+"])#"+(False and "PASS" or "FAIL")
                                    
                        if has_isolationaddress1==False:
                            passed_all=False
                            self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter +"@"+cluster_name+ "=Not-Configured (Expected: =Among:"+str(cluster_all_ips)+")", (False and "PASS" or "FAIL"))
                            message += ", "+datacenter +"@"+cluster_name+"=Not-Configured (Expected: =Among:["+cluster_str+"])#"+(False and "PASS" or "FAIL")
                    else:
                        passed_all=False
                        self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter +"@"+cluster_name+ "=Not-Configured (Expected: =Among:"+str(cluster_all_ips)+")", (False and "PASS" or "FAIL"))
                        message += ", "+datacenter +"@"+cluster_name+"=Not-Configured (Expected: =Among:["+cluster_str+"])#"+(False and "PASS" or "FAIL")
                
            except AttributeError:
                passed_all=False
                self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter +"@"+ "=Not-Configured (Expected: =Among:"+str(cluster_all_ips)+")", (False and "PASS" or "FAIL"))
                message += ", "+datacenter +"@"+"=Not-Configured (Expected: =Among:["+cluster_str+"])#"+(False and "PASS" or "FAIL")
            passed_all = passed_all and passed
        return passed_all , message,path
    
    @checkgroup("cluster_checks", "Cluster Advance Settings das.isolationaddress2",["availability"],"IP Address of any Nutanix CVM")
    def check_cluster_das_isolationaddress2(self):
        path='content.rootFolder.childEntity.hostFolder.childEntity'
        all_cluster = self.get_vc_property(path) or {}
        message = ""
        passed_all = True
        passed = False
        for datacenter, clusters in all_cluster.iteritems():
            try:
                if len(clusters)==0:
                    raise AttributeError
                for cluster in clusters:
                    passed = False
                    cluster_name=cluster.name
                    
                    nics = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity[name='+cluster_name+'].configurationEx.dasVmConfig.key[name=NTNX*CVM].guest.net')
                    cluster_all_ips = []
                    cluster_str = ''
                    for nic, nicInfo in nics.iteritems():
                        if nicInfo != 'Not-Configured': 
                            cluster_all_ips.extend(nicInfo[0].ipAddress)
                    for item in cluster_all_ips:
                        cluster_str += item + " "
                    
                    options=cluster.configuration.dasConfig.option
                    if len(options)!=0:
                        has_isolationaddress2=False
                        isolationaddress2=None
                        for option in options:
                            if option.key=='das.isolationaddress2':
                                has_isolationaddress2=True
                                #print cluster_name, option.key, option.value
                                isolationaddress2=option.value
                                passed = isolationaddress2 in cluster_all_ips
                                self.reporter.notify_progress(self.reporter.notify_checkLog,  datacenter +"@"+cluster_name+ "=" + str(isolationaddress2) + "(Expected: =Among:"+str(cluster_all_ips)+")", (passed and "PASS" or "FAIL"))
                                message += ", "+datacenter +"@"+cluster_name+"="+str(isolationaddress2)+" (Expected: =Among:["+cluster_str+"])#"+(passed and "PASS" or "FAIL")
                            
                            if has_isolationaddress2==True:
                                if option.key=='das.isolationaddress1' or option.key=='das.isolationaddress3':
                                    if isolationaddress2 == option.value:
                                        passed_all=False
                                        self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter +"@"+cluster_name+ "=Advance setting has duplicated value with das.isolationaddress1 or das.isolationaddress3  (Expected: =Among:"+str(cluster_all_ips)+")", (False and "PASS" or "FAIL"))
                                        message += ", "+datacenter +"@"+cluster_name+"=Advance setting has duplicated value with das.isolationaddress1 or das.isolationaddress3 (Expected: =Among:["+cluster_str+"])#"+(False and "PASS" or "FAIL")
                                    
                        if has_isolationaddress2==False:
                            passed_all=False
                            self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter +"@"+cluster_name+ "=Not-Configured (Expected: =Among:"+str(cluster_all_ips)+")", (False and "PASS" or "FAIL"))
                            message += ", "+datacenter +"@"+cluster_name+"=Not-Configured (Expected: =Among:["+cluster_str+"])#"+(False and "PASS" or "FAIL")
                    else:
                       self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter +"@"+cluster_name+ "=Not-Configured (Expected: =Among:"+str(cluster_all_ips)+")", (False and "PASS" or "FAIL"))
                       message += ", "+datacenter +"@"+cluster_name+"=Not-Configured (Expected: =Among:["+cluster_str+"])#"+(False and "PASS" or "FAIL")

            except AttributeError:
                passed_all=False
                self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter +"@"+ "=Not-Configured (Expected: =Among:"+str(cluster_all_ips)+")", (False and "PASS" or "FAIL"))
                message += ", "+datacenter +"@"+"=Not-Configured (Expected: =Among:["+cluster_str+"])#"+(False and "PASS" or "FAIL")
            
            passed_all = passed_all and passed
        return passed_all , message,path
    
    @checkgroup("cluster_checks", "Cluster Advance Settings das.isolationaddress3",["availability"],"IP Address of any Nutanix CVM")
    def check_cluster_das_isolationaddress3(self):
        path='content.rootFolder.childEntity.hostFolder.childEntity'
        all_cluster = self.get_vc_property(path) or {}
        message = ""
        passed_all = True
        passed = False
        for datacenter, clusters in all_cluster.iteritems():
            try:
                if len(clusters)==0:
                    raise AttributeError
                for cluster in clusters:
                    passed = False
                    cluster_name=cluster.name
                    
                    nics = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity[name='+cluster_name+'].configurationEx.dasVmConfig.key[name=NTNX*CVM].guest.net')
                    cluster_all_ips = []
                    cluster_str = ''
                    for nic, nicInfo in nics.iteritems():
                        if nicInfo != 'Not-Configured': 
                            cluster_all_ips.extend(nicInfo[0].ipAddress)
                    for item in cluster_all_ips:
                        cluster_str += item + " "
                    
                    options=cluster.configuration.dasConfig.option
                    if len(options)!=0:
                        has_isolationaddress3=False
                        isolationaddress3=None
                        for option in options:
                            if option.key=='das.isolationaddress3':
                                has_isolationaddress3=True
                                #print cluster_name, option.key, option.value
                                isolationaddress3=option.value
                                passed = isolationaddress3 in cluster_all_ips
                                self.reporter.notify_progress(self.reporter.notify_checkLog,  datacenter +"@"+cluster_name+ "=" + str(isolationaddress3) + "(Expected: =Among:"+str(cluster_all_ips)+")", (passed and "PASS" or "FAIL"))
                                message += ", "+datacenter +"@"+cluster_name+"="+str(isolationaddress3)+" (Expected: =Among:["+cluster_str+"])#"+(passed and "PASS" or "FAIL")
                            
                            if has_isolationaddress3==True:
                                if option.key=='das.isolationaddress1' or option.key=='das.isolationaddress2':
                                    if isolationaddress3 == option.value:
                                        passed_all=False
                                        self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter +"@"+cluster_name+ "=Advance setting has duplicated value with das.isolationaddress1 or das.isolationaddress3  (Expected: =Among:"+str(cluster_all_ips)+")", (False and "PASS" or "FAIL"))
                                        message += ", "+datacenter +"@"+cluster_name+"=Advance setting has duplicated value with das.isolationaddress1 or das.isolationaddress2 (Expected: =Among:["+cluster_str+"])#"+(False and "PASS" or "FAIL")
                                    
                        if has_isolationaddress3==False:
                            passed_all=False
                            self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter +"@"+cluster_name+ "=Not-Configured (Expected: =Among:"+str(cluster_all_ips)+")", (False and "PASS" or "FAIL"))
                            message += ", "+datacenter +"@"+cluster_name+"=Not-Configured (Expected: =Among:["+cluster_str+"])#"+(False and "PASS" or "FAIL")
                    else:
                       self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter +"@"+cluster_name+ "=Not-Configured (Expected: =Among:"+str(cluster_all_ips)+")", (False and "PASS" or "FAIL"))
                       message += ", "+datacenter +"@"+cluster_name+"=Not-Configured (Expected: =Among:["+cluster_str+"])#"+(False and "PASS" or "FAIL")

            except AttributeError:
                passed_all=False
                self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter +"@"+ "=Not-Configured (Expected: =Among:"+str(cluster_all_ips)+")", (False and "PASS" or "FAIL"))
                message += ", "+datacenter +"@"+"=Not-Configured (Expected: =Among:["+cluster_str+"])#"+(False and "PASS" or "FAIL")
            
            passed_all = passed_all and passed
        return passed_all , message,path
 
    @checkgroup("cluster_checks", "Cluster Advance Settings das.ignoreInsufficientHbDatastore",["availability"],"True")
    def check_cluster_das_ignoreInsufficientHbDatastore(self):
        path='content.rootFolder.childEntity.hostFolder.childEntity.configuration.dasConfig.option'
        all_cluster_options = self.get_vc_property(path) or {}
        clusters_with_given_option = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.configuration.dasConfig.option[key=das*ignoreInsufficientHbDatastore].value') or {}
        message = ""
        passed_all = True
        for cluster, options in all_cluster_options.iteritems():
            passed = True
            if cluster in clusters_with_given_option.keys():
                
                if clusters_with_given_option[cluster] == "true":
                    self.reporter.notify_progress(self.reporter.notify_checkLog,  cluster+"=true (Expected: =true)", (passed and "PASS" or "FAIL"))
                    message += ", "+cluster +"=true (Expected: =true)#"+(passed and "PASS" or "FAIL")
                else:
                    passed = False
                    self.reporter.notify_progress(self.reporter.notify_checkLog,  cluster +"=false (Expected: =true)", (passed and "PASS" or "FAIL"))
                    message += ", "+cluster +"=false (Expected: =true)#"+(passed and "PASS" or "FAIL")
            else:
                passed = False
                self.reporter.notify_progress(self.reporter.notify_checkLog,  cluster + "=Not-Configured (Expected: =true)", (passed and "PASS" or "FAIL"))
                message += ", "+cluster +"=Not-Configured (Expected: =true)#"+(passed and "PASS" or "FAIL")
            passed_all = passed_all and passed
        return passed_all , message,path
    
#     @checkgroup("cluster_checks", "Cluster Advance Settings das.useDefaultIsolationAddress",["availability"],"False")
#     def check_cluster_das_useDefaultIsolationAddress(self):
#         path='content.rootFolder.childEntity.hostFolder.childEntity.configuration'
#         all_cluster_hosts = self.get_vc_property(path) or {}
#         clusters_with_given_option = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.configuration.dasConfig.option[key=das*useDefaultIsolationAddress].value') or {}
#         message = ""
#         passed_all = True
#         for cluster, options in all_cluster_hosts.iteritems():
#             passed = True
#             if cluster in clusters_with_given_option.keys():
#                 if clusters_with_given_option[cluster] == "false":
#                     self.reporter.notify_progress(self.reporter.notify_checkLog,  cluster +"=false (Expected: =false)", (passed and "PASS" or "FAIL"))
#                     message += ", "+cluster +"=false (Expected: =false)#"+(passed and "PASS" or "FAIL")
#                 else:
#                     passed = False
#                     self.reporter.notify_progress(self.reporter.notify_checkLog,  cluster +"=true (Expected: =false)", (passed and "PASS" or "FAIL"))
#                     message += ", "+cluster +"=true (Expected: =false)#"+(passed and "PASS" or "FAIL")
#             else:
#                 passed = False
#                 self.reporter.notify_progress(self.reporter.notify_checkLog,  cluster + "=Not-Configured (Expected: =true )", (passed and "PASS" or "FAIL"))
#                 message += ", "+cluster +"=Not-Configured (Expected: =false)#"+(passed and "PASS" or "FAIL")
#                      
#             passed_all = passed_all and passed
#         return passed_all , message,path
    
    @checkgroup("cluster_checks", "Cluster Load Balanced",["performance"],"Load Balanced")
    def check_cluster_load_balanced(self):
        path_curr='content.rootFolder.childEntity.hostFolder.childEntity.summary.currentBalance'
        current_balance = self.get_vc_property(path_curr)
        path_tar='content.rootFolder.childEntity.hostFolder.childEntity.summary.targetBalance'
        target_balance = self.get_vc_property(path_tar)
        message = ""
        passed_all = True
        
        for current_key in current_balance:
            passed = True
            if (current_balance[current_key]<=target_balance[current_key]) and (current_balance[current_key] != -1000) and (target_balance[current_key]!=-1000) and (current_balance[current_key] != "Not-Configured") and (target_balance[current_key]!="Not-Configured") :
                self.reporter.notify_progress(self.reporter.notify_checkLog,  current_key + "="+str(current_balance[current_key])+" (Expected: <="+str(target_balance[current_key])+" )", ("PASS"))
                message += ", "+current_key + "="+str(current_balance[current_key])+" (Expected: <="+str(target_balance[current_key])+")#PASS"
            else:
                cur_bal= "NA" if current_balance[current_key]== -1000 else current_balance[current_key]
                tar_bal= "Load balanced"if (target_balance[current_key]==-1000 or target_balance[current_key]=="Not-Configured") else target_balance[current_key]  
                self.reporter.notify_progress(self.reporter.notify_checkLog, current_key + "="+str(cur_bal)+" (Expected: <="+str(tar_bal)+" )", ("FAIL"))
                message += ", "+current_key + "="+str(cur_bal)+" (Expected: <="+str(tar_bal)+")#FAIL"             
            
            passed_all = passed_all and passed
        
        return passed_all , message,path_curr
    
    @checkgroup("esxi_checks", "Validate the Directory Services Configuration is set to Active Directory",["security"],"True")
    def check_directory_service_set_to_active_directory(self):
        path='content.rootFolder.childEntity.hostFolder.childEntity.host.config.authenticationManagerInfo.authConfig'
        authenticationStoreInfo = self.get_vc_property(path)
       
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
       
        return passed, message,path
    
    @checkgroup("esxi_checks", "Validate NTP client is set to Enabled and is in the running state",["reliability"],"NTP client is enabled and running.")
    def check_ntp_client_enable_running(self):
        path='content.rootFolder.childEntity.hostFolder.childEntity.host'
        datacenter_hosts =self.get_vc_property(path)
        message = ""
        passed = False
        for datacenter in datacenter_hosts.keys():
            try :
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
                        self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter+"."+host.name+" = NTP Client enable:"+str(ruleset_enable) + " and running:"+str(service_running)+" (Expected: ="+" NTP Client enable: True and running: True "+") " , ((ruleset_enable and service_running) and "PASS" or "FAIL"))
                        passed = passed and ((ruleset_enable and service_running) and "PASS" or "FAIL") 
                        message += ", " +datacenter+"@"+host.name+"= NTP Client enabled:"+str(ruleset_enable) + " and running:"+str(service_running)+" (Expected: = NTP Client enable: True and running: True)#"+ ((ruleset_enable and service_running) and "PASS" or "FAIL")
                    except AttributeError:
                        self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter+"."+host.name+" = NTP Client not configured" , ((ruleset_enable and service_running) and "PASS" or "FAIL"))
                        passed = False
                        message += ", " +datacenter+"@"+host.name+" = NTP Client not configured (Expected: = NTP Client enable: True and running: True )#"+ ((ruleset_enable and service_running) and "PASS" or "FAIL")
            except AttributeError:
                    self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter+" = NTP Client not configured (Expected: = NTP Client enable: True and running: True )" , ((ruleset_enable and service_running) and "PASS" or "FAIL"))
                    passed = False
                    message += ", " +datacenter+" = NTP Client not configured (Expected: = NTP Client enable: True and running: True )#"+ ((ruleset_enable and service_running) and "PASS" or "FAIL")
        
        return passed, message, path
    
    @checkgroup("esxi_checks", "NTP Servers Configured",["availability"],"NTP Servers are configured")
    def check_ntp_servers_configured(self):
        path='content.rootFolder.childEntity.hostFolder.childEntity.host'
        all_hosts = self.get_vc_property(path)
        message = ""
        passed_all = True
        
        for cluster, hostObject in all_hosts.iteritems():
            try:
                
                if len(hostObject) == 0:
                    pass
                    #self.reporter.notify_progress(self.reporter.notify_checkLog, cluster+" = No Hosts are configured ( Expected: = At-least 2 NTP Servers are configured )","FAIL")
                    #passed = False
                    #message += ", " +cluster+"= No Hosts are configured (Expected:= At-least 2 NTP Servers are configured ) #FAIL"
                else:
                    for host in hostObject:
                        passed = True
                        ntp_servers = host.config.dateTimeInfo.ntpConfig.server
                        ntp_servers_str = ' '.join(ntp_servers)
                        if len(ntp_servers) < 2:
                            passed = False
                            self.reporter.notify_progress(self.reporter.notify_checkLog, cluster+"."+host.name+" = NTP Servers configured ["+','.join(ntp_servers)+"]  (Expected: = at-least 2 NTP Servers are configured )","FAIL")
                            message += ", " +cluster+"@"+host.name+"="+','.join(ntp_servers)+" (Expected: =At-least 2 NTP Servers are configured ) #FAIL"
                        else:
                            self.reporter.notify_progress(self.reporter.notify_checkLog, cluster+"."+host.name+" = NTP Servers configured ["+','.join(ntp_servers)+"]  (Expected: = at-least 2 NTP Servers are configured )","PASS")
                            message += ", " +cluster+"@"+host.name+"="+','.join(ntp_servers)+" (Expected: =At-least 2 NTP Servers are configured ) #PASS"     
                        
                        passed_all = passed_all and passed
            except AttributeError:
                    self.reporter.notify_progress(self.reporter.notify_checkLog, cluster+"=Not-Configured (Expected: =At-least 2 NTP Servers are configured )","FAIL")
                    message += ", " +cluster+"=Not-Configured (Expected: =At-least 2 NTP Servers are configured ) #FAIL"     
                    passed = False
                    
        
        return passed_all,message,path

    @checkgroup("vcenter_server_checks", "Validate vCenter Server License Expiration Date",["availability"],"No expiration date or expiration date less than 60 days")
    def check_vcenter_server_license_expiry(self):
        expirationDate = self.get_vc_property('content.licenseManager.evaluation.properties[key=expirationDate].value')
        
        message = ""
        passed = False
        for item, expiry_date in expirationDate.iteritems():
            #Currently timezone is not considered for the date difference / Need to add
            xexpiry = datetime.datetime(expiry_date.year,expiry_date.month, expiry_date.day)
            
            valid_60_days = (xexpiry - (datetime.datetime.today() + datetime.timedelta(60))).days > 60 or (xexpiry - (datetime.datetime.today() + datetime.timedelta(60))).days < 0
            self.reporter.notify_progress(self.reporter.notify_checkLog,"License Expiration Validation date:: " + str(expiry_date) + " (Expected: =Not within next 60 days or always valid)" , (valid_60_days and "PASS" or "FAIL"))
            passed = passed and valid_60_days
            message += ", "+"License Expiration Validation = " + str(expiry_date) + " (Expected: =Not within next 60 days or always valid) "+"#"+((valid_60_days) and "PASS" or "FAIL")
        return passed, message,''
    
    @checkgroup("vcenter_server_checks", "Validate vCenter Server has VMware Tools installed and is up to date",["performance"],"Tools Ok")
    def check_vcenter_server_tool_status(self):
        vcenter_ipv4 = self.get_vc_property('content.setting.setting[key=VirtualCenter*AutoManagedIPV4].value')
        vcenter_ip= None
        for key,ip in vcenter_ipv4.iteritems():
            vcenter_ip=ip
        vms = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.host.vm.guest')
         
        message = ""
        passed = True
        for vm in vms.keys():
            guest_info=vms[vm]
            if guest_info != "Not-Configured":
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
         
        return passed,message,''
    
    @checkgroup("network_and_switch_checks", "Virtual Distributed Switch - Network IO Control",["performance"],"Enabled")
    def check_virtual_distributed_switch_networ_io_control(self):
        path='content.rootFolder.childEntity.networkFolder.childEntity'
        datacenter_networks = self.get_vc_property(path)
       
        message = ""
        passed = True
        for datacenter in datacenter_networks.keys():
            network_list = datacenter_networks.get(datacenter)
            dvs_found=False
            for network in network_list:
                if isinstance(network,vim.dvs.VmwareDistributedVirtualSwitch):
                    dvs_found=True
                    nioc_enabled=network.config.networkResourceManagementEnabled
                    self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter+"."+network.name+"="+str(nioc_enabled) + " (Expected: =True) " , (nioc_enabled and "PASS" or "FAIL"))
                    message += ", " +datacenter+"@"+network.name+"="+str(nioc_enabled) + " (Expected: =True) "+"#"+((nioc_enabled) and "PASS" or "FAIL")
                    passed = passed and nioc_enabled
            
            if dvs_found == False:
                passed =False
                self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter+"@=Not-Configured (Expected: =True) " , (False and "PASS" or "FAIL"))
                message += ", " +datacenter+"=Not-Configured (Expected: =True) "+"#"+((False) and "PASS" or "FAIL")
                    
                
        return passed, message, path
        
    @checkgroup("network_and_switch_checks", "Virtual Distributed Switch - MTU",["performance"],"1500")
    def check_virtual_distributed_switch_mtu(self):
        path='content.rootFolder.childEntity.networkFolder.childEntity'
        datacenter_networks = self.get_vc_property(path)
       
        message = ""
        pass_all=True
        for datacenter in datacenter_networks.keys():
            network_list = datacenter_networks.get(datacenter)
            dvs_found=False
            maxMtu_expected=1500
            for network in network_list:
                if isinstance(network,vim.dvs.VmwareDistributedVirtualSwitch):
                    dvs_found=True
                    maxMtu=network.config.maxMtu
                    # default value for maxMtu is 1500. Sometime MOB returns None value. So setting maxMtu value to 1500 as default
                    if maxMtu is None: 
                        maxMtu=1500
                    
                    if maxMtu == maxMtu_expected:
                        message += ", " +datacenter+"@"+network.name+"@="+str(maxMtu) + " (Expected: ="+str(maxMtu_expected)+")"+"#"+(True and "PASS" or "FAIL")
                        self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter+"."+network.name+"="+str(maxMtu) + " (Expected: ="+str(maxMtu_expected)+") " , ( True and "PASS" or "FAIL"))
                    else:
                        pass_all=False
                        self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter+"."+network.name+"="+str(maxMtu) + " (Expected: ="+str(maxMtu_expected)+") " , ( False and "PASS" or "FAIL"))
                        message += ", " +datacenter+"@"+network.name+"@="+str(maxMtu) + " (Expected: ="+str(maxMtu_expected)+")"+"#"+(False and "PASS" or "FAIL")
            
            if dvs_found==False:
                pass_all=False
                self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter+"=Not-Configured (Expected: ="+str(maxMtu_expected)+") " , ( False and "PASS" or "FAIL"))
                message += ", " +datacenter+"@=Not-Configured (Expected: ="+str(maxMtu_expected)+")"+"#"+(False and "PASS" or "FAIL")
            
        
        return pass_all, message, path
    
    @checkgroup("storage_and_vm_checks", "Hardware Acceleration of Datastores", ["performance"], "Supported")
    def check_vStorageSupport(self):
        path ='content.rootFolder.childEntity.hostFolder.childEntity'
        datacenter_host = self.get_vc_property(path)
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
                                message += ", " +host_domain+"@"+ClusterComputeRrc.name+"@"+datastore.name+"="+vStorageSupport+ " (Expected: ="+expected_vStorageSupported+")"+"#"+(True and "PASS" or "FAIL")
                                self.reporter.notify_progress(self.reporter.notify_checkLog, host_domain+"."+ClusterComputeRrc.name+"."+datastore.name+"="+vStorageSupport+ " (Expected: ="+expected_vStorageSupported+")" , ( True and "PASS" or "FAIL"))
                            else:
                                pass_all=False
                                # To handle None Value
                                new_vStorageSupport= vStorageSupport if vStorageSupport else "None"
                                message += ", " +host_domain+"@"+ClusterComputeRrc.name+"@"+datastore.name+"="+new_vStorageSupport + " (Expected: ="+expected_vStorageSupported+")"+"#"+(False and "PASS" or "FAIL")
                                self.reporter.notify_progress(self.reporter.notify_checkLog, host_domain+"."+ClusterComputeRrc.name+"."+datastore.name+"="+new_vStorageSupport+ " (Expected: ="+expected_vStorageSupported+")" , ( False and "PASS" or "FAIL"))
            
                except AttributeError:
                    pass_all=False 
                    message += ", " + host_domain+"@"+ClusterComputeRrc.name+"="+ "DataStore not attached"+ " (Expected: ="+expected_vStorageSupported+")"+"#"+(False and "PASS" or "FAIL")
                    self.reporter.notify_progress(self.reporter.notify_checkLog, host_domain+"."+ClusterComputeRrc.name+"="+ "DataStore not attached"+ " (Expected: ="+expected_vStorageSupported+")", ( False and "PASS" or "FAIL"))
                     
        return pass_all, message,path+'.datastore'