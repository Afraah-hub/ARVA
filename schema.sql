-- ARVA: Predict. Prioritize. Preserve.
-- Production MySQL 8.0+ Database Schema
-- Standard FAO-56 Soil Water Balance & Irrigation Scheduling System

DROP TABLE IF EXISTS sync_events;
DROP TABLE IF EXISTS irrigation_logs;
DROP TABLE IF EXISTS irrigation_recommendations;
DROP TABLE IF EXISTS weather_forecasts;
DROP TABLE IF EXISTS weather_records;
DROP TABLE IF EXISTS farm_zones;
DROP TABLE IF EXISTS crops;
DROP TABLE IF EXISTS soil_types;
DROP TABLE IF EXISTS farms;
DROP TABLE IF EXISTS users;

-- 1. Users Table
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Farms Table
CREATE TABLE farms (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(150) NOT NULL,
    location_name VARCHAR(255) DEFAULT 'Green Valley Community Farm',
    latitude DECIMAL(9, 6) NOT NULL DEFAULT 12.9716,
    longitude DECIMAL(9, 6) NOT NULL DEFAULT 77.5946,
    total_area_sqm DECIMAL(12, 2) NOT NULL DEFAULT 4000.00,
    tank_capacity_litres DECIMAL(12, 2) NOT NULL DEFAULT 20000.00,
    current_tank_litres DECIMAL(12, 2) NOT NULL DEFAULT 14500.00,
    emergency_reserve_percent DECIMAL(5, 2) NOT NULL DEFAULT 15.00,
    default_irrigation_efficiency DECIMAL(4, 2) NOT NULL DEFAULT 0.85,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_farms_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Soil Types (FAO-56 reference parameters)
CREATE TABLE soil_types (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(80) NOT NULL UNIQUE,
    description TEXT,
    field_capacity_pct DECIMAL(5, 2) NOT NULL, -- Volumetric % (theta_FC)
    wilting_point_pct DECIMAL(5, 2) NOT NULL,  -- Volumetric % (theta_WP)
    available_water_capacity_mm_per_m DECIMAL(6, 2) NOT NULL, -- mm water / m depth
    infiltration_rate_mm_hr DECIMAL(6, 2) NOT NULL,
    source_citation VARCHAR(255) DEFAULT 'FAO Irrigation and Drainage Paper 56'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Crops Library (FAO-56 standard coefficients)
CREATE TABLE crops (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) DEFAULT 'Vegetables',
    default_root_depth_m DECIMAL(4, 2) NOT NULL DEFAULT 0.60,
    allowable_depletion_p DECIMAL(4, 2) NOT NULL DEFAULT 0.40, -- FAO-56 p factor
    kc_initial DECIMAL(4, 2) NOT NULL DEFAULT 0.60,
    kc_mid DECIMAL(4, 2) NOT NULL DEFAULT 1.15,
    kc_end DECIMAL(4, 2) NOT NULL DEFAULT 0.80,
    stage_days_initial INT NOT NULL DEFAULT 25,
    stage_days_dev INT NOT NULL DEFAULT 35,
    stage_days_mid INT NOT NULL DEFAULT 40,
    stage_days_late INT NOT NULL DEFAULT 20,
    economic_priority_weight DECIMAL(4, 2) NOT NULL DEFAULT 1.00,
    source_citation VARCHAR(255) DEFAULT 'FAO-56 Table 12 & Table 22'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Farm Zones
CREATE TABLE farm_zones (
    id VARCHAR(36) PRIMARY KEY,
    farm_id VARCHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    area_sqm DECIMAL(10, 2) NOT NULL,
    crop_id VARCHAR(36) NOT NULL,
    growth_stage ENUM('initial', 'development', 'mid', 'late') NOT NULL DEFAULT 'mid',
    soil_type_id VARCHAR(36) NOT NULL,
    root_depth_m DECIMAL(4, 2) NOT NULL,
    current_moisture_pct DECIMAL(5, 2) NOT NULL,
    moisture_data_source ENUM('manual_estimate', 'feel_appearance', 'sample_sensor', 'model_projection') NOT NULL DEFAULT 'model_projection',
    last_moisture_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    priority_override INT DEFAULT 0, -- Higher integer = higher allocation priority during drought
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_zones_farm FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
    CONSTRAINT fk_zones_crop FOREIGN KEY (crop_id) REFERENCES crops(id),
    CONSTRAINT fk_zones_soil FOREIGN KEY (soil_type_id) REFERENCES soil_types(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Weather Records (Observed historical)
CREATE TABLE weather_records (
    id VARCHAR(36) PRIMARY KEY,
    farm_id VARCHAR(36) NOT NULL,
    recorded_date DATE NOT NULL,
    temp_max_c DECIMAL(5, 2),
    temp_min_c DECIMAL(5, 2),
    precipitation_mm DECIMAL(6, 2) NOT NULL DEFAULT 0.00,
    et0_mm DECIMAL(5, 2) NOT NULL DEFAULT 4.00,
    relative_humidity_pct DECIMAL(5, 2),
    source VARCHAR(100) DEFAULT 'Open-Meteo Historical / Local Station',
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_farm_date_hist (farm_id, recorded_date),
    CONSTRAINT fk_weather_hist_farm FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Weather Forecasts (7-day forecast cache)
CREATE TABLE weather_forecasts (
    id VARCHAR(36) PRIMARY KEY,
    farm_id VARCHAR(36) NOT NULL,
    forecast_date DATE NOT NULL,
    temp_max_c DECIMAL(5, 2),
    temp_min_c DECIMAL(5, 2),
    precipitation_mm DECIMAL(6, 2) NOT NULL DEFAULT 0.00,
    precipitation_probability_pct INT DEFAULT 0,
    et0_mm DECIMAL(5, 2) NOT NULL DEFAULT 4.50,
    source VARCHAR(100) DEFAULT 'Open-Meteo Forecast API',
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_farm_date_fore (farm_id, forecast_date),
    CONSTRAINT fk_weather_fore_farm FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Irrigation Recommendations
CREATE TABLE irrigation_recommendations (
    id VARCHAR(36) PRIMARY KEY,
    zone_id VARCHAR(36) NOT NULL,
    recommendation_date DATE NOT NULL,
    suggested_time_window VARCHAR(50) DEFAULT '06:00 - 08:30 (Early Morning)',
    etc_mm DECIMAL(6, 2) NOT NULL,
    effective_rain_mm DECIMAL(6, 2) NOT NULL,
    net_requirement_mm DECIMAL(6, 2) NOT NULL,
    gross_litres DECIMAL(10, 2) NOT NULL,
    remaining_tank_litres DECIMAL(12, 2) NOT NULL,
    status ENUM('irrigate', 'monitor', 'postpone', 'water_limited') NOT NULL,
    rule_triggered VARCHAR(100) NOT NULL,
    explanation TEXT NOT NULL,
    input_snapshot_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_rec_zone FOREIGN KEY (zone_id) REFERENCES farm_zones(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. Irrigation Logs
CREATE TABLE irrigation_logs (
    id VARCHAR(36) PRIMARY KEY,
    zone_id VARCHAR(36) NOT NULL,
    farm_id VARCHAR(36) NOT NULL,
    logged_date DATE NOT NULL,
    recommended_litres DECIMAL(10, 2) NOT NULL,
    actual_litres DECIMAL(10, 2) NOT NULL,
    status ENUM('completed', 'skipped', 'modified') NOT NULL DEFAULT 'completed',
    notes TEXT,
    logged_offline BOOLEAN DEFAULT FALSE,
    sync_status ENUM('synced', 'pending', 'conflict') DEFAULT 'synced',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_log_zone FOREIGN KEY (zone_id) REFERENCES farm_zones(id) ON DELETE CASCADE,
    CONSTRAINT fk_log_farm FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. Sync Events Table (for offline synchronization audit)
CREATE TABLE sync_events (
    id VARCHAR(36) PRIMARY KEY,
    client_id VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(36) NOT NULL,
    action ENUM('create', 'update', 'delete') NOT NULL,
    payload_json JSON NOT NULL,
    status ENUM('success', 'failed', 'conflict') NOT NULL,
    error_message TEXT,
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Indexes for fast querying
CREATE INDEX idx_zones_farm ON farm_zones(farm_id);
CREATE INDEX idx_logs_date ON irrigation_logs(logged_date);
CREATE INDEX idx_logs_zone ON irrigation_logs(zone_id);
CREATE INDEX idx_rec_zone_date ON irrigation_recommendations(zone_id, recommendation_date);
