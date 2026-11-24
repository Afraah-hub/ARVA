"""
ARVA Irrigation Prediction & Soil-Water Balance Engine (Python)
Implementation of FAO-56 (Food and Agriculture Organization) Methodology

Rules:
1. ETc = ET0 * Kc
2. TAW = 1000 * (theta_FC - theta_WP) * Zr (mm)
3. RAW = p * TAW (mm)
4. S_{t+1} = clip(S_t + P_eff + I_net - ETc - Drainage, S_min, S_max)
5. 1 mm over 1 m² = 1 Litre
6. Gross Tank Litres = (Net mm * Area m²) / Irrigation Efficiency
"""

import math
from typing import Dict, Any, List, Optional

def get_stage_kc(crop: Any, stage: str = "mid") -> float:
    s = (stage or "mid").lower()
    kc_initial = getattr(crop, "kc_initial", 0.60) or 0.60
    kc_mid = getattr(crop, "kc_mid", 1.15) or 1.15
    kc_end = getattr(crop, "kc_end", 0.80) or 0.80
    
    if s == "initial":
        return float(kc_initial)
    elif s == "development":
        return round((float(kc_initial) + float(kc_mid)) / 2.0, 2)
    elif s == "mid":
        return float(kc_mid)
    elif s in ["late", "end"]:
        return float(kc_end)
    return float(kc_mid)

def calculate_crop_water_demand(et0: float, kc: float) -> float:
    safe_et0 = max(0.0, float(et0 or 0.0))
    safe_kc = max(0.1, float(kc or 1.0))
    return round(safe_et0 * safe_kc, 2)

def calculate_soil_water_capacity(
    field_capacity_pct: float,
    wilting_point_pct: float,
    root_depth_m: float,
    depletion_fraction_p: float = 0.40
) -> Dict[str, float]:
    fc = max(0.0, float(field_capacity_pct or 25.0)) / 100.0
    wp = max(0.0, float(wilting_point_pct or 12.0)) / 100.0
    zr = max(0.1, float(root_depth_m or 0.60))
    p = min(0.8, max(0.1, float(depletion_fraction_p or 0.40)))

    taw = max(0.0, 1000.0 * (fc - wp) * zr)
    raw = max(0.0, p * taw)
    max_storage = 1000.0 * fc * zr
    min_storage = 1000.0 * wp * zr
    critical_pct = round((fc - p * (fc - wp)) * 100.0, 2)

    return {
        "taw_mm": round(taw, 2),
        "raw_mm": round(raw, 2),
        "max_storage_mm": round(max_storage, 2),
        "min_storage_mm": round(min_storage, 2),
        "critical_moisture_pct": critical_pct,
        "fc_pct": round(fc * 100.0, 2),
        "wp_pct": round(wp * 100.0, 2)
    }

def moisture_pct_to_storage_mm(moisture_pct: float, root_depth_m: float) -> float:
    theta = max(0.0, float(moisture_pct or 0.0)) / 100.0
    zr = max(0.1, float(root_depth_m or 0.60))
    return round(1000.0 * theta * zr, 2)

def storage_mm_to_moisture_pct(storage_mm: float, root_depth_m: float) -> float:
    zr = max(0.1, float(root_depth_m or 0.60))
    if zr <= 0:
        return 0.0
    return round((storage_mm / (1000.0 * zr)) * 100.0, 2)

def calculate_effective_rainfall(rainfall_mm: float, soil_deficit_mm: float) -> float:
    rain = max(0.0, float(rainfall_mm or 0.0))
    deficit = max(0.0, float(soil_deficit_mm or 0.0))

    if rain <= 4.0:
        return 0.0
    potential_infiltration = (rain - 4.0) * 0.80
    return round(min(potential_infiltration, deficit), 2)

def calculate_daily_soil_water_balance(
    current_storage_mm: float,
    etc_mm: float,
    effective_rain_mm: float,
    irrigation_net_mm: float,
    max_storage_mm: float,
    min_storage_mm: float
) -> Dict[str, float]:
    st = float(current_storage_mm or 0.0)
    etc = max(0.0, float(etc_mm or 0.0))
    peff = max(0.0, float(effective_rain_mm or 0.0))
    inet = max(0.0, float(irrigation_net_mm or 0.0))
    s_max = max(0.0, float(max_storage_mm or 0.0))
    s_min = max(0.0, float(min_storage_mm or 0.0))

    raw_next = st + peff + inet - etc
    drainage = max(0.0, raw_next - s_max)
    next_storage = min(s_max, max(s_min, raw_next - drainage))

    return {
        "next_storage_mm": round(next_storage, 2),
        "drainage_loss_mm": round(drainage, 2),
        "net_change_mm": round(next_storage - st, 2)
    }

def calculate_gross_tank_withdrawal(net_depth_mm: float, area_sqm: float, efficiency: float = 0.85) -> float:
    depth = max(0.0, float(net_depth_mm or 0.0))
    area = max(0.0, float(area_sqm or 0.0))
    eff = min(1.0, max(0.2, float(efficiency or 0.85)))

    if area == 0 or depth == 0:
        return 0.0
    net_litres = depth * area
    gross_litres = net_litres / eff
    return round(gross_litres, 1)

def evaluate_zone_recommendation(
    zone: Any,
    crop: Any,
    soil: Any,
    weather_today: Dict[str, Any],
    weather_tomorrow: Dict[str, Any],
    tank_remaining_litres: float = 10000.0,
    emergency_reserve_litres: float = 2000.0,
    efficiency: float = 0.85
) -> Dict[str, Any]:
    kc = get_stage_kc(crop, getattr(zone, "growth_stage", "mid"))
    et0 = float(weather_today.get("et0_mm", 4.2))
    etc = calculate_crop_water_demand(et0, kc)

    soil_cap = calculate_soil_water_capacity(
        getattr(soil, "field_capacity_pct", 27.0),
        getattr(soil, "wilting_point_pct", 12.0),
        getattr(zone, "root_depth_m", 0.70),
        getattr(crop, "allowable_depletion_p", 0.40)
    )

    current_storage = moisture_pct_to_storage_mm(
        getattr(zone, "current_moisture_pct", 20.0),
        getattr(zone, "root_depth_m", 0.70)
    )
    deficit_mm = max(0.0, soil_cap["max_storage_mm"] - current_storage)

    today_rain = float(weather_today.get("precipitation_mm", 0.0))
    tomorrow_rain = float(weather_tomorrow.get("precipitation_mm", 0.0))
    forecast_rain = today_rain + tomorrow_rain
    effective_rain = calculate_effective_rainfall(forecast_rain, deficit_mm)

    current_depletion = max(0.0, soil_cap["max_storage_mm"] - current_storage)
    is_depleted_beyond_raw = current_depletion >= soil_cap["raw_mm"]
    projected_storage_tomorrow = current_storage + effective_rain - etc
    is_projected_to_deplete = (soil_cap["max_storage_mm"] - projected_storage_tomorrow) >= soil_cap["raw_mm"]

    available_tank = max(0.0, tank_remaining_litres - emergency_reserve_litres)

    # Rule 1: High rain forecast suppresses irrigation
    if forecast_rain >= 8.0 and (effective_rain >= etc or effective_rain >= deficit_mm * 0.3 or forecast_rain >= 12.0):
        status = "postpone"
        net_requirement_mm = 0.0
        rule = "RAINFALL_SUPPRESSION"
        explanation = f"Significant rain ({forecast_rain:.1f} mm forecast) is expected to infiltrate approx {effective_rain:.1f} mm into the root zone. Irrigation postponed to prevent surface runoff and conserve water."
    elif is_depleted_beyond_raw or is_projected_to_deplete:
        net_requirement_mm = max(0.0, deficit_mm + etc - effective_rain)
        gross_needed = calculate_gross_tank_withdrawal(net_requirement_mm, getattr(zone, "area_sqm", 500.0), efficiency)

        if gross_needed > available_tank:
            status = "water_limited"
            rule = "TANK_CAPACITY_SHORTFALL"
            explanation = f"Zone root-zone depletion ({current_depletion:.1f} mm) exceeds RAW limit ({soil_cap['raw_mm']:.1f} mm). Needed {gross_needed:,.0f} L, but available tank is only {available_tank:,.0f} L. Water rationing applied."
        else:
            status = "irrigate"
            rule = "DEPLETION_EXCEEDED_RAW"
            explanation = f"Moisture is at {getattr(zone, 'current_moisture_pct', 20.0):.1f}% (below critical threshold {soil_cap['critical_moisture_pct']:.1f}%). Root depletion ({current_depletion:.1f} mm) exceeds RAW ({soil_cap['raw_mm']:.1f} mm). Replenish to Field Capacity."
    else:
        status = "monitor"
        net_requirement_mm = 0.0
        rule = "SOIL_MOISTURE_ADEQUATE"
        explanation = f"Moisture ({getattr(zone, 'current_moisture_pct', 20.0):.1f}%) is within safe available water range (RAW: {soil_cap['raw_mm']:.1f} mm). No irrigation required today."

    gross_litres = calculate_gross_tank_withdrawal(net_requirement_mm, getattr(zone, "area_sqm", 500.0), efficiency)

    return {
        "zone_id": getattr(zone, "id", "z1"),
        "zone_name": getattr(zone, "name", "Zone"),
        "crop_name": getattr(crop, "name", "Crop"),
        "growth_stage": getattr(zone, "growth_stage", "mid"),
        "status": status,
        "kc": kc,
        "et0": et0,
        "etc_mm": etc,
        "effective_rain_mm": effective_rain,
        "forecast_rain_mm": forecast_rain,
        "current_moisture_pct": getattr(zone, "current_moisture_pct", 20.0),
        "critical_moisture_pct": soil_cap["critical_moisture_pct"],
        "taw_mm": soil_cap["taw_mm"],
        "raw_mm": soil_cap["raw_mm"],
        "deficit_mm": round(deficit_mm, 1),
        "net_requirement_mm": round(net_requirement_mm, 2),
        "gross_litres": gross_litres,
        "remaining_tank_litres": tank_remaining_litres,
        "rule_triggered": rule,
        "explanation": explanation,
        "confidence": "HIGH"
    }
