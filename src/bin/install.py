import os
import time
import subprocess
import threading
import sys
import shutil

cmd = 'python get_pip/get_pip.py'
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
out, err = p.communicate()

from distutils.sysconfig import get_python_lib;
default_install = get_python_lib()

if not os.path.exists(default_install):
    print "Installation directory does not exists"
    exit()
else :
    shutil.rmtree(default_install + os.path.sep + "healthcheck", ignore_errors=True)
    default_install+=os.path.sep+'healthcheck'
    os.makedirs(default_install)    

print "Starting HealthCheck Installation..."
def progress_bar():
    for i in range(21):
        sys.stdout.write('\r')
        sys.stdout.write("[%-20s] %d%%" % ('#'*i, 5*i))
        sys.stdout.flush()
        time.sleep(0.40)
    sys.stdout.write('\r')
        
def installing_dependencies():
    with open("install_log.txt", "w+") as output:
        subprocess.call(["python", "./install_helper.py",default_install],stderr=output,stdout=output);

threads = []
thread_installing_dep = threading.Thread(target=installing_dependencies)
thread_progress_bar = threading.Thread(target=progress_bar)
thread_progress_bar.start()
thread_installing_dep.start()
threads.append(thread_progress_bar)
threads.append(thread_installing_dep)
for t in threads:
    t.join()
    
print "Creating healthcheck script..."

healthchecklines=['import os,sys',
'lib_path = ' + "'" + default_install + "'",
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
'lib_path = ' + "'" + default_install + "'",
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
'install_dir = ' + "'" + default_install + "'",                               
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
    
