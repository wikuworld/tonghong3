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
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_gudang_fg`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_gudang_fg` WRITE;
/*!40000 ALTER TABLE `tbl_gudang_fg` DISABLE KEYS */;
INSERT INTO `tbl_gudang_fg` VALUES
(1,1,'FG-260930000005','WIP-20260930-00001','PT. ADIS DIMENSION FOOTWEAR',5,950.00,'out','2026-09-30 12:12:23','2026-09-30 12:16:29','Scan SJ THI-M261007001',1,'THI-M261007001','ok',NULL),
(2,2,'FG-261001000005','WIP-20261001-00001','PT. Test Januari Indonesia',4,1500.00,'out','2026-10-01 22:57:39','2026-10-01 23:05:08','Scan SJ THI-M261010001',2,'THI-M261010001','ok',NULL),
(3,3,'FG-261001000007','WIP-20261001-00001','TAE KWANG INDUSTRIAL CO LTD',1,1000.00,'in_stock','2026-10-01 22:59:14',NULL,NULL,NULL,NULL,NULL,NULL),
(4,4,'FG-261001000011','WIP-20261001-00001','CHANGSHIN INC',3,1500.00,'in_stock','2026-10-01 23:09:59',NULL,NULL,NULL,NULL,NULL,NULL),
(5,5,'FG-261001000014','WIP-20261001-00002','CHANGSHIN INC',2,1500.00,'in_stock','2026-10-01 23:13:55',NULL,NULL,3,'THI-M261003001','ok',NULL),
(6,6,'FG-261001000016','WIP-20261001-00003','PT. Test Januari Indonesia',1,1000.00,'in_stock','2026-10-01 23:32:27',NULL,NULL,4,'THI-M261008001','ok',NULL),
(7,7,'FG-261001000018','WIP-20261001-00004','PT. ADIS DIMENSION FOOTWEAR',1,1200.00,'in_stock','2026-10-01 23:38:33',NULL,NULL,5,'THI-M261001001','ok',NULL);
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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_kulit_lebih`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_kulit_lebih` WRITE;
/*!40000 ALTER TABLE `tbl_kulit_lebih` DISABLE KEYS */;
INSERT INTO `tbl_kulit_lebih` VALUES
(1,1,1,1,'KY-TEST 30 SEPT 2026 003','MCL-00A-123',1000.00,950.00,-50.00,'Kurang','2026-09-30 12:09:27'),
(2,5,3,4,'KY-TEST 30 SEPT 2026 005','MCL-00A-123',5000.00,4500.00,-500.00,'Kurang','2026-10-01 22:55:52'),
(3,2,6,8,'KY-TEST 10 OKT 003','MCL-00A-123',2000.00,1200.00,-800.00,'Kurang','2026-10-01 23:38:03');
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_lab_lot`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_lab_lot` WRITE;
/*!40000 ALTER TABLE `tbl_lab_lot` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_lab_lot_detail`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_lab_lot_detail` WRITE;
/*!40000 ALTER TABLE `tbl_lab_lot_detail` DISABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
(6,'LW-260923000005','TEST02 GAPCHEM',0.01,'verify-mixed','2026-09-23 23:01:27','mixed');
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
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_master_po`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_master_po` WRITE;
/*!40000 ALTER TABLE `tbl_master_po` DISABLE KEYS */;
INSERT INTO `tbl_master_po` VALUES
(1,'PO-THIPM26093001','THIPM26093001','PT. Test Januari Indonesia','VIRGIN HYDRO PU','ATOMIC VIOLET (55V)','1.2 - 1.4','AR-20 M',1000.00,1000.00,1000.00,'cancelled','2026-09-30 11:30:40',62,NULL,1,1000.00,'PUMTH26001260930001'),
(2,'PO-THIPM26093001','THIPM26093001','PT. Test Januari Indonesia','VIRGIN PU','DEEP ROYAL BLUE (47X)','1.2 - 1.4','AR-73 M',1200.00,1200.00,1200.00,'cancelled','2026-09-30 11:30:40',62,NULL,2,1200.00,'PUMTH26001260930002'),
(3,'PO-THIPM26093002','THIPM26093002','PT. ADIS DIMENSION FOOTWEAR','VIRGIN HYDRO PU','ATOMIC VIOLET (55V)','1.2 - 1.4','AR-20 M',1000.00,1000.00,1000.00,'completed','2026-09-30 11:33:09',1,NULL,3,1000.00,'PUMAD002260930001'),
(4,'PO-THIPM26093002','THIPM26093002','PT. ADIS DIMENSION FOOTWEAR','ECO GREEN RECYCLED LEATHER','MOREL (046-79-11)','1.2 - 1.4','AR-100 M',1200.00,1200.00,1200.00,'completed','2026-09-30 11:33:09',1,NULL,4,1200.00,'PUMAD002260930002'),
(5,'PO-THIPM26093003','THIPM26093003','FENG TAY ENTERPRISE CO., LTD','VIRGIN HYDRO PU','ATOMIC VIOLET (55V)','1.2 - 1.4','AR-20 M',1000.00,1000.00,1000.00,'cancelled','2026-09-30 11:39:27',58,NULL,5,1000.00,'PUMFT038260930003'),
(6,'PO-THIPM26093003','THIPM26093003','FENG TAY ENTERPRISE CO., LTD','BABY SOFT PATENT LEATHER','NIGHT INDIGO (117A)','1.2 - 1.4','CPUG (ESR-180-SK2)',1199.00,1199.00,1199.00,'cancelled','2026-09-30 11:39:27',58,NULL,6,1199.00,'PUMFT038260930002'),
(7,'mmm','THIPM26100104','PT. ADIS DIMENSION FOOTWEAR','(PM) GENERIC PU COATED LEATHER','ANTHRACITE (06F)','1.0 - 1.2','UM-16 SM',800.00,800.00,0.00,'cancelled','2026-10-01 22:29:26',1,NULL,9,800.00,'PUMAD002261001001'),
(8,'mmm','THIPM26100103','PT ABCD TEST','ECO GREEN LEATHER','CINNA RED (688)','1.2 - 1.4','AR-175 M',888.00,888.00,0.00,'cancelled','2026-10-01 22:32:51',70,NULL,10,888.00,'PUMABC123TEST261001001'),
(9,'PO-THIPM26100105','THIPM26100105','PT. Test Januari Indonesia','VIRGIN HYDRO PU','ENERGY (3CH)','1.2 - 1.4','R-131 M',1500.00,1500.00,0.00,'cancelled','2026-10-01 22:45:22',62,NULL,11,1500.00,'PUMTH26001261001003'),
(10,'PO-THIPM26100106','THIPM26100106','WEALTH VAST CO,LTD','VIRGIN HYDRO PU','ENERGY (3CH)','1.2 - 1.4','R-131 M',1500.00,1500.00,0.00,'cancelled','2026-10-01 22:45:57',61,'NIKOMAS IY',12,1500.00,'PUMSL044261001001'),
(11,'PO-THIPM26100107','THIPM26100107','POU CHEN CORPORATION','VIRGIN HYDRO PU','ENERGY (3CH)','1.2 - 1.4','R-131 M',1500.00,1500.00,0.00,'cancelled','2026-10-01 22:46:35',59,'NIKOMAS IY',13,1500.00,'PUMPG021261001001'),
(12,'PO-THIPM26100108','THIPM26100108','PT. Test Januari Indonesia','VIRGIN HYDRO PU','ENERGY (3CH)','1.2 - 1.4','R-131 M',1500.00,1500.00,1500.00,'completed','2026-10-01 22:51:09',62,NULL,14,1500.00,'PUMTH26001261001004'),
(13,'PO-THIPM26100109','THIPM26100109','TAE KWANG INDUSTRIAL CO LTD','VIRGIN HYDRO PU','ENERGY (3CH)','1.2 - 1.4','R-131 M',1500.00,1500.00,1500.00,'completed','2026-10-01 22:51:55',60,'NIKOMAS IY',15,1500.00,'PUMTK028261001001'),
(14,'PO-THIPM26100111','THIPM26100111','CHANGSHIN INC','VIRGIN HYDRO PU','ENERGY (3CH)','1.2 - 1.4','R-131 M',1500.00,1500.00,1500.00,'completed','2026-10-01 22:54:08',57,'NIKOMAS IY',17,1500.00,'PUMCS006261001001'),
(15,'PO-THIPM26100112','THIPM26100112','PT. Test Januari Indonesia','VIRGIN HYDRO PU','ATOMIC VIOLET (55V)','1.2 - 1.4','AR-20 M',1000.00,1000.00,1000.00,'completed','2026-10-01 23:29:31',62,NULL,18,1000.00,'PUMTH26001261001005');
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
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_master_treatment`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_master_treatment` WRITE;
/*!40000 ALTER TABLE `tbl_master_treatment` DISABLE KEYS */;
INSERT INTO `tbl_master_treatment` VALUES
(8,'PU','PU - Degrease','2026-08-09 16:20:22',1),
(9,'PU','PU - Base Coat','2026-08-09 16:20:22',1),
(10,'PU','PU - Color Coat','2026-08-09 16:20:22',1),
(11,'PU','PU - Top Coat','2026-08-09 16:20:22',1),
(12,'PU','PU - Emboss / Press','2026-08-09 16:20:22',1),
(13,'Suede','Suede - Buffing','2026-08-09 16:20:22',1),
(14,'Suede','Suede - Dyeing','2026-08-09 16:20:22',1),
(15,'Suede','Suede - Softener','2026-08-09 16:20:22',1),
(16,'Suede','Suede - Finishing Spray','2026-08-09 16:20:22',1),
(17,'PU','PU - Emboss','2026-09-19 21:46:14',1);
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
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_packing`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_packing` WRITE;
/*!40000 ALTER TABLE `tbl_packing` DISABLE KEYS */;
INSERT INTO `tbl_packing` VALUES
(1,'FG-260930000005','WIP-20260930-00001','PO-THIPM26093002','PT. ADIS DIMENSION FOOTWEAR',5,950.00,'finished','2026-09-30 12:10:58','2026-09-30 12:12:23',NULL,NULL,NULL,NULL,NULL,1,NULL),
(2,'FG-261001000005','WIP-20261001-00001','PO-THIPM26100108','PT. Test Januari Indonesia',4,1500.00,'finished','2026-10-01 22:56:29','2026-10-01 22:57:39',NULL,NULL,NULL,NULL,NULL,5,NULL),
(3,'FG-261001000007','WIP-20261001-00001','PO-THIPM26100109','TAE KWANG INDUSTRIAL CO LTD',1,1000.00,'finished','2026-10-01 22:58:42','2026-10-01 22:59:14',NULL,NULL,NULL,NULL,NULL,5,NULL),
(4,'FG-261001000011','WIP-20261001-00001','PO-THIPM26100111','CHANGSHIN INC',3,1500.00,'finished','2026-10-01 23:09:28','2026-10-01 23:09:59',NULL,NULL,NULL,NULL,NULL,5,NULL),
(5,'FG-261001000014','WIP-20261001-00002','PO-THIPM26100111','CHANGSHIN INC',2,1500.00,'finished','2026-10-01 23:13:28','2026-10-01 23:13:55',NULL,NULL,NULL,NULL,NULL,5,NULL),
(6,'FG-261001000016','WIP-20261001-00003','PO-THIPM26100112','PT. Test Januari Indonesia',1,1000.00,'finished','2026-10-01 23:31:09','2026-10-01 23:32:27',NULL,NULL,NULL,NULL,NULL,6,NULL),
(7,'FG-261001000018','WIP-20261001-00004','PO-THIPM26093002','PT. ADIS DIMENSION FOOTWEAR',1,1200.00,'finished','2026-10-01 23:38:22','2026-10-01 23:38:33',NULL,NULL,NULL,NULL,NULL,2,NULL);
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
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_packing_po`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_packing_po` WRITE;
/*!40000 ALTER TABLE `tbl_packing_po` DISABLE KEYS */;
INSERT INTO `tbl_packing_po` VALUES
(1,1,3,'PO-THIPM26093002','THIPM26093002',950.00),
(2,2,12,'PO-THIPM26100108','THIPM26100108',1500.00),
(3,3,13,'PO-THIPM26100109','THIPM26100109',1500.00),
(4,4,14,'PO-THIPM26100111','THIPM26100111',1500.00),
(5,5,14,'PO-THIPM26100111','THIPM26100111',1500.00),
(6,6,15,'PO-THIPM26100112','THIPM26100112',1000.00),
(7,7,4,'PO-THIPM26093002','THIPM26093002',1200.00);
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
  PRIMARY KEY (`id`),
  KEY `packing_id` (`packing_id`),
  CONSTRAINT `tbl_packing_roll_ibfk_1` FOREIGN KEY (`packing_id`) REFERENCES `tbl_packing` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_packing_roll`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_packing_roll` WRITE;
/*!40000 ALTER TABLE `tbl_packing_roll` DISABLE KEYS */;
INSERT INTO `tbl_packing_roll` VALUES
(1,1,1,2,300.00,'2026-09-30 12:11:15',NULL,'FG-260930000001','100+200'),
(2,1,2,1,100.00,'2026-09-30 12:11:32',NULL,'FG-260930000002','100'),
(3,1,3,1,400.00,'2026-09-30 12:11:46',NULL,'FG-260930000003','400'),
(4,1,4,1,150.00,'2026-09-30 12:11:58',NULL,'FG-260930000004','150'),
(5,2,1,1,500.00,'2026-10-01 22:56:37',NULL,'FG-261001000001','500'),
(6,2,2,1,200.00,'2026-10-01 22:56:48',NULL,'FG-261001000002','200'),
(7,2,3,1,600.00,'2026-10-01 22:57:00',NULL,'FG-261001000003','600'),
(8,2,4,1,200.00,'2026-10-01 22:57:33',NULL,'FG-261001000004','200'),
(9,3,1,1,1000.00,'2026-10-01 22:58:52',NULL,'FG-261001000006','1000'),
(10,4,1,1,500.00,'2026-10-01 23:09:34',NULL,'FG-261001000008','500'),
(11,4,2,1,500.00,'2026-10-01 23:09:43',NULL,'FG-261001000009','500'),
(12,4,3,1,500.00,'2026-10-01 23:09:54',NULL,'FG-261001000010','500'),
(13,5,1,1,1000.00,'2026-10-01 23:13:37',NULL,'FG-261001000012','1000'),
(14,5,2,1,500.00,'2026-10-01 23:13:50',NULL,'FG-261001000013','500'),
(15,6,1,1,1000.00,'2026-10-01 23:31:17',NULL,'FG-261001000015','1000'),
(16,7,1,1,1200.00,'2026-10-01 23:38:28',NULL,'FG-261001000017','1200');
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
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_palet_movement`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_palet_movement` WRITE;
/*!40000 ALTER TABLE `tbl_palet_movement` DISABLE KEYS */;
INSERT INTO `tbl_palet_movement` VALUES
(1,'KY-TEST 30 SEPT 2026 001','IN','2026-09-30','TEST KY','2026-09-30 11:46:56',NULL,NULL),
(2,'KY-TEST 30 SEPT 2026 002','IN','2026-09-30',NULL,'2026-09-30 11:51:06',NULL,NULL),
(3,'KY-TEST 30 SEPT 2026 003','IN','2026-09-30',NULL,'2026-09-30 11:51:17',NULL,NULL),
(4,'KY-TEST 30 SEPT 2026 004','IN','2026-09-30',NULL,'2026-09-30 11:51:38',NULL,NULL),
(5,'KY-TEST 30 SEPT 2026 005','IN','2026-09-30',NULL,'2026-09-30 11:51:47',NULL,NULL),
(6,'KY-TEST OKT 001','IN','2026-10-01',NULL,'2026-10-01 23:30:34',NULL,NULL),
(7,'KY-TEST 10 OKT 003','IN','2026-10-01',NULL,'2026-10-01 23:37:31',NULL,NULL);
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_persiapan_kulit`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_persiapan_kulit` WRITE;
/*!40000 ALTER TABLE `tbl_persiapan_kulit` DISABLE KEYS */;
INSERT INTO `tbl_persiapan_kulit` VALUES
(1,'WIP-20260930-00001','RPI-260930000001','PR-260930000004','PO-THIPM26093001, PO-THIPM26093002, PO-THIPM26093003','ATOMIC VIOLET (55V)','1.2 - 1.4','AR-20 M',NULL,'PU','PU - Emboss',2950.00,'completed','2026-09-30 12:09:19','2026-09-30 12:10:15',1,NULL),
(2,'WIP-20260930-00002','RPI-260930000002','PR-260930000005','PO-THIPM26093002','MOREL (046-79-11)','1.2 - 1.4','AR-100 M',NULL,'PU','PU - Emboss',1000.00,'completed','2026-09-30 12:22:40','2026-09-30 12:23:52',2,NULL),
(3,'WIP-20261001-00001','RPI-261001000001','PR-261001000001','PO-THIPM26100108, PO-THIPM26100109, PO-THIPM26100111','ENERGY (3CH)','1.2 - 1.4','R-131 M',NULL,'PU','PU - Emboss',4500.00,'completed','2026-10-01 22:55:46','2026-10-01 22:55:59',5,NULL),
(4,'WIP-20261001-00002','RPI-261001000001','PR-261001000002','PO-THIPM26100111','ENERGY (3CH)','1.2 - 1.4','R-131 M',NULL,'PU','PU - Emboss',1500.00,'completed','2026-10-01 23:12:30','2026-10-01 23:12:45',5,NULL),
(5,'WIP-20261001-00003','RPI-261001000002','PR-261001000003','PO-THIPM26100112','ATOMIC VIOLET (55V)','1.2 - 1.4','AR-20 M',NULL,'PU','PU - Emboss',1000.00,'started','2026-10-01 23:30:52',NULL,6,NULL),
(6,'WIP-20261001-00004','RPI-260930000002','PR-261001000004','PO-THIPM26093002','MOREL (046-79-11)','1.2 - 1.4','AR-100 M',NULL,'PU','PU - Emboss',1200.00,'completed','2026-10-01 23:37:58','2026-10-01 23:38:08',2,NULL);
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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_persiapan_ky`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_persiapan_ky` WRITE;
/*!40000 ALTER TABLE `tbl_persiapan_ky` DISABLE KEYS */;
INSERT INTO `tbl_persiapan_ky` VALUES
(1,1,'KY-TEST 30 SEPT 2026 003','MCL-00A-123',1000.00,950.00,'selesai','2026-09-30 12:09:19',1,950.00,0,NULL),
(2,1,'KY-TEST 30 SEPT 2026 004','MCL-00A-123',2000.00,2000.00,'selesai','2026-09-30 12:09:19',1,2000.00,0,NULL),
(3,2,'KY-TEST 30 SEPT 2026 001','MCL-00A-123',1000.00,1000.00,'selesai','2026-09-30 12:22:40',1,1000.00,0,NULL),
(4,3,'KY-TEST 30 SEPT 2026 005','MCL-00A-123',5000.00,4500.00,'selesai','2026-10-01 22:55:46',1,4500.00,0,NULL),
(5,4,'KY-TEST 30 SEPT 2026 005','MCL-00A-123',500.00,500.00,'selesai','2026-10-01 23:12:30',1,500.00,0,NULL),
(6,4,'KY-TEST 30 SEPT 2026 002','MCL-00A-123',1000.00,1000.00,'selesai','2026-10-01 23:12:30',1,1000.00,0,NULL),
(7,5,'KY-TEST OKT 001','MCL-00A-123',1000.00,1000.00,'selesai','2026-10-01 23:30:52',1,1000.00,0,NULL),
(8,6,'KY-TEST 10 OKT 003','MCL-00A-123',2000.00,1200.00,'selesai','2026-10-01 23:37:58',1,1200.00,0,NULL);
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
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_persiapan_ukur`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_persiapan_ukur` WRITE;
/*!40000 ALTER TABLE `tbl_persiapan_ukur` DISABLE KEYS */;
INSERT INTO `tbl_persiapan_ukur` VALUES
(1,1,300.00,'2026-09-30 12:09:23',1),
(2,1,500.00,'2026-09-30 12:09:24',1),
(3,1,150.00,'2026-09-30 12:09:26',1),
(4,1,1000.00,'2026-09-30 12:09:29',2),
(5,1,500.00,'2026-09-30 12:09:31',2),
(6,1,200.00,'2026-09-30 12:09:32',2),
(7,1,300.00,'2026-09-30 12:09:33',2),
(8,2,200.00,'2026-09-30 12:22:45',3),
(9,2,500.00,'2026-09-30 12:22:46',3),
(10,2,300.00,'2026-09-30 12:22:49',3),
(11,3,4500.00,'2026-10-01 22:55:51',4),
(12,4,500.00,'2026-10-01 23:12:34',5),
(13,4,1000.00,'2026-10-01 23:12:38',6),
(14,5,1000.00,'2026-10-01 23:30:55',7),
(15,6,1200.00,'2026-10-01 23:38:02',8);
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_rencana_item` (`kode_rencana_item`),
  KEY `idx_rencana_item` (`rencana_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_rencana_item`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_rencana_item` WRITE;
/*!40000 ALTER TABLE `tbl_rencana_item` DISABLE KEYS */;
INSERT INTO `tbl_rencana_item` VALUES
(1,1,'RPI-260930000001','WIP-260930000001',62,'PT. Test Januari Indonesia, PT. ADIS DIMENSION FOOTWEAR, FENG TAY ENTERPRISE CO., LTD',NULL,'1.2 - 1.4','ATOMIC VIOLET (55V)','AR-20 M',NULL,NULL,1,'2026-09-30 11:44:56',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL),
(2,1,'RPI-260930000002','WIP-260930000002',1,'PT. ADIS DIMENSION FOOTWEAR',NULL,'1.2 - 1.4','MOREL (046-79-11)','AR-100 M',NULL,NULL,2,'2026-09-30 11:45:00',NULL,NULL,'ECO GREEN RECYCLED LEATHER',NULL,NULL),
(3,1,'RPI-260930000003','WIP-260930000003',62,'PT. Test Januari Indonesia',NULL,'1.2 - 1.4','DEEP ROYAL BLUE (47X)','AR-73 M',NULL,NULL,3,'2026-09-30 11:45:04',NULL,NULL,'VIRGIN PU',NULL,NULL),
(4,1,'RPI-260930000004','WIP-260930000004',69,'FENG TAY ENTERPRISE CO., LTD',NULL,'1.2 - 1.4','NIGHT INDIGO (117A)','CPUG (ESR-180-SK2)',NULL,NULL,4,'2026-09-30 11:45:08',NULL,NULL,'BABY SOFT PATENT LEATHER',NULL,NULL),
(5,2,'RPI-261001000001','WIP-261001000001',62,'PT. Test Januari Indonesia, TAE KWANG INDUSTRIAL CO LTD, CHANGSHIN INC',NULL,'1.2 - 1.4','ENERGY (3CH)','R-131 M',NULL,NULL,1,'2026-10-01 22:55:02',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL),
(6,3,'RPI-261001000002','WIP-261001000002',62,'PT. Test Januari Indonesia',NULL,'1.2 - 1.4','ATOMIC VIOLET (55V)','AR-20 M',NULL,NULL,1,'2026-10-01 23:30:03',NULL,NULL,'VIRGIN HYDRO PU',NULL,NULL);
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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_rencana_item_po`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_rencana_item_po` WRITE;
/*!40000 ALTER TABLE `tbl_rencana_item_po` DISABLE KEYS */;
INSERT INTO `tbl_rencana_item_po` VALUES
(1,1,1,1000.00,1000.00),
(2,1,3,950.00,950.00),
(3,1,5,1000.00,1000.00),
(4,2,4,1200.00,1200.00),
(5,3,2,1200.00,1200.00),
(6,4,6,1199.00,1199.00),
(7,5,12,1500.00,1500.00),
(8,5,13,1500.00,1500.00),
(9,5,14,1500.00,1500.00),
(10,6,15,1000.00,1000.00);
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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_rencana_produksi`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_rencana_produksi` WRITE;
/*!40000 ALTER TABLE `tbl_rencana_produksi` DISABLE KEYS */;
INSERT INTO `tbl_rencana_produksi` VALUES
(1,'RP-260930000001',NULL,'TEST 30 SEPT 2026 001','active','2026-09-30 11:44:52','2026-09-30'),
(2,'RP-261001000001',NULL,'TEST 1 OKT 26 001','active','2026-10-01 22:54:58','2026-10-01'),
(3,'RP-261001000002',NULL,'TEST 10 OKT 002','active','2026-10-01 23:29:59','2026-10-01');
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
('FG',18,'FG','261001'),
('PR',4,'PR','261001'),
('RP',2,'RP','261001'),
('RPI',2,'RPI','261001'),
('WIP',2,'WIP','261001'),
('WIP-PERSIAPAN',4,'WIP','20261001');
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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stock_sisa`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_stock_sisa` WRITE;
/*!40000 ALTER TABLE `tbl_stock_sisa` DISABLE KEYS */;
INSERT INTO `tbl_stock_sisa` VALUES
(1,'kulit','MCL-00A-123','KY-TEST 30 SEPT 2026 003',50.00,'open',NULL,'Sisa KY #1 dikembalikan ke palet','2026-09-30 12:09:27',NULL,NULL,NULL,NULL,NULL,NULL),
(2,'kulit','MCL-00A-123','KY-TEST 30 SEPT 2026 005',500.00,'open',NULL,'Sisa KY #4 dikembalikan ke palet','2026-10-01 22:55:52',NULL,NULL,NULL,NULL,NULL,NULL),
(3,'kulit','MCL-00A-123','KY-TEST 10 OKT 003',800.00,'open',NULL,'Sisa KY #8 dikembalikan ke palet','2026-10-01 23:38:03',NULL,NULL,NULL,NULL,NULL,NULL);
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_kimia_in`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_stok_kimia_in` WRITE;
/*!40000 ALTER TABLE `tbl_stok_kimia_in` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_kimia_out`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_stok_kimia_out` WRITE;
/*!40000 ALTER TABLE `tbl_stok_kimia_out` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_rp_in`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_stok_rp_in` WRITE;
/*!40000 ALTER TABLE `tbl_stok_rp_in` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_rp_out`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_stok_rp_out` WRITE;
/*!40000 ALTER TABLE `tbl_stok_rp_out` DISABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_yl`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_yl` WRITE;
/*!40000 ALTER TABLE `tbl_yl` DISABLE KEYS */;
INSERT INTO `tbl_yl` VALUES
(10,'MCL-00A-123','KY-TEST 30 SEPT 2026 003','1.23','BLACK',50.00,'2026-09-30 12:09:27'),
(11,'MCL-00A-123-R','KY-TEST 30 SEPT 2026 001','1.23','BLACK',300.00,'2026-09-30 12:23:31'),
(15,'MCL-00A-123','KY-TEST 10 OKT 003','1.23','BLACK',800.00,'2026-10-01 23:38:03');
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
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_yl_movement`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tbl_yl_movement` WRITE;
/*!40000 ALTER TABLE `tbl_yl_movement` DISABLE KEYS */;
INSERT INTO `tbl_yl_movement` VALUES
(1,'MCL-00A-123','KY-TEST 30 SEPT 2026 003','OUT','1.23','BLACK',1000.00,'2026-09-30','Keluar proses persiapan — WIP WIP-20260930-00001','2026-09-30 12:09:27'),
(2,'MCL-00A-123','KY-TEST 30 SEPT 2026 003','IN','1.23','BLACK',50.00,'2026-09-30','Sisa KY dikembalikan ke palet — WIP WIP-20260930-00001','2026-09-30 12:09:27'),
(3,'MCL-00A-123','KY-TEST 30 SEPT 2026 004','OUT','1.23','BLACK',2000.00,'2026-09-30','Keluar proses persiapan — WIP WIP-20260930-00001','2026-09-30 12:09:34'),
(4,'MCL-00A-123','KY-TEST 30 SEPT 2026 001','OUT','1.23','BLACK',1000.00,'2026-09-30','Keluar proses persiapan — WIP WIP-20260930-00002','2026-09-30 12:22:50'),
(5,'MCL-00A-123-R','KY-TEST 30 SEPT 2026 001','IN','1.23','BLACK',300.00,'2026-09-30','Retur proses dari MCL-00A-123 — retur WIP WIP-20260930-00002','2026-09-30 12:23:31'),
(6,'MCL-00A-123','KY-TEST 30 SEPT 2026 005','OUT','1.23','BLACK',5000.00,'2026-10-01','Keluar proses persiapan — WIP WIP-20261001-00001','2026-10-01 22:55:52'),
(7,'MCL-00A-123','KY-TEST 30 SEPT 2026 005','IN','1.23','BLACK',500.00,'2026-10-01','Sisa KY dikembalikan ke palet — WIP WIP-20261001-00001','2026-10-01 22:55:52'),
(8,'MCL-00A-123','KY-TEST 30 SEPT 2026 005','OUT','1.23','BLACK',500.00,'2026-10-01','Keluar proses persiapan — WIP WIP-20261001-00002','2026-10-01 23:12:36'),
(9,'MCL-00A-123','KY-TEST 30 SEPT 2026 002','OUT','1.23','BLACK',1000.00,'2026-10-01','Keluar proses persiapan — WIP WIP-20261001-00002','2026-10-01 23:12:39'),
(10,'MCL-00A-123','KY-TEST OKT 001','OUT','1.23','BLACK',1000.00,'2026-10-01','Keluar proses persiapan — WIP WIP-20261001-00003','2026-10-01 23:30:56'),
(11,'MCL-00A-123','KY-TEST 10 OKT 003','OUT','1.23','BLACK',2000.00,'2026-10-01','Keluar proses persiapan — WIP WIP-20261001-00004','2026-10-01 23:38:03'),
(12,'MCL-00A-123','KY-TEST 10 OKT 003','IN','1.23','BLACK',800.00,'2026-10-01','Sisa KY dikembalikan ke palet — WIP WIP-20261001-00004','2026-10-01 23:38:03');
/*!40000 ALTER TABLE `tbl_yl_movement` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

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

-- Dump completed on 2026-10-01 23:47:30
