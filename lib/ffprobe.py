#!/usr/bin/python
# -*- coding: utf-8 -*-

# ffprobe -v quiet -print_format json -show_format -show_streams test.mp4

from subprocess import Popen, PIPE
import os, sys
import simplejson as json
from pprint import pprint

# isvideo, video_br, video_w, video_h, aspect_r, duration, size, total_br, audio_br, video_f, audio_f, file_format

def parse(filename):
    command = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", filename]
    p = Popen(command, stdout=PIPE)
    p.wait()
 
    data = json.loads(p.stdout.read())
    p.stdout.close()
    print data
    print "codec_name %s" % data["streams"][0]["codec_name"]
    print "height %i" % data["streams"][0]["height"]
    print "width %i" % data["streams"][0]["width"]
    print "display_aspect_ratio %s" % data["streams"][0]["display_aspect_ratio"]
    print "bit_rate %s" % data["streams"][0]["bit_rate"]
    print "duration %s" % data["streams"][0]["duration"]



parse("../sampleñí.mp4")

