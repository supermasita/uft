#!/usr/bin/python
# coding: utf-8

#from lib.config import *
#from lib.common import *
from lib.checker import *
#from lib.functions import *
#from pymediainfo import MediaInfo
import time
#import sys
#import hashlib 

# Initialize spawn
spawn = False 
# Check PID file 
pid = str(os.getpid())
pidfile = "%s/checker.pid" % tmppath
if os.path.isfile(pidfile):
    	logthis('%s already exists. The process should be running.' % pidfile)
	sys.exit()
else:
	# Create PID
	file(pidfile, 'w').write(pid)
	# Get sites and their paths 
	for sites in select_sites() :
		site_path = sites[0]
		site_name = sites[1]
		site_id = sites[2]
		# Walk the paths
		for root, folders, files in os.walk("%s/%s" % (incoming, site_path)):
			    # Check each file	
			    for file in files:
				statinfo = os.stat(os.path.join(root,file))
				timedif = time.time() - statinfo.st_ctime
				# Are they old enough to drink?
				if timedif > timedif_to :
					try:	
						# Check metada to know if it si a video
						isvideo, video_br, video_w, video_h, aspect_r, duration, size = media_check(site_path, file)
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
			print "No videos left to add."
	# Clean PID
	os.unlink(pidfile)
	# Spawn encode
	if spawn is True :
		spawn_process("encode")
