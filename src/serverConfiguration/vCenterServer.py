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
#! python
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
                task = cluster.AddHost(add_host,asConnected=True)
            except:
                print "Unexpected error:", sys.exc_info()[0]
                sys.exit(2)

            #Loop till host is getting connected // Write proper logic
            self.wait_for_task(task)
            print "\n[ Host successfully added! ]"
            print "+"+"-"*100+"+"+"\n"
        return True

    def wait_for_task(self,task,actionName="Job",hideResult=False):
        while task.info.state == vim.TaskInfo.State.running:
            time.sleep(1)
    
        if task.info.state == vim.TaskInfo.State.success:
            if task.info.result is not None and not hideResult:
                out = '%s completed successfully, result: %s' % (actionName, task.info.result)
                print out
            else:
                out = '%s completed successfully.' % actionName
                print out
        else:
            out = '%s did not complete successfully ( %s )' % (actionName, task.info.error.msg)
            #raise task.info.error
            print out
            sys.exit(1)

        return task.info.result
    
        
    def get_all_vms(self,dCenter):
        vms = []
        for child in self.si.content.rootFolder.childEntity:
            if hasattr(child, 'vmFolder') and child.name == dCenter.name:
                container = self.si.content.viewManager.CreateContainerView(child, [vim.VirtualMachine], True)
                vms = [ vm for vm in container.view]
        return vms

    
    def do_configuration(self):
        #Specify which version to run
        version = "1.0"
        print "Running version %s of the Nutanix GSO cluster provisioning script"%(version)
        print "+"+"-"*100+"+"+"\n"
        dc = self.create_datacenter()
        print "+"+"-"*100+"+"+"\n"
        newc = self.create_cluster(dc)
        print "+"+"-"*100+"+"+"\n"
        
        #Add hosts to the cluster :
        self.add_host(newc)
        print "+"+"-"*100+"+"+"\n"

        clusterObj = self.get_cluster(dc,self.confDetails['cluster'])
        clusterSpec = vim.cluster.ConfigSpec()
        
        #dasConfig
        print "Configuring vSphere HA"
        dasConfig = vim.cluster.DasConfigInfo()
        dasConfig.dynamicType = ""
        dasConfig.enabled = True
        #dasConfig.hostMonitoring = "enabled"
        dasConfig.admissionControlEnabled = True
        dasConfig.vmMonitoring = vim.cluster.DasConfigInfo.VmMonitoringState.vmMonitoringDisabled
        clusterSpec.dasConfig = dasConfig
        #dasVmConfig
        settings = []
        vms = self.get_all_vms(dc)
        for xvm in vms:
            dasVmConfigSpec = vim.cluster.DasVmConfigSpec()
            dasVmConfigSpec.operation = vim.option.ArrayUpdateSpec.Operation.add

            dasVmConfigInfo = vim.cluster.DasVmConfigInfo()
            dasVmConfigInfo.key = vms[0]
            dasVmConfigInfo.restartPriority = vim.cluster.DasVmConfigInfo.Priority.disabled
            
            vm_settings = vim.cluster.DasVmSettings()
            vm_settings.restartPriority = vim.cluster.DasVmSettings.RestartPriority.disabled
            monitor = vim.cluster.VmToolsMonitoringSettings()
            monitor.vmMonitoring = vim.cluster.DasConfigInfo.VmMonitoringState.vmMonitoringDisabled
            monitor.clusterSettings = False
            vm_settings.vmToolsMonitoringSettings = monitor
            vm_settings.isolationResponse = vim.cluster.DasVmSettings.IsolationResponse.none
            dasVmConfigInfo.dasSettings = vm_settings
            dasVmConfigSpec.info = dasVmConfigInfo
            
            settings.append(dasVmConfigSpec)
        clusterSpec.dasVmConfigSpec = settings
        
        #drsConfig
        print "+"+"-"*100+"+"+"\n"
        print "Configuring vSphere DRS"
        drsConfig = vim.cluster.DrsConfigInfo()
        drsConfig.enabled = True
        #possible values : fullyAutomated/manual/partiallyAutomated
        drsConfig.defaultVmBehavior = vim.cluster.DrsConfigInfo.DrsBehavior.fullyAutomated
        clusterSpec.drsConfig = drsConfig

        #drsVmConfig
        settings = []
        vms = self.get_all_vms(dc)
        for xvm in vms:
            drsVmConfigSpec = vim.cluster.DrsVmConfigSpec()
            drsVmConfigSpec.operation = vim.option.ArrayUpdateSpec.Operation.add

            drsVmConfigInfo = vim.cluster.DrsVmConfigInfo()
            drsVmConfigInfo.key = xvm
            drsVmConfigInfo.enabled = False
            drsVmConfigInfo.behavior = vim.cluster.DrsConfigInfo.DrsBehavior.partiallyAutomated
            
            drsVmConfigSpec.info = drsVmConfigInfo
            settings.append(drsVmConfigSpec)
        clusterSpec.drsVmConfigSpec = settings

        #dpmConfigSpec
        
        
        #Reconfigure cluster with above configuration
        print "+"+"-"*100+"+"+"\n"
        task = clusterObj.ReconfigureCluster_Task(clusterSpec, True)
        print "Reconfigured cluster for Health Check Properties"
        self.wait_for_task(task)
        
        #Reconfigure Host Properties
        #START
        #ESXi Checks
        '''
        #1 host - set hyperthreading enabled 
        #https://github.com/vmware/pyvmomi/blob/master/docs/vim/host/ConfigInfo.rst
        vim.host.ConfigInfo
        
        #2. host - set power management information
        vim.host.ConfigInfo
        
        #3. host - set ntp client to enabled
        vim.host.ConfigInfo
        
        #4. Configure ntp servers

        #5. dns & Routing settings-
        #https://github.com/vmware/pyvmomi/blob/master/docs/vim/host/NetworkInfo.rst

        #6. Authentication inforamtion -
        #https://github.com/vmware/pyvmomi/blob/master/docs/vim/host/AuthenticationManagerInfo.rst
        '''
        #END
        
        #Confirm all ESXi hosts in the cluster has a 'connected' status.
        cluster_hosts = clusterObj.host
        for xhost in cluster_hosts:
            if xhost.runtime.connectionState is 'disconnected':
                xhost.ReconnectHost_Task()

        print "+"+"-"*100+"+"+"\n"
        self.disConnectVC()

        '''
        atexit.register(connect.Disconnect, service_instance)
        atexit.register(endit)
        '''