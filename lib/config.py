#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# UNATTENDED FFMPEG TRANSCODER
# https://github.com/supermasita/uft
# 

# Core root
core_root = "/opt/uft/"
# Absolute path to folder where original videos are copied
original = "/opt/uft/video_original/"
# Absolute path to folder where encoded videos are created
encoded = "/opt/uft/video_encoded/"
# Absolute path to temporal folder (no trailing slash)
tmppath = "/var/tmp"

# Tolerance from last access to a video in video_origin
# Used by "uft-add" to determine if video can be added for encoding
timedif_to = 10

# This host's name in db table "servers"
server_name = "TRX01"

# DB credentials
db_host = "localhost"
db_user = "uft"
db_pass = "uft"
db_database = "uft"

# Absolute name of binaries
ffmpeg_bin = "/usr/local/bin/ffmpeg"

# Create JSON? (True or False)
create_video_json = True

# Dimensions for thumbnail created by create_thumbnail function
# (pixels, integer)
thumbnail_width = 600
thumbnail_height = 338
