#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# UNATTENDED FFMPEG TRANSCODER
# https://github.com/supermasita/uft  
# 

from lib.config import *
from lib.common import *

import ftplib
import os
import sys
import shutil

#
##
###

def select_next_ftp():
	"""Selects lists of next VHASHs ready for FTP transfer. 
	   Returns ftp_list, next_ftp_video_list .
	"""
	db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
	cursor=db.cursor()
	# Create list of FTP destinations
	cursor.execute("select id, ftp_host, ftp_user, ftp_pass, ftp_enabled, local_folder from sites;")
	results=cursor.fetchall()
	ftp_list= []
	for row in results :
                ftp_list.append(row)
        # Create list of videos to send via FTP
	cursor.execute("select video_encoded.encode_status, video_encoded.encode_file, video_encoded.vhash, video_encoded.vpid, video_encoded.ftp_path, video_encoded.site_id, video_encoded.t_created from video_encoded where video_encoded.encode_status=3 and video_encoded.ftp_status=1 and video_encoded.server_name='%s' limit 10;" % server_name )
        results=cursor.fetchall()
	next_ftp_video_list= []
	for row in results :
                next_ftp_video_list.append(row)
        cursor.close ()
        db.close ()
	return ftp_list, next_ftp_video_list


def update_ftp_status(state, u_vhash, u_vpid):
        ftp_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
	cursor=db.cursor()
	cursor.execute("update video_encoded set ftp_status=%i, ftp_time='%s' where vhash='%s' and vpid=%i ;" %  (state, ftp_time, u_vhash, u_vpid) )
	cursor.close ()
        db.commit ()
        db.close ()


#
## 
###

# Check PID file
pid = str(os.getpid())
pidfile = "%s/uft-upload.pid" % tmppath
if os.path.isfile(pidfile):
        logthis('%s already exists. The process should be running.' % pidfile)
	sys.exit()
else:
        # Create PID
	file(pidfile, 'w').write(pid)
	# Get list of videos to upload
	ftp_list, next_ftp_video_list = select_next_ftp()
	# No videos? No work!
	if len(next_ftp_video_list) < 1 :
		logthis('No videos left to upload')
	else :	
	# Oks... let's see what we have to upload
		next_ftp_video_full_list = []
		# Fill list with connection data
		for registry in next_ftp_video_list :
			encode_status = registry[0]
			encode_file = registry[1]
			vhash = registry[2]
			vpid = registry[3]
			ftp_path = registry[4]
			site_id = registry[5]
			for row in ftp_list :
				if site_id == row[0] :
					ftp_host = row[1] 
					ftp_user = row[2]
					ftp_pass = row[3]
					ftp_enabled = row[4]
					local_folder = row[5]				
					break
			next_ftp_video_full_row = encode_status, encode_file, vhash, vpid, ftp_path, site_id, ftp_host, ftp_user, ftp_pass, ftp_enabled, local_folder
			next_ftp_video_full_list.append(next_ftp_video_full_row)
		# Read list and upload
		for registry in next_ftp_video_full_list :
			encode_status = registry[0]
			encode_file = registry[1]
			vhash = registry[2]
			vpid = registry[3]
			ftp_path = registry[4]
			site_id = registry[5]
			ftp_host = registry[6]
			ftp_user = registry[7]
			ftp_pass = registry[8]
			ftp_enabled = registry[9]
			local_folder = registry[10]
			
			# Traigo el path con "/" y lo separo en año, dia y mes
			ftp_path_split = ftp_path.split('/')
			year = ftp_path_split[0]
			month = ftp_path_split[1]
			day = ftp_path_split[2]
			# Are we uploading via ftp?
			if ftp_enabled == 1 :
				# Let's try to upload some videos!
				try :
					# Open FTP
					ftp = ftplib.FTP(ftp_host, ftp_user, ftp_pass)	
					did_ftp=1
					# Update status
					update_ftp_status(2, vhash, vpid)
					# Lets make a list with the folders
					yearlist = []
					ftp.retrlines('NLST',yearlist.append)
					# Year exists?
					if year in yearlist:
						ftp.cwd(year)
						monthlist = []
						ftp.retrlines('NLST',monthlist.append)
						# Month exists? 
						if month in monthlist:
							ftp.cwd(month)
							daylist = []
							ftp.retrlines('NLST',daylist.append)
							# Day exists?
							if day in daylist: 
								ftp.cwd(day)
								vhashlist = []
								ftp.retrlines('NLST',vhashlist.append)
								# Vhash exists?
								if vhash in vhashlist:
									ftp.cwd(vhash)
								else:
									ftp.mkd(vhash)
									ftp.cwd(vhash)
							else:
								ftp.mkd(day)
								ftp.cwd(day)
								ftp.mkd(vhash)
								ftp.cwd(vhash)
						else:
							ftp.mkd(month)
							ftp.cwd(month)
							ftp.mkd(day)
							ftp.cwd(day)
							ftp.mkd(vhash)
							ftp.cwd(vhash)
					else:
						ftp.mkd(year)
						ftp.cwd(year)
						ftp.mkd(month)
						ftp.cwd(month)
						ftp.mkd(day)
						ftp.cwd(day)
						ftp.mkd(vhash)
						ftp.cwd(vhash)
					
					# Upload video 
					encode_file_name, encode_file_ext = os.path.splitext(encode_file)
					logthis('Uploading  %s/%s/%s/%s/%s' % (year, month, day, vhash, encode_file))
					ftp_file = open( '%s%s/%s' % (encoded, vhash, encode_file),'rb')
					ftp.storbinary('STOR ' + encode_file, ftp_file)
					logthis('Uploaded  %s/%s/%s/%s/%s' % (year, month, day, vhash, encode_file))
					# Upload FFMPEG log 
					encode_file_log = "%s.log" % encode_file_name
					logthis('Uploading  %s/%s/%s/%s/%s' % (year, month, day, vhash, encode_file_log))
					ftp_file_log = open( '%s%s/%s' % (encoded, vhash, encode_file_log),'rb')
					ftp.storbinary('STOR ' + encode_file_log, ftp_file_log)
					logthis('Uploaded  %s/%s/%s/%s/%s' % (year, month, day, vhash, encode_file_log))
					# Upload JSON
					try :
						encode_file_json = "%s.json" % vhash
						logthis('Uploading  %s/%s/%s/%s/%s' % (year, month, day, vhash, encode_file_json))
						ftp_file_json = open( '%s%s/%s' % (encoded, vhash, encode_file_json),'rb')
						ftp.storbinary('STOR ' + encode_file_json, ftp_file_json)
						logthis('Uploaded  %s/%s/%s/%s/%s' % (year, month, day, vhash, encode_file_json))
					except :
						pass
					# Upload thumbnail
					try :
						encode_file_thumbnail = "%s.jpg" % vhash
						logthis('Uploading  %s/%s/%s/%s/%s' % (year, month, day, vhash, encode_file_thumbnail))
						ftp_file_json = open( '%s%s/%s' % (encoded, vhash, encode_file_thumbnail),'rb')
						ftp.storbinary('STOR ' + encode_file_thumbnail, ftp_file_json)
						logthis('Uploaded  %s/%s/%s/%s/%s' % (year, month, day, vhash, encode_file_thumbnail))
					except :
						pass
					# Close FTP 
					ftp_file.close()
					# Update status
					update_ftp_status(3, vhash, vpid)
					update_vp_quantity(1, 'vp_done', vhash)
					# Did i open FTP?
					if did_ftp==1 :
						ftp.quit()
				except :
					pass
			# No FTP, moving to local directory
			else :
				# Update status
				update_ftp_status(2, vhash, vpid)	
				# Create directory if it doesnt exists
				if not os.path.exists('%s/%s/%s' % (local_folder, ftp_path, vhash)):
					os.makedirs('%s/%s/%s' % (local_folder, ftp_path, vhash))
				# Upload video
				try :
					logthis('Uploading  %s/%s/%s/%s/%s' % (year, month, day, vhash, encode_file))
					# Copy file using .part and then rename for atomic change
					# Thxs AleD!
					shutil.copy('%s%s/%s' % (encoded, vhash, encode_file), '%s/%s/%s/%s.part' % (local_folder, ftp_path, vhash, encode_file))
					shutil.move('%s/%s/%s/%s.part' % (local_folder, ftp_path, vhash, encode_file), '%s/%s/%s/%s' % (local_folder, ftp_path, vhash, encode_file))
					# Change permissions
					os.chmod('%s/%s/%s/%s' % (local_folder, ftp_path, vhash, encode_file), 0644)
					logthis('Uploaded  %s/%s/%s/%s/%s' % (year, month, day, vhash, encode_file))
				except :
					pass
				# Upload FFMPEG log
				try :
					encode_file_name, encode_file_ext = os.path.splitext(encode_file)
					encode_file_log = "%s.log" % encode_file_name	
					logthis('Uploading  %s/%s/%s/%s/%s' % (year, month, day, vhash, encode_file_log))
					shutil.copy('%s/%s/%s' % (encoded, vhash, encode_file_log), '%s/%s/%s/%s.part' % (local_folder, ftp_path, vhash, encode_file_log))
					shutil.move('%s/%s/%s/%s.part' % (local_folder, ftp_path, vhash, encode_file_log), '%s/%s/%s/%s' % (local_folder, ftp_path, vhash, encode_file_log))
					os.chmod('%s/%s/%s/%s' % (local_folder, ftp_path, vhash, encode_file_log), 0644)
					logthis('Uploaded  %s/%s/%s/%s/%s' % (year, month, day, vhash, encode_file_log))
				except :
					pass
				# Upload JSON
				try :
					encode_file_json = "%s.json" % vhash
					logthis('Uploading  %s/%s/%s/%s/%s' % (year, month, day, vhash, encode_file_json))
					shutil.copy('%s/%s/%s' % (encoded, vhash, encode_file_json), '%s/%s/%s/%s.part' % (local_folder, ftp_path, vhash, encode_file_json))
					shutil.move('%s/%s/%s/%s.part' % (local_folder, ftp_path, vhash, encode_file_json), '%s/%s/%s/%s' % (local_folder, ftp_path, vhash, encode_file_json))
					os.chmod('%s/%s/%s/%s' % (local_folder, ftp_path, vhash, encode_file_json), 0644)
					logthis('Uploaded  %s/%s/%s/%s/%s' % (year, month, day, vhash, encode_file_json))
				except :
					pass
				# Upload thumbnail
				try :
					encode_file_thumbnail = "%s.jpg" % vhash
					# Check if thumbnail has been already uploaded
					if not os.path.isfile('%s/%s/%s/%s' % (local_folder, ftp_path, vhash, encode_file_thumbnail)) :	
						logthis('Uploading  %s/%s/%s/%s/%s' % (year, month, day, vhash, encode_file_thumbnail))
						shutil.copy('%s/%s/%s' % (encoded, vhash, encode_file_thumbnail), '%s/%s/%s/%s.part' % (local_folder, ftp_path, vhash, encode_file_thumbnail))
						shutil.move('%s/%s/%s/%s.part' % (local_folder, ftp_path, vhash, encode_file_thumbnail), '%s/%s/%s/%s' % (local_folder, ftp_path, vhash, encode_file_thumbnail))
						os.chmod('%s/%s/%s/%s' % (local_folder, ftp_path, vhash, encode_file_thumbnail), 0644)
						logthis('Uploaded  %s/%s/%s/%s/%s' % (year, month, day, vhash, encode_file_thumbnail))
				except :
					pass
				# Update status
				update_ftp_status(3, vhash, vpid)
				update_vp_quantity(1, 'vp_done', vhash)
	
	# Clean PID
	os.unlink(pidfile)
