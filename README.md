# UNATTENDED FFMPEG TRANSCODER                     
### https://github.com/supermasita/uft             	     

WORD OF WARNING: 
This proyect is in a development stage and not even the README is complete. 
(!) USE IT AT YOUR OWN RISK (!)


1. INTRODUCTION
1.1 What is UFT ?
1.2 What is not UFT ?
1.3 Features
1.4 To-do
1.5 Credits

2. INSTALLING
2.1 Dependencies
2.2 Creating directories
2.3 Creating database
2.4 Creating FTP
2.5 Configuration
2.6 Installing crons

3. USING UFT
3.1 Encoding workflow
3.1.1 Checker
3.1.2 Encoder
3.1.3 Uploader

4. GETTING HELP
4.1 Troubleshooting  DO THIS!
4.2 Known issues

-------------------------------------------------------------------------------

1. INTRODUCTION


1.1 What is UFT?

	UFT started as a bunch scripts used to encode and upload video in a 
completely unattended way. The goal is to make the encoding and uploading easy 
and foolproof, using presets to "normalize" all your videos, providing encoding 
best practices and specific quality for each device (broadband, mobile, etc.).
	
	When thinking UFT we had in mind the webmaster (or journalist, etc.) 
that has to encode several videos in different qualities for various websites, 
and upload them; UFT will make things easier.

	You can use UFT as a centralize solution for encoding videos, leaving
the encoding profiles to the Admin and not to the users, disabling them from
FTP access and not hogging their computers with CPU intensive tasks.

	UFT could be thought as a simple alternative to other encoding software 
such as: Handbrake, Sorenson Squeeze, Windows Movie Maker, etc. 



1.2 What is not UFT?

	UFT is not a fully featured video edition and encoding software. We 
focus on simple and reliable operation. 

	We plan to extend UFT with other proyects built around it but the "core" 
will always be as simple as possible.


1.3 Features
	
	* Multisite in mind. 
	* Video presets: you can create your own, enable/disable them (globally 
 	  or per site).
	* Simple MySQL structure (no auto increments, no joins).
	* Multiserver in mind (many encoders and master-master DB).
	* Uploads to FTP server (or local directory) using year, month, date 
	  folder structure.
	* Maximum number of FFMPEG processes may be configured for each encoder
	  (default: 2).
	* Non-blocking weighted queues won't let a huge video consume all your 
	  processes and leave all other waiting.
	* Logging in syslog.
	* Per video FFMPEG log.
	* Video hinting.

1.4 To-do
	
	* Create video thumbnail and store it as a blob.
	* Handle exceptions.
	* Create install script.
	* "Pythonize" scripts.
	* Create python daemon and avoid crons.
	* Monitor file last access with inotify.
	* Improve logging.

1.5 Credits

	* Alejandro Ferrari
	  Sysadmin and Wowza expert 

	* Supermasita
	  Python coder wannabe and part time human being

        * "Pymediainfo"
	  Wrapper for Mediainfo CLI 
	  https://github.com/paltman/pymediainfo

        * "qt-faststart"
	  Used to hint videos
	  https://github.com/danielgtaylor/qtfaststart

-------------------------------------------------------------------------------

2. INSTALLING

(!) Don't hesitate to search for our help at Github if you have any trouble or
doubt about installation.

2.1 Dependencies

	* "MySQL-python" http://sourceforge.net/projects/mysql-python/ 
	* "python-simplejson" http://pypi.python.org/pypi/simplejson/ 
	* "FFMPEG" http://ffmpeg.org/ 
	   (if using RHEL best install it from http://atrpms.net/)
	* "Medianfo CLI" http://mediainfo.sourceforge.net/


2.2 Creating directories
	
	1- Create a directory for the scripts (ex: /var/www/html/uft/), where you will
	do the "git clone" or untar.
	2- Inside this directory create the following ones :
		* "video_original" : where UFT temporaly moves original videos.
		* "video_encoded" : where UFT temporaly stores encoded videos.


2.3 Creating database
	
	1- Create a database called "uft" (or whatever you like).
	2- Create a user ("uft") and grants to use the database.
	3- Use the dump located in "lib" to create the tables, like this
	   (from command line):
   	   
	   [you@you uft]$ mysql -u uft -D uft -p < lib/database_structure.sql
	
	(!) USE THE DB, USER AND PASS THAT YOU CREATED IN STEP 1 AND 2


2.4 Creating FTP 
	
	You will need at least one FTP account to upload your videos. Installing
and configuring an FTP server exceeds the reach of this document, please refer
to any online sources (http://www.cyberciti.biz/ offers great guide). 


2.5 Configuration
	
(!) This is the basic configuration to get you running with the "default" site.
Many sites can be configured in the same fashion. We will extend this README.
	
	1- Connect to DB and you would have to update the following fields in the
	   "sites" table with your credentials:
		* ftp_user
		* ftp_pass
		* ftp_host

	2- Modify the file "lib/config.py", changing the following variables
	   with your data (examples are provided in the file):
		* core_root 
		* original
		* encoded
		* tmppath
		* db_host
		* db_user
		* db_pass
		* db_database
		* ffmpeg_bin


2.6 Installing crons

	You will need the following crons running (change accordingly to your
	needs and setup):

	# UFT : MAIN
	* * * * * python /var/www/html/uft/uft-add.py -a dir -s default -f /var/tmp/videos/ > /var/tmp/uft-add.log 2>&1
	* * * * * python /var/www/html/uft/uft-encode.py > /var/tmp/uft-encode.log 2>&1
	* * * * * python /var/www/html/uft/uft-upload.py > /var/tmp/uft-upload.log 2>&1
	# (next line only if u want estimate encode progress on DB)
	* * * * * python /var/www/html/uft/uft-progress.py > /var/tmp/uft-progress.log 2>&1
	# UFT : RECYCLING
	* * * * * python /var/www/html/uft/uft-recycle.py -r encoded > /var/tmp/uft-recycle_encoded.log 2>&1
	* * * * * python /var/www/html/uft/uft-recycle.py -r original > /var/tmp/uft-recycle_original.log 2>&1
	* * * * * python /var/www/html/uft/uft-recycle.py -r registers >/var/tmp/uft-recycle_registers.log 2>&1
	* * * * * python /var/www/html/uft/uft-recycle.py -r nonvideos >/var/tmp/uft-recycle_nonvideos.log 2>&1
	
-------------------------------------------------------------------------------
	ALTERNATIVE IDEAS:
	* You could use inotify to monitor last access of files with INCRON 
	  ( http://inotify.aiken.cz/ )
	* You could use DAEMON TOOLS ( http://cr.yp.to/daemontools.html )
-------------------------------------------------------------------------------

3. USING UFT

3.1 Encoding workflow
	
	* "uft-checker" will scan the directory and if it finds that the file
	has not been modified in a given time period (defined in "config.py") 
	and continue.

	* Using "uft-add" you will add videos for encoding in two different ways:
		1- Adding an specific file. 
		   (ex: uft-add.py -a file -s default -f /var/tmp/videos/lalala.avi)
		2- Adding all videos in a directory.
		   (ex: uft-add.py -a dir -s default -f /var/tmp/videos/)
		   The directory will be scanned and only files update before a 
		   given time period (defined in "config.py") will be added.

	* "Mediainfo" will be used to read the video metadata. The file will be
	move to "video_original" folder and a register in "video_original" 
	table will be created.

	* Registers will be created in "video_encoded" table for each 
	"video_profile" defined in "video_profile" table that is globally 
	enabled, matches the video aspect ratio and is enabled for the site.

	* "uft-encode" is spawned and it will encode any pending video.

	* After each encoding, "uft-upload" is spawned and any pending upload
	video is uploaded. 

	* "uft-recycle" will erase :
		* encoded videos that have already been successfully uploaded.
		* original videos, whose encoded videos have been already recycled.
		* registers for those videos whose encoded and original videos have 
		  been recycled.

3.1.1 Checker (to do)

3.1.2 Encoder (to do)

3.1.3 Uploader (to do)

3.1.4 States (to do)
	
	0 : disabled
	1 : pending
	2 : running
	3 : finished
	4 : error

-------------------------------------------------------------------------------

4. GETTING HELP

(!) To be done! Please contact us at Github!

4.1 Troubleshooting
4.2 Known issues
