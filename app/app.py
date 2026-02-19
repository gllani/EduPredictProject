import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

FORECAST_PATH = Path("data/exports/forecast_output.csv")

st.set_page_config(
    page_title="EduPredict",
    page_icon="🎓",
    layout="wide",
)

# ── Load Data ──────────────────────────────────────────────────────────────────

@st.cache_data
def load_forecasts() -> pd.DataFrame:
    if not FORECAST_PATH.exists():
        st.error("Forecast data not found. Run `python src/models/predict.py` first.")
        st.stop()
    return pd.read_csv(FORECAST_PATH)


df = load_forecasts()

# ── Sidebar Controls ───────────────────────────────────────────────────────────

st.sidebar.title("🎓 EduPredict")
st.sidebar.markdown("Global Enrollment Forecasting System")
st.sidebar.divider()

regions = sorted(df["region"].dropna().unique())
selected_regions = st.sidebar.multiselect("Region", regions, default=regions[:2])

filtered_countries = df[df["region"].isin(selected_regions)]["country_name"].dropna().unique()
selected_country = st.sidebar.selectbox("Country", sorted(filtered_countries))

scenario = st.sidebar.selectbox(
    "Scenario",
    ["baseline", "optimistic", "pessimistic", "All Scenarios"],
)

horizon = st.sidebar.selectbox("Forecast Horizon (years)", [5, 10, 15], index=1)

# ── Filter ─────────────────────────────────────────────────────────────────────

view = df[(df["country_name"] == selected_country) & (df["horizon"] == horizon)]

# ── Header ─────────────────────────────────────────────────────────────────────

st.title(f"EduPredict — {selected_country}")
st.caption(f"Enrollment forecasts · {horizon}-year horizon · Source: UNESCO / World Bank")
st.divider()

# ── Forecast Chart ─────────────────────────────────────────────────────────────

fig = go.Figure()

COLORS = {
    "baseline":   {"line": "#2196F3", "fill": "rgba(33,150,243,0.10)"},
    "optimistic": {"line": "#4CAF50", "fill": "rgba(76,175,80,0.10)"},
    "pessimistic":{"line": "#F44336", "fill": "rgba(244,67,54,0.10)"},
}

scenarios_to_plot = (
    ["baseline", "optimistic", "pessimistic"]
    if scenario == "All Scenarios"
    else [scenario]
)

for s in scenarios_to_plot:
    s_data = view[view["scenario"] == s].sort_values("forecast_year")
    if s_data.empty:
        continue
    line_color = COLORS[s]["line"]
    fill_color = COLORS[s]["fill"]

    fig.add_trace(go.Scatter(
        x=s_data["forecast_year"],
        y=s_data["predicted_enrollment"],
        mode="lines+markers",
        name=s.capitalize(),
        line=dict(color=line_color, width=2.5),
    ))

    fig.add_trace(go.Scatter(
        x=pd.concat([s_data["forecast_year"], s_data["forecast_year"].iloc[::-1]]),
        y=pd.concat([s_data["upper_bound"], s_data["lower_bound"].iloc[::-1]]),
        fill="toself",
        fillcolor=fill_color,
        line=dict(color="rgba(255,255,255,0)"),
        showlegend=False,
        name=f"{s} CI",
    ))

fig.update_layout(
    title=f"Enrollment Forecast — {selected_country} ({horizon}-year horizon)",
    xaxis_title="Year",
    yaxis_title="Total Enrollment",
    legend_title="Scenario",
    hovermode="x unified",
    height=450,
    margin=dict(l=40, r=40, t=60, b=40),
)

st.plotly_chart(fig, use_container_width=True)

# ── Summary Table ──────────────────────────────────────────────────────────────

st.subheader(" Forecast Summary Table")

if scenario == "All Scenarios":
    table_data = view[["forecast_year", "scenario", "predicted_enrollment", "lower_bound", "upper_bound"]]
else:
    table_data = view[view["scenario"] == scenario][
        ["forecast_year", "predicted_enrollment", "lower_bound", "upper_bound"]
    ]

table_data = table_data.sort_values("forecast_year")
table_data.columns = [c.replace("_", " ").title() for c in table_data.columns]

for col in ["Predicted Enrollment", "Lower Bound", "Upper Bound"]:
    if col in table_data.columns:
        table_data[col] = table_data[col].apply(lambda x: f"{x:,.0f}")

st.dataframe(table_data, use_container_width=True, hide_index=True)

# ── Export ─────────────────────────────────────────────────────────────────────

st.divider()
csv = view.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇ Download Forecast CSV",
    data=csv,
    file_name=f"edupredict_{selected_country.replace(' ', '_')}_{horizon}yr.csv",
    mime="text/csv",
)

# ── Footer ─────────────────────────────────────────────────────────────────────

st.caption("EduPredict SP26 Capstone · Forecasts are indicative projections, not guarantees.")
