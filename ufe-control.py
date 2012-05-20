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

#
##
###

def ufe_control_usage():
        """Prints the usage of "ufe-control".
        """
        print """
        Usage example : 
        
        ufe-control.py -a status_check -v {vhash}

        """
def status_check(vhash) :
        """Creates JSON file with the encoded videos profile specs. Usefull to create adaptative
           video playlists.
        """
        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
        cursor=db.cursor()
	#vhash_json = [{"vhash":vhash}]
	# Creste dictionary with video profiles specs
	cursor.execute("SELECT t_created, site_id, server_name, filename_orig, filename_san, recycle_status, status_time, recycle_time, video_br, video_w, video_h, aspect_r, duration, size, total_br, audio_br, video_f, audio_f from video_original where vhash='%s'" % (vhash) )
        results=cursor.fetchall()
        #
        if len(results) > 0 :
                #
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
			total_br = registry[14]
			audio_br = registry[15]
			video_f = registry[16]
			audio_f = registry[17]
                #       
                original_json = { "filename_orig":filename_orig, "filename_san":filename_san, "video_br":video_br, "video_w":video_w, "video_h":video_h, "aspect_r":round(aspect_r, 2), "duration":duration, "size":size, "site_id":site_id, "server_name":server_name, "total_br":total_br, "audio_br":audio_br, "video_f":video_f, "audio_f":audio_f }
		# Get names and attributes of video profiles
		cursor.execute("SELECT vpid, profile_name, video_br, video_h, video_w from video_profile;")
		video_profiles = {}
		# Loop query result and fill dictionary
		while (1):
			result = cursor.fetchone()
			if result == None: break
			#
			video_profiles["%i" % result[0]] = { "profile_name" : result[1],  "video_br" : "%i" % result[2], "video_h" : "%i" % result[3], "video_w" : "%i" % result[4] }
		# Create dictionary with all the encoded videos of a given vhash
		cursor.execute("SELECT vpid, encode_file, encode_status, ftp_path, priority, weight, ftp_status, ftp_time, recycle_status, recycle_time from video_encoded where vhash='%s';" % vhash)
		encoded_json = {}
		# Loop query result and fill dictionary
		while (1):
			result = cursor.fetchone()
			if result == None: break
			#
			encoded_json[video_profiles["%i" % result[0]]["profile_name"]] = { "file" : result[1], "ftp_path" : result[3], "encode_status" : result[2], "video_br" : video_profiles["%i" % result[0]]["video_br"], "video_h" : video_profiles["%i" % result[0]]["video_h"], "video_w" : video_profiles["%i" % result[0]]["video_w"], "priority":result[4], "weight":result[5], "ftp_status":result[6], "ftp_time":str(result[7]), "recycle_status":result[8], "recycle_time":str(result[9]) }
		# Close cursor and DB conn
		cursor.close ()
		db.close()
		# Create JSON file
		status_json = {}
		status_json[vhash] = {"original":original_json, "encoded":encoded_json}
		indented_status_json = simplejson.dumps(status_json, indent=4, sort_keys=True)
	# The vhash doesn exists?
	else :
		status_json = {}
		status_json[vhash] = {"original":"not found", "encoded":"not found"}
		indented_status_json = simplejson.dumps(status_json, indent=4, sort_keys=True)
	#
	return indented_status_json	


#
##
###

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
		indented_status_json = status_check(vhash)	
		print indented_status_json
	else :
		print "\nWrong parameters..."
		ufe_control_usage()
		sys.exit(2)
else :
	print "\nWrong parameters..."
	ufe_control_usage()
	sys.exit(2)

