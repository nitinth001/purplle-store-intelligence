Purplle Store Intelligence System--->>>

Overview:

Purplle Store Intelligence System is an AI-powered retail analytics platform that transforms raw CCTV footage into actionable business intelligence.

The solution processes multi-camera retail store footage, detects and tracks customer movement, generates structured behavioral events, computes store intelligence metrics, detects operational anomalies, and exposes analytics through production-ready FastAPI endpoints and a live Streamlit dashboard.

The system is designed around an event-driven architecture and supports offline analytics as well as simulated real-time event streaming.


Business Problem

Retail stores generate large volumes of CCTV footage but derive very little operational intelligence from it.

Store managers often lack visibility into:

- Visitor footfall
- Zone engagement
- Queue congestion
- Customer drop-off points
- Conversion performance
- Operational anomalies

The goal is to convert passive CCTV infrastructure into an intelligent decision-support platform.


System Architecture

Raw CCTV Footage
↓
YOLOv8 Detection
↓
Visitor Tracking
↓
Event Generation
↓
Event Ingestion Layer
↓
SQLite Event Store
↓
Analytics Engine
↓
FastAPI APIs
↓
Streamlit Dashboard

---

Multi-Camera Design

The challenge provides multiple camera views per store.

The system is designed around camera responsibilities:

Entry Cameras

Generate:

- ENTRY
- EXIT
- REENTRY

Zone Cameras

Generate:

- ZONE_ENTER
- ZONE_EXIT
- ZONE_DWELL

Billing Cameras

Generate:

- BILLING_QUEUE_JOIN
- BILLING_QUEUE_ABANDON
- PURCHASE

All cameras emit standardized events into a common ingestion layer.

---

Event Schema

Each event contains:

- event_id
- store_id
- camera_id
- visitor_id
- event_type
- timestamp
- zone_id
- dwell_ms
- is_staff
- confidence
- metadata

The ingestion layer supports normalization of official sample event names into internal event types.

---

Analytics Generated

Metrics

- Unique Visitors
- Entry Count
- Exit Count
- Conversion Rate
- Average Dwell Time
- Queue Depth
- Queue Abandonment Rate

Funnel

Entry
→ Zone Visit
→ Billing Queue
→ Purchase

Heatmap

Zone-level:

- Visit frequency
- Average dwell
- Engagement score

Anomalies

- Queue Spike
- Conversion Drop
- Low Traffic Zones
- Stale Feed Detection

---

API Endpoints

POST /events/ingest

Ingests structured retail events.

GET /stores/{store_id}/metrics

Returns:

- visitors
- conversion
- dwell
- queue depth

GET /stores/{store_id}/funnel

Returns conversion funnel statistics.

GET /stores/{store_id}/heatmap

Returns zone engagement analytics.

GET /stores/{store_id}/anomalies

Returns active operational anomalies.

GET /health

Returns service and feed status.

---

POS Correlation

The provided POS transactions do not contain customer identity.

Conversion is estimated using:

- store_id
- billing-zone activity
- transaction timestamps

A configurable matching window can be used to correlate visitor sessions with purchases.

---

Technology Stack

- Python
- YOLOv8
- OpenCV
- FastAPI
- SQLAlchemy
- SQLite
- Streamlit
- Render
- GitHub

---

Deployment

Backend API:
[Render URL]

Dashboard:
[Streamlit URL]

---

Future Scaling

Potential production upgrades:

- Kafka Event Streaming
- PostgreSQL
- Redis
- RTSP Live Feeds
- DeepSORT / ByteTrack
- Multi-Store Analytics
- Cloud-Native Deployment
- Real-Time Alerts

---

Repository Structure

app/
dashboard/
pipeline/
tests/
docs/

README.md
DESIGN.md
CHOICES.md

---

Running the Project

1. Clone repository

2. Install dependencies

pip install -r requirements.txt

3. Start API

uvicorn app.main:app --reload

4. Open Swagger

http://127.0.0.1:8000/docs

5. Launch Dashboard

streamlit run dashboard/app.py

---

Live Demo :

Dashboard:
[https://purplle-store-intelligence-kzbmjxpoczqfumomwkusrm.streamlit.app/]

Backend:
[https://purplle-store-intelligence-h03m.onrender.com]

## Staff Exclusion

Store staff are excluded from customer analytics.

The current implementation supports:

- Uniform-color based filtering
- Staff zone whitelisting
- Staff ID tagging

This prevents artificial inflation of dwell and conversion metrics.

## Edge Cases Handled

- Visitor re-entry
- Occlusions
- Temporary tracking loss
- Multiple visitors in same zone
- Queue overlap
- Empty store periods
- Staff movement contamination


## Testing

Run all tests:

pytest tests/

Validated Components:

- Event ingestion
- Metrics APIs
- Funnel APIs
- Heatmap APIs
- Anomaly APIs
