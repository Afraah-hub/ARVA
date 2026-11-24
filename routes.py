from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime, date

from app.db.session import get_db
from app.models.models import Farm, FarmZone, Crop, SoilType, IrrigationLog, WeatherRecord, WeatherForecast, SyncEvent
from app.schemas.schemas import (
    FarmOut, FarmUpdate,
    ZoneOut, ZoneCreate, ZoneUpdate,
    CropOut, SoilTypeOut,
    WeatherForecastOut,
    IrrigationRecommendationOut,
    IrrigationLogOut, IrrigationLogCreate, IrrigationLogUpdate,
    SyncBatchRequest, SyncBatchResponse,
    PredictCropRequest, PredictCropResponse
)
from app.services.irrigation_engine import evaluate_zone_recommendation
from app.services.weather_service import fetch_weather_forecast

router = APIRouter()

# 1. Health Endpoint
@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ARVA Agronomic Irrigation Backend",
        "model": "FAO-56 Dual Soil Water Balance",
        "timestamp": datetime.utcnow().isoformat()
    }

# 2. Farm Management
@router.get("/api/farms/{farm_id}", response_model=FarmOut)
def get_farm(farm_id: str, db: Session = Depends(get_db)):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm

@router.patch("/api/farms/{farm_id}", response_model=FarmOut)
def update_farm(farm_id: str, farm_update: FarmUpdate, db: Session = Depends(get_db)):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    update_data = farm_update.dict(exclude_unset=True)
    for field, val in update_data.items():
        setattr(farm, field, val)
    db.commit()
    db.refresh(farm)
    return farm

# 3. Zone Management
@router.get("/api/farms/{farm_id}/zones", response_model=List[ZoneOut])
def get_farm_zones(farm_id: str, db: Session = Depends(get_db)):
    return db.query(FarmZone).filter(FarmZone.farm_id == farm_id).all()

@router.post("/api/farms/{farm_id}/zones", response_model=ZoneOut)
def create_zone(farm_id: str, zone_in: ZoneCreate, db: Session = Depends(get_db)):
    zone_id = zone_in.id or f"zone-{uuid.uuid4().hex[:8]}"
    db_zone = FarmZone(
        id=zone_id,
        farm_id=farm_id,
        name=zone_in.name,
        area_sqm=zone_in.area_sqm,
        crop_id=zone_in.crop_id,
        growth_stage=zone_in.growth_stage,
        soil_type_id=zone_in.soil_type_id,
        root_depth_m=zone_in.root_depth_m,
        current_moisture_pct=zone_in.current_moisture_pct,
        moisture_data_source=zone_in.moisture_data_source,
        priority_override=zone_in.priority_override or 0,
        last_moisture_update=datetime.utcnow()
    )
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    return db_zone

@router.patch("/api/zones/{zone_id}", response_model=ZoneOut)
def update_zone(zone_id: str, zone_update: ZoneUpdate, db: Session = Depends(get_db)):
    zone = db.query(FarmZone).filter(FarmZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    update_data = zone_update.dict(exclude_unset=True)
    for field, val in update_data.items():
        setattr(zone, field, val)
    zone.last_moisture_update = datetime.utcnow()
    db.commit()
    db.refresh(zone)
    return zone

@router.delete("/api/zones/{zone_id}")
def delete_zone(zone_id: str, db: Session = Depends(get_db)):
    zone = db.query(FarmZone).filter(FarmZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    db.delete(zone)
    db.commit()
    return {"message": "Zone deleted successfully", "id": zone_id}

# 4. Crop & Soil Library
@router.get("/api/crops", response_model=List[CropOut])
def get_crops(db: Session = Depends(get_db)):
    return db.query(Crop).all()

@router.get("/api/soil-types", response_model=List[SoilTypeOut])
def get_soil_types(db: Session = Depends(get_db)):
    return db.query(SoilType).all()

# 5. Weather
@router.get("/api/weather")
async def get_weather(lat: float = 12.9716, lon: float = 77.5946):
    return await fetch_weather_forecast(lat, lon)

# 6. Predictions & Recommendations
@router.get("/api/predictions", response_model=List[IrrigationRecommendationOut])
async def get_all_predictions(farm_id: str = "frm-demo-001", db: Session = Depends(get_db)):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    zones = db.query(FarmZone).filter(FarmZone.farm_id == farm_id).all()
    weather_data = await fetch_weather_forecast(farm.latitude, farm.longitude)
    forecasts = weather_data.get("forecasts", [])
    
    w_today = forecasts[0] if len(forecasts) > 0 else {"et0_mm": 4.5, "precipitation_mm": 0.0}
    w_tomorrow = forecasts[1] if len(forecasts) > 1 else {"precipitation_mm": 0.0}

    reserve_litres = farm.tank_capacity_litres * (farm.emergency_reserve_percent / 100.0)

    recommendations = []
    for zone in zones:
        crop = db.query(Crop).filter(Crop.id == zone.crop_id).first()
        soil = db.query(SoilType).filter(SoilType.id == zone.soil_type_id).first()
        if crop and soil:
            rec = evaluate_zone_recommendation(
                zone=zone,
                crop=crop,
                soil=soil,
                weather_today=w_today,
                weather_tomorrow=w_tomorrow,
                tank_remaining_litres=farm.current_tank_litres,
                emergency_reserve_litres=reserve_litres,
                efficiency=farm.default_irrigation_efficiency
            )
            recommendations.append(rec)
            
    return recommendations

@router.post("/api/predict-crop", response_model=PredictCropResponse)
def predict_crop(req: PredictCropRequest, db: Session = Depends(get_db)):
    # 1. Resolve crop
    crop = None
    if req.crop_id:
        crop = db.query(Crop).filter(Crop.id == req.crop_id).first()
    if not crop and req.crop_name:
        crop = db.query(Crop).filter(Crop.name.ilike(f"%{req.crop_name}%")).first()
    if not crop:
        class CustomCrop:
            name = req.crop_name or "Custom Crop"
            default_root_depth_m = req.root_depth_m or 0.60
            allowable_depletion_p = 0.40
            kc_initial = 0.50
            kc_mid = 1.10
            kc_end = 0.75
            economic_priority_weight = 1.0
        crop = CustomCrop()

    # 2. Resolve soil
    soil = None
    if req.soil_type_id:
        soil = db.query(SoilType).filter(SoilType.id == req.soil_type_id).first()
    if not soil:
        soil = db.query(SoilType).first()
    if not soil:
        class CustomSoil:
            name = "Standard Agricultural Loam"
            field_capacity_pct = 27.0
            wilting_point_pct = 12.0
            available_water_capacity_mm_per_m = 150.0
            infiltration_rate_mm_hr = 15.0
        soil = CustomSoil()

    # 3. Create simulated zone object
    class VirtualZone:
        id = "sim-zone"
        name = f"Virtual {crop.name}"
        area_sqm = req.area_sqm
        growth_stage = req.growth_stage
        root_depth_m = req.root_depth_m or getattr(crop, "default_root_depth_m", 0.60)
        current_moisture_pct = req.current_moisture_pct

    w_today = {"et0_mm": req.et0_mm or 4.5, "precipitation_mm": 0.0}
    w_tomorrow = {"precipitation_mm": req.forecast_rain_mm or 0.0}

    tank_cap = req.tank_capacity_litres or 25000.0
    reserve_pct = req.emergency_reserve_percent if req.emergency_reserve_percent is not None else 15.0
    reserve = tank_cap * (reserve_pct / 100.0)
    current_tank = req.tank_litres if req.tank_litres is not None else 16800.0
    eff = req.efficiency if req.efficiency is not None else 0.85

    rec = evaluate_zone_recommendation(
        zone=VirtualZone(),
        crop=crop,
        soil=soil,
        weather_today=w_today,
        weather_tomorrow=w_tomorrow,
        tank_remaining_litres=current_tank,
        emergency_reserve_litres=reserve,
        efficiency=eff
    )

    return PredictCropResponse(
        crop_name=rec["crop_name"],
        growth_stage=rec["growth_stage"],
        status=rec["status"],
        kc=rec["kc"],
        et0=rec["et0"],
        etc_mm=rec["etc_mm"],
        effective_rain_mm=rec["effective_rain_mm"],
        forecast_rain_mm=rec["forecast_rain_mm"],
        current_moisture_pct=rec["current_moisture_pct"],
        critical_moisture_pct=rec["critical_moisture_pct"],
        taw_mm=rec["taw_mm"],
        raw_mm=rec["raw_mm"],
        deficit_mm=rec["deficit_mm"],
        net_requirement_mm=rec["net_requirement_mm"],
        gross_litres=rec["gross_litres"],
        remaining_tank_litres=rec["remaining_tank_litres"],
        rule_triggered=rec["rule_triggered"],
        explanation=rec["explanation"],
        confidence=rec.get("confidence", "HIGH"),
        engine="FastAPI Python FAO-56 Soil-Water Balance"
    )

# 7. Irrigation Logs
@router.get("/api/irrigation-logs", response_model=List[IrrigationLogOut])
def get_irrigation_logs(farm_id: str = "frm-demo-001", db: Session = Depends(get_db)):
    return db.query(IrrigationLog).filter(IrrigationLog.farm_id == farm_id).order_by(IrrigationLog.logged_date.desc()).all()

@router.post("/api/irrigation-logs", response_model=IrrigationLogOut)
def create_irrigation_log(log_in: IrrigationLogCreate, db: Session = Depends(get_db)):
    log_id = log_in.id or f"log-{uuid.uuid4().hex[:8]}"
    logged_d = log_in.logged_date or date.today()
    
    db_log = IrrigationLog(
        id=log_id,
        zone_id=log_in.zone_id,
        farm_id=log_in.farm_id or "frm-demo-001",
        logged_date=logged_d,
        recommended_litres=log_in.recommended_litres,
        actual_litres=log_in.actual_litres,
        status=log_in.status,
        notes=log_in.notes,
        logged_offline=log_in.logged_offline,
        sync_status="synced"
    )
    db.add(db_log)
    
    # Also update farm tank volume if completed
    farm = db.query(Farm).filter(Farm.id == db_log.farm_id).first()
    if farm and db_log.status == "completed":
        farm.current_tank_litres = max(0.0, farm.current_tank_litres - db_log.actual_litres)
        
    db.commit()
    db.refresh(db_log)
    return db_log

# 8. Offline Queue Synchronization
@router.post("/api/sync", response_model=SyncBatchResponse)
def sync_offline_events(batch: SyncBatchRequest, db: Session = Depends(get_db)):
    processed = 0
    errors = []
    for item in batch.events:
        try:
            # Audit log
            sync_rec = SyncEvent(
                id=item.id,
                client_id="pwa_client",
                entity_type=item.entity,
                entity_id=str(item.payload.get("id", "unknown")),
                action=item.action,
                payload_json=item.payload,
                status="success"
            )
            db.merge(sync_rec)

            if item.entity == "irrigation_log" and item.action == "create":
                payload = item.payload
                log_id = payload.get("id") or f"log-{uuid.uuid4().hex[:8]}"
                existing = db.query(IrrigationLog).filter(IrrigationLog.id == log_id).first()
                if not existing:
                    d_val = payload.get("logged_date")
                    if isinstance(d_val, str):
                        d_val = datetime.strptime(d_val, "%Y-%m-%d").date()
                    elif not d_val:
                        d_val = date.today()

                    new_log = IrrigationLog(
                        id=log_id,
                        zone_id=payload.get("zone_id"),
                        farm_id=payload.get("farm_id", "frm-demo-001"),
                        logged_date=d_val,
                        recommended_litres=float(payload.get("recommended_litres", 0.0)),
                        actual_litres=float(payload.get("actual_litres", 0.0)),
                        status=payload.get("status", "completed"),
                        notes=payload.get("notes"),
                        logged_offline=True,
                        sync_status="synced"
                    )
                    db.add(new_log)
            processed += 1
        except Exception as e:
            errors.append(f"Error syncing {item.id}: {str(e)}")
            
    db.commit()
    return SyncBatchResponse(
        status="synced",
        processed_count=processed,
        errors=errors
    )
