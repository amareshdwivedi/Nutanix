import atexit
from pyVim import connect
from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
from requests.exceptions import ConnectionError
import warnings
import sys

class ClusterProvision:
	def __init__(self,host="10.1.222.184",user="root",pwd="vmware",port=443):
		self.si = None
		self.connectVC(host,user,pwd,port)
	
	def connectVC(self,host,user,pwd,port):
		warnings.simplefilter('ignore')
		try:
			self.si = connect.SmartConnect(host=host,user=user,pwd=pwd,port=port)
			print "Connection Successful"
		except vim.fault.InvalidLogin:
			print "Error : Invalid vCenter Server Username or password"
			sys.exit(2)
		except ConnectionError as e:
			print "Error : Connection Error"
			sys.exit(2)
	
	def disConnectVC(self):
		Disconnect(self.si)

	def list_datacenters(self):
		installed_dcs = []
		childEntity = self.si.content.rootFolder.childEntity
		installed_dcs.extend([childEntity[i].name for i in range(0,len(childEntity))])
		return installed_dcs

	def get_datacenter(self,dcName):
		folder = self.si.content.rootFolder
		if folder is not None and isinstance(folder, vim.Folder):
			for dc in folder.childEntity:
				if dc.name == dcName:
					return dc
		return None


	def create_datacenter(self, dcname=None):
		if len(dcname) > 79:
			raise ValueError("The name of the datacenter must be under 80 characters.")

		# List Datacenters
		avail_datacenters = self.list_datacenters()

		folder = self.si.content.rootFolder
		# Create a new Datacenter 	
		if folder is not None and isinstance(folder, vim.Folder):
			print "Creating new datacenter: %s "%(dcname)
			if dcname in avail_datacenters:
				print "[Datacenter did not create.  Please investigate ]"
				sys.exit(2)
			else:
				newdc = folder.CreateDatacenter(name=dcname)
				print "[ Datacenter successfully created! ]"
		return newdc

	def list_clusters(self,datacenter=None):
		# List Clusters in given Datacenter
		avail_clusters = []
		clusters = datacenter.hostFolder.childEntity
		avail_clusters.extend([clusters[i].name for i in range(0,len(clusters))])
		return avail_clusters

	def create_cluster(self, cname=None, datacenter=None):
		# create new cluster in given Datacenter
		print "[ Creating new cluster: %s in datacenter: %s ]"%(cname,datacenter.name)
		if cname is None:
			raise ValueError("Missing value for name.")
			sys.exit(2)
		if datacenter is None:
			raise ValueError("Missing value for datacenter.")
			sys.exit(2)
		
		cluster_spec = vim.cluster.ConfigSpecEx()
		
		avail_clusters = self.list_clusters(datacenter)
		if cname in avail_clusters:
			print "[Cluster did not create.  Please investigate ]"
			sys.exit(0)
		else:	
			newc = datacenter.hostFolder.CreateClusterEx(name=cname, spec=cluster_spec)
			print "[ Cluster successfully created! ]"

		return newc
	
	def add_host(self,cluster,hosts):
		print "Adding Host"
		#Add host to the Cluster // Add-VMHost equivalent
		print "[ Adding host $vmhost to cluster $clusterName ]"
		print "-- Please be patient.  This could take a few moments --"
		for xhost in hosts:
			print "confi details :",xhost

			# confiugre connectspec using sslThumbprint
			add_host = vim.host.ConnectSpec(hostName=xhost['ip'],userName=xhost['user'],password=xhost['pwd'])
			print "Add Host :",add_host, type(add_host)
			print "Container :",cluster, type(cluster)
			try:
				taskid = cluster.AddHost(add_host,asConnected=True,license="D4:F1:35:5D:60:6D:6F:78:05:B2:70:62:F1:74:FA:B5:BD:29:DD:0E")
			except:
				print "Unexpected error:", sys.exc_info()[0]
			'''
			print "cluster host:",cluster.host
			for item in cluster.host:
				print item.name
			
				connect_host = vim.host.ConnectSpec(hostName=xhost['ip'],userName=xhost['user'],password=xhost['pwd'])
				item.
			print "after adding :",host
			'''
		

if __name__ == "__main__":
	#Specify which version to run
	version = "1.3"
	print "Running version %s of the Nutanix GSO cluster provisioning script"%(version)
	
	if len(sys.argv) <= 6:
		print "invalid number of arguements"
		sys.exit(2)

	host,user,pwd,port = sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
	dcName = sys.argv[5]
	clusterName= sys.argv[6]
	
	# Hosts shold be send as command line arguement in below format // for now host is hardcoded.
        #hostList = sys.argv[7]
	hostList = [{'ip':'10.1.222.83','user':'root','pwd':'nutanix/4u'}]

	provObj = ClusterProvision(host,user,pwd,port)

	dc = provObj.create_datacenter(dcName)
	newc = provObj.create_cluster(clusterName, dc)
	provObj.add_host(newc,hostList)

	provObj.disConnectVC()
	sys.exit(1)
