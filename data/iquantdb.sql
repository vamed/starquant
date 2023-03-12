-- MySQL dump 10.11
--
-- Host: localhost    Database: iquant
-- ------------------------------------------------------
-- Server version	5.0.96-community-nt

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
-- Table structure for table `backtest_record`
--

DROP TABLE IF EXISTS `backtest_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `backtest_record` (
  `id` int(11) NOT NULL auto_increment,
  `account_id` varchar(50) collate utf8_unicode_ci NOT NULL default '0',
  `symbols` varchar(200) collate utf8_unicode_ci default NULL,
  `start` varchar(50) collate utf8_unicode_ci NOT NULL default '',
  `current` varchar(50) collate utf8_unicode_ci NOT NULL default '',
  `end` varchar(50) collate utf8_unicode_ci NOT NULL default '',
  `status` varchar(50) collate utf8_unicode_ci NOT NULL default '0' COMMENT 'finished,suspend',
  `date` date NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `backtest_record`
--

LOCK TABLES `backtest_record` WRITE;
/*!40000 ALTER TABLE `backtest_record` DISABLE KEYS */;
/*!40000 ALTER TABLE `backtest_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `execution_report`
--

DROP TABLE IF EXISTS `execution_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `execution_report` (
  `id` int(11) NOT NULL auto_increment,
  `account_id` varchar(50) collate utf8_unicode_ci default NULL,
  `symbol` varchar(50) collate utf8_unicode_ci NOT NULL default '0',
  `name` varchar(50) collate utf8_unicode_ci default NULL,
  `side` int(2) NOT NULL default '0',
  `price` float NOT NULL default '0',
  `volume` int(11) NOT NULL default '0',
  `amount` decimal(20,2) NOT NULL default '0.00',
  `mode` int(11) default NULL,
  `strategy` varchar(50) collate utf8_unicode_ci default NULL,
  `cl_ord_id` varchar(50) collate utf8_unicode_ci default NULL,
  `order_id` varchar(50) collate utf8_unicode_ci default NULL,
  `trade_date` varchar(50) collate utf8_unicode_ci default NULL,
  `trade_time` varchar(50) collate utf8_unicode_ci default NULL,
  `record_time` datetime default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `execution_report`
--

LOCK TABLES `execution_report` WRITE;
/*!40000 ALTER TABLE `execution_report` DISABLE KEYS */;
/*!40000 ALTER TABLE `execution_report` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `log`
--

DROP TABLE IF EXISTS `log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `log` (
  `id` int(11) NOT NULL auto_increment,
  `date` date default NULL,
  `record_time` datetime NOT NULL,
  `result` tinyint(4) default NULL,
  `type` varchar(50) collate utf8_unicode_ci default NULL,
  `memo` varchar(500) collate utf8_unicode_ci default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `log`
--

LOCK TABLES `log` WRITE;
/*!40000 ALTER TABLE `log` DISABLE KEYS */;
/*!40000 ALTER TABLE `log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myorder`
--

DROP TABLE IF EXISTS `myorder`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `myorder` (
  `id` int(11) NOT NULL auto_increment,
  `account_id` varchar(50) collate utf8_unicode_ci default NULL,
  `symbol` varchar(50) collate utf8_unicode_ci NOT NULL default '0',
  `name` varchar(50) collate utf8_unicode_ci default NULL,
  `side` int(2) NOT NULL default '0',
  `price` float NOT NULL default '0',
  `volume` int(11) NOT NULL default '0',
  `amount` decimal(20,2) NOT NULL default '0.00',
  `strategy` varchar(50) collate utf8_unicode_ci default NULL,
  `trade_date` varchar(50) collate utf8_unicode_ci default NULL,
  `trade_time` varchar(50) collate utf8_unicode_ci default NULL,
  `record_time` datetime default NULL,
  `status` int(11) default NULL,
  `mode` int(11) default NULL,
  `cl_ord_id` varchar(50) collate utf8_unicode_ci default NULL,
  `order_id` varchar(50) collate utf8_unicode_ci default NULL,
  `ex_ord_id` varchar(50) collate utf8_unicode_ci default NULL,
  `created_at` datetime default NULL,
  `updated_at` datetime default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myorder`
--

LOCK TABLES `myorder` WRITE;
/*!40000 ALTER TABLE `myorder` DISABLE KEYS */;
/*!40000 ALTER TABLE `myorder` ENABLE KEYS */;
UNLOCK TABLES;

/*!50003 SET @SAVE_SQL_MODE=@@SQL_MODE*/;

DELIMITER ;;
/*!50003 SET SESSION SQL_MODE="STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION" */;;
/*!50003 CREATE */ /*!50017 DEFINER=`root`@`localhost` */ /*!50003 TRIGGER `myorder_after_update` AFTER UPDATE ON `myorder` FOR EACH ROW BEGIN
DO SLEEP(2);

if NEW.mode=1 AND NEW.status=3 then
if exists (select * FROM `order` where cl_ord_id =NEW.cl_ord_id AND account_id=NEW.account_id AND trade_date=NEW.trade_date) then
 UPDATE `order` SET STATUS=3 WHERE cl_ord_id=NEW.cl_ord_id;
 
END if;
END if;

END */;;

DELIMITER ;
/*!50003 SET SESSION SQL_MODE=@SAVE_SQL_MODE*/;

--
-- Table structure for table `order`
--

DROP TABLE IF EXISTS `order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `order` (
  `id` int(11) NOT NULL auto_increment,
  `account_id` varchar(50) collate utf8_unicode_ci NOT NULL default '0',
  `cl_ord_id` varchar(50) collate utf8_unicode_ci default NULL,
  `symbol` varchar(50) collate utf8_unicode_ci NOT NULL default '0',
  `side` int(11) NOT NULL default '0',
  `price` float NOT NULL default '0',
  `trade_time` datetime NOT NULL default '0000-00-00 00:00:00',
  `volume` int(11) NOT NULL default '0',
  `amount` float NOT NULL default '0',
  `factor` varchar(50) collate utf8_unicode_ci NOT NULL default '0',
  `strategy` varchar(50) collate utf8_unicode_ci NOT NULL default '0',
  `indicator` varchar(500) collate utf8_unicode_ci NOT NULL default '0',
  `status` int(11) NOT NULL default '0',
  `mode` int(11) default NULL,
  `trade_date` varchar(50) collate utf8_unicode_ci NOT NULL,
  `record_time` datetime NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='订单信息';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order`
--

LOCK TABLES `order` WRITE;
/*!40000 ALTER TABLE `order` DISABLE KEYS */;
/*!40000 ALTER TABLE `order` ENABLE KEYS */;
UNLOCK TABLES;

/*!50003 SET @SAVE_SQL_MODE=@@SQL_MODE*/;

DELIMITER ;;
/*!50003 SET SESSION SQL_MODE="STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION" */;;
/*!50003 CREATE */ /*!50017 DEFINER=`root`@`localhost` */ /*!50003 TRIGGER `order_after_insert` BEFORE INSERT ON `order` FOR EACH ROW BEGIN
DO SLEEP(2);

if NEW.mode=2 then
if exists (select * from execution_report where cl_ord_id =NEW.cl_ord_id AND account_id=NEW.account_id AND trade_date=NEW.trade_date) then

  SET NEW.status=3;
END if;
END if;

END */;;

DELIMITER ;
/*!50003 SET SESSION SQL_MODE=@SAVE_SQL_MODE*/;

--
-- Table structure for table `position`
--

DROP TABLE IF EXISTS `position`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `position` (
  `id` int(11) NOT NULL auto_increment,
  `account_id` varchar(50) collate utf8_unicode_ci NOT NULL default '0',
  `code` varchar(20) collate utf8_unicode_ci NOT NULL default '0',
  `symbol` varchar(20) collate utf8_unicode_ci NOT NULL default '0',
  `name` varchar(20) collate utf8_unicode_ci default NULL,
  `strategy` varchar(50) collate utf8_unicode_ci NOT NULL default '',
  `rating` varchar(50) collate utf8_unicode_ci default NULL,
  `open_price` float default NULL COMMENT '平均建仓成本',
  `volume` int(11) default NULL COMMENT '量',
  `amount` float default NULL COMMENT '买入总金额',
  `can_use_volume` int(11) default NULL COMMENT '可用',
  `frozen_volume` int(11) default NULL,
  `yesterday_volume` int(11) default NULL,
  `on_road_volume` int(11) default NULL,
  `price` float NOT NULL default '0' COMMENT '现价',
  `market_value` float default NULL COMMENT '持仓市值(现值)',
  `profit_amount` float default NULL COMMENT '持仓利润',
  `profit_rate` float default NULL COMMENT '持仓利润',
  `inflow` float NOT NULL default '0',
  `factor` varchar(50) collate utf8_unicode_ci NOT NULL default '',
  `date` varchar(20) collate utf8_unicode_ci NOT NULL,
  `update_time` datetime NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='择时';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `position`
--

LOCK TABLES `position` WRITE;
/*!40000 ALTER TABLE `position` DISABLE KEYS */;
/*!40000 ALTER TABLE `position` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `setting`
--

DROP TABLE IF EXISTS `setting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `setting` (
  `id` int(11) NOT NULL auto_increment,
  `account_id` varchar(50) collate utf8_unicode_ci NOT NULL default '0' COMMENT '帐号',
  `initial_capital` decimal(10,2) NOT NULL default '0.00' COMMENT '初始总资金',
  `name` varchar(50) collate utf8_unicode_ci default NULL COMMENT '帐号名帐',
  `max_position` decimal(3,2) default NULL COMMENT '最大持仓',
  `max_single_position` decimal(3,2) default NULL COMMENT '单股最大持仓',
  `per_buy_amount` decimal(10,2) default NULL COMMENT '单次购买金额',
  `max_stock_number` int(11) default NULL COMMENT '最大持股数',
  `memo` varchar(200) collate utf8_unicode_ci default NULL COMMENT '备注',
  `broker` varchar(50) collate utf8_unicode_ci default NULL COMMENT '交易接口服务商（myquant:掘金,xtquant:讯投qmt）',
  `account_type` int(11) default '0' COMMENT '实盘1，模拟盘2',
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='量化参数设置';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `setting`
--

LOCK TABLES `setting` WRITE;
/*!40000 ALTER TABLE `setting` DISABLE KEYS */;
INSERT INTO `setting` VALUES (1,'修改为你掘金创建的模拟交易帐号ID','1000000.00','全新100万','1.00','0.80','20000.00',100,'全新一百万测试帐号','myquant',0),(2,'back_test','1000000.00','回测帐号','1.00','0.50','300000.00',100,'回测','myquant',0);
/*!40000 ALTER TABLE `setting` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stock_pool`
--

DROP TABLE IF EXISTS `stock_pool`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stock_pool` (
  `id` int(11) NOT NULL auto_increment,
  `code` varchar(20) collate utf8_unicode_ci NOT NULL default '0',
  `symbol` varchar(20) collate utf8_unicode_ci default NULL,
  `name` varchar(20) collate utf8_unicode_ci default NULL,
  `strategy` varchar(50) collate utf8_unicode_ci NOT NULL default '',
  `rating` varchar(50) collate utf8_unicode_ci default NULL,
  `price` float NOT NULL default '0',
  `date` varchar(20) collate utf8_unicode_ci NOT NULL,
  `change` float default NULL,
  `close` float default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=140086 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='择时';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stock_pool`
--

LOCK TABLES `stock_pool` WRITE;
/*!40000 ALTER TABLE `stock_pool` DISABLE KEYS */;
INSERT INTO `stock_pool` VALUES (140085,'688008','SHSE.688008','澜起科技','MeanRevertingStrategy','买入',56.17,'2023-03-08',-0.38,56.17);
/*!40000 ALTER TABLE `stock_pool` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trade_record`
--

DROP TABLE IF EXISTS `trade_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `trade_record` (
  `id` int(11) NOT NULL auto_increment,
  `account_id` varchar(50) collate utf8_unicode_ci default NULL,
  `symbol` varchar(50) collate utf8_unicode_ci NOT NULL default '0',
  `name` varchar(50) collate utf8_unicode_ci default NULL,
  `side` int(2) NOT NULL default '0',
  `price` float NOT NULL default '0',
  `volume` int(11) NOT NULL default '0',
  `amount` decimal(20,2) NOT NULL default '0.00',
  `strategy` varchar(50) collate utf8_unicode_ci default NULL,
  `cl_ord_id` varchar(50) collate utf8_unicode_ci default NULL,
  `order_id` varchar(50) collate utf8_unicode_ci default NULL,
  `mode` int(11) default NULL,
  `trade_date` varchar(50) collate utf8_unicode_ci default NULL,
  `trade_time` varchar(50) collate utf8_unicode_ci default NULL,
  `record_time` datetime default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trade_record`
--

LOCK TABLES `trade_record` WRITE;
/*!40000 ALTER TABLE `trade_record` DISABLE KEYS */;
/*!40000 ALTER TABLE `trade_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'iquant'
--
DELIMITER ;;
DELIMITER ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-03-10 15:58:34
