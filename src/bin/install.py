import subprocess
import os
import sys
 
cmd = 'python get_pip/get_pip.py'
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
out, err = p.communicate()

from distutils.sysconfig import get_python_lib;
default_install = get_python_lib()
install_dir = raw_input("Please Specify Installation dir (default: "+default_install+"):") or default_install


if not os.path.exists(install_dir):
    print "Installation directory does not exists"
    exit()
else :
    install_dir+=os.path.sep+'healthcheck'
    os.makedirs(install_dir)
    
print("\n")
print "Starting HealthCheck Installation..."
print("\n")
    
from setuptools.command import easy_install
libs=['colorama-0.3.2.tar.gz','pycrypto-2.6.1.tar.gz','ecdsa-0.11.tar.gz','paramiko-1.15.1.tar.gz','prettytable-0.7.2.tar.gz','requests-2.4.3.tar.gz','six-1.8.0.tar.gz','pyvmomi-5.5.0.2014.1.1.tar.gz','Pillow-2.6.1.tar.gz','reportlab-3.1.8.tar.gz','HealthCheck-1.0.0-py2.7.egg']
lib_path=os.path.abspath(os.path.dirname(__file__))+os.path.sep +"eggs"+os.path.sep
install_dir_lib=install_dir+os.path.sep+'libs'

if not os.path.exists(install_dir_lib):
     os.makedirs(install_dir_lib)
os.environ["PYTHONPATH"] = install_dir_lib
for lib in libs:
#    easy_install.main(["-q","-Z",lib_path+lib])
     if "Pillow" in lib:
         if sys.platform == "win32" or sys.platform == "win64":
            import struct
            if (8 * struct.calcsize("P"))==32: # for 32bit python compiler 
                easy_install.main(["-q","-Z","--install-dir",install_dir_lib,lib_path+'Pillow-2.6.1-py2.7-win32.egg'])
            elif (8 * struct.calcsize("P"))==64: # for 64bit python compiler
                easy_install.main(["-q","-Z","--install-dir",install_dir_lib,lib_path+'Pillow-2.6.1-py2.7-win-amd64.egg'])
            else:
                easy_install.main(["-q","-Z","--install-dir",install_dir_lib,lib_path+lib])
     else :
         easy_install.main(["-q","-Z","--install-dir",install_dir_lib,lib_path+lib])

lines=['import os,sys',
#'lib_path = os.path.abspath(os.path.dirname(__file__))+os.path.sep+"libs"',
'lib_path = ' + "'" + install_dir + "'" + '+os.path.sep+\'libs\'',
'os.environ["PYTHONPATH"] = lib_path',
'executable_path="python "+lib_path+os.path.sep+"HealthCheck-1.0.0-py2.7.egg"+os.path.sep+"src"+os.path.sep+"__main__.pyc "',
'os.system(executable_path+ " ".join(sys.argv[1:]))']

#run_health_check_pyfile=open(install_dir+os.path.sep+"health_check.py","wb")
health_check_pyfile=open("healthcheck.py","wb")
for line in lines:
    health_check_pyfile.writelines(line+"\n")
health_check_pyfile.close()

uninstall_lines=['import os,sys,shutil',
'install_dir = ' + "'" + install_dir + "'",                               
'shutil.rmtree(install_dir, ignore_errors=True)',
'os.remove(\'healthcheck.py\')',
'print "\\nHealthCheck Un-installation Successfull..."']

uninstall_pyfile=open("uninstall.py","wb")
for line in uninstall_lines:
    uninstall_pyfile.writelines(line+"\n")
uninstall_pyfile.close()
print "HealthCheck Installation Successfull..."
