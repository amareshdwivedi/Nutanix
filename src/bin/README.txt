Nutanix Health Check Application V0.1


Table Of Contents
    01 Overview
    02 Installation Instructions
    03 How to Run HealthCheck
    04 How to run IaaS Provisioning
    05 Known Issues

01 Overview
    Nutanix Healthcheck tool connects to vCenter, Nutanix OS and collects configuration of health parameters. It verifies these parameters against best practice values and comes out with a report indicating health check status.

02. Installation Instructions
    Installation of healthcheck tool is one time activity. It is preferred to have Internet connection on the system on which it is being installed. In case some of the python infrastructure packages are not present on the system,install program automatically downloads and installs these dependencies.

    2.1 Windows (Windows 32bit and 64 bit)
       
       2.1.1 Pre-requisites
             - Python 2.7.8 should be installed on the system.
             - Python Path should be set under system environment variables.
             - Microsoft Visual C++ compiler for Python 2.7 should be installed (Download link - http://aka.ms/vcpython27).

       2.1.2 Installation Steps
             - Unzip the HealthCheck-1.0.0 package.
             - Open windows command prompt and navigate to the extracted folder.
             - Verify python command can be executed by typing 'python --version'. It should display version of python installed.
             - Execute python script - 'install.py' at the command prompt. install.py will check if the system has setup tool 'pip' and 'easy_install' available, if not will install these first.Next it will install all the required python packages having extension .egg
             - Once the installation is complete,additional file 'healthcheck.py' and 'webhealthcheck.py' will be created in same folder as well as in installation directory.
             - Run these files to run the command line version or webversion respectively. 

       2.1.3 Un-installation Instructions(Windows 32-bit and 64-bit)
             - Open command prompt and navigate to Healthcheck install folder - PYTHON_HOME/Lib/site-packages/healthcheck.
             - Execute script - 'uninstall.py',this will uninstall and remove all the files which were installed as part of install process.

    2.2 Linux
       2.1.1 Pre-requisites
             - Python 2.7.8 should be installed on the system.
             - Python Path should be set under system environment variables.
             - To install healthcheck make sure you have SUDO or ROOT permission on install system. 

       2.1.2 Installation Steps
             - Unzip the HealthCheck-1.0.0 package.
             - Open command prompt and navigate to the extracted folder.
             - Verify python command can be executed by typing 'python --version'. It should display version of python installed.
             - Execute python script - 'install.py' at the command prompt. 'install.py' will check if the system has setup tool 'pip' and 'easy_install' available, if not will install these first. It also check weather system has 'gcc','python-devel', 'zlib-devel', 'freetype', 'freetype-devel', 'libjpeg-devel' installed, if not it installs these dependences using system package manager (i.e. yum, apt-get etc).  Next it will install all the required python packages having extension .egg
             - Once the installation is complete,additional file 'healthcheck.py' and 'webhealthcheck.py' will be created in /bin and in the same folder.
             - Run these files to run the commandline version or webversion respectively(use SUDO if you don't have root permission). 

       2.1.3 Un-installation Instructions()
             - Open command prompt and navigate to folder python package folder(for Centos: /usr/lib/python2.7/site-packages/healthcheck)
             - Execute script - 'uninstall.py',this will uninstall and remove all the files which were installed as part of install process.

    2.3 Apple Mac
         <TBD>

03 How to run HealthCheck
   
   3.1 Command line        
       Run script 'healthcheck.py'.
       Output is displayed on the console.
       PDF/CSV reports are generated and stored under 'reports' directory which is created at the location from where 'healthchek.py' is run.

   3.2 Web Application
       Run script 'webhealthcheck.py',this will start a Web server listening on port 8080. Connect to Web UI by using url - http://localhost:8080/ from your browser.
       PDF/CSV reports are generated and stored under 'reports' directory which is created at the location from where 'webhealthchek.py' is run.

04 How to run IaaS Provisioning
   4.1 Configuring the input
       Conf file  : install_dir_path\src\conf\input.json
       The input file has three sections Foundation, Prism and vCenter Configurations.
       The user has to update the values(key-pair) in the file.
      
      For example
          For Foundation:
            The user has to enter the ip-address of the foundation server & the restInputs(several details) in the file.
            "foundation":
              {
                  "server": "Enter value here in these quotes.",
                  "restInput":
                   {
                     "cluster_external_ip":"Enter value here in these quotes.",
                   }   
              }
     
   4.2 Running the provisioning script
       Run script 'iaasProvisioning.py'.
       This will provide all the necessary options to perform provisioning ( all steps or explicitely particular step)
       Options provided includes - foundation, cluster_config, vcenter_server_config and run_all.

05 Known issues
   
   <TBD>

