from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, date, timedelta

from app.core.config import settings
from app.db.session import engine, Base, SessionLocal
from app.api.routes import router
from app.models.models import User, Farm, SoilType, Crop, FarmZone, IrrigationLog

# Initialize database schema
Base.metadata.create_all(bind=engine)

def seed_database_if_empty():
    db = SessionLocal()
    try:
        if db.query(Farm).count() == 0:
            # 1. User
            user = User(
                id="usr-demo-001",
                email="farmer@arva.ag",
                password_hash="scrypt_demo_hash_secure",
                full_name="Maria Silva (Head Horticulturist)"
            )
            db.add(user)

            # 2. Farm
            farm = Farm(
                id="frm-demo-001",
                user_id="usr-demo-001",
                name="Green Valley Community Farm",
                location_name="Bangalore Rural Agro-Climatic Zone",
                latitude=12.9716,
                longitude=77.5946,
                total_area_sqm=3200.0,
                tank_capacity_litres=25000.0,
                current_tank_litres=16800.0,
                emergency_reserve_percent=15.0,
                default_irrigation_efficiency=0.85
            )
            db.add(farm)

            # 3. Soil Types
            soils = [
                SoilType(id="soil-01", name="Sandy Loam", description="Coarse texture with rapid drainage.", field_capacity_pct=18.0, wilting_point_pct=8.0, available_water_capacity_mm_per_m=100.0, infiltration_rate_mm_hr=25.0, source_citation="FAO-56 Table 19"),
                SoilType(id="soil-02", name="Loam", description="Ideal agricultural balance.", field_capacity_pct=27.0, wilting_point_pct=12.0, available_water_capacity_mm_per_m=150.0, infiltration_rate_mm_hr=13.0, source_citation="FAO-56 Table 19"),
                SoilType(id="soil-03", name="Clay Loam", description="Heavy soil, high water holding.", field_capacity_pct=32.0, wilting_point_pct=18.0, available_water_capacity_mm_per_m=140.0, infiltration_rate_mm_hr=8.0, source_citation="FAO-56 Table 19"),
                SoilType(id="soil-04", name="Silt Loam", description="High water capacity for horticulture.", field_capacity_pct=31.0, wilting_point_pct=11.0, available_water_capacity_mm_per_m=200.0, infiltration_rate_mm_hr=10.0, source_citation="FAO-56 Table 19")
            ]
            for s in soils:
                db.add(s)

            # 4. Crops
            crops = [
                Crop(id="crop-01", name="Tomato", category="Vegetables", default_root_depth_m=0.70, allowable_depletion_p=0.40, kc_initial=0.60, kc_mid=1.15, kc_end=0.80, economic_priority_weight=1.3, source_citation="FAO-56 Table 12"),
                Crop(id="crop-02", name="Sweet Corn / Maize", category="Grain & Cereal", default_root_depth_m=1.00, allowable_depletion_p=0.55, kc_initial=0.30, kc_mid=1.20, kc_end=0.60, economic_priority_weight=1.0, source_citation="FAO-56 Table 12"),
                Crop(id="crop-03", name="Bell Pepper", category="Vegetables", default_root_depth_m=0.60, allowable_depletion_p=0.30, kc_initial=0.60, kc_mid=1.05, kc_end=0.90, economic_priority_weight=1.4, source_citation="FAO-56 Table 12"),
                Crop(id="crop-04", name="Potato", category="Tubers", default_root_depth_m=0.50, allowable_depletion_p=0.35, kc_initial=0.50, kc_mid=1.15, kc_end=0.75, economic_priority_weight=1.15, source_citation="FAO-56 Table 12"),
                Crop(id="crop-05", name="Spinach / Leafy Greens", category="Horticulture", default_root_depth_m=0.30, allowable_depletion_p=0.20, kc_initial=0.70, kc_mid=1.00, kc_end=0.95, economic_priority_weight=0.90, source_citation="FAO-56 Table 12")
            ]
            for c in crops:
                db.add(c)

            # 5. Farm Zones
            zones = [
                FarmZone(id="zone-01", farm_id="frm-demo-001", name="North Terrace: Roma Tomatoes", area_sqm=800.0, crop_id="crop-01", growth_stage="mid", soil_type_id="soil-02", root_depth_m=0.70, current_moisture_pct=17.5, moisture_data_source="model_projection", priority_override=1),
                FarmZone(id="zone-02", farm_id="frm-demo-001", name="East Plot: Sweet Corn", area_sqm=1200.0, crop_id="crop-02", growth_stage="development", soil_type_id="soil-01", root_depth_m=0.85, current_moisture_pct=14.2, moisture_data_source="manual_estimate", priority_override=0),
                FarmZone(id="zone-03", farm_id="frm-demo-001", name="Polyhouse A: Bell Peppers", area_sqm=500.0, crop_id="crop-03", growth_stage="mid", soil_type_id="soil-02", root_depth_m=0.60, current_moisture_pct=19.8, moisture_data_source="feel_appearance", priority_override=2),
                FarmZone(id="zone-04", farm_id="frm-demo-001", name="South Basin: Yukon Gold Potatoes", area_sqm=700.0, crop_id="crop-04", growth_stage="late", soil_type_id="soil-04", root_depth_m=0.50, current_moisture_pct=22.0, moisture_data_source="model_projection", priority_override=0)
            ]
            for z in zones:
                db.add(z)

            # 6. Sample Logs
            logs = [
                IrrigationLog(id="log-01", zone_id="zone-01", farm_id="frm-demo-001", logged_date=date.today() - timedelta(days=4), recommended_litres=4200.0, actual_litres=4200.0, status="completed", notes="Scheduled drip cycle completed. Roots moist."),
                IrrigationLog(id="log-02", zone_id="zone-02", farm_id="frm-demo-001", logged_date=date.today() - timedelta(days=3), recommended_litres=5800.0, actual_litres=5200.0, status="modified", notes="Slight reduction due to morning cloudiness."),
                IrrigationLog(id="log-03", zone_id="zone-03", farm_id="frm-demo-001", logged_date=date.today() - timedelta(days=2), recommended_litres=2100.0, actual_litres=2100.0, status="completed", notes="Bell peppers early morning cycle.")
            ]
            for l in logs:
                db.add(l)

            db.commit()
            print("Successfully initialized ARVA database with baseline farm and FAO-56 parameters.")
    finally:
        db.close()

seed_database_if_empty()

app = FastAPI(
    title="ARVA — Predict. Prioritize. Preserve.",
    description="Smart Water Tank and Irrigation Scheduler based on FAO-56 Soil-Water Balance",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
