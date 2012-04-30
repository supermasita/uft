#!/usr/bin/python
# coding: utf-8
#
# UNATTENDED FFMPEG ENCODER
# https://github.com/supermasita/ufe  
# 

from lib.config import *
from lib.add import *
from lib.common import *
#from lib.upymediainfo import MediaInfo

#import os
import MySQLdb
#import datetime
#import hashlib
#import time
import sys
import simplejson
import getopt

def ufe_add_usage():
        """Prints the usage of "ufe-add".
        """
        print """
        Usage example : 
        
        ufe-add.py -a file -s default -f /var/tmp/lalala.avi
        ufe-add.py -a dir -s default -f /var/tmp/
        
        -a      Add file or directory
        -s      Name of the site 
        -f      Full path filename or directory
        """


# Get parameters
argv = sys.argv[1:]

try :
        opts, args = getopt.getopt(argv, "a:s:f:")
except :
        ufe_add_usage()
        sys.exit(2)

# Assign parameters as variables
for opt, arg in opts :
        if opt == "-a" :
                add = arg
        elif opt == "-s" :
                site_name = arg
        elif opt == "-f" :
                file_full_path = arg

# Check if all needed variables are set
if vars().has_key('add') and vars().has_key('site_name') and vars().has_key('file_full_path') :
	#
	if add == 'file' :
		#        
        	file_name_only = file_full_path.split("/")[-1]
	        file_path_only = "/".join(file_full_path.split("/")[:-1])+"/"
		# Tell me something about the site
		site_name, site_id, site_enabled = get_site(site_name)
		# Check metada to know if its a video
		isvideo, video_br, video_w, video_h, aspect_r, duration, size = media_check(file_full_path)
		if isvideo == True :
			# Video hash 
			vhash = create_vhash(file_name_only, site_name)
			# Append original filename (with vhash appended) and sanitized filename
			filename_san, filename_orig = create_filename_san(file_name_only, vhash)
			# Insert registers in DB
			create_video_registry(vhash, filename_orig, filename_san, video_br, video_w, video_h, aspect_r, duration, size, site_id, server_name)
			# Move file and create thumbnail blob
			move_original_file(file_path_only, file_name_only, filename_san)
			create_thumbnail(vhash, filename_san)
			logthis('%s was added as  %s for %s' % (filename_orig, filename_san, site_name))
			video_json = { "vhash":vhash, "filename_orig":filename_orig, "filename_san":filename_san, "video_br":video_br, "video_w":video_w, "video_h":video_h, "aspect_r":round(aspect_r, 2), "duration":duration, "size":size, "site_id":site_id, "server_name":server_name }
			print simplejson.dumps(video_json, indent=4, sort_keys=True)
			#
			spawn = True
		else :
			logthis('Couldn\'t add  %s -  Not enough metadata' % file)
	#
	elif add == 'dir' :
	        #        
        	file_path_only = "/".join(file_full_path.split("/")[:-1])+"/"
		# Tell me something about the site
                site_name, site_id, site_enabled = get_site(site_name)
		# Initialize spawn
		spawn = False 
		# Check PID file 
		pidfilename = "%s/ufe-add-dir.pid" % tmppath
		if os.path.isfile(pidfilename):
			logthis('%s already exists. The process should be running.' % pidfile)
			sys.exit()
		else:
			# Create PID
			pid = str(os.getpid())
			pidfile = open(pidfilename, 'w').write(pid)
			# Walk the path
			for root, folders, files in os.walk("%s" % file_path_only):
				    # Check each file   
				    for file in files:
					file_complete = os.path.join(root,file)
					statinfo = os.stat(file_complete)
					timedif = time.time() - statinfo.st_ctime
					# Are they old enough to drink?
					if timedif > timedif_to :
						try:
							# Check metada to know if it si a video
							isvideo, video_br, video_w, video_h, aspect_r, duration, size = media_check('%s' % file_complete)
							if isvideo == True :
								# Video hash 
								vhash = create_vhash(file, site_name)
								# Append original filename (with vhash appended) and sanitized filename
								filename_san, filename_orig = create_filename_san(file, vhash)
								# Insert registers in DB
								create_video_registry(vhash, filename_orig, filename_san, video_br, video_w, video_h, aspect_r, duration, size, site_id, server_name)
								# Move file and create thumbnail blob
								move_original_file(root, file, filename_san)
								create_thumbnail(vhash, filename_san)
								logthis('%s was added as  %s for %s' % (filename_orig, filename_san, site))
								#
								spawn = True
							else :
								logthis('Couldn\'t add  %s -  Not enough metadata' % file)
						except:
							pass
					else :
						logthis('%s was modified not far from now. Please wait.' % file)
			else :
				logthis('No videos left to add in %s' % file_path_only)
			# Clean PID
			os.unlink(pidfilename)
	
	else :
		print "\nPlease check parameters... Do you want to add a 'file' or a 'dir'?"
		ufe_add_usage()
		sys.exit(2)
        
	# Spawn encode
        if spawn is True :
               spawn_process("encode")

else :
        print "\nParameters missing ..."
	ufe_add_usage()
	sys.exit(2)
