#!/usr/bin/python
# coding: utf-8
#
# UNATTENDED FFMPEG ENCODER
# https://github.com/supermasita/ufe  
# 

from lib.recycle import *
import sys
import getopt

#
##
###

def ufe_recycle_usage():
        """Prints the usage of "ufe-recycle".
        """
        print """
        Usage example : 
        
        ufe-recycle.py -r encoded
        ufe-recycle.py -r original
        ufe-recycle.py -r registers
        ufe-recycle.py -r nonvideos

        """
#
##
###


# Get parameters
argv = sys.argv[1:]

try :
        opts, args = getopt.getopt(argv, "r:")
except :
        ufe_recycle_usage()
        sys.exit(2)

# Assign parameters as variables
for opt, arg in opts :
        if opt == "-r" :
                recycle_this = arg

# Check if all needed variables are set
if vars().has_key('recycle_this') :
        #
        if recycle_this == 'encoded' :
		#
		check_pending=1

		# Start looping for videos to recycle
		while check_pending==1 :
			# 
			pending_encoded_recycle, t_created, vhash, encode_time, vpid, encode_file = select_next_encoded_recycle()
			# Is there something to recycle?
			if pending_encoded_recycle == 1 :
				# So long and thanks for all the fish, video!
				os.unlink(encoded+"/"+vhash+"/"+encode_file)
				logthis('%s/%s/%s was erased.' % (encoded, vhash, encode_file))
				# 
				update_encoded_recycle_status(3, vhash, vpid)
			else :
				print "No encoded videos left to recycle."
				check_pending=0
	#
	elif recycle_this  == 'original' :
		# Search next video to recycle
		pending_original_recycle, pending_video_list = select_next_original_recycle()
		if pending_original_recycle == 1 :
			for registry in pending_video_list :
				vhash = registry[0]
				filename_san = registry[1]
				# Delete the file
				os.unlink(original+"/"+filename_san)
				logthis('The file %s/%s was erased.' % (original, filename_san))
				# Delete the directory  
				shutil.rmtree(encoded+"/"+vhash)
				logthis('The directory %s/%s was erased' % (encoded, vhash))
				# Update status
				update_original_recycle_status(3, vhash)
		else :
			print "No original videos left to recycle."
	#
	elif recycle_this  == 'nonvideos' :
		# Call function ...
		recycle_nonvideos()
	#	
	elif recycle_this  == 'registers' :
		# Call function ...
		recycle_old_registers()
	#
	else :
	        print "\nWrong parameters..."
	        ufe_recycle_usage()
        	sys.exit(2)

else :
	print "\nWrong parameters..."
	ufe_recycle_usage()
	sys.exit(2)
