# FAO-56 Soil Water Balance & Irrigation Model

**ARVA Agronomic Formulation & Calculation Reference**

---

## 1. Crop Water Demand ($ET_c$)

Crop evapotranspiration ($ET_c$) represents the daily water depth (mm/day) evaporated from the soil surface and transpired by the crop:

$$ET_c = ET_0 \times K_c$$

Where:
- $ET_0$: Reference evapotranspiration (mm/day) calculated via the FAO Penman-Monteith equation (retrieved from Open-Meteo).
- $K_c$: Crop coefficient reflecting crop canopy, height, and leaf area index.

### Growth-Stage Crop Coefficients ($K_c$)

| Crop | Category | $K_{c,\text{init}}$ | $K_{c,\text{mid}}$ | $K_{c,\text{end}}$ | Root Depth ($Z_r$) | Depletion ($p$) |
|---|---|---|---|---|---|---|
| **Tomato** | Vegetables | 0.60 | 1.15 | 0.80 | 0.70 m | 0.40 |
| **Sweet Corn** | Grain & Cereal | 0.30 | 1.20 | 0.60 | 1.00 m | 0.55 |
| **Bell Pepper** | Vegetables | 0.60 | 1.05 | 0.90 | 0.60 m | 0.30 |
| **Potato** | Tubers | 0.50 | 1.15 | 0.75 | 0.50 m | 0.35 |
| **Spinach** | Leafy Greens | 0.70 | 1.00 | 0.95 | 0.30 m | 0.20 |

*Source: FAO Irrigation and Drainage Paper No. 56, Table 12.*

---

## 2. Soil Water Storage Capacities

- **Total Available Water ($TAW$)**:
  $$TAW = 1000 \times (\theta_{FC} - \theta_{WP}) \times Z_r \quad (\text{mm})$$
- **Readily Available Water ($RAW$)**:
  $$RAW = p \times TAW \quad (\text{mm})$$
- **Critical Moisture Threshold ($\theta_{crit}$)**:
  $$\theta_{crit} = \theta_{FC} - p \times (\theta_{FC} - \theta_{WP}) \quad (\%)$$

When soil moisture drops below $\theta_{crit}$, the crop experiences moisture stress, triggering an **IRRIGATE** recommendation.

---

## 3. Effective Rainfall ($P_{eff}$)

Rainfall below 4.0 mm is assumed to be intercepted by vegetation or lost to rapid surface evaporation without penetrating the root zone:
- If $P \le 4.0$ mm $\implies P_{eff} = 0$.
- If $P > 4.0$ mm $\implies P_{eff} = \min\big((P - 4.0) \times 0.80, \, \text{Storage Deficit}\big)$.

---

## 4. Gross Tank Withdrawal

1 millimetre of water depth over 1 square metre equals exactly 1 Litre:

$$\text{Gross Litres} = \frac{I_{net} \text{ (mm)} \times \text{Area } (m^2)}{\eta_{irrigation}}$$

Where $\eta_{irrigation}$ is irrigation efficiency (default $0.85$ for precision drip systems).

---

## 5. Water Scarcity Triage Algorithm

When total farm demand exceeds available water ($V_{avail} = V_{tank} - V_{reserve}$):

1. **Calculate Zone Priority Score**:
   $$W_{priority} = (W_{crop} \times 0.40) + (S_{stage} \times 0.35) + \left(\frac{D_t}{RAW} \times 0.25\right) + \text{Override}$$
   - Flowering and fruit formation stages receive the highest stage sensitivity ($1.5\times$).
2. **Sort Zones Descending by $W_{priority}$**.
3. **Allocate Available Water Strictly Up to $V_{avail}$** (never allocating more water than available in the tank).
