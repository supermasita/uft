#!/usr/bin/python
# -*- coding: utf-8 -*-

# ffprobe -v quiet -print_format json -show_format -show_streams test.mp4

from subprocess import Popen, PIPE
import os, sys
import simplejson as json
from pprint import pprint


def parse(filename):
    command = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", filename]
    p = Popen(command, stdout=PIPE)
    p.wait()
 
    data = json.loads(p.stdout.read())
    p.stdout.close()
    print data["streams"][0]["codec_name"]


parse("../sampleñí.mp4")

