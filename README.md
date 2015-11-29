
THIS README IS BEING CREATED

# UNATTENDED FFMPEG TRANSCODER                     
https://github.com/supermasita/uft             	     

WORD OF WARNING: 
This proyect is in a development stage and not even the README is complete. 
(!) USE IT AT YOUR OWN RISK (!)

### INTRODUCTION


####  What is UFT?

	UFT started as a bunch scripts used to encode and upload video in a 
completely unattended way. The goal is to make the encoding and uploading easy 
and foolproof, using presets to "normalize" all your videos, providing encoding 
best practices and specific quality for each device (broadband, mobile, etc.).
	
	When thinking UFT we had in mind the webmaster (or journalist, etc.) 
that has to encode several videos in different qualities for various websites, 
and upload them; UFT will make things easier.

	You can use UFT as a centralize solution for encoding videos, leaving
the encoding profiles to the Admin and not to the users, disabling them from
FTP access and not .cron.outging their computers with CPU intensive tasks.

	UFT could be thought as a simple alternative to other encoding software 
such as: Handbrake, Sorenson Squeeze, Windows Movie Maker, etc. 



####  What is not UFT?

	UFT is not a fully featured video edition and encoding software. We 
focus on simple and reliable operation. 

	We plan to extend UFT with other proyects built around it but the "core" 
will always be as simple as possible.


#### Features
	
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
	* Logging in sys.cron.out.
	* Per video FFMPEG .cron.out.
	* Video hinting.


#### Additional credits

        * "Pymediainfo"
	  Wrapper for Mediainfo CLI 
	  https://github.com/paltman/pymediainfo

        * "qt-faststart"
	  Used to hint videos
	  https://github.com/danielgtaylor/qtfaststart


### INSTALLING

#### Use Docker!

Try quickly by building an image with the included Dockerfile

#### Dependencies

	* "MySQL-python" http://sourceforge.net/projects/mysql-python/ 
	* "python-simplejson" http://pypi.python.org/pypi/simplejson/ 
	* "FFMPEG" http://ffmpeg.org/ 
	   (if using RHEL best install it from http://atrpms.net/)
	* "Medianfo CLI" http://mediainfo.sourceforge.net/

#### Creating database
	
	1- Create a database called "uft" (or whatever you like).
	2- Create a user ("uft") and grants to use the database.
	3- Use the dump located in "lib" to create the tables, like this
	   (from command line):
   	   
	   [you@you uft]$ mysql -u uft -D uft -p < lib/database_structure.sql
	
	(!) USE THE DB, USER AND PASS THAT YOU CREATED IN STEP 1 AND 2


#### Configuration
	
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
	* * * * * python /opt/uft/uft-add.py -a dir -s default -f /opt/uft/video-files/watchfolder/ > /var/tmp/uft-add.cron.out 2>&1
	* * * * * python /opt/uft/uft-encode.py > /var/tmp/uft-encode.cron.out 2>&1
	* * * * * python /opt/uft/uft-upload.py > /var/tmp/uft-upload.cron.out 2>&1
	# (next line only if u want estimate encode p.cron.outress on DB)
	* * * * * python /opt/uft/uft-progress.py > /var/tmp/uft-progress.cron.out 2>&1
	# UFT : RECYCLING
	* * * * * python /opt/uft/uft-recycle.py -r encoded > /var/tmp/uft-recycle_encoded.cron.out 2>&1
	* * * * * python /opt/uft/uft-recycle.py -r original > /var/tmp/uft-recycle_original.cron.out 2>&1
	* * * * * python /opt/uft/uft-recycle.py -r registers >/var/tmp/uft-recycle_registers.cron.out 2>&1
	* * * * * python /opt/uft/uft-recycle.py -r nonvideos >/var/tmp/uft-recycle_nonvideos.cron.out 2>&1
	
"""
	ALTERNATIVE IDEAS:
	* You could use inotify to monitor last access of files with INCRON 
	  ( http://inotify.aiken.cz/ )
	* You could use DAEMON TOOLS ( http://cr.yp.to/daemontools.html )
"""

### USING UFT

#### Encoding workflow
	
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

