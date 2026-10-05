-- UAT schemas only. Do not DROP/ALTER tonghong or tonghong_mrp.
CREATE DATABASE IF NOT EXISTS uat_tonghong_erp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS uat_tonghong_mrp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'uat_tonghong_erp'@'localhost' IDENTIFIED BY 'UatTonghongErp2026';
CREATE USER IF NOT EXISTS 'uat_tonghong_erp'@'127.0.0.1' IDENTIFIED BY 'UatTonghongErp2026';
CREATE USER IF NOT EXISTS 'uat_tonghong_erp'@'%' IDENTIFIED BY 'UatTonghongErp2026';
CREATE USER IF NOT EXISTS 'uat_tonghong_mrp'@'localhost' IDENTIFIED BY 'UatTonghongMrp2026';
CREATE USER IF NOT EXISTS 'uat_tonghong_mrp'@'127.0.0.1' IDENTIFIED BY 'UatTonghongMrp2026';
CREATE USER IF NOT EXISTS 'uat_tonghong_mrp'@'%' IDENTIFIED BY 'UatTonghongMrp2026';

ALTER USER 'uat_tonghong_erp'@'localhost' IDENTIFIED BY 'UatTonghongErp2026';
ALTER USER 'uat_tonghong_erp'@'127.0.0.1' IDENTIFIED BY 'UatTonghongErp2026';
ALTER USER 'uat_tonghong_erp'@'%' IDENTIFIED BY 'UatTonghongErp2026';
ALTER USER 'uat_tonghong_mrp'@'localhost' IDENTIFIED BY 'UatTonghongMrp2026';
ALTER USER 'uat_tonghong_mrp'@'127.0.0.1' IDENTIFIED BY 'UatTonghongMrp2026';
ALTER USER 'uat_tonghong_mrp'@'%' IDENTIFIED BY 'UatTonghongMrp2026';

GRANT ALL PRIVILEGES ON `uat_tonghong_erp`.* TO 'uat_tonghong_erp'@'localhost';
GRANT ALL PRIVILEGES ON `uat_tonghong_erp`.* TO 'uat_tonghong_erp'@'127.0.0.1';
GRANT ALL PRIVILEGES ON `uat_tonghong_erp`.* TO 'uat_tonghong_erp'@'%';
GRANT ALL PRIVILEGES ON `uat_tonghong_mrp`.* TO 'uat_tonghong_mrp'@'localhost';
GRANT ALL PRIVILEGES ON `uat_tonghong_mrp`.* TO 'uat_tonghong_mrp'@'127.0.0.1';
GRANT ALL PRIVILEGES ON `uat_tonghong_mrp`.* TO 'uat_tonghong_mrp'@'%';
-- API-only: MRP tidak lagi perlu GRANT SELECT ke DB ERP (akses katalog via HTTP).
FLUSH PRIVILEGES;
