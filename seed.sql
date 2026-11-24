-- ARVA: Seed Data for Hackathon Evaluation & Local Testing
-- Realistic FAO-56 Agricultural Baseline Data

-- 1. Demo User
INSERT INTO users (id, email, password_hash, full_name)
VALUES ('usr-demo-001', 'farmer@arva.ag', '$2b$12$e8Yk26D82eB8zP94v2d6qODq79c2vK3wXmF7P8B9.s1xX.2s7942', 'Maria Silva (Head Horticulturist)');

-- 2. Demo Farm
INSERT INTO farms (id, user_id, name, location_name, latitude, longitude, total_area_sqm, tank_capacity_litres, current_tank_litres, emergency_reserve_percent, default_irrigation_efficiency)
VALUES ('frm-demo-001', 'usr-demo-001', 'Green Valley Community Farm', 'Bangalore Rural Agro-Climatic Zone', 12.9716, 77.5946, 3200.00, 25000.00, 16800.00, 15.00, 0.85);

-- 3. Soil Types (FAO-56 Table 19 Standards)
INSERT INTO soil_types (id, name, description, field_capacity_pct, wilting_point_pct, available_water_capacity_mm_per_m, infiltration_rate_mm_hr, source_citation)
VALUES 
('soil-01', 'Sandy Loam', 'Coarse texture with rapid drainage and moderate moisture retention. Common in river valleys.', 18.00, 8.00, 100.00, 25.00, 'FAO-56 Chapter 3, Table 19'),
('soil-02', 'Loam', 'Ideal agricultural balance of sand, silt, and clay. High water retention with good aeration.', 27.00, 12.00, 150.00, 13.00, 'FAO-56 Chapter 3, Table 19'),
('soil-03', 'Clay Loam', 'Heavy soil with fine texture. High water capacity but slower infiltration rate.', 32.00, 18.00, 140.00, 8.00, 'FAO-56 Chapter 3, Table 19'),
('soil-04', 'Silt Loam', 'Smooth feel with very high available water capacity. Excellent for shallow-rooted horticulture.', 31.00, 11.00, 200.00, 10.00, 'FAO-56 Chapter 3, Table 19');

-- 4. Crops Library (FAO-56 Table 12 & Table 22 Standards)
INSERT INTO crops (id, name, category, default_root_depth_m, allowable_depletion_p, kc_initial, kc_mid, kc_end, stage_days_initial, stage_days_dev, stage_days_mid, stage_days_late, economic_priority_weight, source_citation)
VALUES
('crop-01', 'Tomato', 'Vegetables', 0.70, 0.40, 0.60, 1.15, 0.80, 30, 40, 45, 30, 1.30, 'FAO-56 Table 12 (Fresh Tomatoes)'),
('crop-02', 'Sweet Corn / Maize', 'Grain & Cereal', 1.00, 0.55, 0.30, 1.20, 0.60, 20, 35, 40, 30, 1.00, 'FAO-56 Table 12 (Sweet Corn)'),
('crop-03', 'Bell Pepper', 'Vegetables', 0.60, 0.30, 0.60, 1.05, 0.90, 25, 35, 40, 20, 1.40, 'FAO-56 Table 12 (Sweet Peppers)'),
('crop-04', 'Potato', 'Tubers', 0.50, 0.35, 0.50, 1.15, 0.75, 25, 30, 45, 30, 1.15, 'FAO-56 Table 12 (Potatoes)'),
('crop-05', 'Spinach / Leafy Greens', 'Horticulture', 0.30, 0.20, 0.70, 1.00, 0.95, 15, 20, 25, 10, 0.90, 'FAO-56 Table 12 (Spinach)');

-- 5. Farm Zones (4 distinct zones)
INSERT INTO farm_zones (id, farm_id, name, area_sqm, crop_id, growth_stage, soil_type_id, root_depth_m, current_moisture_pct, moisture_data_source, priority_override)
VALUES
('zone-01', 'frm-demo-001', 'North Field: Roma Tomatoes', 800.00, 'crop-01', 'mid', 'soil-02', 0.70, 17.50, 'model_projection', 1),
('zone-02', 'frm-demo-001', 'East Terrace: Sweet Corn', 1200.00, 'crop-02', 'development', 'soil-01', 0.85, 11.20, 'manual_estimate', 0),
('zone-03', 'frm-demo-001', 'Greenhouse A: Bell Peppers', 500.00, 'crop-03', 'mid', 'soil-02', 0.60, 19.80, 'feel_appearance', 2),
('zone-04', 'frm-demo-001', 'South Basin: Yukon Gold Potatoes', 700.00, 'crop-04', 'late', 'soil-04', 0.50, 22.00, 'model_projection', 0);

-- 6. Recent Historical Weather (Past 5 Days)
INSERT INTO weather_records (id, farm_id, recorded_date, temp_max_c, temp_min_c, precipitation_mm, et0_mm, relative_humidity_pct, source)
VALUES
('w-hist-01', 'frm-demo-001', DATE_SUB(CURRENT_DATE, INTERVAL 4 DAY), 31.2, 19.5, 0.0, 4.8, 55.0, 'Open-Meteo Historical Archive'),
('w-hist-02', 'frm-demo-001', DATE_SUB(CURRENT_DATE, INTERVAL 3 DAY), 32.0, 20.1, 0.0, 5.1, 52.0, 'Open-Meteo Historical Archive'),
('w-hist-03', 'frm-demo-001', DATE_SUB(CURRENT_DATE, INTERVAL 2 DAY), 29.5, 21.0, 4.2, 3.9, 68.0, 'Open-Meteo Historical Archive'),
('w-hist-04', 'frm-demo-001', DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), 28.0, 20.4, 12.5, 3.2, 78.0, 'Open-Meteo Historical Archive'),
('w-hist-05', 'frm-demo-001', CURRENT_DATE, 30.0, 19.8, 0.0, 4.5, 60.0, 'Open-Meteo Weather API');

-- 7. 7-Day Forecast
INSERT INTO weather_forecasts (id, farm_id, forecast_date, temp_max_c, temp_min_c, precipitation_mm, precipitation_probability_pct, et0_mm, source)
VALUES
('w-fore-01', 'frm-demo-001', DATE_ADD(CURRENT_DATE, INTERVAL 1 DAY), 31.0, 20.0, 0.0, 10, 4.7, 'Open-Meteo Forecast 7D'),
('w-fore-02', 'frm-demo-001', DATE_ADD(CURRENT_DATE, INTERVAL 2 DAY), 31.5, 20.2, 0.0, 15, 4.9, 'Open-Meteo Forecast 7D'),
('w-fore-03', 'frm-demo-001', DATE_ADD(CURRENT_DATE, INTERVAL 3 DAY), 29.8, 21.0, 6.5, 65, 3.8, 'Open-Meteo Forecast 7D'),
('w-fore-04', 'frm-demo-001', DATE_ADD(CURRENT_DATE, INTERVAL 4 DAY), 28.2, 20.5, 14.0, 80, 3.1, 'Open-Meteo Forecast 7D'),
('w-fore-05', 'frm-demo-001', DATE_ADD(CURRENT_DATE, INTERVAL 5 DAY), 30.0, 19.5, 2.0, 30, 4.2, 'Open-Meteo Forecast 7D'),
('w-fore-06', 'frm-demo-001', DATE_ADD(CURRENT_DATE, INTERVAL 6 DAY), 31.8, 20.0, 0.0, 10, 4.8, 'Open-Meteo Forecast 7D'),
('w-fore-07', 'frm-demo-001', DATE_ADD(CURRENT_DATE, INTERVAL 7 DAY), 32.2, 20.5, 0.0, 5, 5.0, 'Open-Meteo Forecast 7D');

-- 8. Realistic Irrigation Logs (Past Events)
INSERT INTO irrigation_logs (id, zone_id, farm_id, logged_date, recommended_litres, actual_litres, status, notes, logged_offline, sync_status)
VALUES
('log-01', 'zone-01', 'frm-demo-001', DATE_SUB(CURRENT_DATE, INTERVAL 4 DAY), 4200.00, 4200.00, 'completed', 'Standard drip cycle completed. Roots moist.', FALSE, 'synced'),
('log-02', 'zone-02', 'frm-demo-001', DATE_SUB(CURRENT_DATE, INTERVAL 4 DAY), 5800.00, 5500.00, 'modified', 'Slight reduction due to morning cloudiness.', FALSE, 'synced'),
('log-03', 'zone-03', 'frm-demo-001', DATE_SUB(CURRENT_DATE, INTERVAL 3 DAY), 2200.00, 2200.00, 'completed', 'Bell peppers early morning micro-sprinkler cycle.', FALSE, 'synced'),
('log-04', 'zone-01', 'frm-demo-001', DATE_SUB(CURRENT_DATE, INTERVAL 2 DAY), 3800.00, 0.00, 'skipped', 'Rain observed on horizon, delayed application.', FALSE, 'synced'),
('log-05', 'zone-04', 'frm-demo-001', DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), 2900.00, 2900.00, 'completed', 'Potatoes maturing stage moisture replenishment.', TRUE, 'synced');
