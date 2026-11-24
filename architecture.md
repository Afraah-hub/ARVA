# ARVA System Architecture

**ARVA — Predict. Prioritize. Preserve.**  
*Smart Water Tank and Adaptive Irrigation Scheduler based on FAO-56 Soil-Water Balance*

---

## 1. High-Level Architectural Diagram

```mermaid
graph TD
    subgraph Client ["Client Layer (Offline-First PWA)"]
        UI["React 18 + Tailwind CSS + Lucide + Recharts"]
        Router["React Router (10 Core Pages)"]
        SW["Service Worker (Workbox / CacheStorage)"]
        IDB["IndexedDB Client Store (Dexie)"]
        JSEngine["Client Irrigation Engine (FAO-56 JS)"]
        SyncQueue["Client Sync & Audit Queue"]
        WeatherCache["Client Meteorological Cache"]
    end

    subgraph Backend ["FastAPI Backend (Python 3.13)"]
        API["FastAPI REST Endpoints (/api/...)"]
        PyEngine["Server Irrigation Engine (FAO-56 Python)"]
        WeatherService["Open-Meteo Integration Service"]
        ORM["SQLAlchemy ORM 2.0"]
    end

    subgraph DataStore ["Database Layer"]
        MySQL[("MySQL 8.0+ / SQLite Portability Engine")]
        Schema["schema.sql + seed.sql"]
    end

    subgraph External ["External Services"]
        OpenMeteo["Open-Meteo WMO Forecast & Historical API"]
    end

    UI --> Router
    UI --> SW
    UI --> IDB
    UI --> JSEngine
    IDB <--> SyncQueue
    IDB <--> WeatherCache

    UI -->|Online HTTP / REST| API
    SyncQueue -->|Reconcile Offline Events| API
    WeatherService -->|Fetch Live ET0 & Precip| OpenMeteo

    API --> PyEngine
    API --> WeatherService
    API --> ORM
    ORM --> MySQL
```

---

## 2. Key Architectural Decisions

### A. Dual Engine Pattern for Offline Autonomy
The mathematical core of ARVA is implemented identically in:
1. `frontend/src/engine/irrigationEngine.js` (Client-side JavaScript)
2. `backend/app/services/irrigation_engine.py` (Server-side Python)

This guarantees that a farmer in a remote rural field with no mobile cellular reception can perform full 7-day soil water balance projections, inspect water shortages, and adjust irrigation recommendations offline.

### B. Graceful Degradation & Fallback Strategy
- **Weather Service:** If Open-Meteo is unreachable or the device is offline, ARVA loads the most recent cached meteorological forecast from IndexedDB. If no cache exists, it falls back to a deterministic regional agro-climatic baseline.
- **Database Engine:** The backend connects to MySQL by default. If MySQL is not running on the evaluator's machine, it automatically falls back to an embedded SQLite database (`arva.db`) without throwing unhandled exceptions.

### C. Zero-Conflict Change Synchronization
When actions (e.g. creating a zone, updating moisture, completing an irrigation cycle) are performed offline:
1. Records are assigned client UUIDs and persisted immediately in IndexedDB.
2. The action is recorded in `syncQueue`.
3. When network connectivity is restored, the client posts the batch to `/api/sync`.
4. The server merges events using idempotent keys (`UUID`), preventing duplicates.
