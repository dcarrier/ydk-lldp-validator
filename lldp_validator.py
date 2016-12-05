import inspect
import sys
import ncclient
from argparse import ArgumentParser
from urlparse import urlparse
from collections import defaultdict
from ydk.services import CRUDService
from ydk.providers import NetconfServiceProvider
from ydk.models.ethernet import Cisco_IOS_XR_ethernet_lldp_oper as xr_ethernet_lldp
from ydk.models.shellutil import Cisco_IOS_XR_shellutil_oper as xr_shellutil_oper


def _formatInterface(*args):
	"""Normalizes the name and format of interface names"""
	# Need to test 10G and 40G Support
	# Create list for return tuple
	args_return =[]
	#Loop through each entry in args and format interface name (Support 100G,40G,10G,1G)
	for a in args:
		for i in a:
			if i.isdigit():
				prefix= a[:a.index(i)]
				suffix= a[a.index(i):]
				break
		prefix = prefix.lower()
		if prefix[0]+prefix[1] == "hu":
			prefix = "HundredGigE"
			intf = prefix + suffix
			args_return.append(prefix+suffix)
		elif prefix[0]+prefix[1] == "fo":
		    prefix = "FortyGigE"
		    args_return.append(prefix+suffix)
		elif prefix[0]+prefix[1] == "te":
		    prefix = "TenGigE"
		    args_return.append(prefix+suffix)
		elif prefix[0]+prefix[1] == "gi":
		    prefix = "GigE"
		    args_return.append(prefix+suffix)
		elif prefix[0]+prefix[1] == "fa":
		    prefix = "FastE"
		    args_return.append(prefix+suffix)
		elif prefix[0]+prefix[1] == "et":
		    prefix = "Ethernet"
		    args_return.append(prefix+suffix)
		elif prefix[0]+prefix[1] == "mg":
		    prefix = "MgmtE"
		    args_return.append(prefix+suffix)
		else:
			###Crash / Insert System Exit###
			if prefix:
				print "Error in formatInterface: "+prefix
				sys.exit(1)
				#"Interface "+prefix+" is not a valid/supported interface"
			else:
				sys.exit(1, "No Data Recieved")

	#Return interface coversions in tuple form
	return tuple(args_return)

def _getHost(crud, provider):
	"""Retrieves the hostname of the current node we are verifying"""
	#Create shellutil oper object from ydk
	shell_util = xr_shellutil_oper.SystemTime()

	#Read the object from the XR node
	shell_util = crud.read(provider,shell_util)

	return shell_util.uptime.host_name

def _getlldpInfo(crud,provider):
	"""Retreives the lldp data of the current node we are investigating"""
	#Create lldp oper object from ydk
	lldp_toplevel = xr_ethernet_lldp.Lldp.Nodes()

	#Read the object from the XR node
	lldp_toplevel = crud.read(provider, lldp_toplevel)

	return lldp_toplevel

def _modelDot(node_host):
	"""Converts the provided dot file into python data structures"""
	#Create default dict to append topological information
	dot_topology = defaultdict(list)

	#Read static file in directory /* Add dynamic file passing */
	topology = open('topology.dot','r')

	#Loop through each in the topology and format data, at the end append to dot_topology
	#Check line to ensure it is in the proper format
	for line in topology:
		if "--" and node_host in line:
			line = line.rstrip(';\n').replace(" ", "").split('--')
			#Do in one normal for loop, both node_index & remote_index
			node_index = [i for i, s in enumerate(line) if node_host in s]
			remote_index = [i for i, s in enumerate(line) if node_host not in s]
			node_info = line[node_index[0]].split(':')
			neigh_name, neigh_intf = line[remote_index[0]].split(':')
			if node_info[1].startswith('"'):
				node_info[1] = node_info[1][1:]
			if node_info[1].endswith('"'):
				node_info[1] = node_info[1][:-1]
			if neigh_intf.startswith('"'):
				neigh_intf = neigh_intf[1:]
			if neigh_intf.endswith('"'):
				neigh_intf = neigh_intf[:-1]
			node_info[1], neigh_intf = _formatInterface(node_info[1], neigh_intf)
			dot_topology[node_info[1]].append({neigh_name[1:-1]:neigh_intf})
	return dot_topology

def _modelDevice(lldp_toplevel):
	"""Converts the lldp data of the current node into proper python data structures"""
	intf_list=[]
	device_topology = defaultdict(list)
	neigh_hostname = lldp_toplevel.node[0].neighbors.summaries.summary
	hostname_list = [neigh_hostname[i].lldp_neighbor[0].device_id for i in xrange(len(neigh_hostname))]

	for index, i in enumerate(hostname_list):
			local_interface = neigh_hostname[index].lldp_neighbor[0].receiving_interface_name
			remote_interface = neigh_hostname[index].lldp_neighbor[0].port_id_detail
			local_interface, remote_interface = _formatInterface(local_interface,remote_interface)
			device_topology[i].append({local_interface:remote_interface})
	return device_topology

def _validateTopo(device_topology,dot_topology,node_host):
	"""Validates the node lldp information against the provided dot file informations"""
	bad_wiring = defaultdict(list)
	for key in dot_topology:
		#If Remote Intf Node on a given key on the device != the dot file remote intf for the given key
		for d in device_topology[dot_topology[key][0].keys()[0]]:
			try:
				dev_remote_intf = d[key]
				break
			except:
				pass
		if dev_remote_intf != dot_topology[key][0].values()[0]:
			bad_wiring[dot_topology[key][0].keys()[0]].append({dev_remote_intf:dot_topology[key][0].values()[0]})
	return bad_wiring

def verifylldp():
	parser = ArgumentParser()
	parser.add_argument("device",
						help="NETCONF device (ssh://user:password@host:port)")
	args = parser.parse_args()
	device = urlparse(args.device)
	try:
		provider = NetconfServiceProvider(address=device.hostname,
										  port=device.port,
										  username=device.username,
										  password=device.password,
										  protocol=device.scheme)
	except ncclient.transport.errors.SessionCloseError, err:
		print "Could not connect to the NetConf Agent: ", err
		sys.exit(1)
	except ncclient.transport.errors.AuthenticationError, err:
		print "Could not connect to the NetConf Agent: ", err
		sys.exit(1)

	crud = CRUDService()
	lldp_toplevel = _getlldpInfo(crud, provider)
	node_host = _getHost(crud,provider)
	dot_topology = _modelDot(node_host)
	device_topology = _modelDevice(lldp_toplevel)
	bad_wiring = _validateTopo(device_topology,dot_topology,node_host)
	return node_host, bad_wiring