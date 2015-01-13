import datetime
from validation import Validate
from distutils.log import info


def diff_dates(licencedate):
    today = datetime.date.today()
    licenceDate = datetime.datetime.strptime(licencedate, "%Y-%m-%d").date()
    return  (licenceDate - today).days
    
def get_vc_check_actual_output_format(check_name,actual_value,entity,datacenter,cluster,host,status,message,exp_value_from_msg,vCenterServerIP):
    actual_value=actual_value.strip()
    exp_value_from_msg=exp_value_from_msg.strip()
    
    if entity == "host" and actual_value == "Not-Configured":
        return 'Cluster Skipped', False , ''
        
    # Start of Cluster Checks
    if check_name == "CPU Compatibility-EVC":
        if actual_value == "None":
            return "EVC mode on cluster ["+cluster+"] is set to [Disabled]", True , 'info'
        else:
            return "EVC baseline on cluster ["+cluster+"] is set to ["+actual_value+"]", True , ''
        
    if check_name == "Host's Connected State":
        if actual_value.lower() == 'connected':
            return "Host ["+ host +"] is in [Connected] state" , False, ''
        elif actual_value=='Not-Configured':
            return 'No host found', False , 'info'
        else:
            return "Host ["+host+"] is in ["+actual_value+"] state" , True , 'alert'
        
    if check_name == "Cluster DRS":
        if actual_value == "True":
            return 'DRS on cluster ['+cluster+'] is [Enabled]', True, ''
        elif actual_value == "False":
            return 'DRS on cluster ['+cluster+'] is [Disabled]', True, 'warning'
        else:
            return 'DRS on cluster ['+cluster+'] is ['+actual_value+']', True, 'warning'
        
    if check_name == "Cluster DRS Automation Mode":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, ''
        elif actual_value == "fullyAutomated":
            return 'DRS Automation Mode on cluster ['+cluster+'] is [Fully Automated]', True, ''
        elif actual_value == "manual":
            return 'DRS Automation Mode on cluster ['+cluster+'] is [Manual]', True, 'warning'
        elif actual_value == "partiallyAutomated":
            return 'DRS Automation Mode on cluster ['+cluster+'] is [Partially Automated]', True, 'info'
        else: 
            return actual_value, False, ''
        
    if check_name == "DRS Automation Mode for CVM":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, ''
        elif actual_value == "fullyAutomated":
            return 'DRS Automation Mode On CVM ['+entity+'] is [Not Disabled]', True, 'warning'
        else: 
            return actual_value, False, ''
    
    if check_name == "Cluster Load Balanced":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False , ''
        if actual_value == 'NA':
            return 'Current balance and Target balance are [NA]', True , "warning"
        elif actual_value <= exp_value_from_msg:
            return 'Current balance is ['+str(actual_value)+'] , Target balance is ['+str(exp_value_from_msg)+']', True, "info"
        else: 
            return 'Current balance is ['+str(actual_value)+'] , Target balance is ['+str(exp_value_from_msg)+']' , True, "warning"
    
    if check_name == "Cluster Host Monitoring":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False , ''
        elif actual_value != "enabled":
            return 'Host Monitoring on cluster ['+cluster+'] is ['+actual_value+']', True, 'warning'
        else: 
            return actual_value, False, ''
        
    if check_name == "Cluster Admission Control":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False,''
        elif actual_value == "False":
            return 'Admission Control on cluster ['+cluster+'] is [Disabled]', True , 'warning'
        elif actual_value == "True":
            return 'enabled', False,''
        else: 
            return actual_value, False,''
        
    if check_name == "Host Isolation Response":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, ''
        elif actual_value == "powerOff":
            return 'powerOff', False, ''
        else: 
            return 'Isolation Response on cluster ['+cluster+'] is ['+actual_value+']', True, 'alert'
            
    if check_name == "Validate Datastore Heartbeat":
        if actual_value == "Not-Configured":
            return 'For cluster['+cluster+'], no datastores are configured for storage heartbeating', True, 'info'
        else: 
            return 'For cluster['+cluster+'], datastore['+actual_value+'] are configured for storage heartbeating', True, 'info'
        
    if check_name == "Cluster Advance Settings das.ignoreInsufficientHbDatastore":
        if actual_value == "Not-Configured":
            return 'Advance Settings das.ignoreInsufficientHbDatastore is [Not-Configured]', True, 'info'
        elif actual_value== "false": 
            return 'Advance Settings das.ignoreInsufficientHbDatastorestr is ['+actual_value+']', True, 'info'
        else:
            return actual_value, False, 'info'
        
    if check_name == "Cluster Power Management Setting":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, ''
        elif actual_value == "True":
            return "Off", False, ''
        else: 
            return 'Power Management Setting on cluster ['+cluster+'] is [Not off]', True, 'warning'
        
    if check_name == "VM Swap Placement":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, ''
        elif actual_value == "vmDirectory":
            return "vmDirectory", False, ''
        else: 
            return 'VM Swap Placement on cluster ['+cluster+'] is ['+actual_value+']', True, 'warning'
        
    if check_name == "Cluster Advance Settings das.useDefaultIsolationAddress":
        if actual_value == "false":
            return "false", False, ''
        else: 
            return 'Advance Settings das.useDefaultIsolationAddress on cluster ['+cluster+'] is ['+actual_value+']', True, 'alert'
        
    if check_name == "Cluster Advance Settings das.isolationaddress1":
        if actual_value == "Not-Configured":
            return 'Advance Settings das.isolationaddress1 is [Not Set]', True, 'alert'
        elif status == "FAIL": 
            if actual_value.startswith('Advance'):
                return 'Advance Settings das.isolationaddress1 on cluster ['+cluster+'] is ['+actual_value+']', True, 'alert'
            else:
                return 'Advance Settings das.isolationaddress1 on cluster ['+cluster+'] is [Not CVM IP]', True, 'alert'
        elif status == "PASS": 
            return actual_value, False,''
        
    if check_name == "Cluster Advance Settings das.isolationaddress2":
        if actual_value == "Not-Configured":
            return 'Advance Settings das.isolationaddress2 is [Not Set]', True, 'alert'
        elif status == "FAIL": 
            if actual_value.startswith('Advance'):
                return'Advance Settings das.isolationaddress2 on cluster ['+cluster+'] is ['+actual_value+']', True, 'alert'
            else:
                return 'Advance Settings das.isolationaddress2 on cluster ['+cluster+'] is [Not CVM IP]', True, 'alert'
        elif status == "PASS": 
            return actual_value, False,''
        
    if check_name == "Cluster Advance Settings das.isolationaddress3":
        if actual_value == "Not-Configured":
            return 'Advance Settings das.isolationaddress3 is [Not Set]', True, 'alert'
        elif status == "FAIL": 
            if actual_value.startswith('Advance'):
                return 'Advance Settings das.isolationaddress3 on cluster ['+cluster+'] is ['+actual_value+']', True, 'alert'
            else:
                return 'Advance Settings das.isolationaddress3 on cluster ['+cluster+'] is [Not CVM IP]', True, 'alert'
        elif status == "PASS": 
            return actual_value, False,'' 
          
    if check_name == "DataStore Connectivity with Hosts":
        if status == "FAIL":
            if actual_value == "Not-Configured":
                if host=="":
                    return "No host found", False, 'info'
                else:
                    return "No Datastore mounted to host["+host+"]", True, 'alert'
            elif actual_value == "False": 
                return "Datastore["+entity+"] is not mounted to host["+host+"]", True, 'alert'  
        if status == "PASS":
            return "Datastore["+entity+"] is mounted to host["+host+"]", False, ''
        
    if check_name =="VSphere Cluster Nodes in Same Version":
        if status == "FAIL":
            if actual_value == "Not-Configured":
                return "No host found", False, 'info'
            else:
                return "VSphere Cluster Nodes in multiple version ["+actual_value+"]", True, "warning"
        elif status == "PASS":
            return "VSphere Cluster Nodes in same version ["+actual_value+"]", False, ''
    
    if check_name =="Number of DRS Faults":
        return "On Cluster["+cluster+"] | Number of DRS faults are ["+actual_value+"]", True, ''
    
    if check_name =="Number of Cluster Events":
        return "On Cluster["+cluster+"] | Number of Events are ["+actual_value+"]", True, ''    
    
    if check_name =="Cluster Memory Utilization %":
        if actual_value == "total_memory_is_zero":
            return "On Cluster["+cluster+"] | Total Memory is [0]", True, 'alert'
        return "On Cluster["+cluster+"] | Memory Consumed is ["+actual_value+"]", True, ''
    
    if check_name =="Cluster Memory Overcommitment":
        if actual_value == "total_memory_is_zero":
            return "On Cluster["+cluster+"] | Total Memory is [0]", True, 'alert'
        return "On Cluster["+cluster+"] | Memory Oversubscrption is ["+actual_value+"]", True, ''
    
    if check_name =="Ratio pCPU/vCPU":
        if actual_value == "pCPU_is_zero":
            return "On Cluster["+cluster+"] | pCPU is 0", True, 'alert'
        return "On Cluster["+cluster+"] | Ratio pCPU/vCPU is  ["+actual_value+"]", True, ''
    
    if check_name =="Admission Control Policy - Percentage Based on Nodes in the Cluster":
        if status == 'FAIL':
            if actual_value == "ACP is disabled":
                return "For Cluster["+cluster+"],"+actual_value,True, 'alert'
            else:
                return "For Cluster["+cluster+"],"+actual_value,True, 'warning'
            
    if check_name == "Storage DRS":
        if actual_value == 'False':
            return "Datastore ["+entity+"] is in DRS cluster ["+cluster+"] where DRS autmation is enabled", True, 'alert'
        elif actual_value == 'True':
            return "Datastore ["+entity+"] is in DRS cluster ["+cluster+"] where DRS autmation is enabled", False, 'info'
        else:
            return "Storage Cluster not found", False, 'info'
              
    if check_name == "Resource Pool Memory Limits (in MB)" or check_name=="Resource Pool CPU Limits (in MHz)":
        if status == 'FAIL':
            if actual_value != "Not-Configured":
                return "Cluster["+cluster+"] | Resource Pool["+entity+"] | Limit is "+str(actual_value), True, 'info'
    
    if check_name == "Resource Pool CPU Reservation (in MHz)" or check_name=="Resource Pool Memory Reservation (in MB)":
        if status == 'FAIL':
            if actual_value != "Not-Configured":
                return "Cluster["+cluster+"] | Resource Pool["+entity+"] | Reservation is "+str(actual_value), True, 'info'       
    
    if check_name == "Verify reserved memory and cpu capacity versus Admission control policy set":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, ''
        if 'Reserved-Cpu' in actual_value:
            cpuFailoverResourcesPercent,currentCpuFailoverResourcesPercent,memoryFailoverResourcesPercent,currentMemoryFailoverResourcesPercent=actual_value.split(';')
            cpu=float(cpuFailoverResourcesPercent.split(":")[1])
            current_cpu=float(currentCpuFailoverResourcesPercent.split(":")[1])
            memory=float(memoryFailoverResourcesPercent.split(":")[1])
            current_memory=float(currentMemoryFailoverResourcesPercent.split(":")[1])
            stat='info'
            if current_cpu-cpu > 25 or current_memory-memory > 25:
                stat='info'
            else: stat='warning'
            return "For Cluster["+cluster+"], <br/>"+str(actual_value).replace(';','<br/>'), True, stat
        if actual_value == "ACP is disabled":
                return "For Cluster["+cluster+"], "+actual_value,True, 'alert'
        else:
                return "For Cluster["+cluster+"], "+actual_value,True, 'warning'
            
            
    # Start of CVM Checks
    if check_name == "CVM's Isolation Response":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, ''
        elif actual_value == "none":
            return 'none', False, ''
        else: 
            return  "Isolation response on CVM ["+entity+"] is [Not Leave Powered On]", True, 'alert' 
         
    if check_name == "CVM DRS":
        if actual_value == "False":
            return 'DRS on VM ['+entity+'] is [Disabled]', True, ''
        elif actual_value == "True":
            return 'DRS on VM ['+entity+'] is [Enabled]', True, 'warning'
        elif actual_value == "Not-Configured":
            return 'Not-Configured', False, 'warning'
        else:
            return 'DRS on VM ['+entity+'] is ['+actual_value+']', True, 'warning' 
        
    if check_name=="Validate HBDatastoreCandidatePolicy for Datastores":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, 'warning'
        elif actual_value=="allFeasibleDsWithUserPreference":
            return 'Policy[allFeasibleDsWithUserPreference] set to cluster['+cluster+']', False ,''
        else:
            return 'Policy['+actual_value+'] set to cluster['+cluster+']', True ,'info'
        
    if check_name == "VM Monitoring For CVMs":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, ''
        elif actual_value == "vmMonitoringDisabled":
            return actual_value, False, ''
        else: 
            return 'VM monitoring on CVM ['+entity+'] is not [Disabled]', True, 'alert'
        
    if check_name == "VM Restart Priority For CVMs":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, ''
        elif actual_value == "disabled":
            return 'VM restart Priority on CVM['+entity+'] is [Disabled]', False, ''
        else: 
            return 'VM restart Priority on CVM['+entity+'] is [Not Disabled]', True, 'alert' 
        
    if check_name == "CPU Reservation Per CVM(MHz)":
        if actual_value == "Not-Configured":
            return "Not-Configured", False, ''
        elif actual_value != "10000":
            return "On CVM ["+entity+"] CPU reservation is set to ["+actual_value+"] MHz", True ,"alert"
        else:
            return "On CVM ["+entity+"] CPU reservation is set to ["+actual_value+"] MHz", False ,"alert"
        
    if check_name == "Memory Reservation Per CVM(MB)":
        if actual_value == "Not-Configured":
            return "Not-Configured", False, ''
        elif actual_value is not None:
             if message is not None :
                 messageList = message.split('(Expected: =')
                 expected_result = messageList[1].split(')')[0]             
        if actual_value == expected_result:
            return "CVM ["+entity+"] on Cluster ["+cluster+"] has Memory reservation set to ["+actual_value+"] MB", False ,'alert'
        elif actual_value < expected_result:
            return "CVM ["+entity+"] on Cluster ["+cluster+"] has Memory reservation Not Equal to Memory Size", True ,'alert' 
        elif actual_value == "0":
             return "CVM ["+entity+"] on Cluster ["+cluster+"] has No Memory reservation", True ,'alert'   
        
    if check_name == "CPU Limit per CVM":
        if actual_value == "Not-Configured":
            return "Not-Configured", False, ''
        elif actual_value != "-1":
            return "CVM ["+entity+"] on Cluster ["+cluster+"] has CPU limit set to ["+actual_value+"]", True ,"alert"
        else:
            return "CVM ["+entity+"] on Cluster ["+cluster+"] has CPU limit set to ["+actual_value+"]", False ,"alert"
        
    if check_name == "Memory Limit per CVM":
        if actual_value == "Not-Configured":
            return "Not-Configured", False, ''
        elif actual_value != "-1":
            return "CVM ["+entity+"] on Cluster ["+cluster+"] has Memory limit is set to ["+actual_value+"]", True ,"alert"
        else:
            return "CVM ["+entity+"] on Cluster ["+cluster+"] has Memory limit is set to ["+actual_value+"]", False ,"alert"          
                                        
    # Start of storage_and_vm Checks
    if check_name == "VM hardware version is the most up to date with the ESXI version":
        if status == 'FAIL':
            return "Virtual Machine ["+entity+"] has virtual hardware in version ["+actual_value+"] which is lower then latest supported version",True, 'info'
        else:
            return "Virtual Machine ["+entity+"] has virtual hardware in version ["+actual_value+"] which is lower then latest supported version",False, 'info'
     
    if check_name == "VM using the VMXNET3 virtual network device":
        if status == 'FAIL':
            return "Virtual machine ["+entity+"] has virtual adapter ["+actual_value+"]",True, 'info'
        else : 
            return "Virtual machine ["+entity+"] has virtual adapter ["+actual_value+"]",False, 'info'
        
    if check_name == "VMware Tools Status on VMs":
        if actual_value == "toolsOk":
            return actual_value, False, ''
        else:
            return "VMware tools on virtual machine ["+entity+"] is in ["+actual_value+"] status", True, 'info'     
        
    if check_name == "Storage I/O Control of Datastores":
        if actual_value == "False":
            return actual_value, False, ''
        else:
            return "In Datacenter ["+datacenter+"], Datastore ["+entity+"] has Storage IO [Enabled]", True, 'alert'
                
    if check_name == "Hardware Acceleration of Datastores":
        if actual_value == "vStorageSupported":
            return 'vStorageSupported', False,''
        elif actual_value == "vStorageUnknown":
            return "On host ["+host+"] hardware acceleration on datastore ["+entity+"] is  ["+actual_value+"]", True, 'warning'
        elif actual_value == "vStorageUnsupported":
            return "On host ["+host+"] hardware acceleration on datastore ["+entity+"] is  ["+actual_value+"]", True, 'warning'
        elif actual_value == "Datastore not attached":
            return 'Datastore not attached', False,''
        else: 
            return actual_value, False, ''  
        
    if check_name == "USB Device Connected to VM":
        if status == "FAIL":
            return "Virtual machine ["+entity+"] has connected USB device",True,"info"
        else:
            return "Virtual machine ["+entity+"] has disconnected USB device",False,"info"
        
    if check_name == "RS-232 Serial Port Connected to VM":
        if status == "FAIL":
            return "Virtual machine ["+entity+"] has connected serial port device",True,"info"
        else:
            return "Virtual machine ["+entity+"] has disconnected serial port device",False,"info"
        
    if check_name == "CD-ROM Connected to VM":
        if status == "FAIL":
            return "Virtual machine ["+entity+"] has connected CD-ROM device",True,"info"
        else:
            return "Virtual machine ["+entity+"] has disconnected CD-ROM device",False,"info"
        
    if check_name ==  "VM Ballooned Memory":
        if actual_value == "Not-Configured":
            return actual_value, False, ''
        elif actual_value == "0":
            return actual_value, False, '' 
        else :
            return "On virtual machine ["+entity+"] ballooned memory is ["+actual_value+"] MB", True , 'alert'
     
    if check_name ==  "VM Swapped Memory":
        if actual_value == "Not-Configured":
            return actual_value, False, ''
        elif actual_value == "0":
            return actual_value, False, '' 
        else :
            return "On virtual machine ["+entity+"] swapped memory is ["+actual_value+"] MB", True , 'alert' 
        
    if check_name == "CPU Reservation Per VM(MHz)":
        if actual_value == "Not-Configured":
            return "Not-Configured", False, ''
        elif actual_value != "0":
            return "On VM ["+entity+"] CPU reservation is set to ["+actual_value+"] MHz", True ,"info"
        else:
            return "On VM ["+entity+"] CPU reservation is set to ["+actual_value+"] MHz", False ,"info"
        
    if check_name == "Memory Reservation Per VM(MB)":
        if actual_value == "Not-Configured":
            return "Not-Configured", False, ''
        elif actual_value != "0":
            return "On VM ["+entity+"] memory reservation is set to ["+actual_value+"] MB", True ,'info'
        else:
            return "On VM ["+entity+"] memory reservation is set to ["+actual_value+"] MB", False ,'info'

    if check_name == "VM Advance Setting[isolation.tools.diskWiper.disable]":
        if actual_value == "Not-Configured" and entity != host:
            return "On virtual machine ["+entity+"] advance setting [isolation.tools.diskWiper.disable] is not set", True, 'info'
        elif actual_value != "True" and entity != host:
            return "On virtual machine ["+entity+"] advance setting [isolation.tools.diskWiper.disable] is set to ["+actual_value+"]", True, 'info'
        else:
            return "On virtual machine ["+entity+"] advance setting [isolation.tools.diskWiper.disable] is set to ["+actual_value+"]", False, 'info'

    if check_name == "VM Advance Setting[isolation.tools.diskShrink.disable]":
        if actual_value == "Not-Configured" and entity != host:
            return "On virtual machine ["+entity+"] advance setting [isolation.tools.diskShrink.disable] is not set", True, 'info'
        elif actual_value != "True" and entity != host:
            return "On virtual machine ["+entity+"] advance setting [isolation.tools.diskShrink.disable] is set to ["+actual_value+"]", True, 'info'
        else:
            return "On virtual machine ["+entity+"] advance setting [isolation.tools.diskShrink.disable] is set to ["+actual_value+"]", False, 'info'
        
                
    if check_name == "VM Advance Setting[isolation.tools.copy.disable]":
        if actual_value == "Not-Configured" and entity != host:
            return "On virtual machine ["+entity+"] advance setting [isolation.tools.copy.disable] is not set", True, 'info'
        elif actual_value != "True" and entity != host:
            return "On virtual machine ["+entity+"] advance setting [isolation.tools.copy.disable] is set to ["+actual_value+"]", True, 'info'
        else:
            return "On virtual machine ["+entity+"] advance setting [isolation.tools.copy.disable] is set to ["+actual_value+"]", False, 'info'

    if check_name == "VM Advance Setting[isolation.tools.paste.disable]":
        if actual_value == "Not-Configured" and entity != host:
            return "On virtual machine ["+entity+"] advance setting [isolation.tools.paste.disable] is not set", True, 'info'
        elif actual_value != "True" and entity != host:
            return "On virtual machine ["+entity+"] advance setting [isolation.tools.paste.disable] is set to ["+actual_value+"]", True, 'info'
        else:
            return "On virtual machine ["+entity+"] advance setting [isolation.tools.paste.disable] is set to ["+actual_value+"]", False, 'info'

    if check_name == "VM Advance Setting[log.keepOld]":
        if actual_value == "Not-Configured" and entity != host:
            return "On virtual machine ["+entity+"] advance setting [log.keepOld] is not set", True, 'info'
        elif actual_value != "8" and entity != host:
            return "On virtual machine ["+entity+"] advance setting [log.keepOld] is set to ["+actual_value+"]", True, 'info'
        else:
            return "On virtual machine ["+entity+"] advance setting [log.keepOld] is set to ["+actual_value+"]", False, 'info'

    if check_name == "VM Advance Setting[RemoteDisplay.maxConnections]":
        if actual_value == "Not-Configured" and entity != host:
            return "On virtual machine ["+entity+"] advance setting [RemoteDisplay.maxConnections] is not set", True, 'info'
        elif actual_value != "1" and entity != host:
            return "On virtual machine ["+entity+"] advance setting [RemoteDisplay.maxConnections] is set to ["+actual_value+"]", True, 'info'
        else:
            return "On virtual machine ["+entity+"] advance setting [RemoteDisplay.maxConnections] is set to ["+actual_value+"]", False, 'info'
        
    if check_name ==  "VM Snapshot":
        if actual_value == "Not-Configured":
            return actual_value, False, ''
        elif actual_value is not None:
             if message is not None :
                 messageList = message.split('@')
                 vm_name = messageList[7]             
             actual_date , actual_time = actual_value.split()
             days = abs(diff_dates(actual_date))
             if days > 14:
               return  "Virtual machine ["+vm_name+"] has snapshot which is ["+str(days)+"] days old", True, 'alert'
             elif days > 7 and days < 14:  
               return  "Virtual machine ["+vm_name+"] has snapshot which is ["+str(days)+"] days old", True, 'warning'           
             else:
                 return "Virtual machine ["+vm_name+"] has snapshot which is ["+str(days)+"] days old", True, 'info'   
                           
    if check_name == "CPU Limit per VM":
        if actual_value == "Not-Configured":
            return "Not-Configured", False, ''
        elif actual_value != "-1":
            return "On VM ["+entity+"] CPU limit is set to ["+actual_value+"]", True ,"warning"
        else:
            return "On VM ["+entity+"] CPU limit is set to ["+actual_value+"]", False ,"warning"
        
    if check_name == "Memory Limit per VM":
        if actual_value == "Not-Configured":
            return "Not-Configured", False, ''
        elif actual_value != "-1":
            return "VM ["+entity+"] on Cluster ["+cluster+"] has Memory limit is set to ["+actual_value+"]", True ,"warning"
        else:
            return "VM ["+entity+"] on Cluster ["+cluster+"] has Memory limit is set to ["+actual_value+"]", False ,"warning"        

    if check_name == "VM OS Version same as Guest OS Version":
        if actual_value == "Not-Configured":
            return "Not-Configured", False, ''
        elif status == "FAIL":
            return "VM ["+entity+"] on Cluster ["+cluster+"] has Guest OS ["+actual_value+"] but hardware baseline is set to ["+exp_value_from_msg+"]", True ,"warning"
        else:
            return "VM ["+entity+"] on Cluster ["+cluster+"] has Guest OS ["+actual_value+"] but hardware baseline is set to ["+exp_value_from_msg+"]", False ,"warning"
                
    # Start of vcenter_server Checks 
    if check_name == "Validate vCenter Server has VMware Tools installed and is up to date":
        if actual_value == "toolsOk":
            return actual_value, False, ''
        else:
            return "VMware tools on virtual machine ["+entity+"] is in ["+actual_value+"] status", True, 'warning'
        
    if check_name == "vCenter Server Update Manager Installed":
        if actual_value == "VMware vSphere Update Manager extension":
            return actual_value, False, ''
        elif actual_value == "Not-Configured":
            return "VMware update manager on vCenter Server ["+vCenterServerIP+"] is not installed", True, 'info'
        else:
            return "VMware update manager on vCenter Server ["+vCenterServerIP+"] is not installed", True, 'info'
        
    if check_name == "vCenter Server Statistics Interval":
        if actual_value == "1":
            return actual_value, False, ''
        elif actual_value == "2":
            return "Interval ["+entity+"] is set to ["+actual_value+"]", True, 'warning'
        elif actual_value == "3":
            return "Interval ["+entity+"] is set to ["+actual_value+"]", True, 'alert'  
        elif actual_value == "Not-Configured":
            return 'Not-Configured', False, '' 
 
    if check_name == "vCenter Server SMTP Settings":
        if actual_value == "Not-Configured":
            return "SMTP on vCenter server ["+vCenterServerIP+"] is not configured", True, 'info'
        elif actual_value == None:
            return "SMTP on vCenter server ["+vCenterServerIP+"] seems to be incorrect ["+actual_value+"]", True, 'info'
        elif actual_value == vCenterServerIP:
            return "SMTP on vCenter server ["+vCenterServerIP+"] seems to be incorrect ["+actual_value+"]", True, 'info' 
        else:
            return actual_value, False, ''        
 
    if check_name == "vCenter Server SNMP Receiver Community":
        if actual_value == "Not-Configured":
            return "SNMP Community on vCenter server ["+vCenterServerIP+"] is not configured", True, 'info'
        elif actual_value == None:
            return "SNMP Community on vCenter server ["+vCenterServerIP+"] seems to be incorrect ["+actual_value+"]", True, 'info'
        elif actual_value == vCenterServerIP:
            return "SNMP Community on vCenter server ["+vCenterServerIP+"] seems to be incorrect ["+actual_value+"]", True, 'info' 
        elif actual_value == "localhost":
            return "SNMP Community on vCenter server ["+vCenterServerIP+"] seems to be incorrect ["+actual_value+"]", True, 'info'         
        else:
            return actual_value, False, ''                                               

    if check_name == "vCenter Server SNMP Receiver Name":
        if actual_value == "Not-Configured":
            return "SNMP Name on vCenter server ["+vCenterServerIP+"] is not configured", True, 'info'
        elif actual_value == None:
            return "SNMP Name on vCenter server ["+vCenterServerIP+"] seems to be incorrect ["+actual_value+"]", True, 'info'
        elif actual_value == vCenterServerIP:
            return "SNMP Name on vCenter server ["+vCenterServerIP+"] seems to be incorrect ["+actual_value+"]", True, 'info' 
        elif actual_value == "localhost":
            return "SNMP Name on vCenter server ["+vCenterServerIP+"] seems to be incorrect ["+actual_value+"]", True, 'info'        
        else:
            return actual_value, False, ''  
        
    if check_name == "Validate vCenter Server License Expiration Date":
        if actual_value == "Not-Configured":
            return "vCenter Server ["+vCenterServerIP+"] license expiration date is ["+actual_value+"]", True, 'info'
        else:
             actual_date , actual_time = actual_value.split()
             days = diff_dates(actual_date)
             if days > 180:
               return  "vCenter Server ["+vCenterServerIP+"] license expiration date is ["+actual_date+"]", True, 'info'
             elif days > 60 and days < 180:  
               return  "vCenter Server ["+vCenterServerIP+"] license expiration date is ["+actual_date+"]", True, 'warning'            
             elif days > 0 and days < 60:
               return  "vCenter Server ["+vCenterServerIP+"] license expiration date is ["+actual_date+"]", True, 'alert'
             else:
                 return actual_date, False, '' 

    if check_name == "vCenter Server Role Based Access":
        if actual_value == "Not-Configured":
            return actual_value, False, ''
        elif actual_value == "True":
            return "Role Based Access on vCenter Server ["+vCenterServerIP+"] is Enabled", False, 'info'
        else:
            return "Role Based Access on vCenter Server ["+vCenterServerIP+"] is Disabled", True, 'info' 
        
    if check_name == "vCenter Server Plugins":
        if actual_value == "Not-Configured":
            return actual_value, True, ''
        elif status == "PASS":
            return "VCenter Server Plugins on vCenter Server ["+vCenterServerIP+"] are ["+actual_value+"]", True, 'info'
        else:
            return "VCenter Server Plugins on vCenter Server ["+vCenterServerIP+"] are ["+actual_value+"]", False, 'info'                    
              
    # Start of ESXI Checks      
    if check_name == "Host's HyperThreading Status":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, ''
        elif actual_value == "False":
            return "HyperThreading is not enabled on Host["+host+"]", True, 'warning'
        elif actual_value == "True": 
            return "HyperThreading is enabled on Host["+host+"]", False, ''
        
    if check_name == "Host's Power Management Setting":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, ''
        else: 
            return "Host Power management policy on host ["+host+"] is set to ["+actual_value+"]", True, "info" if actual_value=="Balanced" else "alert"
        
    if check_name == "ESXi Lockdown Mode":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, ''
        elif actual_value == "False":
            return "Lockdown Mode is [Disabled] on Host["+host+"]", False, ''
        elif actual_value == "True": 
            return "Lockdown Mode is [Enabled] on Host["+host+"]", True, 'warning'
        
    if check_name == "[Syslog.global.logHost]":
        if status == "Fail":
            if actual_value == "Not-Configured":
                if host=="":
                    return 'Host not found', False, 'info'
                return '[Syslog.global.logHost] is set to [Not-Configured]', True, 'info'
            elif actual_value=="":
                return '[Syslog.global.logHost] is set to [Blank]', True, 'info'
        else:
            return actual_value, False,''
        
    if check_name == "[Syslog.global.logDirunique]":
        if status == "Fail":
            if actual_value == "Not-Configured":
                if host=="":
                    return 'Host not found', False, 'info'
                return '[Syslog.global.logDirunique] is set to [Not-Configured]', True, 'info'
            elif actual_value=="False":
                return '[Syslog.global.logDirunique] is set to ['+actual_value+']', True,''
        else:
            return actual_value, False,''
        
    if check_name == "Validate the Directory Services Configuration is set to Active Directory":
        if actual_value == "False":
            return "Directory Services is [Not Set] to Active Directory for Host["+host+"]", True,'info'
        elif actual_value == "True":
            return "Directory Services is [Set] to Active Directory for Host["+host+"]", False,''
        
    if check_name == "Validate NTP client is set to Enabled and is in the running state":
        if status == "FAIL":
            if actual_value == "NTP Client not configured":
                if host=="":
                    return "NTP Client not configured", False,'info'
                else:
                    return "NTP Client not configured on Host["+host+"]", True,'alert'
            else:
                is_disable=actual_value.split(':')[1].split(" ")[0]
                #is_running=actual_value.split(':')[2]
                if is_disable == "False":
                    return  "NTP client on Host["+host+"] is [Disabled]", True,'alert'
                else:
                    return  "NTP client on Host["+host+"] is [Enabled but not running]", True,'alert'
        elif status == "PASS":
            return actual_value, False,''
    
    if check_name == "DNS Preferred and Alternate Servers Set for all ESXi Hosts":
        if actual_value == "Not-Configured":
            if host == "":
                return "No host found", False, 'info'
            else:
                return "on Host["+host+"] DNS servers are not configured", True,'warning'         
        else:
            if len(actual_value.split(','))<2:
                return "Host["+host+"] has only one DNS server["+str(actual_value)+"] configured" , True, 'warning'
            else:
                from validation import Validate
                is_dns=False
                for ip in actual_value.split(','):
                    if Validate.valid_ip(ip.strip()) == False:
                        is_dns=True
                        break;
                if is_dns == True:
                    return "Host["+host+"] DNS servers are configured with FQDN names["+str(actual_value)+"]" , True, 'warning'
                else:
                    return "Host["+host+"] DNS servers["+str(actual_value)+"] are configured " , False, ''
                
    if check_name == "NTP Servers Configured":
        if actual_value == "Not-Configured":
            if host == "":
                return "No host found", False, 'info'
            else:
                return "on Host["+host+"] NTP servers are [Not-configured]", True,'warning'
        else:
            if actual_value.split(',')<2:
                return "Host["+host+"] has only one NTP server["+str(actual_value)+"] configured" , True, 'alert'
            else:
                return "Host["+host+"] NTP servers["+str(actual_value)+"] are configured " , False, '' 
    
    if check_name=="Management VMkernel adapter has only Management Traffic enabled":
        if status == 'FAIL':
            if actual_value == "Management-Adapter-Not-Found":
                return "On Host["+host+"], Management-Adapter-Not-Found", True , 'info'
            else:
                return "On Host["+host+"],<br/> for VMKernal Adapter["+entity+"] :<br/>"+ actual_value.replace(';','<br/>'), True , 'info'  
    if check_name=="vMotion VMkernel adapter has only vMotion Traffic enabled":
        if status == 'FAIL':
            if actual_value == "vMotion-Adapter-Not-Found":
                return "On Host["+host+"], vMotion-Adapter-Not-Found", True , 'info'
            else:
                return "On Host["+host+"],<br/> for VMKernal Adapter["+entity+"] :<br/>"+ actual_value.replace(';','<br/>'), True , 'info'
    if check_name=="FTLogging VMkernel adapter has only FTLogging enabled":
        if status == 'FAIL':
            if actual_value == "FTLogging-Adapter-Not-Found":
                return "On Host["+host+"], FTLogging-Adapter-Not-Found", True , 'info'
            else:
                return "On Host["+host+"],<br/> for VMKernal Adapter["+entity+"] :<br/>"+ actual_value.replace(';','<br/>'), True , 'info' 
                 
    # Start of network_and_switch Checks          
    if check_name == "Virtual Standard Switch - Load Balancing":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "loadbalance_ip":
            return "Load Balancing policy on host ["+host+"] on ["+entity+"] is set to ["+actual_value+"]", True,'warning'
        elif actual_value == "loadbalance_srcmac":
            return "Load Balancing policy on host ["+host+"] on ["+entity+"] is set to ["+actual_value+"]", True,'warning'
        elif actual_value == "failover_explicit":
            return "Load Balancing policy on host ["+host+"] on ["+entity+"] is set to ["+actual_value+"]", True,'warning'
        elif actual_value == "loadbalance_loadbased":
            return "Load Balancing policy on host ["+host+"] on ["+entity+"] is set to ["+actual_value+"]", True,'warning'                        
        else:
            return actual_value, False,''
                
    if check_name == "Virtual Standard Switch - Network Failover Detection":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "True":
            return "Network Failover Detection policy on host ["+host+"] on ["+entity+"] is set to ["+actual_value+"]", True,'warning'
        else:
            return actual_value, False,''
        
    if check_name == "Virtual Standard Switch - Notify Switches":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "False":
            return "Notify Switches policy on host ["+host+"] on ["+entity+"] is set to ["+actual_value+"]", True,'warning'
        else:
            return actual_value, False,''
        
    if check_name == "Virtual Standard Switch - Failback":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "False":
            return "Failback policy on host ["+host+"] on ["+entity+"] is set to ["+actual_value+"]", True,'warning'                       
        else:
            return actual_value, False,''
        
    if check_name == "Virtual Networking Security(VSS) - Promiscuous Mode":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "True":
            return "Promiscuous Mode policy on host ["+host+"] on ["+entity+"] is set to ["+actual_value+"]", True,'info'                       
        else:
            return actual_value, False,''

    if check_name == "Virtual Networking Security(VSS) - MAC Address Changes":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "True":
            return "MAC Address Changes policy on host ["+host+"] on ["+entity+"] is set to ["+actual_value+"]", True,'info'                       
        else:
            return actual_value, False,''

    if check_name == "Virtual Networking Security(VSS) - Forged Transmits":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "True":
            return "Forged Transmits policy on host ["+host+"] on ["+entity+"] is set to ["+actual_value+"]", True,'info'                       
        else:
            return actual_value, False,''
        
    if check_name == "Virtual Distributed Switch - Load Balancing":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "loadbalance_ip":
            return "Load Balancing policy on VDS ["+entity+"] is set to ["+actual_value+"]", True,'warning'
        elif actual_value == "loadbalance_srcmac":
            return "Load Balancing policy on VDS ["+entity+"] is set to ["+actual_value+"]", True,'warning'
        elif actual_value == "loadbalance_srcid":
            return "Load Balancing policy on VDS ["+entity+"] is set to ["+actual_value+"]", True,'warning'
        elif actual_value == "failover_explicit":
            return "Load Balancing policy on VDS ["+entity+"] is set to ["+actual_value+"]", True,'warning'
        else:
            return actual_value, False,''
                
    if check_name == "Virtual Distributed Switch - Network Failover Detection":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "True":
            return "Network Failover Detection policy on VDS ["+entity+"] is set to ["+actual_value+"]", True,'warning'
        else:
            return actual_value, False,''
        
    if check_name == "Virtual Distributed Switch - Notify Switches":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "False":
            return "Notify Switches policy on VDS ["+entity+"] is set to ["+actual_value+"]", True,'warning'
        else:
            return actual_value, False,''
        
    if check_name == "Virtual Distributed Switch - Failback":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "False":
            return "Failback policy on VDS ["+entity+"] is set to ["+actual_value+"]", True,'warning'                       
        else:
            return actual_value, False,''
        
    if check_name == "Virtual Networking Security(VDS) - Promiscuous Mode":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "True":
            return "Promiscuous Mode policy on VDS ["+entity+"] is set to ["+actual_value+"]", True,'info'                       
        else:
            return actual_value, False,''

    if check_name == "Virtual Networking Security(VDS) - MAC Address Changes":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "True":
            return "MAC Address Changes policy on VDS ["+entity+"] is set to ["+actual_value+"]", True,'info'                       
        else:
            return actual_value, False,''

    if check_name == "Virtual Networking Security(VDS) - Forged Transmits":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "True":
            return "Forged Transmits policy on VDS ["+entity+"] is set to ["+actual_value+"]", True,'info'                       
        else:
            return actual_value, False,''        
    
    if check_name == "Virtual Distributed Switch - Network IO Control":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "True":
            return "Network IO Control policy on VDS ["+entity+"] is Enabled", True,'warning'                       
        elif actual_value == "False":
            return "Network IO Control policy on VDS ["+entity+"] is Disabled", True,'info' 
    
    if check_name == "Virtual Distributed Switch - MTU":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "1500":
            return "MTU size on vSwitch["+entity+"] has MTU["+actual_value+"]", False,''                       
        else:
            return "MTU size on vSwitch["+entity+"] has MTU["+actual_value+"]", True,'info'
    
    if check_name == "Virtual Standard Switch - MTU":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "1500" or actual_value == "None":
            return "MTU size on vSwitch["+entity+"] on host["+host+"] has MTU["+actual_value+"]", False,''                       
        else:
            return "MTU size on vSwitch["+entity+"] on host["+host+"] has MTU["+actual_value+"]", True,'info'
    
    if check_name == "Check if vSwitchNutanix has no physical adapters":
        if actual_value == "vSwitchNutanix-Not-Found":
            return "On host ["+host+"], vSwitchNutanix not found", True,'alert'
        elif actual_value == "None":
            return "On host ["+host+"], vSwitchNutanix has no physical nic attached", False,''                       
        else:
            return "On host ["+host+"], vSwitchNutanix has physical nics ["+actual_value+"] attached", True,'info'    
    
    if check_name == "vSwitchNutanix Connected to CVM only":
        if status == 'FAIL':
            if actual_value == "vSwitchNutanix-Not-Found":
                return "On Cluster ["+cluster+"], vSwitchNutanix not found", True,'alert'
            else:
                return "Virtual machine ["+actual_value+"] is connected to CVM portgroup["+entity+"]" , True, 'info'
            
    #hardware_and_bios_checks
    if check_name == "VT-D(Virtualization Tech for Direct I/O)":
        if actual_value == "Not-Configured":
            return "On Host["+host+"], VT-D is Not-Configured in BIOS", False, 'info'
        elif actual_value == "False":
            return "On Host["+host+"], VT-D is disabled in BIOS", True, 'alert'
        else:
            return "On Host["+host+"], VT-D is enabled in BIOS", False, 'info'
        
    if check_name == "XD-Execute Disabled":
        if actual_value == "Not-Configured":
            return "Host ["+host+"] has XD Not-Configured in BIOS", False, ''
        elif actual_value == "False":
            return "Host ["+host+"] has XD disabled in BIOS", True, 'warning'
        else:
            return  "Host ["+host+"] has XD enabled in BIOS", False, '' 
        
    if check_name == "Host BIOS Version":
        if actual_value == "Not-Configured":
            return "Host ["+host+"] has BIOS Version Not-Configured", False, ''
        else:
            return  "Host ["+host+"] has BIOS Version["+actual_value+"]", True, 'info'         
        
        
#     if check_name == "Node Models and cluster size":
#         if status == 'FAIL':
#             return "For Cluster["+cluster+"],<br/>"+actual_value.replace(';','<br/>'), True, 'alert'
#         else:
#             return "For Cluster["+cluster+"],<br/>"+actual_value.replace(';','<br/>'), True, 'info'
    #Default return
    return str(actual_value), False,'info'
 
