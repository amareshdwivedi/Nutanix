'''
Created on Oct 14, 2014

@author: krishnamurthy_b
'''


from setuptools import setup, find_packages
from distutils.extension import Extension
requires = ['reportlab >= 3.1.8',
          'pyvmomi >= 5.5.0.2014.1.1',
          'prettytable >= 0.7.2',
          'paramiko >=1.15.1',
          'pycrypto >= 2.6.1', ],

setup(
    author='krishnamurthy_b',
    name='HealthCheck',
    packages=['HealthCheck','HealthCheck.checkers','HealthCheck.reports'],
    include_package_data=True,
    data_files=[('HealthCheck', ['HealthCheck//nutanixlogo.png']),
                  ('HealthCheck//conf', ['HealthCheck//conf//ncc.conf','HealthCheck//conf//vc.conf'])],
    long_description=open('HealthCheck//README.md').read(),
    install_requires=requires,
      )
    
