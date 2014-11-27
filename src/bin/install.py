import os
import time
import subprocess
import threading
import sys
import shutil

cmd = 'python '+os.path.abspath(os.path.dirname(__file__))+os.path.sep +'scripts'+ os.path.sep +'get_pip.py'
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
    with open("install_log.log", "w+") as output:
        install_helper=os.path.abspath(os.path.dirname(__file__))+os.path.sep +'scripts'+ os.path.sep +"install_helper.py"
        subprocess.call(["python", install_helper,default_install],stderr=output,stdout=output);

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

healthchecklines=["#!"+sys.executable+"\n" if sys.platform.startswith("linux") else '','import os,sys',
'lib_path = ' + "'" + default_install + "'",
'os.environ["PYTHONPATH"] = lib_path',
'if not os.path.exists(os.getcwd() + os.path.sep +"reports"):',
'     os.mkdir("reports")',
'executable_path="python "+lib_path+os.path.sep+"HealthCheck-1.0.0-py2.7.egg"+os.path.sep+"src"+os.path.sep+"health_check.pyc "',
'os.system(executable_path+ " ".join(sys.argv[1:]))']

health_check_pyfile=open(default_install+os.path.sep+"healthcheck.py","wb")
for line in healthchecklines:
    health_check_pyfile.writelines(line+"\n")
health_check_pyfile.close()
time.sleep(2)

print "Creating webhealthcheck script..."

webhealthchecklines=["#!"+sys.executable+"\n" if sys.platform.startswith("linux") else '','import os,sys',
'lib_path = ' + "'" + default_install + "'",
'os.environ["PYTHONPATH"] = lib_path',
'cur_dir = os.getcwd()',
'if not os.path.exists(cur_dir + os.path.sep +"reports"):',
'     os.mkdir("reports")',
'os.chdir(lib_path+os.path.sep+"HealthCheck-1.0.0-py2.7.egg"+os.path.sep+"src"+os.path.sep)',
'executable_path="python web_health_check.pyc 8080 " + cur_dir',
'os.system(executable_path)']

web_health_check_pyfile=open(default_install+os.path.sep+"webhealthcheck.py","wb")
for line in webhealthchecklines:
    web_health_check_pyfile.writelines(line+"\n")
web_health_check_pyfile.close()
time.sleep(2)

shutil.copy(default_install+os.path.sep+"healthcheck.py",os.path.abspath(os.path.dirname(__file__)))
shutil.copy(default_install+os.path.sep+"webhealthcheck.py",os.path.abspath(os.path.dirname(__file__)))

if sys.platform.startswith("linux"):
    os.chmod(os.path.abspath(os.path.dirname(__file__))+os.path.sep+"healthcheck.py",0755)
    os.chmod(os.path.abspath(os.path.dirname(__file__))+os.path.sep+"webhealthcheck.py",0755)


if sys.platform.startswith("win"):
    #add to system path
    print "Setting environment path variable..."
    subprocess.call(['setx','Path','%Path%;'+default_install])

if sys.platform.startswith("linux"):
    shutil.copy(default_install+os.path.sep+"healthcheck.py","/bin/healthcheck.py")
    shutil.copy(default_install+os.path.sep+"webhealthcheck.py","/bin/webhealthcheck.py")
    os.chmod("/bin/healthcheck.py",0755)
    os.chmod("/bin/webhealthcheck.py",0755)
    

print "Creating uninstall script..."

uninstall_lines=['import os,sys,shutil,time',
'print "Starting HealthCheck Un-installation..."',                 
'install_dir = ' + "'" + default_install + "'",                               
'shutil.rmtree(install_dir, ignore_errors=True)',
'os.remove(\'/bin/healthcheck.py\')' if sys.platform.startswith("linux") else '',
'os.remove(\'/bin/webhealthcheck.py\')' if sys.platform.startswith("linux") else '',
'time.sleep(2)',
'print "HealthCheck Un-installation Successfull..."']

uninstall_pyfile=open(default_install+os.path.sep+"uninstall.py","wb")
for line in uninstall_lines:
    uninstall_pyfile.writelines(line+"\n")
uninstall_pyfile.close()
time.sleep(2)

print "HealthCheck Installation Successfull..."

    
