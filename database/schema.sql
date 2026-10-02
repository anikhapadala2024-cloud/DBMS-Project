-- =====================================================================
-- AgriTech – Crop Batch Management & Analytics Portal
-- Database Schema Script: agritech_db
-- Compatible with MySQL 5.7+, MySQL 8.0+, and MariaDB 10.3+
-- =====================================================================

CREATE DATABASE IF NOT EXISTS `agritech_db` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE `agritech_db`;

-- ---------------------------------------------------------------------
-- 1. Table: users
-- Roles: 'admin', 'farmer'
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(150) NOT NULL UNIQUE,
    `password` VARCHAR(255) NOT NULL,
    `role` ENUM('admin', 'farmer') NOT NULL DEFAULT 'farmer',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 2. Table: farmers
-- Foreign Key: user_id -> users(id)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `farmers` (
    `farmer_id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NULL,
    `name` VARCHAR(100) NOT NULL,
    `phone` VARCHAR(20) NOT NULL,
    `address` TEXT NOT NULL,
    `village` VARCHAR(100) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_farmers_users` 
        FOREIGN KEY (`user_id`) 
        REFERENCES `users` (`id`) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 3. Table: fields
-- Foreign Key: farmer_id -> farmers(farmer_id)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `fields` (
    `field_id` INT AUTO_INCREMENT PRIMARY KEY,
    `farmer_id` INT NOT NULL,
    `field_name` VARCHAR(100) NOT NULL,
    `location` VARCHAR(150) NOT NULL,
    `area` DECIMAL(8, 2) NOT NULL COMMENT 'Area in acres',
    `soil_type` VARCHAR(50) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_fields_farmers` 
        FOREIGN KEY (`farmer_id`) 
        REFERENCES `farmers` (`farmer_id`) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 4. Table: crops
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `crops` (
    `crop_id` INT AUTO_INCREMENT PRIMARY KEY,
    `crop_name` VARCHAR(100) NOT NULL UNIQUE,
    `crop_type` VARCHAR(50) NOT NULL COMMENT 'Cereal, Pulse, Cash Crop, Vegetable, Fruit, etc.',
    `season` VARCHAR(50) NOT NULL COMMENT 'Kharif, Rabi, Zaid, Year-Round',
    `expected_yield` DECIMAL(10, 2) NOT NULL COMMENT 'Expected yield in quintals or kg per acre',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 5. Table: crop_batches
-- Foreign Keys: field_id -> fields(field_id), crop_id -> crops(crop_id)
-- Statuses: Planned, Planted, Growing, Ready for Harvest, Harvested
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `crop_batches` (
    `batch_id` INT AUTO_INCREMENT PRIMARY KEY,
    `field_id` INT NOT NULL,
    `crop_id` INT NOT NULL,
    `batch_code` VARCHAR(50) NOT NULL UNIQUE,
    `planting_date` DATE NOT NULL,
    `expected_harvest_date` DATE NOT NULL,
    `actual_harvest_date` DATE NULL,
    `quantity` DECIMAL(10, 2) NOT NULL COMMENT 'Planted seed/sapling quantity (kg or count)',
    `yield` DECIMAL(10, 2) NULL DEFAULT 0.00 COMMENT 'Actual harvested yield',
    `status` ENUM('Planned', 'Planted', 'Growing', 'Ready for Harvest', 'Harvested') NOT NULL DEFAULT 'Planned',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_batches_fields` 
        FOREIGN KEY (`field_id`) 
        REFERENCES `fields` (`field_id`) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    CONSTRAINT `fk_batches_crops` 
        FOREIGN KEY (`crop_id`) 
        REFERENCES `crops` (`crop_id`) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 6. Table: cultivation_activities
-- Foreign Key: batch_id -> crop_batches(batch_id)
-- Activity Types: Irrigation, Fertilization, Pest/Disease, Harvesting
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `cultivation_activities` (
    `activity_id` INT AUTO_INCREMENT PRIMARY KEY,
    `batch_id` INT NOT NULL,
    `activity_type` ENUM('Irrigation', 'Fertilization', 'Pest/Disease', 'Harvesting') NOT NULL,
    `activity_date` DATE NOT NULL,
    `description` TEXT NOT NULL,
    `quantity_used` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    `unit` VARCHAR(30) NOT NULL COMMENT 'Liters, Kg, Hours, Bags, etc.',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_activities_batches` 
        FOREIGN KEY (`batch_id`) 
        REFERENCES `crop_batches` (`batch_id`) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- Indexes for High Performance Querying & Analytics
-- ---------------------------------------------------------------------
CREATE INDEX `idx_batches_status` ON `crop_batches` (`status`);
CREATE INDEX `idx_batches_dates` ON `crop_batches` (`planting_date`, `expected_harvest_date`);
CREATE INDEX `idx_activities_type_date` ON `cultivation_activities` (`activity_type`, `activity_date`);
