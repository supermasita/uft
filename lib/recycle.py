#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# UNATTENDED FFMPEG ENCODER
# https://github.com/supermasita/ufe
# 

from config import *
from common import *

import os
import shutil

#
##
###

def recycle_old_registers(interval=5):
        """Removes registers from DB of videos that have already been recycled.
	"""
	db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
        cursor=db.cursor()
        cursor.execute("SELECT vhash from video_original where server_name='%s' and recycle_status=3 and t_created < DATE_SUB(current_timestamp(), INTERVAL %i MINUTE);" % (server_name, interval) )
        results=cursor.fetchall()
	cursor.close ()
	# Any results?
	if len(results) > 0 :
		for registry in results:
			vhash = registry[0]
			cursor_vhash=db.cursor()
			cursor_vhash.execute("delete from video_original where vhash='%s';" % vhash )
			cursor_vhash.execute("delete from video_encoded where vhash='%s';" % vhash )
			db.commit()
			cursor_vhash.close()
			logthis('Deleted all registers for vhash: %s' % vhash)
	else :
		print "There are no old registers to delete."
        db.close ()

def recycle_nonvideos():
        """Removes non videos registers from DB of videos and erases the files.
        """
        db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
        cursor = db.cursor()
        cursor.execute("SELECT vhash, filename_san FROM video_original where video_br is null and video_w is null and server_name='%s';" % server_name )
	results = cursor.fetchall()
	#	
	if len(results) >= 1 :
		#	
		for vhash, filename in results :
			print vhash, filename
			# Delete filename
			try :
				os.unlink('%s/%s' % (original, filename))
				logthis('Deleted nonvideo file : %s/%s' % (original, filename))
			except :
				logthis('Couldn\'t delete nonvideo file : %s/%s' % (original, filename))
			# Delete register
			cursor.execute("DELETE from video_original where vhash='%s';" % vhash) 
			logthis('Deleted nonvideo register : %s' % vhash)
			db.commit ()
	else :
		logthis('No nonvideos left to recycle.')
	#
        cursor.close ()
        db.close ()


def select_next_original_recycle(interval=5):
        """Finds original videos whose encoded videos have been already recycled and deletes them.
        """
        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
        cursor=db.cursor()
        cursor.execute("select vhash, filename_san from video_original where recycle_status=1 and server_name='%s' and status_time<DATE_SUB(CURRENT_TIMESTAMP, INTERVAL %i MINUTE);" % (server_name, interval) )
        results=cursor.fetchall()
        pending_video_list = list()
        lista_vhash = list()
        pending_original_recycle=0
        for registry in results:
                vhash = registry[0]
                filename_san = registry[1]
                lista_vhash.append([vhash, filename_san])
        if vars().has_key('vhash') :
                for registry in lista_vhash :
                        lvhash = registry[0]
			lfilename_san = registry[1]
			# all encoded videos for vhash
			cursor.execute("select count(*) from video_encoded where vhash='%s';" % lvhash )
			result_total = cursor.fetchall()
			# recycled encoded videos for vhash
                        cursor.execute("select count(*) from video_encoded where vhash='%s' and recycle_status=3;" % lvhash )
                        result_recycled = cursor.fetchall()
			# compare
                        if result_total[0][0] == result_recycled[0][0] :
				pending_video = [lvhash, lfilename_san]
				pending_video_list.append(pending_video)
	# Empty list?
	if len(pending_video_list)<1 :
		pending_original_recycle = pending_video_list = 0
	else :
                pending_original_recycle = 1
        cursor.close ()
        db.close ()
	return pending_original_recycle, pending_video_list

def update_encoded_recycle_status(state, u_vhash, u_vpid):
	"""Updates the recycled status of a encoded video.
	"""
        recycle_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
        cursor=db.cursor()
        cursor.execute("update video_encoded set recycle_status=%i, recycle_time='%s' where vhash='%s' and vpid=%i;" %  (state, recycle_time, u_vhash, u_vpid) )
        cursor.close ()
        db.commit ()
        db.close ()


def update_original_recycle_status(state, u_vhash):
	""" Updates de encoded status of a original video.
	"""
        recycle_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
        cursor=db.cursor()
        cursor.execute("update video_original set recycle_status='%i', recycle_time='%s' where vhash='%s' ;" %  (state, recycle_time, u_vhash) )
        cursor.close ()
        db.commit ()
        db.close ()


def select_next_encoded_recycle(interval=5):
	"""Finds already uploaded encoded videos and deletes them.
	"""
        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
        cursor=db.cursor()
        cursor.execute("select t_created, vhash, encode_time, vpid, encode_file from video_encoded where recycle_status=1 and ftp_status=3 and encode_status=3 and ftp_time < DATE_SUB(current_timestamp(), INTERVAL %i MINUTE) and server_name='%s' order by 1 limit 1;" % (interval, server_name) )
        results=cursor.fetchall()
        for registry in results:
                t_created = registry[0]
                vhash = registry[1]
                encode_time = registry[2]
		vpid = registry[3]
		encode_file = registry[4]
        if vars().has_key('vhash') :
                pending_encoded_recycle=1
                return pending_encoded_recycle, t_created, vhash, encode_time, vpid, encode_file
        else :
                pending_encoded_recycle = t_created = vhash = encode_time = vpid = encode_file = 0
                return pending_encoded_recycle, t_created, vhash, encode_time, vpid, encode_file
        cursor.close ()
        db.close ()


