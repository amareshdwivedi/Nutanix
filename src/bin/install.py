import subprocess
import os
import sys
 
cmd = 'python get_pip/get_pip.py'
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
out, err = p.communicate()

from distutils.sysconfig import get_python_lib;
default_install = get_python_lib()
install_dir = raw_input("Please Specify Installation dir (default: "+default_install+"):") or default_install

from setuptools.command import easy_install
libs=['colorama-0.3.2.tar.gz','pycrypto-2.6.1.tar.gz','ecdsa-0.11.tar.gz','paramiko-1.15.1.tar.gz','prettytable-0.7.2.tar.gz','requests-2.4.3.tar.gz','six-1.8.0.tar.gz','pyvmomi-5.5.0.2014.1.1.tar.gz','Pillow-2.6.1.tar.gz','reportlab-3.1.8.tar.gz','HealthCheck-1.0.0-py2.7.egg']
lib_path=os.path.dirname(__file__)+os.path.sep +"eggs"+os.path.sep
print lib_path,"\n",libs
install_dir_lib=install_dir+os.path.sep+'libs'

os.environ["PYTHONPATH"] = install_dir_lib
if not os.path.exists(install_dir_lib):
    os.makedirs(install_dir_lib)

for lib in libs:
    if "Pillow" in lib:
        if sys.platform == "win32" or sys.platform == "win64":
            import struct
            if (8 * struct.calcsize("P"))==32: # for 32bit python compiler 
                easy_install.main(["-Q","-Z","--install-dir",install_dir_lib,lib_path+'Pillow-2.6.1-py2.7-win32.egg'])
            elif (8 * struct.calcsize("P"))==64: # for 64bit python compiler
                easy_install.main(["-Q","-Z","--install-dir",install_dir_lib,lib_path+'Pillow-2.6.1-py3.2-win-amd64.egg'])
        else:
            easy_install.main(["-Q","-Z","--install-dir",install_dir_lib,lib_path+lib])
    else : 
        easy_install.main(["-Q","-Z","--install-dir",install_dir_lib,lib_path+lib])

lines=['import os,sys','executable_path=os.path.dirname(__file__)+os.path.sep+"libs"+os.path.sep+"HealthCheck-1.0.0-py2.7.egg"+os.path.sep+"src"+os.path.sep+"health_check.pyc "'
,'os.system(executable_path+ " ".join(sys.argv[1:]))']
run_health_check_pyfile=open(install_dir+os.path.sep+"run_health_check.py","wb")
for line in lines:
    run_health_check_pyfile.writelines(line+"\n")
run_health_check_pyfile.close()