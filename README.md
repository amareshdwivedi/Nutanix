HealthCheck
===========
Nutanix HealthCheck Tool


Prerequisite to run HealthCheck (Follows Sequence)
==================================================
1.)Download and install Python 2.7.8.
2.)For windows machine download and install - Microsoft Visual C++ Compiler for Python 2.7 (http://www.microsoft.com/en-us/download/details.aspx?id=44266).
3.)Install pip (Follow instructions at - https://pip.pypa.io/en/latest/installing.html#id7).
4.)Install vmware vSphere API- vmware/pyvmomi (pip install pyvmomi).
5.)Install reportlab (pip install reportlab).
6.)Install prettytable (pip install prettytable).
7.)Install paramiko (pip install paramiko).
8.)Install pycrypto (pip install pycrypto).
9.)Install colorama (pip install colorama). 

To create .egg distribution file for HealthCheck use following command
======================================================================
python setup.py bdist_egg --exclude-source-files