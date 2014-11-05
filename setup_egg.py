from setuptools import setup, find_packages
requires = [
          'colorama >=0.3.2', 
          'prettytable >= 0.7.2',
          'paramiko >=1.15.1',
          'pyvmomi >= 5.5.0.2014.1.1',
          'reportlab >= 3.1.8',
          ],
		  
setup(
    author='nutanix',
    name='HealthCheck',
    version = '1.0.0',
	packages=find_packages(),
    package_data ={'' : ['conf//*.conf','bin//*.sh','bin//*.bat','static//fonts//*.*','static//images//*.*','static//js//*.*','static//styles//*.*','templates//*.*']},
    exclude_package_data = { '': ['bin//build*.bat'] },
    install_requires=requires,
    zip_safe=False
      )
    
