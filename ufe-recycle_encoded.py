#!/usr/bin/python
# coding: utf-8

from lib.recycle import *

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
