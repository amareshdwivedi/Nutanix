import os
import sys
import subprocess
from subprocess import call

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
	
with open("install_log.txt", "w+") as output:
    subprocess.call(["python", "./install_helper.py",install_dir],stdout=output);

print("\n")    
print "HealthCheck Installation Successfull..."
    
