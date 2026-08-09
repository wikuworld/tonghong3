-- MRP Production WIP Schema
-- Database: mrp

CREATE TABLE IF NOT EXISTS tbl_palet_movement (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_palet VARCHAR(50) NOT NULL COMMENT 'KY',
    direction ENUM('IN','OUT') NOT NULL,
    tanggal DATE NOT NULL,
    keterangan VARCHAR(255) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_kode_palet (kode_palet),
    INDEX idx_tanggal (tanggal)
);

CREATE TABLE IF NOT EXISTS tbl_yl (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_yl VARCHAR(50) NOT NULL,
    kode_palet VARCHAR(50) NOT NULL COMMENT 'KY',
    thickness VARCHAR(30) DEFAULT NULL,
    warna VARCHAR(100) DEFAULT NULL,
    qty DECIMAL(12,2) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_palet_yl (kode_palet, kode_yl),
    INDEX idx_kode_palet (kode_palet)
);

CREATE TABLE IF NOT EXISTS tbl_yl_movement (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_yl VARCHAR(50) NOT NULL,
    kode_palet VARCHAR(50) NOT NULL,
    direction ENUM('IN','OUT') NOT NULL,
    thickness VARCHAR(30) DEFAULT NULL,
    warna VARCHAR(100) DEFAULT NULL,
    qty DECIMAL(12,2) DEFAULT 0,
    tanggal DATE NOT NULL,
    keterangan VARCHAR(255) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_kode_yl (kode_yl),
    INDEX idx_kode_palet (kode_palet)
);

CREATE TABLE IF NOT EXISTS tbl_master_po (
    id INT AUTO_INCREMENT PRIMARY KEY,
    no_po VARCHAR(50) NOT NULL,
    no_so VARCHAR(50) DEFAULT NULL,
    customer VARCHAR(150) DEFAULT NULL,
    customer_id INT DEFAULT NULL,
    item_name VARCHAR(200) DEFAULT NULL,
    warna VARCHAR(100) DEFAULT NULL,
    tebal VARCHAR(30) DEFAULT NULL,
    emboss VARCHAR(100) DEFAULT NULL,
    sq_ft DECIMAL(12,2) DEFAULT 0,
    qty_order DECIMAL(12,2) DEFAULT 0,
    qty_processed DECIMAL(12,2) DEFAULT 0,
    status ENUM('outstanding','partial','completed') DEFAULT 'outstanding',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_no_po (no_po),
    INDEX idx_status (status)
);

CREATE TABLE IF NOT EXISTS master_customer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_customer VARCHAR(50) DEFAULT NULL,
    nama_customer VARCHAR(150) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_nama_customer (nama_customer)
);

CREATE TABLE IF NOT EXISTS tbl_rencana_produksi (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_rencana VARCHAR(30) DEFAULT NULL,
    kode_lot_wip VARCHAR(30) DEFAULT NULL,
    nama_rencana VARCHAR(200) NOT NULL,
    tanggal_rencana DATE DEFAULT NULL,
    status ENUM('draft','active','completed') DEFAULT 'draft',
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tbl_rencana_item (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rencana_id INT NOT NULL,
    kode_rencana_item VARCHAR(30) NOT NULL UNIQUE,
    kode_lot_wip VARCHAR(30) DEFAULT NULL,
    customer_id INT NOT NULL,
    kode_kulit VARCHAR(50) DEFAULT NULL,
    thickness VARCHAR(30) DEFAULT NULL,
    color VARCHAR(100) DEFAULT NULL,
    emboss VARCHAR(100) DEFAULT NULL,
    color_swatch VARCHAR(100) DEFAULT NULL,
    keterangan VARCHAR(255) DEFAULT NULL,
    urutan INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_rencana_item (rencana_id)
);

CREATE TABLE IF NOT EXISTS tbl_rencana_item_po (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    po_id INT NOT NULL,
    qty_outstanding DECIMAL(12,2) DEFAULT 0,
    qty_proses DECIMAL(12,2) DEFAULT 0,
    INDEX idx_item_po (item_id)
);

CREATE TABLE IF NOT EXISTS tbl_rencana_produksi_detail (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rencana_id INT NOT NULL,
    po_id INT DEFAULT NULL,
    no_po VARCHAR(50) NOT NULL,
    no_so VARCHAR(50) DEFAULT NULL,
    item_name VARCHAR(200) DEFAULT NULL,
    sq_ft DECIMAL(12,2) DEFAULT 0,
    qty_order DECIMAL(12,2) DEFAULT 0,
    qty_proses DECIMAL(12,2) DEFAULT 0,
    qty_sisa DECIMAL(12,2) DEFAULT 0,
    FOREIGN KEY (rencana_id) REFERENCES tbl_rencana_produksi(id) ON DELETE CASCADE,
    INDEX idx_rencana (rencana_id)
);

CREATE TABLE IF NOT EXISTS tbl_master_treatment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    jenis ENUM('PU','Suede') NOT NULL DEFAULT 'PU',
    nama_treatment VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_nama_treatment (nama_treatment)
);

CREATE TABLE IF NOT EXISTS tbl_persiapan_kulit (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_wip VARCHAR(30) NOT NULL,
    kode_rencana VARCHAR(30) NOT NULL,
    kode_proses VARCHAR(30) NOT NULL UNIQUE,
    no_po VARCHAR(50) DEFAULT NULL,
    warna VARCHAR(100) DEFAULT NULL,
    tebal VARCHAR(30) DEFAULT NULL,
    emboss VARCHAR(100) DEFAULT NULL,
    lebar VARCHAR(30) DEFAULT NULL,
    treatment_jenis ENUM('PU','Suede') DEFAULT NULL,
    treatment_list TEXT DEFAULT NULL,
    total_size DECIMAL(12,2) DEFAULT 0,
    status ENUM('draft','started','saved','completed') DEFAULT 'draft',
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_saved DATETIME DEFAULT NULL,
    INDEX idx_kode_wip (kode_wip),
    INDEX idx_kode_rencana (kode_rencana)
);

CREATE TABLE IF NOT EXISTS tbl_persiapan_scan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    persiapan_id INT NOT NULL,
    kode_palet VARCHAR(50) NOT NULL,
    kode_yl VARCHAR(50) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persiapan_id) REFERENCES tbl_persiapan_kulit(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tbl_persiapan_ukur (
    id INT AUTO_INCREMENT PRIMARY KEY,
    persiapan_id INT NOT NULL,
    size_val DECIMAL(12,2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persiapan_id) REFERENCES tbl_persiapan_kulit(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tbl_persiapan_reprint (
    id INT AUTO_INCREMENT PRIMARY KEY,
    persiapan_id INT NOT NULL,
    reprint_ke INT NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persiapan_id) REFERENCES tbl_persiapan_kulit(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS master_chemical (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_chemical VARCHAR(150) NOT NULL,
    satuan VARCHAR(20) DEFAULT 'kg',
    expired_days INT DEFAULT 365
);

CREATE TABLE IF NOT EXISTS master_resep (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_resep VARCHAR(150) NOT NULL,
    chemical_id INT DEFAULT NULL,
    FOREIGN KEY (chemical_id) REFERENCES master_chemical(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS tbl_lab_lot (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_lot_warna VARCHAR(30) NOT NULL UNIQUE,
    nama_lot_warna VARCHAR(150) NOT NULL,
    status ENUM('active','used','expired') DEFAULT 'active',
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_kode_lot_warna (kode_lot_warna)
);

CREATE TABLE IF NOT EXISTS tbl_lab_lot_detail (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_lot_warna VARCHAR(30) NOT NULL,
    kode_kimia VARCHAR(50) NOT NULL,
    nama_kimia VARCHAR(150) DEFAULT NULL,
    resep VARCHAR(150) DEFAULT NULL,
    satuan VARCHAR(20) DEFAULT 'kg',
    qty DECIMAL(12,2) DEFAULT 0,
    remarks TEXT DEFAULT NULL,
    FOREIGN KEY (kode_lot_warna) REFERENCES tbl_lab_lot(kode_lot_warna) ON DELETE CASCADE,
    INDEX idx_lot_detail (kode_lot_warna)
);

CREATE TABLE IF NOT EXISTS tbl_lab_mixing (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_lot_warna VARCHAR(30) NOT NULL UNIQUE,
    nama_chemical VARCHAR(150) NOT NULL,
    resep VARCHAR(150) DEFAULT NULL,
    satuan VARCHAR(20) DEFAULT 'kg',
    qty DECIMAL(12,2) DEFAULT 0,
    remarks TEXT DEFAULT NULL,
    status ENUM('active','used','expired') DEFAULT 'active',
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tbl_usage_color (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_wip VARCHAR(30) NOT NULL,
    kode_lot_warna VARCHAR(30) NOT NULL,
    nama_warna VARCHAR(100) DEFAULT NULL,
    qty_pembuatan DECIMAL(12,2) DEFAULT 0,
    qty_digunakan DECIMAL(12,2) DEFAULT 0,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_kode_wip (kode_wip)
);

CREATE TABLE IF NOT EXISTS master_rp (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_rp VARCHAR(50) NOT NULL UNIQUE,
    nama_rp VARCHAR(150) NOT NULL,
    deskripsi TEXT DEFAULT NULL,
    satuan VARCHAR(20) DEFAULT 'meter',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_kode_rp (kode_rp)
);

CREATE TABLE IF NOT EXISTS tbl_usage_rp (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_wip VARCHAR(30) NOT NULL,
    jenis_rp VARCHAR(150) NOT NULL,
    qty_used DECIMAL(12,2) DEFAULT 0,
    satuan VARCHAR(20) DEFAULT 'meter',
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_kode_wip (kode_wip)
);

CREATE TABLE IF NOT EXISTS master_kimia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_kimia VARCHAR(50) NOT NULL UNIQUE,
    nama_kimia VARCHAR(150) NOT NULL,
    deskripsi TEXT DEFAULT NULL,
    satuan VARCHAR(20) DEFAULT 'kg',
    expired_days INT DEFAULT 365,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_kode_kimia (kode_kimia)
);

CREATE TABLE IF NOT EXISTS tbl_stok_kimia_in (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_internal VARCHAR(50) NOT NULL UNIQUE COMMENT 'Kode BC',
    kimia_id INT NOT NULL,
    qty DECIMAL(12,2) NOT NULL,
    qty_sisa DECIMAL(12,2) NOT NULL,
    satuan VARCHAR(20) DEFAULT 'kg',
    expired_date DATE DEFAULT NULL,
    tanggal_in DATE NOT NULL,
    gudang ENUM('kimia','mixing') DEFAULT 'kimia',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (kimia_id) REFERENCES master_kimia(id),
    INDEX idx_gudang (gudang)
);

CREATE TABLE IF NOT EXISTS tbl_stok_kimia_out (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stok_in_id INT DEFAULT NULL,
    kimia_id INT NOT NULL,
    qty DECIMAL(12,2) NOT NULL,
    tujuan ENUM('mixing','produksi','return') NOT NULL,
    kode_wip VARCHAR(30) DEFAULT NULL,
    tanggal DATE NOT NULL,
    keterangan VARCHAR(255) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stok_in_id) REFERENCES tbl_stok_kimia_in(id) ON DELETE SET NULL,
    FOREIGN KEY (kimia_id) REFERENCES master_kimia(id)
);

CREATE TABLE IF NOT EXISTS tbl_stok_rp_in (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_internal VARCHAR(50) NOT NULL UNIQUE COMMENT 'Kode BC',
    rp_id INT NOT NULL,
    meter_roll DECIMAL(12,2) NOT NULL,
    qty_sisa DECIMAL(12,2) NOT NULL,
    tanggal_in DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rp_id) REFERENCES master_rp(id)
);

CREATE TABLE IF NOT EXISTS tbl_stok_rp_out (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stok_in_id INT DEFAULT NULL,
    rp_id INT NOT NULL,
    meter_roll DECIMAL(12,2) NOT NULL,
    kode_wip VARCHAR(30) DEFAULT NULL,
    tanggal DATE NOT NULL,
    keterangan VARCHAR(255) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stok_in_id) REFERENCES tbl_stok_rp_in(id) ON DELETE SET NULL,
    FOREIGN KEY (rp_id) REFERENCES master_rp(id)
);

CREATE TABLE IF NOT EXISTS tbl_packing (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_packing VARCHAR(30) NOT NULL UNIQUE,
    kode_wip VARCHAR(30) NOT NULL,
    no_po VARCHAR(50) NOT NULL,
    customer VARCHAR(150) DEFAULT NULL,
    total_lembar INT DEFAULT 0,
    total_ukuran DECIMAL(12,2) DEFAULT 0,
    status ENUM('in_progress','finished') DEFAULT 'in_progress',
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_finished DATETIME DEFAULT NULL,
    INDEX idx_kode_wip (kode_wip)
);

CREATE TABLE IF NOT EXISTS tbl_packing_roll (
    id INT AUTO_INCREMENT PRIMARY KEY,
    packing_id INT NOT NULL,
    roll_no INT NOT NULL,
    lembar INT DEFAULT 1,
    ukuran DECIMAL(12,2) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (packing_id) REFERENCES tbl_packing(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS master_kulit (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_kulit VARCHAR(50) NOT NULL UNIQUE,
    nama_kulit VARCHAR(150) DEFAULT NULL,
    thickness VARCHAR(30) DEFAULT NULL,
    warna VARCHAR(100) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_kode_kulit (kode_kulit)
);

CREATE TABLE IF NOT EXISTS tbl_seq (
    name VARCHAR(30) PRIMARY KEY,
    last_val INT NOT NULL DEFAULT 0,
    prefix VARCHAR(10) DEFAULT '',
    date_key VARCHAR(8) DEFAULT ''
);

CREATE TABLE IF NOT EXISTS master_erp (
    id INT AUTO_INCREMENT PRIMARY KEY,
    thickness VARCHAR(30) NOT NULL,
    color VARCHAR(100) NOT NULL,
    emboss VARCHAR(100) NOT NULL,
    color_swatch VARCHAR(100) DEFAULT NULL,
    backer VARCHAR(100) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_erp_combo (thickness, color, emboss)
);

CREATE TABLE IF NOT EXISTS master_material_lain (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_material VARCHAR(50) NOT NULL UNIQUE,
    nama_material VARCHAR(150) NOT NULL,
    deskripsi TEXT DEFAULT NULL,
    satuan VARCHAR(20) DEFAULT 'pcs',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tbl_stok_material_lain_in (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_internal VARCHAR(50) NOT NULL UNIQUE,
    material_id INT NOT NULL,
    qty DECIMAL(12,2) NOT NULL,
    qty_sisa DECIMAL(12,2) NOT NULL,
    satuan VARCHAR(20) DEFAULT 'pcs',
    tanggal_in DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (material_id) REFERENCES master_material_lain(id)
);

CREATE TABLE IF NOT EXISTS tbl_stok_material_lain_out (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stok_in_id INT DEFAULT NULL,
    material_id INT NOT NULL,
    qty DECIMAL(12,2) NOT NULL,
    kode_wip VARCHAR(30) DEFAULT NULL,
    tanggal DATE NOT NULL,
    keterangan VARCHAR(255) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stok_in_id) REFERENCES tbl_stok_material_lain_in(id) ON DELETE SET NULL,
    FOREIGN KEY (material_id) REFERENCES master_material_lain(id)
);

CREATE TABLE IF NOT EXISTS tbl_usage_material_lain (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_wip VARCHAR(30) NOT NULL,
    kode_material VARCHAR(50) NOT NULL,
    nama_material VARCHAR(150) DEFAULT NULL,
    qty_used DECIMAL(12,2) DEFAULT 0,
    satuan VARCHAR(20) DEFAULT 'pcs',
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_kode_wip (kode_wip)
);

CREATE TABLE IF NOT EXISTS tbl_packing_po (
    id INT AUTO_INCREMENT PRIMARY KEY,
    packing_id INT NOT NULL,
    po_id INT DEFAULT NULL,
    no_po VARCHAR(50) NOT NULL,
    no_so VARCHAR(50) DEFAULT NULL,
    qty_sq DECIMAL(12,2) DEFAULT 0,
    FOREIGN KEY (packing_id) REFERENCES tbl_packing(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tbl_gudang_fg (
    id INT AUTO_INCREMENT PRIMARY KEY,
    packing_id INT NOT NULL UNIQUE,
    kode_packing VARCHAR(30) NOT NULL UNIQUE,
    kode_wip VARCHAR(30) NOT NULL,
    customer VARCHAR(150) DEFAULT NULL,
    total_lembar INT DEFAULT 0,
    total_ukuran DECIMAL(12,2) DEFAULT 0,
    status ENUM('in_stock','out') DEFAULT 'in_stock',
    date_in DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_out DATETIME DEFAULT NULL,
    keterangan_out VARCHAR(255) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS tbl_persiapan_ky (
    id INT AUTO_INCREMENT PRIMARY KEY,
    persiapan_id INT NOT NULL,
    kode_palet VARCHAR(50) NOT NULL,
    kode_yl VARCHAR(50) DEFAULT NULL,
    target_qty DECIMAL(12,2) DEFAULT 0,
    actual_qty DECIMAL(12,2) DEFAULT 0,
    status ENUM('active','selesai') DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persiapan_id) REFERENCES tbl_persiapan_kulit(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tbl_kulit_lebih (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rencana_item_id INT NOT NULL,
    persiapan_id INT DEFAULT NULL,
    ky_id INT DEFAULT NULL,
    kode_palet VARCHAR(50) DEFAULT NULL,
    kode_yl VARCHAR(50) DEFAULT NULL,
    target_qty DECIMAL(12,2) DEFAULT 0,
    actual_qty DECIMAL(12,2) DEFAULT 0,
    selisih DECIMAL(12,2) DEFAULT 0,
    keterangan VARCHAR(255) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_rencana_item (rencana_item_id)
);

-- Seed data
INSERT IGNORE INTO tbl_master_treatment (jenis, nama_treatment) VALUES
('PU', 'Treatment A'), ('PU', 'Treatment B'), ('PU', 'Treatment C'), ('PU', 'Treatment D');

INSERT IGNORE INTO master_chemical (nama_chemical, satuan) VALUES
('Pigment Red', 'kg'), ('Pigment Blue', 'kg'), ('Pigment Black', 'kg'), ('Solvent Base', 'kg');

INSERT IGNORE INTO master_resep (nama_resep) VALUES
('Resep Standard A'), ('Resep Standard B'), ('Resep Custom');

INSERT IGNORE INTO master_rp (kode_rp, nama_rp, deskripsi, satuan) VALUES
('RP-001', 'RP Gloss', 'Release paper gloss finish', 'meter'),
('RP-002', 'RP Matte', 'Release paper matte finish', 'meter'),
('RP-003', 'RP Texture', 'Release paper texture finish', 'meter');

INSERT IGNORE INTO master_kimia (kode_kimia, nama_kimia, deskripsi, satuan) VALUES
('KIM-001', 'Chemical Base A', 'Chemical base type A', 'kg'),
('KIM-002', 'Chemical Base B', 'Chemical base type B', 'kg'),
('KIM-003', 'Hardener', 'Hardener chemical', 'kg');

INSERT IGNORE INTO tbl_master_po (no_po, no_so, customer, item_name, warna, tebal, emboss, sq_ft, qty_order, qty_processed, status) VALUES
('PO-2026-001', 'SO-2026-001', 'Customer A', 'Leather Sheet A', 'Brown', '1.2mm', 'Plain', 500, 100, 0, 'outstanding'),
('PO-2026-001', 'SO-2026-001', 'Customer A', 'Leather Sheet A-2', 'Brown', '1.2mm', 'Plain', 200, 50, 0, 'outstanding'),
('PO-2026-001', 'SO-2026-001', 'Customer A', 'Leather Sheet A-3', 'Tan', '1.0mm', 'Emboss X', 150, 30, 0, 'outstanding'),
('PO-2026-002', 'SO-2026-001', 'Customer A', 'Leather Sheet B', 'Black', '1.0mm', 'Emboss A', 300, 80, 0, 'outstanding'),
('PO-2026-002', 'SO-2026-001', 'Customer A', 'Leather Sheet B-2', 'Black', '1.0mm', 'Emboss A', 180, 40, 0, 'outstanding'),
('PO-2026-003', 'SO-2026-002', 'Customer B', 'Leather Sheet C', 'Red', '1.4mm', 'Emboss B', 450, 120, 0, 'outstanding'),
('PO-2026-003', 'SO-2026-002', 'Customer B', 'Leather Sheet C-2', 'Maroon', '1.4mm', 'Emboss B', 220, 60, 0, 'outstanding');

INSERT IGNORE INTO master_erp (thickness, color, emboss, color_swatch, backer) VALUES
('1.0mm', 'Brown', 'Plain', 'SW-BRN-01', 'BK-PU-A'),
('1.0mm', 'Black', 'Emboss A', 'SW-BLK-02', 'BK-PU-B'),
('1.2mm', 'Brown', 'Plain', 'SW-BRN-03', 'BK-PU-A'),
('1.2mm', 'Tan', 'Emboss X', 'SW-TAN-04', 'BK-SUEDE-C'),
('1.4mm', 'Red', 'Emboss B', 'SW-RED-05', 'BK-PU-D'),
('1.4mm', 'Maroon', 'Emboss B', 'SW-MAR-06', 'BK-PU-D');

INSERT IGNORE INTO master_material_lain (kode_material, nama_material, deskripsi, satuan) VALUES
('MAT-001', 'Thread Nylon', 'Benang jahit nylon', 'roll'),
('MAT-002', 'Label Tag', 'Label produk', 'pcs'),
('MAT-003', 'Plastic Wrap', 'Plastik pembungkus', 'roll');
