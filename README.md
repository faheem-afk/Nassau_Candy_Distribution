<div align="center">

<!-- HEADER BANNER -->
<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=1E40AF&height=200&section=header&text=Nassau%20Candy%20Distribution&fontSize=40&fontColor=FFFFFF&fontAlignY=38&desc=Shipping%20Intelligence%20%7C%20Route%20Efficiency%20%7C%20Lead%20Time%20Analytics&descAlignY=58&descSize=16&animation=fadeIn"/>

<!-- BADGES -->
![Python](https://img.shields.io/badge/Python-3.11-1E40AF?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.x-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Status](https://img.shields.io/badge/Status-Complete-16A34A?style=for-the-badge)
![Domain](https://img.shields.io/badge/Domain-Supply%20Chain-D97706?style=for-the-badge)

<br/>

> **End-to-end shipping analytics project for Nassau Candy Distribution — identifying route bottlenecks, measuring lead time efficiency, and surfacing actionable insights through a fully interactive Streamlit dashboard.**

<br/>

[📊 View Dashboard](#-dashboard-preview) · [🔍 Methodology](#-methodology) · [📈 Key Findings](#-key-findings) · [🚀 Getting Started](#-getting-started)

</div>

---

## 📌 Project Overview

Nassau Candy Distribution operates a multi-factory confectionery supply chain shipping across **US regions and states**. This project answers one core business question:

> **Which shipping routes are most efficient — and which ones are bleeding time and money?**

The analysis spans **8,549 shipments** across **5 factories**, **4 customer regions**, **20 states**, and **4 ship modes** — combining rigorous statistical methods with a production-grade interactive dashboard.

---

## 🏗️ Project Architecture

```
nassau-candy-shipping-analytics/
│
├── 📂 data/
│   ├── raw/                        # Original order data
│   └── processed/                  # Cleaned & feature-engineered datasets
│
├── 📂 notebooks/
│   ├── 01_eda.ipynb                # Exploratory Data Analysis
│   ├── 02_lead_time_analysis.ipynb # Lead time & variability deep dive
│   ├── 03_route_efficiency.ipynb   # Route scoring & bottleneck detection
│   └── 04_statistical_bounds.ipynb # Z/T confidence bounds analysis
│
├── 📂 src/
│   ├── preprocessing.py            # Data cleaning pipeline
│   ├── statistical_bounds.py       # Z-bound & T-bound functions
│   ├── route_scoring.py            # Efficiency score engine
│   └── kpi_engine.py              # KPI computation module
│
├── 📂 dashboard/
│   └── shipping_dashboard.py       # Full Streamlit dashboard
│
├── requirements.txt
└── README.md
```

---

## 🔬 Methodology

### 1️⃣ Data Preparation & Feature Engineering

Raw order data was cleaned and enriched with computed fields:

```python
# Shipping Lead Time
df['lead_time'] = (df['ship_date'] - df['order_date']).dt.days

# Net Revenue after discount
df['net_revenue'] = df['quantity'] * df['unit_price'] * (1 - df['discount'])

# Route definition at two granularities
df['route_region'] = df['factory'] + '  →  ' + df['region_customer']
df['route_state']  = df['factory'] + '  →  ' + df['state_customer']
```

---

### 2️⃣ Statistical Confidence Framework

A key challenge: **small sample sizes make averages unreliable.** This was handled by applying appropriate statistical bounds depending on sample size:

| Sample Size | Method | Why |
|---|---|---|
| **≥ 30 (region)** | Z-distribution | CLT applies — normal approximation valid |
| **≥ 20 (state)** | T-distribution | Small sample — heavier tails, more conservative |
| **< 20** | Flagged as `weak` | Excluded from bottleneck conclusions |

```python
# Confidence classification
def classify_confidence(n, threshold=30):
    return 'good' if n >= threshold else 'weak'

# Upper bound selection per row
df['upper_bound'] = df.apply(lambda x:
    round(z_upper_bound(x['avg_lead_time'], x['avg_lead_variability'], x['total_shipments']), 3)
    if x['confidence'] == 'good' else
    round(t_upper_bound(x['avg_lead_time'], x['avg_lead_variability'], x['total_shipments']), 3),
    axis=1
)
```

> **Why this matters:** A route with 8 shipments averaging 16.9 days looks alarming — but it's noise. Only `confidence = 'good'` routes were used for strategic conclusions.

---

### 3️⃣ Route Efficiency Scoring

Rather than ranking by lead time alone (which ignores reliability), a **normalised composite score** was computed:

```python
# Normalise both metrics to [0, 1] scale
df['norm_lead_time']    = (df['avg_lead_time'] - df['avg_lead_time'].min()) / \
                          (df['avg_lead_time'].max() - df['avg_lead_time'].min())

df['norm_variability']  = (df['avg_lead_variability'] - df['avg_lead_variability'].min()) / \
                          (df['avg_lead_variability'].max() - df['avg_lead_variability'].min())

# Equal-weight efficiency score — lower = better
df['efficiency_score']  = (0.5 * df['norm_lead_time']) + (0.5 * df['norm_variability'])
df.sort_values('efficiency_score')
```

> **Speed + Consistency = Efficiency.** A fast but unpredictable route creates customer disappointment and planning failures. This scoring penalises both.

---

### 4️⃣ Bottleneck Detection

Routes were flagged as bottlenecks using a dual-condition filter:

```python
bottleneck_threshold_lt  = df['avg_lead_time'].quantile(0.75)     # Top 25% slowest
bottleneck_threshold_var = df['avg_lead_variability'].quantile(0.75) # Top 25% most variable

bottlenecks = df[
    (df['avg_lead_time']        >= bottleneck_threshold_lt)  |
    (df['avg_lead_variability'] >= bottleneck_threshold_var) &
    (df['confidence'] == 'good')
]
```

---

## 📈 Key Findings

### 🚨 Bottleneck Routes (Good Confidence Only)

| Route | Avg Lead Time | Variability | Issue |
|---|---|---|---|
| Secret Factory → Gulf | 14.98d 🔴 | 2.90 🔴 | Slow **AND** unpredictable |
| Secret Factory → Interior | 14.54d 🟠 | 2.98 🔴 | Most variable route |
| Sugar Shack → Interior | 16.91d 🔴 | 2.19 🟡 | Slowest route (weak confidence) |

### ✅ Most Efficient Routes

| Route | Avg Lead Time | Variability | Efficiency Score |
|---|---|---|---|
| **The Other Factory → Atlantic** | 14.53d 🟢 | 2.46 🟢 | ⭐ Best overall |
| Secret Factory → Pacific | 14.35d 🟢 | 2.63 🟡 | Fastest, less consistent |
| The Other Factory → Pacific | 14.81d 🟡 | 2.43 🟢 | Most consistent |

### 🏭 Factory-Level Insight

> **Secret Factory is the systemic problem** — it appears across 4 routes and consistently produces the highest lead times and variability. The issue is factory-side, not destination-side. Fixing Secret Factory's dispatch process would improve 4 routes simultaneously.

### 🌍 Regional Congestion

| Region | Avg Lead Time | Variability | Risk Level |
|---|---|---|---|
| Gulf | 13.10 🟢 lowest | 2.52 🔴 highest | ⚠️ High — unpredictable |
| Interior | 13.22 🔴 highest | 2.49 🟠 | ⚠️ High — slow |
| Pacific | 13.20 🟠 | 2.51 🟠 | ⚠️ High — high volume pressure |
| Atlantic | 13.22 🔴 | 2.44 🟢 lowest | 🟡 Moderate |

---

## 📊 Dashboard Preview

The project includes a **fully interactive Streamlit dashboard** with 6 analytical modules:

| Module | What It Shows |
|---|---|
| 🎯 **KPI Cards** | Total shipments, avg lead time, delay frequency, efficiency score, net revenue |
| 📊 **Route Efficiency** | Sorted bar chart of avg lead time by route + performance leaderboard |
| 🗺️ **Geographic Map** | US choropleth — lead time & delay % by state |
| 📦 **Ship Mode Comparison** | Box plot distributions + factory × ship mode breakdown |
| 🔥 **Route Drill-Down** | Heatmap of route × ship mode + filterable performance table |
| 📈 **Timelines** | Monthly trend line + lead time distribution histogram |

**Sidebar filters:** Date range · Factory · Region/State toggle · Ship mode · Delay threshold slider · Division

```bash
# Launch dashboard
streamlit run dashboard/shipping_dashboard.py
```

---

## 🧠 Technical Highlights

```python
# ✅ Statistical rigour — Z vs T bounds based on sample size
# ✅ Noise filtering — weak confidence routes excluded from conclusions
# ✅ Composite efficiency scoring — not just speed, but speed + consistency
# ✅ Two-level route granularity — region (threshold: 30) and state (threshold: 20)
# ✅ Dynamic confidence tagging — good / weak per route
# ✅ KPI engine — delay frequency, route efficiency score, net revenue
```

**Key Python patterns used:**
- `groupby().agg()` with named aggregations
- `apply()` with conditional lambda for statistical bounds
- Min-max normalisation for composite scoring
- `isin()` for cross-dataframe validation
- `relativedelta` for accurate date arithmetic
- Dictionary-based dynamic groupby storage

---

## 🚀 Getting Started

### Prerequisites
```bash
Python 3.11+
```

### Installation
```bash
# Clone repo
git clone https://github.com/yourusername/nassau-candy-shipping-analytics.git
cd nassau-candy-shipping-analytics

# Install dependencies
pip install -r requirements.txt
```

### Requirements
```txt
pandas>=2.0
numpy>=1.24
plotly>=5.0
streamlit>=1.28
python-dateutil>=2.8
scipy>=1.11
```

### Run Analysis
```bash
# Run notebooks in order
jupyter notebook notebooks/

# Or launch dashboard directly
streamlit run dashboard/shipping_dashboard.py
```

---

## 📐 KPI Definitions

| KPI | Formula | Purpose |
|---|---|---|
| **Shipping Lead Time** | `Ship Date − Order Date` | Per-order duration |
| **Average Lead Time** | `mean(lead_time)` per route | Route speed benchmark |
| **Lead Time Variability** | `std(lead_time)` per route | Route reliability |
| **Delay Frequency** | `% shipments > threshold` | Operational risk signal |
| **Route Efficiency Score** | `0.5 × norm(lead_time) + 0.5 × norm(variability)` | Composite ranking |
| **Net Revenue** | `Quantity × Unit Price × (1 − Discount)` | True revenue per order |

---

## 🛠️ Tools & Stack

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-8CAAE6?style=flat-square&logo=scipy&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=flat-square&logo=jupyter&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white)

</div>

---

## 👤 Author

<div align="center">

**Your Name**
*Data Analyst · Supply Chain Analytics · Python*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/yourprofile)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/yourusername)
[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-1E40AF?style=for-the-badge&logo=firefox&logoColor=white)](https://yourportfolio.com)

</div>

---

<div align="center">

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=1E40AF&height=100&section=footer&animation=fadeIn"/>

*If this project resonates with you, feel free to ⭐ the repo and connect!*

</div>
