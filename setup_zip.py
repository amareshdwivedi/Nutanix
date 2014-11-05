from setuptools import setup, find_packages          
setup(
    author='nutanix',
    name='HealthCheck',
    version = '1.0.0',
    packages=find_packages(),
    package_data ={'' : ['conf//*.conf','bin//*.sh','bin//*.bat','static//fonts//*.*','static//images//*.*','static//js//*.*','static//styles//*.*','templates//*.*']},
    exclude_package_data = { '': ['bin//build*.bat'] },
    zip_safe=False
      )
    
