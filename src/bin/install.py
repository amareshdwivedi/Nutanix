import os
import time
import subprocess

cmd = 'python get_pip/get_pip.py'
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
out, err = p.communicate()

from distutils.sysconfig import get_python_lib;
default_install = get_python_lib()
install_dir = raw_input("Please Specify Installation dir (default: "+default_install+") :") or default_install

if not os.path.exists(install_dir):
    print "Installation directory does not exists"
    exit()
else :
    install_dir+=os.path.sep+'healthcheck'
    os.makedirs(install_dir)    

print "Starting HealthCheck Installation..."

with open("install_log.txt", "w+") as output:
    subprocess.call(["python", "./install_helper.py",install_dir],stdout=output);

print "Creating healthcheck script..."

healthchecklines=['import os,sys',
'lib_path = ' + "'" + install_dir + "'" + '+os.path.sep+\'libs\'',
'os.environ["PYTHONPATH"] = lib_path',
'executable_path="python "+lib_path+os.path.sep+"HealthCheck-1.0.0-py2.7.egg"+os.path.sep+"src"+os.path.sep+"health_check.pyc "',
'os.system(executable_path+ " ".join(sys.argv[1:]))']

health_check_pyfile=open("healthcheck.py","wb")
for line in healthchecklines:
    health_check_pyfile.writelines(line+"\n")
health_check_pyfile.close()
time.sleep(2)

print "Creating webhealthcheck script..."

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
time.sleep(2)

print "Creating uninstall script..."

uninstall_lines=['import os,sys,shutil,time',
'print "Starting HealthCheck Un-installation..."',                 
'install_dir = ' + "'" + install_dir + "'",                               
'shutil.rmtree(install_dir, ignore_errors=True)',
'os.remove(\'healthcheck.py\')',
'os.remove(\'webhealthcheck.py\')',
'os.remove(\'install_log.txt\')',
'time.sleep(2)',
'print "\\nHealthCheck Un-installation Successfull..."']

uninstall_pyfile=open("uninstall.py","wb")
for line in uninstall_lines:
    uninstall_pyfile.writelines(line+"\n")
uninstall_pyfile.close()
time.sleep(2)
   
print "HealthCheck Installation Successfull..."
    
