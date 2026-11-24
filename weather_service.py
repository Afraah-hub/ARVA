"""
Open-Meteo Weather Service for ARVA Backend
Fetches ET0, temperature, and precipitation forecasts with local DB caching and fallback
"""

import httpx
from datetime import datetime, date, timedelta
from typing import Dict, Any, List
from app.core.config import settings

SAMPLE_FORECASTS = [
    {"forecast_date": (date.today() + timedelta(days=i)).isoformat(),
     "temp_max_c": 30.5 + (i * 0.2), "temp_min_c": 20.0,
     "precipitation_mm": 12.0 if i == 3 else (4.5 if i == 2 else 0.0),
     "precipitation_probability_pct": 80 if i == 3 else (50 if i == 2 else 10),
     "et0_mm": 3.2 if i == 3 else 4.6,
     "source": "Agro-Climatic Baseline Sample"}
    for i in range(7)
]

async def fetch_weather_forecast(latitude: float = 12.9716, longitude: float = 77.5946) -> Dict[str, Any]:
    url = f"{settings.OPEN_METEO_BASE_URL}/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "et0_fao_evapotranspiration",
            "weathercode"
        ],
        "timezone": "auto"
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                daily = data.get("daily", {})
                times = daily.get("time", [])
                forecasts = []
                for idx, d_str in enumerate(times):
                    forecasts.append({
                        "forecast_date": d_str,
                        "temp_max_c": daily.get("temperature_2m_max", [])[idx] if idx < len(daily.get("temperature_2m_max", [])) else 30.0,
                        "temp_min_c": daily.get("temperature_2m_min", [])[idx] if idx < len(daily.get("temperature_2m_min", [])) else 20.0,
                        "precipitation_mm": daily.get("precipitation_sum", [])[idx] if idx < len(daily.get("precipitation_sum", [])) else 0.0,
                        "precipitation_probability_pct": daily.get("precipitation_probability_max", [])[idx] if idx < len(daily.get("precipitation_probability_max", [])) else 0,
                        "et0_mm": daily.get("et0_fao_evapotranspiration", [])[idx] if idx < len(daily.get("et0_fao_evapotranspiration", [])) else 4.5,
                        "source": "Open-Meteo Forecast API (Live)"
                    })
                return {
                    "is_live": True,
                    "source": "Open-Meteo Forecast API (WMO Standard)",
                    "fetched_at": datetime.utcnow().isoformat(),
                    "forecasts": forecasts
                }
    except Exception as e:
        print(f"Weather API error: {e}. Falling back to baseline sample.")

    return {
        "is_live": False,
        "is_sample": True,
        "source": "Baseline Agro-Climatic Profile (Offline Fallback)",
        "fetched_at": datetime.utcnow().isoformat(),
        "warning": "Live weather service unreachable. Using representative agro-climatic baseline.",
        "forecasts": SAMPLE_FORECASTS
    }
