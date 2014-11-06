import os
import sys
import struct
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
            if (8 * struct.calcsize("P")) == 32:  # for 32bit python compiler 
                easy_install.main(["-Z", "--install-dir", install_dir_lib, lib_path + 'Pillow-2.6.1-py2.7-win32.egg'])
            elif (8 * struct.calcsize("P")) == 64:  # for 64bit python compiler
                easy_install.main(["-Z", "--install-dir", install_dir_lib, lib_path + 'Pillow-2.6.1-py2.7-win-amd64.egg'])
            else:
                easy_install.main(["-Z", "--install-dir", install_dir_lib, lib_path + lib])
    else :
        easy_install.main(["-Z", "--install-dir", install_dir_lib, lib_path + lib])

