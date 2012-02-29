#!/usr/bin/python
# coding: utf-8

from config import *
from common import *
import os
import MySQLdb
import time
import datetime
import subprocess

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
	command='%s -i %s %s %s' % (ffmpeg_bin, source, e_param, destination)
	try :
		# Arguments to list in order to use subprocess
        	commandlist=command.split(" ")
        	encode_log_file = open(e_encode_file_log,"wb")
		output = subprocess.call(commandlist, stderr=encode_log_file, stdout=encode_log_file)
	except :
		output = 1
		pass
        # Check command output
        if output != 0 :
                update_encode_status(4, e_vhash, e_vpid)
		update_vp_quantity(-1, 'vp_run', e_vhash)
		update_vp_quantity(1, 'vp_error', e_vhash)
		logthis('Error while trying to encode %s' % e_encode_file)
	else :
                # We use qt-faststart for hinting
		command = '%slib/qt-faststart.py "%s"' % (core_root, destination)
		output = subprocess.call(commandlist)
		#print "qt outputs %i" % output
		#
		update_encode_status(3, e_vhash, e_vpid)
		update_vp_quantity(-1, 'vp_run', e_vhash)
                logthis('%s successfully encoded' % e_encode_file)
        return output






