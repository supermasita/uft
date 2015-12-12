#!/usr/bin/python
# -*- coding: utf-8 -*-

# ffprobe -v quiet -print_format json -show_format -show_streams test.mp4

from subprocess import Popen, PIPE
import os, sys
import simplejson as json
#from pprint import pprint
import getopt

# isvideo, video_br, video_w, video_h, aspect_r, duration, size, total_br, audio_br, video_f, audio_f, file_format
argv = sys.argv[1:]
opts, args = getopt.getopt(argv, "f:")

for opt, arg in opts :
    if opt == "-f" :
	filename = arg

def video_meta(stream_number,data):
    print "codec_type %s" % data["streams"][stream_number]["codec_type"]
    print "video_br %s" % data["streams"][stream_number]["bit_rate"]
    print "video_w %i" % data["streams"][stream_number]["width"]
    print "video_h %i" % data["streams"][stream_number]["height"]
    print "aspect_r %s" % data["streams"][stream_number]["display_aspect_ratio"]
    print "video_f %s" % data["streams"][stream_number]["codec_name"]
    print "duration %s" % data["format"]["duration"]
    print "size %s" % data["format"]["size"]
    print "duration %s" % data["format"]["duration"]
    print "total_br %s" % data["format"]["bit_rate"]
    print "file_format %s" % data["format"]["format_name"]

def audio_meta(stream_number,data):
    print "codec_type %s" % data["streams"][stream_number]["codec_type"]
    print "audio_br %s" % data["streams"][stream_number]["bit_rate"]
    print "audio_f %s" % data["streams"][stream_number]["codec_name"]



def parse(filename):
    command = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", filename]
    p = Popen(command, stdout=PIPE)
    p.wait()
 
    data = json.loads(p.stdout.read())
    p.stdout.close()
    

    print "---------------------------"
    print filename
    print "---------------------------"
    

    try:
        if data["streams"][0]["codec_type"] == "video":
            video_meta(0,data)
        elif data["streams"][0]["codec_type"] == "audio":
            audio_meta(0,data)
    
        if data["streams"][1]["codec_type"] == "video":
            video_meta(1,data)
        elif data["streams"][1]["codec_type"] == "audio":
            audio_meta(1,data)
    except:
        print "Not a video"

    print "---------------------------"
 
    #try:
    #    #print data
    #    print "---------------------------"
    #    print filename
    #    print "---------------------------"
    #    print "video_br %s" % data["streams"][0]["bit_rate"]
    #    print "codec_type %s" % data["streams"][0]["codec_type"]
    #    print "codec_type %s" % data["streams"][1]["codec_type"]
    #    print "video_w %i" % data["streams"][0]["width"]
    #    print "video_h %i" % data["streams"][0]["height"]
    #    print "aspect_r %s" % data["streams"][0]["display_aspect_ratio"]
    #    print "size %s" % data["format"]["size"]
    #    print "duration %s" % data["format"]["duration"]
    #    print "total_br %s" % data["format"]["bit_rate"]
    #    print "audio_br %s" % data["streams"][1]["bit_rate"]
    #    print "video_f %s" % data["streams"][0]["codec_name"]
    #    print "audio_f %s" % data["streams"][1]["codec_name"]
    #    print "file_format %s" % data["format"]["format_name"]
    #    print "---------------------------"
    #    print ""
    #except:
    #   print "is not a video"
    #   print "---------------------------"



#parse("../sampleñí.mp4")
parse(filename)

