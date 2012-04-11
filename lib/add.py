#!/usr/bin/python
# coding: utf-8

from config import *
from common import *

import os
import MySQLdb
import datetime
import hashlib
import time
import sys
from pymediainfo import MediaInfo


"""
Brainstorming ...

ufe-add.py -site default -file /tmp/lalala.avi

better...
ufe.py -action add -site default -file /tmp/lalala.avi
 
"""

def get_site(site_name) :
        """Get site info.
        """
        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
        cursor_sites = db.cursor()
        cursor_sites.execute("select name, id, enabled, incoming_path from sites;")
        results = cursor_sites.fetchall()
        cursor_sites.close ()
        db.close ()
        for result in results :
                site_name = result[0]
		site_id = result[1]
		site_enabled = result[2]
		site_incoming_path = result[3]
	print site_name, site_id, site_enabled, site_incoming_path


def media_check(file) :
        """Checks a file with Mediainfo, to know if it is a video.
           Return isvideo, video_br, video_w, video_h, aspect_r, duration, size
        """
        logthis('Checking with MediaInfo: %s' % (file))
        media_info = MediaInfo.parse(file)
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
        print isvideo, video_br, video_w, video_h, aspect_r, duration, size





get_site('default')

media_check('/var/tmp/01.flv')
