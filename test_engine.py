import pytest
from app.services.irrigation_engine import (
    calculate_crop_water_demand,
    get_stage_kc,
    calculate_soil_water_capacity,
    moisture_pct_to_storage_mm,
    storage_mm_to_moisture_pct,
    calculate_effective_rainfall,
    calculate_daily_soil_water_balance,
    calculate_gross_tank_withdrawal,
    evaluate_zone_recommendation
)

class MockCrop:
    def __init__(self, name="Tomato", kc_initial=0.6, kc_mid=1.15, kc_end=0.8, allowable_depletion_p=0.4):
        self.name = name
        self.kc_initial = kc_initial
        self.kc_mid = kc_mid
        self.kc_end = kc_end
        self.allowable_depletion_p = allowable_depletion_p

class MockSoil:
    def __init__(self, field_capacity_pct=27.0, wilting_point_pct=12.0):
        self.field_capacity_pct = field_capacity_pct
        self.wilting_point_pct = wilting_point_pct

class MockZone:
    def __init__(self, id="z1", name="Zone 1", area_sqm=500.0, root_depth_m=0.7, growth_stage="mid", current_moisture_pct=16.0):
        self.id = id
        self.name = name
        self.area_sqm = area_sqm
        self.root_depth_m = root_depth_m
        self.growth_stage = growth_stage
        self.current_moisture_pct = current_moisture_pct

def test_crop_water_demand():
    assert calculate_crop_water_demand(4.0, 1.15) == 4.60
    assert calculate_crop_water_demand(0, 1.15) == 0.0

def test_stage_kc():
    crop = MockCrop()
    assert get_stage_kc(crop, "initial") == 0.60
    assert get_stage_kc(crop, "mid") == 1.15
    assert get_stage_kc(crop, "late") == 0.80

def test_soil_water_capacity():
    cap = calculate_soil_water_capacity(27.0, 12.0, 0.70, 0.40)
    assert cap["taw_mm"] == 105.0
    assert cap["raw_mm"] == 42.0
    assert cap["max_storage_mm"] == 189.0
    assert cap["min_storage_mm"] == 84.0

def test_effective_rainfall():
    # Light rainfall intercepted
    assert calculate_effective_rainfall(3.0, 40.0) == 0.0
    # Infiltration within deficit
    assert calculate_effective_rainfall(14.0, 50.0) == 8.0
    # Capped at deficit
    assert calculate_effective_rainfall(25.0, 5.0) == 5.0

def test_daily_soil_water_balance():
    # Drainage when storage exceeds max
    bal = calculate_daily_soil_water_balance(180.0, 3.0, 0.0, 25.0, 189.0, 84.0)
    assert bal["next_storage_mm"] == 189.0
    assert bal["drainage_loss_mm"] == 13.0

def test_gross_tank_withdrawal():
    # 10 mm over 500 m² at 80% efficiency = 5000 / 0.8 = 6250 L
    gross = calculate_gross_tank_withdrawal(10.0, 500.0, 0.80)
    assert gross == 6250.0

def test_evaluate_zone_recommendation():
    crop = MockCrop()
    soil = MockSoil()
    zone = MockZone(current_moisture_pct=15.0) # depleted

    # Dry weather with sufficient tank -> should recommend irrigate
    rec_dry = evaluate_zone_recommendation(
        zone=zone,
        crop=crop,
        soil=soil,
        weather_today={"et0_mm": 4.5, "precipitation_mm": 0.0},
        weather_tomorrow={"precipitation_mm": 0.0},
        tank_remaining_litres=100000.0,
        emergency_reserve_litres=2000.0,
        efficiency=0.85
    )
    assert rec_dry["status"] == "irrigate"
    assert rec_dry["gross_litres"] > 0

    # Dry weather with small tank -> should recommend water_limited
    rec_limited = evaluate_zone_recommendation(
        zone=zone,
        crop=crop,
        soil=soil,
        weather_today={"et0_mm": 4.5, "precipitation_mm": 0.0},
        weather_tomorrow={"precipitation_mm": 0.0},
        tank_remaining_litres=5000.0,
        emergency_reserve_litres=2000.0,
        efficiency=0.85
    )
    assert rec_limited["status"] == "water_limited"
    assert "rationing" in rec_limited["explanation"].lower()

    # Heavy rain forecast -> should postpone
    rec_rainy = evaluate_zone_recommendation(
        zone=zone,
        crop=crop,
        soil=soil,
        weather_today={"et0_mm": 3.0, "precipitation_mm": 20.0},
        weather_tomorrow={"precipitation_mm": 10.0},
        tank_remaining_litres=10000.0,
        emergency_reserve_litres=2000.0,
        efficiency=0.85
    )
    assert rec_rainy["status"] == "postpone"
    assert rec_rainy["net_requirement_mm"] == 0.0
