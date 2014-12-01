#!/usr/bin/env python
#title           :clusterProvision.py
#description     :This will do the provisioning like creating datacenter,cluster,resource pool,etc & Adding Host & configuring network etc.
#author          :GaneshM
#date            :2014/11/21
#version         :1.0
#usage           :python clusterProvision.py input.json
#notes           :
#python_version  :2.7.8  
#==============================================================================

import atexit,ast
from pyVim import connect
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
from requests.exceptions import ConnectionError
import warnings
import sys,os,json,time
import requests
import paramiko

class VCenterServerConf:
    def __init__(self,confDetails):
        self.confDetails = confDetails
        self.si = None
        self.connectVC()
    
    def connectVC(self):
        warnings.simplefilter('ignore')
        try:
            self.si = connect.SmartConnect(host=self.confDetails['host'],user=self.confDetails['user'],pwd=self.confDetails['password'],port=self.confDetails['port'])
            print "Connection to vCenter Server(%s) is Successful"%(self.confDetails['host'])
        except vim.fault.InvalidLogin:
            print "Error : Invalid Username and Password Combination."
            sys.exit(2)
        except ConnectionError as e:
            print "Error : Connection Error - Couldn't Connect Specified Server."
            sys.exit(2)
    
    def disConnectVC(self):
        Disconnect(self.si)
        print "Connection to vCenter Server(%s) is Revoked"%(self.confDetails['host'])

    def list_datacenters(self):
        installed_dcs = []
        childEntity = self.si.content.rootFolder.childEntity
        installed_dcs.extend([childEntity[i].name for i in range(0,len(childEntity))])
        return installed_dcs

    def get_datacenter(self,dcName):
        folder = self.si.content.rootFolder
        if folder is not None and isinstance(folder, vim.Folder):
            for dc in folder.childEntity:
                if dc.name == dcName:
                    return dc
        return None


    def create_datacenter(self):
        dcName,reuseAction = self.confDetails['datacenter'],self.confDetails['datacenter_reuse_if_exist']

        avail_datacenters = self.list_datacenters()
        folder = self.si.content.rootFolder
        
        # Create a new Datacenter     
        if folder is not None and isinstance(folder, vim.Folder):    
            name = dcName
            if reuseAction.lower()=="true":
                action = "update"
            else:
                action = "create"
            
            if action == "create":
                if name not in avail_datacenters:
                    print "Creating new datacenter: %s "%(name)
                    newdc = folder.CreateDatacenter(name=name)
                    print "[ Datacenter successfully created! ]"
                else:
                    print "[Datacenter already exists ]"
                    sys.exit(2)
            elif action == "update":
                if name not in avail_datacenters:
                    print "Creating new datacenter: %s "%(name)
                    newdc = folder.CreateDatacenter(name=name)
                    print "[ Datacenter successfully created! ]"
                else:
                    print "[Datacenter already exists; Updating it ]"
                    newdc = self.get_datacenter(name)
            else:
                print "[ Invalid action selected ! ]"
                sys.exit(2)
        return newdc

    def list_clusters(self,datacenter=None):
        # List Clusters in given Datacenter
        avail_clusters = []
        clusters = datacenter.hostFolder.childEntity
        avail_clusters.extend([clusters[i].name for i in range(0,len(clusters))])
        return avail_clusters

    def get_cluster(self,dc,cName):
        folder = dc.hostFolder
        if folder is not None and isinstance(folder, vim.Folder):
            for clust in folder.childEntity:
                if clust.name == cName:
                    return clust
        return None

    def create_cluster(self, datacenter):
        cName,reuseAction = self.confDetails['cluster'],self.confDetails['cluster_reuse_if_exist']
        
        # create new cluster in given Datacenter
        if cName is None:
            raise ValueError("Missing value for name.")
            sys.exit(2)
        if datacenter is None:
            raise ValueError("Missing value for datacenter.")
            sys.exit(2)
        
        #clusterSpec = vim.cluster.ConfigSpecEx()
        clusterSpec = vim.cluster.ConfigSpec()
        avail_clusters = self.list_clusters(datacenter)
        name = cName
        if reuseAction.lower()=="true":
            action = "update"
        else:
            action = "create"

        if action == "create":
            if name not in avail_clusters:
                print "Creating new cluster: %s in datacenter: %s "%(name,datacenter.name)
                newc = datacenter.hostFolder.CreateCluster(name=name, spec=clusterSpec)
                print "[ Cluster successfully created! ]"
            else:
                print "[Cluster already exists ]"
                sys.exit(2)
        elif action == "update":
            if name not in avail_clusters:
                print "Creating new cluster: %s in datacenter: %s "%(name,datacenter.name)
                newc = datacenter.hostFolder.CreateCluster(name=name, spec=clusterSpec)
                print "[ Cluster successfully created! ]"
            else:
                print "[ Cluster already exists; Updating it ]"
                newc = self.get_cluster(datacenter,name)
        else:
            print "[ Invalid action selected ! ]"
            sys.exit(2)        
        return newc

    def getSSLThumbprint(self,host,user,passwd):
        ssh=None
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, username=user, password=passwd)
        except paramiko.AuthenticationException:
            exit_with_message("Error : "+ "Authentication failed - Invalid username or password.")
        except paramiko.SSHException, e:
            exit_with_message("Error : "+ str(e))
        except socket.error, e:
            exit_with_message(str(e))

        cmd = 'openssl x509 -sha1 -in /etc/vmware/ssl/rui.crt -noout -fingerprint'
        stdin, stdout, stderr =  ssh.exec_command(cmd)
        for line in stdout:
            if 'SHA1' in line:
                xsslThumbprint = line.split('=')[1]
        ssh.close()
        return xsslThumbprint.strip()
    
    def add_host(self,cluster):
        avail_hosts =  [ host.name for host in cluster.host ]
        hosts = self.confDetails['hosts']
        for xhost in hosts:
            print "Adding host %s to cluster %s "%(xhost['ip'], cluster.name)

            # confiugre connectspec using sslThumbprint
            sslThumbprint = self.getSSLThumbprint(xhost['ip'],xhost['user'],xhost['pwd'])
            if xhost['ip'] in avail_hosts:
                print "[ Host(%s) already exists ]"%(xhost['ip'])
                print "+"+"-"*100+"+"+"\n"
                continue

            print "-- Please be patient.  This could take a few moments --"
            add_host = vim.host.ConnectSpec(hostName=xhost['ip'],userName=xhost['user'],password=xhost['pwd'],sslThumbprint=sslThumbprint)
            try:
                taskid = cluster.AddHost(add_host,asConnected=True)
            except:
                print "Unexpected error:", sys.exc_info()[0]
                sys.exit(2)

            #Loop till host is getting connected // Write proper logic
            for i in range(15):
                print ".",
                time.sleep(1)

            print "\n[ Host successfully added! ]"
            print "+"+"-"*100+"+"+"\n"
        return True
    
    def do_configuration(self):
        #Specify which version to run
        version = "1.0"
        print "Running version %s of the Nutanix GSO cluster provisioning script"%(version)
        print "+"+"-"*100+"+"+"\n"
        dc = self.create_datacenter()
        print "+"+"-"*100+"+"+"\n"
        newc = self.create_cluster(dc)
        print "+"+"-"*100+"+"+"\n"
        #Enable HA For a cluster
        clusterObj = self.get_cluster(dc,self.confDetails['cluster'])
        clusterSpec = vim.cluster.ConfigSpec()
        
        #cluster parameters
        #possible values :vmDirectory/hostLocal/inherit
        newc.configurationEx.vmSwapPlacement = "hostLocal"

        #dasConfig
        print "Configuring vSphere HA"
        dasconfig = vim.cluster.DasConfigInfo()
        dasconfig.dynamicType = ""
        dasconfig.enabled = True
        dasconfig.hostMonitoring = "enabled"
        dasconfig.admissionControlEnabled = True
        dasconfig.vmMonitoring = "vmMonitoringDisabled"
        clusterSpec.dasConfig = dasconfig

        #dasVmConfig
        dasVmConfig = vim.cluster.DasVmConfigInfo()
        dasVmConfig.restartPriority = "enabled"
        #clusterSpec.dasVmConfigSpec = dasVmConfig

        #drsConfig
        print "+"+"-"*100+"+"+"\n"
        print "Configuring vSphere DRS"
        drsConfig = vim.cluster.DrsConfigInfo()
        drsConfig.enabled = True
        #possible values : fullyAutomated/manual/partiallyAutomated
        drsConfig.defaultVmBehavior = "fullyAutomated"
        clusterSpec.drsConfig = drsConfig

        #drsVmConfig
        clusterSpec_ex = vim.cluster.ConfigSpecEx()
        drsVmConfig = vim.cluster.DrsVmConfigInfo()
        drsVmConfig.enabled = True
        drsVmConfigSpec = vim.cluster.DrsVmConfigSpec()
        drsVmConfigSpec.info = drsVmConfig
        for vm in clusterSpec_ex.drsVmConfigSpec:
            vm.drsVmConfigSpec = drsVmConfigSpec
        
        #Reconfigure cluster with above configuration
        print "+"+"-"*100+"+"+"\n"
        task = clusterObj.ReconfigureCluster_Task(clusterSpec, True)
        print "Reconfigure cluster for Health Check Properties"

        #Reconfigure Host Properties

        #Confirm all ESXi hosts in the cluster has a 'connected' status.
        cluster_hosts = clusterObj.host
        for xhost in cluster_hosts:
            if xhost.runtime.connectionState is 'disconnected':
                xhost.ReconnectHost_Task()

        print "+"+"-"*100+"+"+"\n"
        self.add_host(newc)
        
        #print "+"+"-"*100+"+"+"\n"
        self.disConnectVC()

        '''
        atexit.register(connect.Disconnect, service_instance)
        atexit.register(endit)
        '''