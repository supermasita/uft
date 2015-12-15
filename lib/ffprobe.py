#!/usr/bin/python
# -*- coding: utf-8 -*-

# ffprobe -v quiet -print_format json -show_format -show_streams test.mp4
# isvideo, video_br, video_w, video_h, aspect_r, duration, size, total_br, audio_br, video_f, audio_f, file_format

from __future__ import division
from subprocess import Popen, PIPE
import os, sys
import simplejson as json
import getopt


def video_meta(stream_number,data):
    codec_type = data["streams"][stream_number]["codec_type"]
    video_br = data["streams"][stream_number]["bit_rate"]
    video_w = data["streams"][stream_number]["width"]
    video_h = data["streams"][stream_number]["height"]
    #aspect_r = data["streams"][stream_number]["display_aspect_ratio"]
    aspect_r = "%.2f" % (video_w/video_h)
    video_f = data["streams"][stream_number]["codec_name"]
    duration = data["format"]["duration"]
    size = data["format"]["size"]
    duration = data["format"]["duration"]
    total_br = data["format"]["bit_rate"]
    file_format = data["format"]["format_name"]

    return codec_type, video_br, video_w, video_h, aspect_r, video_f, duration, size, duration, total_br, file_format


def audio_meta(stream_number,data):
    codec_type = data["streams"][stream_number]["codec_type"]
    audio_br = data["streams"][stream_number]["bit_rate"]
    audio_f = data["streams"][stream_number]["codec_name"]

    return codec_type, audio_br, audio_f


def media_check(filename):
    """Checks a file with Mediainfo, to know if it is a video.
       Return isvideo, video_br, video_w, video_h, aspect_r, duration, size
    """
    #logthis('Checking with MediaInfo: %s' % (filename), stdout=0)
    command = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", filename]
    p = Popen(command, stdout=PIPE)
    p.wait()
 
    data = json.loads(p.stdout.read())
    p.stdout.close()
    


    try:
        if data["streams"][0]["codec_type"] == "video":
            codec_type, video_br, video_w, video_h, aspect_r, video_f, duration, size, duration, total_br, file_format = video_meta(0,data)
        elif data["streams"][0]["codec_type"] == "audio":
            codec_type, audio_br, audio_f = audio_meta(0,data)
    
        if data["streams"][1]["codec_type"] == "video":
            codec_type, video_br, video_w, video_h, aspect_r, video_f, duration, size, duration, total_br, file_format = video_meta(1,data)
        elif data["streams"][1]["codec_type"] == "audio":
            codec_type, audio_br, audio_f = audio_meta(1,data)
    
        isvideo=True
    
    except:
        isvideo=False
        video_br, video_w, video_h, aspect_r, duration, size, total_br, audio_br=0,0,0,0,0,0,0,0
        video_f="none"
        audio_f="none"
        codec_type="none"
        file_format="none"
    
    return isvideo, video_br, video_w, video_h, aspect_r, duration, size, total_br, audio_br, video_f, audio_f, file_format, audio_br, audio_f


# Test
argv = sys.argv[1:]
opts, args = getopt.getopt(argv, "f:")

for opt, arg in opts :
    if opt == "-f" :
	filename = arg

isvideo, video_br, video_w, video_h, aspect_r, duration, size, total_br, audio_br, video_f, audio_f, file_format, audio_br, audio_f = media_check(filename)

print "---------------------------"
print filename
print "---------------------------"
    
print isvideo, video_br, video_w, video_h, aspect_r, duration, size, total_br, audio_br, video_f, audio_f, file_format, audio_br, audio_f

print "---------------------------"
