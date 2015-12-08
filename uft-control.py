#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# UNATTENDED FFMPEG TRANSCODER
# https://github.com/supermasita/uft
#

from lib.common import *
from lib.control import *

import sys
import getopt

#
##
###

def uft_control_usage():
    """Prints the usage of "uft-control".
    """
    print """
    Usage example :

    uft-control.py -a status_check -v {vhash}

    """

#
##
###

# Get parameters
argv = sys.argv[1:]

try :
    opts, args = getopt.getopt(argv, "a:v:")
except :
    uft_control_usage()
    sys.exit(2)

# Assign parameters as variables
for opt, arg in opts :
    if opt == "-a" :
        action = arg
    if opt == "-v" :
        vhash = arg

# Check if all needed variables are set
if vars().has_key('action') and vars().has_key('vhash'):
    if action == 'status_check' :
        indented_status_json = status_check(vhash)
        print indented_status_json
    else :
        print "\nWrong parameters..."
        uft_control_usage()
        sys.exit(2)
else :
    print "\nWrong parameters..."
    uft_control_usage()
    sys.exit(2)
