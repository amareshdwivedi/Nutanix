import web
import requests
from web import form
from checkers.ncc_checker import NCCChecker
from checkers.vc_checker import VCChecker
from checkers.base_checker import CheckerBase
from reporters import DefaultConsoleReporter
from PDFGenerator import PDFReportGenerator
from prettytable import PrettyTable
import json
from operator import itemgetter
import csv, time
import sys
import os

import paramiko
import socket
from security import Security
import warnings
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
from requests.exceptions import ConnectionError

'''
def hello(values):
        print "Run these checks:",values
        #return "GaneshManalPatil"
'''

urls = (
  '/', 'index'
  #'/(.*)', 'index'
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
        
    def run_checks(self,data):
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
            
        if data['category'] == "vc":
            checkers_list = ['vc']
            run_logs['vc'] = {'checks': []}
            if data['group'] == "Run All":
                group.append("run_all")
            else:
                group.append(data['group'])
        
        with open("test.json", "w") as myfile:
            json.dump(run_logs, myfile)
        for checker in checkers_list:
            checker_module = self.checkers[checker]
            
            if checker == "vc":
                result = checker_module.execute(group)
            else:    
                result = checker_module.execute(["run_all"])
            
            results[checker] = result.to_dict()
            
            # This is to sort the checks in given checker based on the severity ( asc order )
            try :
                results[checker]['checks'] = sorted(results[checker]['checks'], key=itemgetter('Severity'))
            except KeyError:
                # It means no checks are executed for given checker
                continue
            
        #Generate CSV Reports
        rows = []
        details = []
        details.append(["Nutanix Cluster Health Check Results"])
        rows.append(["Category", "Health Check Variable","Property","Status", "Severity"])
        for xchecker,allChecks in results.iteritems():
            details.append(["IP",allChecks['ip']])
            details.append(["Category",allChecks['Name']])
            details.append(["User Name",allChecks['user']])
            details.append(["Timestamp",str(time.strftime("%B %d, %Y %H:%M:%S"))])
            details.append(["Overall Status",allChecks['Status']])
            
            try:
                for xcheck in allChecks['checks']:
                    if isinstance(xcheck['Properties'], list):
                        rows.append([xchecker, xcheck['Name'],"Overall Status",xcheck['Status'], xcheck['Severity']])
                        for prop in xcheck['Properties']:
                            rows.append([xchecker, xcheck['Name'],prop['Message'],prop['Status'], xcheck['Severity']])
                    else:
                        rows.append([xchecker, xcheck['Name'],None,xcheck['Status'], xcheck['Severity']])
            except KeyError:
                #It means- No checks were executed for this checker. 
                continue
        
        if len(rows) > 1:
            details.append([None])
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            file_name = os.path.abspath(os.path.dirname(__file__))+os.path.sep+'reports'+os.path.sep+'Healthcheck-' + timestamp + '.csv'
            csv_file = open(file_name ,'wb')
            csv_writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerows(details)
            csv_writer.writerows(rows)
            csv_file.close()
            
        #Generate Json Reports 
        outfile = open(os.path.abspath(os.path.dirname(__file__))+os.path.sep+"reports"+os.path.sep+"results.json", 'w')
        json.dump(results, outfile, indent=2)
        outfile.close()
        
        #Generate PDF Report based on results. Temporary comment out
        PDFReportGenerator(results)
            
        return True
    
    def do_config(self,data):
        if data['operation'].split('_')[1] == "vc":
            conf_data = { "vc_port": data['Port'], 
                          "vc_user": data['User'], 
                          "vc_ip": data['Server'], 
                          "cluster": data['Cluster'], 
                          "host": data['Host'],  
                          "vc_pwd": Security.encrypt(data['Password'])
                        }
            CheckerBase.save_auth_into_auth_config("vc",conf_data)
            status = {"Configuration": "Success"}
            return json.dumps(status)

        if data['operation'].split('_')[1] == "ncc":
            conf_data = { "cvm_ip": data['Server'], 
                          "cvm_pwd": Security.encrypt(data['Password']), 
                          "cvm_user": data['User']
                          }

            CheckerBase.save_auth_into_auth_config("ncc",conf_data)
            status = {"Configuration": "Success"}        
            return json.dumps(status)
    
    def check_connect(self,data):
        status = {"Connection": "Failed"}
        if data['operation'].split('_')[1] == "vc":
            ret , msg = self.checkers['vc'].check_connectivity(data['Server'],data['User'],Security.encrypt(data['Password']),data['Port'])
            
            if ret:
                status['Connection'] = "Success"
            return json.dumps(status)
    
        if data['operation'].split('_')[1] == "ncc":
            ret , msg = self.checkers['ncc'].check_connectivity(data['Server'],data['User'],Security.encrypt(data['Password']))
            if ret:
                status['Connection'] = "Success"
            return json.dumps(status)

    def POST(self): 
        data = web.input()
        #print "Post Received Data:",data,type(data)
        
        if data['operation'].split('_')[0] == "config":
            return(self.do_config(data))
            
        if data['operation'].split('_')[0] == "connect":
            return(self.check_connect(data))

        if data['operation'] == "exec_checks":
            if(self.run_checks(data)):
                return "Execution Completed"

        if data['operation'] == "refresh_logs":
            f = open("test.json", 'r')
            return f.read()
       
if __name__ == "__main__":
    web.internalerror = web.debugerror
    app.run()
