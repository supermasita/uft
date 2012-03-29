#!/usr/bin/python
# coding: utf-8

from lib.encode import *

check_and_encode()

##
#check_pending = 1
## Loop to find queued videos
#while check_pending == 1 :	
#	# Test max number of allowed encode instances
#	max_ps_reached = check_running_ps()
#	if max_ps_reached == 0 :
#		update_running_ps("add")
#		# Are there any pending videos?
#		pending_encode = select_next_encode()[0]
#		if pending_encode == 1 :
#			# Nasty random wait to avoid two servers asking for the same video :S
#			random_wait()
#			# Get data for next encode and process 
#			pending_encode, vhash, vpid, encode_status, filename_san, encode_file, param = select_next_encode()
#			encode_video_ffmpeg(vhash, vpid, filename_san, encode_file, param)
#			# Spawn ftp.py
#			spawn_process("ftp")
#		else :
#			print "No videos left to encode."
#			check_pending=0
#		update_running_ps("substract")
#	else :
#		logthis('Max. allowed instances reached.')
#		check_pending = 0
#
