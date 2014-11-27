import datetime


def diff_dates(licencedate):
    today = datetime.date.today()
    licenceDate = datetime.datetime.strptime(licencedate, "%Y-%m-%d").date()
    return  (licenceDate - today).days
    
def get_vc_check_actual_output_format(check_name,actual_value,entity,datacenter,cluster,host,status,exp_value_from_msg,vCenterServerIP):
    actual_value=actual_value.strip()
    exp_value_from_msg=exp_value_from_msg.strip()
    # Start of Cluster Checks
    if check_name == "CPU Compatibility-EVC":
        if actual_value == "None":
            return 'EVC mode on cluster ['+cluster+'] is disabled', True , 'info'
        else:
            return 'EVC baseline on cluster ['+cluster+'] is set to '+actual_value, True , ''
        
    if check_name == "Host's Connected State":
        if actual_value.lower() == 'connected':
            return "Host ["+ host + "] is connected" , False, ''
        elif actual_value=='Not-Configured':
            return 'No host found', False , 'info'
        else:
            return "Host ["+ host + "] is "+str(actual_value) , True , 'alert'
        
    if check_name == "Cluster DRS":
        if actual_value == "True":
            return 'enabled', True, ''
        elif actual_value == "False":
            return 'disabled', True, 'warning'
        else:
            return str(actual_value), True, 'warning'
        
    if check_name == "Cluster DRS Automation Mode":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, ''
        elif actual_value == "fullyAutomated":
            return 'Fully Automated', True, 'info'
        elif actual_value == "manual":
            return 'Manual', True, 'warning'
        elif actual_value == "partiallyAutomated":
            return 'Partially Automated', True, 'info'
        else: 
            return str(actual_value), False, ''
        
    if check_name == "DRS Automation Mode for CVM":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, ''
        elif actual_value == "fullyAutomated":
            return 'On CVM ['+entity+'] DRS automation level is not disabled ', True, 'warning'
        else: 
            return str(actual_value), False, ''
    
    if check_name == "Cluster Load Balanced":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False , ''
        if actual_value == 'NA':
            return 'current balance and target balance is N/A', True , "warning"
        elif actual_value <= exp_value_from_msg:
            return 'current balance('+str(actual_value)+') <= target balance('+str(exp_value_from_msg)+')', True, "info"
        else: 
            return 'current balance('+str(actual_value)+') <= target balance('+str(exp_value_from_msg)+')' , True, "warning"
    
    if check_name == "Cluster Host Monitoring":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False , ''
        elif actual_value != "enabled":
            return str(actual_value), True, 'warning'
        else: 
            return str(actual_value), False, ''
        
    if check_name == "Cluster Admission Control":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False,''
        elif actual_value == "False":
            return 'disabled', True , 'warning'
        elif actual_value == "True":
            return 'enabled', False,''
        else: 
            return str(actual_value), False,''
        
    if check_name == "Host Isolation Response":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, ''
        elif actual_value == "powerOff":
            return 'powerOff', False, ''
        else: 
            return str(actual_value), True, 'alert'
        
    if check_name == "VM Monitoring For CVMs":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, ''
        elif actual_value == "vmMonitoringDisabled":
            return str(actual_value), False, ''
        else: 
            return 'VM monitoring on CVM ['+entity+'] is not Disabled', True, 'alert'
        
    if check_name == "VM Restart Priority For CVMs":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, ''
        elif actual_value == "disabled":
            return 'VM restart Priority on CVM['+entity+'] is disabled', False, ''
        else: 
            return 'VM restart Priority on CVM['+entity+'] is not disabled', True, 'alert' 
            
    if check_name == "Validate datastore heartbeat":
        if actual_value == "Not-Configured":
            return 'Not-Configured', True, 'info'
        else: 
            return str(entity), True, 'info'
        
    if check_name == "Cluster Advance Settings das.ignoreInsufficientHbDatastore":
        if actual_value == "Not-Configured":
            return 'Not-Configured', True, 'info'
        else: 
            return str(actual_value), True, 'info'
        
    if check_name == "Cluster Power Management Setting":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, ''
        elif actual_value == "True":
            return "Off", False, ''
        else: 
            return "Not off", True, 'warning'
        
    if check_name == "VM Swap Placement":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, ''
        elif actual_value == "vmDirectory":
            return "vmDirectory", False, ''
        else: 
            return str(actual_value), True, 'warning'
        
    if check_name == "Cluster Advance Settings das.useDefaultIsolationAddress":
        if actual_value == "false":
            return "false", False, ''
        else: 
            return str(actual_value), True, 'alert'
        
    if check_name == "Cluster Advance Settings das.isolationaddress1":
        if actual_value == "Not-Configured":
            return 'das.isolationaddress1 advance setting not set', True, 'alert'
        elif status == "FAIL": 
            if actual_value.startswith('Advance'):
                return str(actual_value), True, 'alert'
            else:
                return " das.isolationaddress1 advance setting value is not CVM IP address", True, 'alert'
        elif status == "PASS": 
            return str(actual_value), False,''
        
    if check_name == "Cluster Advance Settings das.isolationaddress2":
        if actual_value == "Not-Configured":
            return 'das.isolationaddress2 advance setting not set', True, 'alert'
        elif status == "FAIL": 
            if actual_value.startswith('Advance'):
                return str(actual_value), True, 'alert'
            else:
                return " das.isolationaddress2 advance setting value is not CVM IP address", True, 'alert'
        elif status == "PASS": 
            return str(actual_value), False,''
        
    if check_name == "Cluster Advance Settings das.isolationaddress3":
        if actual_value == "Not-Configured":
            return 'das.isolationaddress3 advance setting not set', True, 'alert'
        elif status == "FAIL": 
            if actual_value.startswith('Advance'):
                return str(actual_value), True, 'alert'
            else:
                return " das.isolationaddress3 advance setting value is not CVM IP address", True, 'alert'
        elif status == "PASS": 
            return str(actual_value), False,'' 
          
    if check_name == "DataStore Connectivity with Hosts":
        if status == "FAIL":
            if actual_value == "Not-Configured":
                if host=="":
                    return "No host found", False, 'info'
                else:
                    return "No datastore mount to host["+host+"]", True, 'alert'
            elif actual_value == "False": 
                return "Datastore["+entity+"] is not mount to host["+host+"]", True, 'alert'  
        if status == "PASS":
            return "Datastore["+entity+"] is mount to host["+host+"]", False, ''
        
    if check_name =="VSphere Cluster Nodes in Same Version":
        if status == "FAIL":
            if actual_value == "Not-Configured":
                return "No host found", False, 'info'
            else:
                return "VSphere Cluster Nodes in multiple version "+str(actual_value), True, "warning"
        elif status == "FAIL":
            return "VSphere Cluster Nodes in same version "+str(actual_value), False, ''
        
    if check_name == "CVM's Isolation Response":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, ''
        elif actual_value == "none":
            return 'none', False, ''
        else: 
            return  "Isolation response on CVM ["+entity+"] is not set to Leave Powered On", True, 'alert' 
         
    if check_name == "CVM DRS":
        if actual_value == "False":
            return 'Disabled', True, ''
        elif actual_value == "True":
            return 'Enabled', True, 'warning'
        elif actual_value == "Not-Configured":
            return 'Not-Configured', False, 'warning'
        else:
            return str(actual_value), True, 'warning' 
        
    # Start of storage_and_vm Checks 
    if check_name == "VMware Tools Status on VMs":
        if actual_value == "toolsOk":
            return str(actual_value), False, ''
        else:
            return "VMware tools on virtual machine ["+entity+"] is in ["+actual_value+"] status", True, 'info'
        
    if check_name == "Hardware Acceleration of Datastores":
        if actual_value == "vStorageSupported":
            return 'vStorageSupported', False,''
        elif actual_value == "vStorageUnknown":
            return "On host ["+host+"] hardware acceleration on datastore ["+entity+"] is  ["+actual_value+"])", True, 'warning'
        elif actual_value == "vStorageUnsupported":
            return "On host ["+host+"] hardware acceleration on datastore ["+entity+"] is  ["+actual_value+"])", True, 'warning'
        elif actual_value == "Datastore not attached":
            return 'Datastore not attached', False,''
        else: 
            return str(actual_value), False, ''  
        
    # Start of vcenter_server Checks 
    if check_name == "Validate vCenter Server has VMware Tools installed and is up to date":
        if actual_value == "toolsOk":
            return str(actual_value), False, ''
        else:
            return "VMware tools on virtual machine ["+entity+"] is in ["+actual_value+"] status", True, 'warning'
        
    if check_name == "vCenter Server Update Manager Installed":
        if actual_value == "VMware vSphere Update Manager extension":
            return str(actual_value), False, ''
        elif actual_value == "Not-Configured":
            return "VMware update manager on vCenter Server ["+vCenterServerIP+"] is not installed", True, 'info'
        else:
            return "VMware update manager on vCenter Server ["+vCenterServerIP+"] is not installed", True, 'info'
        
    if check_name == "vCenter Server Statistics Interval":
        if actual_value == "1":
            return str(actual_value), False, ''
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
             
              
    # Start of ESXI Checks      
    if check_name == "Host HyperThreading Status":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, ''
        elif actual_value == "False":
            return "HT is not enabled on Host["+host+"]", True, 'warning'
        elif actual_value == "True": 
            return "HT is enabled on Host["+host+"]", False, ''
        
    if check_name == "Hosts Power Management Setting":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, ''
        else: 
            return "Host Power management policy on host ["+host+"] is set to "+str(actual_value), True, "info" if actual_value=="Balanced" else "alert"
        
    if check_name == "ESXi Lockdown Mode":
        if actual_value == "Not-Configured":
            return 'Not-Configured', False, ''
        elif actual_value == "False":
            return "Disabled on Host["+host+"]", False, ''
        elif actual_value == "True": 
            return "Enabled on Host["+host+"]", True, 'warning'
        
    if check_name == "[Syslog.global.logHost]":
        if status == "Fail":
            if actual_value == "Not-Configured":
                if host=="":
                    return 'Host not found', False, 'info'
                return 'Not-Configured', True, 'info'
            elif actual_value=="":
                return 'SyslogServerIP is set to black', True, 'info'
        else:
            return str(actual_value), False,''
        
    if check_name == "[Syslog.global.logDirunique]":
        if status == "Fail":
            if actual_value == "Not-Configured":
                if host=="":
                    return 'Host not found', False, 'info'
                return 'Not-Configured', True, 'info'
            elif actual_value=="False":
                return str(actual_value), True,''
        else:
            return str(actual_value), False,''
        
    if check_name == "Validate the Directory Services Configuration is set to Active Directory":
        if actual_value == "False":
            return "Not set to Active Directory for Host["+host+"]", True,'info'
        elif actual_value == "True":
            return "Set to Active Directory for Host["+host+"]", False,''
        
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
                    return  "NTP client on Host["+host+"] is Disabled", True,'alert'
                else:
                    return  "NTP client on Host["+host+"] is Enabled but it is not running", True,'alert'
        elif status == "PASS":
            return str(actual_value), False,''
    
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
                return "on Host["+host+"] NTP servers are not configured", True,'warning'
        else:
            if actual_value.split(',')<2:
                return "Host["+host+"] has only one NTP server["+str(actual_value)+"] configured" , True, 'alert'
            else:
                return "Host["+host+"] NTP servers["+str(actual_value)+"] are configured " , False, ''      
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
            return str(actual_value), False,''
                
    if check_name == "Virtual Standard Switch - Network Failover Detection":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "True":
            return "Network Failover Detection policy on host ["+host+"] on ["+entity+"] is set to ["+actual_value+"]", True,'warning'
        else:
            return str(actual_value), False,''
        
    if check_name == "Virtual Standard Switch - Notify Switches":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "False":
            return "Notify Switches policy on host ["+host+"] on ["+entity+"] is set to ["+actual_value+"]", True,'warning'
        else:
            return str(actual_value), False,''
        
    if check_name == "Virtual Standard Switch - Failback":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "False":
            return "Failback policy on host ["+host+"] on ["+entity+"] is set to ["+actual_value+"]", True,'warning'                       
        else:
            return str(actual_value), False,''
        
    if check_name == "Virtual Networking Security(VSS) - Promiscuous Mode":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "True":
            return "Promiscuous Mode policy on host ["+host+"] on ["+entity+"] is set to ["+actual_value+"]", True,'info'                       
        else:
            return str(actual_value), False,''

    if check_name == "Virtual Networking Security(VSS) - MAC Address Changes":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "True":
            return "MAC Address Changes policy on host ["+host+"] on ["+entity+"] is set to ["+actual_value+"]", True,'info'                       
        else:
            return str(actual_value), False,''

    if check_name == "Virtual Networking Security(VSS) - Forged Transmits":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "True":
            return "Forged Transmits policy on host ["+host+"] on ["+entity+"] is set to ["+actual_value+"]", True,'info'                       
        else:
            return str(actual_value), False,''
        
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
            return str(actual_value), False,''
                
    if check_name == "Virtual Distributed Switch - Network Failover Detection":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "True":
            return "Network Failover Detection policy on VDS ["+entity+"] is set to ["+actual_value+"]", True,'warning'
        else:
            return str(actual_value), False,''
        
    if check_name == "Virtual Distributed Switch - Notify Switches":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "False":
            return "Notify Switches policy on VDS ["+entity+"] is set to ["+actual_value+"]", True,'warning'
        else:
            return str(actual_value), False,''
        
    if check_name == "Virtual Distributed Switch - Failback":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "False":
            return "Failback policy on VDS ["+entity+"] is set to ["+actual_value+"]", True,'warning'                       
        else:
            return str(actual_value), False,''
        
    if check_name == "Virtual Networking Security(VDS) - Promiscuous Mode":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "True":
            return "Promiscuous Mode policy on VDS ["+entity+"] is set to ["+actual_value+"]", True,'info'                       
        else:
            return str(actual_value), False,''

    if check_name == "Virtual Networking Security(VDS) - MAC Address Changes":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "True":
            return "MAC Address Changes policy on VDS ["+entity+"] is set to ["+actual_value+"]", True,'info'                       
        else:
            return str(actual_value), False,''

    if check_name == "Virtual Networking Security(VDS) - Forged Transmits":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "True":
            return "Forged Transmits policy on VDS ["+entity+"] is set to ["+actual_value+"]", True,'info'                       
        else:
            return str(actual_value), False,''        
    
    if check_name == "Virtual Distributed Switch - Network IO Control":
        if actual_value == "Not-Configured":
            return "Not-Configured", False,''
        elif actual_value == "True":
            return "NOIC is enabled", True,'warning'                       
        elif actual_value == "False":
            return "NOIC is disabled", True,'info' 
    
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
    return str(actual_value), True,'info'