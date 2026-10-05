/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.7.2-MariaDB, for Win64 (AMD64)
--
-- Host: 202.10.48.75    Database: mrp
-- ------------------------------------------------------
-- Server version	10.3.39-MariaDB

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
-- Table structure for table `master_chemical`
--

DROP TABLE IF EXISTS `master_chemical`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `master_chemical` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nama_chemical` varchar(150) NOT NULL,
  `satuan` varchar(20) DEFAULT 'kg',
  `expired_days` int(11) DEFAULT 365,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `master_chemical`
--

LOCK TABLES `master_chemical` WRITE;
/*!40000 ALTER TABLE `master_chemical` DISABLE KEYS */;
INSERT INTO `master_chemical` VALUES
(1,'Pigment Red','kg',365),
(2,'Pigment Blue','kg',365),
(3,'Pigment Black','kg',365),
(4,'Solvent Base','kg',365);
/*!40000 ALTER TABLE `master_chemical` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `master_customer`
--

DROP TABLE IF EXISTS `master_customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `master_customer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_customer` varchar(50) DEFAULT NULL,
  `nama_customer` varchar(150) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_nama_customer` (`nama_customer`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `master_customer`
--

LOCK TABLES `master_customer` WRITE;
/*!40000 ALTER TABLE `master_customer` DISABLE KEYS */;
INSERT INTO `master_customer` VALUES
(1,'CUST-CUSTOMER-A','Customer A','2026-07-02 09:41:02'),
(2,'CUST-CUSTOMER-B','Customer B','2026-07-02 09:41:02');
/*!40000 ALTER TABLE `master_customer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `master_erp`
--

DROP TABLE IF EXISTS `master_erp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `master_erp` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `thickness` varchar(30) NOT NULL,
  `color` varchar(100) NOT NULL,
  `emboss` varchar(100) NOT NULL,
  `color_swatch` varchar(100) DEFAULT NULL,
  `backer` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `material_name` varchar(150) DEFAULT NULL,
  `customer` varchar(150) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=252 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `master_erp`
--

LOCK TABLES `master_erp` WRITE;
/*!40000 ALTER TABLE `master_erp` DISABLE KEYS */;
INSERT INTO `master_erp` VALUES
(1,'1.0mm','Brown','Plain','SW-BRN-01','BK-PU-A','2026-07-16 09:55:16','Standard Leather',NULL),
(2,'1.0mm','Black','Emboss A','SW-BLK-02','BK-PU-B','2026-07-16 09:55:16','Standard Leather','Customer A'),
(3,'1.2mm','Brown','Plain','SW-BRN-03','BK-PU-A','2026-07-16 09:55:16','Standard Leather','Customer A'),
(4,'1.2mm','Tan','Emboss X','SW-TAN-04','BK-SUEDE-C','2026-07-16 09:55:16','Standard Leather',NULL),
(5,'1.4mm','Red','Emboss B','SW-RED-05','BK-PU-D','2026-07-16 09:55:16','Standard Leather','Customer B'),
(6,'1.4mm','Maroon','Emboss B','SW-MAR-06','BK-PU-D','2026-07-16 09:55:16','Standard Leather','Customer B'),
(247,'1.0mm','Brown','Plain','SW-BRN-01B','WHITE','2026-07-24 14:56:23','Standard Leather','Customer A'),
(248,'1.2mm','Brown','Plain','SW-BRN-03','BK-PU-A','2026-07-24 14:56:23','Premium Leather','Customer A'),
(249,'1.2mm','Tan','Emboss X','SW-TAN-04','BK-SUEDE-C','2026-07-24 14:56:23','Premium Leather','Customer B'),
(250,'1.4mm','Red','Emboss B','SW-RED-05','BK-PU-D','2026-07-24 14:56:23','Premium Leather','Customer B'),
(251,'1.4mm','Maroon','Emboss B','SW-MAR-06','BK-PU-D','2026-07-24 14:56:23','Premium Leather','Customer B');
/*!40000 ALTER TABLE `master_erp` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `master_kimia`
--

DROP TABLE IF EXISTS `master_kimia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `master_kimia` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_barang` varchar(50) NOT NULL,
  `nama_barang` varchar(150) NOT NULL,
  `satuan` varchar(20) DEFAULT 'kg',
  `expired_days` int(11) DEFAULT 365,
  `kode_kimia` varchar(50) DEFAULT NULL,
  `nama_kimia` varchar(150) DEFAULT NULL,
  `deskripsi` text DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_barang` (`kode_barang`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `master_kimia`
--

LOCK TABLES `master_kimia` WRITE;
/*!40000 ALTER TABLE `master_kimia` DISABLE KEYS */;
INSERT INTO `master_kimia` VALUES
(1,'KIM-001','Chemical Base A','kg',365,'KIM-001','Chemical Base A',NULL,'2026-07-02 08:52:05'),
(2,'KIM-002','Chemical Base B','kg',365,'KIM-002','Chemical Base B',NULL,'2026-07-02 08:52:05'),
(3,'KIM-003','Hardener','kg',365,'KIM-003','Hardener',NULL,'2026-07-02 08:52:05');
/*!40000 ALTER TABLE `master_kimia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `master_kulit`
--

DROP TABLE IF EXISTS `master_kulit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `master_kulit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_kulit` varchar(50) NOT NULL,
  `nama_kulit` varchar(150) DEFAULT NULL,
  `thickness` varchar(30) DEFAULT NULL,
  `warna` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_kulit` (`kode_kulit`),
  KEY `idx_kode_kulit` (`kode_kulit`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `master_kulit`
--

LOCK TABLES `master_kulit` WRITE;
/*!40000 ALTER TABLE `master_kulit` DISABLE KEYS */;
INSERT INTO `master_kulit` VALUES
(1,'KLT-001',NULL,'1.2mm','Brown','2026-07-02 08:36:21'),
(2,'KLT-002','RED 03','1.2','Brown','2026-07-02 09:00:11'),
(3,'KLT-004','Dark Brown','2','Brown','2026-07-03 10:13:21'),
(4,'KLT-005','Dark Blue 1.2mm','1.2','Dark Blue','2026-07-03 10:13:56');
/*!40000 ALTER TABLE `master_kulit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `master_material_lain`
--

DROP TABLE IF EXISTS `master_material_lain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `master_material_lain` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kode_material` varchar(50) NOT NULL,
  `nama_material` varchar(150) NOT NULL,
  `deskripsi` text DEFAULT NULL,
  `satuan` varchar(20) DEFAULT 'pcs',
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_material` (`kode_material`)
) ENGINE=InnoDB AUTO_INCREMENT=214 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `master_material_lain`
--

LOCK TABLES `master_material_lain` WRITE;
/*!40000 ALTER TABLE `master_material_lain` DISABLE KEYS */;
INSERT INTO `master_material_lain` VALUES
(1,'MAT-001','Thread Nylon','Benang jahit nylon','roll','2026-07-16 09:55:17'),
(2,'MAT-002','Label Tag','Label produk','pcs','2026-07-16 09:55:17'),
(3,'MAT-003','Plastic Wrap','Plastik pembungkus','roll','2026-07-16 09:55:17');
/*!40000 ALTER TABLE `master_material_lain` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `master_resep`
--

DROP TABLE IF EXISTS `master_resep`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `master_resep` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nama_resep` varchar(150) NOT NULL,
  `chemical_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `chemical_id` (`chemical_id`),
  CONSTRAINT `master_resep_ibfk_1` FOREIGN KEY (`chemical_id`) REFERENCES `master_chemical` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `master_resep`
--

LOCK TABLES `master_resep` WRITE;
/*!40000 ALTER TABLE `master_resep` DISABLE KEYS */;
INSERT INTO `master_resep` VALUES
(1,'Resep Standard A',NULL),
(2,'Resep Standard B',NULL),
(3,'Resep Custom',NULL);
/*!40000 ALTER TABLE `master_resep` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `master_rp`
--

DROP TABLE IF EXISTS `master_rp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `master_rp` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nama_jenis` varchar(150) NOT NULL,
  `satuan` varchar(20) DEFAULT 'meter',
  `kode_rp` varchar(50) DEFAULT NULL,
  `nama_rp` varchar(150) DEFAULT NULL,
  `deskripsi` text DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `master_rp`
--

LOCK TABLES `master_rp` WRITE;
/*!40000 ALTER TABLE `master_rp` DISABLE KEYS */;
INSERT INTO `master_rp` VALUES
(1,'RP Gloss','meter','RP-001','RP Gloss',NULL,'2026-07-02 08:47:18'),
(2,'RP Matte','meter','RP-002','RP Matte',NULL,'2026-07-02 08:47:18'),
(3,'RP Texture','meter','RP-003','RP Texture',NULL,'2026-07-02 08:47:18');
/*!40000 ALTER TABLE `master_rp` ENABLE KEYS */;
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `packing_id` (`packing_id`),
  UNIQUE KEY `kode_packing` (`kode_packing`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_gudang_fg`
--

LOCK TABLES `tbl_gudang_fg` WRITE;
/*!40000 ALTER TABLE `tbl_gudang_fg` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_kulit_lebih`
--

LOCK TABLES `tbl_kulit_lebih` WRITE;
/*!40000 ALTER TABLE `tbl_kulit_lebih` DISABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_lab_lot`
--

LOCK TABLES `tbl_lab_lot` WRITE;
/*!40000 ALTER TABLE `tbl_lab_lot` DISABLE KEYS */;
INSERT INTO `tbl_lab_lot` VALUES
(1,'LW-260702000002','Red Premium Mix','active','2026-07-02 09:31:43',NULL),
(2,'LW-260702000003','RED PREMIUM MIX','active','2026-07-02 09:37:16',NULL);
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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
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
(5,'LW-260702000003','KIM-002','Chemical Base B','0.4','kg',1.00,NULL);
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
  PRIMARY KEY (`id`),
  KEY `idx_no_po` (`no_po`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_master_po`
--

LOCK TABLES `tbl_master_po` WRITE;
/*!40000 ALTER TABLE `tbl_master_po` DISABLE KEYS */;
INSERT INTO `tbl_master_po` VALUES
(1,'PO-2026-001','SO-2026-001','Customer A','Leather Sheet A','Brown','1.2mm','Plain',500.00,100.00,100.00,'completed','2026-06-16 20:43:55',1,'SW-BRN-03'),
(2,'PO-2026-002','SO-2026-001','Customer A','Leather Sheet B','Black','1.0mm','Emboss A',300.00,80.00,78.00,'partial','2026-06-16 20:43:55',1,'SW-BLK-02'),
(3,'PO-2026-003','SO-2026-002','Customer B','Leather Sheet C','Red','1.4mm','Emboss B',450.00,120.00,110.00,'partial','2026-06-16 20:43:55',2,'SW-RED-05'),
(4,'PO-2026-001','SO-2026-001','Customer A','Leather Sheet A-2','Brown','1.2mm','Plain',200.00,50.00,50.00,'completed','2026-06-21 00:42:32',1,'SW-BRN-03'),
(5,'PO-2026-001','SO-2026-001','Customer A','Leather Sheet A-3','Tan','1.0mm','Emboss X',150.00,30.00,30.00,'completed','2026-06-21 00:42:32',1,NULL),
(6,'PO-2026-002','SO-2026-001','Customer A','Leather Sheet B-2','Black','1.0mm','Emboss A',180.00,40.00,40.00,'completed','2026-06-21 00:42:32',1,'SW-BLK-02'),
(7,'PO-2026-003','SO-2026-002','Customer B','Leather Sheet C-2','Maroon','1.4mm','Emboss B',220.00,60.00,60.00,'completed','2026-06-21 00:42:32',2,'SW-MAR-06');
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_master_treatment`
--

LOCK TABLES `tbl_master_treatment` WRITE;
/*!40000 ALTER TABLE `tbl_master_treatment` DISABLE KEYS */;
INSERT INTO `tbl_master_treatment` VALUES
(1,'PU','Emboss','2026-07-03 09:31:30'),
(2,'PU','Treatment B','2026-07-03 09:31:30'),
(3,'PU','Treatment C','2026-07-03 09:31:30'),
(4,'PU','Treatment D','2026-07-03 09:31:30'),
(5,'Suede','Treatment Sueda A','2026-07-03 10:20:56'),
(6,'PU','Treatment A','2026-07-03 11:18:07');
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_packing` (`kode_packing`),
  KEY `idx_kode_wip` (`kode_wip`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_packing`
--

LOCK TABLES `tbl_packing` WRITE;
/*!40000 ALTER TABLE `tbl_packing` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_packing_po`
--

LOCK TABLES `tbl_packing_po` WRITE;
/*!40000 ALTER TABLE `tbl_packing_po` DISABLE KEYS */;
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
  PRIMARY KEY (`id`),
  KEY `packing_id` (`packing_id`),
  CONSTRAINT `tbl_packing_roll_ibfk_1` FOREIGN KEY (`packing_id`) REFERENCES `tbl_packing` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_packing_roll`
--

LOCK TABLES `tbl_packing_roll` WRITE;
/*!40000 ALTER TABLE `tbl_packing_roll` DISABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
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
(14,'KY-0044','IN','2026-07-03','Keterangan','2026-07-03 10:30:44');
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_proses` (`kode_proses`),
  KEY `idx_kode_wip` (`kode_wip`),
  KEY `idx_kode_rencana` (`kode_rencana`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_persiapan_kulit`
--

LOCK TABLES `tbl_persiapan_kulit` WRITE;
/*!40000 ALTER TABLE `tbl_persiapan_kulit` DISABLE KEYS */;
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
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_persiapan_ky`
--

LOCK TABLES `tbl_persiapan_ky` WRITE;
/*!40000 ALTER TABLE `tbl_persiapan_ky` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_persiapan_reprint`
--

LOCK TABLES `tbl_persiapan_reprint` WRITE;
/*!40000 ALTER TABLE `tbl_persiapan_reprint` DISABLE KEYS */;
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
  PRIMARY KEY (`id`),
  KEY `persiapan_id` (`persiapan_id`),
  CONSTRAINT `tbl_persiapan_scan_ibfk_1` FOREIGN KEY (`persiapan_id`) REFERENCES `tbl_persiapan_kulit` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_persiapan_scan`
--

LOCK TABLES `tbl_persiapan_scan` WRITE;
/*!40000 ALTER TABLE `tbl_persiapan_scan` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_persiapan_ukur`
--

LOCK TABLES `tbl_persiapan_ukur` WRITE;
/*!40000 ALTER TABLE `tbl_persiapan_ukur` DISABLE KEYS */;
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_rencana_item` (`kode_rencana_item`),
  KEY `idx_rencana_item` (`rencana_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_rencana_item`
--

LOCK TABLES `tbl_rencana_item` WRITE;
/*!40000 ALTER TABLE `tbl_rencana_item` DISABLE KEYS */;
INSERT INTO `tbl_rencana_item` VALUES
(1,1,'RPI-260702000001','WIP-260702000001',1,'KLT-001','1.2mm','Brown','Plain','SW01','Item 1',1,'2026-07-02 09:44:12',NULL,NULL,NULL),
(2,1,'RPI-260702000002','WIP-260702000002',2,'KLT-002','1.2','Brown','Emboss X','SW02','Item 2',2,'2026-07-02 09:44:13',NULL,NULL,NULL),
(3,2,'RPI-260702000003','WIP-260702000003',1,'KLT-001','1.2mm','Brown','RP','BROWN DARK','Ketarangan 1',1,'2026-07-02 09:47:56',NULL,NULL,NULL),
(4,2,'RPI-260702000004','WIP-260702000004',2,'KLT-002','1.2','Brown','RP 1','DARK GREY','Keterangan 2',2,'2026-07-02 09:47:56',NULL,NULL,NULL),
(5,2,'RPI-260702000005','WIP-260702000005',1,'KLT-002','1.2','Brown','RP 2','DARK BLUE','Keterngan 3',3,'2026-07-02 09:47:57',NULL,NULL,NULL),
(6,3,'RPI-260703000001','WIP-260703000001',1,'KLT-005','1.2','Dark Blue',NULL,NULL,NULL,1,'2026-07-03 10:43:30',NULL,NULL,NULL),
(7,3,'RPI-260703000002','WIP-260703000002',2,'KLT-002','1.2','Brown',NULL,NULL,NULL,2,'2026-07-03 10:43:31',NULL,NULL,NULL),
(8,4,'RPI-260703000003','WIP-260703000003',1,'KLT-001','1.2mm','Brown','RP','BROWN DARK','Ketarangan 1',1,'2026-07-03 10:49:37',NULL,NULL,NULL),
(9,4,'RPI-260703000004','WIP-260703000004',2,'KLT-002','1.2','Brown','RP','BROWN DARK','Ketarangan 1',2,'2026-07-03 10:49:38',NULL,NULL,NULL),
(10,5,'RPI-260716000001','WIP-260716000001',1,NULL,'1.0mm','Black','Emboss A','SW-BLK-02',NULL,1,'2026-07-16 10:35:03','BK-PU-B','RPI-10MM-EMBOSS-BLACK-01',NULL);
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
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
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
(8,10,2,20.00,18.00),
(9,10,6,5.00,5.00);
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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
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
(5,'RP-260716000001',NULL,'Rencana Produksi 16 July','active','2026-07-16 10:35:03','2026-07-16');
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
('BC-K',1,'BC-K','260703'),
('BC-R',1,'BC-R','260724'),
('LW',3,'LW','260702'),
('RP',1,'RP','260716'),
('RPI',1,'RPI','260716'),
('WIP',1,'WIP','260716');
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
  `kimia_id` int(11) NOT NULL,
  `qty` decimal(12,2) NOT NULL,
  `qty_sisa` decimal(12,2) NOT NULL,
  `satuan` varchar(20) DEFAULT 'kg',
  `expired_date` date DEFAULT NULL,
  `tanggal_in` date NOT NULL,
  `gudang` enum('kimia','mixing') DEFAULT 'kimia',
  `created_at` datetime DEFAULT current_timestamp(),
  `jumlah_kemasan` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_internal` (`kode_internal`),
  KEY `kimia_id` (`kimia_id`),
  KEY `idx_gudang` (`gudang`),
  CONSTRAINT `tbl_stok_kimia_in_ibfk_1` FOREIGN KEY (`kimia_id`) REFERENCES `master_kimia` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_kimia_in`
--

LOCK TABLES `tbl_stok_kimia_in` WRITE;
/*!40000 ALTER TABLE `tbl_stok_kimia_in` DISABLE KEYS */;
INSERT INTO `tbl_stok_kimia_in` VALUES
(1,'BC-K-260623000001',2,100.00,70.00,'kg','2027-06-23','2026-06-23','kimia','2026-06-21 01:48:38',NULL),
(2,'BC-K-260623000002',3,100.00,89.00,'kg','2027-06-23','2026-06-23','mixing','2026-06-21 01:48:49',NULL),
(3,'BC-K-260703000001',2,100.00,100.00,'kg','2027-07-03','2026-07-03','kimia','2026-07-03 10:33:08',NULL);
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
  `kimia_id` int(11) NOT NULL,
  `qty` decimal(12,2) NOT NULL,
  `tujuan` enum('mixing','produksi','return') NOT NULL,
  `kode_wip` varchar(30) DEFAULT NULL,
  `tanggal` date NOT NULL,
  `keterangan` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `jumlah_kemasan` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `stok_in_id` (`stok_in_id`),
  KEY `kimia_id` (`kimia_id`),
  CONSTRAINT `tbl_stok_kimia_out_ibfk_1` FOREIGN KEY (`stok_in_id`) REFERENCES `tbl_stok_kimia_in` (`id`) ON DELETE SET NULL,
  CONSTRAINT `tbl_stok_kimia_out_ibfk_2` FOREIGN KEY (`kimia_id`) REFERENCES `master_kimia` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_kimia_out`
--

LOCK TABLES `tbl_stok_kimia_out` WRITE;
/*!40000 ALTER TABLE `tbl_stok_kimia_out` DISABLE KEYS */;
INSERT INTO `tbl_stok_kimia_out` VALUES
(1,2,3,10.00,'produksi',NULL,'2026-06-23',NULL,'2026-06-21 01:57:34',NULL),
(2,1,2,30.00,'produksi',NULL,'2026-06-23',NULL,'2026-06-21 01:57:55',NULL),
(3,2,3,1.00,'mixing',NULL,'2026-07-03',NULL,'2026-07-03 10:35:16',NULL);
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
  `material_id` int(11) NOT NULL,
  `qty` decimal(12,2) NOT NULL,
  `qty_sisa` decimal(12,2) NOT NULL,
  `satuan` varchar(20) DEFAULT 'pcs',
  `tanggal_in` date NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_internal` (`kode_internal`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_material_lain_in`
--

LOCK TABLES `tbl_stok_material_lain_in` WRITE;
/*!40000 ALTER TABLE `tbl_stok_material_lain_in` DISABLE KEYS */;
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
  `material_id` int(11) NOT NULL,
  `qty` decimal(12,2) NOT NULL,
  `kode_wip` varchar(30) DEFAULT NULL,
  `tanggal` date NOT NULL,
  `keterangan` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_material_lain_out`
--

LOCK TABLES `tbl_stok_material_lain_out` WRITE;
/*!40000 ALTER TABLE `tbl_stok_material_lain_out` DISABLE KEYS */;
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
  `rp_id` int(11) NOT NULL,
  `meter_roll` decimal(12,2) NOT NULL,
  `qty_sisa` decimal(12,2) NOT NULL,
  `tanggal_in` date NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `kode_internal` (`kode_internal`),
  KEY `rp_id` (`rp_id`),
  CONSTRAINT `tbl_stok_rp_in_ibfk_1` FOREIGN KEY (`rp_id`) REFERENCES `master_rp` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_rp_in`
--

LOCK TABLES `tbl_stok_rp_in` WRITE;
/*!40000 ALTER TABLE `tbl_stok_rp_in` DISABLE KEYS */;
INSERT INTO `tbl_stok_rp_in` VALUES
(1,'BC-R-260623000001',1,100.00,100.00,'2026-06-23','2026-06-21 01:59:57'),
(2,'BC-R-260623000002',2,100.00,40.00,'2026-06-23','2026-06-21 02:00:07'),
(3,'BC-R-260702000001',1,100.00,99.00,'2026-07-02','2026-07-02 09:28:20'),
(4,'BC-R-260703000001',3,100.00,98.00,'2026-07-03','2026-07-03 10:35:50'),
(5,'BC-R-260724000001',2,10.00,10.00,'2026-07-24','2026-07-24 15:29:02');
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
  `rp_id` int(11) NOT NULL,
  `meter_roll` decimal(12,2) NOT NULL,
  `kode_wip` varchar(30) DEFAULT NULL,
  `tanggal` date NOT NULL,
  `keterangan` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `stok_in_id` (`stok_in_id`),
  KEY `rp_id` (`rp_id`),
  CONSTRAINT `tbl_stok_rp_out_ibfk_1` FOREIGN KEY (`stok_in_id`) REFERENCES `tbl_stok_rp_in` (`id`) ON DELETE SET NULL,
  CONSTRAINT `tbl_stok_rp_out_ibfk_2` FOREIGN KEY (`rp_id`) REFERENCES `master_rp` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_stok_rp_out`
--

LOCK TABLES `tbl_stok_rp_out` WRITE;
/*!40000 ALTER TABLE `tbl_stok_rp_out` DISABLE KEYS */;
INSERT INTO `tbl_stok_rp_out` VALUES
(1,2,2,60.00,NULL,'2026-06-23',NULL,'2026-06-21 02:00:54'),
(2,3,1,1.00,NULL,'2026-07-02',NULL,'2026-07-02 09:28:55'),
(3,4,3,2.00,NULL,'2026-07-03',NULL,'2026-07-03 10:36:51');
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_usage_color`
--

LOCK TABLES `tbl_usage_color` WRITE;
/*!40000 ALTER TABLE `tbl_usage_color` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_usage_material_lain`
--

LOCK TABLES `tbl_usage_material_lain` WRITE;
/*!40000 ALTER TABLE `tbl_usage_material_lain` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_usage_rp`
--

LOCK TABLES `tbl_usage_rp` WRITE;
/*!40000 ALTER TABLE `tbl_usage_rp` DISABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
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
(26,'KLT-002','KY-0044','1.2','Brown',0.00,'2026-07-03 10:30:44');
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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_yl_movement`
--

LOCK TABLES `tbl_yl_movement` WRITE;
/*!40000 ALTER TABLE `tbl_yl_movement` DISABLE KEYS */;
INSERT INTO `tbl_yl_movement` VALUES
(1,'YL-001','KY-0001','OUT','','',10.00,'2026-06-23',NULL,'2026-06-21 01:10:51');
/*!40000 ALTER TABLE `tbl_yl_movement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'mrp'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-08-05 16:23:19
