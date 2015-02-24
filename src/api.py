'''
Created on Jan 2, 2015

@author: RohitD
'''
import requests
import web
import httplib
from model import DataModel       
from definedconstants import *
import json 
from deployer_web import initiate_deployment
import os,sys
db = web.database(dbn='sqlite', db='deployer')
model = DataModel(db) 

class customers:
    """
        This class expose  restfull api's 
        related to customer.We can get list of customers 
        ,details of specific   customer .
    """

    def GET(self,id = None):
        final_data = {}
        if id:
            get_customer_data = model.get_by_id(id)
            web.header( 'Content-Type','application/json' )
            if get_customer_data:
                get_customer_hostory = model.get_history_by_id(id)
                final_data['customer_record'] = get_customer_data
                final_data['customer_history'] = get_customer_hostory
                final_data['response'] = httplib.OK
            else:
                final_data['response'] = httplib.NOT_FOUND
                final_data['error'] = USER_NOT_FOUND
            return json.dumps(final_data)
        else:
            all_customers = model.get_all_customers()
            if all_customers:
                final_data['customer_record'] = all_customers
                final_data['response'] = httplib.OK
                return json.dumps(final_data)
            else:
                final_data['response'] = httplib.NOT_FOUND
                final_data['error'] = USER_NOT_FOUND
                
            return json.dumps(final_data)  

    def POST(self):
        final_data = {}
        customer_id = None
        customer_name = None
        try:
            data = json.loads(web.data())
            customer_id = data['customer_id']
            customer_name = data['customer_name']
            customer_phone = data['customer_phone']   
            customer_email= data['customer_email']
			
        except:
            final_data['response'] = httplib.NOT_FOUND
            final_data['error'] = INVALID_INPUT
            return json.dumps(final_data)       
        get_customer_data = model.get_by_id(customer_id)
        if get_customer_data:
            final_data['response'] = httplib.FORBIDDEN
            final_data['error'] = USER_ALREADY_EXIST   
            return json.dumps(final_data)         
        else:
            resp = model.add_customer(customer_name,customer_id,customer_email,customer_phone)
            if resp:
                final_data['response'] = httplib.OK
                final_data['customer_id'] = customer_id  
                final_data['message'] = USER_CREATED_SUCCESSFULLY  
                return json.dumps(final_data)                   

class customertasks:
    """
        This class expose  restfull api's 
        related to customer task.Customer can create  task 
        get the details of tasks using this api.
    """    
    
    def POST(self,cid):
        final_data = {}
        data =  web.data()
        input_json = data
        if cid:
            get_customer_data = model.get_by_id(cid)
            if get_customer_data:
                add_to_task = model.add_task(cid,input_json,"Deployment")
                final_data['task_id'] = add_to_task
                final_data['response'] = httplib.OK                
                return json.dumps(final_data)
            else:
                final_data['response'] = httplib.NOT_FOUND
                final_data['error'] = USER_NOT_FOUND   
                return json.dumps(final_data)         
        else:
            final_data['response'] = httplib.NOT_FOUND
            final_data['error'] = BAD_REQUEST            
            return json.dumps(final_data)
 
    def GET(self,cid = None,tid = None):
        final_data = {}
        if cid and tid:
            get_customer_data = model.get_by_id(cid)
            web.header( 'Content-Type','application/json' )
            if get_customer_data:
                get_customer_specific_task = model.get_history_by_taskid(cid,tid)
                if get_customer_specific_task:
                    final_data['customer_task'] = get_customer_specific_task
                    final_data['response'] = httplib.OK
                else:
                    final_data['error'] = TASK_NOT_EXIST
                    final_data['response'] = httplib.NOT_FOUND
            else:
                final_data['response'] = httplib.NOT_FOUND
                final_data['error'] = USER_NOT_FOUND
                
            return json.dumps(final_data)
        elif cid:
            all_tasks = model.get_history_by_id(cid)
            if all_tasks:
                final_data['customer_tasks'] = all_tasks
                final_data['response'] = httplib.OK
                return json.dumps(final_data)
            else:
                final_data['response'] = httplib.NOT_FOUND
                return json.dumps(final_data)
        else:
            final_data['error'] = httplib.BAD_REQUEST
            final_data['response'] = httplib.OK
            return json.dumps(final_data)      

        
        
class nodedetails:
    """
        Will be using this api to get the number of 
        nodes requeired for a perticular model.
        model number will be input to get blocks.
    """     
    def POST(self):
        final_data = {}
        try:
            data = json.loads(web.data())
            model_number = data['model']
        except:
            final_data['response'] = httplib.NOT_FOUND
            final_data['error'] = INVALID_INPUT
            return json.dumps(final_data)
            
        if model_number:
            get_node_data = model.get_number_of_nodes(model_number)
            web.header( 'Content-Type','application/json' )
            if get_node_data:
                final_data['nodes'] = get_node_data
                final_data['response'] = httplib.OK
            else:
                final_data['response'] = httplib.NOT_FOUND
                final_data['error'] = MODEL_NOT_EXIST
            return json.dumps(final_data)

        else:
            final_data['error'] = MODEL_ID_MISSING
            final_data['response'] = httplib.BAD_REQUEST
            return json.dumps(final_data)      


class customeraction:
    """
        This class expose  restfull api's 
        related to customer action.We are initiating and monitoring
        progress of foundation ,vcener and prism .
    """   
    def POST(self):
        final_data = {}
        customer_id = None
        module_id = None
        task_id = None
        modules = ['foundation','prism','vcenter']
		
        try:
            data = json.loads(web.data())
            customer_id = data['customer_id']
            module_id = data['module_id']
            task_id = data['task_id']
        except:
            final_data['response'] = httplib.NOT_FOUND
            final_data['error'] = INVALID_INPUT
            return json.dumps(final_data)
		
        get_customer_data = model.get_by_id(customer_id)
        if get_customer_data:
            task_is_exist = model.get_history_by_taskid(customer_id,task_id)
            json_to_initilize = json.loads(task_is_exist[0]['json_data'])
            if task_is_exist:
                if module_id in modules:
                    deploy = initiate_deployment(json_to_initilize)
                    if not model.get_task_status_by_id(task_id):

                        model.create_task_module_status(task_id,'foundation','Not started')
                        model.create_task_module_status(task_id,'prism',' Not started')
                        model.create_task_module_status(task_id,'vcenter','Not started')
                   
                    if module_id == "foundation":
                        model.update_task(task_id,'In-Progress')
                        model.update_task_module_status(task_id,'foundation','started')
                        try:
                            resp = deploy.initiate_foundation()
                            final_data['response'] = httplib.OK
                            final_data['status'] = resp
                        except:
                            final_data['response'] = httplib.INTERNAL_SERVER_ERROR
                        return json.dumps(final_data)
                    
                    if module_id == "vcenter":
                        model.update_task_module_status(task_id,'vcenter','started')
                        try:
                            resp = deploy.initiate_vcenter_server_config()
                            model.update_task_module_status(task_id,'vcenter','Completed')
                            final_data['response'] = httplib.OK
                        except:
                            resp = None
                            model.update_task_module_status(task_id,'vcenter',"Failed")
                            final_data['response'] = httplib.INTERNAL_SERVER_ERROR
                        if resp:
                            model.update_task_module_status(task_id,'vcenter',"Completed")
                        #else:
                        #    model.update_task_module_status(task_id,'vcenter',"Failed")

                        final_data['status'] = resp
                        return json.dumps(final_data)
                    
                    if module_id == "prism":
                        model.update_task_module_status(task_id,'prism','started')
                        try:
                            resp = deploy.initiate_cluster_config()
                            final_data['response'] = httplib.OK
                            final_data['status'] = resp
                        except:
                            resp = None
                            model.update_task_module_status(task_id,'prism',"Failed")
                            final_data['response'] = httplib.INTERNAL_SERVER_ERROR							
                        if resp :
                            model.update_task_module_status(task_id,'prism',"Completed")
                        
                        return json.dumps(final_data)                                        
                else:
                    final_data['response'] = httplib.NOT_FOUND
                    final_data['error'] = MODULE_NOT_ALLOWED                
                    return json.dumps(final_data)                     
                
            else:
                final_data['response'] = httplib.NOT_FOUND
                final_data['error'] = TASK_NOT_EXIST                
                return json.dumps(final_data) 
            
        else:
            final_data['response'] = httplib.NOT_FOUND
            final_data['error'] = USER_NOT_FOUND   
            return json.dumps(final_data) 
                     

class deploymentstatus:
    
    def GET(self,cid,tid):        
        final_data = {}
        if cid and tid: 
            get_customer_data = model.get_by_id(cid)
            web.header( 'Content-Type','application/json' )
            if get_customer_data:
                get_customer_specific_task = model.get_history_by_taskid(cid,tid)
                if get_customer_specific_task:
                    json_to_initilize = json.loads(get_customer_specific_task[0]['json_data'])
                    deploy = initiate_deployment(json_to_initilize)
                    resp = deploy.check_foundation_progress()   
                    
                    if int(resp) == 100:
                        model.update_task(tid,'Completed') 

                    model.update_task_module_status(tid,'foundation',str(round(float(resp),2))+"%")                  
                    get_task_status = model.get_task_status_by_id(tid)
                    if get_task_status:
                        final_data['task_status'] = get_task_status
                        final_data['response'] = httplib.OK
                    else:
                        final_data['error'] = INTERNAL_SERVER_ERROR
                        final_data['response'] = httplib.INTERNAL_SERVER_ERROR                        
                else:
                    final_data['error'] = TASK_NOT_EXIST
                    final_data['response'] = httplib.NOT_FOUND
            else:
                final_data['response'] = httplib.NOT_FOUND
                final_data['error'] = USER_NOT_FOUND
                
            return json.dumps(final_data)
        elif cid:
            all_tasks = model.get_history_by_id(cid)
            if all_tasks:
                final_data['customer_tasks'] = all_tasks
                final_data['response'] = httplib.OK
                return json.dumps(final_data)
            else:
                final_data['response'] = httplib.NOT_FOUND
                return json.dumps(final_data)
        else:
            final_data['error'] = httplib.BAD_REQUEST
            final_data['response'] = httplib.OK
            return json.dumps(final_data)      

class customerReports:    
    def GET(self,cid):
        if cid:
            customerReportFiles = model.list_report_files(cid)
            import os
            from os import listdir  
            from os.path import isfile, join
            import web_health_check
            if web_health_check.cur_dir is not None:
                reportDir = web_health_check.cur_dir + os.path.sep +"reports"
            else:
                reportDir = os.getcwd() + os.path.sep +"reports"

            allReportFiles = [ f for f in listdir(reportDir) if isfile(join(reportDir,f)) ]
            final_data = {}
            reports = []
            for xitem in customerReportFiles:
                fileName, dateCreated = xitem.values()
                if str(fileName) in allReportFiles:
                    currentReport = {}
                    currentReport['filename'] = str(fileName)
                    currentReport['date_created'] = str(dateCreated)
                    reports.append(currentReport)
            final_data['customer_reports'] = reports
            final_data['response'] = httplib.OK

            web.header( 'Content-Type','application/json' )
            return json.dumps(final_data)

class downloadReports:
    def POST(self):
        try:
            data = json.loads(web.data())
            #web.header('Content-type','application/octet-stream')
            #web.header('Content-transfer-encoding','base64') 
            f = open(os.getcwd() + os.path.sep +"reports" + os.path.sep +data['filename'], 'r')
            return f.read()
            
        except:
            #print sys.exc_info()[0]
            return ''

class isoImages:    
    def POST(self):
        final_data = {}
        try:
            data = json.loads(web.data())
            headers = {'content-type': 'application/json'}
            
            iso_url = ''
            if data['imageType'] == "nos":
                iso_url = "http://"+data['foundationVM']+":8000/foundation/enumerate_nos_isos"
            if data['imageType'] == "hypervisor":
                iso_url = "http://"+data['foundationVM']+":8000/foundation/enumerate_hypervisor_isos"
            
            response = requests.get(iso_url)
            final_data['response'] = httplib.OK
            final_data['images'] = response.text
        except:
            final_data['response'] = httplib.NOT_FOUND
            final_data['images'] = []
        return json.dumps(final_data)

             