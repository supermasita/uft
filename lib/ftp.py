def select_next_ftp():
	"""Selects lists of next VHASHs ready for FTP transfer. 
	   Returns ftp_list, next_ftp_video_list .
	"""
	db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
	cursor=db.cursor()
	# Create list of FTP destinations
	cursor.execute("select sites.id, sites.ftp_host, sites.ftp_user, sites.ftp_pass from sites;")
	results=cursor.fetchall()
	ftp_list= []
	for row in results :
                ftp_list.append(row)
        # Create list of videos to send via FTP
	cursor.execute("select video_encoded.encode_status, video_encoded.encode_file, video_encoded.vhash, video_encoded.vpid, video_encoded.ftp_path, video_encoded.site_id, video_encoded.t_created from video_encoded where video_encoded.encode_status=3 and video_encoded.ftp_status=1 and video_encoded.server_name='%s' limit 10;" % server_name )
        results=cursor.fetchall()
	next_ftp_video_list= []
	for row in results :
                next_ftp_video_list.append(row)
        cursor.close ()
        db.close ()
	return ftp_list, next_ftp_video_list


def update_ftp_status(state, u_vhash, u_vpid):
        ftp_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
	cursor=db.cursor()
	cursor.execute("update video_encoded set ftp_status=%i, ftp_time='%s' where vhash='%s' and vpid=%i ;" %  (state, ftp_time, u_vhash, u_vpid) )
	cursor.close ()
        db.commit ()
        db.close ()
