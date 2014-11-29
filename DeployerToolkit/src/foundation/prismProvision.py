'''
Created on Nov 25, 2014

@author: krishnamurthy_b
'''
import requests
import json
import os
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
        response = requests.get(self.restURL+'v1/disks/', headers=headers, auth=(userName, passwd), verify=False)
        if response.status_code != 200:
            return None

        responseJson = json.loads(response.text)
        return [ disk['id'] for disk in responseJson['entities']]

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
            print response.text
        elif(response_code == 200):
            print "Storage Pool Successfully created"
        elif(response_code == 401):
            print "Incorrect Credentials"
        elif(response_code == 400):
            print "Unauthorized user"
        elif(response_code == 404):
            print "Page Not Found"
        else:
            print "Error occurred"


    def create_container(self):
        userName,passwd = self.loginDetails['username'],self.loginDetails['password']
        self.container['storagePoolId'] = self.get_storagePool_id()
        warnings.simplefilter('ignore')
        headers = {'content-type': 'application/json'}
        response = requests.post(self.restURL+'v1/containers/', headers=headers, auth=(userName,passwd), data=json.dumps(self.container), verify=False)
        
        response_code = response.status_code
        if(response_code == 500):
            print response.text
        elif(response_code == 200):
            print "Container Successfully created"
        elif(response_code == 401):
            print "Incorrect Credentials"
        elif(response_code == 400):
            print "Unauthorized user"
        elif(response_code == 404):
            print "Page Not Found"
        else:
            print "Error occurred"
