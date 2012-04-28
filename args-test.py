import sys
import getopt



def usage():
	print """
Fruta!
Usage :  blavlavla

	"""

argv = sys.argv[1:] 

try :
	opts, args = getopt.getopt(argv, "a:s:f:h")
except :
	usage()
	sys.exit(2)

for opt, arg in opts :
	if opt == "-h" :
		usage() 
	else :
		print "opt:", opt, "arg:", arg
		
