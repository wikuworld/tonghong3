/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.8.6-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: 127.0.0.1    Database: tonghong_mrp
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
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_checkpoint`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_checkpoint` WRITE;
/*!40000 ALTER TABLE `tbl_checkpoint` DISABLE KEYS */;
INSERT INTO `tbl_checkpoint` VALUES
(1,'WIP-260910000001',NULL,'qc',1.100,'soft','OK',1,'UAT MRP SL043',NULL,NULL,'2026-09-10 23:38:29','2026-09-10 23:38:29','QC'),
(2,'WIP-260910000002',NULL,'qc',1.100,'soft','OK',1,'UAT dual',NULL,NULL,'2026-09-10 23:38:33','2026-09-10 23:38:33','QC'),
(3,'WIP-260910000003',NULL,'qc',1.100,'soft','OK',1,'UAT dual C',NULL,NULL,'2026-09-10 23:38:37','2026-09-10 23:38:37','QC'),
(4,'WIP-260913000001',NULL,'qc',1.100,'soft','OK',1,'UAT MRP SL043',NULL,NULL,'2026-09-13 00:15:40','2026-09-13 00:15:40','QC'),
(5,'WIP-260913000002',NULL,'qc',1.100,'soft','OK',1,'UAT dual',NULL,NULL,'2026-09-13 00:15:45','2026-09-13 00:15:45','QC'),
(6,'WIP-260913000003',NULL,'qc',1.100,'soft','OK',1,'UAT dual C',NULL,NULL,'2026-09-13 00:15:48','2026-09-13 00:15:48','QC'),
(7,'WIP-260913000008',NULL,'qc',1.100,'soft','OK',1,'smoke checkpoint',NULL,NULL,'2026-09-14 00:39:13','2026-09-14 00:39:13','QC'),
(8,'WIP-260913000008',NULL,'treatment',NULL,NULL,NULL,1,'smoke treatment',NULL,NULL,'2026-09-14 00:39:13','2026-09-14 00:39:13','PU - Base Coat'),
(9,'WIP-260913000008',NULL,'qc',1.100,'soft','OK',1,'smoke checkpoint',NULL,NULL,'2026-09-14 00:44:20','2026-09-14 00:44:20','QC'),
(10,'WIP-260913000008',NULL,'treatment',NULL,NULL,NULL,1,'smoke treatment',NULL,NULL,'2026-09-14 00:44:21','2026-09-14 00:44:21','PU - Base Coat'),
(11,'WIP-260914000005',NULL,'qc',1.100,'soft','OK',1,'UAT MRP SL043',NULL,NULL,'2026-09-14 00:48:49','2026-09-14 00:48:49','QC'),
(12,'WIP-260914000006',NULL,'qc',1.100,'soft','OK',1,'UAT dual',NULL,NULL,'2026-09-14 00:48:54','2026-09-14 00:48:54','QC'),
(13,'WIP-260914000007',NULL,'qc',1.100,'soft','OK',1,'UAT dual C',NULL,NULL,'2026-09-14 00:48:58','2026-09-14 00:48:58','QC'),
(14,'WIP-260913000008','FG-260914000002','qc',1.100,'soft','OK',1,'smoke checkpoint',7,10,'2026-09-14 02:48:45','2026-09-14 02:48:45','QC'),
(15,'WIP-260913000008','FG-260914000002','treatment',NULL,NULL,NULL,1,'smoke treatment',7,NULL,'2026-09-14 02:48:45','2026-09-14 02:48:45','PU - Base Coat'),
(16,'WIP-260913000008','FG-260914000002','qc',1.100,'soft','OK',1,'smoke checkpoint',7,11,'2026-09-14 02:58:22','2026-09-14 02:58:22','QC'),
(17,'WIP-260913000008','FG-260914000002','treatment',NULL,NULL,NULL,1,'smoke treatment',7,NULL,'2026-09-14 02:58:23','2026-09-14 02:58:23','PU - Base Coat');
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
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_gudang_fg`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_gudang_fg` WRITE;
/*!40000 ALTER TABLE `tbl_gudang_fg` DISABLE KEYS */;
INSERT INTO `tbl_gudang_fg` VALUES
(1,1,'FG-260910000001','WIP-260910000001','PT. SHOETOWN LIGUNG INDONESIA',1,10.00,'out','2026-09-10 23:38:29','2026-09-10 23:38:30','UAT MRP Outstanding',1,'DEL-202609-00001','ok',NULL),
(2,2,'FG-260910000002','WIP-260910000002','PT. SHOETOWN LIGUNG INDONESIA',1,10.00,'out','2026-09-10 23:38:34','2026-09-10 23:38:38','UAT dual SO',2,'DEL-202609-00002','ok',NULL),
(3,3,'FG-260910000003','WIP-260910000003','PT. SHOETOWN LIGUNG INDONESIA',1,10.00,'out','2026-09-10 23:38:38','2026-09-10 23:38:38','UAT dual SO',2,'DEL-202609-00002','ok',NULL),
(4,4,'FG-260913000001','WIP-260913000001','PT. SHOETOWN LIGUNG INDONESIA',1,10.00,'out','2026-09-13 00:15:40','2026-09-13 00:15:41','UAT MRP Outstanding',3,'THI-M260913001','ok',NULL),
(5,5,'FG-260913000002','WIP-260913000002','PT. SHOETOWN LIGUNG INDONESIA',1,10.00,'out','2026-09-13 00:15:45','2026-09-13 00:15:50','UAT dual SO',4,'THI-M260913002','ok',NULL),
(6,6,'FG-260913000003','WIP-260913000003','PT. SHOETOWN LIGUNG INDONESIA',1,10.00,'out','2026-09-13 00:15:49','2026-09-13 00:15:50','UAT dual SO',4,'THI-M260913002','ok',NULL),
(7,9,'FG-260914000003','WIP-260914000005','PT. SHOETOWN LIGUNG INDONESIA',1,10.00,'out','2026-09-14 00:48:49','2026-09-14 00:48:50','UAT MRP Outstanding',5,'THI-M260914001','ok',NULL),
(8,10,'FG-260914000004','WIP-260914000006','PT. SHOETOWN LIGUNG INDONESIA',1,10.00,'out','2026-09-14 00:48:54','2026-09-14 00:48:59','UAT dual SO',6,'THI-M260914002','ok',NULL),
(9,11,'FG-260914000005','WIP-260914000007','PT. SHOETOWN LIGUNG INDONESIA',1,10.00,'out','2026-09-14 00:48:58','2026-09-14 00:48:59','UAT dual SO',6,'THI-M260914002','ok',NULL);
/*!40000 ALTER TABLE `tbl_gudang_fg` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_kulit_lebih`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_kulit_lebih` WRITE;
/*!40000 ALTER TABLE `tbl_kulit_lebih` DISABLE KEYS */;
INSERT INTO `tbl_kulit_lebih` VALUES
(1,12,14,7,'KY-T0914000000','YL-T0914000000',10.00,12.00,2.00,'Lebih','2026-09-14 00:43:50'),
(2,12,16,8,'KY-T0914000000','YL-T0914000000',10.00,12.00,2.00,'Lebih','2026-09-14 00:44:16'),
(3,12,21,12,'KY-T0914000000','YL-T0914000000',10.00,12.00,2.00,'Lebih','2026-09-14 02:48:38'),
(4,12,23,13,'KY-T0914000000','YL-T0914000000',10.00,12.00,2.00,'Lebih','2026-09-14 02:56:36'),
(5,12,25,14,'KY-T9329475928','YL-T9329475928',10.00,12.00,2.00,'Lebih','2026-09-14 02:57:56'),
(6,29,26,16,'KY TEST GREEN 009','1',1800.00,1200.00,-600.00,'Kurang','2026-09-14 11:52:46'),
(7,31,30,19,'KY TEST GREEN 010','2',1000.00,1600.00,600.00,'Lebih','2026-09-14 12:14:58'),
(8,12,34,21,'KY-T9403173357','YL-T9403173357',10.00,12.00,2.00,'Lebih','2026-09-14 23:26:14'),
(9,12,38,24,'KY-T9403188904','YL-T9403188904',10.00,12.00,2.00,'Lebih','2026-09-14 23:26:29'),
(10,36,41,27,'KY-T9329475928','YL-T9329475928',10.00,11.00,1.00,'Lebih','2026-09-14 23:28:10');
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
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_lab_lot`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_lab_lot` WRITE;
/*!40000 ALTER TABLE `tbl_lab_lot` DISABLE KEYS */;
INSERT INTO `tbl_lab_lot` VALUES
(1,'LW-260910000001','UAT LAB SL043 2609102338','active','2026-09-10 23:38:28',2),
(2,'LW-260910000002','UAT LAB SL043 2609102338B','active','2026-09-10 23:38:33',3),
(3,'LW-260910000003','UAT LAB SL043 2609102338C','active','2026-09-10 23:38:37',4),
(4,'LW-260913000001','UAT LAB SL043 2609130015','active','2026-09-13 00:15:40',5),
(5,'LW-260913000002','UAT LAB SL043 2609130015B','active','2026-09-13 00:15:45',6),
(6,'LW-260913000003','UAT LAB SL043 2609130015C','active','2026-09-13 00:15:48',7),
(7,'LW-260914000001','TEST LAB NO RPI 2026-09-14','active','2026-09-14 00:39:09',NULL),
(8,'LW-260914000002','TEST LAB NO RPI 2026-09-14','active','2026-09-14 00:44:17',NULL),
(9,'LW-260914000003','UAT LAB SL043 2609140048','active','2026-09-14 00:48:48',18),
(10,'LW-260914000004','UAT LAB SL043 2609140048B','active','2026-09-14 00:48:54',19),
(11,'LW-260914000005','UAT LAB SL043 2609140048C','active','2026-09-14 00:48:58',20),
(12,'LW-260914000006','mmmm','active','2026-09-14 01:26:05',20),
(13,'LW-260914000007','CAMO GREEN TEST','active','2026-09-14 11:57:07',29),
(14,'LW-260914000008','COURT GREEN TEST','active','2026-09-14 12:30:45',32),
(15,'LW-260914000009','TEST LAB NO RPI 2026-09-14','active','2026-09-14 23:26:17',NULL),
(16,'LW-260914000010','TEST LAB NO RPI 2026-09-14','active','2026-09-14 23:26:32',NULL),
(17,'LW-260914000011','mm','active','2026-09-14 23:29:10',12);
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
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_lab_lot_detail`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_lab_lot_detail` WRITE;
/*!40000 ALTER TABLE `tbl_lab_lot_detail` DISABLE KEYS */;
INSERT INTO `tbl_lab_lot_detail` VALUES
(1,'LW-260910000001','GAPCHEM1786268682','Gap Chem',NULL,'kg',1.00,NULL),
(2,'LW-260910000002','GAPCHEM1786268682','Gap Chem',NULL,'kg',1.00,NULL),
(3,'LW-260910000003','GAPCHEM1786268682','Gap Chem',NULL,'kg',1.00,NULL),
(4,'LW-260913000001','GAPCHEM1786268682','Gap Chem',NULL,'kg',1.00,NULL),
(5,'LW-260913000002','GAPCHEM1786268682','Gap Chem',NULL,'kg',1.00,NULL),
(6,'LW-260913000003','GAPCHEM1786268682','Gap Chem',NULL,'kg',1.00,NULL),
(7,'LW-260914000001','GAPCHEM1786268682','Gap Chem',NULL,'kg',1.00,NULL),
(8,'LW-260914000002','GAPCHEM1786268682','Gap Chem',NULL,'kg',1.00,NULL),
(9,'LW-260914000003','GAPCHEM1786268682','Gap Chem',NULL,'kg',1.00,NULL),
(10,'LW-260914000004','GAPCHEM1786268682','Gap Chem',NULL,'kg',1.00,NULL),
(11,'LW-260914000005','GAPCHEM1786268682','Gap Chem',NULL,'kg',1.00,NULL),
(12,'LW-260914000006','GAPCHEM1786268682','Gap Chem','Resep Custom','kg',90.00,'mm'),
(13,'LW-260914000007','MCH-006-A00129','JWS-35NHR','Resep Standard A','kg',100.00,NULL),
(14,'LW-260914000008','MCH-006-B00063','GREEN 9K299','Resep Custom','kg',10.00,NULL),
(15,'LW-260914000009','GAPCHEM1786268682','Gap Chem',NULL,'kg',1.00,NULL),
(16,'LW-260914000010','GAPCHEM1786268682','Gap Chem',NULL,'kg',1.00,NULL),
(17,'LW-260914000011','GAPCHEM1786268682','Gap Chem','Resep Custom','kg',90.00,'jj');
/*!40000 ALTER TABLE `tbl_lab_lot_detail` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_master_po`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_master_po` WRITE;
/*!40000 ALTER TABLE `tbl_master_po` DISABLE KEYS */;
INSERT INTO `tbl_master_po` VALUES
(2,'PO-PS26090901','PS26090901','WEALTH VAST CO,LTD','HYDRO PRINCESS LEATHER','OBSIDIAN (45B)','1.2 - 1.4','DE-90 M',800.00,800.00,0.00,'outstanding','2026-09-09 00:12:42',61,NULL,2,800.00,'PUMSL044260909001'),
(3,'PO-PS26090901','PS26090901','WEALTH VAST CO,LTD','METAL LEATHER-PATENT','SILVER BLUE TINT (AJ75)','1.2 - 1.4',NULL,1200.00,1200.00,3.00,'partial','2026-09-09 00:12:42',61,NULL,3,1200.00,'PUMSL044260909002'),
(5,'mmm','THIPM26090902','TAE KWANG INDUSTRIAL CO LTD','ACTION PU COATED LEATHER','ANTHRACITE (016)','1.0 - 1.2','DE-172 SM',848.00,848.00,0.00,'outstanding','2026-09-09 00:55:31',60,NULL,4,848.00,'PUMTK028260909002'),
(6,'dsfdsf','PS26091001','PT. PEI HAI INTERNATIONAL WIRATAMA INDONESIA','ACTION LEATHER','CORE BLACK (A0QM)','1.2 - 1.4','AW-44 SG',100.00,100.00,11.00,'partial','2026-09-10 23:00:11',56,'CORE BLACK (A0QM)',5,100.00,'PUMPH001260910001'),
(7,'UAT-SL043-260910233705-A','THIPM26091001','PT. SHOETOWN LIGUNG INDONESIA','VIRGIN HYDRO PU','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',100.00,100.00,0.00,'outstanding','2026-09-10 23:37:10',28,'6FS',6,100.00,'PUMSL043260910002'),
(8,'UAT-SL043-260910233705-B3','THIPM26091004','PT. SHOETOWN LIGUNG INDONESIA','VIRGIN HYDRO PU','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',100.00,100.00,0.00,'outstanding','2026-09-10 23:37:13',28,'6FS',9,100.00,'PUMSL043260910008'),
(9,'UAT-MRP-SL043-2609102337','THIPM26091005','PT. SHOETOWN LIGUNG INDONESIA','VIRGIN HYDRO PU','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',100.00,100.00,50.00,'partial','2026-09-10 23:37:25',28,'6FS',10,100.00,'PUMSL043260910010'),
(10,'UAT-MRP-SL043-2609102338','THIPM26091006','PT. SHOETOWN LIGUNG INDONESIA','VIRGIN HYDRO PU','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',100.00,100.00,10.00,'partial','2026-09-10 23:38:26',28,'6FS',11,100.00,'PUMSL043260910012'),
(11,'UAT-MRP-SL043-2609102338-B','THIPM26091007','PT. SHOETOWN LIGUNG INDONESIA','VIRGIN HYDRO PU','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',100.00,100.00,10.00,'partial','2026-09-10 23:38:31',28,'6FS',12,100.00,'PUMSL043260910014'),
(12,'UAT-MRP-SL043-2609102338-C','THIPM26091008','PT. SHOETOWN LIGUNG INDONESIA','VIRGIN HYDRO PU','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',100.00,100.00,10.00,'partial','2026-09-10 23:38:35',28,'6FS',13,100.00,'PUMSL043260910016'),
(13,'SMOKE-SYNC-260910235736','THIPM26091009','PT. SHOETOWN LIGUNG INDONESIA','VIRGIN HYDRO PU','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',100.00,100.00,50.00,'partial','2026-09-10 23:57:39',28,'6FS',14,100.00,'PUMSL043260910018'),
(14,'UAT-SL043-260913001522-A','THIPM26091301','PT. SHOETOWN LIGUNG INDONESIA','VIRGIN HYDRO PU','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',100.00,100.00,0.00,'outstanding','2026-09-13 00:15:27',28,'6FS',15,100.00,'PUMSL043260913002'),
(15,'UAT-SL043-260913001522-B3','THIPM26091304','PT. SHOETOWN LIGUNG INDONESIA','VIRGIN HYDRO PU','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',100.00,100.00,0.00,'outstanding','2026-09-13 00:15:30',28,'6FS',18,100.00,'PUMSL043260913008'),
(16,'UAT-MRP-SL043-2609130015','THIPM26091305','PT. SHOETOWN LIGUNG INDONESIA','VIRGIN HYDRO PU','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',100.00,100.00,100.00,'completed','2026-09-13 00:15:37',28,'6FS',19,100.00,'PUMSL043260913010'),
(17,'UAT-MRP-SL043-2609130015-B','THIPM26091306','PT. SHOETOWN LIGUNG INDONESIA','VIRGIN HYDRO PU','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',100.00,100.00,100.00,'completed','2026-09-13 00:15:43',28,'6FS',20,100.00,'PUMSL043260913012'),
(18,'UAT-MRP-SL043-2609130015-C','THIPM26091307','PT. SHOETOWN LIGUNG INDONESIA','VIRGIN HYDRO PU','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',100.00,100.00,10.00,'partial','2026-09-13 00:15:47',28,'6FS',21,100.00,'PUMSL043260913014'),
(19,'PO-PS26091302','PS26091302','PT. Test Januari Indonesia','ACTION LEATHER','MAROON (48F0)','1.2 - 1.4','DE-23 SG',1000.00,1000.00,0.00,'outstanding','2026-09-13 21:33:01',62,NULL,23,1000.00,'PUMTH26001260913001'),
(20,'PO-THIPM26091308','THIPM26091308','PT. Test Januari Indonesia','VIRGIN HYDRO PU','BLACK (00A)','1.2 - 1.4',NULL,1000.00,1000.00,1000.00,'completed','2026-09-13 21:37:30',62,NULL,24,1000.00,'PUMTH26001260913002'),
(21,'PO-THIPM26091308','THIPM26091308','PT. Test Januari Indonesia','VIRGIN HYDRO PU','ADOBE (68I)','1.2 - 1.4','AR-196 M',1000.00,1000.00,1000.00,'completed','2026-09-13 21:37:30',62,NULL,25,1000.00,'PUMTH26001260913003'),
(22,'ppp','PS26091303','PT. Test Januari Indonesia','ECO TECH COMFORT','WHITE (10A)','1.0 - 1.2','AR-107 M',1000.00,1000.00,1000.00,'completed','2026-09-13 21:41:21',62,'AED5',26,1000.00,'PUMTH26001260913004'),
(23,'UAT-MRP-SL043-2609140048','THIPM26091402','PT. SHOETOWN LIGUNG INDONESIA','VIRGIN HYDRO PU','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',100.00,100.00,10.00,'partial','2026-09-14 00:48:46',28,'6FS',28,100.00,'PUMSL043260914004'),
(24,'UAT-MRP-SL043-2609140048-B','THIPM26091403','PT. SHOETOWN LIGUNG INDONESIA','VIRGIN HYDRO PU','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',100.00,100.00,10.00,'partial','2026-09-14 00:48:51',28,'6FS',29,100.00,'PUMSL043260914006'),
(25,'UAT-MRP-SL043-2609140044','THIPM26091401','PT. SHOETOWN LIGUNG INDONESIA','VIRGIN HYDRO PU','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',100.00,100.00,0.00,'outstanding','2026-09-14 00:48:51',28,'6FS',27,100.00,'PUMSL043260914002'),
(26,'UAT-MRP-SL043-2609140048-C','THIPM26091404','PT. SHOETOWN LIGUNG INDONESIA','VIRGIN HYDRO PU','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',100.00,100.00,10.00,'partial','2026-09-14 00:48:56',28,'6FS',30,100.00,'PUMSL043260914008'),
(27,'PO-THIPM26091405','THIPM26091405','PT. Test Januari Indonesia','VIRGIN HYDRO PU','ARCTIC GREEN (3KF)','1.2 - 1.4','R-131 M',1800.00,1800.00,1800.00,'completed','2026-09-14 11:38:01',62,NULL,31,1800.00,'PUMTH26001260914001'),
(28,'PO-THIPM26091405','THIPM26091405','PT. Test Januari Indonesia','VIRGIN HYDRO PU','CAMO GREEN (3BA)','1.2 - 1.4','AR-138 M',1400.00,1400.00,1400.00,'completed','2026-09-14 11:38:01',62,NULL,32,1400.00,'PUMTH26001260914002'),
(29,'PO-THIPM26091406','THIPM26091406','PT. SHOETOWN MUSTIKA INDONESIA','VIRGIN HYDRO PU','BARELY GREEN (3JJ)','1.2 - 1.4','AR-138 M',1600.00,1600.00,1600.00,'completed','2026-09-14 11:59:24',50,NULL,33,1600.00,'PUMSL045260914001'),
(30,'PO-THIPM26091407','THIPM26091407','PT. Test Januari Indonesia','VIRGIN HYDRO PU','COURT GREEN (3HK)','1.2 - 1.4','UM-34 M',2000.00,2000.00,2000.00,'completed','2026-09-14 12:22:34',62,NULL,34,2000.00,'PUMTH26001260914003'),
(31,'PO-PS26091401','PS26091401','PT. Test Januari Indonesia','ACTION LEATHER','MAROON (48F0)','1.2 - 1.4','DE-23 SG',1000.00,1000.00,0.00,'outstanding','2026-09-14 13:12:26',62,NULL,35,1000.00,'PUMTH26001260914004'),
(32,'PO-THIPM26091408','THIPM26091408','PT. Test Januari Indonesia','VIRGIN HYDRO PU','ASHEN SLATE (4PB)','1.2 - 1.4','AR-20 M',1000.00,1000.00,1000.00,'completed','2026-09-14 13:53:36',62,NULL,36,1000.00,'PUMTH26001260914005'),
(33,'PO-THIPM26091409','THIPM26091409','PT. Test Januari Indonesia','ACTION PU COATED LEATHER','AQUA FLOAT (791)','1.2 - 1.4','DE-43 SM',1000.00,1000.00,0.00,'outstanding','2026-09-14 14:45:54',62,NULL,37,1000.00,'PUMTH26001260914006');
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
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_master_treatment`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_master_treatment` WRITE;
/*!40000 ALTER TABLE `tbl_master_treatment` DISABLE KEYS */;
INSERT INTO `tbl_master_treatment` VALUES
(8,'PU','PU - Degrease','2026-08-09 16:20:22'),
(9,'PU','PU - Base Coat','2026-08-09 16:20:22'),
(10,'PU','PU - Color Coat','2026-08-09 16:20:22'),
(11,'PU','PU - Top Coat','2026-08-09 16:20:22'),
(12,'PU','PU - Emboss / Press','2026-08-09 16:20:22'),
(13,'Suede','Suede - Buffing','2026-08-09 16:20:22'),
(14,'Suede','Suede - Dyeing','2026-08-09 16:20:22'),
(15,'Suede','Suede - Softener','2026-08-09 16:20:22'),
(16,'Suede','Suede - Finishing Spray','2026-08-09 16:20:22');
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_packing` (`kode_packing`),
  KEY `idx_kode_wip` (`kode_wip`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_packing`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_packing` WRITE;
/*!40000 ALTER TABLE `tbl_packing` DISABLE KEYS */;
INSERT INTO `tbl_packing` VALUES
(1,'FG-260910000001','WIP-260910000001','UAT-MRP-SL043-2609102338','PT. SHOETOWN LIGUNG INDONESIA',1,10.00,'finished','2026-09-10 23:38:29','2026-09-10 23:38:29',NULL,NULL,NULL,1,1),
(2,'FG-260910000002','WIP-260910000002','UAT-MRP-SL043-2609102338-B','PT. SHOETOWN LIGUNG INDONESIA',1,10.00,'finished','2026-09-10 23:38:34','2026-09-10 23:38:34',NULL,NULL,NULL,2,2),
(3,'FG-260910000003','WIP-260910000003','UAT-MRP-SL043-2609102338-C','PT. SHOETOWN LIGUNG INDONESIA',1,10.00,'finished','2026-09-10 23:38:37','2026-09-10 23:38:38',NULL,NULL,NULL,3,3),
(4,'FG-260913000001','WIP-260913000001','UAT-MRP-SL043-2609130015','PT. SHOETOWN LIGUNG INDONESIA',1,10.00,'finished','2026-09-13 00:15:40','2026-09-13 00:15:40',NULL,NULL,NULL,4,4),
(5,'FG-260913000002','WIP-260913000002','UAT-MRP-SL043-2609130015-B','PT. SHOETOWN LIGUNG INDONESIA',1,10.00,'finished','2026-09-13 00:15:45','2026-09-13 00:15:45',NULL,NULL,NULL,5,5),
(6,'FG-260913000003','WIP-260913000003','UAT-MRP-SL043-2609130015-C','PT. SHOETOWN LIGUNG INDONESIA',1,10.00,'finished','2026-09-13 00:15:49','2026-09-13 00:15:49',NULL,NULL,NULL,6,6),
(7,'FG-260914000001','WIP-260913000003','UAT-MRP-SL043-2609130015-C','PT. SHOETOWN LIGUNG INDONESIA',0,0.00,'in_progress','2026-09-14 00:39:14',NULL,NULL,NULL,NULL,6,6),
(8,'FG-260914000002','WIP-260913000008','PO-THIPM26091308','PT. Test Januari Indonesia',0,0.00,'in_progress','2026-09-14 00:44:22',NULL,NULL,NULL,NULL,7,7),
(9,'FG-260914000003','WIP-260914000005','UAT-MRP-SL043-2609140048','PT. SHOETOWN LIGUNG INDONESIA',1,10.00,'finished','2026-09-14 00:48:49','2026-09-14 00:48:49',NULL,NULL,NULL,8,8),
(10,'FG-260914000004','WIP-260914000006','UAT-MRP-SL043-2609140048-B','PT. SHOETOWN LIGUNG INDONESIA',1,10.00,'finished','2026-09-14 00:48:54','2026-09-14 00:48:54',NULL,NULL,NULL,9,9),
(11,'FG-260914000005','WIP-260914000007','UAT-MRP-SL043-2609140048-C','PT. SHOETOWN LIGUNG INDONESIA',1,10.00,'finished','2026-09-14 00:48:58','2026-09-14 00:48:58',NULL,NULL,NULL,10,10),
(12,'FG-260914000006','WIP-260914000007','UAT-MRP-SL043-2609140048-C','PT. SHOETOWN LIGUNG INDONESIA',0,0.00,'in_progress','2026-09-14 02:56:34',NULL,NULL,NULL,NULL,10,10);
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
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_packing_po`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_packing_po` WRITE;
/*!40000 ALTER TABLE `tbl_packing_po` DISABLE KEYS */;
INSERT INTO `tbl_packing_po` VALUES
(1,1,10,'UAT-MRP-SL043-2609102338','THIPM26091006',10.00),
(2,2,11,'UAT-MRP-SL043-2609102338-B','THIPM26091007',10.00),
(3,3,12,'UAT-MRP-SL043-2609102338-C','THIPM26091008',10.00),
(4,4,16,'UAT-MRP-SL043-2609130015','THIPM26091305',10.00),
(5,5,17,'UAT-MRP-SL043-2609130015-B','THIPM26091306',10.00),
(6,6,18,'UAT-MRP-SL043-2609130015-C','THIPM26091307',10.00),
(7,7,18,'UAT-MRP-SL043-2609130015-C','THIPM26091307',10.00),
(8,8,20,'PO-THIPM26091308','THIPM26091308',100.00),
(9,9,23,'UAT-MRP-SL043-2609140048','THIPM26091402',10.00),
(10,10,24,'UAT-MRP-SL043-2609140048-B','THIPM26091403',10.00),
(11,11,26,'UAT-MRP-SL043-2609140048-C','THIPM26091404',10.00),
(12,12,26,'UAT-MRP-SL043-2609140048-C','THIPM26091404',10.00);
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
  PRIMARY KEY (`id`),
  KEY `packing_id` (`packing_id`),
  CONSTRAINT `tbl_packing_roll_ibfk_1` FOREIGN KEY (`packing_id`) REFERENCES `tbl_packing` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_packing_roll`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_packing_roll` WRITE;
/*!40000 ALTER TABLE `tbl_packing_roll` DISABLE KEYS */;
INSERT INTO `tbl_packing_roll` VALUES
(1,1,1,1,10.00,'2026-09-10 23:38:29',NULL),
(2,2,1,1,10.00,'2026-09-10 23:38:34',NULL),
(3,3,1,1,10.00,'2026-09-10 23:38:38',NULL),
(4,4,1,1,10.00,'2026-09-13 00:15:40',NULL),
(5,5,1,1,10.00,'2026-09-13 00:15:45',NULL),
(6,6,1,1,10.00,'2026-09-13 00:15:49',NULL),
(7,9,1,1,10.00,'2026-09-14 00:48:49',NULL),
(8,10,1,1,10.00,'2026-09-14 00:48:54',NULL),
(9,11,1,1,10.00,'2026-09-14 00:48:58',NULL);
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
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_palet_movement`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_palet_movement` WRITE;
/*!40000 ALTER TABLE `tbl_palet_movement` DISABLE KEYS */;
INSERT INTO `tbl_palet_movement` VALUES
(1,'KY-SMOKE-888828','IN','2026-09-09','smoke','2026-09-09 00:33:49',NULL,NULL),
(2,'KY-SMOKE-888828','OUT','2026-09-09','smoke out','2026-09-09 00:33:49',NULL,NULL),
(3,'KY-SMOKE-889264','IN','2026-09-09','smoke','2026-09-09 00:41:04',NULL,NULL),
(4,'KY-SMOKE-889264','OUT','2026-09-09','smoke out','2026-09-09 00:41:04',NULL,NULL),
(5,'KY-UAT-2609102338','IN','2026-09-10','UAT MRP SL043','2026-09-10 23:38:27',NULL,NULL),
(6,'KY-UAT-2609102338B','IN','2026-09-10','UAT dual','2026-09-10 23:38:32',NULL,NULL),
(7,'KY-UAT-2609102338C','IN','2026-09-10','UAT dual C','2026-09-10 23:38:36',NULL,NULL),
(8,'KY-UAT-2609130015','IN','2026-09-13','UAT MRP SL043','2026-09-13 00:15:38',NULL,NULL),
(9,'KY-UAT-2609130015B','IN','2026-09-13','UAT dual','2026-09-13 00:15:43',NULL,NULL),
(10,'KY-UAT-2609130015C','IN','2026-09-13','UAT dual C','2026-09-13 00:15:47',NULL,NULL),
(11,'KY-SMOKE-321147','IN','2026-09-14','smoke','2026-09-14 00:39:07',NULL,NULL),
(12,'KY-SMOKE-321147','OUT','2026-09-14','smoke out','2026-09-14 00:39:07',NULL,NULL),
(13,'KY-T0914000000','IN','2026-09-14','test proses','2026-09-14 00:39:08',NULL,NULL),
(14,'KY-T0914000000','IN','2026-09-14','test proses','2026-09-14 00:43:49',NULL,NULL),
(15,'KY-SMOKE-321453','IN','2026-09-14','smoke','2026-09-14 00:44:13',NULL,NULL),
(16,'KY-SMOKE-321453','OUT','2026-09-14','smoke out','2026-09-14 00:44:13',NULL,NULL),
(17,'KY-T0914000000','IN','2026-09-14','test proses','2026-09-14 00:44:15',NULL,NULL),
(18,'KY-UAT-2609140048','IN','2026-09-14','UAT MRP SL043','2026-09-14 00:48:47',NULL,NULL),
(19,'KY-UAT-2609140048B','IN','2026-09-14','UAT dual','2026-09-14 00:48:52',NULL,NULL),
(20,'KY-UAT-2609140048C','IN','2026-09-14','UAT dual C','2026-09-14 00:48:57',NULL,NULL),
(21,'KY-SMOKE-328909','IN','2026-09-14','smoke','2026-09-14 02:48:29',NULL,NULL),
(22,'KY-SMOKE-328909','IN','2026-09-14','smoke additive','2026-09-14 02:48:30',NULL,NULL),
(23,'KY-SMOKE-328909','OUT','2026-09-14','smoke out','2026-09-14 02:48:30',NULL,NULL),
(24,'KY-T0914000000','IN','2026-09-14','test proses','2026-09-14 02:48:37',NULL,NULL),
(25,'KY-T0914000000','IN','2026-09-14','test proses','2026-09-14 02:56:36',NULL,NULL),
(26,'KY-SMOKE-329397','IN','2026-09-14','smoke','2026-09-14 02:56:37',NULL,NULL),
(27,'KY-SMOKE-329397','IN','2026-09-14','smoke additive','2026-09-14 02:56:37',NULL,NULL),
(28,'KY-SMOKE-329397','OUT','2026-09-14','smoke out','2026-09-14 02:56:38',NULL,NULL),
(29,'KY-T9329475928','IN','2026-09-14','test proses','2026-09-14 02:57:55',NULL,NULL),
(30,'KY-SMOKE-329479','IN','2026-09-14','smoke','2026-09-14 02:57:59',NULL,NULL),
(31,'KY-SMOKE-329479','IN','2026-09-14','smoke additive','2026-09-14 02:57:59',NULL,NULL),
(32,'KY-SMOKE-329479','OUT','2026-09-14','smoke out','2026-09-14 02:57:59',NULL,NULL),
(33,'KY TEST GREEN 009','IN','2026-09-14',NULL,'2026-09-14 11:40:57',NULL,NULL),
(34,'KY TEST GREEN 010','IN','2026-09-14',NULL,'2026-09-14 11:54:57',NULL,NULL),
(35,'KY GREEN TEST 011','IN','2026-09-14',NULL,'2026-09-14 12:24:30',NULL,NULL),
(36,'KY-T9403173357','IN','2026-09-14','test proses','2026-09-14 23:26:13',NULL,NULL),
(37,'KY-P9403174783','IN','2026-09-14','test proses','2026-09-14 23:26:14',NULL,NULL),
(38,'KY-S9403175669','IN','2026-09-14','test proses','2026-09-14 23:26:15',NULL,NULL),
(39,'KY-T9403188904','IN','2026-09-14','test proses','2026-09-14 23:26:28',NULL,NULL),
(40,'KY-P9403190359','IN','2026-09-14','test proses','2026-09-14 23:26:30',NULL,NULL),
(41,'KY-S9403191120','IN','2026-09-14','test proses','2026-09-14 23:26:31',NULL,NULL);
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
  `no_po` varchar(50) DEFAULT NULL,
  `warna` varchar(100) DEFAULT NULL,
  `tebal` varchar(30) DEFAULT NULL,
  `emboss` varchar(100) DEFAULT NULL,
  `lebar` varchar(30) DEFAULT NULL,
  `treatment_jenis` enum('PU','Suede') DEFAULT NULL,
  `treatment_list` text DEFAULT NULL,
  `total_size` decimal(12,2) DEFAULT 0.00,
  `status` enum('draft','started','saved','completed') DEFAULT 'draft',
  `date_created` datetime DEFAULT current_timestamp(),
  `date_saved` datetime DEFAULT NULL,
  `rencana_item_id` int(11) DEFAULT NULL,
  `checkpoint_status` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_proses` (`kode_proses`),
  KEY `idx_kode_wip` (`kode_wip`),
  KEY `idx_kode_rencana` (`kode_rencana`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_persiapan_kulit`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_persiapan_kulit` WRITE;
/*!40000 ALTER TABLE `tbl_persiapan_kulit` DISABLE KEYS */;
INSERT INTO `tbl_persiapan_kulit` VALUES
(4,'WIP-260910000001','RPI-260910000001','PR-260910000001','UAT-MRP-SL043-2609102338','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',NULL,'PU','PU - Base Coat',10.00,'completed','2026-09-10 23:38:27','2026-09-10 23:38:28',2,'QC'),
(5,'WIP-260910000002','RPI-260910000002','PR-260910000002','UAT-MRP-SL043-2609102338-B','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',NULL,'PU','PU - Base Coat',10.00,'completed','2026-09-10 23:38:32','2026-09-10 23:38:33',3,'QC'),
(6,'WIP-260910000003','RPI-260910000003','PR-260910000003','UAT-MRP-SL043-2609102338-C','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',NULL,'PU','PU - Base Coat',10.00,'completed','2026-09-10 23:38:36','2026-09-10 23:38:37',4,'QC'),
(7,'WIP-260913000001','RPI-260913000001','PR-260913000001','UAT-MRP-SL043-2609130015','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',NULL,'PU','PU - Base Coat',10.00,'completed','2026-09-13 00:15:38','2026-09-13 00:15:39',5,'QC'),
(8,'WIP-260913000002','RPI-260913000002','PR-260913000002','UAT-MRP-SL043-2609130015-B','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',NULL,'PU','PU - Base Coat',10.00,'completed','2026-09-13 00:15:44','2026-09-13 00:15:44',6,'QC'),
(9,'WIP-260913000003','RPI-260913000003','PR-260913000003','UAT-MRP-SL043-2609130015-C','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',NULL,'PU','PU - Base Coat',10.00,'completed','2026-09-13 00:15:48','2026-09-13 00:15:48',7,'QC'),
(10,'WIP-260913000008','RPI-260913000008','PR-260913000004','PO-THIPM26091308','BLACK (00A)','1.2 - 1.4','-',NULL,'PU','PU - Emboss / Press',0.00,'draft','2026-09-13 23:05:00',NULL,12,'PU - Base Coat'),
(11,'WIP-260913000008','RPI-260913000008','PR-260913000005','PO-THIPM26091308','BLACK (00A)','1.2 - 1.4','-',NULL,'PU','PU - Base Coat, PU - Color Coat, PU - Degrease, PU - Emboss / Press, PU - Top Coat',0.00,'started','2026-09-13 23:06:21',NULL,12,'PU - Base Coat'),
(12,'WIP-260913000008','RPI-260913000008','PR-260913000006','PO-THIPM26091308','BLACK (00A)','1.2 - 1.4','-',NULL,'PU','PU - Base Coat, PU - Color Coat, PU - Degrease, PU - Emboss / Press, PU - Top Coat',0.00,'started','2026-09-13 23:07:55',NULL,12,'PU - Base Coat'),
(13,'WIP-260913000008','RPI-260913000008','PR-260914000001','PO-THIPM26091308','BLACK (00A)','1.2 - 1.4','-',NULL,'PU','PU - Base Coat',0.00,'draft','2026-09-14 00:43:49',NULL,12,'PU - Base Coat'),
(14,'WIP-260913000008','RPI-260913000008','PR-260914000002','PO-THIPM26091308','BLACK (00A)','1.2 - 1.4','-',NULL,'PU','PU - Base Coat',12.00,'completed','2026-09-14 00:43:49','2026-09-14 00:43:50',12,'PU - Base Coat'),
(15,'WIP-260913000008','RPI-260913000008','PR-260914000003','PO-THIPM26091308','BLACK (00A)','1.2 - 1.4','-',NULL,'PU','PU - Base Coat',0.00,'draft','2026-09-14 00:44:14',NULL,12,'PU - Base Coat'),
(16,'WIP-260913000008','RPI-260913000008','PR-260914000004','PO-THIPM26091308','BLACK (00A)','1.2 - 1.4','-',NULL,'PU','PU - Base Coat',12.00,'completed','2026-09-14 00:44:15','2026-09-14 00:44:16',12,'PU - Base Coat'),
(17,'WIP-260914000005','RPI-260914000005','PR-260914000005','UAT-MRP-SL043-2609140048','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',NULL,'PU','PU - Base Coat',10.00,'completed','2026-09-14 00:48:47','2026-09-14 00:48:48',18,'QC'),
(18,'WIP-260914000006','RPI-260914000006','PR-260914000006','UAT-MRP-SL043-2609140048-B','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',NULL,'PU','PU - Base Coat',10.00,'completed','2026-09-14 00:48:53','2026-09-14 00:48:53',19,'QC'),
(19,'WIP-260914000007','RPI-260914000007','PR-260914000007','UAT-MRP-SL043-2609140048-C','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-121',NULL,'PU','PU - Base Coat',10.00,'completed','2026-09-14 00:48:57','2026-09-14 00:48:58',20,'QC'),
(20,'WIP-260913000008','RPI-260913000008','PR-260914000008','PO-THIPM26091308','BLACK (00A)','1.2 - 1.4','-',NULL,'PU','PU - Base Coat',0.00,'draft','2026-09-14 02:48:36',NULL,12,'PU - Base Coat'),
(21,'WIP-260913000008','RPI-260913000008','PR-260914000009','PO-THIPM26091308','BLACK (00A)','1.2 - 1.4','-',NULL,'PU','PU - Base Coat',12.00,'started','2026-09-14 02:48:37',NULL,12,'PU - Base Coat'),
(22,'WIP-260913000008','RPI-260913000008','PR-260914000010','PO-THIPM26091308','BLACK (00A)','1.2 - 1.4','-',NULL,'PU','PU - Base Coat',0.00,'draft','2026-09-14 02:56:35',NULL,12,'PU - Base Coat'),
(23,'WIP-260913000008','RPI-260913000008','PR-260914000011','PO-THIPM26091308','BLACK (00A)','1.2 - 1.4','-',NULL,'PU','PU - Base Coat',12.00,'started','2026-09-14 02:56:36',NULL,12,'PU - Base Coat'),
(24,'WIP-260913000008','RPI-260913000008','PR-260914000012','PO-THIPM26091308','BLACK (00A)','1.2 - 1.4','-',NULL,'PU','PU - Base Coat',0.00,'draft','2026-09-14 02:57:55',NULL,12,'PU - Base Coat'),
(25,'WIP-260913000008','RPI-260913000008','PR-260914000013','PO-THIPM26091308','BLACK (00A)','1.2 - 1.4','-',NULL,'PU','PU - Base Coat',12.00,'completed','2026-09-14 02:57:56','2026-09-14 02:57:56',12,'PU - Base Coat'),
(26,'WIP-260914000016','RPI-260914000016','PR-260914000014','PO-THIPM26091405','CAMO GREEN (3BA)','1.2 - 1.4','AR-138 M',NULL,'PU','PU - Emboss / Press, PU - Color Coat, PU - Base Coat',1200.00,'completed','2026-09-14 11:39:47','2026-09-14 11:52:54',29,NULL),
(27,'WIP-260914000017','RPI-260914000017','PR-260914000015','PO-THIPM26091405','ARCTIC GREEN (3KF)','1.2 - 1.4','R-131 M',NULL,'PU','PU - Base Coat, PU - Color Coat, PU - Emboss / Press',1800.00,'completed','2026-09-14 11:49:37','2026-09-14 11:51:30',30,NULL),
(28,'WIP-260914000016','RPI-260914000016','PR-260914000016','PO-THIPM26091405','CAMO GREEN (3BA)','1.2 - 1.4','AR-138 M',NULL,'PU','PU - Emboss / Press',1800.00,'completed','2026-09-14 11:57:37','2026-09-14 11:58:08',29,NULL),
(29,'WIP-260914000018','RPI-260914000018','PR-260914000017','PO-THIPM26091406','BARELY GREEN (3JJ)','1.2 - 1.4','AR-138 M',NULL,'PU','PU - Emboss / Press',1600.00,'completed','2026-09-14 12:12:24','2026-09-14 12:13:02',31,NULL),
(30,'WIP-260914000018','RPI-260914000018','PR-260914000018','PO-THIPM26091406','BARELY GREEN (3JJ)','1.2 - 1.4','AR-138 M',NULL,'PU','PU - Base Coat, PU - Emboss / Press, PU - Color Coat',1600.00,'completed','2026-09-14 12:14:25','2026-09-14 12:15:04',31,NULL),
(31,'WIP-260914000019','RPI-260914000019','PR-260914000019','PO-THIPM26091407','COURT GREEN (3HK)','1.2 - 1.4','UM-34 M',NULL,'PU','PU - Emboss / Press',2000.00,'completed','2026-09-14 12:23:11','2026-09-14 12:24:53',32,NULL),
(32,'WIP-260914000020','RPI-260914000020','PR-260914000020','PO-THIPM26091408','ASHEN SLATE (4PB)','1.2 - 1.4','AR-20 M',NULL,'PU','PU - Emboss / Press',0.00,'draft','2026-09-14 14:03:30',NULL,33,NULL),
(33,'WIP-20260914-00001','RPI-260913000008','PR-260914000021','PO-THIPM26091308','BLACK (00A)','1.2 - 1.4','-',NULL,'PU','PU - Base Coat',0.00,'draft','2026-09-14 23:26:12',NULL,12,NULL),
(34,'WIP-20260914-00002','RPI-260913000008','PR-260914000022','PO-THIPM26091308','BLACK (00A)','1.2 - 1.4','-',NULL,'PU','PU - Base Coat',12.00,'completed','2026-09-14 23:26:13','2026-09-14 23:26:14',12,NULL),
(35,'WIP-20260914-00003','RPI-260913000008','PR-260914000023','PO-THIPM26091308','BLACK (00A)','1.2 - 1.4','-',NULL,'PU','PU - Base Coat',0.00,'started','2026-09-14 23:26:15',NULL,12,NULL),
(36,'WIP-20260914-00004','RPI-260913000008','PR-260914000024','PO-THIPM26091308','BLACK (00A)','1.2 - 1.4','-',NULL,'PU','PU - Base Coat',8.00,'started','2026-09-14 23:26:15',NULL,12,NULL),
(37,'WIP-20260914-00005','RPI-260913000008','PR-260914000025','PO-THIPM26091308','BLACK (00A)','1.2 - 1.4','-',NULL,'PU','PU - Base Coat',0.00,'draft','2026-09-14 23:26:28',NULL,12,NULL),
(38,'WIP-20260914-00006','RPI-260913000008','PR-260914000026','PO-THIPM26091308','BLACK (00A)','1.2 - 1.4','-',NULL,'PU','PU - Base Coat',12.00,'completed','2026-09-14 23:26:29','2026-09-14 23:26:29',12,NULL),
(39,'WIP-20260914-00007','RPI-260913000008','PR-260914000027','PO-THIPM26091308','BLACK (00A)','1.2 - 1.4','-',NULL,'PU','PU - Base Coat',0.00,'started','2026-09-14 23:26:30',NULL,12,NULL),
(40,'WIP-20260914-00008','RPI-260913000008','PR-260914000028','PO-THIPM26091308','BLACK (00A)','1.2 - 1.4','-',NULL,'PU','PU - Base Coat',8.00,'started','2026-09-14 23:26:31',NULL,12,NULL),
(41,'WIP-20260914-00009','RPI-260914000023','PR-260914000029','ppp','WHITE (10A)','1.0 - 1.2','AR-107 M',NULL,'PU','PU - Base Coat, PU - Color Coat, PU - Degrease, PU - Emboss / Press, PU - Top Coat',11.00,'completed','2026-09-14 23:27:23','2026-09-14 23:28:15',36,NULL);
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
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_persiapan_ky`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_persiapan_ky` WRITE;
/*!40000 ALTER TABLE `tbl_persiapan_ky` DISABLE KEYS */;
INSERT INTO `tbl_persiapan_ky` VALUES
(1,4,'KY-UAT-2609102338','YL-UAT-2609102338',10.00,10.00,'selesai','2026-09-10 23:38:28',1,10.00,0),
(2,5,'KY-UAT-2609102338B','YL-UAT-2609102338B',10.00,10.00,'selesai','2026-09-10 23:38:32',1,10.00,0),
(3,6,'KY-UAT-2609102338C','YL-UAT-2609102338C',10.00,10.00,'selesai','2026-09-10 23:38:37',1,10.00,0),
(4,7,'KY-UAT-2609130015','YL-UAT-2609130015',10.00,10.00,'selesai','2026-09-13 00:15:39',1,10.00,0),
(5,8,'KY-UAT-2609130015B','YL-UAT-2609130015B',10.00,10.00,'selesai','2026-09-13 00:15:44',1,10.00,0),
(6,9,'KY-UAT-2609130015C','YL-UAT-2609130015C',10.00,10.00,'selesai','2026-09-13 00:15:48',1,10.00,0),
(7,14,'KY-T0914000000','YL-T0914000000',10.00,12.00,'selesai','2026-09-14 00:43:50',1,12.00,0),
(8,16,'KY-T0914000000','YL-T0914000000',10.00,12.00,'selesai','2026-09-14 00:44:15',1,12.00,0),
(9,17,'KY-UAT-2609140048','YL-UAT-2609140048',10.00,10.00,'selesai','2026-09-14 00:48:48',1,10.00,0),
(10,18,'KY-UAT-2609140048B','YL-UAT-2609140048B',10.00,10.00,'selesai','2026-09-14 00:48:53',1,10.00,0),
(11,19,'KY-UAT-2609140048C','YL-UAT-2609140048C',10.00,10.00,'selesai','2026-09-14 00:48:57',1,10.00,0),
(12,21,'KY-T0914000000','YL-T0914000000',10.00,12.00,'selesai','2026-09-14 02:48:37',1,12.00,0),
(13,23,'KY-T0914000000','YL-T0914000000',10.00,12.00,'selesai','2026-09-14 02:56:36',1,12.00,0),
(14,25,'KY-T9329475928','YL-T9329475928',10.00,12.00,'selesai','2026-09-14 02:57:56',1,12.00,0),
(15,27,'KY TEST GREEN 009','1',1800.00,1800.00,'selesai','2026-09-14 11:50:56',1,1800.00,0),
(16,26,'KY TEST GREEN 009','1',1800.00,1200.00,'selesai','2026-09-14 11:52:12',1,1200.00,0),
(17,28,'KY TEST GREEN 010','2',1800.00,1800.00,'selesai','2026-09-14 11:57:54',1,1800.00,0),
(18,29,'KY TEST GREEN 010','2',1600.00,1600.00,'selesai','2026-09-14 12:12:45',1,1600.00,0),
(19,30,'KY TEST GREEN 010','2',1000.00,1600.00,'selesai','2026-09-14 12:14:36',1,1600.00,0),
(20,31,'KY GREEN TEST 011','YL011',2000.00,2000.00,'selesai','2026-09-14 12:24:43',1,2000.00,0),
(21,34,'KY-T9403173357','YL-T9403173357',10.00,12.00,'selesai','2026-09-14 23:26:13',1,12.00,0),
(22,35,'KY-P9403174783','YL-P9403174783',10.00,0.00,'active','2026-09-14 23:26:15',0,0.00,0),
(23,36,'KY-S9403175669','YL-S9403175669',10.00,8.00,'selesai','2026-09-14 23:26:16',1,20.00,1),
(24,38,'KY-T9403188904','YL-T9403188904',10.00,12.00,'selesai','2026-09-14 23:26:29',1,12.00,0),
(25,39,'KY-P9403190359','YL-P9403190359',10.00,0.00,'active','2026-09-14 23:26:30',0,0.00,0),
(26,40,'KY-S9403191120','YL-S9403191120',10.00,8.00,'selesai','2026-09-14 23:26:31',1,20.00,1),
(27,41,'KY-T9329475928','YL-T9329475928',10.00,11.00,'selesai','2026-09-14 23:27:23',1,11.00,0);
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
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_persiapan_reprint`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_persiapan_reprint` WRITE;
/*!40000 ALTER TABLE `tbl_persiapan_reprint` DISABLE KEYS */;
INSERT INTO `tbl_persiapan_reprint` VALUES
(1,19,1,'2026-09-14 01:25:13'),
(2,27,1,'2026-09-14 11:53:43'),
(3,29,1,'2026-09-14 12:13:29'),
(4,30,1,'2026-09-14 12:16:43'),
(5,30,2,'2026-09-14 12:16:44'),
(6,30,3,'2026-09-14 12:16:45'),
(7,31,1,'2026-09-14 12:29:25');
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
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_persiapan_scan`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_persiapan_scan` WRITE;
/*!40000 ALTER TABLE `tbl_persiapan_scan` DISABLE KEYS */;
INSERT INTO `tbl_persiapan_scan` VALUES
(1,4,'KY-UAT-2609102338','YL-UAT-2609102338','2026-09-10 23:38:28',NULL),
(2,5,'KY-UAT-2609102338B','YL-UAT-2609102338B','2026-09-10 23:38:32',NULL),
(3,6,'KY-UAT-2609102338C','YL-UAT-2609102338C','2026-09-10 23:38:37',NULL),
(4,7,'KY-UAT-2609130015','YL-UAT-2609130015','2026-09-13 00:15:39',NULL),
(5,8,'KY-UAT-2609130015B','YL-UAT-2609130015B','2026-09-13 00:15:44',NULL),
(6,9,'KY-UAT-2609130015C','YL-UAT-2609130015C','2026-09-13 00:15:48',NULL),
(7,14,'KY-T0914000000','YL-T0914000000','2026-09-14 00:43:50',NULL),
(8,16,'KY-T0914000000','YL-T0914000000','2026-09-14 00:44:15',NULL),
(9,17,'KY-UAT-2609140048','YL-UAT-2609140048','2026-09-14 00:48:48',NULL),
(10,18,'KY-UAT-2609140048B','YL-UAT-2609140048B','2026-09-14 00:48:53',NULL),
(11,19,'KY-UAT-2609140048C','YL-UAT-2609140048C','2026-09-14 00:48:57',NULL),
(12,21,'KY-T0914000000','YL-T0914000000','2026-09-14 02:48:37',NULL),
(13,23,'KY-T0914000000','YL-T0914000000','2026-09-14 02:56:36',NULL),
(14,25,'KY-T9329475928','YL-T9329475928','2026-09-14 02:57:56',NULL),
(15,27,'KY TEST GREEN 009','1','2026-09-14 11:50:56',NULL),
(16,26,'KY TEST GREEN 009','1','2026-09-14 11:52:12',NULL),
(17,28,'KY TEST GREEN 010','2','2026-09-14 11:57:54',NULL),
(18,29,'KY TEST GREEN 010','2','2026-09-14 12:12:45',NULL),
(19,30,'KY TEST GREEN 010','2','2026-09-14 12:14:36',NULL),
(20,31,'KY GREEN TEST 011','YL011','2026-09-14 12:24:43',NULL),
(21,34,'KY-T9403173357','YL-T9403173357','2026-09-14 23:26:13',NULL),
(22,36,'KY-S9403175669','YL-S9403175669','2026-09-14 23:26:16',NULL),
(23,38,'KY-T9403188904','YL-T9403188904','2026-09-14 23:26:29',NULL),
(24,40,'KY-S9403191120','YL-S9403191120','2026-09-14 23:26:31',NULL);
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
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_persiapan_ukur`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_persiapan_ukur` WRITE;
/*!40000 ALTER TABLE `tbl_persiapan_ukur` DISABLE KEYS */;
INSERT INTO `tbl_persiapan_ukur` VALUES
(1,4,10.00,'2026-09-10 23:38:28',1),
(2,5,10.00,'2026-09-10 23:38:33',2),
(3,6,10.00,'2026-09-10 23:38:37',3),
(4,7,10.00,'2026-09-13 00:15:39',4),
(5,8,10.00,'2026-09-13 00:15:44',5),
(6,9,10.00,'2026-09-13 00:15:48',6),
(7,14,12.00,'2026-09-14 00:43:50',7),
(8,16,12.00,'2026-09-14 00:44:15',8),
(9,17,10.00,'2026-09-14 00:48:48',9),
(10,18,10.00,'2026-09-14 00:48:53',10),
(11,19,10.00,'2026-09-14 00:48:57',11),
(12,21,12.00,'2026-09-14 02:48:37',12),
(13,23,12.00,'2026-09-14 02:56:36',13),
(14,25,12.00,'2026-09-14 02:57:56',14),
(15,27,1000.00,'2026-09-14 11:51:14',15),
(16,27,800.00,'2026-09-14 11:51:21',15),
(18,26,1200.00,'2026-09-14 11:52:38',16),
(19,28,1800.00,'2026-09-14 11:58:03',17),
(20,29,1000.00,'2026-09-14 12:12:52',18),
(21,29,600.00,'2026-09-14 12:12:55',18),
(23,30,1600.00,'2026-09-14 12:14:52',19),
(24,31,2000.00,'2026-09-14 12:24:47',20),
(25,34,12.00,'2026-09-14 23:26:13',21),
(26,36,8.00,'2026-09-14 23:26:16',23),
(27,38,12.00,'2026-09-14 23:26:29',24),
(28,40,8.00,'2026-09-14 23:26:31',26),
(29,41,11.00,'2026-09-14 23:28:02',27);
/*!40000 ALTER TABLE `tbl_persiapan_ukur` ENABLE KEYS */;
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_rencana_item` (`kode_rencana_item`),
  KEY `idx_rencana_item` (`rencana_id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_rencana_item`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_rencana_item` WRITE;
/*!40000 ALTER TABLE `tbl_rencana_item` DISABLE KEYS */;
INSERT INTO `tbl_rencana_item` VALUES
(2,6,'RPI-260910000001','WIP-260910000001',28,'PT. SHOETOWN LIGUNG INDONESIA',NULL,'1.0 - 1.2','PINKSICLE (6FS) FLUORESCENT','AR-121','6FS',NULL,1,'2026-09-10 23:38:27',NULL,NULL,'VIRGIN HYDRO PU',1,1),
(3,7,'RPI-260910000002','WIP-260910000002',28,'PT. SHOETOWN LIGUNG INDONESIA',NULL,'1.0 - 1.2','PINKSICLE (6FS) FLUORESCENT','AR-121','6FS',NULL,1,'2026-09-10 23:38:32',NULL,NULL,'VIRGIN HYDRO PU',2,2),
(4,8,'RPI-260910000003','WIP-260910000003',28,'PT. SHOETOWN LIGUNG INDONESIA',NULL,'1.0 - 1.2','PINKSICLE (6FS) FLUORESCENT','AR-121','6FS',NULL,1,'2026-09-10 23:38:36',NULL,NULL,'VIRGIN HYDRO PU',3,3),
(5,9,'RPI-260913000001','WIP-260913000001',28,'PT. SHOETOWN LIGUNG INDONESIA',NULL,'1.0 - 1.2','PINKSICLE (6FS) FLUORESCENT','AR-121','6FS',NULL,1,'2026-09-13 00:15:38',NULL,NULL,'VIRGIN HYDRO PU',4,4),
(6,10,'RPI-260913000002','WIP-260913000002',28,'PT. SHOETOWN LIGUNG INDONESIA',NULL,'1.0 - 1.2','PINKSICLE (6FS) FLUORESCENT','AR-121','6FS',NULL,1,'2026-09-13 00:15:43',NULL,NULL,'VIRGIN HYDRO PU',5,5),
(7,11,'RPI-260913000003','WIP-260913000003',28,'PT. SHOETOWN LIGUNG INDONESIA',NULL,'1.0 - 1.2','PINKSICLE (6FS) FLUORESCENT','AR-121','6FS',NULL,1,'2026-09-13 00:15:47',NULL,NULL,'VIRGIN HYDRO PU',6,6),
(8,12,'RPI-260913000004','WIP-260913000004',62,'PT. Test Januari Indonesia',NULL,'1.2 - 1.4','BLACK (00A)','-','-',NULL,1,'2026-09-13 22:45:14',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL),
(9,12,'RPI-260913000005','WIP-260913000005',62,'PT. Test Januari Indonesia',NULL,'1.2 - 1.4','ADOBE (68I)','AR-196 M','-',NULL,2,'2026-09-13 22:45:14',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL),
(10,13,'RPI-260913000006','WIP-260913000006',28,'PT. SHOETOWN LIGUNG INDONESIA',NULL,'1.0 - 1.2','PINKSICLE (6FS) FLUORESCENT','AR-121','6FS',NULL,1,'2026-09-13 22:54:24',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL),
(11,13,'RPI-260913000007','WIP-260913000007',28,'PT. SHOETOWN LIGUNG INDONESIA',NULL,'1.0 - 1.2','PINKSICLE (6FS) FLUORESCENT','AR-121','6FS',NULL,2,'2026-09-13 22:54:24',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL),
(12,14,'RPI-260913000008','WIP-260913000008',62,'PT. Test Januari Indonesia',NULL,'1.2 - 1.4','BLACK (00A)','-','-',NULL,1,'2026-09-13 23:03:08',NULL,NULL,'VIRGIN HYDRO PU',7,7),
(13,14,'RPI-260913000009','WIP-260913000009',62,'PT. Test Januari Indonesia',NULL,'1.2 - 1.4','ADOBE (68I)','AR-196 M','-',NULL,2,'2026-09-13 23:03:08',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL),
(14,15,'RPI-260914000001','WIP-260914000001',56,'PT. PEI HAI INTERNATIONAL WIRATAMA INDONESIA',NULL,'1.2 - 1.4','CORE BLACK (A0QM)','AW-44 SG','CORE BLACK (A0QM)',NULL,1,'2026-09-14 00:39:02',NULL,NULL,'ACTION LEATHER',NULL,NULL),
(15,16,'RPI-260914000002','WIP-260914000002',56,'PT. PEI HAI INTERNATIONAL WIRATAMA INDONESIA',NULL,'1.2 - 1.4','CORE BLACK (A0QM)','AW-44 SG','CORE BLACK (A0QM)',NULL,1,'2026-09-14 00:39:03',NULL,NULL,'ACTION LEATHER',NULL,NULL),
(16,17,'RPI-260914000003','WIP-260914000003',61,'WEALTH VAST CO,LTD',NULL,'1.2 - 1.4','SILVER BLUE TINT (AJ75)','-','-',NULL,1,'2026-09-14 00:39:05',NULL,NULL,'METAL LEATHER-PATENT',NULL,NULL),
(17,18,'RPI-260914000004','WIP-260914000004',56,'PT. PEI HAI INTERNATIONAL WIRATAMA INDONESIA',NULL,'1.2 - 1.4','CORE BLACK (A0QM)','AW-44 SG','CORE BLACK (A0QM)',NULL,1,'2026-09-14 00:39:06',NULL,NULL,'ACTION LEATHER',NULL,NULL),
(18,19,'RPI-260914000005','WIP-260914000005',28,'PT. SHOETOWN LIGUNG INDONESIA',NULL,'1.0 - 1.2','PINKSICLE (6FS) FLUORESCENT','AR-121','6FS',NULL,1,'2026-09-14 00:48:47',NULL,NULL,'VIRGIN HYDRO PU',8,8),
(19,20,'RPI-260914000006','WIP-260914000006',28,'PT. SHOETOWN LIGUNG INDONESIA',NULL,'1.0 - 1.2','PINKSICLE (6FS) FLUORESCENT','AR-121','6FS',NULL,1,'2026-09-14 00:48:52',NULL,NULL,'VIRGIN HYDRO PU',9,9),
(20,21,'RPI-260914000007','WIP-260914000007',28,'PT. SHOETOWN LIGUNG INDONESIA',NULL,'1.0 - 1.2','PINKSICLE (6FS) FLUORESCENT','AR-121','6FS',NULL,1,'2026-09-14 00:48:56',NULL,NULL,'VIRGIN HYDRO PU',10,10),
(21,22,'RPI-260914000008','WIP-260914000008',56,'PT. PEI HAI INTERNATIONAL WIRATAMA INDONESIA',NULL,'1.2 - 1.4','CORE BLACK (A0QM)','AW-44 SG','CORE BLACK (A0QM)',NULL,1,'2026-09-14 02:48:39',NULL,NULL,'ACTION LEATHER',NULL,NULL),
(22,23,'RPI-260914000009','WIP-260914000009',56,'PT. PEI HAI INTERNATIONAL WIRATAMA INDONESIA',NULL,'1.2 - 1.4','CORE BLACK (A0QM)','AW-44 SG','CORE BLACK (A0QM)',NULL,1,'2026-09-14 02:48:40',NULL,NULL,'ACTION LEATHER',NULL,NULL),
(23,24,'RPI-260914000010','WIP-260914000010',61,'WEALTH VAST CO,LTD',NULL,'1.2 - 1.4','SILVER BLUE TINT (AJ75)','-','-',NULL,1,'2026-09-14 02:48:42',NULL,NULL,'METAL LEATHER-PATENT',NULL,NULL),
(24,25,'RPI-260914000011','WIP-260914000011',56,'PT. PEI HAI INTERNATIONAL WIRATAMA INDONESIA',NULL,'1.2 - 1.4','CORE BLACK (A0QM)','AW-44 SG','CORE BLACK (A0QM)',NULL,1,'2026-09-14 02:48:43',NULL,NULL,'ACTION LEATHER',NULL,NULL),
(25,26,'RPI-260914000012','WIP-260914000012',56,'PT. PEI HAI INTERNATIONAL WIRATAMA INDONESIA',NULL,'1.2 - 1.4','CORE BLACK (A0QM)','AW-44 SG','CORE BLACK (A0QM)',NULL,1,'2026-09-14 02:58:17',NULL,NULL,'ACTION LEATHER',NULL,NULL),
(26,27,'RPI-260914000013','WIP-260914000013',56,'PT. PEI HAI INTERNATIONAL WIRATAMA INDONESIA',NULL,'1.2 - 1.4','CORE BLACK (A0QM)','AW-44 SG','CORE BLACK (A0QM)',NULL,1,'2026-09-14 02:58:18',NULL,NULL,'ACTION LEATHER',NULL,NULL),
(27,28,'RPI-260914000014','WIP-260914000014',61,'WEALTH VAST CO,LTD',NULL,'1.2 - 1.4','SILVER BLUE TINT (AJ75)','-','-',NULL,1,'2026-09-14 02:58:20',NULL,NULL,'METAL LEATHER-PATENT',NULL,NULL),
(28,29,'RPI-260914000015','WIP-260914000015',56,'PT. PEI HAI INTERNATIONAL WIRATAMA INDONESIA',NULL,'1.2 - 1.4','CORE BLACK (A0QM)','AW-44 SG','CORE BLACK (A0QM)',NULL,1,'2026-09-14 02:58:21',NULL,NULL,'ACTION LEATHER',NULL,NULL),
(29,30,'RPI-260914000016','WIP-260914000016',62,'PT. Test Januari Indonesia',NULL,'1.2 - 1.4','CAMO GREEN (3BA)','AR-138 M','-',NULL,1,'2026-09-14 11:39:08',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL),
(30,30,'RPI-260914000017','WIP-260914000017',62,'PT. Test Januari Indonesia',NULL,'1.2 - 1.4','ARCTIC GREEN (3KF)','R-131 M','-',NULL,2,'2026-09-14 11:39:08',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL),
(31,31,'RPI-260914000018','WIP-260914000018',50,'PT. SHOETOWN MUSTIKA INDONESIA',NULL,'1.2 - 1.4','BARELY GREEN (3JJ)','AR-138 M','-',NULL,1,'2026-09-14 12:11:56',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL),
(32,32,'RPI-260914000019','WIP-260914000019',62,'PT. Test Januari Indonesia',NULL,'1.2 - 1.4','COURT GREEN (3HK)','UM-34 M','-',NULL,1,'2026-09-14 12:22:56',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL),
(33,33,'RPI-260914000020','WIP-260914000020',62,'PT. Test Januari Indonesia',NULL,'1.2 - 1.4','ASHEN SLATE (4PB)','AR-20 M','-',NULL,1,'2026-09-14 14:02:06',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL),
(34,34,'RPI-260914000021','WIP-260914000021',28,'PT. SHOETOWN LIGUNG INDONESIA',NULL,'1.0 - 1.2','PINKSICLE (6FS) FLUORESCENT','AR-121','6FS',NULL,1,'2026-09-14 22:08:05',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL),
(35,34,'RPI-260914000022','WIP-260914000022',28,'PT. SHOETOWN LIGUNG INDONESIA',NULL,'1.0 - 1.2','PINKSICLE (6FS) FLUORESCENT','AR-121','6FS',NULL,2,'2026-09-14 22:08:05',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL),
(36,34,'RPI-260914000023','WIP-260914000023',62,'PT. Test Januari Indonesia',NULL,'1.0 - 1.2','WHITE (10A)','AR-107 M','AED5',NULL,3,'2026-09-14 22:08:06',NULL,NULL,'ECO TECH COMFORT',NULL,NULL);
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
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_rencana_item_po`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_rencana_item_po` WRITE;
/*!40000 ALTER TABLE `tbl_rencana_item_po` DISABLE KEYS */;
INSERT INTO `tbl_rencana_item_po` VALUES
(2,2,10,100.00,10.00),
(3,3,11,100.00,10.00),
(4,4,12,100.00,10.00),
(5,5,16,100.00,10.00),
(6,6,17,100.00,10.00),
(7,7,18,100.00,10.00),
(11,11,17,90.00,90.00),
(12,10,16,90.00,90.00),
(13,8,20,1000.00,900.00),
(14,9,21,1000.00,500.00),
(15,12,20,100.00,100.00),
(16,13,21,500.00,500.00),
(17,14,6,100.00,1.00),
(20,15,6,99.00,2.00),
(22,16,3,1200.00,1.00),
(24,18,23,100.00,10.00),
(25,19,24,100.00,10.00),
(26,20,26,100.00,10.00),
(27,21,6,97.00,1.00),
(30,22,6,96.00,2.00),
(32,23,3,1199.00,1.00),
(33,24,6,94.00,1.00),
(34,25,6,93.00,1.00),
(37,26,6,92.00,2.00),
(39,27,3,1198.00,1.00),
(40,28,6,90.00,1.00),
(41,29,28,1400.00,1400.00),
(42,30,27,1800.00,1800.00),
(43,31,29,1600.00,1600.00),
(44,32,30,2000.00,2000.00),
(45,33,32,1000.00,1000.00),
(46,34,13,100.00,50.00),
(47,35,9,100.00,50.00),
(49,36,22,1000.00,1000.00);
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
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_rencana_produksi`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_rencana_produksi` WRITE;
/*!40000 ALTER TABLE `tbl_rencana_produksi` DISABLE KEYS */;
INSERT INTO `tbl_rencana_produksi` VALUES
(6,'RP-260910000001',NULL,'UAT MRP SL043 2609102338','active','2026-09-10 23:38:26','2026-09-10'),
(7,'RP-260910000002',NULL,'UAT MRP SL043 2609102338B','active','2026-09-10 23:38:32','2026-09-10'),
(8,'RP-260910000003',NULL,'UAT MRP SL043 2609102338C','active','2026-09-10 23:38:36','2026-09-10'),
(9,'RP-260913000001',NULL,'UAT MRP SL043 2609130015','active','2026-09-13 00:15:38','2026-09-13'),
(10,'RP-260913000002',NULL,'UAT MRP SL043 2609130015B','active','2026-09-13 00:15:43','2026-09-13'),
(11,'RP-260913000003',NULL,'UAT MRP SL043 2609130015C','active','2026-09-13 00:15:47','2026-09-13'),
(12,'RP-260913000004',NULL,'TEST 13/09/26 TEST','active','2026-09-13 22:45:13','2026-09-13'),
(13,'RP-260913000005',NULL,'TEST2 19/13/26','active','2026-09-13 22:54:24','2026-09-13'),
(14,'RP-260913000006',NULL,'nama yg baru','active','2026-09-13 23:03:07','2026-09-20'),
(15,'RP-260914000001',NULL,'TEST FROM PO 2026-09-14','active','2026-09-14 00:39:02','2026-09-14'),
(16,'RP-260914000002',NULL,'TEST REPLACE PO 2026-09-14','active','2026-09-14 00:39:03','2026-09-14'),
(17,'RP-260914000003',NULL,'TEST EMBOS DASH 2026-09-14','active','2026-09-14 00:39:04','2026-09-14'),
(18,'RP-260914000004',NULL,'TEST OVERBOOK 2026-09-14','active','2026-09-14 00:39:05','2026-09-14'),
(19,'RP-260914000005',NULL,'UAT MRP SL043 2609140048','active','2026-09-14 00:48:46','2026-09-14'),
(20,'RP-260914000006',NULL,'UAT MRP SL043 2609140048B','active','2026-09-14 00:48:52','2026-09-14'),
(21,'RP-260914000007',NULL,'UAT MRP SL043 2609140048C','active','2026-09-14 00:48:56','2026-09-14'),
(22,'RP-260914000008',NULL,'TEST FROM PO 2026-09-14','active','2026-09-14 02:48:39','2026-09-14'),
(23,'RP-260914000009',NULL,'TEST REPLACE PO 2026-09-14','active','2026-09-14 02:48:40','2026-09-14'),
(24,'RP-260914000010',NULL,'TEST EMBOS DASH 2026-09-14','active','2026-09-14 02:48:42','2026-09-14'),
(25,'RP-260914000011',NULL,'TEST OVERBOOK 2026-09-14','active','2026-09-14 02:48:43','2026-09-14'),
(26,'RP-260914000012',NULL,'TEST FROM PO 2026-09-14','active','2026-09-14 02:58:16','2026-09-14'),
(27,'RP-260914000013',NULL,'TEST REPLACE PO 2026-09-14','active','2026-09-14 02:58:18','2026-09-14'),
(28,'RP-260914000014',NULL,'TEST EMBOS DASH 2026-09-14','active','2026-09-14 02:58:20','2026-09-14'),
(29,'RP-260914000015',NULL,'TEST OVERBOOK 2026-09-14','active','2026-09-14 02:58:21','2026-09-14'),
(30,'RP-260914000016',NULL,'TEST GREEN 14/9/26','active','2026-09-14 11:39:07','2026-09-14'),
(31,'RP-260914000017',NULL,'SHOETOWN TEST','active','2026-09-14 12:11:56','2026-09-14'),
(32,'RP-260914000018',NULL,'TEST COURT GREEN','active','2026-09-14 12:22:56','2026-09-14'),
(33,'RP-260914000019',NULL,'VIRGIN HYDRO SLATE TEST','active','2026-09-14 14:02:06','2026-09-14'),
(34,'RP-260914000020',NULL,'Setengah Setengah, THIPM26091005,  PS26091303, THIPM26091009','active','2026-09-14 22:08:05','2026-09-14');
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
('BC-K',2,'BC-K','260914'),
('BC-M',2,'BC-M','260914'),
('BC-R',2,'BC-R','260914'),
('FG',6,'FG','260914'),
('LW',11,'LW','260914'),
('PR',29,'PR','260914'),
('RP',20,'RP','260914'),
('RPI',23,'RPI','260914'),
('WIP',23,'WIP','260914'),
('WIP-PERSIAPAN',9,'WIP','20260914');
/*!40000 ALTER TABLE `tbl_seq` ENABLE KEYS */;
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
  `gudang` enum('kimia','mixing') DEFAULT 'kimia',
  `created_at` datetime DEFAULT current_timestamp(),
  `jumlah_kemasan` int(11) DEFAULT NULL,
  `erp_material_id` bigint(20) DEFAULT NULL,
  `kode_material` varchar(50) DEFAULT NULL,
  `nama_material` varchar(255) DEFAULT NULL,
  `packing_inbound_id` int(11) DEFAULT NULL,
  `packing_inbound_line_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_internal` (`kode_internal`),
  KEY `kimia_id` (`kimia_id`),
  KEY `idx_gudang` (`gudang`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_kimia_in`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_stok_kimia_in` WRITE;
/*!40000 ALTER TABLE `tbl_stok_kimia_in` DISABLE KEYS */;
INSERT INTO `tbl_stok_kimia_in` VALUES
(1,'BC-K-260914000001',7,5.00,4.50,'kg','2027-09-14','2026-09-14','mixing','2026-09-14 00:39:17',1,7,'GAPCHEM1786268682','Gap Chem',NULL,NULL),
(2,'BC-K-260914000002',7,5.00,4.50,'kg','2027-09-14','2026-09-14','mixing','2026-09-14 00:44:24',1,7,'GAPCHEM1786268682','Gap Chem',NULL,NULL);
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
  `tujuan` enum('mixing','produksi','return') NOT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_kimia_out`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_stok_kimia_out` WRITE;
/*!40000 ALTER TABLE `tbl_stok_kimia_out` DISABLE KEYS */;
INSERT INTO `tbl_stok_kimia_out` VALUES
(1,1,7,0.50,'mixing','WIP-SMOKE-KIMIA','2026-09-14',NULL,'2026-09-14 00:39:17',NULL,7,'GAPCHEM1786268682','Gap Chem'),
(2,2,7,0.50,'mixing','WIP-SMOKE-KIMIA','2026-09-14',NULL,'2026-09-14 00:44:25',NULL,7,'GAPCHEM1786268682','Gap Chem');
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_material_lain_in`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_stok_material_lain_in` WRITE;
/*!40000 ALTER TABLE `tbl_stok_material_lain_in` DISABLE KEYS */;
INSERT INTO `tbl_stok_material_lain_in` VALUES
(1,'BC-M-260914000001',NULL,6.00,5.00,'roll','2026-09-14','2026-09-14 00:39:20',562,'MAT-001','Thread Nylon'),
(2,'BC-M-260914000002',NULL,6.00,5.00,'roll','2026-09-14','2026-09-14 00:44:28',562,'MAT-001','Thread Nylon');
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_material_lain_out`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_stok_material_lain_out` WRITE;
/*!40000 ALTER TABLE `tbl_stok_material_lain_out` DISABLE KEYS */;
INSERT INTO `tbl_stok_material_lain_out` VALUES
(1,1,562,1.00,'WIP-SMOKE-MAT','2026-09-14',NULL,'2026-09-14 00:39:20',562,'MAT-001','Thread Nylon'),
(2,2,562,1.00,'WIP-SMOKE-MAT','2026-09-14',NULL,'2026-09-14 00:44:28',562,'MAT-001','Thread Nylon');
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_internal` (`kode_internal`),
  KEY `rp_id` (`rp_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_rp_in`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_stok_rp_in` WRITE;
/*!40000 ALTER TABLE `tbl_stok_rp_in` DISABLE KEYS */;
INSERT INTO `tbl_stok_rp_in` VALUES
(1,'BC-R-260914000001',3,8.00,7.00,'2026-09-14','2026-09-14 00:39:18',3,'MRP-001-DE107-MT','DE-107 Matte',NULL,NULL),
(2,'BC-R-260914000002',3,8.00,7.00,'2026-09-14','2026-09-14 00:44:26',3,'MRP-001-DE107-MT','DE-107 Matte',NULL,NULL);
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
  PRIMARY KEY (`id`),
  KEY `stok_in_id` (`stok_in_id`),
  KEY `rp_id` (`rp_id`),
  CONSTRAINT `tbl_stok_rp_out_ibfk_1` FOREIGN KEY (`stok_in_id`) REFERENCES `tbl_stok_rp_in` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_rp_out`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_stok_rp_out` WRITE;
/*!40000 ALTER TABLE `tbl_stok_rp_out` DISABLE KEYS */;
INSERT INTO `tbl_stok_rp_out` VALUES
(1,1,3,1.00,'WIP-SMOKE-RP','2026-09-14',NULL,'2026-09-14 00:39:19',3,'MRP-001-DE107-MT','DE-107 Matte'),
(2,2,3,1.00,'WIP-SMOKE-RP','2026-09-14',NULL,'2026-09-14 00:44:26',3,'MRP-001-DE107-MT','DE-107 Matte');
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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_usage_material_lain`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_usage_material_lain` WRITE;
/*!40000 ALTER TABLE `tbl_usage_material_lain` DISABLE KEYS */;
INSERT INTO `tbl_usage_material_lain` VALUES
(1,'WIP-260914000004','MAT-001','Thread Nylon',0.25,'roll','2026-09-14 00:43:51'),
(2,'WIP-260914000004','MAT-001','Thread Nylon',0.25,'roll','2026-09-14 00:44:19'),
(3,'WIP-260914000007','MAT-001','Thread Nylon',0.25,'roll','2026-09-14 02:42:14'),
(4,'WIP-260914000007','MAT-001','Thread Nylon',0.25,'roll','2026-09-14 02:43:49'),
(5,'WIP-260914000007','MAT-001','Thread Nylon',0.25,'roll','2026-09-14 02:48:34');
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
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_yl`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_yl` WRITE;
/*!40000 ALTER TABLE `tbl_yl` DISABLE KEYS */;
INSERT INTO `tbl_yl` VALUES
(3,'YL-UAT-2609102338','KY-UAT-2609102338','1.2','PINKSICLE (6FS) FLUORESCENT',40.00,'2026-09-10 23:38:27'),
(4,'YL-UAT-2609102338B','KY-UAT-2609102338B','1.2','PINKSICLE (6FS) FLUORESCENT',40.00,'2026-09-10 23:38:32'),
(5,'YL-UAT-2609102338C','KY-UAT-2609102338C','1.2','PINKSICLE (6FS) FLUORESCENT',40.00,'2026-09-10 23:38:36'),
(6,'YL-UAT-2609130015','KY-UAT-2609130015','1.2','PINKSICLE (6FS) FLUORESCENT',40.00,'2026-09-13 00:15:38'),
(7,'YL-UAT-2609130015B','KY-UAT-2609130015B','1.2','PINKSICLE (6FS) FLUORESCENT',40.00,'2026-09-13 00:15:43'),
(8,'YL-UAT-2609130015C','KY-UAT-2609130015C','1.2','PINKSICLE (6FS) FLUORESCENT',40.00,'2026-09-13 00:15:47'),
(10,'YL-T0914000000','KY-T0914000000','1.2','BLACK',114.00,'2026-09-14 00:39:08'),
(14,'YL-UAT-2609140048','KY-UAT-2609140048','1.2','PINKSICLE (6FS) FLUORESCENT',40.00,'2026-09-14 00:48:47'),
(15,'YL-UAT-2609140048B','KY-UAT-2609140048B','1.2','PINKSICLE (6FS) FLUORESCENT',40.00,'2026-09-14 00:48:52'),
(16,'YL-UAT-2609140048C','KY-UAT-2609140048C','1.2','PINKSICLE (6FS) FLUORESCENT',40.00,'2026-09-14 00:48:57'),
(23,'YL-T9329475928','KY-T9329475928','1.2','BLACK',27.00,'2026-09-14 02:57:56'),
(29,'YL-T9403173357','KY-T9403173357','1.2','BLACK',38.00,'2026-09-14 23:26:13'),
(30,'YL-P9403174783','KY-P9403174783','1.2','BLACK',40.00,'2026-09-14 23:26:14'),
(32,'YL-T9403188904','KY-T9403188904','1.2','BLACK',38.00,'2026-09-14 23:26:28'),
(33,'YL-P9403190359','KY-P9403190359','1.2','BLACK',40.00,'2026-09-14 23:26:30');
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
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_yl_movement`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_yl_movement` WRITE;
/*!40000 ALTER TABLE `tbl_yl_movement` DISABLE KEYS */;
INSERT INTO `tbl_yl_movement` VALUES
(2,'YL-SMOKE-888828','KY-SMOKE-888828','OUT',NULL,NULL,4.00,'2026-09-09',NULL,'2026-09-09 00:33:49'),
(4,'YL-SMOKE-889264','KY-SMOKE-889264','OUT',NULL,NULL,4.00,'2026-09-09',NULL,'2026-09-09 00:41:04'),
(5,'YL-UAT-2609102338','KY-UAT-2609102338','OUT','1.2','PINKSICLE (6FS) FLUORESCENT',10.00,'2026-09-10',NULL,'2026-09-10 23:38:28'),
(6,'YL-UAT-2609102338B','KY-UAT-2609102338B','OUT','1.2','PINKSICLE (6FS) FLUORESCENT',10.00,'2026-09-10',NULL,'2026-09-10 23:38:33'),
(7,'YL-UAT-2609102338C','KY-UAT-2609102338C','OUT','1.2','PINKSICLE (6FS) FLUORESCENT',10.00,'2026-09-10',NULL,'2026-09-10 23:38:37'),
(8,'YL-UAT-2609130015','KY-UAT-2609130015','OUT','1.2','PINKSICLE (6FS) FLUORESCENT',10.00,'2026-09-13',NULL,'2026-09-13 00:15:39'),
(9,'YL-UAT-2609130015B','KY-UAT-2609130015B','OUT','1.2','PINKSICLE (6FS) FLUORESCENT',10.00,'2026-09-13',NULL,'2026-09-13 00:15:44'),
(10,'YL-UAT-2609130015C','KY-UAT-2609130015C','OUT','1.2','PINKSICLE (6FS) FLUORESCENT',10.00,'2026-09-13',NULL,'2026-09-13 00:15:48'),
(11,'YL-SMOKE-321147','KY-SMOKE-321147','OUT',NULL,NULL,99.00,'2026-09-14',NULL,'2026-09-14 00:39:07'),
(12,'YL-SMOKE-321147','KY-SMOKE-321147','OUT',NULL,NULL,4.00,'2026-09-14',NULL,'2026-09-14 00:39:07'),
(13,'YL-T0914000000','KY-T0914000000','OUT','1.2','BLACK',12.00,'2026-09-14',NULL,'2026-09-14 00:43:50'),
(14,'YL-SMOKE-321453','KY-SMOKE-321453','OUT',NULL,NULL,99.00,'2026-09-14',NULL,'2026-09-14 00:44:13'),
(15,'YL-SMOKE-321453','KY-SMOKE-321453','OUT',NULL,NULL,4.00,'2026-09-14',NULL,'2026-09-14 00:44:13'),
(16,'YL-T0914000000','KY-T0914000000','OUT','1.2','BLACK',12.00,'2026-09-14',NULL,'2026-09-14 00:44:15'),
(17,'YL-UAT-2609140048','KY-UAT-2609140048','OUT','1.2','PINKSICLE (6FS) FLUORESCENT',10.00,'2026-09-14',NULL,'2026-09-14 00:48:48'),
(18,'YL-UAT-2609140048B','KY-UAT-2609140048B','OUT','1.2','PINKSICLE (6FS) FLUORESCENT',10.00,'2026-09-14',NULL,'2026-09-14 00:48:53'),
(19,'YL-UAT-2609140048C','KY-UAT-2609140048C','OUT','1.2','PINKSICLE (6FS) FLUORESCENT',10.00,'2026-09-14',NULL,'2026-09-14 00:48:57'),
(20,'YL-SMOKE-328909','KY-SMOKE-328909','OUT',NULL,NULL,99.00,'2026-09-14',NULL,'2026-09-14 02:48:30'),
(21,'YL-SMOKE-328909','KY-SMOKE-328909','OUT',NULL,NULL,4.00,'2026-09-14',NULL,'2026-09-14 02:48:30'),
(22,'YL-T0914000000','KY-T0914000000','OUT','1.2','BLACK',12.00,'2026-09-14',NULL,'2026-09-14 02:48:38'),
(23,'YL-T0914000000','KY-T0914000000','OUT','1.2','BLACK',12.00,'2026-09-14',NULL,'2026-09-14 02:56:36'),
(24,'YL-SMOKE-329397','KY-SMOKE-329397','OUT',NULL,NULL,99.00,'2026-09-14',NULL,'2026-09-14 02:56:38'),
(25,'YL-SMOKE-329397','KY-SMOKE-329397','OUT',NULL,NULL,4.00,'2026-09-14',NULL,'2026-09-14 02:56:38'),
(26,'YL-T9329475928','KY-T9329475928','OUT','1.2','BLACK',12.00,'2026-09-14',NULL,'2026-09-14 02:57:56'),
(27,'YL-SMOKE-329479','KY-SMOKE-329479','OUT',NULL,NULL,99.00,'2026-09-14',NULL,'2026-09-14 02:57:59'),
(28,'YL-SMOKE-329479','KY-SMOKE-329479','OUT',NULL,NULL,4.00,'2026-09-14',NULL,'2026-09-14 02:57:59'),
(29,'1','KY TEST GREEN 009','OUT','1.2-1.4','Green',1800.00,'2026-09-14',NULL,'2026-09-14 11:51:25'),
(30,'1','KY TEST GREEN 009','OUT','1.2-1.4','Green',1200.00,'2026-09-14',NULL,'2026-09-14 11:52:46'),
(31,'2','KY TEST GREEN 010','OUT','1.2-1.4','Green',1800.00,'2026-09-14',NULL,'2026-09-14 11:58:05'),
(32,'2','KY TEST GREEN 010','OUT','1.2-1.4','Green',1600.00,'2026-09-14',NULL,'2026-09-14 12:12:57'),
(33,'2','KY TEST GREEN 010','OUT','1.2-1.4','Green',1600.00,'2026-09-14',NULL,'2026-09-14 12:14:58'),
(34,'YL011','KY GREEN TEST 011','OUT','1.2-1.4','GREEN',2000.00,'2026-09-14',NULL,'2026-09-14 12:24:49'),
(35,'YL-T9403173357','KY-T9403173357','OUT','1.2','BLACK',12.00,'2026-09-14','Keluar proses persiapan — WIP WIP-20260914-00002','2026-09-14 23:26:14'),
(36,'YL-S9403175669','KY-S9403175669','OUT','1.2','BLACK',8.00,'2026-09-14','Keluar proses persiapan — WIP WIP-20260914-00004','2026-09-14 23:26:16'),
(37,'YL-S9403175669','KY-S9403175669','OUT','1.2','BLACK',12.00,'2026-09-14','Auto adjustment — WIP WIP-20260914-00004','2026-09-14 23:26:16'),
(38,'YL-T9403188904','KY-T9403188904','OUT','1.2','BLACK',12.00,'2026-09-14','Keluar proses persiapan — WIP WIP-20260914-00006','2026-09-14 23:26:29'),
(39,'YL-S9403191120','KY-S9403191120','OUT','1.2','BLACK',8.00,'2026-09-14','Keluar proses persiapan — WIP WIP-20260914-00008','2026-09-14 23:26:31'),
(40,'YL-S9403191120','KY-S9403191120','OUT','1.2','BLACK',12.00,'2026-09-14','Auto adjustment — WIP WIP-20260914-00008','2026-09-14 23:26:31'),
(41,'YL-T9329475928','KY-T9329475928','OUT','1.2','BLACK',11.00,'2026-09-14','Keluar proses persiapan — WIP WIP-20260914-00009','2026-09-14 23:28:10');
/*!40000 ALTER TABLE `tbl_yl_movement` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Dumping events for database 'tonghong_mrp'
--

--
-- Dumping routines for database 'tonghong_mrp'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-09-15 22:37:25
