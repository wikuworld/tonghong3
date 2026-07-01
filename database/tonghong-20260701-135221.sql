/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.8.6-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: tonghong
-- ------------------------------------------------------
-- Server version	11.8.6-MariaDB-ubu2404

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
-- Current Database: `tonghong`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `tonghong` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci */;

USE `tonghong`;

--
-- Table structure for table `accounting_mappings`
--

DROP TABLE IF EXISTS `accounting_mappings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounting_mappings` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `transaction_type` varchar(50) NOT NULL,
  `status` varchar(50) DEFAULT NULL,
  `coa_code` varchar(20) NOT NULL,
  `coa_name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounting_mappings`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `accounting_mappings` WRITE;
/*!40000 ALTER TABLE `accounting_mappings` DISABLE KEYS */;
/*!40000 ALTER TABLE `accounting_mappings` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES
('i5j6k7l8m9n0');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `audit_logs`
--

DROP TABLE IF EXISTS `audit_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_logs` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `entity_type` varchar(80) NOT NULL,
  `entity_id` bigint(20) DEFAULT NULL,
  `action` varchar(40) NOT NULL,
  `payload_before` text DEFAULT NULL,
  `payload_after` text DEFAULT NULL,
  `actor` varchar(120) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=127 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_logs`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `audit_logs` WRITE;
/*!40000 ALTER TABLE `audit_logs` DISABLE KEYS */;
INSERT INTO `audit_logs` VALUES
(1,'sales_order',11,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-04-30 02:17:28'),
(2,'sales_order_line',10,'update','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"LT SMOKE GREY (0AL)\", \"color_family\": \"color\", \"color_reference\": null, \"thickness_text\": \"1.24\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"325.00\", \"line_etd\": \"2026-05-15\", \"backing\": null, \"unit_price\": \"1.0000\"}','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"LT SMOKE GREY (0AL)\", \"color_family\": \"color\", \"color_reference\": null, \"thickness_text\": \"1.24\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"325\", \"line_etd\": \"2026-05-15\", \"backing\": null, \"unit_price\": \"1.0000\"}','Cre@tiv3','2026-04-30 02:17:28'),
(3,'sales_order',11,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-04-30 02:46:20'),
(4,'sales_order_line',10,'update','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"LT SMOKE GREY (0AL)\", \"color_family\": \"color\", \"color_reference\": null, \"thickness_text\": \"1.24\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"325.00\", \"line_etd\": \"2026-05-15\", \"backing\": null, \"unit_price\": \"1.0000\"}','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"LT SMOKE GREY (0AL)\", \"color_family\": \"color\", \"color_reference\": null, \"thickness_text\": \"1.24\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"325\", \"line_etd\": \"2026-05-15\", \"backing\": null, \"unit_price\": \"1.0000\"}','Cre@tiv3','2026-04-30 02:46:21'),
(5,'sales_order',11,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-04-30 02:46:51'),
(6,'sales_order_line',10,'update','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"LT SMOKE GREY (0AL)\", \"color_family\": \"color\", \"color_reference\": null, \"thickness_text\": \"1.24\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"325.00\", \"line_etd\": \"2026-05-15\", \"backing\": null, \"unit_price\": \"1.0000\"}','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"LT SMOKE GREY (0AL)\", \"color_family\": \"color\", \"color_reference\": null, \"thickness_text\": \"1.24\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"325\", \"line_etd\": \"2026-05-15\", \"backing\": null, \"unit_price\": \"1.0000\"}','Cre@tiv3','2026-04-30 02:46:56'),
(7,'sales_order',11,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-04-30 02:47:19'),
(8,'sales_order_line',10,'update','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"LT SMOKE GREY (0AL)\", \"color_family\": \"color\", \"color_reference\": null, \"thickness_text\": \"1.24\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"325.00\", \"line_etd\": \"2026-05-15\", \"backing\": null, \"unit_price\": \"1.0000\"}','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"LT SMOKE GREY (0AL)\", \"color_family\": \"color\", \"color_reference\": null, \"thickness_text\": \"1.24\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"325\", \"line_etd\": \"2026-05-15\", \"backing\": null, \"unit_price\": \"1.0000\"}','Cre@tiv3','2026-04-30 02:47:24'),
(9,'sales_order',11,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-04-30 02:48:43'),
(10,'sales_order_line',10,'update','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"LT SMOKE GREY (0AL)\", \"color_family\": \"color\", \"color_reference\": null, \"thickness_text\": \"1.24\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"325.00\", \"line_etd\": \"2026-05-15\", \"backing\": null, \"unit_price\": \"1.0000\"}','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"LT SMOKE GREY (0AL)\", \"color_family\": \"color\", \"color_reference\": null, \"thickness_text\": \"1.24\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"325\", \"line_etd\": \"2026-05-15\", \"backing\": null, \"unit_price\": \"1.0000\"}','Cre@tiv3','2026-04-30 02:48:46'),
(11,'sales_order',11,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-04-30 02:51:16'),
(12,'sales_order_line',10,'update','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"LT SMOKE GREY (0AL)\", \"color_family\": \"color\", \"color_reference\": null, \"thickness_text\": \"1.24\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"325.00\", \"line_etd\": \"2026-05-15\", \"backing\": null, \"unit_price\": \"1.0000\"}','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"LT SMOKE GREY (0AL)\", \"color_family\": \"color\", \"color_reference\": null, \"thickness_text\": \"1.24\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"325\", \"line_etd\": \"2026-05-15\", \"backing\": null, \"unit_price\": \"1.0000\"}','Cre@tiv3','2026-04-30 02:51:19'),
(13,'sales_order',11,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-04-30 02:51:55'),
(14,'sales_order_line',10,'update','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"LT SMOKE GREY (0AL)\", \"color_family\": \"color\", \"color_reference\": null, \"thickness_text\": \"1.24\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"325.00\", \"line_etd\": \"2026-05-15\", \"backing\": null, \"unit_price\": \"1.0000\"}','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"LT SMOKE GREY (0AL)\", \"color_family\": \"color\", \"color_reference\": null, \"thickness_text\": \"1.24\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"325\", \"line_etd\": \"2026-05-15\", \"backing\": null, \"unit_price\": \"1.0000\"}','Cre@tiv3','2026-04-30 02:51:56'),
(15,'sales_order',11,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-04-30 02:52:33'),
(16,'sales_order_line',10,'update','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"LT SMOKE GREY (0AL)\", \"color_family\": \"color\", \"color_reference\": null, \"thickness_text\": \"1.24\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"325.00\", \"line_etd\": \"2026-05-15\", \"backing\": null, \"unit_price\": \"1.0000\"}','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"LT SMOKE GREY (0AL)\", \"color_family\": \"color\", \"color_reference\": null, \"thickness_text\": \"1.24\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"325\", \"line_etd\": \"2026-05-15\", \"backing\": null, \"unit_price\": \"1.0000\"}','Cre@tiv3','2026-04-30 02:52:33'),
(17,'sales_order',11,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-04-30 02:52:40'),
(18,'sales_order_line',10,'update','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"LT SMOKE GREY (0AL)\", \"color_family\": \"color\", \"color_reference\": null, \"thickness_text\": \"1.24\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"325.00\", \"line_etd\": \"2026-05-15\", \"backing\": null, \"unit_price\": \"1.0000\"}','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"LT SMOKE GREY (0AL)\", \"color_family\": \"color\", \"color_reference\": null, \"thickness_text\": \"1.24\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"325\", \"line_etd\": \"2026-05-15\", \"backing\": null, \"unit_price\": \"1.0000\"}','Cre@tiv3','2026-04-30 02:52:42'),
(19,'sales_order',11,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-04-30 02:56:44'),
(20,'sales_order_line',10,'update','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"LT SMOKE GREY (0AL)\", \"color_family\": \"color\", \"color_reference\": null, \"thickness_text\": \"1.24\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"325.00\", \"line_etd\": \"2026-05-15\", \"backing\": null, \"unit_price\": \"1.0000\"}','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"LT SMOKE GREY (0AL)\", \"color_family\": \"color\", \"color_reference\": null, \"thickness_text\": \"1.24\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"325\", \"line_etd\": \"2026-05-15\", \"backing\": null, \"unit_price\": \"1.0000\"}','Cre@tiv3','2026-04-30 02:56:49'),
(21,'sales_order',13,'create',NULL,'{\"po_number\": \"SO-202605-00001\", \"status\": \"draft\"}','Cre@tiv3','2026-05-04 03:01:46'),
(22,'sales_order_line',11,'create',NULL,'{\"po_id\": 13, \"material_name\": \"VIRGIN HYDRO PU\", \"color\": \"AURA (4AH)\", \"color_family\": \"color\", \"quantity_order\": \"10\", \"unit_price\": null}','Cre@tiv3','2026-05-04 03:01:47'),
(23,'sales_order_line',12,'create',NULL,'{\"po_id\": 13, \"material_name\": \"ECO TECH COMFORT\", \"color\": \"BLACK (00A)\", \"color_family\": \"black\", \"quantity_order\": \"12\", \"unit_price\": \"1.94\"}','Cre@tiv3','2026-05-04 03:01:47'),
(24,'sales_order_line',13,'create',NULL,'{\"po_id\": 13, \"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"BLACK (00A)\", \"color_family\": \"black\", \"quantity_order\": \"1200\", \"unit_price\": \"10\"}','Cre@tiv3','2026-05-04 03:01:48'),
(25,'sales_order_line',14,'create',NULL,'{\"po_id\": 13, \"material_name\": \"VIRGIN HYDRO PU\", \"color\": \"OXYGEN PURPLE (5AX)\", \"color_family\": \"color\", \"quantity_order\": \"1000\", \"unit_price\": \"10\"}','Cre@tiv3','2026-05-04 03:01:48'),
(26,'sales_order_line',15,'create',NULL,'{\"po_id\": 13, \"material_name\": \"VIRGIN HYDRO PU\", \"color\": \"AURA (4AH)\", \"color_family\": \"color\", \"quantity_order\": \"10\", \"unit_price\": \"10\"}','Cre@tiv3','2026-05-04 03:01:49'),
(27,'sales_order',14,'create',NULL,'{\"po_number\": \"SO-202605-00002\", \"status\": \"draft\", \"duplicated_from_po_id\": 13, \"line_count\": 5, \"via\": \"duplicate_po\"}','Cre@tiv3','2026-05-04 03:05:41'),
(28,'sales_order',14,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"confirmed\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-05-04 03:09:46'),
(29,'sales_order',14,'update','{\"status\": \"confirmed\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"confirmed\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-05-04 03:13:01'),
(30,'sales_order',14,'update','{\"status\": \"confirmed\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"confirmed\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-05-04 03:13:01'),
(31,'sales_order',14,'update','{\"status\": \"confirmed\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"confirmed\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-05-04 03:13:02'),
(32,'sales_order',14,'update','{\"status\": \"confirmed\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"confirmed\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-05-04 03:13:03'),
(33,'sales_order',14,'update','{\"status\": \"confirmed\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"confirmed\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-05-04 03:13:04'),
(34,'sales_order',14,'update','{\"status\": \"confirmed\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"confirmed\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-05-04 03:13:05'),
(35,'sales_order',14,'update','{\"status\": \"confirmed\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"confirmed\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-05-04 03:13:07'),
(36,'sales_order',14,'update','{\"status\": \"confirmed\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"confirmed\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-05-04 03:13:10'),
(37,'sales_order',15,'create',NULL,'{\"po_number\": \"SO-202605-00003\", \"status\": \"draft\"}','Cre@tiv3','2026-05-11 18:47:28'),
(38,'sales_order_line',21,'create',NULL,'{\"po_id\": 15, \"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"BLACK (00A)\", \"color_family\": \"black\", \"quantity_order\": \"12\", \"unit_price\": \"1.12\"}','Cre@tiv3','2026-05-11 18:47:28'),
(39,'sales_order',15,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-05-11 18:48:43'),
(40,'sales_order_line',21,'update','{\"thi_line_ref\": \"PU-\"}','{\"thi_line_ref\": \"PUM123260511001\", \"via\": \"generate_lot\"}','Cre@tiv3','2026-05-11 18:48:46'),
(41,'sales_order',15,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-05-11 18:49:07'),
(42,'sales_order_line',21,'update','{\"thi_line_ref\": \"PUM123260511001\"}','{\"thi_line_ref\": \"PUM123456260511001\", \"via\": \"generate_lot\"}','Cre@tiv3','2026-05-11 18:49:11'),
(43,'sales_order',15,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-05-11 18:49:15'),
(44,'sales_order_line',21,'update','{\"thi_line_ref\": \"PUM123456260511001\"}','{\"thi_line_ref\": \"PUM123456260511002\", \"via\": \"generate_lot\"}','Cre@tiv3','2026-05-11 18:49:15'),
(45,'sales_order',15,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-05-11 18:51:35'),
(46,'sales_order_line',21,'update','{\"thi_line_ref\": \"PUM123456260511002\"}','{\"thi_line_ref\": \"PUM123456260511003\", \"via\": \"generate_lot\"}','Cre@tiv3','2026-05-11 18:51:36'),
(47,'sales_order',15,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-05-11 18:51:37'),
(48,'sales_order_line',21,'update','{\"thi_line_ref\": \"PUM123456260511003\"}','{\"thi_line_ref\": \"PUM123456260511004\", \"via\": \"generate_lot\"}','Cre@tiv3','2026-05-11 18:51:42'),
(49,'sales_order',16,'create',NULL,'{\"po_number\": \"SO-202605-00004\", \"status\": \"draft\"}','Cre@tiv3','2026-05-11 19:25:24'),
(50,'sales_order',17,'create',NULL,'{\"po_number\": \"SO-202605-00005\", \"status\": \"draft\"}','Cre@tiv3','2026-05-11 19:28:20'),
(51,'sales_order',18,'create',NULL,'{\"po_number\": \"SO-202605-00006\", \"status\": \"draft\"}','Cre@tiv3','2026-05-11 19:29:31'),
(52,'sales_order_line',22,'create',NULL,'{\"po_id\": 18, \"material_name\": \"ECO TECH COMFORT\", \"color\": \"BLACK (00A)\", \"color_family\": \"black\", \"quantity_order\": \"12\", \"unit_price\": \"1.28\"}','Cre@tiv3','2026-05-11 19:29:36'),
(53,'sales_order',18,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-05-11 20:29:26'),
(54,'sales_order',18,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-05-11 20:29:28'),
(55,'sales_order',18,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-05-11 21:24:27'),
(56,'sales_order',18,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-05-11 21:24:29'),
(57,'sales_order',19,'create',NULL,'{\"po_number\": \"SO-202605-00007\", \"status\": \"draft\"}','Cre@tiv3','2026-05-12 03:19:54'),
(58,'sales_order_line',23,'create',NULL,'{\"po_id\": 19, \"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"WOLF GREY (01V)\", \"color_family\": \"color\", \"quantity_order\": \"1000\", \"unit_price\": \"11.07\"}','Cre@tiv3','2026-05-12 03:19:56'),
(59,'sales_order_line',24,'create',NULL,'{\"po_id\": 19, \"material_name\": \"ECO TECH COMFORT\", \"color\": \"BLACK (00A)\", \"color_family\": \"black\", \"quantity_order\": \"2000\", \"unit_price\": \"1.28\"}','Cre@tiv3','2026-05-12 03:19:56'),
(60,'sales_order',19,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-05-12 03:21:31'),
(61,'sales_order_line',23,'update','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"WOLF GREY (01V)\", \"color_family\": \"color\", \"color_reference\": null, \"color_standard\": null, \"thickness_text\": \"1.02\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"1000.00\", \"line_etd\": null, \"backing\": null, \"unit_price\": \"11.0700\"}','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"WOLF GREY (01V)\", \"color_family\": \"color\", \"color_reference\": null, \"color_standard\": null, \"thickness_text\": \"1.02\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"1000\", \"line_etd\": null, \"backing\": null, \"unit_price\": \"11.0700\"}','Cre@tiv3','2026-05-12 03:21:31'),
(62,'sales_order_line',24,'delete','{\"material_name\": \"ECO TECH COMFORT\", \"unit_price\": \"1.2800\"}',NULL,'Cre@tiv3','2026-05-12 03:21:32'),
(63,'sales_order',20,'create',NULL,'{\"po_number\": \"SO-202605-00008\", \"status\": \"draft\"}','Cre@tiv3','2026-05-12 09:01:47'),
(64,'sales_order_line',25,'create',NULL,'{\"po_id\": 20, \"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"PHANTOM (01X)\", \"color_family\": \"color\", \"quantity_order\": \"10\", \"unit_price\": \"1.07\"}','Cre@tiv3','2026-05-12 09:01:51'),
(65,'sales_order',20,'delete','{\"po_number\": \"SO-202605-00008\", \"status\": \"draft\"}',NULL,'Cre@tiv3','2026-05-19 08:32:31'),
(66,'sales_order',14,'delete','{\"po_number\": \"SO-202605-00002\", \"status\": \"confirmed\"}',NULL,'Cre@tiv3','2026-05-19 08:32:36'),
(67,'sales_order',21,'create',NULL,'{\"po_number\": \"SO-202606-00001\", \"status\": \"draft\"}','Cre@tiv3','2026-06-05 00:51:40'),
(68,'sales_order_line',26,'create',NULL,'{\"po_id\": 21, \"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"ACTIVE FUCHSIA\", \"color_family\": \"color\", \"quantity_order\": \"2000\", \"unit_price\": \"1.07\"}','Cre@tiv3','2026-06-05 00:51:40'),
(69,'sales_order',21,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-06-05 00:52:27'),
(70,'sales_order_line',26,'update','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"ACTIVE FUCHSIA\", \"color_family\": \"color\", \"color_reference\": \"6HJ\", \"color_standard\": \"TMAD0022022061001\", \"thickness_text\": \"1.02\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"2000.00\", \"line_etd\": null, \"backing\": \"6DX\", \"unit_price\": \"1.0700\"}','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"ACTIVE FUCHSIA\", \"color_family\": \"color\", \"color_reference\": \"6HJ\", \"color_standard\": \"TMAD0022022061001\", \"thickness_text\": \"1.02\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"2000\", \"line_etd\": null, \"backing\": \"6DX\", \"unit_price\": \"1.0700\"}','Cre@tiv3','2026-06-05 00:52:30'),
(71,'sales_order',21,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-06-05 01:18:07'),
(72,'sales_order_line',26,'update','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"ACTIVE FUCHSIA\", \"color_family\": \"color\", \"color_reference\": \"6HJ\", \"color_standard\": \"TMAD0022022061001\", \"thickness_text\": \"1.02\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"2000.00\", \"line_etd\": null, \"backing\": \"6DX\", \"unit_price\": \"1.0700\"}','{\"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"ACTIVE FUCHSIA\", \"color_family\": \"color\", \"color_reference\": \"6HJ\", \"color_standard\": \"TMAD0022022061001\", \"thickness_text\": \"1.02\", \"thickness_min\": null, \"thickness_max\": null, \"quantity_order\": \"2000\", \"line_etd\": null, \"backing\": \"6DX\", \"unit_price\": \"1.0700\"}','Cre@tiv3','2026-06-05 01:18:10'),
(73,'sales_order',21,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-06-05 01:50:04'),
(74,'sales_order_line',26,'update','{\"thi_line_ref\": \"PUMSL044260605001\"}','{\"thi_line_ref\": \"PUMSL044260605002\", \"via\": \"generate_lot\"}','Cre@tiv3','2026-06-05 01:50:04'),
(75,'sales_order',21,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-06-05 01:50:06'),
(76,'sales_order_line',26,'update','{\"thi_line_ref\": \"PUMSL044260605002\"}','{\"thi_line_ref\": \"PUMSL044260605003\", \"via\": \"generate_lot\"}','Cre@tiv3','2026-06-05 01:50:06'),
(77,'sales_order',21,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-06-05 01:50:08'),
(78,'sales_order',21,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-06-05 01:50:09'),
(79,'sales_order',21,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-06-05 01:50:10'),
(80,'sales_order',21,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-06-05 01:50:11'),
(81,'sales_order',21,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-06-05 01:50:11'),
(82,'sales_order_line',26,'update','{\"thi_line_ref\": \"PUMSL044260605003\"}','{\"thi_line_ref\": \"PUMSL044260605004\", \"via\": \"generate_lot\"}','Cre@tiv3','2026-06-05 01:50:13'),
(83,'sales_order_line',26,'update','{\"thi_line_ref\": \"PUMSL044260605004\"}','{\"thi_line_ref\": \"PUMSL044260605005\", \"via\": \"generate_lot\"}','Cre@tiv3','2026-06-05 01:50:13'),
(84,'sales_order',21,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-06-05 02:02:22'),
(85,'sales_order',21,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-06-05 02:02:23'),
(86,'sales_order',21,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-06-05 02:02:25'),
(87,'sales_order',25,'create',NULL,'{\"po_number\": \"SO-202606-00002\", \"status\": \"draft\"}','Cre@tiv3','2026-06-05 02:49:33'),
(88,'sales_order_line',27,'create',NULL,'{\"po_id\": 25, \"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"LT SMOKE GREY (0AL)\", \"color_family\": \"color\", \"quantity_order\": \"1000\", \"unit_price\": \"1.07\"}','Cre@tiv3','2026-06-05 02:49:33'),
(89,'sales_order_line',28,'create',NULL,'{\"po_id\": 25, \"material_name\": \"HYDRO SOFT ACTION LEATHER\", \"color\": \"BLACK (NB1000018)\", \"color_family\": \"black\", \"quantity_order\": \"2000\", \"unit_price\": \"10\"}','Cre@tiv3','2026-06-05 02:49:33'),
(90,'sales_order',25,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-06-05 02:52:44'),
(91,'sales_order',25,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-06-05 02:52:45'),
(92,'sales_order',25,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-06-05 02:54:26'),
(93,'sales_order',25,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-06-05 02:54:27'),
(94,'sales_order',25,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-06-05 02:54:28'),
(95,'sales_order',26,'create',NULL,'{\"po_number\": \"SO-202606-00003\", \"status\": \"draft\"}','Cre@tiv3','2026-06-08 21:15:01'),
(96,'sales_order_line',29,'create',NULL,'{\"po_id\": 26, \"material_name\": \"CASHMERE SUEDE\", \"color\": \"BETTER SCARLET (AETG)\", \"color_family\": \"color\", \"quantity_order\": \"90\", \"unit_price\": \"1.06\"}','Cre@tiv3','2026-06-08 21:15:01'),
(97,'sales_order',26,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-06-08 21:35:54'),
(98,'sales_order',26,'workflow_advance',NULL,'{\"mkt_workflow_stage\": \"rekap_printed\"}','Cre@tiv3','2026-06-08 21:49:41'),
(99,'sales_order',26,'workflow_advance',NULL,'{\"mkt_workflow_stage\": \"with_ppic\"}','Cre@tiv3','2026-06-08 21:53:26'),
(100,'sales_order',26,'workflow_advance',NULL,'{\"mkt_workflow_stage\": \"back_to_mkt\"}','Cre@tiv3','2026-06-08 21:53:37'),
(101,'sales_order',26,'workflow_advance',NULL,'{\"mkt_workflow_stage\": \"in_outstanding\"}','Cre@tiv3','2026-06-08 21:53:43'),
(102,'sales_order',26,'workflow_advance',NULL,'{\"mkt_workflow_stage\": \"material_followup\"}','Cre@tiv3','2026-06-08 21:53:53'),
(103,'sales_order',25,'workflow_advance',NULL,'{\"mkt_workflow_stage\": \"rekap_printed\"}','Cre@tiv3','2026-06-08 22:05:46'),
(104,'sales_order',25,'workflow_advance',NULL,'{\"mkt_workflow_stage\": \"with_ppic\"}','Cre@tiv3','2026-06-08 22:05:50'),
(105,'sales_order',26,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"material_followup\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"material_followup\"}','Cre@tiv3','2026-06-08 22:11:33'),
(106,'sales_order',26,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"material_followup\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"material_followup\"}','Cre@tiv3','2026-06-08 22:11:34'),
(107,'sales_order',21,'rekap_printed',NULL,'{\"rekap_printed_at\": \"2026-06-08T22:22:19.458791\", \"po_number\": \"SO-202606-00001\"}','demo_marketing','2026-06-08 22:22:19'),
(108,'sales_order',21,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"confirmed\", \"mkt_workflow_stage\": \"input_system\"}','demo_marketing','2026-06-08 22:23:05'),
(109,'sales_order',21,'auto_advance',NULL,'{\"mkt_workflow_stage\": \"rekap_printed\"}','demo_marketing','2026-06-08 22:23:05'),
(110,'sales_order',21,'auto_advance',NULL,'{\"mkt_workflow_stage\": \"with_ppic\"}','demo_marketing','2026-06-08 22:24:20'),
(111,'sales_order',26,'workflow_rollback',NULL,'{\"mkt_workflow_stage\": \"in_outstanding\"}','demo_marketing','2026-06-08 22:24:34'),
(112,'sales_order',21,'workflow_advance',NULL,'{\"mkt_workflow_stage\": \"back_to_mkt\"}','demo_marketing','2026-06-08 22:25:33'),
(113,'sales_order',26,'auto_advance',NULL,'{\"mkt_workflow_stage\": \"material_followup\"}','Cre@tiv3','2026-06-08 23:57:42'),
(114,'sales_order',25,'workflow_rollback',NULL,'{\"mkt_workflow_stage\": \"rekap_printed\"}','Cre@tiv3','2026-06-08 23:58:51'),
(115,'sales_order',25,'workflow_rollback',NULL,'{\"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-06-08 23:58:58'),
(116,'sales_order',27,'create',NULL,'{\"po_number\": \"SO-202606-00004\", \"status\": \"draft\"}','Cre@tiv3','2026-06-11 03:12:42'),
(117,'sales_order_line',30,'create',NULL,'{\"po_id\": 27, \"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"WOLF GREY (01V)\", \"color_family\": \"color\", \"quantity_order\": \"100\", \"unit_price\": \"1.07\"}','Cre@tiv3','2026-06-11 03:12:42'),
(118,'sales_order',26,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"material_followup\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"material_followup\"}','Cre@tiv3','2026-06-22 11:07:14'),
(121,'sales_order',27,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-06-22 11:07:12'),
(122,'sales_order',26,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"material_followup\"}','{\"status\": \"draft\", \"mkt_workflow_stage\": \"material_followup\"}','Cre@tiv3','2026-06-22 11:07:41'),
(123,'sales_order',27,'update','{\"status\": \"draft\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"confirmed\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-06-22 12:14:28'),
(124,'sales_order',27,'update','{\"status\": \"confirmed\", \"mkt_workflow_stage\": \"input_system\"}','{\"status\": \"confirmed\", \"mkt_workflow_stage\": \"input_system\"}','Cre@tiv3','2026-06-22 12:14:31'),
(125,'sales_order',28,'create',NULL,'{\"po_number\": \"SO-202606-00005\", \"status\": \"draft\"}','Cre@tiv3','2026-06-30 07:59:59'),
(126,'sales_order_line',31,'create',NULL,'{\"po_id\": 28, \"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"color\": \"WOLF GREY (01V)\", \"color_family\": \"color\", \"quantity_order\": \"1000\", \"unit_price\": \"1.07\"}','Cre@tiv3','2026-06-30 07:59:59');
/*!40000 ALTER TABLE `audit_logs` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `brand_buyer_maps`
--

DROP TABLE IF EXISTS `brand_buyer_maps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `brand_buyer_maps` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `brand_id` bigint(20) NOT NULL,
  `buyer_code` varchar(32) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_brand_buyer_map` (`brand_id`,`buyer_code`),
  CONSTRAINT `brand_buyer_maps_ibfk_1` FOREIGN KEY (`brand_id`) REFERENCES `brands` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `brand_buyer_maps`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `brand_buyer_maps` WRITE;
/*!40000 ALTER TABLE `brand_buyer_maps` DISABLE KEYS */;
INSERT INTO `brand_buyer_maps` VALUES
(1,1,'NIKE'),
(2,2,'OIA NIKE'),
(3,3,'ADIDAS'),
(4,4,'NB'),
(5,5,'UA');
/*!40000 ALTER TABLE `brand_buyer_maps` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `brand_constraints`
--

DROP TABLE IF EXISTS `brand_constraints`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `brand_constraints` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `customer_id` bigint(20) NOT NULL,
  `allowed_brand_ids` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`allowed_brand_ids`)),
  `created_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `customer_id` (`customer_id`),
  CONSTRAINT `brand_constraints_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `brand_constraints`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `brand_constraints` WRITE;
/*!40000 ALTER TABLE `brand_constraints` DISABLE KEYS */;
/*!40000 ALTER TABLE `brand_constraints` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `brands`
--

DROP TABLE IF EXISTS `brands`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `brands` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `code` varchar(50) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `brands`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `brands` WRITE;
/*!40000 ALTER TABLE `brands` DISABLE KEYS */;
INSERT INTO `brands` VALUES
(1,'NIKE','NIKE'),
(2,'OIA NIKE','OIA NIKE'),
(3,'ADIDAS','ADIDAS'),
(4,'NB','NB'),
(5,'UA','UA'),
(6,'ON CLOUD','ON CLOUD');
/*!40000 ALTER TABLE `brands` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `buyer_price_lists`
--

DROP TABLE IF EXISTS `buyer_price_lists`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `buyer_price_lists` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `buyer_code` varchar(32) NOT NULL,
  `title` text DEFAULT NULL,
  `period_label` text DEFAULT NULL,
  `period_start` date DEFAULT NULL,
  `period_end` date DEFAULT NULL,
  `meta_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`meta_json`)),
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `currency` varchar(3) NOT NULL DEFAULT 'USD',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_buyer_price_lists_buyer_code` (`buyer_code`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `buyer_price_lists`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `buyer_price_lists` WRITE;
/*!40000 ALTER TABLE `buyer_price_lists` DISABLE KEYS */;
INSERT INTO `buyer_price_lists` VALUES
(13,'NB','LIST HARGA NB MATERIAL','PERIODE 2026/03/01 - 2026/09/30,,,,','2026-03-01','2026-09-30','{\"filename\": \"01_NB.csv\", \"source_label\": \"LIST_HARGA_ALL_BUYER_extracted\", \"header_row_index\": 3, \"csv_line_count\": 17, \"data_row_count\": 9}','2026-04-29 17:12:26','USD'),
(14,'ADIDAS','LIST HARGA MATERIAL ADIDAS','PERIODE 2026/02/01 - 2026/07/31,,,','2026-02-01','2026-07-31','{\"filename\": \"02_ADIDAS.csv\", \"source_label\": \"LIST_HARGA_ALL_BUYER_extracted\", \"header_row_index\": 3, \"csv_line_count\": 89, \"data_row_count\": 17}','2026-04-29 17:12:26','USD'),
(15,'NIKE','LIST HARGA MATERIAL NIKE','PERIODE 2026/01/01 - 2026/06/30,,,,,,,    a. Codes which are not beginning with AR, DE, R belong to special R/P except below R/P,,,,','2026-01-01','2026-06-30','{\"filename\": \"03_NIKE.csv\", \"source_label\": \"LIST_HARGA_ALL_BUYER_extracted\", \"header_row_index\": 4, \"csv_line_count\": 150, \"data_row_count\": 28}','2026-04-29 17:12:26','USD'),
(16,'UA','LIST HARGA MATERIAL UA','PERIODE 2026/02/01 - 2026/07/31,,,,,','2026-02-01','2026-07-31','{\"filename\": \"04_UA.csv\", \"source_label\": \"LIST_HARGA_ALL_BUYER_extracted\", \"header_row_index\": 3, \"csv_line_count\": 39, \"data_row_count\": 7}','2026-04-29 17:12:26','USD'),
(17,'NB01','NB Periode 04 Mei 2026 - 04 mei 2027','NB Periode 04 Mei 2026 - 04 mei 2027','2026-05-04','2027-03-04','{\"column_keys\": [\"ITEM\", \"THICKNESS\", \"COLOR\", \"COLOR WHITE\", \"COLOR BLACK\", \"FLOURASENT\", \"METALIC\", \"EMBOSS\", \"SPESIAL EMBOSS\"]}','2026-05-04 02:28:41','USD');
/*!40000 ALTER TABLE `buyer_price_lists` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `buyer_price_sheet_rows`
--

DROP TABLE IF EXISTS `buyer_price_sheet_rows`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `buyer_price_sheet_rows` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `list_id` bigint(20) NOT NULL,
  `row_number` int(11) NOT NULL,
  `cells` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`cells`)),
  PRIMARY KEY (`id`),
  KEY `ix_buyer_price_sheet_rows_list_id` (`list_id`),
  CONSTRAINT `buyer_price_sheet_rows_ibfk_1` FOREIGN KEY (`list_id`) REFERENCES `buyer_price_lists` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=579 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `buyer_price_sheet_rows`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `buyer_price_sheet_rows` WRITE;
/*!40000 ALTER TABLE `buyer_price_sheet_rows` DISABLE KEYS */;
INSERT INTO `buyer_price_sheet_rows` VALUES
(515,13,0,'{\"ITEM\": \"HYDRO PU COATED LEATHER\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.14\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.1\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(516,13,1,'{\"ITEM\": \"HYDRO PRO ACTION LEATHER\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.05\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.1\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(517,13,2,'{\"ITEM\": \"HYDRO SOFT ACTION LEATHER\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.16\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.1\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(518,13,3,'{\"ITEM\": \"HYDRO SOFT HIDE PU COATED LEATHER\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.29\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.1\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(519,13,4,'{\"ITEM\": \"LACCATO PATENT LEATHER\", \"THICKNESS\": \"1.4-1.8\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.91\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.1\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(520,13,5,'{\"ITEM\": \"LS PATENT LEATHER\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.65\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.1\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(521,13,6,'{\"ITEM\": \"ECO GREEN RECYCLED LETAHER\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.58\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.1\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(522,13,7,'{\"ITEM\": \"SPLIT SUEDE\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.33\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0\", \"METALIC\": \"0\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(523,13,8,'{\"ITEM\": \"SPLIT SUEDE\", \"THICKNESS\": \"1.6-1.8\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.38\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0\", \"METALIC\": \"0\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(524,14,0,'{\"ITEM\": \"PU COATED LEATHER (MAP-ACTION LEATHER) 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.12\", \"COLOR BLACK\": \"0.03\", \"FLOURASENT\": \"0.16\", \"METALIC\": \"0.2\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(525,14,1,'{\"ITEM\": \"PU COATED LEATHER (MAP-ACTION LEATHER) AR-140 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.32\", \"COLOR BLACK\": \"0.03\", \"FLOURASENT\": \"0.16\", \"METALIC\": \"0.2\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(526,14,2,'{\"ITEM\": \"SOFT PU COATED LEATHER (MAP-SOFT PU) 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.15\", \"COLOR BLACK\": \"0.03\", \"FLOURASENT\": \"0.16\", \"METALIC\": \"0.2\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(527,14,3,'{\"ITEM\": \"SOFT PU COATED LEATHER (MAP-SOFT PU) AR-140 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.35\", \"COLOR BLACK\": \"0.03\", \"FLOURASENT\": \"0.16\", \"METALIC\": \"0.2\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(528,14,4,'{\"ITEM\": \"ACTION LEATHER - EPM 5 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.12\", \"COLOR BLACK\": \"0.03\", \"FLOURASENT\": \"0.16\", \"METALIC\": \"0.2\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(529,14,5,'{\"ITEM\": \"HYDRO SOFT PU COATED LEATHER - EPM 3 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.15\", \"COLOR BLACK\": \"0.03\", \"FLOURASENT\": \"0.16\", \"METALIC\": \"0.2\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(530,14,6,'{\"ITEM\": \"SEMI FULL GRAIN (RS) - EPM 5 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.37\", \"COLOR BLACK\": \"0.03\", \"FLOURASENT\": \"0.16\", \"METALIC\": \"0.2\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(531,14,7,'{\"ITEM\": \"HYDRO ECO TECH COMFORT 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.5\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0.1\", \"METALIC\": \"0.2\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(532,14,8,'{\"ITEM\": \"BABY SOFT PATENT LEATHER 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.6\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0.1\", \"METALIC\": \"0.2\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(533,14,9,'{\"ITEM\": \"SOHO NUBUCK 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.63\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0.1\", \"METALIC\": \"0.2\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(534,14,10,'{\"ITEM\": \"LACCATTO PATENT LEATHER - EPM 5 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.91\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0.1\", \"METALIC\": \"0.2\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(535,14,11,'{\"ITEM\": \"LS-SHIFT PATENT LEATHER 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.8\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0.1\", \"METALIC\": \"0.2\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(536,14,12,'{\"ITEM\": \"PRINCESS LEATHER 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.62\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0.1\", \"METALIC\": \"0.2\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(537,14,13,'{\"ITEM\": \"METAL LEATHER - PATENT 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.84\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0\", \"METALIC\": \"0\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(538,14,14,'{\"ITEM\": \"SPLIT SUEDE 1.2 - 1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.22\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0.1\", \"METALIC\": \"0.2\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(539,14,15,'{\"ITEM\": \"HI SUEDE 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.3\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0.1\", \"METALIC\": \"0.2\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(540,14,16,'{\"ITEM\": \"CASHMERE SUEDE 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.78\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0.1\", \"METALIC\": \"0.2\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(541,15,0,'{\"ITEM\": \"VIRGIN HYDRO PU 1.0-1.6 MM\", \"THICKNESS\": \"1.0-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.1\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.25\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(542,15,1,'{\"ITEM\": \"VIRGIN HYDRO PU DE-7 M 1.2-1.4 MM\", \"THICKNESS\": \"1.2-1.4\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.06\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.25\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(543,15,2,'{\"ITEM\": \"VIRGIN HYDRO PU AR-144 M 1.4-1.6 MM\", \"THICKNESS\": \"1.4-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.06\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.25\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(544,15,3,'{\"ITEM\": \"VIRGIN HYDRO PU R-8 ANODIZED 1.2-1.4 MM\", \"THICKNESS\": \"1.2-1.4\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.25\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(545,15,4,'{\"ITEM\": \"VIRGIN HYDRO PU AR-121 SG METALLIC 1.2-1.4 MM\", \"THICKNESS\": \"1.2-1.4\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.25\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(546,15,5,'{\"ITEM\": \"GENERIC PU COATED 1.0-1.6 MM\", \"THICKNESS\": \"1.0-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.1\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.25\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(547,15,6,'{\"ITEM\": \"GENERIC PU COATED DE-7 SM PEARLIZED 1.2-1.4 MM\", \"THICKNESS\": \"1.2-1.4\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.25\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(548,15,7,'{\"ITEM\": \"GENERIC PU COATED DE-41 1.2-1.4 MM\", \"THICKNESS\": \"1.2-1.4\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.06\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.25\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(549,15,8,'{\"ITEM\": \"GENERIC PU COATED UM-T SM PEARLIZED 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.35\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(550,15,9,'{\"ITEM\": \"GENERIC PU COATED AR-185 HG METALLIC 1.4-1.6 MM\", \"THICKNESS\": \"1.4-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.35\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(551,15,10,'{\"ITEM\": \"ECO TECH COMFORT 1.0-1.6 MM\", \"THICKNESS\": \"1.0-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.23\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.25\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(552,15,11,'{\"ITEM\": \"ECO TECH COMFORT R-8 M 1.2-1.4MM\", \"THICKNESS\": \"1.2-1.4\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.18\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.25\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(553,15,12,'{\"ITEM\": \"H. P. ECO TECH COMFORT 1.0-1.6MM\", \"THICKNESS\": \"1.0-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.23\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.25\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(554,15,13,'{\"ITEM\": \"H. P. ECO TECH COMFORT AR-140 DM 1.2-1.4 MM\", \"THICKNESS\": \"1.2-1.4\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.43\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.25\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(555,15,14,'{\"ITEM\": \"SOHO NUBUCK R-231 M 1.2-1.4 MM\", \"THICKNESS\": \"1.2-1.4\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.5\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.25\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(556,15,15,'{\"ITEM\": \"SEMI FULL GRAIN DE-3, DE-45, R-68 G 1.4-1.6 MM\", \"THICKNESS\": \"1.4-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.19\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.25\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(557,15,16,'{\"ITEM\": \"SEMI FULL GRAIN AR-209 SG 1.2-1.4 MM\", \"THICKNESS\": \"1.2-1.4\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.29\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.25\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(558,15,17,'{\"ITEM\": \"SEMI FULL GRAIN AR-140 1.4-1.6 MM\", \"THICKNESS\": \"1.4-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.39\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.25\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(559,15,18,'{\"ITEM\": \"SEMI FULL GRAIN R-83-2 SG 1.2-1.4 MM\", \"THICKNESS\": \"1.2-1.4\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.19\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.25\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(560,15,19,'{\"ITEM\": \"SMART LEATHER 1.2-1.4 MM\", \"THICKNESS\": \"1.2-1.4\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.1\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.25\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(561,15,20,'{\"ITEM\": \"PRINCESS LEATHER AR-59M 1.4-1.6 MM\", \"THICKNESS\": \"1.4-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.55\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.25\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(562,15,21,'{\"ITEM\": \"PRINCESS LEATHER R-8, DE-7 1.4-1.6 MM\", \"THICKNESS\": \"1.4-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.45\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.25\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(563,15,22,'{\"ITEM\": \"LS PATENT LEATHER 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.5\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.25\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(564,15,23,'{\"ITEM\": \"LACCATO PATENT LEATHER 1.4-1.6 MM\", \"THICKNESS\": \"1.4-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.85\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.25\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(565,15,24,'{\"ITEM\": \"LAMPER LEATHER 1.4-1.6 MM\", \"THICKNESS\": \"1.4-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.58\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0.25\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(566,15,25,'{\"ITEM\": \"VIRGIN PU 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.19\", \"COLOR BLACK\": \"0.1\", \"FLOURASENT\": \"0.2\", \"METALIC\": \"0.15\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(567,15,26,'{\"ITEM\": \"(PM) GENERIC PU COATED 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.07\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0.15\", \"METALIC\": \"0.2\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(568,15,27,'{\"ITEM\": \"(PM) GENERIC SPLIT SUEDE, 1.0-1.6MM\", \"THICKNESS\": \"1.0-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.22\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0\", \"METALIC\": \"0\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(569,16,0,'{\"ITEM\": \"Action Pu Coated Leather  1.0-1.6 MM\", \"THICKNESS\": \"1.0-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.12\", \"COLOR BLACK\": \"0.03\", \"FLOURASENT\": \"0.21\", \"METALIC\": \"0\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(570,16,1,'{\"ITEM\": \"Vir Soft PU Coated Leather 1.0-1.6 MM\", \"THICKNESS\": \"1.0-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.24\", \"COLOR BLACK\": \"0.04\", \"FLOURASENT\": \"0.18\", \"METALIC\": \"0\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(571,16,2,'{\"ITEM\": \"LS Patent Leather 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.55\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0\", \"METALIC\": \"0\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(572,16,3,'{\"ITEM\": \"Hydro Eco Tech Comfort 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.9\", \"COLOR BLACK\": \"0.04\", \"FLOURASENT\": \"0.19\", \"METALIC\": \"0\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(573,16,4,'{\"ITEM\": \"Ecogreen Leather 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.69\", \"COLOR BLACK\": \"0.05\", \"FLOURASENT\": \"0\", \"METALIC\": \"0\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(574,16,5,'{\"ITEM\": \"Soho Nubuck 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.48\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0\", \"METALIC\": \"0\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(575,16,6,'{\"ITEM\": \"Nappa Natural Leather 1.2-1.6 MM\", \"THICKNESS\": \"1.2-1.6\", \"COLOR\": \"\", \"COLOR WHITE\": \"1.86\", \"COLOR BLACK\": \"0\", \"FLOURASENT\": \"0\", \"METALIC\": \"0\", \"EMBOSS\": \"0\", \"SPESIAL EMBOSS\": \"0\"}'),
(576,17,0,'{\"ITEM\": \"VIRGIN HYDRO PU\", \"THICKNESS\": \"1.24\", \"COLOR\": \"BLACK (00A)\", \"COLOR WHITE\": 1.12, \"COLOR BLACK\": \"\", \"FLOURASENT\": \"\", \"METALIC\": \"\", \"EMBOSS\": \"\", \"SPESIAL EMBOSS\": \"\"}'),
(577,17,1,'{\"ITEM\": \"(PM) GENERIC PU COATED LEATHER\", \"THICKNESS\": \"1.46\", \"COLOR\": \"BLACK (00A)\", \"COLOR WHITE\": 1.13, \"COLOR BLACK\": \"\", \"FLOURASENT\": \"\", \"METALIC\": \"\", \"EMBOSS\": \"\", \"SPESIAL EMBOSS\": \"\"}'),
(578,17,2,'{\"ITEM\": \"ECO TECH COMFORT\", \"THICKNESS\": \"1.24\", \"COLOR\": \"BLACK (00A)\", \"COLOR WHITE\": 1.14, \"COLOR BLACK\": \"\", \"FLOURASENT\": \"\", \"METALIC\": \"\", \"EMBOSS\": \"\", \"SPESIAL EMBOSS\": \"\"}');
/*!40000 ALTER TABLE `buyer_price_sheet_rows` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `color_swatch_recipes`
--

DROP TABLE IF EXISTS `color_swatch_recipes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `color_swatch_recipes` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `factory_key` varchar(80) NOT NULL,
  `customer_id` bigint(20) DEFAULT NULL,
  `buyer_code` varchar(32) NOT NULL,
  `brand_id` bigint(20) DEFAULT NULL,
  `color_code` varchar(64) NOT NULL DEFAULT '',
  `color_name` varchar(255) NOT NULL DEFAULT '',
  `emboss` varchar(255) NOT NULL DEFAULT '',
  `color_standard` varchar(255) DEFAULT NULL,
  `backing` varchar(120) DEFAULT NULL,
  `material_name` varchar(500) NOT NULL DEFAULT '',
  `legacy_urut` varchar(32) DEFAULT NULL,
  `entered_at` date DEFAULT NULL,
  `source_file` varchar(255) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_color_swatch_recipe_key` (`factory_key`,`buyer_code`,`color_code`,`material_name`,`emboss`) USING HASH,
  KEY `brand_id` (`brand_id`),
  KEY `customer_id` (`customer_id`),
  KEY `ix_color_swatch_factory_key` (`factory_key`),
  KEY `ix_color_swatch_buyer_code` (`buyer_code`),
  KEY `ix_color_swatch_material_name` (`material_name`(191)),
  KEY `ix_color_swatch_color_code` (`color_code`),
  CONSTRAINT `color_swatch_recipes_ibfk_1` FOREIGN KEY (`brand_id`) REFERENCES `brands` (`id`) ON DELETE SET NULL,
  CONSTRAINT `color_swatch_recipes_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=3553 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `color_swatch_recipes`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `color_swatch_recipes` WRITE;
/*!40000 ALTER TABLE `color_swatch_recipes` DISABLE KEYS */;
INSERT INTO `color_swatch_recipes` VALUES
(1001,'NIKOMAS',17,'ADIDAS',3,'ADBD','METAL GREY','DE-73','SCOTDIC','WHITE','PU COATED LEATHER','A589','2019-01-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1002,'PANARUB',19,'ADIDAS',3,'ADBK','DASH GREEB','DE-7','FOLLOW SAMPLE','WHITE','PU COATED LEATHER','E079','2019-03-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1003,'PANARUB',19,'ADIDAS',3,'ADAU','GLORY PINK','DE-7','FOLLOW SAMPLE','PINK','PU COATED LEATHER','E080','2019-03-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1004,'NIKOMAS',17,'ADIDAS',3,'ACE3','ACTIVE MAROON','AR-191','SCOTDIC','RED','PU COATED LEATHER','A591','2019-03-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1005,'PARKLAND',20,'REEBOK',NULL,'002A','BRIGHT YELLOW','CPUG','SCOTDIC','YELLOW','BABY SOFT PANTENT LEATHER','A302','2019-04-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1006,'PARKLAND',20,'REEBOK',NULL,'A7AF','ELEKTRO PINK','CPUG','SCOTDIC','PINK','BABY SOFT PANTENT LEATHER','A303','2019-04-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1007,'PARKLAND',20,'REEBOK',NULL,'A5YS','SOLID TEAL','CPUG','SCOTDIC','3GU','BABY SOFT PANTENT LEATHER','A304','2019-04-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1008,'PARKLAND',20,'REEBOK',NULL,'A1R6','TREK GREY','DE-43','SCOTDIC','L.BROWN','ACTION LEATHER','A305','2019-04-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1009,'PARKLAND',20,'REEBOK',NULL,'AD23','HERITAGE NAVY','DE-43','SCOTDIC','BLACK','ACTION LEATHER','A306','2019-04-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1010,'PARKLAND',20,'REEBOK',NULL,'AD10','EGGPLANT','R-8','NB CSI','PURPLE','ACTION LEATHER','A307','2019-04-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1011,'NIKOMAS',17,'ADIDAS',3,'ABZC','TRUE BLUE S19','DE-7','SCOTDIC','BLUE','SOFT PU COATED','A592','2019-04-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1012,'PARKLAND',20,'REEBOK',NULL,'A6DG','FLINT GREY METALLIC','DE-23','SCOTDIC','WHITE','ACTION LEATHER','A308','2019-04-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1013,'PARKLAND',20,'REEBOK',NULL,'ADH6','GREEN SLATE','R-8','SCOTDIC','4AU','ACTION LEATHER','A309','2019-04-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1014,'PARKLAND 1',20,'REEBOK',NULL,'ADWY','GLASS PINK','DE-23','SCOTDIC','WHITE','ACTION LEATHER','A313','2019-04-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1015,'FENGTAY',7,'NIKE',1,'74F','WHEAT','AR-169','TMFT0062019051401','2CT','VIRGIN HYDRO PU','A120','2019-05-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1016,'FENGTAY',7,'NIKE',1,'74F','WHEAT','UM-14','TMFT0062019051402','2CT','VIRGIN HYDRO PU','A121','2019-05-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1017,'NIKOMAS',17,'ADIDAS',3,'077A','CHALK WHITE','DE-7/AR-64','SCOTDIC','WHITE','SOFT PU COATED LEATHER','A593','2019-05-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1018,'NIKOMAS',17,'ADIDAS',3,'ADAJ','DOVE GREY','DE-7/AR-64','SCOTDIC','GREY','SOFT PU COATED LEATHER','A594','2019-05-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1019,'DEANSHOES',6,'UA',5,'449','AMERICAN BLUE','R-231','CSI UA','44Z','ACTION LEATHER','A123','2019-05-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1020,'DEANSHOES',6,'UA',5,'600','RED','R-231 /DE-43','FOLLOW CSI UA','RED','ACTION PU COATED LEATHER','A124','2026-01-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1021,'DEANSHOES',6,'UA',5,'400','ROYAL','R-231','CSI UA','44Z','ACTION LEATHER','A125','2019-05-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1022,'NIKOMAS',17,'ADIDAS',3,'ADMT','NOBLE PURPLE','DE-7','SCOTDIC','PURPLE','PU COATED LEATHER','A595','2019-05-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1023,'NIKOMAS',17,'ADIDAS',3,'ADMS','GLORY GREY','DE-7','SCOTDIC','01V','PU COATED LEATHER','A596','2019-05-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1024,'NIKOMAS',17,'ADIDAS',3,'ADBK','DASH GREEN','CPUG','SCOTDIC','WHITE','BABY SOFT PATENT LEATHER','A597','2019-06-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1025,'NIKOMAS',17,'ADIDAS',3,'AA2V','GREY FIVE','AR-191','SCOTDIC','GREY','PU COATED LEATHER','A598','2019-06-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1026,'PARKLAND 1',20,'ADIDAS',3,'080A','SILVER MET','CPUG','SCOTDIC','WHITE','M FLAT','A314','2019-07-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1027,'PARKLAND 1',20,'ADIDAS',3,'AAY8','TRACE MARRON','CPUG','SCOTDIC','PINK','M FLAT','A315','2019-07-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1028,'NIKOMAS',17,'ADIDAS',3,'ADLA','PINK TINT','DE-7','SCOTDIC','PINK','PU COATED LEATHER','A599','2019-07-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1029,'HORNMING',13,'PUMA',NULL,'18-1945TCX','18-1945TCX','R-184','PANTONE','RED','SOFT PU COATED','A129','2019-07-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1030,'NIKOMAS',17,'ADIDAS',3,'046A','BOLD BLUE','DE-7','SCOTDIC','44Z','SOFT PU COATED LEATHER','A600','2019-10-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1031,'NIKOMAS',17,'ADIDAS',3,'081A','GOLD MET','R-8','SCOTDIC','2CT','SOFT PU COATED LEATHER','A601','2019-10-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1032,'NIKOMAS',17,'ADIDAS',3,'AD8R','TEAM ROYAL BLUE','R-8','SCOTDIC','44Z','SOFT PU COATED LEATHER','A602','2019-10-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1033,'NIKOMAS',17,'ADIDAS',3,'AA2U','GREY FOUR','R-8','FOLLOW FMCA','GREY','SOFT PU COATED LEATHER','A603','2019-10-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1034,'NIKOMAS',17,'ADIDAS',3,'ADB7','SKY TINT','R-8','SCOTDIC','WHITE','SOFT PU COATED LEATHER','A604','2019-10-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1035,'NIKOMAS',17,'ADIDAS',3,'ADWE','CREW NAVY','R-8','SCOTDIC','4MD','SOFT PU COATED LEATHER','A605','2019-11-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1036,'NIKOMAS',17,'ADIDAS',3,'A7M6','SEMI NIGHT FLASH','DE-7','SCOTDIC','58U','SOFT PU COATED','A606','2019-11-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1037,'NIKOMAS',17,'ADIDAS',3,'A7MX','DUST PURPLE','DE-7','SCOTDIC','WHITE','SOFT PU COATED','A607','2019-11-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1038,'NIKOMAS',17,'ADIDAS',3,'43F0','COLLEGIATE PURPLE','R-8','SCOTDIC','58U','SOFT PU COATED LEATHER','A609','2019-11-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1039,'NIKOMAS',17,'ADIDAS',3,'ADYY','VIVID RED','R-8','SCOTDIC','RED','SOFT PU COATED','A610','2019-11-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1040,'METRO NB',16,'NB',4,'NB-S17-3138','NB RED PAPPER','AR-33','NB CSI','RED','HYDRO PU COATED LEATHER','M027','2019-11-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1041,'NIKOMAS',17,'ADIDAS',3,'ADVW','ACID ORANGE','DE-7','SCOTDIC','2CT','SOFT PU COATED LEATHER','A611','2019-11-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1042,'NIKOMAS',17,'ADIDAS',3,'A0TR','MATTE SILVER','DE-7','SCOTDIC','WHITE','SOFT PU COATED LEATHER','A612','2019-11-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1043,'NIKOMAS',17,'ADIDAS',3,'ADW8','HALO SILVER','AR-169','SCOTDIC','01V','PU COATED LEATHER','A613','2019-11-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1044,'NIKOMAS',17,'ADIDAS',3,'08S1','OFF WHITE','DE-7','SCOTDIC','WHITE','SOFT PU COATED LEATHER','A614','2019-11-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1045,'PANARUB',19,'ADIDAS',3,'ADWS','SCREAMING PINK','DE-7','SCOTDIC','6DX','PU COATED LEATHER','E081','2019-11-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1046,'PANARUB',19,'ADIDAS',3,'A0TB','BRIGHT RED','CPUG','SCOTDIC','RED','BABY SOFT PATENT LEATHER','E082','2019-11-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1047,'NIKOMAS',17,'ADIDAS',3,'A2JM','CLEAR PINK','DE-7','SCOTDIC','PINK','SOFT PU COATED LEATHER','A616','2019-11-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1048,'NIKOMAS',17,'ADIDAS',3,'A62L','SUB GREEN','R-8','SCOTDIC','3GU','SOFT PU COATED LEATHER','A617','2019-11-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1049,'NIKOMAS',17,'ADIDAS',3,'ADWD','CREW BLUE','DE-7','SCOTDIC','4MD','SOFT PU COATED LEATHER','A618','2019-11-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1050,'PANARUB',19,'ADIDAS',3,'ADVY','HAZY ORANGE','R-101','SCOTDIC','2CT','SOFT PU COATED','E083','2019-11-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1051,'NIKOMAS',17,'ADIDAS',3,'ABWQ','FOOTBALL BLUE','CPUG','SCOTDIC','44Z','BABY SOFT','A620','2019-12-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1052,'NIKOMAS',17,'ADIDAS',3,'A1NR','CHERRY MET','AR-191/DE-7','SCOTDIC','6DX','SOFT PU COATED','A621','2019-12-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1053,'NIKOMAS',17,'ADIDAS',3,'ADWG','HAZY GREEN','DE-7','SCOTDIC','4AU','PU COATED','A622','2019-12-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1054,'PANARUB',19,'ADIDAS',3,'A84A','RICH MAUVE','DE-7','SCOTDIC','PURPLE','PU COATED','E084','2019-12-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1055,'PANARUB',19,'ADIDAS',3,'ADVZ','CREW ORANGE','DE-7','SCOTDIC','WHITE','SOFT PU COATED','E085','2019-12-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1056,'PANARUB',19,'ADIDAS',3,'ADYW','ACID MINT','DE-7','SCOTDIC','WHITE','PU COATED','E086','2019-12-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1057,'PANARUB',19,'ADIDAS',3,'ADVV','HALO AMBER','DE-7','SCOTDIC','WHITE','PU COATED','E087','2019-12-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1058,'PANARUB',19,'ADIDAS',3,'ADW1','SCREAMING ORANGE','DE-7','SCOTDIC','80S','SOFT PU COATED','E088','2019-12-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1059,'PARKLAND 2',21,'NB',4,'NB-S21-7834','OCEAN GREY','DE-107','NB CSI','LT BLUE','HYDRO PU COATED LEATHER','A326','2019-12-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1060,'PARKLAND 2',21,'NB',4,'NB0500422','ECLIPSE','DE-107','NB CSI','BLACK','HYDRO PU COATED LEATHER','A327','2019-12-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1061,'PANARUB',19,'ADIDAS',3,'ADY4','HAZY EMERALD','DE-73','SCOTDIC','LIGHT BLUE','SOFT PU COATED LEATHER','E089','2019-12-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1062,'PANARUB',19,'ADIDAS',3,'A0TP','CREAM WHITE','DE-7','NEW FMCA PANARUB','WHITE','PU COATED LEATHER','A181',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59','2026-05-19 03:12:22'),
(1063,'PANARUB',19,'ADIDAS',3,'ADYX','HAZY SKY','DE-7','SCOTDIC','L.BLUE','PU COATED LEATHER','E091','2019-12-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1064,'PANARUB',19,'ADIDAS',3,'ABZK','HI RES YELLOW','DE-7','SCOTDIC','71R','PU COATED LEATHER','E092','2019-12-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1065,'NIKOMAS',17,'ADIDAS',3,'ADWC','BLUE OXIDE','DE-7','SCOTDIC','LT BLUE','SOFT PU COATED','A623','2019-12-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1066,'PANARUB',19,'ADIDAS',3,'ADW3','WILD SEPIA','DE-7','SCOTDIC','80S','PU COATED LEATHER','A093','2019-12-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1067,'PANARUB',19,'ADIDAS',3,'AAXY','CLEAR MINT','DE-7','SCOTDIC','4AU','PU COATED LEATHER','A094','2019-12-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1068,'PARKLAND 2',21,'NB',4,'NB0506276','OUTER SPACE','R-51','NB CSI','BLACK','SOFT ACTION LEATHER','A328','2020-01-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1069,'CHANGSHIN',4,'NIKE',1,'65N','UNIVERSITY RED','AR-138','TMCS0052020010301','RED','VIRGIN HYDRO PU','A111','2020-01-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1070,'CHANGSHIN',3,'NIKE',1,'01V','WOLF GREY','AR-144','FOLLOW SAMPLE','WHITE','VIRGIN HYDRO PU','A113','2020-01-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:11:59',NULL),
(1071,'NIKOMAS IY',18,'NIKE',1,'65N','UNIVERSITY RED','AR-148','TMNS0202020010301','WHITE','VIRGIN HYDRO PU','A831','2020-01-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1072,'PCN G8',59,'NIKE',1,'4EV','GAME ROYAL','R-8','FOLLOW SAMPLE','44Z','VIRGIN HYDRO PU','A850','2020-03-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00','2026-05-19 03:12:00'),
(1073,'POUYUEN',24,'NIKE',1,'44B','MIDNIGHT NAVY','AR-93','TMPY0282020010901','BLACK','VIRGIN HYDRO PU','A833','2020-01-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1074,'POUYUEN',18,'NIKE',1,'04Z','PURE PLATINUM','AR-144','TMNS0202020011501','WHITE','VIRGIN HYDRO PU','A834','2020-01-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1075,'FENGTAY',8,'NIKE',1,'04Z','PURE PLATINUM','R-8','TMFT0072020011501','WHITE','VIRGIN HYDRO PU','A167','2020-01-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1076,'FENGTAY',8,'NIKE',1,'4NP','HYPER ROYAL','R-8','TMFT0072020011502','44Z','VIRGIN HYDRO PU','A168','2020-01-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1077,'FENGTAY',8,'NIKE',1,'4QQ','WORLD INDIGO','DE-90','TMFT0072020011201','WHITE','VIRGIN HYDRO PU','A169','2020-01-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1078,'FENGTAY',7,'NIKE',1,'0AL','LT SMOKE GREY','UM-11','TMFT0062020012801','01V','VIRGIN HYDRO PU','A170','2020-01-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1079,'NIKOMAS IY',18,'NIKE',1,'6HR','FLASH CRIMSON','AR-138','TSNS0202020012801','RED','VIRGIN HYDRO PU','A835','2020-01-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1080,'KMK',15,'NIKE',1,'49W','GLACIER ICE','AR-107','TMKM0012020012401','4AU','VIRGIN HYDRO PU','A171','2020-01-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1081,'CHANGSHIN',4,'NIKE',1,'0AE','VAST GREY','UM-34','TMCS0052020012201','WHITE','VIRGIN HYDRO PU','A114','2020-01-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1082,'SHOETOWN',28,'NIKE',1,'6FS','PINK SICLE','AR-121','TMSL0432020012901','50Q','VIRGIN HYDRO PU','A836',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1083,'CHANGSHIN',4,'NIKE',1,'0AH','DK SMOKE GREY','AR-20','TMCS0052020012902','BLACK','VIRGIN HYDRO PU','A115','2020-02-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1084,'CHANGSHIN',4,'NIKE',1,'11K','SAIL','AR-161','TMCS0052020012903','WHITE','VIRGIN HYDRO PU','A116','2020-02-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1085,'CHANGSHIN',4,'NIKE',1,'04Z','PURE PLATINUM','AR-144M','TMCS0052020012901','WHITE','VIRGIN HYDRO PU','A117','2020-02-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1086,'CHANGSHIN',3,'NIKE',1,'01V','WOLF GREY','AR-144M','TMCS0042020013101','WHITE','VIRGIN HYDRO PU','A118','2020-02-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1087,'VICTORY',31,'NIKE',1,'43G','VIRGIN HYDRO PU','AR-107','TMVC0052020013001','WHITE','VIRGIN HYDRO PU','A198','2020-02-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1088,'PCN G8',59,'NIKE',1,'06B','COOL GREY','R-131/R-231','FOLLOW SAMPLE','GREY','VIRGIN HYDRO PU','A837','2020-02-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1089,'NIKOMAS IY',18,'NIKE',1,'0AL','LT SMOKE GREY','AR-148','TMNS0202020020501','01V','VIRGIN HYDRO PU','A838','2020-02-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1090,'POUYUEN',24,'NIKE',1,'49W','GLACIER ICE','R-131','TMPY0282020021202','4AU','VIRGIN HYDRO PU','A839','2020-02-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1091,'POUYUEN',24,'NIKE',1,'04Z','PURE PLATINUM','UMT','TMPY0282020021101','WHITE','VIRGIN HYDRO PU','A840','2020-02-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1092,'POUYUEN',24,'NIKE',1,'0BB','PHOTON DUST','UMT','TMPY0282020021102','WHITE','VIRGIN HYDRO PU','A841','2020-02-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1093,'POUYUEN',24,'NIKE',1,'4EV','GAME ROYAL','R-8','TMPY0282020021201','44Z','VIRGIN HYDRO PU','A842','2020-02-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1094,'NIKOMAS IY',18,'NIKE',1,'45B','OBSIDIAN','R-8','TMNS0202020021902','BLACK','VIRGIN HYDRO PU','A843','2020-02-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1095,'NIKOMAS IY',18,'NIKE',1,'45B','OBSIDIAN','AR-169','TMNS0202020021901','BLACK','VIRGIN HYDRO PU','A844','2020-02-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1096,'ADIS',1,'NIKE',1,'20Z','FOSSIL','AR-120','TMAD0022020021801','WHITE','VIRGIN HYDRO PU','A440','2020-02-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1097,'ADIS',1,'NIKE',1,'01X','PHANTOM','DE-73','TSAD0022020020701','WHITE','VIRGIN HYDRO PU','A441','2020-02-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1098,'HORNMING',13,'PUMA',NULL,'14-1907TCX','PINK','DE-7','TSHI0242020022001','WHITE','SOFT PU COATED LEATHER','A151','2020-03-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1099,'FENGTAY',7,'NIKE',1,'00A','BLACK','UM-11','SAMPEL UM 11','BLACK','VIRGIN HYDRO PU','A171','2020-03-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1100,'ADIS',1,'NIKE',1,'45B','OBSIDIAN','DE-90','TMAD0022020020701','BLACK','VIRGIN HYDRO PU','A442','2020-02-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1101,'FENGTAY TW',8,'NIKE',1,'4MR','BLUE ORBIT','R-131','TMFT0072020022501','4JE','VIRGIN HYDRO PU','A172','2020-03-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1102,'KMK',15,'NIKE',1,'44B','MIDNIGHT NAVY','AR-144','TMKM0012020022101','BLACK','VIRGIN HYDRO PU','A172','2020-03-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1103,'NIKOMAS IY',18,'NIKE',1,'07A','SILVER','R-8','TMNS02020022501','WHITE','VIRGIN PU','A845','2020-03-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1104,'SHOETOWN',28,'NIKE',1,'0AL','LT SMOKE GREY','R-53','TMSL0432020050401','01V','VIRGIN HYDRO PU','A866','2020-05-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00','2026-05-19 03:12:00'),
(1105,'PCN G8',59,'NIKE',1,'06B','COOL GREY','CPUG','SAMPLE','BLACK','VIRGIN HYDRO PU','A847','2020-03-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1106,'PCN G8',59,'NIKE',1,'4EV','GAME ROYAL','CPUG','SAMPLE','BLACK','VIRGIN HYDRO PU','A848','2020-03-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1107,'HORNMING',13,'PUMA',NULL,'18-1763TCX','B  RED','AR-196','TMHI0242020030401','RED','HYDRO ECOTECH COMFORT','A152','2020-03-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1108,'HORNMING',13,'PUMA',NULL,'107-31-20','DIGI BLUE','AR-196','TMHI0242020030402','3AW','HYDRO ECOTECH COMFORT','A153','2020-03-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1109,'KMK',15,'NIKE',1,'06L','GHOST','AR-167','TMKM0012020031001','WHITE','VIRGIN HYDRO PU','A173','2020-03-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1110,'NIKOMAS',17,'ADIDAS',3,'ADWA','HALO BLUE','DE-7','SCOTDIC','WHITE','SOFT PU COATED LEATHER','A626','2020-03-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1111,'NIKOMAS',17,'ADIDAS',3,'ADCY','TEAM ORANGE','DE-7/R-8','FMCA','80S','SOFT PU COATED LEATHER','A627','2020-03-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1112,'VICTORY',31,'NIKE',1,'2CQ','VELVET BROWN','R-30','TMVC0052020031301','PURPLE','ECO TECH COMFORT','A199',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1113,'VICTORY',31,'NIKE',1,'33X','VINTAGE GREEN','R-30','TMVC0052020031302','33R','ECO TECH COMFORT','A200',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1114,'NIKOMAS',17,'ADIDAS',3,'34F0','COLLEGIATE ORANGE','DE-7/R-8','SCOTDIC','RED','SOFT PU COATED LEATHER','A628','2020-03-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1115,'CHANGSHIN',3,'NIKE',1,'00M','METALIC PLATINUM','AR-144 SG','TMCS0042020031701','WHITE','VIRGIN HYDRO PU','A119','2020-03-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1116,'CHANGSHIN',3,'NIKE',1,'65N','UNIVERSITY RED','AR-33','TMCS0042020031702','RED','VIRGIN HYDRO PU','A120','2020-03-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1117,'NIKOMAS IY',18,'NIKE',1,'06B','COOL GREY','CPUG','TMNS0202020031801','GREY','VIRGIN HYDRO PU','A857','2020-03-20','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1118,'NIKOMAS IY',18,'NIKE',1,'4EV','GAME ROYAL','CPUG','TSNS0202020032401','44Z','VIRGIN HYDRO PU','A852','2020-03-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00','2026-05-19 03:12:00'),
(1119,'PCN G8',59,'NIKE',1,'0AH','DK SMOKE GREY','AR-93','FOLLOW SAMPLE','BLACK','VIRGIN HYDRO PU','A859','2020-03-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1120,'PCN G8',59,'NIKE',1,'0AL','LT SMOKE GREY','R-8','FOLLOW SAMPLE','01V','VIRGIN HYDRO PU','A860','2020-03-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1121,'PCN G8',59,'NIKE',1,'0AJ','SMOKE GREY','AW-12','FOLLOW SAMPLE','GREY','VIRGIN HYDRO PU','A851','2020-03-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1122,'NIKOMAS',17,'ADIDAS',3,'31F0','POWER RED','DE-7','SCOTDIC','RED','SOFT PU COATED LEATHER','A629','2020-03-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1123,'NIKOMAS',17,'ADIDAS',3,'ADAK','SIGNAL CORAL','R-51','SCOTDIC','RED','SOFT PU COATED LEATHER','A630','2020-03-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1124,'ADIS',1,'NIKE',1,'44B','MIDNIGHT NAVY','DE-73','TMAD0022022111801','BLACK','VIRGIN HYDRO PU','A527','2022-11-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00','2026-05-19 03:12:11'),
(1125,'PCN G8',59,'NIKE',1,'6DL','GYM RED','AR-193','TSPG0212020033101','RED','GENERIC PU COATED LEATHER','A853','2020-04-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1126,'PCN G8',59,'NIKE',1,'33X','VINTAGE','AR-20','TSPG0212020040201','BLACK','VIRGIN HYDRO PU','A854','2020-04-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1127,'PCN G8',59,'NIKE',1,'6KD','DESERT BERRY','R-102','TSPG0212020040202','PINK','VIRGIN HYDRO PU','A855','2020-04-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1128,'NIKOMAS IY',18,'NIKE',1,'01X','PHANTOM','AR-73','TSNS0202020033101','WHITE','VIRGIN HYDRO PU','A856','2020-04-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1129,'PRATAMA',25,'NIKE',1,'10L','PALE IVORY','AR-20','TMPT0122020040601','WHITE','VIRGIN HYDRO PU','A426','2020-04-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1130,'PRATAMA',25,'NIKE',1,'6DL','GYM RED','AR-20','TMPT0122020040603','WHITE','VIRGIN HYDRO PU','A427','2020-04-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1131,'ADIS',1,'NIKE',1,'20Z','FOSSIL','AR-138','TMAD0022021032301','WHITE','VIRGIN HYDRO PU','A476','2021-03-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00','2026-05-19 03:12:07'),
(1132,'KMK',15,'NIKE',1,'44B','MIDNIGHT NAVY','AR-107','TMKM0012020041301/02','BLACK','VIRGIN HYDRO PU','A174','2020-04-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1133,'POUYUEN',24,'NIKE',1,'0AH','DK SMOKE GREY','R-131','TMPY0282020040901','BLACK','VIRGIN HYDRO PU','A861','2020-04-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1134,'KMK',15,'NIKE',1,'46B','ASTRONOMY BLUE','AR-107','TMKM0012020041303','44Z','VIRGIN HYDRO PU','A175','2020-04-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1135,'PCN G8',59,'NIKE',1,'74F','WHEAT','AR-144','TMPG0212020042201','2CT','VIRGIN HYDRO PU','A862','2020-04-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1136,'POUYUEN',24,'NIKE',1,'44B','MIDNIGHT NAVY','AR-126','TSPY0282020041601','BLACK','VIRGIN HYDRO PU','A863','2020-04-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1137,'NIKOMAS',17,'ADIDAS',3,'AAGG','CARBON','DE-126','TMNS0162022030401','BLACK','SOFT PU COATED LEATHER','A717','2022-03-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00','2026-05-19 03:12:10'),
(1138,'PRATAMA',25,'NIKE',1,'7AC','SOLAR FLARE','UM-14/AR-20','TMPT0122020041701/702','WHITE','VIRGIN HYDRO PU','A428','2020-04-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1139,'PRATAMA',25,'NIKE',1,'44B','MIDNIGHT NAVY','R-101','TSPT0122020042801','BLACK','VIRGIN HYDRO PU','A429','2020-04-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1140,'KMK',15,'NIKE',1,'0AL','LT SMOKE GREY','AR-107','TMKM0012020042401','WHITE','VIRGIN HYDRO PU','A176','2020-04-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1141,'NIKOMAS IY',18,'NIKE',1,'7AS','SPEED YELLOW','DE-7','TMNS0202020042401','YELLOW','FP VIRGIN PU','A864','2020-04-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1142,'CHANGSHIN',3,'NIKE',1,'74F','WHEAT','AR-144','TSCS0042020042301','2CT','ECO TECH/HYDRO','A121','2020-04-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1143,'PRATAMA',26,'NIKE',1,'0AV','OFF NOIR','R-101','TMPT0132020042802','BLACK','VIRGIN HYDRO PU','A430','2020-05-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1144,'PRATAMA',26,'NIKE',1,'0BB','PHOTON DUST','R-101','TMPT0132020042803','WHITE','VIRGIN HYDRO PU','A431','2020-05-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1145,'PRATAMA JX',26,'NIKE',1,'6BU','PINK GLOW','UM-34','TMPT0132020042801','PINK','VIRGIN HYDRO PU','A432','2020-05-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1146,'CHANGSHIN',3,'NIKE',1,'46B','ASTRONOMY BLUE','UM-34','TMCS0042020042801','44Z','VIRGIN HYDRO PU','A122','2020-05-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1147,'CHANGSHIN',3,'NIKE',1,'58A','EGGPLANT','DE-126/R-102','TSCS0042020042801','58U','VIRGIN HYDRO PU','A123','2020-05-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1148,'ADIS',1,'NIKE',1,'45B','OBSIDIAN','R-8','TMAD0022020043001','BLACK','VIRGIN HYDRO PU','A445','2020-05-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1149,'NIKOMAS',17,'ADIDAS',3,'AE6P','AMBIENT','DE-73','SCOTDIC','L.BLUE','SOFT PU COATED LEATHER','A632','2020-05-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1150,'VICTORY',31,'NIKE',1,'2EJ','TAWNY','AR-140','TMVC0052020043001','2CT','HP ECO TECH COMFORT','A201','2020-05-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1151,'FENGTAY',8,'NIKE',1,'6FS','PINKSICLE','DE-90','TMFT0072020050501','PINK','VIRGIN HYDRO PU','A173','2020-05-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1152,'PCN G8',59,'NIKE',1,'44B','MIDNIGHT NAVY','R-8','TMPG0212020050401','BLACK','ECO TECH COMFORT','A865','2020-05-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1153,'FENGTAY',8,'NIKE',1,'4EV','GAME ROYAL','DE-90','TMFT0072020050601','44Z','ECO TECH COMFORT','A174','2020-05-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1154,'PRATAMA JX',26,'NIKE',1,'32C','SCREAM GREEN','DE-14 SM','TMPT0132020050701','71R','VIRGIN PU','A433','2020-05-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1155,'PCN G8',59,'NIKE',1,'04D','LIGHT SILVER','R-8','TMPG0212020051201','WHITE','ECO TECH COMFORT','A867','2020-05-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1156,'HORNMING',13,'NIKE',1,'16-1710TCX','PALE PINKISH GRAY','AR-196','TMHI0242020051201','PINK','HYDRO ECO TECH COMFORT','A154','2020-05-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1157,'NIKOMAS',17,'ADIDAS',3,'AE67','ROSE TONE','CPUG','SCOTDIC','RED','BABY SOFT PATENT LEATHER','A634','2020-05-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1158,'POUYUEN',24,'NIKE',1,'0BB','PHOTON DUST','R-102','TSPY0282020051403','WHITE','VIRGIN HYDRO PU','A868','2020-05-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1159,'POUYUEN',24,'NIKE',1,'0AP','0AP','R-8','TSPY0282020051401','WHITE','VIRGIN HYDRO PU','A869','2020-05-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1160,'POUYUEN',24,'NIKE',1,'4NP','HYPER ROYAL','B-107','TSPY0282020051402','WHITE','VIRGIN HYDRO PU','A870','2020-05-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1161,'SHOETOWN',61,'NIKE',1,'5BQ','CACTUS FLOWER','R-53','TMSL0442020051401','6DX','VIRGIN HYDRO PU','A871','2020-05-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1162,'PCN G8',59,'NIKE',1,'76I','UNIVERSITY GOLD','AR-196','TMPG0212020052001','2CT','VIRGIN HYDRO PU','A872','2020-06-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1163,'NIKOMAS',17,'ADIDAS',3,'AAYD','SHOCK PINK','CPUG','SCOTDIC','6DX','BABY SOFT PATENT LEATHER','A635','2020-06-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1164,'CHANGSHIN',4,'NIKE',1,'74F','WHEAT','AR-144','TMCS0052020051801','2CT','VIRGIN HYDRO PU','A124','2020-06-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1165,'FENGTAY',7,'NIKE',1,'0AK','PARTICLE GREY','AR-175','TMFT0062020051501','GREY','VIRGIN HYDRO PU','A175','2020-06-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1166,'FENGTAY',7,'NIKE',1,'0AH','DK SMOKE GREY','AR-93','TMFT0062020051502','BLACK','VIRGIN HYDRO PU','A176','2020-06-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1167,'FENGTAY',7,'NIKE',1,'6KD','DESERT BERRY','R-102','TMFT0062020051901','PINK','VIRGIN HYDRO PU','A177','2020-06-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1168,'FENGTAY',7,'NIKE',1,'0AK','PARTICLE GREY','UM-18','TMFT0062020051902','GREY','VIRGIN HYDRO PU','A178','2020-06-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1169,'PRATAMA',25,'NIKE',1,'7AC','SOLAR FLARE','UM-14','TMPT0122020052802','WHITE','VIRGIN HYDRO PU','A434','2020-06-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1170,'PRATAMA',25,'NIKE',1,'7AC','SOLAR FLARE','AR-20','TMPT0122020052801','WHITE','VIRGIN HYDRO PU','A435','2020-06-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1171,'NIKOMAS',17,'ADIDAS',3,'A9NF','LINEN GREEN','DE-7','SCOTDIC','WHITE','SOFT PU COATED LEATHER','A636','2020-06-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1172,'CHANGSHIN',4,'NIKE',1,'0AV','OFF NOIR','AR-138','TMCS0052020060301','BLACK','VIRGIN HYDRO PU','A125','2020-06-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1173,'FENGTAY',8,'NIKE',1,'45B','OBSIDIAN','UM-14','TMFT0072020060401','BLACK','VIRGIN HYDRO PU','A179','2020-06-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1174,'FENGTAY',7,'NIKE',1,'6KD','DESSERT BERRY','DE-7','TMFT0062020060401','PINK','VIRGIN HYDRO PU','A180','2020-06-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1175,'FENGTAY',9,'NIKE',1,'45B','OBSIDIAN','AR-169','TMFT0082022090602','BLACK','VIRGIN HYDRO PU','A266','2022-09-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00','2026-05-19 03:12:11'),
(1176,'VICTORY',31,'NIKE',1,'0AI','IRON GREY','AR-140','TMVC0052020060301','GREY','HP ECO TECH COMFORT','A202','2020-06-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1177,'NIKOMAS',17,'ADIDAS',3,'AE63','VICTORY CRIMSON','DE-73','SCOTDIC','BROWN','SOFT PU COATED LEATHER','A637','2020-06-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1178,'VICTORY',31,'NIKE',1,'4LD','BLACKENED BLUE','AR-167','TMVC0052020060401','BLACK','VIRGIN HYDRO PU','A203','2020-06-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1179,'PRATAMA',25,'NIKE',1,'0AK','PARTICULAR GREY','AR-20','TMPT0122020060502','GREY','VIRGIN HYDRO PU','A436','2020-06-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1180,'PRATAMA',25,'NIKE',1,'20Z','FOSSIL','AR-20','TMPT0122020060505','WHITE','VIRGIN HYDRO PU','A437','2020-06-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1181,'NIKOMAS',17,'ADIDAS',3,'AE6S','WONDER WHITE','DE-7','TSNS0162021042701','WHITE','SOFT PU COATED LEATHER','A673','2021-04-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00','2026-05-19 03:12:07'),
(1182,'VICTORY',31,'NIKE',1,'74I','TWINE','AR-107','TMVC0052020061001','2CT','VIRGIN HYDRO PU','A204','2020-06-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1183,'POUYUEN',24,'NIKE',1,'6BU','PINK GLOW','AR-126','TMPY0282020060901','PINK','VIRGIN HYDRO PU','A873','2020-06-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1184,'VICTORY',31,'NIKE',1,'74I','TWINE','AR-169','TMVC0052020061002','2CT','VIRGIN HYDRO PU','A205','2020-06-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1185,'VICTORY',31,'NIKE',1,'65N','UNIVERSITY RED','AR-169','TMVC0052020061003','RED','VIRGIN HYDRO PU','A206','2020-06-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1186,'HORNMING',13,'PUMA',NULL,'19-4045 TCX','BLUE','AR-196','TMHI0242020060801','44Z','HYDRO ECO TECH COMFORT','A155','2020-06-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1187,'NIKOMAS',17,'ADIDAS',3,'669A','NIGHT SKY','DE-7','SCOTDIC','BLACK','SOFT PU COATED LEATHER','A639','2020-06-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1188,'NIKOMAS',17,'ADIDAS',3,'AC37','ACTIVE PURPLE','DE-7','SCOTDIC','PURPLE','SOFT PU COATED LEATHER','A640','2020-06-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1189,'CHANGSHIN',3,'NIKE',1,'6KD','DESSERT BERRY','R-102','TSCS0042020061501','PINK','VIRGIN HYDRO PU','A126','2020-06-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1190,'FENGTAY',8,'NIKE',1,'0AH','DK SMOKE GREY','DE-90','TMFT0072020061601','BLACK','VIRGIN HYDRO PU','A182','2020-06-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1191,'POUYUEN',24,'NIKE',1,'6HD','CRIMSON BLISS','R-131','TSPY0282020061501','PINK','VIRGIN HYDRO PU','A874','2020-06-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1192,'PANARUB',19,'ADIDAS',3,'ADYU','HALLO GREEN','CPUG','SCOTDIC','WHITE','BABY SOFT PATENT LEATHER','A095','2020-06-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1193,'ADIS',1,'NIKE',1,'01B','METALIC SILVER','AR-138','TMAD0022020061201','WHITE','VIRGIN HYDRO PU','A449','2020-06-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1194,'NIKOMAS',17,'ADIDAS',3,'AE6R','HALO MINT F21','DE-73','SCOTDIC','4AU','SOFT PU COATED LEATHER','A641','2020-06-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1195,'CHANGSHIN',3,'NIKE',1,'07G','LIGHT BONE','UM-34','TMCS0042020062201','WHITE','VIRGIN HYDRO PU','A127',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1196,'PCN G8',59,'NIKE',1,'10A','WHITE','CPUG','TMPG0212020062201','WHITE','FP LS PATENT LEATHER','A875','2020-06-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1197,'NIKOMAS IY',18,'NIKE',1,'76I','UNIVERSITY GOLD','AR-196','TMNS0202020062401','2CT','VIRGIN HYDRO PU','A876','2020-06-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1198,'METRO NB',16,'NB',4,'NB-F16-0054','ANGORA','R-53','NB CSI','WHITE','SEMI FULL GRAIN','M028','2020-06-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1199,'PARKLAND 2',21,'NB',4,'NB-F21-1078','DEEP OCEAN GREY','DE-107','NB CSI','BLACK','SOFT PU COATED LEATHER','A330','2020-06-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1200,'FENGTAY',58,'NIKE',1,'44B','MIDNIGHT NAVY','AR-140','TMFT0382020062401','4MD','VIRGIN HYDRO','A183','2020-06-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1201,'SHOETOWN',61,'NIKE',1,'42C','CONCORD','R-8','TMSL0442020070201','44Z','GENERIC PU COATED','A877','2020-06-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1202,'PCN G8',59,'NIKE',1,'4NP','HYPER ROYAL','AR-121','TMPG0212020062901','44Z','GENERIC PU COATED','A878','2020-06-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1203,'PANARUB',19,'ADIDAS',3,'ADQD','GLORY MINT','DE-73','SCOTDIC','34A','PU COATED LEATHER','A096','2020-07-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1204,'HORNMING',13,'PUMA',NULL,'16-1361 TCX','ORANGE','AR-196','TMHI0242020070101','2CT','HYDRO ECO TECH COMFORT','A156','2020-07-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1205,'FENGTAY',58,'NIKE',1,'0AV','OFF NOIR','UM-34','TMFT0382020070201','BLACK','GENERIC PU COATED LEATHER','A184','2020-07-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1206,'PCN G8',59,'NIKE',1,'10A','WHITE','AR-193','TMPG0212020070201','WHITE','GENERIC PU COATED','A879','2020-07-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1207,'PCN G8',59,'NIKE',1,'10A','WHITE','AR-161','TMPG0212020070701','WHITE','GENERIC PU COATED LEATHER','A880','2020-08-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1208,'VICTORY',31,'NIKE',1,'45B','OBSIDIAN','DE-73','MVC0052020082601','BLACK','VIRGIN HYDRO PU','A210','2020-08-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00','2026-05-19 03:12:01'),
(1209,'POUYUEN',24,'NIKE',1,'44B','MIDNIGHT NAVY','R-131','TMPY0282020070801','BLACK','VIRGIN HYDRO PU','A881','2020-07-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1210,'VICTORY',31,'NIKE',1,'7AP','LT ZITRON','AR-107','TMVC0052020070601','YELLOW','VIRGIN HYDRO PU','A208','2020-07-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1211,'PRATAMA',25,'NIKE',1,'6GL','SUNSET PULSE','UM-14','TMPT0122020071503','PINK','VIRGIN HYDRO PU','A449','2020-07-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1212,'PRATAMA JX',26,'NIKE',1,'12J','SUMMIT WHITE','UM-34','TMPT0132020071403','WHITE','VIRGIN HYDRO PU','A450','2020-07-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1213,'PRATAMA JX',26,'NIKE',1,'4NW','LAGOON PULSE','UM-34','TMPT0132020071401','LT BLUE','VIRGIN HYDRO PU','A451','2020-07-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1214,'PRATAMA JX',26,'NIKE',1,'11K','SAIL','UM-34','TMPT0132020071402','WHITE','VIRGIN HYDRO PU','A452','2020-07-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1215,'PRATAMA',25,'NIKE',1,'51J','DARK RAISIN','AR-20','TMPT0122020071502','PURPLE','VIRGIN HYDRO PU','A453','2020-07-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1216,'PRATAMA',25,'NIKE',1,'0AP','PLATINUM TINT','AR-20','TMPT0122020071501','WHITE','VIRGIN HYDRO PU','A454','2020-07-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1217,'FENGTAY TW',58,'NIKE',1,'65N','UNIVERSITY RED','UM-34 SM','TSFT0382020071501','RED','GENERIC PU COATED LEATHER','A185','2020-07-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1218,'PANARUB',19,'ADIDAS',3,'AA2R','GREY ONE','DE-73','TSPA0202020100902','WHITE','PU COATED LEATHER','A102','2020-10-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00','2026-05-19 03:12:01'),
(1219,'PANARUB',19,'ADIDAS',3,'ADWS','SCREAMING PINK','DE-73','TSPA0202020071601','6DX','SOFT PU COATED LEATHER','A098','2020-07-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1220,'POUYUEN',24,'NIKE',1,'6DX','FIREBERRY FLOURESCENT','R-131','TMPY0282022121601','RED','GENERIC PU COATED','A1073','2022-12-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00','2026-05-19 03:12:11'),
(1221,'FENGTAY',7,'NIKE',1,'4LZ','LIGHT ARMORY BLUE','EV130TPD','TMFT0062020072101','L.BLUE','VIRGIN HYDRO PU','A186','2020-07-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1222,'CHANGSHIN',4,'NIKE',1,'10J','LT OREWOOD BROWN','UM-34','TMCS0052020071701','WHITE','VIRGIN HYDRO PU','A129','2020-07-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1223,'ADIS',1,'NIKE',1,'04Z','LT OREWOOD BROWN','AR-33','TSAD0022020072101','WHITE','VIRGIN HYDRO PU','A451','2020-07-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1224,'PRATAMA',26,'NIKE',1,'85Y','SITRON PULSE','UM-34','TMPT0132020072201','YELLOW','VIRGIN HYDRO PU','A455','2020-07-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1225,'FENGTAY (EAST)',8,'NIKE',1,'0AL','LT SMOKEY GREY','R-8','TMFT0072020072201','WHITE','VIRGIN HYDRO PU','A187','2020-07-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1226,'NIKOMAS IY',18,'NIKE',1,'6CD','BRIGHT CRIMSON','EV130TPD','TMNS0202020072301','RED','VIRGIN HYDRO PU','A883','2020-07-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1227,'ADIS',1,'NIKE',1,'62C','CHAMPAGNE','R-8','TMAD0022020072401','PINK','VIRGIN HYDRO PU','A452','2020-07-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1228,'NIKOMAS',17,'ADIDAS',3,'A9MS','EASY GREEN','EV130TPD','TSNS0162020072403','WHITE','SOFT PU COATED LEATHER','A645','2020-07-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1229,'NIKOMAS',17,'ADIDAS',3,'077A','CHALK WHITE','EV130TPD','TSNS0162020072402','WHITE','SOFT PU COATED LEATHER','A646','2020-07-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1230,'NIKOMAS',17,'ADIDAS',3,'A8KJ','SEMI PINK GLOW','EV130TPD','TSNS0162020072404','WHITE','SOFT PU COATED LEATHER','A647','2020-07-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1231,'NIKOMAS',17,'ADIDAS',3,'002A','BRIGHT YELLOW','EV130TPD','TSNS0162020072401','WHITE','SOFT PU COATED LEATHER','A648','2020-07-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1232,'POUYUEN',24,'NIKE',1,'0AJ','SMOKE GREY','R-131','TMPY0282020073001','GRAY','VIRGIN HYDRO PU','A885','2020-08-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1233,'NIKOMAS IY',18,'NIKE',1,'0AN','GREY FOG','DE-43','TMNS0202020072801','0IV','VIRGIN PU','A884','2020-08-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1234,'NIKOMAS',17,'ADIDAS',3,'A0TF','LIGHT PURPLE','DE-7','SCOTDIC','49D','SOFT PU COATED LEATHER','A649','2020-08-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1235,'FENGTAY (EAST)',8,'NIKE',1,'64M','VARSITY RED','R-231','TMFT0072020080301','RED','VIRGIN HYDRO PU','A188','2020-08-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1236,'FENGTAY TW',58,'NIKE',1,'4KY','THUNDER BLUE','DE-90','TSFT0382020080601','BLACK','PM GENERIC PU COATED LEATHER','A189','2020-08-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1237,'SHOETOWN CINA',61,'NIKE',1,'3HS','TROPICAL TWIST','AR-121','TSSL0442020081001','4AU','PM GENERIC PU COATED LEATHER','A886','2020-08-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1238,'METRO NB',16,'NB',4,'NB1200216','SEA SALT','R-51','TMMP0332020080501','WHITE','SOFT PU COATED LEATHER','M029','2020-08-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:00',NULL),
(1239,'VICTORY',31,'NIKE',1,'0AL','LT SMOKE GREY','R-8','TMVC0052020080601','WHITE','VIRGIN HYDRO PU','A209','2020-10-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1240,'PRATAMA',25,'NIKE',1,'4ME','RACER BLUE','AR-20','TMPT0122020081001','WHITE','VIRGIN HYDRO PU','A456','2020-08-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1241,'PRATAMA',25,'NIKE',1,'11K','SAIL','AR-128','TMPT0122020081101','WHITE','VIRGIN HYDRO PU','A457','2020-08-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1242,'PRATAMA',25,'NIKE',1,'04Z','PURE PLATINUM','UM-14','SPT0122020082701','WHITE','VIRGIN HYDRO PU','A463','2020-08-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01','2026-05-19 03:12:01'),
(1243,'PRATAMA',25,'NIKE',1,'62C','CHAMPAGNE','AR-20','TMPT0122020081003','PINK','VIRGIN HYDRO PU','A459','2020-08-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1244,'PCN G8',59,'NIKE',1,'4EV','GAME ROYAL','R-131','SPG0212020081101','44Z','VIRGIN HYDRO PU','A887','2020-08-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1245,'NIKOMAS IY',18,'NIKE',1,'3NB','TWILIGHT MAISH','DE-90','MNS0202020081201','3MR','ECO TECH COMFORT LEATHER','A888','2020-08-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1246,'PRATAMA',25,'NIKE',1,'65N','UNIVERSITY RED','AR-20','MPT0132020081202','RED','VIRGIN HYDRO PU','A460','2020-08-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1247,'PRATAMA',25,'NIKE',1,'11K','SAIL','AR-196','MPT0132020081201','WHITE','VIRGIN HYDRO PU','A461','2020-08-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1248,'SHOETOWN CINA',61,'NIKE',1,'3KC','GREEN GLOW','AR-161','SSL0442020081302','4AU','PM GENERIC PU','A889','2020-08-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1249,'SHOETOWN CINA',61,'NIKE',1,'71R','VOLT','AR-161','SSL0442020081301','71R','PM GENERIC PU COATED LEATHER','A890','2020-08-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1250,'NIKOMAS IY',18,'NIKE',1,'4NP','HYPER ROYAL','AR-121','MNS0202020081301','44Z','PM GENERIC PU COATED','A891','2020-08-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1251,'FENGTAY',7,'NIKE',1,'05Y','DESERT SAND','UM-34 SM','MFT0072020081301','WHITE','PM GENERIC PU COATED LEATHER','A190','2020-08-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1252,'CHANGSHIN',3,'NIKE',1,'3CN','CYBER','UM-34','MCS0042020081302','71R','VIRGIN HYDRO PU','A130','2020-08-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1253,'CHANGSHIN',3,'NIKE',1,'05Q','FOOTBALL GREY','UM-34','MCS0042020081301','WHITE','VIRGIN HYDRO PU','A131','2020-08-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1254,'ADIS',1,'NIKE',1,'0AN','GREY FOG','R-8','MAD0022020081301','WHITE','VIRGIN HYDRO PU','A453','2020-08-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1255,'ADIS',1,'NIKE',1,'06B','COOL GREY','DE-73','TMAD0022020111002','GREY','VIRGIN HYDRO PU','A466','2020-11-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01','2026-05-19 03:12:01'),
(1256,'PRATAMA',25,'NIKE',1,'86L','CRIMSON TINT','UMT','SPT0122020081801','WHITE','VIRGIN HYDRO PU','A462','2020-08-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1257,'POUYUEN',24,'NIKE',1,'00A','BLACK ANODIZED','AR-33','SPY0282020082401','BLACK','VIRGIN HYDRO PU','A893','2020-08-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1258,'CHANGSHIN',3,'NIKE',1,'45B','OBSIDIAN','AR-161','MCS0052020082201','BLACK','PM GENERIC PU COATED LEATHER','A132','2020-08-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1259,'CHANGSHIN',3,'NIKE',1,'05Q','FOOTBAL GREY','AR-138','MCS0052020082602','WHITE','VIRGIN HYDRO PU','A133','2020-08-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1260,'CHANGSHIN',3,'NIKE',1,'4PA','BLUE VOLD','DE-7 SM','MCS0052020082601','BLACK','PM GENERIC PU COATED LEATHER','A136','2020-08-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1261,'HORNMING',13,'PUMA',NULL,'18-4005TCX','GRAY','AR-196','TMHI0242020082501','BLACK','HYDRO ECO TECH COMFORT','A157','2020-08-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1262,'HORNMING',13,'PUMA',NULL,'11-0623TCX','YELLOW','AR-196','TMHI0242020082502','YELLOW','HYDRO ECO TECH COMFORT','A158','2020-08-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1263,'PANARUB',19,'ADIDAS',3,'806A','VICTORY RED','DE-73','SCOTDIC','RED','PU COATED LEATHER','A099','2020-08-31','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1264,'POUYUEN',24,'NIKE',1,'00A','BLACK','R-231','MPY0282020082801','BLACK','VIRGIN PU','A894','2020-08-31','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1265,'FENGTAY (EAST)',8,'NIKE',1,'44B','MIDNIGHT NAVY','AR-140 M','MFT0072020090102','4MD','VIRIGIN HYDRO PU','A191','2020-09-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1266,'FENGTAY (EAST)',8,'NIKE',1,'65N','UNIVERSITY RED','UM-34 SM','MFT0072020090101','RED','PM GENERIC PU COATED LEATHER','A192','2020-09-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1267,'PRATAMA JX',26,'NIKE',1,'86L','CRIMSON TINT','UMT','TMPT0132020110301','WHITE','VIRGIN HYDRO PU','A465','2020-11-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01','2026-05-19 03:12:01'),
(1268,'POUYUEN',24,'NIKE',1,'4PA','BLUE VOID','DE-7','MPY0282020090201','BLACK','GENERIC PU COATED LEATHER','A895','2020-09-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1269,'NIKOMAS',17,'ADIDAS',3,'A61T','CLEAR BROWN','DE-73','SCOTDIC','WHITE','HYDRO SOFT ACTION LEATHER','A650','2020-09-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1270,'ADIS',1,'NIKE',1,'01B','METALIC SILVER','UM-18','MAD0022020090701','WHITE','GENERIC PU COATED LEATHER','A455','2020-09-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1271,'SHOETOWN CINA',61,'NIKE',1,'51L','COURT PURPLE','AR-185','SSL0442020090901','PURPLE','GENERIC PU COATED LEATHER','A896','2020-09-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1272,'NIKOMAS',17,'ADIDAS',3,'AE6N','AMBIENT BLUSH','DE-73','SCOTDIC','80S','HYDRO SOFT PU COATED LEATHER','A651','2020-09-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1273,'NIKOMAS',17,'ADIDAS',3,'AE68','VIOLET TONE','DE-73','SCOTDIC','WHITE','HYDRO SOFT PU COATED LEATHER','A652','2020-09-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1274,'KMK',15,'NIKE',1,'0AN','GREY FOG','AR-181','TMKM0012020092201','WHITE','GENERIC PU COATED LEATHER','A183','2020-09-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1275,'FENGTAY TW',58,'NIKE',1,'0AV','OFF NOIR','UM-34 SM','TSFT0382020092401','BLACK','PM GENERIC PU COATED LEATHER','A193','2020-09-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1276,'PANARUB',19,'ADIDAS',3,'ADWS','SCREAMING PINK','DE-73','TSPA0202020092901','6DX','PU COATED LEATHER','A100','2020-09-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1277,'FENGTAY (EAST)',8,'NIKE',1,'4KY','THUNDER BLUE','DE-90','TMFT0072020093001','BLACK','PM GENERIC PU COATED LEATHER','A194','2020-09-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1278,'FENGTAY (EAST)',8,'NIKE',1,'05Q','FOOTBALL GREY','R-8','TMFT0072020092901','WHITE','GENERIC PU COATED LEATHER','A195','2020-09-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1279,'PANARUB',19,'ADIDAS',3,'AD14','GLOW PINK','DE-73','TMPA0202020102401','PINK','PU COATED LEATHER','A105','2020-10-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01','2026-05-19 03:12:01'),
(1280,'POUYUEN',24,'NIKE',1,'4EV','GAME ROYAL','R-131','TSPY0282020111101','44Z','VIRGIN HYDRO PU','A913','2020-11-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01','2026-05-19 03:12:01'),
(1281,'SHOETOWN CINA',61,'NIKE',1,'3KC','GREEN GLOW','AR-161','TSSL0442020100202','WHITE','GENERIC PU COATED','A898','2020-10-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1282,'TAEKWANG',30,'NIKE',1,'06T','STADIUM GREY','DE-90','TMTK0272020100603','GREY','ECOTECH COMFORT','A091','2020-10-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1283,'FENGTAY (EAST)',8,'NIKE',1,'44B','MIDNIGHT NAVY','R-8 M','TMFT0072020100801','BLACK','PM GENERIC PU COATED LEATHER','A196','2020-10-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1284,'CHANGSHIN',4,'NIKE',1,'11K','SAIL','AR-196 M','TMCS0052020100901','WHITE','GENERIC PU COATED','A137','2020-10-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1285,'TAEKWANG',30,'NIKE',1,'0AL','LT SMOKE GREY','AR-144','TMTK0272020100901','WHITE','VIRGIN HYDRO PU','A092','2020-10-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1286,'CHANGSHIN',4,'NIKE',1,'0AL','LT SMOKE GREY','AR-161 M','TMCS0052020100903','WHITE','GENERIC PU COATED','A138','2020-10-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1287,'CHANGSHIN',4,'NIKE',1,'0AP','PLATINUM TINT','AR-138 M','TMCS0052020100902','WHITE','VIRGIN HYDRO PU','A139','2020-10-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1288,'PANARUB',19,'ADIDAS',3,'ADVZ','CREW ORANGE','DE-73','TSPA0202020100901','2CT','PU COATED LEATHER','A103','2020-10-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1289,'TAEKWANG',30,'NIKE',1,'53C','ICED LILAC','AR-144','TMTK0272020101201','PINK','VIRGIN HYDRO PU','A093','2020-10-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1290,'ADIS',1,'NIKE',1,'6JE','WASHED CORAL','AR-167','TMAD0022020101201','WHITE','VIRGIN HYDRO PU','A456','2020-10-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1291,'PARKLAND 2',21,'NB',4,'NB-S19-2796','DARK NEPTUNE','AR-194','NB CSI','3AW','HYDRO PRO ACTION LEATHER','A342','2020-10-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1292,'PARKLAND 2',21,'NB',4,'NB1100887','STEEL','DE-7','NB CSI','GREY','HYDRO PRO ACTION LEATHER','A343','2020-10-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1293,'FENGTAY (EAST)',8,'NIKE',1,'76I','UNIVERSITY GOLD','R-8','TSFT0072020101501','YELLOW','PM GENERIC PU COATED LEATHER','A197','2020-10-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1294,'VICTORY',31,'NIKE',1,'44B','MIDNIGHT NAVY','AR-64','TSVC0052020101901','BLACK','ECO TECH COMFORT','A211','2020-10-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1295,'TAEKWANG',30,'NIKE',1,'0AI','IRON GREY','AR-144','TMTK0272020101901','BLACK','VIRGIN HYDRO PU','A094',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1296,'ADIS',1,'NIKE',1,'01B','METALLIC SILVER','AR-107','TMAD0022022062701','WHITE','VIRGIN HYDRO PU','A524','2022-07-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01','2026-05-19 03:12:10'),
(1297,'NIKOMAS',17,'ADIDAS',3,'A8KJ','SEMI PINK GLOW','EV130TPD','FOLLOW FMCA','WHITE','SEMI FULL','A653','2020-10-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1298,'NIKOMAS',17,'ADIDAS',3,'A9MS','EASY GREEN','EV130TPD','FOLLOW FMCA','WHITE','SEMI FULL','A654','2020-10-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1299,'NIKOMAS',17,'ADIDAS',3,'077A','CHALK WHITE','EV130TPD','FOLLOW FMCA','WHITE','SEMI FULL','A655','2020-10-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1300,'NIKOMAS',17,'ADIDAS',3,'A7C6','VIVID MINT','EV130TPD','FOLLOW FMCA','WHITE','SEMI FULL','A656','2020-10-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1301,'NIKOMAS IY',18,'NIKE',1,'04D','LIGHT SILVER','AR-196','TMNS0202020102202','WHITE','VIRGIN HIDRO PU','A899','2020-10-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1302,'NIKOMAS IY',18,'NIKE',1,'6HD','CRIMSON BLISS','R-131','TMNS0202020102201','PINK','VIRGIN HIDRO PU','A900','2020-10-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1303,'TAEKWANG',30,'NIKE',1,'0AN','GREY FOG','AR-144','TMTK0272020102301','01V','VIRGIN HYDRO PU','A095','2020-10-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1304,'PANARUB',19,'ADIDAS',3,'ADW1','SCREAMING ORANGE','DE-73','TMPA0202020102402','WHITE','PU COATED LEATHER','A104','2020-10-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1305,'ADIS',1,'NIKE',1,'6HD','CRIMSON BLISS','DE-73','TMAD0022020102401','80S','VIRGIN HYDRO PU','A459','2020-10-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1306,'PCN G8',59,'NIKE',1,'53G','PURE VIOLET','DE-73','TSPG0212020102701','01V','GENERIC PU COATED LEATHER','A901','2020-10-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1307,'NIKOMAS IY',18,'NIKE',1,'0BB','PHOTON DUST','R-8','TMNS0202020102701','WHITE','VIRGIN PU','A902','2020-10-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1308,'NIKOMAS IY',18,'NIKE',1,'70G','VARSITY MAIZE','DE-73','TMNS0202020102801','YELLOW','GENERIC PU COATED LEATHER','A903','2020-10-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1309,'NIKOMAS IY',18,'NIKE',1,'65N','UNIVERSITY RED','R-8','TMNS0202020102601','RED','VIRGIN PU','A904','2020-10-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1310,'PARKLAND 2',21,'NB',4,'018-68-40','VIBRANT ORANGE','UM-11','NB CSI','WHITE','HYDRO PRO ACTION LEATHER','A344','2020-10-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1311,'CHANGSHIN',4,'NIKE',1,'0AN','GREY FOG','AR-138','TMCS0052020102801','WHITE','VIRGIN HYDRO PU','A140','2020-11-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1312,'CHANGSHIN',3,'NIKE',1,'80K','STARFISH','UM-34','TMCS0042020110303','80S','VIRGIN HYDRO PU','A141','2020-11-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1313,'CHANGSHIN',3,'NIKE',1,'11M','COCONUT MILK','UM-34','TMCS0042020110301','WHITE','VIRGIN HYDRO PU','A142','2020-11-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1314,'VICTORY',31,'NIKE',1,'6CM','VERY BERRY','DE-73','TSVC0052020110301','RED','PM GENERIC PU COATED LEATHER','A212','2020-11-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1315,'SHOETOWN',28,'NIKE',1,'51L','COURT PURPLE','AR-185','TMSL0432020110301','PURPLE','GENERIC PU COATED LEATHER','A905','2020-11-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1316,'KMK',15,'NIKE',1,'52X','LIGHT VIOLET','AR-107','TMKM0012020110201','WHITE','VIRGIN HYDRO PU','A184','2020-11-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1317,'PCN G8',59,'NIKE',1,'00A','BLACK EX-ANODIZED','AR-33','TSPG0212020110401','BLACK','VIRGIN HIDRO PU LEATHER','A906','2020-11-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1318,'NIKOMAS IY',18,'NIKE',1,'4EV','GAME ROYAL','R-131','TMNS0202020110601','44Z','VIRGIN HIDRO PU LEATHER','A907','2020-11-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1319,'HORNMING',13,'PUMA',NULL,'059','WHITE','DE-7','TMHI0242020110401','WHITE','SOFT PU COATED','A159','2020-11-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1320,'ADIS',1,'NIKE',1,'68W','PINK GLAZE','AR-107','TMAD0022020110402','PINK','VIRGIN HYDRO PU','A460','2020-11-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1321,'PANARUB',19,'ADIDAS',3,'AA2T','GREY THREE','DE-73','TMPA0202020110901','GREY','PU COATED LEATHER','A106','2020-11-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1322,'POUYUEN',24,'NIKE',1,'4EV','GAME ROYAL','R-131','TMPY0282020110904','44Z','VIRGIN HIDRO PU LEATHER','A908','2020-11-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1323,'POUYUEN',24,'NIKE',1,'06L','GHOST','DE-107','TMPY0282020110902','WHITE','VIRGIN HIDRO PU LEATHER','A909','2020-11-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1324,'POUYUEN',24,'NIKE',1,'6JB','PINK FOAM','R-131','TMPY0282020110903','PINK','VIRGIN HIDRO PU LEATHER','A910','2020-11-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1325,'POUYUEN',24,'NIKE',1,'0AH','DK SMOKE GREY','R-131','TMPY0282020110901','BLACK','VIRGIN HIDRO PU LEATHER','A911','2020-11-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1326,'CHANGSHIN',4,'NIKE',1,'6GW','BARELY ROSE','R-51 SM','TMCS0052020111203','PINK','PM GENERIC PU COATED LEATHER','A144','2020-11-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1327,'CHANGSHIN',4,'NIKE',1,'04Z','PURE PLATINUM','AR-138','TMCS0052020111201','WHITE','VIRGIN HYDRO','A145','2020-11-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1328,'CHANGSHIN',4,'NIKE',1,'66T','PINK OXFORD','R-51 SM','TMCS0052020111202','PINK','PM GENERIC PU COATED LEATHER','A146','2020-11-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1329,'VICTORY',31,'NIKE',1,'3MC','CLEAR AMERALD','R-231','TSVC0052020111201','3GU','VIRGIN HYDRO PU','A213','2020-11-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1330,'PCN G8',59,'NIKE',1,'11K','SAIL','DE-73 SM','TSPG0212020111001','WHITE','GENERIC PU COATED LEATHER','A912','2020-11-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1331,'NIKOMAS IY',18,'NIKE',1,'6CM','VERY BERRY','DE-73 SM','TMNS0202020111601','RED','GENERIC PU COATED LEATHER','A914','2020-11-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1332,'SHOETOWN',28,'NIKE',1,'3KC','GREEN GLOW','AR-161','TMSL0432020111302','WHITE','GENERIC PU COATED','A915','2020-11-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1333,'SHOETOWN',28,'NIKE',1,'71R','VOLT','AR-161','TMSL0432020111301','71R','GENERIC PU COATED','A916','2020-11-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1334,'ADIS',1,'NIKE',1,'76I','UNIVERSITY GOLD','DE-7','TMAD0022020111801','YELLOW','PM GENERIC PU COATED','A462','2020-11-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1335,'FENGTAY TW',58,'NIKE',1,'6HB','RUSH PINK','AR-107','TSFT0382020120301','6DX','PM GENERIC PU COATED LEATHER','A198','2020-11-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1336,'TAEKWANG',30,'NIKE',1,'45B','OBSIDIAN','R-131','TMTK0272020111801','BLACK','PM GENERIC PU COATED LEATHER','A096','2020-11-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1337,'CHANGSHIN',3,'NIKE',1,'68W','PINK GLAZE','AR-196','TSCS0042020112402','WHITE','PM GENERIC PU COATED LEATHER','A147','2020-11-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1338,'CHANGSHIN',3,'NIKE',1,'44B','MIDNIGHT NAVY','AR-196','TSCS0042020112401','BLACK','PM GENERIC PU COATED LEATHER','A148','2020-11-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1339,'PCN G8',59,'NIKE',1,'0AJ','SMOKE GREY','AR-140','TSPG0212020112301','GREY','ECO TECH COMFORT','A917','2020-11-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1340,'ADIS',1,'NIKE',1,'07G','LIGHT BONE','DE-73','TMAD0022020112001','WHITE','VIRGIN HYDRO PU','A463','2020-11-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1341,'PARKLAND 1',20,'ADIDAS',3,'AEH9','SULFUR GREEN','R-8','TSPA0092020112508','YELLOW','SOFT PU COATED LEATHER','A345','2020-11-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1342,'PARKLAND 1',20,'ADIDAS',3,'AE2Y','DYNAMIC RED','R-8','TSPA0092020112511','RED','SOFT PU COATED LEATHER','A346','2020-11-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1343,'PARKLAND 1',20,'ADIDAS',3,'AE9C','ESSNTIAL BLUE','R-8','TSPA0092020112510','L.BLUE','SOFT PU COATED LEATHER','A347','2020-11-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1344,'PARKLAND 1',20,'ADIDAS',3,'AE8K','LUCID LILAC','R-8','TSPA0092020112506','49D','SOFT PU COATED LEATHER','A348','2020-11-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1345,'PARKLAND 1',20,'ADIDAS',3,'AE8A','ALWAYS YELLOW','R-8','TSPA0092020112507','YELLOW','SOFT PU COATED LEATHER','A349','2020-11-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1346,'PARKLAND 1',20,'ADIDAS',3,'AE3E','COURT BLUE','R-8','TSPA0092020112501','44Z','SOFT PU COATED LEATHER','A350','2020-11-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1347,'PARKLAND 1',20,'ADIDAS',3,'AE9X','ATOMIC PINK','R-8','TSPA0092020112509','PINK','SOFT PU COATED LEATHER','A351','2020-11-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1348,'PARKLAND 1',20,'ADIDAS',3,'A1Q7','FLASH RED','R-8','TSPA0092020112504','RED','SOFT PU COATED LEATHER','A352','2020-11-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1349,'PARKLAND 1',20,'ADIDAS',3,'ADWX','VECTOR RED','R-8','TSPA0092020112503','RED','SOFT PU COATED LEATHER','A353','2020-11-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1350,'PARKLAND 1',20,'ADIDAS',3,'AE9B','BATIK BLUE','R-8','TSPA0092020112502','BLUE','SOFT PU COATED LEATHER','A354','2020-11-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1351,'PARKLAND 1',20,'ADIDAS',3,'ADVB','NIGHT BLACK','R-8','TSPA0092020112505','BLACK','SOFT PU COATED LEATHER','A355','2020-11-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1352,'VICTORY',31,'NIKE',1,'01V','WOLF GREY','DE-73','TMVC0052020111801','WHITE','VIRGIN HYDRO PU','A214','2020-11-20','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1353,'ADIS',1,'NIKE',1,'6CV','HYPER PINK','DE-73','TMAD0022020111003','PINK','VIRGIN HYDRO PU','A464','2020-11-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1354,'ADIS',1,'NIKE',1,'04Z','PURE PLATINUM','AR-33 M','TMAD0022020111001','WHITE','VIRGIN HYDRO PU','A465','2020-11-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1355,'FENGTAY TW',58,'NIKE',1,'22V','VIOLET ORE','R-51 SM','TSFT0382020112601','BLACK','PM GENERIC PU COATED LEATHER','A199','2020-11-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1356,'FENGTAY TW',58,'NIKE',1,'68W','PINK GLAZE','R-51 SM','TSFT0382020112602','PINK','PM GENERIC PU COATED LEATHER','A200','2020-11-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1357,'NIKOMAS IY',18,'NIKE',1,'0AN','GREY FOG','B-92','TMNS0202020112702','WHITE','SEMI FULL GRAIN','A918','2020-11-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1358,'NIKOMAS IY',18,'NIKE',1,'6DL','GYM RED','AR-148','TMNS0202020112701','RED','FP VIRGIN PU','A919','2020-11-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1359,'NIKOMAS',17,'ADIDAS',3,'AED2','SKY RUSH','DE-7','SCOTDIC','3EP','SOFT PU COATED LEATHER','A657','2020-01-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1360,'NIKOMAS',17,'ADIDAS',3,'002A','BRIGHT YELLOW','EV130TPD','FOLLOW FMCA','WHITE','SEMI FULL GRAIN','A658','2020-01-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1361,'NIKOMAS IY',18,'NIKE',1,'0AL','LT SMOKE GREY','AR-140','TMNS0202020120201','GREY','HP ECOTECH CONFORT','A920','2020-12-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1362,'NIKOMAS IY',18,'NIKE',1,'6GM','RUSH PINK','AR-196','TMNS0202020120202','PINK','VIRGIN HYDRO PU','A921','2020-12-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1363,'CHANGSHIN',3,'NIKE',1,'00A','BLACK','AR-135SG/AR-191','BLACK NIKE','BLACK','VIRGIN HYDRO','A149','2020-12-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1364,'NIKOMAS',17,'ADIDAS',3,'AED7','PULSE AMBER','DE-7','SCOTDIC','2CT','SOFT PU COATED LEATHER','A659','2020-12-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1365,'NIKOMAS',17,'ADIDAS',3,'AEDE','MAGIC LILAC','DE-7','SCOTDIC','49D','SOFT PU COATED LEATHER','A660','2020-12-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1366,'CHANGSHIN',4,'NIKE',1,'05I','COLLEGE GREY','R-8','TMCS0052020120301','WHITE','GENERIC PU COATED LEATHER','A150','2020-12-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1367,'CHANGSHIN',4,'NIKE',1,'0AJ','SMOKE GREY','AR-161','TMCS0052020120302','GREY','GENERIC PU COATED LEATHER','A151','2020-12-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1368,'POUYUEN',24,'NIKE',1,'00A','BLACK EX-ANODIZED','AR-33 SM','TSPY0282020120801','BLACK','VIRGIN HYDRO PU','A922','2020-12-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1369,'PCN G8',59,'NIKE',1,'70G','VARSITY MAIZE','DE-73 SM','TSPG0212020121001','YELLOW','GENERIC PU COATED LEATHER','A923','2020-12-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1370,'CHANGSHIN',3,'NIKE',1,'0AH','DK SMOKE GREY','DE-7 SM','TMCS0042020120801','BLACK','GENERIC PU COATED LEATHER','A152','2020-12-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1371,'NIKOMAS IY',18,'NIKE',1,'06B','COOL GREY','DE-43','TMNS0202020121001','GREY','FP VIRGIN PU','A924','2020-12-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1372,'NIKOMAS',17,'ADIDAS',3,'AECU','ALMOST PINK','DE-7','SCOTDIC','PINK','HYDRO SOFT PU','A661','2020-12-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1373,'NIKOMAS',17,'ADIDAS',3,'AED5','ACID RED','DE-7','SCOTDIC','PINK','SOFT PU COATED LEATHER','A662','2020-12-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1374,'NIKOMAS',17,'ADIDAS',3,'AECX','ORANGE RUSH','DE-126','SCOTDIC','2CT','SOFT PU COATED LEATHER','A663','2020-12-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1375,'NIKOMAS',17,'ADIDAS',3,'AEDP','LEGACY INDIGO','DE-126','SCOTDIC','44Z','SOFT PU COATED LEATHER','A664','2020-12-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1376,'NIKOMAS',17,'ADIDAS',3,'AEDS','SHADOW NAVY S22','DE-126','TSNS0162021031601','BLACK','SOFT PU COATED LEATHER','A669','2021-03-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01','2026-05-19 03:12:07'),
(1377,'NIKOMAS',17,'ADIDAS',3,'AEDD','MAGIC GREY','DE-126','SCOTDIC','4AU','SOFT PU COATED LEATHER','A666','2020-12-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1378,'ADIS',1,'NIKE',1,'88N','MAGIC EMBER','AR-107','TSAD0022020121601','80S','VIRGIN HYDRO PU','A467','2020-12-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1379,'CHANGSHIN',3,'NIKE',1,'12J','SUMMIT WHITE','AR-99 SM','TSCS0042020121702','WHITE','GENERIC PU COATED LEATHER','A153','2020-12-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1380,'CHANGSHIN',3,'NIKE',1,'44B','MIDNIGHT NAVY','AR-99 SM','TSCS0042020121701','BLACK','GENERIC PU COATED LEATHER','A154','2020-12-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1381,'FENGTAY (EAST)',8,'NIKE',1,'22V','VIOLET ORE','B-107','TSFT0072020121701','BROWN','FP VIRGIN PU','A201','2020-12-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1382,'PARKLAND 1',20,'ADIDAS',3,'AE8B','FOREST GREEN','R-8','TSPA0092020121801','WHITE','SOFT PU COATED LEATHER','A356','2020-12-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:01',NULL),
(1383,'PARKLAND 1',20,'ADIDAS',3,'AE8P','ALABASTER','R-30/R-8','TSPA0092020121802','WHITE','SOFT PU COATED LEATHER','A357','2020-12-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1384,'PRATAMA JX',25,'NIKE',1,'6DL','GYM RED','AR-196 M','TSPT0122020121801','WHITE','GENERIC PU COATED LEATHER','A466','2020-12-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1385,'KMK',15,'NIKE',1,'00J','SEAFOAM','UM-39','TMKM0012020122101','34A','VIRGIN HYDRO PU','A185','2020-12-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1386,'NIKOMAS',17,'ADIDAS',3,'AEE5','SEMI MINT RUSH','DE-126','SCOTDIC','3GU','SOFT PU COATED LEATHER','A667','2020-12-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1387,'CHANGSHIN',3,'NIKE',1,'42Y','DEEP ROYAL','AR-144','TMCS0042021011303','44Z','VIRGIN HYDRO PU','A158','2021-01-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02','2026-05-19 03:12:02'),
(1388,'CHANGSHIN',4,'NIKE',1,'6CV','HYPER PINK','AR-138','TMCS0052020122101','RED','VIRGIN HYDRO PU','A156','2020-12-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1389,'NIKOMAS IY',18,'NIKE',1,'4AI','COAST','R-8','TMNS0202020122801','44Z','HP ECO TECH COMFORT','A925','2020-12-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1390,'ADIS',1,'NIKE',1,'04Z','PURE PLATINUM','DE-73','TMAD0022021010401','WHITE','VIRGIN HYDRO PU','A468','2021-01-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1391,'NIKOMAS IY',18,'NIKE',1,'73B','CASHMERE','DE-73 SM','TMNS0202021010502','WHITE','PM GENERIC PU COATED LEATHER','A926','2021-01-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1392,'PRATAMA',25,'NIKE',1,'44B','MIDNIGHT NAVY','AR-196 M','TSPT0122021010502','WHITE','PM GENERIC PU COATED LEATHER','A467','2020-01-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1393,'PRATAMA',25,'NIKE',1,'44B','MIDNIGHT NAVY','AR-107','TSPT0122021010503','BLACK','PM GENERIC PU COATED LEATHER','A468','2020-01-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1394,'PRATAMA',25,'NIKE',1,'6JZ','DARK BEETROOT','AR-196 M','TSPT0122021010501','BLACK','PM GENERIC PU COATED LEATHER','A469','2020-01-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1395,'NIKOMAS IY',18,'NIKE',1,'87G','PALE CORAL','DE-73 SM','TMNS0202021010501','WHITE','PM GENERIC PU COATED LEATHER','A927','2021-01-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1396,'FENGTAY (WEST)',7,'NIKE',1,'06B','COOL GREY','AR-107','TMFT0062021010601','GREY','PM GENERIC PU COATED LEATHER','A202','2021-01-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1397,'TAEKWANG',30,'NIKE',1,'04B','CEMENT GREY','DE-90 SM','TMTK0272021010401','GREY','GENERIC PU COATED LEATHER','A097','2021-01-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1398,'NIKOMAS IY',18,'NIKE',1,'34I','ROMA GREEN','R-8','TMNS0202020122802','33R','HP ECOTECH COMFORT','A928',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1399,'CHANGSHIN',3,'NIKE',1,'44B','MIDNIGHT NAVY','DE-7 SM','TMCS0042021010601','BLACK','PM GENERIC PU COATED','A157','2021-01-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1400,'HORNMING',13,'PUMA',NULL,'11-0701','CREAMY WHITE','DE-7','TMHI0242021011101','WHITE','SOFT PU COATED','A160','2021-01-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1401,'HORNMING',13,'PUMA',NULL,'19-1757TCX','RED','DE-7','TMHI0242021011102','RED','SOFT PU COATED','A161','2021-01-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1402,'PARKLAND 2',21,'NB',4,'NB-S20-7546','NATURAL INDIGO','DE-107','TMPW0102021011201','BLACK','HYDRO SOFT PU COATED LEATHER','A358','2021-01-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1403,'FENGTAY TW',58,'NIKE',1,'12J','SUMMIT WHITE','R-51','TSFT0382021011202','WHITE','PM GENERIC PU COATED LEATHER','A203','2021-01-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1404,'FENGTAY TW',58,'NIKE',1,'58C','LILAC','R-8','TSFT0382021011201','WHITE','PM GENERIC PU COATED LEATHER','A204','2021-01-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1405,'ADIS',1,'NIKE',1,'11K','SAIL','DE-73','TMAD0022021011101','WHITE','PM GENERIC PU COATED','A469','2021-01-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1406,'CHANGSHIN',4,'NIKE',1,'44B','MIDNIGHT NAVY','AR-99 SM','TMCS0052021020906','BLACK','PM GENERIC PU COATED','A171','2021-02-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02','2026-05-19 03:12:07'),
(1407,'CHANGSHIN',4,'NIKE',1,'12J','SUMMIT WHITE','AR-99 SM','TMCS0052021020907','WHITE','PM GENERIC PU COATED','A166','2021-02-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02','2026-05-19 03:12:02'),
(1408,'CHANGSHIN',4,'NIKE',1,'68W','PINK GLAZE','AR-107','TMCS0052021011301','PINK','PM GENERIC PU COATED','A161','2021-01-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1409,'HORNMING',13,'PUMA',NULL,'19-3864TCX','BLUE','R-51','TMHI0242021011103','44Z','SOFT PU COATED','A162','2021-01-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1410,'NIKOMAS IY',24,'NIKE',1,'6JB','PINK FOAM','R-131','TSPY0282021012001','PINK','VIRGIN HYDRO PU','A934','2021-01-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02','2026-05-19 03:12:02'),
(1411,'NIKOMAS IY',18,'NIKE',1,'0AJ','SMOKE GREY','AR-140','TMNS0202021011401','GREY','HP ECO TECH COMFORT','A930','2021-01-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1412,'PARKLAND 2',21,'NB',4,'NB1100817','RAIN CLOUD','R-231','TSPW0102021011801','WHITE','HYDRO PRO ACTION LEATHER','A359','2021-01-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1413,'NIKOMAS IY',18,'NIKE',1,'3CS','LIME ICE','R-8','TMNS0202021011802','WHITE','VIRGIN PU','A931','2021-01-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1414,'NIKOMAS IY',18,'NIKE',1,'01V','WOLF GREY','DE-126 SM','TMNS0202021011801','WHITE','PM GENERIC PU COATED','A932','2020-01-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1415,'NIKOMAS IY',18,'NIKE',1,'11K','SAIL','AR-121/R-8','TMNS0202021011803','WHITE','ECO TECH COMFORT','A933','2021-01-20','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1416,'CHANGSHIN',4,'NIKE',1,'6JB','PINK FOAM','AR-196 M','TMCS0052021011801','PINK','PM GENERIC PU COATED','A162','2021-01-20','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1417,'CHANGSHIN',4,'NIKE',1,'0AH','DK SMOKE GREY','DE-7 SM','TMCS0052021032901','BLACK','PM GENERIC PU COATED','A173','2021-03-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02','2026-05-19 03:12:07'),
(1418,'NIKOMAS IY',18,'NIKE',1,'44B/50B','44B/50B','AR-138/R-8','TMNS0202021012101','49D','ECO TECH COMFORT','A935','2021-01-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1419,'CHANGSHIN',4,'NIKE',1,'0AI','IRON GREY','AR-196','TMCS0052021012001','BLACK','PM GENERIC PU COATED','A164','2021-01-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1420,'TAEKWANG',30,'NIKE',1,'6DL','GYM RED','AR-196','TMTK0272021012202','RED','VIRGIN HYDRO PU','A098','2021-01-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1421,'TAEKWANG',30,'NIKE',1,'28C','RATTAN','AR-196','TMTK0272021012201','WHITE','VIRGIN HYDRO PU','A099','2021-01-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1422,'NIKOMAS IY',18,'NIKE',1,'71R/7AN','71R/7AN','AR-121/R-8','TMNS0202021012102','YELLOW','ECO TECH COMFORT','A936','2021-01-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1423,'NIKOMAS IY',18,'NIKE',1,'6CD/82F','6CD/82F','R-8','TMNS0202021012002','80S','ECO TECH COMFORT','A937','2021-01-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1424,'NIKOMAS IY',18,'NIKE',1,'8AD','8AD','AR-121/R-8','TMNS0202021012001','WHITE','ECO TECH COMFORT','A938','2021-01-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1425,'HORNMING',13,'PUMA',NULL,'061-95-51','GREEN FLRSCN','DE-73SM','TMHI0242021012801','WHITE','SOFT PU COATED','A163','2021-01-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1426,'HORNMING',13,'PUMA',NULL,'007-54-40','RED FLRSCN','DE-73SM','TMHI0242021012802','RED','SOFT PU COATED','A164','2021-01-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1427,'METRO NB',16,'NB',4,'NB-F16-0054','ANGORA','R-53','TMMP0332021012701','WHITE','SEMI FULL GRAIN LEATHER','M030','2021-01-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1428,'PRATAMA',26,'NIKE',1,'58C','LILAC','R-8','TMPT0132021012701','WHITE','GENERIC PU COATED LEATHER','A470','2021-01-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1429,'KMK',15,'NIKE',1,'6JB','PINK FOAM','AR-107','TMKM0012021012701','PINK','VIRGIN HYDRO PU','A186','2021-01-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1430,'VICTORY',31,'NIKE',1,'06B','COOL GREY','UM-39','TSVC0052021012901','GREY','VIRGIN HYDRO PU','A215','2021-01-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1431,'TAEKWANG',30,'NIKE',1,'12J','SUMMIT WHITE','AR-99 SM','TMTK0272021012803','WHITE','PM GENERIC PU COATED','A100','2021-01-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1432,'TAEKWANG',30,'NIKE',1,'0AH','DK SMOKE GREY','AR-107','TMTK0272021012801','BLACK','PM GENERIC PU COATED','A101','2021-01-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1433,'TAEKWANG',30,'NIKE',1,'44B','MIDNIGHT NAVY','AR-99 SM','TMTK0272021012802','BLACK','PM GENERIC PU COATED','A102','2021-01-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1434,'TAEKWANG',30,'NIKE',1,'6JB','PINK FOAM','AR-99 SM','TMTK0272021012804','PINK','PM GENERIC PU COATED','A103','2021-01-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1435,'CHINGLUH',5,'NIKE',1,'6CM','VERRY BERRY','DE-73 SM','TSCL0172021013001','RED','PM GENERIC PU COATED','A216','2021-01-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1436,'TAEKWANG',30,'NIKE',1,'11K','SAIL','DE-90 SM','TMTK0272021012903','WHITE','PM GENERIC PU COATED','A104','2021-01-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1437,'TAEKWANG',30,'NIKE',1,'0AJ','SMOKE GREY','AR-107 M','TMTK0272021012902','GREY','PM GENERIC PU COATED','A105','2021-02-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1438,'TAEKWANG',30,'NIKE',1,'0AL','LT SMOKE GREY','AR-107','TMTK0272021012901','WHITE','PM GENERIC PU COATED','A106','2021-02-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1439,'VICTORY',31,'NIKE',1,'0AH','DK SMOKE GREY','AR-107','TSVC0052021020101','BLACK','PM GENERIC PU COATED','A217','2021-02-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1440,'PRATAMA',25,'NIKE',1,'44B','MIDNIGHT NAVY','R-8','TSPT0122021020101','BLACK','GENERIC PU COATED LEATHER','A471',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1441,'ADIS',1,'NIKE',1,'74F','WHEAT','UM-34','TSAD0022021020202','2CT','FP VIRGIN PU','A470','2021-02-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1442,'ADIS',1,'NIKE',1,'74F','WHEAT','UM-14','TSAD0022021020201','2CT','FP VIRGIN PU','A471','2021-02-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1443,'PARKLAND 2',21,'NB',4,'NB-S17-3696','HELIUM','AR-100','TMPW0102021020801','BLUE','HYDRO SOFT PU COATED LEATHER','A360','2021-02-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1444,'CHANGSHIN',4,'NIKE',1,'0AL','LT SMOKE GREY','AR-107','TMCS0052021020901','WHITE','PM GENERIC PU COATED','A165','2021-02-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1445,'CHANGSHIN',4,'NIKE',1,'44B','MIDNIGHT NAVY','AR-196','TMCS0052021030301','BLACK','PM GENERIC PU COATED','A172','2021-03-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02','2026-05-19 03:12:07'),
(1446,'CHANGSHIN',4,'NIKE',1,'4EV','GAME ROYAL','AR-196','TMCS0052021020902','44Z','PM GENERIC PU COATED','A168','2021-02-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1447,'CHANGSHIN',4,'NIKE',1,'11K','SAIL','AR-33 SG','TMCS0052021020905','WHITE','PM GENERIC PU COATED','A169','2021-02-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:02',NULL),
(1448,'CHANGSHIN',4,'NIKE',1,'68W','PINK GLAZE','AR-196','TMCS0052021020904','PINK','PM GENERIC PU COATED','A170','2021-02-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1449,'PANARUB',19,'ADIDAS',3,'A8K4','YELLOW','CPUG','SCOTDIC','YELLOW','BABY SOFT PATENT LEATHER','A107','2021-02-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1450,'PANARUB',19,'ADIDAS',3,'247A','DARK BROWN','CPUG','SCOTDIC','LIGHT BROWN','BABY SOFT PATENT LEATHER','A108','2021-02-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1451,'PANARUB',19,'ADIDAS',3,'A3CW','REAL GREEN','CPUG','SCOTDIC','3GU','BABY SOFT PATENT LEATHER','A109','2021-02-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1452,'PANARUB',19,'ADIDAS',3,'A6W7','BAHIA ORANGE','CPUG','SCOTDIC','80S','BABY SOFT PATENT LEATHER','A110','2021-02-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1453,'HORNMING',13,'PUMA',NULL,'930C','YELLOW FLUORESCENT','DE-7 SM','TMHI0242021021501','WHITE','SOFT PU COATED','A165','2021-02-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1454,'FENGTAY (EAST)',8,'NIKE',1,'58C','LILAC','R-8','TMFT0072021021601','WHITE','PM GENERIC PU COATED LEATHER','A206','2021-02-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1455,'TAEKWANG',30,'NIKE',1,'3JG','SEQUOIA','R-51 SM','TMTK0272021013001','BLACK','PM GENERIC PU COATED','A107','2021-02-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1456,'PANARUB',19,'ADIDAS',3,'806A','VICTORY RED','DE-73','TSPA0202021021701','RED','PU COATED LEATHER ( MAP-ACTION LEATHER)','A111','2021-02-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1457,'TAH SUNG HUNG',34,'ADIDAS',3,'AAJJ','BLUE TINT','R-8','FMCA','WHITE','SOFT PU COATED LEATHER','A682','2021-06-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07','2026-05-19 03:12:08'),
(1458,'FENGTAY TW',58,'NIKE',1,'65M','ARCHAEO PINK','AR-121 SG','TSFT0382021022502','RED','PM GENERIC PU COATED LEATHER','A207','2021-02-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1459,'FENGTAY TW',58,'NIKE',1,'65M','ARCHAEO PINK','AR-167 DM','TSFT0382021022501','RED','PM GENERIC PU COATED LEATHER','A208','2021-02-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1460,'PRATAMA JX',26,'NIKE',1,'44B','MIDNIGHT NAVY','AR-107 M','TMPT0132021022501','BLACK','GENERIC PU COATED LEATHER','A472','2021-02-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1461,'NIKOMAS IY',18,'NIKE',1,'3GT','TURBO GREEN','DE-45 G','TMNS0202021030101','4JE','SEMI FULL GRAIN','A939','2021-03-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1462,'NIKOMAS IY',18,'NIKE',1,'76I','UNIVERSITY GOLD','R-102 SM','TSNS0202021030201','YELLOW','GENERIC PU COATED','A940','2021-03-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1463,'NIKOMAS IY',18,'NIKE',1,'45L','LAPIS','R-102 SM','TSNS0202021030202','44Z','GENERIC PU COATED','A941','2021-03-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1464,'NIKOMAS IY',18,'NIKE',1,'07G','LIGHT BONE','R-102 SM','TSNS0202021030203','WHITE','GENERIC PU COATED','A942','2021-03-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1465,'NIKOMAS IY',18,'NIKE',1,'74F','WHEAT','R-102 SM','TSNS0202021030204','2CT','GENERIC PU COATED','A943','2021-03-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1466,'PARKLAND 2',21,'NB',4,'NB-F21-1078','DEEP OCEAN GREY','DE-107 M','TMPW0102021030602','BLACK','HYDRO SOFT PU COATED LEATHER','A361','2021-03-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1467,'PARKLAND 2',21,'NB',4,'NB-S21-7834','OCEAN GREY','DE-107 M','TMPW0102021030601','L.BLUE','HYDRO SOFT PU COATED LEATHER','A362','2021-03-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1468,'PRATAMA JX',26,'NIKE',1,'06B','COOL GREY','R-8','TMPT0132021030401','GREY','PM GENERIC PU COATED','A473','2021-03-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1469,'VICTORY',31,'NIKE',1,'0AH','DK SMOKE GREY','UMT SM','TSVC0052021031001','BLACK','VIRGIN HYDRO PU','A218','2021-03-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1470,'ADIS',1,'NIKE',1,'71R','VOLT','DE-73 SM','TMAD0022021030901','71R','PM GENERIC PU COATED','A472','2021-03-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1471,'POUYUEN',24,'NIKE',1,'6DQ','SIREN RED','R-131','TSPY0282021031001','RED','VIRGIN HYDRO PU','A944','2021-03-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1472,'POUYUEN',24,'NIKE',1,'50K','CANYON PURPLE','R-131','TSPY0282021031002','PURPLE','VIRGIN HYDRO PU','A945','2021-03-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1473,'VICTORY',31,'NIKE',1,'6HB','RUSH PINK','AR-107','TSVC0052021031201','RED','PM GENERIC PU COATED','A219','2021-03-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1474,'PANARUB',19,'ADIDAS',3,'A5J3','LGH SOLID GREY','DE-7','SCOTDIC','01V','SOFT PU COATED LEATHER','A113','2021-03-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1475,'POUYUEN',24,'NIKE',1,'50K','CANYON PURPLE','R-231','TSPY0282021031601','WHITE','PM GENERIC PU COATED','A946','2021-03-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1476,'ADIS',1,'NIKE',1,'6CV','HYPER PINK','DE-73 SM','TMAD0022021031702','PINK','PM GENERIC PU COATED','A473','2021-03-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1477,'ADIS',1,'NIKE',1,'74F','WHEAT','UM-14 SG','TMAD0022021031701','2CT','VIRGIN HYDRO PU','A474','2021-03-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1478,'ADIS',1,'NIKE',1,'0AH','DK SMOKE GREY','DE-73','TMAD0022021032303','BLACK','PM GENERIC PU COATED','A475','2021-03-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1479,'ADIS',1,'NIKE',1,'54A','PERSIAN VIOLET','DE-73 M','TMAD0022021032302','44Z','VIRGIN HYDRO PU','A477','2021-03-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1480,'ADIS',1,'NIKE',1,'22V','VIOLET ORE','DE-73SM','TMAD0022021032304','BROWN','PM GENERIC PU COATED','A478','2021-03-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1481,'PARKLAND 1',20,'REEBOK',NULL,'ADHE','PURE GREY 3-R','R-8','SCOTDIC','01V','SOFT PU COATED LEATHER','A363','2021-03-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1482,'SHOETOWN',28,'NIKE',1,'29J','PEARL WHITE','AR-161','TMSL0432021032601','WHITE','PM GENERIC PU COATED','A947','2021-03-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1483,'VICTORY',31,'NIKE',1,'65H','CORAL CHALK','AR-107','TSVC0052021032901','PINK','PM GENERIC PU COATED','A220','2021-03-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1484,'ADIS',1,'NIKE',1,'4LB','GYM BLUE','R-131','TMAD0022021032601','44Z','VIRGIN PU','A479','2021-03-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1485,'CHANGSHIN',4,'NIKE',1,'06B','COOL GREY','R-102 SM','TMCS0052021032902','GREY','ECO TECH COMFORT','A174','2021-03-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1486,'CHANGSHIN',4,'NIKE',1,'06T','STADIUM GREY','R-102 SM','TMCS0052021032903','01V','ECO TECH COMFORT','A175','2021-03-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1487,'NIKOMAS',17,'ADIDAS',3,'08S1','OFF WHITE','R-8','FOLLOW FMCA','WHITE','SOFT PU COATED LEATHER','A678','2021-05-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07','2026-05-19 03:12:08'),
(1488,'NIKOMAS IY',18,'NIKE',1,'01B','METALLIC SILVER','EV130TPD','TMNS0202021033101','WHITE','VIRGIN HYDRO PU','A948','2021-04-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1489,'SHOETOWN',28,'NIKE',1,'27Q','DK DRIFTWOOD','AR-161','TMSL0432021033101','2CT','PM GENERIC PU COATED','A949','2021-04-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1490,'POUYUEN',24,'NIKE',1,'06L','GHOST','R-231','TMPY0282021033101','WHITE','VIRGIN HYDRO PU','A950','2021-03-31','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1491,'SCI',32,'NIKE',1,'62E','LIGHT SOFT PINK','AR-169','TMSC0062021033102','WHITE','VIRGIN HYDRO PU','A951','2021-04-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1492,'SCI',32,'NIKE',1,'22V','VIOLET ORE','AR-169','TMSC0062021033101',NULL,'VIRGIN HYDRO PU','A952','2021-04-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1493,'VICTORY',31,'NIKE',1,'3HR','CARGO KHAKI','AR-107','TSVC0052021033001','33R','PM GENERIC PU COATED','A221','2021-03-31','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1494,'KMK',15,'NIKE',1,'0BB','PHOTON DUST','AR-161','TMKM0012021033001','WHITE','PM GENERIC PU COATED','A187',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1495,'NIKOMAS',17,'ADIDAS',3,'AE6E','PULSE YELLOW','DE-73','TSNS0162021040101','YELLOW','SOFT PU','A671','2021-04-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1496,'NIKOMAS IY',18,'NIKE',1,'44B','MIDNIGHT NAVY','AR-167 DM','TMNS0202021040502','BLACK','PM GENERIC PU COATED','A953','2021-04-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1497,'FENGTAY (EAST)',8,'NIKE',1,'65H','CORAL CHALK','AR-107','TSFT0072021040601','PINK','PM GENERIC PU COATED LEATHER','A209','2021-04-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1498,'FENGTAY (EAST)',8,'NIKE',1,'6HB','RUSH PINK','AR-107','TSFT0072021040602','6DX','PM GENERIC PU COATED LEATHER','A210','2021-04-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1499,'CHANGSHIN',3,'NIKE',1,'33S','DARK ARMY','R-102','TSCS0042021040601','BLACK','ECO TECH COMFORT','A176','2021-04-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1500,'CHANGSHIN',3,'NIKE',1,'22V','VIOLET ORE','AR-144','TSCS0042021040702','BROWN','VIRGIN HYDRO PU','A177','2021-04-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1501,'CHANGSHIN',4,'NIKE',1,'06T','STADIUM GREY','AR-144','TMCS0052021073101','WHITE','VIRGIN HYDRO PU','A194','2021-07-31','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07','2026-05-19 03:12:08'),
(1502,'SHOETOWN',28,'NIKE',1,'6HB','RUSH PINK','AR-107','TMSL0432021040702','6DX','PM GENERIC PU COATED','A954','2021-04-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1503,'SHOETOWN',28,'NIKE',1,'65H','CORAL CHALK','AR-107','TMSL0432021040701','PINK','PM GENERIC PU COATED','A955','2021-04-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1504,'CHANGSHIN',3,'NIKE',1,'27T','TWEED','R-102','TSCS0042021040701','WHITE','ECO TECH COMFORT','A179','2021-04-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1505,'CHINGLUH',5,'NIKE',1,'6HB','RUSH PINK','AR-107','TMCL0172021041102','PINK','PM GENERIC PU COATED','A222','2021-04-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1506,'CHINGLUH',5,'NIKE',1,'65H','CORAL CHALK','AR-107','TMCL0172021041101','RED','PM GENERIC PU COATED','A223','2021-04-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1507,'FENGTAY',7,'NIKE',1,'0AL','LT SMOKE GREY','UM-34T SM','TMFT0062021041101','WHITE','PM GENERIC PU COATED LEATHER','A211','2021-04-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1508,'VICTORY',31,'NIKE',1,'06B','COOL GREY','DE-90 M','TSVC0052021041201','BLACK','VIRGIN HYDRO PU','A224','2021-04-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1509,'NIKOMAS IY',18,'NIKE',1,'80K','STARFISH','R-102','TMNS0202021041401','80S','GENERIC PU COATED','A956','2021-04-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1510,'TAEKWANG',30,'NIKE',1,'74F','WHEAT','AR-144','TSTK0272021041401','2CT','ECO TECH COMFORT','A108','2021-04-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1511,'TAEKWANG',30,'NIKE',1,'06T','STADIUM GREY','AR-144','TMTK0272021041601','GREY','VIRGIN HYDRO PU','A109','2021-04-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1512,'NIKOMAS',17,'ADIDAS',3,'ADYY','VIVID RED','UM-36','PASS FMCA','RED','SOFT PU COATED LEATHER','A672','2021-04-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1513,'PRATAMA',25,'NIKE',1,'89L','TEAM ORANGE','AR-196','TSPT0122021041601','RED','PM GENERIC PU COATED','A474','2021-04-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1514,'CHINGLUH',5,'NIKE',1,'6DL','GYM RED','AR-99 SM','TMCL0172021041701','RED','PM GENERIC PU COATED','A225','2021-04-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1515,'PANARUB',19,'ADIDAS',3,'A2CP','EVERGREEN','DE-73','SCOTDIC','33R','PU COATED LEATHER','A117','2021-04-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1516,'PARKLAND 1',20,'NB',4,'NB-S19-2718','LIGHT ALUMINIUM','UM-14SG','FOLLOW CSI','01V','HYDRO SOFT PU COATED LEATHER','A364','2021-04-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1517,'NIKOMAS IY',18,'NIKE',1,'68W','PINK GLAZE','DE-126 SM','TMNS0202021042001','PINK','PM GENERIC PU COATED','A957','2021-04-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1518,'SHOETOWN',28,'NIKE',1,'6JZ','DARK BEETROOT','AR-161 M','TMSL0432021042101','BLACK','PM GENERIC PU COATED','A958','2021-04-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1519,'VICTORY',31,'NIKE',1,'58R','PLUM FOG','AR-188 M','TMVC0052021042101','PINK','VIRGIN HYDRO PU','A226','2021-04-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1520,'FENGTAY TW',58,'NIKE',1,'6HE','HARBENERO RED','AR-140','TSFT0382021042601','RED','PM GENERIC PU COATED LEATHER','A212','2021-04-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1521,'FENGTAY TW',58,'NIKE',1,'07G','LIGHT BONE','B-249','TSFT0382021042701','WHITE','VIRGIN HYDRO PU','A213','2021-04-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1522,'VICTORY',5,'NIKE',1,'4LX','ARMORY NAVY','AR-99 SM','TMCL0172021042801','BLACK','(PM) GENERIC PU COATED','A227','2021-04-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1523,'FENGTAY TW',7,'NIKE',1,'12J','SUMMIT WHITE','R-53','TMFT0062021042902','WHITE','VIRGIN HYDRO PU','A214','2021-04-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1524,'FENGTAY (EAST)',8,'NIKE',1,'22V','VIOLET ORE','R-51 SM','TMFT0072021042902','BLACK','(PM) GENERIC PU COATED','A215','2021-04-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1525,'FENGTAY (EAST)',8,'NIKE',1,'68W','PINK GLAZE','R-51 SM','TMFT0072021042901','PINK','(PM) GENERIC PU COATED','A216','2021-04-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1526,'FENGTAY (WEST)',7,'NIKE',1,'4PB','ASHEN SLATE','UM-34 SM','TMFT0062021042901','WHITE','(PM) GENERIC PU COATED','A217','2021-04-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1527,'PRATAMA JX',26,'NIKE',1,'05B','CHROME METALLIC','AR-196','TMPT0132021043001','WHITE','PM GENERIC PU COATED','A475','2021-04-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1528,'PARKLAND 2',21,'NB',4,'127-23-24','VICTORY BLUE COLORO','UM-14 SG','FOLLOW CSI','44Z','HYDRO SOFT PU COATED LEATHER','A365','2021-04-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1529,'NIKOMAS IY',18,'NIKE',1,'07G','LIGHT BONE','B-249 SG','TMNS0202021042701','WHITE','VIRGIN HYDRO PU','A959','2021-04-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1530,'KMK',15,'NIKE',1,'76I','UNIVERSITY GOLD','DE-126 SM','TMKM0012021042701','YELLOW','PM GENERIC PU COATED','A188','2021-04-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1531,'VICTORY',31,'NIKE',1,'0AL','LT SMOKE GREY','R-53','TSVC0052021043001','WHITE','GENERIC PU COATED','A228','2021-05-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1532,'PANARUB',19,'ADIDAS',3,'020A','GREEN','DE-73','FMCA','33R','PU COATED LEATHER','A123','2021-07-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07','2026-05-19 03:12:08'),
(1533,'FENGTAY (WEST)',7,'NIKE',1,'65M','ARCHAED PINK','AR-167','TMFT0062021050602','RED','(PM) GENERIC PU COATED','A218','2021-05-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1534,'FENGTAY (WEST)',7,'NIKE',1,'65M','ARCHAED PINK','AR-121','TMFT0062021050601','RED','(PM) GENERIC PU COATED','A219','2021-05-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1535,'TAEKWANG',30,'NIKE',1,'45B','OBSIDIAN','AR-107','TMTK0272021050501','BLACK','PM GENERIC PU COATED','A110','2021-05-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1536,'NIKOMAS',17,'ADIDAS',3,'AAJL','ECRU TINT','DE-73','FMCA','WHITE','HYDRO ECO TECH COMFORT','A714','2022-02-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07','2026-05-19 03:12:10'),
(1537,'VICTORY',31,'NIKE',1,'6DL','GYM RED','B-830 SG','TSVC0052021051102','RED','VIRGIN HYDRO PU','A230','2021-05-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1538,'CHANGSHIN',3,'NIKE',1,'74F','WHEAT','AR-144','TSCS00420200472301','2CT','ECO TECH COMFORT','A180','2021-05-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1539,'TAEKWANG',30,'NIKE',1,'50S','VENICE','AR-196','TMTK0272021051101','WHITE','VIRGIN HYRDO PU','A111','2021-05-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1540,'FENGTAY TW',58,'NIKE',1,'40W','PHOTO BLUE','DE-73 SM','TSFT0382021051801','BLUE','(PM) GENERIC PU COATED','A220','2021-05-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1541,'PRATAMA JX',26,'NIKE',1,'89L','TEAM ORANGE','AR-196','TMPT0132021051701','RED','PM GENERIC PU COATED','A476','2021-05-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1542,'TAEKWANG',30,'NIKE',1,'20I','HEMP','AR-196','TMTK0272021051701','01V','VIRGIN HYRDO PU','A112','2021-05-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1543,'TAEKWANG',30,'NIKE',1,'22V','VIOLET ORE','AR-144','TMTK0272021051901','BROWN','VIRGIN HYRDO PU','A113','2021-05-20','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1544,'FENGTAY',8,'NIKE',1,'22V','VIOLET ORE','B-107 SM','TMFT0072021052101','BROWN','GENERIC PU COATED','A221','2021-05-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:07',NULL),
(1545,'NIKOMAS',17,'ADIDAS',3,'014A','COLLEGIATE RED','DE-126','FOLLOW FMCA','RED','SOFT PU COATED LEATHER','A675','2021-05-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1546,'NIKOMAS',17,'ADIDAS',3,'ADWD','CREW BLUE','DE-73','FOLLOW FMCA','4MD','SOFT PU COATED LEATHER','A676','2021-05-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1547,'NIKOMAS',17,'ADIDAS',3,'043A','DARK BLUE','DE-126','FOLLOW FMCA','44Z','SOFT PU COATED LEATHER','A677','2021-05-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1548,'PCN G8',59,'NIKE',1,'0AV','OFF NOIR','R-51 SM','TSPG0212021052901','BLACK','PM GENERIC PU COATED LEATHER','A960','2021-05-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1549,'CHINGLUH',5,'NIKE',1,'3DT','NOBLE GREEN','AR-99 SM','TMCL0172021052801','33R','PM GENERIC PU COATED','A231','2021-05-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1550,'PANARUB',19,'ADIDAS',3,'AAGG','CARBON','DE-73','FOLLOW FMCA','BLACK','PU COATED LEATHER','A119','2021-06-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1551,'FENGTAY',7,'NIKE',1,'65N','UNIVERSITY RED','DE-73 SM','TMFT0062021060401','RED','(PM) GENERIC PU COATED','A222','2021-06-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1552,'FENGTAY',7,'NIKE',1,'07G','LIGHT BONE','B-249 SG','TMFT0062021060402','WHITE','VIRGIN HYDRO PU','A223','2021-06-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1553,'NIKOMAS',17,'ADIDAS',3,'ADCY','TEAM ORANGE','DE-7','TSNS0162021060301','80S','PU COATED','A679','2021-06-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1554,'CHANGSHIN',3,'NIKE',1,'04Z','PURE PLATINUM','AR-144','TSCS0042021060402','WHITE','VIRGIN HYRDO PU','A181','2021-06-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1555,'CHANGSHIN',3,'NIKE',1,'12J','SUMMIT WHITE','AR-144','TSCS0042021060401','WHITE','VIRGIN HYRDO PU','A182','2021-06-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1556,'CHANGSHIN',3,'NIKE',1,'0AL','LT SMOKE GREY','AR-144','TSCS0042021060801','GREY','VIRGIN HYRDO PU','A183','2021-06-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1557,'PCN G8',59,'NIKE',1,'40W','PHOTO BLUE','UM-16SM','TSPG0212021060901','BLUE','PM GENERIC PU COATED LEATHER','A961','2021-06-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1558,'POUYUEN',24,'NIKE',1,'0AN','GREY FOG','UM-16SM','TSPY0282021061102','WHITE','PM GENERIC PU COATED LEATHER','A962','2021-06-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1559,'POUYUEN',24,'NIKE',1,'40W','PHOTO BLUE','UM-16SM','TSPY0282021061104','BLUE','PM GENERIC PU COATED LEATHER','A963','2021-06-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1560,'POUYUEN',24,'NIKE',1,'6JB','PINK FOAM','UM-16SM','TSPY0282021061103','PINK','PM GENERIC PU COATED LEATHER','A964','2021-06-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1561,'POUYUEN',24,'NIKE',1,'6HD','CRIMSON BLISS','R-102','TSPY0282021061101','80S','VIRGIN HYDRO PU','A965','2021-06-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1562,'POUYUEN',24,'NIKE',1,'4KW','WORN BLUE','R-231','TSPY0282021060903','L.BLUE','PM GENERIC PU COATED','A966','2021-06-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1563,'POUYUEN',24,'NIKE',1,'0AN','GREY FOG','R-231','TSPY0282021060901','WHITE','PM GENERIC PU COATED','A967','2021-06-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1564,'SHOETOWN',28,'NIKE',1,'45F','DK POWER BLUE','AR-196','TMSC0432021060901','WHITE','PM GENERIC PU COATED','A968','2021-06-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1565,'PCN G8',59,'NIKE',1,'6JB','PINK FOAM','UM-16 SM','TSPG0212021061501','PINK','PM GENERIC PU COATED','A969',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1566,'NIKOMAS',17,'ADIDAS',3,'AEK8','PULSE LILAC','DE-126','SCOTDIC','PINK','SOFT PU COATED LEATHER','A680','2021-06-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1567,'NIKOMAS',17,'ADIDAS',3,'AELF','SEMI IMPACT ORANGE','DE-126','SCOTDIC','80S','SOFT PU COATED LEATHER','A681','2021-06-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1568,'TAH SUNG HUNG',34,'ADIDAS',3,'AA2S','GREY TWO','R-8','FMCA','01V','SOFT PU COATED LEATHER','A683','2021-06-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1569,'TAH SUNG HUNG',34,'ADIDAS',3,'AA2V','GREY FIVE','R-8','FMCA','GREY','SOFT PU COATED LEATHER','A684','2021-06-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1570,'NIKOMAS',17,'ADIDAS',3,'AED4','PURPLE RUSH','DE-126','SCOTDIC','58U','SOFT PU COATED LEATHER','A685','2021-06-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1571,'NIKOMAS',17,'ADIDAS',3,'AELC','BLISS ORANGE','DE-7','SCOTDIC','WHITE','SOFT PU COATED LEATHER','A686','2021-06-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1572,'NIKOMAS',17,'ADIDAS',3,'AELD','WONDER STEEL','DE-126','SCOTDIC','4MD','SOFT PU COATED LEATHER','A687','2021-06-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1573,'NIKOMAS',17,'ADIDAS',3,'AEJR','ALMOST BLUE','DE-126','SCOTDIC','WHITE','SOFT PU COATED LEATHER','A688','2021-06-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1574,'NIKOMAS',17,'ADIDAS',3,'AEK2','IMPACT YELLOW','DE-126','SCOTDIC','YELLOW','SOFT PU COATED LEATHER','A689','2021-06-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1575,'NIKOMAS',17,'ADIDAS',3,'AEK5','WONDER RED','DE-126','SCOTDIC','RED','SOFT PU COATED LEATHER','A690','2021-06-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1576,'NIKOMAS',17,'ADIDAS',3,'AEDA','MAGICE MAUVE','DE-126','SCOTDIC','PINK','SOFT PU COATED LEATHER','A691','2021-06-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1577,'VICTORY',31,'NIKE',1,'4AH','AURA','AR-188 M','TSVC0052021061801','01V','VIRGIN HYDRO PU','A232','2021-06-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1578,'CHANGSHIN',3,'NIKE',1,'04D','LIGHT SILVER','AR-144','TSCS0042021060901','WHITE','VIRGIN HYRDO PU','A184','2021-06-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1579,'CHANGSHIN',4,'NIKE',1,'22V','VIOLET ORE','AR-144','TMCS0052021061501','BROWN','VIRGIN HYRDO PU','A185','2021-06-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1580,'SHOETOWN',28,'NIKE',1,'43F','DK MARINA BLUE','DE-73','TMSL0432021061501','BLUE','PM GENERIC PU COATED','A970','2021-06-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1581,'HORNMING',13,'PUMA',NULL,'17-1460 TSX','RED','DE-7','TSHI0242021062501','RED','SOFT PU COATED','A165','2021-06-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1582,'HORNMING',13,'PUMA',NULL,'BLUE','BLUE','AR-169','TSHI0242021062502','44Z','HYDRO ECO TECH COMFORT','A166','2021-06-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1583,'VICTORY',31,'NIKE',1,'6DL','GYM RED','R-53','TSVC0052021062501','RED','VIRGIN HYDRO PU','A233','2021-06-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1584,'ADIS',1,'NIKE',1,'65N','UNIVERSITY RED','DE-7SM','TMAD0022021062802','RED','PM GENERIC PU COATED','A480','2021-07-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1585,'ADIS',1,'NIKE',1,'6HU','PINK PRIME','DE-73SM','TMAD0022021062801','6DX','PM GENERIC PU COATED','A481','2021-07-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1586,'FENGTAY (WEST)',7,'NIKE',1,'01X','PHANTOM','AR-167','TSFT0062021070202','WHITE','PM GENERIC PU COATED','A224','2021-07-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1587,'PANARUB',19,'ADIDAS',3,'A0R1','CLEAR AQUA','DE-73','FMCA EVN','4AU','PU COATED LEATHER','A129','2021-09-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08','2026-05-19 03:12:08'),
(1588,'FENGTAY (WEST)',7,'NIKE',1,'01X','PHANTOM','AR-121SG','TSFT0062021070201','WHITE','PM GENERIC PU COATED','A225','2021-07-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1589,'FENGTAY (WEST)',7,'NIKE',1,'6HD','CRIMSON BLISS','UM-34T SM','TSFT0062021070501','80S','PM GENERIC PU COATED','A226','2021-07-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1590,'CHANGSHIN',3,'NIKE',1,'05Q','FOOTBALL GREY','DE-7 SM','TMCS0042021070601','WHITE','PM GENERIC PU COATED','A186','2021-07-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1591,'CHANGSHIN',3,'NIKE',1,'0AV','TSCS0042021070601','R-51 SM','TSCS0042021070601','BLACK','PM GENERIC PU COATED','A187','2021-07-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1592,'NIKOMAS IY',18,'NIKE',1,'01B','METALLIC SILVER','DE-125','TMNS0202021070901','WHITE','VIRGIN PU','A971','2021-07-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1593,'SHOETOWN',28,'NIKE',1,'64M','VARSITY RED','DE-73SM','TMSL0432021070901','RED','GENERIC PU COATED','A972','2021-07-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1594,'PCN G8',59,'NIKE',1,'46L','MARINA','R-8','TSPG0212021071501','BLACK','PU COATED LEATHER','A973','2021-07-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1595,'PCN G8',59,'NIKE',1,'44B','MIDNIGHT NAVY','R-8','TSPG0212021071502','BLACK','PU COATED LEATHER','A974','2021-07-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1596,'ADIS',1,'NIKE',1,'26U','MEDIUM ASH','R-231','TMAD0022021070902','BLACK','GENERIC PU COATED','A482','2021-07-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1597,'ADIS',1,'NIKE',1,'6DQ','SIREN RED FLUORESCENT','DE-73 SM','TMAD0022021070901','RED','GENERIC PU COATED','A483','2021-07-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1598,'PANARUB',19,'ADIDAS',3,'A0T8','CALVI','DE-73','FMCA','WHITE','PU COATED LEATHER','A121','2021-07-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1599,'NIKOMAS',17,'ADIDAS',3,'AEDX','GOLDEN BEIGE','DE-7','SCOTDIC','2CT','SOFT PU COATED LEATHER (MAP-SOFT PU)','A692','2021-07-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1600,'PCN G8',59,'NIKE',1,'12J','SUMMIT WHITE','AR-144','TSPG0212021072301','WHITE','VIRGIN  HYDRO PU LEATHER','A975','2021-07-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1601,'PANARUB',19,'ADIDAS',3,'A2JM','CLEAR PINK','DE-73','FMCA','PINK','PU COATED LEATHER','A122','2021-07-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1602,'PANARUB',19,'ADIDAS',3,'ADF2','TEAM COLLEG PURPLE','DE-73','FOLLOW FMCA 43F0','44Z','PU COATED LEATHER','A124','2021-07-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1603,'ADIS',1,'NIKE',1,'6HU','PINK PRIME','R-231','TMAD0022021071601','6DX','GENERIC PU COATED','A484','2021-07-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1604,'PCN G8',59,'NIKE',1,'37L','BRIGHT SPRUCE','R-8 M','TSPG0212021072302','33R','PM GENERIC PU COATED LEATHER','A976','2021-07-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1605,'PCN G8',59,'NIKE',1,'56S','ELECTRO PURPLE','R-8M','TSPG0212021072303','PURPLE','PM GENERIC PU COATED LEATHER','A977','2021-07-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1606,'CHANGSHIN',4,'NIKE',1,'02Y','FLAT PEWTER','AR-196','TMCS0052021072401','L.BROWN','PM GENERIC PU COATED','A188','2021-07-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1607,'HWASEUNG',14,'ADIDAS',3,'AED3','BLUE RUSH','DE-7','TMHW0352021073001','BLUE','SOFT PU COATED LEATHER (MAP-SOFT PU)','A695','2021-07-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08','2026-05-19 03:12:08'),
(1608,'ADIS',1,'NIKE',1,'73R','VIVID SULFUR','AR-196','TMAD0022021072403','YELLOW','GENERIC PU COATED','A485','2021-07-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1609,'ADIS',1,'NIKE',1,'6KI','CONYON RUSH','R-231','TMAD0022021072405','80S','GENERIC PU COATED','A486','2021-07-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1610,'ADIS',1,'NIKE',1,'4MD','COASTAL BLUE','R-231','TMAD0022021072406','BLUE','VIRGIN PU','A487','2021-07-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1611,'ADIS',1,'NIKE',1,'04D','LIGHT SILVER','DE-73 M','TMAD0022021072404','WHITE','VIRGIN HYDRO PU','A488','2021-07-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1612,'ADIS',1,'NIKE',1,'29J','PEARL WHITE','AR-167','TMAD0022021072401','WHITE','PM GENERIC PU COATED','A489','2021-07-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1613,'ADIS',1,'NIKE',1,'6LA','ROSE WHISPER','AR-196 M','TMAD0022021072402','PINK','PM GENERIC PU COATED','A490','2021-07-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1614,'ADIS',1,'NIKE',1,'00C','DARK GREY','R-8','TMAD0022021072408','GREY','VIRGIN PU','A491','2021-07-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1615,'TAEKWANG',30,'NIKE',1,'33T','CELERY','AR-167','TMTK0272021072402','YELLOW','GENERIC PU COATED LEATHER','A114','2021-07-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1616,'TAEKWANG',30,'NIKE',1,'04D','LIGHT SILVER','AR-144','TMTK0272021072401','WHITE','VIRGIN HDRO PU','A115','2021-07-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1617,'CHANGSHIN',4,'NIKE',1,'04D','LIGHT SILVER','AR-196','TMCS0052021072402','WHITE','PM GENERIC PU COATED','A189','2021-07-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1618,'CHANGSHIN',4,'NIKE',1,'46L','MARINA','AR-144','TMCS0052021082802','L.BLUE','VIRGIN HYDRO PU','A198','2021-09-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08','2026-05-19 03:12:08'),
(1619,'POUYUEN',24,'NIKE',1,'65N','UNIVERSITY RED','R-231','TMPY0282021072804','RED','PM GENERIC PU COATED LEATHER','A978','2021-07-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1620,'POUYUEN',24,'NIKE',1,'0AL','LT SMOKE GREY','R-231','TMPY0282021072803','WHITE','PM GENERIC PU COATED LEATHER','A979','2021-07-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1621,'POUYUEN',24,'NIKE',1,'4EV','GAME ROYAL','R-231','TMPY0282021072802','44Z','PM GENERIC PU COATED LEATHER','A980','2021-07-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1622,'POUYUEN',24,'NIKE',1,'76I','UNIVERSITY GOLD','AR-140','TMPY0282021072801','YELLOW','PM GENERIC PU COATED LEATHER','A981','2021-07-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1623,'ADIS',1,'NIKE',1,'4CA','DARK OBSIDIAN','R-231','TMAD0022021072407','BLACK','VIRGIN PU','A492','2021-07-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1624,'TAEKWANG',30,'NIKE',1,'46L','MARINA','AR-144M','TMTK0272021072801','L.BLUE','VIRGIN HDRO PU','A116','2021-07-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1625,'HWASEUNG',14,'ADIDAS',3,'ADYY','VIVID RED','DE-7','TMHW0352021073002','RED','SOFT PU COATED LEATHER (MAP-SOFT PU)','A694','2021-07-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1626,'POUYUEN',24,'NIKE',1,'50K','CANYON RUSH','R-231','TMPY0282021072901','PURPLE','PM GENERIC PU COATED LEATHER','A982','2021-07-31','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1627,'CHANGSHIN',4,'NIKE',1,'0AV','OFF NOIR','R-51','TMCS0052021073001','BLACK','PM GENERIC PU COATED','A191','2021-07-31','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1628,'CHANGSHIN',4,'NIKE',1,'12J','SUMMIT WHITE','AR-144','TMCS0052021073003','WHITE','VIRGIN HYDRO PU','A192','2021-07-31','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1629,'CHANGSHIN',4,'NIKE',1,'06F','ANTHRACITE','AR-138','TMCS0052021073002','BLACK','VIRGIN HYDRO PU','A193','2021-07-31','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1630,'TAEKWANG',30,'NIKE',1,'04Z','PURE PLATINUM','AR-144M','TMTK0272021073101','WHITE','VIRGIN HDRO PU','A117','2021-07-31','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1631,'ADIS',1,'NIKE',1,'43G','GLACIER BLUE','AR-20','TMAD0022021073101','WHITE','VIRGIN HYDRO PU LEATHER','A493','2021-07-31','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1632,'VICTORY',31,'NIKE',1,'40W','PHOTO BLUE','DE-90','TMVC0052021110501','BLUE','VIRGIN HYDRO PU','A235','2021-11-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08','2026-05-19 03:12:09'),
(1633,'PANARUB',19,'ADIDAS',3,'AECY','MINT RUSH','DE-73','TMPA0202021082602','3GU','PU COATED LEATHER','A127','2021-08-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08','2026-05-19 03:12:08'),
(1634,'PANARUB',19,'ADIDAS',3,'AEDZ','TURBO','DE-73','TMPA0202021082601','RED','PU COATED LEATHER','A128','2021-09-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08','2026-05-19 03:12:08'),
(1635,'ADIS',1,'NIKE',1,'07G','LIGHT BONE','AR-73','TMAD0022021080501','WHITE','VIRGIN PU','A494','2021-08-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1636,'FENGTAY',8,'NIKE',1,'26U','MEDIUM ASH','R-8','TMFT0072021080602','BLACK','PM GENERIC PU COATED','A227','2021-08-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1637,'FENGTAY',8,'NIKE',1,'4EV','GAME ROYAL','AR-93','TMFT0072021080603','44Z','VIRGIN HYDRO PU','A228','2021-08-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1638,'FENGTAY',8,'NIKE',1,'6HE','HABANERO RED','AR-140','TMFT0072021080601','RED','PM GENERIC PU COATED','A229','2021-08-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1639,'KMK',15,'NIKE',1,'31B','MALACHITE','R-102','TMKM0012021080502','3GU','GENERIC PU COATED','A189','2021-08-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1640,'KMK',15,'NIKE',1,'26B','KHAKI','UM-39','TMKM0012021080501','WHITE','VIRGIN HYDRO PU','A190','2021-08-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1641,'KMK',15,'NIKE',1,'11K','SAIL','R-102 SM','TMKM0012021080503','WHITE','GENERIC PU COATED','A191','2021-08-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1642,'CHANGSHIN',3,'NIKE',1,'04Z','PURE PLATINUM','AR-144','TMCS0042021080201','WHITE','VIRGIN HYDRO PU','A195','2021-08-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1643,'TAEKWANG',30,'NIKE',1,'12J','SUMMIT WHITE','AR-144','TMTK0272021080601','WHITE','VIRGIN HDRO PU','A118','2021-08-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1644,'CHANGSHIN',4,'NIKE',1,'01X','PHANTOM','DE-126 SM','TMCS0052021080601','WHITE','PM GENERIC PU COATED','A196','2021-08-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1645,'ADIS',1,'NIKE',1,'0BB','PHOTON DUST','DE-73','TMAD0022021080601','WHITE','VIRGIN PU','A495','2021-08-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1646,'NIKOMAS IY',18,'NIKE',1,'6KI','CANYON RUSH','DE-90','TMNS0202021080601','80S','PM GENERIC PU COATED LEATHER','A983',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1647,'TAEKWANG',30,'NIKE',1,'12J','SUMMIT WHITE','AR-20','TMTK0272021080901','WHITE','ECO TECH COMFORT','A119','2021-08-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1648,'NIKOMAS IY',18,'NIKE',1,'50S','VENICE','R-8','TSNS0202021081401','WHITE','PM GENERIC PU COATED LEATHER','A984','2021-08-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1649,'FENGTAY',8,'NIKE',1,'29J','PEARL WHITE','AR-161 M','TMFT0072021081901','WHITE','PM GENERIC PU COATED','A230','2021-08-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1650,'ADIS',1,'NIKE',1,'12J','SUMMIT WHITE','DE-73','TMAD0022021081601','WHITE','VIRGIN HYDRO PU LEATHER','A496','2021-08-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1651,'NIKOMAS IY',18,'NIKE',1,'56S','ELECTRO PURPLE','R-8','TMNS0202021082002','PURPLE','PM GENERIC PU COATED LEATHER','A985','2021-08-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1652,'NIKOMAS IY',18,'NIKE',1,'37L','BRIGHT SPRUCE','R-8','TMNS0202021082003','33R','PM GENERIC PU COATED LEATHER','A986','2021-08-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1653,'NIKOMAS IY',18,'NIKE',1,'51A','DARK IRIS','DE-90','TMNS0202021082001','PURPLE','PM GENERIC PU COATED LEATHER','A987','2021-08-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1654,'FENGTAY',7,'NIKE',1,'0AJ','SMOKE GREY','UM-34','TMFT0062021082401','GREY','PM GENERIC PU COATED','A231','2021-08-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1655,'FENGTAY',7,'NIKE',1,'01X','PHANTOM','AR-167','TMFT0062021082403','WHITE','PM GENERIC PU COATED','A232','2021-08-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1656,'CHANGSHIN',4,'NIKE',1,'0AL','LT SMOKE GREY','AR-144','TMCS0052021082001','GREY','PM GENERIC PU COATED','A197','2021-08-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1657,'NIKOMAS',17,'ADIDAS',3,'AEK9','PULSE BLUE','DE-126','SCOTDIC','LT BLUE','SOFT PU COATED LEATHER (MAP-SOFT PU)','A696','2021-08-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1658,'NIKOMAS',17,'ADIDAS',3,'AEK6','WONDER OXIDE','DE-7','SCOTDIC','PINK','SOFT PU COATED LEATHER (MAP-SOFT PU)','A697','2021-08-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1659,'DEANSHOES',6,'UA',5,'001','BLACK','AR-216','CSI UA','BLACK','HYDRO ACTION LEATHER','A168','2021-08-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1660,'POUYUEN',24,'NIKE',1,'57I','LIGHT THISTLE','UM-16 SM','TSPY0282021082801','49D','PM GENERIC PU COATED LEATHER','A988','2021-08-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1661,'POUYUEN',24,'NIKE',1,'6JB','PINK FOAM','R-231','TSPY0282021082805','PINK','PM GENERIC PU COATED LEATHER','A989','2021-08-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1662,'POUYUEN',24,'NIKE',1,'6CD','BRIGHT CRIMSON','UM-16 SM','TSPY0282021082804','RED','PM GENERIC PU COATED LEATHER','A990','2021-08-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1663,'POUYUEN',24,'NIKE',1,'3AG','HONEYDEW','UM-16 SM','TSPY0282021082802','34A','PM GENERIC PU COATED LEATHER','A991','2021-08-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1664,'POUYUEN',24,'NIKE',1,'11M','COCONUT MILK','UM-16 SM','TSPY0282021082803','WHITE','PM GENERIC PU COATED LEATHER','A992','2021-08-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1665,'NIKOMAS',17,'ADIDAS',3,'AEDV','QUITE CRIMSON','DE-126','SCOTDIC','BROWN','SOFT PU COATED LEATHER (MAP-SOFT PU)','A698','2021-09-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1666,'NIKOMAS',17,'ADIDAS',3,'AEJV','BLISS BLUE','DE-126','SCOTDIC','4AU','SOFT PU COATED LEATHER (MAP-SOFT PU)','A699','2021-09-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1667,'DEANSHOES',6,'UA',5,'100','WHITE','AR-216','TMDS0262021090201','WHITE','HYDRO ACTION LEATHER','A169','2021-09-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1668,'CHANGSHIN',4,'NIKE',1,'3LQ','WASHED TEAL','R-131','TMCS0052021082801','4AU','GENERIC PU COATED','A199','2021-09-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1669,'NIKOMAS IY',18,'NIKE',1,'2FF','DESERT ORE','R-8','TMNS0202021090301','2CT','VIRGIN PU','A993','2021-09-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1670,'CHANGSHIN',4,'NIKE',1,'04Z','PURE PLATINUM','DE-7 SM','TMCS0052021092101','WHITE','PM GENERIC PU COATED','A206','2021-09-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08','2026-05-19 03:12:09'),
(1671,'CHANGSHIN',4,'NIKE',1,'0BB','PHOTON DUST','DE-7 SM','TMCS0052021092102','WHITE','PM GENERIC PU COATED','A207','2021-09-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08','2026-05-19 03:12:09'),
(1672,'FENGTAY (EAST)',8,'NIKE',1,'65N','UNIVERSITY RED','AR-20','TSFT0072021090701','RED','PM GENERIC PU COATED','A233','2021-09-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1673,'FENGTAY (WEST)',7,'NIKE',1,'31B','MALACHITE','R-102 M','TMFT0062021090901','3GU','GENERIC PU COATED','A234','2021-09-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1674,'FENGTAY (WEST)',7,'NIKE',1,'88M','MAGMA ORANGE','R-102','TMFT0062021090902','80S','GENERIC PU COATED','A235','2021-09-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1675,'HORNMING',13,'PUMA',NULL,'13-0905TCX','GRAY','AR-169','TMHI0242021090901','WHITE','SOFT PU COATED','A170','2021-09-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1676,'HORNMING',13,'PUMA',NULL,'11-0701 TCX','CREAMY WHITE','AR-169','TMHI0242021090902','WHITE','SOFT PU COATED','A171','2021-09-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1677,'PCN G8',59,'NIKE',1,'4PR','MYSTIC NAVY','AR-144','TSPG0212021091001','4MD','VIRGIN HYDRO PU LEATHER','A994','2021-09-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1678,'CHANGSHIN',3,'NIKE',1,'02Y','FLAT PEWTER','AR-144','TSCS0042021091402','GREY','VIRGIN HYDRO PU','A203','2021-09-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:08',NULL),
(1679,'FENGTAY',7,'NIKE',1,'4EV','GAME ROYAL','UM-34','TSFT0062021091401','44Z','GENERIC PU COATED','A236',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1680,'FENGTAY',8,'NIKE',1,'76I','UNIVERSITY GOLD','R-102','TSFT0072021091502','YELLOW','GENERIC PU COATED','A237',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1681,'FENGTAY',8,'NIKE',1,'11K','SAIL','R-102','TSFT0072021091503','WHITE','PM VIRGIN HYDRO','A238',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1682,'CHANGSHIN',3,'NIKE',1,'4PR','MYSTIC NAVY','AR-144','TSCS0042021091401','4MD','VIRGIN HYDRO PU','A204','2021-09-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1683,'PCN G8',59,'NIKE',1,'30X','CLOROPHYLL','R-8','TSPG0212021091601','33R','PM GENERIC PU COATED LEATHER','A995','2021-09-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1684,'PANARUB',19,'ADIDAS',3,'AD8R','TEAM ROYAL BLUE','DE-73','FOLLOW FMCA','44Z','PU COATED LEATHER','A130','2021-09-20','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1685,'CHANGSHIN',4,'NIKE',1,'04D','LIGHT SILVER','AR-144','TMCS0052021080201','WHITE','VIRGIN HYDRO PU','A205','2021-09-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1686,'NIKOMAS',17,'ADIDAS',3,'AEE1','SEMI TURBO','R-53','SCOTDIC','RED','SOFT PU COATED LEATHER (MAP-SOFT PU)','A700',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1687,'PANARUB',19,'ADIDAS',3,'AE6J','ORBIT GREEN','R-231','TMPA0202021092102','3MR','PU COATED LEATHER','A131','2021-09-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1688,'PANARUB',19,'ADIDAS',3,'AE66','BEIGE TONE','R-131','TMPA0202021092101','L.BROWN','PU COATED LEATHER','A132','2021-09-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1689,'FENGTAY',7,'NIKE',1,'3AG','HONEYDEW','UM-34','TSFT0062021092401','34A','GENERIC PU COATED','A239','2021-09-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1690,'ADIS',1,'NIKE',1,'10J','LT OREWOOD BROWN','DE-73','TMAD0022021092402','WHITE','PM GENERIC PU COATED','A497','2021-09-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1691,'ADIS',1,'NIKE',1,'0AN','GREY FOG','DE-73','TMAD0022021092401','WHITE','PM GENERIC PU COATED','A498','2021-09-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1692,'NIKOMAS IY',18,'NIKE',1,'49A','DUTCH BLUE','AR-161','TMNS0202021092901','BLUE','PM GENERIC PU COATED LEATHER','A996','2021-09-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1693,'POUYUEN',24,'NIKE',1,'0BB','PHOTON DUST','DE-73','TMPY0282021093001','WHITE','PM GENERIC PU COATED LEATHER','A997','2021-09-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1694,'FENGTAY',8,'NIKE',1,'4AH','AURA','UM-34','TMFT0072021092801','WHITE','GENERIC PU COATED','A240','2021-09-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1695,'FENGTAY',7,'NIKE',1,'49H','MEDIUM BLUE','R-131','TMFT0062021100101','44Z','VIRGIN HYDRO','A241','2021-10-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1696,'PCN G8',59,'NIKE',1,'86E','KUMQUAT','DE-126','TSPG0212021093001','2CT','PM GENERIC PU COATED LEATHER','A998','2021-10-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1697,'PANARUB',19,'ADIDAS',3,'ABZU','GREY SIX','R-131','SCOTDIC','BLACK','PU COATED LEATHER','A133','2021-10-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1698,'CHANGSHIN',4,'NIKE',1,'4AH','AURA','DE-7 SM','TMCS0052021100601','WHITE','PM GENERIC PU COATED','A208','2021-10-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1699,'NIKOMAS IY',18,'NIKE',1,'44B','MIDNIGHT NAVY','R-51','TMNS0202021100501','BLACK','PM GENERIC PU COATED','A999','2021-10-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1700,'POUYUEN',24,'NIKE',1,'86E','KUMQUAT','DE-125','TMPY0282021100702','2CT','PM GENERIC PU COATED','A1000','2021-10-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1701,'POUYUEN',24,'NIKE',1,'58C','LILAC','R-231','TMPY0282021100701','PINK','PM GENERIC PU COATED','A1001','2021-10-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1702,'PANARUB',19,'ADIDAS',3,'ADVX','HAZY COPPER','DE-73','SCOTDIC','80S','PU COATED LEATHER','A134','2021-10-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1703,'PARKLAND 2',21,'NB',4,'000-73-00','BRIGHTON GREY COLORO','R-131','FOLLOW COLORO','WHITE','HYDRO SOFT PU ACTION LEATHER','A374','2021-10-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1704,'PARKLAND 2',21,'NB',4,'145-17-00','BLACK COLORO','R-131','FOLLOW COLORO','BLACK','HYDRO SOFT PU ACTION LEATHER','A375','2021-10-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1705,'PARKLAND 2',21,'NB',4,'000-27-00','BLACK TOP COLORO','R-131','FOLLOW COLORO','BLACK','HYDRO SOFT PU ACTION LEATHER','A376','2021-10-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1706,'NIKOMAS IY',18,'NIKE',1,'04Z','PURE PLATINUM','AR-20','TMNS0202021101301','WHITE','ECO TECH COMFORT','A1002','2021-10-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1707,'PARKLAND',20,'NB',4,'119-45-01','TITANIUM COLORO','R-131','FOLLOW COLORO','GREY','HYDRO SOFT PU ACTION LEATHER','A377','2021-10-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1708,'FENGTAY (WEST)',7,'NIKE',1,'88U','LT MADDER ROOT','AR-121SG','TMFT0062021102501','PINK','PM GENERIC PU COATED','A242','2021-10-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1709,'FENGTAY (WEST)',7,'NIKE',1,'49H','MEDIUM BLUE','R-8','TMFT0062021102502','44Z','PM GENERIC PU COATED','A243','2021-10-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1710,'FENGTAY (WEST)',7,'NIKE',1,'88U','LT MADDER ROOT','AR-167','TMFT0062021102503','PINK','PM GENERIC PU COATED','A244','2021-10-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1711,'PARKLAND 3',22,'REEBOK',NULL,'AC4K','COLD GREY','R-30','TMPA0102021102501','WHITE','SOFT PU COATED LEATHER','A378','2021-10-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1712,'PARKLAND 3',22,'REEBOK',NULL,'AE8P','ALABASTER R-R','R-30','TMPA0102021102601','WHITE','SOFT PU COATED LEATHER','A379','2021-10-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1713,'KMK',15,'NIKE',1,'11K','SAIL','DE-7','TMKM0012021102501','WHITE','ECO TECH COMFORT','A192','2021-10-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1714,'SCI',32,'NIKE',1,'88U','LT MADDER ROOT','AW-44','TMSC0062021102801','PINK','VIRGIN HYDRO PU','A1003','2021-11-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1715,'HORNMING',13,'PUMA',NULL,'930C','YELLOW','DE-7','TMHI0242021102801','WHITE','SOFT PU COATED','A172','2021-11-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1716,'HORNMING',13,'PUMA',NULL,'14-0740TCX','YELLOW','UM-39','TMHI0242021102802','WHITE','SOFT PU COATED','A173','2021-11-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1717,'DEANSHOES (UA)',6,'UA',5,'400','ROYAL','AR-194','TMDS0262021110103','44Z','HYDRO ACTION LEATHER','A174','2021-11-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1718,'DEANSHOES (UA)',6,'UA',5,'001','BLACK','AR-194','TMDS0262021110101','BLACK','HYDRO ACTION LEATHER','A175','2021-11-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1719,'DEANSHOES (UA)',6,'UA',5,'014','HALO GRAY','AR-194','TMDS0262021110102','WHITE','HYDRO ACTION LEATHER','A176','2021-11-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1720,'DEANSHOES (UA)',6,'UA',5,'608','VERSA RED','AR-194','TMDS0262021110104','RED','HYDRO ACTION LEATHER','A177','2021-11-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1721,'ADIS',1,'NIKE',1,'5CA','IRIS WHISPER','AR-196','TMAD0022021110201','WHITE','PM GENERIC PU COATED','A499','2021-11-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1722,'ADIS',1,'NIKE',1,'88U','LT MADDER ROOT','DE-73','TMAD0022021110204','PINK','PM GENERIC PU COATED','A500','2021-11-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1723,'ADIS',1,'NIKE',1,'77G','SANDED GOLD','AR-196','TMAD0022021110203','2CT','PM GENERIC PU COATED','A501','2021-11-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1724,'ADIS',1,'NIKE',1,'28C','RATTAN','AR-196','TMAD0022021110202','WHITE','PM GENERIC PU COATED','A502','2021-11-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1725,'SHOETOWN',28,'NIKE',1,'74Y','LEMON VENOM','ESR-180-SK2','TMSL0432021110201','71R','PM GENERIC PU COATED','A1004','2021-11-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1726,'POUYUEN',24,'NIKE',1,'0AN','GREY FOG','UM-16 SM','TMPY0282021100101','WHITE','PM GENERIC PU COATED','A1005','2021-11-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1727,'NIKOMAS IY',18,'NIKE',1,'4AH','AURA','R-231','TMNS0202021110401','WHITE','PM GENERIC PU COATED','A1006','2021-11-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1728,'FENGTAY',8,'NIKE',1,'4PR','MYSTIC NAVY','UM-34T SM','TMFT0072021110801','BLACK','PM GENERIC PU COATED','A245','2021-11-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1729,'CHINGLUH',5,'NIKE',1,'4PB','ASHEN SLATE','R-53','TMCL0172021110501','L.BLUE','GENERIC PU COATED','A236','2021-11-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1730,'NIKOMAS IY',18,'NIKE',1,'05D','LT STEEL GREY','AR-140','TSNS0202021111002','01V','PM GENERIC PU COATED','A1007','2021-11-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1731,'NIKOMAS IY',18,'NIKE',1,'44W','FRENCH BLUE','AR-107','TSNS0202021111003','4MD','PM GENERIC PU COATED','A1008','2021-11-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1732,'NIKOMAS IY',18,'NIKE',1,'89N','BRILLIANT ORANGE','AR-185 HG','TSNS0202021111004','80S','GENERIC PU COATED','A1009','2021-11-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1733,'NIKOMAS IY',18,'NIKE',1,'12B','SANDDRIFT','DE-73 SM','TSNS0202021111001','WHITE','PM GENERIC PU COATED','A1010','2021-11-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1734,'ADIS',1,'NIKE',1,'78H','AMARILLO','DE-43','TMAD0022021111002','YELLOW','GENERIC PU COATED','A503','2021-11-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1735,'ADIS',1,'NIKE',1,'4PE','BLUE GAZE','DE-43','TMAD0022021111001','L.BLUE','GENERIC PU COATED','A504','2021-11-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1736,'NIKOMAS IY',18,'NIKE',1,'88M','MAGMA ORANGE','R-131','TMNS0202021111501','80S','PM GENERIC PU COATED','A1011','2021-11-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1737,'PANARUB',19,'ADIDAS',3,'AEST','BLUE DAWN','DE-73','SCOTDIC','L.BLUE','PU COATED LEATHER','A135','2021-11-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1738,'PANARUB',19,'ADIDAS',3,'AEJT','BLISH PINK','DE-73','SCOTDIC','PINK','PU COATED LEATHER','A136','2021-11-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1739,'PANARUB',19,'ADIDAS',3,'AET1','PINK STRATA','DE-73','SCOTDIC','PINK','PU COATED LEATHER','A137','2021-11-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1740,'CHANGSHIN',4,'NIKE',1,'05Q','FOOTBALL GREY','DE-90','TMCS0052021112002','WHITE','PM GENERIC PU COATED','A209','2021-11-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1741,'CHANGSHIN',4,'NIKE',1,'0AL','LT SMOKE GREY','DE-90','TMCS0052021112003','WHITE','PM GENERIC PU COATED','A210','2021-11-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1742,'CHANGSHIN',4,'NIKE',1,'05Q','FOOTBALL GREY','R-8','TMCS0052021112001','WHITE','PM GENERIC PU COATED','A211','2021-11-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1743,'SHOETOWN',28,'NIKE',1,'49A','DUTCH BLUE','AR-161','TMSL0432021111801','BLUE','PM GENERIC PU COATED','A1012','2021-11-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1744,'PCN G8',59,'NIKE',1,'05D','LT STEEL GREY','AR-140','TSPG0212021112902','WHITE','PM GENERIC PU COATED','A1013','2021-11-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1745,'FENGTAY TW',58,'NIKE',1,'25M','SESAME','R-8','TSFT0382021112901','WHITE','PM GENERIC PU COATED','A246','2021-11-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1746,'VICTORY',31,'NIKE',1,'50G','DARK CONCORK','R-53','TMVC0052021113001','58U','GENERIC PU COATED','A237','2021-12-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1747,'TAH SUNG HUNG',34,'ADIDAS',3,'AEJS','LINEN GREEN','DE-73','TSTS0012022020301','WHITE','PU COATED LEATHER','A708','2022-02-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09','2026-05-19 03:12:09'),
(1748,'ADIS',1,'NIKE',1,'25M','SESAME','DE-90','TMAD0022021120402','2CT','PM GENERIC PU COATED','A505','2021-12-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1749,'ADIS',1,'NIKE',1,'05Q','FOOTBALL GREY','DE-90','TMAD0022021120401','WHITE','PM GENERIC PU COATED','A506','2021-12-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1750,'POUYUEN',24,'NIKE',1,'73P','BARELY VOLT','UM-16','TSPY0282021121301','71R','PM GENERIC PU COATED','A1014','2021-12-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1751,'POUYUEN',24,'NIKE',1,'56X','VIOLET FROST','R-231','TSPY0282021121303','WHITE','PM GENERIC PU COATED','A1015','2021-12-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1752,'POUYUEN',24,'NIKE',1,'37L','BRIGHT SPRUCE','R-231','TSPY0282021121302','3AW','PM GENERIC PU COATED','A1016','2021-12-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1753,'SHOETOWN CINA',61,'NIKE',1,'80K','STARFISH','DE-7 SM','TSSL0442021121701','80S','PM GENERIC PU COATED','A1017','2021-12-20','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1754,'CHANGSHIN',4,'NIKE',1,'44B','MIDNIGHT NAVY','AR-144','TMCS0052022012901','BLACK','VIRGIN HYDRO PU','A224','2022-02-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09','2026-05-19 03:12:09'),
(1755,'CHANGSHIN',3,'NIKE',1,'6JB','PINK FOAM','AR-99 SM','TSCS0042021121703','PINK','PM GENERIC PU COATED','A213','2021-12-20','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1756,'CHANGSHIN',3,'NIKE',1,'88G','HOT CURRY','AR-144','TSCS0042021121701','80S','VIRGIN HYDRO PU','A214','2021-12-20','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1757,'SHOETOWN',28,'NIKE',1,'6GV','PARTICLE ROSE','DE-43 SM','TMSL0432021121501','PINK','VIRGIN PU','A1018','2021-12-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1758,'PARKLAND 2',21,'NB',4,'124-23-11','NB NAVY COLORO','AR-100','TMPW0102022070701','BLACK','HYDRO PU COATED LEATHER','A395','2022-07-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09','2026-05-19 03:12:10'),
(1759,'PARKLAND 2',21,'NB',4,'157-53-00','SHADOW GREY','AR-100','CSI COLORO','GREY','HYDRO PU COATED LEATHER','A382','2021-12-20','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1760,'PARKLAND 2',21,'NB',4,'028-64-06','MINDFUL GREY','AR-100','TMPW0102022070801','01V','HYDRO PU COATED LEATHER','A397','2022-07-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09','2026-05-19 03:12:10'),
(1761,'VICTORY',31,'NIKE',1,'64D','FIRE RED','R-53','TMVC0052021122001','RED','GENERIC PU COATED','A238','2021-12-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1762,'SCI',32,'NIKE',1,'0BB','PHOTON DUST','AR-167','TMSC0062021122001','WHITE','VIRGIN HYDRO PU','A1019','2021-12-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1763,'CHINGLUH',5,'NIKE',1,'75E','TAXI','R-53','TMCL0172022020402','2CT','GENERIC PU COATED','A240','2022-02-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09','2026-05-19 03:12:10'),
(1764,'TAH SUNG HUNG',34,'ADIDAS',3,'AEDK','ALTERED BLUE','DE-172 SM','SCOTDIC','BLUE','SOFT PU COATED LEATHER','A702','2021-12-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1765,'TAH SUNG HUNG',34,'ADIDAS',3,'A0RP','COLLEGIATE BURGUNDY','DE-172 SM','SCOTDIC','6DX','SOFT PU COATED LEATHER','A703','2021-12-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1766,'TAH SUNG HUNG',34,'ADIDAS',3,'AELB','MAGIC BERGE','DE-172 SM','SCOTDIC','2CT','SOFT PU COATED LEATHER','A704','2021-12-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1767,'FENGTAY (EAST)',8,'NIKE',1,'4NT','LECHE BLUE','DE-90','TMFT0072021122201','L.BLUE','VIRGIN PU','A247','2021-12-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1768,'SHOETOWN',28,'NIKE',1,'75E','TAXI','DE-7 SM','TMSL0432021122302','YELLOW','PM GENERIC PU COATED','A1020',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1769,'CHANGSHIN',4,'NIKE',1,'39Y','GORGE GREEN','AR-138','TMCS0052021122301','33R','VIRGIN HYDRO PU','A215','2021-12-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1770,'CHANGSHIN',4,'NIKE',1,'6CD','BRIGHT CRIMSON','AR-196','TMCS0052021122302','RED','PM GENERIC PU COATED','A216','2021-12-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1771,'CHANGSHIN',4,'NIKE',1,'2DH','MEDIUM OLIVE','AR-196','TMCS0052021122303','BLACK','PM GENERIC PU COATED','A217','2021-12-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1772,'CHANGSHIN',4,'NIKE',1,'25M','SESAME','AR-196','TMCS0052021122304','WHITE','PM GENERIC PU COATED','A218','2021-12-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1773,'SHOETOWN',28,'NIKE',1,'4NV','PHYCHIC BLUE','AR-161','TMSL0432021122301','L.BLUE','PM GENERIC PU COATED','A1021',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1774,'PCN G8',59,'NIKE',1,'6CV','HYPER PINK','R-8','TSPG0212021122703','WHITE','PM GENERIC PU COATED','A1022','2021-12-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1775,'POUYUEN',24,'NIKE',1,'3MJ','LIGHT MENTA','AR-99 SM','TMPY0282021122701','4AU','PM GENERIC PU COATED','A1023','2021-12-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1776,'PCN G8',59,'NIKE',1,'88G','HOT CURRY','R-8','TSPG0212021122701','WHITE','PM GENERIC PU COATED','A1024','2021-12-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1777,'PCN G8',59,'NIKE',1,'63E','MED SOFT PINK','R-8','TSPG0212021122702','WHITE','PM GENERIC PU COATED','A1025','2021-12-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1778,'PRATAMA',25,'NIKE',1,'11B','LIGHT STONE','AR-128','TSPT0122021122801','WHITE','VIRGIN HYDRO PU LEATHER','A477','2022-01-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1779,'PANARUB',19,'ADIDAS',3,'AET1','PINK STRATA','DE-73','FOLLOW FMCA','PINK','PU COATED LEATHER (MAP-ACTION LEATHER)','A138','2022-01-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1780,'CHANGSHIN RJ',4,'NIKE',1,'37L','BRIGHT SPRUCE','AR-138','TMCS0052021122901','WHITE','VIRGIN HYDRO PU','A219','2022-01-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1781,'CHANGSHIN RJ',4,'NIKE',1,'56X','VIOLET FROST','AR-196','TMCS0052021122902','WHITE','PM GENERIC PU COATED','A220','2022-01-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1782,'NIKOMAS IY',18,'NIKE',1,'3JJ','BARELY GREEN','UM-16 SM','TSNS0202021122801','WHITE','PM GENERIC PU COATED','A1026','2022-01-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1783,'POUYUEN',24,'NIKE',1,'3MJ','LIGHT MENTA','DE-73 SM','TMPY0282021122801','4AU','PM GENERIC PU COATED','A1027','2022-01-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1784,'ADIS',1,'NIKE',1,'6CD','BRIGHT CRIMSON','DE-73','TMAD0022021122904','RED','VIRGIN HYDRO PU','A507','2022-01-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1785,'ADIS',1,'NIKE',1,'25M','SESAME','DE-73 SM','TMAD0022021122905','2CT','VIRGIN HYDRO PU LEATHER','A508','2022-01-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1786,'ADIS',1,'NIKE',1,'4PB','ASHEN SLATE','AR-167 DM','TMAD0022021122901','LIGHT BLUE','PM GENERIC PU COATED','A509','2022-01-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1787,'ADIS',1,'NIKE',1,'58B','DOLL','AR-167 DM','TMAD0022021122902','WHITE','PM GENERIC PU COATED','A510','2022-01-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1788,'ADIS',1,'NIKE',1,'44B','MIDNIGHT NAVY','AR-167 DM','TMAD0022021122903','BLACK','PM GENERIC PU COATED','A511','2022-01-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1789,'TAH SUNG HUNG',34,'ADIDAS',3,'AD8R','TEAM ROYAL BLUE','DE-73 SM','TMTS0012021122901','44Z','PU COATED LEATHER (MAP-ACTION LEATHER)','A705','2022-01-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1790,'TAEKWANG',30,'NIKE',1,'88G','HOT CURRY','AR-144','TMTK0272022010401','80S','VIRGIN HDRO PU','A120','2022-01-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1791,'SHOETOWN',28,'NIKE',1,'36Z','VIVID GREEN','AR-161','TMSL0432022010401','34A','PM GENERIC PU COATED','A1028','2022-01-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1792,'NIKOMAS IY',18,'NIKE',1,'44B','MIDNIGHT NAVY','AR-138','TMNS0202022010501','BLACK','ECO TECH COMFORT','A1029','2022-01-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1793,'CHANGSHIN RJ',4,'NIKE',1,'37L','BRIGHT SPRUCE','AR-196','TMCS0052022010601','3AW','PM GENERIC PU COATED','A221','2022-01-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1794,'ADIS',1,'NIKE',1,'88G','HOT CURRY','UM-14 SG','TMAD0022022010701','80S','VIRGIN PU','A512','2021-01-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1795,'ADIS',1,'NIKE',1,'40H','LASER BLUE','R-231','TMAD0022022010702','44Z','PM GENERIC PU COATED','A513','2021-01-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1796,'NIKOMAS IY',18,'NIKE',1,'0AN','GREY FOG','B-92','TMNS0202022011001','WHITE','GENERIC PU COATED','A1030','2022-01-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1797,'PRATAMA JX',26,'NIKE',1,'0BB','PHOTON DUST','UMT','TMPT0132022011201','WHITE','VIRGIN HYDRO PU LEATHER','A478','2022-01-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1798,'PARKLAND 3',22,'ADIDAS',3,'AE8M','CHALK-R','R-53','TMPA0102022010701','WHITE','SOFT PU COATED LEATHER','A384','2022-01-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1799,'ADIS',1,'NIKE',1,'25M','SESAME','UM-34','TMAD0022022011401','2CT','VIRGIN HYDRO PU','A514','2022-01-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1800,'ADIS',1,'NIKE',1,'6JF','PINK GAZE','DE-73 SM','TMAD0022022010703','PINK','(PM) GENERIC PU COATED','A515','2022-01-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1801,'NIKOMAS',17,'ADIDAS',3,'AE6K','FOKUS ORANGE F21','DE-7','SCOTDIC','2CT','SOFT PU COATED LEATHER','A706','2022-01-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1802,'NIKOMAS IY',61,'NIKE',1,'64D','FIRED RED','R-8','TSSL0442022010501','RED','GENERIC PU COATED','A 1031','2022-01-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1803,'FENGTAY (EAST)',8,'NIKE',1,'4KY','THUNDER BLUE','UM-34T SM','TSFT0072022012601','BLACK','PM GENERIC PU COATED','A248','2022-01-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1804,'ADIS',1,'NIKE',1,'74F','WHEAT','UM-34 SM','TMAD0022022012601','2CT','VIRGIN HYDRO PU','A516','2022-01-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1805,'TAEKWANG',30,'NIKE',1,'47N','UNIVERSITY BLUE','AR-185 HG','TMTK0272022012501','BLUE','GENERIC PU COATED','A121','2022-01-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1806,'TAEKWANG',30,'NIKE',1,'6JB','PINK FOAM','AR-185 HG','TMTK0272022012002','PINK','GENERIC PU COATED','A122','2022-01-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1807,'TAEKWANG',30,'NIKE',1,'89N','BRILLIANT ORANGE','AR-185 HG','TMTK0272022012001','80S','GENERIC PU COATED','A123','2022-01-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1808,'FENGTAY (WEST)',7,'NIKE',1,'25M','SESAME','AR-121','TMFT0062022012802','WHITE','VIRGIN HYDRO PU LEATHER','A249','2022-02-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1809,'FENGTAY (WEST)',7,'NIKE',1,'63E','MED SOFT PINK','UM-34T SM','TMFT0062022012801','PINK','PM GENERIC PU COATED','A250','2022-02-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1810,'FENGTAY (WEST)',8,'NIKE',1,'74G','YELLOW OCHER','UM-34T SM','TMFT0072022012701','YELLOW','PM GENERIC PU COATED','A251','2022-02-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1811,'CHANGSHIN RJ',4,'NIKE',1,'6JB','PINK FOAM','AR-196','TMCS0052022012903','RED','PM GENERIC PU COATED','A222','2022-02-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1812,'CHANGSHIN RJ',4,'NIKE',1,'6JB','PINK FOAM','AR-99 SM','TMCS0052022012902','PINK','PM GENERIC PU COATED','A223','2022-02-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1813,'TAH SUNG HUNG',34,'ADIDAS',3,'AA2V','GREY FIVE','DE-73','TSTS0012022020305','BLACK','PU COATED LEATHER','A707','2022-02-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1814,'TAH SUNG HUNG',34,'ADIDAS',3,'08S1','OFF WHITE','DE-73','TSTS0012022020303','WHITE','PU COATED LEATHER','A709','2022-02-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:09',NULL),
(1815,'TAH SUNG HUNG',34,'ADIDAS',3,'AAJL','ECRU TINT','DE-73','TSTS0012022020302','WHITE','PU COATED LEATHER','A710','2022-02-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1816,'TAH SUNG HUNG',34,'ADIDAS',3,'AEJR','ALMOST BLUE','DE-73','TSTS0012022020304','WHITE','PU COATED LEATHER','A711','2022-02-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1817,'CHINGLUH',5,'NIKE',1,'64D','FIRE RED','R-53','TMCL0172022030201','RED','GENERIC PU COATED','A243','2022-03-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10','2026-05-19 03:12:10'),
(1818,'ADIS',1,'NIKE',1,'4NC','ROYAL TINT','AR-107','TSAD0022022020701','WHITE','VIRGIN HYDRO PU','A517','2022-02-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1819,'TAH SUNG HUNG',34,'ADIDAS',3,'A0TP','CREAMY WHITE','DE-172','TSTS0012022020801','WHITE','SOFT PU COATED LEATHER','A712','2022-02-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1820,'FENGTAY (WEST)',7,'NIKE',1,'0AN','GREY FOG','AR-121','TMFT0062022020901','01V','VIRGIN HYDRO PU LEATHER','A252','2022-02-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1821,'TAH SUNG HUNG',34,'ADIDAS',3,'A091','SCARLET','DE-172','TMTS0012022021101','RED','SOFT PU COATED LEATHER','A713','2022-02-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1822,'PANARUB',19,'ADIDAS',3,'ADVX','HAZY COPPER','DE-73','FOLLOW FMCA','80S','PU COATED LEATHER (MAP-ACTION LEATHER)','A139','2022-02-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1823,'POUYUEN',24,'NIKE',1,'86R','CITRON TINT','R-231','TSPY0282022021501','71R','PM GENERIC PUM COATED','A1032','2022-02-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1824,'NIKOMAS IY',18,'NIKE',1,'12B','SANDRIFT','AR-161','TMNS0202022021601','WHITE','PM GENERIC PUM COATED','A1033','2022-02-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1825,'NIKOMAS IY',18,'NIKE',1,'6LC','PICANTE RED','R-8','TSNS0202022021601','RED','ECO TECH COMFORT','A1034','2022-02-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1826,'CHANGSHIN RJ',4,'NIKE',1,'2EU','MOON PARTICLE','AR-161','TMCS0052022021601','01V','PM GENERIC PU COATED','A226','2022-02-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1827,'HORNMING',13,'PUMA',NULL,'11-4300TCX','MILK','DE-7','TMHI0242022022201','WHITE','SOFT PU COATED','A180','2022-02-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1828,'PCN G8',59,'NIKE',1,'64D','FIRED RED','R-53','TSPG0212022022301','RED','VIRGIN HYDRO PU LEATHER','A1035','2022-02-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1829,'TAH SUNG HUNG',34,'ADIDAS',3,'AEDK','ALTERED BLUE','DE-172','FMCA','BLUE','SOFT PU COATED LEATHER','A724','2022-04-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10','2026-05-19 03:12:10'),
(1830,'METRO',16,'NB',4,'076-94-00','WHITE','AR-100','FOLLOW COLORO','WHITE','HYDRO SOFT PU COATED LEATHER','M031','2022-02-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1831,'TAH SUNG HUNG',34,'ADIDAS',3,'AELB','MAGIC BEIGE','DE-172','FMCA','BROWN','SOFT PU COATED LEATHER','A721','2022-03-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10','2026-05-19 03:12:10'),
(1832,'CHINGLUH',31,'NIKE',1,'04Z','PURE PLATINUM','R-131','TMVC0052022030701','WHITE','VIRGIN HYDRO PU','A242','2022-03-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1833,'CHANGSHIN',3,'NIKE',1,'4EW','RUSH BLUE','R-131','TMCS0042022030701','44Z','GENERIC PU COATED LEATHER','A227','2022-03-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1834,'CHANGSHIN',3,'NIKE',1,'67P','TEAM RED','R-131','TMCS0042022030702','RED','GENERIC PU COATED LEATHER','A228','2022-03-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1835,'PANARUB',19,'ADIDAS',3,'AEJT','BLISS PINK','DE-73','FOLLOW FMCA','PINK','PU COATED LEATHER (MAP-ACTION LEATHER)','A140','2022-03-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1836,'CHANGSHIN',3,'NIKE',1,'79H','TOUR YELLOW','R-131','TMCS0042022030704','YELLOW','GENERIC PU COATED LEATHER','A229','2022-03-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1837,'CHANGSHIN',3,'NIKE',1,'4NP','HYPER ROYAL','R-131','TMCS0042022030703','44Z','GENERIC PU COATED LEATHER','A230','2022-03-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1838,'SENGDAM',35,'NB',4,'NB-S18-4459','PRISM PURPLE','AR-100','FOLLOW CSI','PURPLE','HYDRO PU COATED LEATHER','A385','2022-03-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1839,'PANARUB',19,'ADIDAS',3,'AEST','BLUE DAWN','DE-73','FOLLOW FMCA','L.BLUE','PU COATED LEATHER (MAP-ACTION LEATHER)','A141','2022-03-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1840,'PCN G8',59,'NIKE',1,'50G','DARK CONCORD','R-53','TSPG0212022031001','44Z','VIRGIN HYDRO PU LEATHER','A1036','2022-03-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1841,'TAH SUNG HUNG',34,'ADIDAS',3,'A0RP','COLLEGIATE BURGUNDY','DE-172','TSTS0012022030401','RED','SOFT PU COATED LEATHER','A718','2022-03-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1842,'SENGDAM',35,'NB',4,'NB-S18-4469','NB BURGUNDY','AR-100','FOLLOW CSI','RED','HYDRO PU COATED LEATHER','A386','2022-03-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1843,'PCN G8',59,'NIKE',1,'4QG','VALERIAN BLUE','AR-144','TSPG0212022031501','4MD','VIRGIN HYDRO PU LEATHER','A1037','2022-03-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1844,'PCN G8',59,'NIKE',1,'01X','PHANTOM','AR-144','TSPG0212022031502','WHITE','VIRGIN HYDRO PU LEATHER','A1038','2022-03-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1845,'SHOETOWN',28,'NIKE',1,'50G','DARK CONCORD','R-53','TMSL0432022031501','44Z','VIRGIN HYDRO PU LEATHER','A1039','2022-03-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1846,'HORNMING',13,'PUMA',NULL,'11-4300TCX','MILK','AR-169','TMHI0242022031401','WHITE','HYDRO ECO TECH COMFORT','A181','2022-03-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1847,'PARKLAND 2',21,'NB',4,'NB-F17-2422','PHANTOM','UM-11','TMPW0102022031401','BLACK','HYDRO ACTION LEATHER','A387','2022-03-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1848,'PANARUB',19,'ADIDAS',3,'A61T','CLEAR BROWN','DE-73','FOLLOW FMCA','WHITE','SOFT PU COATED LEATHER','A142','2022-03-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1849,'SENGDAM',35,'NB',4,'NB-S19-2719','SUMMER FOG','AR-100','FOLLOW CSI','WHITE','HYDRO PU COATED LEATHER','A388','2022-03-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1850,'PANARUB',19,'ADIDAS',3,'AETG','BETTER SCARLET','DE-172','FMCA','RED','SOFT PU COATED LEATHER','A145','2022-03-31','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10','2026-05-19 03:12:10'),
(1851,'CHANGSHIN',4,'NIKE',1,'42X','SOAR','DE-73','TMCS0052022040501','BLUE','GENERIC PU COATED LEATHER','A233','2022-04-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10','2026-05-19 03:12:10'),
(1852,'ADIS',1,'NIKE',1,'56X','VIOLET FROST','R-8','TMAD0022022031601','WHITE','VIRGIN HYDRO PU','A518','2022-03-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1853,'KMK',15,'NIKE',1,'2FI','LIGHT CREAM','AR-161','TMKM0012022031801','WHITE','GENERIC PU COATED','A193','2022-03-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1854,'PCN G8',59,'NIKE',1,'25M','SEASAME','R-101','TSPG0212022032101','2CT','ECO TECH COMFORT','A1040','2022-03-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1855,'CHINGLUH',31,'NIKE',1,'50G','DARK CONCORT','R-53','TSVC0052022032201','58U','GENERIC PU COATED','A244','2022-03-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1856,'VICTORY',31,'NIKE',1,'3LY','NEPTUNE GREEN','AR-193','TMVC0052022032801','3GU','GENERIC PU COATED','A245','2022-03-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1857,'VICTORY',31,'NIKE',1,'11M','COCONUT MILK','AR-193','TMVC0052022032802','WHITE','GENERIC PU COATED','A246','2022-03-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1858,'SCI',32,'NIKE',1,'01B','METALLIC SILVER','AR-20','TMSC0062022032801','WHITE','PM GENERIC PU COATED','A1041','2022-03-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1859,'HORNMING',13,'PUMA',NULL,'15-1058TCX','ORANGE','AR-169','TMHI0242022032801','WHITE','SOFT PU COATED','A182','2022-03-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1860,'VICTORY',31,'NIKE',1,'50G','DARK CONCORT','R-53','TMVC0052022041301','44Z','VIRGIN HYDRO PU LEATHER','A248','2022-04-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10','2026-05-19 03:12:10'),
(1861,'PANARUB',19,'ADIDAS',3,'AA2R','GREY ONE','DE-172','FMCA','01V','SOFT PU COATED LEATHER','A144','2022-03-31','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1862,'SHOETOWN',28,'NIKE',1,'01B','METALLIC SILVER','AR-128','TMSL0432022040101','WHITE','PM GENERIC PU COATED','A1042','2022-04-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1863,'NIKOMAS IY',18,'NIKE',1,'0AN','GREY FOG','AR-201','TMNS0202022033101','WHITE','VIRGIN HYDRO','A1043','2022-04-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1864,'CHANGSHIN',4,'NIKE',1,'56X','VIOLET FROST','AR-138','TMCS0052022033101','WHITE','VIRGIN HYDRO PU','A232','2022-04-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1865,'NIKOMAS',17,'ADIDAS',3,'A0TP','CREAM WHITE','DE-126','TMNS0162022040502','WHITE','SOFT PU COATED LEATHER','A722','2022-04-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1866,'NIKOMAS',17,'ADIDAS',3,'08S1','OFF WHITE','DE-73','TMNS0162022040501','WHITE','HYDRO ECO TECH COMFORT','A723','2022-04-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1867,'PARKLAND 2',21,'NB',4,'NB102','WHITE MUNSELL','AR-100','TMPW0102022040501','WHITE','HYDRO PU COATED LEATHER','A388','2022-04-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1868,'POUYUEN',24,'NIKE',1,'4ME','RACER BLUE','R-8','TMPY0282022040801','44Z','VIRGIN PU','A1044','2022-04-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1869,'PANARUB',19,'ADIDAS',3,'AA2S','GREY TWO','DE-73','FMCA','GREY','SOFT PU COATED LEATHER','A146','2022-04-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1870,'PANARUB',19,'ADIDAS',3,'076A','CORE WHITE','DE-7','FMCA','WHITE','SOFT PU COATED LEATHER','A147','2022-04-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1871,'PANARUB',19,'ADIDAS',3,'AAYC','CLOUD WHITE','AR-196','FMCA','WHITE','SOFT PU COATED LEATHER','A148','2022-04-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1872,'VICTORY',31,'NIKE',1,'04Z','PURE PLATINUM','R-131','TMVC0052022041202','WHITE','VIRGIN HYDRO','A249','2022-04-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1873,'TAEKWANG',30,'NIKE',1,'4QG','VALERIAN BLUE','AR-144','TMTK0272022041201','4MD','VIRGIN HYDRO PU LEATHER','A124','2022-04-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1874,'CHANGSHIN',3,'NIKE',1,'01X','PHANTOM','AR-144','TSCS0042022041402','WHITE','VIRGIN HYDRO PU','A234','2022-04-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1875,'CHANGSHIN',3,'NIKE',1,'4QG','VALERIAN BLUE','AR-144','TSCS0042022041401','4MD','VIRGIN HYDRO PU','A235','2022-04-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1876,'FENGTAY',7,'NIKE',1,'66T','PINK OXFORD','AR-167','TMFT0062022041402','PINK','GENERIC PU COATED','A253','2022-04-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1877,'FENGTAY',7,'NIKE',1,'66T','PINK OXFORD','AR-121 SG','TMFT0062022041401','PINK','GENERIC PU COATED','A254','2022-04-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1878,'TAH SUNG HUNG',34,'ADIDAS',3,'AEK9','PULSE BLUE','DE-73','TMTS0012022052301','44Z','PU COATED LEATHER','A729','2022-05-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10','2026-05-19 03:12:10'),
(1879,'KMK',15,'NIKE',1,'33D','ARMY OLIVE','R-8','TMKM0012022041802','33R','PM GENERIC PU COATED','A194','2022-04-20','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1880,'KMK',15,'NIKE',1,'2DH','MEDIUM OLIVE','AR-167','TMKM0012022041803','LIGHT BROWN','PM GENERIC PU COATED','A195','2022-04-20','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1881,'KMK',15,'NIKE',1,'62E','LIGHT PINK','AR-167','TMKM0012022041801','WHITE','PM GENERIC PU COATED','A196','2022-04-20','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1882,'TAH SUNG HUNG',34,'ADIDAS',3,'A0RP','COLLEGIATE BURGUNDY','DE-172','FMCA','RED','PU COATED LEATHER','A726','2022-04-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1883,'NIKOMAS',17,'ADIDAS',3,'AE63','VICTORY CRIMSON','DE-73','TMNS0162022042001','BROWN','SOFT PU','A727','2022-04-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1884,'FENGTAY TW',58,'NIKE',1,'88I','MONARCH','R-8','TSFT0382022042301','80S','GENERIC PU COATED','A255','2022-04-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1885,'FENGTAY TW',8,'NIKE',1,'04Z','PURE PLATINUM','DE-90','TMFT0072022042701','WHITE','VIRGIN HYDRO PU','A256','2022-04-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1886,'SCI',32,'NIKE',1,'01B','METALLIC SILVER','AR-196','TMSC0062022053101','WHITE','PM GENERIC PU COATED','A1048','2022-05-31','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10','2026-05-19 03:12:10'),
(1887,'ADIS',1,'NIKE',1,'4QZ','BLUE LIGHTNING','B-27','TMAD0022022051201','4JE','VIRGIN HYDRO PU','A519','2022-05-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1888,'PARKLAND 2',59,'NB',4,'076-94-00','COLORO WHITE','AR-221','TSPG0212022051201','WHITE','HYDRO SEMI FULL GRAIN','A389','2022-05-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1889,'KMK',15,'NIKE',1,'6BA','NIGHT MAROON','DE-73','TMKM0012022051401','PURPLE','PM GENERIC PU COATED','A197','2022-05-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1890,'VICTORY',31,'NIKE',1,'06B','COOL GREY','DE-43','TMVC0052022051301','GREY','VIRGIN HYDRO','A250','2022-05-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1891,'PANARUB',19,'ADIDAS',3,'AEJP','ALMOST YELLOW','DE-7','FMCA','YELLOW','SOFT PU COATED LEATHER','A151','2022-06-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10','2026-05-19 03:12:10'),
(1892,'NIKOMAS',17,'ADIDAS',3,'057A','BROWN','CPUG','TMNS0162022090901','BROWN','BABY SOFT PATENT LEATHER','A747','2022-09-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10','2026-05-19 03:12:11'),
(1893,'POUYUEN/SHOETOWN/PCN',59,'NIKE',1,'44M','AQUATONE','R-53','FOLLOW SAMPLE YONGIL','4JE','GENERIC PU COATED LEATHER','A1046','2022-05-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1894,'ADIS',1,'NIKE',1,'62E','LIGHT SOFT PINK','R-8','TMAD0022022051903','WHITE','VIRGIN HYDRO PU','A520','2022-05-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1895,'SMJ',36,'NIKE',1,'3MF','GREEN NOISE','AR-128','TMPT0142022051901','3GU','VIRGIN HYDRO','A1047','2022-05-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1896,'VICTORY',31,'NIKE',1,'04B','CEMENT GREY','R-53','TMVC0052022052002','GREY','VIRGIN HYDRO','A251','2022-05-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1897,'TAEKWANG',30,'NIKE',1,'05V','LT IRON ORE','AR-185 HG','TMTK0272022052001','01V','GENERIC PU COATED','A125','2022-05-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1898,'VICTORY',31,'NIKE',1,'64D','FIRE RED','R-53','TMVC0052022052001','RED','VIRGIN HYDRO','A252','2022-05-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1899,'VICTORY',31,'NIKE',1,'02Y','FLAT PEWTER','AR-169','TMVC0052022051901','GREY','VIRGIN HYDRO','A253','2022-05-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1900,'CHANGSHIN',3,'NIKE',1,'06F','ANTHRACITE','UM-34','TMCS0042022051801','BLACK','VIRGIN HYDRO PU','A236','2022-05-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1901,'VICTORY',31,'NIKE',1,'60F','PEAR PINK','AR-169','TMVC0052022052501','WHITE','VIRGIN HYDRO','A254','2022-05-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1902,'VICTORY',31,'NIKE',1,'44M','AQUATONE','R-53','TMVC0052022052502','4JE','GENERIC PU COATED','A255','2022-05-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1903,'VICTORY',31,'NIKE',1,'38W','LUCKY GREEN','R-53','TMVC0052022090101','3GU','GENERIC PU COATED','A256','2022-05-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1904,'KMK',15,'NIKE',1,'44B','MIDNIGHT NAVY','DE-73','TMKM0012022052701','BLACK','PM GENERIC PU COATED','A198','2022-05-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1905,'TAH SUNG HUNG',34,'ADIDAS',3,'AD8T','TEAM DARK GREEN','DE-73','SCOTDIC','33R','PU COATED LEATHER','A730','2022-06-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1906,'TAH SUNG HUNG',34,'ADIDAS',3,'AET2','PRELOVED RED','DE-172','SCOTDIC','RED','SOFT PU COATED LEATHER','A731','2022-06-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1907,'VICTORY',31,'NIKE',1,'43K','TRUE BLUE','R-53','TMVC0052022060201','44Z','VIRGIN HYDRO','A257','2022-06-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1908,'VICTORY',31,'NIKE',1,'27W','PALOMINO','R-53','TMVC0052022060202','LT BROWN','VIRGIN HYDRO','A258','2022-06-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1909,'VICTORY',31,'NIKE',1,'64D','FIRE RED','R-8','TSVC0052022060602','RED','GENERIC PU COATED','A259','2022-06-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10','2026-05-19 03:12:10'),
(1910,'ADIS',1,'NIKE',1,'66B','PINK FOIL','AR-100','TMAD0022022060901','6DX','VIRGIN PU','A522','2022-06-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1911,'PANARUB',19,'ADIDAS',3,'A1U3','SOLAR GREEN','AR-175','SCOTDIC','34A','SOFT PU COATED LEATHER','A150','2022-06-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1912,'CHINGLUH',5,'NIKE',1,'67M','CHERRYWOOD RED','R-53','TMCL0172022060801','PURPLE','GENERIC PU COATED','A260','2022-06-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1913,'FENGTAY TW',58,'NIKE',1,'65N','UNIVERSITY RED','CPUG','TSFT0382022061301','RED','VIRGIN HYDRO PU','A257','2022-06-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1914,'ADIS',1,'NIKE',1,'6HJ','ACTIVE FUCHSIA','B-27','TMAD0022022061001','6DX','VIRGIN HYDRO PU','A523','2022-06-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1915,'SHOETOWN',28,'NIKE',1,'64D','FIRE RED','R-53','TMSL0432022061001','RED','VIRGIN HYDRO PU','A1049','2022-03-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1916,'POUYUEN',24,'NIKE',1,'27W','PALOMINO','R-53','TSPY0282022061501','L.BROWN','VIRGIN HYDRO PU','A1050','2022-06-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1917,'CHANGSHIN RJ',4,'NIKE',1,'2CQ','VELVET BROWN','R-8','TMCS0052022061501','PURPLE','PM GENERIC PU COATED','A237','2022-06-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1918,'POUYUEN',24,'NIKE',1,'64D','FIRED RED','R-53','TMPY0282022061501','RED','VIRGIN HYDRO PU','A1051','2022-06-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1919,'FENGTAY (EAST)',8,'NIKE',1,'87T','ORANGE TRANCE','DE-90','TMFT0072022061501','2CT','VIRGIN HYDRO PU','A258','2022-06-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1920,'CHANGSHIN',3,'NIKE',1,'60F','PEARL PINK','AR-144','TSCS0042022061602','WHITE','VIRGIN HYDRO PU','A238','2022-06-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1921,'CHANGSHIN',3,'NIKE',1,'40X','BALTIC BLUE','AR-144','TSCS0042022061603','GREY','VIRGIN HYDRO PU','A239','2022-06-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1922,'PARKLAND 2',21,'NB',4,'157-53-00 COLORO','SHADOW GREY','AR-100','TMPW0102022061702','GREY','HYDRO PU COATED LEATHER','A391','2022-06-20','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1923,'PARKLAND 2',21,'NB',4,'145-17-00 COLORO','BLACK','AR-100','TMPW0102022061701','BLACK','HYDRO COATED LEATHER','A392','2022-06-20','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1924,'PANARUB',19,'ADIDAS',3,'ADAT','ALUMINA','DE-73','FMCA','WHITE','PU COATED LEATHER','A152','2022-06-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1925,'CHANGSHIN',3,'NIKE',1,'4NR','DIFFUSED BLUE','AR-144','TSCS0042022061601','4MD','VIRGIN HYDRO PU','A240','2022-06-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1926,'FENGTAY (EAST)',9,'NIKE',1,'12J','SUMMITH WHITE','AR-99 SM','TMFT0082022062301','WHITE','GENERIC PU COATED','A259','2022-06-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1927,'FENGTAY (EAST)',9,'NIKE',1,'01X','PHANTOM','AR-144','TMFT0082022062302','WHITE','VIRGIN HYDRO PU','A260','2022-06-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1928,'PANARUB',19,'ADIDAS',3,'AEDQ','SHADOW RED','DE-7','SCOTDIC','BROWN','PU COATED LEATHER','A153','2022-06-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1929,'PARKLAND 2',21,'NB',4,'028-59-26','CANYON','AR-191','COLORO','2CT','HYDRO COATED LEATHER','A393','2022-06-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1930,'CHANGSHIN',3,'NIKE',1,'4NW','LAGOON PULSE','UM-34','TMCS0042022070701','LT BLUE','VIRGIN HYDRO PU','A243','2022-07-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10','2026-05-19 03:12:10'),
(1931,'POUYUEN',24,'NIKE',1,'40X','BALTIC BLUE','AR-144','TMPY0282022072001','GREY','VIRGIN HYDRO PU','A1058','2022-07-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10','2026-05-19 03:12:11'),
(1932,'NIKOMAS IY',18,'NIKE',1,'6FX','TRACK RED','R-8','TMNS0202022062702','80S','ECO TECH COMFORT','A1053','2022-06-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1933,'NIKOMAS IY',18,'NIKE',1,'47X','DEEP ROYAL BLUE','R-51','TMNS0202022062701','44Z','ECO TECH COMFORT','A1054','2022-06-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1934,'TAEKWANG',30,'NIKE',1,'11K','SAIL','R-53','TMTK0272022062701','WHITE','VIRGIN HYDRO PU','A126','2022-06-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1935,'FENGTAY',8,'NIKE',1,'6JT','COSMIC FUCHSIA','UM-34','TMFT0072022062801','6DX','GENERIC PU COATED','A261','2022-06-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1936,'TAH SUNG HUNG',34,'ADIDAS',3,'A8L4','TALK','DE-73','SCOTDIC','WHITE','SOFT PU COATED LEATHER','A733','2022-06-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1937,'VICTORY',31,'NIKE',1,'64M','VARSITY RED','R-8','TMVC0052022070101','RED','VIRGIN HYRDO PU','A261','2022-07-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1938,'KMK',15,'NIKE',1,'40X','BALTIC BLUE','AR-161','TMKM0012022062701','4JE','PM GENERIC PU COATED','A199','2022-07-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1939,'TAEKWANG',30,'NIKE',1,'60F','PEARL PINK','AR-20','TMTK0272022063001','WHITE','ECO TECH COMFORT','A127','2022-07-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1940,'NIKOMAS IY',18,'NIKE',1,'67B','CRIMSON','AR-100','TMNS0202022070401','RED','PM GENERIC PU COATED','A1055','2022-07-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1941,'FENGTAY',9,'NIKE',1,'81J','SAFETY ORANGE','AR-20','TMFT0082022070101','WHITE','GENERIC PU COATED','A262','2022-07-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1942,'TAEKWANG',30,'NIKE',1,'60F','PEARL PINK','AR-144','TMTK0272022070401','WHITE','VIRGIN HYDRO PU','A128','2022-07-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1943,'DIAMOND INTERNATIONAL',38,'NB',4,'076-94-00','WHITE COLORO','AR-100','TMDI0242022070101','WHITE','HYDRO SOFT PU COATED LEATHER','A394','2022-07-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1944,'PARKLAND 2',21,'NB',4,'076-94-00','WHITE COLORO','R-134','TMPW0102022070702','WHITE','HYDRO SOFT PU COATED LEATHER','A396','2022-07-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1945,'VICTORY',31,'NIKE',1,'64D','FIRE RED','R-53','TMVC0052022070601','RED','VIRGIN HYRDO PU LEATHER','A263','2022-07-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1946,'CHANGSHIN',4,'NIKE',1,'07G','LIGHT BONE','AR-138','TMCS0052022070701','WHITE','VIRGIN HYDRO PU','A242','2022-07-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1947,'PANARUB',19,'ADIDAS',3,'54F0','COLLEGIATE NAVY','DE-73','FMCA','BLACK','PU COATED LEATHER','A154','2022-07-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1948,'PANARUB',19,'ADIDAS',3,'A0RP','COLLEGIATE BURGUNDY','DE-73','FMCA','RED','PU COATED LEATHER','A155','2022-07-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1949,'TAH SUNG HUNG',34,'ADIDAS',3,'329A','CLEAR ONIX','R-53','SCOTDIC','01V','PU COATED LEATHER','A734','2022-07-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10',NULL),
(1950,'TAH SUNG HUNG',34,'ADIDAS',3,'A0TP','CREAM WHITE','R-53','FMCA','WHITE','PU COATED LEATHER','A736','2022-07-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:10','2026-05-19 03:12:11'),
(1951,'NIKOMAS IY',18,'NIKE',1,'25M','SEASAME','DE-146','TMNS0202022071801','2CT','PM GENERIC PU COATED','A1056','2022-07-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1952,'CHANGSHIN',3,'NIKE',1,'4NQ','COBALT BLISS','AR-144','TMCS0042022070702','LT BLUE','VIRGIN HYDRO PU','A244','2022-07-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1953,'FENGTAY',9,'NIKE',1,'12J','SUMMITH WHITE','AR-20','TMFT0082022071101','WHITE','GENERIC PU COATED','A263','2022-07-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1954,'NIKOMAS IY',18,'NIKE',1,'2FV','FUCHSIA FLUX','DE-126','TMNS0202022072001','PINK','HP ECO TECH COMFORT','A1057',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1955,'PANARUB',19,'ADIDAS',3,'A0TP','CREAM WHITE','DE-7','FMCA','01V','SOFT PU COATED LEA','A156','2022-07-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1956,'CHANGSHIN',4,'NIKE',1,'60I','CHINA ROSE','R-8','TMCS0052022070501','PINK','PM GENERIC PU COATED','A245','2022-07-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1957,'TAEKWANG',30,'NIKE',1,'4NQ','COBALT BLISS','AR-144','TMTK0272022071801','L.BLUE','VIRGIN HYDRO PU','A129','2022-07-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1958,'PANARUB',19,'ADIDAS',3,'ADB3','ORBIT GREY','DE-7','FMCA','WHITE','SOFT PU COATED LEA','A157','2022-07-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1959,'PANARUB',19,'ADIDAS',3,'020A','GREEN','DE-7','FMCA','33R','SOFT PU COATED LEA','A158','2022-07-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1960,'PANARUB',19,'ADIDAS',3,'039A','BLUE BIRD','DE-73','FMCA','BLUE','PU COATED LEATHER','A159','2022-07-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1961,'FENGTAY',8,'NIKE',1,'60F','PEARL PINK','DE-90','TMFT0072022072201','WHITE','VIRGIN HYDRO PU LEATHER','A264','2022-07-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1962,'TAH SUNG HUNG',34,'ADIDAS',3,'AETG','BETTER SCARLET','DE-73','FMCA','RED','PU COATED LEATHER','A738','2022-08-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11','2026-05-19 03:12:11'),
(1963,'PANARUB',19,'ADIDAS',3,'AA2S','GREY TWO','DE-172','FMCA','GREY','SOFT PU COATED LEA','A164','2022-08-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11','2026-05-19 03:12:11'),
(1964,'PANARUB',19,'ADIDAS',3,'AET2','PRELOVED RED','DE-172','FMCA','RED','SOFT PU COATED LEA','A165','2022-08-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11','2026-05-19 03:12:11'),
(1965,'PANARUB',19,'ADIDAS',3,'A0TP','CREAM WHITE','DE-172','TMPA0202022072801','WHITE','SOFT PU COATED LEA','A162','2022-07-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1966,'CHANGSHIN',4,'NIKE',1,'3JG','SEQUOIA','AR-138','TMCS0052022072901','BLACK','VIRGIN HYDRO PU','A246','2022-08-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1967,'CHANGSHIN',4,'NIKE',1,'4QX','BLUE WHISPER','AR-138','TMCS0052022072902','WHITE','VIRGIN HYDRO PU','A247','2022-08-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1968,'NIKOMAS IY',18,'NIKE',1,'6LC','PICANTE RED','AR-100','TMNS0202022080104','RED','GENERIC PU COATED','A1059','2022-08-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1969,'NIKOMAS IY',18,'NIKE',1,'6BA','NIGHT MAROON','AR-100','TMNS0202022080101','PURPLE','GENERIC PU COATED','A1060','2022-08-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1970,'NIKOMAS IY',18,'NIKE',1,'2GY','CACAO WOW','AR-100','TMNS0202022080106','BROWN','GENERIC PU COATED','A1061','2022-08-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1971,'NIKOMAS IY',18,'NIKE',1,'24Q','EARTH','AR-100','TMNS0202022080102','BROWN','GENERIC PU COATED','A1062','2022-08-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1972,'NIKOMAS IY',18,'NIKE',1,'4KQ','LT CURRENT BLUE','AR-100','TMNS0202022080103','4JE','GENERIC PU COATED','A1063','2022-08-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1973,'NIKOMAS IY',18,'NIKE',1,'6DA','LIGHT CRIMSON','AR-100','TMNS0202022080105','RED','GENERIC PU COATED','A1064','2022-08-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1974,'DIAMOND INTERNATIONAL',38,'NB',4,'NB-S20-7546','NATURAL INDIGO','AR-100','TMDI0242022080401','BLACK','HYDRO SOFT PU COATED LEATHER','A398','2022-08-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1975,'DIAMOND INTERNATIONAL',38,'NB',4,'NB-S18-4459/134-31-29','PRISM PURPLE','AR-100','TMDI0242022080402','PURPLE','HYDRO SOFT PU COATED LEATHER','A399','2022-08-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1976,'PANARUB',19,'ADIDAS',3,'040A','BLUE','DE-73','FMCA','44Z','PU COATED LEATHER','A166','2022-08-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11','2026-05-19 03:12:11'),
(1977,'PARKLAND',21,'NB',4,'076-27-12','NIGHT WATCH GREEN COLORO','AR-108','TMPW0102022080801','33R','HYDRO SOFT PU COATED LEATHER','A400','2022-08-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1978,'FENGTAY',8,'NIKE',1,'47X','DEEP ROYAL BLUE','R-8','TMFT0072022080401','BLACK','PM GENERIC PU COATED','A265','2022-08-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1979,'TAH SUNG HUNG',34,'ADIDAS',3,'54F0','COLLEGIATE NAVY','DE-73','FMCA','BLACK','PU COATED LEATHER','A739','2022-08-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1980,'TAH SUNG HUNG',34,'ADIDAS',3,'AETG','BETTER SCARLET','DE-172','FMCA','RED','SOFT PU COATED LEATHER','A748','2022-09-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11','2026-05-19 03:12:11'),
(1981,'TAH SUNG HUNG',34,'ADIDAS',3,'AA2R','GREY ONE','DE-172','FMCA','WHITE','SOFT PU COATED LEATHER','A752','2022-10-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11','2026-05-19 03:12:11'),
(1982,'NIKOMAS',17,'ADIDAS',3,'AECU','ALMOST PINK','DE-7','TMNS0162022060301','PINK','SOFT PU','A742','2022-08-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1983,'POUYUEN',24,'NIKE',1,'38W','LUCKY GREEN','R-53','TMPY0282022081601','3GU','GENERIC PU COATED','A1065','2022-08-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1984,'POUYUEN',24,'NIKE',1,'44M','AQUATONE','R-53','TSPY0282022082401','4JE','GENERIC PU COATED','A1066','2022-08-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1985,'TAH SUNG HUNG',34,'ADIDAS',3,'329A','CLEAR ONIX','DE-73','FMCA','WHITE','PU COATED LEATHER','A743','2022-08-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1986,'TAH SUNG HUNG',34,'ADIDAS',3,'A0RP','COLLEGIATE BURGUNDY','DE-73','FMCA','RED','PU COATED LEATHER','A751','2022-09-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11','2026-05-19 03:12:11'),
(1987,'CHANGSHIN',3,'NIKE',1,'3HJ','LIGHT DEW','UM-34 SM','TMCS0042022082502','4AU','VIRGIN HYDRO PU','A248',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1988,'CHANGSHIN',3,'NIKE',1,'84V','TURF ORANGE','UM-34 SM','TMCS0042022082501','80S','VIRGIN HYDRO PU','A249',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1989,'PANARUB',19,'ADIDAS',3,'A0TP','CREAM WHITE','DE-172','FMCA','WHITE','SOFT PU COATED LEATHER','A167','2022-08-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1990,'PARKLAND 2',21,'NB',4,'076-27-12','NIGHT WATCH GREEN COLORO','AR-191','FOLLOW COLORO','33R','HYDRO SOFT PU COATED LEATHER','A401','2022-08-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1991,'NIKOMAS',17,'ADIDAS',3,'AEDC','MAGIC LIME','DE-7','SCOTDIC','34A','SOFT PU COATED LEATHER','A745','2022-08-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1992,'PANARUB',19,'ADIDAS',3,'A8L5','CRYSTAL WHITE','DE-90','FMCA','WHITE','SOFT PU COATED LEATHER','A168','2022-09-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1993,'PANARUB',19,'ADIDAS',3,'AA2S','GREY TWO','DE-172','TMPA0202022090601','WHITE','SOFT PU COATED LEATHER','A169','2022-09-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1994,'FENGTAY',9,'NIKE',1,'45B','OBSIDIAN','UM-14 G','TMFT0082022090601','BLACK','VIRGIN HYDRO PU','A267','2022-09-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1995,'NIKOMAS',17,'ADIDAS',3,'ADWA','HALO BLUE','CPUG','FMCA','WHITE','BABY SOFT PATENT LEATHER','A750','2022-09-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11','2026-05-19 03:12:11'),
(1996,'CHANGSHIN RJ',4,'NIKE',1,'6FX','TRACKED RED','AR-138','TMCS0052022091201','RED','VIRGIN HYDRO PU','A250',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1997,'CHANGSHIN RJ',4,'NIKE',1,'04Z','PURE PLATINUM','AR-138','TMCS0052022091203','WHITE','VIRGIN HYDRO PU','A251','2022-09-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1998,'CHANGSHIN RJ',4,'NIKE',1,'01X','PHANTOM','AR-138','TMCS0052022091202','WHITE','VIRGIN HYDRO PU','A252','2022-09-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(1999,'FENGTAY',7,'NIKE',1,'88I','MONARCH','R-8','TMFT0062022091301','80S','GENERIC PU COATED','A268','2022-09-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2000,'PANARUB',19,'ADIDAS',3,'AEWN','WONDER BEIGE','R-231','FMCA','01V','SOHO NUBUCK','A174','2022-10-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11','2026-05-19 03:12:11'),
(2001,'NIKOMAS',17,'ADIDAS',3,'ADW5','HALO BLUE','CPUG','SCOTDIC','YELLOW','BABY SOFT PATENT LEATHER','A749','2022-09-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2002,'DIAMOND',38,'NB',4,'000-68-00','RAIN CLOUD','R-231','FOLLOW COLORO','01V','SOHU NUBUCK','A402','2022-09-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2003,'CHANGSHIN RJ',4,'NIKE',1,'01B','METALLIC SILVER','DE-100 SG','TMCS0052022092701','WHITE','VIRGIN HYDRO PU','A253','2022-09-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2004,'PANARUB',19,'ADIDAS',3,'AESS','SAND STRATA','DE-7','SCOTDIC','2CT','HYDRO SOFT PU COATED LEATHER','A172','2022-10-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2005,'PCN G8',59,'NIKE',1,'06B','COOL GREY','AR-144','TMPG0212022100501','GREY','VIRGIN HYDRO PU LEATHER','A1067','2022-10-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2006,'DIAMOND',38,'NB',4,'039-90-05','ANGORA','AR-100','TSDI0242022100502','WHITE','HYDRO SOFT PU COATED LEATHER','A403','2022-10-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2007,'DIAMOND',38,'NB',4,'036-90-02','SEA SALT','AR-100','TSDI0242022100501','WHITE','HYDRO SOFT PU COATED LEATHER','A404','2022-10-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2008,'DIAMOND',38,'NB',4,'000-47-00','PORT OF GRAY','AR-100','TSDI0242022100504','GREY','HYDRO SOFT PU COATED LEATHER','A405','2022-10-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2009,'DIAMOND',38,'NB',4,'118-36-30','BLUE COLORO','AR-100','TSDI0242022100503','44Z','HYDRO SOFT PU COATED LEATHER','A406','2022-10-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2010,'DIAMOND',38,'NB',4,'122-36-01','GRAPHITE COLORO','AR-100','FOLLOW COLORO','BLACK','HYDRO SOFT PU COATED LEATHER','A407','2022-10-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2011,'DIAMOND',38,'NB',4,'034-84-05','LINEN COLORO','AR-100','FOLLOW COLORO','WHITE','HYDRO SOFT PU COATED LEATHER','A408','2022-10-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2012,'DIAMOND',38,'NB',4,'010-35-35','TEAM RED COLORO','AR-100','TSDI0242022122905','RED','HYDRO SOFT PU COATED LEATHER','A444','2023-01-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11','2026-05-19 03:12:11'),
(2013,'DIAMOND',38,'NB',4,'118-53-17','BLUE LAGUNA COLORO','AR-100','TSDI0242022122906','BLUE','HYDRO SOFT PU COATED LEATHER','A445','2023-01-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11','2026-05-19 03:12:11'),
(2014,'DIAMOND',38,'NB',4,'NB-F21-1523','ORANGE','AR-100','TSDI0242022101001','80S','HYDRO SOFT PU COATED LEATHER','A411','2022-10-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2015,'DIAMOND',38,'NB',4,'124-38-32','MARINE BLUE COLORO','AR-100','TSDI0242022101802','BLACK','HYDRO SOFT PU COATED LEATHER','A420','2022-10-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11','2026-05-19 03:12:11'),
(2016,'DIAMOND',38,'NB',4,'049-65-00','CONCRETE COLORO','AR-100','TMDI0242023041701','WHITE','HYDRO SOFT PU COATED LEATHER','A465','2023-04-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11','2026-05-19 03:12:12'),
(2017,'DIAMOND',38,'NB',4,'126-22-11','TEAM NAVY','AR-100','FOLLOW COLORO','BLACK','HYDRO SOFT PU COATED LEATHER','A414','2022-10-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2018,'DIAMOND',38,'NB',4,'NB-S17-6713','TEAM CAROLINA','AR-100','TSDI0242022101801','WHITE','HYDRO SOFT PU COATED LEATHER','A419','2022-10-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11','2026-05-19 03:12:11'),
(2019,'DIAMOND',38,'NB',4,'017-54-37','TEAM ORANGE COLORO','AR-100','TSDI0242022122902','WHITE','HYDRO SOFT PU COATED LEATHER','A441','2023-01-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11','2026-05-19 03:12:11'),
(2020,'DIAMOND',38,'NB',4,'032-76-04','TIMBER WOLF','AR-100','FOLLOW COLORO','01V','HYDRO SOFT PU COATED LEATHER','A417','2022-10-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2021,'DIAMOND',38,'NB',4,'035-64-33','VARSITY GOLD COLORO','AR-100','TSDI0242022122904','YELLOW','HYDRO SOFT PU COATED LEATHER','A443','2023-01-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11','2026-05-19 03:12:11'),
(2022,'ADIS',1,'NIKE',1,'3GS','STADIUM GREEN','AR-107','TMAD0022022101701','WHITE','VIRGIN HYDRO PU','A525','2022-10-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2023,'SAI',37,'NB',4,'000-47-00','HARBOR GREY','AR-100','COLORO','GREY','HYDRO PU COATED LEATHER','A421','2022-10-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2024,'SAI',37,'NB',4,'036-90-02','SEA SALT','DE-74','COLORO','WHITE','HYDRO SOFT ACTION LEATHER','A422','2022-10-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2025,'SAI',37,'NB',4,'125-39-04','DARK ARTIC GREY','DE-74','COLORO','BLACK','HYDRO SOFT ACTION LEATHER','A423','2022-10-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2026,'SAI',37,'NB',4,'017-79-00','GREY MATTER','DE-14','COLORO','01V','HYDRO SOFT ACTION LEATHER','A424','2022-10-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2027,'SAI',37,'NB',4,'110-66-12','CHROME BLUE','DE-74','COLORO','LT BLUE','HYDRO SOFT ACTION LEATHER','A425','2022-10-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2028,'PANARUB',19,'ADIDAS',3,'AESS','SAND STRATA S23','DE-7','FMCA','2CT','SOFT PU COATED LEATHER','A173','2022-10-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2029,'PANARUB',19,'ADIDAS',3,'A0TP','CREAM WHITE','R-231','FMCA','WHITE','SOHO NUBUCK','A175','2022-10-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2030,'METRO',16,'NB',4,'124-23-11','NEW NAVY','AR-100','TMMP0332022102401','BLACK','HYDRO SOFT PU COATED LEATHER','M032','2022-02-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2031,'TAEKWANG',30,'NIKE',1,'28C','RATTAN','AR-196','TMTK0272022102702','WHITE','VIRGIN HYDRO PU LEATHER','A130','2022-10-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2032,'TAEKWANG',30,'NIKE',1,'04D','LIGHT SILVER','AR-196','TMTK0272022102701','WHITE','VIRGIN HYDRO PU LEATHER','A131','2022-10-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2033,'KMK',15,'NIKE',1,'117-15-00','CONVERSE BLACK','DE-90','BLACK CONVERSE','BLACK','1.24 NAPPA NATURAL LEATHER','A200','2022-11-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2034,'PWI 2',21,'NB',4,'076-27-12','NIGHTWATCH GREEN COLORO','AR-191','TMPW0102022110201','33R','HYDRO SOFT PU COATED LEATHER','A426','2022-11-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2035,'CHANGSHIN',4,'NIKE',1,'3HS','TROPICAL TWIST','AR-138','TMCS0052022110701','4AU','VIRGIN HYDRO PU','A254','2022-11-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2036,'CHANGSHIN',4,'NIKE',1,'52X','LIGHT VIOLET','AR-138','TMCS0052022110702','WHITE','VIRGIN HYDRO PU','A255','2022-11-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2037,'DIAMOND',38,'NB',4,'11-0601TCX','BRIGHT WHIE','AR-100','PANTONE COLORO','WHITE','HYDRO PU COATED LEATHER','A427','2022-11-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2038,'DIAMOND',38,'NB',4,'056-26-07','KOMBU COLORO','AR-100','COLORO','33R','HYDRO PU COATED LEATHER','A428','2022-11-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2039,'ADIS',1,'NIKE',1,'0BA','PLATINUM VIOLET PEARLIZED','UM-T SM','TSAD0022022111001','01V','GENERIC PU COATED LEATHER','A526','2022-11-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2040,'DIAMOND',38,'NB',4,'008-85-11','SHELL PINK','AR-100','TSDI0242023011103','PINK','HYDRO PU COATED LEATHER','A447','2023-01-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11','2026-05-19 03:12:11'),
(2041,'DIAMOND',38,'NB',4,'148-84-34','ORBIT PINK','AR-100','TSDI0242023011102','PINK','HYDRO PU COATED LEATHER','A446','2023-01-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11','2026-05-19 03:12:11'),
(2042,'NIKOMAS',17,'ADIDAS',3,'AEWY','PRELOVED BROWN','DE-73','SCOTDIC','BROWN','HYDRO ECOTECH LEATHER','A753','2022-11-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2043,'ADIS',1,'NIKE',1,'45B','OBSIDIAN','UM-34','TMAD0022022111802','BLACK','VIRGIN HYDRO PU','A528','2022-11-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2044,'PARKLAND 2',21,'NB',4,'000-27-00','BLACK TOP COLORO','AR-191','TMPW0102022112201','BLACK','HYDRO SOFT PU COATED LEATHER','A431','2022-11-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2045,'PARKLAND 2',21,'NB',4,'028-59-26','CANYON COLORO','AR-191','TMPW0102022112202','2CT','HYDRO SOFT PU COATED LEATHER','A432','2022-11-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2046,'POUYUEN',24,'NIKE',1,'5CB','SKY J PURPLE','R-53','TSPY0282022112201','58U','GENERIC PU COATED','A1068','2022-11-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2047,'POUYUEN',24,'NIKE',1,'5CD','SKY J LT PURPLE','R-53','TSPY0282022112202','49D','GENERIC PU COATED','A1069','2022-11-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2048,'POUYUEN',24,'NIKE',1,'31M','SPRING GREEN','R-8','TMPY0282022112801','4AU','GENERIC PU COATED','A1070','2022-11-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2049,'VICTORY',31,'NIKE',1,'60F','PEARL PINK','AR-169','TMVC0052022112801','PINK','VIRGIN PU','A264','2022-11-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2050,'PCN G8',59,'NIKE',1,'6GA','RED STARDUST','R-8','TMPG0212022120901','PINK','VIRGIN PU','A1071','2022-12-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2051,'POUYUEN',24,'NIKE',1,'4NQ','COBALT BLISS','UM-16','TMPY0282022120901','BLUE','GENERIC PU COATED','A1072','2022-12-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2052,'LONGRICH',41,'UA',5,'310','BAROQUE GREEN','AR-194','TMLR0262022121201','BLACK','HYDRO ACTION LEATHER','A183','2022-12-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2053,'CHANGSHIN',4,'NIKE',1,'45B','OBSIDIAN','AR-138','TMCS0052022121201','BLACK','VIRGIN HYDRO PU','A256','2022-12-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2054,'SENGDAM/SAI',37,'NB',4,'000-47-00','HARBOR GREY COLORO','AR-100','TMSD0462022121401','GREY','HYDRO PU COATED LEATHER','A433','2022-12-15','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2055,'PARKLAND 2',21,'NB',4,'021-71-03','MOON ROCK COLORO','AR-140','TMPW0102023072001','01V','HYDRO PU COATED LEATHER','A478',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11','2026-05-19 03:12:13'),
(2056,'DIAMOND INTERNATIONAL',38,'NB',4,'028-56-06','DRIFTWOOD COLORO','AR-100','COLORO','01V','HYDRO PU COATED LEATHER','A435','2022-12-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2057,'SAI',37,'NB',4,'041-57-00','TEAM AWAY GREY COLORO','R-53','COLORO','01V','HYDRO PU COATED LEATHER','A436','2022-12-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2058,'NIKOMAS',17,'ADIDAS',3,'ADWZ','CREW YELLOW','DE-126','SCOTDIC','YELLOW','SOFT PU COATED LEATHER','A754','2022-12-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2059,'NIKOMAS',17,'ADIDAS',3,'AF4Q','PRELOVED SCARLET','DE-126','SCOTDIC','RED','SOFT PU COATED LEATHER','A755','2022-12-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2060,'NIKOMAS',17,'ADIDAS',3,'AF4P','CHARCOAL','DE-126','SCOTDIC','LIGHT BROWN','SOFT PU COATED LEATHER','A756','2022-12-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2061,'NIKOMAS',17,'ADIDAS',3,'AF4D','SEMI BLUE BURST','DE-126','SCOTDIC','BLUE','SOFT PU COATED LEATHER','A757','2022-12-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2062,'CHANGSHIN',4,'NIKE',1,'20I','HEMP','R-8','TMCS0052022121603','2CT','VIRGIN HYDRO PU','A257','2022-12-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2063,'CHANGSHIN',4,'NIKE',1,'4CA','DARK OBSIDIAN','AR-33','TMCS0052022121601','BLACK','VIRGIN HYDRO PU','A258','2022-12-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2064,'SAI',37,'NB',4,'126-22-11','TEAM NAVY COLORO','AR-100','TSSD0462022121903','BLACK','HYDRO SOFT PU COATED LEATHER','A437','2022-12-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2065,'SAI',37,'NB',4,'000-73-00','BRIGHTON GREY COLORO','AR-100','TSSD0462022121902','WHITE','HYDRO SOFT PU COATED LEATHER','A438','2022-12-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2066,'SAI',37,'NB',4,'032-76-04','TIMBER WOLF COLORO','AR-100','TSSD0462022121901','WHITE','HYDRO SOFT PU COATED LEATHER','A439','2022-12-19','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2067,'NIKOMAS',17,'ADIDAS',3,'082A','SOLAR YELLOW','DE-41','SCOTDIC','YELLOW','SEMI FULL GRAIN','A758','2022-12-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2068,'FENGTAY',9,'NIKE',1,'73W','OPTI YELLOW','AR-169','TMFT0082022122101','YELLOW','VIRGIN HYDRO PU LEATHER','A269','2022-12-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2069,'TAEKWANG',30,'NIKE',1,'3MI','EMERALD RISE','AR-144','TMTK0272022122201','4AU','VIRGIN HYDRO PU LEATHER','A132','2022-12-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2070,'KMK',15,'NIKE',1,'3MG','DEEP JUNGLE','AR-161','TMKM0012022122701','WHITE','GENERIC PU COATED','A201','2022-12-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2071,'DIAMOND',38,'NB',4,'11-0601 TCX','BRIGHT WHITE','AR-100','TSDI0242022122901','WHITE','HYDRO PU COATED LEATHER','A440','2023-01-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2072,'PCN G8',59,'NIKE',1,'74I','TWINE','AR-20','TMPG0212023010201','2CT','GENERIC PU COATED','A1074','2023-01-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2073,'CHANGSHIN',3,'NIKE',1,'68W','PINK GLAZE','UM-34','TMCS0042023010401','PINK','VIRGIN HYDRO PU','A259','2023-01-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2074,'ADIS',1,'NIKE',1,'6LC','PICANTE RED','DE-90','TMAD0022023010401','WHITE','GENERIC PU COATED','A529','2023-01-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2075,'ADIS',1,'NIKE',1,'3MI','EMERALD RISE','DE-73','TMAD0022023010402','WHITE','GENERIC PU COATED','A530','2023-01-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2076,'NIKOMAS IY',18,'NIKE',1,'44B','MIDNIGHT NAVY','UMT','TSNS0202023010401','BLACK','GENERIC PU COATED','A1075','2023-01-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2077,'NIKOMAS IY',18,'NIKE',1,'6LE','PINK BLOOM','DE-73 SM','TSNS0202023010501','PINK','GENERIC PU COATED','A1076','2023-01-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2078,'ADIS',1,'NIKE',1,'6GV','PARTICLE ROSE','DE-43','TSAD0022023010601','PINK','VIRGIN PU','A531','2023-01-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2079,'NIKOMAS IY',18,'NIKE',1,'73W','OPTI YELLOW','R-8 SG','FOLLOW SAMPLE A4','YELLOW','GENERIC PU COATED','A1077','2023-01-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2080,'NIKOMAS IY',18,'NIKE',1,'81J','SAFETY ORANGE','R-8 SG','FOLLOW SAMPLE A4','80S','GENERIC PU COATED','A1078','2023-01-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2081,'DIAMOND',38,'NB',4,'038-84-04','TURTLEDOVE COLORO','AR-100','FOLLOW COLORO','WHITE','HYDRO PU COATED LEATHER','A448','2023-01-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2082,'ADIS',1,'NIKE',1,'3QW','JADE ICE','UM-16','TMAD0022023011801','WHITE','GENERIC PU COATED','A532','2023-01-20','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2083,'VICTORY',31,'NIKE',1,'05V','LT IRON ORE','AR-107','TMVC0052023011901','WHITE','GENERIC PU COATED','A265','2023-01-20','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2084,'FENGTAY',7,'NIKE',1,'3QW','JADE ICE','DE-7','TMFT0062023011801','LIGHT BLUE','GENERIC PU COATED','A270','2023-01-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2085,'SAI',37,'NB',4,'028-24-06','RICHEARTH COLORO','AR-100','FOLLOW COLORO','L. BROWN','HYDRO PU COATED LEATHER','A449','2023-01-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2086,'SCI',32,'NIKE',1,'86W','GUAVA ICE','AR-161','TMSC0062023012402','WHITE','GENERIC PU COATED','A1079','2023-01-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2087,'SCI',32,'NIKE',1,'44B','MIDNIGHT NAVY','UMT','TMSC0062023012401','BLACK','GENERIC PU COATED','A1080','2023-01-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2088,'DIAMOND',38,'NB',4,'017-54-37','TEAM ORANGE COLORO','AR-100 M','TMDI0242023012701','WHITE','HYDRO SOFT PU COATED LEATHER','A450','2023-01-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2089,'VICTORY',31,'NIKE',1,'3QW','JADE ICE','AR-20','TMVC0052023012701','4AU','GENERIC PU COATED','A266','2023-01-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2090,'CHINGLUH',5,'NIKE',1,'3MI','EMERALD RISE','AR-59','TMCL0172023013001','2CT','PRINCESS LEATHER','A268','2023-01-31','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2091,'CHINGLUH',5,'NIKE',1,'4EV','GAME ROYAL','R-8','TMCL0172023013003','2CT','PRINCESS LEATHER','A269','2023-01-31','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2092,'CHINGLUH',5,'NIKE',1,'05Q','FOOTBALL GREY','AR-59','TMCL0172023013002','2CT','PRINCESS LEATHER','A270','2023-01-31','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2093,'CHINGLUH',5,'NIKE',1,'47N','UNIVERITY BLUE','R-8','TMCL0172023013005','2CT','PRINCESS LEATHER','A272','2023-01-31','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2094,'ADIS',1,'NIKE',1,'3MG','DEEP JUNGLE','UM-16','TMAD0022023013101','3AW','GENERIC PU COATED','A533','2023-02-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2095,'POUYUEN',24,'NIKE',1,'47X','DEEP ROYAL BLUE','R-8 M','TMPY0282023020101','BLACK','ECO TECH COMFORT','A1081','2023-02-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2096,'YOUNG TREE',33,'UA',5,'011','MOD GREY','AR-196','TMYT0012023020201','GREY','ACTION HYDRO PU LEATHER','A184','2023-02-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:11',NULL),
(2097,'YOUNG TREE',33,'UA',5,'001','BLACK','AR-196','TMYT0012023020202','BLACK','ACTION HYDRO PU LEATHER','A185','2023-02-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2098,'DIAMOND',38,'NB',4,'079-26-18','MARSH GREEN COLORO','AR-73','FOLLOW COLORO','33R','HYDRO SOFT PU COATED LEATHER','A451','2023-02-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2099,'CHANGSHIN',4,'NIKE',1,'3QW','JADE ICE','AR-138','TMCS0052023020301','4AU','VIRGIN HYDRO PU','A260','2023-02-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2100,'CHANGSHIN',4,'NIKE',1,'3ND','GEODE TEAL','AR-138','TMCS0052023020302','3AW','VIRGIN HYDRO PU LEATHER','A261','2023-02-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2101,'NIKOMAS',17,'ADIDAS',3,'043A','DARK BLUE','DE-126','TMNS0162023020301','44Z','SOFT PU','A759','2023-02-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2102,'TAEKWANG',30,'NIKE',1,'05Q','FOOTBALL GREY','UM-16SM','TMTK0272023020601','WHITE','GENERIC PU COATED','A133','2023-02-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2103,'CHINGLUH',5,'NIKE',1,'5CB','SKY J PURPLE','DE-7SM','TMCL0172023020301','BLACK','GENERIC PU COATED','A273','2023-02-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2104,'CHINGLUH',5,'NIKE',1,'79W','TEAM GOLD','AR-20','TMCL0172023020302','YELLOW','GENERIC PU COATED','A274','2023-02-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2105,'CHANGSHIN',4,'NIKE',1,'0AJ','SMOKE GREY','DE-73SM','TMCS0052023020601','BLACK','GEENRIC PU COATED','A262','2023-02-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2106,'CHANGSHIN',4,'NIKE',1,'0AJ','SMOKE GREY','AR-107M','TMCS0052023020602','BLACK','GENERIC PU COATED','A263','2023-02-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2107,'CHANGSHIN',4,'NIKE',1,'4PA','BLUE VOID','DE-7SM','TMCS0052023020603','BLACK','GENERIC PU COATED','A264','2023-02-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2108,'CHANGSHIN',4,'NIKE',1,'0AF','OIL GREY','AR-161M','TMCS0052023020604','BLACK','GENERIC PU COATED','A265','2023-02-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2109,'DIAMOND',38,'NB',4,'148-84-34','ORBIT PINK','AR-100M','TMDI0242023020601','PINK','HYDRO SOFT PU COATED LEATHER','A452','2023-02-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2110,'DIAMOND',38,'NB',4,'056-26-07','COMBU COLORO','AR-100 M','TMDI0242023022001','33R','HYDRO SOFT PU COATED LEATHER','A453','2023-02-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2111,'DIAMOND',38,'NB',4,'018-48-26','INFIELD CLAY COLORO','AR-120M','FOLLOW COLORO','80S','HYDRO SOFT PU COATED LEATHER','A454','2023-02-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2112,'PARKLAND 2',21,'NB',4,'032-76-04','TIMBERWOLF COLORO','AR-140','TSPW0102023013101','WHITE','HYDRO SOFT PU COATED LEATHER','A455','2023-02-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2113,'POUYUEN',24,'NIKE',1,'6LF','FIERCE PINK','AR-161 M','TMPY0282023020801','6DX','GENERIC PU COATED','A1082','2023-02-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2114,'POUYUEN',24,'NIKE',1,'04B','CEMENT GREY','AR-107 M','TMPY0282023020802','GREY','GENERIC PU COATED','A1083','2023-02-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2115,'CHANGSHIN',4,'NIKE',1,'6GJ','LT FUSION  RED FLUORESCENCE','AR-196','TMCS0052023020901','RED','GENRIC PU COATED','A266','2023-02-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2116,'POUYUEN',24,'NIKE',1,'65H','CORAL CHALK','UM-16 SM','TMPY0282023021001','PINK','GENERIC PU COATED','A1084','2023-02-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2117,'YOUNG TREE',33,'UA',5,'697','PINK ELIXIR','R-231','TMYT0012023021001','PINK','SOHO NUBUCK','A186','2023-02-14','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2118,'CHANGSHIN',3,'NIKE',1,'0AH','DK SMOKE GREY','DE-7','TMCS0042023021001','BLACK','GENERIC PU COATED','A267','2023-02-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2119,'CHANGSHIN RJ',4,'NIKE',1,'12J','SUMMITH WHITE','R-8M','TMCS0052023021501','WHITE','GENERIC PU COATED','A268','2023-02-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2120,'CHANGSHIN RJ',4,'NIKE',1,'12J','SUMMITH WHITE','DE-90','TMCS0052023021502','WHITE','GENERIC PU COATED','A269','2023-02-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2121,'CHANGSHIN RJ',4,'NIKE',1,'12J','SUMMITH WHITE','UMT','TMCS0052023021503','WHITE','GENERIC PU COATED','A270','2023-02-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2122,'CHINGLUH',31,'NIKE',1,'47N','UNIVERITY BLUE','DE-7','TMVC0052023021501','44Z','GENERIC PU COATED','A275','2023-02-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2123,'NIKOMAS',17,'ADIDAS',3,'08S1','OFF WHITE','DE-7','TMNS0162023021401','WHITE','SOFT PU COATED','A760','2023-02-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2124,'CHINGLUH',5,'NIKE',1,'71R','VOLT','AR-20','TMCL0172023021301','YELLOW','GENERIC PU COATED','A276','2023-02-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2125,'PRATAMA JX',26,'NIKE',1,'05Q','FOOTBALL GREY','R-8','TMPT0132023022001','WHITE','PM GENERIC PU COATED','A479','2022-02-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2126,'CHINGLUH',5,'NIKE',1,'6LF','FIERCE PINK','AR-161 M','TMCL0172023022001',NULL,'GENERIC PU COATED','A277','2023-02-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2127,'DIAMOND',38,'NB',4,'008-85-11','SHELL PINK','AR-100','TMDI0242023020602','PINK','HYDRO SOFT PU COATED LEATHER','A457','2023-02-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2128,'LONGRICH',42,'UA',5,'202','NUBUCK TAN','AR-175','FOLLOW CSI UA','WHITE','ECO GREEN LEATHER','A187','2023-02-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2129,'LONGRICH',42,'UA',5,'044','DOWNPOUR GRAY','AR-175','FOLLOW CSI UA','BLACK','ECO GREEN LEATHER','A188','2023-02-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2130,'LONGRICH',42,'UA',5,'482','RADIAL TURQUOISE','AR-175','FOLLOW CSI UA','WHITE','ECO GREEN LEATHER','A189','2023-02-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2131,'NIKOMAS IY',24,'NIKE',1,'73W','OPTI YELLOW','R-8 M','TMPY0282023022101','YELLOW','ECO TECH COMFORT','A1085','2023-02-25','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2132,'KMK',15,'NIKE',1,'09M','SEA GLASS','R-8','TMKM0012023022301','WHITE','GENERIC PU COATED','A202','2023-02-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2133,'SCI',32,'NIKE',1,'73W','OPTI YELLOW','AR-161M','TMSC0062023022301','WHITE','GENERIC PU COATED','A1086','2023-02-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2134,'NIKOMAS IY',18,'NIKE',1,'74I','TWINE','AR-20','TMNS0202023022801','2CT','GENERIC PU','A1087','2023-03-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2135,'NIKOMAS IY',18,'NIKE',1,'65N','UNIVERSITY RED','R-8','TMNS0202023022701','RED','ECO TECH COMFORT','A1088','2023-03-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2136,'SHOETOWN',28,'NIKE',1,'76H','SUNDIAL','DE-7 SM','TSSL0432023022702','WHITE','GENERIC PU COATED','A1089','2023-03-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2137,'SHOETOWN',28,'NIKE',1,'40X','BALTIC BLUE','DE-7 SM','TSSL0432023022701','WHITE','GENERIC PU COATED','A1090','2023-03-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2138,'POUYUEN',24,'NIKE',1,'81J','SAFETY ORANGE','R-8','TMPY0282023030101','80S','ECO TECH COMFORT','A1091','2023-03-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2139,'ADIS',1,'NIKE',1,'12B','SANDDRIFT','AR-196 M','TMAD0022023021401','WHITE','GENERIC PU COATED','A534','2023-03-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2140,'LONGRICH',42,'UA',5,'56I','STARLIGHT','AR-175','FOLLOW CSI UA','BLACK','ECO GREEN LEATHER','A190','2023-03-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2141,'LONGRICH',42,'UA',5,'688','CINNA RED','AR-175','FOLLOW CSI UA','WHITE','ECO GREEN LEATHER','A191','2023-03-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2142,'CHANGSHIN',3,'NIKE',1,'53C','ICED LILAC','AR-144','TMCS0042023030601','PINK','VIRGIN HYDRO PU','A271','2023-03-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2143,'CHANGSHIN',3,'NIKE',1,'4CA','DARK OBSIDIAN','AR-33','TMCS0042023030602','BLACK','VIRGIN HYDRO PU LEATHER','A272','2023-03-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2144,'FENGTAY (WEST)',8,'NIKE',1,'0AV','OFF NOIR','UM-34','TMFT0072023030201','BLACK','GENERIC PU COATED','A271','2023-03-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2145,'NIKOMAS IY',18,'NIKE',1,'44B','MIDNIGHT NAVY','DE-73 SM','TMNS0202023030301','BLACK','GENERIC PU COATED','A1092','2023-07-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2146,'NIKOMAS IY',18,'NIKE',1,'60S','SHEEN','R-8','TSNS0202023030701','PINK','VIRGIN HYDRO PU','A1093','2023-03-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2147,'POUYUEN',24,'NIKE',1,'05Q','FOOTBALL GREY','UM-16','TSPY0282023030801','WHITE','PM GENERIC PU COATED','A1094','2023-03-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2148,'POUYUEN',24,'NIKE',1,'6DX','FIREBERRY FLOURESCENT','UM-16','TSPY0282023030901','6DX','PM GENERIC PU COATED','A1095','2023-03-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2149,'POUYUEN',24,'NIKE',1,'0AL','LT SMOKE GREY','UM-16 SM','TMPY0282023031001','WHITE','PM GENERIC PU COATED','A1096','2023-03-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2150,'FENGTAY',7,'NIKE',1,'88R','MANTRA ORANGE','UM-34','TMFT0062023031001','RED','GENERIC PU COATED','A272','2023-03-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2151,'YOUNG TREE',33,'UA',5,'810','BOLT RED','AR-196','TMYT0012023031001','RED','ACTION HYDRO PU LEATHER','A192','2023-03-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2152,'DIAMOND',38,'NB',4,'028-56-06','DRIFTWOOD COLORO','AR-100','TMDI0242023031302','01V','HYDRO SOFT PU COATED LEATHER','A458','2023-03-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2153,'DIAMOND',38,'NB',4,'000-68-00','RAIN CLOUD','AR-100','TMDI0242023031301','01V','HYDRO SOFT PU COATED LEATHER','A459','2023-03-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2154,'SHOETOWN CINA',28,'NIKE',1,'65N','UNIVERSITY RED','ESR-180SK2/CPUG','TMSL0432023031501','RED','PM GENERIC PU COATED','A1097','2023-03-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2155,'CHANGSHIN',3,'NIKE',1,'4CA','DARK OBSIDIAN','AR-144','TMCS0042023031501','BLACK','VIRGIN HYDRO PU','A273','2023-03-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2156,'CHANGSHIN',4,'NIKE',1,'0AL','LT SMOKE GREY','AR-138','TMCS0052023031601','WHITE','VIRGIN HYDRO PU','A274','2023-03-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2157,'CHANGSHIN',4,'NIKE',1,'10L','PALE IVORY','AR-138','TMCS0052023031501','WHITE','VIRGIN HYDRO PU','A275','2023-03-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2158,'CHINGLUH',31,'NIKE',1,'10J','LT OREWOOD BROWN','AR-169','TMVC0052023031402','WHITE','VIRGIN HYDRO PU','A278','2023-03-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2159,'VICTORY',31,'NIKE',1,'12J','SUMMITH WHITE','AR-169','TMVC0052023031401','WHITE','VIRGIN HYDRO PU','A279','2023-03-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2160,'VICTORY',31,'NIKE',1,'12J','SUMMITH WHITE','AR-107DM','TMVC0052023031403','WHITE','VIRGIN HYDRO PU','A280','2023-03-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2161,'VICTORY',31,'NIKE',1,'10J','LT OREWOOD BROWN','AR-107DM','TMVC0052023031404','WHITE','VIRGIN HYDRO PU','A281','2023-03-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2162,'SHOETOWN',28,'NIKE',1,'58I','LT ULTAMARINE','DE-7 SM','TSSL0432023031602','49D','PM GENERIC PU COATED','A1098','2023-03-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2163,'SHOETOWN',28,'NIKE',1,'65N','UNIVERSITY RED','DE-7 SM','TSSL0432023031601','RED','PM GENERIC PU COATED','A1099','2023-03-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2164,'SHOETOWN',28,'NIKE',1,'3ND','GEODE TEAL','AR-161','TSSL0432023031603','3AW','PM GENERIC PU COATED','A1100','2023-03-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2165,'SAI',37,'NB',4,'025-35-14','TRUE BROWN COLORO','AR-100','FOLLOW COLORO','LT BROWN','HYDRO PU COATED LEATHER','A460','2023-03-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2166,'TAEKWANG',30,'NIKE',1,'4CA','DARK OBSIDIAN','R-8M','TMTK0272023032002','BLACK','PM GENERIC PU COATED','A134','2023-03-20','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2167,'TAEKWANG',30,'NIKE',1,'10L','PALE IVORY','R-8M','TMTK0272023032001','WHITE','PM GENERIC PU COATED','A135','2023-03-20','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2168,'TAEKWANG',30,'NIKE',1,'0AL','LT SMOKE GREY','R-8M','TMTK0272023032003','WHITE','PM GENERIC PU COATED','A136','2023-03-20','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2169,'PRATAMA JX',26,'NIKE',1,'60F','PEARL PINK','DE-90','TMPT0132023032301','WHITE','VIRGIN HYDRO PU LEATHER','A480','2022-03-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2170,'SCI',32,'NIKE',1,'09M','SEA GLASS','R-8','TMSC0062023032103','WHITE','PM GENERIC PU COATED','A1101','2023-03-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2171,'SCI',32,'NIKE',1,'2BB','AMBER BROWN','AR-107','TMSC0062023032101','WHITE','PM GENERIC PU COATED','A1102','2023-03-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2172,'SCI',32,'NIKE',1,'05Q','FOOTBALL GREY','R-8','TMSC0062023032102','WHITE','PM GENERIC PU COATED','A1103','2023-03-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2173,'POUYUEN',24,'NIKE',1,'73R','VIVID SULFUR','R-8 M','TSPY0282023032801','YELLOW','VIRGIN PU','A1104','2023-03-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2174,'FENGTAY (WEST)',7,'NIKE',1,'6LG','PLAYFULL PINK','R-231','TMFT0062023033001','6DX','GENERIC PU COATED','A273','2023-03-31','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2175,'ADIS',1,'NIKE',1,'0AL','LT SMOKE GREY','DE-73','TMAD0022023030701','WHITE','GENERIC PU COATED','A535','2023-04-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2176,'ADIS',1,'NIKE',1,'3NC','LIME BLAST','DE-73M','TMAD0022023032901','34A','GENERIC PU COATED','A536','2023-04-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2177,'CHANGSHIN',3,'NIKE',1,'06F','ANTHRACITE','DE-7','TMCS0042023033101','BLACK','GENERIC PU COATED','A276','2023-04-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2178,'NIKOMAS',17,'ADIDAS',3,'AF42','IVORY','DE-7','MNS0162023103001','WHITE','SOFT PU COATED','A774',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12','2026-05-19 03:12:14'),
(2179,'DIAMOND',38,'NB',4,'038-84-04','TURTLEDOVE COLORO','AR-100','TMDI0242023040501','WHITE','HYDRO SOFT PU COATED LEATHER','A461','2023-04-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2180,'CHANGSHIN',4,'NIKE',1,'22Z','BAROQUE BROWN','R-8','TMCS0052023051101','BLACK','ECO TECH COMFORT','A282','2023-05-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12','2026-05-19 03:12:13'),
(2181,'CHANGSHIN',3,'NIKE',1,'04D','LIGHT SILVER','R-8','TMCS0042023040502','WHITE','ECO TECH COMFORT','A278','2023-04-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2182,'VICTORY',31,'NIKE',1,'2GD','FOSSIL STONE','AR-20 M','TMVC0052023041001','WHITE','GENERIC PU COATED','A282','2023-04-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2183,'VICTORY',31,'NIKE',1,'42M','BRIGHT CONCORT','DE-7 SM','TMVC0052023041002','44Z','GENERIC PU COATED','A283','2023-04-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2184,'CHANGSHIN',3,'NIKE',1,'47N','UNIVERSITY BLUE','R-8','TMCS0042023040503','BLUE','ECO TECH COMFORT','A279','2023-04-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2185,'SCI',32,'NIKE',1,'3MG','DEEP JUNGLE','AR-161 M','TMSC0062023040501','WHITE','GENRIC PU COATED','A1105','2023-04-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2186,'FENGTAY (WEST)',7,'NIKE',1,'0AL','LT SMOKE GREY','R-8 M','TMFT0062023041001','01V','GENERIC PU COATED','A274','2023-04-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2187,'METRO NB',16,'NB',4,'036-90-02','NEW SEA SALT','AR-122 SG','TSMP0332023040601','WHITE','HYDRO PU COATED LEATHER','M033','2023-04-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2188,'METRO NB',16,'NB',4,'147-70-20','PINK SUGAR','AR-122 SG','TSMP0332023040602','PINK','HYDRO PU COATED LEATHER','M034','2023-04-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2189,'METRO NB',16,'NB',4,'043-89-00','REFLECTION','AR-122 SG','TSMP0332023040603','WHITE','HYDRO PU COATED LEATHER','M035','2023-04-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2190,'YOUNG TREE',33,'UA',5,'001','BLACK','R-231','TMYT0012023041201','BLACK','SOHO NUBUCK','A193','2023-04-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2191,'POUYUEN',24,'NIKE',1,'53C','ICED LILAC','AR-144','TMPY0282023041201','PINK','VIRGIN HYDRO PU','A1106','2023-04-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2192,'POUYUEN',24,'NIKE',1,'09M','SEA GLASS','R-102','TMPY0282023041204','WHITE','GENERIC PU COATED','A1107','2023-04-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2193,'POUYUEN',24,'NIKE',1,'3EP','GREEN ABYSS','R-8','TMPY0282023041206','3AW','VIRGIN PU','A1108','2023-04-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2194,'POUYUEN',24,'NIKE',1,'3GS','STADIUM GREEN','R-8','TMPY0282023041205','WHITE','VIRGIN PU','A1109','2023-04-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2195,'POUYUEN',24,'NIKE',1,'4KZ','BLUE TINT','R-8','TMPY0282023041203','WHITE','VIRGIN PU','A1110','2023-04-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2196,'POUYUEN',24,'NIKE',1,'40X','BALTIC BLUE','R-8','TMPY0282023041202','4JE','VIRGIN PU','A1111','2023-04-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2197,'PARKLAND 2',21,'NB',4,'022-60-08','FLAT TAUPE','AR-140','FOLLOW COLORO','01V','HYDRO SOFT PU COATED LEATHER','A462','2023-04-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2198,'PARKLAND 2',21,'NB',4,'105-27-15','DEEP SEA','AR-140','FOLLOW COLORO','3AW','HYDRO SOFT PU COATED LEATHER','A463','2023-04-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2199,'PARKLAND 2',21,'NB',4,'040-72-34','GINGER LEMON','AR-140','FOLLOW COLORO','YELLOW','HYDRO SOFT PU COATED LEATHER','A464','2023-04-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2200,'METRO NB',16,'NB',4,'061-81-06','NATURAL MINT','AR-100','FOLLOW COLORO','34A','HYDRO PU COATED LEATHER','M036','2023-04-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2201,'NIKOMAS',17,'ADIDAS',3,'AESX','SILVER GREEN','DE-7','SCOTDIC','34A','PU COATED LEATHER (MAP-ACTION LEATHER)','A762','2023-04-26','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2202,'CHANGSHIN RJ',4,'NIKE',1,'6JB','PINK FOAM','AR-196 M','TMCS0052023042701','PINK','GENERIC PU COATED','A280','2023-04-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2203,'PARKLAND 2',21,'NB',4,'011-50-32','BLAST RED','AR-140','FOLLOW COLORO','TUNGGU XIE','HYDRO SOFT PU COATED LEATHER','A466','2023-04-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2204,'METRO NB',16,'NB',4,'022-63-24','COPPER','AR-100','FOLLOW COLORO','TUNGGU XIE','HYDRO PU COATED LEATHER','M037','2023-04-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2205,'POUYUEN',24,'NIKE',1,'42M','BRIGHT CONCORD','AR-161 M','TSPY0282023041801','PURPLE','GENERIC PU COATED','A1112','2023-05-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2206,'TAEKWANG',30,'NIKE',1,'4PA','BLUE VOID','DE-7','TMTK0272023050401','BLACK','GENERIC PU COATED','A137','2023-05-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2207,'YOUNG TREE',33,'UA',5,'400','ROYAL','AR-196','TMYT0012023050501','44Z','ACTION HYDRO LEATHER','A194','2023-05-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2208,'NIKOMAS IY',18,'NIKE',1,'01B','METALLIC SILVER','UM-T SM','TMNS0202023050501','WHITE','GENERIC PU COATED','A1113','2023-05-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2209,'POUYUEN',24,'NIKE',1,'54U','PURPLE VENOM','AR-161 M','TMPY0282023041801','PURPLE','GENERIC PU COATED LEATHER','A1114','2023-05-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2210,'SAI',37,'NB',4,'019-27-14','RICH OAK COLORO','AR-100','FOLLOW COLORO','BROWN','HYDRO PU COATED LEATHER','A468','2023-05-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2211,'PRATAMA',25,'NIKE',1,'11K','SAIL','AR-185 HG','TMPT0122023050801','WHITE','GENERIC PU COATED LEATHER','A481','2023-10-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2212,'CHANGSHIN',3,'NIKE',1,'44B','MIDNIGHT NAVY','DE-7 SM','TMCS0042023050901','BLACK','GENERIC PU COATED','A281','2023-05-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2213,'POUYUEN',24,'NIKE',1,'86R','CITRON TINT FLOURESCENT','R-8 M','TMPY0282023050901','71R','VIRGIN PU','A1115','2023-05-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2214,'POUYUEN',24,'NIKE',1,'44B','MIDNIGHT NAVY','R-8 M','TMPY0282023050902','BLACK','VIRGIN PU','A1116','2023-05-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2215,'POUYUEN',24,'NIKE',1,'6LC','PICANTE RED','R-8 M','TMPY0282023050903','RED','VIRGIN PU','A1117','2023-05-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2216,'POUYUEN',24,'NIKE',1,'6LD','PINK SPELL FLUORESCENT','R-8 M','TMPY0282023050904','PINK','VIRGIN PU','A1118','2023-05-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2217,'POUYUEN',24,'NIKE',1,'81J','SAFETY ORANGE','R-8 M','TMPY0282023050905','80S','VIRGIN PU','A1119','2023-05-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2218,'POUYUEN',24,'NIKE',1,'76H','SUNDIAL FLUORESCENT','R-8 M','TMPY0282023050906','YELLOW','VIRGIN PU','A1120','2023-05-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:12',NULL),
(2219,'NIKOMAS',17,'ADIDAS',3,'AEDR','SHADOW OLIVE','DE-41','SCOTDIC','LIGHT BROWN','SEMI FULL GRAIN','A763','2023-05-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2220,'POUYUEN',24,'NIKE',1,'3HR','CHARGO KHAKI','R-102 M','TMPY0282023051101','BLACK','GENERIC PU COATED','A1121','2023-05-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2221,'POUYUEN',24,'NIKE',1,'4CA','DARK OBSIDIAN','AR-144 M','TMPY0282023051102','BLACK','VIRGIN HYDRO PU','A1122','2023-05-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2222,'CHANGSHIN RJ',4,'NIKE',1,'3FM','LUCID GREEN','R-8 M','TMCS0052023051301','3GU','GENERIC PU COATED','A283','2023-05-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2223,'CHANGSHIN RJ',4,'NIKE',1,'5BC','STELLAR INDIGO','R-8 M','TMCS0052023051302','GREY','GENERIC PU COATED','A284','2023-05-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2224,'CHANGSHIN RJ',4,'NIKE',1,'47N','UNIVERSITY BLUE','R-8','TMCS0052023051303','BLUE','ECO TECH COMFORT','A285','2023-05-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2225,'PCN G8',59,'NIKE',1,'76B','BRONZINE FLUORESCENT','AR-121 M','TMPG0212023051501','2CT','VIRGIN HYDRO PU LEATHER','A1123','2023-05-16','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2226,'CHANGSHIN RJ',4,'NIKE',1,'73R','VIVID SULFUR','R-102','TMCS0052023051501','YELLOW','GENERIC PU COATED LEATHER','A286',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2227,'CHANGSHIN RJ',4,'NIKE',1,'3CB','OIL GREEN','R-102','TMCS0052023051502','33R','GENERIC PU COATED LEATHER','A287',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2228,'CHANGSHIN RJ',4,'NIKE',1,'44B','MIDNIGHT NAVY','DE-7 SM','TMCS0052023051601','BLACK','GENERIC PU COATED','A288','2023-05-17','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2229,'PANARUB',19,'ADIDAS',3,'48F0','MAROON','AR-167','SCOTDIC','BROWN','SOFT PU COATED LEATHER','A176',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2230,'NIKOMAS IY',18,'NIKE',1,'04Z','PURE PLATINUM','AR-196 M','TMNS0202023051701','WHITE','GENERIC PU COATED LEATHER','A1124','2023-05-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2231,'LONGRICH',41,'UA',5,'001','BLACK','R-184','TMLR0262023052301','BLACK','ACTION PU COATED LEATHER','A195',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2232,'PARKLAND 2',21,'NB',4,'NB 102','WHITE MUNSELL','DE-43','MPW0102023052501','WHITE','HYDRO PU COATED LEATHER','A469',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2233,'NIKOMAS IY',18,'NIKE',1,'0BB','PHOTON DUST','R-131','TMNS0202023052601','WHITE','GENERIC PU COATED','A1125',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2234,'LONGRICH',42,'UA',5,'406','PHOTON BLUE','R-184','MLR0262023071203','44Z','ACTION PU COATED LEATHER','A207',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13','2026-05-19 03:12:13'),
(2235,'LONGRICH',42,'UA',5,'560','PROVENCE PURPLE','R-184','MLR0262023071202','PURPLE','ACTION PU COATED LEATHER','A206',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13','2026-05-19 03:12:13'),
(2236,'LONGRICH',42,'UA',5,'543','PURPLE ACE','R-184','MLR0262023072001','PINK','ACTION PU COATED LEATHER','A208',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13','2026-05-19 03:12:13'),
(2237,'LONGRICH',42,'UA',5,'486','VERSA BLUE','R-184','MLR0262023061502','44Z','ACTION PU COATED LEATHER','A203',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13','2026-05-19 03:12:13'),
(2238,'LONGRICH',42,'UA',5,'419','CAPRI','R-184','MLR0262023071201','4JE','ACTION PU COATED LEATHER','A205',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13','2026-05-19 03:12:13'),
(2239,'CHANGSHIN',3,'NIKE',1,'4HI','HYPER COBALT','R-8','MCS0042023053101','44Z','GENERIC PU COATED','A289','2023-03-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2240,'PCN G8',59,'NIKE',1,'04B','CEMENT GREY','AR-161  M','MPG0212023060501','GREY','GENERIC PU COATED','A1126','2023-07-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2241,'PCN G8',59,'NIKE',1,'74G','YELLOW OCHER','AR-161  M','MPG0212023060502','YELLOW','GENERIC PU COATED','A1127','2023-07-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2242,'NIKOMAS IY',18,'NIKE',1,'11K','SAIL','AR-20 M','TMNS0202023060701','WHITE','GENERIC PU COATED','A1128','2023-08-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2243,'PANARUB',19,'ADIDAS',3,'48F0','MAROON','AR-167','MPA0202023060601','BROWN','SOFT PU COATED LEATHER (MAP-SOFT PU)','A177','2023-08-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2244,'YOUNG TREE',33,'UA',5,'683','PINK SHOCK','AR-196','MYT0012023060601','RED','ACTION PU COATED LEATHER','A201','2023-08-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2245,'POUYUEN',24,'NIKE',1,'44B','MIDNIGHT NAVY','UM-16 SM','TSPY0282023060601','BLACK','GENERIC PU COATED','A1129','2023-09-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2246,'NIKOMAS IY',18,'NIKE',1,'4LX','ARMORY NAVY','AR-107','TSNS0202023060901','BLACK','GENERIC PU COATED','A1130','2023-09-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2247,'CHANGSHIN',3,'NIKE',1,'10J','LT OREWOOD BROWN','AR-144','MCS0042023060901','WHITE','VIRGIN HYDRO PU LEATHER','A290',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2248,'POUYUEN',24,'NIKE',1,'74G','YELLOW OCHER','AR-107 M','TSPY0282023061201','YELLOW','GENERIC PU COATED','A1131',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2249,'NIKOMAS IY',18,'NIKE',1,'76B','BRONZINE FLUORESCENT','AR-121 M','TMNS0202023061301','2CT','VIRGIN HYDRO PU','A1132',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2250,'SAI',37,'NB',4,'145-17-00','BLACK COLORO','R-53','TMSD0462023061401','BLACK','HYDRO SOFT ACTION LEATHER','A470',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2251,'ADIS',1,'NIKE',1,'05Q','FOOTBALL GREY','DE-73','TMAD0022023061501','WHITE','GENERIC PU COATED','A537',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2252,'CHANGSHIN RJ',4,'NIKE',1,'22I','DARK PONY','AR-138','MCS0052023061501','BROWN','VIRGIN HYDRO PU LEATHER','A291',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2253,'CHANGSHIN RJ',4,'NIKE',1,'24Q','EARTH','R-102','MCS0052023061502','BROWN','ECO TECH COMFORT','A292',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2254,'CHANGSHIN RJ',4,'NIKE',1,'05Q','FOOTBALL GREY','R-102','MCS0052023061601','WHITE','ECO TECH COMFORT','A293',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2255,'CHANGSHIN RJ',4,'NIKE',1,'4KY','THUNDER BLUE','R-102','MCS0052023061602','BLACK','ECO TECH COMFORT','A294',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2256,'CHANGSHIN RJ',4,'NIKE',1,'2FN','SMOKEY MAUVE','R-102','MCS0052023061503','PINK','ECO TECH COMFORT','A295',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2257,'LONGRICH',42,'UA',5,'600','RED','R-184','MLR0262023061501','RED','ACTION PU COATED LEATHER','A202',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2258,'TAEKWANG',30,'NIKE',1,'76B','BRONZINE FLUORESCENT','AR-121 M','MTK0272023061601','2CT','VIRGIN HYDRO PU LEATHER','A138',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2259,'POUYUEN',24,'NIKE',1,'6DZ','PINK WASH','AR-161','TSPY0282023062001','PINK','GENERIC PU COATED','A1133',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2260,'SHOETOWN CINA',61,'NIKE',1,'02J','DARK SHADOW','AR-161','MSL0442023062101','BLACK','GENERIC PU COATED','A1134',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2261,'SHOETOWN CINA',61,'NIKE',1,'45F','POWDER BLUE','AR-161','MSL0442023062102','4JE','GENERIC PU COATED','A1135',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2262,'SHOETOWN CINA',61,'NIKE',1,'3KU','VAPOR GREEN','AR-161','MSL0442023062103','71R','GENERIC PU COATED','A1136',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2263,'SHOETOWN CINA',61,'NIKE',1,'37J','NEW EMERALD','AR-161','MSL0442023062104','3GU','GENERIC PU COATED','A1137',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2264,'SCI',32,'NIKE',1,'5AJ','BARELY GRAPE','AR-161','MSC0062023062101','WHITE','GENERIC PU COATED','A1138',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2265,'SCI',32,'NIKE',1,'6LG','PLAYFULL PINK','AR-161','MSC0062023062102','6DX','GENERIC PU COATED','A1139',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2266,'FENGTAY (WEST)',7,'NIKE',1,'4LZ','LT ARMORY BLUE','R-8','MFT0062023062001','WHITE','GENERIC PU COATED','A275',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2267,'ADIS',1,'NIKE',1,'44B','MIDNIGHT NAVY','DE-73','TMAD0022023062201','BLACK','GENERIC PU COATED','A538',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2268,'SMJ',36,'NIKE',1,'04B','CEMENT GREY','AR-20 M','MPT0142023062201','GREY','GENERIC PU COATED','A1140',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2269,'CHINGLUH',5,'NIKE',1,'60Z','LOBSTER','R-8 M','MCL0172023070301','RED','GENERIC PU COATED','A288','2023-04-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2270,'CHINGLUH',5,'NIKE',1,'37J','NEW EMERALD','AR-20 M','MCL0172023070302','3GU','GENERIC PU COATED','A289','2023-04-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2271,'CHINGLUH',5,'NIKE',1,'48A','SPORT BLUE','AR-20 M','MCL0172023070303','44Z','GENERIC PU COATED','A290','2023-04-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2272,'VICTORY/CHINGLUH',31,'NIKE',1,'44M','AQUATONE','AR-20 M','MVC0052023062801','4JE','GENERIC PU COATED','A291','2023-05-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2273,'CHINGLUH',5,'NIKE',1,'44M','AQUATONE','AR-20 M','MCL0172023062801','44Z','GENERIC PU COATED','A292','2023-05-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2274,'FENGTAY',7,'NIKE',1,'10A','WHITE','AR- 121 SG','MFT0082023062801','WHITE','GENERIC PU COATED','A276','2023-05-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2275,'SHOETOWN',28,'NIKE',1,'74G','YELLOW OCHER','AR-161','MSL0442023070401','WHITE','GENERIC PU COATED','A1141','2023-05-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2276,'POUYUEN',24,'NIKE',1,'74G','YELLOW OCHER','AR-161 M','TMPY0282023070401','YELLOW','GENERIC PU COATED','A1142','2023-05-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2277,'POUYUEN',24,'NIKE',1,'12B','SANDDRIFT','R-8 M','TMPY0282023070402','WHITE','GENERIC PU COATED','A1143','2023-05-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2278,'KMK',15,'NIKE',1,'4MD','COASTEL BLUE','R-8 M','MKM0012023070401','4MD','GENERIC PU COATED','A203','2023-05-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2279,'PWI 2',21,'NB',4,'033-75-20','SAND DUNE COLORO','AR-140','FOLLOW COLORO','2CT','HYDRO PU COATED LEATHER','A471','2023-05-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2280,'PWI 2',21,'NB',4,'031-63-17','DOLCE COLORO','DE-135','FOLLOW COLORO','2CT','HYDRO PU COATED LEATHER','A472','2023-05-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2281,'DIAMOND',38,'NB',4,'001-53-09','ROSEWOOD COLORO','AR-100','FOLLOW COLORO','PINK','HYDRO PU COATED LEATHER','A473','2023-05-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2282,'DIAMOND INTERNATIONAL',38,'NB',4,'117-38-21','BLUE AGATE COLORO','AR-100','FOLLOW COLORO','BLUE','HYDRO SOFT PU COATED LEATHER','A474','2023-06-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2283,'PWI 2',21,'NB',4,'117-47-13','HERON BLUE COLORO','AR-140','FOLLOW COLORO','4MD','HYDRO SOFT PU COATED LEATHER','A475','2023-06-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2284,'PWI 2',21,'NB',4,'091-37-08','NEW SPURCE COLORO','DE-135','FOLLOW COLORO','33R','HYDRO SOFT PU COATED LEATHER','A476','2023-06-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2285,'POUYUEN',24,'NIKE',1,'04B','CEMENT GREY','AR-161 M','TMPY0282023070601','GREY','GENERIC PU COATED','A1144','2023-08-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2286,'POUYUEN',24,'NIKE',1,'4NZ','HALF BLUE','R-131 M','TMPY0282023070602','WHITE','GENERIC PU COATED','A1145','2023-08-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2287,'LONGRICH',42,'UA',5,'100','WHITE','R-184','MLR0262023070701','WHITE','ACTION PU COATED LEATHER','A204','2023-08-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2288,'VICTORY',31,'NIKE',1,'4PB','ASHEN SLATE','AR-20','MVC0052023070601','LT BLUE','GENERIC PU COATED','A293','2023-11-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2289,'CHINGLUH',5,'NIKE',1,'02J','DARK SHADOW','AR-161','MCL0172023070601','BLACK','GENERIC PU COATED','A294','2023-11-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2290,'SHOETOWN',28,'NIKE',1,'6DZ','PINK WASH','AR-161 M','MSL0432023071301','WHITE','GENERIC PU COATED','A1146',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2291,'DIAMOND',38,'NB',4,'114-81-10','BRIGHT SKY COLORO','AR-100','FOLLOW COLORO','LT BLUE','HYDRO PU COATED LEATHER','A477',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2292,'METRO',16,'NB',4,'006-70-08','ORB PINK COLORO','AR-100','FOLLOW COLORO','PINK','HYDRO PU COATED LEATHER','M038',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2293,'METRO',16,'NB',4,'123-76-02','GRANITE COLORO','AR-100','FOLLOW COLORO','OIV','HYDRO PU COATED LEATHER','M039',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2294,'VICTORY/CHINGLUH',31,'NIKE',1,'74G','YELLOW OCHER','R-53 M','MCL0172023071701','YELLOW','GENERIC PU COATED','A295',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2295,'CHANGSHIN',3,'NIKE',1,'4NP','HYPER BLUE','AR-20 M','MCS0042023071701','WHITE','GENERIC PU COATED','A296',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2296,'CHANGSHIN',3,'NIKE',1,'45B','OBSIDIAN','AR-20 M','MCS0042023071702','BLACK','GENERIC PU COATED','A297',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2297,'CHANGSHIN RJ',4,'NIKE',1,'76B','BRONZINE FLUORESCENT','AR-121 M','MCS0052023071701','2CT','VIRGIN HYDRO PU LEATHER','A298',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2298,'CHANGSHIN RJ',4,'NIKE',1,'7BA','SATURN GOLD','AR-121 M','MCS0052023071702','YELLOW','VIRGIN HYDRO PU LEATHER','A299',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2299,'CHINGLUH',5,'NIKE',1,'74G','YELLOW OCHER','AR-161 M','MCL0172023072001','WHITE','GENERIC PU COATED','A296',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2300,'CHINGLUH',5,'NIKE',1,'45F','DK POWDER BLUE','AR-161','MCL0172023070602','4JE','GENERIC PU COATED','A297',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2301,'VICTORY',31,'NIKE',1,'5BX','AMETHIST ASH','AR-20 M','MVC0052023070602','01V','GENERIC PU COATED','A298',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2302,'CHANGSHIN RJ',4,'NIKE',1,'2EQ','PARTICLE BEIGE','UMT','MCS0052023072002','WHITE','GENERIC PU COATED','A300',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2303,'CHANGSHIN RJ',4,'NIKE',1,'45B','OBSIDIAN','AR-20','MCS0052023072003','BLACK','GENERIC PU COATED','A301',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2304,'CHANGSHIN RJ',4,'NIKE',1,'4NP','HYPER ROYAL','AR-20','MCS0052023072004','WHITE','GENERIC PU COATED','A302',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2305,'CHANGSHIN RJ',4,'NIKE',1,'0AI','IRON GREY','AR-196','MCS0052023072005','BLACK','GENERIC PU COATED','A303',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2306,'CHANGSHIN RJ',4,'NIKE',1,'2EQ','PARTICLE BEIGE','DE-90','MCS0052023072001','WHITE','GENERIC PU COATED','A304',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2307,'NIKOMAS',17,'ADIDAS',3,'AA2R','GREY ONE','DE-41','MNS0162023071701','WHITE','SEMI FULL GRAIN','A764','2023-07-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2308,'ADIS',1,'NIKE',1,'6JE','WASHED CORAL','AR-20','MAD0022023072001','PINK','VIRGIN HYDRO PU LEATHER','A539',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2309,'FENGTAY',7,'NIKE',1,'0BB','PHOTON DUST','AR-144','MFT0062023071701','WHITE','VIRGIN HYDRO PU','A277',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2310,'TAH SUNG HUNG',34,'ADIDAS',3,'AELB','MAGIC BEIGE','DE-73 SM','MTS0012023072001','WHITE (REQ BACKING)','PU COATED LEATHER (MAP ACTION LEATHER)','A765',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2311,'PARKLAND 2',21,'NB',4,'022-60-08','FLAT TAUPE','AR-140','TMPW0102023072101','01V','HYDRO PU COATED LEATHER','A479',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2312,'CHINGLUH',5,'NIKE',1,'37J','NEW EMERALD','AR-161 M','MCL0172023072601','3GU','GENERIC PU COATED','A299',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2313,'CHINGLUH',5,'NIKE',1,'06B','COOL GREY','AR-161','MCL0172023072602','GREY','GENERIC PU COATED','A300',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2314,'CHINGLUH',5,'NIKE',1,'3KU','VAPOR GREEN','AR-161 M','MCL0172023072603','71R','GENERIC PU COATED','A301',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2315,'DIAMOND INTERNATIONAL',38,'NB',4,'001-53-09','ROSEWOOD COLORO','AR-100','TSDI0242023072701','PINK','HYDRO PU COATED LEATHER','A480',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2316,'DIAMOND INTERNATIONAL',38,'NB',4,'079-26-18','MARSH GREEN COLORO','AR-100','TSDI0242023072702','33R','HYDRO PU COATED LEATHER','A481',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2317,'DIAMOND INTERNATIONAL',38,'NB',4,'034-84-05','LINEN COLORO','AR-73','TSDI0242023072703','WHITE','HYDRO PU COATED LEATHER','A482',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2318,'PARKLAND 2',21,'NB',4,'079-26-18','MARSH GREEN COLORO','AR-140','TSPW0102023072801','33R','HYDRO PU COATED LEATHER','A483',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2319,'PARKLAND 2',21,'NB',4,'110-66-12','CHROME BLUE','AR-140','TSPW0102023072802','LT BLUE','HYDRO PU COATED LEATHER','A484',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2320,'PARKLAND 2',21,'NB',4,'011-50-32','BLAST RED COLORO','AR-140','TSPW0102023072803','RED','HYDRO PU COATED LEATHER','A485',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2321,'SHOETOWN',28,'NIKE',1,'45F','DK POWDER BLUE','AR-161','MSL0432023072801','4JE','GENERIC PU COATED (1031422)','A1147',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2322,'SHOETOWN',28,'NIKE',1,'37J','NEW EMERALD','AR-161','MSL0432023072802','3GU','GENERIC PU COATED','A1148',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2323,'SHOETOWN',28,'NIKE',1,'02J','DARK SHADOW','AR-161','MSL0432023072803','BLACK','GENERIC PU COATED (1031430)','A1149',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2324,'SHOETOWN',28,'NIKE',1,'3KU','VAPOR GREEN','AR-161','MSL0432023072804','71R','GENERIC PU COATED (1031561)','A1150',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2325,'CHANGSHIN RJ',4,'NIKE',1,'01X','PHANTOM','DE-126','MCS0052023072701','WHITE','GENERIC PU COATED','A305','2023-01-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2326,'CHINGLUH',5,'NIKE',1,'04B','CEMENT GREY','AR-161 M','MCL0172023080101','01V','GENERIC PU COATED','A302',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2327,'PRATAMA',25,'NIKE',1,'24Q','EARTH','R-53','MPT0122023072801','BROWN','GENERIC PU COATED LEATHER','A482','2023-02-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2328,'PARKLAND 2',21,'NB',4,'034-84-05','LINEN COLORO','AR-64','TSPW0102023080201','WHITE','HYDRO PU COATED LEATHER','A486','2023-08-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2329,'METRO',16,'NB',4,'117-41-18','SEA STONE','DE-90','FOLLOW COLORO','BLUE','HYDRO PU COATED LEATHER','M040','2023-08-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2330,'METRO',16,'NB',4,'NB103','WHITE','DE-90','SAMPLE PINJAM','WHITE','HYDRO PU COATED LEATHER','M041','2023-08-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2331,'TAEKWANG',30,'NIKE',1,'10J','LT OREWOOD BROWN','AR-144','TMTK0272023080401','WHITE','VIRGIN HYDRO PU LEATHER','A139','2023-08-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2332,'PARKLAND 2',21,'NB',4,'117-47-13','HERON BLUE COLORO','AR-140','TSPW0102023080401','BLACK','HYDRO PU COATED LEATHER','A487','2023-08-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2333,'PARKLAND 2',21,'NB',4,'033-75-20','SAND DUNE COLORO','AR-140','TSPW0102023080402','2CT','HYDRO PU COATED LEATHER','A488','2023-08-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2334,'PARKLAND 2',21,'NB',4,'105-27-15','DEEP SEA','AR-140','TSPW0102023080403','3AW','HYDRO PU COATED LEATHER','A489','2023-08-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2335,'SAI',37,'NB',4,'019-27-14','RICH OAK COLORO','AR-100 M','TMSD0462023080701','BROWN','HYDRO PU COATED LEATHER','A490','2023-09-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2336,'KMK',15,'NIKE',1,'0BA','PLATINUM VIOLET','AR-167 DM','MKM0012023080901','WHITE','GENERIC PU COATED','A204','2023-09-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2337,'LONGRICH/YMUV',41,'UA',5,'572','VIVID MAGENTA','R-184','MYM0012023080901','6DX','ACTION PU COATED LEATHER','A209','2023-11-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2338,'LONGRICH/YMUV',41,'UA',5,'464','NIMBUS BLUE','R-184','MYM0012023080902','WHITE','ACTION PU COATED LEATHER','A210','2023-11-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2339,'LONGRICH/YMUV',41,'UA',5,'432','TECH BLUE','R-184','MYM0012023080903','44Z','ACTION PU COATED LEATHER','A211','2023-11-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2340,'LONGRICH/YMUV',41,'UA',5,'011','MOD GREY','R-184','MYM0012023080904','GREY','ACTION PU COATED LEATHER','A212','2023-11-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2341,'PCN G8',59,'NIKE',1,'01V','WOLF GREY','UM-34','MPG0212023081101','WHITE','GENERIC PU COATED','A1151','2023-11-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2342,'CHANGSHIN RJ',4,'NIKE',1,'6JB','PINK FOAM','AR-33','MCS0052023080901','PINK','VIRGIN HYDRO PU LEATHER','A306','2023-11-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2343,'NIKOMAS IY',18,'NIKE',1,'4LX','ARMORY NAVY','AR-107 M','TMNS0202023081401','BLACK','GENERIC PU COATED (MB020018432)','A1152',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2344,'METRO NB',16,'NB',4,'072-35-21','CLASSIC PINE COLORO','AR-100 M','FOLLOW COLORO','33R','HYDRO PU COATED LEATHER','M042',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2345,'METRO NB',16,'NB',4,'115-40-33','BLUE OASIS COLORO','DE-90','FOLLOW COLORO','BLUE','HYDRO SOFT ACTION LEATHER','M043',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2346,'CHANGSHIN RJ',4,'NIKE',1,'2FN','SMOKEY MAUVE','R-53','MCS0052023081401','PINK','GENERIC PU COATED LEATHER','A307',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2347,'CHINGLUH',5,'NIKE',1,'37J','NEW EMERALD','AR-20 M','MCL0172023081401','3GU','GENERIC PU COATED (RI0085751037J)','A303',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2348,'LONGRICH/YMUV',41,'UA',5,'400','TEAM ROYAL','R-184','MYM0012023081401','44Z','ACTION PU COATED LEATHER','A213',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2349,'TAEKWANG',30,'NIKE',1,'6GM','RUST PINK','AR-196 M','TMTK0272023080402','PINK','VIRGIN HYDRO PU','A140',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2350,'METRO NB',16,'NB',4,'152-76-11','MID CENTURY PINK COLORO','AR-100 M','FOLLOW COLORO','PINK','HYDRO PU COATED LEATHER','M044',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2351,'LONGRICH/YMUV',41,'UA',5,'525','LAVISH','R-184','MYM0012023081402','PURPLE','ACTION PU COATED LEATHER','A214',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2352,'METRO NB',16,'NB',4,'012-39-36','TRUE RED COLORO','AR-100','FOLLOW COLORO','RED','HYDRO PU COATED LEATHER','M045',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2353,'LONGRICH',42,'UA',5,'011','MOD GRAY','AR-175','FOLLOW CSI UA','GREY','ECO TECH GREEN LEATHER','A215',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2354,'LONGRICH',42,'UA',5,'482','RADIAL TURQUOISE','R-184','MLR0262023072601','3GU','ACTION PU COATED LEATHER','A216',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2355,'LONGRICH',42,'UA',5,'014','HALO GRAY','AR-175','FOLLOW CSI UA','WHITE','ECO GREEN LEATHER','A217',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2356,'DWI PRIMA SENTOSA',45,'UA',5,'023','DISTANT GRAY','R-231','FOLLOW CSI UA','WHITE','SOHO NUBUCK','A218',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2357,'LONGRICH',42,'UA',5,'500','PURPLE','R-184','MLR0262023082201','BLACK','ACTION PU COATED LEATHER','A219',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2358,'ADIS',1,'NIKE',1,'73P','BARELY VOLT FLUORESCENT','AR-20 M','MAD0022023082501','WHITE','VIRGIN HYDRO PU LEATHER','A540',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2359,'CHANGSHIN RJ',4,'NIKE',1,'65N','UNIVERSITY RED','DE-73','MCS0052023082501','RED','GENERIC PU COATED','A308',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2360,'NIKOMAS',17,'ADIDAS',3,'A0TO','CLAY','DE-7','SCOTDIC','3MR','SOFT PU COATED LEATHER (MAP-SOFT PU)','A766',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2361,'NIKOMAS',17,'ADIDAS',3,'AF45','PUTTY GREY','DE-7','MNS0162023111702','01V','SOFT PU COATED LEATHER (MAP-SOFT PU)','A778',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13','2026-05-19 03:12:19'),
(2362,'NIKOMAS',17,'ADIDAS',3,'AF4M','PRELOVED','DE-7','SCOTDIC','01V','SOFT PU COATED LEATHER (MAP-SOFT PU)','A768',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2363,'NIKOMAS',17,'ADIDAS',3,'AEKE','SHADOW GREEN','DE-7','SCOTDIC','BLACK','SOFT PU COATED LEATHER (MAP-SOFT PU)','A769',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2364,'NIKOMAS',17,'ADIDAS',3,'AESW','SILVER PEBBLE','DE-7','SCOTDIC','3MR','SOFT PU COATED LEATHER (MAP-SOFT PU)','A770',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2365,'NIKOMAS',17,'ADIDAS',3,'AFAP','SEMI PINK SPARK','DE-7','SCOTDIC','PINK','SOFT PU COATED LEATHER (MAP-SOFT PU)','A771',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2366,'DIAMOND INTERNATIONAL',38,'NB',4,'020-77-45','HOT MANGO COLORO','AR-100 M','FOLLOW COLORO','80S','HYDRO PU COATED LEATHER','A491',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2367,'DIAMOND INTERNATIONAL',38,'NB',4,'088-64-27','AIRY TEAL COLORO','AR-100 M','FOLLOW COLORO','3GU','HYDRO PU COATED LEATHER','A492',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2368,'CHANGSHIN',3,'NIKE',1,'0AE','VAST GREY','UM-34','MCS0042023083001','WHITE','VIRGIN HYDRO PU LEATHER','A309',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2369,'METRO NB',16,'NB',4,'120-84-00','QUARTER GREY COLORO','AR-100 M','FOLLOW COLORO','01V','HYDRO PU COATED LEATHER','A493','2023-01-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2370,'PARKLAND 2',21,'NB',4,'049-66-05','OLIVINE COLORO','DE-135','FOLLOW COLORO','3MR','HYDRO PU COATED LEATHER','A494','2023-04-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2371,'PARKLAND 2',21,'NB',4,'149-40-00','CASTLEROCK COLORO','DE-135','FOLLOW COLORO','GREY','HYDRO PU COATED LEATHER','A495','2023-04-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:13',NULL),
(2372,'LONGRICH',42,'UA',5,'432','TECH BLUE','AR-194','MLR0262023112202','44Z','ACTION PU COATED LEATHER','A236',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14','2026-05-19 03:12:19'),
(2373,'NIKOMAS IY',18,'NIKE',1,'70Z','SOFT YELLOW','R-8 M','TMNS0202023090601','YELLOW','VIRGIN HYDRO PU (MB 020019160)','A1153','2023-08-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2374,'KMK',15,'NIKE',1,'0BA','PLATINUM VIOLET','R-8 SG','MKM0012023090501','WHITE','GENERIC PU COATED','A205','2023-11-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2375,'FENGTAY',7,'NIKE',1,'6LG','PLAYFULL PINK FLUORESCENT','R-8 SG','MFT0382023090701','6DX','GENERIC PU COATED','A278','2023-11-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2376,'DWI PRIMA SENTOSA',45,'UA',5,'279','STONE','AR-194','FOLLOW CSI UA','WHITE','PU COATED LEATHER','A221','2023-12-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2377,'VICTORY',31,'NIKE',1,'3KC','GREEN GLOW FLUORESCENT','R-53','MVC0052023090801','4AU','GENERIC PU COATED LEATHER','A304',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2378,'NIKOMAS',17,'ADIDAS',3,'AETG','BETTER SCARLET','DE-41','MNS0162023091101','RED','SEMI FULL GRAIN (RS)','A772',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2379,'NIKOMAS',17,'ADIDAS',3,'A8L5','CRYSTAL WHITE','DE-41','MNS0162023091102','WHITE','SEMI FULL GRAIN (RS)','A773',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2380,'BIG',2,'ADIDAS',3,'AD8R','TEAM ROYAL BLUE','AR-194','FMCA PANARUB','44Z','PU COATED LEATHER (MAP-ACTION LEATHER)','A178',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2381,'YMUV',39,'UA',5,'500','PURPLE','R-184','MYM0012023091501','BLACK','ACTION PU COATED LEATHER','A222',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2382,'ADIS',1,'NIKE',1,'32D','AQUAMARINE FLUORESCENT','DE-73 SM','MAD0022023091501','4JE','GENERIC PU COATED','A541',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2383,'NIKOMAS IY',18,'NIKE',1,'31B','MALACHITE','R-53','TMNS0202023091901','3GU','VIRGIN HYDRO PU (MB 020019085)','A1154',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2384,'PCN G8',59,'NIKE',1,'0BA','PLATINUM VIOLET','R-8SG','MPG0212023092101','WHITE','GENERIC PU COATED (MB020018432)','A1155','2023-09-21','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2385,'CHANGSHIN RJ',4,'NIKE',1,'6HM','BURGUNDY CRUSH','AR-138','MCS0052023092501','BROWN','VIRGIN HYDRO PU LEATHER','A310',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2386,'ADIS',1,'NIKE',1,'50Z','VIOTECH FLOURESCENT','DE-73 SM','MAD0022023092701','PURPLE','GEENRIC PU COATED','A542','2023-03-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2387,'CHANGSHIN RJ',4,'NIKE',1,'01X','PHANTOM','AR-138','MCS0052023100201','WHITE','VIRGIN HYDRO PU LEATHER','A311','2023-03-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2388,'CHANGSHIN RJ',4,'NIKE',1,'0AH','DK SMOKE GREY','R-102','TMCS0052025070101','BLACK','ECO TECH COMFORT','A399','2025-01-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14','2026-05-19 03:12:24'),
(2389,'PCN G8',59,'NIKE',1,'86L','CRIMSON TINT','UM-34','MPG0212023100201','WHITE','GENERIC PU COATED','A1155','2023-03-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2390,'PCN G8',59,'NIKE',1,'0BA','PLATINUM VIOLET','R-8SG','MPG0212023092101','WHITE','GENERIC PU COATED','A1156','2023-05-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2391,'FENGTAY',7,'NIKE',1,'14A','OFF WHITE','AR-121 M','MFT0382023100501','WHITE','GENRIC PU COATED','A279','2023-05-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2392,'SCI',32,'NIKE',1,'4LZ','LT ARMORY BLUE','AR-161 M','MSC0062023092601','LT. BLUE','GENERIC PU COATED','A1157','2023-05-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2393,'POUYUEN',24,'NIKE',1,'33X','VINTAGE GREEN','R-8 M','TMPY0282023100501','WHITE','GENERIC PU COATED','A1158','2023-05-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2394,'METRO NB',16,'NB',4,'024-80-25','NB PEACH BLOSSOM','AR-140','TMMP0332024053002','2CT','HYDRO PU COATED LEATHER','M066','2024-07-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14','2026-05-19 03:12:21'),
(2395,'METRO NB',16,'NB',4,'074-80-06','CLAY ASH','AR-140','TMMP0332024053001','34A','HYDRO PU COATED LEATHER','M065','2024-07-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14','2026-05-19 03:12:21'),
(2396,'METRO NB',16,'NB',4,'125-55-08','DUSK SHOWER','AR-100','FOLLOW COLORO','49D','HYDRO PU COATED LEATHER','M048','2023-06-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2397,'METRO NB',16,'NB',4,'156-81-08','ROSE SUGAR','AR-140','TMMP0332024053003','PINK','HYDRO PU COATED LEATHER','M067','2024-07-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14','2026-05-19 03:12:21'),
(2398,'METRO NB',16,'NB',4,'072-45-06','DARK JUNIPER','AR-100','FOLLOW COLORO','33R','HYDRO PU COATED LEATHER','M050','2023-10-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2399,'METRO NB',16,'NB',4,'124-91-00/NB103','WHITE','AR-140','FOLLOW COLORO','WHITE','HYDRO PU COATED LEATHER','M051','2023-10-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2400,'PANARUB',19,'ADIDAS',3,'48F0','MAROON','AR-169 DM','MPA0202023100901','BROWN','SOFT PU COATED LEATHER (MAP-SOFT PU)','A179','2023-10-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2401,'YMUV',39,'UA',5,'110','SUMMIT WHITE','R-184','FOLLOW CSI UA','WHITE','ACTION PU COATED LEATHER','A223','2023-11-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2402,'YMUV',39,'UA',5,'410','MIDNIGHT NAVY','R-184','FOLLOW CSI UA','4MD','ACTION PU COATED LEATHER','A224','2023-11-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2403,'YMUV',39,'UA',5,'428','ELECTRIC BLUE','R-184','FOLLOW CSI UA','4JE','ACTION PU COATED LEATHER','A225','2023-11-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2404,'YMUV',39,'UA',5,'464','NIMBUS BLUE','UM-T SM','FOLLOW CSI UA','WHITE','ACTION PU COATED LEATHER','A226','2023-11-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2405,'YMUV',39,'UA',5,'514','ANDROMEDA PURPLE','R-184','FOLLOW CSI UA','6DX','ACTION PU COATED LEATHER','A227','2023-11-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2406,'SMJ',36,'NIKE',1,'4KY','THUNDER BLUE','AR-20','MPT0142023100201','BLACK','GENERIC PU COATED','A1159','2023-11-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2407,'YMUV',39,'UA',5,'114','WHITE CLAY','UM-T SM','FOLLOW CSI UA','WHITE','PU COATED LEATHER','A228','2023-12-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2408,'YMUV',39,'UA',5,'639','PINK VORTEX','R-184','FOLLOW CSI UA','PINK','ACTION PU COATED LEATHER','A229','2023-12-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2409,'DWI PRIMA SENTOSA',45,'UA',5,'465','HORIZON BLUE','UM-T SM','FOLLOW CSI UA','LT. BLUE','PU COATED LEATHER','A230','2023-12-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2410,'LONGRICH',42,'UA',5,'731','HIGH-VIS YELLOW','AR-216','MLR0262024011602','71R','ACTION PU COATED LEATHER','A248',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14','2026-05-19 03:12:20'),
(2411,'METRO NB',16,'NB',4,'011-80-11','PINK HAZE','AR-100 M','FOLLOW COLORO','PINK','HYDRO PU COATED LEATHER','M052',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2412,'VICTORY',31,'NIKE',1,'42Z','COURT BLUE','R-8','MVC0052023101601','44Z','ECO TECH COMFORT','A305',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2413,'FENGTAY',7,'NIKE',1,'05Y','DESERT SAND','UM-34','MFT0072023101701','WHITE','GENERIC PU COATED','A280',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2414,'DIAMOND',38,'NB',4,'028-67-41','MARIGOLD','AR-100 M','FOLLOW COLORO','2CT','HYDRO PU COATED LEATHER','A497',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2415,'DIAMOND',38,'NB',4,'19-3952 TPX','SURF THE WEB','AR-100 M','FOLLOW PANTONE TPX','44Z','HYDRO PU COATED LEATHER','A498',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2416,'DWI PRIMA SENTOSA',45,'UA',5,'100','WHITE LEATHER','UM-T SM','FOLLOW CSI UA LEATHER','WHITE','ACTION PU COATED LEATHER','A232',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2417,'YMUV',39,'UA',5,'862','ARES RED','R-184','FOLLOW CSI UA','80S','ACTION PU COATED LEATHER','A233',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2418,'KMK',15,'NIKE',1,'0AH','DK SMOKE GREY','R-8','MKM0012023102601','BLACK','VIRGIN HYDRO PU','A206',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2419,'METRO NB',16,'NB',4,'006-70-08','ORB PINK COLORO','AR-100 M','TMMP0332023102601','PINK','HYDRO PU COATED LEATHER','M053',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2420,'VICTORY',31,'NIKE',1,'12B','SANDDRIFT','AR-20 M','MVC0052023103001','WHITE','GENERIC PU COATED','A306',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2421,'CHINGLUH',5,'NIKE',1,'05Q','FOOTBALL GREY','UM-T SM','MCL0172023103001','WHITE','GENERIC PU COATED','A307',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2422,'POUYUEN',24,'NIKE',1,'0BA','PLATINUM VIOLET','R-8 SG','TMPY0282023110101','WHITE','GENERIC PU COATED','A1160','2023-03-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2423,'FENGTAY',7,'NIKE',1,'14A','OFF WHITE','AR-121 M','MFT0062023110201','WHITE','GENERIC PU COATED','A281','2023-03-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2424,'METRO NB',16,'NB',4,'11-4001TCX','BRILLIANT WHITE','AR-100','TMMP0332023110601','WHITE','HYDRO PU COATED LEATHER','M054','2023-11-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2425,'PARKLAND 2',21,'NB',4,'091-37-08','NEW SPURCE COLORO','DE-135','TMPW0102023110201','33R','HYDRO PU COATED LEATHER','A499','2023-07-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2426,'PARKLAND 2',21,'NB',4,'031-63-17','DOLCE COLORO','DE-135','TMPW0102023110202','2CT','HYDRO PU COATED LEATHER','A500','2023-07-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2427,'PARKLAND 2',21,'NB',4,'124-23-11','NB NAVY COLORO','DE-135','TMPW0102023110301','BLACK','HYDRO PU COATED LEATHER','A501','2023-07-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2428,'PARKLAND 2',21,'NB',4,'036-90-02','SEA SALT COLORO','DE-135','TMPW0102023110302','WHITE','HYDRO PU COATED LEATHER','A502','2023-07-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2429,'PARKLAND 2',21,'NB',4,'8001C','SILVER METALLIC PANTONE','AR-140','TMPW0102024031201','WHITE','HYDRO PU COATED LEATHER','A511',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14','2026-05-19 03:12:20'),
(2430,'METRO NB',16,'NB',4,'036-90-02','NEW SEA SALT','AR-100 M','TMMP0332023110602','WHITE','HYDRO PU COATED LEATHER','M055','2023-07-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2431,'CHANGSHIN RJ',4,'NIKE',1,'6FW','RACER PINK FLUORESCENT','AR-20 M','MCS0052023110601','RED','GENERIC PU COATED','A313','2023-07-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2432,'CHANGSHIN RJ',4,'NIKE',1,'4KY','THUNDER BLUE','AR-20','MCS0052023110602','BLACK','GENERIC PU COATED','A314','2023-07-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2433,'DIAMOND',38,'NB',4,'020-77-45','HOT MANGO COLORO','AR-100 M','TMDI0242023110901','80S','HYDRO PU COATED LEATHER','A504','2023-10-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2434,'DIAMOND',38,'NB',4,'088-64-27','AIRY TEAL COLORO','AR-100','TMDI0242023110902','3GU','HYDRO PU COATED LEATHER','A505','2023-10-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2435,'DPS',45,'UA',5,'001','BLACK','AR-191 M','MDW0012023110901','BLACK','ACTION PU COATED LEATHER','A234',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2436,'VICTORY',31,'NIKE',1,'11K','SAIL','AR-196 M','MVC0052023110601','WHITE','GENERIC PU COATED','A308',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14',NULL),
(2437,'CHANGSHIN RJ',4,'NIKE',1,'4LX','ARMORY NAVY','R-102','TMCS0052025012001','BLACK','ECO TECH COMFORT','A376',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:14','2026-05-19 03:12:23'),
(2438,'DIAMOND INTERNATIONAL',38,'NB',4,'075-35-13','TEAM FOREST GREEN','AR-100','TSDI0242024020101','33R','HYDRO PU COATED LEATHER','A510','2024-06-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19','2026-05-19 03:12:20'),
(2439,'POUYUEN',24,'NIKE',1,'47X','DEEP ROYAL BLUE','R-53','TMPY0282023111401','44Z','GENERIC PU COATED','A1161',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2440,'BIG',2,'ADIDAS',3,'48F0','MAROON','AR-169','FMCA PANARUB','BROWN','SOFT PU COATED LEATHER (MAP-SOFT PU)','A180',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2441,'NIKOMAS',17,'ADIDAS',3,'A172','CYBER MET','DE-7','SCOTDIC','2CT','SOFT PU COATED LEATHER (MAP-SOFT PU)','A775',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2442,'NIKOMAS',17,'ADIDAS',3,'AFDF','PURE RUBY','DE-7','SCOTDIC','RED','SOFT PU COATED LEATHER (MAP-SOFT PU)','A776',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2443,'NIKOMAS IY',18,'NIKE',1,'4LZ','LIGHT ARMORY BLUE','R-53','TMNS0202023111501','LT. BLUE','GENERIC PU COATED MB020019438','A1162',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2444,'NIKOMAS',17,'ADIDAS',3,'AE6S','WONDER WHITE','DE-7','MNS0162023111701','WHITE','SOFT PU COATED LEATHER (MAP-SOFT PU)','A777',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2445,'NIKOMAS IY',18,'NIKE',1,'3KD','LEGION GREEN','UM-34T SM','TSNS0202023111601','33R','GENERIC PU COATED MB020020037','A1163',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2446,'NIKOMAS IY',18,'NIKE',1,'27Q','DK DRIFTWOOD','UM-34T SM','TSNS0202023111602','2CT','GENERIC PU COATED MB020020182','A1164',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2447,'PCN G8',59,'NIKE',1,'44B','MIDNIGHT NAVY','DE-7','MPG0212023111701','4MD','GENERIC PU COATED','A1165',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2448,'VICTORY',31,'NIKE',1,'44B','MIDNIGHT NAVY','AR-20 M','MVC0052023111401','BLACK','GENERIC PU COATED','A309',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2449,'KMK',15,'NIKE',1,'25M','SESAME','AR-120 M','MKM0012023112101','2CT','VIRGIN HYDRO PU','A207',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2450,'NIKOMAS',17,'ADIDAS',3,'AFA7','UTILITY YELLOW','DE-7','SCOTDIC','YELLOW','SOFT PU COATED LEATHER (MAP-SOFT PU)','A779',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2451,'LONGRICH',42,'UA',5,'001','BLACK','AR-194','MLR0262023112201','BLACK','ACTION PU COATED LEATHER','A235',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2452,'METRO NB',16,'NB',4,'011-50-32','BLAST RED','AR-100','TMMP0332023112401','RED','HYDRO PU COATED LEATHER','M057',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2453,'POUYUEN',24,'NIKE',1,'44B','MIDNIGHT NAVY','DE-7','TSPY0282023112301','BLACK','GENERIC PU COATED','A1166',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2454,'TAEKWANG',30,'NIKE',1,'4RD','AQUARIUS BLUE','AR-144 M','TMTK0272023112701','4JE','VIRGIN HYDRO PU','A141',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2455,'LONGRICH',42,'UA',5,'014','HALO GRAY','R-184','MLR0262023112901','WHITE','ACTION PU COATED LEATHER','A237',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2456,'SHOETOWN',28,'NIKE',1,'01X','PHANTOM','AR-167','MSL0432023113001','WHITE','GENERIC PU COATED','A1167','2023-01-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2457,'LONGRICH',42,'UA',5,'628','BETA','AR-194','MLR0262023120501','WHITE','ACTION PU COATED LEATHER','A238','2023-05-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2458,'DIAMOND INTERNATIONAL',38,'NB',4,'117-38-21','BLUE AGATE COLORO','AR-100','TMDI0242023120602','BLUE','HYDRO PU COATED LEATHER','A507','2023-08-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2459,'NIKOMAS',17,'ADIDAS',3,'AECV','WONDER MAUVE','DE-41','SCOTDIC','PINK','SEMI FULL GRAIN','A780','2023-08-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2460,'DIAMOND INTERNATIONAL',38,'NB',4,'114-81-10','BRIGHT SKY COLORO','AR-100','TMDI0242023120601','LT BLUE','HYDRO PU COATED LEATHER','A508','2023-08-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2461,'KMK',15,'NIKE',1,'0BA','PLATINUM VIOLET','AR-144','MKM0012023121101','PINK','VIRGIN HYDRO PU','A208','2023-12-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2462,'SHOETOWN',28,'NIKE',1,'51B','BLACK RASPBERRY','DE-73','MSL0432023121501','49D','GENERIC PU COATED','A1168',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2463,'PCN G8',59,'NIKE',1,'64M','VARSITY RED','CPUG','SPG0212023121301','WHITE','FP LS PATENT LEATHER','A1169',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2464,'FENGTAY',7,'NIKE',1,'46B','ASTRONOMY BLUE','AR-144','MFT0082023121201','44Z','VIRGIN HYDRO PU','A282',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2465,'METRO NB',16,'NB',4,'128-34-13','DREAM STATE','AR-140','TMMP0332024071501','49D','HYDRO PU COATED LEATHER','M070',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19','2026-05-19 03:12:22'),
(2466,'LONGRICH',42,'UA',5,'572','VIVID MAGENTA','R-184','MLR0262023121901','6DX','ACTION PU COATED LEATHER','A239',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2467,'LONGRICH',42,'UA',5,'464','NIMBUS BLUE','R-184','MLR0262023121902','WHITE','ACTION PU COATED LEATHER','A240',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2468,'LONGRICH',42,'UA',5,'011','MOD GREY','R-184','MLR0262023121903','GREY','ACTION PU COATED','A241',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2469,'PARKLAND 2',21,'NB',4,'039-90-05','ANGORA COLORO','AR-140','FOLLOW COLORO','WHITE','HYDRO PU COATED LEATHER','A509',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2470,'METRO NB',16,'NB',4,'135-70-21','LILAC GLO','AR-100','TMMP0332024042501','49D','HYDRO PU COATED LEATHER','M061',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19','2026-05-19 03:12:21'),
(2471,'LONGRICH',42,'UA',5,'432','TECH BLUE','R-184','MLR0262023122001','44Z','ACTION PU COATED LEATHER','A242',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2472,'LONGRICH',42,'UA',5,'400','TEAM ROYAL','AR-216','MLR0262023122103','44Z','ACTION PU COATED LEATHER','A243',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2473,'GLOSTAR (ADS)',12,'ADIDAS',3,'A0TR','MATTE SILVER','DE-7','MGS0072023122101','WHITE','SOFT PU COATED LEATHER','A781',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2474,'GLOSTAR',11,'ADIDAS',3,'AEKE','SHADOW GREEN','DE-7','MGS0072023122102','BLACK','SOFT PU COATED','A782',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2475,'NIKOMAS IY',18,'NIKE',1,'44B','MIDNIGHT NAVY','DE-7 SM','TMNS0202023122201','4MD','GENERIC PU COATED MB 020021033','A1170',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2476,'LONGRICH',42,'UA',5,'100','WHITE','AR-216','MLR0262023122101','WHITE','ACTION PU COATED LEATHER','A244',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2477,'LONGRICH',42,'UA',5,'001','BLACK','AR-216','MLR0262023122102','BLACK','ACTION PU COATED LEATHER','A245',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2478,'GLOSTAR',11,'ADIDAS',3,'AE6S','WONDER WHITE','DE-7','MGS0072023122601','WHITE','SOFT PU COATED','A783','2024-02-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2479,'NIKOMAS IY',18,'NIKE',1,'44B','MIDNIGHT NAVY','DE-7 SM','TMNS0202023122801','4MD','GENERIC PU COATED (MB020021032)','A1171','2024-02-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2480,'SCI',32,'NIKE',1,'33X','VINTAGE GREEN','AR-144','MSC0062023122601','33R','VIRGIN HYDRO PU LEATHER','A1172','2023-03-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2481,'CHINGLUH',5,'NIKE',1,'63D','FIRE PINK','DE-7','MCL0172023122902','WHITE','GENERIC PU COATED','A310','2023-03-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2482,'CHINGLUH',5,'NIKE',1,'44B','MIDNIGHT NAVY','DE-7','MCL0172023122901','BLACK','GENERIC PU COATED','A311','2023-03-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2483,'HWASEUNG',14,'ADIDAS',3,'AFAY','ICE LAVENDER','R-231','MHW0352024010201','01V','SOHO NUBUCK','A784','2023-04-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2484,'HWASEUNG',14,'ADIDAS',3,'AF4Q','PRELOVED SCARLET','R-231','MHW0352024010202','80S','SOHO NUBUCK','A785','2023-04-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2485,'METRO NB',16,'NB',4,'124-91-00 (NB103)','WHITE','DE-90','TSMP0332024010301','WHITE','HYDRO PU COATED LEATHER','M060','2024-04-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2486,'GLOSTAR (ADS)',12,'ADIDAS',3,'AA2R','GREY ONE','DE-7','MGS0072024010301','WHITE','SOFT PU COATED','A786','2024-04-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2487,'GLOSTAR (ADS)',12,'ADIDAS',3,'48F0','MAROON','DE-7','MGS0072024010302','BROWN','SOFT PU COATED','A787','2024-04-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2488,'KMK',15,'NIKE',1,'10J','LT OREWOOD BROWN','AR-120 M','MKM0012024010801','WHITE','VIRGIN HYDRO PU','A209','2024-08-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2489,'KMK',15,'NIKE',1,'3PT','OLIVE AURA','AR-120 M','MKM0012024010802','34A','VIRGIN HYDRO PU','A210','2024-08-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:19',NULL),
(2490,'FENGTAY (WEST)',7,'NIKE',1,'33X','VINTAGE GREEN','AR-144 M','MFT0062024010401','33R','VIRGIN HYDRO PU LEATHER','A283','2024-08-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2491,'ADIS',1,'NIKE',1,'4LX','ARMORY NAVY','DE-73','MAD0022024010901','BLACK','VIRGIN  HYDRO PU','A543','2024-11-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2492,'CHANGSHIN RJ',4,'NIKE',1,'0BA','PLATINUM VIOLET','AR-144','MCS0042024010901','PINK','VIRGIN HYDRO PU LEATHER','A316','2024-11-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2493,'ADIS',1,'NIKE',1,'6GW','BARELY ROSE','AR-20 M','MAD0022024011101','PINK','VIRGIN HYDRO PU LEATHER','A544',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2494,'CHANGSHIN RJ',4,'NIKE',1,'4LX','ARMORY NAVY','R-131 M','MCS0052024011001','BLACK','GENERIC PU COATED','A317',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2495,'LONGRICH',42,'UA',5,'535','SALT PURPLE','AR-216','MLR0262024011603','WHITE','ACTION PU COATED LEATHER','A246',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2496,'LONGRICH',42,'UA',5,'011','MOD GRAY','AR-216','MLR0262024011601','WHITE','ACTION PU COATED LEATHER','A247',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2497,'LONGRICH',42,'UA',5,'525','LAVISH','AR-216','MLR0262024011604','PURPLE','ACTION PU COATED LEATHER','A249',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2498,'NIKOMAS IY',18,'NIKE',1,'4HT','STORM BLUE','UM-34','TMNS0202024011801','4MD','GENERIC PU COATED (MB020021032)','A1173',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2499,'SHOETOWN',28,'NIKE',1,'6DQ','SIREN RED','DE-73','MSL0442024012301','WHITE','PM GENERIC PU COATED','A1174',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2500,'CHANGSHIN RJ',4,'NIKE',1,'40H','LASER BLUE','DE-73','MCS0052024011901','44Z','GENERIC PU COATED','A318',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2501,'DWI PRIMA SENTOSA',45,'UA',5,'001','BLACK','AR-191 M','MDW0012024012301/BLACK UA /UT BLACK','BLACK','ACTION PU COATED LEATHER','A250',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2502,'DWI PRIMA SENTOSA',45,'UA',5,'100','WHITE','AR-191 M','MDW0012024012501','WHITE','ACTION PU COATED LEATHER','A251',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2503,'POUYUEN',24,'NIKE',1,'64M','VARSITY RED','CPUG','TMPY0282024012901','RED','LT PATENT LEATHER','A1175',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2504,'BIG',2,'ADIDAS',3,'AEJT','BLISS PINK','DE-7','MBI0202024012901','PINK','SOFT PU COATED','A788',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2505,'ADIS',1,'NIKE',1,'74F','WHEAT','UM-14 SG','TMAD0022025071101','2CT','VIRGIN PU','A575',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20','2026-05-19 03:12:24'),
(2506,'CHINGLUH',5,'NIKE',1,'37B','OXIDIZED GREEN','AR-107','MVC0052024011901','YELLOW','GENERIC PU COATED','A312',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2507,'PCN G8',59,'NIKE',1,'47N','UNIVERSITY BLUE','ESR-180SK2/CPUG','SPG0212024013001','LIGHT BLUE','GENERIC PU COATED','A1176','2024-02-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2508,'LONGRICH',42,'UA',5,'014','HALO GRAY','AR-194','MLR0262024013001','WHITE','ACTION PU COATED LEATHER','A252','2024-02-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2509,'BIG',2,'ADIDAS',3,'AF42','IVORY','AR-140','MBI0202024013101','WHITE','SOFT PU COATED','A789','2024-02-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2510,'CHANGSHIN RJ',4,'NIKE',1,'46B','ASTRONOMY BLUE','R-8','MCS0052024020101','44Z','GENERIC PU COATED','A319','2024-02-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2511,'CHINGLUH',5,'NIKE',1,'01E','NEUTRAL GREY','AR-107','MCL0172024012901','GREY','GENERIC PU COATED','A313','2024-06-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2512,'BIG',2,'ADIDAS',3,'AF4P','CHARCOAL','AR-169','MBI0202024012902','BLACK','SOFT PU COATED','A790','2024-06-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2513,'PRATAMA',25,'NIKE',1,'74F','WHEAT','AR-20','MPT0122024020701','2CT','GENERIC PU COATED','A483','2024-12-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2514,'SCI',32,'NIKE',1,'33W','LIGHT ARMY','AR-167','MSC0062024012601','3MR','GENERIC PU COATED','A1177','2024-12-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2515,'LONGRICH',42,'UA',5,'100','WHITE LEATHER','AR-194','MLR0262024020601','WHITE','NAPA NATURAL LEATHER','A253',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2516,'LONGRICH',42,'UA',5,'075','BASEBALL GRAY','AR-194','MLR0262024020602','WHITE','NAPA NATURAL LEATHER','A254',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2517,'LONGRICH',42,'UA',5,'290','DESERT SAND','AR-194','FOLLOW CSI UA','01V','NAPA NATURAL LEATHER','A255',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2518,'LONGRICH',42,'UA',5,'390','MARINE OD GREEN','AR-194','FOLLOW CSI UA','3MR','NAPA NATURAL LEATHER','A256',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2519,'ADIS',1,'NIKE',1,'0BA','PLATINUM VIOLET','UM-34','MAD0022024020601','WHITE','VIRGIN HYDRO PU LEATHER','A546',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2520,'VICTORY',31,'NIKE',1,'5CA','IRIS WHISPER','DE-7 SM','MVC0052024020701','WHITE','GENERIC PU COATED','A314',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2521,'GLOSTAR',11,'ADIDAS',3,'AF45','PUTTY GREY','DE-7','MGS0072024021501','01V','SOFT PU COATED','A791',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2522,'CHANGSHIN RJ',4,'NIKE',1,'45B','OBSIDIAN','R-231','MAD0022024021301','BLACK','GENERIC PU COATED','A320',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2523,'CHANGSHIN',3,'NIKE',1,'33X','VINTAGE GREEN','AR-144','MCS0042024021501','33R','VIRGIN HYDRO PU LEATHER','A321',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2524,'LONGRICH',42,'UA',5,'114','WHITE QUARTZ','AR-175','FOLLOW CSI UA','WHITE','ECO GREEN LEATHER','A257',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2525,'NIKOMAS',17,'ADIDAS',3,'AETL','SEMI LUCID FUCHSIA','R-8','TMNS0162024082302','6DX','SEMI FULL GRAIN','A817',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20','2026-05-19 03:12:22'),
(2526,'NIKOMAS',17,'ADIDAS',3,'003A','YELLOW','R-8','FMCA PCI','YELLOW','SEMI FULL GRAIN','A793',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2527,'LONGRICH',42,'UA',5,'001','BLACK','AR-194','MLR0262024022101','BLACK','NAPPA NATURAL LEATHER','A258',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2528,'CHINGLUH',5,'NIKE',1,'4NP','HYPER ROYAL','AR-64','MCL0172024022201','44Z','VIRGIN HYDRO PU','A315',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2529,'NIKOMAS IY',18,'NIKE',1,'47N','UNIVERSITY BLUE','CPUG','SPG0212024022601','44Z','LS PATENT LEATHER','A1178',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2530,'NIKOMAS IY',18,'NIKE',1,'88N','MAGIC EMBER FLUORESCENT','R-131 M','TSNS0202024022801','80S','VIRGIN HYDRO PU MB020021365','A1179',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2531,'POUYUEN',24,'NIKE',1,'4EV','GAME ROYAL','CPUG','TSPY0282024030501','44Z','LS PATENT LEATHER','A1180','2024-06-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2532,'POUYUEN',24,'NIKE',1,'47N','UNIVERSITY BLUE','CPUG','TSPY0282024030502','LIGHT BLUE','LS PATENT LEATHER','A1181','2024-06-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2533,'KMK',15,'NIKE',1,'4NT','LECHE BLUE','AR-120 M','MKM0012024030501','LIGHT BLUE','VIRGIN HYDRO PU','A211','2024-06-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2534,'KMK',15,'NIKE',1,'00J','SEAFOAM','AR-120 M','MKM0012024030502','34A','VIRGIN HYDRO PU','A212','2024-06-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2535,'SHOETOWN CINA',61,'NIKE',1,'6HV','ACTIVE PINK','DE-73','SSL0442024022801','WHITE','GENERIC PU COATED','A1182','2024-06-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2536,'SHOETOWN CINA',61,'NIKE',1,'65N','UNIVERSITY RED FLUORESCENT','DE-73','SSL0442024022803','WHITE','GENERIC PU COATED','A1183','2024-06-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2537,'SHOETOWN CINA',61,'NIKE',1,'3PS','DUSTY OLIVE','DE-73','SSL0442024022802','WHITE','GENERIC PU COATED','A1184','2024-07-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2538,'NIKOMAS',17,'ADIDAS',3,'AFDL','WARM SANDSTONE','DE-7','SCOTDIC','2CT','SOFT PU COATED LEATHER','A794','2024-08-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2539,'CHANGSHIN',3,'NIKE',1,'0AE','VAST GREY','R-102','MCS0052024031301','WHITE','ECO TECH COMFORT','A322',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2540,'PARKLAND 2',21,'NB',4,'032-49-15','GREAT PLAINS COLORO','DE-135','FOLLOW COLORO','2CT','HYDRO PU COATED LEATHER','A512',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:20',NULL),
(2541,'PARKLAND 2',21,'NB',4,'032-64-10','INCESE COLORO','DE-135','FOLLOW COLORO','2CT','HYDRO PU COATED LEATHER','A513',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2542,'PARKLAND 2',21,'NB',4,'098-26-13','DEEP OCEAN COLORO','DE-135','FOLLOW COLORO','33R','HYDRO PU COATED LEATHER','A514',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2543,'PARKLAND 2',21,'NB',4,'121-28-31','TEAM ROYAL COLORO','DE-135','FOLLOW COLORO','44Z','HYDRO PU COATED LEATHER','A515',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2544,'PARKLAND 2',21,'NB',4,'121-34-10','VINTAGE INDIGO COLORO','DE-135','FOLLOW COLORO','4MD','HYDRO PU COATED LEATHER','A516',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2545,'GLOSTAR (ADS)',12,'ADIDAS',3,'AESW','SILVER PEBBLE','DE-7','FMCA PCI','3MR','SOFT PU COATED LEATHER','A795',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2546,'GLOSTAR (ADS)',12,'ADIDAS',3,'A0TO','CLAY','DE-7','MGS0072024031801','3MR','SOFT PU COATED LEATHER','A796',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2547,'VICTORY',31,'NIKE',1,'0AP','PLATINUM TINT','AR-169','MVC0052024031501','WHITE','VIRGIN HYDRO PU','A316',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2548,'LONGRICH',42,'UA',5,'016','ANTHRACITE','AR-216','MLR0262024032101','BLACK','ACTION PU COATED LEATHER','A259',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2549,'LONGRICH',42,'UA',5,'600','RED','AR-216','MLR0262024032102','RED','ACTION PU COATED LEATHER','A260',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2550,'LONGRICH',42,'UA',5,'389','HYPER GREEN','AR-216','MLR0262024032201','34A','ACTION PU COATED LEATHER','A261',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2551,'PRATAMA',25,'NIKE',1,'6JD','LASER FUCHIA FLUORESCENT','R-8 M','MPT0122024032701','PINK','GENERIC PU COATED','A484',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2552,'PRATAMA',25,'NIKE',1,'63E','MED SOFT PINK','R-8','MPT0122024032702','WHITE','GENERIC PU COATED','A485',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2553,'PRATAMA',25,'NIKE',1,'6CV','HYPER PINK FLUORESCENT','R-8','MPT0122024032703','WHITE','GENERIC PU COATED','A486',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2554,'PRATAMA',25,'NIKE',1,'66I','REDWOOD','R-8','MPT0122024032704','RED','GENERIC PU COATED','A487',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2555,'PRATAMA',25,'NIKE',1,'4NB','ROYAL PULSE','R-8','MPT0122024032705','44Z','GENERIC PU COATED','A488',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2556,'PCN G8',59,'NIKE',1,'6EK','DIGITAL PINK','R-131','MPG0212024040101','RED','VIRGIN HYDRO PU LEATHER','A1185','2024-02-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2557,'ADIS',1,'NIKE',1,'51J','DARK RAISIN','DE-73','MAD0022024032801','BLACK','VIRGIN HYDRO PU LEATHER','A547','2024-02-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2558,'ADIS',1,'NIKE',1,'01B','METALLIC SILVER','AR-169','MAD0022024032802','WHITE','VIRGIN HYDRO PU LEATHER','A548','2024-02-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2559,'ADIS',1,'NIKE',1,'01B','METALLIC SILVER','AR-107 DM','MAD0022024032803','WHITE','VIRGIN HYDRO PU LEATHER','A549','2024-02-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2560,'LONGRICH',42,'UA',5,'721','SUNSPARK','AR-216','FOLLOW CSI UA','YELLOW','ACTION PU COATED LEATHER','A262','2024-02-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2561,'LONGRICH',42,'UA',5,'825','BLAZE ORANGE FLUORESCENT','AR-216','FOLLOW CSI UA','80S','ACTION PU COATED LEATHER','A263','2024-02-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2562,'POUYUEN',24,'NIKE',1,'05Q','FOOTBALL GREY','ESR-180SK2/CPUG','SPY0282024032701 CMP','WHITE','GENERIC PU COATED','A1186','2024-02-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2563,'LONGRICH',42,'UA',5,'914','SKY BLUE','AR-163','FOLLOW CSI UA','LT BLUE','ACTION PU COATED LEATHER','A264','2024-03-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2564,'ADIS',1,'NIKE',1,'10J','LT OREWOOD BROWN','AR-107 DM','MAD0022024040401','WHITE','VIRGIN HYDRO PU LEATHER','A550','2024-05-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2565,'ADIS',1,'NIKE',1,'10J','LT OREWOOD BROWN','AR-169','MAD0022024040402','WHITE','VIRGIN HYDRO PU LEATHER','A551','2024-05-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2566,'VICTORY',31,'NIKE',1,'4NP','HYPER ROYAL FLUORESCENT','DE-7 SM','MCL0172024040201','44Z','GENERIC PU COATED','A317','2024-05-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2567,'FENGTAY',7,'NIKE',1,'4KY','THUNDER BLUE','UM-14 G','MFT0062024040401','BLACK','VIRGIN HYDRO PU','A285','2024-05-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2568,'FENGTAY',7,'NIKE',1,'4KY','THUNDER BLUE','AR-169','MFT0062024040402','BLACK','VIRGIN HYDRO PU','A286','2024-05-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2569,'BIG',2,'ADIDAS',3,'AD8R','TEAM ROYAL BLUE','DE-7','MBI0202024040301','44Z','PU COATED LEATHER (MAP-ACTION LEATHER)','A797',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2570,'BIG',2,'ADIDAS',3,'AAYC','CLOUD WHITE','DE-7','MBI0202024040302','WHITE','SOFT PU COATED LEATHER (MAP-SOFT PU)','A798',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2571,'BIG',2,'ADIDAS',3,'043A','DARK BLUE','DE-7','MBI0202024040303','BLACK','SOFT PU COATED LEATHER (MAP-SOFT PU)','A799',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2572,'LONGRICH',42,'UA',5,'016','ANTHRACITE','AR-163/DE-145','MLR0262024040401','BLACK','ACTION PU COATED LEATHER','A265',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2573,'LONGRICH',42,'UA',5,'001','BLACK','AR-163','MLR0262024040402','BLACK','ACTION PU COATED LEATHER','A266',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2574,'LONGRICH',42,'UA',5,'790','TAXI','AR-163','MLR0262024040403','YELLOW','ACTION PU COATED LEATHER','A267',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2575,'LONGRICH',42,'UA',5,'304','MORPH GREEN','AR-163','MLR0262024040404','71R','ACTION PU COATED LEATHER','A268',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2576,'LONGRICH',42,'UA',5,'011','MOD GREY','AR-163','MLR0262024040405','01V','ACTION PU COATED LEATHER','A269',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2577,'LONGRICH',42,'UA',5,'100','WHITE','AR-163','MLR0262024040406','WHITE','ACTION PU COATED LEATHER','A270',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2578,'VICTORY',31,'NIKE',1,'4EV','GAME ROYAL','R-53','MVC0052024040501','BLACK','GENERIC PU COATED','A318',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2579,'TAEKWANG',30,'NIKE',1,'3HR','CARGO KHAKI','AR-206 M','TMTK0272024041601','BLACK','VIRGIN HYDRO PU','A142',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2580,'TAEKWANG',30,'NIKE',1,'0AH','DK SMOKE GREY','AR-181 M','TMTK0272024041602','BLACK','VIRGIN HYDRO PU','A143',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2581,'TAEKWANG',30,'NIKE',1,'0AJ','SMOKE GREY','AR-206 M','TMTK0272024041603','BLACK','VIRGIN HYDRO PU','A144',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2582,'TAEKWANG',30,'NIKE',1,'4KY','THUNDER BLUE','AR-206 M','TMTK0272024041604','BLACK','VIRGIN HYDRO OU','A145',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2583,'CHANGSHIN',3,'NIKE',1,'20I','HEMP','AR-144','MCS0042024041801','2CT','VIRGIN HYDRO PU LEATHER','A323',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2584,'PCN G8',59,'NIKE',1,'43G','GLACIER BLUE','R-8 M','TMPG0212024041801','4AU','GENERIC PU COATED','A1187',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2585,'TAEKWANG',30,'NIKE',1,'04F','LIGHT PUMICE','AR-181 M','TMTK0272024041901','GREY','GENERIC PU COATED','A146',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2586,'ADIS',1,'NIKE',1,'4KY','THUNDER BLUE','R-102','TMAD0022024041801','BLACK','GENERIC PU COATED LEATHER','A552',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2587,'ADIS',1,'NIKE',1,'04B','CEMENT GREY','R-102','TMAD0022024041802','GREY','GENERIC PU COATED LEATHER','A553',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2588,'ADIS',1,'NIKE',1,'20I','HEMP','R-102','TMAD0022024041803','2CT','GENERIC PU COATED LEATHER','A554',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2589,'ADIS',1,'NIKE',1,'20I','HEMP','DE-73','TMAD0022024041901','2CT','GENERIC PU COATED','A555',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2590,'ADIS',1,'NIKE',1,'6HN','BURGUNDY ASH','R-102','TMAD0022024041902','BROWN','GENERIC PU COATED LEATHER','A556',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2591,'PRATAMA',25,'NIKE',1,'04B','CEMENT GREY','R-8','TMPT0122024042301','GREY','GENERIC PU COATED','A489',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2592,'PRATAMA JX',25,'NIKE',1,'3MG','DEEP JUNGLE','R-8','TMPT0122024042302','BLACK','GENERIC PU COATED','A490',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2593,'NIKOMAS IY',18,'NIKE',1,'43G','GLACIER BLUE','DE-125 SM','TMNS0202024042301','4AU','GENERIC PU COATED','A1189',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2594,'CHINGLUH',5,'NIKE',1,'63I','BORDEAUX','DE-73','TMCL0172024042301','PURPLE','GENERIC PU COATED','A319',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2595,'BIG',2,'ADIDAS',3,'AD8R','TEAM ROYAL BLUE','DE-7','TMBI0202024042201','44Z','SOFT PU COATED LEATHER','A800',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2596,'YMUV',39,'UA',5,'652','REBEL PINK','AR-216','FOLLOW CSI UA','6DX','ACTION PU COATED LEATHER','A271',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2597,'YMUV',39,'UA',5,'566','OCTANE','AR-216','FOLLOW CSI UA','PINK','ACTION PU COATED LEATHER','A272',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2598,'YMUV',39,'UA',5,'453','BLUE CALM','AR-216','FOLLOW CSI UA','LT BLUE','ACTION PU COATED LEATHER','A273',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2599,'YMUV',39,'UA',5,'402','BLUE ATLANTIS','AR-216','FOLLOW CSI UA','44Z','ACTION PU COATED LEATHER','A274',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2600,'METRO NB',16,'NB',4,'124-23-11','NEW NAVY','AR-100','TMMP0332024042502','BLACK','HYDRO PU COATED LEATHER','M062',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2601,'METRO NB',16,'NB',4,'072-45-06','DARK JUNIPER','AR-140','TMMP0332024042504','33R','HYDRO PU COATED LEATHER','M064',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2602,'CHANGSHIN',4,'NIKE',1,'06F','ANTHRACITE','AR-138','TMCS0052024042601','BLACK','VIRGIN HYDRO PU LEATHER','A324',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2603,'NIKOMAS IY',18,'NIKE',1,'6EK','DIGITAL PINK','R-131 M','TMNS0202024042401','RED','VIRGIN HYDRO PU MB020021809','A1190',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2604,'CHINGLUH',5,'NIKE',1,'05Q','FOOTBALL GREY','DE-73','TMCL0172024041901','WHITE','GENERIC COATED','A320',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2605,'CHINGLUH',5,'NIKE',1,'4EV','GAME ROYAL','R-53','TMCL0172024042401','44Z','GENERIC PU COATED','A321',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2606,'YMUV',39,'UA',5,'500','PURPLE','AR-216','FOLLOW CSI UA','58U','GENERIC PU COATED','A275','2024-01-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2607,'POUYUEN',24,'NIKE',1,'4EV','GAME ROYAL','R-53','TMPY0282024043001','BLACK','GENERIC PU COATED','A1191','2024-02-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2608,'FENGTAY',9,'NIKE',1,'04Z','PURE PLATINUM','AR-121 SG','TMFT0082024043001','WHITE','VIRGIN HYDRO PU LEATHER','A287','2024-02-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2609,'VICTORY',31,'NIKE',1,'3NV','JADE HORIZON','AR-169 M','TMVC0052024043001','WHITE','VIRGIN HYDRO PU','A322','2024-02-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2610,'VICTORY',31,'NIKE',1,'3NV','JADE HORIZON','AR-20 M','TMVC0052024043002','WHITE','GENERIC PU COATED','A323','2024-02-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2611,'CHINGLUH',5,'NIKE',1,'2HB','LEGEND LT BROWN','DE-73 SM','TMCL0172024043001','WHITE','GENERIC PU COATED','A324','2024-02-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2612,'POUYUEN',24,'NIKE',1,'2DH','MEDIUM OLIVE','R-53 SM','TMPY0282024050201','BLACK','GENERIC PU COATED','A1192','2024-05-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2613,'POUYUEN',24,'NIKE',1,'0AI','IRON GREY','R-53 SM','TMPY0282024050202','BLACK','GENERIC PU COATED','A1193','2024-05-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2614,'SAI',37,'NB',4,'154-63-12','PINK TAFFY COLORO','AR-100','FOLLOW COLORO','PINK','HYDRO PU COATED LEATHER','A517','2024-08-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2615,'CHANGSHIN RJ',4,'NIKE',1,'51J','DARK RAISIN','R-102','TMCS0052024050601','PURPLE','ECO TECH COMFORT','A325','2024-08-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2616,'CHANGSHIN RJ',4,'NIKE',1,'51J','DARK RAISIN','AR-138 M','TMCS0052024050602','PURPLE','VIRGIN HYDRO PU LEATHER','A326','2024-08-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2617,'LONGRICH',41,'UA',5,'10162C','METALLIC GOLD','AR-163','TMLR0262024042901','2CT','ACTION PU COATED LEATHER','A276','2024-10-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2618,'SCI',32,'NIKE',1,'3NV','JADE HORIZON','AR-167 DM','TMSC0062024050601','34A','GENERIC PU COATED','A1194','2024-10-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2619,'GLOSTAR (ADS)',11,'ADIDAS',3,'080A','SILVER METALLIC','DE-7','TMGS0072024051001','WHITE','SOFT PU COATED','A801',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2620,'SMJ',36,'NIKE',1,'74F','WHEAT','AR-20 M','MPT0142024022001','2CT','GENERIC PU COATED','A1195',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2621,'VICTORY',31,'NIKE',1,'6CT','SPIRIT PINK','R-53','TMVC0052024051401','PINK','GENERIC PU COATED','A325',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2622,'NIKOMAS IY',18,'NIKE',1,'08B','DARK BLUE GREY','R-8 M','TSNS0202024051401','BLACK','GENERIC PU COATED','A1196',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2623,'NIKOMAS',17,'ADIDAS',3,'AFAF','AURORA INK','DE-7','SCOTDIC','BLACK','SOFT PU COATED LEATHER (MAP-SOFT-PU)','A802',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2624,'NIKOMAS',17,'ADIDAS',3,'AETA','SEMI COURT GREEN','DE-7','SCOTDIC','3GU','SOFT PU CAOTED LEATHER (MAD-SOFT-PU)','A803',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2625,'NIKOMAS',17,'ADIDAS',3,'AFAL','PRELOVED PURPLE','DE-7','SCOTDIC','PINK','SOFT PU COATED','A804',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2626,'NIKOMAS',17,'ADIDAS',3,'AEXY','SEMI FLASH AQUA','DE-7','SCOTDIC','4AU','SOFT PU COATED','A805',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2627,'PCN G8',59,'NIKE',1,'6DA','LT CRIMSON FLUORESCENT','DE-7 SM','TMPG0212024051601','RED','GENERIC PU COATED','A1197',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2628,'NIKOMAS IY',18,'NIKE',1,'01B','METALLIC SILVER','UM-34','TSNS0202024051601','WHITE','GENERIC PU COATED','A1198',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2629,'ADIS',1,'NIKE',1,'79C','LEMON DROP','R-102','TMAD0022024052001','WHITE','GENERIC PU COATED LEATHER','A557',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2630,'ADIS',1,'NIKE',1,'2FQ','TERRA BLUSH','R-102','TMAD0022024052002','80S','GENERIC PU COATED LEATHER','A558',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2631,'ADIS',1,'NIKE',1,'22Z','BAROQUE BROWN','R-102','TMAD0022024052003','BROWN','GENERIC PU COATED LEATHER','A559',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2632,'SCI',32,'NIKE',1,'6LF','FIERCE PINK FLUORESCENT','AR-144','TMSC0062024052001','6DX','VIRGIN HYDRO PU LEATHER','A1199',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2633,'FENGTAY',7,'NIKE',1,'6LF','FIERCE PINK FLUORESCENT','AR-144','TMFT0062024051701','6DX','VIRGIN HYDRO PU LEATHER','A288',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2634,'NIKOMAS IY',18,'NIKE',1,'11M','COCONUT MILK','R-8 M','TMNS0202024051701','WHITE','VIRGIN HYDRO PU MB020020876','A1200',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2635,'GLOSTAR',11,'ADIDAS',3,'076A','CORE WHITE','DE-7','TMGS0072024052701','WHITE','SOFT PU COATED','A806',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2636,'GLOSTAR',11,'ADIDAS',3,'AFA7','UTILITY YELLOW','DE-7','TMGS0072024053101','YELLOW','SOFT PU COATED','A807','2024-03-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2637,'NIKOMAS IY',18,'NIKE',1,'6DL','GYM RED','DE-45 G','TMNS0202024053101','RED','SEMI FULL GRAIN','A1201',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2638,'FENGTAY TW',58,'NIKE',1,'0AM','SPRUCE AURA','R-8 M','TMFT0382024060301','WHITE','GENERIC PU COATED','A289','2024-05-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2639,'FENGTAY (WEST)',7,'NIKE',1,'6HN','BURGUNDY ASH','AR-144','TMFT0062024053101','BROWN','VIRGIN HYDRO PU LEATHER','A290','2024-05-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2640,'LONGRICH',41,'UA',5,'014','HALO GRAY','AR-163','TMLR0262024060301','WHITE','ACTION PU COATED LEATHER','A277','2024-06-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2641,'LONGRICH',41,'UA',5,'014','HALO GRAY','AR-216','TMLR0262024060303','WHITE','ACTION PU COATED LEATHER','A278','2024-06-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2642,'FENGTAY TW',58,'NIKE',1,'6GV','PARTICLE ROSE','R-8 M','TMFT0382024060401','GREY','GENERIC PU COATED','A291','2024-06-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2643,'METRO NB',16,'NB',4,'124-91-00 (NB103)','WHITE','AR-140','TMMP0332024053004','WHITE','HYDRO PU COATED LEATHER','M068','2024-07-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2644,'LONGRICH UA',41,'UA',5,'044','DOWNPOUR GRAY','AR-216','TMLR0262024060302','BLACK','ACTION PU COATED LEATHER','A279',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2645,'LONGRICH UA',41,'UA',5,'721','SUNSPARK','AR-216','TMLR0262024060305','YELLOW','ACTION PU COATED LEATHER','A280','2024-06-18','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2646,'PCN G8',59,'NIKE',1,'6JU','MAGIC FLAMINGO','R-8 M','TMPG0212024061801','PINK','VIRGIN PU','A1202',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2647,'LONGRICH UA',41,'UA',5,'825','BLAZE ORANGE FLUORESCENT','AR-216','TMLR0262024060304','80S','ACTION PU COATED LEATHER','A281',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2648,'CHINGLUH',31,'NIKE',1,'11M','COCONUT MILK','DE-7 SM','TMVC0052024062101','WHITE','GENERIC PU COATED','A326',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2649,'VICTORY',31,'NIKE',1,'0AV','OFF NOIR','DE-7 SM','TMVC0052024061901','BLACK','GENERIC PU COATED','A327',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2650,'SHOETOWN CINA',61,'NIKE',1,'04Z','PURE PLATINUM','R-53','TMSL0442024062401','WHITE','GENERIC PU COATED LEATHER','A1203',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2651,'CHINGLUH',5,'NIKE',1,'30R','PINE GREEN','AR-20 M','TMCL0172024062101','33R','GENERIC PU COATED','A328',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2652,'ADIS',1,'NIKE',1,'43Z','ALUMUNIUM','AR-196','TMAD0022024062501','44Z','GENERIC PU COATED','A560',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2653,'GLOSTAR (ADS)',11,'ADIDAS',3,'AFDL','WARM SANDSTONE','DE-7','TMGS0072024062401','2CT','SOFT PU COATED','A808',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2654,'TAEKWANG',30,'NIKE',1,'01X','PHANTOM','DE-7 SM','TMTK0272024062501','WHITE','GENERIC PU COATED','A147',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2655,'LONGRICH UA',41,'UA',5,'389','HYPER GREEN','AR-163 M','TMLR0262024061901','34A','ACTION PU COATED LEATHER (FLUORESCENCE)','A282',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2656,'POUYUEN',24,'NIKE',1,'06B','COOL GREY','ESR-180SK2/CPUG','TSPY0282024062601 CMP','GREY','GENERIC PU COATED','A1204',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2657,'POUYUEN',24,'NIKE',1,'6JB','PINK FOAM','ESR-180SK2/CPUG','TSPY0282024062602 CMP','PINK','GENERIC PU COATED','A1205',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2658,'POUYUEN',24,'NIKE',1,'64M','VARSITY RED','ESR-180SK2/CPUG','TSPY0282024062603 CMP','RED','GENERIC PU COATED','A1206',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2659,'ADIS',1,'NIKE',1,'55V','ANTOMIC VIOLET','AR-20 M','TMAD0022024062801','WHITE','VIRGIN HYDRO PU LEATHER','A561','2024-02-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2660,'METRO NB',16,'NB',4,'032-76-04','TIMBERWOLF COLORO','DE-90','TMMP0332024062801','WHITE','HYDRO PU COATED LEATHER','M069','2024-02-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2661,'DWI PRIMA SENTOSA',45,'UA',5,'016','ANTHRACITE','AR-191 M','FOLLOW CSI UA','BLACK','VIR SOFT ACTION','A283','2024-03-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2662,'CHANGSHIN RJ',4,'NIKE',1,'61D','ECHO PINK','R-102','TMCS0052024070201','PINK','ECO TECH COMFORT','A327','2024-04-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2663,'POUYUEN',24,'NIKE',1,'0AV','OFF NOIR','DE-7','TMPY0282024070101','BLACK','GENERIC PU COATED','A1207','2024-04-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2664,'CHINGLUH',31,'NIKE',1,'0AV','OFF NOIR','DE-7 SM','TMVC0052024070101','BLACK','GENERIC PU COATED','A329','2024-04-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2665,'CHINGLUH',5,'NIKE',1,'6JB','PINK FOAM','DE-73 SM','TMCL0172024070201','PINK','GENERIC PU COATED','A330','2024-04-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2666,'VICTORY',31,'NIKE',1,'79W','TEAM GOLD','AR-20','TMVC0052024070102','YELLOW','GENERIC PU COATED','A331','2024-04-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2667,'VICTORY',31,'NIKE',1,'0AP','PLATINUM TINT','AR-20 M','TMVC0052024062701','WHITE','GENERIC PU COATED','A332','2024-04-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2668,'HWASEUNG',14,'ADIDAS',3,'08S1','OFF WHITE','R-231','TMHW0352024070201','WHITE','SOHO NUBUCK','A809','2024-04-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2669,'HWASEUNG',14,'ADIDAS',3,'AEJT','BLISS PINK','R-231','TMHW0352024070202','PINK','SOHO NUBUCK','A810','2024-04-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2670,'HWASEUNG',14,'ADIDAS',3,'A7LA','FLASH PINK','R-231','TMHW0352024070203','6DX','SOHO NUBUCK','A811','2024-04-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2671,'PCN G8',59,'NIKE',1,'46A','LEGEND BLUE','R-8','TMPG0212024070401','LIGHT BLUE','GENERIC PU COATED','A1208','2024-05-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2672,'SFI',40,'NB',4,'032-76-04','TIMBERWOLF','DE-135','TSPW0202024070401','WHITE','HYDRO PU COATED LEATHER','A518','2024-05-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2673,'SFI',40,'NB',4,'121-34-10','VINTAGE INDIGO','DE-135','TSPW0202024070402','4MD','HYDRO PU COATED LEATHER','A519','2024-05-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2674,'SFI',40,'NB',4,'032-64-10','INCESE','DE-135','TSPW0202024070403','2CT','HYDRO PU COATED LEATHER','A520','2024-05-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2675,'SFI',40,'NB',4,'032-49-15','GREAT PLAINS','DE-135','TSPW0202024070404','2CT','HYDRO PU COATED LEATHER','A521','2024-05-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2676,'LONGRICH UA',41,'UA',5,'514','ANDROMEDA PURPLE','R-184','TMLR0262024070401','6DX','ACTION PU COATED LEATHER','A284','2024-08-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2677,'LONGRICH UA',41,'UA',5,'428','ELECTRIC BLUE','R-184','TMLR0262024070404','4JE','ACTION PU COATED LEATHER','A285','2024-08-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2678,'LONGRICH UA',41,'UA',5,'639','PINK VORTEX','R-184','TMLR0262024070406','PINK','ACTION PU COATED LEATHER','A286','2024-08-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2679,'LONGRICH UA',41,'UA',5,'279','STONE','R-184','TMLR0262024070407','WHITE','ACTION PU COATED LEATHER','A287','2024-08-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2680,'LONGRICH UA',41,'UA',5,'110','SUMMIT WHITE','R-184','TMLR0262024070408','WHITE','ACTION PU COATED LEATHER','A288','2024-08-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21',NULL),
(2681,'CHANGSHIN',4,'NIKE',1,'12G','MTLC SUMMIT WHITE','DE-135 SG','TMCS0052024102801','WHITE','GENERIC PU COATED LEATHER','A354',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:21','2026-05-19 03:12:22'),
(2682,'KMK',15,'NIKE',1,'06F','ANTHRACITE','R-8 M','TMKM0012024070301','BLACK','VIRGIN HYDRO PU','A213','2024-09-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2683,'PRATAMA',25,'NIKE',1,'50Z','VIOTECH FLOURESCENT','R-8','TSPT0122024070801','6DX','GENERIC PU COATED','A491','2024-10-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2684,'LONGRICH UA',41,'UA',5,'410','MIDNIGHT NAVY','R-184','TMLR0262024070405','4MD','ACTION PU COATED LEATHER','A289','2024-10-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2685,'LONGRICH UA',41,'UA',5,'114','WHITE CLAY','AR-216','TMLR0262024070801','WHITE','ACTION PU COATED LEATHER','A290','2024-10-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2686,'HWASEUNG',14,'ADIDAS',3,'AEJS','LINEN GREEN','R-231','TMHW035202407080','WHITE','SOHO NUBUCK','A812','2024-11-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2687,'PCN G8',59,'NIKE',1,'70Z','SOFT YELLOW','R-131','TMPG0212024071001','YELLOW','VIRGIN HYDRO PU LEATHER','A1209','2024-11-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2688,'LONGRICH UA',41,'UA',5,'862','ARES RED','AR-216','TMLR0262024071101','80S','ACTION PU COATED LEATHER (FLUORESCENCE)','A291','2024-12-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2689,'LONGRICH UA',41,'UA',5,'862','ARES RED','R-184','TMLR0262024070402','80S','ACTION PU COATED LEATHER (FLUORESCENCE)','A292','2024-12-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2690,'LONGRICH UA',41,'UA',5,'862','ARES RED','AR-194','TMLR0262024070403','80S','ACTION PU COATED LEATHER (FLUORESCENCE)','A293','2024-12-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2691,'GLOSTAR (ADS)',11,'ADIDAS',3,'AFDF','PURE RUBY','DE-7','TMGS0072024071201','RED','SOFT PU COATED','A813',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2692,'METRO NB',16,'NB',4,'010-35-35','NEW TEAM RED','AR-140','TMMP0332024071502','RED','HYDRO PU COATED LEATHER','M071',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2693,'PANARUB',19,'ADIDAS',3,'08S1','OFF WHITE','DE-7','FMCA PANARUB','WHITE','PU COATED LEATHER (MAP-ACTION LEATHER)','A182',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2694,'HWASEUNG',14,'ADIDAS',3,'ADVZ','CREW ORANGE','R-231','TMHW0352024071801','2CT','SOHO NUBUCK','A814',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2695,'CHANGSHIN RJ',4,'NIKE',1,'01B','METALLIC SILVER','DE-135 SG','TMCS0052024071901','WHITE','GENERIC PU COATED LEATHER','A329',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2696,'NIKOMAS',17,'ADIDAS',3,'088A','SOLAR RED','DE-7','SCOTDIC','RED','SOFT PU COATED LEATHER','A815',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2697,'SHOETOWN',28,'NIKE',1,'44B','MIDNIGHT NAVY','DE-7','TMSL0432024072301','BLACK','GENERIC PU COATED','A1210',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2698,'TAEKWANG',30,'NIKE',1,'2HI','DESERT KHAKI','R-231 M','TMTK0272024072301','WHITE','GENERIC PU COATED','A148',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2699,'POUYUEN',24,'NIKE',1,'64M','VARSITY RED','ESR-180 SK2 SG','TMPY0282024072401 CMP','BLACK','GENERIC PU COATED','A1211',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2700,'CHANGSHIN RJ',4,'NIKE',1,'39Y','GORGE GREEN','AR-77','TMCS0052024072401','33R','GENERIC PU COATED LEATHER','A330',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2701,'CHANGSHIN RJ',4,'NIKE',1,'26U','MEDIUM ASH','DE-135 SG','TMCS0052024072402','BLACK','GENERIC PU COATED LEATHER','A331',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2702,'CHANGSHIN RJ',4,'NIKE',1,'06Q','MTLC COOL GREY','DE-135 SG','TMCS0052024072404','BLACK','GENERIC PU COATED LEATHER','A332',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2703,'POUYUEN',24,'NIKE',1,'6JB','PINK FOAM','DE-73 SM','TMPY0282024072901','PINK','GENERIC PU COATED','A1212',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2704,'POUYUEN',24,'NIKE',1,'6JU','MAGIC FLAMINGO','R-8 M','TMPY0282024072902','PINK','VIRGIN PU','A1213',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2705,'PWI 2',21,'NB',4,'039-90-05','ANGORA COLORO','AR-140','TMPW0102024072601','WHITE','HYDRO PU COATED LEATHER','A522',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2706,'CHANGSHIN RJ',4,'NIKE',1,'2EK','CAVE STONE','DE-135 SG','TMCS0052024072403','LIGHT BROWN','GENERIC PU COATED LEATHER','A333',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2707,'CHANGSHIN RJ',4,'NIKE',1,'0AM','SPRUCE AURA','R-8 M','TMCS0052024072901','WHITE','GENERIC PU COATED LEATHER','A334',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2708,'CHANGSHIN RJ',4,'NIKE',1,'0AM','SPRUCE AURA','DE-90 M','TMCS0052024072902','WHITE','GENERIC PU COATED LEATHER','A335',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2709,'CHANGSHIN RJ',4,'NIKE',1,'0AM','SPRUCE AURA','UM-T SM','TMCS0052024072903','WHITE','GENERIC PU COATED LEATHER','A336',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2710,'PCN G8',59,'NIKE',1,'44B','MIDNIGHT NAVY','ESR-180 SK2 HG','TMPG0212024072901','BLACK','GENERIC PU COATED','A1214',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2711,'SHOETOWN CINA',61,'NIKE',1,'45F','DK POWDER BLUE','DE-73 SM','TMSL0442024072901','4JE','GENERIC PU COATED','A1215',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2712,'SAI',37,'NB',4,'043-89-00','REFLECTION','AR-100 M','FOLLOW COLORO','WHITE','HYDRO PU COATED LEATHER','A523','2024-01-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2713,'SAI',37,'NB',4,'112-82-07','FROSTED GLASS','AR-100 M','TMSD0462024112801','WHITE','HYDRO PU COATED LEATHER','A530','2024-03-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22','2026-05-19 03:12:23'),
(2714,'FENGTAY (WEST)',7,'NIKE',1,'6LF','FIERCE PINK FLUORESCENT','DE-7 SM','TMFT0062024071101','6DX','GENERIC PU COATED','A292','2024-06-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2715,'FENGTAY',7,'NIKE',1,'61D','ECHO PINK','AR-144 M','TMFT0062024073101','PINK','VIRGIN HYDRO PU','A293','2024-06-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2716,'NIKOMAS IY',18,'NIKE',1,'44B','MIDNIGHT NAVY','CPUG','TMNS0202024090601','BLACK','LS PATENT LEATHER MB 020021535','A1219','2024-11-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22','2026-05-19 03:12:22'),
(2717,'NIKOMAS IY',18,'NIKE',1,'3HC','FILAMENT GREEN','UM-34T SM','TSNS0202024080502','4AU','GENERIC PU COATED MB020020496','A1217','2024-09-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2718,'PARKLAND 2',21,'NB',4,'032-76-04','TIMBERWOLF COLORO','DE-135','TMPW0102024080801','WHITE','HYDRO PU COATED LEATHER','A525','2024-09-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2719,'DWI PRIMA SENTOSA',45,'UA',5,'587','JASPER BLUE','DE-73','FOLLOW CSI UA','LIGHT BLUE','ACTION PU COATED LEATHER','A294','2024-12-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2720,'ADIS',1,'NIKE',1,'4PA','BLUE VOID','AR-196 M','TMAD0022024080901','BLACK','GENERIC PU COATED','A562','2024-12-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2721,'LONGRICH UA',41,'UA',5,'914','SKY BLUE','AR-163','TMLR0262024081201','4AU','ACTION PU COATED LEATHER','A295',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2722,'FENGTAY',7,'NIKE',1,'4QM','BLUE BEYOND','AR-144 M','TMFT0062024081201','LIGHT BLUE','VIRGIN HYDRO PU','A294',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2723,'POUYUEN',24,'NIKE',1,'01X','PHANTOM','R-8 M','TMPY0282024081201CMP','WHITE','GENERIC PU COATED','A1218',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2724,'METRO NB',16,'NB',4,'036-90-02','NEW SEA SALT','DE-90','TMMP0332024081501','WHITE','HYDRO PU COATED LEATHER','M072',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2725,'CHANGSHIN RJ',4,'NIKE',1,'0AD','ATMOSPHERE GREY','R-8 M','TMCS0052024081501','GREY','GENERIC PU COATED LEATHER','A337',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2726,'CHANGSHIN RJ',4,'NIKE',1,'4QM','BLUE BEYOND','R-8 M','TMCS0052024081502','BLUE','GENERIC PU COATED LEATHER','A338',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2727,'CHANGSHIN RJ',4,'NIKE',1,'6JD','LASER FUCHIA FLUORESCENT','R-8 M','TMCS0052024081503','PINK','GENERIC PU COATED LEATHER','A339',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2728,'NIKOMAS',17,'ADIDAS',3,'ADAT','ALUMINA','R-8','TMNS0162024082301','WHITE','SEMI FULL GRAIN','A816',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2729,'METRO NB',16,'NB',4,'036-90-02','NEW SEA SALT','R-8','TSMP0332024082301','WHITE','HYDRO PU COATED LEATHER','M073',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2730,'METRO NB',16,'NB',4,'008-24-00','BLACK CEMENT','DE-90 M','TSMP0332024082304','BLACK','HYDRO PU COATED LEATHER','M074',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2731,'METRO NB',16,'NB',4,'121-34-10','NEW VINTAGE INDIGO','R-53 M','TSMP0332024082302','BLACK','HYDRO PU COATED LEATHER','M075',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2732,'METRO NB',16,'NB',4,'005-37-12','WASHED BURGUNDY','R-53 M','TSMP0332024082701','BLACK','HYDRO PU COATED LEATHER','M076',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2733,'GLOSTAR (ADS)',11,'ADIDAS',3,'A172','CYBER MET','DE-7','TMGS0072024082901','2CT','SOFT PU COATED','A818','2024-02-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2734,'TAEKWANG',30,'NIKE',1,'45B','OBSIDIAN','UM-T','TMTK0272024091001','BLACK','VIRGIN HYDRO PU LEATHER','A149',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2735,'PCN G8',59,'NIKE',1,'04D','LIGHT SILVER','R-8 M','TMPG0212024091201','WHITE','GENERIC PU COATED','A1220',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2736,'PCN G8',59,'NIKE',1,'0AM','SPRUCE AURA','R-8','TMPG0212024091202','WHITE','GENERIC PU COATED','A1221',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2737,'BIG',2,'ADIDAS',3,'076A','CORE WHITE','DE-7','TMBI0202024091201','WHITE','SOFT PU COATED LEATHER','A820',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2738,'CHANGSHIN',57,'NIKE',1,'7AX','LT LEMON TWIST','DE-135 SG','TMCS0062024091901','BLACK','GENERIC PU COATED','A340',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2739,'CHANGSHIN',3,'NIKE',1,'45B','OBSIDIAN','AR-176 M','TMCS0042024091801','BLACK','GENERIC PU COATED LEATHER','A341',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2740,'PANARUB',19,'ADIDAS',3,'AF4L','PRELOVED INK','DE-7','SCOTDIC','4MD','GENERIC PU COATED LEATHER','A183',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2741,'PCN G8',59,'NIKE',1,'47N','UNIVERSITY BLUE','ESR-180 SK2','TMPG0212024092401','WHITE','GENERIC PU COATED','A1222',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2742,'METRO NB',16,'NB',4,'091-37-08','NEW SPRUCE','R-8 M','TMMP0332025020601','BLACK','HYDRO PU COATED LEATHER','M087','2025-12-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22','2026-05-19 03:12:23'),
(2743,'FENGTAY (WEST)',7,'NIKE',1,'4PA','BLUE VOID','DE-7','TMFT0062024092401 (CMP)','BLACK','GENERIC PU COATED','A295',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2744,'CHINGLUH',5,'NIKE',1,'44B','MIDNIGHT NAVY','R-53','TMCL0172024091901','BLACK','GENERIC PU COATED','A333',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2745,'CHINGLUH',5,'NIKE',1,'6GM','RUST PINK','R-53','TMCL0172024091902','PINK','GENERIC PU COATED','A334',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2746,'CHANGSHIN RJ',4,'NIKE',1,'45B','OBSIDIAN','AR-138','TMCS0052025020302','BLACK','VIRGIN HYDRO PU LEATHER','A378','2025-05-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22','2026-05-19 03:12:23'),
(2747,'CHANGSHIN RJ',4,'NIKE',1,'45B','OBSIDIAN','R-102','TMCS0052025020301','BLACK','ECO TECH COMFORT','A377','2025-05-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22','2026-05-19 03:12:23'),
(2748,'NIKOMAS',17,'ADIDAS',3,'AETF','EARTH STRATA','DE-7','SCOTDIC','LIGHT BROWN','SOFT PU COATED LEATHER (MAP-SOFT OU)','A821','2024-03-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2749,'NIKOMAS',17,'ADIDAS',3,'AFAY','ICE LAVENDER','DE-7','SCOTDIC','PINK','SOFT PU COATED LEATHER (MAP-SOFT PU)','A822','2024-07-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2750,'NIKOMAS',17,'ADIDAS',3,'AFH3','AURORA PLUM','R-53','SCOTDIC','58U','SOFT PU COATED LEATHER (MAP-SOFT PU)','A823','2024-07-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2751,'PCN G8',59,'NIKE',1,'04D','LIGHT SILVER','AR-144','TMPG0212024100201','WHITE','VIRGIN HYDRO PU LEATHER','A1223','2024-07-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2752,'SCI',32,'NIKE',1,'11H','MUSLIN','AR-167 DM','TMSC0062024100201','2CT','GENERIC PU COATED','A1224','2024-07-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2753,'SCI',32,'NIKE',1,'6JE','WASHED CORAL','AR-167 DM','TMSC0062024100202','PINK','GENERIC PU COATED','A1225','2024-07-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2754,'CHINGLUH',5,'NIKE',1,'01B','METTALIC SILVER','R-53','TMCL0172024100201','WHITE','GENERIC PU COATED','A335','2024-07-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2755,'SFI',40,'NB',4,'039-90-05','ANGORA COLORO','DE-135','TMPW0202024100401','WHITE','HYDRO PU COATED LEATHER','A526','2024-09-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2756,'SFI',40,'NB',4,'036-90-02','SEA SALT COLORO','DE-135','TMPW0202024100301','WHITE','HYDRO PU COATED LEATHER','A527','2024-09-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2757,'SAI',37,'NB',4,'000-55-00','SLATE GREY','AR-100 M','TMSD0472025092901','GREY','HYDRO PU COATED LEATHER','A589',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22','2026-05-19 03:12:25'),
(2758,'SAI',37,'NB',4,'035-73-04','SHIPYARD','AR-100 M','FOLLOW COLORO','WHITE','HYDRO PU COATED LEATHER','A529','2024-09-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2759,'METRO NB',16,'NB',4,'120-76-08','OXFORD BLUE COLORO','DE-90','FOLLOW COLORO','WHITE','HYDRO PU COATED LEATHER','M078','2024-09-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2760,'METRO NB',16,'NB',4,'010-40-13','RED ROCK COLORO','AR-100 M','FOLLOW COLORO','80S','HYDRO PU COATED LEATHER','M079','2024-09-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2761,'METRO NB',16,'NB',4,'102-45-08','SALT WATER COLORO','AR-100 M','FOLLOW COLORO','3AW','HYDRO PU COATED LEATHER','M080','2024-09-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2762,'METRO NB',16,'NB',4,'124-49-17','FAIRWEATHER BLUE COLORO','AR-100 M','FOLLOW COLORO','49D','HYDRO PU COATED LEATHER','M081','2024-09-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2763,'CHANGSHIN RJ',4,'NIKE',1,'4MQ','BLUE FURY','R-8 SG','TMCS0052024100701','4JE','GENERIC PU COATED','A344','2024-09-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2764,'CHANGSHIN RJ',4,'NIKE',1,'3FL','CLEAR JADE II FLUORESCENT','R-8 SG','TMCS0052024100702','3GU','GENERIC PU COATED','A345','2024-09-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2765,'POUYUEN',24,'NIKE',1,'44B','MIDNIGHT NAVY','R-53 SM','TSPY0282024100901','BLACK','GENERIC PU COATED','A1226',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2766,'POUYUEN',24,'NIKE',1,'6GM','RUST PINK','R-53 SM','TSPY0282024100902','PINK','GENERIC PU COATED','A1227',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2767,'POUYUEN',24,'NIKE',1,'5BM','DUSTY AMETHYST','CPUG','TSPY0282024100903','49D','GENERIC PU COATED','A1228',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2768,'POUYUEN',24,'NIKE',1,'4HT','STORM BLUE','CPUG','TSPY0282024100904','BLACK','GENERIC PU COATED','A1229',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2769,'PANARUB',19,'ADIDAS',3,'AFDS','POWDER YELLOW','CPUG','FOLLOW SAMPLE','YELLOW','BABY SOFT PATENT LEATHER','A184',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2770,'POUYUEN',24,'NIKE',1,'6CV','HYPER PINK','DE-73 SM','TMPY0282024101101','PINK','GENERIC PU COATED','A1230',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2771,'POUYUEN',24,'NIKE',1,'4HT','STORM BLUE','R-8 M','TSPY0282024101101','4MD','GENERIC PU COATED','A1231',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2772,'CHANGSHIN RJ',4,'NIKE',1,'4KY','THUNDER BLUE','DE-135 SG','TMCS0052024101101','BLACK','GENERIC PU COATED','A346',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2773,'CHANGSHIN RJ',4,'NIKE',1,'0AJ (Mettalic)','SMOKE GREY','DE-135 SG','TMCS0052024101501','BLACK','GENERIC PU COATED','A347',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2774,'CHANGSHIN RJ',4,'NIKE',1,'0AV','OFF NOIR','R-102','TMCS0052024101502','BLACK','GENERIC PU COATED','A348',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2775,'CHINGLUH',5,'NIKE',1,'6CV','HYPER PINK FLUORESCENT','DE-73 SM','TMCL0172024100401','PINK','GENERIC PU COATED','A336',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2776,'NIKOMAS IY',18,'NIKE',1,'0AL','LT SMOKE GREY','AR-107 M','TSNS0202024101801','WHITE','GENERIC PU COATED MB020022319','A1232',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2777,'SHOETOWN',28,'NIKE',1,'0AV','OFF NOIR','R-53','TMSL0432024101801','BLACK','GENERIC PU COTED LEATHER','A1233',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2778,'LONGRICH UA',41,'UA',5,'538','TRANSPARENT','R-231','FOLLOW SAMPLE','49D','ACTION PU COATED LEATHER','A296',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2779,'DWI PRIMA SENTOSA',45,'UA',5,'035','STEEL','R-231','FOLLOW CSI UA','GREY','SOHO NUBUCK','A297',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2780,'DWI PRIMA SENTOSA',45,'UA',5,'498','WHAM BLUE','R-231','FOLLOW CSI UA','BLUE','SOHO NUBUCK','A298',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2781,'DWI PRIMA SENTOSA',45,'UA',5,'280','SANDSTORM','R-231','FOLLOW CSI UA','WHITE','SOHO NUBUCK','A299',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2782,'DWI PRIMA SENTOSA',45,'UA',5,'520','PURPLE LUXE','R-231','FOLLOW CSI UA','PURPLE','SOHO NUBUCK','A300',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2783,'DWI PRIMA SENTOSA',45,'UA',5,'008','ULTIMATE BLACK','AR-191 M','FOLLOW CSI UA','BLACK','VIR SOFT ACTION LEATHER','A301',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2784,'DWI PRIMA SENTOSA',45,'UA',5,'536','PURPLE CREST','AR-191 M','FOLLOW CSI UA','49D','VIR SOFT ACTION LEATHER','A302',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2785,'NIKOMAS',17,'ADIDAS',3,'AAGD','CHALK PEARL','R-53','SCOTDIC','01V','SOFT PU COATED LEATHER (MAP-SOFT PU)','A824',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2786,'METRO NB',16,'NB',4,'045-36-09','WAKAME COLOR','DE-90 M','TMMP0332025071602','3MR','HYDRO PU COATED LEATHER','M096',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22','2026-05-19 03:12:24'),
(2787,'CHANGSHIN',3,'NIKE',1,'4NP','HYPER ROYAL FLUORESCENT','R-8 M','TMCS0042024102201','44Z','GENERIC PU COATED','A349',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2788,'CHANGSHIN',3,'NIKE',1,'04D','LIGHT SILVER','R-8 M','TMCS0042024102202','WHITE','GENERIC PU COATED','A350',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2789,'CHANGSHIN',3,'NIKE',1,'00M','MTLC PLATINUM','DE-135 SG','TMCS0042024102203','WHITE','GENERIC PU COATED','A351',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2790,'PRATAMA JX 2',27,'NIKE',1,'04D','LIGHT SILVER','R-8 M','TMPT0152024102201','GREY','GENERIC PU COATED','A492',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2791,'PRATAMA JX 2',27,'NIKE',1,'4NP','HYPER ROYAL FLUORESCENT','R-8 M','TMPT0152024102202','44Z','GENERIC PU COATED','A493',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2792,'DWI PRIMA SENTOSA',45,'UA',5,'471','BLUE BLUR','DE-73','FOLLOW CSI UA','4JE','ACTION PU COATED LEATHER','A303',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2793,'DWI PRIMA SENTOSA',45,'UA',5,'391','FADE GREEN','DE-73','FOLLOW CSI UA','71R','ACTION PU COATED LEATHER','A304',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2794,'DWI PRIMA SENTOSA',45,'UA',5,'025','CASTLEROCK','DE-73','TMDW0012024122702','BLACK','ACTION PU COATED LEATHER','A307','2025-06-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22','2026-05-19 03:12:23'),
(2795,'SHOETOWN',28,'NIKE',1,'6CV','HYPER PINK','DE-73 SM','TMSL0432024102401','PINK','GENERIC PU COATED','A1234',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2796,'CHANGSHIN RJ',4,'NIKE',1,'67K','WILD CHERRY FLUORESCENT','R-8 M','TMCS0052024102401','RED','GENERIC PU COATED','A352',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2797,'PANARUB',19,'ADIDAS',3,'AED5','ACID RED','CPUG','FMCA PRB','PINK','BABY SOFT PATENT LEATHER','A185',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2798,'CHANGSHIN RJ',4,'NIKE',1,'05Y','DESERT SAND','R-8 M','TMCS0052024102501','WHITE','GENERIC PU COATED','A353',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2799,'SHOETOWN',28,'NIKE',1,'45F','DK POWDER BLUE','DE-73 SM','TMSL0432024102801','4JE','GENERIC PU COATED','A1236',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2800,'CHANGSHIN',4,'NIKE',1,'7AX','LT LEMON TWIST FLUORESCENT','DE-135 SG','TMCS0052024103001','BLACK','GENERIC PU COATED LEATHER','A355',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2801,'CHANGSHIN',4,'NIKE',1,'40T','MOUNTAIN BLUE','R-8 M','TMCS0052024103002','44Z','GENERIC PU COATED LEATHER','A356',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2802,'CHANGSHIN',4,'NIKE',1,'3KG','TEAL TINT','R-8 M','TMCS0052024103003','LIGHT BLUE','GENERIC PU COATED','A357',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2803,'CHANGSHIN',4,'NIKE',1,'89L','TEAM ORANGE','R-8 M','TMCS0052024103004','RED','GENERIC PU COATED','A358',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2804,'POUYUEN',24,'NIKE',1,'86W','GUAVA ICE','AR-107 M','TMPY0282024103001','WHITE','GENERIC PU COATED LEATHER','A1237',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2805,'PCN G8',59,'NIKE',1,'6DL','GYM RED','CPUG','TSPG0212024110101','BLACK','LS PATENT LEATHER','A1238','2024-05-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2806,'PCN G8',59,'NIKE',1,'4HT','STROMBLUE','CPUG','TSPG0212024110102','BLACK','LS PATENT LEATHER','A1239','2024-05-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2807,'PCN G8',59,'NIKE',1,'4HT','STROMBLUE','R-8 M','TSPG0212024110103','44Z','GENERIC PU COATED','A1240','2024-05-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2808,'PCN G8',59,'NIKE',1,'5BM','DUSTY AMETHYST','CPUG','TSPG0212024112601','49D','LS PATENT LEATHER','A1247','2024-03-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22','2026-05-19 03:12:23'),
(2809,'ADIS',1,'NIKE',1,'6JE','WASHED CORAL','AR-20 M','TMAD0022024103101','PINK','VIRGIN HYDRO PU LEATHER','A563','2024-05-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2810,'ADIS',1,'NIKE',1,'30X','CHLOROPHYL','AR-196 M','TMAD0022024103102','33R','GENERIC PU COATED LEATHER','A564','2024-05-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2811,'ADIS',1,'NIKE',1,'10L','PALE IVORY','AR-20 M','TMAD0022024110401','WHITE','VIRGIN HYDRO PU LEATHER','A565','2024-06-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2812,'TAEKWANG',30,'NIKE',1,'07G','LIGHT  BONE','AR-20','TMTK0272024110401','WHITE','ECO TECH COMFORT','A150','2024-06-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2813,'CHANGSHIN',3,'NIKE',1,'4LD','BLACKENED BLUE','R-102','TMCS0042024110501','BLACK','ECO TECH COMFORT','A359','2024-06-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2814,'CHANGSHIN',3,'NIKE',1,'4LD','BLACKENED BLUE','AR-138 M','TMCS0042024110502','BLACK','VIRGIN HYDRO PU COATED','A360','2024-06-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2815,'WEALTH VAST CO. LTD',61,'NIKE',1,'6CV','HYPER PINK','DE-73 SM','TSSL0442024110501','PINK','GENERIC PU COATED','A1242','2024-06-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2816,'NIKOMAS IY',18,'NIKE',1,'4NP','HYPER ROYAL FLUORESCENT','R-131 M','TSNS0202024110501','44Z','VIRGIN HYDRO PU MB020023491','A1243','2024-06-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2817,'PRATAMA JX 2',27,'NIKE',1,'7AX','LT LEMON TWIST','DE-146 SM','TMPT0152024110501','71R','GENERIC PU COATED','A494','2024-06-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2818,'NIKOMAS IY',18,'NIKE',1,'80K','STARFISH FLUORESCENT','R-8','TSNS0202024110601','80S','GENERIC PU COATED MB020023385','A1244','2024-08-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2819,'CHANGSHIN RJ',4,'NIKE',1,'0AP','PLATINUM TINT','R-8 M','TMCS0052024110601','WHITE','GENERIC PU COATED','A361','2024-08-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2820,'NIKOMAS',17,'ADIDAS',3,'ABZE','TRUE GREEN','CPUG','SCOTDIC','3GU','LS SHIFT PATENT LEATHER','A825','2024-11-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2821,'NIKOMAS',17,'ADIDAS',3,'44B','CLEAR SKY','CPUG','SCOTDIC','LIGHT BLUE','LS SHIFT PATENT LEATHER','A826','2024-11-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2822,'SHOETOWN',28,'NIKE',1,'44B','MIDNIGHT NAVY','R-53','TMSL0432024110701','BLACK','GENERIC PU COATED LEATHER','A1245','2024-11-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2823,'KMK',15,'NIKE',1,'3HR','CARGO KHAKI','R-8 M','TMKM0012024110601','BLACK','VIRGIN HYDRO PU','A214','2024-11-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2824,'KMK',15,'NIKE',1,'33W','LIGHT ARMY','R-8 M','TMKM0012024110602','3MR','VIRGIN HYDRO PU','A215','2024-11-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2825,'FENGTAY (WEST)',7,'NIKE',1,'80Z','SPORT SPICE','AR-144 M','TMFT0062024110801','80S','VIRGIN HYDRO PU','A296','2024-11-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2826,'BIG',2,'ADIDAS',3,'A2JM','CLEAR PINK','DE-7','TMBI0202024111101','PINK','SOFT PU COATED LEATHER','A827',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2827,'NIKOMAS',17,'ADIDAS',3,'A7ZV','FROZEN GREEN','CPUG','SCOTDIC','4AU','LS SHIFT PATENT LEATHER','A828',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2828,'NIKOMAS',17,'ADIDAS',3,'ADFX','TEAM VICTORY RED','AR-100','FOLLOW SAMPLE','RED','COATED LEATHER (MAP-ACTION LEATHER)','A829',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2829,'NIKOMAS',17,'ADIDAS',3,'AA2K','ICEY BLUE','CPUG','SCOTDIC','4AU','LS SHIFT PATENT LEATHER','A830',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2830,'CHANGSHIN INC',57,'NIKE',1,'07P','SOFT PEARL','DE-135 SG','TMCS0062024111801','WHITE','GENERIC PU COATED LEATHER','A362',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2831,'NIKOMAS',17,'ADIDAS',3,'AFH2','AURORA IVY','DE-7','SCOTDIC','4MD','COATED LEATHER (MAP-ACTION LEATHER)','A831','2024-02-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22',NULL),
(2832,'PCN G8',59,'NIKE',1,'64M','VARSITY RED','CPUG','TSPG0212025031201','BLACK','LS PATENT LEATHER','A1260',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:22','2026-05-19 03:12:23'),
(2833,'PRATAMA',25,'NIKE',1,'6DA','LT CRIMSON FLUORESCENT','R-8 M','TSPT0122024120201','RED','GENERIC PU COATED','A495','2024-03-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2834,'METRO NB',16,'NB',4,'036-90-02','NEW SEA SALT COLORO','AR-140 M','TSMP0332026051102','WHITE','HYDRO PU COATED LEATHER','A655','2026-12-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23','2026-05-19 03:12:27'),
(2835,'POUYUEN',24,'NIKE',1,'12J','SUMMIT WHITE','ESR-180 SK2 HG','TMPY0282024120301','WHITE','GENERIC PU COATED','A1248','2024-04-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2836,'POUYUEN',24,'NIKE',1,'6DL','GYM RED','CPUG','TSPY0282025021201','BLACK','LS PATENT LEATHER','A1255',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23','2026-05-19 03:12:23'),
(2837,'CHANGSHIN',3,'NIKE',1,'0AE','VAST GREY','DE-41','TMCS0042024120301','WHITE','GENERIC PU COATED LEATHER','A363','2024-04-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2838,'CHANGSHIN',3,'NIKE',1,'06F','ANTHRACITE','DE-41','TMCS0042024120302','BLACK','GENERIC PU COATED LEATHER','A364','2024-04-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2839,'CHANGSHIN',3,'NIKE',1,'45B','OBSIDIAN','R-102','TMCS0042024120303','BLACK','ECO TECH COMFORT','A365','2024-04-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2840,'CHANGSHIN',3,'NIKE',1,'0AE','VAST GREY','AR-138','TMCS0042024120304','WHITE','VIRGIN HYDRO PU LEATHER','A366','2024-04-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2841,'GLOSTAR',12,'NB',4,'145-17-00','BLACK COLORO','AR-100 M','TSGS0092024120501','BLACK','HYDRO PU COATED LEATHER','A531','2024-09-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2842,'GLOSTAR',12,'NB',4,'000-73-00','BRIGHTON GREY COLORO','AR-100 M','TSGS0092024120502','01V','HYDRO PU COATED LEATHER','A532','2024-09-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2843,'GLOSTAR',12,'NB',4,'149-40-00','CASTLEROCK','AR-100 M','TSGS0092024120503','BLACK','HYDRO PU COATED LEATHER','A533','2024-09-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2844,'GLOSTAR',12,'NB',4,'120-65-07','LIGHT ARCTIC GREY','AR-100 M','TSGS0092024120504','LT BLUE','HYDRO PU COATED LEATHER','A534','2024-09-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2845,'GLOSTAR',12,'NB',4,'8001C','SILVER METALLIC','AR-100 M','TSGS0092024120505','WHITE','HYDRO PU COATED LEATHER','A535','2024-09-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2846,'NIKOMAS',17,'ADIDAS',3,'AE65','CRYSTAL SKY','AR-211 SG','SCOTDIC','WHITE','COATED LEATHER (MAP-ACTION LEATHER)','A832',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2847,'NIKOMAS',17,'ADIDAS',3,'A7EK','STONE KHAKI','DE-7','SCOTDIC','2CT','COATED LEATHER (MAP-ACTION LEATHER)','A833',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2848,'VICTORY',31,'NIKE',1,'5BM','DUSTY AMETHYST','DE-73 SM','TMVC0052024121201','WHITE','GENERIC PU COATED','A337',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2849,'PCN G8',59,'NIKE',1,'52X','LIGHT VIOLET','R-8 SG','TMPG0212024121601','WHITE','GENERIC PU COATED','A1250',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2850,'PCN G8',59,'NIKE',1,'53C','ICED LILAC','R-8 SG','TMPG0212024121602','PINK','GENERIC PU COATED','A1251',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2851,'PRATAMA',25,'NIKE',1,'24E','WHITE ONYX','R-8 M','TSPT0122024121601','WHITE','GENERIC PU COATED','A496',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2852,'CHANGSHIN',4,'NIKE',1,'06B','COOL GREY','DE-135 SG','TMCS0052024120401','GREY','GENERIC PU COATED LEATHER','A367',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2853,'METRO NB',16,'NB',4,'016-22-05','NEW BLACK COFFEE','DE-90 M','TMMP0332025071601','BROWN','HYDRO PU COATED LEATHER','M097',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23','2026-05-19 03:12:24'),
(2854,'METRO NB',16,'NB',4,'118-33-13','DARK SHORELINE BLUE','DE-90 M','FOLLOW COLORO','4MD','HYDRO PU COATED LEATHER','M085',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2855,'GLOSTAR (ADS)',11,'ADIDAS',3,'024A','COLLIGIATE GREEN','DE-7','TMGS0072024121701','3AW','SOFT PU COATED','A834',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2856,'SCI',32,'NIKE',1,'6GC','PARTICLE PINK','AR-167 DM','TMSC0062024122001','PINK','GENERIC PU COATED','A1252',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2857,'CHANGSHIN RJ',4,'NIKE',1,'81J','SAFETY ORANGE FLUORESCENT','R-8 SG','TMCS0052024122401','80S','GENERIC PU COATED','A368',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2858,'CHANGSHIN RJ',4,'NIKE',1,'06F','ANTHRACITE','DE-41','TMCS0052024122402','BLACK','GENERIC PU COATED LEATHER','A369',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2859,'CHANGSHIN RJ',4,'NIKE',1,'0AE','VAST GREY','DE-41','TMCS0052024122403','WHITE','GENERIC PU COATED','A370',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2860,'CHANGSHIN RJ',4,'NIKE',1,'06F','ANTHRACITE','AR-176 M','TMCS0052024122404','BLACK','GENERIC PU COATED LEATHER','A371',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2861,'NIKOMAS',17,'ADIDAS',3,'A7CS','SEMI SOLAR YELLOW','DE-7','SCOTDIC','71R','PU COATED LEATHER','A835','2025-03-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2862,'NIKOMAS',17,'ADIDAS',3,'AE7Y','LUCID ORANGE','DE-7','SCOTDIC','80S','PU COATED LEATHER','A836','2025-03-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2863,'SAI',37,'NB',4,'159-77-06','STONE PINK','AR-100','FOLLOW COLORO','PINK','HYDRO PU COATED LEATHER','A536','2025-03-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2864,'SAI',37,'NB',4,'071-65-06','MOSAIC GREEN','AR-100','FOLLOW COLORO','4AU','HYDRO PU COATED LEATHER','A537','2025-03-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2865,'SAI',37,'NB',4,'017-30-20','RELIC BROWN','AR-100 M','FOLLOW COLORO','RED','HYDRO PU COATED LEATHER','A538','2025-03-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2866,'SAI',37,'NB',4,'020-25-10','PUMPERNICKLE','AR-100','FOLLOW COLORO','BROWN','HYDRO PU COATED LEATHER','A539','2025-03-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2867,'METRO NB',16,'NB',4,'115-66-17','BLUE HAZE','AR-100 M','FOLLOW COLORO','LIGHT BLUE','HYDRO PU COATED LEATHER','M086','2025-06-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2868,'DWI PRIMA SENTOSA',45,'UA',5,'016','ANTHRACITE','DE-73','TMDW0012024122701','BLACK','ACTION PU COATED LEATHER','A306','2025-06-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2869,'DWI PRIMA SENTOSA',45,'UA',5,'110','SUMMIT WHITE','DE-73','TMDW0012024122703','WHITE','ACTION PU COATED LEATHER','A308','2025-06-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2870,'DWI PRIMA SENTOSA',45,'UA',5,'001','BLACK','DE-73','TMDW0012024122704','BLACK','ACTION PU COATED LEATHER','A309','2025-06-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2871,'CHINGLUH',5,'NIKE',1,'30R','PINE GREEN','R-8','TMCL0172024122701','33R','VIRGIN HYDRO PU','A338','2025-06-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2872,'ADIS',1,'NIKE',1,'6GC','PARTICLE PINK','AR-196 M','TMAD0022024122701','PINK','GENERIC PU COATED LEATHER','A566','2025-06-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2873,'VICTORY',31,'NIKE',1,'51L','COURT PURPLE','DE-73 SM','TMVC0052025010601','PURPLE','GENERIC PU COATED','A340','2025-08-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2874,'VICTORY',31,'NIKE',1,'47X','DEEP ROYAL BLUE','DE-73 SM','TMVC0052025010602','44Z','GENERIC PU COATED','A341','2025-08-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2875,'VICTORY',31,'NIKE',1,'3GS','STADIUM GREEN','DE-73 SM','TMVC0052025010603','33R','GENERIC PU COATED','A342','2025-08-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2876,'VICTORY',31,'NIKE',1,'01E','NEUTRAL GREY','DE-73 SM','TMVC0052025010701','WHITE','GENERIC PU COATED','A343','2025-08-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2877,'KMK',15,'NIKE',1,'74F','WHEAT','R-8','TMKM0012025010701','2CT','GENERIC PU COATED','A216','2025-08-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2878,'KMK',15,'NIKE',1,'79V','CLUB GOLD','R-8 M','TMKM0012025010702','2CT','GENERIC PU COATED','A217','2025-08-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2879,'KMK',15,'NIKE',1,'6DY','DARK TEAM RED','AR-144 M','TMKM0012025010703','RED','VIRGIN HYDRO PU','A218','2025-08-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2880,'PRATAMA',25,'NIKE',1,'52J','WILD GRAPE','R-8 M','TSPT0122025010701','BLACK','GENERIC PU COATED','A497','2025-08-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2881,'PRATAMA',25,'NIKE',1,'54A','PERSIAN VIOLET','R-8 M','TSPT0122025010702','44Z','GENERIC PU COATED','A498','2025-08-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2882,'VICTORY/SCI',31,'NIKE',1,'4NP','HYPER ROYAL FLUORESCENT','DE-172','TMVC0052025010604','44Z','VIRGIN HYDRO PU LEATHER','A344','2025-08-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2883,'SAI',37,'NB',4,'154-63-12','PINK TIFFANY COLORO','AR-100 M','TMSD0462025010801','PINK','HYDRO PU COATED LEATHER','A540','2025-09-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2884,'PRATAMA',25,'NIKE',1,'2GY','CACAO WOW','R-8 M','TSPT0122025011001','BROWN','GENERIC PU COATED','A499','2025-11-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2885,'PRATAMA',25,'NIKE',1,'27K','LT BRITISH TAN','R-8 M','TSPT0122025011002','3MR','GENERIC PU COATED','A500','2025-11-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2886,'SAI',37,'NB',4,'138-81-07','TARO','AR-100 M','FOLLOW COLORO','01V','HYDRO  PU COATED LEATHER','A541',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2887,'SAI',37,'NB',4,'157-90-05','PINK SALT','AR-100 M','FOLLOW COLORO','WHITE','HYDRO  PU COATED LEATHER','A542',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2888,'CHANGSHIN RJ',4,'NIKE',1,'63E','MED SOFT PINK','R-8 M','TMCS0052025011401','PINK','GENERIC PU COATED LEATHER','A372',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2889,'FENGTAY (WEST)',7,'NIKE',1,'4RE','DENIM TURQ','AR-144 M','TMFT0062025010201','WHITE','VIRGIN HYDRO PU','A297',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2890,'PRATAMA JX 2',25,'NIKE',1,'63E','MED SOFT PINK','R-8 M','TSPT0122025011601','PINK','GENERIC PU COATED','A501',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2891,'PRATAMA',25,'NIKE',1,'3LU','MINT FOAM','R-8 M','TSPT0122025011602','WHITE','GENERIC PU COATED','A502',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2892,'NIKOMAS',17,'ADIDAS',3,'AFAY','ICE LAVENDER','DE-7','TMNS0162025011601','PURPLE','PU COATED LEATHER','A837',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2893,'CHINGLUH',5,'NIKE',1,'80K','STARFISH FLUORESCENT','DE-73 SM','TMCL0172025011501','2CT','GENERIC PU COATED','A345',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2894,'CHANGSHIN',3,'NIKE',1,'88V','MADDER ROOT','DE-41','TMCS0042025011701','80S','GENERIC PU COATED LEATHER','A373',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2895,'CHANGSHIN',3,'NIKE',1,'88U','LT MADDER ROOT','DE-41','TMCS0042025011702','PINK','GENERIC PU COATED LEATHER','A374',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2896,'PRATAMA',25,'NIKE',1,'3HR','CARGO KHAKI','R-8 M','TSPT0122025012001','33R','GENERIC PU COATED','A503',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2897,'CHANGSHIN RJ',4,'NIKE',1,'4ME','RACER BLUE','DE-135 SG','TMCS0052025011601','44Z','GENERIC PU COATED LEATHER','A375',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2898,'SHOETOWN',28,'NIKE',1,'3DI','OCEAN CUBE','AR-122','TMSL0432025012001','4AU','VIRGIN HYDRO PU LEATHER','A1253',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2899,'BIG',2,'ADIDAS',3,'ADWA','HALO BLUE','CPUG','TMBI0202025012101','WHITE','BABY SOFT PATENT LEATHER','A838',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2900,'POUYUEN',59,'NIKE',1,'02Y','FLAT PEWTER','CPUG','TSPG0212025030301','GREY','LS PATENT LEATHER','A1256','2025-04-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23','2026-05-19 03:12:23'),
(2901,'DWI PRIMA SENTOSA',45,'UA',5,'647','PRIME PINK','AR-191 M','FOLLOW CSI UA','PINK','VIR SOFT ACTION LEATHER','A310','2025-05-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2902,'ADIS',1,'NIKE',1,'6HM','BURGUNDY CRUSH','R-102','TMAD0022025020301','BROWN','ECO TECH COMFORT','A567','2025-05-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2903,'CHINGLUH',5,'NIKE',1,'80K','STARFISH FLUORESCENT','AR-64  M','TMCL0172025020301','80S','HYDRO PU COATED LEATHER','A346','2025-06-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2904,'VICTORY',31,'NIKE',1,'6GC','PARTICLE PINK','R-8 M','TMVC0052025020401','PINK','ECO TECH COMFORT','A347','2025-06-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2905,'FENGTAY',8,'NIKE',1,'06B','COOL GREY','AR-107 DM','TMFT0072025020401','GREY','ECO TECH COMFORT','A298','2025-07-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2906,'CHANGSHIN RJ',4,'NIKE',1,'2EQ','PARTICLE BEIGE','R-8 M','TMCS0052025020701','WHITE','GENERIC PU COATED','A379','2025-10-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2907,'CHANGSHIN RJ',4,'NIKE',1,'2EQ','PARTICLE BEIGE','DE-90 M','TMCS0052025020702','WHITE','GENERIC PU COATED','A380','2025-10-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2908,'CHANGSHIN RJ',4,'NIKE',1,'52J','WILD GRAPE','R-8 SG','TMCS0052025020703','58U','GENERIC PU COATED','A381','2025-10-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2909,'CHANGSHIN RJ',4,'NIKE',1,'0AI','IRON GREY','DE-41','TMCS0052025020704','GREY','GENERIC PU COATED','A382','2025-10-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2910,'CHANGSHIN RJ',57,'NIKE',1,'0AV','OFF NOIR','DE-41','TMCS0062025020601','WHITE','GENERIC PU COATED','A383','2025-10-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2911,'DWI PRIMA SENTOSA',45,'UA',5,'024','TITAN GRAY','DE-73','FOLLOW CSI UA','GREY','ACTION PU COATED LEATHER','A311','2025-02-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2912,'NIKOMAS',17,'ADIDAS',3,'080A','SILVER MET','CPUG','FMCA PCI','WHITE','LS SHIFT PATENT LEATHER','A839','2025-12-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2913,'NIKOMAS',17,'ADIDAS',3,'AETG','BETTER SCARLET','CPUG','FMCA PCI','RED','LS SHIFT PATENT LEATHER','A840','2025-12-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2914,'CHANGSHIN',3,'NIKE',1,'40N','PACIFIC BLUE','UM-34 SM','TMCS0042025021301','BLUE','VIRGIN HYDRO PU LEATHER','A384',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2915,'CHANGSHIN',4,'NIKE',1,'2FF','DESERT ORE','R-8 M','TMCS0052025021301','2CT','GENERIC PU COATED','A385',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2916,'SHYANG HUNG TAH',48,'NB',4,'124-23-11','NB NAVY COLORO','AR-100 M','TSSH0012025021701','BLACK','HYDRO PU COATED LEATHER','A543',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2917,'CHANGSHIN',3,'NIKE',1,'11M','COCONUT MILK','UM-34','TMCS0042025021901','WHITE','VIRGIN HYDRO PU LEATHER','A386',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2918,'CHANGSHIN',3,'NIKE',1,'3KH','MINERAL TEAL','UM-34','TMCS0042025021902','3AW','VIRGIN HYDRO PU LEATHER','A387',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2919,'CHANGSHIN',3,'NIKE',1,'80K','STARFISH FLUORESCENT','UM-34','TMCS0042025021903','80S','VIRGIN HYDRO PU LEATHER','A388',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2920,'SAI',37,'NB',4,'008-26-26','PODIUM RED','AR-100 M','FOLLOW COLORO','RED','HYDRO PU COATED LEATHER','A544',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2921,'SAI',37,'NB',4,'046-79-11','MOREL','AR-100 M','FOLLOW COLORO','34A','ECO GREEN RECYCLED LEATHER','A545',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2922,'METRO NB',16,'NB',4,'119-31-22','ATLANTIC BLUE','AR-100 M','FOLLOW COLORO','44Z','HYDRO PU COATED LEATHER','M088',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2923,'METRO NB',16,'NB',4,'058-99-35','NEW AFTER GLOW','AR-100 M','FOLLOW COLORO','71R','HYDRO PU COATED LEATHER','M089',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2924,'METRO NB',16,'NB',4,'003-68-23','DOUBLE BUBBLE','AR-100 M','FOLLOW COLORO','PINK','HYDRO PU COATED LEATHER','M090',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2925,'TAEKWANG',30,'NIKE',1,'6GV','PARTICLE ROSE','R-8 M','TMTK0272025022101','PINK','GENERIC PU COATED','A151',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2926,'CHANGSHIN RJ',4,'NIKE',1,'2EQ','PARTICLE BEIGE','UM-T SM','TMCS0052025021801','WHITE','GENERIC PU COATED','A389',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2927,'FENGTAY TW',58,'NIKE',1,'2BQ','SHIMMER','R-8 SG','TSFT0382025022401','2CT','GENERIC PU COATED','A299',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2928,'FENGTAY (WEST)',7,'NIKE',1,'20I','HEMP','AR-144 M','TMFT0062025022601','BROWN','VIRGIN HYDRO PU','A300',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2929,'ADIS',1,'NIKE',1,'44B','MIDNIGHT NAVY','R-53','TMAD0022025022601','BLACK','VIRGIN PU','A568',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2930,'PANARUB',19,'ADIDAS',3,'A6XY','TECH GREY MET','DE-7','SCOTDIC','WHITE','PU COATED LEATHER','A186','2025-04-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2931,'PANARUB',19,'ADIDAS',3,'ADFX','TEAM VICTORY RED','CPUG','FMCA PRB','RED','BABY SOFT PATENT LEATHER','A194','2025-08-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23','2026-05-19 03:12:23'),
(2932,'WEALTH VAST CO. LTD',61,'NIKE',1,'31B','MALACHITE','DE-41','TSSL0442025030601','3GU','GENERIC PU COATED LEATHER','A1257','2025-06-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2933,'WEALTH VAST CO. LTD',61,'NIKE',1,'6FT','PINK BLAST','DE-41','TSSL0442025030401','PINK','GENERIC PU COATED LEATHER','A1258','2025-06-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2934,'WEALTH VAST CO. LTD',61,'NIKE',1,'6LB','MYSTIC HIBISCUS','DE-41','TSSL0442025030402','RED','GENERIC PU COATED LEATHER','A1259','2025-06-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2935,'PANARUB',19,'ADIDAS',3,'AF44','PUTTY MAUVE','CPUG','SCOTDIC','WHITE','BABY SOFT PATENT LEATHER','A188','2025-06-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2936,'PANARUB',19,'ADIDAS',3,'AFH9','PRELOVED LIME','DE-7','SCOTDIC','71R','PU COATED LEATHER (MAP-ACTION LEATHER)','A189','2025-12-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2937,'PANARUB',19,'ADIDAS',3,'077A','CHALK WHITE','DE-7','FMCA PRB','WHITE','SOFT PU COATED LEATHER','A190',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2938,'PANARUB',19,'ADIDAS',3,'AJ3C','KHAKI THREE','DE-7','SCOTDIC','01V','PU COATED LEATHER (MAP-ACTION LEATHER)','A191',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2939,'PANARUB',19,'ADIDAS',3,'AJ3D','PURE LEMON','DE-7','SCOTDIC','YELLOW','PU COATED LEATHER (MAP-ACTION LEATHER)','A192',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2940,'ADIS',1,'NIKE',1,'2HI','DESERT KHAKI','R-231 M','TMAD0022025031301','WHITE','GENERIC PU COATED','A569',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2941,'ADIS',1,'NIKE',1,'2FL','BRONZE ECLIPSE','R-102','TMAD0022025031401','BROWN','GENERIC PU COATED LEATHER','A570',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2942,'ADIS',1,'NIKE',1,'20M','FLAX','R-102','TMAD0022025031402','2CT','GENERIC PU COATED LEATHER','A571',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2943,'ADIS',1,'NIKE',1,'0AC','LIGHT CARBON','R-102','TMAD0022025031403','GREY','GENERIC PU COATED LEATHER','A572',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2944,'VICTORY',31,'NIKE',1,'4PA','BLUE VOID','R-53','TMVC0052025031401','4MD','GENERIC PU COATED','A348',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2945,'SHOETOWN',28,'NIKE',1,'01B','METTALIC SILVER','AR-128','TMSL0432025031301','WHITE','VIRGIN PU','A1261',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2946,'POUYUEN',24,'NIKE',1,'3ME','MIDNIGHT GREEN','R-53 SM','TSPY0282025031702','BLACK','GENERIC PU COATED','A1262',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2947,'POUYUEN',24,'NIKE',1,'66Q','REDSTONE','R-53 SM','TMPY0282025042302','RED','GENERIC PU COATED','A1272',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23','2026-05-19 03:12:24'),
(2948,'HWASEUNG (HWP)',14,'ADIDAS',3,'AESR','WONDER QUARTZ','R-231','TMHW0362025031301','WHITE','SOHO NUBUCK','A841',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2949,'HWASEUNG (HWP)',14,'ADIDAS',3,'ADAT','ALUMINA','R-231','TMHW0362025031302','WHITE','SOHO NUBUCK','A842',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2950,'VICTORY',31,'NIKE',1,'63E','MED SOFT PINK','DE-73 SM','TMVC0052025031701','PINK','GENERIC PU COATED','A349',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2951,'VICTORY',31,'NIKE',1,'3NV','JADE HORIZON','R-53','TMVC0052025031801','WHITE','GENERIC PU COATED LEATHER','A350',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2952,'WEALTH VAST CO. LTD',61,'NIKE',1,'66Q','REDSTONE','R-53','TSSL0442025032101','RED','GENERIC PU COATED LEATHER','A1264',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2953,'WEALTH VAST CO. LTD',61,'NIKE',1,'3ME','MIDNIGHT GREEN','R-53','TSSL0442025032102','33R','GENERIC PU COATED LEATHER','A1265',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2954,'WEALTH VAST CO. LTD',61,'NIKE',1,'4PA','BLUE VOID','R-53','TSSL0442025032103','WHITE','GENERIC PU COATED LEATHER','A1266',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2955,'PANARUB',19,'ADIDAS',3,'AFDP','WONDER ALUMINA','CPUG','SCOTDIC','WHITE','BABY SOFT PATENT LEATHER','A193',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2956,'POUYUEN',24,'NIKE',1,'63E','MED SOFT PINK','CPUG','TSPY0282025032401','WHITE','LS PATENT LEATHER','A1267',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2957,'CHINGLUH',5,'NIKE',1,'0AK','PARTICLE GREY','AR-161 M','TMCL0172025032001','GREY','GENERIC PU COATED','A351',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2958,'CHINGLUH',5,'NIKE',1,'65N','UNIVERSITY RED','AR-161 M','TMCL0172025032002','RED','GENERIC PU COATED','A352',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2959,'POUYUEN',24,'NIKE',1,'64M','VARSITY RED','CPUG','TMPY0282025032701','BLACK','LS PATENT LEATHER','A1268','2025-08-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2960,'CHANGSHIN RJ',4,'NIKE',1,'0AH','DK SMOKE GREY','AR-138 M','TMCS0052025032601','BLACK','VIRGIN HYDRO PU LEATHER','A390','2025-08-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2961,'CHANGSHIN',3,'NIKE',1,'52X','LIGHT VIOLET','R-8 M','TMCS0042025032601','WHITE','GENERIC PU COATED','A391','2025-12-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2962,'NIKOMAS IY',18,'NIKE',1,'4LD','BLACKENED BLUE','AR-209 SG','TMNS0202025040901','BLACK','SEMI FULL GRAIN','A1269','2025-12-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2963,'KMK',15,'NIKE',1,'51L','COURT PURPLE','CPUG','TMKM0012025050801','WHITE','LACCATO PATENT LEATHER','A223',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23','2026-05-19 03:12:24'),
(2964,'NIKOMAS',17,'ADIDAS',3,'08F0','LIGHT BROWN','DE-7','SCOTDIC','01V','SOFT PU COATED LEATHER (MAP-SOFT PU)','A843',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2965,'NIKOMAS',17,'ADIDAS',3,'AJ3B','KHAKI SIX','DE-7','SCOTDIC','33R','SOFT PU COATED LEATHER (MAP-SOFT PU)','A844',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2966,'TAEKWANG',30,'NIKE',1,'4KY','THUNDER BLUE','AR-206 M','TMTK0272025041501','BLACK','VIRGIN HYDRO PU LEATHER','A152',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2967,'METRO NB',16,'NB',4,'115-38-04','NEW SHADOW BLUE','DE-90 M','FOLLOW COLORO','4MD','VIRGIN HYDRO PU LEATHER','M091',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2968,'PRATAMA',25,'NIKE',1,'87F','BRIGHT CERAMIC','AR-194 M','TSPT0122025041401','80S','VIRGIN HYDRO PU','A504',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2969,'PRATAMA',25,'NIKE',1,'0AH','DK SMOKE GREY','AR-194','TSPT0122025041402','BLACK','VIRGIN HYDRO PU','A505',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2970,'PRATAMA',25,'NIKE',1,'4LZ','LT ARMORY BLUE','R-8 M','TSPT0122025041403','WHITE','GENERIC PU COATED','A506',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2971,'PRATAMA',25,'NIKE',1,'6LD','PINK SPELL FLUORESCENT','R-8 M','TSPT0122025041404','PINK','GENERIC PU COATED','A507',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2972,'CHINGLUH',5,'NIKE',1,'4EI','BLUE CHILL','R-53','TMCL0172025041101','4AU','GENERIC PU COATED LEATHER','A353',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2973,'CHINGLUH',5,'NIKE',1,'64M','VARSITY RED','CPUG','TMCL0172025041401','RED','LS PATENT LEATHER','A354',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2974,'CHANGSHIN RJ',4,'NIKE',1,'12J','SUMMIT WHITE','AR-144','TMCS0052025041501','WHITE','VIRGIN HYDRO PU LEATHER','A392',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2975,'DWI PRIMA SENTOSA',45,'UA',5,'625','VINTAGE MAROON','AR-191 M','TMDW0012026010602','BLACK','VIR SOFT ACTION LEATHER','A393','2026-08-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23','2026-05-19 03:12:26'),
(2976,'DWI PRIMA SENTOSA',45,'UA',5,'932','ZEPPELIN YELLOW','AR-191 M','FOLLOW CSI UA','YELLOW','VIR SOFT ACTION LEATHER','A313',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23',NULL),
(2977,'DWI PRIMA SENTOSA',45,'UA',5,'997','BLACKOUT NAVI','AR-191 M','TMDW0012026010702','BLACK','VIR SOFT ACTION LEATHER','A394','2026-08-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:23','2026-05-19 03:12:26'),
(2978,'DWI PRIMA SENTOSA',45,'UA',5,'034','BLUE FOG','AR-191 M','FOLLOW CSI UA','WHITE','VIR SOFT ACTION LEATHER','A315',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(2979,'DWI PRIMA SENTOSA',45,'UA',5,'361','NEO TURQUOISE','AR-191 M','FOLLOW CSI UA','4AU','VIR SOFT ACTION LEATHER','A316',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(2980,'DWI PRIMA SENTOSA',45,'UA',5,'430','AEGEAN BLUE','AR-191 M','FOLLOW CSI UA','BLUE','VIR SOFT ACTION LEATHER','A317',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(2981,'DWI PRIMA SENTOSA',45,'UA',5,'622','CLARET','AR-191 M','FOLLOW CSI UA','RED','VIR SOFT ACTION LEATHER','A318',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(2982,'DWI PRIMA SENTOSA',45,'UA',5,'791','AQUA FLOAT','AR-191 M','FOLLOW CSI UA','4AU','VIR SOFT ACTION LEATHER','A319',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(2983,'CHINGLUH',5,'NIKE',1,'66Q','REDSTONE','R-53 M','TMCL0172025041601','80S','GENERIC PU COATED LEATHER','A355',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(2984,'TAEKWANG',30,'NIKE',1,'33X','VINTAGE GREEN','AR-144','TMTK0272025042101','33R','VIRGIN HYDRO PU LEATHER','A153',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(2985,'TAEKWANG',30,'NIKE',1,'55P','DEEP NIGHT','AR-144','TMTK0272025042102','44Z','VIRGIN HYDRO PU LEATHER','A154',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(2986,'TAEKWANG',30,'NIKE',1,'06L','GHOST','AR-144','TMTK0272025042201','WHITE','VIRGIN HYDRO PU LEATHER','A155',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(2987,'SHOETOWN',17,'NIKE',1,'3NV','JADE HORIZON','R-53','TMNS0432025042201','WHITE','GENERIC PU COATED LEATHER','A1270',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(2988,'SHT',48,'NB',4,'006-48-07','PEBBLE COLORO','AR-100 M','FOLLOW COLORO','PINK','HYDRO PU COATED LEATHER','A546',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(2989,'SAI',37,'NB',4,'012-77-19','PINK LEMONADE','AR-100 M','FOLLOW COLORO','80S','HYDRO PU COATED LEATHER','A547',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(2990,'SAI',37,'NB',4,'157-90-05','PINK SALT COLORO','AR-100 M','TSSD0462025042201','WHITE','HYDRO PU COATED LEATHER','A548',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(2991,'SAI',37,'NB',4,'058-99-35','NEW AFTER GLOW','AR-100 M','TSSD0462025042202','WHITE','HYDRO PU COATED LEATHER','A549',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(2992,'SAI',37,'NB',4,'119-31-22','ATLANTIC BLUE','AR-100 M','TSSD0462025042203','44Z','HYDRO PU COATED LEATHER','A550',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(2993,'SAI',37,'NB',4,'015-65-41','TANGERINE HEAT COLORO','AR-100 M','FOLLOW COLORO','RED/80S','HYDRO PU COATED LEATHER','A561',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24','2026-05-19 03:12:24'),
(2994,'SAI',37,'NB',4,'003-68-23','DOUBLE BUBBLE','AR-100 M','TSSD0462025042205','PINK','HYDRO PU COATED LEATHER','A552',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(2995,'SAI',37,'NB',4,'026-94-43','WHITE PEACH','AR-100 M','TSSD0462025042206','WHITE','HYDRO PU COATED LEATHER','A553',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(2996,'SAI',37,'NB',4,'049-65-00','CONCRETE COLORO','AR-100 M','TSSD0462025042207','WHITE','HYDRO PU COATED LEATHER','A554',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(2997,'SAI',37,'NB',4,'036-90-02','NEW SEA SALT','AR-100 M','TSSD0462025042208','WHITE','HYDRO PU COATED LEATHER','A555',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(2998,'SAI',37,'NB',4,'138-39-02','NEPTUNE GREY','AR-100 M','FOLLOW COLORO','GREY/BLACK','HYDRO PU COATED LEATHER','A641','2026-07-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24','2026-05-19 03:12:26'),
(2999,'SAI',37,'NB',4,'000-68-00','RAINCLOUND COLORO','AR-100 M','TSSD0462025042210','WHITE','HYDRO PU COATED LEATHER','A557',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3000,'SHOETOWN',28,'NIKE',1,'66Q','REDSTONE','R-53','TMSL0432025042301','RED','GENERIC PU COATED LEATHER','A1271',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3001,'FENGTAY',9,'NIKE',1,'64M','VARSITY RED','AR-99 M','TMFT0082025042301','RED','GENERIC PU COATED','A301',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3002,'SHT',48,'NB',4,'034-81-27','CELEMEN TINE COLORO','AR-100 M','FOLLOW COLORO','YELLOW','HYDRO PU COATED LEATHER','A558',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3003,'SHT',48,'NB',4,'127-83-02','FRESH AIR COLORO','AR-100 M','FOLLOW COLORO','01V','HYDRO PU COATED LEATHER','A559',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3004,'SHT',48,'NB',4,'100-64-21','BLUE GAZE COLORO','AR-100 M','FOLLOW COLORO','4JE','HYDRO PU COATED LEATHER','A560',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3005,'POUYUEN',24,'NIKE',1,'4PA','BLUE VOID','R-53 SM','TMPY0282025042301','WHITE','GENERIC PU COATED','A1273',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3006,'PANARUB',19,'ADIDAS',3,'AJ3L','SOLAR PURPLE','CPUG','SCOTDIC','58U','LACATTO PATENT LEATHER','A195',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3007,'SAI',37,'NB',4,'049-86-07','PISTACHIO BUTTER','AR-100 M','FOLLOW COLORO','WHITE','HYDRO PU COATED LEATHER','A562',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3008,'SAI',37,'NB',4,'035-88-12','CALCIUM','AR-100 M','FOLLOW COLORO','WHITE','HYDRO PU COATED LEATHER','A563',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3009,'METRO NB',16,'NB',4,'121-48-06','ARTIC GREY','CPUG','FOLLOW COLORO','LIGHT BLUE','LACATTO PATENT LEATHER','M092',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3010,'METRO NB',16,'NB',4,'036-79-07','BONE','CPUG','FOLLOW COLORO','WHITE','LACATTO PATENT LEATHER','M093',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3011,'SAI',37,'NB',4,'067-69-01','LONG STAR GREY','AR-100 M','TMSD0472025123001','WHITE','HYDRO PU COATED LEATHER','A622',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24','2026-05-19 03:12:26'),
(3012,'GLOSTAR',12,'NB',4,'000-55-00','SLATE GREY','AR-169 M','TSGS0092025042401','WHITE','HYDRO PU COATED LEATHER','A565',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3013,'DWI PRIMA SENTOSA',45,'UA',5,'760','FIELD YELLOW','AR-191 M','FOLLOW CSI UA','YELLOW','VIR SOFT ACTION LEATHER','A320','2025-02-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3014,'PRATAMA',25,'NIKE',1,'01B','METTALLIC SILVER','AR-172 M','TMPT0122025042901','WHITE','GENERIC PU COATED','A508','2025-02-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3015,'FENGTAY (WEST)',7,'NIKE',1,'55P','DEEP NIGHT','AR-144','TMFT0062025042501','44Z','VIRGIN HYDRO PU LEATHER','A302','2025-02-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3016,'FENGTAY (WEST)',7,'NIKE',1,'06L','GHOST','AR-144','TMFT0062025042502','WHITE','VIRGIN HYDRO PU LEATHER','A303','2025-02-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3017,'FENGTAY (WEST)',7,'NIKE',1,'58A','EGGPLANT','DE-126','TMFT0062025042901','PURPLE','VIRGIN HYDRO PU LEATHER','A304','2025-02-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3018,'CHINGLUH',5,'NIKE',1,'22Z','BAROQUE BROWN','R-53','TMCL0172025042801','BLACK','GENERIC PU COATED LEATHER','A356','2025-02-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3019,'CHINGLUH',5,'NIKE',1,'6GN','SPEED GREEN','DE-73 SM','TMCL0172025042901','WHITE','GENERIC PU COATED','A357','2025-02-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3020,'CHINGLUH',5,'NIKE',1,'4EV','GAME ROYAL','DE-73 SM','TMCL0172025042902','44Z','GENERIC PU COATED','A358','2025-02-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3021,'CHINGLUH',5,'NIKE',1,'77C','GOLD','DE-73 SM','TMCL0172025042903','2CT','GENERIC PU COATED','A359','2025-02-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3022,'VICTORY',31,'NIKE',1,'4PA','BLUE VOID','R-53','TSVC0052025043001','WHITE','GENERIC PU COATED LEATHER','A360','2025-02-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3023,'KMK',15,'NIKE',1,'38W','LUCKY GREEN','CPUG','TMKM0012025043001','WHITE','LACCATO PATENT LEATHER','A220','2025-06-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3024,'KMK',15,'NIKE',1,'65N','UNIVERSITY RED','CPUG','TMKM0012025043002','WHITE','LACCATO PATENT LEATHER','A221','2025-06-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3025,'KMK',15,'NIKE',1,'40I','NAVY','CPUG','TMKM0012025043003','WHITE','LACCATO PATENT LEATHER','A222','2025-06-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3026,'CHANGSHIN',3,'NIKE',1,'68W','PINK GLAZE','UM-34','TMCS0042025050201','PINK','VIRGIN HYDRO PU LEATHER','A393','2025-06-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3027,'CHINGLUH',5,'NIKE',1,'04Z','PURE PLATINUM','R-53','TMCL0172025050201','WHITE','VIRGIN HYDRO PU LEATHER','A361','2025-06-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3028,'PANARUB',19,'ADIDAS',3,'AJ3C','KHAKI THREE','DE-7','FMCA PRB','01V','PU COATED LEATHER (MAP ACTION LEATHER)','A196','2025-06-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3029,'PANARUB',19,'ADIDAS',3,'AF4L','PRELOVED INK','DE-7','FMCA PRB','GREY','PU COATED LEATHER (MAP ACTION LEATHER)','A197','2025-06-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3030,'CHANGSHIN RJ',4,'NIKE',1,'6GD','SILT RED','DE-135 SG','TMCS0052025050601','WHITE','GENERIC PU COATED LEATHER','A394','2025-09-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3031,'PRATAMA',25,'NIKE',1,'24Q','SILT RED','R-53 SM','TSPT0122025050601','BROWN','GENERIC PU COATED LEATHER','A509','2025-09-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3032,'SAI',37,'NB',4,'008-35-06','FAST TRACK','AR-100','FOLLOW COLORO','BROWN','HYDRO PU COATED LEATHER','A566','2025-10-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3033,'SAI',37,'NB',4,'142-49-03','OFF-LINE GREY','AR-100','FOLLOW COLORO','GREY','HYDRO PU COATED LEATHER','A567','2025-10-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3034,'NIKOMAS',17,'ADIDAS',3,'AFK7','VIOLET','CPUG','SCOTDIC','58U','BABY SOFT PATENT LEATHER','A845','2025-10-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3035,'YOUNG TREE SOLO',46,'UA',5,'919','ARDEN GREEN','AR-191','TMYT0022025071001','BLACK','ACTION PU COATED LEATHER','A334','2025-11-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24','2026-05-19 03:12:24'),
(3036,'METRO NB',16,'NB',4,'038-75-26','LIGHT MARS YELLOW','AW-28 SG','FOLLOW COLORO','YELLOW','HYDRO PU COATED LEATHER','M094',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3037,'METRO NB',16,'NB',4,'072-45-16','OUTFIELD','AW-28 SG','FOLLOW COLORO','33R','HYDRO PU COATED LEATHER','M095',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3038,'NIKOMAS IY',18,'NIKE',1,'42Z','COURT BLUE','AR-20 M','TSNS0202025051401','BLUE','VIRGIN PU','A1274',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3039,'NIKOMAS',17,'ADIDAS',3,'AEYV','LUCID PINK','CPUG','TMNS0162025080801','6DX','BABY SOFT PATENT LEATHER','A853','2025-08-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24','2026-05-19 03:12:24'),
(3040,'SHT',48,'NB',4,'131-74-12','SMOKED VIOLET COLORO','AR-100 M','TSSH0012025061101','49D','HYDRO PU COATED LEATHER','A569',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24','2026-05-19 03:12:24'),
(3041,'TSH',34,'ADIDAS',3,'AE5Z','CRYSTAL LINEN','DE-7','SCOTDIC','01V','PU COATED LEATHER','A847',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3042,'YOUNG TREE SOLO',46,'UA',5,'877C','METALLIC SILVER (PEARLIZED)','AR-191','TMYT0022025063004','WHITE','ACTION PU COATED LEATHER','A327','2025-01-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24','2026-05-19 03:12:24'),
(3043,'ADIS',1,'NIKE',1,'07G','LIGHT BONE','AR-73 M','TMAD0022025052601','WHITE','VIRGIN PU','A573',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3044,'PRATAMA',25,'NIKE',1,'50B','SAPPHIRE','DE-7 SM','TSPT0122025060501','44Z','GENERIC PU COATED','A510','2025-10-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3045,'PRATAMA',25,'NIKE',1,'26U','MEDIUM ASH','DE-7 SM','TSPT0122025060502','BLACK','GENERIC PU COATED','A511','2025-10-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3046,'GLOSTAR (ADS)',11,'ADIDAS',3,'AAGG','CARBON','DE-7','TMGS0072025060301','BLACK','SOFT PU','A848','2025-10-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3047,'GLOSTAR (ADS)',11,'ADIDAS',3,'AETF','EARTH STRATA','DE-7','TMGS0072025060302','LIGHT BROWN','SOFT PU','A849','2025-10-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3048,'CHINGLUH',5,'NIKE',1,'01E','NEUTRAL GREY','DE-41','TMCL0172025060901','WHITE','GENERIC PU COATED LEATHER','A362','2025-10-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3049,'CHINGLUH',5,'NIKE',1,'6GV','PARTICLE ROSE','DE-41','TMCL0172025060902','PINK','GENERIC PU COATED LEATHER','A363','2025-10-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3050,'CHANGSHIN',3,'NIKE',1,'3AW','HASTA','R-8 M','TMCS0042025061001','GREY','GENERIC PU COATED','A395','2025-12-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3051,'WEALTH VAST CO. LTD',61,'NIKE',1,'6JF','PINK GAZE','DE-73 SM','TSSL0442025061001','WHITE','GENERIC PU COATED LEATHER','A1276','2025-12-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3052,'WEALTH VAST CO. LTD',61,'NIKE',1,'45F','DK POWDER BLUE','DE-73 SM','TSSL0442025061002','WHITE','GENERIC PU COATED','A1277','2025-12-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3053,'WEALTH VAST CO. LTD',61,'NIKE',1,'3MZ','VINTAGE LICHEN','R-53','TSSL0442025061003','WHITE','GENERIC PU COATED LEATHER','A1278','2025-12-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3054,'WEALTH VAST CO. LTD',61,'NIKE',1,'4AH','AURA','R-53','TSSL0442025061004','WHITE','GENERIC PU COATED LEATHER','A1279','2025-12-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3055,'WEALTH VAST CO. LTD',61,'NIKE',1,'6DU','INFRARED 23','R-53','TSSL0442025061005','RED','GENERIC PU COATED LEATHER','A1280','2025-12-06','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3056,'ADIS',1,'NIKE',1,'05Q','FOOTBALL GREY','AR-73 M','TMAD0022025081901','WHITE','VIRGIN PU','A577',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24','2026-05-19 03:12:25'),
(3057,'CHANGSHIN RJ',4,'NIKE',1,'60I','CHINA ROSE FLUORESCENT','R-8 M','TMCS0052025060301','6DX','GENERIC PU COATED','A396',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3058,'TAEKWANG KR',60,'NIKE',1,'01V','WOLF GREY','AR-172','TMTK0282025061301','01V','GENERIC PU COATED','A156',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3059,'SCI',32,'NIKE',1,'2BQ','SHIMMER','AR-167 DM','TMSC0062025061101','WHITE','GENERIC PU COATED','A1281',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3060,'CHANGSHIN RJ',4,'NIKE',1,'27K','LT BRITISH TAN','R-8 M','TMCS0052025051901','BROWN','GENERIC PU COATED','A397',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3061,'TSH',34,'ADIDAS',3,'AETE','OLIVE STRATA','DE-7','SCOTDIC','3MR','PU COATED LEATHER','A850',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3062,'KMK',15,'NIKE',1,'6HN','BURGUNDY CRUSH','R-8 M','TSKM0012025061906','BLACK','GENERIC PU COATED','A224',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3063,'SAI',37,'NB',4,'068-55-00','BAYBERRY','AR-100 M','TMSD04720260108010','GREY','HYDRO PU COATED LEATHER','A626','2026-09-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24','2026-05-19 03:12:26'),
(3064,'SAI',37,'NB',4,'107-31-15','STREAMSONG','AR-100 M','FOLLOW COLORO','3AX','HYDRO PU COATED LEATHER','A571',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3065,'KMK',15,'NIKE',1,'42Z','COURT BLUE','R-8 M','TSKM0012025061901','44Z','GENERIC PU COATED','A225',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3066,'KMK',15,'NIKE',1,'3PM','EVERGREEN AURA','R-8 M','TSKM0012025061905','33R','GENERIC PU COATED','A226',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3067,'KMK',15,'NIKE',1,'0AJ','SMOKE GREY','R-8 M','TSKM0012025061909','BLACK','GENERIC PU COATED','A227',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3068,'YOUNG TREE SOLO',46,'UA',5,'011','MOD GREY','DE-172','TMYT0022025063001','01V','ACTION PU COATED LEATHER','A323','2025-01-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3069,'YOUNG TREE SOLO',46,'UA',5,'011','MOD  GREY (PEARLIZED)','AR-191','FOLLOW SAMPLE','01V','ACTION PU COATED LEATHER','A324',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3070,'YOUNG TREE SOLO',46,'UA',5,'919','ARDEN GREEN','DE-172','TMYT0022025063005','BLACK','ACTION PU COATED LEATHER','A325','2025-01-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3071,'YOUNG TREE SOLO',46,'UA',5,'016','ANTHRACITE','DE-172','TMYT0022025070401','BLACK','ACTION PU COATED LEATHER','A326','2025-01-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3072,'YOUNG TREE SOLO',46,'UA',5,'023','DISTANT GRAY','AR-191','TMYT0022025063003','WHITE','ACTION PU COATED LEATHER','A328','2025-01-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3073,'CHANGSHIN RJ',4,'NIKE',1,'2DR','TAUPE HAZE','R-102','TMCS0052025070102','LIGHT BROWN','ECO TECH COMFORT','A398','2025-01-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3074,'CHANGSHIN',4,'NIKE',1,'65N','UNIVERSITY RED','R-8 M','TMCS0052025063001','RED','(PM) GENERIC PU COATED','A400','2025-01-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3075,'NIKOMAS IY',18,'NIKE',1,'3PI','SAFFRON QUARTZ','R-131','TSNS0202025070101','YELLOW','VIRGIN HYDRO PU','A1282','2025-03-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3076,'YOUNG TREE SOLO',46,'UA',5,'338','RACK GREEN','AR-191','TSYT0022025071601','3AW','ACTION PU COATED LEATHER','A338',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24','2026-05-19 03:12:24'),
(3077,'KMK',15,'NIKE',1,'4AH','AURA','R-8 M','TSKM0012025061902','WHITE','(PM) GENERIC PU COATED','A228',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3078,'KMK',15,'NIKE',1,'01X','PHANTOM','R-8 M','TSKM0012025061908','WHITE','(PM) GENERIC PU COATED','A229',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3079,'FENGTAY',7,'NIKE',1,'0BL','PENCIL POINT','R-8 SG','TSFT0062025062001','GREY','GENERIC PU COATED','A305',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3080,'CHINGLUH',5,'NIKE',1,'3MZ','VINTAGE LICHEN','R-53','TMCL0172025062501','3MR','GENERIC PU COATED LEATHER','A364',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3081,'POUYUEN',24,'NIKE',1,'45F','DK POWDER BLUE','DE-73','TMPY0282025062601','WHITE','(PM) GENERIC PU COATED','A1283',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3082,'KMK',15,'NIKE',1,'0AP','PLATINUM TINT','R-8 M','TSKM0012025061903','WHITE','(PM) GENERIC PU COATED','A230',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3083,'PRATAMA',25,'NIKE',1,'2HG','LT KHAKI','AR-188','TSPT0122025070301','WHITE','VIRGIN HYDRO PU','A512','2025-04-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3084,'YOUNG TREE SOLO',46,'UA',5,'290','DESSERT SAND','DE-172','TMYT0022025063002','WHITE','ACTION PU COATED LEATHER','A330','2025-04-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3085,'POUYUEN',24,'NIKE',1,'45B','OBSIDIAN','DE-73','TMPY0282025062301','BLACK','(PM) GENERIC PU COATED','A1284',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3086,'POUYUEN',24,'NIKE',1,'6JF','PINK GAZE FLUORESCENT','DE-73','TMPY0282025071401','WHITE','(PM) GENERIC PU COATED','A1285',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3087,'CHINGLUH',5,'NIKE',1,'6JF','PINK GAZE FLUORESCENT FLUORESCENCE','DE-73','TMCL0172025062401','WHITE','(PM) GENERIC PU COATED','A365',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3088,'CHINGLUH',5,'NIKE',1,'10L','PALE IVORY','DE-41','TMCL0172025062502','WHITE','GENERIC PU COATED LEATHER DE-41','A366',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3089,'YOUNG TREE SOLO',46,'UA',5,'001 PEARLIZED','BLACK','AR-191','TMYT0022025070901','BLACK','ACTION PU COATED LEATHER','A331','2025-09-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3090,'YOUNG TREE SOLO',46,'UA',5,'600','RED','AR-191','TMYT0022025070902','RED','ACTION PU COATED LEATHER','A332','2025-09-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3091,'YOUNG TREE SOLO',46,'UA',5,'400','ROYAL','AR-191','TMYT0022025070903','44Z','ACTION PU COATED LEATHER','A333','2025-09-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3092,'CHANGSHIN RJ',4,'NIKE',1,'0AJ','SMOKE GREY','DE-135 SG','TMCS0052025070901','GREY','GENERIC PU COATED LEATHER','A401','2025-10-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3093,'YOUNG TREE SOLO',46,'UA',5,'011','MOD GRAY','AE-191','TSYT0022025071001','0IV','ACTION PU COATED LEATHER','A335','2025-11-07','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3094,'POUYUEN',24,'NIKE',1,'3MZ','VINTAGE LICHEN','R-53','TMPY0282025071402','WHITE','GENERIC PU COATED','A1286',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3095,'SHT',48,'NB',4,'008-85-11','NEW SHELL PINK','AR-140','TMSH0012025071501','WHITE','HYDRO PU COATED LEATHER','A572',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3096,'YOUNG TREE SOLO',46,'UA',5,'001','BLACK','DE-172','TMYT0022025071401','BLACK','ACTION PU COATED LEATHER','A336',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3097,'YOUNG TREE SOLO',46,'UA',5,'025','CASTLEROCK (PEARLIZED)','AR-191','TMYT0022025071501','BLACK','ACTION PU COATED LEATHER','A337',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3098,'SHT',48,'NB',4,'017-79-00','GREY MATTER','AR-100 M','TMSH0012025072101','WHITE','HYDRO PU COATED LEATHER','A573',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3099,'KMK',15,'NIKE',1,'0AN','GREY FOG','R-8 M','TSKM0012025061904','WHITE','(PM) GENERIC PU COATED','A231',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3100,'KMK',15,'NIKE',1,'12J','SUMMIT WHITE','R-8 M','TSKM0012025061907','WHITE','(PM) GENERIC PU COATED','A232',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3101,'KMK',15,'NIKE',1,'22Z','BAROQUE BROWN','R-8','TMKM0012025072901','BROWN','VIRGIN HYDRO PU LEATHER','A233',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3102,'SHOETOWN',28,'NIKE',1,'45F','DK POWER BLUE','AR-196M','TMSL0432025072101','WHITE','(PM) GENERIC PU COATED','A1287',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3103,'SHOETOWN',28,'NIKE',1,'3MZ','VINTAGE GREEN','R-53','TMSL0432025072102','3MR','GENERIC PU COATED LEATHER','A1288',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3104,'POUYUEN',24,'NIKE',1,'06B','COOL GREY','CPUG','TSPY0282025072901','BLACK','LS PATENT LEATHER','A1289',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3105,'POUYUEN',24,'NIKE',1,'4LC','SQUADRON BLUE','CPUG','TMPY0282025102401','WHITE','LS PATENT LEATHER','A1315',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24','2026-05-19 03:12:25'),
(3106,'CHANGSHIN',3,'NIKE',1,'6GD','SILT RED','R-8 M','TSCS0042025071802','WHITE','(PM) GENERIC PU COATED','A402',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3107,'CHANGSHIN',3,'NIKE',1,'70H','SONIC YELLOW (FLUORESCENT)','R-8 M','TSCS0042025071801','YELLOW','(PM) GENERIC PU COATED','A403',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3108,'CHANGSHIN RJ',4,'NIKE',1,'01X','PHANTOM','DE-135 SG','TMCS0052025071801','WHITE','GENERIC PU COATED LEATHER','A404',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3109,'CHANGSHIN RJ',4,'NIKE',1,'29E','CREAM II','DE-135 SG','TMCS0052025071802','01V','GENERIC PU COATED LEATHER','A405',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3110,'FENGTAY',7,'NIKE',1,'44B','MIDNIGHT NAVY','AR-144 M','TMFT0062025062601','BLACK','VIRGIN HYDRO PU LEATHER','A306',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3111,'FENGTAY (NORTH)',9,'NIKE',1,'06F','ANTHRACITE','AR-99 SM','TMFT0082025072401','BLACK','(PM) GENERIC PU COATED','A307',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3112,'GLOSTAR (ADS)',11,'ADIDAS',3,'AFAF','AURORA INK','DE-7','TMGS0072025072401','BLACK','SOFT PU','A851',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3113,'NIKOMAS',17,'ADIDAS',3,'AA2S','GREY TWO','DE-7','TMNS0162025073001','GREY','PU COATED LEATHER','A852',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3114,'TAEKWANG',30,'NIKE',1,'06F','ANTHRACITE','AR-172','TMTK0272025072101','BLACK','(PM) GENERIC PU COATED','A157',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3115,'CHINGLUH',5,'NIKE',1,'4AH','AURA','R-53','TMCL0172025072301','WHITE','GENERIC PU COATED','A367',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3116,'SHT',48,'NB',4,'032-76-04','TIMBERWOLF','AR-100 M','TMSH0012025072102','WHITE','HYDRO PU COATED LEATHER','A574','2025-06-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3117,'SHT',48,'NB',4,'8001C','SILVER METTALIC','AR-140 M','TMSH0012025072103','WHITE','HYDRO PU COATED LEATHER','A575','2025-06-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3118,'POUYUEN',24,'NIKE',1,'6FS','PINKSICLE FLUORESCENT','R-8 M','TMPY0282025080401','RED','GENERIC PU COATED','A1291','2025-06-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3119,'POUYUEN',24,'NIKE',1,'63E','MED SOFT PINK','R-8 M','TMPY0282025072901','PINK','GENERIC PU COATED','A1292','2025-06-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3120,'FENGTAY (NORTH)',9,'NIKE',1,'10L','PALE IVORY','AR-107 M','TMFT0082025073101','WHITE','GENERIC PU COATED','A308','2025-06-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3121,'CHINGLUH',5,'NIKE',1,'6JF','PINK GAZE','R-51 SM','TMCL0172025072901','WHITE','GENERIC PU COATED','A368','2025-06-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3122,'YOUNG TREE SOLO',46,'UA',5,'024','TITAN GRAY','AR-191 M','TSYT0022025080501','BLACK','ACTION PU COATED LEATHER','A339','2025-06-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3123,'NIKOMAS IY',18,'NIKE',1,'84V','TURF ORANGE','R-131 M','TSNS0202025080501','80S','VIRGIN HYDRO PU','A1293','2025-06-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3124,'NIKOMAS IY',18,'NIKE',1,'4LA','WORK BLUE','R-131 M','TSNS0202025080502','LIGHT BLUE','VIRGIN HYDRO PU','A1294','2025-06-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3125,'NIKOMAS IY',18,'NIKE',1,'31B','MALACHITE','R-131 M','TSNS0202025080503','3GU','VIRGIN HYDRO PU','A1295','2025-06-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3126,'NIKOMAS IY',18,'NIKE',1,'51L','COURT PURPLE','CPUG','TSNS0202025080504','PURPLE','VIRGIN HYDRO PU','A1296','2025-06-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3127,'ADIS',1,'NIKE',1,'45B','OBSIDIAN','R-131','TMAD0022025080801','BLACK','VIRGIN PU','A576','2025-08-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3128,'CHANGSHIN RJ',4,'NIKE',1,'5BC','STELLAR INDIGO','R-8 M','TMCS0052025072804','GREY','(PM) GENERIC PU COATED','A406','2025-08-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3129,'CHANGSHIN RJ',4,'NIKE',1,'07G','LIGHT BONE','R-8 M','TMCS0052025080601','WHITE','(PM) GENERIC PU COATED','A407','2025-08-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3130,'CHANGSHIN RJ',4,'NIKE',1,'3AW','HASTA','R-8 M','TMCS0052025080602','GREY','(PM) GENERIC PU COATED','A408','2025-08-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3131,'CHANGSHIN RJ',4,'NIKE',1,'3FM','LUCID GREEN','R-8 M','TMCS0052025072805','3GU','(PM) GENERIC PU COATED','A409','2025-08-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3132,'SHOETOWN',28,'NIKE',1,'6DL','GYM RED','R-53','TMSL0432025080701','RED','VIRGIN HYDRO PU LEATHER','A1297','2025-08-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3133,'YOUNG TREE SOLO',46,'UA',5,'230','INCENSE BROWN','DE-172','FOLLOW CSI','BROWN','ACTION PU COATED LEATHER','A340','2025-09-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3134,'YOUNG TREE SOLO',46,'UA',5,'246','KONA BROWN','DE-172','FOLLOW CSI','BLACK','ACTION PU COATED LEATHER','A341','2025-09-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3135,'YOUNG TREE SOLO',46,'UA',5,'860','DARK OARNGE','DE-172','FOLLOW CSI','RED','ACTION PU COATED LEATHER','A342','2025-09-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3136,'CHANGSHIN RJ',4,'NIKE',1,'60F','PEARL PINK','R-8 M','TMCS0052025081102','WHITE','ECO TECH COMFORT','A410','2025-12-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3137,'CHANGSHIN RJ',4,'NIKE',1,'6GC','PARTICLE PINK','R-8 M','TMCS0052025081103','PINK','ECO TECH COMFORT','A411','2025-12-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3138,'CHANGSHIN RJ',4,'NIKE',1,'20I','HEMP','R-8 M','TMCS0052025081101','2CT','ECO TECH COMFORT','A412','2025-12-08','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3139,'PCN G8',59,'NIKE',1,'42Z','COURT BLUE','R-8 M','TMPG0212025081201','44Z','GENERIC PU COATED','A1298',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3140,'DWI PRIMA SENTOSA',45,'UA',5,'011','MOD GRAY','DE-73 SM','TMDW0012025081201','GREY','ACTION PU COATED LEATHER','A343',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:24',NULL),
(3141,'DWI PRIMA SENTOSA',45,'UA',5,'471','BLUE BLUR','DE-73 SM','TMDW0012025081203','4JE','ACTION PU COATED LEATHER','A344',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3142,'DWI PRIMA SENTOSA',45,'UA',5,'391','FADE GREEN','DE-73 SM','TMDW0012025081204','WHITE','ACTION PU COATED LEATHER','A345',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3143,'DWI PRIMA SENTOSA',45,'UA',5,'035','STEEL','DE-73 SM','TMDW0012025081205','BLACK','ACTION PU COATED LEATHER','A346',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3144,'DWI PRIMA SENTOSA',45,'UA',5,'024','TITAN GRAY','DE-73 SM','TMDW0012025081206','BLACK','ACTION PU COATED LEATHER','A347',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3145,'FENGTAY (WEST)',8,'NIKE',1,'04Z','PURE PLATINUM','AR-144 M','TMFT0072025081301','WHITE','VIRGIN HYDRO PU','A309',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3146,'YOUNG TREE SOLO',46,'UA',5,'280','SANDSTORM','AR-191 M','TMYT0022025081401','WHITE','ACTION PU COATED LEATHER','A348',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3147,'YOUNG TREE SOLO',46,'UA',5,'025','CASTLEROCK','DE-172','TMYT0022025081501','BLACK','ACTION PU COATED LEATHER','A349',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3148,'KMK',15,'NIKE',1,'14A','OFF WHITE','R-8 M','TMKM0012025081401','WHITE','(PM) GENERIC PU COATED','A234',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3149,'SAI',37,'NB',4,'004-24-14','NB BURGANDY','AR-100','FOLLOW COLORO','BROWN','HYDRO PU COATED LEATHER','A576',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3150,'SHT',48,'NB',4,'115-66-17','BLUE HAZE','AR-100 M','TMSH0012025082001','LIGHT BLUE','HYDRO PU COATED LEATHER','A577',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3151,'SHT',48,'NB',4,'003-68-23','DOUBLE BUBBLE','AR-100 M','TMSH0012025082002','PINK','HYDRO PU COATED LEATHER','A578',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3152,'SHT',48,'NB',4,'124-23-11','NB NAVY COLORO','AR-100 M','TMSH0012025082003','BLACK','HYDRO PU COATED LEATHER','A579',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3153,'SHT',48,'NB',4,'157-90-05','PINK SALT COLORO','AR-100 M','TMSH0012025082004','WHITE','HYDRO PU COATED LEATHER','A580',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3154,'CHANGSHIN RJ',4,'NIKE',1,'77D','NEON YELLOW','R-8M','TMCS0052025082201','71R','(PM) GENERIC PU COATED','A413',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3155,'YOUNG TREE SOLO',46,'UA',5,'524','GRIMMACE','DE-172','TMYT0022025082201','58U','ACTION PU COATED LEATHER','A350',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3156,'GLOSTAR (ADS)',11,'ADIDAS',3,'076A','CORE WHITE','AR-211 SG','TMGS0072025082501','WHITE','PU COATED LEATHER','A854',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3157,'BIG',2,'ADIDAS',3,'AETG','BETTER SCARLET','DE-7 SM','TMBI0202025082501','RED','PU COATED LEATHER','A855',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3158,'PCN G8',59,'NIKE',1,'06B','COOL GREY','CPUG','TSPG0212025082901','BLACK','LS PATENT LEATHER','A1299','2025-01-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3159,'PCN G8',59,'NIKE',1,'4LC','SQUADRON BLUE','CPUG','TSPG0212025082902','WHITE','LS PATENT LEATHER','A1300','2025-01-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3160,'HWASEUNG',14,'ADIDAS',3,'AEK3','IMPACT ORANGE','R-231','TMHW0362025090101','80S','SOHO NUBUCK','A856','2025-02-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3161,'NIKOMAS',17,'ADIDAS',3,'A0RP','COLLEGIATE BURGUNDY','DE-7 SM','TSNS0162025090201','RED','SOFT PU COATED LEATHER (MAP-SOFT PU)','A857','2025-02-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3162,'BIG',2,'ADIDAS',3,'ACEP','ACTIVE GOLD','DE-73 SM','TMBI0202025090101','YELLOW','PU COATED LEATHER','A858','2025-03-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3163,'SHT',48,'NB',4,'011-80-11','PINK HAZE','AR-100 M','TSSH0012025090101','PINK','HYDRO PU COATED LEATHER','A581','2025-03-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3164,'FENGTAY (WEST)',7,'NIKE',1,'0AL','LT SMOKE GREY','AR-144 M','TMFT0062025090201','GREY','VIRGIN HYDRO PU','A310','2025-03-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3165,'FENGTAY (WEST)',7,'NIKE',1,'51R','TATTOO','AR-144 M','TMFT0062025090202','BROWN','VIRGIN HYDRO PU','A311','2025-03-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3166,'PANARUB',19,'ADIDAS',3,'AFH2','AURORA IVY','DE-7 SM','FMCA PRB','GREY','PU COATED LEATHER','A198','2025-06-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3167,'DWI PRIMA SENTOSA',45,'UA',5,'110','SUMMIT WHITE','DE-73 SM','TMDW0012025081202','WHITE','ACTION PU COATED LEATHER','A351',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3168,'CHINGLUH',5,'NIKE',1,'4EV','GAME ROYAL','R-51 SM','TMCL0172025090401','44Z','(PM) GENERIC PU COATED','A369','2025-07-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3169,'METRO NB',16,'NB',4,'032-64-10','NEW INCENSE COLORO','DE-90 M','TMMP0332025090401','2CT','HYDRO PU COATED LEATHER','M098','2025-07-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3170,'SHT',48,'NB',4,'000-73-00','BRIGHTON GREY COLORO','AR-140 M','TMSH0012025090301','WHITE','HYDRO PU COATED LEATHER','A582','2025-08-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3171,'PCN G8',59,'NIKE',1,'0AL','LT SMOKE GREY','R-8 M','TSPG0212025090401','GREY','(PM) GENERIC PU COATED','A1301','2025-07-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3172,'PCN G8',59,'NIKE',1,'6GD','SILT RED','R-8 M','TSPG0212025090402','PINK','(PM) GENERIC PU COATED','A1302','2025-07-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3173,'POUYUEN',24,'NIKE',1,'42Z','COURT BLUE','R-8 M','TMPY0282025090801','44Z','(PM) GENERIC PU COATED','A1303','2025-08-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3174,'PCN G8',59,'NIKE',1,'4LZ','LIGHT ARMORY BLUE','AR-20 M','TSPG0212025091001','WHITE','(PM) GENERIC PU COATED','A1304','2025-11-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3175,'TSH',34,'ADIDAS',3,'117A','NIGHT INDIGO','CPUG','SCOTDIC','BLACK','BABY SOFT PATENT LEATHER','A859','2025-12-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3176,'SHT',48,'NB',4,'058-99-35','NEW AFTERGLOW (FLUORESTCENT)','AR-100 M','TMSH0012025090802','71R','HYDRO PU COATED LEATHER','A583','2025-10-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3177,'NIKOMAS IY',18,'NIKE',1,'80S','TOTAL ORANGE (FLUORESCENT)','R-131 M','TMNS0202025091101','80S','VIRGIN HY PI','A1305','2025-12-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3178,'GLOSTAR (ADS)',11,'ADIDAS',3,'AA2S','GREY TWO','DE-7 SM','TMGS0072025091101','GREY','SOFT PU','A860','2025-11-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3179,'GLOSTAR (ADS)',11,'ADIDAS',3,'043A','DARK BLUE','DE-7 SM','TMGS0072025091102','44Z','SOFT PU','A861','2025-11-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3180,'VFI',55,'UA',5,'100','WHITE','R-231 M','TMVF00492025091001','WHITE','ACTION PU COATED LEATHER','A352','2025-10-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3181,'SHT',48,'NB',4,'119-31-22','ATLANTIC BLUE','AR-100 M','TMSH0012025090801','44Z','HYDRO PU COATED LEATHER','A584','2025-10-09','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3182,'CHANGSHIN RJ',4,'NIKE',1,'65N','UNIVERSITY RED FLUORESCENT','DE-126 SM','TMCS0052025091601','WHITE','(PM) GENERIC PU COATED','A414',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3183,'PRATAMA',25,'NIKE',1,'10J','LT OREWOOD BRN','AR-169 M','TSPT0122025091701','WHITE','VIRGIN HYDRU PU','A513',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3184,'VICTORY',31,'NIKE',1,'28G','LINEN','R-53 SM','TMVC0052025091601','WHITE','GENERIC PU COATED','A370',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3185,'HWASEUNG (HWP)',14,'ADIDAS',3,'AFDL','WARM SANDSTONE','R-231 M','TMHW0362025091601','WHITE','SOHO NUBUCK','A862',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3186,'PRATAMA',25,'NIKE',1,'44B','MIDNIGHT NAVY','AR-20 M','TSPT0122025092201','BLACK','(PM) GENERIC PI COATED','A514',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3187,'PRATAMA',25,'NIKE',1,'79W','TEAM GOLD','AR-20 M','TSPT0122025092202','YELLOW','(PM) GENERIC PU COATED','A515',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3188,'KMK',15,'NIKE',1,'71R','VOLT (FLUORESCENT)','AR-175 M','TMKM0012025092201','71R','ECO TECH COMFORT','A235',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3189,'POUYUEN',24,'NIKE',1,'5AC','VIOLET MIST','DE-73 SM','TMPY0282025092201','WHITE','(PM) GENERIC PU COATED','A1306',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3190,'SHOETOWN',28,'NIKE',1,'6EP','ICED CARMINE','R-53 SM','TMSL0432025092501','PINK','GENERIC PU COATED','A1307',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3191,'CHINGLUH',5,'NIKE',1,'48A','SPORT BLUE','R-8 M','TMCL0172025091901','44Z','VIRGIN HYDRO PU LEATHER','A371',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3192,'PRATAMA',25,'NIKE',1,'4NR','DIFFUSED BLUE','AR-20 M','TSPT0122025092401','BLACK','(PM) GENERIC PU COATED','A516',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3193,'SHT',48,'NB',4,'124-49-17','FAIREATHER BLUE COLORO','AR- 100 M','TMSH0012025092401','49D','HYDRO PU COATED LEATHER','A585',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3194,'FENGTAY TW',58,'NIKE',1,'0BL','PENCIL POINT','R-8 SG','TMFT0382025092601','GREY','(PM) GENERIC PU COATED','A312',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3195,'FENGTAY (WEST)',7,'NIKE',1,'48P','BLUE CRYSTAL','AR-144 M','TMFT0062025092401','44Z','VIRGIN HYDRO PU','A313',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3196,'ADIS',1,'NIKE',1,'01B','METALLIC SILVER','R-8 M','TMAD0022025092501','WHITE','(PM)GENERIC PU COATED','A578',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3197,'WEALTH VAST CO. LTD',61,'NIKE',1,'11F','SWAN','R-53','TSSL0442025092501','WHITE','GENERIC PU COATED LEATHER','A1308',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3198,'POUYUEN',24,'NIKE',1,'47N','UNIVERSITY BLUE','R-53 M','TSPY0282025092601','BLUE','GENERIC PU COATED','A1309',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3199,'NIKOMAS',17,'ADIDAS',3,'05F0','PYRITE','DE-7 SM','SCOTDIC','YELLOW','SOFT PU COATED LEATHER','A863',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3200,'NIKOMAS',17,'ADIDAS',3,'ADA3','TEAM LIGHT BLUE','DE-7 SM','SCOTDIC','LIGHT BLUE','SOFT PU COATED LEATHER','A864',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3201,'METRO NB',16,'NB',4,'034-84-05','NEW LINEN COLORO','DE-90 M','TMMP0332025093001','WHITE','HYDRO PU COATED LEATHER','M099','2025-01-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3202,'METRO NB',16,'NB',4,'120-76-08','OXFORD BLUE COLORO','DE-90 M','TMMP0332025093002','WHITE','HYDRO PU COATED LEATHER','M100','2025-01-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3203,'SAI',37,'NB',4,'122-36-01','GRAPHITE','AR-100 M','TMSD0472025091901','BLACK','HYDRO PU COATED LEATHER','A586',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3204,'SAI',37,'NB',4,'124-23-11','NB NAVY','AR-100 M','TMSD0472025091902','BLACK','HYDRO PU COATED LEATHER','A587',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3205,'SAI',37,'NB',4,'071-65-06','MOSAIC GREEN','AR-100 M','TMSD0472025091904','4AU','HYDRO PU COATED LEATHER','A588',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3206,'BIG',2,'ADIDAS',3,'AE6Z','DUSKY PETROL','DE-7 SM','TMBI0202025100201','44Z','PU COATED LEATHER','A865','2025-03-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3207,'SAI',37,'NB',4,'059-40-11','UTILITY GREEN','AR-100 M','FOLLOW COLORO','33R','HYDRO PU COATED LEATHER','A590','2025-02-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3208,'SAI',37,'NB',4,'134-68-00','ALIMINUM GREY COLORO','AR-100 M','FOLLOW COLORO','01V','HYDRO PU COATED LEATHER','A591','2025-02-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3209,'SHT',48,'NB',4,'026-79-03','MOONBEAN COLORO','AR-100 M','FOLLOW COLORO','WHITE','HYDRO PU COATED LEATHER','A592','2025-02-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3210,'SAI',37,'NB',4,'061-81-01','LIGHT BOYLSTON GREY COLORO','AR-100 M','FOLLOW COLORO','WHITE','HYDRO PU COATED LEATHER','A593','2025-02-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3211,'SAI',37,'NB',4,'024-86-12','ORANGE FROST','AR-100 M','FOLLOW COLORO','WHITE','HYDRO PU COATED LEATHER','A594','2025-02-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3212,'SAI',37,'NB',4,'023-70-28','FADED POPPY COLORO','AR-100 M','FOLLOW COLORO','80S','HYDRO PU COATED LEATHER','A595','2025-02-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3213,'SAI',37,'NB',4,'159-77-06','STONE PINK','AR-100 M','TMSD0472025091903','PINK','HYDRO PU COATED LEATHER','A596','2025-06-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3214,'SHT',48,'NB',4,'141-60-26','ORCHID COLORO','AR-100 M','FOLLOW COLORO','6DX','HYDRO PU COATED LEATHER','A597','2025-06-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3215,'SHT',48,'NB',4,'008-32-14','BROWNSTONE COLORO','AR-100 M','FOLLOW COLORO','RED','HYDRO PU COATED LEATHER','A598','2025-06-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3216,'SHT',48,'NB',4,'028-60-16','COCONUT SUGAR COLORO','AR-100 M','FOLLOW COLORO','2CT','HYDRO PU COATED LEATHER','A599','2025-06-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3217,'SAI',37,'NB',4,'028-68-12','LIGHT COCONUT SUGAR COLORO','AR-100 M','FOLLOW COLORO','2CT','HYDRO PU COATED LEATHER','A600','2025-06-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3218,'SHT',48,'NB',4,'061-76-02','SEA GLASS COLORO','AR-100 M','FOLLOW COLORO','WHITE','HYDRO PU COATED LEATHER','A601','2025-06-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3219,'SAI',37,'NB',4,'152-85-11','PINK FIZE COLORO','AR-100 M','FOLLOW COLORO','PINK','HYDRO PU COATED LEATHER','A602','2025-06-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3220,'SHT',48,'NB',4,'154-22-12','BLACK RUBBY COLORO','AR-100 M','FOLLOW COLORO','BROWN','HYDRO PU COATED LEATHER','A603','2025-06-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3221,'CHANGSHIN RJ',4,'NIKE',1,'47N','UNIVERSITY BLUE','R-8 M','TMCS0052025100301','44Z','ECO TECH COMFORT','A415','2025-06-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3222,'CHANGSHIN RJ',4,'NIKE',1,'4MT','HYDROGEN BLUE','R-8 M','TMCS0052025100302','WHITE','ECO TECH COMFORT','A416','2025-06-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3223,'CHANGSHIN RJ',4,'NIKE',1,'22V','VIOLET ORE','R-8 M','TMCS0052025100303','LIGHT  BROWN','ECO TECH COMFORT','A417','2025-06-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3224,'CHANGSHIN RJ',4,'NIKE',1,'52X','LIGHT VIOLET','R-8 M','TMCS0052025100304','WHITE','ECO TECH COMFORT','A418','2025-06-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3225,'CHINGLUH',5,'NIKE',1,'6EP','ICED CARMINE','DE-41 SG','TMCL0172025100601','PINK','GENERIC PU COATED','A372','2025-07-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3226,'CHINGLUH',5,'NIKE',1,'44B','MIDNIGHT NAVY','R-53 SM','TMCL0172025100301','BLACK','GENERIC PU COATED','A373','2025-07-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3227,'CHINGLUH',5,'NIKE',1,'0AV','OFF NOIR','DE-73 SM','TMCL0172025100602','BLACK','(PM) GENERIC PU COATED','A374','2025-08-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3228,'CHINGLUH',5,'NIKE',1,'5AC','VIOLET MIST','DE-73 SM','TMCL0172025100603','WHITE','(PM) GENERIC PU COATED','A375','2025-08-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3229,'CHINGLUH',5,'NIKE',1,'5AJ','BARELY GRAPE','DE-73 SM','TMCL0172025100604','WHITE','(PM) GENERIC PU COATED','A376','2025-08-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3230,'PRATAMA',25,'NIKE',1,'26U','MEDIUM ASH','AR-188 M','TSPT0122025100701','BLACK','VIRGIN HYDRO PU','A517','2025-08-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3231,'FENGTAY (WEST)',7,'NIKE',1,'06Q','MTLC COOL GREY (METALLIC)','AR-262','TMFT0062025101001','BLACK','(PM) GENERIC PU COATED','A314',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3232,'CHINGLUH',5,'NIKE',1,'47N','UNIVERSITY BLUE','R-53 SM','TMCL0172025101001','BLUE','GENERIC PU COATED','A377',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3233,'POUYUEN',24,'NIKE',1,'06B','COOL GREY','- (CPUG)','TSPY0282025101301','BLACK','LS PATENT LEATHER','A1310',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3234,'WEALTH VAST CO. LTD',61,'NIKE',1,'65N','UNIVERSITY RED (FLUORESCENT)','CPUG','SPG0212025101301','WHITE','LS PATENT LEATHER','A1311',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3235,'VICTORY FOOTWEAR',55,'UA',5,'19-3937 TPG','-','R-231','TMVF0502025100901','BLACK','ACTION PU COATED LEATHER','A353','2025-10-10','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3236,'GLOSTAR (NB)',12,'NB',4,'145-17-00','BLACK COLORO','AR-169 M','TMGS0092025101401','BLACK','HYDRO PU COATED LEATHER','A604',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3237,'GLOSTAR (NB)',12,'NB',4,'032-76-04','TIMBERWOLF COLORO','AR-169 M','TMGS0092025101402','WHITE','HYDRO PU COATED LEATHER','A605',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3238,'SHT',48,'NB',4,'122-36-01','GRAPHITE','AR-140 M','TMSH0012025101401','BLACK','HYDRO PU COATED LEATHER','A606',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3239,'WEALTH VAST CO. LTD',61,'NIKE',1,'4LC','SQUADRON BLUE','R-53','TSSL0442025101401','BLACK','GENERIC PU COATED LEATHER','A1312',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3240,'NIKOMAS IY',18,'NIKE',1,'34N','CLEAR JADE (FLUORESCENT)','UM-34 SM','TMNS0202025101601','3GU','(PM) GENERIC PU COATED','A1313',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3241,'TAEKWANG',30,'NIKE',1,'12A','OATMEAL','R-231 M','TMTK0272025101701','WHITE','SOHO NUBUCK','A158',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3242,'TAEKWANG',30,'NIKE',1,'4MT','HYDROGEN BLUE','R-231 M','TMTK0272025101702','WHITE','SOHO NUBUCK','A159',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3243,'TAEKWANG',30,'NIKE',1,'6JB','PINK FOAM','R-231 M','TMTK0272025101704','PINK','SOHO NUBUCK','A160',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3244,'PCN G8',59,'NIKE',1,'6FT','PINK BLAST (FLUORESCENCE)','AR-185 HG','TSPG0212025102001','PINK','GENERIC PU COATED LEATHER','A1314',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3245,'FENGTAY (NORTH)',9,'NIKE',1,'01X','PHANTOM','AR-144','TMFT0082025101401','WHITE','VIRGIN HYDRO PU LEATHER','A315',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3246,'CHINGLUH',5,'NIKE',1,'4EV','GAME ROYAL','ESR-180 SK2 HG','TMCL0172025101701','44Z','(PM) GENERIC PU COATED','A378',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3247,'CHINGLUH',5,'NIKE',1,'0AV','OFF NOIR','DE-73','TMCL0172025102101','BLACK','(PM) GENERIC PU COATED','A379',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3248,'CHINGLUH',5,'NIKE',1,'01X','PHANTOM','DE-73','TMCL0172025102102','WHITE','(PM) GENERIC PU COATED','A380',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3249,'LONGRICH',41,'UA',5,'700','PALE LEMON','DE-43 M','TMLR0262025121109','YELLOW','ACTION PU COATED LEATHER','A384',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25','2026-05-19 03:12:26'),
(3250,'TSH',34,'ADIDAS',3,'AJ7B','OLIVE TWO','DE-7 SM','SCOTDIC','3MR','PU COATED LEATHER (MAP ACTION LEATHER)','A866',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3251,'TAEKWANG',30,'NIKE',1,'12J','SUMMIT WHITE','AR-172','TMTK0272025111001','WHITE','(PM) GENERIC PU COATED','A162','2025-11-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25','2026-05-19 03:12:25'),
(3252,'SHOETOWN',28,'NIKE',1,'44B','MIDNIGHT NAVY','R-53 SM','TMSL0432025102701','BLACK','GENERIC PU COATED LEATHER','A1316',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3253,'SHOETOWN',28,'NIKE',1,'4LC','SQUADRON BLUE','R-53 SM','TMSL0432025102702','BLACK','GENERIC PU COATED LEATHER','A1317',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3254,'NIKOMAS IY',18,'NIKE',1,'09G','GREY MIST','R-131 M','TMNS0202025102901','WHITE','VIRGIN PU','A1318',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3255,'YOUNG TREE SOLO',46,'UA',5,'361','COMET GREEN','DE-172 SM','TSYT0022025110405','4AU','ACTION PU COATED LEATHER','A367','2025-05-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25','2026-05-19 03:12:25'),
(3256,'YOUNG TREE SOLO',46,'UA',5,'647','PRIME PINK','AR-191 M','TMYT0022025103101','PINK','ACTION PU COATED LEATHER','A356',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3257,'YOUNG TREE SOLO',46,'UA',5,'279','STONE','AR-191 M','TMYT0022025103102','WHITE','ACTION PU COATED LEATHER','A357',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3258,'YOUNG TREE SOLO',46,'UA',5,'110','SUMMIT WHITE','AR-191 M','TMYT0022025103103','WHITE','ACTION PU COATED LEATHER','A358',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3259,'YOUNG TREE SOLO',46,'UA',5,'430','AEGEAN BLUE','AR-191 M','TSYT0022025103101','44Z','ACTION PU COATED LEATHER','A359',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3260,'YOUNG TREE SOLO',46,'UA',5,'997','BLACKOUT NAVY','AR-191 M','TSYT0022025103102','BLACK','ACTION PU COATED LEATHER','A360',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3261,'YOUNG TREE SOLO',46,'UA',5,'016','ANTHRACITE','AR-191 M','TSYT0022025103103','BLACK','ACTION PU COATED LEATHER','A361',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3262,'YOUNG TREE SOLO',46,'UA',5,'075','BASEBALL GRAY','DE-172 SM','TSYT0022025110406','WHITE','ACTION PU COATED LEATHER','A368','2025-05-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25','2026-05-19 03:12:25'),
(3263,'PANARUB',19,'ADIDAS',3,'AJ77','KHAKI TWO','AR-201','SCOTDIC','WHITE','SOFT PU COATED LEATHER (MAP SOFT PU)','A867','2025-05-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3264,'YOUNG TREE SOLO',46,'UA',5,'932','ZEPPELIN YELLOW','DE-172 SM','TSYT0022025110401','YELLOW','ACTION PU COATED LEATHER','A363','2025-05-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3265,'YOUNG TREE SOLO',46,'UA',5,'110','SUMMIT WHITE','DE-172 SM','TSYT0022025110402','WHITE','ACTION PU COATED LEATHER','A364','2025-05-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3266,'YOUNG TREE SOLO',46,'UA',5,'279','STONE','DE-172 SM','TSYT0022025110403','WHITE','ACTION PU COATED LEATHER','A365','2025-05-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3267,'YOUNG TREE SOLO',46,'UA',5,'860','DARK ORANGE','DE-172 SM','TSYT0022025110404','RED','ACTION PU COATED LEATHER','A366','2025-05-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3268,'KMK',15,'NIKE',1,'4PS','CELESTINE BLUE','AR-144 M','TMKM0012025110601','LIGHT BLUE','VIRGIN HYDRO PU LEATHER','A236','2025-07-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3269,'SCI',32,'NIKE',1,'88U','LT MADDER ROOT (FLUORESCENT)','AW-44 SG','TMSC0062025103101','PINK','VIRGIN HYDRO PU LEATHER','A1319','2025-07-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3270,'NIKOMAS IY',18,'NIKE',1,'3KF','ARCTIC GREEN','R-131 M','TSNS0202025110601','WHITE','VIRGIN HYDRO PU','A1320','2025-07-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3271,'NIKOMAS IY',18,'NIKE',1,'3CH','ENERGY','R-131 M','TSNS0202025110602','3GU','VIRGIN HYDRO PU','A1321','2025-07-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3272,'POUYUEN',24,'NIKE',1,'0AH','DK SMOKE GREY','AR-194 M','TSPY0282025110601','BLACK','VIRGIN HYDRO PU','A1322','2025-07-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3273,'CHANGSHIN RJ',4,'NIKE',1,'13B','CHALK','AR-138 M','TMCS0052025110701','WHITE','VIRGIN HYDRO PU LEATHER','A419','2025-10-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3274,'KMK',15,'NIKE',1,'3PX','SPIRAL SAGE','AR-144 M','TMKM0012025110701','33R','VIRGIN HYDRO PU LEATHER','A237','2025-10-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3275,'YOUNG TREE SOLO',46,'UA',5,'246','KONA BROWN','DE-172 SM','TSYT0022025110701','BLACK','VIR SOFT PU COATED LEATHER','A369','2025-10-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3276,'YOUNG TREE SOLO',46,'UA',5,'230','INCENSE BROWN','DE-172 SM','TSYT0022025111001','BLACK','ACTION PU COATED LEATHER','A370','2025-11-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3277,'YOUNG TREE SOLO',46,'UA',5,'008','ULTIMATE BLACK','DE-172','TSYT0022025111002','BLACK','ACTION PU COATED LEATHER','A371','2025-01-11','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3278,'SAI',37,'NB',4,'138-81-07','TARO COLORO','AR-100 M','TMSD0472025103001','01V','HYDRO PU COATED LEATHER','A607',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3279,'NIKOMAS IY',18,'NIKE',1,'6FT','PINK BLAST  (FLUORESCENT)','AR-185 HG','TMNS0202025111401','PINK','GENERIC PU COATED','A1323',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3280,'NIKOMAS',17,'ADIDAS',3,'080A','SILVER MET','CPUG','TMNS0162025111901','WHITE','METAL LEATHER PATENT','A868',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3281,'ADIS',1,'NIKE',1,'47X','DEEP ROYAL BLUE','AR-73 M','TMAD0022025122401','44Z','VIRGIN PU','A582',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25','2026-05-19 03:12:26'),
(3282,'SHT',48,'NB',4,'036-90-02','NEW SEA SALT COLORO','AW-02','TSSH0012025112401','WHITE','HYDRO PU COATED LEATHER','A608',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3283,'NIKOMAS IY',18,'NIKE',1,'22Z','BAROQUE BROWN','AR-20 M','TMNS0202025112001','BROWN','VIRGIN PU','A1324',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3284,'FENGTAY (EAST)',7,'NIKE',1,'3HI','MINERAL SLATE','AR-144 M','TMFT0062025111901','33R','VIRGIN HYDRO PU AR-144','A316',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3285,'FENGTAY (EAST)',7,'NIKE',1,'0AE','VAST GREY','AR-144 M','TMFT0062025111902','WHITE','VIRGIN HYDRO PU AR-144','A317',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3286,'BIG',2,'ADIDAS',3,'A0TP','CREAM WHITE','DE-7 SM','TMBI0202025112801','WHITE','PU COATED LEATHER','A869','2025-01-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3287,'CHINGLUH',5,'NIKE',1,'01B','METALLIC SILVER','UM-T SM','TMCL0172025112801','WHITE','(PM) GENERIC PU COATED','A381','2025-01-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3288,'KMK',15,'NIKE',1,'01X','PHANTOM','AR-144 M','TMKM0012025120101','WHITE','VIRGIN HYDRO PU LEATHER','A238','2025-03-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3289,'WEALTH VAST CO. LTD',61,'NIKE',1,'01X','PHANTOM','R-53','TSSL0442025120201','WHITE','GENERIC PU COATED LEATHER','A1325','2025-03-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3290,'SHT',48,'NB',4,'036-90-02','NEW SEA SALT COLORO','AR-100','TMSH0012025120201','WHITE','HYDRO PU COATED LEATHER','A609','2025-03-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3291,'SCI',32,'NIKE',1,'53C','ICED LILAC','AR-144 M','TMSC0062025120801','PINK','VIRGIN HYDRO PU','A1326','2025-10-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3292,'ULTIMATE NOBLE',49,'NB',4,'008-26-26','PODIUM RED COLORO','AW-28 SG','TMMP0342025120401','RED','HYDRO PU COATED LEATHER','A610','2025-05-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3293,'ULTIMATE NOBLE',49,'NB',4,'072-45-16','OUTFIELD','AW-28 SG','TMMP0342025120402','33R','HYDRO PU COATED LEATHER','A611','2025-05-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3294,'SAI',37,'NB',4,'004-24-14','NB BURGANDY','AR-100 M','TMSD0472025120201','BROWN','HYDRO PU COATED LEATHER','A612','2025-03-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3295,'SMJ',36,'NIKE',1,'22U','DK VIOLET ORE','DE-7 SM','TMPT0142025120501','BROWN','(PM) GENERIC PU COATED','A1327','2025-08-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3296,'PCN G8',59,'NIKE',1,'13B','CHALK','AR-196M','TSPG0212025121101','WHITE','GENERIC PU COATED LEATHER','A1328','2025-11-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3297,'CHINGLUH',5,'NIKE',1,'10J','LT OREWOOD BRN','DE-73 SM','TMCL0172025120401','WHITE','(PM) GENERIC PU COATED','A382','2025-08-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3298,'CHINGLUH',5,'NIKE',1,'3MJ','LIGHT MENTA','DE-73 SM','TMCL0172025120402','4AU','(PM) GENERIC PU COATED','A383','2025-08-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3299,'NIKOMAS',17,'ADIDAS',3,'A3NF','IRON MET (METALLIC)','CPUG','TMNS0162025122301','WHITE','METAL LEATHER PATENT','A878',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25','2026-05-19 03:12:26'),
(3300,'NIKOMAS',17,'ADIDAS',3,'AJ75','SILVER BLUE TINT','CPUG','TSNS0162026022502','WHITE','METAL LEATHER PATENT','A883','2026-02-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25','2026-05-19 03:12:26'),
(3301,'NIKOMAS',17,'ADIDAS',3,'AJ7M','SEMI FROZEN AQUA','CPUG','TSNS0162026022501','4AU','METAL LEATHER PATENT','A882','2026-02-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25','2026-05-19 03:12:26'),
(3302,'LONGRICH',41,'UA',5,'025','CASTLEROCK','DE-43 M','TMLR0262025120501','GREY','ACTION PU COATED LEATHER','A372','2025-12-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3303,'LONGRICH',41,'UA',5,'430','AEGEAN BLUE','DE-43 M','TMLR0262025120502','44Z','ACTION PU COATED LEATHER','A373','2025-12-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3304,'LONGRICH',41,'UA',5,'408','ACADEMY','DE-43 M','TMLR0262025120503','BLACK','ACTION PU COATED LEATHER','A374','2025-12-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3305,'LONGRICH',41,'UA',5,'706','ANTHEM RED','DE-43 M','TMLR0262025121101','RED','ACTION PU COATED LEATHER','A375','2025-12-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3306,'LONGRICH',41,'UA',5,'016','ANTHRACITE','DE-43 M','TMLR0262025121102','BLACK','ACTION PU COATED LEATHER','A376','2025-12-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3307,'LONGRICH',41,'UA',5,'791','AQUA FLOAT','DE-43 M','TMLR0262025121103','4AU','ACTION PU COATED LEATHER','A377','2025-12-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3308,'LONGRICH',41,'UA',5,'001','BLACK','DE-43 M','TMLR0262025121104/UT BLACK','BLACK','ACTION PU COATED LEATHER','A378','2025-12-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3309,'LONGRICH',41,'UA',5,'476','BLUE FLOAT','DE-43 M','TMLR0262025121105','44Z','ACTION PU COATED LEATHER','A379','2025-12-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3310,'LONGRICH',41,'UA',5,'394','GREEN CITRINE','DE-43 M','TMLR0262025121106','71R','ACTION PU COATED LEATHER','A380','2025-12-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:25',NULL),
(3311,'LONGRICH',41,'UA',5,'361','NEO TURQUOISE','DE-43 M','TMLR0262025121108','4AU','ACTION PU COATED LEATHER','A381','2025-12-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3312,'ULTIMATE NOBLE',16,'NB',4,'038-75-26','LIGHT MARS YELLOW','AW-28 SG','TMMP0332025121001','YELLOW','HYDRO PU COATED LEATHER','A613','2025-12-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3313,'FENGTAY (EAST)',7,'NIKE',1,'0AN','GREY FOG','AR-144 M','TMFT0062025121101','GREY','VIRGIN HYDRO PU AR-144','A318',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3314,'DWI PRIMA SENTOSA',45,'UA',5,'034','BLUE FOG','AR-191 M','TMDW0012025121501','GREY','VIR SOFT PU COATED','A382',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3315,'LONGRICH',41,'UA',5,'014','HALO GRAY','DE-43 M','TMLR0262025121107','WHITE','ACTION PU COATED LEATHER','A383',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3316,'LONGRICH',41,'UA',5,'603','POSH PINK','DE-43 M','TMLR0262025121110','PINK','ACTION PU COATED LEATHER','A385',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3317,'LONGRICH',41,'UA',5,'647','PRIME PINK','DE-43 M','TMLR0262025121111','PINK','ACTION PU COATED LEATHER','A386',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3318,'LONGRICH',41,'UA',5,'429','SPACKLE BLUE','DE-43 M','TMLR0262025121112','WHITE','ACTION PU COATED LEATHER','A387',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3319,'LONGRICH',41,'UA',5,'024','TITAN GRAY','DE-43 M','TMLR0262025120504','BLACK','ACTION PU COATED LEATHER','A388',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3320,'LONGRICH',41,'UA',5,'637','PINK FRENZY','DE-43 M','TMLR0262025120505','6DX','ACTION PU COATED LEATHER','A389',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3321,'CHINGLUH',5,'NIKE',1,'45F','DK POWDER BLUE','R-8 M','TMCL0172025121001','4JE','VIRGIN HYDRO PU LEATHER','A384',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3322,'SCI',32,'NIKE',1,'01X','PHANTOM','AR-144 M','TMSC0062025121501','WHITE','VIRGIN HYDRO PU','A1329',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3323,'SCI',32,'NIKE',1,'45B','OBSIDIAN','AR-167 DM','TMSC0062025121502','BLACK','(PM) GENERIC PU COATED','A1330',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3324,'SHOETOWN',28,'NIKE',1,'6FX','TRACK FLUORESCENT','R-53 SM','TMSL0432025121601','RED','GENERIC PU COATED LEATHER','A1331',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3325,'SHOETOWN',28,'NIKE',1,'65N','UNIVERSITY RED FLUORESCENT','CPUG','TMSL0432025121602','WHITE','LS PATENT LEATHER','A1332',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3326,'SHT',48,'NB',4,'115-38-04','NEW SHADOW BLUE','AR-100 M','TMSH0012025121601','4MD','HYDRO PU COATED LEATHER','A614',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3327,'GLOSTAR (ADS)',11,'ADIDAS',3,'08F0','LIGTH BROWN','DE-7 SM','TMGS0072025121501','01V','SOFT PU','A873',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3328,'GLOSTAR (ADS)',11,'ADIDAS',3,'AJ3B','KHAKI SIX','DE-7 SM','TMGS0072025121502','3MR','SOFT PU','A874',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3329,'GLOSTAR (ADS)',11,'ADIDAS',3,'AECV','WONDER MAUVE','CPUG','TMGS0072025121503','PINK','BABY SOFT PATENT LEATHER','A875',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3330,'SHT',48,'NB',4,'022-30-08','BURNT TOAST COLORO','AR-100 M','FOLLOW COLORO','BROWN','HYDRO PU COATED LEATHER','A615',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3331,'ADIS',1,'NIKE',1,'14A','OFF WHITE','AR-169 M','TMAD0022025121602','WHITE','VIRGIN HYDRO PU LEATHER','A580',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3332,'ADIS',1,'NIKE',1,'14A','OFF WHITE','AR-107 M','TMAD0022025121601','WHITE','VIRGIN HYDRO PU LEATHER','A581',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3333,'CHINGLUH',5,'NIKE',1,'64M','VARSITY RED','R-53 SM','TMCL0172025121502','WHITE','GENERIC PU COATED','A385',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3334,'SHT',48,'NB',4,'043-90-14','DAW GLOW COLORO','AR-100 M','FOLLOW COLORO','WHITE','HYDRO PU COATED LEATHER','A616',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3335,'SHT',48,'NB',4,'116-85-09','OXYGEN COLORO','AR-100 M','FOLLOW COLORO','WHITE','HYDRO PU COATED LEATHER','A617',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3336,'SHT',48,'NB',4,'127-48-17','RAINSHADOW COLORO','AR-100 M','FOLLOW COLORO','49D','HYDRO PU COATED LEATHER','A618',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3337,'SHT',48,'NB',4,'111-59-06','LIGHT SHADOW BLUE','AR-100 M','FOLLOW COLORO','LIGHT BLUE','HYDRO PU COATED LEATHER','A619',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3338,'CHINGLUH',5,'NIKE',1,'43K','TRUE BLUE','R-53 M','TMCL0172025121501','WHITE','GENERIC PU COATED','A386',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3339,'CHINGLUH',5,'NIKE',1,'6JB','PINK FOAM','DE-73 SM','TMCL0172025121901','WHITE','(PM) GENERIC PU COATED','A387',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3340,'CHINGLUH',5,'NIKE',1,'0AV','OFF NOIR','DENIM-21 M','TMCL0172025121902','WHITE','(PM) GENERIC PU COATED','A388',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3341,'CHINGLUH',5,'NIKE',1,'6KG','SWEET BEET','DENIM-21 M','TMCL0172025121903','WHITE','(PM) GENERIC PU COATED','A389',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3342,'SHT',48,'NB',4,'156-27-20','RED VELVET','AR-100 M','FOLLOW COLORO','6DX','HYDRO PU COATED LEATHER','A620',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3343,'SHT',48,'NB',4,'022-79-25','LIGHT FADED POPPY','AR-100 M','FOLLOW COLORO','2CT','HYDRO PU COATED LEATHER','A621',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3344,'TSH',34,'ADIDAS',3,'A0TP','CREAM WHITE','DE-7','TMTS0012025122201','WHITE','PU COATED LEATHER (MAP ACTION LEATHER)','A876',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3345,'NIKOMAS',17,'ADIDAS',3,'AAG4','HI-RES BLUE','DE-7 SM','TMNS0162025122301','44Z','SOFT PU','A877',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3346,'FENGTAY (NORTH)',9,'NIKE',1,'10J','LT OREWOOD BRN','AR-20 M','TMFT0082025122201','WHITE','(PM) GENERIC PU COATED','A319',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3347,'POUYUEN',24,'NIKE',1,'13B','CHALK','AR-169 M','TSPY0282025122401','WHITE','GENERIC PU COATED','A1333',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3348,'TAEKWANG',30,'NIKE',1,'10J','LT OREWOOD BRN','R-8 M','TMTK0272025122901','WHITE','(PM) GENERIC PU COATED','A163',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3349,'CHINGLUH',5,'NIKE',1,'65N','UNIVERSITY RED (FLUORESCENT)','R-53 SM','TMCL0172025122901','RED','GENERIC PU COATED','A390',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3350,'SAI',37,'NB',4,'202 C','CARDINAL PANTONE','AR-100 M','TMSD0472025123002','RED','HYDRO PU COATED LEATHER','A623',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3351,'SHT',48,'NB',4,'118-69-22','LIGHT ACRYLIC BLUE','AR-100 M','FOLLOW COLORO','LIGHT BLUE','HYDRO PU COATED LEATHER','A624',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3352,'METRO NB',16,'NB',4,'124-91-00','NB 103 WHITE','DE-41','TMMP0332025123001','WHITE','HYDRO PU COATED LEATHER','M101',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3353,'METRO NB',16,'NB',4,'020-25-10','PUMPERNICKLE','R-78','TMMP0332025123002','BROWN','HYDRO PU COATED LEATHER','M102',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3354,'ULTIMATE NOBLE',49,'NB',4,'121-34-10','NEW VINTAGE INDIGO','AW-28 SG','TMMP0342025123101','4MD','HYDRO PU COATED LEATHER','A625','2026-05-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3355,'SHOETOWN',28,'NIKE',1,'6KD','DESSERT SAND','R-53 SM','TMSL0432026010501','PINK','GENERIC PU COATED LEATHER','A1334','2026-05-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3356,'TAEKWANG',30,'NIKE',1,'58V','BLEACHEAD LILAC','UMT M','TMTK0272026010501','WHITE','LAMPER LEATHER','A164','2026-07-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3357,'TAEKWANG',30,'NIKE',1,'29E','CREAM II','UMT M','TMTK0272026010502','WHITE','LAMPER LEATHER','A165','2026-07-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3358,'TAEKWANG',30,'NIKE',1,'2FE','PARACHUTE BEIGE','UMT M','TMTK0272026010503','WHITE','LAMPER LEATHER','A166','2026-07-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3359,'FENGTAY (NORTH)',30,'NIKE',1,'6KG','SWEET BEET','DENIM-21 M','TMTK0272026010503','6DX','(PM) GENERIC PU COATED','A320','2026-07-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3360,'FENGTAY (NORTH)',9,'NIKE',1,'14A','OFF WHITE','AR-161 M','TMFT0082026010502','WHITE','(PM) GENERIC PU COATED','A321','2026-07-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3361,'DPS',45,'UA',5,'016','ANTHRACITE','AR-191 M','TMDW0012026010703','BLACK','VIR SOFT ACTION LEATHER','A390','2026-08-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3362,'DWI PRIMA SENTOSA',45,'UA',5,'279','STONE','AR-191 M','TMDW0012026010701','WHITE','VIR SOFT ACTION LEATHER','A391','2026-08-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3363,'DWI PRIMA SENTOSA',45,'UA',5,'390','MARINE OD GREEN','AR-191 M','TMDW0012026010601','BLACK','VIR SOFT ACTION LEATHER','A392','2026-08-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3364,'SMJ',36,'NIKE',1,'05I','COLEGE GREY','DE-7 SM','TMPT0142026010901','WHITE','(PM) GENERIC PU COATED','A1335','2026-09-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3365,'SHOETOWN',28,'NIKE',1,'01X','PHANTOM','AR-167 M','TMSL0432026010901','WHITE','GENERIC PU COATED','A1336','2026-12-01','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3366,'YMUV',39,'UA',5,'430','MISTY SKY BLUE','DE-43 M','FOLLOW CSI UA','LIGHT BLUE','ACTION PU COATED LEATHER','A395',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3367,'YMUV',39,'UA',5,'381','PRISM GREEN','DE-43 M','FOLLOW CSI UA','4AU','ACTION PU COATED LEATHER','A396',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3368,'LONGRICH',42,'UA',5,'389','SEANSPRAY','DE-43 M','FOLLOW CSI UA','34A','ACTION PU COATED LEATHER','A397',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3369,'LONGRICH',42,'UA',5,'421','KINECT BLUE','DE-43 M','FOLLOW CSI UA','4MD','ACTION PU COATED LEATHER','A398',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3370,'LONGRICH',42,'UA',5,'511','SUGAR FLUM','DE-43 M','FOLLOW CSI UA','PURPLE','ACTION PU COATED LEATHER','A399',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3371,'LONGRICH',42,'UA',5,'400','TEAM ROYAL','DE-43 M','FOLLOW CSI UA','44Z','ACTION PU COATED LEATHER','A400',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3372,'LONGRICH',45,'UA',5,'044','DOWNPOUR GRAY','DE-43 M','TMDW0012026011701','BLACK','ACTION PU COATED LEATHER','A401',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3373,'YMUV',39,'UA',5,'1066C','METALLIC PINK MIRAGE','DE-43 M','FOLLOW SAMPLE','PINK','ACTION PU COATED LEATHER','A402',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3374,'VICTORY',31,'NIKE',1,'6JB','PINK FOAM','DE-73 SM','TMVC0052026012001','WHITE','(PM) GENERIC PU COATED','A392',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3375,'CHINGLUH',5,'NIKE',1,'0AV','OFF NOIR','AR-20 M','TMCL0172026011401','BLACK','(PM) GENERIC PU COATED','A393',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3376,'NIKOMAS IY',18,'NIKE',1,'07G','LIGHT BONE','R-8 M','TMNS0202026012101','WHITE','ECO TECH COMFORT','A1337',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3377,'NIKOMAS IY',18,'NIKE',1,'45B','OBSIDIAN','R-8 M','TMNS0202026012102','BLACK','ECO TECH COMFORT','A1338',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3378,'FENGTAY (NORTH)',9,'NIKE',1,'0AH','DK SMOKE GREY','AR-20 M','TMFT0082026012001','BLACK','(PM) GENERIC PU COATED','A322',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3379,'FENGTAY (WEST)',7,'NIKE',1,'0AH','DK SMOKE GREY','R-8 M','TMFT0062026011901','BLACK','(PM) GENERIC PU COATED','A323',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3380,'FENGTAY (WEST)',7,'NIKE',1,'06L','GHOST','R-8 M','TMFT0062026011902','WHITE','(PM) GENERIC PU COATED','A324',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3381,'BIG',2,'ADIDAS',3,'AE6S','WONDER WHITE','DE-7 SM','TSBI0202026012002','WHITE','PU COATED LEATHER','A879',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3382,'BIG',2,'ADIDAS',3,'08S1','OFF WHITE','DE-7 SM','TSBI0202026012001','WHITE','PU COATED LEATHER','A880',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3383,'TAEKWANG',30,'NIKE',1,'0AJ','SMOKE GREY','R-131 M','TMTK0272026011201','BLACK','(PM) GENERIC PU COATED','A167',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3384,'FENGTAY (WEST)',8,'NIKE',1,'05Q','FOOTBALL GREY','R-8 M','TMFT0072026012201','WHITE','(PM) GENERIC PU COATED','A325',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3385,'NIKOMAS IY',18,'NIKE',1,'4QM','BLUE BEYOND','S-953 NEVADA','TMNS0202026012103','LIGHT BLUE','GENERIC PU COATED','A1339',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3386,'SHT',48,'NB',4,'142-43-00','MAGNET COLORO','AR-100 M','FOLLOW COLORO','BLACK','HYDRO PU COATED LEATHER','A627',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3387,'SHOETOWN',28,'NIKE',1,'01X','PHANTOM','R-53 SM','TMSL0432026012301','WHITE','GENERIC PU COATED','A1340',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3388,'SHOETOWN',28,'NIKE',1,'4AH','AURA','AR-167 M','TMSL0432026012601','WHITE','GENERIC PU COATED','A1341',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3389,'CHINGLUH',5,'NIKE',1,'43K','TRUE BLUE','R-51 SM','TMCL0172026012301','BLUE','(PM) GENERIC PU COATED','A394',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3390,'CHINGLUH',5,'NIKE',1,'68X','VIVID PINK','R-51 SM','TMCL0172026012302','RED','(PM) GENERIC PU COATED','A395',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3391,'TAEKWANG',30,'NIKE',1,'0AI','IRON GREY','R-131 M','TMTK0272026011202','GREY','(PM) GENERIC PU COATED','A168',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3392,'DWI PRIMA SENTOSA',45,'UA',5,'502','OLIVE TINT','AR-191 M','FOLLOW CSI UA','WHITE','VIR SOFT ACTION LEATHER','A403',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3393,'TAEKWANG',30,'NIKE',1,'04Z','PURE PLATINUM','DE-7 SM','TMTK0272026012901','WHITE','(PM) GENERIC PU COATED','A169',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3394,'FENGTAY (WEST)',7,'NIKE',1,'11K','SAIL','R-8 M','TMFT0062026012701','WHITE','(PM) GENERIC PU COATED','A326',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3395,'CHINGLUH',31,'NIKE',1,'44B','MIDNIGHT NAVY','AR-20 M','TMVC0052026012801','BLACK','(PM) GENERIC PU COATED','A396',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3396,'YOUNG TREE SOLO',46,'UA',5,'600','BASHFUL PINK','AR-191 M','FOLLOW CSI UA','WHITE','ACTION PU COATED LEATHER','A404','2026-04-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3397,'YOUNG TREE SOLO',46,'UA',5,'276','GRAYSTONE','AR-191 M','FOLLOW CSI UA','01V','ACTION PU COATED LEATHER','A405','2026-04-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3398,'YOUNG TREE SOLO',46,'UA',5,'870','ORANGE BLOC','AR-191 M','FOLLOW CSI UA','2CT','ACTION PU COATED LEATHER','A406','2026-04-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3399,'TAEKWANG',30,'NIKE',1,'04Z','ORANGE BLOC','R-131 M','TMTK0272026020201','WHITE','(PM) GENERIC PU COATED','A170','2026-04-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3400,'VICTORY',31,'NIKE',1,'11K','SAIL','AR-20 M','TMVC0052026020301','WHITE','(PM) GENERIC PU COATED','A397','2026-04-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3401,'KMK',15,'NIKE',1,'06B','COOL GREY','AR-144 M','TMKM0012026020301','GREY','VIRGIN HYDRO PU LEATHER','A239','2026-04-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3402,'YOUNG TREE SOLO',46,'UA',5,'603','POSH PINK','AR-191 M','FOLLOW CSI UA','80S','ACTION PU COATED LEATHER','A407','2026-05-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3403,'YOUNG TREE SOLO',46,'UA',5,'013','ASH GRAY','AR-191 M','FOLLOW CSI UA','LIGHT BLUE','ACTION PU COATED LEATHER','A408','2026-05-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3404,'NIKOMAS IY',18,'NIKE',1,'06B','COOL GREY','CPUG','TMNS0202026020401','GREY','LACCATTO PATENT LEATHER','A1342','2026-05-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3405,'TAEKWANG',30,'NIKE',1,'07G','LIGHT BONE','R-262','TMTK0272026020402','WHITE','(PM) GENERIC PU COATED','A171','2026-02-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3406,'METRO NB',16,'NB',4,'127-83-02','FRESH AIR COLORO','AR-100 M','TSMP0332026020501','01V','HYDRO PU COATED LEATHER','M103','2026-06-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3407,'TAEKWANG',30,'NIKE',1,'01V','WOLF GREY','R-131 M','TMTK0272026020401','01V','(PM) GENERIC PU COATED','A172','2026-06-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3408,'NIKOMAS IY',18,'NIKE',1,'60I','CHINA ROSE (FLUORESCENT)','S-953 NEVADA','TSNS0202026020601','6DX','GENERIC PU COATED','A1343','2026-06-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3409,'NIKOMAS IY',18,'NIKE',1,'01V','WOLF GREY','R-131 M','TSNS0202026020602','01V','VIRGIN HYDRO PU','A1344','2026-06-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3410,'NIKOMAS IY',18,'NIKE',1,'4ET','BLUE ECLIPSE','AR-20 M','TSNS0202026020603','BLACK','VIRGIN PU','A1345','2026-06-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3411,'BIG',2,'ADIDAS',3,'A3N9','BRANCH','DE-7 SM','TSBI0202026022602','BLACK','PU COATED LEATHER','A885','2026-02-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26','2026-05-19 03:12:26'),
(3412,'FENGTAY (WEST)',7,'NIKE',1,'43Z','ALUMINUM','R-8 M','TMFT0062026020501','WHITE','(PM) GENERIC PU COATED','A327','2026-09-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3413,'SAI',37,'NB',4,'006-48-07','PEBBLE COLORO','AR-100 M','TMSD0472026020601','PINK','HYDRO PU COATED LEATHER','A628','2026-09-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3414,'SAI',37,'NB',4,'008-35-06','FAST TRACK','AR-100 M','TMSD0472026020602','BROWN','HYDRO PU COATED LEATHER','A629','2026-09-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3415,'VICTORY',31,'NIKE',1,'4EC','LT PHOTO BLUE','AR-20 M','TMVC0052026020901','BLUE','(PM) GENERIC PU COATED','A398','2026-11-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3416,'VICTORY',31,'NIKE',1,'01V','WOLF GREY','AR-20 M','TMVC0052026020902','01V','(PM) GENERIC PU COATED','A399','2026-11-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3417,'VICTORY',31,'NIKE',1,'2DH','MEDIUM OLIVE','AR-20 M','TMVC0052026020903','3MR','(PM) GENERIC PU COATED','A400','2026-11-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3418,'VICTORY',31,'NIKE',1,'25Q','NEUTRAL OLIVE','AR-20 M','TMVC0052026020904','3MR','(PM) GENERIC PU COATED','A401','2026-11-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3419,'FENGTAY',7,'NIKE',1,'07W','GEYSER GREY','DE-73 SM','TMFT0062026021001','01V','(PM) GENERIC PU COATED','A328','2026-11-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3420,'LONGRICH UA',41,'UA',5,'448','BLUE WIND','DE-43 M','TSLR0262026020901','LIGHT BLUE','ACTION PU COATED LEATHER','A409','2026-11-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3421,'VICTORY',31,'NIKE',1,'0AP','PLATINUM TINT','AR-20 M','TMVC0052026021001','WHITE','(PM) GENERIC PU COATED','A402','2026-11-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3422,'VICTORY',31,'NIKE',1,'3LU','MINT FOAM','AR-20 M','TMVC0052026021002','WHITE','(PM) GENERIC PU COATED','A403','2026-11-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3423,'METRO NB',16,'NB',4,'19-4128 TCX','NEW TITAN','R-78 M','FOLLOW SAMPLE','BLACK','HYDRO PU COATED LEATHER','M104','2026-12-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3424,'LONGRICH UA',41,'UA',5,'069','TITANIUM','DE-43 M','TMLR0262026021101','01V','ACTION PU COATED LEATHER','A410','2026-12-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3425,'LONGRICH UA',41,'UA',5,'709','CLAY GREEN','DE-43 M','TMLR0262026021103','GREY','ACTION PU COATED LEATHER','A411','2026-12-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3426,'CHANGSHIN RJ',4,'NIKE',1,'0AE','VAST GREY','DE-90 M','TMCS0052026021101','GREY','(PM) GENERIC PU COATED','A420','2026-12-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3427,'CHANGSHIN RJ',4,'NIKE',1,'2EU','MOON PARTICLE','AR-161 M',NULL,'WHITE','(PM) GENERIC PU COATED','A421','2026-12-02','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3428,'SCI',32,'NIKE',1,'06B','COOL GREY','AR-144 M','TMSC0062026021301','GREY','VIRGIN HYDRO PU LEATHER','A1346',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3429,'SHOETOWN',28,'NIKE',1,'0AJ','SMOKE GREY','AR-167 M','TMSL0432026021801','GREY','GENERIC PU COATED','A1347',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3430,'VICTORY',31,'NIKE',1,'6LC','PICANTE FOAM','AR-20 M','TMVC0052026022001','WHITE','(PM) GENERIC PU COATED','A404',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3431,'CHANGSHIN RJ',4,'NIKE',1,'0AL','LT SMOKE GREY','R-131 M','TMCS0052026022301','WHITE','(PM) GENERIC PU COATED','A422',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3432,'CHANGSHIN',3,'NIKE',1,'2EU','MOON PARTICLE','R-8 M','TSCS0042026022401','WHITE','ECO TECH COMFORT','A423',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3433,'CHANGSHIN',3,'NIKE',1,'0BL','PENCIL POINT','R-8 M','TSCS0042026022402','GREY','ECO TECH COMFORT','A424',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3434,'ADIS',1,'NIKE',1,'06F','ANTHRACITE','R-102 M','TMAD0022026022301','BLACK','GENERIC PU COATED LEATHER','A583',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3435,'ADIS',1,'NIKE',1,'06B','COOL GREY','R-102 M','TMAD0022026022302','GREY','GENERIC PU COATED LEATHER','A584',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3436,'NIKOMAS IY',18,'NIKE',1,'05I','COLLEGE GREY','R-8 M','TMNS0202026022401','WHITE','ECO TECH COMFORT','A1348',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3437,'VICTORY',31,'NIKE',1,'43Z','ALUMINUM','DE-73 SM','TMVC0052026022401','WHITE','(PM) GENERIC PU COATED','A405',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3438,'VICTORY',31,'NIKE',1,'41S','COLLEGE NAVY','R-53 SM','TMVC0052026022101','WHITE','GENERIC PU COATED LEATHER','A406',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3439,'VICTORY',31,'NIKE',1,'03A','TECH GREY','R-53 SM','TMVC0052026022102','WHITE','GENERIC PU COATED LEATHER','A407',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3440,'LONGRICH UA',41,'UA',5,'808','OUTRAGEOUS ORANGE','DE-43 M','TMLR0262026021102','80S','ACTION PU COATED LEATHER','A412',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3441,'NIKOMAS IY',18,'NIKE',1,'29J','PEARL WHITE','S-953 NEVADA','TMNS0202026022601','WHITE','GENERIC PU COATED','A1349',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3442,'BIG',2,'ADIDAS',3,'48F0','MAROON','DE-7 SM','TSBI0202026022601','PURPLE','PU COATED LEATHER','A884','2026-02-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3443,'TAH SUNG HUNG',34,'ADIDAS',3,'AEX5','SHADOW BROWN','DE-7 SM','SCOTDIC','BROWN','PU COATED LEATHER','A886','2026-03-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3444,'NIKOMAS',17,'ADIDAS',3,'AJ6X','SILVER BLUE','DE-7 SM','SCOTDIC','LIGHT BLUE','PU COATED LEATHER','A887','2026-03-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3445,'BIG',2,'ADIDAS',3,'AA2S','GREY TWO','DE-7 SM','TSBI0202026030501','WHITE','SOFT PU COATED LEATHER','A888','2026-06-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3446,'BIG',2,'ADIDAS',3,'A0TP','CREAM WHITE','DE-7 SM','TSBI0202026030502','WHITE','SOFT PU COATED LEATHER','A889','2026-06-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3447,'PCN G8',24,'NIKE',1,'49R','VARSITY ROYAL','S-953 NEVADA','TSPY0212026031101','44Z','GENERIC PU COATED LEATHER','A1350','2026-12-03','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3448,'NIKOMAS',17,'ADIDAS',3,'080A','SILVER MET (METALIC)','CPUG','TMNS0162026031201','WHITE','BABY SOFT PATENT LEATHER','A890',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3449,'FENGTAY',7,'NIKE',1,'0AP','PLATINUM TINT','R-8 M','TMFT0062026031301','WHITE','(PM) GENERIC PU COATED','A330',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3450,'SHOETOWN',28,'NIKE',1,'14A','OFF WHITE','R-8 M','TSSL0432026031301','WHITE','VIRGIN HYDRO PU LEATHER','A1351',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3451,'GLOSTAR',11,'ADIDAS',3,'08S1','OFF WHITE','CPUG','TMGS0072026031801','WHITE','BABY SOFT PATENT LEATHER','A891',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3452,'ADIS',1,'NIKE',1,'0AN','GREY FOG','R-102 M','TMAD0022026031801','WHITE','GENERIC PU COATED LEATHER','A585',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3453,'ADIS',1,'NIKE',1,'21I','BROWN','R-102 M','TMAD0022026031802','BROWN','GENERIC PU COATED LEATHER','A586',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3454,'POUYUEN',59,'NIKE',1,'01V','WOLF GREY','AR-188 M','TSPG0282026031701','01V','VIRGIN HYDRO PU LEATHER','A1352',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3455,'METRO NB',16,'NB',4,'134-85-05','LILAC AIR','AR-100 M','FOLLOW COLORO','WHITE','ECO GREEN RECYCLED LEATHER','A630',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3456,'METRO NB',16,'NB',4,'154-72-07','TWINLIGHT HAZE','AR-100 M','FOLLOW COLORO','WHITE','ECO GREEN RECYCLED LEATHER','A631',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3457,'METRO NB',16,'NB',4,'115-52-06','ZINC BLUE','AR-100 M','FOLLOW COLORO','WHITE','ECO GREEN RECYCLED LEATHER','A632',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3458,'SHOETOWN',28,'NIKE',1,'41S','COLLEGE NAVY','R-53 SM','TMSL0432026040602','WHITE','GENERIC PU COATED LEATHER','A1353','2026-06-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3459,'SHOETOWN',28,'NIKE',1,'03A','TECH GREY','R-53','TMSL0432026040601','WHITE','GENERIC PU COATED LEATHER','A1354','2026-06-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3460,'FENGTAY',9,'NIKE',1,'0AI','IRON GREY','AR-144 M','TMFT0082026020501','BLACK','VIRGIN HYDRO PU LEATHER','A331','2026-06-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3461,'SAI',37,'NB',4,'025-62-04','LIGHT MUSHROOM','AR-100 M','FOLLOW COLORO','01V','HYDRO PU COATED LEATHER','A633','2026-07-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3462,'YMUV',39,'UA',5,'699','ASTEROID PINK','DE-43 M','FOLLOW CSI UA','6DX','ACTION PU COATED LEATHER','A413','2026-01-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3463,'YMUV',39,'UA',5,'481','FRESCO BLUE','DE-43 M','FOLLOW CSI UA','4AU','ACTION PU COATED LEATHER','A417','2026-01-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26','2026-05-19 03:12:26'),
(3464,'YMUV',39,'UA',5,'681','PINK MIRAGE','DE-43 M','FOLLOW CSI UA','PINK','ACTION PU COATED LEATHER','A415','2026-01-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3465,'YMUV',39,'UA',5,'598','BLITHE PINK (FLUORESCENT)','DE-43 M','FOLLOW CSI UA','PINK','ACTION PU COATED LEATHER','A416','2026-01-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3466,'YMUV',39,'UA',5,'417','TEAL VIBE','DE-43 M','FOLLOW CSI UA','BLUE','ACTION PU COATED LEATHER','A418','2026-01-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3467,'METRO NB',16,'NB',4,'020-25-10','PUMPERNICKLE','AW-28 SG','TMMP0332026033101','BROWN','HYDRO PU COATED LEATHER','A634','2026-01-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3468,'METRO NB',16,'NB',4,'043-89-00','REPLECTION','DE-90','TMMP0332026033102','WHITE','HYDRO PU COATED LEATHER','A635','2026-01-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3469,'METRO NB',48,'NB',4,'039-90-05','ANGORA COLORO','AR-100 M','TSSH0012026040603','WHITE','HYDRO PU COATED LEATHER','A636','2026-07-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3470,'METRO NB',16,'NB',4,'100-64-21','BLUE GAZE COLORO','AR-100 M','TSMP0332026040601','4JE','HYDRO PU COATED LEATHER','A637','2026-07-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3471,'METRO NB',48,'NB',4,'034-84-05','NEW LINEN COLORO','AR-100 M','TSSH0012026040602','WHITE','HYDRO PU COATED LEATHER','A638','2026-07-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3472,'METRO NB',48,'NB',4,'012-77-19','PINK LEMONADE COLORO','AR-100 M','TSSH0012026040601','80S','HYDRO PU COATED LEATHER','A639','2026-07-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3473,'SAI',37,'NB',4,'059-43-01','KELP','AR-100 M','FOLLOW COLORO','GREY/ WHITE','HYDRO PU COATED LEATHER','A640','2026-07-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3474,'FENGTAY TW',58,'NIKE',1,'06F','ANTHRACITE','R-8 M','TSFT0382026040701','BLACK','(PM) GENERIC PU COATED','A332','2026-07-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3475,'TAEKWANG',30,'NIKE',1,'6EY','ARCTIC PINK','R-8 M','TMTK0272026040601','PINK','(PM) GENERIC PU COATED','A173','2026-09-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3476,'TAEKWANG',30,'NIKE',1,'06L','GHOST','R-8 M','TMTK0272026040602','WHITE','(PM) GENERIC PU COATED','A174','2026-09-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3477,'POUYUEN',24,'NIKE',1,'41S','COLLEGE NAVY','R-53 SM','TMPY0282026040801','BLACK','GENERIC PU COATED','A1355','2026-09-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3478,'NIKOMAS IY',18,'NIKE',1,'11H','MUSLIN','R-8 M','TMNS0202026040901','WHITE','VIRGIN PU','A1356','2026-09-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3479,'CHANGSHIN',4,'NIKE',1,'80S','TOTAL ORANGE (FLUORESCENT)','R-231 M','TMCS0052026050503','WHITE','(PM) GENERIC PU COATED','A436','2026-06-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26','2026-05-19 03:12:27'),
(3480,'METRO NB',16,'NB',4,'061-83-02','SAGE FOG','AR-100 M','FOLLOW COLORO','WHITE','HYDRO PU COATED LEATHER','A642',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:26',NULL),
(3481,'METRO NB',16,'NB',4,'101-83-06','GLIDE','AR-100 M','FOLLOW COLORO','WHITE','HYDRO PU COATED LEATHER','A643',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3482,'METRO NB',16,'NB',4,'039-75-01','BOYLSTON GREY','AR-100 M','FOLLOW COLORO','01V','HYDRO PU COATED LEATHER','A644',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3483,'METRO NB',16,'NB',4,'008-80-10','NEW CRYSTALL PINK','AR-100 M','FOLLOW COLORO','PINK','HYDRO PU COATED LEATHER','A645',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3484,'METRO NB',16,'NB',4,'024-35-06','CORTADO','AR-100 M','FOLLOW COLORO','LIGHT BROWN','HYDRO PU COATED LEATHER','A646',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3485,'METRO NB',16,'NB',4,'019-29-05','NEW OFF ROAD','AR-100 M','FOLLOW COLORO','BROWN','HYDRO PU COATED LEATHER','A647',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3486,'METRO NB',16,'NB',4,'076-24-10','NORDIC GREEN','AR-100 M','FOLLOW COLORO','3AW','HYDRO PU COATED LEATHER','A648',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3487,'METRO NB',16,'NB',4,'005-29-22','BEACON HILL','AR-100 M','FOLLOW COLORO','RED','HYDRO PU COATED LEATHER','A649',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3488,'NIKOMAS',17,'ADIDAS',3,'A3MS','SHIFT BLUE','AR-196','SCOTDIC','belum di kasih backer  sama Mr.Xie','METAL SHIFT LEATHER','A892','2026-08-04','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3489,'DPS',45,'UA',5,'615','CORDOVA RED','AR-191','FOLLOW CSI UA','RED','VIR SOFT ACTION LEATHER','A419',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3490,'SHOETOWN',28,'NIKE',1,'6DL','GYM RED','DE-41','TMSL0432026041401','RED','GENERIC PU COATED LEATHER','A1357',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3491,'NIKOMAS',17,'ADIDAS',3,'AJ3C','KHAKI THREE','CPUG','TMNS0162026041401','01V','BABY SOFT PATENT LEATHER','A893',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3492,'NIKOMAS',17,'ADIDAS',3,'AEDS','SHADOW NAVY','CPUG','TMNS0162026041402','BLACK','BABY SOFT PATENT LEATHER','A894',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3493,'METRO NB',16,'NB',4,'045-36-09','WAKAME COLORO','AR-100 M','TMMP0332026041401','3MR','HYDRO PU COATED LEATHER','A650',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3494,'FENGTAY TW',58,'NIKE',1,'0AJ','SMOKE GREY','R-8 M','TSFT0382026041501','BLACK','VIRGIN PU','A333',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3495,'CHANGSHIN',3,'NIKE',1,'4PB','ASHEN SLATE','AR-144 M','TSCS0042026041401','GREY','VIRGIN HYDRO PU LEATHER','A426',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3496,'CHANGSHIN',4,'NIKE',1,'65N','UNIVERSITY RED (FLUORESCENT)','AR-144 M','TMCS0052026042202','RED','VIRGIN HYDRO PU LEATHER','A432','1912-05-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27','2026-05-19 03:12:27'),
(3497,'FENGTAY TW',58,'NIKE',1,'6GM','RUST PINK','R-8 M','TSFT0382026041502','PINK','(PM) GENERIC PU COATED','A334',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3498,'ADIS',1,'NIKE',1,'44B','MIDNIGHT NAVY','UM-16 SG','TMAD0022026041501','BLACK','VIRGIN PU','A587',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3499,'CHANGSHIN',4,'NIKE',1,'0AJ','SMOKE GREY','R-102 M','TMCS0052026041501','BLACK','ECO TECH COMFORT','A428',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3500,'NIKOMAS IY',18,'NIKE',1,'49R 1A','VARSITY ROYAL','S-953 NEVADA','TMNS0202026041301','44Z','GENERIC PU COATED','A1358',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3501,'YMUV',39,'UA',5,'692','GALA (METALLIC)','DE-43 M','FOLLOW CSI UA','RED','ACTION PU COATED LEATHER','A420',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3502,'YMUV',39,'UA',5,'307','METALLIC PINK LUNAR GREEN','DE-43 M','FOLLOW CSI UA','4AU','ACTION PU COATED LEATHER','A421',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3503,'SHOETOWN MUSTIKA',50,'NB',4,'000-64-00','COLORO TAILORED GREY NB','AW-02','FOLLOW COLORO','01V','HYDRO PU COATED LEATHER','A651',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3504,'CHANGSHIN',4,'NIKE',1,'0BB','PHOTON DUST','AR-138 M','TMCS0052026041601','WHITE','VIRGON HYDRO PU','A429',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3505,'CHANGSHIN',4,'NIKE',1,'04Z','PURE PLATINUM','AR-138 M','TMCS0052026041602','WHITE','VIRGON HYDRO PU','A430',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3506,'CHANGSHIN',4,'NIKE',1,'01V','WOLF GREY','AR-138 M','TMCS0052026041603','01V','VIRGON HYDRO PU','A431',NULL,'DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3507,'NIKOMAS IY',18,'NIKE',1,'86V','CAMPFIRE OARNGE','AR-185 HG','TMNS0202026042201','80S','GENERIC PU COATED','A1359','2026-04-22','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3508,'SCI',32,'NIKE',1,'74F','WHEAT','AR-144 M','TMSC0062026042001','2CT','VIRGIN HYDRO PU LEATHER','A1360','2026-04-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3509,'NIKOMAS IY',18,'NIKE',1,'2ET','SHADOW BROWN','AR-185 HG','TSNS0202026042201','BLACK','GENERIC PU COATED','A1361','2026-04-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3510,'VICTORY',31,'NIKE',1,'11K','SAIL','AR-161 M','TMVC0052026042101','WHITE','VIRGIN HYDRO PU LEATHER','A408','2026-04-23','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3511,'CHINGLUH',5,'NIKE',1,'03A','TECH GREY','R-53 SM','TMCL0172026042301','WHITE','GENERIC PU COATED','A409','2026-04-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3512,'TAEKWANG',30,'NIKE',1,'06F','ANTHRACITE','R-131 M','TMTK0272026042301','BLACK','(PM) GENERIC PU COATED','A175','2026-04-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3513,'NIKOMAS IY',18,'NIKE',1,'3HR','CARGO KHAKI','R-8 M','TSNS0202026042301','33R','ECO TECH COMFORT','A1362','2026-04-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3514,'POUYUEN',24,'NIKE',1,'10L','PALE IVORY','R-53 SM','TMPY0282026042401','WHITE','GENERIC PU COATED','A1363','2026-04-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3515,'CHANGSHIN',3,'NIKE',1,'0AL','LT SMOKE GREY','AR-144 M','TSCS0042026042701','GREY','VIRGIN HYDRO PU LEATHER','A433','2026-04-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3516,'NIKOMAS',17,'ADIDAS',3,'AE5S','AURORA COFFEE','DE-7 SM','SCOTDIC','BLACK','PU COATED LEATHER','A895','1912-09-12','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3517,'NIKOMAS IY',18,'NIKE',1,'64M','VARSITY RED','R-8 M','TMNS0202026042701','RED','VIRGIN PU','A1364','2026-04-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3518,'METRO NB',16,'NB',4,'043-89-00','REFLECTION','AR-100 M','TSMP0332026042401','WHITE','ECO GREEN RECYCLED LEATHER','A652','2026-04-27','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3519,'NIKOMAS IY',18,'NIKE',1,'01B','METALLIC SILVER','CPUG','TMNS0202026042702','WHITE','LACCATTO PATENT LEATHER','A1365','2026-04-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3520,'TAEKWANG',30,'NIKE',1,'65N','UNIVERSITY RED (FLUORESCENT)','AR-144 M','TMTK0272026042401','RED','VIRGIN HYDRO PU LEATHER','A176','2026-04-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3521,'METRO NB',16,'NB',4,'156-27-20','RED VELVET','AR-100 M','TSMP0332026042701','6DX','HYDRO PU COATED LEATHER','A653','2026-04-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3522,'CHINGLUH',5,'NIKE',1,'6DL','GYM RED','AR-64 M','TMCL0172026042401','RED','VIRGIN HYDRO PU LEATHER','A410','2026-04-28','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3523,'METRO NB',16,'NB',4,'036-90-02','NEW SEA SALT','DE-90 M','TSMP0332026042901','WHITE','HYDRO PU COATED LEATHER','A654','2026-04-29','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3524,'CHINGLUH',5,'NIKE',1,'41S','COLLEGE NAVY','R-53 SM','TMCL0172026042302','WHITE','GENERIC PU COATED','A411','2026-04-24','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3525,'TAEKWANG',30,'NIKE',1,'4PB','ASHEAN SLATE','AR-144 M','TMTK0272026042901','GREY','VIRGIN HYDRO PU LEATHER','A177','2026-04-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3526,'FENGTAY TW',58,'NIKE',1,'04Z','PURE PLATINUM','R-8 M','TSFT0382026042901','WHITE','(PM) GENERIC PU COATED','A335','2026-04-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3527,'VICTORY',31,'NIKE',1,'4NR','DIFFUSED BLUE','AR-20 M','TMVC0052026042801','GREY','(PM) GENERIC PU COATED','A412','2026-04-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3528,'NIKOMAS IY',18,'NIKE',1,'14A','OFF WHITE','R-8 M','TMNS0202026042901','WHITE','ECO TECH COMFORT','A1366','2026-04-30','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3529,'NIKOMAS',17,'ADIDAS',3,'AFDM','WARM VANILLA','DE-7 SM','SCOTDIC','2CT','PU COATED LEATHER','A896','2026-04-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3530,'NIKOMAS IY',18,'NIKE',1,'2CQ','VELVET BROWN','R-8 M','TMNS0202026043001','BLACK','VIRGIN PU','A1367','2026-04-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3531,'CHANGSHIN',4,'NIKE',1,'06F','ANTHRACITE','AR-126 M','TMCS0052026050502','GREY','(PM) GENERIC PU COATED','A434','2026-06-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3532,'CHANGSHIN',4,'NIKE',1,'10J','LT OREWOOD BRN','AR-126 M','TMCS0052026050501','WHITE','(PM) GENERIC PU COATED','A435','2026-06-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3533,'CHANGSHIN',4,'NIKE',1,'29J','PEARL WHITE','AR-107 M','TMCS0052026050601','WHITE','(PM) GENERIC PU COATED','A437','2026-06-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3534,'CHANGSHIN',4,'NIKE',1,'86Z','FUEL ORANGE (FLUORESCENT)','DE-146 SM','TMCS0052026050602','2CT','(PM) GENERIC PU COATED','A438','2026-06-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3535,'LONGRICH UA',41,'UA',5,'997','BLACKOUT NAVI','DE-43 M','TSLR0262026050501','BLACK','ACTION PU COATED LEATHER','A422','2026-06-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3536,'LONGRICH UA',41,'UA',5,'825','BLAZE ORANGE FLUORESCENT','DE-43 M','TSLR0262026050502','80S','ACTION PU COATED LEATHER','A423','2026-06-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3537,'LONGRICH UA',41,'UA',5,'1066C','METALLIC PINK MIRAGE','DE-43 M','TSLR0262026050504','PINK','ACTION PU COATED LEATHER','A424','2026-06-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3538,'LONGRICH UA',41,'UA',5,'410','KINECT BLUE','DE-43 M','TSLR0262026050505','BLACK','ACTION PU COATED LEATHER','A425','2026-06-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3539,'LONGRICH UA',41,'UA',5,'430-M','MISTY SKY BLUE','DE-43 M','TSLR0262026050506','LIGHT BLUE','ACTION PU COATED LEATHER','A426','2026-06-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3540,'LONGRICH UA',41,'UA',5,'381','PRISM GREEN','DE-43 M','TSLR0262026050507','4AU','ACTION PU COATED LEATHER','A427','2026-06-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3541,'LONGRICH UA',41,'UA',5,'400','TEAM ROYAL','DE-43 M','TSLR0262026050511','44Z','ACTION PU COATED LEATHER','A428','2026-06-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3542,'LONGRICH UA',41,'UA',5,'421','KINECT BLUE','DE-43 M','TSLR0262026050503','BLACK','ACTION PU COATED LEATHER','A429','2026-08-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3543,'LONGRICH UA',41,'UA',5,'600','RED','DE-43 M','TSLR0262026050508','RED','ACTION PU COATED LEATHER','A430','2026-08-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3544,'LONGRICH UA',41,'UA',5,'389-S','SEANSPRAY','DE-43 M','TSLR0262026050509','WHITE','ACTION PU COATED LEATHER','A431','2026-08-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3545,'LONGRICH UA',41,'UA',5,'511','SUGAR FLUM','DE-43 M','TSLR0262026050510','WHITE','ACTION PU COATED LEATHER','A432','2026-08-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3546,'VICTORY',31,'NIKE',1,'65N','UNIVERSITY RED (FLUORESCENT)','AR-20 M','TMVVC0052026050601','RED','(PM) GENERIC PU COATED','A413','2026-08-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3547,'CHINGLUH',5,'NIKE',1,'04B','CEMENT GREY','R-8 M','TMCL0172026050701','RED','(PM) GENERIC PU COATED','A414','2026-08-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3548,'CHANGSHIN',4,'NIKE',1,'4NR','DIFFUSED BLUE','R-102 M','TMCS0052026050701','4MD','ECO TECH COMFORT','A439','2026-08-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3549,'NIKOMAS',17,'ADIDAS',3,'AAGC','CHALK BLUE','DE-7 SM','SCOTDIC','49D','PU COATED LEATHER','A897','2026-11-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3550,'METRO NB',16,'NB',4,'124-91-00 (NB103)','NB 103 WHITE','AR-100','TSMP0332026051101','WHITE','ECO GREEN RECYCLED LEATHER','A656','2026-12-05','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3551,'NIKOMAS',17,'ADIDAS',3,'080A','SILVER MET','DE-7 SM','TSNS0162026051301','WHITE','PU COATED LEATHER','A898','2026-05-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL),
(3552,'VICTORY',31,'NIKE',1,'45B','OBSIDIAN','AR-20 M','TMVC0052026051201','BLACK','(PM) GENERIC PU COATED','A415','2026-05-13','DATA COLOR SWATCH.csv',1,'2026-05-19 03:12:27',NULL);
/*!40000 ALTER TABLE `color_swatch_recipes` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `customer_brand_mappings`
--

DROP TABLE IF EXISTS `customer_brand_mappings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_brand_mappings` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `customer_id` bigint(20) NOT NULL,
  `brand_id` bigint(20) NOT NULL,
  `is_default` tinyint(1) NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_customer_brand` (`customer_id`,`brand_id`),
  KEY `brand_id` (`brand_id`),
  CONSTRAINT `customer_brand_mappings_ibfk_1` FOREIGN KEY (`brand_id`) REFERENCES `brands` (`id`),
  CONSTRAINT `customer_brand_mappings_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=95 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer_brand_mappings`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `customer_brand_mappings` WRITE;
/*!40000 ALTER TABLE `customer_brand_mappings` DISABLE KEYS */;
INSERT INTO `customer_brand_mappings` VALUES
(1,1,1,0,NULL),
(2,1,2,0,NULL),
(4,3,1,0,NULL),
(5,3,2,0,NULL),
(6,4,1,0,NULL),
(7,4,2,0,NULL),
(8,5,1,0,NULL),
(9,5,2,0,NULL),
(10,7,1,0,NULL),
(11,7,2,0,NULL),
(12,8,1,0,NULL),
(13,8,2,0,NULL),
(14,9,1,0,NULL),
(15,9,2,0,NULL),
(18,12,4,0,NULL),
(19,13,4,0,NULL),
(21,15,1,0,NULL),
(22,15,2,0,NULL),
(23,16,4,0,NULL),
(25,18,1,0,NULL),
(26,18,2,0,NULL),
(29,21,4,0,NULL),
(31,23,4,0,NULL),
(32,24,4,0,NULL),
(33,25,1,0,NULL),
(34,25,2,0,NULL),
(35,26,1,0,NULL),
(36,26,2,0,NULL),
(37,27,1,0,NULL),
(38,27,2,0,NULL),
(39,28,1,0,NULL),
(40,28,2,0,NULL),
(41,30,1,0,NULL),
(42,30,2,0,NULL),
(43,31,1,0,NULL),
(44,31,2,0,NULL),
(45,32,1,0,NULL),
(46,32,2,0,NULL),
(47,33,5,0,NULL),
(49,35,4,0,NULL),
(50,36,1,0,NULL),
(51,36,2,0,NULL),
(52,37,4,0,NULL),
(53,38,4,0,NULL),
(54,40,4,0,NULL),
(55,41,5,0,NULL),
(56,42,6,0,NULL),
(57,43,4,0,NULL),
(60,46,5,0,NULL),
(61,48,4,0,NULL),
(62,49,4,0,NULL),
(63,50,4,0,NULL),
(65,52,4,0,NULL),
(67,54,4,0,NULL),
(68,54,6,0,NULL),
(69,55,5,0,NULL),
(71,57,1,0,NULL),
(72,57,2,0,NULL),
(73,58,1,0,NULL),
(74,58,2,0,NULL),
(75,59,1,0,NULL),
(76,59,2,0,NULL),
(77,60,1,0,NULL),
(78,60,2,0,NULL),
(79,61,1,0,NULL),
(80,61,2,0,NULL),
(81,2,3,0,NULL),
(82,10,3,0,NULL),
(83,11,3,0,NULL),
(84,14,3,0,NULL),
(85,17,3,0,NULL),
(86,19,3,0,NULL),
(87,20,3,0,NULL),
(88,22,3,0,NULL),
(89,34,3,0,NULL),
(90,44,3,0,NULL),
(91,45,3,0,NULL),
(92,51,3,0,NULL),
(93,53,3,0,NULL),
(94,56,3,0,NULL);
/*!40000 ALTER TABLE `customer_brand_mappings` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `customer_pics`
--

DROP TABLE IF EXISTS `customer_pics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_pics` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `customer_id` bigint(20) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `title` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `customer_id` (`customer_id`),
  CONSTRAINT `customer_pics_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer_pics`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `customer_pics` WRITE;
/*!40000 ALTER TABLE `customer_pics` DISABLE KEYS */;
INSERT INTO `customer_pics` VALUES
(5,52,'Wiranto','081250009139','notewiranto@gmail.com','Purchasing Manager'),
(6,52,'William','085311688881','william.tansil.90@gmail.com','Finance Manager');
/*!40000 ALTER TABLE `customer_pics` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `customer_special_prices`
--

DROP TABLE IF EXISTS `customer_special_prices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_special_prices` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `customer_id` bigint(20) NOT NULL,
  `buyer_code` varchar(32) NOT NULL,
  `material_pattern` varchar(255) DEFAULT NULL,
  `price_override` decimal(14,4) DEFAULT NULL,
  `discount_percentage` decimal(5,2) DEFAULT NULL,
  `valid_from` date DEFAULT NULL,
  `valid_to` date DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `customer_id` (`customer_id`),
  CONSTRAINT `customer_special_prices_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer_special_prices`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `customer_special_prices` WRITE;
/*!40000 ALTER TABLE `customer_special_prices` DISABLE KEYS */;
/*!40000 ALTER TABLE `customer_special_prices` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `code` varchar(50) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `contact_person` varchar(255) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `city` varchar(120) DEFAULT NULL,
  `tax_id` varchar(32) DEFAULT NULL,
  `remark` text DEFAULT NULL,
  `wilayah_province_code` varchar(8) DEFAULT NULL,
  `wilayah_regency_code` varchar(16) DEFAULT NULL,
  `wilayah_district_code` varchar(24) DEFAULT NULL,
  `wilayah_village_code` varchar(32) DEFAULT NULL,
  `skep_kb_number` varchar(80) DEFAULT NULL,
  `customs_office_code` varchar(32) DEFAULT NULL,
  `is_export_customer` tinyint(1) NOT NULL DEFAULT 0,
  `position` varchar(120) DEFAULT NULL,
  `payment_terms` varchar(120) DEFAULT NULL,
  `default_currency` varchar(3) DEFAULT NULL,
  `tax_mode` varchar(32) DEFAULT NULL,
  `reference_quotation` varchar(100) DEFAULT NULL,
  `billing_address` text DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=62 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
INSERT INTO `customers` VALUES
(1,'AD002','PT. ADIS DIMENSION FOOTWEAR','JL.RAYA SERANG KM 24 BALARAJA,TANGERANG INDONESIA 15610',NULL,'2026-04-29 16:48:47',NULL,NULL,NULL,'INDONESIA',NULL,'0018827378057000','KPPBC: TANGERANG | Kode Bea Cukai: 150300 | No Izin: KM-149/WBC.07/2023 | NITKU: 0018827378057000000000',NULL,NULL,NULL,NULL,'KM-149/WBC.07/2023','150300',0,NULL,NULL,NULL,NULL,NULL,'JL.RAYA SERANG KM 24 BALARAJA,TANGERANG INDONESIA 15610',1),
(2,'BI020','PT. BINTANG INDOKARYA GEMILANG (PBB)','JL. CENDRAWASIH TENGGULI NO. 6 KM. 20 KEL. TENGGULI KEC. TANJUNG BREBES JAWA TENGAH',NULL,'2026-04-29 16:48:47',NULL,NULL,NULL,'INDONESIA',NULL,'0029884624501000','KPPBC: TEGAL | Kode Bea Cukai: 061000 | No Izin: 180/WBC.10/2020 | NITKU: 0029884624501000000000',NULL,NULL,NULL,NULL,'180/WBC.10/2020','061000',0,NULL,NULL,NULL,NULL,NULL,'JL. CENDRAWASIH TENGGULI NO. 6 KM. 20 KEL. TENGGULI KEC. TANJUNG BREBES JAWA TENGAH',1),
(3,'CS004','PT. CHANG SHIN INDONESIA','JL. DUSUN GINTUNGKOLOT RT 16/04 DESA GINTUNGKERTA,KLARI KARAWANG-JABAR',NULL,'2026-04-29 16:48:47',NULL,NULL,NULL,'INDONESIA',NULL,'0311964266433000','KPPBC: PURWAKARTA | Kode Bea Cukai: 050800 | No Izin: KEP-157/WBC.09/2023 | NITKU: 0311964266433000000000',NULL,NULL,NULL,NULL,'KEP-157/WBC.09/2023','050800',0,NULL,NULL,NULL,NULL,NULL,'JL. DUSUN GINTUNG KOLOT RT.016/04 KLARI KARAWANG, JAWA BARAT',1),
(4,'CS005','PT. CHANGSHIN REKSA JAYA','JL. RAYA LELES NO.134, KAMPUNG KARANG MEKAR RT.02 RW.08 DS. CIBURIAL KECAMATAN LELES  , GARUT',NULL,'2026-04-29 16:48:47',NULL,NULL,NULL,'INDONESIA',NULL,'0312977754443000','KPPBC: TASIKMALAYA | Kode Bea Cukai: 050600 | No Izin: 448/KM.4/2018 | NITKU: 0312977754443000000000',NULL,NULL,NULL,NULL,'448/KM.4/2018','050600',0,NULL,NULL,NULL,NULL,NULL,'JL. RAYA LELES NO. 134 KAMPUNG KARANG MEKAR RT 02 RW 08 DS. CIBURIAL KEC. LELES, GARUT',1),
(5,'CL017','PT. CHING LUH INDONESIA','JL. RAYA SERANG KM.16 DESA TALAGASARI KEC.CIKUPA TANGERANG INDONESIA 15710',NULL,'2026-04-29 16:48:47',NULL,NULL,NULL,'INDONESIA',NULL,'0017603861451000','KPPBC: TANGERANG | Kode Bea Cukai: 150300 | No Izin: KM-87/WBC.07/2021 | NITKU: 0017603861451000000000',NULL,NULL,NULL,NULL,'KM-87/WBC.07/2021','150300',0,NULL,NULL,NULL,NULL,NULL,'JL.RAYA SERANG KM. 16 RT 006 / RW 003, DESA TALAGASARI, KECAMATAN CIKUPA, KABUPATEN TANGERANG, BANTEN',1),
(6,'DS026','PT. DEANSHOES (UA)','DUSUN SERANG RT 10 RW 05 DESA MEKARJAYA KEC. PURWASARI KARAWANG 41361',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'312471451433000','KPPBC: PURWAKARTA | Kode Bea Cukai: 050800 | No Izin: 163/WBC.09/KPP.MP.03/2018',NULL,NULL,NULL,NULL,'163/WBC.09/KPP.MP.03/2018','050800',0,NULL,NULL,NULL,NULL,NULL,'JL.DUSUN SERANG RT.10/05 DESA MEKARJAYA KECAMATAN PURBASARI KARAWANG 41361',1),
(7,'FT006','PT. FENG TAY INDONESIA ENTERPRISES (WEST)','JL.RAYA BANJARAN KM.14,6,DESA BOJONG MANGGU KEC.PAMEUNGPEUK,BANDUNG-JABAR',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0016713240445000','KPPBC: BANDUNG | Kode Bea Cukai: 050500 | No Izin: KEP-7/MK.4/WBC.09/2024 | NITKU: 0016713240445000000000',NULL,NULL,NULL,NULL,'KEP-7/MK.4/WBC.09/2024','050500',0,NULL,NULL,NULL,NULL,NULL,'JL RAYA BANJARAN KM 14,6 DESA BOJONG MANGGU KEC PAMEUNGPEUK KAB BANDUNG JAWABARAT',1),
(8,'FT007','PT. FENG TAY INDONESIA ENTERPRISES (EAST)','JL.RAYA BANJARAN KM.14,6,DESA BOJONG MANGGU KEC.PAMEUNGPEUK,BANDUNG-JABAR',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0016713240445000','KPPBC: BANDUNG | Kode Bea Cukai: 050500 | No Izin: KEP-7/MK.4/WBC.09/2024 | NITKU: 0016713240445000000000',NULL,NULL,NULL,NULL,'KEP-7/MK.4/WBC.09/2024','050500',0,NULL,NULL,NULL,NULL,NULL,'JL RAYA BANJARAN KM 14,6 DESA BOJONG MANGGU KEC PAMEUNGPEUK KAB BANDUNG JAWABARAT',1),
(9,'FT008','PT. FENG TAY INDONESIA ENTERPRISES (NORTH)','JL. RAYA BANJARAN KM.14,6 DESA BOJONG MANGGU KEC. PAMEUNGPEUK, BANDUNG-JABAR',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0016713240445000','KPPBC: BANDUNG | Kode Bea Cukai: 050500 | No Izin: KEP-7/MK.4/WBC.09/2024 | NITKU: 0016713240445000000000',NULL,NULL,NULL,NULL,'KEP-7/MK.4/WBC.09/2024','050500',0,NULL,NULL,NULL,NULL,NULL,'JL RAYA BANJARAN KM 14,6 DESA BOJONG MANGGU KEC PAMEUNGPEUK KAB BANDUNG JAWABARAT',1),
(10,'PGS30','PT. GLOSTAR INDONESIA (PGS)','JL. RAYA SUKABUMI-CIANJUR KM13 DESA TITISAN , KECAMATAN SUKALARANG',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0210079638441000','KPPBC: BOGOR | Kode Bea Cukai: 050300 | No Izin: 2378/KM.4/2017 | NITKU: 0210079638441000000000',NULL,NULL,NULL,NULL,'2378/KM.4/2017','050300',0,NULL,NULL,NULL,NULL,NULL,'JL. RAYA SUKABUMI-CIANJUR KM13 DESA TITISAN , KECAMATAN SUKALARANG',1),
(11,'GS007','PT. GLOSTAR INDONESIA (PGD)','JL.PELABUHAN II KM.14,5 KP.SAMPORA RT.3 RW. 5 DS.BOJONGRAHARJA, KEC.CIKEMBAR SUKABUMI-JABAR',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0210079638441000','KPPBC: BOGOR | Kode Bea Cukai: 050300 | No Izin: 1213/KM.4/2016 | NITKU: 0210079638441000000000',NULL,NULL,NULL,NULL,'1213/KM.4/2016','050300',0,NULL,NULL,NULL,NULL,NULL,'JL PELABUHAN II KM 14,5 KP SAMPORA RT 003 RW 005 DESA BOJONGRAHARJA KEC CIKEMBAR KAB SUKABUMI JAWABARAT',1),
(12,'GS009','PT. GLOSTAR INDONESIA (PYS)','JL. PELABUHAN II KM. 14.5 KP. SAMPORA, DS. BOJONG, KEC. CIKEMBAR, SUKABUMI, JAWA BARAT 43157',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'210079638441000','KPPBC: BOGOR | Kode Bea Cukai: 050300 | No Izin: 1213/KM.4/2016 | NITKU: 0210079638441000000000',NULL,NULL,NULL,NULL,'1213/KM.4/2016','050300',0,NULL,NULL,NULL,NULL,NULL,'JL PELABUHAN II KM 14,5 KP SAMPORA RT 003 RW 005 DESA BOJONGRAHARJA KEC CIKEMBAR KAB SUKABUMI JAWABARAT',1),
(13,'HI024','PT. HORN MING INDONESIA','JL. RAYA KM. 18,8 DS. SUKANAGARA, CIKUPA - TANGERANG - 15710',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'010617421057000','KPPBC: TANGERANG | Kode Bea Cukai: 150300 | No Izin: KM-42/WBC.07/2019 | NITKU: 0010617421057000000000',NULL,NULL,NULL,NULL,'KM-42/WBC.07/2019','150300',0,NULL,NULL,NULL,NULL,NULL,'JL.RAYA SERANG KM.18,8 DESA SUKANEGARA KECAMATAN CIKUPA TANGERANG BANTEN',1),
(14,'HW036','PT. HWA SEUNG INDONESIA','Jl Raya Pati Rembang KM 17 Desa Bumimulyo  RT01/RW01 Kec Batangan Kab Pati. Jawa tengah',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0759058803516000','KPPBC: KUDUS | Kode Bea Cukai: 060300 | No Izin: 45/KM.4/WBC.10/2024 | NITKU: 0759058803516000000000',NULL,NULL,NULL,NULL,'53/WBC.10/2022','060300',0,NULL,NULL,NULL,NULL,NULL,'JALAN RAYA PATI-REMBANG KM 17, DESA\nBUMIMULYO RT 001/RW 001, KEC. BATANGAN, KAB. PATI,\nJAWA TENGAH',1),
(15,'KM001','PT. KMK GLOBAL SPORTS','JL.CIKUPAMAS RAYA NO 17 TANGERANG-BANTEN INDONESIA',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0018827444451000','KPPBC: TANGERANG | Kode Bea Cukai: 150300 | No Izin: 1568/KM.4/2012 | NITKU: 0018827444451000000000',NULL,NULL,NULL,NULL,'1568/KM.4/2012','150300',0,NULL,NULL,NULL,NULL,NULL,'JL.CIKUPAMAS RAYA NO 17 TANGERANG-BANTEN INDONESIA',1),
(16,'MP033','PT. METRO PEARL INDONESIA (NB)','JL. PRAMUKA KM 0.99 NO. 18 KEL. BUNDER KEC. JATILUHUR KAB. PURWAKARTA, JAWA BARAT',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0030169775409000','KPPBC: PURWAKARTA | Kode Bea Cukai: 050800 | No Izin: 610/KM.4/2017 | NITKU: 0030169775409000000000',NULL,NULL,NULL,NULL,'610/KM.4/2017','050800',0,NULL,NULL,NULL,NULL,NULL,'JL.PRAMUKA KM.0,99 NO.18 BUNDER JATILUHUR PURWAKARTA JAWABARAT',1),
(17,'NS016','PT. NIKOMAS GEMILANG','JL.RAYA SERANG KM 71 DESA TAMBAK KEC KIBIN SERANG BANTEN',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0013862305401000','KPPBC: MERAK | Kode Bea Cukai: 050400 | No Izin: 115/MK/WBC.07/2025 | NITKU: 0013862305401000000000',NULL,NULL,NULL,NULL,'115/MK/WBC.07/2025','050400',0,NULL,NULL,NULL,NULL,NULL,'JL.RAYA SERANG KM 71 DESA TAMBAK KEC KIBIN SERANG BANTEN',1),
(18,'NS020','PT. NIKOMAS GEMILANG (IY)','JL.RAYA SERANG KM 71 DESA TAMBAK KEC KIBIN SERANG BANTEN',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0013862305401000','KPPBC: MERAK | Kode Bea Cukai: 050400 | No Izin: 115/MK/WBC.07/2025 | NITKU: 0013862305401000000000',NULL,NULL,NULL,NULL,'115/MK/WBC.07/2025','050400',0,NULL,NULL,NULL,NULL,NULL,'JL.RAYA SERANG KM 71 DESA TAMBAK KEC KIBIN SERANG BANTEN',1),
(19,'PA020','PT. PANARUB INDUSTRY','JL. MOCH. TOHA KM1, GRENDENG, TANGERANG, INDONESIA',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0011204369057000','KPPBC: TANGERANG | Kode Bea Cukai: 150300 | No Izin: 82/MK/WBC.07/2025 | NITKU: 0011204369057000000000',NULL,NULL,NULL,NULL,'82/MK/WBC.07/2025','150300',0,NULL,NULL,NULL,NULL,NULL,'JL. MOCH. TOHA KM1, GRENDENG, TANGERANG, INDONESIA',1),
(20,'PA009','PT. PARKLAND WORLD INDONESIA 1','JALAN RAYA SERANG KM68 DESA NAMBO ILIR KIBIN,CIKANDE,SERANG BANTEN,INDONESIA',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'021930615401000','KPPBC: MERAK | Kode Bea Cukai: 050400 | No Izin: KM-5/WBC.07/2019 | NITKU: 0021930615401000000000',NULL,NULL,NULL,NULL,'KM-5/WBC.07/2019','050400',0,NULL,NULL,NULL,NULL,NULL,'JALAN RAYA SERANG KM68 DESA NAMBO ILIR KIBIN, CIKANDE, SERANG BANTEN, INDONESIA',1),
(21,'PW010','PT. PARKLAND WORLD INDONESIA 2','JL.LANUD GORDA KM68 D DESA JULANG,KEC.CIKANDE,SERANG BANTEN-INDONESIA',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'021930615401000','KPPBC: MERAK | Kode Bea Cukai: 050400 | No Izin: KM-6/WBC.07/2019 | NITKU: 0021930615401000000000',NULL,NULL,NULL,NULL,'KM-6/WBC.07/2019','050400',0,NULL,NULL,NULL,NULL,NULL,'JL LANUD GORDA KM 68 DESA JULANG KEC CIKANDE KAB SERANG',1),
(22,'PA010','PT. PARKLAND WORLD INDONESIA 3','JALAN RAYA JEPARA KUDUS RT. 006 RW. 002 PELANG MAYONG KAB. JEPARA JAWA TENGAH 59645',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'021930615401000','KPPBC: KUDUS | Kode Bea Cukai: 060300 | No Izin: 214/WBC.10/2021 | NITKU: 0021930615401000000000',NULL,NULL,NULL,NULL,'214/WBC.10/2021','060300',0,NULL,NULL,NULL,NULL,NULL,'JALAN RAYA JEPARA KUDUS RT. 006 RW. 002 PELANG MAYONG KAB. JEPARA JAWA TENGAH 59645',1),
(23,'PW030','PT. PARKLAND WORLD INDONESIA (PWA)','JL. RAYA REMBANG - PAMOTAN KM.5, PAMOTAN, KECAMATAN PAMOTAN, KABUPATEN REMBANG, JAWA TENGAH',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'021930615401000','KPPBC: KUDUS | Kode Bea Cukai: 060300 | No Izin: 215/WBC.10/2021 | NITKU: 0021930615401000000000',NULL,NULL,NULL,NULL,'215/WBC.10/2021','060300',0,NULL,NULL,NULL,NULL,NULL,'JL.RAYA REMBANG - PAMOTAN KM.5, PAMOTAN, KECAMATAN PAMOTAN, KABUPATEN REMBANG, JAWA TENGAH',1),
(24,'PY028','PT. POU YUEN INDONESIA','KP. LEMBUR SAWAH NO. RT 001 RW 001 KEL. SUKASIRNA, KEC. SUKALUYU CIANJUR, JAWA BARAT',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0668716095406000','KPPBC: BOGOR | Kode Bea Cukai: 050300 | No Izin: KEP-729/WBC.09/2018 | NITKU: 0668716095406000000000',NULL,NULL,NULL,NULL,'KEP-729/WBC.09/2018','050300',0,NULL,NULL,NULL,NULL,NULL,'KP. LEMBUR SAWAH NO. RT 001 RW 001 KEL. SUKASIRNA, KEC. SUKALUYU CIANJUR, JAWA BARAT',1),
(25,'PT012','PT. PRATAMA ABADI INDUSTRI IR','JL.RAYA SERPONG KM 7 PAKUALAM ,SERPONG UTARA, TANGERANG SELATAN, BANTEN 15335',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'001.061.827.0-057.000','KPPBC: TANGERANG | Kode Bea Cukai: 150300 | No Izin: 2661/KM.4/2017 | NITKU: 0010618270057000000000',NULL,NULL,NULL,NULL,'2661/KM.4/2017','150300',0,NULL,NULL,NULL,NULL,NULL,'JL.RAYA SERPONG KM 7 PAKUALAM ,SERPONG UTARA, TANGERANG SELATAN, BANTEN 15320',1),
(26,'PT013','PT. PRATAMA ABADI INDUSTRI JX','BLOK SATONG PARIGI DESA TITISAN KECAMATAN SUKALARANG KABUPATEN SUKABUMI JAWA BARAT',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'001.061.827.0-057.000','KPPBC: BOGOR | Kode Bea Cukai: 050300 | No Izin: 149/KM.4/2017 | NITKU: 0010618270057000000000',NULL,NULL,NULL,NULL,'149/KM.4/2017','050300',0,NULL,NULL,NULL,NULL,NULL,'BLOK SATONG PARIGI DESA TITISAN KEC SUKALARANG KAB SUKABUMI JAWABARAT',1),
(27,'PT015','PT. PRATAMA ABADI INDUSTRI JX2','JALAN RAYA BANDUNG-TASIKMALAYA KM 43, CIJOLANG, BL LIMBANGAN, KAB. GARUT, JAWA BARAT 44186',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'001.061.827.0-057.000','KPPBC: TASIKMALAYA | Kode Bea Cukai: 050600 | No Izin: 493/WBC.09/2022 | NITKU: 0010618270057000000000',NULL,NULL,NULL,NULL,'493/WBC.09/2022','050600',0,NULL,NULL,NULL,NULL,NULL,'Jl. Raya Bandung - Tasikmalaya Km. 43, Kel. Cijolang, Kec. Bl. Limbangan, Kab. Garut, Provinsi Jawa Barat Kode Pos: 44186',1),
(28,'SL043','PT. SHOETOWN LIGUNG INDONESIA','JL. LANUD SUKANI, DESA BUNTU, KEC. LIGUNG KAB. MAJALENGKA 45456',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0769849761451000','KPPBC: CIREBON | Kode Bea Cukai: 050700 | No Izin: KEP-602/WBC.09/2018 | NITKU: 0769849761451000000000',NULL,NULL,NULL,NULL,'KEP-602/WBC.09/2018','050700',0,NULL,NULL,NULL,NULL,NULL,'JL. LANUD SUKANI, DESA BUNTU, KEC. LIGUNG KAB. MAJALENGKA 45456',1),
(29,'SY008','PT. SHYANG YAO FUNG','JL. INDUSTRI RAYA BLOKD NO.2 PASIR JAYA KEC. JATIUWUNG, TANGERANG 15000',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'027555275415001','KPPBC: TANGERANG | Kode Bea Cukai: 150300 | No Izin: KEP-166/WBC.07/KPP.MP.02/2018 | NITKU: 0027555275415001000000',NULL,NULL,NULL,NULL,'KEP-166/WBC.07/KPP.MP.02/2018','150300',0,NULL,NULL,NULL,NULL,NULL,'JL INDUSTRI RAYA BLOK D NO 2 KEL PASIR JAYA KEC JATIUWUNG KOTA TANGERANG BANTEN',1),
(30,'TK027','PT. TKG TAEKWANG INDONESIA','DUSUN BELENDUNG II RT 017 RW 006, BELENDUNG, CIBOGO, KAB. SUBANG, JAWA BARAT 41285',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0028239598439000','KPPBC: PURWAKARTA | Kode Bea Cukai: 050800 | No Izin: 58/KM.4/WBC.09/2025 | NITKU: 0028239598439000000000',NULL,NULL,NULL,NULL,'58/KM.4/WBC.09/2025','050800',0,NULL,NULL,NULL,NULL,NULL,'DUSUN BELENDUNG II RT 017 RW 006, BELENDUNG, CIBOGO, SUBANG, JAWA BARAT',1),
(31,'VC005','PT. VICTORY CHINGLUH INDONESIA','JL.OTONOM PASAR KEMIS NO 48/49,PASAR KEMIS,TANGERANG BANTEN 15560',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0210629747418000','KPPBC: TANGERANG | Kode Bea Cukai: 150300 | No Izin: KM-231/WBC.07/2021 | NITKU: 0210629747418000000000',NULL,NULL,NULL,NULL,'KM-231/WBC.07/2021','150300',0,NULL,NULL,NULL,NULL,NULL,'JL.OTONOM PASAR KEMIS NO.48/49 PASAR KEMIS TANGERANG BANTEN 15560',1),
(32,'SC006','PT. SELALU CINTA INDONESIA','JL. LINGKAR SELATAN SALATIGA DUSUN TETEP NO. RT 003 RW . 003 KEL RANDUACIR KEC. ARGOMULYO, SALATIGA',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0729241489505000','KPPBC: SEMARANG | Kode Bea Cukai: 060800 | No Izin: 193/WBC.10/2020 | NITKU: 0729241489505000000000',NULL,NULL,NULL,NULL,'193/WBC.10/2020','060800',0,NULL,NULL,NULL,NULL,NULL,'JL. LINGKAR SELATAN SALATIGA DUSUN TETEP NO. RT 003 RW . 003 KEL RANDUACIR KEC. ARGOMULYO, SALATIGA',1),
(33,'YT001','PT.YOUNG TREE INDUSTRIES','JL. RAYA BANAR KEL. KETIMANG KEC. WONOAYU SIDOARJO JAWA TIMUR',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'026381244641000','KPPBC: SIDOARJO | Kode Bea Cukai: 071500 | No Izin: 992/WBC.11/2022 | NITKU: 0026381244641000000000',NULL,NULL,NULL,NULL,'992/WBC.11/2022','071500',0,NULL,NULL,NULL,NULL,NULL,'JL. RAYA BANAR RT.07/RW.02 DESA KETIMANG, KECAMATAN WONOAYU, KAB. SIDOARJO, JAWA TIMUR',1),
(34,'TS001','PT. TAH SUNG HUNG','JALAN PEMUDA NOMOR 35A, KEL. JAGAPURA, KEC. KERSANA, KAB. BREBES, JAWA TENGAH',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0810012757501000','KPPBC: TEGAL | Kode Bea Cukai: 061000 | No Izin: 31/MK/WBC.10/2026 | NITKU: 0810012757501000000000',NULL,NULL,NULL,NULL,'31/MK/WBC.10/2026','061000',0,NULL,NULL,NULL,NULL,NULL,'JALAN PEMUDA NOMOR 35A, KEL. JAGAPURA, KEC. KERSANA, KAB. BREBES, JAWA TENGAH',1),
(35,'SD048','PT. SENGDAM JAYA ABADI','DUSUN MANDURO MANGGUNG GAJAH RT.015 RW.003 KEC. NGORO, KAB. MOJOKERTO JAWA TIMUR 61385',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'210667317602000','KPPBC: SIDOARJO | Kode Bea Cukai: 071500 | No Izin: KEP-1941/WBC.11/2020 | NITKU: 0210667317602000000000',NULL,NULL,NULL,NULL,'KEP-1941/WBC.11/2020','071500',0,NULL,NULL,NULL,NULL,NULL,'DUSUN MANDURO MANGGUNG GAJAH RT.015 RW.003 KEC. NGORO, KAB. MOJOKERTO JAWA TIMUR 61385',1),
(36,'PT014','PT. SUMBER MASANDA JAYA','JL. RAYA BANGSRI RT.001 RW.001, BANGSRI BULAKAMBA, KAB. BREBES, JAWA TENGAH 52253',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'001.330.990.1-057.000','KPPBC: TEGAL | Kode Bea Cukai: 061000 | No Izin: 50/WBC.10/2022 | NITKU: 0013309901057000000000',NULL,NULL,NULL,NULL,'50/WBC.10/2022','061000',0,NULL,NULL,NULL,NULL,NULL,'JL. RAYA BANGSRI RT.001 RW.001, BANGSRI BULAKAMBA, KAB. BREBES, JAWA TENGAH 52253',1),
(37,'SD047','PT. SUKSES ABADI INDONESIA','JL. GONDANG - LENGKONG, KEL. GONDANGKULON, KEC. GONDANG, KAB. NGANJUK, PROVINSI JAWA TIMUR  64451',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'934861444655000','KPPBC: KEDIRI | Kode Bea Cukai: 070800 | No Izin: 279/WBC.12/2021 | NITKU: 0934861444655000000000',NULL,NULL,NULL,NULL,'279/WBC.12/2021','070800',0,NULL,NULL,NULL,NULL,NULL,'JL. GONDANG - LENGKONG RT.000 RW.000, GONDANGKULON, GONDANG, KAB. NGANJUK JAWA TIMUR 64551',1),
(38,'DI024','PT. DIAMOND INTERNATIONAL INDONESIA','JL. RAYA TONJONG-JATIWANGI ANDIR, KAB MAJALENGKA JABAR',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'811913383438000','KPPBC: CIREBON | Kode Bea Cukai: 050700 | No Izin: 261/KM.4/WBC.09/2024 | NITKU: 0811913383438000000000',NULL,NULL,NULL,NULL,'261/KM.4/WBC.09/2024','050700',0,NULL,NULL,NULL,NULL,NULL,'JL. RAYA TONJONG JATIWANGI, ANDIR, JATIWANGI, KAB. MAJALENGKA, JAWA BARAT, 45454',1),
(39,'YC027','PT.YC TEC INDONESIA','KP.CISANTRI RT 02 RW 01, DESA CILANDAK. KEC CIBATU  KAB PURWAKARTA-JAWA BARAT',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0314492117409000','KPPBC: PURWAKARTA | Kode Bea Cukai: 050800 | No Izin: KEP-122/WBC.09/2023 | NITKU: 0314492117409000000000',NULL,NULL,NULL,NULL,'KEP-122/WBC.09/2023','050800',0,NULL,NULL,NULL,NULL,NULL,'KP CISANTRI, RW 001, RT 002, CILANDAK, CIBATU, KAB. PURWAKARTA, JAWA BARAT, 41183',1),
(40,'PW020','PT. SEJIN FASHION INDONESIA','JL. RAYA PATI - KUDUS KM 7 , KEL. BUMIREJO, KEC. MARGOREJO, KAB. PATI, KODE POS: 11480',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'915989206031000','KPPBC: KUDUS | Kode Bea Cukai: 060300 | No Izin: 75/WBC.10/2021 | NITKU: 0915989206031000000000',NULL,NULL,NULL,NULL,'75/WBC.10/2021','060300',0,NULL,NULL,NULL,NULL,NULL,'JL RAYA PATI - KUDUS KM 7, RW 003, RT 003, BUMIREJO, MARGOREJO, KAB. PATI, JAWA TENGAH, 73163',1),
(41,'LR026','PT. LONGRICH INDONESIA-UA','JL. D.I. PANJAITAN DUSUN PAING NO.08 RT.004 RW.002 SIDARESMI PABEDILAN,KAB. CIREBON JAWA BARAT 45193',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0735239725451000','KPPBC: CIREBON | Kode Bea Cukai: 050700 | No Izin: 234/MK/WBC.09/2025 | NITKU: 0735239725451000000000',NULL,NULL,NULL,NULL,'234/MK/WBC.09/2025','050700',0,NULL,NULL,NULL,NULL,NULL,'JL. D I PANJAITAN DUSUN PAING, NO. 08, RW 002, RT 004, SIDARESMI, PABEDILAN, KAB. CIREBON, JAWA BARAT, 45193',1),
(42,'LR027','PT. LONG RICH INDONESIA-FIO','JL. D.I. PANJAITAN DUSUN PAING NO.08 RT.004 RW.002 SIDARESMI PABEDILAN,KAB. CIREBON JAWA BARAT 45193',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0735239725451000','KPPBC: CIREBON | Kode Bea Cukai: 050700 | No Izin: 234/MK/WBC.09/2025 | NITKU: 0735239725451000000000',NULL,NULL,NULL,NULL,'234/MK/WBC.09/2025','050700',0,NULL,NULL,NULL,NULL,NULL,'JL. D I PANJAITAN DUSUN PAING, NO. 08, RW 002, RT 004, SIDARESMI, PABEDILAN, KAB. CIREBON, JAWA BARAT, 45193',1),
(43,'LR028','PT. LONG RICH INDONESIA NB','JL. D.I. PANJAITAN DUSUN PAING NO.08 RT.004 RW.002 SIDARESMI PABEDILAN,KAB. CIREBON JAWA BARAT 45193',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0735239725451000','KPPBC: CIREBON | Kode Bea Cukai: 050700 | No Izin: 234/MK/WBC.09/2025 | NITKU: 0735239725451000000000',NULL,NULL,NULL,NULL,'234/MK/WBC.09/2025','050700',0,NULL,NULL,NULL,NULL,NULL,'JL. D I PANJAITAN DUSUN PAING, NO. 08, RW 002, RT 004, SIDARESMI, PABEDILAN, KAB. CIREBON, JAWA BARAT, 45193',1),
(44,'LR029','PT. LONG RICH INDONESIA ADIDAS','JL. D.I. PANJAITAN DUSUN PAING NO.08 RT.004 RW.002 SIDARESMI PABEDILAN,KAB. CIREBON JAWA BARAT 45193',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,NULL,'KPPBC: CIREBON | Kode Bea Cukai: 050700 | No Izin: 234/MK/WBC.09/2025 | NITKU: 0735239725451000000000',NULL,NULL,NULL,NULL,'234/MK/WBC.09/2025','050700',0,NULL,NULL,NULL,NULL,NULL,'JL. D I PANJAITAN DUSUN PAING, NO. 08, RW 002, RT 004, SIDARESMI, PABEDILAN, KAB. CIREBON, JAWA BARAT, 45193',1),
(45,'DW001','PT. DWI PRIMA SENTOSA','JL.RAYA NGAWI-CARUBAN KM04 DUSUN CABEAN RT03/01 DS.KARANGTENGAH-PRANDON KEC/KAB. NGAWI JAWA TIMUR',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0024189466059000','KPPBC: MADIUN | Kode Bea Cukai: 071000 | No Izin: 15/MK/WBC.12/2025 | NITKU: 0024189466059000000000',NULL,NULL,NULL,NULL,'15/MK/WBC.12/2025','071000',0,NULL,NULL,NULL,NULL,NULL,'JL.RAYA NGAWI-CARUBAN KM04 DUSUN CABEAN RT03/01 DS.KARANGTENGAH-PRANDON KEC/KAB. NGAWI JAWA TIMUR',1),
(46,'YT002','PT.YOUNG TREE INDUSTRIES (SOLO)','JL. SLAMET RIYADI NO 258 GUMPANG, KARTASURA, SUKOHARJO, DUSUN III JAWA TENGAH 57169',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'026381244641000','KPPBC: SURAKARTA | Kode Bea Cukai: 060600 | No Izin: 051/WBC.10/2023 | NITKU: 0026381244641000000000',NULL,NULL,NULL,NULL,'051/WBC.10/2023','060600',0,NULL,NULL,NULL,NULL,NULL,'Jl. Slamet Riyadi No 258 Gumpang, kartasura, Sukoharjo, Dusun III Jawa Tengah 57169',1),
(47,'SJ010','PT. SHOENARY JAVANESIA INC','Jalan Raya Temanggung-Secang KM 8 kavling 8, Kel. Badran,\nKec. Kranggan, Kab. Temanggung, Prov. Jawa Tengah',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'803198399452000','KPPBC: MAGELANG | Kode Bea Cukai: 061100 | No Izin: 52/WBC.10/2020 | NITKU: 0803198399452000000000',NULL,NULL,NULL,NULL,'52/WBC.10/2020','061100',0,NULL,NULL,NULL,NULL,NULL,'JL RAYA TEMANGGUNG-SECANG KM 8 KAVLING 8, RW 006, RT 002, BADRAN, KRANGGAN, KAB. TEMANGGUNG, JAWA TENGAH, 56271',1),
(48,'SH001','PT. SHYANG HUNG TAH','JALAN PRUPUK-PEJAGAN, KEL. MARGA AYU, KEC. MARGASARI, KAB. TEGAL,',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'420848996501000','KPPBC: TEGAL | Kode Bea Cukai: 061000 | No Izin: 15/KM.4/WBC.10/2025 | NITKU: 0420848996501000000000',NULL,NULL,NULL,NULL,'15/KM.4/WBC.10/2025','061000',0,NULL,NULL,NULL,NULL,NULL,'JL PRUPUK PEJAGAN, RW 001, RT 005, MARGA AYU, MARGASARI, KAB. TEGAL, JAWA TENGAH, 52463',1),
(49,'MP034','PT. ULTIMATE NOBLE INDONESIA','JL. SASAK BEUSI, NO. 13 RT 013 RW 011 SINDANGSUKA, CIBATU',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0631079639443000','KPPBC: TASIKMALAYA | Kode Bea Cukai: 050600 | No Izin: KEP-413/WBC.09/2023 | NITKU: 0631079639443000000000',NULL,NULL,NULL,NULL,'KEP-413/WBC.09/2023','050600',0,NULL,NULL,NULL,NULL,NULL,'JL. SASAK BEUSI, NO. 13 RT 013 RW 011 SINDANGSUKA, CIBATU',1),
(50,'SL045','PT. SHOETOWN MUSTIKA INDONESIA','JALAN RAYA GRESIK LAMONGAN KM 25, REJOSARI,DEKET, KAB. LAMONGAN, JAWA TIMUR, 62291',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0212265292645000','KPPBC: GRESIK | Kode Bea Cukai: 070300 | No Izin: 35/KM.4/WBC.11/2025 | NITKU: 0212265292645000000000',NULL,NULL,NULL,NULL,'35/KM.4/WBC.11/2025','070300',0,NULL,NULL,NULL,NULL,NULL,'JALAN RAYA GRESIK LAMONGAN KM 25, REJOSARI,DEKET, KAB. LAMONGAN, JAWA TIMUR, 62291',1),
(51,'HA001','PT. HARDASES ABADI INDONESIA','JL. RAYA WANGANDOWO, SAMPIH. WONOPRINGGO. KAB. PEKALONGAN. JAWA TENGAH 51811',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0947106811502000','KPPBC: TEGAL | Kode Bea Cukai: 061000 | No Izin: 105/MK/WBC.10/2025 | NITKU: 0947106811502000000000',NULL,NULL,NULL,NULL,'105/MK/WBC.10/2025','061000',0,NULL,NULL,NULL,NULL,NULL,'JL. RAYA WANGANDOWO, SAMPIH. WONOPRINGGO. KAB. PEKALONGAN. JAWA TENGAH 51811',1),
(52,'HA002','PT. HARDASES ABADI INDONESIA (PYN)','JL. RAYA WANGANDOWO RT 04 RW 02, SAMPIH, KEC. WONOPRINGGO, KAB. PEKALONGAN, JAWA TENGAH, 51129','081250009139','2026-04-29 16:48:48','2026-05-04 02:18:15','notewiranto@gmail.com','Wiranto','Indonesia',NULL,'0947106811502000','KPPBC: TEGAL | Kode Bea Cukai: 061000 | No Izin: 105/MK/WBC.10/2025 | NITKU: 0947106811502000000000','33','33.26','33.26.12','33.26.12.2009','105/MK/WBC.10/2025','061000',0,'Purchasing Manager','DP 50% + Pelunasan sebelum kirim','USD','pkp',NULL,'JL. RAYA WANGANDOWO RT 04 RW 02, SAMPIH, KEC. WONOPRINGGO, KAB. PEKALONGAN, JAWA TENGAH, 51129',1),
(53,'AD003','PT. ADONIA FOOTWEAR INDONESIA','JL RAYA BARAT RUAS 77 RT 005 RW 006 LEBAKSIU KIDUL LEBAKSIU KAB. TEGAL JAWA TENGAH 52461',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0415709740508000','KPPBC: TEGAL | Kode Bea Cukai: 061000 | No Izin: 159/KM.4/WBC.10/2024 | NITKU: 0415709740508000000000',NULL,NULL,NULL,NULL,'159/KM.4/WBC.10/2024','061000',0,NULL,NULL,NULL,NULL,NULL,'JL RAYA BARAT RUAS 77 RT 005 RW 006 LEBAKSIU KIDUL LEBAKSIU KAB. TEGAL JAWA TENGAH 52461',1),
(54,'LW001','PT. LONG WELL INTERNATIONAL','JALAN RAYA BANJARMULYA - PADURAKSA , Desa/Kelurahan Kramat,Kec. Pemalang, Kab. Pemalang 52318',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0539384396502000','KPPBC: TEGAL | Kode Bea Cukai: 061000 | No Izin: 137/MK/WBC.10/2025 | NITKU: 0539384396502000000000',NULL,NULL,NULL,NULL,'137/MK/WBC.10/2025','061000',0,NULL,NULL,NULL,NULL,NULL,'JALAN RAYA BANJARMULYA - PADURAKSA , Desa/Kelurahan Kramat,Kec. Pemalang, Kab. Pemalang 52318',1),
(55,'VF050','PT. VICTORY FOOTWEAR INDONESIA','Jl. Raya Cirebon Tegal, Ds. Bangsri RT 006 RW 002, Kec. Bulakamba, Kab. Brebes, Jawa Tengah',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,'0396418147077000','KPPBC: TEGAL | Kode Bea Cukai: 061000 | No Izin: 93/MK/WBC.10/2025 | NITKU: 0396418147077000000000',NULL,NULL,NULL,NULL,'93/MK/WBC.10/2025','061000',0,NULL,NULL,NULL,NULL,NULL,'Jl. Raya Cirebon Tegal, Ds. Bangsri RT 006 RW 002, Kec. Bulakamba, Kab. Brebes, Jawa Tengah',1),
(56,'PH001','PT. PEI HAI INTERNATIONAL WIRATAMA INDONESIA','DSN. GERIH, JANTI, JOGOROTO, KAB. JOMBANG, JAWA TIMUR',NULL,'2026-04-29 16:48:48',NULL,NULL,NULL,'INDONESIA',NULL,NULL,'KPPBC: KEDIRI | Kode Bea Cukai: 070800 | No Izin: 327/WBC.12/2022 | NITKU: 0010828820631000000000',NULL,NULL,NULL,NULL,'327/WBC.12/2022','070800',0,NULL,NULL,NULL,NULL,NULL,'DSN. GERIH, JANTI, JOGOROTO, KAB. JOMBANG, JAWA TIMUR',1),
(57,'CS006','CHANGSHIN INC','242, JANGPYEONG-RO SAHA-GU, BUSAN, KOREA','TEL: 503-736-5900 FAX: 503-493-2092','2026-04-29 16:50:12',NULL,'Julie.Zhu@oiaglobal.com','JULIE ZHU','KOREA',NULL,NULL,'Bill To: OIA GLOBAL LOGISTICS-SCM, INC.',NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL,NULL,'2100 SW RIVER PARKWAY, SUITE 800 PORTLAND, OR 97201 UNITED STATES',1),
(58,'FT038','FENG TAY ENTERPRISE CO., LTD','52 KEGUNG 8TH ROAD, TOU-LIO YUN-LIN HSIEN, TAIWAN 640','TEL: 503-736-5900 FAX: 503-493-2092','2026-04-29 16:50:12',NULL,'Evelyn.Lin@oiaglobal.com','EVELYN LIN','TAIWAN',NULL,NULL,'Bill To: OIA GLOBAL LOGISTICS-SCM, INC.',NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL,NULL,'2100 SW RIVER PARKWAY, SUITE 800 PORTLAND, OR 97201 UNITED STATES',1),
(59,'PG021','POU CHEN CORPORATION','NO. 2 FU KUN ROAD,FU HISN,CHANG HWA,TAIWAN R.O.C.','TEL: 503-736-5900 FAX: 503-493-2092','2026-04-29 16:50:12',NULL,'Nell.Chen@oiaglobal.com','NELL','TAIWAN',NULL,NULL,'Bill To: OIA GLOBAL LOGISTICS-SCM, INC.',NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL,NULL,'2100 SW RIVER PARKWAY, SUITE 800 PORTLAND, OR 97201 UNITED STATES',1),
(60,'TK028','TAE KWANG INDUSTRIAL CO LTD','26, GIMHAE-DAERO 2635BEON-GIL , GIMHAE , KOREA','TEL: 503-736-5900 FAX: 503-493-2092','2026-04-29 16:50:13',NULL,'Candy.Xiong@oiaglobal.com','CANDY XIONG','KOREA',NULL,NULL,'Bill To: OIA GLOBAL LOGISTICS-SCM, INC.',NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL,NULL,'2100 SW RIVER PARKWAY, SUITE 800 PORTLAND, OR 97201 UNITED STATES',1),
(61,'SL044','WEALTH VAST CO,LTD','372DRP, LOK MA CHAU, SAN TIN, NT, HONG KONG','TEL: 503-736-5900 FAX: 503-493-2092','2026-04-29 16:50:13',NULL,'Daisy.He@oiaglobal.com','DAISY','HONGKONG',NULL,NULL,'Bill To: OIA GLOBAL LOGISTICS-SCM, INC.',NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL,NULL,'2100 SW RIVER PARKWAY, SUITE 800 PORTLAND, OR 97201 UNITED STATES',1);
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `customs_aju_sheet_rows`
--

DROP TABLE IF EXISTS `customs_aju_sheet_rows`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `customs_aju_sheet_rows` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `declaration_id` bigint(20) NOT NULL,
  `sheet_code` varchar(64) NOT NULL,
  `row_number` int(11) NOT NULL,
  `cells` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`cells`)),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_customs_aju_sheet_rows_decl_sheet_row` (`declaration_id`,`sheet_code`,`row_number`),
  CONSTRAINT `customs_aju_sheet_rows_ibfk_1` FOREIGN KEY (`declaration_id`) REFERENCES `customs_declarations` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customs_aju_sheet_rows`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `customs_aju_sheet_rows` WRITE;
/*!40000 ALTER TABLE `customs_aju_sheet_rows` DISABLE KEYS */;
/*!40000 ALTER TABLE `customs_aju_sheet_rows` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `customs_declarations`
--

DROP TABLE IF EXISTS `customs_declarations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `customs_declarations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nomor_aju` varchar(64) NOT NULL,
  `kode_dokumen` varchar(16) DEFAULT NULL,
  `source_label` varchar(255) DEFAULT NULL,
  `versi_template` varchar(32) DEFAULT NULL,
  `meta_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`meta_json`)),
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_customs_declarations_nomor_aju` (`nomor_aju`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customs_declarations`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `customs_declarations` WRITE;
/*!40000 ALTER TABLE `customs_declarations` DISABLE KEYS */;
/*!40000 ALTER TABLE `customs_declarations` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `delivery_details`
--

DROP TABLE IF EXISTS `delivery_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `delivery_details` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `delivery_id` bigint(20) DEFAULT NULL,
  `production_detail_id` bigint(20) DEFAULT NULL,
  `qty` decimal(12,2) DEFAULT NULL,
  `qty_roll` int(11) DEFAULT NULL,
  `qty_pcs` int(11) DEFAULT NULL,
  `weight` decimal(12,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `delivery_id` (`delivery_id`),
  KEY `production_detail_id` (`production_detail_id`),
  CONSTRAINT `delivery_details_ibfk_1` FOREIGN KEY (`delivery_id`) REFERENCES `delivery_headers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `delivery_details_ibfk_2` FOREIGN KEY (`production_detail_id`) REFERENCES `production_details` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `delivery_details`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `delivery_details` WRITE;
/*!40000 ALTER TABLE `delivery_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `delivery_details` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `delivery_headers`
--

DROP TABLE IF EXISTS `delivery_headers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `delivery_headers` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `delivery_number` varchar(100) DEFAULT NULL,
  `customer_id` bigint(20) DEFAULT NULL,
  `delivery_date` date DEFAULT NULL,
  `driver_name` varchar(100) DEFAULT NULL,
  `vehicle_number` varchar(50) DEFAULT NULL,
  `destination` text DEFAULT NULL,
  `status` varchar(32) NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `packing_id` bigint(20) DEFAULT NULL,
  `surat_jalan_printed_at` datetime DEFAULT NULL,
  `bc_number` varchar(80) DEFAULT NULL,
  `bc_date` date DEFAULT NULL,
  `delivery_zone` varchar(16) DEFAULT NULL,
  `delivery_type` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `delivery_number` (`delivery_number`),
  KEY `fk_delivery_headers_packing` (`packing_id`),
  KEY `ix_delivery_headers_customer_id` (`customer_id`),
  CONSTRAINT `delivery_headers_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`),
  CONSTRAINT `fk_delivery_headers_packing` FOREIGN KEY (`packing_id`) REFERENCES `packing_headers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `delivery_headers`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `delivery_headers` WRITE;
/*!40000 ALTER TABLE `delivery_headers` DISABLE KEYS */;
/*!40000 ALTER TABLE `delivery_headers` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `document_sequences`
--

DROP TABLE IF EXISTS `document_sequences`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `document_sequences` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `doc_type` varchar(20) NOT NULL,
  `period` varchar(10) NOT NULL,
  `last_value` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_document_sequences_doc_period` (`doc_type`,`period`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `document_sequences`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `document_sequences` WRITE;
/*!40000 ALTER TABLE `document_sequences` DISABLE KEYS */;
INSERT INTO `document_sequences` VALUES
(1,'SO','202604',4),
(2,'SO','202605',8),
(3,'SO','202606',5);
/*!40000 ALTER TABLE `document_sequences` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `exchange_rates`
--

DROP TABLE IF EXISTS `exchange_rates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `exchange_rates` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `idr_per_usd` decimal(18,4) NOT NULL,
  `effective_date` date NOT NULL,
  `notes` text DEFAULT NULL,
  `created_by` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `valid_from` date DEFAULT NULL,
  `valid_to` date DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exchange_rates`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `exchange_rates` WRITE;
/*!40000 ALTER TABLE `exchange_rates` DISABLE KEYS */;
/*!40000 ALTER TABLE `exchange_rates` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `fluorescent_color_masters`
--

DROP TABLE IF EXISTS `fluorescent_color_masters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `fluorescent_color_masters` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `buyer_code` varchar(32) NOT NULL DEFAULT 'GLOBAL',
  `season_label` varchar(64) DEFAULT NULL,
  `season_year` int(11) DEFAULT NULL,
  `season_type` varchar(16) DEFAULT NULL,
  `color_name` varchar(255) NOT NULL,
  `color_code` varchar(64) DEFAULT NULL,
  `color_class` varchar(32) NOT NULL DEFAULT 'fluorescent',
  `source_file` varchar(255) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_fluorescent_color_master` (`buyer_code`,`season_label`,`color_code`,`color_name`),
  KEY `ix_fluorescent_color_masters_buyer` (`buyer_code`),
  KEY `ix_fluorescent_color_masters_season` (`season_label`)
) ENGINE=InnoDB AUTO_INCREMENT=1678 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fluorescent_color_masters`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `fluorescent_color_masters` WRITE;
/*!40000 ALTER TABLE `fluorescent_color_masters` DISABLE KEYS */;
INSERT INTO `fluorescent_color_masters` VALUES
(1059,'NB','SS 2014',2014,'SS','POISON BERRY','NB 0403757','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1060,'NB','SS 2014',2014,'SS','EXUBERANT PINK','NB 0305152','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1061,'NB','SS 2014',2014,'SS','PINK GLO','NB 0305449','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1062,'NB','SS 2014',2014,'SS','PINK FLAMINGO','NB 0300474','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1063,'NB','SS 2014',2014,'SS','PAPAYA','NB 0201248','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1064,'NB','SS 2014',2014,'SS','ATOMIC YELLOW','NB 0101165','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1065,'NB','SS 2014',2014,'SS','WATERMELON','NB 0201808','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1066,'NB','SS 2014',2014,'SS','BLACK PLUM','NB 0401948','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1067,'NB','SS 2014',2014,'SS','AMETHYST','NB 0403608','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1068,'NB','SS 2014',2014,'SS','SOLAR YELLOW','NB 0101851','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1069,'NB','SS 2014',2014,'SS','GREEN FLASH','NB 0905576','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1070,'NB','SS 2014',2014,'SS','CRIMSON','NB 0301241','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1071,'NB','SS 2014',2014,'SS','RUBY RED','NB 0201534','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1072,'NB','SS 2014',2014,'SS','COSMIC CORAL','NB 0202575','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1073,'NB','FW 2014',2014,'FW','VELOCITY RED','NB 0301062','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1074,'NB','FW 2014',2014,'FW','UV BLUE','NB 0505941','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1075,'NB','FW 2014',2014,'FW','BUBBLEGUM','NB 0301444','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1076,'NB','FW 2014',2014,'FW','DYNOMITE','NB 0202944','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1077,'NB','FW 2014',2014,'FW','DRAGONFLY','NB 0102901','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1078,'NB','FW 2014',2014,'FW','IGNITE','NB 0305058','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1079,'NB','FW 2014',2014,'FW','MULBERRY','NB 0402523','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1080,'NB','FW 2014',2014,'FW','PLUM','NB 0402253','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1081,'NB','FW 2014',2014,'FW','HI-LITE','NB 0102097','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1082,'NB','FW 2014',2014,'FW','SOLAR YELLOW','NB 0101851','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1083,'NB','FW 2014',2014,'FW','CARNIVAL','NB 0303529','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1084,'NB','FW 2014',2014,'FW','CHEMICAL GREEN','NB 0906179','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1085,'NB','FW 2014',2014,'FW','BENGAL TIGER','NB 0200461','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1086,'NB','FW 2014',2014,'FW','FIREBALL','NB 0201617','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1087,'NB','Q1 & Q2 2015',2015,'SS','HI-LIFE','NB 0102097','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1088,'NB','Q1 & Q2 2015',2015,'SS','ACIDIC GREEN','NB 0906219','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1089,'NB','Q1 & Q2 2015',2015,'SS','CHEMICAL GREEN','NB 0906179','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1090,'NB','Q1 & Q2 2015',2015,'SS','AMP PINK','NB 0305438','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1091,'NB','Q1 & Q2 2015',2015,'SS','VOLTAGE VIOLET','NB 0403884','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1092,'NB','Q1 & Q2 2015',2015,'SS','FIJI','NB 0202908','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1093,'NB','Q1 & Q2 2015',2015,'SS','BRIGHT CHERRY','NB 0305515','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1094,'NB','Q1 & Q2 2015',2015,'SS','DYNOMITE','NB 0202944','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1095,'NB','Q1 & Q2 2015',2015,'SS','BOLD CITRUS','NB 0202931','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1096,'NB','Q1 & Q2 2015',2015,'SS','AFRICAN VIOLET','NB 0402698','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1097,'NB','Q1 & Q2 2015',2015,'SS','VIVID ROSE','NB 0305610','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1098,'NB','Q1 & Q2 2015',2015,'SS','POPSICLE PINK','NB 0302939','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1099,'NB','Q1 & Q2 2015',2015,'SS','INDIAN ROSE','NB 0402040','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1100,'NB','Q1 & Q2 2015',2015,'SS','BLUSH','NB 0301009','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1101,'NB','Q1 & Q2 2015',2015,'SS','PINK FRAMINGO','NB 0300474','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1102,'NB','Q1 & Q2 2015',2015,'SS','VELOCITY RED','NB 0301062','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1103,'NB','Q3 & Q4 2015',2015,'FW','EMBERS','NB 0303760','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1104,'NB','Q3 & Q4 2015',2015,'FW','CERISE','NB 0305185','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1105,'NB','Q3 & Q4 2015',2015,'FW','EXUBERANT PINK','NB 0305152','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1106,'NB','Q3 & Q4 2015',2015,'FW','DEEP ORCHID','NB 0400719','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1107,'NB','Q3 & Q4 2015',2015,'FW','IMPERIAL','NB 0401994','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1108,'NB','Q3 & Q4 2015',2015,'FW','HI-LITE','NB 0102097','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1109,'NB','Q3 & Q4 2015',2015,'FW','PINK ZING','NB 0305404','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1110,'NB','Q1 & Q2 2016',2016,'SS','LAVA','NB 0202932','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1111,'NB','Q1 & Q2 2016',2016,'SS','IMPULSE','NB 0203256','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1112,'NB','Q1 & Q2 2016',2016,'SS','DRAGONFLY','NB 0102901','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1113,'NB','Q1 & Q2 2016',2016,'SS','COSMIC CORAL','NB 0202575','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1114,'NB','Q1 & Q2 2016',2016,'SS','AMP PINK','NB 0305438','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1115,'NB','Q1 & Q2 2016',2016,'SS','VIPER','NB 0102106','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1116,'NB','Q1 & Q2 2016',2016,'SS','TOXIC','NB 0906764','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1117,'NB','Q1 & Q2 2016',2016,'SS','BENGAL TIGER','NB 0200461','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1118,'NB','Q1 & Q2 2016',2016,'SS','APRICOT','NB 0200218','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1119,'NB','Q1 & Q2 2016',2016,'SS','CORAL GLOW','NB 0201643','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1120,'NB','Q1 & Q2 2016',2016,'SS','FIREBALL','NB 0201617','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1121,'NB','Q1 & Q2 2016',2016,'SS','AZALEA','NB 0403733','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1122,'NB','Q1 & Q2 2016',2016,'SS','CARNIVAL','NB 0303529','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1123,'NB','Q1 & Q2 2016',2016,'SS','PINK FLAMINGO','NB 0300474','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1124,'NB','Q1 & Q2 2016',2016,'SS','PACIFIC','NB 0505943','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1125,'NB',NULL,NULL,NULL,'SILVER (877C)','877C','metallic','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1126,'NB','Q3&Q4’16',NULL,'FW','IMPULSE','NB 0203256','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1127,'NB','Q3&Q4’16',NULL,'FW','AQUARIUS','NB 0602257','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1128,'NB','Q3&Q4’16',NULL,'FW','BRIGHT CHERRY','NB 0305515','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1129,'NB','Q3&Q4’16',NULL,'FW','POISON BERRY','NB 0403757','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1130,'NB','Q3&Q4’16',NULL,'FW','TOXIC','NB 0906764','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1131,'NB','Q3&Q4’16',NULL,'FW','ATOMIC','NB-F16-6438','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1132,'NB','Q3&Q4’16',NULL,'FW','FIREFLY','NB-F16-2384','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1133,'NB','Q3&Q4’16',NULL,'FW','PEONY','NB-F16-6410','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1134,'NB','Q3&Q4’16',NULL,'FW','GUAVA','NB-F16-6411','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1135,'NB','Q3&Q4’16',NULL,'FW','NEBULA','NB-F16-6412','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1136,'NB','Q3&Q4’16',NULL,'FW','PLASMA','NB-F16-3313','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1137,'NB','Q3&Q4’16',NULL,'FW','FUSION','NB-F16-4196','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1138,'ADIDAS','constants',NULL,NULL,'solar yellow (electricity)','082A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1139,'ADIDAS','constants',NULL,NULL,'solar gold','A1U4','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1140,'ADIDAS','constants',NULL,NULL,'solar green','A1U3','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1141,'ADIDAS','constants',NULL,NULL,'solar pink','A1U1','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1142,'ADIDAS','constants',NULL,NULL,'solar slime (slime)','084A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1143,'ADIDAS','constants',NULL,NULL,'macaw','A0U0','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1144,'ADIDAS','constants',NULL,NULL,'spark','085A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1145,'ADIDAS','constants',NULL,NULL,'zest','086A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1146,'ADIDAS','constants',NULL,NULL,'solar orange (warning)','087A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1147,'ADIDAS','constants',NULL,NULL,'solar red (infrared)','088A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1148,'ADIDAS','constants',NULL,NULL,'pop','089A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1149,'ADIDAS','Team Colors',NULL,NULL,'Team Solar Green','ADFL','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1150,'ADIDAS','Team Colors',NULL,NULL,'Team Solar Yellow','ADFN','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1151,'ADIDAS','Team Colors',NULL,NULL,'Team Solar Orange','ADFM','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1152,'ADIDAS','Team Colors',NULL,NULL,'Team Shock Pink','ADFF','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1153,'ADIDAS','SS 2026',2026,'SS','Ice Tangerine S26','AE7V','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1154,'ADIDAS','SS 2026',2026,'SS','Lucid Orange S26','AE7Y','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1155,'ADIDAS','SS 2026',2026,'SS','Lucid Tangerine S26','AE85','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1156,'ADIDAS','SS 2026',2026,'SS','Pure Orange S26','AE9H','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1157,'ADIDAS','SS 2026',2026,'SS','Pure Tangerine S26','AEAQ','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1158,'ADIDAS','FW 2025',2025,'FW','Lime Burst F25','AFH4','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1159,'ADIDAS','SS 2025',2025,'SS','Lucid Red S25','AFDD','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1160,'ADIDAS','FW 2024',2024,'FW','Pink Spark F24','AFAJ','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1161,'ADIDAS','FW 2024',2024,'FW','Purple Burst F24','AFAM','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1162,'ADIDAS','SS 2024',2024,'SS','Spark S24','AF47','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1163,'ADIDAS','SS 2024',2024,'SS','Semi Green Spark S24','AF4B','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1164,'ADIDAS','SS 2024',2024,'SS','Green Spark S24','AF4A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1165,'ADIDAS','FW 2023',2023,'FW','Flash Aqua F23','AEWR','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1166,'ADIDAS','FW 2023',2023,'FW','Lucid Cyan F23','AEWW','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1167,'ADIDAS','FW 2023',2023,'FW','Lucid Lemon F23','AEWQ','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1168,'ADIDAS','FW 2023',2023,'FW','Lucid Lime F23','AEWV','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1169,'ADIDAS','FW 2023',2023,'FW','Lucid Pink F23','AEYV','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1170,'ADIDAS','SS 2023',2023,'SS','Lucid FuchsiaS23','AETJ','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1171,'ADIDAS','FW 2022',2022,'FW','Bliss Blue F22','AEJV','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1172,'ADIDAS','FW 2022',2022,'FW','Beam Yellow F22','AEJW','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1173,'ADIDAS','FW 2022',2022,'FW','Beam Orange F22','AEJX','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1174,'ADIDAS','FW 2022',2022,'FW','Beam Pink F22','AEJY','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1175,'ADIDAS','FW 2022',2022,'FW','Beam Green F22','AEJZ','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1176,'ADIDAS','FW 2022',2022,'FW','Impact Orange F22','AEK3','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1177,'ADIDAS','SS 2022',2022,'SS','Orange Rush S22','AECX','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1178,'ADIDAS','SS 2022',2022,'SS','Mint Rush S22','AECY','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1179,'ADIDAS','SS 2022',2022,'SS','Acid Red S22','AED5','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1180,'ADIDAS','SS 2022',2022,'SS','Pulse Mint S22','AED9','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1181,'ADIDAS','SS 2022',2022,'SS','Turbo S22','AEDZ','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1182,'ADIDAS','SS 2022',2022,'SS','Semi Mint Rush S22','AEE5','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1183,'ADIDAS','FW 2021',2021,'FW','Pulse Aqua F21','AE6F','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1184,'ADIDAS','FW 2021',2021,'FW','Screaming Green F21','AE6V','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1185,'ADIDAS','FW 2021',2021,'FW','Semi Screaming Green F21','AE78','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1186,'ADIDAS','SS 2021',2021,'SS','Acid Orange S21','ADVW','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1187,'ADIDAS','SS 2021',2021,'SS','Screaming Orange S21','ADW1','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1188,'ADIDAS','SS 2021',2021,'SS','Acid Yellow S21','ADW6','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1189,'ADIDAS','SS 2021',2021,'SS','Screaming Pink S21','ADWS','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1190,'ADIDAS','FW 2020',2020,'FW','signal pink F20','ADL3','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1191,'ADIDAS','FW 2020',2020,'FW','signal orange F20','ADL4','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1192,'ADIDAS','FW 2020',2020,'FW','APP signal orange F20','ADPU','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1193,'ADIDAS','SS 2020',2020,'SS','signal coral S20','ADAK','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1194,'ADIDAS','SS 2020',2020,'SS','signal green S20','ADB5','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1195,'ADIDAS','FW 2019',2019,'FW','hi-res coral F19','ACET','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1196,'ADIDAS','FW 2019',2019,'FW','flash orange F19','ACE5','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1197,'ADIDAS','SS 2019',2019,'SS','hi-res yellow S19','ABZK','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1198,'ADIDAS','SS 2019',2019,'SS','shock red S19','ABZL','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1199,'ADIDAS','FW 2018',2018,'FW','clear orange F18','AAXW','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1200,'ADIDAS','FW 2018',2018,'FW','hi-res aqua F18','AAY2','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1201,'ADIDAS','FW 2018',2018,'FW','shock lime F18','AAY3','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1202,'ADIDAS','FW 2018',2018,'FW','shock pink F18','AAYD','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1203,'ADIDAS','SS 2018',2018,'SS','hi-res green S18','AAFX','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1204,'ADIDAS','SS 2018',2018,'SS','hi-res orange S18','AAG2','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1205,'ADIDAS','SS 2018',2018,'SS','real gold S18','AAG1','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1206,'ADIDAS','FW 2017',2017,'FW','energy aqua F17','AA2J','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1207,'ADIDAS','SS 2017',2017,'SS','easy green S17','A9MS','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1208,'ADIDAS','SS 2017',2017,'SS','haze coral S17','A9MV','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1209,'ADIDAS','SS 2017',2017,'SS','energy blue S17','A9MY','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1210,'ADIDAS','SS 2017',2017,'SS','energy green S17','A9MZ','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1211,'ADIDAS','FW 2016',2016,'FW','shock slime F16','A98G','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1212,'ADIDAS','FW 2016',2016,'FW','shock purple F16','A98J','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1213,'ADIDAS','SS 2016',2016,'SS','shock mint S16','A8M7','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1214,'ADIDAS','SS 2016',2016,'SS','shock green S16','A8L1','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1215,'ADIDAS','SS 2016',2016,'SS','shock pink S16','A8KG','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1216,'ADIDAS','SS 2016',2016,'SS','shock red S16','A8KC','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1217,'ADIDAS','SS 2016',2016,'SS','solar lime S16','A8KW','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1218,'ADIDAS','SS 2016',2016,'SS','eqt orange S16','A8K7','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1219,'ADIDAS','SS 2016',2016,'SS','pink glow S16','A8KH','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1220,'ADIDAS','SS 2016',2016,'SS','green glow S16','A8L2','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1221,'ADIDAS','SS 2016',2016,'SS','sun glow S16','A8K9','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1222,'ADIDAS','SS 2016',2016,'SS','spring green S16-ST','A8MG','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1223,'ADIDAS','FW 2015',2015,'FW','flash lime F15','A7ZC','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1224,'ADIDAS','FW 2015',2015,'FW','frozen yellow F15','A7Z2','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1225,'ADIDAS','SS 2015',2015,'SS','light flash yellow S15','A7LV','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1226,'ADIDAS','SS 2015',2015,'SS','light flash orange S15','A7L4','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1227,'ADIDAS','SS 2015',2015,'SS','light flash red S15','A7L3','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1228,'ADIDAS','SS 2015',2015,'SS','light flash green S15','A7L5','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1229,'ADIDAS','SS 2015',2015,'SS','flash red S15','A7L6','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1230,'ADIDAS','SS 2015',2015,'SS','flash orange S15','A7L7','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1231,'ADIDAS','SS 2015',2015,'SS','flash green S15','A7L8','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1232,'ADIDAS','SS 2015',2015,'SS','flash pink S15','A7LA','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1233,'ADIDAS','SS 2015',2015,'SS','bright green S15','A7L2','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1234,'ADIDAS','SS 2014',2014,'SS','glow S14','A6WH','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1235,'ADIDAS','SS 2014',2014,'SS','glow orange S14','A6W1','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1236,'ADIDAS','SS 2013',2013,'SS','vivid pink S13','A62B','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1237,'ADIDAS','SS 2013',2013,'SS','pink zest S13','A61Y','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1238,'ADIDAS','SS 2013',2013,'SS','green zest S13','A621','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1239,'ADIDAS','SS 2013',2013,'SS','red zest S13','A61X','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1240,'ADIDAS','SS 2013',2013,'SS','haze coral S13','A61K','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1241,'ADIDAS','SS 2012',2012,'SS','ultra glow S12','A521','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1242,'ADIDAS','SS 2012',2012,'SS','ultra bright S12','A522','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1243,'ADIDAS','SS 2012',2012,'SS','ultra green S12','A525','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1244,'ADIDAS','SS 2012',2012,'SS','ultra pop S12','A53V','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1245,'ADIDAS','FW 2012',2012,'FW','hyper green F12','A5NC','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1246,'ADIDAS','FW 2012',2012,'FW','hyper orange F12','A5MT','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1247,'ADIDAS','FW 2012',2012,'FW','hyper pop F12','A5N4','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1248,'ADIDAS','FW 2011',2011,'FW','turbo F11','A3MC','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1249,'ADIDAS','FW 2011',2011,'FW','intense orange F11','A3MA','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1250,'ADIDAS','SS 2011',2011,'SS','fresh gold S11','A3D6','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1251,'ADIDAS','FW 2010',2010,'FW','wonder glow F10','A327','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1252,'ADIDAS','FW 2010',2010,'FW','radiant gold F10','A32B','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1253,'ADIDAS','SS 2010',2010,'SS','no fluorescent color',NULL,'fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1254,'ADIDAS','FW 2009',2009,'FW','high yellow F09','A2HK','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1255,'ADIDAS','SS 2009',2009,'SS','fluro green S09','A29F','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1256,'ADIDAS','SS 2009',2009,'SS','fluro S09','A29S','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1257,'ADIDAS','SS 2009',2009,'SS','neon red S09','A29U','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1258,'ADIDAS','SS 2009',2009,'SS','neon yellow S09','A29M','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1259,'ADIDAS','SS 2009',2009,'SS','nu orange S09','A29Q','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1260,'ADIDAS','SS 2008',2008,'SS','lucid red F08','A1MP','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1261,'GLOBAL','SP/SU 09',NULL,'SS','Mean Green','30H','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1262,'GLOBAL','SP01',NULL,'SS','Crystal Green','30M','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1263,'GLOBAL','SP01',NULL,'SS','Bright Teal','30T','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1264,'GLOBAL','SP/SU 14',NULL,'SS','Venom Green','30V','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1265,'GLOBAL','FA/HO 19',NULL,'FW','Scream Green','32C','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1266,'GLOBAL','SP02',NULL,'SS','Aquamarine','32D','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1267,'GLOBAL','SP/SU 10',NULL,'SS','Bright Cactus','32M','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1268,'GLOBAL','SP/SU 13',NULL,'SS','Poison Green','33C','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1269,'GLOBAL','SP04',NULL,'SS','Cactus','33K','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1270,'GLOBAL','SP/SU 14',NULL,'SS','Lt Lucid Green','33V','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1271,'GLOBAL','SP/SU 09',NULL,'SS','Liquid Lime','34A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1272,'GLOBAL','FA/HO 10',NULL,'FW','Hot Lime','34C','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1273,'GLOBAL','SPSU 24',NULL,'SS','Clear Jade','34N','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1274,'GLOBAL','SU08',NULL,NULL,'Lime','34R','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1275,'GLOBAL','SU08',NULL,NULL,'Tourmaline','35A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1276,'GLOBAL','SP11',NULL,'SS','Neo Lime','35H','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1277,'GLOBAL','SP/SU 13',NULL,'SS','Crystal Mint','36A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1278,'GLOBAL','SP10',NULL,'SS','Cool Mint','36C','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1279,'GLOBAL','SP/SU 10',NULL,'SS','Electric Green','36E','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1280,'GLOBAL','SP05',NULL,'SS','Green Spark','36F','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1281,'GLOBAL','SP11',NULL,'SS','Green Apple','36N','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1282,'GLOBAL','SP/SU 09',NULL,'SS','Citron','38D','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1283,'GLOBAL','SP04',NULL,'SS','Bright Kiwi','39S','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1284,'GLOBAL','SP/SU 15',NULL,'SS','Lt Poison Green','3BK','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1285,'GLOBAL','FA/HO 11',NULL,'FW','High Voltage','3CE','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1286,'GLOBAL','SP02',NULL,'SS','Lime Chill','3CK','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1287,'GLOBAL','SP02',NULL,'SS','Cyber','3CN','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1288,'GLOBAL','SP08',NULL,'SS','Lt Green Spark','3EC','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1289,'GLOBAL','SP06',NULL,'SS','Atomic Green','3EK','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1290,'GLOBAL','SP07',NULL,'SS','Radiant Green','3FI','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1291,'GLOBAL','SP07',NULL,'SS','Clear Jade II','3FL','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1292,'GLOBAL','SP/SU 09',NULL,'SS','Electrolime','3GH','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1293,'GLOBAL','SP/SU 12',NULL,'SS','Action Green','3HN','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1294,'GLOBAL','SP/SU 13',NULL,'SS','Atomic Teal','3JL','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1295,'GLOBAL','FA/HO 14',NULL,'FW','Hyper Jade','3JZ','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1296,'GLOBAL','FA/HO 13',NULL,'FW','Green Glow','3KC','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1297,'GLOBAL','FA/HO 13',NULL,'FW','Flash Lime','3KJ','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1298,'GLOBAL','SP/SU 15',NULL,'SS','Menta','3KT','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1299,'GLOBAL','FA/HO 15',NULL,'FW','Green Shock','3KV','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1300,'GLOBAL','FA/HO 15',NULL,'FW','Green Strike','3KX','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1301,'GLOBAL','FA/HO 15',NULL,'FW','Electro Green','3KY','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1302,'GLOBAL','FA/HO 15',NULL,'FW','Voltage Green','3KZ','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1303,'GLOBAL','FA/HO 15',NULL,'FW','Ghost Green','3LH','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1304,'GLOBAL','SP/SU 16',NULL,'SS','Rage Green','3LL','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1305,'GLOBAL','FA/HO 17',NULL,'FW','Aphid Green','3LP','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1306,'GLOBAL','FA/HO 17',NULL,'FW','Illusion Green','3LV','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1307,'GLOBAL','FA/HO 17',NULL,'FW','Aurora Green','3LW','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1308,'GLOBAL','FA/HO 18',NULL,'FW','Lime Blast','3NC','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1309,'GLOBAL','SP/SU 20',NULL,'SS','Oracle Aqua','3PL','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1310,'GLOBAL','SPSU 23',NULL,'SS','Sub Lime','3QL','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1311,'GLOBAL','SP/SU 21',NULL,'SS','Lime Glow','3QM','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1312,'GLOBAL','SPSU 23',NULL,'SS','Electric Algae','3QT','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1313,'GLOBAL','FAHO 23',NULL,'FW','Sky J Lt Olive','3QU','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1314,'GLOBAL','SP04',NULL,'SS','Photo Blue','40W','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1315,'GLOBAL','SP03',NULL,'SS','Orion Blue','41C','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1316,'GLOBAL','FA/HO 10',NULL,'FW','Retro','46Y','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1317,'GLOBAL','SP/SU 14',NULL,'SS','Polarized Blue','4AU','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1318,'GLOBAL','FA03',NULL,NULL,'Sea Blue','4DN','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1319,'GLOBAL','SPSU 23',NULL,'SS','Aero Blue','4ES','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1320,'GLOBAL','SPSU\'22',NULL,'SS','Turquoise Blue','4GT','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1321,'GLOBAL','SP/SU 15',NULL,'SS','Blue Lagoon','4JV','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1322,'GLOBAL','SP/SU 16',NULL,'SS','Racer Blue','4ME','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1323,'GLOBAL','SPSU\'22',NULL,'SS','Indigo Burst','4NL','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1324,'GLOBAL','SPSU\'22',NULL,'SS','Hyper Royal','4NP','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1325,'GLOBAL','SPSU 23',NULL,'SS','Blue Lightening','4QZ','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1326,'GLOBAL','FAHO 23',NULL,'FW','Blue Joy','4RC','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1327,'GLOBAL','FA/HO 19',NULL,'FW','Voltage Purple','50A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1328,'GLOBAL','FA02',NULL,NULL,'Dark Concord','50G','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1329,'GLOBAL','SP/SU 14',NULL,'SS','Bright Grape','50J','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1330,'GLOBAL','FA/HO 12',NULL,'FW','Viola','50Q','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1331,'GLOBAL','SP02',NULL,'SS','Viotech','50Z','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1332,'GLOBAL','SP08',NULL,'SS','Red Plum','51G','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1333,'GLOBAL','SP03',NULL,'SS','Violet Pop','51T','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1334,'GLOBAL','SP05',NULL,'SS','Magenta','52C','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1335,'GLOBAL','SP/SU 21',NULL,'SS','Wild Berry','52H','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1336,'GLOBAL','SP11',NULL,'SS','Bright Violet','52I','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1337,'GLOBAL','SP/SU 14',NULL,'SS','Bright Magenta','53B','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1338,'GLOBAL','SPSU\'22',NULL,'SS','Persian Violet','54A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1339,'GLOBAL','FA/HO 09',NULL,'FW','New Magenta','54C','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1340,'GLOBAL','SP/SU 14',NULL,'SS','Purple Venom','54U','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1341,'GLOBAL','SP00',NULL,'SS','Purple Passion','55D','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1342,'GLOBAL','FA/HO 11',NULL,'FW','Bold Berry','55N','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1343,'GLOBAL','SP/SU 13',NULL,'SS','Atomic Purple','55Z','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1344,'GLOBAL','FA/HO 11',NULL,'FW','Vivid Grape','56A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1345,'GLOBAL','SP/SU 13',NULL,'SS','Laser Purple','56H','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1346,'GLOBAL','SP/SU 13',NULL,'SS','Violet Force','56M','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1347,'GLOBAL','FAHO 23',NULL,'FW','Electro Purple','56S','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1348,'GLOBAL','SP/SU 09',NULL,'SS','Pure Purple','57A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1349,'GLOBAL','SPSU 23',NULL,'SS','Grape Ice','57E','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1350,'GLOBAL','FA/HO 14',NULL,'FW','Hyper Grape','57Q','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1351,'GLOBAL','SP/SU 15',NULL,'SS','Fuchsia Flash','57R','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1352,'GLOBAL','SP/SU 15',NULL,'SS','Fuchsia Glow','57S','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1353,'GLOBAL','SP/SU 15',NULL,'SS','Medium Berry','57T','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1354,'GLOBAL','FA/HO 15',NULL,'FW','Vivid Purple','57V','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1355,'GLOBAL','SP/SU 20',NULL,'SS','Eggplant','58A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1356,'GLOBAL','SP/SU 14',NULL,'SS','Red Violet','58D','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1357,'GLOBAL','SPSU 24',NULL,'SS','Hot Fuchsia','58E','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1358,'GLOBAL','FAHO 23',NULL,'FW','Lt Ultramarine','58I','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1359,'GLOBAL','SP/SU 16',NULL,'SS','Cosmic Purple','58S','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1360,'GLOBAL','SP/SU 16',NULL,'SS','Hyper Violet','58T','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1361,'GLOBAL','SP/SU 16',NULL,'SS','Fierce Purple','58U','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1362,'GLOBAL','SP/SU 16',NULL,'SS','Dynamic Berry','58W','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1363,'GLOBAL','SP06',NULL,'SS','Vivid Violet','59R','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1364,'GLOBAL','FA/HO 17',NULL,'FW','Action Grape','5AE','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1365,'GLOBAL','SP/SU 18',NULL,'SS','Rush Fuchsia','5AP','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1366,'GLOBAL','SP/SU 18',NULL,'SS','Fuchsia Blast','5AR','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1367,'GLOBAL','SP/SU 18',NULL,'SS','Hyper Magenta','5AS','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1368,'GLOBAL','FA/HO 20',NULL,'FW','Purple Nebula','5BG','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1369,'GLOBAL','FA/HO 19',NULL,'FW','Psychic Purple','5BP','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1370,'GLOBAL','FA/HO 20',NULL,'FW','Cactus Flower','5BQ','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1371,'GLOBAL','SPSU 23',NULL,'SS','Fuchsia Dream','5BZ','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1372,'GLOBAL','FAHO 23',NULL,'FW','Disco Purple','5CF','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1373,'GLOBAL','FAHO 23',NULL,'FW','Purple Cosmos','5CG','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1374,'GLOBAL','FA/HO 09',NULL,'FW','China Rose','60I','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1375,'GLOBAL','FA/HO 10',NULL,'FW','Voltage Cherry','60K','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1376,'GLOBAL','SP01',NULL,'SS','Light Hot Red','60X','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1377,'GLOBAL','SP07',NULL,'SS','Light Lava','61E','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1378,'GLOBAL','SP/SU 10',NULL,'SS','Rose','61G','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1379,'GLOBAL','SP04',NULL,'SS','Hot Pink','61H','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1380,'GLOBAL','FA/HO 10',NULL,'FW','Wineberry','61K','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1381,'GLOBAL','FA/HO 14',NULL,'FW','Hyper Punch','61U','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1382,'GLOBAL','SP/SU 14',NULL,'SS','Geranium','62A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1383,'GLOBAL','SP05',NULL,'SS','Pimento','62F','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1384,'GLOBAL','FA/HO 11',NULL,'FW','Bright Cerise','62J','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1385,'GLOBAL','FA/HO 11',NULL,'FW','Cherry','63C','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1386,'GLOBAL','SP/SU 16',NULL,'SS','Fire Pink','63D','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1387,'GLOBAL','HO11',NULL,'FW','Laser Pink','63K','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1388,'GLOBAL','SPSU 23',NULL,'SS','Fire Red','64D','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1389,'GLOBAL','SP/SU 10',NULL,'SS','Pink Flash','64F','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1390,'GLOBAL','FA/HO 10',NULL,'FW','Solar Red','64G','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1391,'GLOBAL','FA/HO 09',NULL,'FW','Hot Red','64H','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1392,'GLOBAL','SP/SU 15',NULL,'SS','Rio','64U','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1393,'GLOBAL','FA04',NULL,NULL,'Flame','65D','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1394,'GLOBAL','SU08',NULL,NULL,'Coral Chalk','65H','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1395,'GLOBAL','SP/SU 12',NULL,'SS','University Red','65N','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1396,'GLOBAL','FA/HO 13',NULL,'FW','Pink Foil','66B','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1397,'GLOBAL','SP06',NULL,'SS','Flame Red','66D','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1398,'GLOBAL','SP/SU 09',NULL,'SS','Light Rose','66J','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1399,'GLOBAL','SP03',NULL,'SS','Lotus Pink','66L','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1400,'GLOBAL','FA08',NULL,NULL,'Pinkfire II','66Z','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1401,'GLOBAL','SP10',NULL,'SS','Crimson','67B','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1402,'GLOBAL','FA/HO 18',NULL,'FW','Watermelon','67G','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1403,'GLOBAL','HO08',NULL,'FW','Chile Red','67J','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1404,'GLOBAL','SP/SU 18',NULL,'SS','Wild Cherry','67K','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1405,'GLOBAL','FA02',NULL,NULL,'Coral Rose','67L','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1406,'GLOBAL','FA08',NULL,NULL,'Dark Red','68C','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1407,'GLOBAL','SP06',NULL,'SS','Wild Mango','68E','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1408,'GLOBAL','SP/SU 14',NULL,'SS','Laser Crimson','68U','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1409,'GLOBAL','SP/SU 14',NULL,'SS','Legion Red','68V','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1410,'GLOBAL','SP/SU 10',NULL,'SS','Vivid Pink','68X','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1411,'GLOBAL','SP/SU 09',NULL,'SS','Brilliant Magenta','68Y','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1412,'GLOBAL','HO11',NULL,'FW','Desert Pink','69A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1413,'GLOBAL','FA/HO 12',NULL,'FW','Berry','69B','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1414,'GLOBAL','SP/SU 08',NULL,'SS','Bright Fuchsia','69H','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1415,'GLOBAL','SP11',NULL,'SS','Spark','6AG','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1416,'GLOBAL','SP/SU 15',NULL,'SS','Sunblush','6BC','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1417,'GLOBAL','FA/HO 10',NULL,'FW','Daring Red','6BN','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1418,'GLOBAL','SP/SU 14',NULL,'SS','Pink Glow','6BU','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1419,'GLOBAL','SP08',NULL,'SS','Alarming','6BX','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1420,'GLOBAL','FA/HO 12',NULL,'FW','Bright Crimson','6CD','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1421,'GLOBAL','SP/SU 10',NULL,'SS','Challenge Red','6CG','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1422,'GLOBAL','FA/HO 09',NULL,'FW','Very Berry','6CM','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1423,'GLOBAL','SP10',NULL,'SS','Aster Pink','6CR','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1424,'GLOBAL','SPSU\'22',NULL,'SS','Sangria','6CS','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1425,'GLOBAL','FA/HO 14',NULL,'FW','Hyper Pink','6CV','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1426,'GLOBAL','SP/SU 12',NULL,'SS','Lt Vltge Cherry','6CW','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1427,'GLOBAL','FA/HO 10',NULL,'FW','Lt Wild Mango','6CX','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1428,'GLOBAL','SP11',NULL,'SS','Gym Pink','6CZ','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1429,'GLOBAL','SP/SU 14',NULL,'SS','Lt Crimson','6DA','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1430,'GLOBAL','FA/HO 11',NULL,'FW','Scarlet Fire','6DG','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1431,'GLOBAL','SP/SU 12',NULL,'SS','Action Red','6DK','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1432,'GLOBAL','SP/SU 12',NULL,'SS','Hot Punch','6DP','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1433,'GLOBAL','SP/SU 12',NULL,'SS','Siren Red','6DQ','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1434,'GLOBAL','FA/HO 14',NULL,'FW','Infrared','6DU','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1435,'GLOBAL','FA/HO 12',NULL,'FW','Fireberry','6DX','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1436,'GLOBAL','SP/SU 13',NULL,'SS','Hyper Red','6EF','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1437,'GLOBAL','SP/SU 13',NULL,'SS','Pink Force','6EH','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1438,'GLOBAL','SP/SU 13',NULL,'SS','Dynamic Pink','6EI','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1439,'GLOBAL','SP/SU 13',NULL,'SS','Digital Pink','6EK','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1440,'GLOBAL','SP/SU 13',NULL,'SS','Polarized Pink','6EL','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1441,'GLOBAL','SP/SU 13',NULL,'SS','Fusion Pink','6EM','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1442,'GLOBAL','SP/SU 13',NULL,'SS','Ion Pink','6EN','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1443,'GLOBAL','FA/HO 13',NULL,'FW','Atomic Red','6EQ','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1444,'GLOBAL','FA/HO 13',NULL,'FW','Distance Red','6ER','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1445,'GLOBAL','FA/HO 13',NULL,'FW','Fusion Red','6ES','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1446,'GLOBAL','FA/HO 13',NULL,'FW','Atomic Pink','6ET','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1447,'GLOBAL','FA/HO 14',NULL,'FW','Fuchsia Force','6EU','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1448,'GLOBAL','FA/HO 13',NULL,'FW','Hyper Fuchsia','6EZ','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1449,'GLOBAL','FA/HO 13',NULL,'FW','Club Pink','6FF','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1450,'GLOBAL','SP/SU 15',NULL,'SS','Dk Fireberry','6FK','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1451,'GLOBAL','SP/SU 15',NULL,'SS','Pink Pow','6FM','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1452,'GLOBAL','SP/SU 15',NULL,'SS','Lava Glow','6FN','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1453,'GLOBAL','SP/SU 16',NULL,'SS','Prime Red','6FQ','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1454,'GLOBAL','FA/HO 15',NULL,'FW','Pinksicle','6FS','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1455,'GLOBAL','SP/SU 16',NULL,'SS','Pink Blast','6FT','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1456,'GLOBAL','FA/HO 16',NULL,'FW','Fuchsia Flux','6FV','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1457,'GLOBAL','SP/SU 17',NULL,'SS','Racer Pink','6FW','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1458,'GLOBAL','SP/SU 17',NULL,'SS','Track Red','6FX','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1459,'GLOBAL','FA/HO 17',NULL,'FW','Deadly Pink','6FZ','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1460,'GLOBAL','FA/HO 17',NULL,'FW','Lethal Pink','6GB','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1461,'GLOBAL','FA/HO 17',NULL,'FW','Lethal Fuchsia','6GE','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1462,'GLOBAL','FA/HO 17',NULL,'FW','Rush Red','6GG','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1463,'GLOBAL','FA/HO 17',NULL,'FW','Pink Nebula','6GH','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1464,'GLOBAL','FA/HO 17',NULL,'FW','Lt Fusion Red','6GJ','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1465,'GLOBAL','SP/SU 18',NULL,'SS','Sunset Pulse','6GL','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1466,'GLOBAL','SP/SU 18',NULL,'SS','Speed Red','6GN','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1467,'GLOBAL','SP/SU 18',NULL,'SS','Tropical Pink','6GT','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1468,'GLOBAL','SP/SU 18',NULL,'SS','Arctic Punch','6GZ','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1469,'GLOBAL','SP/SU 18',NULL,'SS','Pink Beam','6HA','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1470,'GLOBAL','SP/SU 18',NULL,'SS','Rush Pink','6HB','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1471,'GLOBAL','SP/SU 18',NULL,'SS','Lt Atomic Pink','6HC','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1472,'GLOBAL','SPSU\'22',NULL,'SS','Crimson Bliss','6HD','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1473,'GLOBAL','SP/SU 18',NULL,'SS','Habernero Red','6HE','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1474,'GLOBAL','SP/SU 19',NULL,'SS','Mystic Red','6HF','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1475,'GLOBAL','SP/SU 19',NULL,'SS','Active Fuchsia','6HJ','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1476,'GLOBAL','FA/HO 18',NULL,'FW','Pink Tint','6HK','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1477,'GLOBAL','FA/HO 18',NULL,'FW','Oracle Pink','6HL','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1478,'GLOBAL','FA/HO 18',NULL,'FW','Flash Crimson','6HR','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1479,'GLOBAL','FA/HO 18',NULL,'FW','Red Orbit','6HS','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1480,'GLOBAL','SP/SU 19',NULL,'SS','Psychic Pink','6HT','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1481,'GLOBAL','FA/HO 18',NULL,'FW','Pink Prime','6HU','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1482,'GLOBAL','FA/HO 18',NULL,'FW','Active Pink','6HV','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1483,'GLOBAL','SP/SU 19',NULL,'SS','Laser Fuchsia','6JD','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1484,'GLOBAL','SP/SU 19',NULL,'SS','Pink Gaze','6JF','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1485,'GLOBAL','SPSU 23',NULL,'SS','Global Red','6KL','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1486,'GLOBAL','SPSU\'22',NULL,'SS','Mystic Hibiscus','6LB','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1487,'GLOBAL','SPSU 23',NULL,'SS','Picante Red','6LC','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1488,'GLOBAL','SPSU 23',NULL,'SS','Pink Spell','6LD','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1489,'GLOBAL','FAHO 23',NULL,'FW','Fierce Pink','6LF','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1490,'GLOBAL','FAHO 23',NULL,'FW','Playful Pink','6LG','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1491,'GLOBAL','SPSU 24',NULL,'SS','Alchemy Pink','6LH','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1492,'GLOBAL','SP/SU 10',NULL,'SS','Varsity Maize','70G','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1493,'GLOBAL','FA/HO 11',NULL,'FW','Sonic Yellow','70H','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1494,'GLOBAL','SP/SU 10',NULL,'SS','Vibrant Yellow','70M','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1495,'GLOBAL','SP01',NULL,'SS','Lt Voltage Yellow','70R','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1496,'GLOBAL','FA03',NULL,NULL,'Yellow Zest','70X','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1497,'GLOBAL','SP/SU 13',NULL,'SS','Midas Gold','71A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1498,'GLOBAL','FA/HO 10',NULL,'FW','Lemon Twist','71D','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1499,'GLOBAL','FA00',NULL,NULL,'Sunshine','71Q','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1500,'GLOBAL','SP/SU 10',NULL,'SS','Volt','71R','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1501,'GLOBAL','FA/HO 19',NULL,'FW','Bicycle Yellow','71S','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1502,'GLOBAL','SP/SU 14',NULL,'SS','Volt Ice','72U','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1503,'GLOBAL','SP04',NULL,'SS','Lightening','73I','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1504,'GLOBAL','SP/SU 19',NULL,'SS','Barely Volt','73P','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1505,'GLOBAL','SP/SU 13',NULL,'SS','Electric Yellow','73Q','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1506,'GLOBAL','SP/SU 16',NULL,'SS','Opti Yellow','73W','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1507,'GLOBAL','FA/HO 09',NULL,'FW','Zitron','74A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1508,'GLOBAL','FA/HO 09',NULL,'FW','Del Sol','74H','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1509,'GLOBAL','SP/SU 18',NULL,'SS','Volt Glow','74L','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1510,'GLOBAL','FA/HO 18',NULL,'FW','Dynamic Yellow','74M','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1511,'GLOBAL','SP/SU 20',NULL,'SS','Lemon Venom','74Y','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1512,'GLOBAL','SP01',NULL,'SS','Voltage Yellow','75B','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1513,'GLOBAL','SP02',NULL,'SS','Dandelion','76C','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1514,'GLOBAL','SPSU 23',NULL,'SS','Sundial','76H','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1515,'GLOBAL','SP00',NULL,'SS','Neon Yellow','77D','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1516,'GLOBAL','FA/HO 09',NULL,'FW','Midwest Gold','77I','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1517,'GLOBAL','FA/HO 18',NULL,'FW','Amarillo','78H','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1518,'GLOBAL','SPSU 23',NULL,'SS','Sundown','79Q','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1519,'GLOBAL','FAHO\'21',NULL,'FW','Yellow Strike','79S','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1520,'GLOBAL','SP07',NULL,'SS','Voltage Yellow II','7AF','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1521,'GLOBAL','SP/SU 10',NULL,'SS','Ultralime','7AQ','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1522,'GLOBAL','SPSU 24',NULL,'SS','Lt Lemon Twist','7AX','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1523,'GLOBAL','SP08',NULL,'SS','Bright Mango','80A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1524,'GLOBAL','FA/HO 12',NULL,'FW','Starfish','80K','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1525,'GLOBAL','SP04',NULL,'SS','Camellia','80P','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1526,'GLOBAL','SP/SU 10',NULL,'SS','Total Orange','80S','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1527,'GLOBAL','SP/SU 20',NULL,'SS','Alpha Orange','80T','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1528,'GLOBAL','SP/SU 15',NULL,'SS','Hot Lava','81C','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1529,'GLOBAL','FA04',NULL,NULL,'Orange Flash','81H','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1530,'GLOBAL','SP/SU 12',NULL,'SS','Safety Orange','81J','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1531,'GLOBAL','SP/SU 13',NULL,'SS','Bright Citrus','81M','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1532,'GLOBAL','SU08',NULL,NULL,'Orange Chrome','81V','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1533,'GLOBAL','SP11',NULL,'SS','Peach Cream','82A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1534,'GLOBAL','SP/SU 10',NULL,'SS','Orange Blaze','82F','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1535,'GLOBAL','SP/SU 10',NULL,'SS','Urgent Orange','82X','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1536,'GLOBAL','FA/HO 11',NULL,'FW','Orange Peel','83F','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1537,'GLOBAL','FA/HO 12',NULL,'FW','Mesa Orange','83H','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1538,'GLOBAL','SP/SU 14',NULL,'SS','Atomic Orange','83V','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1539,'GLOBAL','SP/SU 13',NULL,'SS','Total Crimson','83Y','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1540,'GLOBAL','SP06',NULL,'SS','Bright Mandarin','84A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1541,'GLOBAL','FAHO\'21',NULL,'FW','Orange','84D','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1542,'GLOBAL','SP/SU 13',NULL,'SS','Electro Orange','84K','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1543,'GLOBAL','SP/SU 13',NULL,'SS','Melon Tint','84L','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1544,'GLOBAL','FA/HO 13',NULL,'FW','Urban Orange','84N','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1545,'GLOBAL','FA/HO 13',NULL,'FW','Laser Orange','84P','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1546,'GLOBAL','FA/HO 13',NULL,'FW','Gamma Orange','84Q','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1547,'GLOBAL','SP/SU 14',NULL,'SS','Atomic Mango','84T','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1548,'GLOBAL','SP/SU 14',NULL,'SS','Turf Orange','84V','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1549,'GLOBAL','FA/HO 15',NULL,'FW','Hyper Orange','84Y','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1550,'GLOBAL','SP01',NULL,'SS','Citrus','85A','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1551,'GLOBAL','FA/HO 18',NULL,'FW','Cone','85J','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1552,'GLOBAL','FA/HO 14',NULL,'FW','Copper Flash','85M','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1553,'GLOBAL','FA/HO 14',NULL,'FW','Hyper Crimson','85N','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1554,'GLOBAL','SP/SU 15',NULL,'SS','Sunset Glow','85P','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1555,'GLOBAL','FA/HO 15',NULL,'FW','Ember Glow','85S','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1556,'GLOBAL','SP/SU 17',NULL,'SS','Orange Charge','85U','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1557,'GLOBAL','FA/HO 17',NULL,'FW','Lt Laser Orange','85X','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1558,'GLOBAL','SP/SU 18',NULL,'SS','Citron Pulse','85Y','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1559,'GLOBAL','SP/SU 18',NULL,'SS','Orange Pulse','85Z','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1560,'GLOBAL','HO08',NULL,'FW','Mandarin','86C','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1561,'GLOBAL','SP07',NULL,'SS','Tart','86D','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1562,'GLOBAL','FAHO\'21',NULL,'FW','Crimson Tint','86L','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1563,'GLOBAL','SP/SU 18',NULL,'SS','Crimson Pulse','86M','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1564,'GLOBAL','SP/SU 18',NULL,'SS','Vintage Coral','86N','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1565,'GLOBAL','SP/SU 18',NULL,'SS','Rush Coral','86P','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1566,'GLOBAL','SP/SU 18',NULL,'SS','Rush Orange','86Q','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1567,'GLOBAL','SPSU 23',NULL,'SS','Citron Tint','86R','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1568,'GLOBAL','SP/SU 18',NULL,'SS','Tangerine Tint','86T','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1569,'GLOBAL','SP/SU 19',NULL,'SS','Fuel Orange','86Z','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1570,'GLOBAL','SP/SU 09',NULL,'SS','Bright Coral','88F','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1571,'GLOBAL','FA/HO 10',NULL,'FW','Spice','88J','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1572,'GLOBAL','SP/SU 20',NULL,'SS','Magma Orange','88M','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1573,'GLOBAL','SP/SU 20',NULL,'SS','Magic Ember','88N','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1574,'GLOBAL','SPSU\'22',NULL,'SS','Lt Madder Root','88U','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1575,'GLOBAL','SP/SU 13',NULL,'SS','Melon','89C','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1576,'GLOBAL','SP/SU 09',NULL,'SS','Bright Peach','89F','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1577,'GLOBAL','SP/SU 18',NULL,'SS','Sea Coral','89G','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1578,'GLOBAL','SP/SU 12',NULL,'SS','Vivid Orange','89K','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1579,'GLOBAL','SP/SU 10',NULL,'SS','Team Orange','89L','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1580,'GLOBAL','SPSU 23',NULL,'SS','Brilliant Orange','89N','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1581,'GLOBAL','SPSU 23',NULL,'SS','Orange Horizon','89Q','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1582,'GLOBAL','SP/SU 27',NULL,'SS','Victory Lapis','4RG','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1583,'GLOBAL','SP/SU 27',NULL,'SS','Pink Grapefruit','6LO','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1584,'GLOBAL','SP/SU 27',NULL,'SS','Neo Pink','6LP','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1585,'GLOBAL','SP/SU 27',NULL,'SS','Burning Net','6LR','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1586,'GLOBAL','SP/SU 27',NULL,'SS','Happy Yellow','7BB','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1587,'GLOBAL','SP/SU 27',NULL,'SS','Vintage honey','7BD','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1588,'UA','SS21 Fluorescent',NULL,'SS','Antifreeze 396','396','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1589,'UA','SS21 Fluorescent',NULL,'SS','Beta 628','628','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1590,'UA','SS21 Fluorescent',NULL,'SS','Beta Tint 658','658','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1591,'UA','SS21 Fluorescent',NULL,'SS','Blaze Orange 825','825','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1592,'UA','SS21 Fluorescent',NULL,'SS','High-Vis Yellow 731','731','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1593,'UA','SS21 Fluorescent',NULL,'SS','Hyper Green 389','389','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1594,'UA','SS21 Fluorescent',NULL,'SS','Pale Moonlight 911','911','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1595,'UA','SS21 Fluorescent',NULL,'SS','Pink Shock 683','683','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1596,'UA','SS21 Fluorescent',NULL,'SS','Playful Peach 164','164','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1597,'UA','SS21 Fluorescent',NULL,'SS','Pop Pink 979','979','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1598,'UA','SS21 Fluorescent',NULL,'SS','Rush Red 820','820','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1599,'UA','SS21 Fluorescent',NULL,'SS','Solar Pink 670','670','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1600,'UA','SS21 Fluorescent',NULL,'SS','Vapor Green 299','299','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1601,'UA','SS22 Fluorescent',NULL,'SS','Color Standards','Standards','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1602,'UA','SS22 Fluorescent',NULL,'SS','Beta 628','628','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1603,'UA','SS22 Fluorescent',NULL,'SS','Beta Tint 658','658','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1604,'UA','SS22 Fluorescent',NULL,'SS','Blaze Orange 825','825','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1605,'UA','SS22 Fluorescent',NULL,'SS','Electric Tangerine 824','824','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1606,'UA','SS22 Fluorescent',NULL,'SS','Electro Pink 695','695','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1607,'UA','SS22 Fluorescent',NULL,'SS','Green Typhon 375','375','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1608,'UA','SS22 Fluorescent',NULL,'SS','High-Vis Yellow 731','731','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1609,'UA','SS22 Fluorescent',NULL,'SS','Pale Moonlight 911','911','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1610,'UA','SS22 Fluorescent',NULL,'SS','Penta Pink 975','975','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1611,'UA','SS22 Fluorescent',NULL,'SS','Pink Sands 981','981','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1612,'UA','SS22 Fluorescent',NULL,'SS','Quirky Lime 752','752','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1613,'UA','SS22 Fluorescent',NULL,'SS','Rush Red 820','820','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1614,'UA','SS22 Fluorescent',NULL,'SS','Vapor Green 299','299','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1615,'UA','SS23 Fluorescent',NULL,'SS','After Burn 877','877','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1616,'UA','SS23 Fluorescent',NULL,'SS','Beta 628','628','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1617,'UA','SS23 Fluorescent',NULL,'SS','High-Vis Yellow 731','731','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1618,'UA','SS23 Fluorescent',NULL,'SS','Lime Surge 369','369','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1619,'UA','SS23 Fluorescent',NULL,'SS','Orange Blast 866','866','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1620,'UA','SS23 Fluorescent',NULL,'SS','Orange Tropic 906','906','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1621,'UA','SS23 Fluorescent',NULL,'SS','Pink Shock 683','683','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1622,'UA','SS23 Fluorescent',NULL,'SS','Rush Red 820','820','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1623,'UA','SS24 Fluorescent',NULL,'SS','Beta 628','628','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1624,'UA','SS24 Fluorescent',NULL,'SS','Blaze Orange 825','825','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1625,'UA','SS24 Fluorescent',NULL,'SS','Fluo Pink 682','682','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1626,'UA','SS24 Fluorescent',NULL,'SS','High-Vis Yellow 731','731','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1627,'UA','SS24 Fluorescent',NULL,'SS','Nova Orange 803','803','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1628,'UA','SS24 Fluorescent',NULL,'SS','Orange Blast 866','866','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1629,'UA','SS24 Fluorescent',NULL,'SS','Phoenix Fire 296','296','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1630,'UA','SS24 Fluorescent',NULL,'SS','Rush Red 820','820','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1631,'UA','SS24 Fluorescent',NULL,'SS','Vapor Green 299','299','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1632,'UA','FW20 Fluorescent',NULL,'FW','Beta 628','628','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1633,'UA','FW20 Fluorescent',NULL,'FW','Beta Tint 658','658','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1634,'UA','FW20 Fluorescent',NULL,'FW','Cerise 653','653','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1635,'UA','FW20 Fluorescent',NULL,'FW','Laser Green 387','387','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1636,'UA','FW20 Fluorescent',NULL,'FW','Lime Fizz 291','291','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1637,'UA','FW20 Fluorescent',NULL,'FW','Lunar Orange 880','880','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1638,'UA','FW20 Fluorescent',NULL,'FW','Panic Orange 869','869','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1639,'UA','FW20 Fluorescent',NULL,'FW','Pink Craze 645','645','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1640,'UA','FW20 Fluorescent',NULL,'FW','Rush Red 820','820','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1641,'UA','FW20 Fluorescent',NULL,'FW','Yellow Ray 705','705','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1642,'UA','FW21 Fluorescent',NULL,'FW','Beta 628','628','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1643,'UA','FW21 Fluorescent',NULL,'FW','Beta Tint 658','658','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1644,'UA','FW21 Fluorescent',NULL,'FW','Brilliance 819','819','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1645,'UA','FW21 Fluorescent',NULL,'FW','Cerise 653','653','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1646,'UA','FW21 Fluorescent',NULL,'FW','Electro Pink 695','695','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1647,'UA','FW21 Fluorescent',NULL,'FW','High-Vis Yellow 731','731','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1648,'UA','FW21 Fluorescent',NULL,'FW','Omega Orange 857','857','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1649,'UA','FW21 Fluorescent',NULL,'FW','Pale Moonlight 911','911','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1650,'UA','FW21 Fluorescent',NULL,'FW','Phoenix Fire 296','296','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1651,'UA','FW21 Fluorescent',NULL,'FW','Rush Red 820','820','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1652,'UA','FW21 Fluorescent',NULL,'FW','Stadium Green 341','341','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1653,'UA','FW22 Fluorescent',NULL,'FW','Afterglow 864','864','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1654,'UA','FW22 Fluorescent',NULL,'FW','Antifreeze 396','396','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1655,'UA','FW22 Fluorescent',NULL,'FW','Beta 628','628','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1656,'UA','FW22 Fluorescent',NULL,'FW','Blitz Red 810','810','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1657,'UA','FW22 Fluorescent',NULL,'FW','High-Vis Yellow 731','731','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1658,'UA','FW22 Fluorescent',NULL,'FW','Lunar Coral 871','871','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1659,'UA','FW22 Fluorescent',NULL,'FW','Orange Ice 814','814','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1660,'UA','FW22 Fluorescent',NULL,'FW','Orange Shock 809','809','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1661,'UA','FW22 Fluorescent',NULL,'FW','Panic Orange 869','869','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1662,'UA','FW22 Fluorescent',NULL,'FW','Pink Punk 640','640','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1663,'UA','FW22 Fluorescent',NULL,'FW','Rush Red 820','820','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1664,'UA','FW22 Fluorescent',NULL,'FW','Yellow Ray 705','705','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1665,'UA','FW23 Fluorescent',NULL,'FW','Beta 628','628','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1666,'UA','FW23 Fluorescent',NULL,'FW','Eclectic Pink 690','690','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1667,'UA','FW23 Fluorescent',NULL,'FW','Formula Orange 801','801','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1668,'UA','FW23 Fluorescent',NULL,'FW','Green Screen 316','316','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1669,'UA','FW23 Fluorescent',NULL,'FW','High-Vis Yellow 731','731','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1670,'UA','FW23 Fluorescent',NULL,'FW','Pink Shock 683','683','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1671,'UA','FW23 Fluorescent',NULL,'FW','Rush Red 820','820','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1672,'UA','FW24 Fluorescent',NULL,'FW','Beta 628','628','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1673,'UA','FW24 Fluorescent',NULL,'FW','Flare Orange 897','897','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1674,'UA','FW24 Fluorescent',NULL,'FW','High-Vis Yellow 731','731','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1675,'UA','FW24 Fluorescent',NULL,'FW','Orange Blast 866','866','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1676,'UA','FW24 Fluorescent',NULL,'FW','Rebel Pink 652','652','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21'),
(1677,'UA','FW24 Fluorescent',NULL,'FW','Rush Red 820','820','fluorescent','fluorescent_csv_pack',1,'2026-04-29 18:31:21');
/*!40000 ALTER TABLE `fluorescent_color_masters` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `invoice_details`
--

DROP TABLE IF EXISTS `invoice_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoice_details` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `invoice_id` bigint(20) DEFAULT NULL,
  `item_description` varchar(255) DEFAULT NULL,
  `color` varchar(100) DEFAULT NULL,
  `qty` decimal(12,2) DEFAULT NULL,
  `unit_price` decimal(12,2) DEFAULT NULL,
  `amount` decimal(14,2) DEFAULT NULL,
  `roll` int(11) DEFAULT NULL,
  `pcs` int(11) DEFAULT NULL,
  `net_weight` decimal(12,2) DEFAULT NULL,
  `gross_weight` decimal(12,2) DEFAULT NULL,
  `remark` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `invoice_id` (`invoice_id`),
  CONSTRAINT `invoice_details_ibfk_1` FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoice_details`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `invoice_details` WRITE;
/*!40000 ALTER TABLE `invoice_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `invoice_details` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `invoices`
--

DROP TABLE IF EXISTS `invoices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoices` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `invoice_number` varchar(100) DEFAULT NULL,
  `packing_list_number` varchar(100) DEFAULT NULL,
  `po_number` varchar(100) DEFAULT NULL,
  `customer_name` varchar(255) DEFAULT NULL,
  `customer_address` text DEFAULT NULL,
  `customer_phone` varchar(50) DEFAULT NULL,
  `invoice_date` date DEFAULT NULL,
  `description` text DEFAULT NULL,
  `term_of_payment` varchar(100) DEFAULT NULL,
  `bank_name` varchar(255) DEFAULT NULL,
  `account_number` varchar(100) DEFAULT NULL,
  `bank_address` text DEFAULT NULL,
  `bank_phone` varchar(50) DEFAULT NULL,
  `total_amount` decimal(14,2) DEFAULT NULL,
  `total_in_words` text DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `delivery_id` bigint(20) DEFAULT NULL,
  `due_date` date DEFAULT NULL,
  `tax_invoice_no` varchar(80) DEFAULT NULL,
  `tax_invoice_date` date DEFAULT NULL,
  `receipt_no` varchar(80) DEFAULT NULL,
  `received_by` varchar(120) DEFAULT NULL,
  `received_date` date DEFAULT NULL,
  `nopen` varchar(80) DEFAULT NULL,
  `nomor_aju` varchar(80) DEFAULT NULL,
  `payment_date` date DEFAULT NULL,
  `payment_bank_account` varchar(100) DEFAULT NULL,
  `payment_proof_url` varchar(500) DEFAULT NULL,
  `payment_status` varchar(20) NOT NULL DEFAULT 'unpaid',
  `customer_id` bigint(20) DEFAULT NULL,
  `po_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_invoices_delivery_id` (`delivery_id`),
  KEY `ix_invoices_customer_id` (`customer_id`),
  KEY `ix_invoices_po_id` (`po_id`),
  CONSTRAINT `fk_invoices_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`),
  CONSTRAINT `fk_invoices_delivery_id` FOREIGN KEY (`delivery_id`) REFERENCES `delivery_headers` (`id`),
  CONSTRAINT `fk_invoices_po_id` FOREIGN KEY (`po_id`) REFERENCES `po_headers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoices`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `invoices` WRITE;
/*!40000 ALTER TABLE `invoices` DISABLE KEYS */;
/*!40000 ALTER TABLE `invoices` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `journal_entries`
--

DROP TABLE IF EXISTS `journal_entries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `journal_entries` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `transaction_type` varchar(50) NOT NULL,
  `transaction_id` bigint(20) NOT NULL,
  `coa_code` varchar(20) NOT NULL,
  `coa_name` varchar(100) NOT NULL,
  `debit` decimal(14,2) NOT NULL DEFAULT 0.00,
  `credit` decimal(14,2) NOT NULL DEFAULT 0.00,
  `description` text DEFAULT NULL,
  `entry_date` date NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `journal_entries`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `journal_entries` WRITE;
/*!40000 ALTER TABLE `journal_entries` DISABLE KEYS */;
/*!40000 ALTER TABLE `journal_entries` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `lot_sequences`
--

DROP TABLE IF EXISTS `lot_sequences`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `lot_sequences` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `prefix` varchar(8) NOT NULL,
  `factory_code` varchar(32) NOT NULL,
  `date_ymd` varchar(8) NOT NULL,
  `last_value` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_lot_sequences_prefix_factory_date` (`prefix`,`factory_code`,`date_ymd`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lot_sequences`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `lot_sequences` WRITE;
/*!40000 ALTER TABLE `lot_sequences` DISABLE KEYS */;
INSERT INTO `lot_sequences` VALUES
(1,'PUM','123','20260511',3),
(2,'PUM','123456','20260511',4),
(3,'PUM','12322','20260511',1),
(4,'PUM','ccc','20260511',1),
(5,'MYC','LR003','20260512',2),
(6,'PUM','AD002','20260512',2),
(7,'PUM','CS004','20260519',1),
(9,'PUM','SL044','20260605',5),
(10,'PUM','AD002','20260605',2),
(11,'MYC','TK028','20260608',1),
(12,'PUM','SL044','20260611',1),
(13,'PUM','SL044','20260630',1);
/*!40000 ALTER TABLE `lot_sequences` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `marketing_outstanding_snapshots`
--

DROP TABLE IF EXISTS `marketing_outstanding_snapshots`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `marketing_outstanding_snapshots` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `label` varchar(255) DEFAULT NULL,
  `filter_params_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`filter_params_json`)),
  `rows_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`rows_json`)),
  `row_count` int(11) NOT NULL DEFAULT 0,
  `created_at` datetime DEFAULT current_timestamp(),
  `created_by_username` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_mkt_out_snap_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `marketing_outstanding_snapshots`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `marketing_outstanding_snapshots` WRITE;
/*!40000 ALTER TABLE `marketing_outstanding_snapshots` DISABLE KEYS */;
INSERT INTO `marketing_outstanding_snapshots` VALUES
(1,NULL,'{\"balance_filter\": \"exclude_zero\", \"computed_balance\": true, \"po_q\": null, \"shipment_status\": \"all\", \"material_status\": null, \"factory_code\": null, \"po_category\": null, \"order_date_from\": null, \"order_date_to\": null}','[{\"order_date\": \"2026-06-05\", \"thi_order\": \"PUMSL044260605001\", \"customer_name\": \"\\u2014\", \"brand\": \"\\u2014\", \"order_type\": \"PROD\", \"no_po\": \"SO-202606-00001\", \"po_customer_ref\": \"PO-SO-202606-00001\", \"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"thickness\": \"1.02\", \"emboss\": \"B-27\", \"softness_type\": \"Vir Soft\", \"color\": \"ACTIVE FUCHSIA\", \"softness\": \"\", \"qty_sf\": \"2000.00\", \"unit_price\": \"1.0700\", \"color_reference\": \"6HJ\", \"color_standard\": \"TMAD0022022061001\", \"backing\": \"6DX\", \"model\": \"\", \"style_article\": \"\", \"rtd_text\": \"\", \"line_etd\": null, \"stock_wh_qty\": \"\", \"balance_qty\": \"2000.00\", \"system_reference\": \"\", \"detail_remark\": \"\", \"remark_system\": \"Order 2000.00 SF | Terkirim 0 | Saldo 2000.00\", \"remark_marketing\": \"\", \"material_followup_remark_header\": \"\", \"material_followup_done_header\": false, \"status_material\": \"Follow-up material: belum\", \"delivered_qty\": \"0\", \"production_status\": \"\", \"po_id\": 21, \"po_detail_id\": 26, \"po_status\": \"draft\", \"mkt_stage\": \"input_system\", \"delivery_1_qty\": \"\", \"delivery_1_date\": \"\", \"delivery_2_qty\": \"\", \"delivery_2_date\": \"\", \"delivery_3_qty\": \"\", \"delivery_3_date\": \"\", \"delivery_4_qty\": \"\", \"delivery_4_date\": \"\", \"delivery_5_qty\": \"\", \"delivery_5_date\": \"\", \"delivery_6_qty\": \"\", \"delivery_6_date\": \"\", \"delivery_7_qty\": \"\", \"delivery_7_date\": \"\", \"delivery_8_qty\": \"\", \"delivery_8_date\": \"\", \"schedule_qty_total\": \"\", \"schedule_unallocated_qty\": \"2000.00\", \"actual_vs_schedule_qty\": \"\"}, {\"order_date\": \"2026-05-12\", \"thi_order\": \"PUMAD002260512001\", \"customer_name\": \"\\u2014\", \"brand\": \"\\u2014\", \"order_type\": \"PROD\", \"no_po\": \"SO-202605-00007\", \"po_customer_ref\": \"POABC\", \"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"thickness\": \"1.02\", \"emboss\": \"DE-73 (SEMI MATTE)\", \"softness_type\": \"Vir Soft\", \"color\": \"WOLF GREY (01V)\", \"softness\": \"\", \"qty_sf\": \"1000.00\", \"unit_price\": \"11.0700\", \"color_reference\": \"\", \"color_standard\": \"\", \"backing\": \"\", \"model\": \"\", \"style_article\": \"\", \"rtd_text\": \"\", \"line_etd\": null, \"stock_wh_qty\": \"\", \"balance_qty\": \"1000.00\", \"system_reference\": \"\", \"detail_remark\": \"test\", \"remark_system\": \"Order 1000.00 SF | Terkirim 0 | Saldo 1000.00\", \"remark_marketing\": \"\", \"material_followup_remark_header\": \"\", \"material_followup_done_header\": false, \"status_material\": \"Follow-up material: belum\", \"delivered_qty\": \"0\", \"production_status\": \"\", \"po_id\": 19, \"po_detail_id\": 23, \"po_status\": \"draft\", \"mkt_stage\": \"input_system\", \"delivery_1_qty\": \"\", \"delivery_1_date\": \"\", \"delivery_2_qty\": \"\", \"delivery_2_date\": \"\", \"delivery_3_qty\": \"\", \"delivery_3_date\": \"\", \"delivery_4_qty\": \"\", \"delivery_4_date\": \"\", \"delivery_5_qty\": \"\", \"delivery_5_date\": \"\", \"delivery_6_qty\": \"\", \"delivery_6_date\": \"\", \"delivery_7_qty\": \"\", \"delivery_7_date\": \"\", \"delivery_8_qty\": \"\", \"delivery_8_date\": \"\", \"schedule_qty_total\": \"\", \"schedule_unallocated_qty\": \"1000.00\", \"actual_vs_schedule_qty\": \"\"}, {\"order_date\": \"2026-05-12\", \"thi_order\": \"PUMccc260511001\", \"customer_name\": \"\\u2014\", \"brand\": \"\\u2014\", \"order_type\": \"PROD\", \"no_po\": \"SO-202605-00006\", \"po_customer_ref\": \"PO-SO-202605-00006\", \"material_name\": \"ECO TECH COMFORT\", \"thickness\": \"1.24\", \"emboss\": \"DE-43 (SEMI MATTE)\", \"softness_type\": \"Vir Soft\", \"color\": \"BLACK (00A)\", \"softness\": \"\", \"qty_sf\": \"12.00\", \"unit_price\": \"1.2800\", \"color_reference\": \"\", \"color_standard\": \"\", \"backing\": \"\", \"model\": \"\", \"style_article\": \"\", \"rtd_text\": \"\", \"line_etd\": null, \"stock_wh_qty\": \"\", \"balance_qty\": \"12.00\", \"system_reference\": \"\", \"detail_remark\": \"\", \"remark_system\": \"Order 12.00 SF | Terkirim 0 | Saldo 12.00\", \"remark_marketing\": \"\", \"material_followup_remark_header\": \"\", \"material_followup_done_header\": false, \"status_material\": \"Follow-up material: belum\", \"delivered_qty\": \"0\", \"production_status\": \"\", \"po_id\": 18, \"po_detail_id\": 22, \"po_status\": \"draft\", \"mkt_stage\": \"input_system\", \"delivery_1_qty\": \"\", \"delivery_1_date\": \"\", \"delivery_2_qty\": \"\", \"delivery_2_date\": \"\", \"delivery_3_qty\": \"\", \"delivery_3_date\": \"\", \"delivery_4_qty\": \"\", \"delivery_4_date\": \"\", \"delivery_5_qty\": \"\", \"delivery_5_date\": \"\", \"delivery_6_qty\": \"\", \"delivery_6_date\": \"\", \"delivery_7_qty\": \"\", \"delivery_7_date\": \"\", \"delivery_8_qty\": \"\", \"delivery_8_date\": \"\", \"schedule_qty_total\": \"\", \"schedule_unallocated_qty\": \"12.00\", \"actual_vs_schedule_qty\": \"\"}, {\"order_date\": \"2026-05-12\", \"thi_order\": \"PUM123456260511004\", \"customer_name\": \"\\u2014\", \"brand\": \"\\u2014\", \"order_type\": \"PROD\", \"no_po\": \"SO-202605-00003\", \"po_customer_ref\": \"123\", \"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"thickness\": \"1.46\", \"emboss\": \"R-8 (SEMI GLOSS)\", \"softness_type\": \"Vir Soft\", \"color\": \"BLACK (00A)\", \"softness\": \"\", \"qty_sf\": \"12.00\", \"unit_price\": \"1.1200\", \"color_reference\": \"\", \"color_standard\": \"\", \"backing\": \"\", \"model\": \"\", \"style_article\": \"\", \"rtd_text\": \"\", \"line_etd\": \"2026-05-12\", \"stock_wh_qty\": \"\", \"balance_qty\": \"12.00\", \"system_reference\": \"\", \"detail_remark\": \"\", \"remark_system\": \"Order 12.00 SF | Terkirim 0 | Saldo 12.00 | ETD 2026-05-12\", \"remark_marketing\": \"\", \"material_followup_remark_header\": \"\", \"material_followup_done_header\": false, \"status_material\": \"Follow-up material: belum\", \"delivered_qty\": \"0\", \"production_status\": \"\", \"po_id\": 15, \"po_detail_id\": 21, \"po_status\": \"draft\", \"mkt_stage\": \"input_system\", \"delivery_1_qty\": \"1.00\", \"delivery_1_date\": \"2026-05-12\", \"delivery_2_qty\": \"1.00\", \"delivery_2_date\": \"2026-05-19\", \"delivery_3_qty\": \"1.00\", \"delivery_3_date\": \"2026-05-26\", \"delivery_4_qty\": \"1.00\", \"delivery_4_date\": \"2026-06-02\", \"delivery_5_qty\": \"1.00\", \"delivery_5_date\": \"2026-06-09\", \"delivery_6_qty\": \"1.00\", \"delivery_6_date\": \"2026-06-16\", \"delivery_7_qty\": \"1.00\", \"delivery_7_date\": \"2026-06-23\", \"delivery_8_qty\": \"1.00\", \"delivery_8_date\": \"2026-06-30\", \"schedule_qty_total\": \"12.00\", \"schedule_unallocated_qty\": \"0.00\", \"actual_vs_schedule_qty\": \"-12.00\"}, {\"order_date\": \"2026-05-04\", \"thi_order\": \"THI-\", \"customer_name\": \"\\u2014\", \"brand\": \"\\u2014\", \"order_type\": \"PROD\", \"no_po\": \"SO-202605-00001\", \"po_customer_ref\": \"NO123456\", \"material_name\": \"VIRGIN HYDRO PU\", \"thickness\": \"1.24\", \"emboss\": \"AR-20 (MATTE)\", \"softness_type\": \"Soft\", \"color\": \"AURA (4AH)\", \"softness\": \"\", \"qty_sf\": \"10.00\", \"unit_price\": \"\", \"color_reference\": \"\", \"color_standard\": \"\", \"backing\": \"\", \"model\": \"\", \"style_article\": \"\", \"rtd_text\": \"\", \"line_etd\": \"2026-05-04\", \"stock_wh_qty\": \"\", \"balance_qty\": \"10.00\", \"system_reference\": \"\", \"detail_remark\": \"\", \"remark_system\": \"Order 10.00 SF | Terkirim 0 | Saldo 10.00 | ETD 2026-05-04\", \"remark_marketing\": \"\", \"material_followup_remark_header\": \"\", \"material_followup_done_header\": false, \"status_material\": \"Follow-up material: belum\", \"delivered_qty\": \"0\", \"production_status\": \"\", \"po_id\": 13, \"po_detail_id\": 11, \"po_status\": \"draft\", \"mkt_stage\": \"input_system\", \"delivery_1_qty\": \"1.00\", \"delivery_1_date\": \"2026-05-04\", \"delivery_2_qty\": \"1.00\", \"delivery_2_date\": \"2026-05-11\", \"delivery_3_qty\": \"1.00\", \"delivery_3_date\": \"2026-05-18\", \"delivery_4_qty\": \"1.00\", \"delivery_4_date\": \"2026-05-25\", \"delivery_5_qty\": \"1.00\", \"delivery_5_date\": \"2026-06-01\", \"delivery_6_qty\": \"1.00\", \"delivery_6_date\": \"2026-06-08\", \"delivery_7_qty\": \"1.00\", \"delivery_7_date\": \"2026-06-15\", \"delivery_8_qty\": \"1.00\", \"delivery_8_date\": \"2026-06-22\", \"schedule_qty_total\": \"10.00\", \"schedule_unallocated_qty\": \"0.00\", \"actual_vs_schedule_qty\": \"-10.00\"}, {\"order_date\": \"2026-05-04\", \"thi_order\": \"THI-\", \"customer_name\": \"\\u2014\", \"brand\": \"\\u2014\", \"order_type\": \"PROD\", \"no_po\": \"SO-202605-00001\", \"po_customer_ref\": \"NO123456\", \"material_name\": \"ECO TECH COMFORT\", \"thickness\": \"1.24\", \"emboss\": \"DE-43 (SEMI MATTE)\", \"softness_type\": \"\", \"color\": \"BLACK (00A)\", \"softness\": \"\", \"qty_sf\": \"12.00\", \"unit_price\": \"1.9400\", \"color_reference\": \"\", \"color_standard\": \"\", \"backing\": \"\", \"model\": \"\", \"style_article\": \"\", \"rtd_text\": \"\", \"line_etd\": null, \"stock_wh_qty\": \"\", \"balance_qty\": \"12.00\", \"system_reference\": \"\", \"detail_remark\": \"\", \"remark_system\": \"Order 12.00 SF | Terkirim 0 | Saldo 12.00\", \"remark_marketing\": \"\", \"material_followup_remark_header\": \"\", \"material_followup_done_header\": false, \"status_material\": \"Follow-up material: belum\", \"delivered_qty\": \"0\", \"production_status\": \"\", \"po_id\": 13, \"po_detail_id\": 12, \"po_status\": \"draft\", \"mkt_stage\": \"input_system\", \"delivery_1_qty\": \"1.00\", \"delivery_1_date\": \"2026-05-04\", \"delivery_2_qty\": \"1.00\", \"delivery_2_date\": \"2026-05-11\", \"delivery_3_qty\": \"1.00\", \"delivery_3_date\": \"2026-05-18\", \"delivery_4_qty\": \"1.00\", \"delivery_4_date\": \"2026-05-25\", \"delivery_5_qty\": \"1.00\", \"delivery_5_date\": \"2026-06-01\", \"delivery_6_qty\": \"1.00\", \"delivery_6_date\": \"2026-06-08\", \"delivery_7_qty\": \"1.00\", \"delivery_7_date\": \"2026-06-15\", \"delivery_8_qty\": \"1.00\", \"delivery_8_date\": \"2026-06-22\", \"schedule_qty_total\": \"10.00\", \"schedule_unallocated_qty\": \"2.00\", \"actual_vs_schedule_qty\": \"-10.00\"}, {\"order_date\": \"2026-05-04\", \"thi_order\": \"THI-\", \"customer_name\": \"\\u2014\", \"brand\": \"\\u2014\", \"order_type\": \"PROD\", \"no_po\": \"SO-202605-00001\", \"po_customer_ref\": \"NO123456\", \"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"thickness\": \"1.46\", \"emboss\": \"R-8 (SEMI GLOSS)\", \"softness_type\": \"\", \"color\": \"BLACK (00A)\", \"softness\": \"\", \"qty_sf\": \"1200.00\", \"unit_price\": \"10.0000\", \"color_reference\": \"\", \"color_standard\": \"\", \"backing\": \"\", \"model\": \"\", \"style_article\": \"\", \"rtd_text\": \"\", \"line_etd\": null, \"stock_wh_qty\": \"\", \"balance_qty\": \"1200.00\", \"system_reference\": \"\", \"detail_remark\": \"\", \"remark_system\": \"Order 1200.00 SF | Terkirim 0 | Saldo 1200.00\", \"remark_marketing\": \"\", \"material_followup_remark_header\": \"\", \"material_followup_done_header\": false, \"status_material\": \"Follow-up material: belum\", \"delivered_qty\": \"0\", \"production_status\": \"\", \"po_id\": 13, \"po_detail_id\": 13, \"po_status\": \"draft\", \"mkt_stage\": \"input_system\", \"delivery_1_qty\": \"1.00\", \"delivery_1_date\": \"2026-05-04\", \"delivery_2_qty\": \"1.00\", \"delivery_2_date\": \"2026-05-11\", \"delivery_3_qty\": \"1.00\", \"delivery_3_date\": \"2026-05-18\", \"delivery_4_qty\": \"1.00\", \"delivery_4_date\": \"2026-05-25\", \"delivery_5_qty\": \"1.00\", \"delivery_5_date\": \"2026-06-01\", \"delivery_6_qty\": \"1.00\", \"delivery_6_date\": \"2026-06-08\", \"delivery_7_qty\": \"1.00\", \"delivery_7_date\": \"2026-06-15\", \"delivery_8_qty\": \"1.00\", \"delivery_8_date\": \"2026-06-22\", \"schedule_qty_total\": \"10.00\", \"schedule_unallocated_qty\": \"1190.00\", \"actual_vs_schedule_qty\": \"-10.00\"}, {\"order_date\": \"2026-05-04\", \"thi_order\": \"THI-\", \"customer_name\": \"\\u2014\", \"brand\": \"\\u2014\", \"order_type\": \"PROD\", \"no_po\": \"SO-202605-00001\", \"po_customer_ref\": \"NO123456\", \"material_name\": \"VIRGIN HYDRO PU\", \"thickness\": \"1.24\", \"emboss\": \"AR-140 (MATTE)\", \"softness_type\": \"\", \"color\": \"OXYGEN PURPLE (5AX)\", \"softness\": \"\", \"qty_sf\": \"1000.00\", \"unit_price\": \"10.0000\", \"color_reference\": \"\", \"color_standard\": \"\", \"backing\": \"\", \"model\": \"\", \"style_article\": \"\", \"rtd_text\": \"\", \"line_etd\": null, \"stock_wh_qty\": \"\", \"balance_qty\": \"1000.00\", \"system_reference\": \"\", \"detail_remark\": \"\", \"remark_system\": \"Order 1000.00 SF | Terkirim 0 | Saldo 1000.00\", \"remark_marketing\": \"\", \"material_followup_remark_header\": \"\", \"material_followup_done_header\": false, \"status_material\": \"Follow-up material: belum\", \"delivered_qty\": \"0\", \"production_status\": \"\", \"po_id\": 13, \"po_detail_id\": 14, \"po_status\": \"draft\", \"mkt_stage\": \"input_system\", \"delivery_1_qty\": \"1.00\", \"delivery_1_date\": \"2026-05-04\", \"delivery_2_qty\": \"1.00\", \"delivery_2_date\": \"2026-05-11\", \"delivery_3_qty\": \"1.00\", \"delivery_3_date\": \"2026-05-18\", \"delivery_4_qty\": \"1.00\", \"delivery_4_date\": \"2026-05-25\", \"delivery_5_qty\": \"1.00\", \"delivery_5_date\": \"2026-06-01\", \"delivery_6_qty\": \"1.00\", \"delivery_6_date\": \"2026-06-08\", \"delivery_7_qty\": \"1.00\", \"delivery_7_date\": \"2026-06-15\", \"delivery_8_qty\": \"1.00\", \"delivery_8_date\": \"2026-06-22\", \"schedule_qty_total\": \"10.00\", \"schedule_unallocated_qty\": \"990.00\", \"actual_vs_schedule_qty\": \"-10.00\"}, {\"order_date\": \"2026-05-04\", \"thi_order\": \"THI-\", \"customer_name\": \"\\u2014\", \"brand\": \"\\u2014\", \"order_type\": \"PROD\", \"no_po\": \"SO-202605-00001\", \"po_customer_ref\": \"NO123456\", \"material_name\": \"VIRGIN HYDRO PU\", \"thickness\": \"1.24\", \"emboss\": \"AR-20 (MATTE)\", \"softness_type\": \"\", \"color\": \"AURA (4AH)\", \"softness\": \"\", \"qty_sf\": \"10.00\", \"unit_price\": \"10.0000\", \"color_reference\": \"\", \"color_standard\": \"\", \"backing\": \"\", \"model\": \"\", \"style_article\": \"\", \"rtd_text\": \"\", \"line_etd\": null, \"stock_wh_qty\": \"\", \"balance_qty\": \"10.00\", \"system_reference\": \"\", \"detail_remark\": \"\", \"remark_system\": \"Order 10.00 SF | Terkirim 0 | Saldo 10.00\", \"remark_marketing\": \"\", \"material_followup_remark_header\": \"\", \"material_followup_done_header\": false, \"status_material\": \"Follow-up material: belum\", \"delivered_qty\": \"0\", \"production_status\": \"\", \"po_id\": 13, \"po_detail_id\": 15, \"po_status\": \"draft\", \"mkt_stage\": \"input_system\", \"delivery_1_qty\": \"\", \"delivery_1_date\": \"\", \"delivery_2_qty\": \"\", \"delivery_2_date\": \"\", \"delivery_3_qty\": \"\", \"delivery_3_date\": \"\", \"delivery_4_qty\": \"\", \"delivery_4_date\": \"\", \"delivery_5_qty\": \"\", \"delivery_5_date\": \"\", \"delivery_6_qty\": \"\", \"delivery_6_date\": \"\", \"delivery_7_qty\": \"\", \"delivery_7_date\": \"\", \"delivery_8_qty\": \"\", \"delivery_8_date\": \"\", \"schedule_qty_total\": \"\", \"schedule_unallocated_qty\": \"10.00\", \"actual_vs_schedule_qty\": \"\"}, {\"order_date\": \"2026-04-29\", \"thi_order\": \"PU-2910\", \"customer_name\": \"PT. GLOSTAR INDONESIA (PGD)\", \"brand\": \"ADIDAS\", \"order_type\": \"PROD\", \"no_po\": \"SO-202604-00010\", \"po_customer_ref\": \"AUTO-0429-010\", \"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"thickness\": \"1.24\", \"emboss\": \"UM-34T (SEMI MATTE)\", \"softness_type\": \"\", \"color\": \"LT SMOKE GREY (0AL)\", \"softness\": \"\", \"qty_sf\": \"325.00\", \"unit_price\": \"1.0000\", \"color_reference\": \"\", \"color_standard\": \"\", \"backing\": \"\", \"model\": \"\", \"style_article\": \"\", \"rtd_text\": \"\", \"line_etd\": \"2026-05-15\", \"stock_wh_qty\": \"\", \"balance_qty\": \"325.00\", \"system_reference\": \"SYS-SO-202604-00010\", \"detail_remark\": \"auto seed transaksi\", \"remark_system\": \"Order 325.00 SF | Terkirim 0 | Saldo 325.00 | ETD 2026-05-15\", \"remark_marketing\": \"\", \"material_followup_remark_header\": \"\", \"material_followup_done_header\": false, \"status_material\": \"Follow-up material: belum\", \"delivered_qty\": \"0\", \"production_status\": \"\", \"po_id\": 11, \"po_detail_id\": 10, \"po_status\": \"draft\", \"mkt_stage\": \"input_system\", \"delivery_1_qty\": \"130.00\", \"delivery_1_date\": \"2026-05-06\", \"delivery_2_qty\": \"113.75\", \"delivery_2_date\": \"2026-05-13\", \"delivery_3_qty\": \"81.25\", \"delivery_3_date\": \"2026-05-20\", \"delivery_4_qty\": \"\", \"delivery_4_date\": \"\", \"delivery_5_qty\": \"\", \"delivery_5_date\": \"\", \"delivery_6_qty\": \"\", \"delivery_6_date\": \"\", \"delivery_7_qty\": \"\", \"delivery_7_date\": \"\", \"delivery_8_qty\": \"\", \"delivery_8_date\": \"\", \"schedule_qty_total\": \"325.00\", \"schedule_unallocated_qty\": \"0.00\", \"actual_vs_schedule_qty\": \"-325.00\"}, {\"order_date\": \"2026-04-29\", \"thi_order\": \"PU-2909\", \"customer_name\": \"PT. GLOSTAR INDONESIA (PGS)\", \"brand\": \"ADIDAS\", \"order_type\": \"PROD\", \"no_po\": \"SO-202604-00009\", \"po_customer_ref\": \"AUTO-0429-009\", \"material_name\": \"ECO TECH COMFORT\", \"thickness\": \"1.24\", \"emboss\": \"AR-107 (MATTE)\", \"softness_type\": \"\", \"color\": \"WHITE (10A)\", \"softness\": \"\", \"qty_sf\": \"300.00\", \"unit_price\": \"1.5000\", \"color_reference\": \"\", \"color_standard\": \"\", \"backing\": \"\", \"model\": \"\", \"style_article\": \"\", \"rtd_text\": \"\", \"line_etd\": \"2026-05-14\", \"stock_wh_qty\": \"\", \"balance_qty\": \"300.00\", \"system_reference\": \"SYS-SO-202604-00009\", \"detail_remark\": \"auto seed transaksi\", \"remark_system\": \"Order 300.00 SF | Terkirim 0 | Saldo 300.00 | ETD 2026-05-14\", \"remark_marketing\": \"\", \"material_followup_remark_header\": \"\", \"material_followup_done_header\": false, \"status_material\": \"Follow-up material: belum\", \"delivered_qty\": \"0\", \"production_status\": \"\", \"po_id\": 10, \"po_detail_id\": 9, \"po_status\": \"draft\", \"mkt_stage\": \"input_system\", \"delivery_1_qty\": \"120.00\", \"delivery_1_date\": \"2026-05-06\", \"delivery_2_qty\": \"105.00\", \"delivery_2_date\": \"2026-05-13\", \"delivery_3_qty\": \"75.00\", \"delivery_3_date\": \"2026-05-20\", \"delivery_4_qty\": \"\", \"delivery_4_date\": \"\", \"delivery_5_qty\": \"\", \"delivery_5_date\": \"\", \"delivery_6_qty\": \"\", \"delivery_6_date\": \"\", \"delivery_7_qty\": \"\", \"delivery_7_date\": \"\", \"delivery_8_qty\": \"\", \"delivery_8_date\": \"\", \"schedule_qty_total\": \"300.00\", \"schedule_unallocated_qty\": \"0.00\", \"actual_vs_schedule_qty\": \"-300.00\"}, {\"order_date\": \"2026-04-29\", \"thi_order\": \"PU-2908\", \"customer_name\": \"PT. FENG TAY INDONESIA ENTERPRISES (NORTH)\", \"brand\": \"NIKE\", \"order_type\": \"PROD\", \"no_po\": \"SO-202604-00008\", \"po_customer_ref\": \"AUTO-0429-008\", \"material_name\": \"VIRGIN HYDRO PU\", \"thickness\": \"1.24\", \"emboss\": \"AR-140 (MATTE)\", \"softness_type\": \"\", \"color\": \"OXYGEN PURPLE (5AX)\", \"softness\": \"\", \"qty_sf\": \"275.00\", \"unit_price\": \"1.1000\", \"color_reference\": \"\", \"color_standard\": \"\", \"backing\": \"\", \"model\": \"\", \"style_article\": \"\", \"rtd_text\": \"\", \"line_etd\": \"2026-05-13\", \"stock_wh_qty\": \"\", \"balance_qty\": \"275.00\", \"system_reference\": \"SYS-SO-202604-00008\", \"detail_remark\": \"auto seed transaksi\", \"remark_system\": \"Order 275.00 SF | Terkirim 0 | Saldo 275.00 | ETD 2026-05-13\", \"remark_marketing\": \"\", \"material_followup_remark_header\": \"\", \"material_followup_done_header\": false, \"status_material\": \"Follow-up material: belum\", \"delivered_qty\": \"0\", \"production_status\": \"\", \"po_id\": 9, \"po_detail_id\": 8, \"po_status\": \"draft\", \"mkt_stage\": \"input_system\", \"delivery_1_qty\": \"110.00\", \"delivery_1_date\": \"2026-05-06\", \"delivery_2_qty\": \"96.25\", \"delivery_2_date\": \"2026-05-13\", \"delivery_3_qty\": \"68.75\", \"delivery_3_date\": \"2026-05-20\", \"delivery_4_qty\": \"\", \"delivery_4_date\": \"\", \"delivery_5_qty\": \"\", \"delivery_5_date\": \"\", \"delivery_6_qty\": \"\", \"delivery_6_date\": \"\", \"delivery_7_qty\": \"\", \"delivery_7_date\": \"\", \"delivery_8_qty\": \"\", \"delivery_8_date\": \"\", \"schedule_qty_total\": \"275.00\", \"schedule_unallocated_qty\": \"0.00\", \"actual_vs_schedule_qty\": \"-275.00\"}, {\"order_date\": \"2026-04-29\", \"thi_order\": \"PU-2907\", \"customer_name\": \"PT. FENG TAY INDONESIA ENTERPRISES (EAST)\", \"brand\": \"NIKE\", \"order_type\": \"PROD\", \"no_po\": \"SO-202604-00007\", \"po_customer_ref\": \"AUTO-0429-007\", \"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"thickness\": \"1.02\", \"emboss\": \"DE-73 (SEMI MATTE)\", \"softness_type\": \"\", \"color\": \"WOLF GREY (01V)\", \"softness\": \"\", \"qty_sf\": \"250.00\", \"unit_price\": \"1.0700\", \"color_reference\": \"\", \"color_standard\": \"\", \"backing\": \"\", \"model\": \"\", \"style_article\": \"\", \"rtd_text\": \"\", \"line_etd\": \"2026-05-12\", \"stock_wh_qty\": \"\", \"balance_qty\": \"250.00\", \"system_reference\": \"SYS-SO-202604-00007\", \"detail_remark\": \"auto seed transaksi\", \"remark_system\": \"Order 250.00 SF | Terkirim 0 | Saldo 250.00 | ETD 2026-05-12\", \"remark_marketing\": \"\", \"material_followup_remark_header\": \"\", \"material_followup_done_header\": false, \"status_material\": \"Follow-up material: belum\", \"delivered_qty\": \"0\", \"production_status\": \"\", \"po_id\": 8, \"po_detail_id\": 7, \"po_status\": \"draft\", \"mkt_stage\": \"input_system\", \"delivery_1_qty\": \"100.00\", \"delivery_1_date\": \"2026-05-06\", \"delivery_2_qty\": \"87.50\", \"delivery_2_date\": \"2026-05-13\", \"delivery_3_qty\": \"62.50\", \"delivery_3_date\": \"2026-05-20\", \"delivery_4_qty\": \"\", \"delivery_4_date\": \"\", \"delivery_5_qty\": \"\", \"delivery_5_date\": \"\", \"delivery_6_qty\": \"\", \"delivery_6_date\": \"\", \"delivery_7_qty\": \"\", \"delivery_7_date\": \"\", \"delivery_8_qty\": \"\", \"delivery_8_date\": \"\", \"schedule_qty_total\": \"250.00\", \"schedule_unallocated_qty\": \"0.00\", \"actual_vs_schedule_qty\": \"-250.00\"}, {\"order_date\": \"2026-04-29\", \"thi_order\": \"PU-2906\", \"customer_name\": \"PT. FENG TAY INDONESIA ENTERPRISES (WEST)\", \"brand\": \"NIKE\", \"order_type\": \"PROD\", \"no_po\": \"SO-202604-00006\", \"po_customer_ref\": \"AUTO-0429-006\", \"material_name\": \"(PM) GENERIC PU COATED LEATHER\", \"thickness\": \"1.46\", \"emboss\": \"R-8 (SEMI GLOSS)\", \"softness_type\": \"\", \"color\": \"BLACK (00A)\", \"softness\": \"\", \"qty_sf\": \"225.00\", \"unit_price\": \"1.1200\", \"color_reference\": \"\", \"color_standard\": \"\", \"backing\": \"\", \"model\": \"\", \"style_article\": \"\", \"rtd_text\": \"\", \"line_etd\": \"2026-05-11\", \"stock_wh_qty\": \"\", \"balance_qty\": \"225.00\", \"system_reference\": \"SYS-SO-202604-00006\", \"detail_remark\": \"auto seed transaksi\", \"remark_system\": \"Order 225.00 SF | Terkirim 0 | Saldo 225.00 | ETD 2026-05-11\", \"remark_marketing\": \"\", \"material_followup_remark_header\": \"\", \"material_followup_done_header\": false, \"status_material\": \"Follow-up material: belum\", \"delivered_qty\": \"0\", \"production_status\": \"\", \"po_id\": 7, \"po_detail_id\": 6, \"po_status\": \"draft\", \"mkt_stage\": \"input_system\", \"delivery_1_qty\": \"90.00\", \"delivery_1_date\": \"2026-05-06\", \"delivery_2_qty\": \"78.75\", \"delivery_2_date\": \"2026-05-13\", \"delivery_3_qty\": \"56.25\", \"delivery_3_date\": \"2026-05-20\", \"delivery_4_qty\": \"\", \"delivery_4_date\": \"\", \"delivery_5_qty\": \"\", \"delivery_5_date\": \"\", \"delivery_6_qty\": \"\", \"delivery_6_date\": \"\", \"delivery_7_qty\": \"\", \"delivery_7_date\": \"\", \"delivery_8_qty\": \"\", \"delivery_8_date\": \"\", \"schedule_qty_total\": \"225.00\", \"schedule_unallocated_qty\": \"0.00\", \"actual_vs_schedule_qty\": \"-225.00\"}, {\"order_date\": \"2026-04-29\", \"thi_order\": \"PU-2905\", \"customer_name\": \"PT. CHING LUH INDONESIA\", \"brand\": \"NIKE\", \"order_type\": \"PROD\", \"no_po\": \"SO-202604-00005\", \"po_customer_ref\": \"AUTO-0429-005\", \"material_name\": \"ECO TECH COMFORT\", \"thickness\": \"1.24\", \"emboss\": \"DE-43 (SEMI MATTE)\", \"softness_type\": \"\", \"color\": \"BLACK (00A)\", \"softness\": \"\", \"qty_sf\": \"200.00\", \"unit_price\": \"1.2800\", \"color_reference\": \"\", \"color_standard\": \"\", \"backing\": \"\", \"model\": \"\", \"style_article\": \"\", \"rtd_text\": \"\", \"line_etd\": \"2026-05-10\", \"stock_wh_qty\": \"\", \"balance_qty\": \"200.00\", \"system_reference\": \"SYS-SO-202604-00005\", \"detail_remark\": \"auto seed transaksi\", \"remark_system\": \"Order 200.00 SF | Terkirim 0 | Saldo 200.00 | ETD 2026-05-10\", \"remark_marketing\": \"\", \"material_followup_remark_header\": \"\", \"material_followup_done_header\": false, \"status_material\": \"Follow-up material: belum\", \"delivered_qty\": \"0\", \"production_status\": \"\", \"po_id\": 6, \"po_detail_id\": 5, \"po_status\": \"draft\", \"mkt_stage\": \"input_system\", \"delivery_1_qty\": \"80.00\", \"delivery_1_date\": \"2026-05-06\", \"delivery_2_qty\": \"70.00\", \"delivery_2_date\": \"2026-05-13\", \"delivery_3_qty\": \"50.00\", \"delivery_3_date\": \"2026-05-20\", \"delivery_4_qty\": \"\", \"delivery_4_date\": \"\", \"delivery_5_qty\": \"\", \"delivery_5_date\": \"\", \"delivery_6_qty\": \"\", \"delivery_6_date\": \"\", \"delivery_7_qty\": \"\", \"delivery_7_date\": \"\", \"delivery_8_qty\": \"\", \"delivery_8_date\": \"\", \"schedule_qty_total\": \"200.00\", \"schedule_unallocated_qty\": \"0.00\", \"actual_vs_schedule_qty\": \"-200.00\"}, {\"order_date\": \"2026-04-29\", \"thi_order\": \"PU-2904\", \"customer_name\": \"PT. CHANGSHIN REKSA JAYA\", \"brand\": \"NIKE\", \"order_type\": \"PROD\", \"no_po\": \"SO-202604-00004\", \"po_customer_ref\": \"AUTO-0429-004\", \"material_name\": \"SOFT PU COATED LEATHER (MAP-SOFT PU)\", \"thickness\": \"1.46\", \"emboss\": \"DE-73 (SEMI MATTE)\", \"softness_type\": \"\", \"color\": \"YELLOW (003A)\", \"softness\": \"\", \"qty_sf\": \"175.00\", \"unit_price\": \"1.0000\", \"color_reference\": \"\", \"color_standard\": \"\", \"backing\": \"\", \"model\": \"\", \"style_article\": \"\", \"rtd_text\": \"\", \"line_etd\": \"2026-05-09\", \"stock_wh_qty\": \"\", \"balance_qty\": \"175.00\", \"system_reference\": \"SYS-SO-202604-00004\", \"detail_remark\": \"auto seed transaksi\", \"remark_system\": \"Order 175.00 SF | Terkirim 0 | Saldo 175.00 | ETD 2026-05-09\", \"remark_marketing\": \"\", \"material_followup_remark_header\": \"\", \"material_followup_done_header\": false, \"status_material\": \"Follow-up material: belum\", \"delivered_qty\": \"0\", \"production_status\": \"\", \"po_id\": 5, \"po_detail_id\": 4, \"po_status\": \"draft\", \"mkt_stage\": \"input_system\", \"delivery_1_qty\": \"70.00\", \"delivery_1_date\": \"2026-05-06\", \"delivery_2_qty\": \"61.25\", \"delivery_2_date\": \"2026-05-13\", \"delivery_3_qty\": \"43.75\", \"delivery_3_date\": \"2026-05-20\", \"delivery_4_qty\": \"\", \"delivery_4_date\": \"\", \"delivery_5_qty\": \"\", \"delivery_5_date\": \"\", \"delivery_6_qty\": \"\", \"delivery_6_date\": \"\", \"delivery_7_qty\": \"\", \"delivery_7_date\": \"\", \"delivery_8_qty\": \"\", \"delivery_8_date\": \"\", \"schedule_qty_total\": \"175.00\", \"schedule_unallocated_qty\": \"0.00\", \"actual_vs_schedule_qty\": \"-175.00\"}, {\"order_date\": \"2026-04-29\", \"thi_order\": \"PU-2903\", \"customer_name\": \"PT. CHANG SHIN INDONESIA\", \"brand\": \"NIKE\", \"order_type\": \"PROD\", \"no_po\": \"SO-202604-00003\", \"po_customer_ref\": \"AUTO-0429-003\", \"material_name\": \"VIRGIN HYDRO PU\", \"thickness\": \"1.46\", \"emboss\": \"AR-193 (MATTE)\", \"softness_type\": \"\", \"color\": \"WHITE (10A)\", \"softness\": \"\", \"qty_sf\": \"150.00\", \"unit_price\": \"1.1000\", \"color_reference\": \"\", \"color_standard\": \"\", \"backing\": \"\", \"model\": \"\", \"style_article\": \"\", \"rtd_text\": \"\", \"line_etd\": \"2026-05-08\", \"stock_wh_qty\": \"\", \"balance_qty\": \"150.00\", \"system_reference\": \"SYS-SO-202604-00003\", \"detail_remark\": \"auto seed transaksi\", \"remark_system\": \"Order 150.00 SF | Terkirim 0 | Saldo 150.00 | ETD 2026-05-08\", \"remark_marketing\": \"\", \"material_followup_remark_header\": \"\", \"material_followup_done_header\": false, \"status_material\": \"Follow-up material: belum\", \"delivered_qty\": \"0\", \"production_status\": \"\", \"po_id\": 4, \"po_detail_id\": 3, \"po_status\": \"draft\", \"mkt_stage\": \"input_system\", \"delivery_1_qty\": \"60.00\", \"delivery_1_date\": \"2026-05-06\", \"delivery_2_qty\": \"52.50\", \"delivery_2_date\": \"2026-05-13\", \"delivery_3_qty\": \"37.50\", \"delivery_3_date\": \"2026-05-20\", \"delivery_4_qty\": \"\", \"delivery_4_date\": \"\", \"delivery_5_qty\": \"\", \"delivery_5_date\": \"\", \"delivery_6_qty\": \"\", \"delivery_6_date\": \"\", \"delivery_7_qty\": \"\", \"delivery_7_date\": \"\", \"delivery_8_qty\": \"\", \"delivery_8_date\": \"\", \"schedule_qty_total\": \"150.00\", \"schedule_unallocated_qty\": \"0.00\", \"actual_vs_schedule_qty\": \"-150.00\"}, {\"order_date\": \"2026-04-29\", \"thi_order\": \"PU-2902\", \"customer_name\": \"PT. BINTANG INDOKARYA GEMILANG (PBB)\", \"brand\": \"ADIDAS\", \"order_type\": \"PROD\", \"no_po\": \"SO-202604-00002\", \"po_customer_ref\": \"AUTO-0429-002\", \"material_name\": \"VIRGIN HYDRO PU\", \"thickness\": \"1.46\", \"emboss\": \"UM-34 (MATTE)\", \"softness_type\": \"\", \"color\": \"BLACK (00A)\", \"softness\": \"\", \"qty_sf\": \"125.00\", \"unit_price\": \"1.0000\", \"color_reference\": \"\", \"color_standard\": \"\", \"backing\": \"\", \"model\": \"\", \"style_article\": \"\", \"rtd_text\": \"\", \"line_etd\": \"2026-05-07\", \"stock_wh_qty\": \"\", \"balance_qty\": \"125.00\", \"system_reference\": \"SYS-SO-202604-00002\", \"detail_remark\": \"auto seed transaksi\", \"remark_system\": \"Order 125.00 SF | Terkirim 0 | Saldo 125.00 | ETD 2026-05-07\", \"remark_marketing\": \"\", \"material_followup_remark_header\": \"\", \"material_followup_done_header\": false, \"status_material\": \"Follow-up material: belum\", \"delivered_qty\": \"0\", \"production_status\": \"\", \"po_id\": 3, \"po_detail_id\": 2, \"po_status\": \"draft\", \"mkt_stage\": \"input_system\", \"delivery_1_qty\": \"50.00\", \"delivery_1_date\": \"2026-05-06\", \"delivery_2_qty\": \"43.75\", \"delivery_2_date\": \"2026-05-13\", \"delivery_3_qty\": \"31.25\", \"delivery_3_date\": \"2026-05-20\", \"delivery_4_qty\": \"\", \"delivery_4_date\": \"\", \"delivery_5_qty\": \"\", \"delivery_5_date\": \"\", \"delivery_6_qty\": \"\", \"delivery_6_date\": \"\", \"delivery_7_qty\": \"\", \"delivery_7_date\": \"\", \"delivery_8_qty\": \"\", \"delivery_8_date\": \"\", \"schedule_qty_total\": \"125.00\", \"schedule_unallocated_qty\": \"0.00\", \"actual_vs_schedule_qty\": \"-125.00\"}, {\"order_date\": \"2026-04-29\", \"thi_order\": \"PU-2901\", \"customer_name\": \"PT. ADIS DIMENSION FOOTWEAR\", \"brand\": \"NIKE\", \"order_type\": \"PROD\", \"no_po\": \"SO-202604-00001\", \"po_customer_ref\": \"AUTO-0429-001\", \"material_name\": \"VIRGIN HYDRO PU\", \"thickness\": \"1.24\", \"emboss\": \"AR-167 (DEEP MATTE)\", \"softness_type\": \"\", \"color\": \"BLACK (00A)\", \"softness\": \"\", \"qty_sf\": \"100.00\", \"unit_price\": \"1.1500\", \"color_reference\": \"\", \"color_standard\": \"\", \"backing\": \"\", \"model\": \"\", \"style_article\": \"\", \"rtd_text\": \"\", \"line_etd\": \"2026-05-06\", \"stock_wh_qty\": \"\", \"balance_qty\": \"100.00\", \"system_reference\": \"SYS-SO-202604-00001\", \"detail_remark\": \"auto seed transaksi\", \"remark_system\": \"Order 100.00 SF | Terkirim 0 | Saldo 100.00 | ETD 2026-05-06\", \"remark_marketing\": \"\", \"material_followup_remark_header\": \"\", \"material_followup_done_header\": false, \"status_material\": \"Follow-up material: belum\", \"delivered_qty\": \"0\", \"production_status\": \"\", \"po_id\": 2, \"po_detail_id\": 1, \"po_status\": \"draft\", \"mkt_stage\": \"input_system\", \"delivery_1_qty\": \"40.00\", \"delivery_1_date\": \"2026-05-06\", \"delivery_2_qty\": \"35.00\", \"delivery_2_date\": \"2026-05-13\", \"delivery_3_qty\": \"25.00\", \"delivery_3_date\": \"2026-05-20\", \"delivery_4_qty\": \"\", \"delivery_4_date\": \"\", \"delivery_5_qty\": \"\", \"delivery_5_date\": \"\", \"delivery_6_qty\": \"\", \"delivery_6_date\": \"\", \"delivery_7_qty\": \"\", \"delivery_7_date\": \"\", \"delivery_8_qty\": \"\", \"delivery_8_date\": \"\", \"schedule_qty_total\": \"100.00\", \"schedule_unallocated_qty\": \"0.00\", \"actual_vs_schedule_qty\": \"-100.00\"}]',19,'2026-06-05 00:55:09','Cre@tiv3');
/*!40000 ALTER TABLE `marketing_outstanding_snapshots` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `master_items`
--

DROP TABLE IF EXISTS `master_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `master_items` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `item_code` varchar(50) NOT NULL,
  `thickness_mm` decimal(10,3) DEFAULT NULL,
  `material_name` varchar(500) DEFAULT NULL,
  `emboss` varchar(500) DEFAULT NULL,
  `color` varchar(500) DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `softness` varchar(100) DEFAULT NULL,
  `color_reference` varchar(255) DEFAULT NULL,
  `backing` varchar(255) DEFAULT NULL,
  `quantity_order_default` decimal(12,2) DEFAULT NULL,
  `style_article` varchar(100) DEFAULT NULL,
  `model` varchar(100) DEFAULT NULL,
  `exim_material_code` varchar(80) DEFAULT NULL,
  `thickness_range` varchar(80) DEFAULT NULL,
  `color_standard` varchar(255) DEFAULT NULL,
  `model_takedown` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_master_items_item_code` (`item_code`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `master_items`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `master_items` WRITE;
/*!40000 ALTER TABLE `master_items` DISABLE KEYS */;
INSERT INTO `master_items` VALUES
(2,'FG00001',NULL,'VIRGIN HYDRO PU','AR-167 (DEEP MATTE)','BLACK (00A)','PU','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(3,'FG00002',NULL,'VIRGIN HYDRO PU','UM-34 (MATTE)','BLACK (00A)','PU','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.4-1.6',NULL,NULL),
(4,'FG00005',NULL,'VIRGIN HYDRO PU','AR-193 (MATTE)','WHITE (10A)','PU','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.4-1.6',NULL,NULL),
(5,'FG02849',NULL,'SOFT PU COATED LEATHER (MAP-SOFT PU)','DE-73 (SEMI MATTE)','YELLOW (003A)','PU','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.4-1.6',NULL,NULL),
(6,'FG00007',NULL,'ECO TECH COMFORT','DE-43 (SEMI MATTE)','BLACK (00A)','PU','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(7,'FG00008',NULL,'(PM) GENERIC PU COATED LEATHER','R-8 (SEMI GLOSS)','BLACK (00A)','PU','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.4-1.6',NULL,NULL),
(8,'FG00162',NULL,'(PM) GENERIC PU COATED LEATHER','DE-73 (SEMI MATTE)','WOLF GREY (01V)','PU','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.0-1.2',NULL,NULL),
(9,'FG00011',NULL,'VIRGIN HYDRO PU','AR-140 (MATTE)','OXYGEN PURPLE (5AX)','PU','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(10,'FG00012',NULL,'ECO TECH COMFORT','AR-107 (MATTE)','WHITE (10A)','PU','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(11,'FG00013',NULL,'(PM) GENERIC PU COATED LEATHER','UM-34T (SEMI MATTE)','LT SMOKE GREY (0AL)','PU','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(12,'FG00014',NULL,'HYDRO SOFT PU COATED LEATHER','R-53 (MATTE)','WHITE MUNSELL (NB102)','PU','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(13,'FG00015',NULL,'HYDRO SOFT ACTION LEATHER','R-51 (SEMI MATTE)','BLACK (NB1000018)','PU','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(14,'FG00016',NULL,'VIRGIN HYDRO PU','AR-20 (MATTE)','SAIL (11K)','PU','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(15,'FG00017',NULL,'(PM) GENERIC PU COATED LEATHER','DE-126 (SEMI MATTE)','PHANTOM (01X)','PU','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(16,'FG01348',NULL,'VIRGIN PU','DE-73 (SEMI MATTE)','WOLF GREY (01V)','PU','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.0-1.2',NULL,NULL),
(17,'FG00019',NULL,'VIRGIN HYDRO PU','AR-167 (DEEP MATTE)','AURA (4AH)','PU','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(18,'FG00020',NULL,'VIRGIN HYDRO PU','AR-167 (DEEP MATTE)','WASHED CORAL (6JE)','PU','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(19,'FG00021',NULL,'VIRGIN HYDRO PU','AR-20 (MATTE)','AURA (4AH)','PU','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(20,'FG00022',NULL,'VIRGIN PU','AR-73 (MATTE)','WHITE (10A)','PU','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(21,'FG00023',NULL,'VIRGIN PU','AR-73 (MATTE)','BLACK (00A)','PU','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.4-1.6',NULL,NULL),
(22,'FG01831',NULL,'HI SUEDE',NULL,'ALUMINA (ADAT)','Suide','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(23,'FG03324',NULL,'SPLIT SUEDE',NULL,'ALUMINA (ADAT)','Suide','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(24,'FG05099',NULL,'SPLIT SUEDE',NULL,'ANGORA COLORO (039-90-05)','Suide','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(25,'FG03819',NULL,'EH SUEDE',NULL,'ASHEN SLATE (4PB)','Suide','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(26,'FG05508',NULL,'CASHMERE SUEDE',NULL,'BETTER SCARLET (AETG)','Suide','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(27,'FG05699',NULL,'SPLIT SUEDE',NULL,'BETTER SCARLET (AETG)','Suide','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(28,'FG01772',NULL,'OPTIK SUEDE',NULL,'BLACK (00A)','Suide','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.4-1.6',NULL,NULL),
(29,'FG05211',NULL,'HI SUEDE',NULL,'BLACK (00A)','Suide','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.4-1.6',NULL,NULL),
(30,'FG00657',NULL,'SPLIT SUEDE',NULL,'BLACK (NB1000018)','Suide','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.4-1.6',NULL,NULL),
(31,'FG05126',NULL,'SPLIT SUEDE',NULL,'BLACK CEMENT (008-24-00)','Suide','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.4-1.6',NULL,NULL),
(32,'FG02480',NULL,'SPLIT SUEDE',NULL,'BLACK COLORO (145-17-00)','Suide','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.6-1.8',NULL,NULL),
(33,'FG04858',NULL,'SPLIT SUEDE',NULL,'BLACK COLORO (145-17-00)','Suide','2026-04-29 17:03:07',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.4-1.6',NULL,NULL),
(34,'TEST123',NULL,'TEST','TEST','TEST','PU','2026-05-04 02:23:36',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.0-1.2',NULL,NULL),
(35,'SUB0001',NULL,'ULTRA SUEDE',NULL,'CHALK WHITE (077A)','SubKon','2026-06-22 18:02:05',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(36,'SUB0002',NULL,'ULTRA SUEDE',NULL,'WHITE (01F7)','SubKon','2026-06-22 18:02:05',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(37,'SUB0003',NULL,'PRO ACTION LEATHER',NULL,NULL,'SubKon','2026-06-22 18:02:05',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(38,'SUB0004',NULL,'SPLIT SUEDE',NULL,NULL,'SubKon','2026-06-22 18:02:05',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(39,'SUB0005',NULL,'SPLIT SUEDE',NULL,NULL,'SubKon','2026-06-22 18:02:05',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.4-1.6',NULL,NULL),
(40,'SUB0007',NULL,'ULTRA SUEDE',NULL,'NIGHT SKY (669A)','SubKon','2026-06-22 18:02:05',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(41,'SUB0008',NULL,'SPLIT SUEDE',NULL,NULL,'SubKon','2026-06-22 18:02:05',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(42,'SUB0009',NULL,'SPLIT SUEDE',NULL,'CORE BLACK (A0QM)','SubKon','2026-06-22 18:02:05',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(43,'SUB0011',NULL,'ULTRA SUEDE',NULL,'GREY TWO (AA2S)','SubKon','2026-06-22 18:02:05',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.4-1.6',NULL,NULL),
(44,'SUB0012',NULL,'COW LEATHER',NULL,'0AJ/6CD','SubKon','2026-06-22 18:02:05',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.4-1.6',NULL,NULL),
(45,'SUB0013',NULL,'SPLIT SUEDE',NULL,NULL,'SubKon','2026-06-22 18:02:05',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.6-1.8',NULL,NULL),
(46,'SUB0014',NULL,'ULTRA SUEDE',NULL,NULL,'SubKon','2026-06-22 18:02:05',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.4-1.6',NULL,NULL),
(47,'SUB0015',NULL,'ULTRA SUEDE',NULL,NULL,'SubKon','2026-06-22 18:02:05',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(48,'SUB0016',NULL,'CHEWBACCA SUEDE',NULL,NULL,'SubKon','2026-06-22 18:02:05',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.4-1.6',NULL,NULL),
(49,'SUB0017',NULL,'SPLIT SUEDE',NULL,'CORE BLACK (A0QM)','SubKon','2026-06-22 18:02:05',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.4-1.6',NULL,NULL),
(50,'SUB0018',NULL,'SPLIT SUEDE',NULL,'SKY RUSH (AED2)','SubKon','2026-06-22 18:02:05',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.4-1.6',NULL,NULL),
(51,'SUB0019',NULL,'SPLIT SUEDE',NULL,'NB VELVET','SubKon','2026-06-22 18:02:05',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(52,'SUB0027',NULL,'ULTRA SUEDE',NULL,'GREY ONE (AA2R)','SubKon','2026-06-22 18:02:05',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.4-1.6',NULL,NULL),
(53,'SUB0028',NULL,'HI SUEDE',NULL,'BLISS ORANGE (AELC)','SubKon','2026-06-22 18:02:05',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(54,'SUB0029',NULL,'HI SUEDE',NULL,'WHITE (01F7)','SubKon','2026-06-22 18:02:05',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL),
(55,'SUB0030',NULL,'EMBOSSED SUEDE',NULL,'MILKY WHITE (11-0701TPX)','SubKon','2026-06-22 18:02:05',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.4-1.6',NULL,NULL),
(56,'SUB0031',NULL,'WORN SUEDE',NULL,'SAIL (11K)','SubKon','2026-06-22 18:02:05',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'1.2-1.4',NULL,NULL);
/*!40000 ALTER TABLE `master_items` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `master_prices`
--

DROP TABLE IF EXISTS `master_prices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `master_prices` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `line_no` int(11) DEFAULT NULL,
  `material_category` varchar(255) DEFAULT NULL,
  `material_type` varchar(255) DEFAULT NULL,
  `material_name` varchar(500) DEFAULT NULL,
  `thickness_range` varchar(80) DEFAULT NULL,
  `price_white_usd` decimal(14,4) DEFAULT NULL,
  `price_black_usd` decimal(14,4) DEFAULT NULL,
  `price_color_usd` decimal(14,4) DEFAULT NULL,
  `price_metallic_usd` decimal(14,4) DEFAULT NULL,
  `remark` varchar(255) DEFAULT NULL,
  `price_tier` varchar(32) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `master_prices`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `master_prices` WRITE;
/*!40000 ALTER TABLE `master_prices` DISABLE KEYS */;
/*!40000 ALTER TABLE `master_prices` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `material_receipt_details`
--

DROP TABLE IF EXISTS `material_receipt_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `material_receipt_details` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `receipt_id` bigint(20) NOT NULL,
  `material_id` bigint(20) NOT NULL,
  `quantity` decimal(12,2) NOT NULL,
  `unit_cost` decimal(14,4) DEFAULT NULL,
  `total_cost` decimal(14,2) DEFAULT NULL,
  `remark` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `material_id` (`material_id`),
  KEY `receipt_id` (`receipt_id`),
  CONSTRAINT `material_receipt_details_ibfk_1` FOREIGN KEY (`material_id`) REFERENCES `raw_materials` (`id`),
  CONSTRAINT `material_receipt_details_ibfk_2` FOREIGN KEY (`receipt_id`) REFERENCES `material_receipts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `material_receipt_details`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `material_receipt_details` WRITE;
/*!40000 ALTER TABLE `material_receipt_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `material_receipt_details` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `material_receipts`
--

DROP TABLE IF EXISTS `material_receipts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `material_receipts` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `receipt_number` varchar(50) NOT NULL,
  `supplier_name` varchar(255) DEFAULT NULL,
  `receipt_date` date NOT NULL,
  `warehouse_id` bigint(20) NOT NULL,
  `total_amount` decimal(14,2) DEFAULT NULL,
  `remark` text DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `receipt_number` (`receipt_number`),
  KEY `warehouse_id` (`warehouse_id`),
  CONSTRAINT `material_receipts_ibfk_1` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `material_receipts`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `material_receipts` WRITE;
/*!40000 ALTER TABLE `material_receipts` DISABLE KEYS */;
/*!40000 ALTER TABLE `material_receipts` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `material_stocks`
--

DROP TABLE IF EXISTS `material_stocks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `material_stocks` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `material_id` bigint(20) NOT NULL,
  `warehouse_id` bigint(20) NOT NULL,
  `current_stock` decimal(12,2) NOT NULL,
  `reserved_stock` decimal(12,2) NOT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_material_warehouse` (`material_id`,`warehouse_id`),
  KEY `warehouse_id` (`warehouse_id`),
  CONSTRAINT `material_stocks_ibfk_1` FOREIGN KEY (`material_id`) REFERENCES `raw_materials` (`id`),
  CONSTRAINT `material_stocks_ibfk_2` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `material_stocks`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `material_stocks` WRITE;
/*!40000 ALTER TABLE `material_stocks` DISABLE KEYS */;
/*!40000 ALTER TABLE `material_stocks` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL,
  `title` varchar(180) NOT NULL,
  `message` text DEFAULT NULL,
  `category` varchar(40) NOT NULL,
  `entity_type` varchar(80) DEFAULT NULL,
  `entity_id` bigint(20) DEFAULT NULL,
  `route_path` varchar(255) DEFAULT NULL,
  `route_query` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`route_query`)),
  `is_read` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `read_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_notifications_user_id` (`user_id`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
INSERT INTO `notifications` VALUES
(1,1,'PO baru SO-202604-00001','Sales order dibuat oleh admin','po','sales_order',1,'/admin/po','{\"po_id\": 1}',1,'2026-04-23 13:12:08','2026-04-23 13:12:55'),
(2,1,'PO baru SO-202604-00002','Sales order dibuat oleh admin','po','sales_order',2,'/admin/po','{\"po_id\": 2}',1,'2026-04-23 13:12:12','2026-04-23 13:12:57'),
(3,1,'PO baru SO-202604-00003','Sales order dibuat oleh admin','po','sales_order',3,'/admin/po','{\"po_id\": 3}',1,'2026-04-23 13:12:39','2026-04-23 13:12:58'),
(4,1,'PO baru SO-202604-00004','Sales order dibuat oleh admin','po','sales_order',4,'/admin/po','{\"po_id\": 4}',1,'2026-04-23 13:12:47','2026-04-23 13:12:58'),
(5,1,'PO baru SO-202605-00001','Sales order dibuat oleh Cre@tiv3','po','sales_order',13,'/admin/po','{\"po_id\": 13}',1,'2026-05-04 03:01:46','2026-05-04 03:04:06'),
(6,1,'PO salinan SO-202605-00002','Duplikat dari PO SO-202605-00001 oleh Cre@tiv3','po','sales_order',14,'/admin/po','{\"po_id\": 14}',1,'2026-05-04 03:05:41','2026-05-04 03:06:01'),
(7,1,'Status PO SO-202605-00002: confirmed','Diubah oleh Cre@tiv3','po_status','sales_order',14,'/admin/po','{\"po_id\": 14}',1,'2026-05-04 03:09:46','2026-05-04 03:25:09'),
(8,1,'PO baru SO-202605-00003','Sales order dibuat oleh Cre@tiv3','po','sales_order',15,'/admin/po','{\"po_id\": 15}',1,'2026-05-11 18:47:28','2026-05-11 18:51:42'),
(9,1,'PO baru SO-202605-00004','Sales order dibuat oleh Cre@tiv3','po','sales_order',16,'/admin/po','{\"po_id\": 16}',1,'2026-05-11 19:25:24','2026-05-11 19:28:58'),
(10,1,'PO baru SO-202605-00005','Sales order dibuat oleh Cre@tiv3','po','sales_order',17,'/admin/po','{\"po_id\": 17}',1,'2026-05-11 19:28:20','2026-05-11 19:28:58'),
(11,1,'PO baru SO-202605-00006','Sales order dibuat oleh Cre@tiv3','po','sales_order',18,'/admin/po','{\"po_id\": 18}',1,'2026-05-11 19:29:31','2026-05-11 19:29:46'),
(12,1,'PO baru SO-202605-00007','Sales order dibuat oleh Cre@tiv3','po','sales_order',19,'/admin/po','{\"po_id\": 19}',1,'2026-05-12 03:19:56','2026-05-12 03:46:24'),
(13,1,'PO baru SO-202605-00008','Sales order dibuat oleh Cre@tiv3','po','sales_order',20,'/admin/po','{\"po_id\": 20}',1,'2026-05-12 09:01:47','2026-05-19 02:41:09'),
(14,1,'PO baru SO-202606-00001','Sales order dibuat oleh Cre@tiv3','po','sales_order',21,'/admin/po','{\"po_id\": 21}',1,'2026-06-05 00:51:40','2026-06-05 00:52:53'),
(15,1,'PO baru SO-202606-00002','Sales order dibuat oleh Cre@tiv3','po','sales_order',25,'/admin/po','{\"po_id\": 25}',1,'2026-06-05 02:49:33','2026-06-05 02:55:11'),
(16,1,'PO baru SO-202606-00003','Sales order dibuat oleh Cre@tiv3','po','sales_order',26,'/admin/po','{\"po_id\": 26}',1,'2026-06-08 21:15:01','2026-06-08 21:50:00'),
(17,1,'PO SO-202606-00003 masuk tahap rekap_printed','Tahap alur marketing diperbarui menjadi: rekap_printed','workflow','sales_order',26,'/admin/marketing-flow','{\"po_id\": 26}',1,'2026-06-08 21:49:42','2026-06-08 21:49:58'),
(18,1,'PO SO-202606-00003 masuk tahap with_ppic','Tahap alur marketing diperbarui menjadi: with_ppic','workflow','sales_order',26,'/admin/marketing-flow','{\"po_id\": 26}',1,'2026-06-08 21:53:26','2026-06-08 21:55:18'),
(19,1,'PO SO-202606-00003 masuk tahap back_to_mkt','Tahap alur marketing diperbarui menjadi: back_to_mkt','workflow','sales_order',26,'/admin/marketing-flow','{\"po_id\": 26}',1,'2026-06-08 21:53:37','2026-06-08 21:55:18'),
(20,1,'PO SO-202606-00003 masuk tahap in_outstanding','Tahap alur marketing diperbarui menjadi: in_outstanding','workflow','sales_order',26,'/admin/marketing-flow','{\"po_id\": 26}',1,'2026-06-08 21:53:43','2026-06-08 21:55:18'),
(21,1,'PO SO-202606-00003 masuk tahap material_followup','Tahap alur marketing diperbarui menjadi: material_followup','workflow','sales_order',26,'/admin/marketing-flow','{\"po_id\": 26}',1,'2026-06-08 21:53:53','2026-06-08 21:55:18'),
(22,1,'PO SO-202606-00002 masuk tahap rekap_printed','Tahap alur marketing diperbarui menjadi: rekap_printed','workflow','sales_order',25,'/admin/marketing-flow','{\"po_id\": 25}',1,'2026-06-08 22:05:46','2026-06-08 22:06:40'),
(23,1,'PO SO-202606-00002 masuk tahap with_ppic','Tahap alur marketing diperbarui menjadi: with_ppic','workflow','sales_order',25,'/admin/marketing-flow','{\"po_id\": 25}',1,'2026-06-08 22:05:50','2026-06-08 22:06:40'),
(24,1,'Status PO SO-202606-00001: confirmed','Diubah oleh demo_marketing','po_status','sales_order',21,'/admin/po','{\"po_id\": 21}',1,'2026-06-08 22:23:05','2026-06-08 23:58:47'),
(25,3,'Status PO SO-202606-00001: confirmed','Diubah oleh demo_marketing','po_status','sales_order',21,'/admin/po','{\"po_id\": 21}',0,'2026-06-08 22:23:05',NULL),
(26,4,'Status PO SO-202606-00001: confirmed','Diubah oleh demo_marketing','po_status','sales_order',21,'/admin/po','{\"po_id\": 21}',0,'2026-06-08 22:23:05',NULL),
(27,5,'Status PO SO-202606-00001: confirmed','Diubah oleh demo_marketing','po_status','sales_order',21,'/admin/po','{\"po_id\": 21}',0,'2026-06-08 22:23:05',NULL),
(28,1,'PO SO-202606-00003 rollback ke tahap in_outstanding','Tahap alur marketing dirollback menjadi: in_outstanding','workflow','sales_order',26,'/admin/marketing-flow','{\"po_id\": 26}',1,'2026-06-08 22:24:34','2026-06-08 23:58:47'),
(29,3,'PO SO-202606-00003 rollback ke tahap in_outstanding','Tahap alur marketing dirollback menjadi: in_outstanding','workflow','sales_order',26,'/admin/marketing-flow','{\"po_id\": 26}',0,'2026-06-08 22:24:34',NULL),
(30,4,'PO SO-202606-00003 rollback ke tahap in_outstanding','Tahap alur marketing dirollback menjadi: in_outstanding','workflow','sales_order',26,'/admin/marketing-flow','{\"po_id\": 26}',0,'2026-06-08 22:24:34',NULL),
(31,1,'PO SO-202606-00001 masuk tahap back_to_mkt','Tahap alur marketing diperbarui menjadi: back_to_mkt','workflow','sales_order',21,'/admin/marketing-flow','{\"po_id\": 21}',1,'2026-06-08 22:25:33','2026-06-08 23:58:47'),
(32,3,'PO SO-202606-00001 masuk tahap back_to_mkt','Tahap alur marketing diperbarui menjadi: back_to_mkt','workflow','sales_order',21,'/admin/marketing-flow','{\"po_id\": 21}',0,'2026-06-08 22:25:33',NULL),
(33,4,'PO SO-202606-00001 masuk tahap back_to_mkt','Tahap alur marketing diperbarui menjadi: back_to_mkt','workflow','sales_order',21,'/admin/marketing-flow','{\"po_id\": 21}',0,'2026-06-08 22:25:33',NULL),
(34,1,'PO SO-202606-00002 rollback ke tahap rekap_printed','Tahap alur marketing dirollback menjadi: rekap_printed','workflow','sales_order',25,'/admin/marketing-flow','{\"po_id\": 25}',1,'2026-06-08 23:58:51','2026-06-09 00:01:57'),
(35,3,'PO SO-202606-00002 rollback ke tahap rekap_printed','Tahap alur marketing dirollback menjadi: rekap_printed','workflow','sales_order',25,'/admin/marketing-flow','{\"po_id\": 25}',0,'2026-06-08 23:58:51',NULL),
(36,4,'PO SO-202606-00002 rollback ke tahap rekap_printed','Tahap alur marketing dirollback menjadi: rekap_printed','workflow','sales_order',25,'/admin/marketing-flow','{\"po_id\": 25}',0,'2026-06-08 23:58:51',NULL),
(37,1,'PO SO-202606-00002 rollback ke tahap input_system','Tahap alur marketing dirollback menjadi: input_system','workflow','sales_order',25,'/admin/marketing-flow','{\"po_id\": 25}',1,'2026-06-08 23:58:58','2026-06-09 00:01:57'),
(38,3,'PO SO-202606-00002 rollback ke tahap input_system','Tahap alur marketing dirollback menjadi: input_system','workflow','sales_order',25,'/admin/marketing-flow','{\"po_id\": 25}',0,'2026-06-08 23:58:58',NULL),
(39,4,'PO SO-202606-00002 rollback ke tahap input_system','Tahap alur marketing dirollback menjadi: input_system','workflow','sales_order',25,'/admin/marketing-flow','{\"po_id\": 25}',0,'2026-06-08 23:58:58',NULL),
(40,1,'PO baru SO-202606-00004','Sales order dibuat oleh Cre@tiv3','po','sales_order',27,'/admin/po','{\"po_id\": 27}',1,'2026-06-11 03:12:42','2026-06-11 11:59:17'),
(41,3,'PO baru SO-202606-00004','Sales order dibuat oleh Cre@tiv3','po','sales_order',27,'/admin/po','{\"po_id\": 27}',0,'2026-06-11 03:12:42',NULL),
(42,4,'PO baru SO-202606-00004','Sales order dibuat oleh Cre@tiv3','po','sales_order',27,'/admin/po','{\"po_id\": 27}',0,'2026-06-11 03:12:42',NULL),
(43,1,'Status PO SO-202606-00004: confirmed','Diubah oleh Cre@tiv3','po_status','sales_order',27,'/admin/po','{\"po_id\": 27}',1,'2026-06-22 12:14:28','2026-06-22 12:15:45'),
(44,3,'Status PO SO-202606-00004: confirmed','Diubah oleh Cre@tiv3','po_status','sales_order',27,'/admin/po','{\"po_id\": 27}',0,'2026-06-22 12:14:28',NULL),
(45,4,'Status PO SO-202606-00004: confirmed','Diubah oleh Cre@tiv3','po_status','sales_order',27,'/admin/po','{\"po_id\": 27}',0,'2026-06-22 12:14:28',NULL),
(46,5,'Status PO SO-202606-00004: confirmed','Diubah oleh Cre@tiv3','po_status','sales_order',27,'/admin/po','{\"po_id\": 27}',0,'2026-06-22 12:14:28',NULL),
(47,1,'PO baru SO-202606-00005','Sales order dibuat oleh Cre@tiv3','po','sales_order',28,'/admin/po','{\"po_id\": 28}',0,'2026-06-30 07:59:59',NULL),
(48,3,'PO baru SO-202606-00005','Sales order dibuat oleh Cre@tiv3','po','sales_order',28,'/admin/po','{\"po_id\": 28}',0,'2026-06-30 07:59:59',NULL),
(49,4,'PO baru SO-202606-00005','Sales order dibuat oleh Cre@tiv3','po','sales_order',28,'/admin/po','{\"po_id\": 28}',0,'2026-06-30 07:59:59',NULL);
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `outstanding_materials`
--

DROP TABLE IF EXISTS `outstanding_materials`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `outstanding_materials` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `po_detail_id` bigint(20) NOT NULL,
  `material_name` varchar(255) DEFAULT NULL,
  `total_qty` decimal(12,2) DEFAULT NULL,
  `delivered_qty` decimal(12,2) DEFAULT NULL,
  `balance_qty` decimal(12,2) DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `po_detail_id` (`po_detail_id`),
  CONSTRAINT `outstanding_materials_ibfk_1` FOREIGN KEY (`po_detail_id`) REFERENCES `po_details` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `outstanding_materials`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `outstanding_materials` WRITE;
/*!40000 ALTER TABLE `outstanding_materials` DISABLE KEYS */;
/*!40000 ALTER TABLE `outstanding_materials` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `packing_details`
--

DROP TABLE IF EXISTS `packing_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `packing_details` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `packing_id` bigint(20) DEFAULT NULL,
  `production_detail_id` bigint(20) DEFAULT NULL,
  `qty_packed` decimal(12,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `packing_id` (`packing_id`),
  KEY `production_detail_id` (`production_detail_id`),
  CONSTRAINT `packing_details_ibfk_1` FOREIGN KEY (`packing_id`) REFERENCES `packing_headers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `packing_details_ibfk_2` FOREIGN KEY (`production_detail_id`) REFERENCES `production_details` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `packing_details`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `packing_details` WRITE;
/*!40000 ALTER TABLE `packing_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `packing_details` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `packing_headers`
--

DROP TABLE IF EXISTS `packing_headers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `packing_headers` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `packing_number` varchar(100) DEFAULT NULL,
  `production_id` bigint(20) DEFAULT NULL,
  `qc_header_id` bigint(20) DEFAULT NULL,
  `status` varchar(32) NOT NULL DEFAULT 'draft',
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `invpl_printed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `packing_number` (`packing_number`),
  KEY `production_id` (`production_id`),
  KEY `qc_header_id` (`qc_header_id`),
  CONSTRAINT `packing_headers_ibfk_1` FOREIGN KEY (`production_id`) REFERENCES `production_orders` (`id`),
  CONSTRAINT `packing_headers_ibfk_2` FOREIGN KEY (`qc_header_id`) REFERENCES `qc_headers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `packing_headers`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `packing_headers` WRITE;
/*!40000 ALTER TABLE `packing_headers` DISABLE KEYS */;
/*!40000 ALTER TABLE `packing_headers` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `po_detail_deliveries`
--

DROP TABLE IF EXISTS `po_detail_deliveries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `po_detail_deliveries` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `po_detail_id` bigint(20) NOT NULL,
  `sequence_no` int(11) NOT NULL,
  `qty` decimal(14,2) DEFAULT NULL,
  `delivery_date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_po_detail_deliveries_detail_seq` (`po_detail_id`,`sequence_no`),
  CONSTRAINT `po_detail_deliveries_ibfk_1` FOREIGN KEY (`po_detail_id`) REFERENCES `po_details` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=130 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `po_detail_deliveries`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `po_detail_deliveries` WRITE;
/*!40000 ALTER TABLE `po_detail_deliveries` DISABLE KEYS */;
INSERT INTO `po_detail_deliveries` VALUES
(1,1,1,40.00,'2026-05-06'),
(2,1,2,35.00,'2026-05-13'),
(3,1,3,25.00,'2026-05-20'),
(4,2,1,50.00,'2026-05-06'),
(5,2,2,43.75,'2026-05-13'),
(6,2,3,31.25,'2026-05-20'),
(7,3,1,60.00,'2026-05-06'),
(8,3,2,52.50,'2026-05-13'),
(9,3,3,37.50,'2026-05-20'),
(10,4,1,70.00,'2026-05-06'),
(11,4,2,61.25,'2026-05-13'),
(12,4,3,43.75,'2026-05-20'),
(13,5,1,80.00,'2026-05-06'),
(14,5,2,70.00,'2026-05-13'),
(15,5,3,50.00,'2026-05-20'),
(16,6,1,90.00,'2026-05-06'),
(17,6,2,78.75,'2026-05-13'),
(18,6,3,56.25,'2026-05-20'),
(19,7,1,100.00,'2026-05-06'),
(20,7,2,87.50,'2026-05-13'),
(21,7,3,62.50,'2026-05-20'),
(22,8,1,110.00,'2026-05-06'),
(23,8,2,96.25,'2026-05-13'),
(24,8,3,68.75,'2026-05-20'),
(25,9,1,120.00,'2026-05-06'),
(26,9,2,105.00,'2026-05-13'),
(27,9,3,75.00,'2026-05-20'),
(64,10,1,130.00,'2026-05-06'),
(65,10,2,113.75,'2026-05-13'),
(66,10,3,81.25,'2026-05-20'),
(67,11,1,1.00,'2026-05-04'),
(68,11,2,1.00,'2026-05-11'),
(69,11,3,1.00,'2026-05-18'),
(70,11,4,1.00,'2026-05-25'),
(71,11,5,1.00,'2026-06-01'),
(72,11,6,1.00,'2026-06-08'),
(73,11,7,1.00,'2026-06-15'),
(74,11,8,1.00,'2026-06-22'),
(75,11,9,1.00,'2026-06-29'),
(76,11,10,1.00,'2026-07-06'),
(77,11,11,0.00,'2026-07-13'),
(78,11,12,0.00,'2026-07-20'),
(79,12,1,1.00,'2026-05-04'),
(80,12,2,1.00,'2026-05-11'),
(81,12,3,1.00,'2026-05-18'),
(82,12,4,1.00,'2026-05-25'),
(83,12,5,1.00,'2026-06-01'),
(84,12,6,1.00,'2026-06-08'),
(85,12,7,1.00,'2026-06-15'),
(86,12,8,1.00,'2026-06-22'),
(87,12,9,1.00,'2026-06-29'),
(88,12,10,1.00,'2026-07-06'),
(89,12,11,0.00,'2026-07-13'),
(90,12,12,0.00,'2026-07-20'),
(91,13,1,1.00,'2026-05-04'),
(92,13,2,1.00,'2026-05-11'),
(93,13,3,1.00,'2026-05-18'),
(94,13,4,1.00,'2026-05-25'),
(95,13,5,1.00,'2026-06-01'),
(96,13,6,1.00,'2026-06-08'),
(97,13,7,1.00,'2026-06-15'),
(98,13,8,1.00,'2026-06-22'),
(99,13,9,1.00,'2026-06-29'),
(100,13,10,1.00,'2026-07-06'),
(101,13,11,0.00,'2026-07-13'),
(102,13,12,0.00,'2026-07-20'),
(103,14,1,1.00,'2026-05-04'),
(104,14,2,1.00,'2026-05-11'),
(105,14,3,1.00,'2026-05-18'),
(106,14,4,1.00,'2026-05-25'),
(107,14,5,1.00,'2026-06-01'),
(108,14,6,1.00,'2026-06-08'),
(109,14,7,1.00,'2026-06-15'),
(110,14,8,1.00,'2026-06-22'),
(111,14,9,1.00,'2026-06-29'),
(112,14,10,1.00,'2026-07-06'),
(113,14,11,0.00,'2026-07-13'),
(114,14,12,0.00,'2026-07-20'),
(115,21,1,1.00,'2026-05-12'),
(116,21,2,1.00,'2026-05-19'),
(117,21,3,1.00,'2026-05-26'),
(118,21,4,1.00,'2026-06-02'),
(119,21,5,1.00,'2026-06-09'),
(120,21,6,1.00,'2026-06-16'),
(121,21,7,1.00,'2026-06-23'),
(122,21,8,1.00,'2026-06-30'),
(123,21,9,1.00,'2026-07-07'),
(124,21,10,1.00,'2026-07-14'),
(125,21,11,1.00,'2026-07-21'),
(126,21,12,1.00,'2026-07-28'),
(127,26,1,2000.00,'2026-06-05'),
(128,29,1,90.00,'2026-06-09'),
(129,30,1,100.00,'2026-06-11');
/*!40000 ALTER TABLE `po_detail_deliveries` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `po_details`
--

DROP TABLE IF EXISTS `po_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `po_details` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `po_id` bigint(20) DEFAULT NULL,
  `material_name` varchar(255) DEFAULT NULL,
  `color` varchar(100) DEFAULT NULL,
  `thickness_min` decimal(10,3) DEFAULT NULL,
  `thickness_max` decimal(10,3) DEFAULT NULL,
  `softness` varchar(100) DEFAULT NULL,
  `color_reference` varchar(255) DEFAULT NULL,
  `backing` varchar(255) DEFAULT NULL,
  `quantity_order` decimal(12,2) DEFAULT NULL,
  `style_article` varchar(100) DEFAULT NULL,
  `model` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `line_etd` date DEFAULT NULL,
  `unit_price` decimal(14,4) DEFAULT NULL,
  `copied_from_detail_id` bigint(20) DEFAULT NULL,
  `master_item_id` bigint(20) DEFAULT NULL,
  `thi_line_ref` varchar(100) DEFAULT NULL,
  `emboss` varchar(255) DEFAULT NULL,
  `thickness_text` varchar(80) DEFAULT NULL,
  `vir_softness_type` varchar(100) DEFAULT NULL,
  `rtd_text` varchar(80) DEFAULT NULL,
  `etd_excel_serial` int(11) DEFAULT NULL,
  `stock_wh_qty` decimal(14,2) DEFAULT NULL,
  `balance_qty` decimal(14,2) DEFAULT NULL,
  `system_reference` varchar(120) DEFAULT NULL,
  `detail_remark` text DEFAULT NULL,
  `color_family` varchar(32) DEFAULT NULL,
  `marketing_outstanding_remark` text DEFAULT NULL,
  `color_standard` varchar(255) DEFAULT NULL,
  `color_swatch_recipe_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_po_details_master_item_id` (`master_item_id`),
  KEY `ix_po_details_po_id` (`po_id`),
  KEY `ix_po_details_color_swatch_recipe_id` (`color_swatch_recipe_id`),
  CONSTRAINT `fk_po_details_color_swatch_recipe` FOREIGN KEY (`color_swatch_recipe_id`) REFERENCES `color_swatch_recipes` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_po_details_master_item_id` FOREIGN KEY (`master_item_id`) REFERENCES `master_items` (`id`) ON DELETE SET NULL,
  CONSTRAINT `po_details_ibfk_1` FOREIGN KEY (`po_id`) REFERENCES `po_headers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `po_details`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `po_details` WRITE;
/*!40000 ALTER TABLE `po_details` DISABLE KEYS */;
INSERT INTO `po_details` VALUES
(1,2,'VIRGIN HYDRO PU','BLACK (00A)',NULL,NULL,NULL,NULL,NULL,100.00,NULL,NULL,'2026-04-29 21:19:20','2026-05-06',1.1500,NULL,2,NULL,'AR-167 (DEEP MATTE)','1.24',NULL,NULL,NULL,NULL,NULL,'SYS-SO-202604-00001','auto seed transaksi','black',NULL,NULL,NULL),
(2,3,'VIRGIN HYDRO PU','BLACK (00A)',NULL,NULL,NULL,NULL,NULL,125.00,NULL,NULL,'2026-04-29 21:19:20','2026-05-07',1.0000,NULL,3,NULL,'UM-34 (MATTE)','1.46',NULL,NULL,NULL,NULL,NULL,'SYS-SO-202604-00002','auto seed transaksi','black',NULL,NULL,NULL),
(3,4,'VIRGIN HYDRO PU','WHITE (10A)',NULL,NULL,NULL,NULL,NULL,150.00,NULL,NULL,'2026-04-29 21:19:20','2026-05-08',1.1000,NULL,4,NULL,'AR-193 (MATTE)','1.46',NULL,NULL,NULL,NULL,NULL,'SYS-SO-202604-00003','auto seed transaksi','color',NULL,NULL,NULL),
(4,5,'SOFT PU COATED LEATHER (MAP-SOFT PU)','YELLOW (003A)',NULL,NULL,NULL,NULL,NULL,175.00,NULL,NULL,'2026-04-29 21:19:20','2026-05-09',1.0000,NULL,5,NULL,'DE-73 (SEMI MATTE)','1.46',NULL,NULL,NULL,NULL,NULL,'SYS-SO-202604-00004','auto seed transaksi','color',NULL,NULL,NULL),
(5,6,'ECO TECH COMFORT','BLACK (00A)',NULL,NULL,NULL,NULL,NULL,200.00,NULL,NULL,'2026-04-29 21:19:20','2026-05-10',1.2800,NULL,6,NULL,'DE-43 (SEMI MATTE)','1.24',NULL,NULL,NULL,NULL,NULL,'SYS-SO-202604-00005','auto seed transaksi','black',NULL,NULL,NULL),
(6,7,'(PM) GENERIC PU COATED LEATHER','BLACK (00A)',NULL,NULL,NULL,NULL,NULL,225.00,NULL,NULL,'2026-04-29 21:19:20','2026-05-11',1.1200,NULL,7,NULL,'R-8 (SEMI GLOSS)','1.46',NULL,NULL,NULL,NULL,NULL,'SYS-SO-202604-00006','auto seed transaksi','black',NULL,NULL,NULL),
(7,8,'(PM) GENERIC PU COATED LEATHER','WOLF GREY (01V)',NULL,NULL,NULL,NULL,NULL,250.00,NULL,NULL,'2026-04-29 21:19:20','2026-05-12',1.0700,NULL,8,NULL,'DE-73 (SEMI MATTE)','1.02',NULL,NULL,NULL,NULL,NULL,'SYS-SO-202604-00007','auto seed transaksi','color',NULL,NULL,NULL),
(8,9,'VIRGIN HYDRO PU','OXYGEN PURPLE (5AX)',NULL,NULL,NULL,NULL,NULL,275.00,NULL,NULL,'2026-04-29 21:19:20','2026-05-13',1.1000,NULL,9,NULL,'AR-140 (MATTE)','1.24',NULL,NULL,NULL,NULL,NULL,'SYS-SO-202604-00008','auto seed transaksi','color',NULL,NULL,NULL),
(9,10,'ECO TECH COMFORT','WHITE (10A)',NULL,NULL,NULL,NULL,NULL,300.00,NULL,NULL,'2026-04-29 21:19:20','2026-05-14',1.5000,NULL,10,NULL,'AR-107 (MATTE)','1.24',NULL,NULL,NULL,NULL,NULL,'SYS-SO-202604-00009','auto seed transaksi','color',NULL,NULL,NULL),
(10,11,'(PM) GENERIC PU COATED LEATHER','LT SMOKE GREY (0AL)',NULL,NULL,NULL,NULL,NULL,325.00,NULL,NULL,'2026-04-29 21:19:20','2026-05-15',1.0000,NULL,11,NULL,'UM-34T (SEMI MATTE)','1.24',NULL,NULL,NULL,NULL,NULL,'SYS-SO-202604-00010','auto seed transaksi','color',NULL,NULL,NULL),
(11,13,'VIRGIN HYDRO PU','AURA (4AH)',NULL,NULL,NULL,NULL,NULL,10.00,NULL,NULL,'2026-05-04 03:01:47','2026-05-04',NULL,NULL,19,NULL,'AR-20 (MATTE)','1.24','Soft',NULL,NULL,NULL,NULL,NULL,NULL,'color',NULL,NULL,NULL),
(12,13,'ECO TECH COMFORT','BLACK (00A)',NULL,NULL,NULL,NULL,NULL,12.00,NULL,NULL,'2026-05-04 03:01:47',NULL,1.9400,NULL,6,NULL,'DE-43 (SEMI MATTE)','1.24',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'black',NULL,NULL,NULL),
(13,13,'(PM) GENERIC PU COATED LEATHER','BLACK (00A)',NULL,NULL,NULL,NULL,NULL,1200.00,NULL,NULL,'2026-05-04 03:01:48',NULL,10.0000,NULL,7,NULL,'R-8 (SEMI GLOSS)','1.46',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'black',NULL,NULL,NULL),
(14,13,'VIRGIN HYDRO PU','OXYGEN PURPLE (5AX)',NULL,NULL,NULL,NULL,NULL,1000.00,NULL,NULL,'2026-05-04 03:01:48',NULL,10.0000,NULL,9,NULL,'AR-140 (MATTE)','1.24',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'color',NULL,NULL,NULL),
(15,13,'VIRGIN HYDRO PU','AURA (4AH)',NULL,NULL,NULL,NULL,NULL,10.00,NULL,NULL,'2026-05-04 03:01:49',NULL,10.0000,NULL,19,NULL,'AR-20 (MATTE)','1.24',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'color',NULL,NULL,NULL),
(21,15,'(PM) GENERIC PU COATED LEATHER','BLACK (00A)',NULL,NULL,NULL,NULL,NULL,12.00,NULL,NULL,'2026-05-11 18:47:28','2026-05-12',1.1200,NULL,7,'PUM123456260511004','R-8 (SEMI GLOSS)','1.46','Vir Soft',NULL,NULL,NULL,NULL,NULL,NULL,'black',NULL,NULL,NULL),
(22,18,'ECO TECH COMFORT','BLACK (00A)',NULL,NULL,NULL,NULL,NULL,12.00,NULL,NULL,'2026-05-11 19:29:36',NULL,1.2800,NULL,6,'PUMccc260511001','DE-43 (SEMI MATTE)','1.24','Vir Soft',NULL,NULL,NULL,NULL,NULL,NULL,'black',NULL,NULL,NULL),
(23,19,'(PM) GENERIC PU COATED LEATHER','WOLF GREY (01V)',NULL,NULL,NULL,NULL,NULL,1000.00,NULL,NULL,'2026-05-12 03:19:56',NULL,11.0700,NULL,8,'PUMAD002260512001','DE-73 (SEMI MATTE)','1.02','Vir Soft',NULL,NULL,NULL,NULL,NULL,'test','color',NULL,NULL,NULL),
(26,21,'(PM) GENERIC PU COATED LEATHER','ACTIVE FUCHSIA',NULL,NULL,NULL,'6HJ','6DX',2000.00,NULL,NULL,'2026-06-05 00:51:40',NULL,1.0700,NULL,NULL,'PUMSL044260605005','B-27','1.02','Vir Soft',NULL,NULL,NULL,NULL,NULL,NULL,'color',NULL,'TMAD0022022061001',NULL),
(27,25,'(PM) GENERIC PU COATED LEATHER','LT SMOKE GREY (0AL)',NULL,NULL,NULL,NULL,NULL,1000.00,NULL,NULL,'2026-06-05 02:49:33',NULL,1.0700,NULL,11,'PUMAD002260605001','UM-34T (SEMI MATTE)','1.24','Vir Soft',NULL,NULL,NULL,NULL,NULL,NULL,'color',NULL,NULL,NULL),
(28,25,'HYDRO SOFT ACTION LEATHER','BLACK (NB1000018)',NULL,NULL,NULL,NULL,'Free text',2000.00,'Free Text','Free text','2026-06-05 02:49:33',NULL,10.0000,NULL,13,'PUMAD002260605002','R-51 (SEMI MATTE)','1.24',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'black',NULL,'TMAD00XXXX',NULL),
(29,26,'CASHMERE SUEDE','BETTER SCARLET (AETG)',NULL,NULL,NULL,NULL,'mm',90.00,NULL,'mm','2026-06-08 21:15:01',NULL,1.0600,NULL,26,'MYCTK028260608001',NULL,'1.2 - 1.4','Vir Soft',NULL,NULL,NULL,NULL,NULL,'kkkjkj','color',NULL,'mmm',NULL),
(30,27,'(PM) GENERIC PU COATED LEATHER','WOLF GREY (01V)',NULL,NULL,NULL,NULL,NULL,100.00,NULL,NULL,'2026-06-11 03:12:42',NULL,1.0700,NULL,8,'PUMSL044260611001','DE-73 (SEMI MATTE)','1.0 - 1.2','Vir Soft',NULL,NULL,NULL,NULL,NULL,'a','color',NULL,NULL,NULL),
(31,28,'(PM) GENERIC PU COATED LEATHER','WOLF GREY (01V)',NULL,NULL,NULL,NULL,NULL,1000.00,NULL,NULL,'2026-06-30 07:59:59',NULL,1.0700,NULL,8,'PUMSL044260630001','DE-73 (SEMI MATTE)','1.0 - 1.2','Vir Soft',NULL,NULL,NULL,NULL,NULL,NULL,'color',NULL,NULL,NULL);
/*!40000 ALTER TABLE `po_details` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `po_headers`
--

DROP TABLE IF EXISTS `po_headers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `po_headers` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `po_number` varchar(100) DEFAULT NULL,
  `customer_id` bigint(20) DEFAULT NULL,
  `customer_code` varchar(50) DEFAULT NULL,
  `po_category` varchar(32) NOT NULL,
  `buyer` varchar(100) DEFAULT NULL,
  `order_date` date DEFAULT NULL,
  `etd` date DEFAULT NULL,
  `status` varchar(32) NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL,
  `billing_address` text DEFAULT NULL,
  `delivery_address` text DEFAULT NULL,
  `brand_id` bigint(20) DEFAULT NULL,
  `marketing_excel_date_serial` int(11) DEFAULT NULL,
  `po_customer_ref` text DEFAULT NULL,
  `order_type_label` varchar(50) DEFAULT NULL,
  `brand_name_snapshot` varchar(255) DEFAULT NULL,
  `customer_name_snapshot` varchar(255) DEFAULT NULL,
  `customs_declaration_id` bigint(20) DEFAULT NULL,
  `mkt_workflow_stage` varchar(48) NOT NULL,
  `mkt_workflow_updated_at` datetime DEFAULT NULL,
  `rekap_printed_at` datetime DEFAULT NULL,
  `material_followup_remark` text DEFAULT NULL,
  `material_followup_done` tinyint(1) NOT NULL DEFAULT 0,
  `factory_code` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `po_number` (`po_number`),
  KEY `fk_po_headers_brand` (`brand_id`),
  KEY `ix_po_headers_customs_declaration_id` (`customs_declaration_id`),
  KEY `ix_po_headers_customer_id` (`customer_id`),
  KEY `ix_po_headers_mkt_workflow_stage` (`mkt_workflow_stage`),
  KEY `ix_po_headers_status` (`status`),
  CONSTRAINT `fk_po_headers_brand` FOREIGN KEY (`brand_id`) REFERENCES `brands` (`id`),
  CONSTRAINT `fk_po_headers_customs_declaration_id` FOREIGN KEY (`customs_declaration_id`) REFERENCES `customs_declarations` (`id`) ON DELETE SET NULL,
  CONSTRAINT `po_headers_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `po_headers`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `po_headers` WRITE;
/*!40000 ALTER TABLE `po_headers` DISABLE KEYS */;
INSERT INTO `po_headers` VALUES
(2,'SO-202604-00001',1,'AD002','production','NIKE','2026-04-29','2026-05-06','draft','2026-04-29 21:19:20',NULL,'JL.RAYA SERANG KM 24 BALARAJA,TANGERANG INDONESIA 15610','JL.RAYA SERANG KM 24 BALARAJA,TANGERANG INDONESIA 15610',1,NULL,'AUTO-0429-001','PROD','NIKE','PT. ADIS DIMENSION FOOTWEAR',NULL,'input_system',NULL,NULL,NULL,0,NULL),
(3,'SO-202604-00002',2,'BI020','production','ADIDAS','2026-04-29','2026-05-07','draft','2026-04-29 21:19:20',NULL,'JL. CENDRAWASIH TENGGULI NO. 6 KM. 20 KEL. TENGGULI KEC. TANJUNG BREBES JAWA TENGAH','JL. CENDRAWASIH TENGGULI NO. 6 KM. 20 KEL. TENGGULI KEC. TANJUNG BREBES JAWA TENGAH',3,NULL,'AUTO-0429-002','PROD','ADIDAS','PT. BINTANG INDOKARYA GEMILANG (PBB)',NULL,'input_system',NULL,NULL,NULL,0,NULL),
(4,'SO-202604-00003',3,'CS004','production','NIKE','2026-04-29','2026-05-08','draft','2026-04-29 21:19:20',NULL,'JL. DUSUN GINTUNGKOLOT RT 16/04 DESA GINTUNGKERTA,KLARI KARAWANG-JABAR','JL. DUSUN GINTUNGKOLOT RT 16/04 DESA GINTUNGKERTA,KLARI KARAWANG-JABAR',1,NULL,'AUTO-0429-003','PROD','NIKE','PT. CHANG SHIN INDONESIA',NULL,'input_system',NULL,NULL,NULL,0,NULL),
(5,'SO-202604-00004',4,'CS005','production','NIKE','2026-04-29','2026-05-09','draft','2026-04-29 21:19:20',NULL,'JL. RAYA LELES NO.134, KAMPUNG KARANG MEKAR RT.02 RW.08 DS. CIBURIAL KECAMATAN LELES  , GARUT','JL. RAYA LELES NO.134, KAMPUNG KARANG MEKAR RT.02 RW.08 DS. CIBURIAL KECAMATAN LELES  , GARUT',1,NULL,'AUTO-0429-004','PROD','NIKE','PT. CHANGSHIN REKSA JAYA',NULL,'input_system',NULL,NULL,NULL,0,NULL),
(6,'SO-202604-00005',5,'CL017','production','NIKE','2026-04-29','2026-05-10','draft','2026-04-29 21:19:20',NULL,'JL. RAYA SERANG KM.16 DESA TALAGASARI KEC.CIKUPA TANGERANG INDONESIA 15710','JL. RAYA SERANG KM.16 DESA TALAGASARI KEC.CIKUPA TANGERANG INDONESIA 15710',1,NULL,'AUTO-0429-005','PROD','NIKE','PT. CHING LUH INDONESIA',NULL,'input_system',NULL,NULL,NULL,0,NULL),
(7,'SO-202604-00006',7,'FT006','production','NIKE','2026-04-29','2026-05-11','draft','2026-04-29 21:19:20',NULL,'JL.RAYA BANJARAN KM.14,6,DESA BOJONG MANGGU KEC.PAMEUNGPEUK,BANDUNG-JABAR','JL.RAYA BANJARAN KM.14,6,DESA BOJONG MANGGU KEC.PAMEUNGPEUK,BANDUNG-JABAR',1,NULL,'AUTO-0429-006','PROD','NIKE','PT. FENG TAY INDONESIA ENTERPRISES (WEST)',NULL,'input_system',NULL,NULL,NULL,0,NULL),
(8,'SO-202604-00007',8,'FT007','production','NIKE','2026-04-29','2026-05-12','draft','2026-04-29 21:19:20',NULL,'JL.RAYA BANJARAN KM.14,6,DESA BOJONG MANGGU KEC.PAMEUNGPEUK,BANDUNG-JABAR','JL.RAYA BANJARAN KM.14,6,DESA BOJONG MANGGU KEC.PAMEUNGPEUK,BANDUNG-JABAR',1,NULL,'AUTO-0429-007','PROD','NIKE','PT. FENG TAY INDONESIA ENTERPRISES (EAST)',NULL,'input_system',NULL,NULL,NULL,0,NULL),
(9,'SO-202604-00008',9,'FT008','production','NIKE','2026-04-29','2026-05-13','draft','2026-04-29 21:19:20',NULL,'JL. RAYA BANJARAN KM.14,6 DESA BOJONG MANGGU KEC. PAMEUNGPEUK, BANDUNG-JABAR','JL. RAYA BANJARAN KM.14,6 DESA BOJONG MANGGU KEC. PAMEUNGPEUK, BANDUNG-JABAR',1,NULL,'AUTO-0429-008','PROD','NIKE','PT. FENG TAY INDONESIA ENTERPRISES (NORTH)',NULL,'input_system',NULL,NULL,NULL,0,NULL),
(10,'SO-202604-00009',10,'PGS30','production','ADIDAS','2026-04-29','2026-05-14','draft','2026-04-29 21:19:20',NULL,'JL. RAYA SUKABUMI-CIANJUR KM13 DESA TITISAN , KECAMATAN SUKALARANG','JL. RAYA SUKABUMI-CIANJUR KM13 DESA TITISAN , KECAMATAN SUKALARANG',3,NULL,'AUTO-0429-009','PROD','ADIDAS','PT. GLOSTAR INDONESIA (PGS)',NULL,'input_system',NULL,NULL,NULL,0,NULL),
(11,'SO-202604-00010',2,'GS007','production','ADIDAS','2026-04-29','2026-05-15','draft','2026-04-29 21:19:20',NULL,'JL.PELABUHAN II KM.14,5 KP.SAMPORA RT.3 RW. 5 DS.BOJONGRAHARJA, KEC.CIKEMBAR SUKABUMI-JABAR','JL.PELABUHAN II KM.14,5 KP.SAMPORA RT.3 RW. 5 DS.BOJONGRAHARJA, KEC.CIKEMBAR SUKABUMI-JABAR',3,NULL,'AUTO-0429-010','PROD','ADIDAS','PT. GLOSTAR INDONESIA (PGD)',NULL,'input_system',NULL,NULL,NULL,0,NULL),
(13,'SO-202605-00001',33,NULL,'production','UA','2026-05-04','2026-05-04','draft','2026-05-04 03:01:46',NULL,'JL. RAYA BANAR KEL. KETIMANG KEC. WONOAYU SIDOARJO JAWA TIMUR','JL. RAYA BANAR KEL. KETIMANG KEC. WONOAYU SIDOARJO JAWA TIMUR',5,NULL,'NO123456',NULL,NULL,NULL,NULL,'input_system',NULL,NULL,NULL,0,NULL),
(15,'SO-202605-00003',1,NULL,'production','NIKE','2026-05-12','2026-05-12','draft','2026-05-11 18:47:28',NULL,'26, GIMHAE-DAERO 2635BEON-GIL , GIMHAE , KOREA','26, GIMHAE-DAERO 2635BEON-GIL , GIMHAE , KOREA',1,NULL,'123',NULL,NULL,NULL,NULL,'input_system',NULL,NULL,NULL,0,'123456'),
(16,'SO-202605-00004',1,NULL,'production','NIKE','2026-05-12',NULL,'draft','2026-05-11 19:25:24',NULL,'JL.RAYA SERANG KM 24 BALARAJA,TANGERANG INDONESIA 15610','JL.RAYA SERANG KM 24 BALARAJA,TANGERANG INDONESIA 15610',1,NULL,'PO-SO-202605-00004',NULL,NULL,NULL,NULL,'input_system',NULL,NULL,NULL,0,NULL),
(17,'SO-202605-00005',1,NULL,'production','NIKE','2026-05-12',NULL,'draft','2026-05-11 19:28:20',NULL,'JL.RAYA SERANG KM 24 BALARAJA,TANGERANG INDONESIA 15610','JL.RAYA SERANG KM 24 BALARAJA,TANGERANG INDONESIA 15610',1,NULL,'PO-SO-202605-00005',NULL,NULL,NULL,NULL,'input_system',NULL,NULL,NULL,0,NULL),
(18,'SO-202605-00006',1,NULL,'production','NIKE','2026-05-12',NULL,'draft','2026-05-11 19:29:31',NULL,'NO. 2 FU KUN ROAD,FU HISN,CHANG HWA,TAIWAN R.O.C.','NO. 2 FU KUN ROAD,FU HISN,CHANG HWA,TAIWAN R.O.C.',1,NULL,'PO-SO-202605-00006',NULL,NULL,NULL,NULL,'input_system',NULL,NULL,NULL,0,'ccc'),
(19,'SO-202605-00007',1,NULL,'production','NIKE','2026-05-12',NULL,'draft','2026-05-12 03:19:54',NULL,'372DRP, LOK MA CHAU, SAN TIN, NT, HONG KONG','372DRP, LOK MA CHAU, SAN TIN, NT, HONG KONG',1,NULL,'POABC',NULL,NULL,NULL,NULL,'input_system',NULL,NULL,NULL,0,'AD002'),
(21,'SO-202606-00001',1,'AD002','production','NIKE','2026-06-05',NULL,'confirmed','2026-06-05 00:51:40',NULL,'372DRP, LOK MA CHAU, SAN TIN, NT, HONG KONG','372DRP, LOK MA CHAU, SAN TIN, NT, HONG KONG',1,NULL,'PO-SO-202606-00001',NULL,'NIKE','PT. ADIS DIMENSION FOOTWEAR',NULL,'back_to_mkt','2026-06-08 22:25:33','2026-06-08 22:22:19',NULL,1,'SL044'),
(25,'SO-202606-00002',1,'AD002','production','NIKE','2026-06-05',NULL,'draft','2026-06-05 02:49:33',NULL,'JL.RAYA SERANG KM 24 BALARAJA,TANGERANG INDONESIA 15610','JL.RAYA SERANG KM 24 BALARAJA,TANGERANG INDONESIA 15610',1,NULL,'ABC123',NULL,'NIKE','PT. ADIS DIMENSION FOOTWEAR',NULL,'input_system','2026-06-08 23:58:58','2026-06-08 22:05:46',NULL,1,'AD002'),
(26,'SO-202606-00003',60,'TK028','production','NIKE','2026-06-09',NULL,'draft','2026-06-08 21:15:01',NULL,'26, GIMHAE-DAERO 2635BEON-GIL , GIMHAE , KOREA','26, GIMHAE-DAERO 2635BEON-GIL , GIMHAE , KOREA',1,NULL,'mmm',NULL,'NIKE','TAE KWANG INDUSTRIAL CO LTD',NULL,'material_followup','2026-06-08 23:57:42','2026-06-08 21:49:41',NULL,1,'TK028'),
(27,'SO-202606-00004',61,'SL044','production','NIKE','2026-06-11',NULL,'confirmed','2026-06-11 03:12:42',NULL,'372DRP, LOK MA CHAU, SAN TIN, NT, HONG KONG','372DRP, LOK MA CHAU, SAN TIN, NT, HONG KONG',1,NULL,'123',NULL,'NIKE','WEALTH VAST CO,LTD',NULL,'input_system',NULL,NULL,NULL,1,'SL044'),
(28,'SO-202606-00005',61,'SL044','production','NIKE','2026-06-30',NULL,'draft','2026-06-30 07:59:59',NULL,'372DRP, LOK MA CHAU, SAN TIN, NT, HONG KONG','372DRP, LOK MA CHAU, SAN TIN, NT, HONG KONG',1,NULL,'123456777',NULL,'NIKE','WEALTH VAST CO,LTD',NULL,'input_system',NULL,NULL,NULL,0,'SL044');
/*!40000 ALTER TABLE `po_headers` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `ppic_assignments`
--

DROP TABLE IF EXISTS `ppic_assignments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ppic_assignments` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `po_id` bigint(20) NOT NULL,
  `ppic_user_id` bigint(20) NOT NULL,
  `status` varchar(20) NOT NULL,
  `notes` text DEFAULT NULL,
  `assigned_at` timestamp NULL DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL,
  `po_detail_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `po_id` (`po_id`),
  KEY `ppic_user_id` (`ppic_user_id`),
  KEY `po_detail_id` (`po_detail_id`),
  CONSTRAINT `ppic_assignments_ibfk_1` FOREIGN KEY (`po_id`) REFERENCES `po_headers` (`id`),
  CONSTRAINT `ppic_assignments_ibfk_2` FOREIGN KEY (`ppic_user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `ppic_assignments_ibfk_3` FOREIGN KEY (`po_detail_id`) REFERENCES `po_details` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ppic_assignments`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `ppic_assignments` WRITE;
/*!40000 ALTER TABLE `ppic_assignments` DISABLE KEYS */;
INSERT INTO `ppic_assignments` VALUES
(1,21,4,'completed','UAT','2026-06-08 22:24:20','2026-06-08 22:25:08',NULL),
(2,26,4,'completed','mmm','2026-06-08 23:57:42','2026-06-09 00:01:39',NULL);
/*!40000 ALTER TABLE `ppic_assignments` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `production_details`
--

DROP TABLE IF EXISTS `production_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `production_details` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `production_id` bigint(20) DEFAULT NULL,
  `po_detail_id` bigint(20) DEFAULT NULL,
  `qty_planned` decimal(12,2) DEFAULT NULL,
  `qty_actual` decimal(12,2) DEFAULT NULL,
  `lot_number` varchar(100) DEFAULT NULL,
  `batch_number` varchar(100) DEFAULT NULL,
  `status` varchar(32) NOT NULL,
  `is_over_production` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `production_id` (`production_id`),
  KEY `po_detail_id` (`po_detail_id`),
  CONSTRAINT `production_details_ibfk_2` FOREIGN KEY (`production_id`) REFERENCES `production_orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `production_details_ibfk_3` FOREIGN KEY (`po_detail_id`) REFERENCES `po_details` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `production_details`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `production_details` WRITE;
/*!40000 ALTER TABLE `production_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `production_details` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `production_orders`
--

DROP TABLE IF EXISTS `production_orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `production_orders` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `production_number` varchar(100) DEFAULT NULL,
  `po_id` bigint(20) DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `status` varchar(32) NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `production_number` (`production_number`),
  KEY `po_id` (`po_id`),
  CONSTRAINT `production_orders_ibfk_1` FOREIGN KEY (`po_id`) REFERENCES `po_headers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `production_orders`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `production_orders` WRITE;
/*!40000 ALTER TABLE `production_orders` DISABLE KEYS */;
/*!40000 ALTER TABLE `production_orders` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `qc_details`
--

DROP TABLE IF EXISTS `qc_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `qc_details` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `qc_id` bigint(20) DEFAULT NULL,
  `production_detail_id` bigint(20) DEFAULT NULL,
  `roll_number` varchar(50) DEFAULT NULL,
  `batch_number` varchar(100) DEFAULT NULL,
  `thickness_actual` decimal(10,3) DEFAULT NULL,
  `softness_actual` varchar(100) DEFAULT NULL,
  `thickness_min` decimal(10,3) DEFAULT NULL,
  `thickness_max` decimal(10,3) DEFAULT NULL,
  `softness_standard` varchar(100) DEFAULT NULL,
  `result` varchar(8) DEFAULT NULL,
  `is_ok` tinyint(1) DEFAULT NULL,
  `device_id` varchar(50) DEFAULT NULL,
  `port` varchar(20) DEFAULT NULL,
  `raw_value` varchar(100) DEFAULT NULL,
  `remark` text DEFAULT NULL,
  `measured_at` datetime DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `qty_checked` decimal(12,2) DEFAULT NULL,
  `qty_reject` decimal(12,2) DEFAULT NULL,
  `reject_reason` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `production_detail_id` (`production_detail_id`),
  KEY `qc_id` (`qc_id`),
  CONSTRAINT `qc_details_ibfk_1` FOREIGN KEY (`production_detail_id`) REFERENCES `production_details` (`id`),
  CONSTRAINT `qc_details_ibfk_2` FOREIGN KEY (`qc_id`) REFERENCES `qc_headers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `qc_details`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `qc_details` WRITE;
/*!40000 ALTER TABLE `qc_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `qc_details` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `qc_headers`
--

DROP TABLE IF EXISTS `qc_headers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `qc_headers` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `qc_number` varchar(100) DEFAULT NULL,
  `production_id` bigint(20) DEFAULT NULL,
  `po_id` bigint(20) DEFAULT NULL,
  `qc_date` date DEFAULT NULL,
  `operator_name` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `po_id` (`po_id`),
  KEY `production_id` (`production_id`),
  CONSTRAINT `qc_headers_ibfk_1` FOREIGN KEY (`po_id`) REFERENCES `po_headers` (`id`),
  CONSTRAINT `qc_headers_ibfk_2` FOREIGN KEY (`production_id`) REFERENCES `production_orders` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `qc_headers`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `qc_headers` WRITE;
/*!40000 ALTER TABLE `qc_headers` DISABLE KEYS */;
/*!40000 ALTER TABLE `qc_headers` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `quotation_headers`
--

DROP TABLE IF EXISTS `quotation_headers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `quotation_headers` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `quotation_number` varchar(100) DEFAULT NULL,
  `customer_id` bigint(20) DEFAULT NULL,
  `quotation_date` date DEFAULT NULL,
  `currency` varchar(3) DEFAULT 'USD',
  `payment_terms` varchar(255) DEFAULT NULL,
  `valid_until` date DEFAULT NULL,
  `salesperson` varchar(100) DEFAULT NULL,
  `remark` text DEFAULT NULL,
  `status` varchar(32) NOT NULL DEFAULT 'draft',
  `total_amount` decimal(14,2) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `quotation_number` (`quotation_number`),
  KEY `ix_quotation_headers_customer_id` (`customer_id`),
  KEY `ix_quotation_headers_status` (`status`),
  KEY `ix_quotation_headers_quotation_date` (`quotation_date`),
  CONSTRAINT `quotation_headers_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `quotation_headers`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `quotation_headers` WRITE;
/*!40000 ALTER TABLE `quotation_headers` DISABLE KEYS */;
/*!40000 ALTER TABLE `quotation_headers` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `quotation_lines`
--

DROP TABLE IF EXISTS `quotation_lines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `quotation_lines` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `quotation_id` bigint(20) NOT NULL,
  `line_no` int(11) NOT NULL,
  `master_item_id` bigint(20) DEFAULT NULL,
  `item_code` varchar(80) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `color` varchar(200) DEFAULT NULL,
  `specification` varchar(500) DEFAULT NULL,
  `quantity` decimal(12,2) DEFAULT NULL,
  `unit` varchar(20) DEFAULT 'S/F',
  `unit_price` decimal(14,4) DEFAULT NULL,
  `discount_amount` decimal(14,2) DEFAULT 0.00,
  `tax_rate` decimal(5,2) DEFAULT 0.00,
  `line_amount` decimal(14,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `master_item_id` (`master_item_id`),
  KEY `ix_quotation_lines_quotation_id` (`quotation_id`),
  CONSTRAINT `quotation_lines_ibfk_1` FOREIGN KEY (`master_item_id`) REFERENCES `master_items` (`id`) ON DELETE SET NULL,
  CONSTRAINT `quotation_lines_ibfk_2` FOREIGN KEY (`quotation_id`) REFERENCES `quotation_headers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `quotation_lines`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `quotation_lines` WRITE;
/*!40000 ALTER TABLE `quotation_lines` DISABLE KEYS */;
/*!40000 ALTER TABLE `quotation_lines` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `raw_materials`
--

DROP TABLE IF EXISTS `raw_materials`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `raw_materials` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `code` varchar(50) NOT NULL,
  `name` varchar(255) NOT NULL,
  `material_type` varchar(50) NOT NULL,
  `unit` varchar(20) NOT NULL,
  `default_warehouse_id` bigint(20) DEFAULT NULL,
  `min_stock` decimal(12,2) DEFAULT NULL,
  `cost_price` decimal(14,4) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_raw_material_code` (`code`),
  KEY `default_warehouse_id` (`default_warehouse_id`),
  CONSTRAINT `raw_materials_ibfk_1` FOREIGN KEY (`default_warehouse_id`) REFERENCES `warehouses` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `raw_materials`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `raw_materials` WRITE;
/*!40000 ALTER TABLE `raw_materials` DISABLE KEYS */;
/*!40000 ALTER TABLE `raw_materials` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `role_permissions`
--

DROP TABLE IF EXISTS `role_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `role_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `role` varchar(32) NOT NULL,
  `module_key` varchar(80) NOT NULL,
  `action` varchar(32) NOT NULL,
  `allowed` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_role_permissions_key` (`role`,`module_key`,`action`)
) ENGINE=InnoDB AUTO_INCREMENT=63 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role_permissions`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `role_permissions` WRITE;
/*!40000 ALTER TABLE `role_permissions` DISABLE KEYS */;
INSERT INTO `role_permissions` VALUES
(1,'marketing','customers','view',1,'2026-04-29 16:47:10'),
(2,'sales','customers','view',1,'2026-04-29 16:47:10'),
(3,'finance','customers','view',1,'2026-04-29 16:47:10'),
(4,'marketing','customers','create',1,'2026-04-29 16:47:10'),
(5,'sales','customers','create',1,'2026-04-29 16:47:10'),
(6,'marketing','customers','update',1,'2026-04-29 16:47:10'),
(7,'sales','customers','update',1,'2026-04-29 16:47:10'),
(8,'marketing','po','view',1,'2026-04-29 16:47:10'),
(9,'ppic','po','view',1,'2026-04-29 16:47:10'),
(10,'sales','po','view',1,'2026-04-29 16:47:10'),
(11,'production','po','view',1,'2026-04-29 16:47:10'),
(12,'finance','po','view',1,'2026-04-29 16:47:10'),
(13,'marketing','po','create',1,'2026-04-29 16:47:10'),
(14,'ppic','po','create',1,'2026-04-29 16:47:10'),
(15,'sales','po','create',1,'2026-04-29 16:47:10'),
(16,'marketing','po','update',1,'2026-04-29 16:47:10'),
(17,'ppic','po','update',1,'2026-04-29 16:47:10'),
(18,'finance','po','update',1,'2026-04-29 16:47:10'),
(19,'marketing','po','advance',1,'2026-04-29 16:47:10'),
(20,'ppic','po','advance',1,'2026-04-29 16:47:10'),
(21,'marketing','quotations','view',1,'2026-04-29 16:47:10'),
(22,'sales','quotations','view',1,'2026-04-29 16:47:10'),
(23,'finance','quotations','view',1,'2026-04-29 16:47:10'),
(24,'marketing','quotations','create',1,'2026-04-29 16:47:10'),
(25,'sales','quotations','create',1,'2026-04-29 16:47:10'),
(26,'marketing','quotations','update',1,'2026-04-29 16:47:10'),
(27,'sales','quotations','update',1,'2026-04-29 16:47:10'),
(28,'marketing','quotations','delete',1,'2026-04-29 16:47:10'),
(29,'production','production','view',1,'2026-04-29 16:47:10'),
(30,'ppic','production','view',1,'2026-04-29 16:47:10'),
(31,'qc','production','view',1,'2026-04-29 16:47:10'),
(32,'production','production','create',1,'2026-04-29 16:47:10'),
(33,'ppic','production','create',1,'2026-04-29 16:47:10'),
(34,'production','production','update',1,'2026-04-29 16:47:10'),
(35,'qc','qc','view',1,'2026-04-29 16:47:10'),
(36,'warehouse','qc','view',1,'2026-04-29 16:47:10'),
(37,'production','qc','view',1,'2026-04-29 16:47:10'),
(38,'qc','qc','create',1,'2026-04-29 16:47:10'),
(39,'qc','qc','update',1,'2026-04-29 16:47:10'),
(40,'warehouse','packing','view',1,'2026-04-29 16:47:10'),
(41,'warehouse','packing','create',1,'2026-04-29 16:47:10'),
(42,'warehouse','packing','update',1,'2026-04-29 16:47:10'),
(43,'warehouse','packing','print',1,'2026-04-29 16:47:10'),
(44,'warehouse','delivery','view',1,'2026-04-29 16:47:10'),
(45,'marketing','delivery','view',1,'2026-04-29 16:47:10'),
(46,'warehouse','delivery','create',1,'2026-04-29 16:47:10'),
(47,'warehouse','delivery','update',1,'2026-04-29 16:47:10'),
(48,'warehouse','delivery','print',1,'2026-04-29 16:47:10'),
(49,'marketing','delivery','print',1,'2026-04-29 16:47:10'),
(50,'finance','invoice','view',1,'2026-04-29 16:47:10'),
(51,'finance','invoice','create',1,'2026-04-29 16:47:10'),
(52,'finance','invoice','update',1,'2026-04-29 16:47:10'),
(53,'marketing','reports','view',1,'2026-04-29 16:47:10'),
(54,'ppic','reports','view',1,'2026-04-29 16:47:10'),
(55,'finance','reports','view',1,'2026-04-29 16:47:10'),
(56,'exim','reports','view',1,'2026-04-29 16:47:10'),
(57,'sales','reports','view',1,'2026-04-29 16:47:10'),
(58,'marketing','reports','export',1,'2026-04-29 16:47:10'),
(59,'ppic','reports','export',1,'2026-04-29 16:47:10'),
(60,'finance','reports','export',1,'2026-04-29 16:47:10'),
(61,'exim','reports','export',1,'2026-04-29 16:47:10'),
(62,'sales','reports','export',1,'2026-04-29 16:47:10');
/*!40000 ALTER TABLE `role_permissions` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `special_prices`
--

DROP TABLE IF EXISTS `special_prices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `special_prices` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `buyer_code` varchar(32) NOT NULL,
  `material_pattern` varchar(255) DEFAULT NULL,
  `emboss_pattern` varchar(100) DEFAULT NULL,
  `color_pattern` varchar(100) DEFAULT NULL,
  `discount_type` varchar(20) NOT NULL,
  `discount_value` decimal(14,4) NOT NULL,
  `valid_from` date DEFAULT NULL,
  `valid_to` date DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `special_prices`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `special_prices` WRITE;
/*!40000 ALTER TABLE `special_prices` DISABLE KEYS */;
/*!40000 ALTER TABLE `special_prices` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `subcon_invoices`
--

DROP TABLE IF EXISTS `subcon_invoices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `subcon_invoices` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `po_id` bigint(20) NOT NULL,
  `invoice_type` varchar(20) NOT NULL,
  `invoice_number` varchar(100) DEFAULT NULL,
  `amount` decimal(14,2) NOT NULL,
  `description` text DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `po_id` (`po_id`),
  CONSTRAINT `subcon_invoices_ibfk_1` FOREIGN KEY (`po_id`) REFERENCES `po_headers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subcon_invoices`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `subcon_invoices` WRITE;
/*!40000 ALTER TABLE `subcon_invoices` DISABLE KEYS */;
/*!40000 ALTER TABLE `subcon_invoices` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `username` varchar(80) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` varchar(32) NOT NULL DEFAULT 'admin',
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT NULL,
  `department` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES
(1,'Cre@tiv3','$2b$12$HGJ1.oFaJaPBJ00NPw05.uIMN.Zj3Q375q/0unVaZcW3VGyTdkUni','admin',1,'2026-04-22 20:49:43','2026-04-29 16:18:59',NULL),
(2,'demo_sales','$2b$12$U4CDg1FrbAKeWX5ZMNDls.P..Yl4HL9NMxchr5z1gSEg7jqLmGhJS','sales',1,'2026-06-08 22:15:36',NULL,'sales'),
(3,'demo_marketing','$2b$12$U4CDg1FrbAKeWX5ZMNDls.P..Yl4HL9NMxchr5z1gSEg7jqLmGhJS','marketing',1,'2026-06-08 22:15:36',NULL,'marketing'),
(4,'demo_ppic','$2b$12$U4CDg1FrbAKeWX5ZMNDls.P..Yl4HL9NMxchr5z1gSEg7jqLmGhJS','ppic',1,'2026-06-08 22:15:36',NULL,'ppic'),
(5,'demo_production','$2b$12$U4CDg1FrbAKeWX5ZMNDls.P..Yl4HL9NMxchr5z1gSEg7jqLmGhJS','production',1,'2026-06-08 22:15:36',NULL,'production'),
(6,'demo_qc','$2b$12$U4CDg1FrbAKeWX5ZMNDls.P..Yl4HL9NMxchr5z1gSEg7jqLmGhJS','qc',1,'2026-06-08 22:15:36',NULL,'qc'),
(7,'demo_warehouse','$2b$12$U4CDg1FrbAKeWX5ZMNDls.P..Yl4HL9NMxchr5z1gSEg7jqLmGhJS','warehouse',1,'2026-06-08 22:15:36',NULL,'warehouse'),
(8,'demo_finance','$2b$12$U4CDg1FrbAKeWX5ZMNDls.P..Yl4HL9NMxchr5z1gSEg7jqLmGhJS','finance',1,'2026-06-08 22:15:36',NULL,'finance');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `warehouses`
--

DROP TABLE IF EXISTS `warehouses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `warehouses` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `code` varchar(32) NOT NULL,
  `name` varchar(255) NOT NULL,
  `location` text DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `warehouses`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `warehouses` WRITE;
/*!40000 ALTER TABLE `warehouses` DISABLE KEYS */;
/*!40000 ALTER TABLE `warehouses` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Dumping routines for database 'tonghong'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-07-01  6:52:22
