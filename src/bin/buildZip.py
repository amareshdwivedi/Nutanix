import subprocess
import os
import shutil
import zipfile
import sys
import time

build_dir = os.getcwd()
os.chdir(".."+os.path.sep+".."+os.path.sep)
home_dir = os.getcwd()

cmd = 'python setup_zip.py bdist_egg --exclude-source-files'
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
out, err = p.communicate()
if err:
	print "Failed with error #errorlevel."
	sys.exit(0)

print "HealthCheck Egg Created..."
time.sleep(2)
print "Creating Zip Package..."
time.sleep(2)

if os.path.exists("HealthCheck-1.0.0"):
	shutil.rmtree("HealthCheck-1.0.0", ignore_errors=True)

os.mkdir("HealthCheck-1.0.0")
os.chdir("HealthCheck-1.0.0")
os.mkdir("eggs")
os.mkdir("get_pip")

print "Copying Required Files....."
time.sleep(2)
os.chdir(home_dir)
shutil.copy("get_pip.py", "HealthCheck-1.0.0"+os.sep+"get_pip")

os.chdir(home_dir+os.sep+"dist")

shutil.copy("HealthCheck-1.0.0-py2.7.egg", home_dir+os.sep+"HealthCheck-1.0.0"+os.sep+"eggs")

os.chdir(home_dir+os.sep+"src"+os.sep+"libs")
for xfile in os.listdir("."):
	shutil.copy(xfile, home_dir+os.sep+"HealthCheck-1.0.0"+os.sep+"eggs")


os.chdir(home_dir+os.sep+"src"+os.sep+"bin")
for xfile in os.listdir("."):
	if (xfile.startswith("build") or xfile.startswith("BUILD")):
		continue
	else:
         shutil.copy(xfile, home_dir+os.sep+"HealthCheck-1.0.0")

os.chdir(home_dir+os.sep+"src"+os.sep+"bin")

os.chdir(home_dir)
zf = zipfile.ZipFile("HealthCheck-1.0.0.zip", "w")
for dirname, subdirs, files in os.walk("HealthCheck-1.0.0"):
    zf.write(dirname)
    for filename in files:
      zf.write(os.path.join(dirname, filename))
zf.close()

print "Removing Temporary Files....."
time.sleep(2)

shutil.rmtree("dist", ignore_errors=True)
shutil.rmtree("build", ignore_errors=True)
shutil.rmtree("HealthCheck.egg-info", ignore_errors=True)
shutil.rmtree("HealthCheck-1.0.0", ignore_errors=True)

print "HealthCheck-1.0.0.zip Created Successfully at: " + os.getcwd()

