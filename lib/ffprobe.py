#!/usr/bin/python
# -*- coding: utf-8 -*-

# ffprobe -v quiet -print_format json -show_format -show_streams test.mp4

from subprocess import Popen, PIPE
import os, sys
import simplejson as json
#from pprint import pprint

# isvideo, video_br, video_w, video_h, aspect_r, duration, size, total_br, audio_br, video_f, audio_f, file_format

def parse(filename):
    command = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", filename]
    p = Popen(command, stdout=PIPE)
    p.wait()
 
    data = json.loads(p.stdout.read())
    p.stdout.close()
    #print data
    print "video_br %s" % data["streams"][0]["bit_rate"]
    print "video_w %i" % data["streams"][0]["width"]
    print "video_h %i" % data["streams"][0]["height"]
    print "aspect_r %s" % data["streams"][0]["display_aspect_ratio"]
    print "size %s" % data["format"]["size"]
    print "duration %s" % data["format"]["duration"]
    print "total_br %s" % data["format"]["bit_rate"]
    print "audio_br %s" % data["streams"][1]["bit_rate"]
    print "video_f %s" % data["streams"][0]["codec_name"]
    print "audio_f %s" % data["streams"][1]["codec_name"]
    print "file_format %s" % data["format"]["format_name"]



parse("../sampleñí.mp4")

