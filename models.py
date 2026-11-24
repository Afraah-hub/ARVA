from sqlalchemy import Column, String, Integer, Float, Boolean, Date, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    farms = relationship("Farm", back_populates="user", cascade="all, delete-orphan")

class Farm(Base):
    __tablename__ = "farms"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    location_name = Column(String(255), default="Green Valley Community Farm")
    latitude = Column(Float, default=12.9716)
    longitude = Column(Float, default=77.5946)
    total_area_sqm = Column(Float, default=4000.0)
    tank_capacity_litres = Column(Float, default=20000.0)
    current_tank_litres = Column(Float, default=14500.0)
    emergency_reserve_percent = Column(Float, default=15.0)
    default_irrigation_efficiency = Column(Float, default=0.85)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="farms")
    zones = relationship("FarmZone", back_populates="farm", cascade="all, delete-orphan")
    weather_records = relationship("WeatherRecord", back_populates="farm", cascade="all, delete-orphan")
    weather_forecasts = relationship("WeatherForecast", back_populates="farm", cascade="all, delete-orphan")
    irrigation_logs = relationship("IrrigationLog", back_populates="farm", cascade="all, delete-orphan")

class SoilType(Base):
    __tablename__ = "soil_types"
    id = Column(String(36), primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    field_capacity_pct = Column(Float, nullable=False)
    wilting_point_pct = Column(Float, nullable=False)
    available_water_capacity_mm_per_m = Column(Float, nullable=False)
    infiltration_rate_mm_hr = Column(Float, nullable=False)
    source_citation = Column(String(255), default="FAO Irrigation and Drainage Paper 56")

    zones = relationship("FarmZone", back_populates="soil_type")

class Crop(Base):
    __tablename__ = "crops"
    id = Column(String(36), primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), default="Vegetables")
    default_root_depth_m = Column(Float, default=0.6)
    allowable_depletion_p = Column(Float, default=0.40)
    kc_initial = Column(Float, default=0.60)
    kc_mid = Column(Float, default=1.15)
    kc_end = Column(Float, default=0.80)
    stage_days_initial = Column(Integer, default=25)
    stage_days_dev = Column(Integer, default=35)
    stage_days_mid = Column(Integer, default=40)
    stage_days_late = Column(Integer, default=20)
    economic_priority_weight = Column(Float, default=1.0)
    source_citation = Column(String(255), default="FAO-56 Table 12 & Table 22")

    zones = relationship("FarmZone", back_populates="crop")

class FarmZone(Base):
    __tablename__ = "farm_zones"
    id = Column(String(36), primary_key=True)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    area_sqm = Column(Float, nullable=False)
    crop_id = Column(String(36), ForeignKey("crops.id"), nullable=False)
    growth_stage = Column(String(30), default="mid")
    soil_type_id = Column(String(36), ForeignKey("soil_types.id"), nullable=False)
    root_depth_m = Column(Float, nullable=False)
    current_moisture_pct = Column(Float, nullable=False)
    moisture_data_source = Column(String(50), default="model_projection")
    last_moisture_update = Column(DateTime, default=datetime.utcnow)
    priority_override = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    farm = relationship("Farm", back_populates="zones")
    crop = relationship("Crop", back_populates="zones")
    soil_type = relationship("SoilType", back_populates="zones")
    recommendations = relationship("IrrigationRecommendation", back_populates="zone", cascade="all, delete-orphan")
    logs = relationship("IrrigationLog", back_populates="zone", cascade="all, delete-orphan")

class WeatherRecord(Base):
    __tablename__ = "weather_records"
    id = Column(String(36), primary_key=True)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    recorded_date = Column(Date, nullable=False)
    temp_max_c = Column(Float, nullable=True)
    temp_min_c = Column(Float, nullable=True)
    precipitation_mm = Column(Float, default=0.0)
    et0_mm = Column(Float, default=4.0)
    relative_humidity_pct = Column(Float, nullable=True)
    source = Column(String(100), default="Open-Meteo Historical Archive")
    fetched_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="weather_records")

class WeatherForecast(Base):
    __tablename__ = "weather_forecasts"
    id = Column(String(36), primary_key=True)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    forecast_date = Column(Date, nullable=False)
    temp_max_c = Column(Float, nullable=True)
    temp_min_c = Column(Float, nullable=True)
    precipitation_mm = Column(Float, default=0.0)
    precipitation_probability_pct = Column(Integer, default=0)
    et0_mm = Column(Float, default=4.5)
    source = Column(String(100), default="Open-Meteo Forecast API")
    fetched_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="weather_forecasts")

class IrrigationRecommendation(Base):
    __tablename__ = "irrigation_recommendations"
    id = Column(String(36), primary_key=True)
    zone_id = Column(String(36), ForeignKey("farm_zones.id", ondelete="CASCADE"), nullable=False)
    recommendation_date = Column(Date, nullable=False)
    suggested_time_window = Column(String(50), default="06:00 - 08:30 (Early Morning)")
    etc_mm = Column(Float, nullable=False)
    effective_rain_mm = Column(Float, nullable=False)
    net_requirement_mm = Column(Float, nullable=False)
    gross_litres = Column(Float, nullable=False)
    remaining_tank_litres = Column(Float, nullable=False)
    status = Column(String(30), nullable=False) # irrigate, monitor, postpone, water_limited
    rule_triggered = Column(String(100), nullable=False)
    explanation = Column(Text, nullable=False)
    input_snapshot_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    zone = relationship("FarmZone", back_populates="recommendations")

class IrrigationLog(Base):
    __tablename__ = "irrigation_logs"
    id = Column(String(36), primary_key=True)
    zone_id = Column(String(36), ForeignKey("farm_zones.id", ondelete="CASCADE"), nullable=False)
    farm_id = Column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    logged_date = Column(Date, nullable=False)
    recommended_litres = Column(Float, nullable=False)
    actual_litres = Column(Float, nullable=False)
    status = Column(String(30), default="completed") # completed, skipped, modified
    notes = Column(Text, nullable=True)
    logged_offline = Column(Boolean, default=False)
    sync_status = Column(String(30), default="synced")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    zone = relationship("FarmZone", back_populates="logs")
    farm = relationship("Farm", back_populates="irrigation_logs")

class SyncEvent(Base):
    __tablename__ = "sync_events"
    id = Column(String(36), primary_key=True)
    client_id = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(36), nullable=False)
    action = Column(String(20), nullable=False) # create, update, delete
    payload_json = Column(JSON, nullable=False)
    status = Column(String(20), nullable=False) # success, failed, conflict
    error_message = Column(Text, nullable=True)
    synced_at = Column(DateTime, default=datetime.utcnow)
