#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# UNATTENDED FFMPEG ENCODER
# https://github.com/supermasita/ufe
# 

from common import *

import simplejson

#
##
###

def status_check(vhash) :
        """Creates JSON file with the encoded videos profile specs. Usefull to create adaptative
           video playlists.
        """
        db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
        cursor = db.cursor()
        # Get names and attributes of video profiles
        cursor.execute("SELECT vpid, profile_name, video_br, video_h, video_w from video_profile;")
        video_profiles = {}
        # Loop query result and fill dictionary
        while (1):
		result = cursor.fetchone()
		if result == None: break
		#
		video_profiles["%i" % result[0]] = { "profile_name" : result[1],  "video_br" : "%i" % result[2], "video_h" : "%i" % result[3], "video_w" : "%i" % result[4] }

	# Create dictionary with video profiles specs
	cursor.execute("SELECT t_created, site_id, server_name, filename_orig, filename_san, recycle_status, status_time, recycle_time, video_br, video_w, video_h, aspect_r, duration, size, total_br, audio_br, video_f, audio_f from video_original where vhash='%s';" % (vhash) )
        results = cursor.fetchall()
	# Any results?
        if len(results) > 0 :
                # Create json for original video
		for t_created, site_id, server_name, filename_orig, filename_san, recycle_status, status_time, recycle_time, video_br, video_w, video_h, aspect_r, duration, size, total_br, audio_br, video_f, audio_f in results :
                #       
                	original_json = { "filename_orig":filename_orig, "filename_san":filename_san, "video_br":video_br, "video_w":video_w, "video_h":video_h, "aspect_r":round(aspect_r, 2), "duration":duration, "size":size, "site_id":site_id, "server_name":server_name, "total_br":total_br, "audio_br":audio_br, "video_f":video_f, "audio_f":audio_f }
	
		# Create dictionary with all the encoded videos 
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
