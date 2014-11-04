from setuptools import setup, find_packages          
setup(
    author='nutanix',
    name='HealthCheck',
    version = '1.0.0',
    packages=find_packages(),
    package_data ={'' : ['conf//*.conf','bin//*.sh','bin//*.bat','resources//images//*.png']},
    exclude_package_data = { '': ['bin//build*.bat'] },
    zip_safe=False
      )
    
