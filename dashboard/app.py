import streamlit as st
import requests
import pandas as pd

API_BASE = "https://purplle-store-intelligence-h03m.onrender.com"
STORE_ID = "STORE_PURPLLE_001"

st.set_page_config(
    page_title="Purplle Store Intelligence Dashboard",
    layout="wide"
)

st.title("🏪 Purplle Store Intelligence Dashboard")
st.caption("Live analytics generated from CCTV-based detection, tracking, event streaming, and FastAPI intelligence APIs.")

def get_api(endpoint):
    try:
        response = requests.get(f"{API_BASE}{endpoint}", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API connection failed: {e}")
        st.stop()

metrics = get_api(f"/stores/{STORE_ID}/metrics")
heatmap = get_api(f"/stores/{STORE_ID}/heatmap")
funnel = get_api(f"/stores/{STORE_ID}/funnel")
anomalies = get_api(f"/stores/{STORE_ID}/anomalies")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Unique Visitors", metrics["unique_visitors"])
col2.metric("Entries", metrics["entry_count"])
col3.metric("Queue Depth", metrics["current_queue_depth"])
col4.metric("Conversion Rate", f"{metrics['conversion_rate'] * 100:.1f}%")

st.divider()

st.subheader("📍 Zone Heatmap")

heatmap_df = pd.DataFrame(heatmap["heatmap"])

if not heatmap_df.empty:
    st.dataframe(heatmap_df, use_container_width=True)
    st.bar_chart(
        heatmap_df.set_index("zone_id")["visit_count"]
    )
else:
    st.info("No zone data available yet.")

st.divider()

st.subheader("🧭 Conversion Funnel")

funnel_data = funnel["funnel"]
funnel_df = pd.DataFrame({
    "Stage": list(funnel_data.keys()),
    "Count": list(funnel_data.values())
})

st.dataframe(funnel_df, use_container_width=True)
st.bar_chart(funnel_df.set_index("Stage")["Count"])

st.divider()

st.subheader("🚨 Active Anomalies")

if anomalies["active_anomalies"]:
    for anomaly in anomalies["active_anomalies"]:
        st.warning(
            f"{anomaly['type']} | {anomaly['severity']} | {anomaly['suggested_action']}"
        )
else:
    st.success("No active anomalies detected.")

st.divider()

st.subheader("Raw API Snapshot")

with st.expander("Metrics JSON"):
    st.json(metrics)

with st.expander("Funnel JSON"):
    st.json(funnel)

with st.expander("Heatmap JSON"):
    st.json(heatmap)

with st.expander("Anomalies JSON"):
    st.json(anomalies)