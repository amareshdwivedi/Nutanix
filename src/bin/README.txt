Nutanix GSO Toolkit V0.1


Table of Contents
    01 Overview
    02 Installation Instructions
    03 How to Run IaaS Provisioning
    04 How to Run HealthCheck
    05 Known Issues
    06 Prerequisites

01 Overview

    Nutanix GSO tool kit consists of deployment scripts and Healthcheck tool. Deployment scripts help in configuration of new server using Foundation,
    Prism configuration and Vcenter configuration. Healthcheck tool connects to vCenter, Nutanix OS and collects configuration of health parameters.
    It verifies these parameters against best practice values and comes out with a report indicating health check status.


02. Installation Instructions

    Installation of GSO tool kit is one time activity. It is preferred to have Internet connection on the system on which it is being installed. In case some of the python infrastructure packages are not present on the system, install program automatically downloads and installs these dependencies.

    2.1 Windows (Windows 32-bit and 64-bit)
       
       2.1.1 Pre-requisites
             - Python 2.7.8 should be installed on the system. (Python 3.0 is not tested)
             - Python Path should be set under system environment variables
             - Verify python command can be executed by typing 'python --version'. It should display version of python installed.

       2.1.2 Installation Steps
             - Extract the content of Zip file
             - Open windows command prompt and navigate to the extracted folder.
             - Execute python script, 'install.py' at the command prompt. 
                   Install.py will check if the system has setup tool 'pip' and 'easy_install', if not will install these first.
                   Next it will install all the required python packages having extension .egg
                   Once the installation is complete, additional files, 'iaasProvisioning.py', 'healthcheck.py' and 'webhealthcheck.py' will be created in same folder and in installation directory.
             - Run these files to run the command line version or webversion of the application.
             - This release include only command line version of deployer toolkit, 'iaasProvisioning.py'.

       2.1.3 Un-installation Instructions(Windows 32-bit and 64-bit)
             - Open command prompt and navigate to install folder - PYTHON_HOME\Lib\site-packages\service_toolkit.
             - Execute script - 'uninstall.py',this will uninstall and remove all the files which were installed as part of install process.

    2.2 Linux

       2.1.1 Pre-requisites
             - Python 2.7.8 should be installed on the system.
             - Python Path should be set under system environment variables.
             - To install service_toolkit make sure you have SUDO or ROOT permission on install system. 

       2.1.2 Installation Steps
             - Extract the content of Zip file
             - Open command prompt and navigate to the extracted folder.
             - Verify python command can be executed by typing 'python --version'. It should display version of python installed.
             - Execute python script, 'install.py' at the command prompt. 
                   Install.py will check if the system has setup tool 'pip' and 'easy_install', if not will install these first.
                   Next it will install all the required python packages having extension .egg
                   Once the installation is complete, additional files, 'iaasProvisioning.py', 'healthcheck.py' and 'webhealthcheck.py' will be created in same folder and in installation directory.
             - Run these files to run the commandline version or webversion of the application (use SUDO if you don't have root permission).
             - This release include only command line version of deployer toolkit, 'iaasProvisioning.py'.

       2.1.3 Un-installation Instructions()
             - Open command prompt and navigate to folder python package folder(for Centos: /usr/lib/python2.7/site-packages/service_toolkit)
             - Execute script - 'uninstall.py',this will uninstall and remove all the files which were installed as part of install process.

    2.3 Apple Mac
         <TBD>

03 How to Run IaaS Provisioning (Deployer Toolkit)

   3.1 Configuring input parameters

       This script accepts input in the form of JSON file. JSON file has key value pairs. Input file is located at, <install_dir_path>service_toolkit-1.0.0-py2.7.egg\src\conf\input.json.
       On windows, this file is located at, PYTHON_HOME\Lib\site-packages\service_toolkit\service_toolkit-1.0.0-py2.7.egg\src\conf

       The input file has three sections Foundation, Prism and vCenter Configurations. Update the file by entering values for respective keys.

       Below example demonstrates how to modify foundation server IP address.

         Open input.json using any text editor
         Goto line which has "foundation":
            For example
          For Foundation:
           
            "foundation":
              {
                  "server": "Enter the server ip",
                  "restInput":
                   {
                     "cluster_external_ip":"Enter the cluster_external_ip",
                   }   
              }

        Goto line "server", replace text "Enter the server ip" with IP address of foundation server.
       
        For Prism:

             "prismDetails":
              {
                  "restURL" :"Enter restURL",
                  "authentication":
                  {
                      "username" :"Enter username",
                      "password" :"Enter password" 
                  }
                  "container":
                  {
                      "name": "Enter the name of the container to be created here"
                  } 
              }

        Goto line "restURL", replace text "Enter restURL" with actual restURL for the foundation server,
        Goto line "username", replace text "Enter username" with valid rest server username, etc.


        For vCenter config:

             "vCenterConf":
              {
                  "host":"Enter host ip here",
                  "user":"Enter username here",
                  "password":"Enter password here",
                  "datacenter":"Enter DataCenter Name",
                  "cluster":"Enter Cluster Name"
              }                
        
        Goto line "datacenter", replace text "Enter DataCenter Name" with a string that will be used as Datacenter name,
        Goto line "cluster", replace text "Enter Cluster Name" with a string that will be used as Cluster name, etc.

   3.2 Running provisioning script

       Run script 'iaasProvisioning.py'.
       This prints all options for provisioning tasks. Available options are, foundation, cluster_config, vcenter_server_config and run_all.

            foundation:  Performs only foundation portion of deployment
            cluster_config:  Performs Prism configuration
            vcenter_server_config:  Performs vcenter server configuration

            run_all:  Performs all tasks in the order of foundation, cluster_config, vcenter_server_config.


04 How to run HealthCheck
   
   4.1 Command line        
       Run script 'healthcheck.py'.
       Output is displayed on the console.
       PDF/CSV reports are generated and stored under 'reports' directory which is created at the location from where 'healthchek.py' is run.

   4.2 Web Application
       Run script 'webhealthcheck.py',this will start a Web server listening on port 8080. Connect to Web UI by using url - http://localhost:8080/ from your browser.
       PDF/CSV reports are generated and stored under 'reports' directory which is created at the location from where 'webhealthchek.py' is run.


05 Known issues
   
   5.1 Deployer Scripts:
   			This is alpha release of deployer toolkit. The input parameter validations are not done in this release. Please review input values before executing the script.
   5.2 Health Check Scripts:
   			VMware Horizon View Health Check working only on WINDOWS based machine. If installed on NON-WINDOWS machine, operating system not supported message will shown.

06 Prerequisites
	6.1 For VMware Horizon View Health Check - 
		6.1.1 On Connection Broker Server , open command prompt(having Administrator privileges) do following configuration for WINRM:
			1	Run the following command to set the default WinRM configuration values.
					c:\> winrm quickconfig
		
			2	(Optional) Run the following command to check whether a listener is running, and verify the default ports.
					c:\> winrm e winrm/config/listener
					The default ports are 5985 for HTTP, and 5986 for HTTPS.
		
			3	Enable basic authentication on the WinRM service.
						a.	Run the following command to check whether basic authentication is allowed.
							c:\> winrm get winrm/config
						b.	Run the following command to enable basic authentication.
							c:\> winrm set winrm/config/service/auth @{Basic="true"}
						
			4	Run the following command to allow transfer of unencrypted data on the WinRM service.
					c:\> winrm set winrm/config/service @{AllowUnencrypted="true"}
				
			5 	Enable and configure Windows PowerShell Remoting using Group Policy: 
					Online help : http://blog.powershell.no/2010/03/04/enable-and-configure-windows-powershell-remoting-using-group-policy/
					- Open group-policy (Start > Run > Edit Group Policy) and do following steps
					a. Enabling WinRM
							i.	Browse to:
								Policies > Computer Configuration> Administrative Templates > Windows Components > Windows Remote Management (WinRM) > WinRM Service
									- Open the “Allow Remote Server management through WinRM” policy setting (Server 2008 R2 and later).
									- Open the “Allow automatic configuration of listeners” policy setting (Server 2008 and earlier).
							ii.	Set the Policy to Enabled.
							iii.Set the IPv4 and IPv6 filters to * unless you need something specific there (check out the help on the right).
					b.	Setting the Firewall Rules:
							i.	Browse to:
								Policies > Computer Configuration > Administrative Templates > Network > Network Connections > Windows Firewall > Domain Profile
							ii.	Open the “Windows Firewall: Define inbound port exceptions” policy setting.
							iii.Set it to Enabled if it isn’t already.
							iv.	Click the “Show…” button and add the port exception. We’re going to be opening TCP port 5985, so the exception string will look something like this:
								5985:TCP:*:enabled:WSMan
					c. Service Configuration
						At this point we have enough in place to get this working, but I like to do a few more things to ensure that the WinRM service is configured to start automatically and to restart on failure.
			
							i.	Browse to:
								Policies > Computer Configuration>  Windows Settings > Security Settings > System Services
							ii.	Find the “Windows Remote Management (WS-Management)” service.
							iii.Define the policy and give it a startup mode of Automatic.
							iv.	Browse to:
								Preferences > Control Panel Settings > Services
								Create a new Service preference item with the following parameters:
								-	General Tab
									# 	Startup: No Change (the policy we set above will take precedence over this anyway)
									#	Service name: WinRM
									#	Service action (optional): Start service
								-	Recovery Tab
										First, Second, and Subsequent Failures: Restart the Service
		
		6.1.2 On Client( healthcheck installable ) machine, open command prompt(having Administrator privileges) do following configuration for WINRM::
	
			1.	Run the following command to set the default WinRM configuration values.
				c:\> winrm quickconfig
		
			2.	(Optional) Run the following command to check whether a listener is running, and verify the default ports.
				c:\> winrm e winrm/config/listener
				The default ports are 5985 for HTTP, and 5986 for HTTPS.
		
			3.	Enable basic authentication on the WinRM service.
					a.	Run the following command to check whether basic authentication is allowed.
						c:\> winrm get winrm/config
					b.	Run the following command to enable basic authentication.
						c:\> winrm set winrm/config/client/auth @{Basic="true"}
		
			4.	Run the following command to allow transfer of unencrypted data on the WinRM service.
				c:\> winrm set winrm/config/client @{AllowUnencrypted="true"}
		
		6.1.3 For Configuring healthcheck for VMware Horizon View Health Check
			Check weather Connection Broker user has domain account and having access to VMware PowerCLI access as well as machine access. 
