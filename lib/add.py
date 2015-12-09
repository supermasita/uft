#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# UNATTENDED FFMPEG TRANSCODER
# https://github.com/supermasita/uft
#

from config import *
from common import *
from upymediainfo import MediaInfo
from encode import create_video_json_file

import os
import MySQLdb
import datetime
import hashlib
import time
import shutil
import base64

#
##
###

def get_site(site_name) :
    """Get site info.
    """
    db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
    cursor_sites=db.cursor()
    cursor_sites.execute("select name, id, enabled, vp_priority from sites;")
    results=cursor_sites.fetchall()
    cursor_sites.close ()
    db.close ()
    for result in results :
        site_name=result[0]
        site_id=result[1]
        site_enabled=result[2]
        vp_priority=result[3]
    return site_name, site_id, site_enabled, vp_priority


def media_check(file) :
    """Checks a file with Mediainfo, to know if it is a video.
       Return isvideo, video_br, video_w, video_h, aspect_r, duration, size
    """
    logthis('Checking with MediaInfo: %s' % (file), stdout=0)
    media_info=MediaInfo.parse(file)
    # check mediainfo tracks
    for track in media_info.tracks:
        if track.track_type == 'Video':
            video_w=track.width
            video_h=track.height
            aspect_r=round(float(track.display_aspect_ratio),2)
            video_br=track.bit_rate
            video_f=track.format
        if track.track_type == 'General':
            total_br=track.overall_bit_rate
            duration=track.duration
            file_format=track.format
            size=track.file_size
        if track.track_type == 'Audio':
            audio_f=track.format
            audio_br=track.bit_rate
    # If there no video_br use the total_br
    if not vars().has_key('video_br'):
        video_br=total_br
    elif video_br is None :
        video_br=total_br
    # No audio meta?
    if not vars().has_key('audio_br'):
        audio_br=0
    elif audio_br is None :
        audio_br=0
    # No file format?
    if not vars().has_key('file_format'):
        file_format="none"
    # Check if its has overall bitrate and video width - we need it to choose video profiles
    if vars().has_key('video_br') and vars().has_key('video_w'):
        isvideo=True
    else :
        isvideo=False
        video_br, video_w, video_h, aspect_r, duration, size, total_br, audio_br=0,0,0,0,0,0,0,0
        video_f="none"
        audio_f="none"
        #
        logthis('%s : not enough metadata; %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' % (file, video_br, video_w, video_h, aspect_r, duration, size, total_br, audio_br, video_f, audio_f, file_format), stdout=0)
    return isvideo, video_br, video_w, video_h, aspect_r, duration, size, total_br, audio_br, video_f, audio_f, file_format


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
    filename_orig_n, filename_orig_e=os.path.splitext(file)
    filename_orig="%s-%s%s" % (filename_orig_n, vhash, filename_orig_e)
    # sanitize filename
    filename_san=filename_orig_n.decode("utf-8").lower()
    sanitize_list=[' ', 'ñ', '(', ')', '[', ']', '{', '}', 'á', 'é', 'í', 'ó', 'ú', '?', '¿', '!', '¡']
    for item in sanitize_list :
        filename_san=filename_san.replace(item.decode("utf-8"), '_')
    filename_san="%s-%s%s" % (filename_san[:20], vhash, filename_orig_e)
    return filename_san, filename_orig


def create_video_registry(vhash, filename_orig, filename_san, video_br, video_w, video_h, aspect_r, duration, size, site_id, server_name, total_br, audio_br, video_f, audio_f, root, file, vp_priority, file_format):
    """Creates registry in table VIDEO_ORIGINAL.
       Creates registries in table VIDEO_ENCODED according to the video profiles that match the original video.
    """
    t_created=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
    cursor=db.cursor()
    # Insert original video registry
    cursor.execute("insert into video_original set vhash='%s', filename_orig='%s', filename_san='%s', video_br=%i, video_w=%i, video_h=%i, aspect_r=%f, t_created='%s', duration=%i, size=%i, site_id=%i, server_name='%s', total_br=%i, audio_br=%i, video_f='%s', audio_f='%s', file_format='%s';" % (vhash, filename_orig, filename_san, video_br, video_w, video_h, aspect_r, t_created, duration, size, site_id, server_name, total_br, audio_br, video_f, audio_f, file_format) )
    db.commit()
    # Check profiles enabled for the site - NULL will use all profiles enabled globally
    cursor.execute("select vp_enabled from sites where id=%i;" % site_id )
    vp_enabled=cursor.fetchall()[0]
    ## Check the aspect ratio of the video and choose profiles?
    #aspect_split=1.6
    #aspect_wide=1.77
    #aspect_square=1.33
    # Choose video profile based on aspect ratio and min_video_w (TODO: check min_video_br)
    ## 4:3
    #if aspect_r <= aspect_split :
    #    if vp_enabled[0] is None :
    #        cursor.execute("select vpid, profile_name, video_br, video_w, video_f, file_format from video_profile where %i>=min_video_w and round(aspect_r,2)=%f and enabled='1';" % (video_w, aspect_square))
    #        resultado=cursor.fetchall()
    #    else :
    #        cursor.execute("select vpid, profile_name, video_br, video_w, video_f, file_format from video_profile where %i>=min_video_w and round(aspect_r,2)=%f and enabled='1' and vpid in (%s);" % (video_w, aspect_square, vp_enabled[0]) )
    #        resultado=cursor.fetchall()
    ## 16:9
    #elif aspect_r > aspect_split :
    #    if vp_enabled[0] is None :
    #        cursor.execute("select vpid, profile_name, video_br, video_w, video_f, file_format from video_profile where %i>=min_video_w and round(aspect_r,2)=%f and enabled='1';" % (video_w, aspect_wide))
    #        resultado=cursor.fetchall()
    #    else :
    #        cursor.execute("select vpid, profile_name, video_br, video_w, video_f, file_format from video_profile where %i>=min_video_w and round(aspect_r,2)=%f and enabled='1' and vpid in (%s);" % (video_w, aspect_wide, vp_enabled[0]) )
    #        resultado=cursor.fetchall()
    if vp_enabled[0] is None :
        cursor.execute("select vpid, profile_name, video_br, video_w, video_f, file_format from video_profile where %i>=min_video_w and enabled='1';" % (video_w))
        resultado=cursor.fetchall()
    else :
        cursor.execute("select vpid, profile_name, video_br, video_w, video_f, file_format from video_profile where %i>=min_video_w and enabled='1' and vpid in (%s);" % (video_w, vp_enabled[0]) )
        resultado=cursor.fetchall()
    # We create a registry for each video profile
    vp_total=0
    for registro in resultado :
        vpid=registro[0]
        profile_name=registro[1]
        vp_video_br=registro[2]
        vp_video_w=registro[3]
        vp_video_f=registro[4]
        vp_file_format=registro[5]
        # Check if vp priority according to site config
        if vp_priority == vpid :
            priority=0
        else :
            priority=10
        # Create filename for the encoded video, according to video profile
        filename_san_n, nombre_orig_e=os.path.splitext(filename_san)
        encode_file="%s-%s.mp4" % (filename_san_n, profile_name)
        # We assign an integer based on specifications of the original video and the video profile
        # in order identify which videos will be more resource intense
        weight=int((duration*(float(vp_video_br)/float(vp_video_w)))/10)
        # Timestamp
        t_created=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # Path used in FTP - we will use the date
        year=time.strftime("%Y", time.localtime())
        month=time.strftime("%m", time.localtime())
        day=time.strftime("%d", time.localtime())
        ftp_path="%s/%s/%s" % (year, month, day)
        ## Skip transcoding if the original file matches target quality
        #if (vp_video_f == video_f) and (video_br in range(vp_video_br-100000,vp_video_br+100000)) and (vp_file_format == file_format):
        #    # Add registry with encode_status as done
        #    cursor.execute("insert into video_encoded set encode_status=3, vhash='%s', vpid=%i, encode_file='%s', t_created='%s', weight=%i, ftp_path='%s', site_id=%i, server_name='%s';" % (vhash, vpid, encode_file, t_created, weight, ftp_path, site_id, server_name) )
        #    # Create directory if it doesnt exists
        #    if not os.path.exists('%s/%s' % (encoded, vhash)):
        #        os.makedirs('%s/%s' % (encoded, vhash))
        #    # Copy file with vp name
        #    shutil.copy(os.path.join(root,file), "%s/%s/%s" % (encoded, vhash, encode_file))
        #    # Create fake FFMPEG log
        #    log_filename="%s-%s.log" % (filename_san_n, profile_name)
        #    log_file=open("%s/%s/%s" % (encoded, vhash, log_filename), "w")
        #    log_file.write("File was not transcoded: original video matched profile\n")
        #    log_file.close()
        #    logthis('%s will not be transcoded: original video matched profile' % encode_file, stdout=0)
        #else:
        #    # We insert registrys for each video profile
        #    cursor.execute("insert into video_encoded set vhash='%s', vpid=%i, encode_file='%s', t_created='%s', weight=%i, ftp_path='%s', site_id=%i, server_name='%s', priority='%s';" % (vhash, vpid, encode_file, t_created, weight, ftp_path, site_id, server_name, priority) )
        cursor.execute("insert into video_encoded set vhash='%s', vpid=%i, encode_file='%s', t_created='%s', weight=%i, ftp_path='%s', site_id=%i, server_name='%s', priority='%s';" % (vhash, vpid, encode_file, t_created, weight, ftp_path, site_id, server_name, priority) )
        db.commit ()
        #
        logthis('Registry added for %s' % encode_file, stdout=0)
        # We add 1 to the total quantity of profiles for video
        vp_total=vp_total+1
    # Create json
    create_video_json_file(vhash)
    # Update the total quantity of profiles for video
    cursor.execute("update video_original set vp_total=%i where vhash='%s';" % (vp_total, vhash) )
    db.commit ()
    cursor.close ()
    db.close ()

def create_nonvideo_registry(vhash, filename_orig, filename_san, site_id, server_name ):
    """Creates registry in table VIDEO_ORIGINAL for a file that is not a video
       or is a video with insufficiente METADATA.
    """
    t_created=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
    cursor=db.cursor()
    # Insert original video registry
    cursor.execute("insert into video_original set vhash='%s', filename_orig='%s', filename_san='%s', t_created='%s', site_id=%i, server_name='%s';" % (vhash, filename_orig, filename_san, t_created, site_id, server_name) )
    db.commit()
    cursor.close ()
    db.close ()


def move_original_file(root, file, filename_san) :
    """Moves original video file from video_origin folder to video_original folder.
    """
    # Create directory for original videos
    if not os.path.exists(original):
        os.makedirs(original)
    # We use shutil to be able to move files from different filesystems
    shutil.move(os.path.join(root,file), original+filename_san)



def create_thumbnail_blob(vhash, filename_san) :
    """Creates thumbail (80x60px) from original video and stores it video original db table as a blob.
       Thumbnail is taken at 00:00:02 (second video frame).
    """
    filename_san_n, filename_san_e=os.path.splitext(filename_san)
    source="%s/%s" % (original, filename_san)
    destination="%s/%s.jpg" % (original, filename_san_n)
    command='%s -itsoffset -2 -i %s -vcodec mjpeg -vframes 1 -an -f rawvideo -s 80x60 %s -y' % (ffmpeg_bin, source, destination)
    try :
        commandlist=command.split(" ")
        output=subprocess.call(commandlist, stdout=open('/dev/null', 'w'), stderr=subprocess.STDOUT)
    except :
        output=1
        pass

    if output == 0 :
        # Insert into blob
        thumbnail=open(destination, 'rb')
        thumbnail_blob=base64.b64encode(thumbnail.read())
        thumbnail.close()
        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
        cursor=db.cursor()
        cursor.execute("UPDATE video_original SET thumbnail_blob='%s' WHERE vhash='%s';" % (MySQLdb.escape_string(thumbnail_blob), vhash) )
        cursor.close()
        db.commit()
        db.close()
        # Remove thumbnail file
        os.unlink(destination)



def create_thumbnail(vhash, filename_san) :
    """Creates thumbail from original video and stores it with the encoded videos.
       Thumbnail is taken at 00:00:02 (second video frame).
    """
    filename_san_n, filename_san_e=os.path.splitext(filename_san)
    source="%s/%s" % (original, filename_san)
    destination="%s/%s/%s.jpg" % (encoded, vhash, vhash)
    command='%s -itsoffset -2 -i %s -vcodec mjpeg -vframes 1 -an -f rawvideo -s %sx%s %s -y' % (ffmpeg_bin, source, thumbnail_width, thumbnail_height, destination)
    try :
        commandlist=command.split(" ")
        output=subprocess.call(commandlist, stdout=open('/dev/null', 'w'), stderr=subprocess.STDOUT)
    except :
        output=1
        pass
