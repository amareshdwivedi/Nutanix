from setuptools import setup, find_packages          
setup(
    author='nutanix',
    name='HealthCheck',
    version = '1.0.0',
    packages=find_packages(),
    package_data ={'' : ['conf//*.*','static//fonts//*.*','static//images//*.*','static//js//*.*','static//styles//*.*','templates//*.*']},
    zip_safe=False
      )
    
