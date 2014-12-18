from __future__ import division
from bdb import effective
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
   
    @checkgroup("cluster_checks", "Cluster Advance Settings das.ignoreInsufficientHbDatastore",["availability"],"True")
    def check_cluster_das_ignoreInsufficientHbDatastore(self):
        path='content.rootFolder.childEntity.hostFolder.childEntity'
        cluster_map = self.get_vc_property(path)
        passed = True
        message = ""
        message_all = ""
        for clusters_key, clusters in cluster_map.iteritems():
            if clusters!="Not-Configured":
                for cluster in clusters:
                    cluster_name=cluster.name
                    
                    if self.authconfig['cluster']!='':
                        if cluster_name not in self.authconfig['cluster']:
                            #print "skipping "+cluster_name
                            continue
                    
                    if not isinstance(cluster, vim.ClusterComputeResource):
                        #condition to check if any host attached to datacenter without adding to any cluster
                        continue
                    heartbeatDatastoreInfos=cluster.RetrieveDasAdvancedRuntimeInfo.__call__().heartbeatDatastoreInfo
                    if len(heartbeatDatastoreInfos)>=1:                        
                        is_option_set=False
                        for option in cluster.configuration.dasConfig.option:
                            if option.key=="das.ignoreInsufficientHbDatastore":
                                #print cluster_name , option.value
                                passed = False
                                if option.value=='true':
                                    self.reporter.notify_progress(self.reporter.notify_checkLog,  clusters_key  +'@'+cluster_name+ "=true (Expected: =true)", (True and "PASS" or "FAIL"))
                                    message += ", "+clusters_key  +'@'+cluster_name+ "=true (Expected: =true)#"+(True and "PASS" or "FAIL")
                                else:
                                    self.reporter.notify_progress(self.reporter.notify_checkLog,  clusters_key  +'@'+cluster_name+ "=false (Expected: =true)", (False and "PASS" or "FAIL"))
                                    message += ", "+clusters_key  +'@'+cluster_name+ "=false (Expected: =true)#"+(False and "PASS" or "FAIL")
                                is_option_set=True
                                break
                            
                        if is_option_set == False:
                            passed = False
                            self.reporter.notify_progress(self.reporter.notify_checkLog,  clusters_key +'@'+cluster_name+ "=Not-Configured (Expected: =true)", (False and "PASS" or "FAIL"))
                            message += ", "+clusters_key +"=Not-Configured (Expected: =true)#"+(False and "PASS" or "FAIL")
        return passed, message,path
   
   
    
    @checkgroup("cluster_checks", "Validate Datastore Heartbeat", ["availability"],"Heatbeat Datastore Name")
    def check_datastore_heartbeat(self):
        path='content.rootFolder.childEntity.hostFolder.childEntity'
        cluster_map = self.get_vc_property(path)
        passed = True
        message = ""
        message_all = ""
        for clusters_key, clusters in cluster_map.iteritems():
            if clusters!="Not-Configured":
                for cluster in clusters:
                    cluster_name=cluster.name
                    
                    if self.authconfig['cluster']!='':
                        if cluster_name not in self.authconfig['cluster']:
                            #print "skipping "+cluster_name
                            continue
                        
                    if not isinstance(cluster, vim.ClusterComputeResource):
                        #condition to check if any host attached to datacenter without adding to any cluster
                        continue
                    heartbeatDatastoreInfos=cluster.RetrieveDasAdvancedRuntimeInfo.__call__().heartbeatDatastoreInfo
                    if len(heartbeatDatastoreInfos)==0:
                        passed = False
                        self.reporter.notify_progress(self.reporter.notify_checkLog,clusters_key+"@"+cluster_name+"=Not-Configured (Expected: =Datastore Name) " , (False and "PASS" or "FAIL"))
                        message += ", " +clusters_key+"@"+cluster_name+"=Not-Configured (Expected: =Datastore Name) "+"#"+(False and "PASS" or "FAIL")
                    else:
                        datastore_names=[]
                        for heartbeatDatastoreInfo in heartbeatDatastoreInfos:
                            datastore_names.append(heartbeatDatastoreInfo.datastore.name)
                        names=','.join(datastore_names)
                        self.reporter.notify_progress(self.reporter.notify_checkLog,clusters_key+"@"+cluster_name+"="+names+" (Expected: =Datastore Name) " , (True and "PASS" or "FAIL"))
                        message += ", " +clusters_key+"@"+cluster_name+"="+names+" (Expected: =Datastore Name) "+"#"+(True and "PASS" or "FAIL")
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
                        if self.authconfig['cluster']!='':
                            if xcluster.name not in self.authconfig['cluster']:
                                #print "skipping "+xcluster.name
                                continue
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
                    
                    if self.authconfig['cluster']!='':
                        if cluster_name not in self.authconfig['cluster']:
                            #print "skipping "+cluster_name
                            continue
                        
                    
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
                    
                    if self.authconfig['cluster']!='':
                        if cluster_name not in self.authconfig['cluster']:
                            #print "skipping "+cluster_name
                            continue
                        
                    
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
                    
                    if self.authconfig['cluster']!='':
                        if cluster_name not in self.authconfig['cluster']:
                            #print "skipping "+cluster_name
                            continue
                        
                    
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
 
#    @checkgroup("cluster_checks", "Cluster Advance Settings das.ignoreInsufficientHbDatastore",["availability"],"True")
#     def check_cluster_das_ignoreInsufficientHbDatastore(self):
#         path='content.rootFolder.childEntity.hostFolder.childEntity.configuration.dasConfig.option'
#         all_cluster_options = self.get_vc_property(path) or {}
#         clusters_with_given_option = self.get_vc_property('content.rootFolder.childEntity.hostFolder.childEntity.configuration.dasConfig.option[key=das*ignoreInsufficientHbDatastore].value') or {}
#         message = ""
#         passed_all = True
#         for cluster, options in all_cluster_options.iteritems():
#             passed = True
#             if cluster in clusters_with_given_option.keys():
#                 
#                 if clusters_with_given_option[cluster] == "true":
#                     self.reporter.notify_progress(self.reporter.notify_checkLog,  cluster+"=true (Expected: =true)", (passed and "PASS" or "FAIL"))
#                     message += ", "+cluster +"=true (Expected: =true)#"+(passed and "PASS" or "FAIL")
#                 else:
#                     passed = False
#                     self.reporter.notify_progress(self.reporter.notify_checkLog,  cluster +"=false (Expected: =true)", (passed and "PASS" or "FAIL"))
#                     message += ", "+cluster +"=false (Expected: =true)#"+(passed and "PASS" or "FAIL")
#             else:
#                 passed = False
#                 self.reporter.notify_progress(self.reporter.notify_checkLog,  cluster + "=Not-Configured (Expected: =true)", (passed and "PASS" or "FAIL"))
#                 message += ", "+cluster +"=Not-Configured (Expected: =true)#"+(passed and "PASS" or "FAIL")
#             passed_all = passed_all and passed
#         return passed_all , message,path
#     
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
    
    @checkgroup("cluster_checks", "Storage DRS",["performance"],"False")
    def check_cluster_storgae_drs(self):
        path_curr='content.rootFolder.childEntity.datastoreFolder.childEntity'
        storage_clusters_map = self.get_vc_property(path_curr)
        
        message = ""
        passed_all = True
        
        for datacenter, storage_clusters in storage_clusters_map.iteritems():
            passed = True
            if storage_clusters == "Not-Configured":
                continue
            storage_clusters_found=False
            ntnx_datastore_found=False
            storage_cluster_name=None
            for storage_cluster in storage_clusters:
                if not isinstance(storage_cluster, vim.StoragePod):
                    continue
                
                storage_clusters_found=True
                storage_cluster_name=storage_cluster.name
                for datastore in storage_cluster.childEntity:
                    
                    datastore_name=datastore.name
                    if not fnmatch.fnmatch(datastore_name,"NTNX-local-ds*"):
                        #condition to check if NTNX-local name of Datastore found
                        #if not found skip check
                        continue
                    ntnx_datastore_found=True
                    mount_remote_host=datastore.info.nas.remoteHost
                    
                    if mount_remote_host != "192.168.5.2":
                        # condition to check if NTNX-local datastore mounted to 192.168.5.2
                        # if not mounted then skip check
                        continue
                    
                
                    
                    storage_drs= storage_cluster.podStorageDrsEntry.storageDrsConfig.podConfig.enabled
                    self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter +"@"+storage_cluster_name+"@"+datastore_name+"="+str(storage_drs)+" (Expected: =false)", ((not storage_drs) and "PASS" or "FAIL"))
                    message += ", "+datacenter +"@"+storage_cluster_name+"@"+datastore_name+ "="+str(storage_drs)+" (Expected: =false)#"+((not storage_drs) and "PASS" or "FAIL")            
                        
            if storage_clusters_found == False:
                self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter + "=Storage-Cluster-not-found (Expected: =false)", (True and "PASS" or "FAIL"))
                message += ", "+datacenter + "=No-Storage-Cluster-found (Expected: =false)#"+(True and "PASS" or "FAIL")
                passed=False
            elif ntnx_datastore_found==False:
                self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter + "@"+storage_cluster_name+"=NTNX-Datastore-not-found (Expected: =false)", (True and "PASS" or "FAIL"))
                message += ", "+datacenter +"@"+storage_cluster_name+ "=NTNX-Datastore-not-found (Expected: =false)#"+(True and "PASS" or "FAIL")
                passed=False
            
              
            passed_all = passed_all and passed
        
        return passed_all , message,path_curr+".datastore"
    
    @checkgroup("cluster_checks", "Number of DRS Faults",["performance"],"Number of DRS Faults")
    def check_cluster_drs_fault_count(self):
        path_curr='content.rootFolder.childEntity.hostFolder.childEntity.drsFault'
        clusters_map = self.get_vc_property(path_curr)
        
        message = ""
        passed_all = True
        
        for datacenter, clusters_drs_faults in clusters_map.iteritems():
            
            if clusters_drs_faults == "Not-Configured":
                continue
            
            count=len(clusters_drs_faults) if clusters_drs_faults !=None else 0                
            self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter + "="+str(count)+" (Expected: =0)", ((True if count ==0 else False) and "PASS" or "FAIL"))
            message += ", "+datacenter + "="+str(count)+" (Expected: =0)#"+((True if count ==0 else False) and "PASS" or "FAIL") 
            passed = (True if count ==0 else False)
            passed_all = passed_all and passed
        
        return passed_all , message,path_curr
    
    @checkgroup("cluster_checks", "Number of Cluster Events",["performance"],"Number of Cluster Events")
    def check_cluster_events_count(self):
        path_curr='content.rootFolder.childEntity.hostFolder.childEntity.configIssue'
        clusters_map = self.get_vc_property(path_curr)
        
        message = ""
        passed_all = True
        
        for datacenter, clusters_events in clusters_map.iteritems():
            
            if clusters_events == "Not-Configured":
                continue
            
            count=len(clusters_events) if clusters_events !=None else 0                
            self.reporter.notify_progress(self.reporter.notify_checkLog, datacenter + "="+str(count)+" (Expected: =0)", ((True if count ==0 else False) and "PASS" or "FAIL"))
            message += ", "+datacenter + "="+str(count)+" (Expected: =0)#"+((True if count ==0 else False) and "PASS" or "FAIL") 
            passed = (True if count ==0 else False)
            passed_all = passed_all and passed
        
        return passed_all , message,path_curr    
    
    @checkgroup("cluster_checks", "Cluster Memory Utilization %",["performance"],"Memory Consumed %")
    def check_cluster_memory_utilization(self):
        path='content.rootFolder.childEntity.hostFolder.childEntity.summary'
        clusters_summary = self.get_vc_property(path)
        message = ""
        passed_all = True
         
        for clusters_key, clusters_summ in clusters_summary.iteritems():
            
            if clusters_summ == "Not-Configured":
                continue
             
            passed = True
            effectiveMemory =clusters_summ.effectiveMemory
            totalMemory=clusters_summ.totalMemory
            
            if totalMemory > 0:
                effectiveMemory_to_bytes= effectiveMemory* 1000000 # converting to bytes
                cpu_utilization_percentage= round((effectiveMemory_to_bytes*100)/totalMemory,2)
                self.reporter.notify_progress(self.reporter.notify_checkLog, clusters_key + "="+str(cpu_utilization_percentage)+"% (Expected: =memory-consumed-%)", (True and "PASS" or "FAIL"))
                message += ", "+clusters_key + "="+str(cpu_utilization_percentage)+"% (Expected: =memory-consumed-%)#"+(True and "PASS" or "FAIL")
             
            passed_all = passed_all and passed
        return passed_all , message,path
    
    @checkgroup("cluster_checks", "Cluster Memory Overcommitment",["performance"],"Memory Oversubscrption %")
    def check_cluster_memory_overcommitment(self):
        path='content.rootFolder.childEntity.hostFolder.childEntity'
        clusters_map= self.get_vc_property(path)
        message = ""
        passed_all = True
         
        for clusters_key, clusters in clusters_map.iteritems():
            passed = True
            
            for cluster in clusters:
                cluster_name= cluster.name
                
                if self.authconfig['cluster']!='':
                        if cluster_name not in self.authconfig['cluster']:
                            #print "skipping "+cluster_name
                            continue
                
                cluster_total_memory=cluster.summary.totalMemory
                vRam=0
                for host in cluster.host:
                    for vm in host.vm:                        
                        vRam+= 0  if vm.summary.config.memorySizeMB == None else vm.summary.config.memorySizeMB
                        
                vRam=vRam*1000000
                if cluster_total_memory >0:
                    
                    #cluster_total_memory=(cluster_total_memory/1024)/1024
                    memory_overcommitment=round((vRam/cluster_total_memory),2) 
                    memory_overcommitment_percentage= (memory_overcommitment*100)%100
                    #print   cluster_name,   cluster_total_memory , vRam , memory_overcommitment, memory_overcommitment_percentage
                    self.reporter.notify_progress(self.reporter.notify_checkLog, clusters_key+"@" +cluster_name+ "="+str(memory_overcommitment_percentage)+"% (Expected: =memory-oversubscrption-%)", (True and "PASS" or "FAIL"))
                    message += ", "+clusters_key+"@" +cluster_name+ "="+str(memory_overcommitment_percentage)+"% (Expected: =memory-oversubscrption-%)#"+(True and "PASS" or "FAIL")
                    
        passed_all = passed_all and passed
        return passed_all , message,path
    
    @checkgroup("cluster_checks", "Ratio pCPU/vCPU",["performance"],"pCPU/vCPU ratio")
    def check_cluster_ratio_pCPU_vCPU(self):
        path='content.rootFolder.childEntity.hostFolder.childEntity'
        clusters_map= self.get_vc_property(path)
        message = ""
        passed_all = True
         
        for clusters_key, clusters in clusters_map.iteritems():
            passed = True
            
            for cluster in clusters:
                cluster_name= cluster.name
                
                if self.authconfig['cluster']!='':
                        if cluster_name not in self.authconfig['cluster']:
                            #print "skipping "+cluster_name
                            continue
                
                numCpuCores=cluster.summary.numCpuCores
                pCPU=round(numCpuCores+numCpuCores*.3)
                vCPU=0
                for host in cluster.host:
                    for vm in host.vm:
                        vCPU+= 0 if vm.summary.config.numCpu == None else vm.summary.config.numCpu
                        
                
                if pCPU >0:
                    ratio= "1:"+str(int(round(vCPU/pCPU)))                    
                    self.reporter.notify_progress(self.reporter.notify_checkLog, clusters_key+"@" +cluster_name+ "="+str(ratio)+" (Expected: =pCPU/vCPU)", (True and "PASS" or "FAIL"))
                    message += ", "+clusters_key+"@" +cluster_name+ "="+str(ratio)+" (Expected: =pCPU/vCPU)#"+(True and "PASS" or "FAIL")
                    
                passed_all = passed_all and passed
        return passed_all , message,path
    
    @checkgroup("cluster_checks", "Admission Control Policy - Percentage Based on Nodes in the Cluster",["performance"],"True")
    def check_cluster_acpPercentage_basedOn_nodes(self):
        path='content.rootFolder.childEntity.hostFolder.childEntity'
        clusters_map= self.get_vc_property(path)
        message = ""
        passed_all = True
         
        for clusters_key, clusters in clusters_map.iteritems():
            passed = True
            
            if clusters == "Not-Configured":
                continue
            
            for cluster in clusters:
                
                if not isinstance(cluster, vim.ClusterComputeResource):
                    #condition to check if host directly attached to cluster
                    continue
                cluster_name= cluster.name
                
                if self.authconfig['cluster']!='':
                        if cluster_name not in self.authconfig['cluster']:
                            #print "skipping "+cluster_name
                            continue
                
                
                acp_enabled=cluster.configuration.dasConfig.admissionControlEnabled
                if not acp_enabled:
                    
                    passed = False
                    self.reporter.notify_progress(self.reporter.notify_checkLog, clusters_key+"@" +cluster_name+ "=ACP is disabled (Expected: =true)", (False and "PASS" or "FAIL"))
                    message += ", "+clusters_key+"@" +cluster_name+ "=ACP is disabled (Expected: =true)#"+(False and "PASS" or "FAIL")
                    continue
                
                admissionControlPolicy=cluster.configuration.dasConfig.admissionControlPolicy
                if not isinstance(admissionControlPolicy, vim.cluster.FailoverResourcesAdmissionControlPolicy):
                    passed = False
                    self.reporter.notify_progress(self.reporter.notify_checkLog, clusters_key+"@" +cluster_name+ "=ACP is set to different policy than percentage based (Expected: =true)", (False and "PASS" or "FAIL"))
                    message += ", "+clusters_key+"@" +cluster_name+ "=ACP is set to different policy than percentage based (Expected: =true)#"+(False and "PASS" or "FAIL")
                    continue
                
                cpuFailoverResourcesPercent=cluster.configuration.dasConfig.admissionControlPolicy.cpuFailoverResourcesPercent
                memoryFailoverResourcesPercent=cluster.configuration.dasConfig.admissionControlPolicy.memoryFailoverResourcesPercent        
                numberof_nodes=len(cluster.host)
                nplus=numberof_nodes+1
                nplus_policy_based_percentage=round(100/nplus)
                
                if (nplus_policy_based_percentage != cpuFailoverResourcesPercent) and (memoryFailoverResourcesPercent !=nplus_policy_based_percentage):
                    passed = False
                    self.reporter.notify_progress(self.reporter.notify_checkLog, clusters_key+"@" +cluster_name+ "=ACP reservation policy does not meet N+1 failover requirements (Expected: =true)", (False and "PASS" or "FAIL"))
                    message += ", "+clusters_key+"@" +cluster_name+ "=ACP reservation policy does not meet N+1 failover requirements (Expected: =true)#"+(False and "PASS" or "FAIL")
                else:
                    self.reporter.notify_progress(self.reporter.notify_checkLog, clusters_key+"@" +cluster_name+ "=true (Expected: =true)", (True and "PASS" or "FAIL"))
                    message += ", "+clusters_key+"@" +cluster_name+ "=true (Expected: =true)#"+(True and "PASS" or "FAIL")
                           
                passed_all = passed_all and passed
        return passed_all , message,path
    
    @checkgroup("cluster_checks", "Verify reserved memory and cpu capacity versus Admission control policy set",["performance"],"Cluster Failover Resources %")
    def check_cluster_validate_reserverdMemory_and_reservedCPU_vs_acp(self):
        path='content.rootFolder.childEntity.hostFolder.childEntity'
        clusters_map= self.get_vc_property(path)
        message = ""
        passed_all = True
         
        for clusters_key, clusters in clusters_map.iteritems():
            passed = True
            
            if clusters == "Not-Configured":
                continue
            
            for cluster in clusters:
                
                if not isinstance(cluster, vim.ClusterComputeResource):
                    #condition to check if host directly attached to cluster
                    continue
                cluster_name= cluster.name
                
                if self.authconfig['cluster']!='':
                        if cluster_name not in self.authconfig['cluster']:
                            #print "skipping "+cluster_name
                            continue
                
                
                acp_enabled=cluster.configuration.dasConfig.admissionControlEnabled
                if not acp_enabled:
                    
                    passed = False
                    self.reporter.notify_progress(self.reporter.notify_checkLog, clusters_key+"@" +cluster_name+ "=ACP is disabled (Expected: =Cluster Failover Resources %)", (False and "PASS" or "FAIL"))
                    message += ", "+clusters_key+"@" +cluster_name+ "=ACP is disabled (Expected: =Cluster Failover Resources %)#"+(False and "PASS" or "FAIL")
                    continue
                
                admissionControlPolicy=cluster.configuration.dasConfig.admissionControlPolicy
                if not isinstance(admissionControlPolicy, vim.cluster.FailoverResourcesAdmissionControlPolicy):
                    passed = False
                    self.reporter.notify_progress(self.reporter.notify_checkLog, clusters_key+"@" +cluster_name+ "=ACP is set to different policy than percentage based (Expected: =Cluster Failover Resources %)", (False and "PASS" or "FAIL"))
                    message += ", "+clusters_key+"@" +cluster_name+ "=ACP is set to different policy than percentage based (Expected: =Cluster Failover Resources %)#"+(False and "PASS" or "FAIL")
                    continue
                
                cpuFailoverResourcesPercent=cluster.configuration.dasConfig.admissionControlPolicy.cpuFailoverResourcesPercent
                memoryFailoverResourcesPercent=cluster.configuration.dasConfig.admissionControlPolicy.memoryFailoverResourcesPercent        
                
                currentCpuFailoverResourcesPercent=cluster.summary.admissionControlInfo.currentCpuFailoverResourcesPercent
                currentMemoryFailoverResourcesPercent=cluster.summary.admissionControlInfo.currentMemoryFailoverResourcesPercent
                
                cpu_diff=currentCpuFailoverResourcesPercent - cpuFailoverResourcesPercent
                memory_diff=currentMemoryFailoverResourcesPercent - memoryFailoverResourcesPercent
                
                      
                if (cpu_diff > 25 ) and (memory_diff > 25):
                    passed = True
                else:
                    passed = False
                
                msg="Reserved-Cpu:"+str(cpuFailoverResourcesPercent)+"; Current-Cpu:"+str(currentCpuFailoverResourcesPercent)+"; Reserved-Memory:"+str(memoryFailoverResourcesPercent)+"; Current-Memory:"+str(currentMemoryFailoverResourcesPercent)
                
                self.reporter.notify_progress(self.reporter.notify_checkLog, clusters_key+"@" +cluster_name+ "="+msg+" (Expected: =Cluster Failover Resources %)", (passed and "PASS" or "FAIL"))
                message += ", "+clusters_key+"@" +cluster_name+ "="+msg+" (Expected: =Cluster Failover Resources %)#"+(passed and "PASS" or "FAIL")

                passed_all = passed_all and passed
        return passed_all , message,path
    
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
                        host_name=host.name
                        if self.authconfig['host']!='':
                            if host_name not in self.authconfig['host']:
                                #print "skipping host "+host_name
                                continue
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
                        host_name=host.name
                        if self.authconfig['host']!='':
                            if host_name not in self.authconfig['host']:
                                #print "skipping host "+host_name
                                continue
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
    #{"name" : "vCenter Server Plugins", "path" : "content.extensionManager.extensionList.description.key", "operator":"=", "ref-value": "", "category": ["security"],"expectedresult": "Plugin is Registered"}
    @checkgroup("vcenter_server_checks", "VCenter Server Plugins",["performance"],"List of plugins")
    def check_vcenter_server_plugins(self):
        vcenter_plugins_map = self.get_vc_property('content.extensionManager.extensionList')
               
        message = ""
        passed = True
        plug_list=[]
        for key, plugins in vcenter_plugins_map.iteritems():
            if plugins ==None:
                continue
            for plugin in plugins:
                plug_list.append(plugin.description.label)
            
        if len(plug_list) > 0:
            self.reporter.notify_progress(self.reporter.notify_checkLog,"vCenter Plugins= [" + ','.join(set(plug_list)) + "] (Expected: =Plugin List)" , (True and "PASS" or "FAIL"))
            message += ", "+"License Expiration Validation = " + ','.join(set(plug_list)) + " (Expected: =Plugin List) "+"#"+((True) and "PASS" or "FAIL")
        else:
            passed = False
            self.reporter.notify_progress(self.reporter.notify_checkLog,"vCenter Plugins= Plugins-Not-Found (Expected: =Plugin List)" , (False and "PASS" or "FAIL"))
            message += ", "+"License Expiration Validation = Plugins-Not-Found (Expected: =Plugin List) "+"#"+((False) and "PASS" or "FAIL")
         
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
    
    @checkgroup("network_and_switch_checks", "Check if vSwitchNutanix has no physical adapters",["performance"],"None")
    def check_vswitch_no_physical_nic(self):
        path='content.rootFolder.childEntity.hostFolder.childEntity.host.configManager.networkSystem.networkInfo'
        host_networks = self.get_vc_property(path)
       
        message = ""
        pass_all=True
        
        for key, network in host_networks.iteritems():
            passed = True
            if network == "Not-Configured":
                continue
            
            vswitchs=network.vswitch
            if vswitchs is None:
                continue
            vSwitchNutanix_found=False
            for vswitch in vswitchs:
                if vswitch.name == "vSwitchNutanix":
                     vSwitchNutanix_found=True
                     if len(vswitch.pnic)==0:
                         #print vswitch.name+" as no pnic"
                         message += ", " +key+"@"+vswitch.name+"=None (Expected: =None)"+"#"+(True and "PASS" or "FAIL")
                         self.reporter.notify_progress(self.reporter.notify_checkLog,key+"@"+vswitch.name+"=None (Expected: =None)",(True and "PASS" or "FAIL"))
                     else:
                         passed = False
                         pnic_dict={}
                         for nic in network.pnic:
                               pnic_dict[nic.key]=nic.device
                         nic_names=[]                        
                         for pnic in vswitch.pnic:
                             nic_names.append(pnic_dict[pnic])
                             
                         #print vswitch.name+"="+(','.join(nic_names))
                         message += ", " +key+"@"+vswitch.name+"="+(','.join(nic_names))+" (Expected: =None)"+"#"+(False and "PASS" or "FAIL")
                         self.reporter.notify_progress(self.reporter.notify_checkLog,key+"@"+vswitch.name+"="+(','.join(nic_names))+" (Expected: =None)",(False and "PASS" or "FAIL"))
                     
            if vSwitchNutanix_found==False:
                passed = False
                message += ", " +key+"=vSwitchNutanix-Not-Found (Expected: =None)"+"#"+(False and "PASS" or "FAIL")
                self.reporter.notify_progress(self.reporter.notify_checkLog,key+"=vSwitchNutanix-Not-Found (Expected: =None)",(False and "PASS" or "FAIL"))
            pass_all = passed and pass_all    
 
        return pass_all, message, path
    
    @checkgroup("storage_and_vm_checks", "Hardware Acceleration of Datastores", ["performance"], "Supported")
    def check_vStorageSupport(self):
        path ='content.rootFolder.childEntity.hostFolder.childEntity'
        clusters_object= self.get_vc_property(path)
        message = ""
        pass_all=True
        
        for dcs_key, clusters in clusters_object.iteritems():
            if clusters == 'Not-Configured' :
                #condition to check if any clusters not found 
                continue
            
            for cluster in clusters:
                if not isinstance(cluster, vim.ClusterComputeResource):
                    #condition to check if host directly attached to cluster
                    continue
                
                cluster_name=cluster.name
                # Start of Datastore VStorageSupport
                if cluster.environmentBrowser ==None:
                    continue 
                datastore_dict={}
                datastores=cluster.environmentBrowser.QueryConfigTarget().datastore
                for datastore in datastores:
                    datastore_dict[datastore.name]=datastore.vStorageSupport
                # End of Datastore VStorageSupport
                
                # Start of datastore mount to host
                if cluster.datastore ==None:
                    #condition to check if any host exist in cluster
                    continue
                
                for cluster_ds in cluster.datastore:
                    cluster_ds_name=cluster_ds.name
                    if fnmatch.fnmatch(cluster_ds_name,"NTNX-local-ds*"):
                        continue
                    host_mounted_map={} 
                    for cluster_ds_host_mount in cluster_ds.host:
                        hostname=cluster_ds_host_mount.key.name
                        #host_name=host.name
                        if self.authconfig['host']!='':
                            if hostname not in self.authconfig['host']:
                                #print "skipping host "+hostname
                                continue
                        if cluster_ds_host_mount.mountInfo.accessible== True:
                            #print cluster_name, hostname , cluster_ds_name ,cluster_ds_host_mount.mountInfo.accessible ,datastore_dict[cluster_ds_name]
                            expected_vStorageSupported="vStorageSupported"
                            actual_vStorageSupported=datastore_dict[cluster_ds_name]
                            
                            message += ", " +dcs_key+"@"+cluster_name+"@"+hostname+"@"+cluster_ds_name+"="+actual_vStorageSupported+ " (Expected: ="+expected_vStorageSupported+")"+"#"+((expected_vStorageSupported == actual_vStorageSupported) and "PASS" or "FAIL")
                            self.reporter.notify_progress(self.reporter.notify_checkLog,dcs_key+"@"+cluster_name+"@"+hostname+"@"+cluster_ds_name+"="+actual_vStorageSupported+ " (Expected: ="+expected_vStorageSupported+")" , ( (expected_vStorageSupported == actual_vStorageSupported) and "PASS" or "FAIL"))
                # End of datastore mount to host            
        return pass_all, message,path+'.host.datastore'
    
    
    @checkgroup("storage_and_vm_checks", "USB Device Connected to VM", ["manageability","reliability"], "False")
    def check_usb_disabled(self):
        path ='content.rootFolder.childEntity.hostFolder.childEntity.host.vm.config.hardware.device'
        vms_virtual_hardware= self.get_vc_property(path)
        message = ""
        pass_all=True
        
        for vms_key, vms_vDevice in vms_virtual_hardware.iteritems():
            passed = True
            if vms_vDevice == 'Not-Configured' :
                #condition to check if any clusters not found 
                continue
            usb_found=False
            for device in vms_vDevice:
                if isinstance(device, vim.vm.device.VirtualUSB):
                    usb_found=True
                    usb_connected=device.connectable.connected
                    passed=not usb_connected
                    message += ", " +vms_key+"="+str(usb_connected) + " (Expected: =False)"+"#"+(not usb_connected and "PASS" or "FAIL")
                    self.reporter.notify_progress(self.reporter.notify_checkLog, vms_key+"="+str(usb_connected) + " (Expected: =False)", (not usb_connected and "PASS" or "FAIL"))
                    break
            if usb_found==False:
                message += ", " +vms_key+"=Not-Attached (Expected: =False)"+"#"+(True and "PASS" or "FAIL")
                self.reporter.notify_progress(self.reporter.notify_checkLog, vms_key+"=Not-Attached (Expected: =False)", (True and "PASS" or "FAIL"))
            pass_all= pass_all and passed    
        return pass_all, message,path
    
    @checkgroup("storage_and_vm_checks", "RS-232 Serial Port Connected to VM", ["manageability","reliability"], "False")
    def check_rs232_serial_port_disabled(self):
        path ='content.rootFolder.childEntity.hostFolder.childEntity.host.vm.config.hardware.device'
        vms_virtual_hardware= self.get_vc_property(path)
        message = ""
        pass_all=True
        
        for vms_key, vms_vDevice in vms_virtual_hardware.iteritems():
            if vms_vDevice == 'Not-Configured' :
                #condition to check if any clusters not found 
                continue
            serial_found=False
            passed=True
            for device in vms_vDevice:
                if isinstance(device, vim.vm.device.VirtualSerialPort):
                    serial_found= True
                    serial_connected=device.connectable.connected
                    passed=not serial_connected
                    message += ", " +vms_key+"="+str(serial_connected) + " (Expected: =False)"+"#"+(( not serial_connected) and "PASS" or "FAIL")
                    self.reporter.notify_progress(self.reporter.notify_checkLog, vms_key+"="+str(serial_connected) + " (Expected: =False)", ((not serial_connected) and "PASS" or "FAIL"))
                    break 
            if serial_found==False:
                message += ", " +vms_key+"=Not-Attached (Expected: =False)"+"#"+(True and "PASS" or "FAIL")
                self.reporter.notify_progress(self.reporter.notify_checkLog, vms_key+"=Not-Attached (Expected: =False)", (True and "PASS" or "FAIL"))                   
            pass_all= pass_all and passed
        return pass_all, message,path
    
    @checkgroup("storage_and_vm_checks", "CD-ROM Connected to VM",["manageability","reliability"], "False")
    def check_cdrom_disabled(self):
        path ='content.rootFolder.childEntity.hostFolder.childEntity.host.vm.config.hardware.device'
        vms_virtual_hardware= self.get_vc_property(path)
        message = ""
        pass_all=True
        
        for vms_key, vms_vDevice in vms_virtual_hardware.iteritems():
            if vms_vDevice == 'Not-Configured' :
                #condition to check if any clusters not found 
                continue
            cdrom_found=False
            passed =True
            for device in vms_vDevice:
                if isinstance(device, vim.vm.device.VirtualCdrom):
                    cdrom_found=True
                    cdrom_connected= device.connectable.connected
                    passed=not cdrom_connected
                    message += ", " +vms_key+"="+str(cdrom_connected) + " (Expected: =False)"+"#"+(( not cdrom_connected) and "PASS" or "FAIL")
                    self.reporter.notify_progress(self.reporter.notify_checkLog, vms_key+"="+str(cdrom_connected) + " (Expected: =False)", ((not cdrom_connected) and "PASS" or "FAIL"))
                    break
            if cdrom_found==False:
                message += ", " +vms_key+"=Not-Attached (Expected: =False)"+"#"+(True and "PASS" or "FAIL")
                self.reporter.notify_progress(self.reporter.notify_checkLog, vms_key+"=Not-Attached (Expected: =False)", (True and "PASS" or "FAIL"))     
            pass_all= pass_all and passed
        return pass_all, message,path
    
    @checkgroup("storage_and_vm_checks", "VM CPU limit", ["manageability"], "CPU Limit")
    def check_vm_cpu_limit(self):
        path ='content.rootFolder.childEntity.hostFolder.childEntity.host.vm[name!=NTNX*CVM].summary'
        vms_map= self.get_vc_property(path)
        message = ""
        pass_all=True
        
        for vms_key, vm in vms_map.iteritems():
              
            if vm == 'Not-Configured' :
                #condition to check if any clusters not found 
                continue
            passed=True
            vms_key='@'.join(vms_key.split('@')[0:-1])
            maxCpuUsage=vm.runtime.maxCpuUsage
            
            if maxCpuUsage == None:
                passed=False
                message += ", " +vms_key+"=maxCpuUsage-Not-Configured (Expected: =False)"+"#"+(False and "PASS" or "FAIL")
                self.reporter.notify_progress(self.reporter.notify_checkLog, vms_key+"=maxCpuUsage-Not-Configured (Expected: =False)", (False and "PASS" or "FAIL"))
                continue
            
            numCpu=vm.config.numCpu
            if numCpu == None:
                passed=False
                message += ", " +vms_key+"=numCpu-Not-Configured (Expected: =False)"+"#"+(False and "PASS" or "FAIL")
                self.reporter.notify_progress(self.reporter.notify_checkLog, vms_key+"=numCpu-Not-Configured (Expected: =False)", (False and "PASS" or "FAIL"))
                continue
            
            cpuMhz=vm.runtime.host.summary.hardware.cpuMhz
            if cpuMhz == None:
                passed=False
                message += ", " +vms_key+"=cpuMhz-Not-Configured (Expected: =False)"+"#"+(False and "PASS" or "FAIL")
                self.reporter.notify_progress(self.reporter.notify_checkLog, vms_key+"=cpuMhz-Not-Configured (Expected: =False)", (False and "PASS" or "FAIL"))
                continue
                
            if maxCpuUsage == (cpuMhz*numCpu):
                message += ", " +vms_key+"=true (Expected: =False)"+"#"+(True and "PASS" or "FAIL")
                self.reporter.notify_progress(self.reporter.notify_checkLog, vms_key+"=true (Expected: =False)", (True and "PASS" or "FAIL"))
                
            else:
                passed=False
                message += ", " +vms_key+"=true (Expected: =False)"+"#"+(True and "PASS" or "FAIL")
                self.reporter.notify_progress(self.reporter.notify_checkLog, vms_key+"=true (Expected: =False)", (True and "PASS" or "FAIL"))
                
            pass_all= pass_all and passed
  
        return pass_all, message,path
    
    @checkgroup("cvm_checks", "CPU limit per CVM", ["manageability"], "CPU Limit")
    def check_cvm_cpu_limit(self):
        path ='content.rootFolder.childEntity.hostFolder.childEntity.host.vm[name=NTNX*CVM].summary'
        vms_map= self.get_vc_property(path)
        message = ""
        pass_all=True
        
        for vms_key, vm in vms_map.iteritems():
              
            if vm == 'Not-Configured' :
                #condition to check if any clusters not found 
                continue
            passed=True
            
            vms_key='@'.join(vms_key.split('@')[0:-1])
            
            maxCpuUsage=vm.runtime.maxCpuUsage
            
            if maxCpuUsage == None:
                passed=False
                message += ", " +vms_key+"=maxCpuUsage-Not-Configured (Expected: =False)"+"#"+(False and "PASS" or "FAIL")
                self.reporter.notify_progress(self.reporter.notify_checkLog, vms_key+"=maxCpuUsage-Not-Configured (Expected: =False)", (False and "PASS" or "FAIL"))
                continue
            
            numCpu=vm.config.numCpu
            if numCpu == None:
                passed=False
                message += ", " +vms_key+"=numCpu-Not-Configured (Expected: =False)"+"#"+(False and "PASS" or "FAIL")
                self.reporter.notify_progress(self.reporter.notify_checkLog, vms_key+"=numCpu-Not-Configured (Expected: =False)", (False and "PASS" or "FAIL"))
                continue
            
            cpuMhz=vm.runtime.host.summary.hardware.cpuMhz
            if cpuMhz == None:
                passed=False
                message += ", " +vms_key+"=cpuMhz-Not-Configured (Expected: =False)"+"#"+(False and "PASS" or "FAIL")
                self.reporter.notify_progress(self.reporter.notify_checkLog, vms_key+"=cpuMhz-Not-Configured (Expected: =False)", (False and "PASS" or "FAIL"))
                continue
                
            if maxCpuUsage == (cpuMhz*numCpu):
                message += ", " +vms_key+"=true (Expected: =False)"+"#"+(True and "PASS" or "FAIL")
                self.reporter.notify_progress(self.reporter.notify_checkLog, vms_key+"=true (Expected: =False)", (True and "PASS" or "FAIL"))
                
            else:
                passed=False
                message += ", " +vms_key+"=true (Expected: =False)"+"#"+(True and "PASS" or "FAIL")
                self.reporter.notify_progress(self.reporter.notify_checkLog, vms_key+"=true (Expected: =False)", (True and "PASS" or "FAIL"))
                
            pass_all= pass_all and passed
  
        return pass_all, message,path
    
    @checkgroup("storage_and_vm_checks", "VM using the VMXNET3 virtual network device",["performance"], "Vmxnet3")
    def check_vm_using_vmxnet3(self):
        path ='content.rootFolder.childEntity.hostFolder.childEntity.host.vm.config'
        vms= self.get_vc_property(path)
        message = ""
        pass_all=True
        
        for vm_key, vm in vms.iteritems():
            if vm == 'Not-Configured' :
                #condition to check if any clusters not found 
                continue
            
            #vm version
            version=vm.version
            
            #Version Number from version string 
            version_no=int(version.replace("vmx-",""))
            
            if version_no < 7 :
                #print vm_key , version_no ,"Skipping check"
                #skip check if version is less then 7 as need to check version above 7
                continue
            
            passed =True
            
            adapter=set()
            #Device used by VM 
            #print vm_key , version_no
            for device in vm.hardware.device:
                if isinstance(device, vim.vm.device.VirtualEthernetCard):
                    #print "\t",type(device).__class__
                    adapter.add(((type(device).__name__).split('.')[-1]).replace("Virtual",""))
            #print "\t\t", ','.join(adapter)
            if 'Vmxnet3' in adapter:
                passed = True
            else : 
                passed= False
            
            message += ", " +vm_key+"="+(','.join(adapter))+" (Expected: =Vmxnet3)"+"#"+(passed and "PASS" or "FAIL")
            self.reporter.notify_progress(self.reporter.notify_checkLog,vm_key+"="+(','.join(adapter))+" (Expected: =Vmxnet3)", (passed and "PASS" or "FAIL"))     
            pass_all= pass_all and passed
        return pass_all, message,path