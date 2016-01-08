#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# UNATTENDED FFMPEG TRANSCODER
# https://github.com/supermasita/uft
#

from lib.config import *
from lib.add import *
from lib.common import *
from lib.control import status_check

import MySQLdb
import shutil
import sys
import simplejson
import getopt

def uft_add_usage():
    """Prints the usage of "uft-add".
    """
    print """
    Usage example :

    uft-add.py -a file -s default -f /var/tmp/lalala.avi
    uft-add.py -a dir -s default -f /var/tmp/

    -a      Add file or directory
    -s      Name of the site
    -f      Full path filename or directory
    """


# Get parameters
argv = sys.argv[1:]

try :
    opts, args = getopt.getopt(argv, "a:s:f:")
except :
    uft_add_usage()
    sys.exit(2)

# Assign parameters as variables
for opt, arg in opts :
    if opt == "-a" :
        add = arg
    elif opt == "-s" :
        site_name = arg
    elif opt == "-f" :
        file_full_path = arg

"""
IMPROVE THIS!!!
"""

# Check if all needed variables are set
if vars().has_key('add') and vars().has_key('site_name') and vars().has_key('file_full_path') :
    # Tell me something about the site
    site_name, site_id, site_enabled, vp_priority = get_site(site_name)
    #
    file_name_only = file_full_path.split("/")[-1]
    file_path_only = "/".join(file_full_path.split("/")[:-1])+"/"
    #
    if add == 'file' :
        # Check metada to know if its a video
        isvideo, video_br, video_w, video_h, aspect_r, duration, size, total_br, audio_br, video_f, audio_f, file_format = media_check(file_full_path)
        print isvideo, video_br, video_w, video_h, aspect_r, duration, size, total_br, audio_br, video_f, audio_f, file_format
        if isvideo == True :
            # Video hash
            vhash = create_vhash(file_name_only, site_name)
            # Append original filename (with vhash appended) and sanitized filename
            filename_san, filename_orig = create_filename_san(file_name_only, vhash)
            # Insert registers in DB
            root = file_path_only
            file = file_name_only
            create_video_registry(vhash, filename_orig, filename_san, video_br, video_w, video_h, aspect_r, duration, size, site_id, server_name, total_br, audio_br, video_f, audio_f, root, file, vp_priority, file_format)
            # Move file
            move_original_file(file_path_only, file_name_only, filename_san)
            # Create thumbnails
            create_thumbnail(vhash, filename_san)
            create_thumbnail_blob(vhash, filename_san)
            logthis('%s was added as %s for %s' % (filename_orig, filename_san, site_name), stdout=0)
            indented_status_json = status_check(vhash)
            print indented_status_json
            # If its a video, spawn encode
            if not vars().has_key('spawn') :
                spawn = True
        else :
            # Video hash
            vhash = create_vhash(file_name_only, site_name)
            # Append original filename (with vhash appended) and sanitized filename
            filename_san, filename_orig = create_filename_san(file_name_only, vhash)
            # Insert registers in DB
            create_nonvideo_registry(vhash, filename_orig, filename_san, site_id, server_name)
            move_original_file(file_path_only, file_name_only, filename_san)
            logthis('Couldn\'t add %s : not enough metadata or not a video.' % file_name_only)
            # Don't spawn
            if not vars().has_key('spawn') :
                spawn = False
    #
    elif add == 'dir' :
        # Initialize spawn
        spawn = False
        # Check PID file
        pidfilename = "%s/uft-add-dir.pid" % tmppath
        if os.path.isfile(pidfilename):
            logthis('%s already exists. The process should be running.' % pidfilename, stdout=1)
            sys.exit()
        else:
            # Create PID
            pid = str(os.getpid())
            pidfile = open(pidfilename, 'w').write(pid)
            # Walk the path
            for root, folders, files in os.walk("%s" % file_path_only):
                # Check each file
                for file in files:
                    file_complete = os.path.join(root,file)
                    statinfo = os.stat(file_complete)
                    timedif = time.time() - statinfo.st_ctime
                    # Are they old enough to drink?
                    if timedif > timedif_to :
                        try:
                            # Check metada to know if it si a video
                            isvideo, video_br, video_w, video_h, aspect_r, duration, size, total_br, audio_br, video_f, audio_f, file_format = media_check('%s' % file_complete)
                            if isvideo is True :
                                # Video hash
                                vhash = create_vhash(file, site_name)
                                # Append original filename (with vhash appended) and sanitized filename
                                filename_san, filename_orig = create_filename_san(file, vhash)
                                # Insert registers in DB
                                create_video_registry(vhash, filename_orig, filename_san, video_br, video_w, video_h, aspect_r, duration, size, site_id, server_name, total_br, audio_br, video_f, audio_f, root, file, vp_priority, file_format)
                                # Move file
                                move_original_file(root, file, filename_san)
                                # Create thumbnails
                                create_thumbnail(vhash, filename_san)
                                create_thumbnail_blob(vhash, filename_san)
                                logthis('%s was added as  %s for %s' % (filename_orig, filename_san, site), stdout=0)
                                # If its a video, spawn encode
                                if not vars().has_key('spawn') :
                                    spawn = True
                            else :
                                # Video hash
                                vhash = create_vhash(file, site_name)
                                # Append original filename (with vhash appended) and sanitized filename
                                filename_san, filename_orig = create_filename_san(file, vhash)
                                # Insert registers in DB
                                create_nonvideo_registry(vhash, filename_orig, filename_san, site_id, server_name)
                                move_original_file(root, file, filename_san)
                                logthis('Couldn\'t add %s : not enough metadata or not a video.' % file)
                                # Don't spawn
                                if not vars().has_key('spawn') :
                                    spawn = False

                        except:
                            pass
                    else :
                        logthis('%s was modified not far from now. Please wait.' % file)
            else :
                logthis('No videos left to add in %s' % file_path_only)
            # Clean PID
            os.unlink(pidfilename)

    else :
        print "\nPlease check parameters... Do you want to add a 'file' or a 'dir'?"
        uft_add_usage()
        sys.exit(2)

    # Spawn encode
    if spawn is True :
        spawn_process("encode")

else :
    print "\nParameters missing ..."
    uft_add_usage()
    sys.exit(2)
