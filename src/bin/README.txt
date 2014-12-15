Nutanix GSO Toolkit V0.1


Table of Contents
    01 Overview
    02 Installation Instructions
    03 How to run deployer scripts
    04 How to Run HealthCheck
    05 Known Issues

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
             - Microsoft Visual C++ compiler for Python 2.7 should be installed (Download link - http://aka.ms/vcpython27)

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
             - Open command prompt and navigate to Healthcheck install folder - PYTHON_HOME/Lib/site-packages/healthcheck.
             - Execute script - 'uninstall.py',this will uninstall and remove all the files which were installed as part of install process.

    2.2 Linux

       2.1.1 Pre-requisites
             - Python 2.7.8 should be installed on the system.
             - Python Path should be set under system environment variables.
             - To install healthcheck make sure you have SUDO or ROOT permission on install system. 

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
             - Open command prompt and navigate to folder python package folder(for Centos: /usr/lib/python2.7/site-packages/healthcheck)
             - Execute script - 'uninstall.py',this will uninstall and remove all the files which were installed as part of install process.

    2.3 Apple Mac
         <TBD>

03 How to run IaaS Provisioning (Deployer tool kit)

   3.1 Configuring input parameters

       This script accepts input in the form of JSON file. JSON file has key value pairs. Input file is located at, <install_dir_path>\src\conf\input.json.
       On windows, this file is located at, PYTHON_HOME\Lib\site-packages\healthcheck\src\conf\input.json

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
   
   Deployer Scripts:

   This is alpha release of deplopyer toolkit. The input parameter validations are not done in this release. Please review input values before executing the script.


