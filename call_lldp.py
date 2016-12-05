from lldp_validator import verifylldp

if __name__ == "__main__":
 	node, results =verifylldp()
 	print "\n"
 	print "Scanned Node: "+node+"\n"
 	print "Format: {Node : [{RECEIVED (Device Interface) : EXPECTED (Dot Interface)}]\n"
 	if results:
 		print results
 	else:
 		print "Everything is looking good"
 	print "\n"
