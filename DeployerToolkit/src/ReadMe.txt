###################################################################################################
Software Dependency :
python Version                :    2.7.8
Package Dependency            :    lepl (5.1.3)     / pip install lepl 
                                   paramiko (1.15.1) / pip install paramiko (dependency same as health check)
                                   pyvmomi (5.5.0.2014.1.1) / pip install pyvmomi
###################################################################################################
directory Structure -
\src : Project Home Directory
\src\iaasProvisioning.py     :    Driver script for foundation , prism provisioning & vCenter server configuration.
\src\conf                    :    input.json - all the details for provisioning process at a single place.
\src\foundation              :    Source for Infra-structure provisioning.
\src\serverConfiguration     :    Source for Server configuration ( only vCenter for now).

###################################################################################################
Usage                        :    python iaasProvisioning    
