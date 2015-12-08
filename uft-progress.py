#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# UNATTENDED FFMPEG TRANSCODER
# https://github.com/supermasita/uft
#

import re
import os
import time
from lib.common import *
from lib.config import *


#
##
###

def get_running_videos() :
    """List of vhash, vpids and filename of videos that are being encoded.
    """
    db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
    cursor = db.cursor()
    cursor.execute("SELECT vhash, vpid, encode_file from video_encoded where encode_status=2 and server_name='%s';" % server_name)
    results = cursor.fetchall()
    cursor.close()
    db.close()
    running_videos_list = []
    for registry in results :
        vhash = registry[0]
        vpid = registry[1]
        encode_file = registry[2]
        running_videos_list.append([vhash,vpid,encode_file])
    return running_videos_list

def update_encode_percent(vhash,vpid,encode_percent):
    """Updates encode_percent field of video_encoded table.
    """
    db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
    cursor = db.cursor()
    cursor.execute("UPDATE video_encoded set encode_percent='%f' where vhash='%s' and vpid=%i;" % (encode_percent, vhash, vpid))
    cursor.close()
    db.commit()
    db.close()

#
##
###

# Get video list
running_videos_list = get_running_videos()

if len(running_videos_list)>0 :
    for video in running_videos_list :
        vhash = video[0]
        vpid = video[1]
        encode_file_name, encode_file_ext = os.path.splitext(video[2])
        encode_file_log = "%s.log" % encode_file_name
        # Let parse the log
        log = open("%s/%s/%s" % (encoded, vhash, encode_file_log), "r")
        #
        for line in log:
            # frame=   29 fps=  0 q=2.6 size=     114kB time=0.79 bitrate=1181.0kbits/s
            #
            duration_re = re.compile("""Duration: (?P<duration>\S+),""")
            match = re.search(duration_re, line, re.M)
            m = re.findall(duration_re, line)
            if match is not None:
                duration = m[0]
            #
            time_done_re = re.compile("""time=(?P<time>\S+)""")
            match = re.search(time_done_re, line, re.M)
            m = re.findall(time_done_re, line)
            if match is not None:
                time_done = m[-1:][0]
                #print time_done
        log.close()

        time_done_int = float(time_done.replace(":", "").replace(".",""))
        duration_int = float(duration.replace(":", "").replace(".",""))
        encode_percent = round(float((time_done_int*100 )/duration_int),2)
        #
        update_encode_percent(vhash,vpid,encode_percent)
else :
    print "No videos running"
