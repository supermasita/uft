def recycle_old_registers():
        """Removes registers from DB of videos that have already been recycled.
	"""
	db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
        cursor=db.cursor()
        cursor.execute("SELECT vhash from video_original where server_name='%s' and recycle_status=3 and t_created < DATE_SUB(current_timestamp(), INTERVAL 48 HOUR);" % server_name )
        results=cursor.fetchall()
	cursor.close ()
	# Any results?
	if len(results) > 0 :
		for registry in results:
			vhash = registry[0]
			cursor_vhash=db.cursor()
			cursor_vhash.execute("delete from video_original where vhash='%s';" % vhash )
			cursor_vhash.execute("delete from video_encoded where vhash='%s';" % vhash )
			db.commit()
			cursor_vhash.close()
			logthis('Deleted all registers for vhash: %s' % vhash)
	else :
		print "There are no old registers to delete."
        db.close ()

def select_next_original_recycle():
	"""Finds original videos whose encoded videos have been already recycled and deletes them.
	"""
        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
        cursor=db.cursor()
        cursor.execute("select vhash, filename_san, vp_total from video_original where vp_total=vp_done and recycle_status=1 and server_name='%s' order by 1 limit 10;" % server_name )
        results=cursor.fetchall()
	pending_video_list = list()
	lista_vhash = list()	
	pending_original_recycle=0
	for registry in results:
		vhash = registry[0]
		filename_san = registry[1]
		vp_total = registry[2]
		lista_vhash.append([vhash, filename_san])
	if vars().has_key('vhash') :	
		for registry in lista_vhash :			
			lvhash = registry[0]
			lfilename_san = registry[1]
			cursor.execute("select count(*) from video_encoded where vhash='%s' and recycle_status=3;" % lvhash )
			results2=cursor.fetchall()
			if vp_total==results2[0][0] :
				pending_video = [lvhash, lfilename_san]
				pending_video_list.append(pending_video)
				pending_original_recycle=1	
	else :
        	pending_original_recycle = pending_video_list = 0
	cursor.close ()
        db.close ()
	return pending_original_recycle, pending_video_list


def update_encoded_recycle_status(state, u_vhash, u_vpid):
	"""Updates the recycled status of a encoded video.
	"""
        recycle_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
        cursor=db.cursor()
        cursor.execute("update video_encoded set recycle_status=%i, recycle_time='%s' where vhash='%s' and vpid=%i;" %  (state, recycle_time, u_vhash, u_vpid) )
        cursor.close ()
        db.commit ()
        db.close ()


def update_original_recycle_status(state, u_vhash):
	""" Updates de encoded status of a original video.
	"""
        recycle_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
        cursor=db.cursor()
        cursor.execute("update video_original set recycle_status='%i', recycle_time='%s' where vhash='%s' ;" %  (state, recycle_time, u_vhash) )
        cursor.close ()
        db.commit ()
        db.close ()


def select_next_encoded_recycle():
	"""Finds already uploaded encoded videos and deletes them.
	"""
        db=MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_database )
        cursor=db.cursor()
        cursor.execute("select t_created, vhash, encode_time, vpid, encode_file from video_encoded where recycle_status=1 and ftp_status=3 and encode_status=3 and ftp_time < DATE_SUB(current_timestamp(), INTERVAL 30 MINUTE) and server_name='%s' order by 1 limit 1;" % server_name )
        results=cursor.fetchall()
        for registry in results:
                t_created = registry[0]
                vhash = registry[1]
                encode_time = registry[2]
		vpid = registry[3]
		encode_file = registry[4]
        if vars().has_key('vhash') :
                pending_encoded_recycle=1
                return pending_encoded_recycle, t_created, vhash, encode_time, vpid, encode_file
        else :
                pending_encoded_recycle = t_created = vhash = encode_time = vpid = encode_file = 0
                return pending_encoded_recycle, t_created, vhash, encode_time, vpid, encode_file
        cursor.close ()
        db.close ()






