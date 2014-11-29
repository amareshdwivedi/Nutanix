'''
Created on Nov 29, 2014

@author: GaneshM
'''
import json
import os
import sys
import time

from foundation.nutanixFoundation import FoundationProvision
from foundation.prismProvision import PrismActions
from serverConfiguration.vCenterServer import VCenterServerConf

import ssl
from functools import wraps
def sslwrap(func):
    @wraps(func)
    def bar(*args, **kw):
        kw['ssl_version'] = ssl.PROTOCOL_TLSv1
        return func(*args, **kw)
    return bar

if __name__ == "__main__":   
	ssl.wrap_socket = sslwrap(ssl.wrap_socket)

	confFile = os.getcwd()+os.path.sep+"conf"+os.path.sep+"input.json"
	fp = open(confFile,"r")
	inputData = json.load(fp)
	
	#Foundation Process
	print "+"+"-"*100+"+"+"\n"
	fProcess = FoundationProvision(inputData['foundation'])
	fProcess.init_foundation()
	while True:
		progPercent = fProcess.get_progress()
		num = int(progPercent.split('.')[0])

		if num == -1:
			print "Error Occurred !"
			sys.exit(1)

		sys.stdout.write('\r')
		sys.stdout.write("[ "+"#"*num+"."*(100-num)+" ] %s%%"%(num))
		time.sleep(1)
		
		if num == 100:
			break
	time.sleep(20)
	print "\n+"+"-"*100+"+"+"\n"
	print "Fondation Process Complete"
	
	#Prism Configuration
	ssl.wrap_socket = sslwrap(ssl.wrap_socket)
	prismObj = PrismActions(inputData['prismDetails'])
	print "\n+"+"-"*100+"+"+"\n"
	prismObj.create_storage_pool()
	print "\n+"+"-"*100+"+"+"\n"
	prismObj.create_container()
	
	#vCenterServer Configuration
	print "+"+"-"*100+"+"+"\n"
	vServer = VCenterServerConf(inputData['vCenterConf'])
	vServer.do_configuration()
	print "+"+"-"*100+"+"+"\n"
	print "Foundation + PrismAPI + vCenterServer Configuration :- Successfully Done."
	print "+"+"-"*100+"+"+"\n"
	sys.exit(0)

	
