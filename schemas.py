from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime

class FarmBase(BaseModel):
    name: str
    location_name: Optional[str] = "Green Valley Community Farm"
    latitude: float = 12.9716
    longitude: float = 77.5946
    total_area_sqm: float = 4000.0
    tank_capacity_litres: float = 20000.0
    current_tank_litres: float = 14500.0
    emergency_reserve_percent: float = 15.0
    default_irrigation_efficiency: float = 0.85

class FarmCreate(FarmBase):
    id: Optional[str] = None
    user_id: Optional[str] = "usr-demo-001"

class FarmUpdate(BaseModel):
    name: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_area_sqm: Optional[float] = None
    tank_capacity_litres: Optional[float] = None
    current_tank_litres: Optional[float] = None
    emergency_reserve_percent: Optional[float] = None
    default_irrigation_efficiency: Optional[float] = None

class FarmOut(FarmBase):
    id: str
    user_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class SoilTypeOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    field_capacity_pct: float
    wilting_point_pct: float
    available_water_capacity_mm_per_m: float
    infiltration_rate_mm_hr: float
    source_citation: Optional[str] = None
    class Config:
        from_attributes = True

class CropOut(BaseModel):
    id: str
    name: str
    category: Optional[str] = "Vegetables"
    default_root_depth_m: float
    allowable_depletion_p: float
    kc_initial: float
    kc_mid: float
    kc_end: float
    stage_days_initial: int
    stage_days_dev: int
    stage_days_mid: int
    stage_days_late: int
    economic_priority_weight: float
    source_citation: Optional[str] = None
    class Config:
        from_attributes = True

class ZoneBase(BaseModel):
    name: str
    area_sqm: float
    crop_id: str
    growth_stage: str = "mid"
    soil_type_id: str
    root_depth_m: float
    current_moisture_pct: float
    moisture_data_source: str = "model_projection"
    priority_override: Optional[int] = 0

class ZoneCreate(ZoneBase):
    id: Optional[str] = None
    farm_id: Optional[str] = "frm-demo-001"

class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    area_sqm: Optional[float] = None
    crop_id: Optional[str] = None
    growth_stage: Optional[str] = None
    soil_type_id: Optional[str] = None
    root_depth_m: Optional[float] = None
    current_moisture_pct: Optional[float] = None
    moisture_data_source: Optional[str] = None
    priority_override: Optional[int] = None

class ZoneOut(ZoneBase):
    id: str
    farm_id: str
    last_moisture_update: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class WeatherForecastOut(BaseModel):
    id: Optional[str] = None
    forecast_date: date
    temp_max_c: Optional[float] = None
    temp_min_c: Optional[float] = None
    precipitation_mm: float = 0.0
    precipitation_probability_pct: int = 0
    et0_mm: float = 4.5
    source: str = "Open-Meteo Forecast API"
    class Config:
        from_attributes = True

class IrrigationRecommendationOut(BaseModel):
    zone_id: str
    zone_name: str
    crop_name: str
    growth_stage: str
    status: str # irrigate, monitor, postpone, water_limited
    kc: float
    et0: float
    etc_mm: float
    effective_rain_mm: float
    forecast_rain_mm: float
    current_moisture_pct: float
    critical_moisture_pct: float
    taw_mm: float
    raw_mm: float
    deficit_mm: float
    net_requirement_mm: float
    gross_litres: float
    remaining_tank_litres: float
    rule_triggered: str
    explanation: str
    confidence: str = "HIGH"

class IrrigationLogBase(BaseModel):
    zone_id: str
    farm_id: Optional[str] = "frm-demo-001"
    logged_date: Optional[date] = None
    recommended_litres: float
    actual_litres: float
    status: str = "completed"
    notes: Optional[str] = None
    logged_offline: bool = False
    sync_status: str = "synced"

class IrrigationLogCreate(IrrigationLogBase):
    id: Optional[str] = None

class IrrigationLogUpdate(BaseModel):
    actual_litres: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    sync_status: Optional[str] = None

class IrrigationLogOut(IrrigationLogBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class SyncEventItem(BaseModel):
    id: str
    entity: str
    action: str
    payload: Dict[str, Any]
    created_at: Optional[str] = None

class SyncBatchRequest(BaseModel):
    events: List[SyncEventItem]

class SyncBatchResponse(BaseModel):
    status: str
    processed_count: int
    errors: List[str] = []

class PredictCropRequest(BaseModel):
    crop_id: Optional[str] = "crop-01"
    crop_name: Optional[str] = None
    growth_stage: str = "mid"
    soil_type_id: Optional[str] = "soil-02"
    area_sqm: float = 800.0
    current_moisture_pct: float = 18.0
    root_depth_m: Optional[float] = None
    et0_mm: Optional[float] = 4.5
    forecast_rain_mm: Optional[float] = 0.0
    tank_litres: Optional[float] = 16800.0
    tank_capacity_litres: Optional[float] = 25000.0
    emergency_reserve_percent: Optional[float] = 15.0
    efficiency: Optional[float] = 0.85

class PredictCropResponse(BaseModel):
    crop_name: str
    growth_stage: str
    status: str
    kc: float
    et0: float
    etc_mm: float
    effective_rain_mm: float
    forecast_rain_mm: float
    current_moisture_pct: float
    critical_moisture_pct: float
    taw_mm: float
    raw_mm: float
    deficit_mm: float
    net_requirement_mm: float
    gross_litres: float
    remaining_tank_litres: float
    rule_triggered: str
    explanation: str
    confidence: str = "HIGH"
    engine: str = "FastAPI Python FAO-56 Soil-Water Balance"

