#!/usr/bin/python
# coding: utf-8
#
# UNATTENDED FFMPEG ENCODER
# https://github.com/supermasita/ufe  
# 

from lib.common import *
import sys
import getopt
import simplejson

def ufe_control_usage():
        """Prints the usage of "ufe-control".
        """
        print """
        Usage example : 
        
        ufe-control.py -a status_check -v {vhash}

        """

def status_check(vhash):
        """Checks status of video using vhash.
	   Prints JSON to STDOUT.
	"""
	db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
        cursor=db.cursor()
        cursor.execute("SELECT t_created, site_id, server_name, filename_orig, filename_san, recycle_status, status_time, recycle_time, video_br, video_w, video_h, aspect_r, duration, size from video_original where vhash='%s'" % (vhash) )
        results=cursor.fetchall()
	#
	status_full_json = []
	#
	if len(results) > 0 :
		#
		status_original_json = []
		for registry in results:
			t_created = registry[0]
			site_id = registry[1]
			server_name = registry[2]
			filename_orig = registry[3]
			filename_san = registry[4]
			recycle_status = registry[5]
			status_time = registry[6]
			recycle_time = registry[7]
			video_br = registry[8]
			video_w = registry[9]
			video_h = registry[10]
			aspect_r = registry[11]
			duration = registry[12]
			size = registry[13]
		#	
		status_original_json.append({ "vhash":vhash, "filename_orig":filename_orig, "filename_san":filename_san, "video_br":video_br, "video_w":video_w, "video_h":video_h, "aspect_r":round(aspect_r, 2), "duration":duration, "size":size, "site_id":site_id, "server_name":server_name })
	
	else :
		print "nothing there ..."

	#
	cursor.execute("SELECT t_created, site_id, server_name, vpid, weight, encode_status, ftp_status, recycle_status, encode_time, encode_file, ftp_time, ftp_path, recycle_time  from video_encoded where vhash='%s'" % (vhash) )
        results=cursor.fetchall()
        #
        if len(results) > 0 :
		#
		status_encoded_json = []
                for registry in results:
                        t_created = registry[0]
			site_id = registry[1]
			server_name = registry[2]
			vpid = registry[3]
			weight = registry[4]
			encode_status = registry[5]
			ftp_status = registry[6]
			recycle_status = registry[7]
			encode_time = registry[8]
			encode_file = registry[9]
			ftp_time = registry[10]
			ftp_path = registry[11]
			recycle_time = registry[12]
                	#       
                        status_encoded_json.append({ "vpid":vpid, "weight":weight, "encode_status":encode_status, "ftp_status":ftp_status, "recycle_status":recycle_status, "encode_time":str(encode_time), "encode_file":encode_file, "ftp_time":str(ftp_time), "ftp_path":ftp_path, "recycle_time":str(recycle_time) })                        
                
		#        
		status_original_json.append(status_encoded_json)
		status_full_json.append(status_original_json)
		#
		print simplejson.dumps(status_full_json, indent=4, sort_keys=True)

	else :
                print "nothing there ..."

	cursor.close ()
	db.close ()






# Get parameters
argv = sys.argv[1:]

try :
        opts, args = getopt.getopt(argv, "a:v:")
except :
        ufe_control_usage()
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
		status_check(vhash)	
	else :
		print "\nWrong parameters..."
		ufe_control_usage()
		sys.exit(2)
else :
	print "\nWrong parameters..."
	ufe_control_usage()
	sys.exit(2)

