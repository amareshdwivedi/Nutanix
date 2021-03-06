from setuptools import setup, find_packages
requires = [
          'colorama >=0.3.2', 
          'prettytable >= 0.7.2',
          'paramiko >=1.15.1',
          'pyvmomi >= 5.5.0.2014.1.1',
          'reportlab >= 3.1.8',
          'web.py >= 0.37',
          'lepl >= 5.1.3',
          ],
setup(
    author='nutanix',
    name='service_toolkit',
    version = '1.0.0',
	packages=find_packages(),
    package_data ={'' : ['conf//*.*',
                         'static//deployer//css//*.*',
                         'static//deployer//fonts//corbel//*.*','static//deployer//fonts//fontawesome//*.*','static//deployer//fonts//icon_sweet//*.*','static//deployer//fonts//proxima//*.*',
                         'static//deployer//images//*.*','static//deployer//images//button//*.*','static//deployer//images//form_elements//*.*','static//deployer//images//loaders//*.*',
                         'static//deployer//js//*.*','static//deployer//js//cl_editor//*.*','static//deployer//js//cl_editor//*.*','static//deployer//js//cl_editor//images//*.*','static//deployer//js//jq_tables//*.*',
                         'static//deployer//uploadify//*.*',
                         'static//fonts//corbel//*.*','static//fonts//fontawesome//*.*','static//fonts//icon_sweet//*.*','static//fonts//proxima//*.*','static//fonts//*.*',
                         'static//images//*.*','static//images//button//*.*','static//images//form_elements//*.*','static//images//loaders//*.*',
                         'static//js//*.*','static//js//jq_tables//*.*',
                         'static//styles//*.*','static//styles//css//*.*','static//styles//fonts//corbel//*.*','static//styles//fonts//fontawesome//*.*','static//styles//fonts//icon_sweet//*.*','static//styles//fonts//proxima//*.*','static//styles//uploadify//*.*',
                         'static//uploadify//*.*',
                         'templates//*.*',
                         'deployer']},
    install_requires=requires,
    zip_safe=False
      )
    
