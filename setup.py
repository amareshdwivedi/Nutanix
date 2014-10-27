from setuptools import setup, find_packages
requires = [
          'reportlab >= 3.1.8',
          'pyvmomi >= 5.5.0.2014.1.1',
          'prettytable >= 0.7.2',
          'paramiko >=1.15.1',
          'pycrypto >= 2.6.1',
          'colorama >=0.3.2',
          ],

setup(
    author='nutanix',
    name='HealthCheck',
    version = '1.0.0',
	packages=find_packages(),
    package_data ={'' : ['*.png','conf//*.conf','bin//*.sh','bin//*.bat']},
    install_requires=requires
      )
    
