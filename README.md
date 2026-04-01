<div align="center">
<div align="center">
    
<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=2,3,12&height=220&section=header&text=Nassau%20Candy%20Distributor&fontSize=42&fontColor=FFFFFF&fontAlignY=36&desc=Shipping%20Route%20Efficiency%20%26%20Lead%20Time%20Analytics&descAlignY=56&descSize=17&animation=fadeIn"/>


<br/>

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1.24-013243?style=for-the-badge&logo=numpy&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-1.11-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=for-the-badge&logo=jupyter&logoColor=white)

<br/>

> **A full-cycle supply chain analytics project for Nassau Candy Distributor — from raw messy data to statistically rigorous route efficiency rankings, bottleneck detection, and an interactive Streamlit dashboard.**

<br/>

[🔍 Problem Statement](#-problem-statement) &nbsp;·&nbsp; [🏗 Architecture](#-project-structure) &nbsp;·&nbsp; [🧹 Data Wrangling](#-data-wrangling--quality-fixes) &nbsp;·&nbsp; [📐 Methodology](#-analytical-methodology) &nbsp;·&nbsp; [📊 Key Findings](#-key-findings) &nbsp;·&nbsp; [🚀 Quick Start](#-quick-start)

</div>

---

## 🎯 Problem Statement

Nassau Candy Distributor ships confectionery products from **5 factories** across the US to customers in **4 regions** and **multiple states**, using **4 shipping modes**. The business needed answers to:

- Which **factory → region/state routes** are most and least efficient?
- Which **regions and states** are congestion-prone?
- Does paying for **expedited shipping** actually deliver faster?
- How do we make **statistically reliable** comparisons when some routes have only a handful of shipments?

---

## 🏗 Project Structure

```
NASSAU CANDY DISTRIBUTOR/
│
├── 📂 data/
│   ├── raw/
│   │   ├── Nassau Candy Distributor.csv   ← Main orders dataset
│   │   ├── factories.csv                  ← Factory locations & coordinates
│   │   └── products_factories.csv         ← Product–factory mapping
│   └── processed/
│       └── preprocessed_df.csv            ← Cleaned, merged, feature-enriched
│
├── 📂 notebook/
│   └── nassau_shipping.ipynb              ← Full analysis (227 cells)
│
└── app.py                                 ← Streamlit dashboard
```

---

## 🧹 Data Wrangling & Quality Fixes

This project had **significant real-world data messiness** — each issue was diagnosed, reasoned about, and fixed deliberately.

---

### 1. Duplicate `Order ID` Investigation

Duplicate order IDs were not blindly dropped. They were **investigated first**:

```python
# Each Order ID maps to exactly one product — confirmed via groupby
x = df.groupby(['Order ID']).agg(count=('Product Name', 'nunique')).reset_index()
(x['count'] > 1).sum()  # → 0 — no order has multiple products
```

**Root cause identified:** Same customer re-ordering the same product with a different quantity in the same session (cart updates). The fix was to **aggregate, not drop**:

```python
dframe = df.groupby('Order ID').agg(
    order_date           = ('Order Date',    'max'),
    ship_date            = ('Ship Date',     'max'),
    ship_mode            = ('Ship Mode',     'max'),
    customer_id          = ('Customer ID',   'max'),
    state_customer       = ('State/Province','max'),
    region_customer      = ('Region',        'max'),
    product_name         = ('Product Name',  'max'),
    sales                = ('Sales',         'sum'),   # ← aggregated
    units                = ('Units',         'sum'),   # ← aggregated
    ...
).reset_index()
```

---

### 2. Ship Date Corruption — Lead Time Fix ‼️

The `ship_date` column contained dates **years into the future** — a clear data corruption issue. After investigation:

```python
dframe['lead_time'].min(), dframe['lead_time'].max()
# → Raw values were inflated by ~100x
```

**Fix:** Lead times were corrected by dividing by 100 and rounding — capped at the realistic maximum of ~16 days (accounting for transfer logistics):

```python
dframe['lead_time'] = round(dframe['lead_time'] / 100).astype(int)
```

---

### 3. Text Standardisation Pipeline

A custom reusable function was built to clean all string columns consistently:

```python
def preprocessing_names(x):
    pattern = "[^a-zA-Z0-9 ]"
    val = re.sub(pattern, "", x).lower()   # remove special characters
    val = ' '.join(val.split())            # normalise whitespace
    return val

# Applied across: product_name, factory, city, state, region, country
for col in ['product_name', 'city_customer', 'state_customer', 'region_customer']:
    dframe[col] = dframe[col].apply(preprocessing_names)
```

---

### 4. Division Misclassification Fix

`fizzy lifting drinks` was labelled as `Other` in the products table — but produced by `Sugar Shack` and classified as `Sugar` in the main orders data. Fixed with a targeted correction:

```python
df_products.loc[df_products['product_name'] == 'fizzy lifting drinks', 'division'] = 'Sugar'
```

---

### 5. Three-Way Data Merge

The cleaned orders, products, and factories tables were merged into a single analytical dataset:

```python
# Step 1 — Orders + Products (on product_name + division)
dframe = dframe.merge(df_products, how='inner', on=['product_name', 'division'])

# Step 2 — Result + Factories (on factory name)
dframe = dframe.merge(df_factories, how='inner', on='factory')

preprocessed_df.to_csv("preprocessed_df.csv", index=False)
```

---

## 📐 Analytical Methodology

### Custom Statistical Utilities

Two bespoke functions were written for upper-bound confidence interval estimation:

```python
from scipy.stats import t

def t_upper_bound(mean, std, n, confidence=0.95):
    """For small samples — uses t-distribution (heavier tails, more conservative)"""
    df    = n - 1
    t_crit = t.ppf((1 + confidence) / 2, df)
    se    = std / np.sqrt(n)
    return mean + t_crit * se

def z_upper_bound(mean, std, n):
    """For larger samples — uses Z-distribution (CLT applies)"""
    return mean + (1.96 * (std / np.sqrt(n)))
```

A custom **percentile analysis utility** was also built to inform all threshold decisions:

```python
def q(x, arr):
    """Returns count above/below each percentile threshold"""
    n = len(x)
    qs = {}
    for i in arr:
        threshold = math.ceil(n * i)
        qs[f"{round(i*100)}%"] = [x[threshold], n - np.ceil(n*i), np.ceil(n*i)]
    return qs

# Used before every threshold decision — data-driven, not arbitrary
y = df['total_shipments'].sort_values().tolist()
q(y, [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
```

---

### Statistical Confidence Framework

> **The problem:** Small sample sizes make averages unreliable. A route with 3 shipments averaging 16 days could just be noise.

Every aggregation level has its own **data-driven threshold** set by inspecting the percentile distribution first:

| Analysis Level | Threshold | Percentile | Confidence Logic |
|---|---|---|---|
| Ship Mode × Region | 30 | ~30th | Z-bound if ≥ 30, T-bound otherwise |
| Ship Mode × State | 12 | ~40th | Z-bound if ≥ 30, T-bound if ≥ 10 |
| Factory → Region | 18 | ~20th | Z-bound if ≥ 30, T-bound otherwise |
| Factory → State | 16 | ~20th | Z-bound if ≥ 30, T-bound if ≥ 10 |
| Congestion (Region) | 35 | ~30th | Direct efficiency scoring |
| Congestion (State) | 34 | ~35th | Direct efficiency scoring |

**Upper bound** was used (not the mean) to reflect **worst-case scenario planning** — conservative and operationally sound:

```python
# Applied consistently across all aggregation levels
df['avg_lead_time'] = df.apply(lambda x:
    round(z_upper_bound(x['avg_lead_time'], x['avg_lead_variability'], x['total_shipments']), 3)
    if x['confidence'] == 'good' else
    round(t_upper_bound(x['avg_lead_time'], x['avg_lead_variability'], x['total_shipments']), 3),
    axis=1
)
```

---

### Efficiency Score Engineering

A composite efficiency score combining **speed** and **consistency** — because a fast but unpredictable route is not truly efficient:

```python
# Normalise lead time to [0, 1]
df['norm_lead_time'] = round(
    (df['avg_lead_time'] - df['avg_lead_time'].min()) /
    (df['avg_lead_time'].max() - df['avg_lead_time'].min()), 3)

# Normalise variability to [0, 1]
df['norm_variability'] = round(
    (df['avg_lead_variability'] - df['avg_lead_variability'].min()) /
    (df['avg_lead_variability'].max() - df['avg_lead_variability'].min()), 3)

# Equal-weight composite — lower = more efficient
df['efficiency_score'] = (0.5 * df['norm_lead_time']) + (0.5 * df['norm_variability'])
```

---

### Analysis Dimensions

The analysis was structured across **6 dimensions** — each at two granularities:

```
1. Factory Performance Overview
2. Ship Mode Performance Overview
3. Ship Mode × Factory
4. Ship Mode × Region   ─── }  Best ship method per area
5. Ship Mode × State    ─── }
6. Factory → Region     ─── }  Best route per destination
7. Factory → State      ─── }
8. Congestion Analysis (Region + State)
9. Expedited vs Standard Shipping Comparison
```

---

## 📊 Key Findings

### 🏆 Most Efficient Routes (Factory → Region)

```python
factory_region_grouped.sort_values('efficiency_score', ascending=False)[:10]
```

Best routes combined low average lead time **and** low variability — showing that the most efficient routes are also the most **predictable**.

---

### 🚨 Bottleneck Routes

```python
bottleneck_regions = least_efficient_routes[
    least_efficient_routes['total_shipments'] >= 35   # high volume = real problem
].reset_index(drop=True)
```

Routes were flagged as bottlenecks only when they had **both** poor efficiency scores **and** sufficient volume — preventing noise from driving conclusions.

---

### 🌍 Congestion-Prone Regions

```python
congested_prone_regions.sort_values('efficiency_score', ascending=True).style.apply(
    lambda x: ['background-color: lightblue']*len(x) if x['efficiency_score'] <= 0.2 else ['']*len(x),
    axis=1
)
```

Regions with efficiency score ≤ 0.20 were highlighted as congestion-prone — combining high lead times with high unpredictability.

---

### ✈️ Expedited vs Standard Shipping

```python
shipping['shipping_category'] = shipping['ship_mode'].apply(
    lambda x: 'Expedited Shipping' if x in ('First Class', 'Same Day') else 'Standard Shipping'
)

shipping_grouped = shipping.groupby('shipping_category').agg(
    total_shipments      = ('total_shipments', 'sum'),
    avg_lead_time        = ('avg_lead_time',   'mean'),   # ← mean of means
    avg_lead_variability = ('avg_lead_variability', 'mean'),
)
```

Compared side-by-side to determine whether premium shipping modes actually deliver meaningfully better lead times across the distribution network.

---

## 🛠 Tech Stack

<div align="center">

| Layer | Tools |
|---|---|
| **Language** | Python 3.11 |
| **Data Manipulation** | Pandas, NumPy |
| **Statistical Analysis** | SciPy (`t.ppf`), custom Z/T bound functions |
| **Visualisation** | Plotly, Streamlit |
| **Environment** | Jupyter Notebook, VS Code |
| **Data Format** | CSV (raw + processed) |

</div>

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/yourusername/nassau-candy-shipping.git
cd nassau-candy-shipping

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the notebook
jupyter notebook notebook/nassau_shipping.ipynb

# 4. Launch the dashboard
streamlit run app.py
```

**Requirements:**
```
pandas>=2.0
numpy>=1.24
scipy>=1.11
plotly>=5.0
streamlit>=1.28
```

---

## 💡 What Makes This Project Stand Out

```
✅ Real data problems — corrupted dates, cart-update duplicates, misclassified divisions
✅ Every threshold is data-driven — q() utility used before every filter decision
✅ Statistically rigorous — Z vs T bounds selected by sample size, not hardcoded
✅ Upper bound CI — worst-case planning, not optimistic averages
✅ Composite efficiency score — speed + consistency, not just speed
✅ Six analysis dimensions — factory, ship mode, region, state, routes, congestion
✅ Production dashboard — fully interactive Streamlit app with live filters
```

---

## 👤 Author

<div align="center">

**Faheem Bhat**
*Data Analyst · Supply Chain · Python*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/faheemb)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/faheem-afk)
[![Portfolio](https://img.shields.io/badge/Portfolio-View-1E40AF?style=for-the-badge&logo=firefox&logoColor=white)](https://faheem-afk.github.io)

</div>

---

<div align="center">
<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=2,3,12&height=100&section=footer&animation=fadeIn"/>

*If this resonates, drop a ⭐ and let's connect!*
</div>
