-- MySQL dump 10.13  Distrib 5.5.46, for debian-linux-gnu (x86_64)
--
-- Host: jet.rss.chalmers.se    Database: smr
-- ------------------------------------------------------
-- Server version	5.1.41-3ubuntu12

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
-- Table structure for table `level1`
--

DROP TABLE IF EXISTS `level1`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `level1` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `orbit` int(11) NOT NULL,
  `backend` text,
  `freqmode` varchar(20) DEFAULT NULL,
  `nscans` smallint(6) DEFAULT NULL,
  `nspectra` smallint(6) DEFAULT NULL,
  `calversion` float DEFAULT NULL,
  `attversion` float DEFAULT NULL,
  `processed` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `uploaded` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `filename` text,
  `logname` text,
  `start_utc` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `stop_utc` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  KEY `key` (`orbit`,`backend`(3),`calversion`),
  KEY `orbit` (`orbit`),
  KEY `start` (`start_utc`)
) ENGINE=MyISAM AUTO_INCREMENT=297796 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `level1`
--
-- WHERE:  id in (253802,253802,297466,297414,297365,256523,256522)

LOCK TABLES `level1` WRITE;
/*!40000 ALTER TABLE `level1` DISABLE KEYS */;
INSERT INTO `level1` VALUES (253802,79656,'AC2','1',62,4252,6,20,'2015-10-01 07:19:36','2015-10-01 07:19:36','6.0/AC2/137/OC1B13728.HDF.gz','6.0/AC2/137/OC1B13728.LOG','2015-09-24 12:27:45','2015-09-24 14:03:27'),(256522,80324,'AC2','1',62,2460,7,20,'2015-11-10 14:14:27','2015-11-10 14:14:27','7.0/AC2/139/OC1B139C4.HDF.gz','7.0/AC2/139/OC1B139C4.LOG','2015-11-07 22:57:01','2015-11-08 00:32:43'),(256523,80325,'AC1','2',61,1216,7,20,'2015-11-10 14:14:59','2015-11-10 14:15:30','7.0/AC1/139/OB1B139C5.HDF.gz','7.0/AC1/139/OB1B139C5.LOG','2015-11-08 00:32:43','2015-11-08 02:08:24'),(297365,66445,'AC2','0',0,0,6.1,20,'2015-11-26 06:13:33','2015-11-26 06:46:38','6.1/AC1/103/OB1B103A6.HDF.gz','6.1/AC1/103/OB1B103A6.LOG','2013-04-27 13:47:05','2013-04-27 15:23:11'),(297414,66470,'AC1','2,19',47,3062,6.1,20,'2015-11-26 06:45:54','2015-11-26 07:23:10','6.1/AC2/103/OC1B103BE.HDF.gz','6.1/AC2/103/OC1B103BE.LOG','2013-04-29 05:49:46','2013-04-29 07:25:52'),(297466,80330,'AC1','19',39,1381,6,20,'2015-11-26 11:03:55','2015-11-26 11:04:30','6.0/AC1/139/OB1B139CA.HDF.gz','6.0/AC1/139/OB1B139CA.LOG','2015-11-08 08:31:12','2015-11-08 10:06:53');
/*!40000 ALTER TABLE `level1` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `level1b_gem`
--

DROP TABLE IF EXISTS `level1b_gem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `level1b_gem` (
  `id` bigint(20) unsigned NOT NULL COMMENT 'Id is linked to smr.level1.',
  `filename` varchar(30) NOT NULL COMMENT 'The filename on disk, note not full path',
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Time the file was downloaded',
  PRIMARY KEY (`id`,`filename`),
  KEY `match` (`id`,`date`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='All files downloaded from pdc';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `level1b_gem`
--
-- WHERE:  id in (253802,253802,297466,297414,297365,256523,256522)

LOCK TABLES `level1b_gem` WRITE;
/*!40000 ALTER TABLE `level1b_gem` DISABLE KEYS */;
INSERT INTO `level1b_gem` VALUES (253802,'6.0/AC2/137/OC1B13728.HDF','2015-10-02 00:59:10'),(253802,'6.0/AC2/137/OC1B13728.LOG','2015-10-02 00:59:10'),(253802,'6.0/AC2/137/OC1B13728.PTZ','2015-10-02 10:03:55'),(256522,'7.0/AC2/139/OC1B139C4.HDF','2015-11-11 01:52:33'),(256522,'7.0/AC2/139/OC1B139C4.LOG','2015-11-11 01:52:33'),(256522,'7.0/AC2/139/OC1B139C4.PTZ','2015-11-11 04:20:40'),(256523,'7.0/AC1/139/OB1B139C5.HDF','2015-11-11 01:52:29'),(256523,'7.0/AC1/139/OB1B139C5.LOG','2015-11-11 01:52:29'),(256523,'7.0/AC1/139/OB1B139C5.PTZ','2015-11-11 04:17:56'),(297466,'6.0/AC1/139/OB1B139CA.HDF','2015-11-27 02:02:20'),(297466,'6.0/AC1/139/OB1B139CA.LOG','2015-11-27 02:02:21'),(297466,'6.0/AC1/139/OB1B139CA.PTZ','2015-11-27 14:50:43');
/*!40000 ALTER TABLE `level1b_gem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `status`
--

DROP TABLE IF EXISTS `status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `status` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `status` smallint(6) DEFAULT NULL,
  `errmsg` text,
  UNIQUE KEY `id` (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=297796 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `status`
--
-- WHERE:  id in (253802,253802,297466,297414,297365,256523,256522)

LOCK TABLES `status` WRITE;
/*!40000 ALTER TABLE `status` DISABLE KEYS */;
INSERT INTO `status` VALUES (253802,1,' '),(256522,1,' '),(256523,1,' '),(297466,1,' ');
/*!40000 ALTER TABLE `status` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `statusl2`
--

DROP TABLE IF EXISTS `statusl2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `statusl2` (
  `id` bigint(20) NOT NULL DEFAULT '0' COMMENT 'Same id as in level1',
  `fqid` tinyint(4) NOT NULL DEFAULT '0',
  `version` varchar(7) NOT NULL,
  `errmsg` text,
  `proccount` int(11) DEFAULT '1',
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`,`fqid`,`version`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Information on filelevel.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `statusl2`
--
-- WHERE:  id in (253802,253802,297466,297414,297365,256523,256522)

LOCK TABLES `statusl2` WRITE;
/*!40000 ALTER TABLE `statusl2` DISABLE KEYS */;
INSERT INTO `statusl2` VALUES (253802,29,'2-1','',1,'2015-10-03 12:11:30');
/*!40000 ALTER TABLE `statusl2` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `level2`
--

DROP TABLE IF EXISTS `level2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `level2` (
  `id` mediumint(8) unsigned NOT NULL DEFAULT '0' COMMENT 'Id maps to level1 table.',
  `version2` varchar(5) NOT NULL DEFAULT '',
  `latitude` double DEFAULT '0',
  `longitude` double DEFAULT '0',
  `mjd` double DEFAULT '0',
  `date` datetime DEFAULT '0000-00-00 00:00:00',
  `sunZD` double DEFAULT '0',
  `fqid` tinyint(2) unsigned zerofill NOT NULL DEFAULT '00',
  `quality` tinyint(4) DEFAULT '0',
  `p_offs` double DEFAULT '0',
  `f_shift` double DEFAULT '0',
  `chi2` double DEFAULT '0',
  `chi2_y` double DEFAULT '0',
  `chi2_x` double DEFAULT '0',
  `marq_start` double DEFAULT '0',
  `marq_stop` double DEFAULT '0',
  `marq_min` double DEFAULT '0',
  `n_iter` mediumint(9) DEFAULT '0',
  `scanno` tinyint(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`,`version2`,`fqid`,`scanno`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 PACK_KEYS=1 COMMENT='Information from the l2p-hdf files.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `level2`
--
-- WHERE:  id in (253802,253802,297466,297414,297365,256523,256522)

LOCK TABLES `level2` WRITE;
/*!40000 ALTER TABLE `level2` DISABLE KEYS */;
INSERT INTO `level2` VALUES (253802,'2-1',-18.6854286193848,-131.118469238281,57289.6351407014,'2015-09-24 15:14:36',80.8290252685547,29,0,0.03551,-287000,0.78,0.78,0.0058,0.1,0.01,0.01,2,31),(253802,'2-1',-50.9078521728516,-132.120574951172,57289.6411021664,'2015-09-24 15:23:11',82.8581390380859,29,6,0.009604,-120000,19,19,0.048,0.1,150000,1.6,13,37),(253802,'2-1',-61.8903198242188,-132.109970092773,57289.6431838365,'2015-09-24 15:26:11',84.135612487793,29,6,0.004673,-785000,17,17,0.022,0.1,95000,7.8,9,39),(253802,'2-1',-78.7653656005859,-128.912170410156,57289.646387348,'2015-09-24 15:30:47',86.6474456787109,29,6,0.008537,-1180000,15,15,0.032,0.1,190000,3.9,15,42);
/*!40000 ALTER TABLE `level2` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `level2files`
--

DROP TABLE IF EXISTS `level2files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `level2files` (
  `id` bigint(20) NOT NULL DEFAULT '0' COMMENT 'Same id as in level1',
  `fqid` tinyint(4) NOT NULL DEFAULT '0',
  `version` varchar(7) NOT NULL,
  `nscans` tinyint(4) DEFAULT NULL,
  `verstr` varchar(15) DEFAULT '',
  `hdfname` varchar(60) DEFAULT NULL,
  `pdcname` varchar(60) DEFAULT NULL,
  `processed` datetime DEFAULT NULL,
  `uploaded` datetime DEFAULT NULL,
  PRIMARY KEY (`id`,`fqid`,`version`),
  KEY `match` (`id`,`fqid`,`version`,`processed`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='Information on filelevel.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `level2files`
--
-- WHERE:  id in (253802,253802,297466,297414,297365,256523,256522)

LOCK TABLES `level2files` WRITE;
/*!40000 ALTER TABLE `level2files` DISABLE KEYS */;
INSERT INTO `level2files` VALUES (253802,29,'2-1',4,'Qsmr-2-1-55','SMRhdf/Qsmr-2-1/SM_AC2ab/SCH_5018_C13728_021.L2P','version_2.1/SM_AC2ab/SCH_5018_C13728_021.L2P','2015-10-03 14:11:29','2015-10-03 14:11:30');
/*!40000 ALTER TABLE `level2files` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-11-30 10:37:06
