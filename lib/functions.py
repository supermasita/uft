#!/usr/bin/python
# coding: utf-8

#from config import *
#from common import *
#import os
#import MySQLdb
#import time
#import datetime
#import random
#import subprocess
#import syslog
#import hashlib
#from pymediainfo import MediaInfo


#def logthis(message) :
#        """Writes message to SYSLOG and prints it to STDOUT.
#        """
#        syslog.syslog(syslog.LOG_INFO, '%s' % message )
#        print "%s" % message


#def random_wait() :
#	"""Random wait (ms).
#	"""
#	random.seed()
#	n = random.random()
#	time.sleep(n)


#def select_sites() :
#	"""Selects enabled sites and their incoming paths.
#	   Returns nested list.
#	"""
#        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
#        cursor_sites=db.cursor()
#        cursor_sites.execute("select incoming_path, name, id from sites where enabled=1;")
#        results_sites=cursor_sites.fetchall()
#        cursor_sites.close ()
#        db.close ()
#        sites_list = []
#        for row in results_sites :
#                sites_list.append(row)
#	return sites_list


#def create_video_registry(c_vhash, c_filename_orig, c_filename_san, c_video_br, c_video_w, c_video_h, c_aspect_r, c_duration, c_size, c_site_id, c_server_name ):
#	"""Creates registry in table VIDEO_ORIGINAL. 
#	   Creates registries in table VIDEO_ENCODED according to the video profiles that match the original video. 
#	"""
#	t_created = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#	db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
#	cursor=db.cursor()
#	# Insert original video registry
#	cursor.execute("insert into video_original set vhash='%s', filename_orig='%s', filename_san='%s', video_br=%i, video_w=%i, video_h=%i, aspect_r=%f, t_created='%s', duration=%i, size=%i, site_id=%i, server_name='%s';" % (c_vhash, c_filename_orig, c_filename_san, c_video_br, c_video_w, c_video_h, c_aspect_r, t_created, c_duration, c_size, c_site_id, c_server_name ) )
#	db.commit()
#	# Check profiles enabled for the site - NULL will use all profiles enabled globally
#	cursor.execute("select vp_enabled from sites where id=%i;" % c_site_id )
#	vp_enabled=cursor.fetchall()[0]
#	# Check the aspect ratio of the video and choose profiles?
#	aspect_split=1.6
#	aspect_wide=1.77
#	aspect_square=1.33
#	if c_aspect_r <= aspect_split :
#		if vp_enabled[0] is None :
#                	cursor.execute("select vpid, profile_name, bitrate, width from video_profile where %i>=min_width and round(aspect_r,2)=%f and enabled='1';" % (c_video_w, aspect_square))
#                	resultado=cursor.fetchall()
#        	else :
#                	cursor.execute("select vpid, profile_name, bitrate, width from video_profile where %i>=min_width and round(aspect_r,2)=%f and enabled='1' and vpid in (%s);" % (c_video_w, aspect_square, vp_enabled[0]) )
#                	resultado=cursor.fetchall()
#	elif c_aspect_r > aspect_split :
#                if vp_enabled[0] is None :
#                        cursor.execute("select vpid, profile_name, bitrate, width from video_profile where %i>=min_width and round(aspect_r,2)=%f and enabled='1';" % (c_video_w, aspect_wide))
#			resultado=cursor.fetchall()
#                else :
#                        cursor.execute("select vpid, profile_name, bitrate, width from video_profile where %i>=min_width and round(aspect_r,2)=%f and enabled='1' and vpid in (%s);" % (c_video_w, aspect_wide, vp_enabled[0]) )
#			resultado=cursor.fetchall()
#	# We create a registry for each video profile
#	vp_total=0
#	for registro in resultado :
#		vpid = registro[0]
#		profile_name = registro[1]
#		bitrate = registro[2]
#		width = registro[3]
#		# Create filename for the encoded video, according to video profile
#		filename_san_n, nombre_orig_e = os.path.splitext(c_filename_san)
#		encode_file = "%s-%s.mp4" % (filename_san_n, profile_name)
#		# We assign an integer based on specifications of the original video and the video profile
#		# in order identify which videos will be more resource intense
#		weight=int((c_duration*(float(bitrate)/float(width)))/10)
#		# Timestamp                             
#		t_created = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#		# Path used in FTP - we will use the date
#                year = time.strftime("%Y", time.localtime())
#                month = time.strftime("%m", time.localtime())
#                day = time.strftime("%d", time.localtime())
#		c_ftp_path="%s/%s/%s" % (year, month, day)
#		# We insert registrys for each video profile
#                cursor.execute("insert into video_encoded set vhash='%s', vpid=%i, encode_file='%s', t_created='%s', weight=%i, ftp_path='%s', site_id=%i, server_name='%s';" % (c_vhash, vpid, encode_file, t_created, weight, c_ftp_path, c_site_id, c_server_name) )
#		db.commit ()
#		logthis('Registry added for %s' % encode_file)	
#		# We add 1 to the total quantity of profiles for video
#		vp_total=vp_total+1
#        # Update the total quantity of profiles for video
#	cursor.execute("update video_original set vp_total=%i where vhash='%s';" % (vp_total, c_vhash) )
#	db.commit ()
#	cursor.close ()
#	db.close ()

#def update_running_ps(operation):
#        """Adds/Substracts 1 to/from running_ps for the given server_name.
#        """
#        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
#        cursor=db.cursor()
#	if operation == "add" :
#        	cursor.execute("update servers set running_ps=running_ps+1 where name='%s';" % server_name )
#        elif operation == "substract" :
#		cursor.execute("update servers set running_ps=running_ps-1 where name='%s';" % server_name )
#	cursor.close ()
#        db.commit ()
#        db.close ()


#def check_running_ps():
#	"""Checks how many processes are running for a given server_name.
#	   Returns max_ps_reached (int. binary)
#	"""
#        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
#        cursor=db.cursor()
#        cursor.execute("select servers_id, name, role, enabled, handicap, running_ps, max_ps from servers where name='%s';" % server_name )
#        results=cursor.fetchall()
#        cursor.close ()
#        db.close ()
#	for registry in results:
#                servers_id=registry[0]
#                name=registry[1]
#                role=registry[2]
#                enabled=registry[3]
#                handicap=registry[4]
#                running_ps=registry[5]
#                max_ps=registry[6]
#        if running_ps>=max_ps :
#                max_ps_reached=1
#        else :
#                max_ps_reached=0
#	return max_ps_reached


#def select_next_encode():
#        """Selects next video to encode.
#           Returns pending_encode, vhash, vpid, encode_status, filename_san, encode_file, param.
#        """
#        random_wait()
#	db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
#	# We check if there already is a VP running for the VHASH. We exclude this VHASH from the choice of next encode.
#	cursor=db.cursor()
#        cursor.execute("select video_encoded.vhash from video_encoded where video_encoded.encode_status=2 and video_encoded.server_name='%s';" % server_name )
#	results=cursor.fetchall()
#	# We create a string to use as "NOT IN"	in the query
#	skip_vhash=""
#	for row in results :
#		skip_vhash=skip_vhash+"'"+row[0]+"'"+","
#	skip_vhash=skip_vhash[:-1]			
#	# No VP running? We choose any VHASH. Else, use "NOT IN"
#	if len(skip_vhash) == 0 :
#		cursor.execute("select video_encoded.vhash, video_encoded.vpid, video_encoded.encode_status, video_encoded.encode_file from video_encoded where video_encoded.encode_status=1 and video_encoded.server_name='%s' order by video_encoded.weight limit 1;" % server_name )
#	else :
#		cursor.execute("select video_encoded.vhash, video_encoded.vpid, video_encoded.encode_status, video_encoded.encode_file from video_encoded where video_encoded.encode_status=1 and video_encoded.server_name='%s' and video_encoded.vhash not in (%s) order by video_encoded.weight limit 1;" % (server_name, skip_vhash) )
#	results=cursor.fetchall()
#	# Any videos pending?
#	for registry in results:
#                #print registry
#		vhash=registry[0]
#                vpid=registry[1]
#                encode_status=registry[2]
#                encode_file=registry[3]
#	if vars().has_key('vhash') :
#                # get the original filename
#                cursor.execute("select video_original.filename_san from video_original where vhash='%s';" % vhash )
#                results=cursor.fetchall()
#		for registry in results:
#                        filename_san=registry[0]
#                # get the video profile parameters
#                cursor.execute("select video_profile.param_ffmpeg from video_profile where vpid=%i;" % vpid )
#                results=cursor.fetchall()
#                for registry in results:
#                        param=registry[0]
#		# set pending_encode as true (1)
#		pending_encode=1
#        else :
#                pending_encode = vhash = vpid = encode_status = filename_san = encode_file = param = 0
#        cursor.close ()
#	db.close ()
#	return pending_encode, vhash, vpid, encode_status, filename_san, encode_file, param


#def select_next_ftp():
#	"""Selects lists of next VHASHs ready for FTP transfer. 
#	   Returns ftp_list, next_ftp_video_list .
#	"""
#	db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
#	cursor=db.cursor()
#	# Create list of FTP destinations
#	cursor.execute("select sites.id, sites.ftp_host, sites.ftp_user, sites.ftp_pass from sites;")
#	results=cursor.fetchall()
#	ftp_list= []
#	for row in results :
#                ftp_list.append(row)
#        # Create list of videos to send via FTP
#	cursor.execute("select video_encoded.encode_status, video_encoded.encode_file, video_encoded.vhash, video_encoded.vpid, video_encoded.ftp_path, video_encoded.site_id, video_encoded.t_created from video_encoded where video_encoded.encode_status=3 and video_encoded.ftp_status=1 and video_encoded.server_name='%s' limit 10;" % server_name )
#        results=cursor.fetchall()
#	next_ftp_video_list= []
#	for row in results :
#                next_ftp_video_list.append(row)
#        cursor.close ()
#        db.close ()
#	return ftp_list, next_ftp_video_list
#

#def recycle_old_registers():
#        """Removes registers from DB of videos that have already been recycled.
#	"""
#	db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
#        cursor=db.cursor()
#        cursor.execute("SELECT vhash from video_original where server_name='%s' and recycle_status=3 and t_created < DATE_SUB(current_timestamp(), INTERVAL 48 HOUR);" % server_name )
#        results=cursor.fetchall()
#	cursor.close ()
#	# Any results?
#	if len(results) > 0 :
#		for registry in results:
#			vhash = registry[0]
#			cursor_vhash=db.cursor()
#			cursor_vhash.execute("delete from video_original where vhash='%s';" % vhash )
#			cursor_vhash.execute("delete from video_encoded where vhash='%s';" % vhash )
#			db.commit()
#			cursor_vhash.close()
#			logthis('Deleted all registers for vhash: %s' % vhash)
#	else :
#		print "There are no old registers to delete."
#        db.close ()
#
#
#def select_next_encoded_recycle():
#	"""Finds already uploaded encoded videos and deletes them.
#	"""
#        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
#        cursor=db.cursor()
#        cursor.execute("select t_created, vhash, encode_time, vpid, encode_file from video_encoded where recycle_status=1 and ftp_status=3 and encode_status=3 and ftp_time < DATE_SUB(current_timestamp(), INTERVAL 30 MINUTE) and server_name='%s' order by 1 limit 1;" % server_name )
#        results=cursor.fetchall()
#        for registry in results:
#                t_created = registry[0]
#                vhash = registry[1]
#                encode_time = registry[2]
#		vpid = registry[3]
#		encode_file = registry[4]
#        if vars().has_key('vhash') :
#                pending_encoded_recycle=1
#                return pending_encoded_recycle, t_created, vhash, encode_time, vpid, encode_file
#        else :
#                pending_encoded_recycle = t_created = vhash = encode_time = vpid = encode_file = 0
#                return pending_encoded_recycle, t_created, vhash, encode_time, vpid, encode_file
#        cursor.close ()
#        db.close ()
#
#
#def select_next_original_recycle():
#	"""Finds original videos whose encoded videos have been already recycled and deletes them.
#	"""
#        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
#        cursor=db.cursor()
#        cursor.execute("select vhash, filename_san, vp_total from video_original where vp_total=vp_done and recycle_status=1 and server_name='%s' order by 1 limit 10;" % server_name )
#        results=cursor.fetchall()
#	pending_video_list = list()
#	lista_vhash = list()	
#	pending_original_recycle=0
#	for registry in results:
#		vhash = registry[0]
#		filename_san = registry[1]
#		vp_total = registry[2]
#		lista_vhash.append([vhash, filename_san])
#	if vars().has_key('vhash') :	
#		for registry in lista_vhash :			
#			lvhash = registry[0]
#			lfilename_san = registry[1]
#			cursor.execute("select count(*) from video_encoded where vhash='%s' and recycle_status=3;" % lvhash )
#			results2=cursor.fetchall()
#			if vp_total==results2[0][0] :
#				pending_video = [lvhash, lfilename_san]
#				pending_video_list.append(pending_video)
#				pending_original_recycle=1	
#	else :
#        	pending_original_recycle = pending_video_list = 0
#	cursor.close ()
#        db.close ()
#	return pending_original_recycle, pending_video_list
#
#
#def update_encoded_recycle_status(state, u_vhash, u_vpid):
#	"""Updates the recycled status of a encoded video.
#	"""
#        recycle_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
#        cursor=db.cursor()
#        cursor.execute("update video_encoded set recycle_status=%i, recycle_time='%s' where vhash='%s' and vpid=%i;" %  (state, recycle_time, u_vhash, u_vpid) )
#        cursor.close ()
#        db.commit ()
#        db.close ()
#
#
#def update_original_recycle_status(state, u_vhash):
#	""" Updates de encoded status of a original video.
#	"""
#        recycle_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
#        cursor=db.cursor()
#        cursor.execute("update video_original set recycle_status='%i', recycle_time='%s' where vhash='%s' ;" %  (state, recycle_time, u_vhash) )
#        cursor.close ()
#        db.commit ()
#        db.close ()
#
#
#def update_encode_status(state, u_vhash, u_vpid):
#	"""Updates the encoded status of a video the table "video_encoded".
#	"""
#	encode_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
#	cursor=db.cursor()
#	cursor.execute("update video_encoded set encode_status=%i, encode_time='%s' where vhash='%s' and vpid=%i ;" %  (state, encode_time, u_vhash, u_vpid) )
#        cursor.close ()
#        db.commit ()
#        db.close ()
#
#
#def update_vp_quantity(u_quantity, u_vp_status, u_vhash):
#	"""Increments or decrements the total of video profiles with for the vhash on the video_original table.
#	"""
#	status_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
#        cursor=db.cursor()
#        cursor.execute("update video_original set %s=%s+(%i), status_time='%s' where vhash='%s';" %  (u_vp_status, u_vp_status, u_quantity, status_time, u_vhash) )
#        cursor.close ()
#        db.commit ()
#        db.close ()
#
#
#def update_ftp_status(state, u_vhash, u_vpid):
#        ftp_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
#	cursor=db.cursor()
#	cursor.execute("update video_encoded set ftp_status=%i, ftp_time='%s' where vhash='%s' and vpid=%i ;" %  (state, ftp_time, u_vhash, u_vpid) )
#	cursor.close ()
#        db.commit ()
#        db.close ()
#

#def encode_video_ffmpeg(e_vhash, e_vpid, e_filename_san, e_encode_file, e_param) :
#        """Encodes video with FFMPEG.
#           Returns integer - STDOUT status.
#        """
#        update_encode_status(2, e_vhash, e_vpid)
#	update_vp_quantity(1, 'vp_run', e_vhash) 
#	# Create folder for vhash
#        if not os.path.exists('%s%s' % (encoded, e_vhash)):
#                os.makedirs('%s%s' % (encoded, e_vhash))
#        # Source and destination for FFMPEG
#        source = "%s%s" % (original, e_filename_san)
#        destination = "%s%s/%s" % (encoded, e_vhash, e_encode_file)
#	# Log path and filename 
#	e_encode_file_name, e_encode_file_e = os.path.splitext(e_encode_file)
#	e_encode_file_log = "%s%s/%s.log" % (encoded, e_vhash, e_encode_file_name)
#	# FFMPEG command
#	command='%s -i %s %s %s' % (ffmpeg_bin, source, e_param, destination)
#	try :
#		# Arguments to list in order to use subprocess
#        	commandlist=command.split(" ")
#        	encode_log_file = open(e_encode_file_log,"wb")
#		output = subprocess.call(commandlist, stderr=encode_log_file, stdout=encode_log_file)
#	except :
#		output = 1
#		pass
#        # Check command output
#        if output != 0 :
#                update_encode_status(4, e_vhash, e_vpid)
#		update_vp_quantity(-1, 'vp_run', e_vhash)
#		update_vp_quantity(1, 'vp_error', e_vhash)
#		logthis('Error while trying to encode %s' % e_encode_file)
#	else :
#                # We use qt-faststart for hinting
#		command = '%slib/qt-faststart.py "%s"' % (core_root, destination)
#		output = subprocess.call(commandlist)
#		#print "qt outputs %i" % output
#		#
#		update_encode_status(3, e_vhash, e_vpid)
#		update_vp_quantity(-1, 'vp_run', e_vhash)
#                logthis('%s successfully encoded' % e_encode_file)
#        return output


#def create_vhash(c_file, c_site_name) :	
#	"""Creates hash for video from filename and site name.
#	   Returns vhash (string).
#	"""
#	vhash_full=hashlib.sha1(str(time.time())+c_file+server_name+c_site_name).hexdigest()
#	vhash=vhash_full[:10]
#	return vhash
#

#def create_filename_san(file, vhash) :
#	"""Creates a sanitized and timestamped filename from the original filename.
#	   Returns filename_san (string) and filename_orig (string).
#	"""
#	filename_orig_n, filename_orig_e = os.path.splitext(file)
#	filename_orig = "%s-%s%s" % (filename_orig_n, vhash, filename_orig_e)
#	# sanitize filename
#	filename_san = filename_orig_n.decode("utf-8").lower()
#	sanitize_list = [' ', 'ñ', '(', ')', '[', ']', '{', '}', 'á', 'é', 'í', 'ó', 'ú', '?', '¿', '!', '¡']
#	for item in sanitize_list :
#		filename_san = filename_san.replace(item.decode("utf-8"), '_')
#	filename_san = "%s-%s%s" % (filename_san, vhash, filename_orig_e)	
#	return filename_san, filename_orig
#
#
#def create_thumbnail(vhash, filename_san) :
#	"""Creates thumbail (80x60px) from original video and stores it video original db table as a blob.
#	   Thumbnail is taken at 00:00:02 of the video.
#	"""
#	filename_san_n, filename_san_e = os.path.splitext(filename_san)
#	source = "%s/%s" % (original, filename_san)
#	destination = "%s/%s.jpg" % (original, filename_san_n)
#	command = '%s -itsoffset -2 -i %s -vcodec mjpeg -vframes 1 -an -f rawvideo -s 80x60 %s -y' % (ffmpeg_bin, source, destination)
#	try :
#		commandlist = command.split(" ")
#		output = subprocess.call(commandlist)
#        except :
#                output = 1
#                pass
#
#	if output == 0 :
#		# Insert into blob
#		thumbnail = open(destination, 'rb')
#		thumbnail_blob = repr(thumbnail.read())
#		thumbnail.close()
#		db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
#		cursor = db.cursor()
#		cursor.execute("UPDATE video_original SET thumbnail_blob='%s' WHERE vhash='%s';" % (MySQLdb.escape_string(thumbnail_blob), vhash) )
#		cursor.close()
#		db.commit()
#		db.close()
#		# Remove thumbnail file
#		os.unlink(destination)
#
#
#def move_original_file(root, file, filename_san):
#	"""Moves original video file from video_origin folder to video_original folder.
#	"""
#	os.rename(os.path.join(root,file), original+filename_san)
#
#
#def media_check(site_path, file) :
#	"""Checks a file with Mediainfo, to know if it is a video.
#	   Return isvideo, video_br, video_w, video_h, aspect_r, duration, size
#	"""
#	logthis('Checking with MediaInfo: %s/%s/%s' % (incoming, site_path, file))	
#	media_info = MediaInfo.parse('%s/%s/%s' % (incoming, site_path, file) )
#	# check mediainfo tracks
#	for track in media_info.tracks:
#		if track.track_type == 'Video':
#			video_w = track.width
#			video_h = track.height
#			aspect_r = round(float(track.display_aspect_ratio),2)
#		if track.track_type == 'General':
#			video_br = track.overall_bit_rate
#			duration = track.duration
#			size = track.file_size
#	# check if its has overall bitrate and video width - we need it to choose video profiles	
#	if vars().has_key('video_br') and vars().has_key('video_w'):
#		isvideo = True
#	else :
#		isvideo, video_br, video_w, video_h, aspect_r, duration, size = False
#	return isvideo, video_br, video_w, video_h, aspect_r, duration, size
#
#def spawn_process(process) :
#	"""Spawns a process like encode.py or ftp.py. It does not wait for the spawned process to finish.
#	"""
#	if process=="encode":
#		pid = subprocess.Popen(["%s/ufe-encode.py" % core_root]).pid		
#		logthis('Spawned %s with PID %i' % (process, pid))
#	elif process=="ftp":
#		pid = subprocess.Popen(["%s/ufe-ftp.py" % core_root]).pid
#		logthis('Spawned %s with PID %i' % (process, pid))
#	else:
#		logthis('No process named %s !' % process)
