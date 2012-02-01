#!/usr/bin/python
# coding: utf-8

from config import *
from common import *
import os
import MySQLdb
import datetime
import hashlib
from pymediainfo import MediaInfo

def select_sites() :
	"""Selects enabled sites and their incoming paths.
	   Returns nested list.
	"""
        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
        cursor_sites=db.cursor()
        cursor_sites.execute("select incoming_path, name, id from sites where enabled=1;")
        results_sites=cursor_sites.fetchall()
        cursor_sites.close ()
        db.close ()
        sites_list = []
        for row in results_sites :
                sites_list.append(row)
	return sites_list


def media_check(site_path, file) :
	"""Checks a file with Mediainfo, to know if it is a video.
	   Return isvideo, video_br, video_w, video_h, aspect_r, duration, size
	"""
	print "loooo"
	logthis('Checking with MediaInfo: %s/%s/%s' % (incoming, site_path, file))	
	media_info = MediaInfo.parse('%s/%s/%s' % (incoming, site_path, file) )
	print '%s/%s/%s' % (incoming, site_path, file)
	# check mediainfo tracks
	for track in media_info.tracks:
		if track.track_type == 'Video':
			video_w = track.width
			video_h = track.height
			aspect_r = round(float(track.display_aspect_ratio),2)
		if track.track_type == 'General':
			video_br = track.overall_bit_rate
			duration = track.duration
			size = track.file_size
	# check if its has overall bitrate and video width - we need it to choose video profiles	
	if vars().has_key('video_br') and vars().has_key('video_w'):
		isvideo = True
	else :
		isvideo, video_br, video_w, video_h, aspect_r, duration, size = False
	return isvideo, video_br, video_w, video_h, aspect_r, duration, size


def create_vhash(c_file, c_site_name) :	
	"""Creates hash for video from filename and site name.
	   Returns vhash (string).
	"""
	vhash_full=hashlib.sha1(str(time.time())+c_file+server_name+c_site_name).hexdigest()
	vhash=vhash_full[:10]
	return vhash



def create_filename_san(file, vhash) :
	"""Creates a sanitized and timestamped filename from the original filename.
	   Returns filename_san (string) and filename_orig (string).
	"""
	filename_orig_n, filename_orig_e = os.path.splitext(file)
	filename_orig = "%s-%s%s" % (filename_orig_n, vhash, filename_orig_e)
	# sanitize filename
	filename_san = filename_orig_n.decode("utf-8").lower()
	sanitize_list = [' ', 'ñ', '(', ')', '[', ']', '{', '}', 'á', 'é', 'í', 'ó', 'ú', '?', '¿', '!', '¡']
	for item in sanitize_list :
		filename_san = filename_san.replace(item.decode("utf-8"), '_')
	filename_san = "%s-%s%s" % (filename_san, vhash, filename_orig_e)	
	return filename_san, filename_orig



def create_video_registry(c_vhash, c_filename_orig, c_filename_san, c_video_br, c_video_w, c_video_h, c_aspect_r, c_duration, c_size, c_site_id, c_server_name ):
	"""Creates registry in table VIDEO_ORIGINAL. 
	   Creates registries in table VIDEO_ENCODED according to the video profiles that match the original video. 
	"""
	t_created = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
	cursor=db.cursor()
	# Insert original video registry
	cursor.execute("insert into video_original set vhash='%s', filename_orig='%s', filename_san='%s', video_br=%i, video_w=%i, video_h=%i, aspect_r=%f, t_created='%s', duration=%i, size=%i, site_id=%i, server_name='%s';" % (c_vhash, c_filename_orig, c_filename_san, c_video_br, c_video_w, c_video_h, c_aspect_r, t_created, c_duration, c_size, c_site_id, c_server_name ) )
	db.commit()
	# Check profiles enabled for the site - NULL will use all profiles enabled globally
	cursor.execute("select vp_enabled from sites where id=%i;" % c_site_id )
	vp_enabled=cursor.fetchall()[0]
	# Check the aspect ratio of the video and choose profiles?
	aspect_split=1.6
	aspect_wide=1.77
	aspect_square=1.33
	if c_aspect_r <= aspect_split :
		if vp_enabled[0] is None :
                	cursor.execute("select vpid, profile_name, bitrate, width from video_profile where %i>=min_width and round(aspect_r,2)=%f and enabled='1';" % (c_video_w, aspect_square))
                	resultado=cursor.fetchall()
        	else :
                	cursor.execute("select vpid, profile_name, bitrate, width from video_profile where %i>=min_width and round(aspect_r,2)=%f and enabled='1' and vpid in (%s);" % (c_video_w, aspect_square, vp_enabled[0]) )
                	resultado=cursor.fetchall()
	elif c_aspect_r > aspect_split :
                if vp_enabled[0] is None :
                        cursor.execute("select vpid, profile_name, bitrate, width from video_profile where %i>=min_width and round(aspect_r,2)=%f and enabled='1';" % (c_video_w, aspect_wide))
			resultado=cursor.fetchall()
                else :
                        cursor.execute("select vpid, profile_name, bitrate, width from video_profile where %i>=min_width and round(aspect_r,2)=%f and enabled='1' and vpid in (%s);" % (c_video_w, aspect_wide, vp_enabled[0]) )
			resultado=cursor.fetchall()
	# We create a registry for each video profile
	vp_total=0
	for registro in resultado :
		vpid = registro[0]
		profile_name = registro[1]
		bitrate = registro[2]
		width = registro[3]
		# Create filename for the encoded video, according to video profile
		filename_san_n, nombre_orig_e = os.path.splitext(c_filename_san)
		encode_file = "%s-%s.mp4" % (filename_san_n, profile_name)
		# We assign an integer based on specifications of the original video and the video profile
		# in order identify which videos will be more resource intense
		weight=int((c_duration*(float(bitrate)/float(width)))/10)
		# Timestamp                             
		t_created = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
		# Path used in FTP - we will use the date
                year = time.strftime("%Y", time.localtime())
                month = time.strftime("%m", time.localtime())
                day = time.strftime("%d", time.localtime())
		c_ftp_path="%s/%s/%s" % (year, month, day)
		# We insert registrys for each video profile
                cursor.execute("insert into video_encoded set vhash='%s', vpid=%i, encode_file='%s', t_created='%s', weight=%i, ftp_path='%s', site_id=%i, server_name='%s';" % (c_vhash, vpid, encode_file, t_created, weight, c_ftp_path, c_site_id, c_server_name) )
		db.commit ()
		logthis('Registry added for %s' % encode_file)	
		# We add 1 to the total quantity of profiles for video
		vp_total=vp_total+1
        # Update the total quantity of profiles for video
	cursor.execute("update video_original set vp_total=%i where vhash='%s';" % (vp_total, c_vhash) )
	db.commit ()
	cursor.close ()
	db.close ()



def create_thumbnail(vhash, filename_san) :
	"""Creates thumbail (80x60px) from original video and stores it video original db table as a blob.
	   Thumbnail is taken at 00:00:02 of the video.
	"""
	filename_san_n, filename_san_e = os.path.splitext(filename_san)
	source = "%s/%s" % (original, filename_san)
	destination = "%s/%s.jpg" % (original, filename_san_n)
	command = '%s -itsoffset -2 -i %s -vcodec mjpeg -vframes 1 -an -f rawvideo -s 80x60 %s -y' % (ffmpeg_bin, source, destination)
	try :
		commandlist = command.split(" ")
		output = subprocess.call(commandlist)
        except :
                output = 1
                pass

	if output == 0 :
		# Insert into blob
		thumbnail = open(destination, 'rb')
		thumbnail_blob = repr(thumbnail.read())
		thumbnail.close()
		db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
		cursor = db.cursor()
		cursor.execute("UPDATE video_original SET thumbnail_blob='%s' WHERE vhash='%s';" % (MySQLdb.escape_string(thumbnail_blob), vhash) )
		cursor.close()
		db.commit()
		db.close()
		# Remove thumbnail file
		os.unlink(destination)




def move_original_file(root, file, filename_san):
	"""Moves original video file from video_origin folder to video_original folder.
	"""
	os.rename(os.path.join(root,file), original+filename_san)








