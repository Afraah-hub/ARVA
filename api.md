# ARVA REST API Documentation

**FastAPI Backend Service Specifications**

---

## Base URL
- Local: `http://localhost:8000`
- Interactive Swagger UI: `http://localhost:8000/docs`
- Interactive ReDoc: `http://localhost:8000/redoc`

---

## Endpoints

### 1. System Health
- **`GET /health`**
  - **Response:**
    ```json
    {
      "status": "healthy",
      "service": "ARVA Agronomic Irrigation Backend",
      "model": "FAO-56 Dual Soil Water Balance",
      "timestamp": "2026-10-21T07:20:29.025546"
    }
    ```

### 2. Farms
- **`GET /api/farms/{farm_id}`**
  - Retrieves farm metadata, reservoir capacity, and current tank volume.
- **`PATCH /api/farms/{farm_id}`**
  - Updates farm properties (tank volume, reserve percentage, efficiency).

### 3. Farm Zones
- **`GET /api/farms/{farm_id}/zones`**
  - Returns array of cultivated zones with crop, soil, and moisture records.
- **`POST /api/farms/{farm_id}/zones`**
  - Creates a new cultivation plot.
- **`PATCH /api/zones/{zone_id}`**
  - Updates zone parameters (growth stage, current moisture, priority override).
- **`DELETE /api/zones/{zone_id}`**
  - Removes a zone.

### 4. Crop & Soil Library
- **`GET /api/crops`**
  - Returns FAO-56 crop coefficients, stages, and allowable depletion fractions.
- **`GET /api/soil-types`**
  - Returns soil types with field capacities, wilting points, and infiltration rates.

### 5. Weather
- **`GET /api/weather?lat=12.9716&lon=77.5946`**
  - Returns live 7-day meteorological forecast including $ET_0$ and precipitation.

### 6. Recommendations
- **`GET /api/predictions?farm_id=frm-demo-001`**
  - Returns today's evaluated irrigation recommendations for all zones.

### 7. Irrigation Logs
- **`GET /api/irrigation-logs`**
  - Returns chronological history of completed and skipped irrigation events.
- **`POST /api/irrigation-logs`**
  - Records a completed or modified irrigation event and updates tank level.

### 8. Synchronization
- **`POST /api/sync`**
  - Receives offline queued actions from the PWA client, reconciles them into the database, and returns processed counts.
