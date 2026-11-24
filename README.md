# 🌱 ARVA

### Predict. Prioritize. Preserve.

**An Offline-First Smart Water Tank & Adaptive Irrigation Scheduler powered by FAO-56 Soil-Water Balance Modeling**

<p align="center">

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-Latest-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![PWA](https://img.shields.io/badge/PWA-Offline%20First-5A0FC8?style=for-the-badge)
![FAO-56](https://img.shields.io/badge/Agronomy-FAO--56-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</p>

<p align="center">
<b>Helping farmers save water without expensive sensors.</b><br>
Built for the Smart Water Tank & Irrigation Scheduler Challenge.
</p>

---

## 📖 Table of Contents

- [🌍 Overview](#-overview)
- [🚨 Problem Statement](#-problem-statement)
- [💡 Key Innovations](#-key-innovations)
- [✨ Features](#-features)
- [🏗 System Architecture](#-system-architecture)
- [🛠 Technology Stack](#-technology-stack)
- [🚀 Quick Start](#-quick-start)
- [📂 Project Structure](#-project-structure)
- [✅ Testing](#-testing)
- [🎬 Demo Walkthrough](#-demo-walkthrough)
- [🔬 Scientific Basis](#-scientific-basis)
- [🗺 Future Roadmap](#-future-roadmap)
- [⚠ Scientific Disclaimer](#-scientific-disclaimer)
- [📄 License](#-license)

---

# 🌍 Overview

ARVA is an intelligent irrigation decision-support system that predicts root-zone soil water conditions and recommends **when** and **how much** to irrigate using internationally recognized **FAO-56 soil-water balance standards**.

Unlike sensor-dependent systems, ARVA delivers precise irrigation guidance using weather data, crop characteristics, soil properties, and tank capacity estimates without requiring costly hardware installations.

### Designed For

✅ Smallholder Farmers

✅ Community Gardens

✅ Rural Agriculture Cooperatives

✅ Water-Scarce Regions

✅ Sustainable Farming Initiatives

---

# 🚨 Problem Statement

Traditional irrigation systems commonly rely on fixed calendar schedules rather than actual crop water demand.

This leads to:

- Excessive water consumption
- Nutrient leaching
- Increased pumping costs
- Reservoir depletion
- Reduced agricultural sustainability

Physical sensor networks address some of these challenges but introduce additional costs, maintenance requirements, and connectivity dependencies.

**ARVA solves this problem by combining agronomic science with offline-first technology to provide intelligent irrigation recommendations without additional hardware.**

---

# 💡 Key Innovations

## 1️⃣ FAO-56 Water Balance Engine

Calculates:

- Reference Evapotranspiration (ET₀)
- Crop Water Requirement (ETc)
- Readily Available Water (RAW)
- Total Available Water (TAW)
- Effective Rainfall
- Deep Percolation Losses

### Formula

```text
ETc = ET₀ × Kc
```

---

## 2️⃣ Dual Offline Calculation Engines

### Frontend

```text
frontend/src/engine/irrigationEngine.js
```

### Backend

```text
backend/app/services/irrigation_engine.py
```

Both engines produce consistent irrigation recommendations, ensuring system resilience even during connectivity outages.

---

## 3️⃣ Explainable Recommendations

Every irrigation recommendation includes:

- Water deficit calculations
- Root zone depletion
- Effective rainfall contributions
- Triggered irrigation rules
- Tank availability checks

Users always understand *why* a recommendation was generated.

---

## 4️⃣ Water Savings Lab

Compare:

```text
Traditional Fixed Irrigation Schedule
                VS
ARVA Adaptive Scheduling Engine
```

Features:

- Rainy Week Simulation
- Dry Season Simulation
- Water Savings Estimation
- Side-by-Side Analytics

---

## 5️⃣ Emergency Water Allocation

When water reserves become critically low, ARVA:

- Prioritizes sensitive crop stages
- Protects flowering and fruiting crops
- Maintains minimum reserve levels
- Prevents over-allocation

---

# ✨ Features

| Feature | Description |
|----------|-------------|
| 🌦 Weather Integration | Forecast & historical weather analysis |
| 🌱 Smart Irrigation Scheduler | Adaptive water recommendations |
| 💧 Water Savings Lab | Compare smart vs fixed scheduling |
| 🚨 Emergency Mode | Intelligent water rationing |
| 📊 Analytics Dashboard | Visual farm performance insights |
| 🔍 Explainability Engine | Transparent recommendation logic |
| 📱 Responsive Design | Desktop, tablet, and mobile support |
| 📦 Offline PWA | Works without internet connection |
| 💾 IndexedDB Storage | Local-first data persistence |
| 🔄 Sync Queue | Automatic synchronization when online |

---

# 🏗 System Architecture

```text
                    Open-Meteo API
                           │
                           ▼

┌─────────────────────────────────────┐
│           FastAPI Backend           │
│    FAO-56 Water Balance Engine      │
└─────────────────┬───────────────────┘
                  │
                  ▼

┌─────────────────────────────────────┐
│           React Frontend            │
│      Smart Scheduler Interface      │
└─────────────────┬───────────────────┘
                  │
                  ▼

         IndexedDB Local Storage

                  │
                  ▼

            Offline PWA Mode
```

---

# 🛠 Technology Stack

## Frontend

- React 18
- Vite
- Tailwind CSS
- React Router DOM
- Recharts
- Lucide React

## Backend

- Python 3.13
- FastAPI
- SQLAlchemy 2.0
- Pydantic
- HTTPX

## Database

- MySQL 8+
- SQLite Fallback

## Offline Infrastructure

- IndexedDB (Dexie)
- Workbox Service Worker
- Progressive Web App Manifest

## External Services

- Open-Meteo Weather API

---

# 🚀 Quick Start

## Prerequisites

- Node.js v18+
- Python v3.10+
- Git

---

## Start Backend

```bash
cd backend

python -m pip install -r requirements.txt

python -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload
```

### Backend URLs

```text
API:
http://localhost:8000

Swagger:
http://localhost:8000/docs
```

---

## Start Frontend

```bash
cd frontend

npm install

npm run dev
```

### Frontend URL

```text
http://localhost:5173
```

---

## Optional MySQL Setup

```sql
CREATE DATABASE arva_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Import schema:

```bash
mysql -u root -p arva_db < database/schema.sql

mysql -u root -p arva_db < database/seed.sql
```

Configure:

```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/arva_db
```

> If MySQL is unavailable, ARVA automatically falls back to SQLite.

---

# 📂 Project Structure

```text
ARVA/
│
├── frontend/
│   ├── src/
│   │   ├── engine/
│   │   ├── pages/
│   │   ├── components/
│   │   └── services/
│   │
│   ├── public/
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── models/
│   │   └── tests/
│   │
│   └── requirements.txt
│
├── database/
│   ├── schema.sql
│   └── seed.sql
│
└── README.md
```

---

# ✅ Testing

## Frontend Tests

```bash
cd frontend

npm test
```

Validates:

- ETc calculations
- Rainfall infiltration
- Water balance logic
- Savings simulations
- Emergency rationing scenarios

---

## Backend Tests

```bash
cd backend

pytest app/tests
```

Validates:

- FAO-56 equations
- API endpoints
- Scheduler logic
- Edge-case handling

---

# 🎬 Demo Walkthrough

## 1. Farm Dashboard

Show:

- Current tank level
- Soil depletion
- Water demand
- Recommended actions

---

## 2. Explainability Engine

Open:

```text
Why ARVA Recommends This
```

Demonstrate:

- ET₀ calculations
- ETc estimation
- Root-zone depletion

---

## 3. Water Savings Lab

Navigate to:

```text
/savings-lab
```

Compare:

```text
Fixed Timer
vs
ARVA Smart Scheduling
```

Show projected water savings under rainfall scenarios.

---

## 4. Emergency Mode

Navigate to:

```text
/emergency
```

Reduce tank reserves and demonstrate intelligent crop prioritization.

---

## 5. Offline Mode

Navigate to:

```text
/offline
```

Demonstrate:

- Offline scheduling
- Local storage
- Sync queue processing

---

# 🔬 Scientific Basis

ARVA follows FAO Irrigation & Drainage Paper 56 guidelines.

### Core Formula

```text
ETc = ET₀ × Kc
```

Where:

- ET₀ = Reference Evapotranspiration
- Kc = Crop Coefficient
- ETc = Crop Water Requirement

Reference:

https://www.fao.org/land-water/databases-and-software/cropwat/en/

---

# 🗺 Future Roadmap

- IoT Sensor Integration
- Satellite Weather Layers
- SMS Advisory Alerts
- Offline pumps, valves, or irrigation infrastructure.
- Water savings calculations are simulation-based estimates.

---

# 📄 License

MIT License

Developed for the **Smart Water Tank and Irrigation Scheduler Challenge**.

Feel free to use, modify, and contribute.

---

# 👨‍💻 Team ARVA

### Predict. Prioritize. Preserve.

> Smarter irrigation today. More water tomorrow.

⭐ Star this repository if you find ARVA useful.
