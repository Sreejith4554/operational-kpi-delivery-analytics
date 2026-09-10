from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
portfolio = pd.read_csv(ROOT / "data" / "portfolio_delivery.csv", parse_dates=["start_date", "baseline_finish", "forecast_finish"])
raid = pd.read_csv(ROOT / "data" / "raid.csv", parse_dates=["due_date"])
resources = pd.read_csv(ROOT / "data" / "resources.csv")

portfolio["variance_days"] = (portfolio["forecast_finish"] - portfolio["baseline_finish"]).dt.days
portfolio["budget_variance_pct"] = ((portfolio["actual_cost"] - portfolio["planned_cost"]) / portfolio["planned_cost"] * 100).round(1)
portfolio["delivery_ratio"] = (portfolio["completed_deliverables"] / portfolio["planned_deliverables"] * 100).round(1)

st.set_page_config(page_title="Operational Delivery Analytics", layout="wide")
st.title("Operational KPI & Delivery Analytics")
st.caption("Synthetic portfolio case study — designed for recruiter and interview demonstration")

region = st.sidebar.multiselect("Region", sorted(portfolio["region"].unique()), default=sorted(portfolio["region"].unique()))
workstream = st.sidebar.multiselect("Workstream", sorted(portfolio["workstream"].unique()), default=sorted(portfolio["workstream"].unique()))
filtered = portfolio[portfolio["region"].isin(region) & portfolio["workstream"].isin(workstream)].copy()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Projects", len(filtered))
c2.metric("Red projects", int((filtered["rag_status"] == "Red").sum()))
c3.metric("Avg. forecast variance", f"{filtered['variance_days'].mean():.1f} days" if len(filtered) else "—")
c4.metric("Open High/Critical RAID", int(len(raid[(raid["status"] == "Open") & (raid["severity"].isin(["High", "Critical"]))])))

st.subheader("Forecast variance by project")
fig = px.bar(filtered.sort_values("variance_days"), x="variance_days", y="project_name", orientation="h", hover_data=["rag_status", "completion_pct"])
st.plotly_chart(fig, use_container_width=True)

st.subheader("Portfolio table")
st.dataframe(filtered[["project_id","project_name","workstream","region","rag_status","completion_pct","variance_days","budget_variance_pct","delivery_ratio"]], use_container_width=True)

st.subheader("Open RAID items")
st.dataframe(raid[raid["status"] == "Open"], use_container_width=True)

st.subheader("Capacity vs demand")
res = resources.melt(id_vars="workstream", value_vars=["capacity_fte","demand_fte"], var_name="metric", value_name="fte")
fig2 = px.bar(res, x="workstream", y="fte", color="metric", barmode="group")
st.plotly_chart(fig2, use_container_width=True)
