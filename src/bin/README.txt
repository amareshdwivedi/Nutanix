Installation Pre-requisites(Windows 32bit and 64 bit) :-
---------------------------------------------------------
1.)Python 2.7.8 should be installed on the system.
2.)Python Path should be set under system environment variables.
3.)Microsoft Visual C++ compiler for Python 27 should be installed(Download from link - http://www.microsoft.com/en-us/download/details.aspx?id=44266).

Installation Instructions For HealthCheck-1.0.0.zip Package(Windows 32bit and 64 bit) :-
-----------------------------------------------------------------------------------------
1.)Unzip the HealthCheck-1.0.0 package to your Python home directory(c:\Python27 or c:\Program Files\Python27).
2.)Open windows command prompt and navigate to the extracted folder.
3.)Execute command - 'install.bat' at the command prompt.
   3.1.)Install.bat will check if the system has 'pip' and 'easy_install' available and if not will install these first.
   3.2)Next it will install all the required .egg files.
4.)Once the installation is complete,user is switched to the directory where HealthCheck is installed 
   (c:\Python27\HealthCheck-1.0.0-py2.7.egg\src\bin or c:\Program Files\Python27\HealthCheck-1.0.0-py2.7.egg\src\bin).
5.)Application can be started by running healthcheck.bat file.     

Un-installation Instructions(Windows 32bit and 64 bit) :-
----------------------------------------------------------
1.)Open command prompt and navigate to folder which unzipped in step 1 during installation process(HealthCheck-1.0.0).
2.)Execute commaned - 'uninstall.bat',this will uninstall and remove all the .egg files which were installed as part of install process.
3.)Delete the 'HealthCheck-1.0.0' directory.