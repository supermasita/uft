#!/usr/bin/python
# coding: utf-8
#
# UNATTENDED FFMPEG ENCODER
# https://github.com/supermasita/ufe
# 


from config import *
from common import *

import os
import MySQLdb
import time
import datetime
import subprocess
import simplejson

#
##
###

def select_next_encode():
        """Selects next video to encode.
           Returns pending_encode, vhash, vpid, encode_status, filename_san, encode_file, param.
        """
        random_wait()
	db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
	# We check if there already is a VP running for the VHASH. We exclude this VHASH from the choice of next encode.
	cursor=db.cursor()
        cursor.execute("select video_encoded.vhash from video_encoded where video_encoded.encode_status=2 and video_encoded.server_name='%s';" % server_name )
	results=cursor.fetchall()
	# We create a string to use as "NOT IN"	in the query
	skip_vhash=""
	for row in results :
		skip_vhash=skip_vhash+"'"+row[0]+"'"+","
	skip_vhash=skip_vhash[:-1]			
	# No VP running? We choose any VHASH. Else, use "NOT IN"
	if len(skip_vhash) == 0 :
		cursor.execute("select video_encoded.vhash, video_encoded.vpid, video_encoded.encode_status, video_encoded.encode_file from video_encoded where video_encoded.encode_status=1 and video_encoded.server_name='%s' order by video_encoded.weight limit 1;" % server_name )
	else :
		cursor.execute("select video_encoded.vhash, video_encoded.vpid, video_encoded.encode_status, video_encoded.encode_file from video_encoded where video_encoded.encode_status=1 and video_encoded.server_name='%s' and video_encoded.vhash not in (%s) order by video_encoded.weight limit 1;" % (server_name, skip_vhash) )
	results=cursor.fetchall()
	# Any videos pending?
	for registry in results:
                #print registry
		vhash=registry[0]
                vpid=registry[1]
                encode_status=registry[2]
                encode_file=registry[3]
	if vars().has_key('vhash') :
                # get the original filename
                cursor.execute("select video_original.filename_san from video_original where vhash='%s';" % vhash )
                results=cursor.fetchall()
		for registry in results:
                        filename_san=registry[0]
                # get the video profile parameters
                cursor.execute("select video_profile.param_ffmpeg from video_profile where vpid=%i;" % vpid )
                results=cursor.fetchall()
                for registry in results:
                        param=registry[0]
		# set pending_encode as true (1)
		pending_encode=1
        else :
                pending_encode = vhash = vpid = encode_status = filename_san = encode_file = param = 0
        cursor.close ()
	db.close ()
	return pending_encode, vhash, vpid, encode_status, filename_san, encode_file, param


def update_encode_status(state, u_vhash, u_vpid):
	"""Updates the encoded status of a video the table "video_encoded".
	"""
	encode_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
	cursor=db.cursor()
	cursor.execute("update video_encoded set encode_status=%i, encode_time='%s' where vhash='%s' and vpid=%i ;" %  (state, encode_time, u_vhash, u_vpid) )
        cursor.close ()
        db.commit ()
        db.close ()


def update_vp_quantity(u_quantity, u_vp_status, u_vhash):
	"""Increments or decrements the total of video profiles with for the vhash on the video_original table.
	"""
	status_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
        cursor=db.cursor()
        cursor.execute("update video_original set %s=%s+(%i), status_time='%s' where vhash='%s';" %  (u_vp_status, u_vp_status, u_quantity, status_time, u_vhash) )
        cursor.close ()
        db.commit ()
        db.close ()


def encode_video_ffmpeg(e_vhash, e_vpid, e_filename_san, e_encode_file, e_param) :
        """Encodes video with FFMPEG.
           Returns integer - STDOUT status.
        """
        update_encode_status(2, e_vhash, e_vpid)
	update_vp_quantity(1, 'vp_run', e_vhash) 
	# Create folder for vhash
        if not os.path.exists('%s%s' % (encoded, e_vhash)):
                os.makedirs('%s%s' % (encoded, e_vhash))
        # Source and destination for FFMPEG
        source = "%s%s" % (original, e_filename_san)
        destination = "%s%s/%s" % (encoded, e_vhash, e_encode_file)
	# Log path and filename 
	e_encode_file_name, e_encode_file_e = os.path.splitext(e_encode_file)
	e_encode_file_log = "%s%s/%s.log" % (encoded, e_vhash, e_encode_file_name)
	# FFMPEG command
	#command='%s -i %s %s %s' % (ffmpeg_bin, source, e_param, destination)
	try :
		logthis("Encode started : %s" % e_encode_file)
		# FFMPEG - Arguments to list in order to use subprocess
		command='%s -i %s %s %s' % (ffmpeg_bin, source, e_param, destination)
		commandlist=command.split(" ")
        	encode_log_file = open(e_encode_file_log,"wb")
		output = subprocess.call(commandlist, stderr=encode_log_file, stdout=encode_log_file)
	except :
		output = 1
		pass
        # Check command output
        if output != 0 :
		logthis("Encode failed : %s" % e_encode_file)
                update_encode_status(4, e_vhash, e_vpid)
		update_vp_quantity(-1, 'vp_run', e_vhash)
		update_vp_quantity(1, 'vp_error', e_vhash)
	else :
		logthis("Encode successful : %s" % e_encode_file)
		logthis("Hinting started : %s" % e_encode_file)
                # We use qt-faststart for hinting
                qt_command = '%slib/qt-faststart.py %s' % (core_root, destination)
                qt_commandlist = qt_command.split(" ")
		qt_log_file = open("%s%s/%s.qt.log" % (encoded, e_vhash, e_encode_file_name), "wb")
		qt_output = subprocess.call(qt_commandlist, stderr=qt_log_file, stdout=qt_log_file)
		#
		logthis("Hinting successful : %s" % e_encode_file)
		update_encode_status(3, e_vhash, e_vpid)
		update_vp_quantity(-1, 'vp_run', e_vhash)
		# Try to create JSON file
		if create_video_json is True :
			try :
				create_video_json_file(e_vhash)
				logthis("JSON created : %s" % e_vhash)
			except :
				logthis("JSON failed : %s" % e_vhash)
				pass
        return output



def create_video_json_file(vhash) :
	"""Creates JSON file with the encoded videos profile specs. Usefull to create adaptative
	   video playlists.
	"""
	db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
	cursor=db.cursor()
	
	# Create dictionary with video profiles specs
	cursor.execute("SELECT vpid, profile_name, bitrate, height, width from video_profile;")
	video_profiles = {}

	# Loop query result and fill dictionary
	while (1):
		result = cursor.fetchone()
		if result == None: break
		#
		video_profiles["%i" % result[0]] = { "profile_name" : result[1],  "bitrate" : "%i" % result[2], "height" : "%i" % result[3], "width" : "%i" % result[4] }



	# Create dictionary with all the encoded videos of a given vhash
	cursor.execute("SELECT vpid, encode_file, encode_status, ftp_path from video_encoded where vhash='%s';" % vhash)
	video_json = {}

	# Loop query result and fill dictionary
	while (1):
		result = cursor.fetchone()
		if result == None: break
		#
		video_json[video_profiles["%i" % result[0]]["profile_name"]] = { "file" : result[1], "ftp_path" : result[3], "encode_status" : result[2], "bitrate" : video_profiles["%i" % result[0]]["bitrate"], "height" : video_profiles["%i" % result[0]]["height"], "width" : video_profiles["%i" % result[0]]["width"] }


	# Close cursor and DB conn
	cursor.close ()
	db.close()

	# Create JSON file
	video_json_content = simplejson.dumps(video_json, indent=4, sort_keys=True)
	video_json_file = open("%s%s/%s.json" % (encoded, vhash, vhash), 'w')
	video_json_file.write(video_json_content)


#def check_and_encode() :
#	"""Checks for pending videos and encodes them.
#	"""
#	check_pending = 1
#	# Loop to find queued videos
#	while check_pending == 1 :
#		# Test max number of allowed encode instances
#		max_ps_reached = check_running_ps()
#		if max_ps_reached == 0 :
#			update_running_ps("add")
#			# Are there any pending videos?
#			pending_encode = select_next_encode()[0]
#			if pending_encode == 1 :
#				# Nasty random wait to avoid two servers asking for the same video :S
#				random_wait()
#				# Get data for next encode and process 
#				pending_encode, vhash, vpid, encode_status, filename_san, encode_file, param = select_next_encode()
#				encode_video_ffmpeg(vhash, vpid, filename_san, encode_file, param)
#				# Spawn ftp.py
#				spawn_process("upload")
#			else :
#				print "No videos left to encode."
#				check_pending=0
#			update_running_ps("substract")
#		else :
#			logthis('Max. allowed instances reached.')
#			check_pending = 0

