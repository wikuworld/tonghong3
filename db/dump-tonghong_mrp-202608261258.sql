/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.7.2-MariaDB, for Win64 (AMD64)
--
-- Host: 10.227.82.65    Database: tonghong_mrp
-- ------------------------------------------------------
-- Server version	11.8.8-MariaDB-ubu2404

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

LOCK TABLES `master_resep` WRITE;
/*!40000 ALTER TABLE `master_resep` DISABLE KEYS */;
INSERT INTO `master_resep` VALUES
(1,'Resep Standard A'),
(2,'Resep Standard B'),
(3,'Resep Custom');
/*!40000 ALTER TABLE `master_resep` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_checkpoint`
--

LOCK TABLES `tbl_checkpoint` WRITE;
/*!40000 ALTER TABLE `tbl_checkpoint` DISABLE KEYS */;
INSERT INTO `tbl_checkpoint` VALUES
(1,'WIP-BRIDGE-TEST',NULL,'inline',1.200,NULL,'OK',1,NULL,NULL,NULL,'2026-08-09 14:37:14','2026-08-09 14:37:14',NULL),
(2,'WIP-BRIDGE-TEST',NULL,'inline',NULL,NULL,'OK',1,NULL,5,4,'2026-08-09 14:37:21','2026-08-09 14:37:21',NULL),
(3,'WIP-260809000017',NULL,'inline',1.050,'soft','OK',1,'smoke',NULL,NULL,'2026-08-09 16:42:18','2026-08-09 16:42:18',NULL),
(4,'WIP-260809000017','FG-260809000006','inline',1.100,'soft','OK',1,'smoke checkpoint',NULL,NULL,'2026-08-09 16:44:20','2026-08-09 16:44:20',NULL),
(5,'WIP-260817000001',NULL,'inline',1.100,'soft','OK',1,'UAT MRP SL043',NULL,NULL,'2026-08-17 06:17:07','2026-08-17 06:17:07',NULL),
(6,'WIP-260824000002',NULL,'inline',1.210,'soft','OK',1,NULL,NULL,NULL,'2026-08-24 04:25:37','2026-08-24 04:25:37',NULL),
(7,'WIP-260824000002',NULL,'inline',1.210,NULL,'OK',1,'NAPPA',NULL,NULL,'2026-08-24 04:28:10','2026-08-24 04:28:10',NULL),
(8,'WIP-20260826-00002',NULL,'treatment',NULL,NULL,NULL,1,'agent verify',NULL,NULL,'2026-08-26 04:59:40','2026-08-26 04:59:40','PU - Base Coat'),
(9,'WIP-20260826-00002',NULL,'qc',1.200,NULL,'OK',1,'agent qc',NULL,NULL,'2026-08-26 04:59:43','2026-08-26 04:59:43','QC'),
(10,'WIP-20260826-00002',NULL,'treatment',NULL,NULL,NULL,1,NULL,NULL,NULL,'2026-08-26 05:02:53','2026-08-26 05:02:53','PU - Base Coat'),
(11,'WIP-260826000001',NULL,'treatment',NULL,NULL,NULL,1,NULL,NULL,NULL,'2026-08-26 05:10:09','2026-08-26 05:10:09','PU - Base Coat'),
(12,'WIP-260826000001',NULL,'treatment',NULL,NULL,NULL,1,NULL,NULL,NULL,'2026-08-26 05:10:19','2026-08-26 05:10:19','PU - Color Coat'),
(13,'WIP-260826000001',NULL,'treatment',NULL,NULL,NULL,1,NULL,NULL,NULL,'2026-08-26 05:10:26','2026-08-26 05:10:26','PU - Degrease'),
(14,'WIP-260826000001',NULL,'treatment',NULL,NULL,NULL,1,NULL,NULL,NULL,'2026-08-26 05:10:33','2026-08-26 05:10:33','PU - Emboss / Press'),
(15,'WIP-260826000001',NULL,'qc',NULL,NULL,'OK',1,NULL,NULL,NULL,'2026-08-26 05:10:39','2026-08-26 05:10:39','QC');
/*!40000 ALTER TABLE `tbl_checkpoint` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_gudang_fg`
--

LOCK TABLES `tbl_gudang_fg` WRITE;
/*!40000 ALTER TABLE `tbl_gudang_fg` DISABLE KEYS */;
INSERT INTO `tbl_gudang_fg` VALUES
(1,1,'FG-260809000001','WIP-260716000001','Customer A',5,12.50,'out','2026-08-09 06:42:34','2026-08-09 06:42:34','P3 E2E OUT',2,'DEL-202608-00001','ok',NULL),
(2,3,'FG-260809000003','WIP-260716000001','PT. SEJIN',2,8.00,'out','2026-08-09 12:06:41','2026-08-09 12:06:41','P0 bridge E2E',3,'DEL-202608-00002','ok',NULL),
(3,4,'FG-260809000004','WIP-260716000001','PT. SEJIN',1,9999.00,'in_stock','2026-08-09 12:06:49',NULL,NULL,NULL,NULL,'failed','Qty kirim (9999.0) melebihi saldo order (127.50 SF). Revisi PO/marketing jika perlu menambah qty order.'),
(4,5,'FG-260809000005','WIP-260716000001','SEJIN',1,5.00,'in_stock','2026-08-09 14:37:29',NULL,NULL,NULL,NULL,NULL,NULL),
(5,7,'FG-260817000001','WIP-260817000001','PT. SHOETOWN LIGUNG INDONESIA',1,10.00,'out','2026-08-17 06:17:13','2026-08-17 06:17:20','UAT MRP',5,'DEL-202608-00003','ok',NULL),
(6,8,'FG-260823000001','WIP-260823000001','PT. HARDASES ABADI INDONESIA',1,100.00,'out','2026-08-23 18:47:32','2026-08-23 18:47:37','Wave invoice PS26082302',6,'DEL-202608-00004','ok',NULL);
/*!40000 ALTER TABLE `tbl_gudang_fg` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_kulit_lebih`
--

LOCK TABLES `tbl_kulit_lebih` WRITE;
/*!40000 ALTER TABLE `tbl_kulit_lebih` DISABLE KEYS */;
INSERT INTO `tbl_kulit_lebih` VALUES
(1,10,1,1,'KY-TEST-1','YL-1',10.00,3.50,-6.50,'Kurang','2026-08-09 09:45:36'),
(2,10,1,2,'VKYPAL1786268736','VKYYL1786268736',1.00,0.00,-1.00,'Kurang','2026-08-09 09:45:37'),
(3,27,3,3,'KY-T0809000000','YL-T0809000000',10.00,12.00,2.00,'Lebih','2026-08-09 16:16:49'),
(4,27,5,4,'KY-T0809000000','YL-T0809000000',10.00,12.00,2.00,'Lebih','2026-08-09 16:20:26'),
(5,27,7,5,'KY-T0809000000','YL-T0809000000',10.00,12.00,2.00,'Lebih','2026-08-09 16:23:34');
/*!40000 ALTER TABLE `tbl_kulit_lebih` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_lab_lot`
--

LOCK TABLES `tbl_lab_lot` WRITE;
/*!40000 ALTER TABLE `tbl_lab_lot` DISABLE KEYS */;
INSERT INTO `tbl_lab_lot` VALUES
(1,'LW-260702000002','Red Premium Mix','active','2026-07-02 09:31:43',NULL),
(2,'LW-260702000003','RED PREMIUM MIX','active','2026-07-02 09:37:16',NULL),
(3,'LW-260809000001','Test Lot P2','used','2026-08-09 06:34:50',NULL),
(4,'LW-260809000002','TEST LAB NO RPI 2026-08-09','active','2026-08-09 16:20:21',NULL),
(5,'LW-260809000003','TEST LAB NO RPI 2026-08-09','active','2026-08-09 16:23:29',NULL),
(6,'LW-260809000004','TEST LAB NO RPI 2026-08-09','active','2026-08-09 16:32:56',NULL),
(8,'LW-260815000001','BLACK','active','2026-08-15 14:24:47',27),
(9,'LW-260817000001','UAT LAB SL043 2608170616','active','2026-08-17 06:17:06',35),
(10,'LW-260824000001','WHITE LEATHER','active','2026-08-24 04:24:20',38),
(11,'LW-260826000001','Premium Mix','active','2026-08-26 05:47:16',39);
/*!40000 ALTER TABLE `tbl_lab_lot` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_lab_lot_detail`
--

LOCK TABLES `tbl_lab_lot_detail` WRITE;
/*!40000 ALTER TABLE `tbl_lab_lot_detail` DISABLE KEYS */;
INSERT INTO `tbl_lab_lot_detail` VALUES
(1,'LW-260702000002','KIM-001','Chemical Base A','Resep A','kg',10.00,'base'),
(2,'LW-260702000002','KIM-003','Hardener','Resep A','kg',2.00,'hardener'),
(3,'LW-260702000003','KIM-001','Chemical Base A','0.5','kg',100.00,NULL),
(4,'LW-260702000003','KIM-003','Hardener','0.1','kg',100.00,NULL),
(5,'LW-260702000003','KIM-002','Chemical Base B','0.4','kg',1.00,NULL),
(6,'LW-260809000001','KIM-001','Chemical Base A',NULL,'kg',1.50,NULL),
(7,'LW-260809000002','GAPCHEM1786268682','Gap Chem',NULL,'kg',1.00,NULL),
(8,'LW-260809000003','GAPCHEM1786268682','Gap Chem',NULL,'kg',1.00,NULL),
(9,'LW-260809000004','GAPCHEM1786268682','Gap Chem',NULL,'kg',1.00,NULL),
(10,'LW-260815000001','MCH-001-C00001','MEK','Resep Custom','kg',1.00,NULL),
(11,'LW-260815000001','KIM-002','Chemical Base B','Resep Custom','kg',1.00,NULL),
(12,'LW-260817000001','GAPCHEM1786268682','Gap Chem',NULL,'kg',1.00,NULL),
(13,'LW-260824000001','KIM-001','Chemical Base A','Resep Standard A','kg',100.00,NULL),
(14,'LW-260826000001','KIM-001','Chemical Base A','Resep Custom','kg',1.00,'100'),
(15,'LW-260826000001','MCH-004-A00002','JU-1047E','Resep Standard A','kg',12.00,NULL),
(16,'LW-260826000001','MCH-004-A00006','JU-1100 GHR','Resep Standard B','kg',11.00,NULL);
/*!40000 ALTER TABLE `tbl_lab_lot_detail` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_lab_mixing`
--

LOCK TABLES `tbl_lab_mixing` WRITE;
/*!40000 ALTER TABLE `tbl_lab_mixing` DISABLE KEYS */;
INSERT INTO `tbl_lab_mixing` VALUES
(1,'LW-260619000001','Pigment Black','Resep Standard A','kg',9999.00,'xcfx','active','2026-06-16 20:46:40'),
(2,'LW-260702000001','Pigment Black','10','kg',1.00,'OK','active','2026-07-02 08:41:35');
/*!40000 ALTER TABLE `tbl_lab_mixing` ENABLE KEYS */;
UNLOCK TABLES;

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
  `status` enum('outstanding','partial','completed') DEFAULT 'outstanding',
  `created_at` datetime DEFAULT current_timestamp(),
  `customer_id` int(11) DEFAULT NULL,
  `color_swatch` varchar(100) DEFAULT NULL,
  `source_detail_id` int(11) DEFAULT NULL,
  `qty_balance_erp` decimal(12,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_no_po` (`no_po`),
  KEY `idx_status` (`status`),
  KEY `idx_master_po_source_detail` (`source_detail_id`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_master_po`
--

LOCK TABLES `tbl_master_po` WRITE;
/*!40000 ALTER TABLE `tbl_master_po` DISABLE KEYS */;
INSERT INTO `tbl_master_po` VALUES
(1,'PO-2026-001','SO-2026-001','Customer A','Leather Sheet A','Brown','1.2mm','Plain',500.00,100.00,100.00,'completed','2026-06-16 20:43:55',67,'SW-BRN-03',NULL,NULL),
(2,'PO-2026-002','SO-2026-001','Customer A','Leather Sheet B','Black','1.0mm','Emboss A',300.00,80.00,80.00,'completed','2026-06-16 20:43:55',67,'SW-BLK-02',NULL,NULL),
(3,'PO-2026-003','SO-2026-002','Customer B','Leather Sheet C','Red','1.4mm','Emboss B',450.00,120.00,120.00,'completed','2026-06-16 20:43:55',66,'SW-RED-05',NULL,NULL),
(4,'PO-2026-001','SO-2026-001','Customer A','Leather Sheet A-2','Brown','1.2mm','Plain',200.00,50.00,50.00,'completed','2026-06-21 00:42:32',67,'SW-BRN-03',NULL,NULL),
(5,'PO-2026-001','SO-2026-001','Customer A','Leather Sheet A-3','Tan','1.0mm','Emboss X',150.00,30.00,30.00,'completed','2026-06-21 00:42:32',67,NULL,NULL,NULL),
(6,'PO-2026-002','SO-2026-001','Customer A','Leather Sheet B-2','Black','1.0mm','Emboss A',180.00,40.00,40.00,'completed','2026-06-21 00:42:32',67,'SW-BLK-02',NULL,NULL),
(7,'PO-2026-003','SO-2026-002','Customer B','Leather Sheet C-2','Maroon','1.4mm','Emboss B',220.00,60.00,60.00,'completed','2026-06-21 00:42:32',66,'SW-MAR-06',NULL,NULL),
(8,'PO-THIPM26080307','THIPM26080301','PT. Test Januari Indonesia','ACTION PU COATED LEATHER','BLACK (001)','1.0 - 1.2','DE-172 SM',100.00,100.00,0.00,'outstanding','2026-08-09 09:44:41',62,NULL,23,100.00),
(9,'123456','THIPM26071501','WEALTH VAST CO,LTD','(PM) GENERIC PU COATED LEATHER','ARMORY NAVY (4LX)','1.0 - 1.2','R-131 M',2000.00,2000.00,1.00,'partial','2026-08-09 09:44:41',61,'6CV',1,2000.00),
(10,'aaa','PS26072802','PT. ULTIMATE NOBLE INDONESIA','(PM) GENERIC SPLIT SUEDE','TEAM RED (67P)','1.2 - 1.4',NULL,7.00,7.00,0.00,'outstanding','2026-08-09 09:44:41',49,NULL,13,7.00),
(11,'mmm','PS26072801','PT. PEI HAI INTERNATIONAL WIRATAMA INDONESIA','ACTION LEATHER','MAROON (48F0)','1.2 - 1.4','DE-23 SG',90.00,90.00,0.00,'outstanding','2026-08-09 09:44:41',56,NULL,12,90.00),
(12,'ABC123','THIPM26072701','PT. VICTORY FOOTWEAR INDONESIA','ECO TECH COMFORT','TANGERINE TINT (86T)','1.2 - 1.4','R-102 M',1000.00,1000.00,0.00,'outstanding','2026-08-09 09:44:41',55,NULL,8,1000.00),
(13,'ADIDAS123','PS26072501','PT. LONG RICH INDONESIA ADIDAS','BABY SOFT PATENT LEATHER','BETTER SCARLET (AETG)','1.4 - 1.6','CPUG (ESR-180-SK2)',2000.00,2000.00,0.00,'outstanding','2026-08-09 09:44:41',44,NULL,7,2000.00),
(14,'ADIDAS123','PS26072501','PT. LONG RICH INDONESIA ADIDAS','(PM) GENERIC SPLIT SUEDE','LT OREWOOD BRN (10J)','1.2 - 1.4',NULL,1000.00,1000.00,0.00,'outstanding','2026-08-09 09:44:41',44,NULL,6,1000.00),
(15,'sejin-20260720','PS26072001','PT. SEJIN FASHION INDONESIA','(PM) GENERIC PU COATED','COOL GREY (06B)','1.4-1.6',NULL,150.00,150.00,150.00,'completed','2026-08-09 09:44:41',40,NULL,5,127.50),
(16,'sejin-20260720','PS26072001','PT. SEJIN FASHION INDONESIA','SPARK CT','BLACK (00A)','1.2-1.4',NULL,150.00,150.00,133.00,'partial','2026-08-09 09:44:41',40,NULL,3,150.00),
(17,'123456','THIPM26071501','WEALTH VAST CO,LTD','(PM) GENERIC PU COATED LEATHER','BALTIC BLUE (40X)','1.0 - 1.2','AR-161 M',2000.00,2000.00,0.00,'outstanding','2026-08-09 09:44:41',61,'6CV',2,2000.00),
(18,'PS26081001','PO-PS26081001','PT. Test Januari Indonesia','AROMA-P','LT SMOKE GREY (0AL)','1.2 - 1.4','R-53 M',99.00,99.00,0.00,'outstanding','2026-08-10 03:10:26',62,NULL,26,99.00),
(19,'PS26081001','PO-PS26081001','PT. Test Januari Indonesia','ACTION PU COATED LEATHER','BLACK (001)','1.0 - 1.2','DE-172 SM',100.00,100.00,0.00,'outstanding','2026-08-10 03:10:28',62,NULL,27,100.00),
(20,'UAT-SL043-2608170558-A','THIPM26081701','PT. SHOETOWN LIGUNG INDONESIA','VIRGIN HYDRO PU','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-33 M',100.00,100.00,0.00,'outstanding','2026-08-17 05:59:02',28,'6FS',35,100.00),
(21,'UAT-SL043-2608170558-B1','THIPM26081702','PT. SHOETOWN LIGUNG INDONESIA','VIRGIN HYDRO PU','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-33 M',100.00,100.00,0.00,'outstanding','2026-08-17 05:59:08',28,'PINKSICLE (6FS)',36,100.00),
(22,'UAT-SL043-2608170558-B2','THIPM26081703','PT. SHOETOWN LIGUNG INDONESIA','VIRGIN HYDRO PU','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-33 M',100.00,100.00,0.00,'outstanding','2026-08-17 05:59:10',28,'WAITING C/S',37,100.00),
(23,'UAT-SL043-2608170558-B3','THIPM26081704','PT. SHOETOWN LIGUNG INDONESIA','VIRGIN HYDRO PU','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-33 M',100.00,100.00,0.00,'outstanding','2026-08-17 05:59:12',28,'6FS',38,100.00),
(24,'UAT-MRP-SL043-2608170616','THIPM26081705','PT. SHOETOWN LIGUNG INDONESIA','VIRGIN HYDRO PU','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-33 M',100.00,100.00,10.00,'partial','2026-08-17 06:16:43',28,'6FS',39,90.00),
(25,'THIPM26082301','AAA','PT. DWI PRIMA SENTOSA','(PM) GENERIC PU COATED LEATHER','ACTION RED (6DK) FLUORESCENT','1.2 - 1.4','DE-73 SM',1000.00,1000.00,0.00,'outstanding','2026-08-23 07:01:36',45,'WAITING C/S',42,1000.00),
(26,'cvvv','PS26082302','PT. HARDASES ABADI INDONESIA','ACTION LEATHER','MAROON (48F0)','1.2 - 1.4','DE-23 SG',2000.00,2000.00,100.00,'partial','2026-08-23 08:10:11',51,'assa',43,1900.00),
(27,'cvvv','PS26082302','PT. HARDASES ABADI INDONESIA','LAMPER LEATHER','BLEACHED LILAC (58V)','1.4 - 1.6','UM-T SM',2940.00,2940.00,0.00,'outstanding','2026-08-23 08:10:13',51,'WAITING C/S',44,2940.00),
(28,'123456','THIPM26071501','WEALTH VAST CO,LTD','(PM) GENERIC PU COATED LEATHER','ARMORY NAVY (4LX)','1.0 - 1.2','R-131 M',2000.00,2000.00,0.00,'outstanding','2026-08-23 18:17:19',61,'6CV',22,2000.00),
(29,'sejin-20260720','PS26072001','PT. SEJIN FASHION INDONESIA','SPARK CT','BLACK (00A)','1.2-1.4',NULL,150.00,150.00,0.00,'outstanding','2026-08-23 18:17:19',40,NULL,4,150.00),
(30,'PO-THIPM26082401','THIPM26082401','PT. LONGRICH INDONESIA-UA','ACTION PU COATED LEATHER','SALT PURPLE (535)','1.2 - 1.4','AR-216 M',2000.00,2000.00,0.00,'outstanding','2026-08-24 03:45:31',41,'535',45,2000.00),
(31,'PO-THIPM26082401','THIPM26082401','PT. LONGRICH INDONESIA-UA','ACTION PU COATED LEATHER','STONE (279) PEARLIZED','1.2 - 1.4','AR-191 M',1000.00,1000.00,0.00,'outstanding','2026-08-24 03:45:33',41,'279',46,1000.00),
(32,'PO-THIPM26082401','THIPM26082401','PT. LONGRICH INDONESIA-UA','NAPPA NATURAL LEATHER','WHITE LEATHER (100)','1.2 - 1.4','AR-194 M',1500.00,1500.00,0.00,'outstanding','2026-08-24 03:45:35',41,'100',47,1500.00),
(33,'PO-THIPM26082601','THIPM26082601','PT. SUMBER MASANDA JAYA','VIRGIN HYDRO PU','CARGO KHAKI (3HR)','1.2 - 1.4','R-102 M',15000.00,15000.00,0.00,'outstanding','2026-08-26 01:48:01',36,'CHARGO KHAKI (3HR)',48,15000.00),
(34,'PO-THIPM26082603','THIPM26082603','PT. SUMBER MASANDA JAYA','VIRGIN HYDRO PU','CARGO KHAKI (3HR)','1.2 - 1.4','AR-206 M',15000.00,15000.00,15000.00,'completed','2026-08-26 02:15:14',36,'CHARGO KHAKI (3HR)',50,15000.00);
/*!40000 ALTER TABLE `tbl_master_po` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_packing`
--

LOCK TABLES `tbl_packing` WRITE;
/*!40000 ALTER TABLE `tbl_packing` DISABLE KEYS */;
INSERT INTO `tbl_packing` VALUES
(1,'FG-260809000001','WIP-260716000001','PO-2026-002','Customer A',5,12.50,'finished','2026-08-09 06:42:33','2026-08-09 06:42:34',NULL,NULL,NULL,NULL,NULL),
(2,'FG-260809000002','WIP-260716000001','PO-2026-002','Customer A',10,165.50,'in_progress','2026-08-09 10:55:36',NULL,'SOFT',188.67,185.37,NULL,NULL),
(3,'FG-260809000003','WIP-260716000001','PS26072001','PT. SEJIN',2,8.00,'finished','2026-08-09 12:06:41','2026-08-09 12:06:41',NULL,NULL,NULL,NULL,NULL),
(4,'FG-260809000004','WIP-260716000001','PS26072001','PT. SEJIN',1,9999.00,'finished','2026-08-09 12:06:49','2026-08-09 12:06:49',NULL,NULL,NULL,NULL,NULL),
(5,'FG-260809000005','WIP-260716000001','PS26072001','SEJIN',1,5.00,'finished','2026-08-09 14:37:28','2026-08-09 14:37:29',NULL,NULL,NULL,3,6),
(6,'FG-260809000006','WIP-260809000017','PO-2026-002','Customer A',0,0.00,'in_progress','2026-08-09 16:37:18',NULL,NULL,NULL,NULL,NULL,NULL),
(7,'FG-260817000001','WIP-260817000001','THIPM26081705','PT. SHOETOWN LIGUNG INDONESIA',1,10.00,'finished','2026-08-17 06:17:08','2026-08-17 06:17:13',NULL,NULL,NULL,6,9),
(8,'FG-260823000001','WIP-260823000001','cvvv','PT. HARDASES ABADI INDONESIA',1,100.00,'finished','2026-08-23 18:47:27','2026-08-23 18:47:32',NULL,NULL,NULL,7,10);
/*!40000 ALTER TABLE `tbl_packing` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_packing_po`
--

LOCK TABLES `tbl_packing_po` WRITE;
/*!40000 ALTER TABLE `tbl_packing_po` DISABLE KEYS */;
INSERT INTO `tbl_packing_po` VALUES
(1,1,15,'PS26072001','SO-2026-001',12.50),
(2,2,NULL,'PO-2026-002','',10.00),
(3,3,15,'PS26072001','sejin-20260720',12.50),
(4,4,15,'PS26072001','',9999.00),
(5,5,15,'PS26072001','',5.00),
(6,6,2,'PO-2026-002','SO-2026-001',1.00),
(7,7,24,'THIPM26081705','UAT-MRP-SL043-2608170616',10.00),
(8,8,26,'cvvv','PS26082302',100.00);
/*!40000 ALTER TABLE `tbl_packing_po` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_packing_roll`
--

LOCK TABLES `tbl_packing_roll` WRITE;
/*!40000 ALTER TABLE `tbl_packing_roll` DISABLE KEYS */;
INSERT INTO `tbl_packing_roll` VALUES
(1,1,1,5,12.50,'2026-08-09 06:42:34',NULL),
(2,2,1,10,165.50,'2026-08-09 10:55:37','AESS lot'),
(3,3,1,2,8.00,'2026-08-09 12:06:41',NULL),
(4,4,1,1,9999.00,'2026-08-09 12:06:49',NULL),
(5,5,1,1,5.00,'2026-08-09 14:37:29',NULL),
(6,7,1,1,10.00,'2026-08-17 06:17:12',NULL),
(7,8,1,1,100.00,'2026-08-23 18:47:30','wave invoice');
/*!40000 ALTER TABLE `tbl_packing_roll` ENABLE KEYS */;
UNLOCK TABLES;

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
  PRIMARY KEY (`id`),
  KEY `idx_kode_palet` (`kode_palet`),
  KEY `idx_tanggal` (`tanggal`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_palet_movement`
--

LOCK TABLES `tbl_palet_movement` WRITE;
/*!40000 ALTER TABLE `tbl_palet_movement` DISABLE KEYS */;
INSERT INTO `tbl_palet_movement` VALUES
(1,'KY-0001','IN','2026-06-23','','2026-06-21 01:09:47'),
(2,'KY-00002','IN','2026-06-23','','2026-06-21 01:27:19'),
(3,'KY-00002','OUT','2026-06-23','Proses 1','2026-06-21 01:28:11'),
(4,'KY-001','IN','2026-07-02','123456','2026-07-02 09:05:14'),
(5,'KY-002','IN','2026-07-02','','2026-07-02 09:06:02'),
(6,'DEBUG-TEST-001','IN','2026-07-02','test','2026-07-02 09:07:09'),
(7,'DEBUG-TEST-002','IN','2026-07-02','','2026-07-02 09:07:28'),
(9,'KY-VERIFY-FIX','IN','2026-07-02','','2026-07-02 09:09:25'),
(10,'KY-VERIFY-LOG','IN','2026-07-02','','2026-07-02 09:09:31'),
(11,'KY-1234561','IN','2026-07-02','Ok','2026-07-02 09:13:03'),
(12,'KY-1234562','IN','2026-07-02','Ok','2026-07-02 09:13:35'),
(13,'KY-1234564','IN','2026-07-02','Ok','2026-07-02 09:25:26'),
(14,'KY-0044','IN','2026-07-03','Keterangan','2026-07-03 10:30:44'),
(15,'GAPPAL1786268682','IN','2026-08-09','','2026-08-09 09:44:42'),
(16,'GAPPAL1786268682','OUT','2026-08-09','','2026-08-09 09:44:43'),
(17,'GAPPAL1786268717','IN','2026-08-09','gap','2026-08-09 09:45:18'),
(18,'GAPPAL1786268717','OUT','2026-08-09','gap-out','2026-08-09 09:45:19'),
(19,'VKYPAL1786268736','IN','2026-08-09','','2026-08-09 09:45:36'),
(20,'VKYPAL1786268736','OUT','2026-08-09','','2026-08-09 09:45:37'),
(21,'KY-T0809000000','IN','2026-08-09','test proses','2026-08-09 16:16:48'),
(22,'KY-T0809000000','IN','2026-08-09','test proses','2026-08-09 16:20:24'),
(23,'KY-T0809000000','IN','2026-08-09','test proses','2026-08-09 16:23:33'),
(24,'KY-SMOKE-294057','IN','2026-08-09','smoke','2026-08-09 16:47:37'),
(25,'KY-SMOKE-294057','OUT','2026-08-09','smoke out','2026-08-09 16:47:38'),
(26,'KY-UAT-2608170616','IN','2026-08-17','UAT MRP SL043','2026-08-17 06:16:52'),
(27,'KY-PS27-260823','IN','2026-08-23','seed wave PS26082302','2026-08-23 18:47:16'),
(28,'KY-0000012345','IN','2026-08-24',NULL,'2026-08-24 04:06:47'),
(29,'KY-TEST-001','IN','2026-08-26',NULL,'2026-08-26 02:39:21');
/*!40000 ALTER TABLE `tbl_palet_movement` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_persiapan_kulit`
--

LOCK TABLES `tbl_persiapan_kulit` WRITE;
/*!40000 ALTER TABLE `tbl_persiapan_kulit` DISABLE KEYS */;
INSERT INTO `tbl_persiapan_kulit` VALUES
(1,'WIP-260716000001','RPI-260716000001','PR-260809000001','PO-2026-002','Black','1.0mm','Emboss A',NULL,'PU','Emboss',3.50,'saved','2026-08-09 06:34:47','2026-08-09 06:34:48',10,NULL),
(2,'WIP-260809000017','RPI-260809000017','PR-260809000002','PO-2026-002','Black','1.0mm','Emboss A',NULL,'PU','Treatment A',0.00,'draft','2026-08-09 16:16:47',NULL,27,NULL),
(3,'WIP-260809000017','RPI-260809000017','PR-260809000003','PO-2026-002','Black','1.0mm','Emboss A',NULL,'PU','Treatment A',12.00,'completed','2026-08-09 16:16:48','2026-08-09 16:16:50',27,NULL),
(4,'WIP-260809000017','RPI-260809000017','PR-260809000004','PO-2026-002','Black','1.0mm','Emboss A',NULL,'PU','Treatment A',0.00,'draft','2026-08-09 16:20:24',NULL,27,NULL),
(5,'WIP-260809000017','RPI-260809000017','PR-260809000005','PO-2026-002','Black','1.0mm','Emboss A',NULL,'PU','Treatment A',12.00,'completed','2026-08-09 16:20:25','2026-08-09 16:20:26',27,NULL),
(6,'WIP-260809000017','RPI-260809000017','PR-260809000006','PO-2026-002','Black','1.0mm','Emboss A',NULL,'PU','Treatment A',0.00,'draft','2026-08-09 16:23:32',NULL,27,NULL),
(7,'WIP-260809000017','RPI-260809000017','PR-260809000007','PO-2026-002','Black','1.0mm','Emboss A',NULL,'PU','Treatment A',12.00,'completed','2026-08-09 16:23:33','2026-08-09 16:23:34',27,NULL),
(8,'WIP-260809000020','RPI-260809000020','PR-260810000001','PS26072001','BLACK (00A)','1.2-1.4','-',NULL,'PU','PU - Base Coat',0.00,'draft','2026-08-10 01:47:50',NULL,30,NULL),
(9,'WIP-260817000001','RPI-260817000001','PR-260817000001','THIPM26081705','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-33 M',NULL,'PU','Emboss',10.00,'completed','2026-08-17 06:16:53','2026-08-17 06:17:02',35,NULL),
(10,'WIP-260817000001','RPI-260817000001','PR-260818000001','THIPM26081705','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-33 M',NULL,'PU','PU - Base Coat, PU - Color Coat',0.00,'draft','2026-08-18 01:53:36',NULL,35,NULL),
(11,'WIP-260817000001','RPI-260817000001','PR-260818000002','THIPM26081705','PINKSICLE (6FS) FLUORESCENT','1.0 - 1.2','AR-33 M',NULL,'PU','PU - Emboss / Press',0.00,'draft','2026-08-18 02:24:35',NULL,35,NULL),
(12,'WIP-260823000001','RPI-260823000001','PR-260823000001','cvvv','MAROON (48F0)','1.2 - 1.4','DE-23 SG',NULL,'PU','Emboss',100.00,'completed','2026-08-23 18:47:16','2026-08-23 18:47:24',36,NULL),
(13,'WIP-260824000001','RPI-260824000001','PR-260824000001','','BLACK','1.2 - 1.4','AR-194',NULL,'PU','PU - Base Coat, PU - Degrease, PU - Emboss / Press',0.00,'draft','2026-08-24 03:57:48',NULL,37,NULL),
(14,'WIP-260824000002','RPI-260824000002','PR-260824000002','','WHITE LEATHER','1.2 - 1.4','AR-194',NULL,'PU','PU - Base Coat',1000.00,'completed','2026-08-24 04:00:37','2026-08-24 04:11:16',38,NULL),
(15,'WIP-260824000002','RPI-260824000002','PR-260824000003','','WHITE LEATHER','1.2 - 1.4','AR-194',NULL,'PU','PU - Base Coat',0.00,'draft','2026-08-24 04:23:30',NULL,38,NULL),
(16,'WIP-20260826-00002','RPI-260826000001','PR-260826000001','PO-THIPM26082603','CARGO KHAKI','1.2 - 1.4','AR-206 M',NULL,'PU','PU - Emboss / Press',0.00,'draft','2026-08-26 04:27:33',NULL,39,'PU - Base Coat'),
(17,'WIP-20260826-00003','RPI-260826000001','PR-260826000002','PO-THIPM26082603','CARGO KHAKI (3HR)','1.2-1.4','AR-206 M',NULL,'PU','PU - Emboss / Press',1000.00,'completed','2026-08-26 04:27:33','2026-08-26 04:29:06',39,NULL);
/*!40000 ALTER TABLE `tbl_persiapan_kulit` ENABLE KEYS */;
UNLOCK TABLES;

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
  `status` enum('active','selesai') DEFAULT 'active',
  `created_at` datetime DEFAULT current_timestamp(),
  `yl_consumed` tinyint(1) NOT NULL DEFAULT 0,
  `qty_consumed` decimal(12,2) NOT NULL DEFAULT 0.00,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_persiapan_ky`
--

LOCK TABLES `tbl_persiapan_ky` WRITE;
/*!40000 ALTER TABLE `tbl_persiapan_ky` DISABLE KEYS */;
INSERT INTO `tbl_persiapan_ky` VALUES
(1,1,'KY-TEST-1','YL-1',10.00,3.50,'selesai','2026-08-09 06:34:47',0,0.00),
(2,1,'VKYPAL1786268736','VKYYL1786268736',1.00,0.00,'selesai','2026-08-09 09:45:37',0,0.00),
(3,3,'KY-T0809000000','YL-T0809000000',10.00,12.00,'selesai','2026-08-09 16:16:49',1,12.00),
(4,5,'KY-T0809000000','YL-T0809000000',10.00,12.00,'selesai','2026-08-09 16:20:25',1,12.00),
(5,7,'KY-T0809000000','YL-T0809000000',10.00,12.00,'selesai','2026-08-09 16:23:33',1,12.00),
(6,9,'KY-UAT-2608170616','YL-UAT-2608170616',10.00,10.00,'selesai','2026-08-17 06:16:56',1,10.00),
(7,12,'KY-PS27-260823','YL-PS27-260823',100.00,100.00,'selesai','2026-08-23 18:47:19',1,100.00),
(8,14,'KY-0000012345','1200',1000.00,1000.00,'selesai','2026-08-24 04:10:14',1,1000.00);
/*!40000 ALTER TABLE `tbl_persiapan_ky` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_persiapan_reprint`
--

LOCK TABLES `tbl_persiapan_reprint` WRITE;
/*!40000 ALTER TABLE `tbl_persiapan_reprint` DISABLE KEYS */;
INSERT INTO `tbl_persiapan_reprint` VALUES
(1,1,1,'2026-08-09 16:08:38'),
(2,17,1,'2026-08-26 04:29:15');
/*!40000 ALTER TABLE `tbl_persiapan_reprint` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_persiapan_scan`
--

LOCK TABLES `tbl_persiapan_scan` WRITE;
/*!40000 ALTER TABLE `tbl_persiapan_scan` DISABLE KEYS */;
INSERT INTO `tbl_persiapan_scan` VALUES
(1,1,'KY-TEST-1','YL-1','2026-08-09 06:34:47',NULL),
(2,1,'VKYPAL1786268736','VKYYL1786268736','2026-08-09 09:45:37',NULL),
(3,3,'KY-T0809000000','YL-T0809000000','2026-08-09 16:16:49',NULL),
(4,5,'KY-T0809000000','YL-T0809000000','2026-08-09 16:20:25',NULL),
(5,7,'KY-T0809000000','YL-T0809000000','2026-08-09 16:23:33',NULL),
(6,9,'KY-UAT-2608170616','YL-UAT-2608170616','2026-08-17 06:16:56',NULL),
(7,12,'KY-PS27-260823','YL-PS27-260823','2026-08-23 18:47:19',NULL),
(8,14,'KY-0000012345','1200','2026-08-24 04:10:14',NULL),
(9,17,'KY-TEST-001','Pu','2026-08-26 04:27:33',1000.00);
/*!40000 ALTER TABLE `tbl_persiapan_scan` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_persiapan_ukur`
--

LOCK TABLES `tbl_persiapan_ukur` WRITE;
/*!40000 ALTER TABLE `tbl_persiapan_ukur` DISABLE KEYS */;
INSERT INTO `tbl_persiapan_ukur` VALUES
(1,1,3.50,'2026-08-09 06:34:48',1),
(2,3,12.00,'2026-08-09 16:16:49',3),
(3,5,12.00,'2026-08-09 16:20:25',4),
(4,7,12.00,'2026-08-09 16:23:34',5),
(5,9,10.00,'2026-08-17 06:17:00',6),
(6,12,100.00,'2026-08-23 18:47:22',7),
(7,14,1000.00,'2026-08-24 04:11:02',8);
/*!40000 ALTER TABLE `tbl_persiapan_ukur` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_rencana_item`
--

LOCK TABLES `tbl_rencana_item` WRITE;
/*!40000 ALTER TABLE `tbl_rencana_item` DISABLE KEYS */;
INSERT INTO `tbl_rencana_item` VALUES
(1,1,'RPI-260702000001','WIP-260702000001',65,'Customer A','KLT-001','1.2mm','Brown','Plain','SW01','Item 1',1,'2026-07-02 09:44:12',NULL,NULL,NULL,NULL,NULL),
(2,1,'RPI-260702000002','WIP-260702000002',66,'Customer B','KLT-002','1.2','Brown','Emboss X','SW02','Item 2',2,'2026-07-02 09:44:13',NULL,NULL,NULL,NULL,NULL),
(3,2,'RPI-260702000003','WIP-260702000003',65,'Customer A','KLT-001','1.2mm','Brown','RP','BROWN DARK','Ketarangan 1',1,'2026-07-02 09:47:56',NULL,NULL,NULL,NULL,NULL),
(4,2,'RPI-260702000004','WIP-260702000004',66,'Customer B','KLT-002','1.2','Brown','RP 1','DARK GREY','Keterangan 2',2,'2026-07-02 09:47:56',NULL,NULL,NULL,NULL,NULL),
(5,2,'RPI-260702000005','WIP-260702000005',65,'Customer A','KLT-002','1.2','Brown','RP 2','DARK BLUE','Keterngan 3',3,'2026-07-02 09:47:57',NULL,NULL,NULL,NULL,NULL),
(6,3,'RPI-260703000001','WIP-260703000001',65,'Customer A','KLT-005','1.2','Dark Blue',NULL,NULL,NULL,1,'2026-07-03 10:43:30',NULL,NULL,NULL,NULL,NULL),
(7,3,'RPI-260703000002','WIP-260703000002',66,'Customer B','KLT-002','1.2','Brown',NULL,NULL,NULL,2,'2026-07-03 10:43:31',NULL,NULL,NULL,NULL,NULL),
(8,4,'RPI-260703000003','WIP-260703000003',65,'Customer A','KLT-001','1.2mm','Brown','RP','BROWN DARK','Ketarangan 1',1,'2026-07-03 10:49:37',NULL,NULL,NULL,NULL,NULL),
(9,4,'RPI-260703000004','WIP-260703000004',66,'Customer B','KLT-002','1.2','Brown','RP','BROWN DARK','Ketarangan 1',2,'2026-07-03 10:49:38',NULL,NULL,NULL,NULL,NULL),
(10,5,'RPI-260716000001','WIP-260716000001',65,'Customer A',NULL,'1.0mm','Black','Emboss A','SW-BLK-02',NULL,1,'2026-07-16 10:35:03','BK-PU-B','RPI-10MM-EMBOSS-BLACK-01',NULL,3,6),
(11,6,'RPI-260809000001','WIP-260809000001',65,'Customer A',NULL,'1.2mm','Brown','Plain','SW-BLK-02',NULL,1,'2026-08-09 14:59:57',NULL,NULL,'Premium Leather',NULL,NULL),
(12,8,'RPI-260809000002','WIP-260809000002',61,'WEALTH VAST CO,LTD',NULL,'1.0 - 1.2','ARMORY NAVY (4LX)','R-131 M','6CV',NULL,1,'2026-08-09 15:06:32',NULL,NULL,'(PM) GENERIC PU COATED LEATHER',NULL,NULL),
(13,9,'RPI-260809000003','WIP-260809000003',65,'Customer A',NULL,'1.0mm','Black','Emboss A','SW-BLK-02',NULL,1,'2026-08-09 15:08:54','BK-PU-B',NULL,'Standard Leather',NULL,NULL),
(14,10,'RPI-260809000004','WIP-260809000004',66,'Customer B',NULL,'1.4mm','Red','Emboss B','SW-RED-05',NULL,1,'2026-08-09 15:17:03',NULL,NULL,'Leather Sheet C',NULL,NULL),
(15,11,'RPI-260809000005','WIP-260809000005',40,'PT. SEJIN FASHION INDONESIA',NULL,'1.4-1.6','COOL GREY (06B)','-','-',NULL,1,'2026-08-09 15:20:40',NULL,NULL,'(PM) GENERIC PU COATED',NULL,NULL),
(16,12,'RPI-260809000006','WIP-260809000006',40,'PT. SEJIN FASHION INDONESIA',NULL,'1.2-1.4','BLACK (00A)','-','-',NULL,1,'2026-08-09 15:22:27',NULL,NULL,'SPARK CT',NULL,NULL),
(17,13,'RPI-260809000007','WIP-260809000007',66,'Customer B',NULL,'1.4mm','Red','Emboss B','SW-RED-05',NULL,1,'2026-08-09 15:26:42',NULL,NULL,'Leather Sheet C',NULL,NULL),
(18,14,'RPI-260809000008','WIP-260809000008',66,'Customer B',NULL,'1.4mm','Red','Emboss B','SW-RED-05',NULL,1,'2026-08-09 15:26:45',NULL,NULL,'Leather Sheet C',NULL,NULL),
(19,15,'RPI-260809000009','WIP-260809000009',40,'PT. SEJIN FASHION INDONESIA',NULL,'1.2-1.4','BLACK (00A)','-','-',NULL,1,'2026-08-09 15:28:36',NULL,NULL,'SPARK CT',NULL,NULL),
(20,16,'RPI-260809000010','WIP-260809000010',65,'Customer A',NULL,'1.0mm','Black','Emboss A','SW-BLK-02',NULL,1,'2026-08-09 16:05:38',NULL,NULL,'Leather Sheet B',NULL,NULL),
(21,17,'RPI-260809000011','WIP-260809000011',65,'Customer A',NULL,'1.0mm','Black','Emboss A','SW-BLK-02',NULL,1,'2026-08-09 16:05:41',NULL,NULL,'Leather Sheet B',NULL,NULL),
(22,18,'RPI-260809000012','WIP-260809000012',40,'PT. SEJIN FASHION INDONESIA',NULL,'1.2-1.4','BLACK (00A)','-','-',NULL,1,'2026-08-09 16:05:46',NULL,NULL,'SPARK CT',NULL,NULL),
(23,19,'RPI-260809000013','WIP-260809000013',65,'Customer A',NULL,'1.0mm','Black','Emboss A','SW-BLK-02',NULL,1,'2026-08-09 16:05:49',NULL,NULL,'Leather Sheet B',NULL,NULL),
(24,20,'RPI-260809000014','WIP-260809000014',65,'Customer A',NULL,'1.0mm','Black','Emboss A','SW-BLK-02',NULL,1,'2026-08-09 16:09:09',NULL,NULL,'Leather Sheet B',NULL,NULL),
(25,21,'RPI-260809000015','WIP-260809000015',65,'Customer A',NULL,'1.0mm','Black','Emboss A','SW-BLK-02',NULL,1,'2026-08-09 16:09:13',NULL,NULL,'Leather Sheet B',NULL,NULL),
(26,22,'RPI-260809000016','WIP-260809000016',40,'PT. SEJIN FASHION INDONESIA',NULL,'1.2-1.4','BLACK (00A)','-','-',NULL,1,'2026-08-09 16:09:17',NULL,NULL,'SPARK CT',NULL,NULL),
(27,23,'RPI-260809000017','WIP-260809000017',65,'Customer A',NULL,'1.0mm','Black','Emboss A','SW-BLK-02',NULL,1,'2026-08-09 16:09:21',NULL,NULL,'Leather Sheet B',NULL,NULL),
(28,24,'RPI-260809000018','WIP-260809000018',65,'Customer A',NULL,'1.0mm','Black','Emboss A','SW-BLK-02',NULL,1,'2026-08-09 17:21:24',NULL,NULL,'Leather Sheet B',NULL,NULL),
(29,25,'RPI-260809000019','WIP-260809000019',65,'Customer A',NULL,'1.0mm','Black','Emboss A','SW-BLK-02',NULL,1,'2026-08-09 17:21:34',NULL,NULL,'Leather Sheet B',NULL,NULL),
(30,26,'RPI-260809000020','WIP-260809000020',40,'PT. SEJIN FASHION INDONESIA',NULL,'1.2-1.4','BLACK (00A)','-','-',NULL,1,'2026-08-09 17:21:49',NULL,NULL,'SPARK CT',NULL,NULL),
(31,27,'RPI-260809000021','WIP-260809000021',65,'Customer A',NULL,'1.0mm','Black','Emboss A','SW-BLK-02',NULL,1,'2026-08-09 17:21:57',NULL,NULL,'Leather Sheet B',NULL,NULL),
(32,28,'RPI-260814000001','WIP-260814000001',67,'Customer A',NULL,'1.0mm','Black','Emboss A','SW-BLK-02',NULL,1,'2026-08-14 05:26:15',NULL,NULL,'Leather Sheet B',NULL,NULL),
(33,28,'RPI-260814000002','WIP-260814000002',67,'Customer A',NULL,'1.0mm','Black','Emboss A','SW-BLK-02',NULL,2,'2026-08-14 05:26:16',NULL,NULL,'Leather Sheet B-2',NULL,NULL),
(34,28,'RPI-260814000003','WIP-260814000003',68,'Customer B',NULL,'1.4mm','Red','Emboss B','SW-RED-05',NULL,3,'2026-08-14 05:26:16',NULL,NULL,'Leather Sheet C',NULL,NULL),
(35,29,'RPI-260817000001','WIP-260817000001',28,'PT. SHOETOWN LIGUNG INDONESIA',NULL,'1.0 - 1.2','PINKSICLE (6FS) FLUORESCENT','AR-33 M','6FS',NULL,1,'2026-08-17 06:16:50',NULL,NULL,'VIRGIN HYDRO PU',6,9),
(36,30,'RPI-260823000001','WIP-260823000001',51,'PT. HARDASES ABADI INDONESIA',NULL,'1.2 - 1.4','MAROON (48F0)','DE-23 SG','assa',NULL,1,'2026-08-23 18:47:15',NULL,NULL,'ACTION LEATHER',7,10),
(37,31,'RPI-260824000001','WIP-260824000001',41,'PT. LONGRICH INDONESIA-UA',NULL,'1.2 - 1.4','BLACK','AR-194','LONGRICH',NULL,1,'2026-08-24 03:53:46','BLACK',NULL,'NAPPA NATURAL LEATHER',NULL,NULL),
(38,32,'RPI-260824000002','WIP-260824000002',41,'PT. LONGRICH INDONESIA-UA',NULL,'1.2 - 1.4','WHITE LEATHER','AR-194','LONGRICH',NULL,1,'2026-08-24 04:00:10','WHITE',NULL,'NAPPA NATURAL LEATHER',NULL,NULL),
(39,33,'RPI-260826000001','WIP-260826000001',36,'PT. SUMBER MASANDA JAYA',NULL,'1.2 - 1.4','CARGO KHAKI','AR-206 M','TMTK0272024041601','Ket',1,'2026-08-26 02:57:25','BLACK',NULL,'VIRGIN  HYDRO PU',NULL,NULL);
/*!40000 ALTER TABLE `tbl_rencana_item` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_rencana_item_po`
--

LOCK TABLES `tbl_rencana_item_po` WRITE;
/*!40000 ALTER TABLE `tbl_rencana_item_po` DISABLE KEYS */;
INSERT INTO `tbl_rencana_item_po` VALUES
(1,3,1,100.00,100.00),
(2,3,4,50.00,50.00),
(3,4,7,60.00,60.00),
(4,5,5,30.00,30.00),
(5,8,2,80.00,60.00),
(6,8,6,40.00,35.00),
(7,9,3,120.00,110.00),
(10,10,2,2.00,2.00),
(11,12,9,2000.00,1.00),
(12,14,3,10.00,1.00),
(13,15,15,150.00,150.00),
(14,16,16,150.00,100.00),
(15,17,3,9.00,1.00),
(19,19,16,50.00,30.00),
(21,18,3,8.00,2.00),
(22,20,2,18.00,1.00),
(25,21,2,17.00,2.00),
(27,22,16,20.00,1.00),
(28,23,2,15.00,1.00),
(32,25,2,13.00,2.00),
(34,26,16,19.00,1.00),
(35,27,2,11.00,1.00),
(36,28,2,10.00,1.00),
(41,30,16,18.00,1.00),
(42,31,2,7.00,1.00),
(43,32,2,6.00,6.00),
(44,33,6,5.00,5.00),
(45,34,3,6.00,6.00),
(46,35,24,100.00,10.00),
(47,24,2,1.00,1.00),
(48,29,2,2.00,2.00),
(49,36,26,2000.00,100.00),
(50,39,34,15000.00,15000.00);
/*!40000 ALTER TABLE `tbl_rencana_item_po` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_rencana_produksi`
--

LOCK TABLES `tbl_rencana_produksi` WRITE;
/*!40000 ALTER TABLE `tbl_rencana_produksi` DISABLE KEYS */;
INSERT INTO `tbl_rencana_produksi` VALUES
(1,'RP-260702000001',NULL,'Plan Juli 2026','draft','2026-07-02 09:44:12','2026-07-02'),
(2,'RP-260702000002',NULL,'RENCANA PRODUKSI 2 JULY','active','2026-07-02 09:47:55','2026-07-02'),
(3,'RP-260703000001',NULL,'RENCANA PRODUKSI 3 JULY','draft','2026-07-03 10:43:30','2026-07-03'),
(4,'RP-260703000002',NULL,'RENCANA PRODUKSI 3B','active','2026-07-03 10:49:37','2026-07-03'),
(5,'RP-260716000001',NULL,'Rencana Produksi 16 July','active','2026-07-16 10:35:03','2026-07-16'),
(6,'RP-260809000001',NULL,'ddsds','active','2026-08-09 14:59:57','2026-08-09'),
(8,'RP-260809000003',NULL,'SMOKE AUTO-SYNC 2026-08-09','active','2026-08-09 15:06:32','2026-08-09'),
(9,'RP-260809000004',NULL,'assasasa','active','2026-08-09 15:08:54','2026-08-09'),
(10,'RP-260809000005',NULL,'TEST FROM PO 2026-08-09','active','2026-08-09 15:17:02','2026-08-09'),
(11,'RP-260809000006',NULL,'mmmmm','active','2026-08-09 15:20:39','2026-08-09'),
(12,'RP-260809000007',NULL,'aaaa','active','2026-08-09 15:22:27','2026-08-09'),
(13,'RP-260809000008',NULL,'TEST FROM PO 2026-08-09','active','2026-08-09 15:26:42','2026-08-09'),
(14,'RP-260809000009',NULL,'TEST REPLACE PO 2026-08-09','active','2026-08-09 15:26:45','2026-08-09'),
(15,'RP-260809000010',NULL,'mmmm','active','2026-08-09 15:28:36','2026-08-09'),
(16,'RP-260809000011',NULL,'TEST FROM PO 2026-08-09','active','2026-08-09 16:05:38','2026-08-09'),
(17,'RP-260809000012',NULL,'TEST REPLACE PO 2026-08-09','active','2026-08-09 16:05:41','2026-08-09'),
(18,'RP-260809000013',NULL,'TEST EMBOS DASH 2026-08-09','active','2026-08-09 16:05:46','2026-08-09'),
(19,'RP-260809000014',NULL,'TEST OVERBOOK 2026-08-09','active','2026-08-09 16:05:49','2026-08-09'),
(20,'RP-260809000015',NULL,'TEST FROM PO 2026-08-09','active','2026-08-09 16:09:09','2026-08-09'),
(21,'RP-260809000016',NULL,'TEST REPLACE PO 2026-08-09','active','2026-08-09 16:09:13','2026-08-09'),
(22,'RP-260809000017',NULL,'TEST EMBOS DASH 2026-08-09','active','2026-08-09 16:09:17','2026-08-09'),
(23,'RP-260809000018',NULL,'TEST OVERBOOK 2026-08-09','active','2026-08-09 16:09:21','2026-08-09'),
(24,'RP-260809000019',NULL,'TEST FROM PO 2026-08-09','active','2026-08-09 17:21:24','2026-08-09'),
(25,'RP-260809000020',NULL,'TEST REPLACE PO 2026-08-09','active','2026-08-09 17:21:33','2026-08-09'),
(26,'RP-260809000021',NULL,'TEST EMBOS DASH 2026-08-09','active','2026-08-09 17:21:48','2026-08-09'),
(27,'RP-260809000022',NULL,'TEST OVERBOOK 2026-08-09','active','2026-08-09 17:21:56','2026-08-09'),
(28,'RP-260814000001',NULL,'RENCANA1','active','2026-08-14 05:26:15','2026-08-14'),
(29,'RP-260817000001',NULL,'UAT MRP SL043 2608170616','active','2026-08-17 06:16:50','2026-08-17'),
(30,'RP-260823000001',NULL,'WAVE PS26082302 2026-08-23','active','2026-08-23 18:47:15','2026-08-23'),
(31,'RP-260824000001',NULL,'TEST 28','active','2026-08-24 03:53:46','2026-08-24'),
(32,'RP-260824000002',NULL,'TESTT NAPPA','active','2026-08-24 04:00:10','2026-08-24'),
(33,'RP-260826000001',NULL,'TEST 2608','active','2026-08-26 02:57:24','2026-08-26');
/*!40000 ALTER TABLE `tbl_rencana_produksi` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbl_rencana_produksi_detail`
--

DROP TABLE IF EXISTS `tbl_rencana_produksi_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_rencana_produksi_detail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `rencana_id` int(11) NOT NULL,
  `po_id` int(11) DEFAULT NULL,
  `no_po` varchar(50) NOT NULL,
  `no_so` varchar(50) DEFAULT NULL,
  `item_name` varchar(200) DEFAULT NULL,
  `sq_ft` decimal(12,2) DEFAULT 0.00,
  `qty_order` decimal(12,2) DEFAULT 0.00,
  `qty_proses` decimal(12,2) DEFAULT 0.00,
  `qty_sisa` decimal(12,2) DEFAULT 0.00,
  PRIMARY KEY (`id`),
  KEY `idx_rencana` (`rencana_id`),
  CONSTRAINT `tbl_rencana_produksi_detail_ibfk_1` FOREIGN KEY (`rencana_id`) REFERENCES `tbl_rencana_produksi` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_rencana_produksi_detail`
--

LOCK TABLES `tbl_rencana_produksi_detail` WRITE;
/*!40000 ALTER TABLE `tbl_rencana_produksi_detail` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbl_rencana_produksi_detail` ENABLE KEYS */;
UNLOCK TABLES;

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

LOCK TABLES `tbl_seq` WRITE;
/*!40000 ALTER TABLE `tbl_seq` DISABLE KEYS */;
INSERT INTO `tbl_seq` VALUES
('BC-K',8,'BC-K','260809'),
('BC-M',7,'BC-M','260809'),
('BC-R',7,'BC-R','260809'),
('FG',1,'FG','260823'),
('LW',1,'LW','260826'),
('PR',2,'PR','260826'),
('RP',1,'RP','260826'),
('RPI',1,'RPI','260826'),
('WIP',1,'WIP','260826'),
('WIP-PERSIAPAN',3,'WIP','20260826');
/*!40000 ALTER TABLE `tbl_seq` ENABLE KEYS */;
UNLOCK TABLES;

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
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_internal` (`kode_internal`),
  KEY `kimia_id` (`kimia_id`),
  KEY `idx_gudang` (`gudang`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_kimia_in`
--

LOCK TABLES `tbl_stok_kimia_in` WRITE;
/*!40000 ALTER TABLE `tbl_stok_kimia_in` DISABLE KEYS */;
INSERT INTO `tbl_stok_kimia_in` VALUES
(1,'BC-K-260623000001',2,100.00,68.00,'kg','2027-06-23','2026-06-23','kimia','2026-06-21 01:48:38',NULL,5,'KIM-002','Chemical Base B'),
(2,'BC-K-260623000002',3,100.00,89.00,'kg','2027-06-23','2026-06-23','mixing','2026-06-21 01:48:49',NULL,6,'KIM-003','Hardener'),
(3,'BC-K-260703000001',2,100.00,100.00,'kg','2027-07-03','2026-07-03','kimia','2026-07-03 10:33:08',NULL,5,'KIM-002','Chemical Base B'),
(4,'BC-K-260809000001',1,10.00,10.00,'kg','2027-08-09','2026-08-09','kimia','2026-08-09 07:05:52',1,4,'KIM-001','Chemical Base A'),
(5,'BC-K-260809000002',1,100.00,97.00,'kg','2027-08-09','2026-08-09','kimia','2026-08-09 09:45:19',NULL,4,'KIM-001','Chemical Base A'),
(6,'BC-K-260809000003',27,5.00,4.50,'kg','2027-08-09','2026-08-09','mixing','2026-08-09 16:51:06',1,2,'MCH-004-A00020','60VH'),
(7,'BC-K-260809000004',NULL,5.00,5.00,'kg','2027-08-09','2026-08-09','kimia','2026-08-09 17:41:42',1,7,'GAPCHEM1786268682','Gap Chem'),
(8,'BC-K-260809000005',7,5.00,4.50,'kg','2027-08-09','2026-08-09','mixing','2026-08-09 17:48:15',1,7,'GAPCHEM1786268682','Gap Chem'),
(9,'BC-K-260809000006',7,5.00,4.50,'kg','2027-08-09','2026-08-09','mixing','2026-08-09 17:49:28',1,7,'GAPCHEM1786268682','Gap Chem'),
(10,'BC-K-260809000007',7,5.00,4.50,'kg','2027-08-09','2026-08-09','mixing','2026-08-09 17:52:31',1,7,'GAPCHEM1786268682','Gap Chem'),
(11,'BC-K-260809000008',7,5.00,4.50,'kg','2027-08-09','2026-08-09','mixing','2026-08-09 17:53:20',1,7,'GAPCHEM1786268682','Gap Chem');
/*!40000 ALTER TABLE `tbl_stok_kimia_in` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_kimia_out`
--

LOCK TABLES `tbl_stok_kimia_out` WRITE;
/*!40000 ALTER TABLE `tbl_stok_kimia_out` DISABLE KEYS */;
INSERT INTO `tbl_stok_kimia_out` VALUES
(1,2,3,10.00,'produksi',NULL,'2026-06-23',NULL,'2026-06-21 01:57:34',NULL,NULL,NULL,NULL),
(2,1,2,30.00,'produksi',NULL,'2026-06-23',NULL,'2026-06-21 01:57:55',NULL,NULL,NULL,NULL),
(3,2,3,1.00,'mixing',NULL,'2026-07-03',NULL,'2026-07-03 10:35:16',NULL,NULL,NULL,NULL),
(4,1,2,2.00,'produksi','WIP-TEST','2026-08-09',NULL,'2026-08-09 07:05:52',NULL,NULL,NULL,NULL),
(5,5,1,3.00,'produksi','WIP-260716000001','2026-08-09',NULL,'2026-08-09 09:45:21',NULL,NULL,NULL,NULL),
(6,6,27,0.50,'mixing','WIP-SMOKE-KIMIA','2026-08-09',NULL,'2026-08-09 16:51:06',NULL,NULL,NULL,NULL),
(7,8,7,0.50,'mixing','WIP-SMOKE-KIMIA','2026-08-09',NULL,'2026-08-09 17:48:21',NULL,7,'GAPCHEM1786268682','Gap Chem'),
(8,9,7,0.50,'mixing','WIP-SMOKE-KIMIA','2026-08-09',NULL,'2026-08-09 17:49:33',NULL,7,'GAPCHEM1786268682','Gap Chem'),
(9,10,7,0.50,'mixing','WIP-SMOKE-KIMIA','2026-08-09',NULL,'2026-08-09 17:52:38',NULL,7,'GAPCHEM1786268682','Gap Chem'),
(10,11,7,0.50,'mixing','WIP-SMOKE-KIMIA','2026-08-09',NULL,'2026-08-09 17:53:24',NULL,7,'GAPCHEM1786268682','Gap Chem');
/*!40000 ALTER TABLE `tbl_stok_kimia_out` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_material_lain_in`
--

LOCK TABLES `tbl_stok_material_lain_in` WRITE;
/*!40000 ALTER TABLE `tbl_stok_material_lain_in` DISABLE KEYS */;
INSERT INTO `tbl_stok_material_lain_in` VALUES
(1,'BC-M-260809000001',1,8.00,7.00,'roll','2026-08-09','2026-08-09 07:05:55',562,'MAT-001','Thread Nylon'),
(2,'BC-M-260809000002',1,6.00,5.00,'roll','2026-08-09','2026-08-09 16:55:33',562,'MAT-001','Thread Nylon'),
(3,'BC-M-260809000003',NULL,6.00,5.00,'roll','2026-08-09','2026-08-09 17:41:46',562,'MAT-001','Thread Nylon'),
(4,'BC-M-260809000004',NULL,6.00,5.00,'roll','2026-08-09','2026-08-09 17:48:40',562,'MAT-001','Thread Nylon'),
(5,'BC-M-260809000005',NULL,6.00,5.00,'roll','2026-08-09','2026-08-09 17:49:48',562,'MAT-001','Thread Nylon'),
(6,'BC-M-260809000006',NULL,6.00,5.00,'roll','2026-08-09','2026-08-09 17:52:52',562,'MAT-001','Thread Nylon'),
(7,'BC-M-260809000007',NULL,6.00,5.00,'roll','2026-08-09','2026-08-09 17:53:41',562,'MAT-001','Thread Nylon');
/*!40000 ALTER TABLE `tbl_stok_material_lain_in` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_material_lain_out`
--

LOCK TABLES `tbl_stok_material_lain_out` WRITE;
/*!40000 ALTER TABLE `tbl_stok_material_lain_out` DISABLE KEYS */;
INSERT INTO `tbl_stok_material_lain_out` VALUES
(1,1,1,1.00,'WIP-260716000001','2026-08-09',NULL,'2026-08-09 07:05:56',NULL,NULL,NULL),
(2,2,1,1.00,'WIP-SMOKE-MAT','2026-08-09',NULL,'2026-08-09 16:55:33',NULL,NULL,NULL),
(3,3,562,1.00,'WIP-SMOKE-MAT','2026-08-09',NULL,'2026-08-09 17:41:47',562,'MAT-001','Thread Nylon'),
(4,4,562,1.00,'WIP-SMOKE-MAT','2026-08-09',NULL,'2026-08-09 17:48:46',562,'MAT-001','Thread Nylon'),
(5,5,562,1.00,'WIP-SMOKE-MAT','2026-08-09',NULL,'2026-08-09 17:49:53',562,'MAT-001','Thread Nylon'),
(6,6,562,1.00,'WIP-SMOKE-MAT','2026-08-09',NULL,'2026-08-09 17:52:56',562,'MAT-001','Thread Nylon'),
(7,7,562,1.00,'WIP-SMOKE-MAT','2026-08-09',NULL,'2026-08-09 17:53:45',562,'MAT-001','Thread Nylon');
/*!40000 ALTER TABLE `tbl_stok_material_lain_out` ENABLE KEYS */;
UNLOCK TABLES;

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
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_internal` (`kode_internal`),
  KEY `rp_id` (`rp_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_rp_in`
--

LOCK TABLES `tbl_stok_rp_in` WRITE;
/*!40000 ALTER TABLE `tbl_stok_rp_in` DISABLE KEYS */;
INSERT INTO `tbl_stok_rp_in` VALUES
(1,'BC-R-260623000001',1,100.00,97.00,'2026-06-23','2026-06-21 01:59:57',354,'RP-001','RP Gloss'),
(2,'BC-R-260623000002',2,100.00,40.00,'2026-06-23','2026-06-21 02:00:07',355,'RP-002','RP Matte'),
(3,'BC-R-260702000001',1,100.00,99.00,'2026-07-02','2026-07-02 09:28:20',354,'RP-001','RP Gloss'),
(4,'BC-R-260703000001',3,100.00,98.00,'2026-07-03','2026-07-03 10:35:50',356,'RP-003','RP Texture'),
(5,'BC-R-260724000001',2,10.00,10.00,'2026-07-24','2026-07-24 15:29:02',355,'RP-002','RP Matte'),
(6,'BC-R-260809000001',1,25.00,25.00,'2026-08-09','2026-08-09 07:05:53',354,'RP-001','RP Gloss'),
(7,'BC-R-260809000002',4,8.00,7.00,'2026-08-09','2026-08-09 16:53:29',3,'MRP-001-DE107-MT','DE-107 Matte'),
(8,'BC-R-260809000003',NULL,8.00,8.00,'2026-08-09','2026-08-09 17:41:44',3,'MRP-001-DE107-MT','DE-107 Matte'),
(9,'BC-R-260809000004',3,8.00,7.00,'2026-08-09','2026-08-09 17:48:28',3,'MRP-001-DE107-MT','DE-107 Matte'),
(10,'BC-R-260809000005',3,8.00,7.00,'2026-08-09','2026-08-09 17:49:39',3,'MRP-001-DE107-MT','DE-107 Matte'),
(11,'BC-R-260809000006',3,8.00,7.00,'2026-08-09','2026-08-09 17:52:44',3,'MRP-001-DE107-MT','DE-107 Matte'),
(12,'BC-R-260809000007',3,8.00,7.00,'2026-08-09','2026-08-09 17:53:29',3,'MRP-001-DE107-MT','DE-107 Matte');
/*!40000 ALTER TABLE `tbl_stok_rp_in` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_rp_out`
--

LOCK TABLES `tbl_stok_rp_out` WRITE;
/*!40000 ALTER TABLE `tbl_stok_rp_out` DISABLE KEYS */;
INSERT INTO `tbl_stok_rp_out` VALUES
(1,2,2,60.00,NULL,'2026-06-23',NULL,'2026-06-21 02:00:54',NULL,NULL,NULL),
(2,3,1,1.00,NULL,'2026-07-02',NULL,'2026-07-02 09:28:55',NULL,NULL,NULL),
(3,4,3,2.00,NULL,'2026-07-03',NULL,'2026-07-03 10:36:51',NULL,NULL,NULL),
(4,1,1,3.00,'WIP-TEST','2026-08-09',NULL,'2026-08-09 07:05:53',NULL,NULL,NULL),
(5,7,4,1.00,'WIP-SMOKE-RP','2026-08-09',NULL,'2026-08-09 16:53:30',NULL,NULL,NULL),
(7,9,3,1.00,'WIP-SMOKE-RP','2026-08-09',NULL,'2026-08-09 17:48:32',3,'MRP-001-DE107-MT','DE-107 Matte'),
(8,10,3,1.00,'WIP-SMOKE-RP','2026-08-09',NULL,'2026-08-09 17:49:43',3,'MRP-001-DE107-MT','DE-107 Matte'),
(9,11,3,1.00,'WIP-SMOKE-RP','2026-08-09',NULL,'2026-08-09 17:52:47',3,'MRP-001-DE107-MT','DE-107 Matte'),
(10,12,3,1.00,'WIP-SMOKE-RP','2026-08-09',NULL,'2026-08-09 17:53:33',3,'MRP-001-DE107-MT','DE-107 Matte');
/*!40000 ALTER TABLE `tbl_stok_rp_out` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_usage_color`
--

LOCK TABLES `tbl_usage_color` WRITE;
/*!40000 ALTER TABLE `tbl_usage_color` DISABLE KEYS */;
INSERT INTO `tbl_usage_color` VALUES
(1,'WIP-260716000001','LW-260809000001','Test Lot P2',1.50,0.50,'2026-08-09 07:05:54'),
(2,'WIP-260716000001','LW-260809000001','Test Lot P2',1.50,3.00,'2026-08-09 09:45:21'),
(3,'WIP-260716000001','LW-260702000003','RED PREMIUM MIX',201.00,0.10,'2026-08-09 09:45:38');
/*!40000 ALTER TABLE `tbl_usage_color` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_usage_material_lain`
--

LOCK TABLES `tbl_usage_material_lain` WRITE;
/*!40000 ALTER TABLE `tbl_usage_material_lain` DISABLE KEYS */;
INSERT INTO `tbl_usage_material_lain` VALUES
(1,'WIP-260716000001','MAT-001','Thread Nylon',2.00,'roll','2026-08-09 07:05:56'),
(2,'WIP-260809000017','MAT-001','Thread Nylon',0.25,'roll','2026-08-09 16:58:52'),
(3,'WIP-260809000021','MAT-001','Thread Nylon',0.25,'roll','2026-08-09 17:49:08');
/*!40000 ALTER TABLE `tbl_usage_material_lain` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_usage_rp`
--

LOCK TABLES `tbl_usage_rp` WRITE;
/*!40000 ALTER TABLE `tbl_usage_rp` DISABLE KEYS */;
INSERT INTO `tbl_usage_rp` VALUES
(1,'WIP-260716000001','RP Gloss',1.50,'meter','2026-08-09 07:05:55');
/*!40000 ALTER TABLE `tbl_usage_rp` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_yl`
--

LOCK TABLES `tbl_yl` WRITE;
/*!40000 ALTER TABLE `tbl_yl` DISABLE KEYS */;
INSERT INTO `tbl_yl` VALUES
(1,'YL-001','KY-0001','0.3','Brown',100.00,'2026-06-21 01:09:47'),
(2,'YL-002','KY-0001','0.4','Black',100.00,'2026-06-21 01:09:47'),
(3,'YL-1001','KY-00002','0.3','Brown',100.00,'2026-06-21 01:27:19'),
(4,'YL-1002','KY-00002','0.4','Yellow',100.00,'2026-06-21 01:27:19'),
(5,'KLT-002','KY-001','1.2','Brown',0.00,'2026-07-02 09:05:14'),
(7,'KLT-001','KY-001','1.2mm','Brown',5.00,'2026-07-02 09:05:14'),
(12,'KLT-NEW-999','DEBUG-TEST-002','2mm','Red',10.00,'2026-07-02 09:07:28'),
(14,'KLT-001','KY-VERIFY-FIX','1.2mm','Brown',99.00,'2026-07-02 09:09:25'),
(15,'KLT-002','KY-VERIFY-LOG','1.2','Brown',50.00,'2026-07-02 09:09:31'),
(16,'KLT-001','KY-1234561','1.2mm','Brown',2000.00,'2026-07-02 09:13:03'),
(17,'KLT-002','KY-1234561','1.2','Brown',1000.00,'2026-07-02 09:13:03'),
(19,'KLT-001','KY-1234562','1.2mm','Brown',1000.00,'2026-07-02 09:13:35'),
(21,'KLT-002','KY-1234562','1.2','Brown',10.00,'2026-07-02 09:13:35'),
(22,'KLT-001','KY-1234564','1.2mm','Brown',10.00,'2026-07-02 09:25:26'),
(23,'KLT-002','KY-1234564','1.2','Brown',20.00,'2026-07-02 09:25:26'),
(24,'KLT-005','KY-0044','1.2','Dark Blue',100.00,'2026-07-03 10:30:44'),
(25,'KLT-004','KY-0044','2','Brown',100.00,'2026-07-03 10:30:44'),
(26,'KLT-002','KY-0044','1.2','Brown',0.00,'2026-07-03 10:30:44'),
(29,'YL-T0809000000','KY-T0809000000','1.2','BLACK',38.00,'2026-08-09 16:16:48'),
(33,'YL-UAT-2608170616','KY-UAT-2608170616','1.2','PINKSICLE (6FS) FLUORESCENT',40.00,'2026-08-17 06:16:52'),
(34,'YL-PS27-260823','KY-PS27-260823','1.2','MAROON',20.00,'2026-08-23 18:47:16'),
(35,'1200','KY-0000012345','1200','WHITE',200.00,'2026-08-24 04:06:47'),
(36,'Pu','KY-TEST-001','1.2-1.4','CARGO KHAKI (3HR)',1000.00,'2026-08-26 02:39:21');
/*!40000 ALTER TABLE `tbl_yl` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_yl_movement`
--

LOCK TABLES `tbl_yl_movement` WRITE;
/*!40000 ALTER TABLE `tbl_yl_movement` DISABLE KEYS */;
INSERT INTO `tbl_yl_movement` VALUES
(1,'YL-001','KY-0001','OUT','','',10.00,'2026-06-23',NULL,'2026-06-21 01:10:51'),
(2,'KLT-NEW-999','DEBUG-TEST-002','OUT','2mm','Red',10.00,'2026-08-09',NULL,'2026-08-09 07:05:58'),
(4,'GAPYL1786268717','GAPPAL1786268717','OUT','1.0','Black',5.00,'2026-08-09',NULL,'2026-08-09 09:45:18'),
(5,'YL-T0809000000','KY-T0809000000','OUT','1.2','BLACK',12.00,'2026-08-09',NULL,'2026-08-09 16:16:49'),
(6,'YL-T0809000000','KY-T0809000000','OUT','1.2','BLACK',12.00,'2026-08-09',NULL,'2026-08-09 16:20:26'),
(7,'YL-T0809000000','KY-T0809000000','OUT','1.2','BLACK',12.00,'2026-08-09',NULL,'2026-08-09 16:23:34'),
(9,'YL-SMOKE-294057','KY-SMOKE-294057','OUT',NULL,NULL,4.00,'2026-08-09',NULL,'2026-08-09 16:47:38'),
(10,'YL-UAT-2608170616','KY-UAT-2608170616','OUT','1.2','PINKSICLE (6FS) FLUORESCENT',10.00,'2026-08-17',NULL,'2026-08-17 06:17:01'),
(11,'YL-PS27-260823','KY-PS27-260823','OUT','1.2','MAROON',100.00,'2026-08-23',NULL,'2026-08-23 18:47:23'),
(12,'1200','KY-0000012345','OUT','1200','WHITE',1000.00,'2026-08-24',NULL,'2026-08-24 04:11:09');
/*!40000 ALTER TABLE `tbl_yl_movement` ENABLE KEYS */;
UNLOCK TABLES;

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

-- Dump completed on 2026-08-26 12:58:51
