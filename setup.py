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
          'pycrypto >= 2.6.1',
          'colorama >=0.3.2',],

setup(
    author='krishnamurthy_b',
    name='HealthCheck',
     version = '1.0.0',
    packages=['src','src.checkers','src.reports'],
    include_package_data=True,
    data_files=[('src', ['src//nutanixlogo.png']),
                  ('src//conf', ['src//conf//ncc.conf','src//conf//vc.conf','src//conf//auth.conf'])],
    long_description=open('README.md').read(),
    install_requires=requires
      )
    
