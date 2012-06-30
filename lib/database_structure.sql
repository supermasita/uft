-- MySQL dump 10.11
--
-- Host: localhost    Database: ufe
-- ------------------------------------------------------
-- Server version	5.0.77

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `servers`
--

DROP TABLE IF EXISTS `servers`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `servers` (
  `servers_id` int(11) NOT NULL,
  `name` varchar(45) NOT NULL default '',
  `role` varchar(45) NOT NULL,
  `enabled` int(1) NOT NULL default '0',
  `ip` varchar(45) default NULL,
  `handicap` int(2) NOT NULL default '1',
  `load` float default '0',
  `running_ps` int(11) default '0',
  `max_ps` int(11) NOT NULL default '2',
  PRIMARY KEY  (`servers_id`),
  UNIQUE KEY `name_UNIQUE` (`name`),
  UNIQUE KEY `servers_id_UNIQUE` (`servers_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `servers`
--

LOCK TABLES `servers` WRITE;
/*!40000 ALTER TABLE `servers` DISABLE KEYS */;
INSERT INTO `servers` VALUES (1,'encoder01','encoder',1,'127.0.0.1',1,0,0,2);
/*!40000 ALTER TABLE `servers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sites`
--

DROP TABLE IF EXISTS `sites`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `sites` (
  `id` int(2) NOT NULL,
  `name` varchar(45) NOT NULL,
  `enabled` int(1) NOT NULL default '0',
  `site_url` varchar(45) default NULL,
  `local_folder` varchar(45) NOT NULL,
  `ftp_enabled` varchar(45) NOT NULL default '0',
  `ftp_user` varchar(45) default NULL,
  `ftp_pass` varchar(45) default NULL,
  `ftp_host` varchar(45) default NULL,
  `vp_default` int(2) NOT NULL,
  `vp_enabled` varchar(45) default NULL,
  `vp_priority` int(2) default NULL,
  PRIMARY KEY  (`id`,`name`),
  UNIQUE KEY `name_UNIQUE` (`name`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `sites`
--

LOCK TABLES `sites` WRITE;
/*!40000 ALTER TABLE `sites` DISABLE KEYS */;
INSERT INTO `sites` VALUES (1,'default',1,'','/var/tmp/ufe-uploaded','0','ufe','ufepassword','127.0.0.1',0,NULL,3);
/*!40000 ALTER TABLE `sites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `video_encoded`
--

DROP TABLE IF EXISTS `video_encoded`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `video_encoded` (
  `vhash` varchar(64) NOT NULL,
  `t_created` timestamp NULL default '0000-00-00 00:00:00',
  `site_id` int(2) NOT NULL,
  `server_name` varchar(45) NOT NULL,
  `vpid` int(11) NOT NULL default '1',
  `priority` int(2) NOT NULL default '10',
  `weight` int(11) NOT NULL default '0',
  `encode_status` int(1) NOT NULL default '1',
  `ftp_status` int(1) NOT NULL default '1',
  `recycle_status` int(1) NOT NULL default '1',
  `encode_time` timestamp NULL default '0000-00-00 00:00:00',
  `encode_file` varchar(120) NOT NULL,
  `ftp_time` timestamp NULL default '0000-00-00 00:00:00',
  `ftp_path` varchar(120) NOT NULL default '',
  `recycle_time` timestamp NULL default '0000-00-00 00:00:00',
  `encode_percent` float default NULL,
  PRIMARY KEY  (`vhash`,`vpid`),
  KEY `idx_status` (`encode_status`),
  KEY `idx_vhash` (`vhash`),
  KEY `idx_site_id` (`site_id`),
  KEY `idx_server_name` (`server_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `video_encoded`
--

LOCK TABLES `video_encoded` WRITE;
/*!40000 ALTER TABLE `video_encoded` DISABLE KEYS */;
/*!40000 ALTER TABLE `video_encoded` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `video_original`
--

DROP TABLE IF EXISTS `video_original`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `video_original` (
  `vhash` varchar(64) NOT NULL,
  `t_created` timestamp NULL default '0000-00-00 00:00:00',
  `site_id` int(2) default NULL,
  `server_name` varchar(45) default NULL,
  `filename_orig` varchar(120) NOT NULL default '',
  `filename_san` varchar(120) default NULL,
  `vp_total` int(2) NOT NULL default '0',
  `vp_done` int(2) NOT NULL default '0',
  `vp_run` int(2) NOT NULL default '0',
  `vp_error` int(2) NOT NULL default '0',
  `recycle_status` int(1) NOT NULL default '1',
  `status_time` timestamp NULL default '0000-00-00 00:00:00',
  `recycle_time` timestamp NULL default '0000-00-00 00:00:00',
  `file_format` varchar(45) default NULL,
  `video_br` int(11) default NULL,
  `video_w` int(11) default NULL,
  `video_h` int(11) default NULL,
  `aspect_r` float default NULL,
  `duration` int(11) default NULL,
  `size` bigint(20) default NULL,
  `total_br` int(11) default NULL,
  `audio_br` int(11) default NULL,
  `video_f` varchar(45) default NULL,
  `audio_f` varchar(45) default NULL,
  `thumbnail_blob` blob,
  PRIMARY KEY  (`vhash`),
  UNIQUE KEY `vhash_UNIQUE` (`vhash`),
  KEY `idx_vhash` (`vhash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `video_original`
--

LOCK TABLES `video_original` WRITE;
/*!40000 ALTER TABLE `video_original` DISABLE KEYS */;
/*!40000 ALTER TABLE `video_original` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `video_profile`
--

DROP TABLE IF EXISTS `video_profile`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `video_profile` (
  `vpid` int(11) NOT NULL,
  `profile_name` varchar(45) NOT NULL,
  `enabled` int(1) NOT NULL default '0',
  `file_format` varchar(45) NOT NULL default 'MPEG-4',
  `video_f` varchar(45) NOT NULL,
  `video_br` int(11) NOT NULL,
  `video_h` int(11) NOT NULL,
  `video_w` int(11) NOT NULL,
  `aspect_r` float NOT NULL,
  `min_video_br` int(11) NOT NULL,
  `min_video_w` int(11) NOT NULL,
  `param_ffmpeg` varchar(1024) NOT NULL,
  PRIMARY KEY  (`vpid`),
  UNIQUE KEY `vpid_UNIQUE` (`vpid`),
  UNIQUE KEY `profile_name_UNIQUE` (`profile_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `video_profile`
--

LOCK TABLES `video_profile` WRITE;
/*!40000 ALTER TABLE `video_profile` DISABLE KEYS */;
INSERT INTO `video_profile` VALUES (1,'720pw',1,'MPEG-4','AVC',1500000,720,1280,1.77,1500000,1280,'-async 1 -b 1500k -vf scale=1280:trunc(ow/a/2)*2 -vcodec libx264 -flags +loop -me_method hex -g 60 -qcomp 0.6 -qmin 10 -qmax 51 -qdiff 4 -bf 3 -b_strategy 1 -i_qfactor 0.71 -cmp +chroma -subq 8 -me_range 16 -coder 1 -sc_threshold 40 -flags2 +bpyramid+wpred+mixed_refs-dct8x8+fastpskip -keyint_min 25 -refs 3 -trellis 1 -level 31 -directpred 1 -partitions -parti8x8-parti4x4-partp8x8-partp4x4-partb8x8 -threads 0 -acodec aac -strict experimental -ar 44100 -ab 128k -deinterlace -metadata comment=Encoded_by_UFE -y'),(2,'480pw',0,'MPEG-4','AVC',800000,480,854,1.77,800000,854,'-async 1 -b 800k -vf scale=854:trunc(ow/a/2)*2 -vcodec libx264 -flags +loop -me_method hex -g 60 -qcomp 0.6 -qmin 10 -qmax 51 -qdiff 4 -bf 3 -b_strategy 1 -i_qfactor 0.71 -cmp +chroma -subq 8 -me_range 16 -coder 1 -sc_threshold 40 -flags2 +bpyramid+wpred+mixed_refs-dct8x8+fastpskip -keyint_min 25 -refs 3 -trellis 1 -level 31 -directpred 1 -partitions -parti8x8-parti4x4-partp8x8-partp4x4-partb8x8 -threads 0 -acodec aac -strict experimental -ar 44100 -ab 128k -deinterlace -metadata comment=Encoded_by_UFE -y'),(3,'360pw',1,'MPEG-4','AVC',500000,360,640,1.77,500000,640,'-async 1 -b 500k -vf scale=640:trunc(ow/a/2)*2 -vcodec libx264 -flags +loop -me_method hex -g 60 -qcomp 0.6 -qmin 10 -qmax 51 -qdiff 4 -bf 0 -b_strategy 1 -i_qfactor 0.71 -cmp +chroma -subq 8 -me_range 16 -coder 0 -sc_threshold 40 -flags2 +bpyramid-wpred+mixed_refs-dct8x8+fastpskip -wpredp 0 -keyint_min 25 -refs 3 -trellis 1 -level 30 -directpred 1 -partitions -parti8x8-parti4x4-partp8x8-partp4x4-partb8x8 -threads 0 -acodec aac -strict experimental -ar 44100 -ab 96k -deinterlace -metadata comment=Encoded_by_UFE -y'),(4,'240pw',1,'MPEG-4','AVC',250000,240,400,1.77,0,0,'-async 1 -r 15 -b 250k -vf scale=400:trunc(ow/a/2)*2 -vcodec libx264 -flags +loop -me_method hex -g 60 -qcomp 0.6 -qmin 10 -qmax 51 -qdiff 4 -bf 0 -b_strategy 1 -i_qfactor 0.71 -cmp +chroma -subq 8 -me_range 16 -coder 0 -sc_threshold 40 -flags2 +bpyramid-wpred+mixed_refs-dct8x8+fastpskip -wpredp 0 -keyint_min 25 -refs 3 -trellis 1 -level 30 -directpred 1 -partitions -parti8x8-parti4x4-partp8x8-partp4x4-partb8x8 -threads 0 -acodec aac -strict experimental -ar 22050 -ab 32k -deinterlace -metadata comment=Encoded_by_UFE -y'),(5,'480p',1,'MPEG-4','AVC',800000,480,640,1.33,800000,640,'-async 1 -b 800k -vf scale=640:trunc(ow/a/2)*2 -vcodec libx264 -flags +loop -me_method hex -g 60 -qcomp 0.6 -qmin 10 -qmax 51 -qdiff 4 -bf 3 -b_strategy 1 -i_qfactor 0.71 -cmp +chroma -subq 8 -me_range 16 -coder 1 -sc_threshold 40 -flags2 +bpyramid+wpred+mixed_refs-dct8x8+fastpskip -keyint_min 25 -refs 3 -trellis 1 -level 31 -directpred 1 -partitions -parti8x8-parti4x4-partp8x8-partp4x4-partb8x8 -threads 0 -acodec aac -strict experimental -ar 44100 -ab 128k -deinterlace -metadata comment=Encoded_by_UFE -y'),(6,'360p',1,'MPEG-4','AVC',500000,360,480,1.33,500000,480,'-async 1 -b 500k -vf scale=480:trunc(ow/a/2)*2 -vcodec libx264 -flags +loop -me_method hex -g 60 -qcomp 0.6 -qmin 10 -qmax 51 -qdiff 4 -bf 0 -b_strategy 1 -i_qfactor 0.71 -cmp +chroma -subq 8 -me_range 16 -coder 0 -sc_threshold 40 -flags2 +bpyramid-wpred+mixed_refs-dct8x8+fastpskip -wpredp 0 -keyint_min 25 -refs 3 -trellis 1 -level 30 -directpred 1 -partitions -parti8x8-parti4x4-partp8x8-partp4x4-partb8x8 -threads 0 -acodec aac -strict experimental -ar 44100 -ab 96k -deinterlace -metadata comment=Encoded_by_UFE -y'),(7,'240p',1,'MPEG-4','AVC',250000,240,320,1.33,0,0,'-async 1 -r 15 -b 250k -vf scale=320:trunc(ow/a/2)*2 -vcodec libx264 -flags +loop -me_method hex -g 60 -qcomp 0.6 -qmin 10 -qmax 51 -qdiff 4 -bf 0 -b_strategy 1 -i_qfactor 0.71 -cmp +chroma -subq 8 -me_range 16 -coder 0 -sc_threshold 40 -flags2 +bpyramid-wpred+mixed_refs-dct8x8+fastpskip -wpredp 0 -keyint_min 25 -refs 3 -trellis 1 -level 30 -directpred 1 -partitions -parti8x8-parti4x4-partp8x8-partp4x4-partb8x8 -threads 0 -acodec aac -strict experimental -ar 22050 -ab 32k -deinterlace -metadata comment=Encoded_by_UFE -y');
/*!40000 ALTER TABLE `video_profile` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2012-06-06  5:41:31
