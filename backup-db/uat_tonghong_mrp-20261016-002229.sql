/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.8.6-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: 127.0.0.1    Database: uat_tonghong_mrp
-- ------------------------------------------------------
-- Server version	11.8.6-MariaDB-5ubuntu0.1 from Ubuntu

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Current Database: `uat_tonghong_mrp`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `uat_tonghong_mrp` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;

USE `uat_tonghong_mrp`;

--
-- Table structure for table `master_resep`
--

DROP TABLE IF EXISTS `master_resep`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `master_resep` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nama_resep` varchar(150) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `master_resep`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `master_resep` WRITE;
/*!40000 ALTER TABLE `master_resep` DISABLE KEYS */;
INSERT INTO `master_resep` VALUES
(1,'Resep Standard A'),
(2,'Resep Standard B'),
(3,'Resep Custom');
/*!40000 ALTER TABLE `master_resep` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `mrp_role_permissions`
--

DROP TABLE IF EXISTS `mrp_role_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `mrp_role_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `role` varchar(32) NOT NULL,
  `module_key` varchar(80) NOT NULL,
  `action` varchar(32) NOT NULL,
  `allowed` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_mrp_role_permissions_key` (`role`,`module_key`,`action`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mrp_role_permissions`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `mrp_role_permissions` WRITE;
/*!40000 ALTER TABLE `mrp_role_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `mrp_role_permissions` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `mrp_users`
--

DROP TABLE IF EXISTS `mrp_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `mrp_users` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `username` varchar(80) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` varchar(32) NOT NULL DEFAULT 'operator',
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `department` varchar(50) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mrp_users`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `mrp_users` WRITE;
/*!40000 ALTER TABLE `mrp_users` DISABLE KEYS */;
INSERT INTO `mrp_users` VALUES
(1,'admin','$2b$12$3i6aDf0nRmpbr6.Wl3RUtOsc2pbIXZgswWlP4.I2PUUQJXFhcWgq.','admin',1,'all','2026-09-19 07:34:57',NULL),
(2,'operator','$2b$12$9RmLsxEhc1OceDtYZqe1QePKjjRDTpOtuDoMBBicG8AH.LK8Lhaqy','operator',1,'produksi','2026-09-19 07:34:57',NULL),
(3,'packing','$2b$12$/wCu4fJVT3yvEQCu.XZxbO5yCRYw/FTYRGoitATFT748lFYJbad4.','packing',1,'packing','2026-09-19 07:34:57',NULL);
/*!40000 ALTER TABLE `mrp_users` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_checkpoint`
--

DROP TABLE IF EXISTS `tbl_checkpoint`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_checkpoint` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_wip` varchar(30) NOT NULL,
  `kode_packing` varchar(30) DEFAULT NULL,
  `checkpoint_type` varchar(50) DEFAULT 'inline',
  `thickness_actual` decimal(10,3) DEFAULT NULL,
  `softness_actual` varchar(100) DEFAULT NULL,
  `result` varchar(16) DEFAULT NULL,
  `is_ok` tinyint(1) DEFAULT NULL,
  `remark` varchar(255) DEFAULT NULL,
  `erp_production_detail_id` bigint(20) DEFAULT NULL,
  `erp_qc_detail_id` bigint(20) DEFAULT NULL,
  `measured_at` datetime DEFAULT current_timestamp(),
  `created_at` datetime DEFAULT current_timestamp(),
  `treatment` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_checkpoint_wip` (`kode_wip`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_checkpoint`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_checkpoint` WRITE;
/*!40000 ALTER TABLE `tbl_checkpoint` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_checkpoint` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_gudang_fg`
--

DROP TABLE IF EXISTS `tbl_gudang_fg`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_gudang_fg` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `packing_id` int(11) NOT NULL,
  `kode_packing` varchar(30) NOT NULL,
  `kode_wip` varchar(30) NOT NULL,
  `customer` varchar(150) DEFAULT NULL,
  `total_lembar` int(11) DEFAULT 0,
  `total_ukuran` decimal(12,2) DEFAULT 0.00,
  `status` enum('in_stock','out') DEFAULT 'in_stock',
  `date_in` datetime DEFAULT current_timestamp(),
  `date_out` datetime DEFAULT NULL,
  `keterangan_out` varchar(255) DEFAULT NULL,
  `erp_delivery_id` bigint(20) DEFAULT NULL,
  `erp_delivery_number` varchar(100) DEFAULT NULL,
  `bridge_status` varchar(32) DEFAULT NULL,
  `bridge_error` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `packing_id` (`packing_id`),
  UNIQUE KEY `kode_packing` (`kode_packing`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_gudang_fg`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_gudang_fg` WRITE;
/*!40000 ALTER TABLE `tbl_gudang_fg` DISABLE KEYS */;
INSERT INTO `tbl_gudang_fg` VALUES
(1,1,'FG-261002000004','WIP-20261002-00001','PT. NIKOMAS GEMILANG (IY)',3,3000.00,'in_stock','2026-10-02 10:57:08',NULL,NULL,NULL,NULL,NULL,NULL),
(2,2,'FG-261002000007','WIP-20261002-00002','PT. NIKOMAS GEMILANG (IY)',3,2000.00,'out','2026-10-02 11:03:19','2026-10-06 14:39:09','Scan SJ THI-M261009001',1,'THI-M261009001','ok',NULL),
(3,4,'FG-261003000005','WIP-20261003-00002','PT. ADIS DIMENSION FOOTWEAR',2,300.00,'in_stock','2026-10-03 16:26:40',NULL,NULL,NULL,NULL,NULL,NULL),
(4,5,'FG-261003000008','WIP-20261003-00003','PT. ADIS DIMENSION FOOTWEAR',2,1000.00,'out','2026-10-03 16:30:24','2026-10-06 14:36:30','Scan SJ THI-M261003001',2,'THI-M261003001','ok',NULL),
(5,6,'FG-261006000003','WIP-20261006-00001','PT. ADIS DIMENSION FOOTWEAR',3,1000.00,'in_stock','2026-10-06 14:20:23',NULL,NULL,3,'THI-M261014001','ok',NULL),
(6,8,'FG-261012000002','WIP-20261012-00002','PT. FENG TAY INDONESIA ENTERPRISES (EAST)',4,68.00,'in_stock','2026-10-12 17:35:35',NULL,NULL,NULL,NULL,NULL,NULL),
(7,9,'FG-261012000004','WIP-20261012-00001','PT. VICTORY CHINGLUH INDONESIA',3,61.00,'in_stock','2026-10-12 17:52:53',NULL,NULL,NULL,NULL,NULL,NULL),
(8,11,'FG-261013000004','WIP-20261013-00002','PT. ADIS DIMENSION FOOTWEAR',1,500.00,'in_stock','2026-10-13 11:08:49',NULL,NULL,NULL,NULL,NULL,NULL),
(9,10,'FG-261013000002','WIP-20261013-00002','PT. ADIS DIMENSION FOOTWEAR',4,111.00,'in_stock','2026-10-13 11:09:38',NULL,NULL,NULL,NULL,NULL,NULL),
(10,12,'FG-261014000003','WIP-20261014-00002','PT. ADIS DIMENSION FOOTWEAR',2,500.00,'in_stock','2026-10-14 23:02:52',NULL,NULL,4,'THI-M261014002','ok',NULL),
(11,13,'FG-261014000007','WIP-20261014-00001','PT. ADIS DIMENSION FOOTWEAR',3,1000.00,'in_stock','2026-10-14 23:03:29',NULL,NULL,4,'THI-M261014002','ok',NULL),
(12,14,'TWH-P-2','TWH-WIP-2','PT. NIKOMAS GEMILANG (IY)',1,800.00,'in_stock','2026-10-14 23:06:04',NULL,NULL,NULL,NULL,NULL,NULL),
(13,15,'TWH-P-3','TWH-WIP-3','PT. METRO PEARL INDONESIA (NB)',1,598.40,'in_stock','2026-10-14 23:06:04',NULL,NULL,NULL,NULL,NULL,NULL),
(14,16,'TWH-P-4','TWH-WIP-4','PT. METRO PEARL INDONESIA (NB)',1,800.00,'in_stock','2026-10-14 23:06:04',NULL,NULL,NULL,NULL,NULL,NULL),
(15,17,'TWH-P-9','TWH-WIP-9','PT. LONG RICH INDONESIA ADIDAS',1,393.60,'in_stock','2026-10-14 23:06:04',NULL,NULL,NULL,NULL,NULL,NULL),
(16,18,'TWH-P-12','TWH-WIP-12','PT. SUKSES ABADI INDONESIA',1,409.20,'in_stock','2026-10-14 23:06:04',NULL,NULL,NULL,NULL,NULL,NULL),
(17,19,'TWH-P-14','TWH-WIP-14','PT. ADIS DIMENSION FOOTWEAR',1,400.00,'in_stock','2026-10-14 23:06:04',NULL,NULL,NULL,NULL,NULL,NULL),
(18,20,'TWH-P-15','TWH-WIP-15','PT. NIKOMAS GEMILANG (IY)',1,48.80,'in_stock','2026-10-14 23:06:04',NULL,NULL,NULL,NULL,NULL,NULL),
(19,21,'TWH-P-16','TWH-WIP-16','PT. NIKOMAS GEMILANG (IY)',1,727.20,'in_stock','2026-10-14 23:06:04',NULL,NULL,NULL,NULL,NULL,NULL),
(20,22,'TWH-P-17','TWH-WIP-17','PT. LONG RICH INDONESIA ADIDAS',1,4.00,'in_stock','2026-10-14 23:06:04',NULL,NULL,NULL,NULL,NULL,NULL),
(21,23,'TWH-P-18','TWH-WIP-18','PT. ADIS DIMENSION FOOTWEAR',1,200.00,'in_stock','2026-10-14 23:06:04',NULL,NULL,NULL,NULL,NULL,NULL),
(22,24,'FG-261015000027','WIP-20261015-00001','PT. LONG RICH INDONESIA ADIDAS',27,1000.00,'in_stock','2026-10-15 23:33:00',NULL,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `tbl_gudang_fg` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_gudang_mod`
--

DROP TABLE IF EXISTS `tbl_gudang_mod`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_gudang_mod` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_mod` varchar(30) NOT NULL,
  `persiapan_id` int(11) NOT NULL,
  `ky_id` int(11) DEFAULT NULL,
  `kode_wip` varchar(30) NOT NULL,
  `kode_palet` varchar(50) NOT NULL COMMENT 'KY lama',
  `kode_yl` varchar(50) NOT NULL,
  `reject_qty` decimal(12,2) NOT NULL DEFAULT 0.00,
  `treatment_list` text DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `reject_lembar` int(11) NOT NULL DEFAULT 0 COMMENT 'Jumlah baris/lembar pengukuran',
  `status` enum('in_stock','out') NOT NULL DEFAULT 'in_stock',
  `consumed_persiapan_id` int(11) DEFAULT NULL,
  `date_out` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_gudang_mod_kode` (`kode_mod`),
  KEY `idx_gudang_mod_wip` (`kode_wip`),
  KEY `idx_gudang_mod_persiapan` (`persiapan_id`),
  KEY `idx_gudang_mod_ky` (`ky_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_gudang_mod`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_gudang_mod` WRITE;
/*!40000 ALTER TABLE `tbl_gudang_mod` DISABLE KEYS */;
INSERT INTO `tbl_gudang_mod` VALUES
(1,'MOD-260928000001',25,26,'WIP-20260928-00008','KY-TEST TONGHONG 28 SEPT','MCL-00A-123',10.00,'PU - Emboss','2026-09-28 22:31:24',0,'in_stock',NULL,NULL),
(2,'MOD-260928000002',24,25,'WIP-20260928-00007','KY-TEST 28 002','MCL-00A-123',500.00,'PU - Emboss','2026-09-28 22:43:24',1,'in_stock',NULL,NULL);
/*!40000 ALTER TABLE `tbl_gudang_mod` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_kulit_lebih`
--

DROP TABLE IF EXISTS `tbl_kulit_lebih`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_kulit_lebih` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `rencana_item_id` int(11) NOT NULL,
  `persiapan_id` int(11) DEFAULT NULL,
  `ky_id` int(11) DEFAULT NULL,
  `kode_palet` varchar(50) DEFAULT NULL,
  `kode_yl` varchar(50) DEFAULT NULL,
  `target_qty` decimal(12,2) DEFAULT 0.00,
  `actual_qty` decimal(12,2) DEFAULT 0.00,
  `selisih` decimal(12,2) DEFAULT 0.00,
  `keterangan` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_rencana_item` (`rencana_item_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_kulit_lebih`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_kulit_lebih` WRITE;
/*!40000 ALTER TABLE `tbl_kulit_lebih` DISABLE KEYS */;
INSERT INTO `tbl_kulit_lebih` VALUES
(1,1,1,2,'KY-TEST TH 002','MCL-00A-123',2000.00,1000.00,-1000.00,'Kurang','2026-10-02 10:56:07'),
(2,3,6,7,'KY-TEST 10/6/26 001','MCL-00A-123',5000.00,1000.00,-4000.00,'Kurang','2026-10-06 14:16:26'),
(3,4,7,8,'KY-TEST 10/6/26 001','MCL-00A-123',4000.00,2000.00,-2000.00,'Kurang','2026-10-06 14:21:19'),
(4,10,9,10,'KY-1002','MCL-00A-102',5000.00,68.00,-4932.00,'Kurang','2026-10-12 17:24:12'),
(5,14,10,11,'KY-TEST 10/6/26 001','MCL-00A-123',1839.00,77.00,-1762.00,'Kurang','2026-10-13 10:34:20'),
(6,15,12,13,'KY-1001','MCL-01V-134',10000.00,1000.00,-9000.00,'Kurang','2026-10-14 22:59:11'),
(7,16,13,14,'KY-1001','MCL-01V-134',9000.00,500.00,-8500.00,'Kurang','2026-10-14 23:00:39'),
(8,27,24,15,'KY-1001','MCL-01V-134',8500.00,1000.00,-7500.00,'Kurang','2026-10-15 23:05:10');
/*!40000 ALTER TABLE `tbl_kulit_lebih` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_lab_lot`
--

DROP TABLE IF EXISTS `tbl_lab_lot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_lab_lot` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_lot_warna` varchar(30) NOT NULL,
  `nama_lot_warna` varchar(150) NOT NULL,
  `status` enum('active','used','expired') DEFAULT 'active',
  `date_created` datetime DEFAULT current_timestamp(),
  `rencana_item_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_lot_warna` (`kode_lot_warna`),
  KEY `idx_kode_lot_warna` (`kode_lot_warna`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_lab_lot`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_lab_lot` WRITE;
/*!40000 ALTER TABLE `tbl_lab_lot` DISABLE KEYS */;
INSERT INTO `tbl_lab_lot` VALUES
(1,'LW-261006000001','test 10/6/26 001','active','2026-10-06 16:04:35',3),
(2,'LW-261006000002','COATING 1','active','2026-10-06 21:56:07',3),
(3,'LW-261006000003','COATING 2','active','2026-10-06 22:01:18',3),
(4,'LW-261006000002-2','TEst','active','2026-10-08 00:53:27',4),
(5,'LW-261006000002-3','Test','active','2026-10-08 00:53:27',4),
(6,'LW-261006000002-4','Coating 1','active','2026-10-08 00:58:54',4),
(7,'LW-261006000002-5','Coating 2','active','2026-10-08 00:58:54',4),
(8,'LW-261006000001-2','TEST LAB LOT','active','2026-10-11 02:33:05',3),
(9,'LW-261012000002-1','AR-144 BLACK 00A','active','2026-10-12 17:25:32',10),
(10,'LW-261013000003-1','coating 1','active','2026-10-13 10:49:30',14);
/*!40000 ALTER TABLE `tbl_lab_lot` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_lab_lot_detail`
--

DROP TABLE IF EXISTS `tbl_lab_lot_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_lab_lot_detail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_lot_warna` varchar(30) NOT NULL,
  `kode_kimia` varchar(50) NOT NULL,
  `nama_kimia` varchar(150) DEFAULT NULL,
  `resep` varchar(150) DEFAULT NULL,
  `satuan` varchar(20) DEFAULT 'kg',
  `qty` decimal(12,2) DEFAULT 0.00,
  `remarks` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_lot_detail` (`kode_lot_warna`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_lab_lot_detail`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_lab_lot_detail` WRITE;
/*!40000 ALTER TABLE `tbl_lab_lot_detail` DISABLE KEYS */;
INSERT INTO `tbl_lab_lot_detail` VALUES
(1,'LW-261006000001','MCH-001-C00001','MEK','Resep Custom','kg',100.00,'test'),
(2,'LW-261006000002','MCH-001-C00001','MEK','Resep Custom','kg',100.00,NULL),
(3,'LW-261006000002','MCH-006-B00010','KH BLACK','Resep Custom','kg',50.00,NULL),
(4,'LW-261006000002','MCH-006-B00009','KH WHITE 10A','Resep Custom','kg',50.00,NULL),
(5,'LW-261006000003','MCH-001-C00001','MEK','Resep Custom','kg',100.00,NULL),
(6,'LW-261006000003','MCH-006-B00009','KH WHITE 10A','Resep Custom','kg',100.00,NULL),
(7,'LW-261006000002-2','MCH-001-C00001','MEK',NULL,'kg',10.00,NULL),
(8,'LW-261006000002-2','MCH-006-B00009','KH WHITE 10A',NULL,'kg',10.00,'Lot No: 002'),
(9,'LW-261006000002-3','MCH-006-B00010','KH BLACK',NULL,'kg',10.00,'Lot No: 003'),
(10,'LW-261006000002-4','MCH-001-C00001','MEK',NULL,'kg',15.00,'test'),
(11,'LW-261006000002-4','MCH-006-B00009','KH WHITE 10A',NULL,'kg',15.00,'test · Lot No: 002'),
(12,'LW-261006000002-5','TEST01','TEST KIMIA 01',NULL,'KG',110.00,'Catatan COating 2 · Lot No: LN-00001'),
(13,'LW-261006000002-5','MCH-006-B00009','KH WHITE 10A',NULL,'kg',15.00,'Catatan COating 2 · Lot No: 002'),
(14,'LW-261006000002-5','MCH-006-B00010','KH BLACK',NULL,'kg',5.00,'Catatan COating 2 · Lot No: 003'),
(15,'LW-261006000001-2','MCH-001-C00001','MEK',NULL,'kg',10.00,'TEST'),
(16,'LW-261006000001-2','MCH-006-B00010','KH BLACK',NULL,'kg',10.00,'TEST · Lot No: 003'),
(17,'LW-261012000002-1','MCH-006-B00009','KH WHITE 10A',NULL,'kg',10.00,'Lot No: 002'),
(18,'LW-261012000002-1','MCH-006-B00010','KH BLACK',NULL,'kg',5.00,'Lot No: 003'),
(19,'LW-261012000002-1','MCH-001-C00001','MEK',NULL,'kg',5.00,NULL),
(20,'LW-261013000003-1','MCH-001-C00001','MEK',NULL,'kg',20.00,NULL),
(21,'LW-261013000003-1','MCH-006-B00010','KH BLACK',NULL,'kg',10.00,'Lot No: 003'),
(22,'LW-261013000003-1','MCH-006-B00009','KH WHITE 10A',NULL,'kg',5.00,'Lot No: 002');
/*!40000 ALTER TABLE `tbl_lab_lot_detail` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_lab_lot_sisa`
--

DROP TABLE IF EXISTS `tbl_lab_lot_sisa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_lab_lot_sisa` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_lot_warna` varchar(30) NOT NULL,
  `nama_lot_warna` varchar(150) DEFAULT NULL,
  `qty_sisa` decimal(12,2) NOT NULL,
  `notes` text DEFAULT NULL,
  `date_created` datetime DEFAULT current_timestamp(),
  `status` enum('open','mixed') NOT NULL DEFAULT 'open',
  PRIMARY KEY (`id`),
  KEY `idx_lab_sisa_lot` (`kode_lot_warna`),
  KEY `idx_lab_sisa_date` (`date_created`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_lab_lot_sisa`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_lab_lot_sisa` WRITE;
/*!40000 ALTER TABLE `tbl_lab_lot_sisa` DISABLE KEYS */;
INSERT INTO `tbl_lab_lot_sisa` VALUES
(1,'LW-260923000003','Lot Warna',0.50,NULL,'2026-09-23 10:52:30','open'),
(2,'LW-260923000005','TEST02 GAPCHEM',1.00,'TEST02','2026-09-23 19:45:52','open'),
(3,'LW-260923000005','TEST02 GAPCHEM',1.00,'TEST03','2026-09-23 19:56:25','open'),
(4,'LW-260923000005','TEST02 GAPCHEM',0.10,NULL,'2026-09-23 20:56:46','open'),
(5,'LW-260923000004','TEST GAP CHEM',1.00,'TEST SISA','2026-09-23 21:20:30','open'),
(6,'LW-260923000005','TEST02 GAPCHEM',0.01,'verify-mixed','2026-09-23 23:01:27','mixed'),
(7,'LW-261006000002','COATING 1',100.00,'TEST','2026-10-06 22:19:25','open'),
(8,'LW-261006000002-2','TEst',10.00,NULL,'2026-10-08 01:05:34','open'),
(9,'LW-261006000001-2','TEST LAB LOT',2.00,'TEST','2026-10-11 02:36:44','open');
/*!40000 ALTER TABLE `tbl_lab_lot_sisa` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_lab_mixing`
--

DROP TABLE IF EXISTS `tbl_lab_mixing`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_lab_mixing` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_lot_warna` varchar(30) NOT NULL,
  `nama_chemical` varchar(150) NOT NULL,
  `resep` varchar(150) DEFAULT NULL,
  `satuan` varchar(20) DEFAULT 'kg',
  `qty` decimal(12,2) DEFAULT 0.00,
  `remarks` text DEFAULT NULL,
  `status` enum('active','used','expired') DEFAULT 'active',
  `date_created` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_lot_warna` (`kode_lot_warna`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_lab_mixing`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_lab_mixing` WRITE;
/*!40000 ALTER TABLE `tbl_lab_mixing` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_lab_mixing` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_master_po`
--

DROP TABLE IF EXISTS `tbl_master_po`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_master_po` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `no_po` varchar(50) NOT NULL,
  `no_so` varchar(50) DEFAULT NULL,
  `customer` varchar(150) DEFAULT NULL,
  `item_name` varchar(200) DEFAULT NULL,
  `warna` varchar(100) DEFAULT NULL,
  `tebal` varchar(30) DEFAULT NULL,
  `emboss` varchar(100) DEFAULT NULL,
  `sq_ft` decimal(12,2) DEFAULT 0.00,
  `qty_order` decimal(12,2) DEFAULT 0.00,
  `qty_processed` decimal(12,2) DEFAULT 0.00,
  `status` enum('outstanding','partial','completed','cancelled') DEFAULT 'outstanding',
  `created_at` datetime DEFAULT current_timestamp(),
  `customer_id` int(11) DEFAULT NULL,
  `color_swatch` varchar(100) DEFAULT NULL,
  `source_detail_id` int(11) DEFAULT NULL,
  `qty_balance_erp` decimal(12,2) DEFAULT NULL,
  `lot_number` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_master_po_source_detail` (`source_detail_id`),
  KEY `idx_no_po` (`no_po`),
  KEY `idx_status` (`status`),
  KEY `idx_master_po_source_detail` (`source_detail_id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_master_po`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_master_po` WRITE;
/*!40000 ALTER TABLE `tbl_master_po` DISABLE KEYS */;
INSERT INTO `tbl_master_po` VALUES
(1,'NIKOMAS 123','PS26100201','PT. NIKOMAS GEMILANG (IY)','(PM) GENERIC PU COATED LEATHER','UNIVERSITY RED (65N) FLUORESCENT','1.2 - 1.4','R-8 M',5000.00,5000.00,5000.00,'completed','2026-10-02 10:21:24',18,'CHANGSHIN',1,5000.00,'PUMNS020261002001'),
(2,'NIKOMAS 123','PS26100201','PT. NIKOMAS GEMILANG (IY)','(PM) GENERIC SPLIT SUEDE','TEAM RED (67P)','1.2 - 1.4',NULL,2000.00,2000.00,0.00,'outstanding','2026-10-02 10:21:24',18,NULL,2,2000.00,'MYCNS020261002001'),
(3,'METRO123','PS26100202','PT. METRO PEARL INDONESIA (NB)','ECO GREEN RECYCLED LEATHER','MOONBEAM COLORO (026-79-03)','1.2 - 1.4','AR-100 M',1496.00,1496.00,1496.00,'completed','2026-10-02 10:41:35',16,NULL,3,1496.00,'PUMMP033261002001'),
(4,'TEST 3/10/26','THIPM26100301','PT. ADIS DIMENSION FOOTWEAR','VIRGIN HYDRO PU','ATOMIC VIOLET (55V)','1.2 - 1.4','AR-20 M',1000.00,1000.00,1000.00,'completed','2026-10-03 16:11:15',1,'ADIS',5,0.00,'PUMAD002261003001'),
(5,'W26B773 220NU','THIPM26100501','PT. FENG TAY INDONESIA ENTERPRISES (EAST)','VIRGIN HYDRO PU','BLACK (00A)','1.4 - 1.6','AR-144 M',60.00,60.00,60.00,'completed','2026-10-05 16:11:49',8,NULL,6,60.00,'PUMFT007261005001'),
(6,'3605264-1101757346-10(3-3400723)','THIPM26100502','PT. VICTORY CHINGLUH INDONESIA','(PM) GENERIC PU COATED LEATHER','OBSIDIAN (45B)','1.2 - 1.4','AR-20 M',161.00,161.00,161.00,'completed','2026-10-05 16:14:35',31,'VICTORY',7,161.00,'PUMVC005261005001'),
(7,'PO-PS26100504','PS26100504','PT. LONG RICH INDONESIA ADIDAS','ECO TECH COMFORT','ANTHRACITE (06F)','1.2 - 1.4','R-102 M',984.00,984.00,984.00,'completed','2026-10-05 23:25:01',44,NULL,9,984.00,'PUMLR029261005001'),
(8,'PO-THIPM26100508','THIPM26100508','PT. ADIS DIMENSION FOOTWEAR','VIRGIN HYDRO PU','ATOMIC VIOLET (55V)','1.2 - 1.4','AR-20 M',111.00,111.00,111.00,'completed','2026-10-05 23:29:16',1,NULL,10,111.00,'PUMAD002261005001'),
(9,'PO-THIPM26100601','THIPM26100601','PT. ADIS DIMENSION FOOTWEAR','VIRGIN HYDRO PU','ATOMIC VIOLET (55V)','1.2 - 1.4','AR-20 M',5000.00,5000.00,5000.00,'completed','2026-10-06 14:12:33',1,'ADIS',11,4000.00,'PUMAD002261006001'),
(10,'PO#00596~00611-12-10 0292/PO-SAI/X/2026','PS26100601','PT. SUKSES ABADI INDONESIA','HYDRO SOFT ACTION LEATHER','BLACK (145-17-00)','1.2 - 1.4','R-53 SM',1023.00,1023.00,1023.00,'completed','2026-10-06 15:32:21',37,NULL,12,1023.00,'PUMSD047261006001'),
(11,'PO-THIPM26100602','THIPM26100602','PT. ADIS DIMENSION FOOTWEAR','VIRGIN HYDRO PU','ATOMIC VIOLET (55V)','1.2 - 1.4','AR-20 M',1000.00,1000.00,1000.00,'completed','2026-10-06 16:46:00',1,'ADIS',13,1000.00,'PUMAD002261006002'),
(12,'PO-THIPM26100603','THIPM26100603','PT. ADIS DIMENSION FOOTWEAR','VIRGIN HYDRO PU','ARCTIC GREEN (3KF)','1.2 - 1.4','R-131 M',1000.00,1000.00,1000.00,'completed','2026-10-06 21:47:13',1,'NIKOMAS IY',14,1000.00,'PUMAD002261006003'),
(13,'4000842518 MB020029174','THIPM26100701','PT. NIKOMAS GEMILANG (IY)','VIRGIN HYDRO PU','VOLT (71R) FLUORESCENT','1.2 - 1.4','R-131 M',122.00,122.00,122.00,'completed','2026-10-07 14:16:48',18,NULL,15,122.00,'PUMNS020261007001'),
(14,'4000842519 MB020000523','THIPM26100702','PT. NIKOMAS GEMILANG (IY)','VIRGIN HYDRO PU','BLACK (00A)','1.2 - 1.4','R-131 M',1818.00,1818.00,1818.00,'completed','2026-10-07 14:24:46',18,NULL,16,1818.00,'PUMNS020261007002'),
(15,'aaa','THIPM26101301','PT. LONG RICH INDONESIA ADIDAS','ACTION PU COATED LEATHER','ANTHRACITE (016)','1.0 - 1.2','DE-172 SM',10.00,10.00,0.00,'outstanding','2026-10-13 23:01:55',44,NULL,17,10.00,'PUMLR029261013001'),
(16,'PO-THIPM26101401','THIPM26101401','PT. ADIS DIMENSION FOOTWEAR','VIRGIN HYDRO PU','BARELY ROSE (6GW)','1.2 - 1.4','AR-20 M',500.00,500.00,0.00,'outstanding','2026-10-14 22:57:07',1,'ADIS',18,500.00,'PUMAD002261014001'),
(17,'PO-THIPM26101401','THIPM26101401','PT. ADIS DIMENSION FOOTWEAR','ECO TECH COMFORT','ARMORY NAVY (4LX)','1.2 - 1.4','R-102 M',1000.00,1000.00,1000.00,'completed','2026-10-14 22:57:07',1,'CHANGSHIN RJ',19,0.00,'PUMAD002261014002'),
(18,'PO-THIPM26101401','THIPM26101401','PT. ADIS DIMENSION FOOTWEAR','VIRGIN HYDRO PU','ATOMIC VIOLET (55V)','1.2 - 1.4','AR-20 M',500.00,500.00,500.00,'completed','2026-10-14 22:57:07',1,'ADIS',20,300.00,'PUMAD002261014003'),
(19,'METRO123','PS26100202','PT. METRO PEARL INDONESIA (NB)','ECO GREEN RECYCLED LEATHER','MOONBEAM COLORO (026-79-03)','1.2 - 1.4','AR-100 M',2000.00,2000.00,0.00,'outstanding','2026-10-14 23:06:04',16,NULL,4,2000.00,'PUMMP033261002002'),
(20,'THIPM26101402','THIPM26101402','PT. ADIS DIMENSION FOOTWEAR','VIRGIN HYDRO PU','ADOBE (68I)','1.2 - 1.4','AR-196 M',1000.00,1000.00,1000.00,'completed','2026-10-14 23:28:24',1,NULL,21,1000.00,'PUMAD002261014004'),
(21,'PS26101502','PS26101502','PT. LONG RICH INDONESIA ADIDAS','SPLIT SUEDE','COLLEGIATE GREEN (024A)','1.2 - 1.4','-',1000.00,1000.00,1000.00,'completed','2026-10-15 23:04:15',44,NULL,24,1000.00,'MYCLR029261015003');
/*!40000 ALTER TABLE `tbl_master_po` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_master_treatment`
--

DROP TABLE IF EXISTS `tbl_master_treatment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_master_treatment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `jenis` enum('PU','Suede') NOT NULL,
  `nama_treatment` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=82 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_master_treatment`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_master_treatment` WRITE;
/*!40000 ALTER TABLE `tbl_master_treatment` DISABLE KEYS */;
INSERT INTO `tbl_master_treatment` VALUES
(8,'PU','PU - Spray 1','2026-08-09 16:20:22',1),
(9,'PU','PU - Spray 2','2026-08-09 16:20:22',1),
(10,'PU','PU - Spray 3','2026-08-09 16:20:22',1),
(11,'PU','PU - Rotopia A','2026-08-09 16:20:22',1),
(12,'PU','PU - Rotopia B','2026-08-09 16:20:22',1),
(13,'Suede','Suede - Dyeing','2026-08-09 16:20:22',1),
(14,'Suede','Suede - Dyeing','2026-08-09 16:20:22',1),
(15,'Suede','Suede - Softener','2026-08-09 16:20:22',1),
(16,'Suede','Suede - Finishing Spray','2026-08-09 16:20:22',1),
(17,'PU','PU - Press','2026-09-19 21:46:14',1),
(18,'PU','PU - Vibration','2026-10-07 22:05:44',1),
(19,'PU','PU - Base Coat','2026-10-07 22:05:59',0),
(20,'PU','PU - Color Coat','2026-10-07 22:06:16',0),
(21,'PU','PU - Top Coat','2026-10-07 22:08:46',0),
(22,'PU','PU - Emboss / Press','2026-10-07 22:09:08',0),
(23,'PU','PU - Emboss','2026-10-07 22:09:34',0),
(24,'PU','PU - Degrease','2026-10-07 22:09:45',0),
(81,'Suede','Suede - Buffing','2026-10-07 23:13:55',1);
/*!40000 ALTER TABLE `tbl_master_treatment` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_packing`
--

DROP TABLE IF EXISTS `tbl_packing`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_packing` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_packing` varchar(30) NOT NULL,
  `kode_wip` varchar(30) NOT NULL,
  `no_po` varchar(50) NOT NULL,
  `customer` varchar(150) DEFAULT NULL,
  `total_lembar` int(11) DEFAULT 0,
  `total_ukuran` decimal(12,2) DEFAULT 0.00,
  `status` enum('in_progress','finished') DEFAULT 'in_progress',
  `date_created` datetime DEFAULT current_timestamp(),
  `date_finished` datetime DEFAULT NULL,
  `softness` varchar(50) DEFAULT NULL,
  `gross_weight` decimal(12,2) DEFAULT NULL,
  `net_weight` decimal(12,2) DEFAULT NULL,
  `erp_production_id` bigint(20) DEFAULT NULL,
  `erp_production_detail_id` bigint(20) DEFAULT NULL,
  `rencana_item_id` int(11) DEFAULT NULL,
  `stock_sisa_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_packing` (`kode_packing`),
  KEY `idx_kode_wip` (`kode_wip`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_packing`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_packing` WRITE;
/*!40000 ALTER TABLE `tbl_packing` DISABLE KEYS */;
INSERT INTO `tbl_packing` VALUES
(1,'FG-261002000004','WIP-20261002-00001','NIKOMAS 123','PT. NIKOMAS GEMILANG (IY)',3,3000.00,'finished','2026-10-02 10:56:33','2026-10-02 10:57:08',NULL,NULL,NULL,NULL,NULL,1,NULL),
(2,'FG-261002000007','WIP-20261002-00002','NIKOMAS 123','PT. NIKOMAS GEMILANG (IY)',3,2000.00,'finished','2026-10-02 11:02:38','2026-10-02 11:03:19',NULL,NULL,NULL,NULL,NULL,1,NULL),
(3,'FG-261003000002','WIP-20261003-00001','TEST 3/10/26','PT. ADIS DIMENSION FOOTWEAR',1,1000.00,'in_progress','2026-10-03 16:20:21',NULL,NULL,NULL,NULL,NULL,NULL,2,NULL),
(4,'FG-261003000005','WIP-20261003-00002','TEST 3/10/26','PT. ADIS DIMENSION FOOTWEAR',2,300.00,'finished','2026-10-03 16:25:06','2026-10-03 16:26:40',NULL,NULL,NULL,NULL,NULL,2,NULL),
(5,'FG-261003000008','WIP-20261003-00003','TEST 3/10/26','PT. ADIS DIMENSION FOOTWEAR',2,1000.00,'finished','2026-10-03 16:29:26','2026-10-03 16:30:24',NULL,NULL,NULL,NULL,NULL,2,NULL),
(6,'FG-261006000003','WIP-20261006-00001','PO-THIPM26100601','PT. ADIS DIMENSION FOOTWEAR',3,1000.00,'finished','2026-10-06 14:17:47','2026-10-06 14:20:23',NULL,NULL,NULL,NULL,NULL,3,NULL),
(7,'FG-261012000007','WIP-20261006-00002','PO-THIPM26100601','PT. ADIS DIMENSION FOOTWEAR',9,1998.00,'in_progress','2026-10-06 14:21:38',NULL,NULL,NULL,NULL,NULL,NULL,4,NULL),
(8,'FG-261012000002','WIP-20261012-00002','W26B773 220NU','PT. FENG TAY INDONESIA ENTERPRISES (EAST)',4,68.00,'finished','2026-10-12 17:30:44','2026-10-12 17:35:35',NULL,NULL,NULL,NULL,NULL,10,NULL),
(9,'FG-261012000004','WIP-20261012-00001','3605264-1101757346-10(3-3400723)','PT. VICTORY CHINGLUH INDONESIA',3,61.00,'finished','2026-10-12 17:52:10','2026-10-12 17:52:53',NULL,NULL,NULL,NULL,NULL,9,NULL),
(10,'FG-261013000002','WIP-20261013-00002','PO-THIPM26100508','PT. ADIS DIMENSION FOOTWEAR',4,111.00,'finished','2026-10-13 11:04:29','2026-10-13 11:09:38',NULL,NULL,NULL,NULL,NULL,14,NULL),
(11,'FG-261013000004','WIP-20261013-00002','PO-THIPM26100602','PT. ADIS DIMENSION FOOTWEAR',1,500.00,'finished','2026-10-13 11:07:53','2026-10-13 11:08:49',NULL,NULL,NULL,NULL,NULL,14,NULL),
(12,'FG-261014000003','WIP-20261014-00002','PO-THIPM26101401','PT. ADIS DIMENSION FOOTWEAR',2,500.00,'finished','2026-10-14 23:01:44','2026-10-14 23:02:52',NULL,NULL,NULL,NULL,NULL,16,NULL),
(13,'FG-261014000007','WIP-20261014-00001','PO-THIPM26101401','PT. ADIS DIMENSION FOOTWEAR',3,1000.00,'finished','2026-10-14 23:02:59','2026-10-14 23:03:29',NULL,NULL,NULL,NULL,NULL,15,NULL),
(14,'TWH-P-2','TWH-WIP-2','NIKOMAS 123','PT. NIKOMAS GEMILANG (IY)',1,800.00,'finished','2026-10-14 23:06:04','2026-10-14 23:06:04',NULL,NULL,NULL,NULL,NULL,17,NULL),
(15,'TWH-P-3','TWH-WIP-3','METRO123','PT. METRO PEARL INDONESIA (NB)',1,598.40,'finished','2026-10-14 23:06:04','2026-10-14 23:06:04',NULL,NULL,NULL,NULL,NULL,18,NULL),
(16,'TWH-P-4','TWH-WIP-4','METRO123','PT. METRO PEARL INDONESIA (NB)',1,800.00,'finished','2026-10-14 23:06:04','2026-10-14 23:06:04',NULL,NULL,NULL,NULL,NULL,19,NULL),
(17,'TWH-P-9','TWH-WIP-9','PO-PS26100504','PT. LONG RICH INDONESIA ADIDAS',1,393.60,'finished','2026-10-14 23:06:04','2026-10-14 23:06:04',NULL,NULL,NULL,NULL,NULL,20,NULL),
(18,'TWH-P-12','TWH-WIP-12','PO#00596~00611-12-10 0292/PO-SAI/X/2026','PT. SUKSES ABADI INDONESIA',1,409.20,'finished','2026-10-14 23:06:04','2026-10-14 23:06:04',NULL,NULL,NULL,NULL,NULL,21,NULL),
(19,'TWH-P-14','TWH-WIP-14','PO-THIPM26100603','PT. ADIS DIMENSION FOOTWEAR',1,400.00,'finished','2026-10-14 23:06:04','2026-10-14 23:06:04',NULL,NULL,NULL,NULL,NULL,22,NULL),
(20,'TWH-P-15','TWH-WIP-15','4000842518 MB020029174','PT. NIKOMAS GEMILANG (IY)',1,48.80,'finished','2026-10-14 23:06:04','2026-10-14 23:06:04',NULL,NULL,NULL,NULL,NULL,23,NULL),
(21,'TWH-P-16','TWH-WIP-16','4000842519 MB020000523','PT. NIKOMAS GEMILANG (IY)',1,727.20,'finished','2026-10-14 23:06:04','2026-10-14 23:06:04',NULL,NULL,NULL,NULL,NULL,24,NULL),
(22,'TWH-P-17','TWH-WIP-17','aaa','PT. LONG RICH INDONESIA ADIDAS',1,4.00,'finished','2026-10-14 23:06:04','2026-10-14 23:06:04',NULL,NULL,NULL,NULL,NULL,25,NULL),
(23,'TWH-P-18','TWH-WIP-18','PO-THIPM26101401','PT. ADIS DIMENSION FOOTWEAR',1,200.00,'finished','2026-10-14 23:06:04','2026-10-14 23:06:04',NULL,NULL,NULL,NULL,NULL,26,NULL),
(24,'FG-261015000027','WIP-20261015-00001','PS26101502','PT. LONG RICH INDONESIA ADIDAS',27,1000.00,'finished','2026-10-15 23:07:37','2026-10-15 23:33:00',NULL,NULL,NULL,NULL,NULL,27,NULL);
/*!40000 ALTER TABLE `tbl_packing` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_packing_inbound`
--

DROP TABLE IF EXISTS `tbl_packing_inbound`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_packing_inbound` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_dokumen` varchar(40) NOT NULL,
  `jenis` enum('kulit','rp','kimia') NOT NULL,
  `nomor_packing` varchar(80) DEFAULT NULL,
  `tanggal` date DEFAULT NULL,
  `supplier_name` varchar(150) DEFAULT NULL,
  `container_no` varchar(80) DEFAULT NULL,
  `invoice_no` varchar(80) DEFAULT NULL,
  `currency` varchar(10) DEFAULT 'USD',
  `source_filename` varchar(255) DEFAULT NULL,
  `status` enum('draft','posted','cancelled') NOT NULL DEFAULT 'draft',
  `posted_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_dokumen` (`kode_dokumen`),
  KEY `idx_pli_jenis` (`jenis`),
  KEY `idx_pli_status` (`status`),
  KEY `idx_pli_tanggal` (`tanggal`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_packing_inbound`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_packing_inbound` WRITE;
/*!40000 ALTER TABLE `tbl_packing_inbound` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_packing_inbound` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_packing_inbound_line`
--

DROP TABLE IF EXISTS `tbl_packing_inbound_line`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_packing_inbound_line` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `packing_inbound_id` int(11) NOT NULL,
  `item_name` varchar(255) DEFAULT NULL,
  `item_code_src` varchar(80) DEFAULT NULL,
  `qty` decimal(14,3) DEFAULT NULL,
  `qty_unit` varchar(20) DEFAULT NULL,
  `kemasan` int(11) DEFAULT NULL,
  `unit_price` decimal(14,4) DEFAULT NULL,
  `amount` decimal(14,4) DEFAULT NULL,
  `remark` varchar(255) DEFAULT NULL,
  `match_status` varchar(20) DEFAULT 'unmatched',
  `erp_material_id` bigint(20) DEFAULT NULL,
  `kode_material` varchar(50) DEFAULT NULL,
  `nama_material` varchar(255) DEFAULT NULL,
  `kode_yl` varchar(50) DEFAULT NULL,
  `thickness` varchar(50) DEFAULT NULL,
  `warna` varchar(120) DEFAULT NULL,
  `pcs` decimal(12,2) DEFAULT NULL,
  `net_weight` decimal(12,2) DEFAULT NULL,
  `gross_weight` decimal(12,2) DEFAULT NULL,
  `tekstur` varchar(120) DEFAULT NULL,
  `size_grade` varchar(120) DEFAULT NULL,
  `emboss` varchar(80) DEFAULT NULL,
  `finish` varchar(80) DEFAULT NULL,
  `size_width` decimal(10,3) DEFAULT NULL,
  `jenis_kode` varchar(10) DEFAULT NULL,
  `jenis_nama` varchar(80) DEFAULT NULL,
  `posted_ref` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_pli_line_doc` (`packing_inbound_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_packing_inbound_line`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_packing_inbound_line` WRITE;
/*!40000 ALTER TABLE `tbl_packing_inbound_line` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_packing_inbound_line` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_packing_po`
--

DROP TABLE IF EXISTS `tbl_packing_po`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_packing_po` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `packing_id` int(11) NOT NULL,
  `po_id` int(11) DEFAULT NULL,
  `no_po` varchar(50) NOT NULL,
  `no_so` varchar(50) DEFAULT NULL,
  `qty_sq` decimal(12,2) DEFAULT 0.00,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_packing_po`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_packing_po` WRITE;
/*!40000 ALTER TABLE `tbl_packing_po` DISABLE KEYS */;
INSERT INTO `tbl_packing_po` VALUES
(1,1,1,'NIKOMAS 123','PS26100201',5000.00),
(2,2,1,'NIKOMAS 123','PS26100201',5000.00),
(3,3,4,'TEST 3/10/26','THIPM26100301',1000.00),
(4,4,4,'TEST 3/10/26','THIPM26100301',1000.00),
(5,5,4,'TEST 3/10/26','THIPM26100301',1000.00),
(6,6,9,'PO-THIPM26100601','THIPM26100601',1000.00),
(7,7,9,'PO-THIPM26100601','THIPM26100601',2000.00),
(8,8,5,'W26B773 220NU','THIPM26100501',60.00),
(9,9,6,'3605264-1101757346-10(3-3400723)','THIPM26100502',161.00),
(10,10,8,'PO-THIPM26100508','THIPM26100508',111.00),
(11,11,11,'PO-THIPM26100602','THIPM26100602',1000.00),
(12,12,18,'PO-THIPM26101401','THIPM26101401',500.00),
(13,13,17,'PO-THIPM26101401','THIPM26101401',1000.00),
(14,14,2,'NIKOMAS 123','PS26100201',800.00),
(15,15,3,'METRO123','PS26100202',598.40),
(16,16,19,'METRO123','PS26100202',800.00),
(17,17,7,'PO-PS26100504','PS26100504',393.60),
(18,18,10,'PO#00596~00611-12-10 0292/PO-SAI/X/2026','PS26100601',409.20),
(19,19,12,'PO-THIPM26100603','THIPM26100603',400.00),
(20,20,13,'4000842518 MB020029174','THIPM26100701',48.80),
(21,21,14,'4000842519 MB020000523','THIPM26100702',727.20),
(22,22,15,'aaa','THIPM26101301',4.00),
(23,23,16,'PO-THIPM26101401','THIPM26101401',200.00),
(24,24,21,'PS26101502','PS26101502',1000.00);
/*!40000 ALTER TABLE `tbl_packing_po` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_packing_roll`
--

DROP TABLE IF EXISTS `tbl_packing_roll`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_packing_roll` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `packing_id` int(11) NOT NULL,
  `roll_no` int(11) NOT NULL,
  `lembar` int(11) DEFAULT 1,
  `ukuran` decimal(12,2) DEFAULT 0.00,
  `created_at` datetime DEFAULT current_timestamp(),
  `remark` varchar(255) DEFAULT NULL,
  `kode_packing` varchar(30) DEFAULT NULL,
  `sizes_text` varchar(500) DEFAULT NULL,
  `impactiva_grading` varchar(120) DEFAULT NULL,
  `moisture` varchar(40) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `packing_id` (`packing_id`),
  CONSTRAINT `tbl_packing_roll_ibfk_1` FOREIGN KEY (`packing_id`) REFERENCES `tbl_packing` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=62 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_packing_roll`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_packing_roll` WRITE;
/*!40000 ALTER TABLE `tbl_packing_roll` DISABLE KEYS */;
INSERT INTO `tbl_packing_roll` VALUES
(1,1,1,1,1000.00,'2026-10-02 10:56:42',NULL,'FG-261002000001','1000',NULL,NULL),
(2,1,2,1,1500.00,'2026-10-02 10:56:51',NULL,'FG-261002000002','1500',NULL,NULL),
(3,1,3,1,500.00,'2026-10-02 10:57:01',NULL,'FG-261002000003','500',NULL,NULL),
(4,2,1,2,1200.00,'2026-10-02 11:03:01',NULL,'FG-261002000005','1000+200',NULL,NULL),
(5,2,2,1,800.00,'2026-10-02 11:03:12',NULL,'FG-261002000006','800',NULL,NULL),
(6,3,1,1,1000.00,'2026-10-03 16:20:36',NULL,'FG-261003000001','1000',NULL,NULL),
(7,4,1,1,100.00,'2026-10-03 16:25:37',NULL,'FG-261003000003','100',NULL,NULL),
(8,4,2,1,200.00,'2026-10-03 16:26:09',NULL,'FG-261003000004','200',NULL,NULL),
(9,5,1,1,500.00,'2026-10-03 16:29:49',NULL,'FG-261003000006','500',NULL,NULL),
(10,5,2,1,500.00,'2026-10-03 16:30:10',NULL,'FG-261003000007','500',NULL,NULL),
(11,6,1,2,900.00,'2026-10-06 14:18:37',NULL,'FG-261006000001','800+100',NULL,NULL),
(12,6,2,1,100.00,'2026-10-06 14:19:09',NULL,'FG-261006000002','100',NULL,NULL),
(13,7,1,1,500.00,'2026-10-06 14:21:47',NULL,'FG-261006000004','500',NULL,NULL),
(14,8,1,4,68.00,'2026-10-12 17:31:19',NULL,'FG-261012000001','16+20+17+15',NULL,NULL),
(15,9,1,3,61.00,'2026-10-12 17:52:31',NULL,'FG-261012000003','22+18+21',NULL,NULL),
(16,7,2,4,69.00,'2026-10-12 17:54:20',NULL,'FG-261006000005','15+17+18+19',NULL,NULL),
(17,7,3,3,60.00,'2026-10-12 17:56:12',NULL,'FG-261012000005','20+18+22',NULL,NULL),
(18,7,4,1,1369.00,'2026-10-12 18:10:22',NULL,'FG-261012000006','1369',NULL,NULL),
(19,10,1,4,111.00,'2026-10-13 11:05:23',NULL,'FG-261013000001','15+30+40+26',NULL,NULL),
(20,11,1,1,500.00,'2026-10-13 11:08:02',NULL,'FG-261013000003','500',NULL,NULL),
(21,12,1,1,200.00,'2026-10-14 23:01:54',NULL,'FG-261014000001','200',NULL,NULL),
(22,12,2,1,300.00,'2026-10-14 23:02:47',NULL,'FG-261014000002','300',NULL,NULL),
(23,13,1,1,200.00,'2026-10-14 23:03:06',NULL,'FG-261014000004','200',NULL,NULL),
(24,13,2,1,300.00,'2026-10-14 23:03:14',NULL,'FG-261014000005','300',NULL,NULL),
(25,13,3,1,500.00,'2026-10-14 23:03:24',NULL,'FG-261014000006','500',NULL,NULL),
(26,14,1,1,800.00,'2026-10-14 23:06:04','seed test stock WH','TWH-P-2',NULL,NULL,NULL),
(27,15,1,1,598.40,'2026-10-14 23:06:04','seed test stock WH','TWH-P-3',NULL,NULL,NULL),
(28,16,1,1,800.00,'2026-10-14 23:06:04','seed test stock WH','TWH-P-4',NULL,NULL,NULL),
(29,17,1,1,393.60,'2026-10-14 23:06:04','seed test stock WH','TWH-P-9',NULL,NULL,NULL),
(30,18,1,1,409.20,'2026-10-14 23:06:04','seed test stock WH','TWH-P-12',NULL,NULL,NULL),
(31,19,1,1,400.00,'2026-10-14 23:06:04','seed test stock WH','TWH-P-14',NULL,NULL,NULL),
(32,20,1,1,48.80,'2026-10-14 23:06:04','seed test stock WH','TWH-P-15',NULL,NULL,NULL),
(33,21,1,1,727.20,'2026-10-14 23:06:04','seed test stock WH','TWH-P-16',NULL,NULL,NULL),
(34,22,1,1,4.00,'2026-10-14 23:06:04','seed test stock WH','TWH-P-17',NULL,NULL,NULL),
(35,23,1,1,200.00,'2026-10-14 23:06:04','seed test stock WH','TWH-P-18',NULL,NULL,NULL),
(36,24,1,1,10.00,'2026-10-15 23:07:49',NULL,'FG-261015000001','10',NULL,NULL),
(37,24,2,1,10.00,'2026-10-15 23:10:42',NULL,'FG-261015000002','10',NULL,NULL),
(38,24,3,1,10.00,'2026-10-15 23:10:50',NULL,'FG-261015000003','10',NULL,NULL),
(39,24,4,1,10.00,'2026-10-15 23:11:00',NULL,'FG-261015000004','10',NULL,NULL),
(40,24,5,1,10.00,'2026-10-15 23:12:28',NULL,'FG-261015000005','10',NULL,NULL),
(41,24,6,1,10.00,'2026-10-15 23:12:34',NULL,'FG-261015000006','10',NULL,NULL),
(42,24,7,1,10.00,'2026-10-15 23:12:43',NULL,'FG-261015000007','10',NULL,NULL),
(43,24,8,1,10.00,'2026-10-15 23:14:14',NULL,'FG-261015000008','10',NULL,NULL),
(44,24,9,1,10.00,'2026-10-15 23:15:37',NULL,'FG-261015000009','10',NULL,NULL),
(45,24,10,1,10.00,'2026-10-15 23:16:18',NULL,'FG-261015000010','10',NULL,NULL),
(46,24,11,1,10.00,'2026-10-15 23:16:38',NULL,'FG-261015000011','10',NULL,NULL),
(47,24,12,1,10.00,'2026-10-15 23:18:14',NULL,'FG-261015000012','10',NULL,NULL),
(48,24,13,1,10.00,'2026-10-15 23:18:20',NULL,'FG-261015000013','10',NULL,NULL),
(49,24,14,1,10.00,'2026-10-15 23:18:26',NULL,'FG-261015000014','10',NULL,NULL),
(50,24,15,1,10.00,'2026-10-15 23:18:32',NULL,'FG-261015000015','10',NULL,NULL),
(51,24,16,1,10.00,'2026-10-15 23:18:39',NULL,'FG-261015000016','10',NULL,NULL),
(52,24,17,1,10.00,'2026-10-15 23:18:47',NULL,'FG-261015000017','10',NULL,NULL),
(53,24,18,1,10.00,'2026-10-15 23:19:00',NULL,'FG-261015000018','10',NULL,NULL),
(54,24,19,1,10.00,'2026-10-15 23:19:07',NULL,'FG-261015000019','10',NULL,NULL),
(55,24,20,1,10.00,'2026-10-15 23:19:14',NULL,'FG-261015000020','10',NULL,NULL),
(56,24,21,1,10.00,'2026-10-15 23:19:23',NULL,'FG-261015000021','10',NULL,NULL),
(57,24,22,1,10.00,'2026-10-15 23:19:43',NULL,'FG-261015000022','10',NULL,NULL),
(58,24,23,1,10.00,'2026-10-15 23:30:04',NULL,'FG-261015000023','10',NULL,NULL),
(59,24,24,2,20.00,'2026-10-15 23:32:30',NULL,'FG-261015000024','10+10',NULL,NULL),
(60,24,25,1,250.00,'2026-10-15 23:32:43',NULL,'FG-261015000025','250',NULL,NULL),
(61,24,26,1,500.00,'2026-10-15 23:32:54',NULL,'FG-261015000026','500',NULL,NULL);
/*!40000 ALTER TABLE `tbl_packing_roll` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_palet_movement`
--

DROP TABLE IF EXISTS `tbl_palet_movement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_palet_movement` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_palet` varchar(50) NOT NULL COMMENT 'KY',
  `direction` enum('IN','OUT') NOT NULL,
  `tanggal` date NOT NULL,
  `keterangan` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `packing_inbound_id` int(11) DEFAULT NULL,
  `packing_inbound_line_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_kode_palet` (`kode_palet`),
  KEY `idx_tanggal` (`tanggal`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_palet_movement`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_palet_movement` WRITE;
/*!40000 ALTER TABLE `tbl_palet_movement` DISABLE KEYS */;
INSERT INTO `tbl_palet_movement` VALUES
(1,'KY-TEST TH 001','IN','2026-10-02',NULL,'2026-10-02 10:30:35',NULL,NULL),
(2,'KY-TEST TH 002','IN','2026-10-02',NULL,'2026-10-02 10:32:35',NULL,NULL),
(3,'KY-TEST TH 003','IN','2026-10-02',NULL,'2026-10-02 10:32:46',NULL,NULL),
(4,'KY-TEST 3/10/26','IN','2026-10-03','TEST KY','2026-10-03 16:22:20',NULL,NULL),
(5,'KY-TEST 3/10/26 02','IN','2026-10-03',NULL,'2026-10-03 16:27:43',NULL,NULL),
(6,'KY-TEST 10/6/26 001','IN','2026-10-06','TEST','2026-10-06 14:14:41',NULL,NULL),
(7,'KY-1001','IN','2026-10-12',NULL,'2026-10-12 17:13:52',NULL,NULL),
(8,'KY-1002','IN','2026-10-12',NULL,'2026-10-12 17:18:11',NULL,NULL);
/*!40000 ALTER TABLE `tbl_palet_movement` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_persiapan_kulit`
--

DROP TABLE IF EXISTS `tbl_persiapan_kulit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_persiapan_kulit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_wip` varchar(30) NOT NULL,
  `kode_rencana` varchar(30) NOT NULL,
  `kode_proses` varchar(30) NOT NULL,
  `no_po` varchar(500) DEFAULT NULL,
  `warna` varchar(100) DEFAULT NULL,
  `tebal` varchar(30) DEFAULT NULL,
  `emboss` varchar(100) DEFAULT NULL,
  `lebar` varchar(30) DEFAULT NULL,
  `treatment_jenis` enum('PU','Suede') DEFAULT NULL,
  `treatment_list` text DEFAULT NULL,
  `total_size` decimal(12,2) DEFAULT 0.00,
  `status` enum('draft','started','saved','completed','voided') DEFAULT 'draft',
  `date_created` datetime DEFAULT current_timestamp(),
  `date_saved` datetime DEFAULT NULL,
  `rencana_item_id` int(11) DEFAULT NULL,
  `checkpoint_status` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_proses` (`kode_proses`),
  KEY `idx_kode_wip` (`kode_wip`),
  KEY `idx_kode_rencana` (`kode_rencana`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_persiapan_kulit`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_persiapan_kulit` WRITE;
/*!40000 ALTER TABLE `tbl_persiapan_kulit` DISABLE KEYS */;
INSERT INTO `tbl_persiapan_kulit` VALUES
(1,'WIP-20261002-00001','RPI-261002000001','PR-261002000001','NIKOMAS 123','UNIVERSITY RED (65N) FLUORESCENT','1.2 - 1.4','R-8 M',NULL,'PU','PU - Emboss',3000.00,'completed','2026-10-02 10:55:58','2026-10-02 10:56:16',1,NULL),
(2,'WIP-20261002-00002','RPI-261002000001','PR-261002000002','NIKOMAS 123','UNIVERSITY RED (65N) FLUORESCENT','1.2 - 1.4','R-8 M',NULL,'PU','PU - Emboss',2000.00,'completed','2026-10-02 11:01:49','2026-10-02 11:02:25',1,NULL),
(3,'WIP-20261003-00001','RPI-261003000001','PR-261003000001','TEST 3/10/26','ATOMIC VIOLET (55V)','1.2 - 1.4','AR-20 M',NULL,'PU','PU - Emboss',1000.00,'completed','2026-10-03 16:19:12','2026-10-03 16:24:04',2,NULL),
(4,'WIP-20261003-00002','RPI-261003000001','PR-261003000002','TEST 3/10/26','ATOMIC VIOLET (55V)','1.2 - 1.4','AR-20 M',NULL,'PU','PU - Emboss',300.00,'completed','2026-10-03 16:22:54','2026-10-03 16:23:27',2,NULL),
(5,'WIP-20261003-00003','RPI-261003000001','PR-261003000003','TEST 3/10/26','ATOMIC VIOLET (55V)','1.2 - 1.4','AR-20 M',NULL,'PU','PU - Emboss',1000.00,'completed','2026-10-03 16:28:14','2026-10-03 16:28:46',2,NULL),
(6,'WIP-20261006-00001','RPI-261006000001','PR-261006000001','PO-THIPM26100601','ATOMIC VIOLET (55V)','1.2 - 1.4','AR-20 M',NULL,'PU','PU - Emboss',1000.00,'completed','2026-10-06 14:16:21','2026-10-06 14:17:03',3,NULL),
(7,'WIP-20261006-00002','RPI-261006000002','PR-261006000002','PO-THIPM26100601','ATOMIC VIOLET (55V)','1.2 - 1.4','AR-20 M',NULL,'PU','PU - Emboss',2000.00,'completed','2026-10-06 14:21:13','2026-10-06 14:21:24',4,NULL),
(8,'WIP-20261012-00001','RPI-261012000001','PR-261012000001','3605264-1101757346-10(3-3400723)','OBSIDIAN (45B)','1.2 - 1.4','AR-20 M',NULL,'PU','PU - Press, PU - Rotopia A',161.00,'started','2026-10-12 15:42:22',NULL,9,NULL),
(9,'WIP-20261012-00002','RPI-261012000002','PR-261012000002','W26B773 220NU','BLACK (00A)','1.4 - 1.6','AR-144 M',NULL,'PU','PU - Press, PU - Rotopia A',68.00,'completed','2026-10-12 17:24:05','2026-10-12 17:32:36',10,NULL),
(10,'WIP-20261013-00001','RPI-261013000003','PR-261013000001','PO-THIPM26100508, PO-THIPM26100602','ATOMIC VIOLET (55V)','1.2 - 1.4','AR-20 M',NULL,'PU','PU - Rotopia A, PU - Rotopia B',77.00,'completed','2026-10-13 10:34:13','2026-10-13 10:34:33',14,NULL),
(11,'WIP-20261013-00002','RPI-261013000003','PR-261013000002','PO-THIPM26100508, PO-THIPM26100602','ATOMIC VIOLET (55V)','1.2 - 1.4','AR-20 M',NULL,'PU','PU - Press, PU - Spray 1, PU - Spray 2, PU - Spray 3, PU - Rotopia A',1200.00,'completed','2026-10-13 10:44:48','2026-10-13 10:46:22',14,NULL),
(12,'WIP-20261014-00001','RPI-261014000001','PR-261014000001','PO-THIPM26101401','ARMORY NAVY (4LX)','1.2 - 1.4','R-102 M',NULL,'PU','PU - Spray 1',1000.00,'completed','2026-10-14 22:59:07','2026-10-14 23:00:09',15,NULL),
(13,'WIP-20261014-00002','RPI-261014000002','PR-261014000002','PO-THIPM26101401','ATOMIC VIOLET (55V)','1.2 - 1.4','AR-20 M',NULL,'PU','PU - Spray 1',500.00,'completed','2026-10-14 23:00:34','2026-10-14 23:00:44',16,NULL),
(14,'TWH-WIP-2','TWH-R-2','TWH-PR-2','NIKOMAS 123',NULL,NULL,NULL,NULL,NULL,NULL,1200.00,'started','2026-10-14 23:06:04',NULL,17,NULL),
(15,'TWH-WIP-3','TWH-R-3','TWH-PR-3','METRO123',NULL,NULL,NULL,NULL,NULL,NULL,897.60,'started','2026-10-14 23:06:04',NULL,18,NULL),
(16,'TWH-WIP-4','TWH-R-4','TWH-PR-4','METRO123',NULL,NULL,NULL,NULL,NULL,NULL,1200.00,'started','2026-10-14 23:06:04',NULL,19,NULL),
(17,'TWH-WIP-9','TWH-R-9','TWH-PR-9','PO-PS26100504',NULL,NULL,NULL,NULL,NULL,NULL,590.40,'started','2026-10-14 23:06:04',NULL,20,NULL),
(18,'TWH-WIP-12','TWH-R-12','TWH-PR-12','PO#00596~00611-12-10 0292/PO-SAI/X/2026',NULL,NULL,NULL,NULL,NULL,NULL,613.80,'started','2026-10-14 23:06:04',NULL,21,NULL),
(19,'TWH-WIP-14','TWH-R-14','TWH-PR-14','PO-THIPM26100603',NULL,NULL,NULL,NULL,NULL,NULL,600.00,'started','2026-10-14 23:06:04',NULL,22,NULL),
(20,'TWH-WIP-15','TWH-R-15','TWH-PR-15','4000842518 MB020029174',NULL,NULL,NULL,NULL,NULL,NULL,73.20,'started','2026-10-14 23:06:04',NULL,23,NULL),
(21,'TWH-WIP-16','TWH-R-16','TWH-PR-16','4000842519 MB020000523',NULL,NULL,NULL,NULL,NULL,NULL,1090.80,'started','2026-10-14 23:06:04',NULL,24,NULL),
(22,'TWH-WIP-17','TWH-R-17','TWH-PR-17','aaa',NULL,NULL,NULL,NULL,NULL,NULL,6.00,'started','2026-10-14 23:06:04',NULL,25,NULL),
(23,'TWH-WIP-18','TWH-R-18','TWH-PR-18','PO-THIPM26101401',NULL,NULL,NULL,NULL,NULL,NULL,300.00,'started','2026-10-14 23:06:04',NULL,26,NULL),
(24,'WIP-20261015-00001','RPI-261015000001','PR-261015000001','PS26101502','COLLEGIATE GREEN (024A)','1.2 - 1.4','-',NULL,'PU','PU - Spray 1',1000.00,'completed','2026-10-15 23:05:06','2026-10-15 23:07:24',27,NULL);
/*!40000 ALTER TABLE `tbl_persiapan_kulit` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_persiapan_ky`
--

DROP TABLE IF EXISTS `tbl_persiapan_ky`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_persiapan_ky` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `persiapan_id` int(11) NOT NULL,
  `kode_palet` varchar(50) NOT NULL,
  `kode_yl` varchar(50) DEFAULT NULL,
  `target_qty` decimal(12,2) DEFAULT 0.00,
  `actual_qty` decimal(12,2) DEFAULT 0.00,
  `status` enum('planned','active','selesai') DEFAULT 'planned',
  `created_at` datetime DEFAULT current_timestamp(),
  `yl_consumed` tinyint(1) NOT NULL DEFAULT 0,
  `qty_consumed` decimal(12,2) NOT NULL DEFAULT 0.00,
  `tidak_ada_sisa` tinyint(1) NOT NULL DEFAULT 0,
  `gudang_mod_id` int(11) DEFAULT NULL COMMENT 'Sumber stok Gudang MOD',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_persiapan_ky`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_persiapan_ky` WRITE;
/*!40000 ALTER TABLE `tbl_persiapan_ky` DISABLE KEYS */;
INSERT INTO `tbl_persiapan_ky` VALUES
(1,1,'KY-TEST TH 001','MCL-00A-123',2000.00,2000.00,'selesai','2026-10-02 10:55:58',1,2000.00,0,NULL),
(2,1,'KY-TEST TH 002','MCL-00A-123',2000.00,1000.00,'selesai','2026-10-02 10:55:58',1,1000.00,0,NULL),
(3,2,'KY-TEST TH 003','MCL-00A-123',2000.00,2000.00,'selesai','2026-10-02 11:01:49',1,2000.00,0,NULL),
(4,3,'KY-TEST TH 002','MCL-00A-123',1000.00,1000.00,'selesai','2026-10-03 16:19:12',1,1000.00,0,NULL),
(5,4,'KY-TEST 3/10/26','MCL-00A-123',300.00,300.00,'selesai','2026-10-03 16:22:54',1,300.00,0,NULL),
(6,5,'KY-TEST 3/10/26 02','MCL-00A-123',1000.00,1000.00,'selesai','2026-10-03 16:28:14',1,1000.00,0,NULL),
(7,6,'KY-TEST 10/6/26 001','MCL-00A-123',5000.00,1000.00,'selesai','2026-10-06 14:16:21',1,1000.00,0,NULL),
(8,7,'KY-TEST 10/6/26 001','MCL-00A-123',4000.00,2000.00,'selesai','2026-10-06 14:21:13',1,2000.00,0,NULL),
(9,8,'KY-TEST 10/6/26 001','MCL-00A-123',161.00,161.00,'selesai','2026-10-12 15:42:22',1,161.00,0,NULL),
(10,9,'KY-1002','MCL-00A-102',5000.00,68.00,'selesai','2026-10-12 17:24:05',1,68.00,0,NULL),
(11,10,'KY-TEST 10/6/26 001','MCL-00A-123',1839.00,77.00,'selesai','2026-10-13 10:34:13',1,77.00,0,NULL),
(12,11,'KY-TEST 10/6/26 001','MCL-00A-123',1200.00,1200.00,'selesai','2026-10-13 10:44:48',1,1200.00,0,NULL),
(13,12,'KY-1001','MCL-01V-134',10000.00,1000.00,'selesai','2026-10-14 22:59:07',1,1000.00,0,NULL),
(14,13,'KY-1001','MCL-01V-134',9000.00,500.00,'selesai','2026-10-14 23:00:34',1,500.00,0,NULL),
(15,24,'KY-1001','MCL-01V-134',8500.00,1000.00,'selesai','2026-10-15 23:05:06',1,1000.00,0,NULL);
/*!40000 ALTER TABLE `tbl_persiapan_ky` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_persiapan_reprint`
--

DROP TABLE IF EXISTS `tbl_persiapan_reprint`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_persiapan_reprint` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `persiapan_id` int(11) NOT NULL,
  `reprint_ke` int(11) NOT NULL DEFAULT 1,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `persiapan_id` (`persiapan_id`),
  CONSTRAINT `tbl_persiapan_reprint_ibfk_1` FOREIGN KEY (`persiapan_id`) REFERENCES `tbl_persiapan_kulit` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_persiapan_reprint`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_persiapan_reprint` WRITE;
/*!40000 ALTER TABLE `tbl_persiapan_reprint` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_persiapan_reprint` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_persiapan_scan`
--

DROP TABLE IF EXISTS `tbl_persiapan_scan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_persiapan_scan` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `persiapan_id` int(11) NOT NULL,
  `kode_palet` varchar(50) NOT NULL,
  `kode_yl` varchar(50) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `target_qty` decimal(12,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `persiapan_id` (`persiapan_id`),
  CONSTRAINT `tbl_persiapan_scan_ibfk_1` FOREIGN KEY (`persiapan_id`) REFERENCES `tbl_persiapan_kulit` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_persiapan_scan`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_persiapan_scan` WRITE;
/*!40000 ALTER TABLE `tbl_persiapan_scan` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_persiapan_scan` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_persiapan_ukur`
--

DROP TABLE IF EXISTS `tbl_persiapan_ukur`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_persiapan_ukur` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `persiapan_id` int(11) NOT NULL,
  `size_val` decimal(12,2) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `ky_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `persiapan_id` (`persiapan_id`),
  CONSTRAINT `tbl_persiapan_ukur_ibfk_1` FOREIGN KEY (`persiapan_id`) REFERENCES `tbl_persiapan_kulit` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_persiapan_ukur`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_persiapan_ukur` WRITE;
/*!40000 ALTER TABLE `tbl_persiapan_ukur` DISABLE KEYS */;
INSERT INTO `tbl_persiapan_ukur` VALUES
(1,1,2000.00,'2026-10-02 10:56:02',1),
(2,1,1000.00,'2026-10-02 10:56:05',2),
(3,2,2000.00,'2026-10-02 11:01:54',3),
(4,3,1000.00,'2026-10-03 16:19:15',4),
(5,4,300.00,'2026-10-03 16:23:00',5),
(6,5,1000.00,'2026-10-03 16:28:18',6),
(7,6,1000.00,'2026-10-06 14:16:24',7),
(8,7,2000.00,'2026-10-06 14:21:18',8),
(9,8,161.00,'2026-10-12 15:42:25',9),
(10,9,15.00,'2026-10-12 17:24:08',10),
(11,9,17.50,'2026-10-12 17:24:09',10),
(12,9,18.90,'2026-10-12 17:24:10',10),
(13,9,16.60,'2026-10-12 17:24:11',10),
(14,10,15.00,'2026-10-13 10:34:16',11),
(15,10,20.00,'2026-10-13 10:34:17',11),
(16,10,17.00,'2026-10-13 10:34:18',11),
(17,10,25.00,'2026-10-13 10:34:19',11),
(18,11,500.00,'2026-10-13 10:44:51',12),
(19,11,500.00,'2026-10-13 10:44:52',12),
(20,11,200.00,'2026-10-13 10:44:53',12),
(21,12,1000.00,'2026-10-14 22:59:10',13),
(22,13,500.00,'2026-10-14 23:00:37',14),
(23,24,1000.00,'2026-10-15 23:05:09',15);
/*!40000 ALTER TABLE `tbl_persiapan_ukur` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_proses_return`
--

DROP TABLE IF EXISTS `tbl_proses_return`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_proses_return` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `persiapan_id` int(11) NOT NULL,
  `ky_id` int(11) DEFAULT NULL,
  `kode_wip` varchar(30) NOT NULL,
  `kode_palet` varchar(50) NOT NULL COMMENT 'KY lama',
  `kode_yl_lama` varchar(50) NOT NULL,
  `kode_yl_baru` varchar(55) NOT NULL COMMENT 'YL lama + -R',
  `return_qty` decimal(12,2) NOT NULL DEFAULT 0.00,
  `treatment_list` text DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_proses_return_wip` (`kode_wip`),
  KEY `idx_proses_return_persiapan` (`persiapan_id`),
  KEY `idx_proses_return_ky` (`ky_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_proses_return`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_proses_return` WRITE;
/*!40000 ALTER TABLE `tbl_proses_return` DISABLE KEYS */;
INSERT INTO `tbl_proses_return` VALUES
(1,11,11,'WIP-20260923-00002','KY=TEST 20SEP26','PU','PU-R',10.00,'PU - Emboss','2026-09-23 22:41:54'),
(2,11,11,'WIP-20260923-00002','KY=TEST 20SEP26','PU','PU-R',10.00,'PU - Emboss','2026-09-23 22:58:11'),
(3,11,11,'WIP-20260923-00002','KY=TEST 20SEP26','PU','PU-R',20.00,'PU - Emboss','2026-09-28 22:32:31'),
(4,2,3,'WIP-20260930-00002','KY-TEST 30 SEPT 2026 001','MCL-00A-123','MCL-00A-123-R',300.00,'PU - Emboss','2026-09-30 12:23:31');
/*!40000 ALTER TABLE `tbl_proses_return` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_rencana_item`
--

DROP TABLE IF EXISTS `tbl_rencana_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_rencana_item` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `rencana_id` int(11) NOT NULL,
  `kode_rencana_item` varchar(30) NOT NULL,
  `kode_lot_wip` varchar(30) DEFAULT NULL,
  `customer_id` int(11) NOT NULL,
  `nama_customer` varchar(150) DEFAULT NULL,
  `kode_kulit` varchar(50) DEFAULT NULL,
  `thickness` varchar(30) DEFAULT NULL,
  `color` varchar(100) DEFAULT NULL,
  `emboss` varchar(100) DEFAULT NULL,
  `color_swatch` varchar(100) DEFAULT NULL,
  `keterangan` varchar(255) DEFAULT NULL,
  `urutan` int(11) DEFAULT 1,
  `created_at` datetime DEFAULT current_timestamp(),
  `backer` varchar(100) DEFAULT NULL,
  `kode_barcode` varchar(50) DEFAULT NULL,
  `material_name` varchar(150) DEFAULT NULL,
  `erp_production_id` bigint(20) DEFAULT NULL,
  `erp_production_detail_id` bigint(20) DEFAULT NULL,
  `print_qty` decimal(12,2) DEFAULT NULL,
  `print_schedule` varchar(80) DEFAULT NULL,
  `print_remarks` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_rencana_item` (`kode_rencana_item`),
  KEY `idx_rencana_item` (`rencana_id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_rencana_item`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_rencana_item` WRITE;
/*!40000 ALTER TABLE `tbl_rencana_item` DISABLE KEYS */;
INSERT INTO `tbl_rencana_item` VALUES
(1,1,'RPI-261002000001','WIP-261002000001',18,'PT. NIKOMAS GEMILANG (IY)',NULL,'1.2 - 1.4','UNIVERSITY RED (65N) FLUORESCENT','R-8 M',NULL,NULL,1,'2026-10-02 10:26:21',NULL,NULL,'(PM) GENERIC PU COATED LEATHER',NULL,NULL,NULL,NULL,NULL),
(2,2,'RPI-261003000001','WIP-261003000001',1,'PT. ADIS DIMENSION FOOTWEAR',NULL,'1.2 - 1.4','ATOMIC VIOLET (55V)','AR-20 M',NULL,NULL,1,'2026-10-03 16:18:43',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL,NULL,NULL,NULL),
(3,3,'RPI-261006000001','WIP-261006000001',1,'PT. ADIS DIMENSION FOOTWEAR',NULL,'1.2 - 1.4','ATOMIC VIOLET (55V)','AR-20 M',NULL,NULL,1,'2026-10-06 14:13:16',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL,NULL,NULL,NULL),
(4,4,'RPI-261006000002','WIP-261006000002',1,'PT. ADIS DIMENSION FOOTWEAR',NULL,'1.2 - 1.4','ATOMIC VIOLET (55V)','AR-20 M',NULL,NULL,1,'2026-10-06 14:13:53',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL,NULL,NULL,NULL),
(5,5,'RPI-261006000003','WIP-261006000003',44,'PT. LONG RICH INDONESIA ADIDAS',NULL,'1.2 - 1.4','ANTHRACITE (06F)','R-102 M',NULL,NULL,1,'2026-10-06 14:55:45',NULL,NULL,'ECO TECH COMFORT',NULL,NULL,NULL,NULL,NULL),
(6,5,'RPI-261006000004','WIP-261006000004',16,'PT. METRO PEARL INDONESIA (NB)',NULL,'1.2 - 1.4','MOONBEAM COLORO (026-79-03)','AR-100 M',NULL,NULL,2,'2026-10-06 14:55:49',NULL,NULL,'ECO GREEN RECYCLED LEATHER',NULL,NULL,NULL,NULL,NULL),
(7,5,'RPI-261006000005','WIP-261006000005',1,'PT. ADIS DIMENSION FOOTWEAR',NULL,'1.2 - 1.4','ATOMIC VIOLET (55V)','AR-20 M',NULL,NULL,3,'2026-10-06 14:55:53',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL,NULL,NULL,NULL),
(8,6,'RPI-261006000006','WIP-261006000006',1,'PT. ADIS DIMENSION FOOTWEAR',NULL,'1.2 - 1.4','ARCTIC GREEN (3KF)','R-131 M',NULL,NULL,1,'2026-10-06 21:48:06',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL,NULL,NULL,NULL),
(9,7,'RPI-261012000001','WIP-261012000001',31,'PT. VICTORY CHINGLUH INDONESIA',NULL,'1.2 - 1.4','OBSIDIAN (45B)','AR-20 M',NULL,NULL,1,'2026-10-12 15:40:13',NULL,NULL,'(PM) GENERIC PU COATED LEATHER',NULL,NULL,NULL,NULL,NULL),
(10,7,'RPI-261012000002','WIP-261012000002',8,'PT. FENG TAY INDONESIA ENTERPRISES (EAST)',NULL,'1.4 - 1.6','BLACK (00A)','AR-144 M',NULL,NULL,2,'2026-10-12 15:40:17',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL,NULL,NULL,NULL),
(11,7,'RPI-261012000003','WIP-261012000003',37,'PT. SUKSES ABADI INDONESIA',NULL,'1.2 - 1.4','BLACK (145-17-00)','R-53 SM',NULL,NULL,3,'2026-10-12 15:40:22',NULL,NULL,'HYDRO SOFT ACTION LEATHER',NULL,NULL,NULL,NULL,NULL),
(12,8,'RPI-261013000001','WIP-261013000001',18,'PT. NIKOMAS GEMILANG (IY)',NULL,'1.2 - 1.4','BLACK (00A)','R-131 M',NULL,NULL,1,'2026-10-13 10:30:17',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL,NULL,NULL,NULL),
(13,8,'RPI-261013000002','WIP-261013000002',18,'PT. NIKOMAS GEMILANG (IY)',NULL,'1.2 - 1.4','VOLT (71R) FLUORESCENT','R-131 M',NULL,NULL,2,'2026-10-13 10:30:22',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL,NULL,NULL,NULL),
(14,8,'RPI-261013000003','WIP-261013000003',1,'PT. ADIS DIMENSION FOOTWEAR',NULL,'1.2 - 1.4','ATOMIC VIOLET (55V)','AR-20 M',NULL,NULL,3,'2026-10-13 10:30:26',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL,NULL,NULL,NULL),
(15,9,'RPI-261014000001','WIP-261014000001',1,'PT. ADIS DIMENSION FOOTWEAR',NULL,'1.2 - 1.4','ARMORY NAVY (4LX)','R-102 M',NULL,NULL,1,'2026-10-14 22:58:29',NULL,NULL,'ECO TECH COMFORT',NULL,NULL,NULL,NULL,NULL),
(16,9,'RPI-261014000002','WIP-261014000002',1,'PT. ADIS DIMENSION FOOTWEAR',NULL,'1.2 - 1.4','ATOMIC VIOLET (55V)','AR-20 M',NULL,NULL,2,'2026-10-14 22:58:33',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL,NULL,NULL,NULL),
(17,10,'TWH-I-2','TWH-L-2',18,'PT. NIKOMAS GEMILANG (IY)',NULL,'1.2 - 1.4','TEAM RED (67P)',NULL,NULL,'seed test stock WH',1,'2026-10-14 23:06:04',NULL,NULL,'(PM) GENERIC SPLIT SUEDE',NULL,NULL,NULL,NULL,NULL),
(18,11,'TWH-I-3','TWH-L-3',16,'PT. METRO PEARL INDONESIA (NB)',NULL,'1.2 - 1.4','MOONBEAM COLORO (026-79-03)','AR-100 M',NULL,'seed test stock WH',1,'2026-10-14 23:06:04',NULL,NULL,'ECO GREEN RECYCLED LEATHER',NULL,NULL,NULL,NULL,NULL),
(19,12,'TWH-I-4','TWH-L-4',16,'PT. METRO PEARL INDONESIA (NB)',NULL,'1.2 - 1.4','MOONBEAM COLORO (026-79-03)','AR-100 M',NULL,'seed test stock WH',1,'2026-10-14 23:06:04',NULL,NULL,'ECO GREEN RECYCLED LEATHER',NULL,NULL,NULL,NULL,NULL),
(20,13,'TWH-I-9','TWH-L-9',44,'PT. LONG RICH INDONESIA ADIDAS',NULL,'1.2 - 1.4','ANTHRACITE (06F)','R-102 M',NULL,'seed test stock WH',1,'2026-10-14 23:06:04',NULL,NULL,'ECO TECH COMFORT',NULL,NULL,NULL,NULL,NULL),
(21,14,'TWH-I-12','TWH-L-12',37,'PT. SUKSES ABADI INDONESIA',NULL,'1.2 - 1.4','BLACK (145-17-00)','R-53 SM',NULL,'seed test stock WH',1,'2026-10-14 23:06:04',NULL,NULL,'HYDRO SOFT ACTION LEATHER',NULL,NULL,NULL,NULL,NULL),
(22,15,'TWH-I-14','TWH-L-14',1,'PT. ADIS DIMENSION FOOTWEAR',NULL,'1.2 - 1.4','ARCTIC GREEN (3KF)','R-131 M',NULL,'seed test stock WH',1,'2026-10-14 23:06:04',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL,NULL,NULL,NULL),
(23,16,'TWH-I-15','TWH-L-15',18,'PT. NIKOMAS GEMILANG (IY)',NULL,'1.2 - 1.4','VOLT (71R) FLUORESCENT','R-131 M',NULL,'seed test stock WH',1,'2026-10-14 23:06:04',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL,NULL,NULL,NULL),
(24,17,'TWH-I-16','TWH-L-16',18,'PT. NIKOMAS GEMILANG (IY)',NULL,'1.2 - 1.4','BLACK (00A)','R-131 M',NULL,'seed test stock WH',1,'2026-10-14 23:06:04',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL,NULL,NULL,NULL),
(25,18,'TWH-I-17','TWH-L-17',44,'PT. LONG RICH INDONESIA ADIDAS',NULL,'1.0 - 1.2','ANTHRACITE (016)','DE-172 SM',NULL,'seed test stock WH',1,'2026-10-14 23:06:04',NULL,NULL,'ACTION PU COATED LEATHER',NULL,NULL,NULL,NULL,NULL),
(26,19,'TWH-I-18','TWH-L-18',1,'PT. ADIS DIMENSION FOOTWEAR',NULL,'1.2 - 1.4','BARELY ROSE (6GW)','AR-20 M',NULL,'seed test stock WH',1,'2026-10-14 23:06:04',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL,NULL,NULL,NULL),
(27,20,'RPI-261015000001','WIP-261015000001',44,'PT. LONG RICH INDONESIA ADIDAS',NULL,'1.2 - 1.4','COLLEGIATE GREEN (024A)','-',NULL,NULL,1,'2026-10-15 23:04:41',NULL,NULL,'SPLIT SUEDE',NULL,NULL,1000.00,'10/11/26','TEST UPDATE'),
(28,21,'RPI-261015000002','WIP-261015000002',1,'PT. ADIS DIMENSION FOOTWEAR',NULL,'1.2 - 1.4','ADOBE (68I)','AR-196 M',NULL,NULL,1,'2026-10-15 23:06:46',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `tbl_rencana_item` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_rencana_item_po`
--

DROP TABLE IF EXISTS `tbl_rencana_item_po`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_rencana_item_po` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `item_id` int(11) NOT NULL,
  `po_id` int(11) NOT NULL,
  `qty_outstanding` decimal(12,2) DEFAULT 0.00,
  `qty_proses` decimal(12,2) DEFAULT 0.00,
  PRIMARY KEY (`id`),
  KEY `idx_item_po` (`item_id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_rencana_item_po`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_rencana_item_po` WRITE;
/*!40000 ALTER TABLE `tbl_rencana_item_po` DISABLE KEYS */;
INSERT INTO `tbl_rencana_item_po` VALUES
(2,1,1,5000.00,5000.00),
(3,2,4,1000.00,1000.00),
(4,3,9,5000.00,1000.00),
(5,4,9,4000.00,2000.00),
(6,5,7,984.00,984.00),
(7,6,3,1446.00,1446.00),
(8,7,9,2000.00,2000.00),
(9,8,12,1000.00,1000.00),
(10,9,6,161.00,161.00),
(11,10,5,60.00,60.00),
(12,11,10,1023.00,1023.00),
(13,12,14,1818.00,1818.00),
(14,13,13,122.00,122.00),
(15,14,11,1000.00,1000.00),
(16,14,8,111.00,111.00),
(17,15,17,1000.00,1000.00),
(18,16,18,500.00,500.00),
(19,17,2,2000.00,0.00),
(20,18,3,1496.00,0.00),
(21,19,19,2000.00,0.00),
(22,20,7,984.00,0.00),
(23,21,10,1023.00,0.00),
(24,22,12,1000.00,0.00),
(25,23,13,122.00,0.00),
(26,24,14,1818.00,0.00),
(27,25,15,10.00,0.00),
(28,26,16,500.00,0.00),
(30,28,20,1000.00,1000.00),
(31,27,21,1000.00,1000.00);
/*!40000 ALTER TABLE `tbl_rencana_item_po` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_rencana_produksi`
--

DROP TABLE IF EXISTS `tbl_rencana_produksi`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_rencana_produksi` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_rencana` varchar(30) NOT NULL,
  `kode_lot_wip` varchar(30) DEFAULT NULL,
  `nama_rencana` varchar(200) NOT NULL,
  `status` enum('draft','active','completed') DEFAULT 'draft',
  `date_created` datetime DEFAULT current_timestamp(),
  `tanggal_rencana` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_rencana` (`kode_rencana`),
  UNIQUE KEY `kode_lot_wip` (`kode_lot_wip`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_rencana_produksi`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_rencana_produksi` WRITE;
/*!40000 ALTER TABLE `tbl_rencana_produksi` DISABLE KEYS */;
INSERT INTO `tbl_rencana_produksi` VALUES
(1,'RP-261002000001',NULL,'TEST  2 OKT TH 002','active','2026-10-02 10:26:17','2026-10-02'),
(2,'RP-261003000001',NULL,'TEST RENCANA 3/10/26','active','2026-10-03 16:18:39','2026-10-03'),
(3,'RP-261006000001',NULL,'TEST TH 10/6/26 001','active','2026-10-06 14:13:12','2026-10-06'),
(4,'RP-261006000002',NULL,'TEST TH 10/6/26 002','active','2026-10-06 14:13:49','2026-10-06'),
(5,'RP-261006000003',NULL,'TEST 10/6/26 003','active','2026-10-06 14:55:40','2026-10-06'),
(6,'RP-261006000004',NULL,'TEST 6/10/26 003','active','2026-10-06 21:48:02','2026-10-06'),
(7,'RP-261012000001',NULL,'RENCANA PRODUKSI 13 OKTOBER 2026','active','2026-10-12 15:40:08','2026-10-13'),
(8,'RP-261013000001',NULL,'lll','active','2026-10-13 10:30:13','2026-10-13'),
(9,'RP-261014000001',NULL,'TEST 14 OKT','active','2026-10-14 22:58:24','2026-10-14'),
(10,'TWH-R-2','TWH-L-2','TEST STOCK WH PS26100201','active','2026-10-14 23:06:04','2026-10-14'),
(11,'TWH-R-3','TWH-L-3','TEST STOCK WH PS26100202','active','2026-10-14 23:06:04','2026-10-14'),
(12,'TWH-R-4','TWH-L-4','TEST STOCK WH PS26100202','active','2026-10-14 23:06:04','2026-10-14'),
(13,'TWH-R-9','TWH-L-9','TEST STOCK WH PS26100504','active','2026-10-14 23:06:04','2026-10-14'),
(14,'TWH-R-12','TWH-L-12','TEST STOCK WH PS26100601','active','2026-10-14 23:06:04','2026-10-14'),
(15,'TWH-R-14','TWH-L-14','TEST STOCK WH THIPM26100603','active','2026-10-14 23:06:04','2026-10-14'),
(16,'TWH-R-15','TWH-L-15','TEST STOCK WH THIPM26100701','active','2026-10-14 23:06:04','2026-10-14'),
(17,'TWH-R-16','TWH-L-16','TEST STOCK WH THIPM26100702','active','2026-10-14 23:06:04','2026-10-14'),
(18,'TWH-R-17','TWH-L-17','TEST STOCK WH THIPM26101301','active','2026-10-14 23:06:04','2026-10-14'),
(19,'TWH-R-18','TWH-L-18','TEST STOCK WH THIPM26101401','active','2026-10-14 23:06:04','2026-10-14'),
(20,'RP-261015000001',NULL,'TEST OKT 15','active','2026-10-15 23:04:37','2026-10-15'),
(21,'RP-261015000002',NULL,'TEST OKT 15 002','active','2026-10-15 23:06:42','2026-10-15');
/*!40000 ALTER TABLE `tbl_rencana_produksi` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_seq`
--

DROP TABLE IF EXISTS `tbl_seq`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_seq` (
  `name` varchar(30) NOT NULL,
  `last_val` int(11) NOT NULL DEFAULT 0,
  `prefix` varchar(10) DEFAULT '',
  `date_key` varchar(8) DEFAULT '',
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_seq`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_seq` WRITE;
/*!40000 ALTER TABLE `tbl_seq` DISABLE KEYS */;
INSERT INTO `tbl_seq` VALUES
('BC-K',2,'BC-K','261008'),
('BC-R',3,'BC-R','261006'),
('FG',27,'FG','261015'),
('LW',3,'LW','261006'),
('PR',1,'PR','261015'),
('RP',2,'RP','261015'),
('RPI',2,'RPI','261015'),
('WIP',2,'WIP','261015'),
('WIP-PERSIAPAN',1,'WIP','20261015');
/*!40000 ALTER TABLE `tbl_seq` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_stock_sisa`
--

DROP TABLE IF EXISTS `tbl_stock_sisa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_stock_sisa` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sumber` varchar(20) NOT NULL COMMENT 'kimia|kulit|wip|fg',
  `barcode` varchar(80) DEFAULT NULL,
  `lot` varchar(80) DEFAULT NULL,
  `qty` decimal(12,2) NOT NULL DEFAULT 0.00,
  `status` varchar(20) NOT NULL DEFAULT 'open' COMMENT 'open|reserved|consumed|approved',
  `po_id` int(11) DEFAULT NULL,
  `notes` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `kode_rpi` varchar(30) DEFAULT NULL,
  `kode_wip` varchar(30) DEFAULT NULL,
  `material_name` varchar(200) DEFAULT NULL,
  `warna` varchar(100) DEFAULT NULL,
  `tebal` varchar(30) DEFAULT NULL,
  `treatment_jenis` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_stock_sisa_status` (`status`),
  KEY `idx_stock_sisa_sumber` (`sumber`),
  KEY `idx_stock_sisa_barcode` (`barcode`),
  KEY `idx_stock_sisa_po` (`po_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stock_sisa`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_stock_sisa` WRITE;
/*!40000 ALTER TABLE `tbl_stock_sisa` DISABLE KEYS */;
INSERT INTO `tbl_stock_sisa` VALUES
(1,'kulit','MCL-00A-123','KY-TEST TH 002',1000.00,'open',NULL,'Sisa KY #2 dikembalikan ke palet','2026-10-02 10:56:07',NULL,NULL,NULL,NULL,NULL,NULL),
(2,'kulit','MCL-00A-123','KY-TEST 10/6/26 001',4000.00,'open',NULL,'Sisa KY #7 dikembalikan ke palet','2026-10-06 14:16:26',NULL,NULL,NULL,NULL,NULL,NULL),
(3,'kulit','MCL-00A-123','KY-TEST 10/6/26 001',2000.00,'open',NULL,'Sisa KY #8 dikembalikan ke palet','2026-10-06 14:21:19',NULL,NULL,NULL,NULL,NULL,NULL),
(4,'kulit','MCL-00A-102','KY-1002',4932.00,'open',NULL,'Sisa KY #10 dikembalikan ke palet','2026-10-12 17:24:12',NULL,NULL,NULL,NULL,NULL,NULL),
(5,'fg','FG-261012000006','FG-261012000006',10.00,'open',NULL,'Pengukuran sisa packing','2026-10-12 18:10:57','RPI-261006000002','WIP-20261006-00002','VIRGIN HYDRO PU','ATOMIC VIOLET (55V)','1.2 - 1.4','PU'),
(6,'kulit','MCL-00A-123','KY-TEST 10/6/26 001',1762.00,'open',NULL,'Sisa KY #11 dikembalikan ke palet','2026-10-13 10:34:20',NULL,NULL,NULL,NULL,NULL,NULL),
(7,'kulit','MCL-01V-134','KY-1001',9000.00,'open',NULL,'Sisa KY #13 dikembalikan ke palet','2026-10-14 22:59:11',NULL,NULL,NULL,NULL,NULL,NULL),
(8,'kulit','MCL-01V-134','KY-1001',8500.00,'open',NULL,'Sisa KY #14 dikembalikan ke palet','2026-10-14 23:00:39',NULL,NULL,NULL,NULL,NULL,NULL),
(9,'kulit','MCL-01V-134','KY-1001',7500.00,'open',NULL,'Sisa KY #15 dikembalikan ke palet','2026-10-15 23:05:10',NULL,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `tbl_stock_sisa` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_stock_sisa_fg_assign`
--

DROP TABLE IF EXISTS `tbl_stock_sisa_fg_assign`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_stock_sisa_fg_assign` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sisa_id` int(11) NOT NULL,
  `po_id` int(11) NOT NULL,
  `qty` decimal(12,2) NOT NULL,
  `notes` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_sisa_fg_assign_sisa` (`sisa_id`),
  KEY `idx_sisa_fg_assign_po` (`po_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stock_sisa_fg_assign`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_stock_sisa_fg_assign` WRITE;
/*!40000 ALTER TABLE `tbl_stock_sisa_fg_assign` DISABLE KEYS */;
INSERT INTO `tbl_stock_sisa_fg_assign` VALUES
(1,13,3,4.00,NULL,'2026-09-23 12:20:53'),
(2,13,3,1.00,NULL,'2026-09-23 23:02:11'),
(3,19,3,45.00,NULL,'2026-09-23 23:24:45');
/*!40000 ALTER TABLE `tbl_stock_sisa_fg_assign` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_stok_kimia_in`
--

DROP TABLE IF EXISTS `tbl_stok_kimia_in`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_stok_kimia_in` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_internal` varchar(50) NOT NULL COMMENT 'Kode BC',
  `kimia_id` int(11) DEFAULT NULL,
  `qty` decimal(12,2) NOT NULL,
  `qty_sisa` decimal(12,2) NOT NULL,
  `satuan` varchar(20) DEFAULT 'kg',
  `expired_date` date DEFAULT NULL,
  `tanggal_in` date NOT NULL,
  `gudang` enum('utama','lapangan') DEFAULT 'utama',
  `created_at` datetime DEFAULT current_timestamp(),
  `jumlah_kemasan` int(11) DEFAULT NULL,
  `erp_material_id` bigint(20) DEFAULT NULL,
  `kode_material` varchar(50) DEFAULT NULL,
  `nama_material` varchar(255) DEFAULT NULL,
  `packing_inbound_id` int(11) DEFAULT NULL,
  `packing_inbound_line_id` int(11) DEFAULT NULL,
  `lot_number` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_internal` (`kode_internal`),
  KEY `kimia_id` (`kimia_id`),
  KEY `idx_gudang` (`gudang`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_kimia_in`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_stok_kimia_in` WRITE;
/*!40000 ALTER TABLE `tbl_stok_kimia_in` DISABLE KEYS */;
INSERT INTO `tbl_stok_kimia_in` VALUES
(1,'BC-K-261006000001',8,1000.00,500.00,'kg','2027-10-06','2026-10-06','utama','2026-10-06 15:21:16',10,8,'MCH-001-C00001','MEK',NULL,NULL,NULL),
(2,'BC-K-261006000002',8,500.00,140.00,'kg','2027-10-06','2026-10-06','lapangan','2026-10-06 15:27:07',NULL,8,'MCH-001-C00001','MEK',NULL,NULL,NULL),
(3,'BC-K-261006000003',92,1000.00,500.00,'kg','2027-10-06','2026-10-06','utama','2026-10-06 21:35:39',10,92,'MCH-006-B00009','KH WHITE 10A',NULL,NULL,'002'),
(4,'BC-K-261006000004',93,1000.00,500.00,'kg','2027-10-06','2026-10-06','utama','2026-10-06 21:35:54',10,93,'MCH-006-B00010','KH BLACK',NULL,NULL,'003'),
(5,'BC-K-261006000005',92,500.00,295.00,'kg','2027-10-06','2026-10-06','lapangan','2026-10-06 21:36:22',NULL,92,'MCH-006-B00009','KH WHITE 10A',NULL,NULL,'002'),
(6,'BC-K-261006000006',93,500.00,410.00,'kg','2027-10-06','2026-10-06','lapangan','2026-10-06 21:36:35',NULL,93,'MCH-006-B00010','KH BLACK',NULL,NULL,'003'),
(7,'BC-K-261008000001',777,1000.00,0.00,'KG','2027-10-08','2026-10-07','utama','2026-10-08 00:39:06',NULL,777,'TEST01','TEST KIMIA 01',NULL,NULL,'LN-00001'),
(8,'BC-K-261008000002',777,1000.00,890.00,'KG','2027-10-08','2026-10-07','lapangan','2026-10-08 00:39:19',NULL,777,'TEST01','TEST KIMIA 01',NULL,NULL,'LN-00001');
/*!40000 ALTER TABLE `tbl_stok_kimia_in` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_stok_kimia_out`
--

DROP TABLE IF EXISTS `tbl_stok_kimia_out`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_stok_kimia_out` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `stok_in_id` int(11) DEFAULT NULL,
  `kimia_id` int(11) DEFAULT NULL,
  `qty` decimal(12,2) NOT NULL,
  `tujuan` enum('mixing','produksi','return','lapangan','keluar') NOT NULL,
  `kode_wip` varchar(30) DEFAULT NULL,
  `tanggal` date NOT NULL,
  `keterangan` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `jumlah_kemasan` int(11) DEFAULT NULL,
  `erp_material_id` bigint(20) DEFAULT NULL,
  `kode_material` varchar(50) DEFAULT NULL,
  `nama_material` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `stok_in_id` (`stok_in_id`),
  KEY `kimia_id` (`kimia_id`),
  CONSTRAINT `tbl_stok_kimia_out_ibfk_1` FOREIGN KEY (`stok_in_id`) REFERENCES `tbl_stok_kimia_in` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_kimia_out`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_stok_kimia_out` WRITE;
/*!40000 ALTER TABLE `tbl_stok_kimia_out` DISABLE KEYS */;
INSERT INTO `tbl_stok_kimia_out` VALUES
(1,1,8,500.00,'lapangan',NULL,'2026-10-06',NULL,'2026-10-06 15:27:07',NULL,8,'MCH-001-C00001','MEK'),
(2,2,8,100.00,'produksi','WIP-261006000001','2026-10-06','Lab lot LW-261006000001','2026-10-06 16:04:35',NULL,8,'MCH-001-C00001','MEK'),
(3,3,92,500.00,'lapangan',NULL,'2026-10-06',NULL,'2026-10-06 21:36:22',NULL,92,'MCH-006-B00009','KH WHITE 10A'),
(4,4,93,500.00,'lapangan',NULL,'2026-10-06',NULL,'2026-10-06 21:36:35',NULL,93,'MCH-006-B00010','KH BLACK'),
(5,2,8,100.00,'produksi','WIP-261006000001','2026-10-06','Lab lot LW-261006000002','2026-10-06 21:56:07',NULL,8,'MCH-001-C00001','MEK'),
(6,6,93,50.00,'produksi','WIP-261006000001','2026-10-06','Lab lot LW-261006000002','2026-10-06 21:56:07',NULL,93,'MCH-006-B00010','KH BLACK'),
(7,5,92,50.00,'produksi','WIP-261006000001','2026-10-06','Lab lot LW-261006000002','2026-10-06 21:56:07',NULL,92,'MCH-006-B00009','KH WHITE 10A'),
(8,2,8,100.00,'produksi','WIP-261006000001','2026-10-06','Lab lot LW-261006000003','2026-10-06 22:01:18',NULL,8,'MCH-001-C00001','MEK'),
(9,5,92,100.00,'produksi','WIP-261006000001','2026-10-06','Lab lot LW-261006000003','2026-10-06 22:01:18',NULL,92,'MCH-006-B00009','KH WHITE 10A'),
(10,7,777,1000.00,'lapangan',NULL,'2026-10-07',NULL,'2026-10-08 00:39:19',NULL,777,'TEST01','TEST KIMIA 01'),
(11,2,8,10.00,'produksi','WIP-261006000002','2026-10-08','Lab lot LW-261006000002-2','2026-10-08 00:53:27',NULL,8,'MCH-001-C00001','MEK'),
(12,5,92,10.00,'produksi','WIP-261006000002','2026-10-08','Lab lot LW-261006000002-2','2026-10-08 00:53:27',NULL,92,'MCH-006-B00009','KH WHITE 10A'),
(13,6,93,10.00,'produksi','WIP-261006000002','2026-10-08','Lab lot LW-261006000002-3','2026-10-08 00:53:27',NULL,93,'MCH-006-B00010','KH BLACK'),
(14,2,8,15.00,'produksi','WIP-261006000002','2026-10-08','Lab lot LW-261006000002-4','2026-10-08 00:58:54',NULL,8,'MCH-001-C00001','MEK'),
(15,5,92,15.00,'produksi','WIP-261006000002','2026-10-08','Lab lot LW-261006000002-4','2026-10-08 00:58:54',NULL,92,'MCH-006-B00009','KH WHITE 10A'),
(16,8,777,110.00,'produksi','WIP-261006000002','2026-10-08','Lab lot LW-261006000002-5','2026-10-08 00:58:54',NULL,777,'TEST01','TEST KIMIA 01'),
(17,5,92,15.00,'produksi','WIP-261006000002','2026-10-08','Lab lot LW-261006000002-5','2026-10-08 00:58:54',NULL,92,'MCH-006-B00009','KH WHITE 10A'),
(18,6,93,5.00,'produksi','WIP-261006000002','2026-10-08','Lab lot LW-261006000002-5','2026-10-08 00:58:54',NULL,93,'MCH-006-B00010','KH BLACK'),
(19,2,8,10.00,'produksi','WIP-261006000001','2026-10-11','Lab lot LW-261006000001-2','2026-10-11 02:33:05',NULL,8,'MCH-001-C00001','MEK'),
(20,6,93,10.00,'produksi','WIP-261006000001','2026-10-11','Lab lot LW-261006000001-2','2026-10-11 02:33:05',NULL,93,'MCH-006-B00010','KH BLACK'),
(21,5,92,10.00,'produksi','WIP-261012000002','2026-10-12','Lab lot LW-261012000002-1','2026-10-12 17:25:32',NULL,92,'MCH-006-B00009','KH WHITE 10A'),
(22,6,93,5.00,'produksi','WIP-261012000002','2026-10-12','Lab lot LW-261012000002-1','2026-10-12 17:25:32',NULL,93,'MCH-006-B00010','KH BLACK'),
(23,2,8,5.00,'produksi','WIP-261012000002','2026-10-12','Lab lot LW-261012000002-1','2026-10-12 17:25:32',NULL,8,'MCH-001-C00001','MEK'),
(24,2,8,20.00,'produksi','WIP-261013000003','2026-10-13','Lab lot LW-261013000003-1','2026-10-13 10:49:30',NULL,8,'MCH-001-C00001','MEK'),
(25,6,93,10.00,'produksi','WIP-261013000003','2026-10-13','Lab lot LW-261013000003-1','2026-10-13 10:49:30',NULL,93,'MCH-006-B00010','KH BLACK'),
(26,5,92,5.00,'produksi','WIP-261013000003','2026-10-13','Lab lot LW-261013000003-1','2026-10-13 10:49:30',NULL,92,'MCH-006-B00009','KH WHITE 10A');
/*!40000 ALTER TABLE `tbl_stok_kimia_out` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_stok_material_lain_in`
--

DROP TABLE IF EXISTS `tbl_stok_material_lain_in`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_stok_material_lain_in` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_internal` varchar(50) NOT NULL,
  `material_id` int(11) DEFAULT NULL,
  `qty` decimal(12,2) NOT NULL,
  `qty_sisa` decimal(12,2) NOT NULL,
  `satuan` varchar(20) DEFAULT 'pcs',
  `tanggal_in` date NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `erp_material_id` bigint(20) DEFAULT NULL,
  `kode_material` varchar(50) DEFAULT NULL,
  `nama_material` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_internal` (`kode_internal`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_material_lain_in`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_stok_material_lain_in` WRITE;
/*!40000 ALTER TABLE `tbl_stok_material_lain_in` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_stok_material_lain_in` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_stok_material_lain_out`
--

DROP TABLE IF EXISTS `tbl_stok_material_lain_out`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_stok_material_lain_out` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `stok_in_id` int(11) DEFAULT NULL,
  `material_id` int(11) DEFAULT NULL,
  `qty` decimal(12,2) NOT NULL,
  `kode_wip` varchar(30) DEFAULT NULL,
  `tanggal` date NOT NULL,
  `keterangan` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `erp_material_id` bigint(20) DEFAULT NULL,
  `kode_material` varchar(50) DEFAULT NULL,
  `nama_material` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_material_lain_out`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_stok_material_lain_out` WRITE;
/*!40000 ALTER TABLE `tbl_stok_material_lain_out` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_stok_material_lain_out` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_stok_rp_in`
--

DROP TABLE IF EXISTS `tbl_stok_rp_in`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_stok_rp_in` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_internal` varchar(50) NOT NULL COMMENT 'Kode BC',
  `rp_id` int(11) DEFAULT NULL,
  `meter_roll` decimal(12,2) NOT NULL,
  `qty_sisa` decimal(12,2) NOT NULL,
  `tanggal_in` date NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `erp_material_id` bigint(20) DEFAULT NULL,
  `kode_material` varchar(50) DEFAULT NULL,
  `nama_material` varchar(255) DEFAULT NULL,
  `packing_inbound_id` int(11) DEFAULT NULL,
  `packing_inbound_line_id` int(11) DEFAULT NULL,
  `gudang` varchar(20) NOT NULL DEFAULT 'utama',
  `lot_number` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_internal` (`kode_internal`),
  KEY `rp_id` (`rp_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_rp_in`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_stok_rp_in` WRITE;
/*!40000 ALTER TABLE `tbl_stok_rp_in` DISABLE KEYS */;
INSERT INTO `tbl_stok_rp_in` VALUES
(1,'BC-R-261006000001',3,100.00,80.00,'2026-10-06','2026-10-06 15:11:14',3,'MRP-001-DE107-MT','DE-107 Matte',NULL,NULL,'utama',NULL),
(2,'BC-R-261006000002',3,5.00,5.00,'2026-10-06','2026-10-06 15:12:03',3,'MRP-001-DE107-MT','DE-107 Matte',NULL,NULL,'lapangan',NULL),
(3,'BC-R-261006000003',3,10.00,10.00,'2026-10-06','2026-10-06 15:12:21',3,'MRP-001-DE107-MT','DE-107 Matte',NULL,NULL,'lapangan',NULL);
/*!40000 ALTER TABLE `tbl_stok_rp_in` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_stok_rp_out`
--

DROP TABLE IF EXISTS `tbl_stok_rp_out`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_stok_rp_out` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `stok_in_id` int(11) DEFAULT NULL,
  `rp_id` int(11) DEFAULT NULL,
  `meter_roll` decimal(12,2) NOT NULL,
  `kode_wip` varchar(30) DEFAULT NULL,
  `tanggal` date NOT NULL,
  `keterangan` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `erp_material_id` bigint(20) DEFAULT NULL,
  `kode_material` varchar(50) DEFAULT NULL,
  `nama_material` varchar(255) DEFAULT NULL,
  `gudang` varchar(20) DEFAULT NULL,
  `tujuan` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `stok_in_id` (`stok_in_id`),
  KEY `rp_id` (`rp_id`),
  CONSTRAINT `tbl_stok_rp_out_ibfk_1` FOREIGN KEY (`stok_in_id`) REFERENCES `tbl_stok_rp_in` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_rp_out`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_stok_rp_out` WRITE;
/*!40000 ALTER TABLE `tbl_stok_rp_out` DISABLE KEYS */;
INSERT INTO `tbl_stok_rp_out` VALUES
(1,1,3,5.00,NULL,'2026-10-06',NULL,'2026-10-06 15:11:46',3,'MRP-001-DE107-MT','DE-107 Matte','utama','produksi'),
(2,1,3,5.00,NULL,'2026-10-06',NULL,'2026-10-06 15:12:03',3,'MRP-001-DE107-MT','DE-107 Matte','utama','lapangan'),
(3,1,3,10.00,NULL,'2026-10-06',NULL,'2026-10-06 15:12:20',3,'MRP-001-DE107-MT','DE-107 Matte','utama','lapangan');
/*!40000 ALTER TABLE `tbl_stok_rp_out` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_usage_color`
--

DROP TABLE IF EXISTS `tbl_usage_color`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_usage_color` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_wip` varchar(30) NOT NULL,
  `kode_lot_warna` varchar(30) NOT NULL,
  `nama_warna` varchar(100) DEFAULT NULL,
  `qty_pembuatan` decimal(12,2) DEFAULT 0.00,
  `qty_digunakan` decimal(12,2) DEFAULT 0.00,
  `date_created` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_kode_wip` (`kode_wip`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_usage_color`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_usage_color` WRITE;
/*!40000 ALTER TABLE `tbl_usage_color` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_usage_color` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_usage_material_lain`
--

DROP TABLE IF EXISTS `tbl_usage_material_lain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_usage_material_lain` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_wip` varchar(30) NOT NULL,
  `kode_material` varchar(50) NOT NULL,
  `nama_material` varchar(150) DEFAULT NULL,
  `qty_used` decimal(12,2) DEFAULT 0.00,
  `satuan` varchar(20) DEFAULT 'pcs',
  `date_created` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_kode_wip` (`kode_wip`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_usage_material_lain`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_usage_material_lain` WRITE;
/*!40000 ALTER TABLE `tbl_usage_material_lain` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_usage_material_lain` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_usage_rp`
--

DROP TABLE IF EXISTS `tbl_usage_rp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_usage_rp` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_wip` varchar(30) NOT NULL,
  `jenis_rp` varchar(150) NOT NULL,
  `qty_used` decimal(12,2) DEFAULT 0.00,
  `satuan` varchar(20) DEFAULT 'meter',
  `date_created` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_kode_wip` (`kode_wip`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_usage_rp`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_usage_rp` WRITE;
/*!40000 ALTER TABLE `tbl_usage_rp` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_usage_rp` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_yl`
--

DROP TABLE IF EXISTS `tbl_yl`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_yl` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_yl` varchar(50) NOT NULL,
  `kode_palet` varchar(50) NOT NULL COMMENT 'KY',
  `thickness` varchar(30) DEFAULT NULL,
  `warna` varchar(100) DEFAULT NULL,
  `qty` decimal(12,2) DEFAULT 0.00,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_palet_yl` (`kode_palet`,`kode_yl`),
  KEY `idx_kode_palet` (`kode_palet`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_yl`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_yl` WRITE;
/*!40000 ALTER TABLE `tbl_yl` DISABLE KEYS */;
INSERT INTO `tbl_yl` VALUES
(10,'MCL-00A-123','KY-1001','1.23','BLACK',3000.00,'2026-10-12 17:13:52'),
(14,'MCL-33R-123','KY-1002','1.23','33R',1000.00,'2026-10-12 17:18:11'),
(15,'MCL-00A-123','KY-1002','1.23','BLACK',2000.00,'2026-10-12 17:18:11'),
(16,'MCL-00A-102','KY-1002','1.02','BLACK',4932.00,'2026-10-12 17:24:12'),
(17,'MCL-00A-123','KY-TEST 10/6/26 001','1.23','BLACK',562.00,'2026-10-13 10:34:20'),
(20,'MCL-01V-134','KY-1001','','',7500.00,'2026-10-15 23:05:10');
/*!40000 ALTER TABLE `tbl_yl` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tbl_yl_movement`
--

DROP TABLE IF EXISTS `tbl_yl_movement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_yl_movement` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_yl` varchar(50) NOT NULL,
  `kode_palet` varchar(50) NOT NULL,
  `direction` enum('IN','OUT') NOT NULL,
  `thickness` varchar(30) DEFAULT NULL,
  `warna` varchar(100) DEFAULT NULL,
  `qty` decimal(12,2) DEFAULT 0.00,
  `tanggal` date NOT NULL,
  `keterangan` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_kode_yl` (`kode_yl`),
  KEY `idx_kode_palet` (`kode_palet`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_yl_movement`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_yl_movement` WRITE;
/*!40000 ALTER TABLE `tbl_yl_movement` DISABLE KEYS */;
INSERT INTO `tbl_yl_movement` VALUES
(1,'MCL-00A-123','KY-TEST TH 001','OUT','1.23','BLACK',2000.00,'2026-10-02','Keluar proses persiapan — WIP WIP-20261002-00001','2026-10-02 10:56:03'),
(2,'MCL-00A-123','KY-TEST TH 002','OUT','1.23','BLACK',2000.00,'2026-10-02','Keluar proses persiapan — WIP WIP-20261002-00001','2026-10-02 10:56:07'),
(3,'MCL-00A-123','KY-TEST TH 002','IN','1.23','BLACK',1000.00,'2026-10-02','Sisa KY dikembalikan ke palet — WIP WIP-20261002-00001','2026-10-02 10:56:07'),
(4,'MCL-00A-123','KY-TEST TH 003','OUT','1.23','BLACK',2000.00,'2026-10-02','Keluar proses persiapan — WIP WIP-20261002-00002','2026-10-02 11:01:56'),
(5,'MCL-00A-123','KY-TEST TH 002','OUT','1.23','BLACK',1000.00,'2026-10-03','Keluar proses persiapan — WIP WIP-20261003-00001','2026-10-03 16:19:16'),
(6,'MCL-00A-123','KY-TEST 3/10/26','OUT','1.23','BLACK',300.00,'2026-10-03','Keluar proses persiapan — WIP WIP-20261003-00002','2026-10-03 16:23:02'),
(7,'MCL-00A-123','KY-TEST 3/10/26 02','OUT','1.23','BLACK',1000.00,'2026-10-03','Keluar proses persiapan — WIP WIP-20261003-00003','2026-10-03 16:28:19'),
(8,'MCL-00A-123','KY-TEST 10/6/26 001','OUT','1.23','BLACK',5000.00,'2026-10-06','Keluar proses persiapan — WIP WIP-20261006-00001','2026-10-06 14:16:26'),
(9,'MCL-00A-123','KY-TEST 10/6/26 001','IN','1.23','BLACK',4000.00,'2026-10-06','Sisa KY dikembalikan ke palet — WIP WIP-20261006-00001','2026-10-06 14:16:26'),
(10,'MCL-00A-123','KY-TEST 10/6/26 001','OUT','1.23','BLACK',4000.00,'2026-10-06','Keluar proses persiapan — WIP WIP-20261006-00002','2026-10-06 14:21:19'),
(11,'MCL-00A-123','KY-TEST 10/6/26 001','IN','1.23','BLACK',2000.00,'2026-10-06','Sisa KY dikembalikan ke palet — WIP WIP-20261006-00002','2026-10-06 14:21:19'),
(12,'MCL-00A-123','KY-TEST 10/6/26 001','OUT','1.23','BLACK',161.00,'2026-10-12','Keluar proses persiapan — WIP WIP-20261012-00001','2026-10-12 15:42:26'),
(13,'MCL-00A-102','KY-1002','OUT','1.02','BLACK',5000.00,'2026-10-12','Keluar proses persiapan — WIP WIP-20261012-00002','2026-10-12 17:24:12'),
(14,'MCL-00A-102','KY-1002','IN','1.02','BLACK',4932.00,'2026-10-12','Sisa KY dikembalikan ke palet — WIP WIP-20261012-00002','2026-10-12 17:24:12'),
(15,'MCL-00A-123','KY-TEST 10/6/26 001','OUT','1.23','BLACK',1839.00,'2026-10-13','Keluar proses persiapan — WIP WIP-20261013-00001','2026-10-13 10:34:20'),
(16,'MCL-00A-123','KY-TEST 10/6/26 001','IN','1.23','BLACK',1762.00,'2026-10-13','Sisa KY dikembalikan ke palet — WIP WIP-20261013-00001','2026-10-13 10:34:20'),
(17,'MCL-00A-123','KY-TEST 10/6/26 001','OUT','1.23','BLACK',1200.00,'2026-10-13','Keluar proses persiapan — WIP WIP-20261013-00002','2026-10-13 10:44:54'),
(18,'MCL-01V-134','KY-1001','OUT','','',10000.00,'2026-10-14','Keluar proses persiapan — WIP WIP-20261014-00001','2026-10-14 22:59:11'),
(19,'MCL-01V-134','KY-1001','IN','','',9000.00,'2026-10-14','Sisa KY dikembalikan ke palet — WIP WIP-20261014-00001','2026-10-14 22:59:11'),
(20,'MCL-01V-134','KY-1001','OUT','','',9000.00,'2026-10-14','Keluar proses persiapan — WIP WIP-20261014-00002','2026-10-14 23:00:39'),
(21,'MCL-01V-134','KY-1001','IN','','',8500.00,'2026-10-14','Sisa KY dikembalikan ke palet — WIP WIP-20261014-00002','2026-10-14 23:00:39'),
(22,'MCL-01V-134','KY-1001','OUT','','',8500.00,'2026-10-15','Keluar proses persiapan — WIP WIP-20261015-00001','2026-10-15 23:05:10'),
(23,'MCL-01V-134','KY-1001','IN','','',7500.00,'2026-10-15','Sisa KY dikembalikan ke palet — WIP WIP-20261015-00001','2026-10-15 23:05:10');
/*!40000 ALTER TABLE `tbl_yl_movement` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Dumping events for database 'uat_tonghong_mrp'
--

--
-- Dumping routines for database 'uat_tonghong_mrp'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-10-16  0:22:29
