from __future__ import division
from bdb import effective
from test.test_pydoc import expected_data_docstrings
__author__ = 'anand nevase'
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
import os


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

class HorizonViewChecker(CheckerBase):

    _NAME_ = "view"

    def __init__(self):
        super(HorizonViewChecker, self).__init__(HorizonViewChecker._NAME_)
        self.config_form =  form.Form( 
                form.Textbox("Server",value=self.authconfig['view_ip']),
                form.Textbox("User",value=self.authconfig['view_user']),
                form.Password("Password",value=Security.decrypt(self.authconfig['view_pwd'])))() 

        self.si = None
        self.categories=['security','performance','availability','manageability','recoverability','reliability','post-install']
        self.category=None

    def get_name(self):
        return HorizonViewChecker._NAME_

    def get_desc(self):
        return "Performs Vmware Horizon View health checks"

    def configure(self, config, reporter):
        self.config = config
        self.reporter = reporter
        self.authconfig=self.get_auth_config(self.get_name())
        CheckerBase.validate_config(self.authconfig, "view_ip")
        CheckerBase.validate_config(self.authconfig, "view_user")
        CheckerBase.validate_config(self.authconfig, "view_pwd")
        #CheckerBase.validate_config(self.authconfig, "vc_port")

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
        
#         for category in self.categories:
#             x.add_row([category,"Run "+category+' category'])
        x.add_row(["run_all", "Run all Horizon View checks"])
        x.add_row(["setup", "Set Vmware Horizon View Configuration"])
        message = message is None and str(x) or "\nERROR: "+ message + "\n\n" + str(x)
        exit_with_message(message)

    def setup(self):
        print "\nConfiguring Vmware Horizon View Server:\n"
        
#         print "Current configuration for vCenter Server is:\n vCenter Server IP: %s \n vCenter User Name: %s \n VCenter Port: %d\n Clusters: %s \n hosts: %s"%\
#               (self.authconfig['vc_ip'], self.authconfig['vc_user'], self.authconfig['vc_port'],self.authconfig['cluster'],self.authconfig['host'] )
        current_vc_ip = self.authconfig['view_ip'] if ('view_ip' in self.authconfig.keys()) else "Not Set"
        vc_ip=raw_input("Enter Vmware Horizon View Server IP [default: "+current_vc_ip+"]: ")
        vc_ip=vc_ip.strip()
        if vc_ip == "":
            if(current_vc_ip == "Not Set"):
                exit_with_message("Error: Set Vmware Horizon View Server IP.")
            vc_ip=current_vc_ip
        
        if Validate.valid_ip(vc_ip) == False:
            exit_with_message("\nError: Invalid Vmware Horizon View Server IP address")
                
        current_vc_user=self.authconfig['view_user'] if ('view_user' in self.authconfig.keys()) else "Not Set"
        vc_user=raw_input("Enter Vmware Horizon View Server User Name [default: "+current_vc_user+"]: ")
        vc_user=vc_user.strip()
        if vc_user == "":
            if(current_vc_user == "Not Set"):
                exit_with_message("Error: Set Vmware Horizon View Server User Name.")
            vc_user=current_vc_user
            
            
        current_pwd=self.authconfig['view_pwd'] if  ('view_pwd' in self.authconfig.keys()) else "Not Set"
        new_vc_pwd=getpass.getpass('Enter Vmware Horizon View Server Password [Press enter to use previous password]: ')
        
        if new_vc_pwd == "":
            if(current_pwd == "Not Set"):
                exit_with_message("Error: Set Vmware Horizon View Server Password.")
            vc_pwd = current_pwd
        else:
            confirm_pass=getpass.getpass('Re-Enter Vmware Horizon View Server Password: ')
            if new_vc_pwd !=confirm_pass :
                exit_with_message("\nError: Password miss-match.Please run \"vc setup\" command again")
            vc_pwd=Security.encrypt(new_vc_pwd)
       
#         #Test Connection Status
#         print "Checking Vmware Horizon View Server Connection Status:",
#         
#         if not sys.platform.startswith("win"):
#             exit_with_message("Plateform Not supported \n Windows system required to run Vmware Horizon View Checks")
#         status, message = self.check_connectivity(vc_ip, vc_user, vc_pwd, vc_port)
#         if status == True:
#             print Fore.GREEN+" Connection successful"+Fore.RESET
#         else:
#            print Fore.RED+" Connection failure"+Fore.RESET
#            exit_with_message(message)
           
        #print "vc_ip :"+vc_ip+" vc_user :"+vc_user+" vc_pwd : "+vc_pwd+ " vc_port:"+str(vc_port)+" cluster : "+cluster+" host : "+hosts
 
        view_auth = dict()
        view_auth["view_ip"]=vc_ip;
        view_auth["view_user"]=vc_user;
        view_auth["view_pwd"]=vc_pwd;
        
        CheckerBase.save_auth_into_auth_config(self.get_name(),view_auth)
        exit_with_message("Vmware Horizon View Server is configured Successfully ")
        return
    
    def check_connectivity(self,vc_ip,vc_user,vc_pwd,vc_port):
        from subprocess import check_output  
    
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

        self.reporter.notify_progress(self.reporter.notify_info,"Starting Vmware Horizon View Checks")
        self.result = CheckerResult("view",self.authconfig)
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
        
#         print check_functions
#         exit()
#         try:
#             self.si = SmartConnect(host=self.authconfig['vc_ip'], user=self.authconfig['vc_user'], pwd=Security.decrypt(self.authconfig['vc_pwd']), port=self.authconfig['vc_port'])
#         except vim.fault.InvalidLogin:
#             exit_with_message("Error : Invalid vCenter Server Username or password\n\nPlease run \"vc setup\" command to configure vc")
#         except ConnectionError as e:
#             exit_with_message("Error : Connection Error"+"\n\nPlease run \"vc setup\" command to configure vc")
#         
        passed_all = True
        
        for check_group in check_groups_run:          
            self.reporter.notify_progress(self.reporter.notify_checkGroup,check_group)
           
            for check in self.config[check_group]:
                self.reporter.notify_progress(self.reporter.notify_checkName,check['name'])              
                
                if self.category!=None: #condition for category 
                    if self.category not in check['category']:
                        continue
                
                if check['property_type'].lower()== "powershell":
                    check_name=check['name']
                    operator=check['operator']
                    expected=check['ref-value']
                    actual = self.get_view_property(check['property'])
                    passed=HorizonViewChecker.apply_operator(actual, expected, operator)
                    message="Actual="+actual + " (Expected: " + operator + expected+ ") "
                    self.reporter.notify_progress(self.reporter.notify_checkLog,message, passed and "PASS" or "FAIL")
                    self.result.add_check_result(CheckerResult(check_name,None, passed, message))
                    #self.reporter.notify_one_line(check_name, str(passed))
                #self.result.add_check_result(CheckerResult(check['name'], None, passed, message, check['category'],None,check['expectedresult']))
                passed_all = passed_all and passed
       
            if check_group in check_functions:
                for check_function in check_functions[check_group]:
                     
                    if self.category!=None:#condition for category for custom checks 
                        if self.category not in check_function.category:
                            continue                      
                    passed, message,path = check_function()
                    #self.result.add_check_result(CheckerResult(check_name,None, passed, message))
                    #self.result.add_check_result(CheckerResult(check_name,authconfig=self.authconfig, message=message,category=check_function.category,path=None,expected_result=check_function.expected_result))
                    #self.result.add_check_result(CheckerResult(check_function.descr, None, passed, message, check_function.category, path,check_function.expected_result))
                    passed_all = passed_all and passed
            self.reporter.notify_progress(self.reporter.notify_checkName,"")
        

#         Disconnect(self.si)
        self.result.passed = ( passed_all and "PASS" or "FAIL" )
        self.result.message = "View Checks completed with " + (passed_all and "success" or "failure")
        self.reporter.notify_progress(self.reporter.notify_info," Vmware Horizon View Checks complete")

        return self.result

    def get_view_property(self,powershell_cmd):
        actual=HorizonViewChecker.run_powershell(self.authconfig['view_ip'],self.authconfig['view_user'],Security.decrypt(self.authconfig['view_pwd']),powershell_cmd)
        return actual
        
    
    @staticmethod
    def run_powershell(host_ip,host_username,host_password,powershell_cmd):
        #print host_ip,host_username,host_password,command
        power_shell_text = """winrs -r:{0} -u:{1} -p:{2} powershell Add-PSSnapin VMware.View.Broker ;{3} 2>&1\"""".format(
                            host_ip,host_username,host_password,powershell_cmd)
        proc= os.popen(power_shell_text)
        output=proc.read()
        exit_code=proc.close()
        #print output , exit_code
        if exit_code == None:
            return output.strip()
        else:
            return "command-error"
    
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
    
    @checkgroup("view_components_checks", "Verify View Connection Brokers runs on a supported operating system",["Availability"],"[Windows Server 2008 R2 (64 bit),Windows Server 2008 R2 SP1 (64 bit),Windows 2012 R2 (64 bit)]")
    def check_connectionbroker_os(self):
        powershell_cmd="(Get-WmiObject Win32_OperatingSystem ).Caption + (Get-WmiObject -class Win32_OperatingSystem).OSArchitecture"
        output=self.get_view_property(powershell_cmd)
        
        expected = [ 'Windows Server 2008 R2','Windows Server 2008 R2 SP1','Windows 2012 R2']
        
        message = ""
        passed_all = True
        
        self.reporter.notify_progress(self.reporter.notify_checkLog, "Actual="+output+" (Expected: ="+str(expected)+")", (True and "PASS" or "FAIL"))
        message = "Actual="+output+" (Expected: ="+str(expected)+")#"+(True and "PASS" or "FAIL") 
        
        #passed_all = passed_all and passed
        
        return passed_all , message,None
    
    @checkgroup("view_components_checks", "View Connection Brokers has correct CPUs",["Performance"],"For 1-50 Desktop; CB cpu >=2 ,for 51-2000 Desktop; CB cpu >=4, for 2001-5000 Desktop; CB CPU >=6")
    def check_connectionbroker_cpu(self):
        
        cpu_powershell='$cpu=0;ForEach ($obj in  Get-WmiObject -class win32_processor) { $cpu+=$obj.NumberOfCores}; $cpu'
        cpu=self.get_view_property(cpu_powershell)
        vms=self.get_view_property('(Get-DesktopVM).length')
                
        message = ""
        passed= True
        actual=None
        expected=None
        if cpu == 'command-error' or  vms == 'command-error':
            return None, None,None
        else:
            cpu=int(cpu)
            vms=int(vms)
        if vms >0 and vms <= 50: 
            if cpu <2:
                 passed= False
            expected = "For 1-50 Desktops, Number of Cpu:>=6"
        elif vms >50 and vms <=2000: 
            if cpu <4:
                 passed= False
            expected = "For 51-2000 Desktops, Number of Cpu:>=4"
        elif vms >2000 and vms <=5000: 
            if cpu <6:
                 passed= False
            expected = "For 2001-5000 Desktops, number of Cpu:>=6"
        actual= "Number of Cpu:"+str(cpu)+"; Number of Desktop:"+str(vms)
        self.reporter.notify_progress(self.reporter.notify_checkLog, "Result="+actual+" (Expected: ="+str(expected)+")", (passed and "PASS" or "FAIL"))
        message = "Result="+actual+" (Expected: ="+str(expected)+")#"+(passed and "PASS" or "FAIL")
        #passed_all = passed_all and passed
        
        return passed , message,None
    
    @checkgroup("view_components_checks", "View Connection Brokers has correct Memory",["Performance"],"For 1-50 Desktop; CB Memory >=4GB ,for 51-2000 Desktop; CB cpu >=10GB, for 2001-5000 Desktop; CB CPU >=12GB")
    def check_connectionbroker_memory(self):
        
        memory_powershell='(Get-WmiObject CIM_PhysicalMemory).Capacity / 1GB'
        memory=self.get_view_property(memory_powershell)
        vms=self.get_view_property('(Get-DesktopVM).length')
                
        message = ""
        passed= True
        actual=None
        expected=None
        if memory == 'command-error' or  vms == 'command-error':
            return None, None,None
        else:
            memory=int(memory)
            vms=int(vms)
        if vms >0 and vms <= 50: 
            if memory <4:
                 passed= False
            expected = "For 1-50 Desktops, Memory:>=4GB"
        elif vms >50 and vms <=2000: 
            if memory <10:
                 passed= False
            expected = "For 51-2000 Desktops, Memory:>=10GB"
        elif vms >2000 and vms <=5000: 
            if memory <12:
                 passed= False
            expected = "For 2001-5000 Desktops, Memory:>=12GB"
        actual= "Memory:"+str(memory)+"GB; Number of Desktop:"+str(vms)
        self.reporter.notify_progress(self.reporter.notify_checkLog, "Result="+actual+" (Expected: ="+str(expected)+")", (passed and "PASS" or "FAIL"))
        message = "Result="+actual+" (Expected: ="+str(expected)+")#"+(passed and "PASS" or "FAIL")
        #passed_all = passed_all and passed
        
        return passed , message,None
    
    @checkgroup("view_components_checks", "Verify that the Maximum number of desktops in a pool is no more than 1000",["Availability"],"<=1000 Desktops")
    def check_max_desktop_per_pool(self):
        powershell_cmd='ForEach($Pool in Get-Pool){Write-Host $Pool.displayName = $Pool.maximumCount}'
        output=self.get_view_property(powershell_cmd)
        
        if output == 'command-error':
            return None,None,None
        
        pools= output.split("\n")
        message = ""
        passed_all = True
        for pool in pools:
            pool_name, max_vm_in_pool= pool.split("=")
            pool_name=pool_name.strip()
            max_vm_in_pool=int(max_vm_in_pool.strip())
            flag=True
            if max_vm_in_pool >1000:
                flag=False
            output="Pool["+pool_name + "],Max Desktop :"+str(max_vm_in_pool)
            expected="Max Desktop <=10000"
            self.reporter.notify_progress(self.reporter.notify_checkLog, "Result="+output+" (Expected: = "+str(expected)+")", (flag and "PASS" or "FAIL"))
            message = "Result="+output+" (Expected: ="+str(expected)+")#"+(flag and "PASS" or "FAIL") 
        
        #passed_all = passed_all and passed
        
        return passed_all , message,None