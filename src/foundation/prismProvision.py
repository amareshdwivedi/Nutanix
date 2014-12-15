'''
Created on Nov 25, 2014

@author: krishnamurthy_b
'''
import requests
import json
import os,sys
import warnings

class PrismActions:
    def __init__(self,provDetails):
        self.restURL = provDetails['restURL']
        self.loginDetails = provDetails['authentication']
        self.storagePool = provDetails['storagepool']
        self.container = provDetails['container']

        #self.create_storage_pool()
        #self.create_container()
    def get_disk_ids(self):
        userName,passwd = self.loginDetails['username'],self.loginDetails['password']
        
        warnings.simplefilter('ignore')
        headers = {'content-type': 'application/json'}
        try:
            response = requests.get(self.restURL+'v1/disks/', headers=headers, auth=(userName, passwd), verify=False)
            if response.status_code != 200:
                return None
            responseJson = json.loads(response.text)
            return [ disk['id'] for disk in responseJson['entities']]
        except requests.ConnectionError, e:
            print 'A connection attempt failed because the Prism API serer did not properly responded' 
            sys.exit(1)
        except :
            print "Unexpected error:", sys.exc_info()[0]
            sys.exit(1)

    def get_storagePool_id(self):
        userName,passwd = self.loginDetails['username'],self.loginDetails['password']
    
        warnings.simplefilter('ignore')
        headers = {'content-type': 'application/json'}
        response = requests.get(self.restURL+'v1/storage_pools/', headers=headers, auth=(userName, passwd), verify=False)
        if response.status_code != 200:
            return None

        responseJson = json.loads(response.text)
        return responseJson['entities'][0]['id']


    def create_storage_pool(self):
        userName,passwd = self.loginDetails['username'],self.loginDetails['password']
    
        warnings.simplefilter('ignore')
        self.storagePool['disks'] = self.get_disk_ids()
        self.storagePool['id'] = None

        headers = {'content-type': 'application/json'}
        response = requests.post(self.restURL+'v1/storage_pools/?force=true', headers=headers, auth=(userName, passwd), data=json.dumps(self.storagePool), verify=False)
        response_code = response.status_code
        if(response_code == 500):
            return "A Storage Pool named "+self.storagePool['name']+" already exists"
        elif(response_code == 200):
            return "Storage Pool Successfully created"
        elif(response_code == 401):
            return "Exception : Incorrect Credentials"
        elif(response_code == 400):
            return "Exception : Unauthorized user"
        elif(response_code == 404):
            return "Exception : Page Not Found"
        else:
            return "Exception : Unknown Error occurred"


    def create_container(self):
        userName,passwd = self.loginDetails['username'],self.loginDetails['password']
        self.container['storagePoolId'] = self.get_storagePool_id()
        warnings.simplefilter('ignore')
        headers = {'content-type': 'application/json'}
        response = requests.post(self.restURL+'v1/containers/', headers=headers, auth=(userName,passwd), data=json.dumps(self.container), verify=False)
        response_code = response.status_code
        if(response_code == 500):
            return "A container named "+self.container['name']+" already exists"
        if(response_code == 200):
            return "Container Successfully created"
        elif(response_code == 401):
            return "Exception : Incorrect Credentials"
        elif(response_code == 400):
            return "Exception : Unauthorized user"
        elif(response_code == 404):
            return "Exception : Page Not Found"
        else:
            return "Exception : Unknown Error occurred"
