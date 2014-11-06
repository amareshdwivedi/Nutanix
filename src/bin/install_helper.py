import subprocess
import os
import sys
    
from setuptools.command import easy_install
install_dir=sys.argv[1]
libs=['web.py-0.37.tar.gz','colorama-0.3.2.tar.gz','pycrypto-2.6.1.tar.gz','ecdsa-0.11.tar.gz','paramiko-1.15.1.tar.gz','prettytable-0.7.2.tar.gz','requests-2.4.3.tar.gz','six-1.8.0.tar.gz','pyvmomi-5.5.0.2014.1.1.tar.gz','Pillow-2.6.1.tar.gz','reportlab-3.1.8.tar.gz','HealthCheck-1.0.0-py2.7.egg']
lib_path=os.path.abspath(os.path.dirname(__file__))+os.path.sep +"eggs"+os.path.sep
install_dir_lib=install_dir+os.path.sep+'libs'

if not os.path.exists(install_dir_lib):
     os.makedirs(install_dir_lib)
os.environ["PYTHONPATH"] = install_dir_lib
for lib in libs:
     if "Pillow" in lib:
         if sys.platform == "win32" or sys.platform == "win64":
            import struct
            if (8 * struct.calcsize("P"))==32: # for 32bit python compiler 
                easy_install.main(["-Z","--install-dir",install_dir_lib,lib_path+'Pillow-2.6.1-py2.7-win32.egg'])
            elif (8 * struct.calcsize("P"))==64: # for 64bit python compiler
                easy_install.main(["-Z","--install-dir",install_dir_lib,lib_path+'Pillow-2.6.1-py2.7-win-amd64.egg'])
            else:
                easy_install.main(["-Z","--install-dir",install_dir_lib,lib_path+lib])
     else :
         easy_install.main(["-Z","--install-dir",install_dir_lib,lib_path+lib])

healthchecklines=['import os,sys',
#'lib_path = os.path.abspath(os.path.dirname(__file__))+os.path.sep+"libs"',
'lib_path = ' + "'" + install_dir + "'" + '+os.path.sep+\'libs\'',
'os.environ["PYTHONPATH"] = lib_path',
'executable_path="python "+lib_path+os.path.sep+"HealthCheck-1.0.0-py2.7.egg"+os.path.sep+"src"+os.path.sep+"health_check.pyc "',
'os.system(executable_path+ " ".join(sys.argv[1:]))']

#run_health_check_pyfile=open(install_dir+os.path.sep+"health_check.py","wb")
health_check_pyfile=open("healthcheck.py","wb")
for line in healthchecklines:
    health_check_pyfile.writelines(line+"\n")
health_check_pyfile.close()


webhealthchecklines=['import os,sys',
'lib_path = ' + "'" + install_dir + "'" + '+os.path.sep+\'libs\'',
'os.environ["PYTHONPATH"] = lib_path',
'os.chdir(lib_path+os.path.sep+"HealthCheck-1.0.0-py2.7.egg"+os.path.sep+"src"+os.path.sep)',
'executable_path="python web_health_check.pyc"',
'os.system(executable_path+ " ".join(sys.argv[1:]))']


web_health_check_pyfile=open("webhealthcheck.py","wb")
for line in webhealthchecklines:
    web_health_check_pyfile.writelines(line+"\n")
web_health_check_pyfile.close()


uninstall_lines=['import os,sys,shutil',
'install_dir = ' + "'" + install_dir + "'",                               
'shutil.rmtree(install_dir, ignore_errors=True)',
'os.remove(\'healthcheck.py\')',
'os.remove(\'webhealthcheck.py\')',
'os.remove(\'install_log.txt\')',
'print "\\nHealthCheck Un-installation Successfull..."']

uninstall_pyfile=open("uninstall.py","wb")
for line in uninstall_lines:
    uninstall_pyfile.writelines(line+"\n")
uninstall_pyfile.close()

