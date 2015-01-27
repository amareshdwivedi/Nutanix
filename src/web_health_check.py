import web
import requests
from web import form
from checkers.ncc_checker import NCCChecker
from checkers.vc_checker import VCChecker
from checkers.base_checker import CheckerBase
from reporters import DefaultConsoleReporter
from report_generator import PDFReportGenerator,CSVReportGenerator
from prettytable import PrettyTable
import json
from operator import itemgetter
import csv, time
import sys
import os
import httplib
import paramiko
import socket
from security import Security
import warnings
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
from requests.exceptions import ConnectionError
from deployer_web import initiate_deployment
import api
import reportGenerator


if (len(sys.argv) > 2):
    cur_dir=sys.argv[2]
else:
    cur_dir = None
    
urls = (

    '/v1/deployer/customers/$','api.customers' ,       
    '/v1/deployer/customers/(\d+)/$','api.customers',   
    '/v1/deployer/customers/(\d+)/tasks/$','api.customertasks',
    '/v1/deployer/customers/(\d+)/tasks/(\d+)/$','api.customertasks',   
    '/v1/deployer/utils/nodedetails/$','api.nodedetails',
    '/v1/deployer/utils/foundationprogress/$','api.foundationprogress',
    '/v1/deployer/action/$','api.customeraction',
    '/v1/deployer/customers/(\d+)/tasks/(\d+)/status/$','api.deploymentstatus',
    '/config', 'config',
    '/connect', 'connect',
    '/run', 'runChecks',
    '/refresh', 'refresh',
    '/', 'index',
    '/GeneratePdf/','reportGenerator.GeneratePdf'
)

app = web.application(urls, globals())
#web.header('Content-Type', 'applicaton/json')
#render = web.template.render('templates/')
render = web.template.render('templates/')


class index:
    def __init__(self):
        self.checkers = {}
        self.callback_name = ''
        for checker_class in CheckerBase.__subclasses__():
            checker = checker_class()
            self.checkers[checker.get_name()] = checker
        
        for checker in self.checkers.keys():
            checker_conf_path=os.path.abspath(os.path.dirname(__file__))+os.path.sep +"conf" + os.path.sep + checker + ".conf"
            fp = open(checker_conf_path, 'r')
            checker_config = json.load(fp)
            fp.close()
            checker_module = self.checkers[checker]
            self.reporter = DefaultConsoleReporter(checker)
            checker_module.configure(checker_config, self.reporter)

    def GET(self):
        #print self.checkers
        return render.index(self.checkers)
    
class config:
    def __init__(self):
        pass

    def POST(self):
        data = web.input()
        if data['checker'] == "vc":
            conf_data = { "vc_port": data['vCenter Server Port'], 
                          "vc_user": data['vCenter Server Username'], 
                          "vc_ip": data['vCenter Server IP'], 
                          "cluster": data['Clusters(Comma Seperated List)'], 
                          "host": data['Hosts(Comma Seperated List)'],  
                          "vc_pwd": Security.encrypt(data['vCenter Server Password'])
                        }
            CheckerBase.save_auth_into_auth_config("vc",conf_data)
            status = {"Configuration": "Success"}
            return json.dumps(status)

        if data['checker'] == "ncc":
            conf_data = { "cvm_ip": data['CVM IP'], 
                          "cvm_pwd": Security.encrypt(data['CVM SSH Host Password']), 
                          "cvm_user": data['CVM SSH Host Username']
                          }

            CheckerBase.save_auth_into_auth_config("ncc",conf_data)
            status = {"Configuration": "Success"}        
            return json.dumps(status)

class connect:
    def __init__(self):
        self.checkers = {}
        self.callback_name = ''
        for checker_class in CheckerBase.__subclasses__():
            checker = checker_class()
            self.checkers[checker.get_name()] = checker

    def POST(self):
        data = web.input()
        
        status = {"Connection": "Failed"}
        if data['checker'] == "vc":
            ret , msg = self.checkers['vc'].check_connectivity(data['vCenter Server IP'],data['vCenter Server Username'],Security.encrypt(data['vCenter Server Password']),data['vCenter Server Port'])
            if ret:
                status['Connection'] = "Success"
            return json.dumps(status)
    
        if data['checker'] == "ncc":
            ret , msg = self.checkers['ncc'].check_connectivity(data['CVM IP'],data['CVM SSH Host Username'],Security.encrypt(data['CVM SSH Host Password']))
            if ret:
                status['Connection'] = "Success"
            return json.dumps(status)
    
class runChecks:
    def __init__(self):
        self.checkers = {}
        self.callback_name = ''
        for checker_class in CheckerBase.__subclasses__():
            checker = checker_class()
            self.checkers[checker.get_name()] = checker
        
        for checker in self.checkers.keys():
            checker_conf_path=os.path.abspath(os.path.dirname(__file__))+os.path.sep +"conf" + os.path.sep + checker + ".conf"
            fp = open(checker_conf_path, 'r')
            checker_config = json.load(fp)
            fp.close()
            checker_module = self.checkers[checker]
            self.reporter = DefaultConsoleReporter(checker)
            checker_module.configure(checker_config, self.reporter)

    def POST(self):
        data = web.input()
        results = {}
        run_logs = {}
        
        checkers_list, group = [], []
        if data['category'] == "Run All":
            checkers_list = self.checkers.keys()
            for item in checkers_list:
                run_logs[item] = {'checks': []}

        if data['category'] == "ncc":
            checkers_list = ['ncc']
            run_logs['ncc'] = {'checks': []}
            if data['group'] == "Run All":
                group.append("run_all")
            else:
                group.append(data['group'] + " " + "run_all")
                
        if data['category'] == "vc":
            checkers_list = ['vc']
            run_logs['vc'] = {'checks': []}
            if data['group'] == "Run All":
                group.append("run_all")
            else:
                group.append(data['group'])
        
        with open("display_json.json", "w") as myfile:
            json.dump(run_logs, myfile)

        for checker in checkers_list:
            checker_module = self.checkers[checker]
            
            if checker == "vc":
                result = checker_module.execute(group)
            elif checker == 'ncc':
                result = checker_module.execute(group)
            else:        
                result = checker_module.execute(["run_all"])
            
            results[checker] = result.to_dict()
            
        #Generate Json Reports 
        outfile = open(os.getcwd() + os.path.sep +"reports"+os.path.sep+"results.json", 'w')
        json.dump(results, outfile, indent=2)
        outfile.close()
                    
        #Generate CSV Reports
        CSVReportGenerator(results,cur_dir)
        
        #Generate PDF Report based on results. 
        PDFReportGenerator(results,cur_dir)
            
        return True

class refresh:
    def __init__(self):
        pass

    def GET(self):
        try:
            f = open("display_json.json", 'r')
            return f.read()
        except:
            return True
      
if __name__ == "__main__":
    web.internalerror = web.debugerror
    app.run()
