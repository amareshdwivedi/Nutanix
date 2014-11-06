Nutanix Health Check Application v0.1


Table Of Contents

    01 Overview
    02 Installation Instructions
    03 How to Run Health check
    04 Known Issues

01 Overview
    Nutanix healthcheck tool connects to vCenter, Nutanix OS and collects configuration of
    health parameters. It verifies these parameters against best practice values and comes
    out with a report indicating health check status in the form of pass/fail results.

02. Installation Instructions
  
    Installation of healthcheck tool is one time activity. It is preferred to have Internet
    connection to the system on which it is being installed. In case some of the python 
    infrastructure packages are not present on the system install program automatically downloads 
    and installs these dependencies.

    2.1 Windows (Windows 32bit and 64 bit)
       
       2.1.1 Pre-requisites

             - Python 2.7.8 should be installed on the system.
             - Python Path should be set under system environment variables.
             - Microsoft Visual C++ compiler for Python 27 should be installed
               (Download from link - http://www.microsoft.com/en-us/download/details.aspx?id=44266).

       2.1.2 Installation Steps

             - Unzip the HealthCheck-1.0.0 package.
             - Open windows command prompt and navigate to the extracted folder.
             - Verify python command can be executed by typing 'python --version'. It should display 
               version of python installed.
             - Execute python script - 'install.py' at the command prompt.
                install.py will check if the system has setup tool 'pip' and 'easy_install' available,
                if not will install these first.
                Next it will install all the required python packages having extension .egg
             - Once the installation is complete,additional file 'healthcheck.py' and 'webhealthcheck.py' will be created in same folder.
             - Run these files to run the command line version or webversion respectively. 

       2.1.3 Un-installation Instructions(Windows 32-bit and 64-bit)

             - Open command prompt and navigate to folder unzipped during step 1 during installation process 
              (HealthCheck-1.0.0).
             - Execute script - 'uninstall.py',this will uninstall and remove all the .egg files which were
              installed as part of install process.

    2.2 Linux
         <TBD>

    2.3 Apple Mac
         <TBD>

03 How to run healthcheck
   
   3.1 Command line        
       Run script 'healthcheck.py'.
       Output is displayed on the screen.
       PDF/CSV reports are generated and stored under reports directory,the complete path will be displayed once the run is complete.


    3.2 Web Application
        Run script 'webhealthcheck.py',this will start a Web server listening on port 8080
        Connect to Web UI by using url http://localhost:8080/ from your browser.


04 Known issues
   
   <TBD>
