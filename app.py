import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import t

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="ShipPulse — Supply Chain Analytics",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

COLORS = {
    "bg":       "#F8F9FB",
    "card":     "#FFFFFF",
    "border":   "#E5E7EB",
    "text":     "#111827",
    "text2":    "#6B7280",
    "text3":    "#9CA3AF",
    "accent":   "#6366F1",
    "accent2":  "#4F46E5",
    "success":  "#10B981",
    "warning":  "#F59E0B",
    "danger":   "#EF4444",
}

CHART_COLORS = ["#6366F1", "#8B5CF6", "#06B6D4", "#10B981", "#F59E0B", "#EC4899",
                "#3B82F6", "#14B8A6", "#F97316", "#A855F7"]

_BASE_LAYOUT = dict(
    font=dict(family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", color="#374151", size=12),
    title_font=dict(size=15, color="#111827", family="Inter, sans-serif"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=True, gridcolor="#F3F4F6", gridwidth=1, linecolor="#E5E7EB",
               tickfont=dict(size=11, color="#6B7280"), title_font=dict(size=12, color="#6B7280"),
               zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="#F3F4F6", gridwidth=1, linecolor="#E5E7EB",
               tickfont=dict(size=11, color="#6B7280"), title_font=dict(size=12, color="#6B7280"),
               zeroline=False),
    legend=dict(font=dict(size=11, color="#6B7280"), bgcolor="rgba(0,0,0,0)", borderwidth=0),
    margin=dict(l=40, r=24, t=56, b=40),
    hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="#E5E7EB",
                    font=dict(family="Inter, sans-serif", size=12, color="#111827")),
    colorway=CHART_COLORS,
)

import copy
def _deep_merge(base, overrides):
    result = copy.deepcopy(base)
    for k, v in overrides.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result

def styled_layout(**overrides):
    return _deep_merge(_BASE_LAYOUT, overrides)

# ══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── hide streamlit chrome ── */
    #MainMenu, header, footer, .stDeployButton,
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"] { display: none !important; }

    /* ── global ── */
    .stApp {
        background-color: #F8F9FB;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .main .block-container {
        padding: 2rem 2.5rem 3rem 2.5rem;
        max-width: 1380px;
    }

    /* ── typography ── */
    h1 { color: #111827; font-weight: 800; font-size: 1.7rem; letter-spacing: -0.035em; margin-bottom: 0; }
    h2 { color: #111827; font-weight: 700; font-size: 1.25rem; letter-spacing: -0.02em; }
    h3 { color: #374151; font-weight: 600; font-size: 1.05rem; }
    p, li, span, div, label { font-family: 'Inter', sans-serif; }
    .caption-text { color: #9CA3AF; font-size: 0.82rem; font-weight: 400; margin-top: 2px; }

    /* ── metric cards ── */
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E8EAF0;
        border-radius: 14px;
        padding: 1.15rem 1.35rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.03), 0 1px 2px rgba(0,0,0,0.02);
        transition: all 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        box-shadow: 0 4px 16px rgba(99,102,241,0.08);
        border-color: #C7D2FE;
    }
    div[data-testid="stMetric"] label {
        color: #6B7280 !important;
        font-weight: 600 !important;
        font-size: 0.72rem !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #111827 !important;
        font-weight: 700 !important;
        font-size: 1.55rem !important;
    }

    /* ── sidebar ── */
    section[data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E8EAF0;
    }
    section[data-testid="stSidebar"] h1 {
        font-size: 1.15rem;
        font-weight: 700;
        color: #6366F1;
        letter-spacing: -0.02em;
    }
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stDateInput label,
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stSelectbox label {
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #6B7280 !important;
    }

    /* ── tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 2px solid #F3F4F6;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.85rem;
        color: #9CA3AF;
        padding: 0.65rem 1.25rem;
        border-radius: 0;
        border-bottom: 2px solid transparent;
        margin-bottom: -2px;
        transition: all 0.15s ease;
    }
    .stTabs [data-baseweb="tab"]:hover { color: #6366F1; }
    .stTabs [aria-selected="true"] {
        color: #6366F1 !important;
        border-bottom: 2px solid #6366F1 !important;
        background: transparent !important;
    }

    /* ── charts in cards ── */
    .stPlotlyChart {
        background: #FFFFFF;
        border: 1px solid #E8EAF0;
        border-radius: 14px;
        padding: 0.6rem 0.4rem 0.2rem 0.4rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
    }

    /* ── dataframes ── */
    .stDataFrame {
        border: 1px solid #E8EAF0;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
    }

    /* ── radio/input styling ── */
    .stRadio > div { gap: 0.35rem; }
    .stRadio label span { font-weight: 500; font-size: 0.88rem; }

    /* ── divider ── */
    hr { border: none; border-top: 1.5px solid #F3F4F6; margin: 1.5rem 0; }

    /* ── expander ── */
    [data-testid="stExpanderHeader"], .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 0.9rem;
        color: #374151;
    }

    /* ── slider ── */
    .stSlider [data-baseweb="slider"] div[role="slider"] {
        background: #6366F1;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def t_upper_bound(mean, std, n, confidence=0.95):
    df_t = n - 1
    t_crit = t.ppf((1 + confidence) / 2, df_t)
    se = std / np.sqrt(n)
    return mean + t_crit * se

def z_upper_bound(mean, std, n):
    return mean + (1.96 * (std / np.sqrt(n)))

def _apply_ci(row):
    if pd.isna(row['avg_lead_variability']) or row['avg_lead_variability'] == 0:
        return row['avg_lead_time']
    if row['confidence'] == 'good':
        return round(z_upper_bound(row['avg_lead_time'], row['avg_lead_variability'], row['total_shipments']), 3)
    return round(t_upper_bound(row['avg_lead_time'], row['avg_lead_variability'], row['total_shipments']), 3)

def _norm(series):
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(0.0, index=series.index)
    return round((series - mn) / (mx - mn), 3)

def _confidence_col(s):
    return s.apply(lambda x: 'good' if x >= 30 else 'medium' if x >= 20 else 'weak')

def _efficiency(df):
    return round(1 - (0.5 * df['norm_lead_time'] + 0.5 * df['norm_variability']), 3)

def average_lead_time_by_route(preprocessed_df, area):
    threshold = 0.6 if area == 'state' else 0.2
    grouped = preprocessed_df.groupby(['factory', f'{area}_customer']).agg(
        total_shipments=('Order ID', 'count'),
        avg_lead_time=('lead_time', lambda x: round(x.mean(), 3)),
        avg_lead_variability=('lead_time', lambda x: round(x.std(), 3)),
    ).reset_index()
    route_col = f'factory → {area}(customers)'
    grouped.insert(0, route_col, grouped['factory'] + " → " + grouped[f'{area}_customer'])
    grouped.drop(columns=['factory', f'{area}_customer'], inplace=True)
    threshold_value = grouped['total_shipments'].quantile(threshold)
    grouped = grouped[grouped['total_shipments'] >= threshold_value].copy()
    grouped['confidence'] = _confidence_col(grouped['total_shipments'])
    grouped['avg_lead_time'] = grouped.apply(_apply_ci, axis=1)
    grouped['norm_lead_time'] = _norm(grouped['avg_lead_time'])
    grouped['norm_variability'] = _norm(grouped['avg_lead_variability'].fillna(0))
    grouped['efficiency_score'] = _efficiency(grouped)
    return grouped.sort_values('efficiency_score', ascending=False).reset_index(drop=True)

def overall_factory_performance(preprocessed_df):
    return preprocessed_df.groupby('factory').agg(
        total_shipments=('Order ID', 'count'),
        avg_lead_time=('lead_time', 'mean'),
        avg_lead_time_variability=('lead_time', 'std'),
        total_gross_profit=('gross_profit', 'sum'),
        total_cost=('cost', 'sum'),
    ).sort_values('total_gross_profit', ascending=False).reset_index()

def overall_shipping_performance(preprocessed_df):
    return preprocessed_df.groupby('ship_mode').agg(
        total_shipments=('Order ID', 'count'),
        avg_lead_time=('lead_time', lambda x: round(x.mean(), 3)),
        avg_lead_variability=('lead_time', lambda x: round(x.std(), 3)),
    ).sort_values('avg_lead_time', ascending=False).reset_index()

def shipping_across_area(preprocessed_df, area):
    grouped = preprocessed_df.groupby(['ship_mode', f'{area}_customer']).agg(
        total_shipments=('Order ID', 'count'),
        avg_lead_time=('lead_time', lambda x: round(x.mean(), 3)),
        avg_lead_variability=('lead_time', lambda x: round(x.std(), 3)),
    ).reset_index()
    if area == 'state':
        threshold_value = grouped['total_shipments'].quantile(0.45)
        grouped = grouped[grouped['total_shipments'] >= threshold_value].copy()
    grouped['confidence'] = _confidence_col(grouped['total_shipments'])
    grouped['avg_lead_time'] = grouped.apply(_apply_ci, axis=1)
    grouped['norm_lead_time'] = _norm(grouped['avg_lead_time'])
    grouped['norm_variability'] = _norm(grouped['avg_lead_variability'].fillna(0))
    grouped['efficiency_score'] = _efficiency(grouped)
    return grouped.sort_values('efficiency_score', ascending=False).reset_index(drop=True)

def shipping_across_factories(preprocessed_df):
    sf = preprocessed_df.groupby(['ship_mode', 'factory']).agg(
        total_shipments=('Order ID', 'count'),
        avg_lead_time=('lead_time', lambda x: round(x.mean(), 3)),
        avg_lead_variability=('lead_time', lambda x: round(x.std(), 3)),
    ).reset_index()
    sf = sf[sf['total_shipments'] > 11].copy()
    sf['confidence'] = _confidence_col(sf['total_shipments'])
    sf['avg_lead_time'] = sf.apply(_apply_ci, axis=1)
    sf['norm_lead_time'] = _norm(sf['avg_lead_time'])
    sf['norm_variability'] = _norm(sf['avg_lead_variability'].fillna(0))
    sf['efficiency_score'] = _efficiency(sf)
    return sf.sort_values('factory').reset_index(drop=True)

# ── state name → 2-letter code ────────────────────────────────────────────────

STATE_MAP = {
    'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
    'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
    'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
    'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
    'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
    'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
    'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
    'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
    'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
    'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
    'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
    'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
    'wisconsin': 'WI', 'wyoming': 'WY', 'district of columbia': 'DC',
}

# ══════════════════════════════════════════════════════════════════════════════
# DATA
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/preprocessed_df.csv")
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['ship_date'] = pd.to_datetime(df['ship_date'])
    return df

df = load_data()

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
            <div style="width:32px;height:32px;background:linear-gradient(135deg,#6366F1,#8B5CF6);
                        border-radius:8px;display:flex;align-items:center;justify-content:center;">
                <span style="color:#fff;font-size:16px;font-weight:800;">◆</span>
            </div>
            <span style="font-size:1.1rem;font-weight:800;color:#111827;letter-spacing:-0.03em;">ShipPulse</span>
        </div>
    """, unsafe_allow_html=True)
    st.caption("Supply Chain Analytics")
    st.markdown("---")

    min_date = df['order_date'].min().date()
    max_date = df['order_date'].max().date()
    date_range = st.date_input("Date Range", value=(min_date, max_date),
                               min_value=min_date, max_value=max_date)

    all_regions = sorted(df['region_customer'].dropna().unique())
    selected_regions = st.multiselect("Region", options=all_regions, default=all_regions)

    all_ship_modes = sorted(df['ship_mode'].dropna().unique())
    selected_ship_modes = st.multiselect("Ship Mode", options=all_ship_modes, default=all_ship_modes)

    all_states = sorted(df['state_customer'].dropna().unique())
    selected_states = st.multiselect("State / Province", options=all_states)

    max_lead = int(df['lead_time'].max())
    lead_threshold = st.slider(
        "Lead-Time Threshold (days)",
        min_value=int(df['lead_time'].min()),
        max_value=max_lead,
        value=int(df['lead_time'].quantile(0.50)),
        help="Shipments exceeding this are flagged as delayed",
    )

# ══════════════════════════════════════════════════════════════════════════════
# APPLY FILTERS
# ══════════════════════════════════════════════════════════════════════════════

filtered = df.copy()
if len(date_range) == 2:
    filtered = filtered[(filtered['order_date'].dt.date >= date_range[0]) &
                        (filtered['order_date'].dt.date <= date_range[1])]
if selected_regions:
    filtered = filtered[filtered['region_customer'].isin(selected_regions)]
if selected_ship_modes:
    filtered = filtered[filtered['ship_mode'].isin(selected_ship_modes)]
if selected_states:
    filtered = filtered[filtered['state_customer'].isin(selected_states)]

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
    <div style="margin-bottom:0.3rem;">
        <h1 style="margin:0;">Supply Chain Shipping Dashboard</h1>
        <p class="caption-text">Real-time logistics performance monitoring across factories, routes & regions</p>
    </div>
""", unsafe_allow_html=True)

date_str = f"{date_range[0].strftime('%b %d, %Y')} – {date_range[1].strftime('%b %d, %Y')}" if len(date_range) == 2 else "–"
st.markdown(f"""
    <div style="display:inline-flex;align-items:center;gap:8px;background:#EEF2FF;
                padding:6px 14px;border-radius:20px;margin-bottom:1rem;">
        <span style="font-size:0.78rem;font-weight:600;color:#6366F1;">
            {len(filtered):,} orders</span>
        <span style="color:#C7D2FE;">|</span>
        <span style="font-size:0.78rem;font-weight:500;color:#818CF8;">{date_str}</span>
    </div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# KPI ROW
# ══════════════════════════════════════════════════════════════════════════════

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Shipments", f"{len(filtered):,}")
k2.metric("Avg Lead Time", f"{filtered['lead_time'].mean():.1f} days")
delay_pct = (filtered['lead_time'] > lead_threshold).mean() * 100
k3.metric("Delay Frequency", f"{delay_pct:.1f}%")
k4.metric("Gross Profit", f"${filtered['gross_profit'].sum():,.0f}")
k5.metric("Total Cost", f"${filtered['cost'].sum():,.0f}")

st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4 = st.tabs([
    "⬡  Route Efficiency",
    "◎  Geographic Map",
    "⇄  Ship Mode Comparison",
    "⊞  Route Drill-Down",
])

# ──────────────────────────────────────────────────────────────────────────────
# TAB 1 — ROUTE EFFICIENCY
# ──────────────────────────────────────────────────────────────────────────────

with tab1:
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    area_choice = st.radio("Group by", ["region", "state"], horizontal=True, key="route_area")

    try:
        route_df = average_lead_time_by_route(filtered, area_choice)
    except Exception:
        st.warning("Not enough data with the current filters.")
        st.stop()

    route_col = f'factory → {area_choice}(customers)'
    top_n = min(20, len(route_df))

    col_chart, col_table = st.columns([1.4, 1], gap="medium")

    with col_chart:
        chart_df = route_df.head(top_n).sort_values('efficiency_score', ascending=True)
        fig = px.bar(
            chart_df, x='efficiency_score', y=route_col, orientation='h',
            color='efficiency_score', color_continuous_scale=["#FCA5A5", "#FDE68A", "#6EE7B7", "#6366F1"],
            labels={'efficiency_score': 'Efficiency Score', route_col: ''},
            title=f"Top {top_n} Routes — Efficiency Score",
        )
        fig.update_layout(**styled_layout(
            height=520, coloraxis_showscale=False,
            yaxis=dict(tickfont=dict(size=10.5, color="#374151"))))
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True, theme=None)

    with col_table:
        st.markdown(f"""
            <div style="font-size:0.78rem;font-weight:600;text-transform:uppercase;
                        letter-spacing:0.06em;color:#6B7280;margin-bottom:8px;">
                Route Leaderboard — Top {top_n}
            </div>
        """, unsafe_allow_html=True)
        display_cols = [route_col, 'total_shipments', 'avg_lead_time',
                        'avg_lead_variability', 'efficiency_score', 'confidence']
        st.dataframe(
            route_df[display_cols].head(top_n).style
                .background_gradient(subset=['efficiency_score'], cmap='RdYlGn', vmin=0, vmax=1)
                .format({'avg_lead_time': '{:.1f}', 'avg_lead_variability': '{:.2f}',
                         'efficiency_score': '{:.3f}'}),
            use_container_width=True, height=520,
        )

# ──────────────────────────────────────────────────────────────────────────────
# TAB 2 — GEOGRAPHIC MAP
# ──────────────────────────────────────────────────────────────────────────────

with tab2:
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    geo_metric = st.radio(
        "Map metric",
        ["avg_lead_time", "delay_frequency", "efficiency_score"],
        format_func=lambda x: {"avg_lead_time": "Avg Lead Time",
                                "delay_frequency": "Delay Frequency (%)",
                                "efficiency_score": "Efficiency Score"}[x],
        horizontal=True, key="geo_radio",
    )

    us_df = filtered[filtered['country_customer'].str.lower() == 'united states']

    if us_df.empty:
        st.info("No US customer data with current filters.")
    else:
        state_agg = us_df.groupby('state_customer').agg(
            total_shipments=('Order ID', 'count'),
            avg_lead_time=('lead_time', 'mean'),
            delay_frequency=('lead_time', lambda x: round((x > lead_threshold).mean() * 100, 1)),
        ).reset_index()

        mn, mx = state_agg['avg_lead_time'].min(), state_agg['avg_lead_time'].max()
        state_agg['efficiency_score'] = round(1 - (state_agg['avg_lead_time'] - mn) / (mx - mn), 3) if mx > mn else 1.0
        state_agg['state_code'] = state_agg['state_customer'].str.lower().map(STATE_MAP)
        state_agg = state_agg.dropna(subset=['state_code'])

        cscale = {"avg_lead_time": [[0, "#EEF2FF"], [0.5, "#A5B4FC"], [1, "#4338CA"]],
                  "delay_frequency": [[0, "#FFF7ED"], [0.5, "#FDBA74"], [1, "#C2410C"]],
                  "efficiency_score": [[0, "#FEE2E2"], [0.5, "#FDE68A"], [1, "#6366F1"]]}
        clabel = {"avg_lead_time": "Lead Time (days)", "delay_frequency": "Delay %",
                  "efficiency_score": "Efficiency"}

        fig_map = px.choropleth(
            state_agg, locations='state_code', locationmode='USA-states',
            color=geo_metric, scope='usa',
            color_continuous_scale=cscale[geo_metric],
            hover_data={'state_code': False, 'state_customer': True,
                        'total_shipments': True, 'avg_lead_time': ':.1f', 'delay_frequency': ':.1f'},
            labels={geo_metric: clabel[geo_metric]},
        )
        fig_map.update_layout(**styled_layout(
            height=480,
            title=dict(text=f"US Shipping Performance — {clabel[geo_metric]}",
                       font=dict(size=15, color="#111827", family="Inter, sans-serif")),
            geo=dict(bgcolor="rgba(0,0,0,0)", lakecolor="#F8F9FB",
                     landcolor="#F8F9FB", subunitcolor="#E5E7EB"),
            coloraxis_colorbar=dict(title=dict(text=clabel[geo_metric], font=dict(size=11)),
                                     tickfont=dict(size=10), len=0.5, thickness=14),
        ))
        st.plotly_chart(fig_map, use_container_width=True, theme=None)

    # Regional bottleneck
    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    st.markdown("""
        <div style="font-size:0.78rem;font-weight:600;text-transform:uppercase;
                    letter-spacing:0.06em;color:#6B7280;margin-bottom:4px;">
            Regional Bottleneck Analysis
        </div>
    """, unsafe_allow_html=True)

    region_agg = filtered.groupby('region_customer').agg(
        avg_lead_time=('lead_time', 'mean'),
        total_shipments=('Order ID', 'count'),
        delay_pct=('lead_time', lambda x: round((x > lead_threshold).mean() * 100, 1)),
    ).reset_index().sort_values('avg_lead_time', ascending=False)

    fig_region = go.Figure()
    fig_region.add_trace(go.Bar(
        x=region_agg['region_customer'], y=region_agg['avg_lead_time'],
        marker=dict(color=region_agg['delay_pct'],
                    colorscale=[[0, "#C7D2FE"], [1, "#4338CA"]],
                    showscale=True, cornerradius=6,
                    colorbar=dict(title="Delay %", tickfont=dict(size=10), len=0.5, thickness=14)),
        text=[f"{v:.1f}d" for v in region_agg['avg_lead_time']],
        textposition='outside', textfont=dict(size=11, color="#374151", family="Inter"),
        hovertemplate="<b>%{x}</b><br>Lead Time: %{y:.1f}d<br>Delay: %{marker.color:.1f}%<extra></extra>",
    ))
    fig_region.update_layout(**styled_layout(
        height=360, showlegend=False,
        title=dict(text="Avg Lead Time & Delay Rate by Region"),
        yaxis=dict(title=dict(text="Avg Lead Time (days)")),
        xaxis=dict(title=dict(text="")),
    ))
    st.plotly_chart(fig_region, use_container_width=True, theme=None)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 3 — SHIP MODE COMPARISON
# ──────────────────────────────────────────────────────────────────────────────

with tab3:
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    ship_perf = overall_shipping_performance(filtered)
    delay_by_mode = filtered.groupby('ship_mode')['lead_time'].apply(
        lambda x: round((x > lead_threshold).mean() * 100, 1),
    ).reset_index(name='delay_pct')
    ship_perf = ship_perf.merge(delay_by_mode, on='ship_mode', how='left')

    c1, c2 = st.columns([1.3, 1], gap="medium")

    with c1:
        fig_ship = go.Figure()
        colors_ship = ["#6366F1", "#8B5CF6", "#06B6D4", "#10B981"]
        for i, row in ship_perf.iterrows():
            fig_ship.add_trace(go.Bar(
                x=[row['ship_mode']], y=[row['avg_lead_time']],
                error_y=dict(type='data', array=[row['avg_lead_variability']], color="#D1D5DB", thickness=1.5),
                marker=dict(color=colors_ship[i % len(colors_ship)], cornerradius=6),
                text=f"{row['avg_lead_time']:.1f}d", textposition='outside',
                textfont=dict(size=11, color="#374151"), name=row['ship_mode'],
                showlegend=False,
                hovertemplate=f"<b>{row['ship_mode']}</b><br>Lead Time: {row['avg_lead_time']:.1f}d<br>"
                              f"Variability: ±{row['avg_lead_variability']:.2f}d<br>"
                              f"Delay Rate: {row['delay_pct']:.1f}%<extra></extra>",
            ))
        fig_ship.update_layout(**styled_layout(
            height=400, title="Lead Time by Shipping Method",
            yaxis=dict(title=dict(text="Avg Lead Time (days)")),
            xaxis=dict(title=dict(text="")),
        ))
        st.plotly_chart(fig_ship, use_container_width=True, theme=None)

    with c2:
        st.markdown("""
            <div style="font-size:0.78rem;font-weight:600;text-transform:uppercase;
                        letter-spacing:0.06em;color:#6B7280;margin-bottom:8px;">
                Ship Mode Summary
            </div>
        """, unsafe_allow_html=True)
        st.dataframe(
            ship_perf.style
                .background_gradient(subset=['delay_pct'], cmap='OrRd', vmin=0)
                .background_gradient(subset=['avg_lead_time'], cmap='Blues', vmin=ship_perf['avg_lead_time'].min())
                .format({'avg_lead_time': '{:.1f}', 'avg_lead_variability': '{:.2f}', 'delay_pct': '{:.1f}%'}),
            use_container_width=True, height=400,
        )

    # Heatmap
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    hm_col, eff_col = st.columns(2, gap="medium")

    with hm_col:
        try:
            sf_df = shipping_across_factories(filtered)
            pivot = sf_df.pivot_table(values='avg_lead_time', index='factory', columns='ship_mode')
            fig_heat = px.imshow(
                pivot, color_continuous_scale=[[0, "#EEF2FF"], [0.5, "#A5B4FC"], [1, "#4338CA"]],
                text_auto='.1f', aspect='auto',
                labels={'color': 'Lead Time (days)', 'x': 'Ship Mode', 'y': 'Factory'},
            )
            fig_heat.update_layout(**styled_layout(
                height=380, title="Ship Mode × Factory Heatmap",
                xaxis=dict(tickfont=dict(size=11, color="#6B7280"), side='bottom'),
                yaxis=dict(tickfont=dict(size=11, color="#6B7280")),
                coloraxis_colorbar=dict(len=0.6, thickness=14, tickfont=dict(size=10)),
            ))
            fig_heat.update_traces(textfont=dict(size=11, color="#374151"))
            st.plotly_chart(fig_heat, use_container_width=True, theme=None)
        except Exception:
            st.info("Not enough data for heatmap.")

    with eff_col:
        try:
            ship_region = shipping_across_area(filtered, 'region')
            fig_sr = px.bar(
                ship_region, x='region_customer', y='efficiency_score',
                color='ship_mode', barmode='group',
                color_discrete_sequence=CHART_COLORS,
                labels={'region_customer': 'Region', 'efficiency_score': 'Efficiency', 'ship_mode': 'Ship Mode'},
                title="Ship Mode Efficiency by Region",
            )
            fig_sr.update_layout(**styled_layout(
                height=380, legend=dict(orientation='h', y=-0.18, x=0.5, xanchor='center')))
            fig_sr.update_traces(marker_line_width=0, marker_cornerradius=4)
            st.plotly_chart(fig_sr, use_container_width=True, theme=None)
        except Exception:
            st.info("Not enough data.")

# ──────────────────────────────────────────────────────────────────────────────
# TAB 4 — ROUTE DRILL-DOWN
# ──────────────────────────────────────────────────────────────────────────────

with tab4:
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    col_sel1, col_sel2 = st.columns(2, gap="medium")
    with col_sel1:
        drill_state = st.selectbox("State / Province",
                                   sorted(filtered['state_customer'].dropna().unique()))
    with col_sel2:
        drill_factory = st.selectbox("Factory",
                                     ["All"] + sorted(filtered['factory'].dropna().unique()))

    sf = filtered[filtered['state_customer'] == drill_state].copy()
    if drill_factory != "All":
        sf = sf[sf['factory'] == drill_factory]

    if sf.empty:
        st.warning("No data for this combination.")
    else:
        # KPIs
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Shipments", f"{len(sf):,}")
        m2.metric("Avg Lead Time", f"{sf['lead_time'].mean():.1f} days")
        m3.metric("Delay Rate", f"{(sf['lead_time'] > lead_threshold).mean() * 100:.1f}%")
        m4.metric("Gross Profit", f"${sf['gross_profit'].sum():,.0f}")

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        dist_col, trend_col = st.columns(2, gap="medium")

        with dist_col:
            fig_hist = px.histogram(
                sf, x='lead_time', color='ship_mode', nbins=16, barmode='overlay', opacity=0.8,
                color_discrete_sequence=CHART_COLORS,
                labels={'lead_time': 'Lead Time (days)', 'ship_mode': 'Ship Mode'},
                title=f"Lead Time Distribution — {drill_state.title()}",
            )
            fig_hist.add_vline(x=lead_threshold, line_dash='dash', line_color="#EF4444", line_width=2,
                               annotation_text=f"Threshold ({lead_threshold}d)",
                               annotation_font=dict(size=11, color="#EF4444"),
                               annotation_position="top right")
            fig_hist.update_layout(**styled_layout(
                height=370, legend=dict(orientation='h', y=-0.2, x=0.5, xanchor='center')))

            fig_hist.update_traces(marker_line_width=0)
            st.plotly_chart(fig_hist, use_container_width=True, theme=None)

        with trend_col:
            trend = sf.set_index('order_date').resample('ME')['lead_time'].mean().dropna().reset_index()
            trend.columns = ['month', 'avg_lead_time']
            if len(trend) > 1:
                fig_trend = px.area(
                    trend, x='month', y='avg_lead_time',
                    labels={'month': '', 'avg_lead_time': 'Avg Lead Time (days)'},
                    title=f"Monthly Lead Time Trend — {drill_state.title()}",
                    color_discrete_sequence=["#6366F1"],
                )
                fig_trend.update_traces(line=dict(width=2.5), fillcolor="rgba(99,102,241,0.08)")
                fig_trend.update_layout(**styled_layout(height=370))
                st.plotly_chart(fig_trend, use_container_width=True, theme=None)
            else:
                st.info("Not enough monthly data for trend chart.")

        # Order-level table
        st.markdown("""
            <div style="font-size:0.78rem;font-weight:600;text-transform:uppercase;
                        letter-spacing:0.06em;color:#6B7280;margin:12px 0 8px 0;">
                Order-Level Shipment Timeline
            </div>
        """, unsafe_allow_html=True)
        timeline_cols = ['Order ID', 'order_date', 'ship_date', 'lead_time',
                         'ship_mode', 'factory', 'product_name', 'sales', 'gross_profit']
        st.dataframe(
            sf[timeline_cols].sort_values('order_date', ascending=False)
                .style.format({'sales': '${:,.2f}', 'gross_profit': '${:,.2f}', 'lead_time': '{:.0f}d'})
                .background_gradient(subset=['lead_time'], cmap='RdYlGn_r',
                                     vmin=sf['lead_time'].min(), vmax=sf['lead_time'].max()),
            use_container_width=True, height=420,
        )
