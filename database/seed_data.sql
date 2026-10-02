-- =====================================================================
-- AgriTech – Crop Batch Management & Analytics Portal
-- Sample Data Seeding Script
-- Contains: 6 Users, 5 Farmers, 6 Fields, 6 Crops, 10 Batches, 22 Activities
-- =====================================================================

USE `agritech_db`;

-- ---------------------------------------------------------------------
-- 1. Seed Users (Default Passwords: Admin@123 for admin, Farmer@123 for farmers)
-- ---------------------------------------------------------------------
INSERT INTO `users` (`id`, `name`, `email`, `password`, `role`) VALUES
(1, 'AgriTech Admin', 'admin@agritech.com', 'scrypt:32768:8:1$YhA7w0ICFqusbzXn$19c92d98759c14168bbaef25bb81a9446c3e557f250da69cfb7ce6c71b2b900c93d8056058c525d4b4b95d8b014b20240dc0d777c6bb9cec4dc9fe16e75f83e0', 'admin'),
(2, 'Ramesh Kumar Patel', 'farmer.ramesh@agritech.com', 'scrypt:32768:8:1$CtR0deGXA2vC7dPC$e7dcfab3de91b3c3037d45ceaa2893edaf436ee71a8fc7a94146006533b53f50b2e7f1c3f4e04568f3fbec44978c404aa626972e407b500a2d7a6c3c506c8f41', 'farmer'),
(3, 'Suresh Chandra Sharma', 'farmer.suresh@agritech.com', 'scrypt:32768:8:1$CtR0deGXA2vC7dPC$e7dcfab3de91b3c3037d45ceaa2893edaf436ee71a8fc7a94146006533b53f50b2e7f1c3f4e04568f3fbec44978c404aa626972e407b500a2d7a6c3c506c8f41', 'farmer'),
(4, 'Priya Devi Verma', 'farmer.priya@agritech.com', 'scrypt:32768:8:1$CtR0deGXA2vC7dPC$e7dcfab3de91b3c3037d45ceaa2893edaf436ee71a8fc7a94146006533b53f50b2e7f1c3f4e04568f3fbec44978c404aa626972e407b500a2d7a6c3c506c8f41', 'farmer'),
(5, 'Anita Bai Singh', 'farmer.anita@agritech.com', 'scrypt:32768:8:1$CtR0deGXA2vC7dPC$e7dcfab3de91b3c3037d45ceaa2893edaf436ee71a8fc7a94146006533b53f50b2e7f1c3f4e04568f3fbec44978c404aa626972e407b500a2d7a6c3c506c8f41', 'farmer'),
(6, 'Rajesh Mohan Deshmukh', 'farmer.rajesh@agritech.com', 'scrypt:32768:8:1$CtR0deGXA2vC7dPC$e7dcfab3de91b3c3037d45ceaa2893edaf436ee71a8fc7a94146006533b53f50b2e7f1c3f4e04568f3fbec44978c404aa626972e407b500a2d7a6c3c506c8f41', 'farmer')
ON DUPLICATE KEY UPDATE `name`=VALUES(`name`);

-- ---------------------------------------------------------------------
-- 2. Seed Farmers (5 Farmers)
-- ---------------------------------------------------------------------
INSERT INTO `farmers` (`farmer_id`, `user_id`, `name`, `phone`, `address`, `village`) VALUES
(1, 2, 'Ramesh Kumar Patel', '+91 98261 45012', 'House No. 24, Canal Road', 'Greenfield Agro Colony'),
(2, 3, 'Suresh Chandra Sharma', '+91 94140 28931', 'Plot 5B, Temple Street', 'Kisan Nagar'),
(3, 4, 'Priya Devi Verma', '+91 87654 11980', 'Near Primary School, Ward 3', 'Sundarpur'),
(4, 5, 'Anita Bai Singh', '+91 91234 56789', 'Farm House 12, River Belt', 'Anandpur'),
(5, 6, 'Rajesh Mohan Deshmukh', '+91 99887 65432', 'National Highway Bypass', 'Navgaon')
ON DUPLICATE KEY UPDATE `name`=VALUES(`name`);

-- ---------------------------------------------------------------------
-- 3. Seed Fields (6 Fields)
-- ---------------------------------------------------------------------
INSERT INTO `fields` (`field_id`, `farmer_id`, `field_name`, `location`, `area`, `soil_type`) VALUES
(1, 1, 'North Meadow - Plot A', 'North Ridge Sector 1', 12.50, 'Alluvial'),
(2, 1, 'Canal View - Plot B', 'East Canal Basin', 8.00, 'Loamy'),
(3, 2, 'Valley Sunshine Field', 'Valley Floor West', 15.00, 'Black'),
(4, 3, 'Sundarpur Terraces', 'Hill Slope South', 6.50, 'Red'),
(5, 4, 'Riverbank Fertile Basin', 'Riverbed North Zone', 18.00, 'Clay Loam'),
(6, 5, 'Navgaon Highfield', 'Highway Corridor Block 4', 10.00, 'Sandy Loam')
ON DUPLICATE KEY UPDATE `field_name`=VALUES(`field_name`);

-- ---------------------------------------------------------------------
-- 4. Seed Crops (6 Crops)
-- ---------------------------------------------------------------------
INSERT INTO `crops` (`crop_id`, `crop_name`, `crop_type`, `season`, `expected_yield`) VALUES
(1, 'Golden Sharbati Wheat', 'Cereal', 'Rabi', 22.50),
(2, 'Basmati Paddy (Rice)', 'Cereal', 'Kharif', 28.00),
(3, 'Sweet Yellow Corn (Maize)', 'Cereal', 'Kharif', 32.00),
(4, 'Black Gold Soybean', 'Pulse', 'Kharif', 14.50),
(5, 'Long Staple BT Cotton', 'Cash Crop', 'Kharif', 12.00),
(6, 'Hybrid Roma Tomato', 'Vegetable', 'Year-Round', 45.00)
ON DUPLICATE KEY UPDATE `crop_name`=VALUES(`crop_name`);

-- ---------------------------------------------------------------------
-- 5. Seed Crop Batches (10 Batches with diverse statuses & lifecycle)
-- ---------------------------------------------------------------------
INSERT INTO `crop_batches` (`batch_id`, `field_id`, `crop_id`, `batch_code`, `planting_date`, `expected_harvest_date`, `actual_harvest_date`, `quantity`, `yield`, `status`) VALUES
(1, 1, 1, 'BATCH-2025-WHT01', '2025-11-10', '2026-03-25', '2026-03-24', 500.00, 275.00, 'Harvested'),
(2, 2, 6, 'BATCH-2025-TOM01', '2025-12-05', '2026-02-28', '2026-03-02', 200.00, 350.00, 'Harvested'),
(3, 3, 4, 'BATCH-2026-SOY01', '2026-06-15', '2026-10-10', NULL, 600.00, 0.00, 'Growing'),
(4, 4, 2, 'BATCH-2026-RIC01', '2026-06-20', '2026-10-25', NULL, 300.00, 0.00, 'Growing'),
(5, 5, 5, 'BATCH-2026-COT01', '2026-05-18', '2026-11-15', NULL, 450.00, 0.00, 'Ready for Harvest'),
(6, 6, 3, 'BATCH-2026-MAZ01', '2026-07-01', '2026-10-15', NULL, 400.00, 0.00, 'Growing'),
(7, 1, 2, 'BATCH-2026-RIC02', '2026-07-10', '2026-11-05', NULL, 550.00, 0.00, 'Planted'),
(8, 2, 6, 'BATCH-2026-TOM02', '2026-08-01', '2026-10-30', NULL, 250.00, 0.00, 'Planted'),
(9, 3, 1, 'BATCH-2026-WHT02', '2026-11-01', '2027-03-15', NULL, 650.00, 0.00, 'Planned'),
(10, 5, 3, 'BATCH-2026-MAZ02', '2026-10-20', '2027-02-10', NULL, 500.00, 0.00, 'Planned')
ON DUPLICATE KEY UPDATE `batch_code`=VALUES(`batch_code`);

-- ---------------------------------------------------------------------
-- 6. Seed Cultivation Activities (22 Activities across batches)
-- ---------------------------------------------------------------------
INSERT INTO `cultivation_activities` (`activity_id`, `batch_id`, `activity_type`, `activity_date`, `description`, `quantity_used`, `unit`) VALUES
-- Batch 1 Activities (Wheat - Harvested)
(1, 1, 'Irrigation', '2025-11-15', 'Initial soaking irrigation after sowing seeds', 4500.00, 'Liters'),
(2, 1, 'Fertilization', '2025-12-05', 'Application of NPK 12-32-16 basal fertilizer', 150.00, 'Kg'),
(3, 1, 'Irrigation', '2026-01-10', 'Crown root stage flood irrigation', 6000.00, 'Liters'),
(4, 1, 'Pest/Disease', '2026-01-28', 'Preventive spraying for yellow rust disease using Propiconazole', 2.50, 'Liters'),
(5, 1, 'Harvesting', '2026-03-24', 'Combine harvester operation for prime Sharbati grain', 275.00, 'Quintals'),

-- Batch 2 Activities (Tomato - Harvested)
(6, 2, 'Irrigation', '2025-12-08', 'Drip irrigation for transplanted seedling establishment', 1200.00, 'Liters'),
(7, 2, 'Fertilization', '2025-12-24', 'Water soluble Calcium Nitrate fertigation', 35.00, 'Kg'),
(8, 2, 'Pest/Disease', '2026-01-15', 'Organic neem oil spray against whitefly and aphids', 5.00, 'Liters'),
(9, 2, 'Harvesting', '2026-03-02', 'Manual hand picking of first grade red tomatoes', 350.00, 'Crates'),

-- Batch 3 Activities (Soybean - Growing)
(10, 3, 'Irrigation', '2026-06-25', 'Early vegetative irrigation post germination', 5000.00, 'Liters'),
(11, 3, 'Fertilization', '2026-07-12', 'DAP and Rhizobium culture soil broadcast', 120.00, 'Kg'),
(12, 3, 'Pest/Disease', '2026-08-04', 'Monocrotophos spray against stem fly infestation', 3.00, 'Liters'),

-- Batch 4 Activities (Rice - Growing)
(13, 4, 'Irrigation', '2026-06-28', 'Paddy field ponding water depth maintained to 5cm', 8500.00, 'Liters'),
(14, 4, 'Fertilization', '2026-07-18', 'Urea top dressing at tillering stage', 90.00, 'Kg'),
(15, 4, 'Pest/Disease', '2026-08-10', 'Chlorantraniliprole treatment for stem borer', 1.80, 'Liters'),

-- Batch 5 Activities (Cotton - Ready for Harvest)
(16, 5, 'Irrigation', '2026-05-25', 'Alternate furrow irrigation during square formation', 4000.00, 'Liters'),
(17, 5, 'Fertilization', '2026-06-30', 'Potassium Schoenite and Zinc Sulphate foliar nutrition', 45.00, 'Kg'),
(18, 5, 'Pest/Disease', '2026-07-25', 'Bollworm scouting and pheromone trap deployment', 15.00, 'Traps'),
(19, 5, 'Pest/Disease', '2026-08-20', 'Biocontrol Trichogramma card release', 10.00, 'Cards'),

-- Batch 6 Activities (Corn - Growing)
(20, 6, 'Irrigation', '2026-07-15', 'Sprinkler irrigation at knee-high stage', 3500.00, 'Liters'),
(21, 6, 'Fertilization', '2026-08-02', 'Secondary nitrogen boost with granular ammonium sulphate', 75.00, 'Kg'),

-- Batch 7 Activities (Rice 2 - Planted)
(22, 7, 'Irrigation', '2026-07-14', 'Nursery transplant bed saturation', 3000.00, 'Liters')
ON DUPLICATE KEY UPDATE `description`=VALUES(`description`);
