#!/usr/bin/python
# coding: utf-8
#
# UNATTENDED FFMPEG ENCODER
# https://github.com/supermasita/ufe  
# 

from lib.config import *
from lib.common import *

import ftplib
import os
import sys

def select_next_ftp():
	"""Selects lists of next VHASHs ready for FTP transfer. 
	   Returns ftp_list, next_ftp_video_list .
	"""
	db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
	cursor=db.cursor()
	# Create list of FTP destinations
	cursor.execute("select sites.id, sites.ftp_host, sites.ftp_user, sites.ftp_pass from sites;")
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



############################################################################



# Check PID file
pid = str(os.getpid())
pidfile = "%s/ftp.pid" % tmppath
if os.path.isfile(pidfile):
        logthis('%s already exists. The process should be running.' % pidfile)
	sys.exit()
else:
        # Create PID
	file(pidfile, 'w').write(pid)
	# Get list of videos to upload
	ftp_list, next_ftp_video_list = select_next_ftp()
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
                                break
		next_ftp_video_full_row = encode_status, encode_file, vhash, vpid, ftp_path, site_id, ftp_host, ftp_user, ftp_pass
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
		# Let's try to upload some videos!
		try :
			# Open FTP
			ftp = ftplib.FTP(ftp_host, ftp_user, ftp_pass)	
			did_ftp=1
			# Actualizo estado
			update_ftp_status(2, vhash, vpid)
			# Traigo el path con "/" y lo separo en año, dia y mes
			ftp_path_split=ftp_path.split('/')
			year=ftp_path_split[0]
			month=ftp_path_split[1]
			day=ftp_path_split[2]
			# Busco si existe la carpeta del año
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
			# 
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
			if create_video_json is True :
				try :
					encode_file_json = "%s.json" % vhash
	       	 	                logthis('Uploading  %s/%s/%s/%s/%s' % (year, month, day, vhash, encode_file_json))
		                        ftp_file_json = open( '%s%s/%s' % (encoded, vhash, encode_file_json),'rb')
		                        ftp.storbinary('STOR ' + encode_file_json, ftp_file_json)
	        	                logthis('Uploaded  %s/%s/%s/%s/%s' % (year, month, day, vhash, encode_file_json))
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
	# Clean PID
	os.unlink(pidfile)
