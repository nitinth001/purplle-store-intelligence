
System Overview:

The Purplle Store Intelligence System converts CCTV footage into structured retail analytics.

The architecture follows an event-driven design where detections and tracking information are transformed into business events that power analytics and dashboards.

---

Processing Pipeline

CCTV Video

↓

YOLOv8 Person Detection

↓

Multi-Object Tracking

↓

Zone Mapping

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

Detection Layer

YOLOv8 is used for person detection.

Responsibilities:

- Person localization
- Confidence estimation
- Real-time inference

Output:

- Bounding boxes
- Confidence scores
- Track initialization

---

Tracking Layer

Tracking maintains visitor identity across frames.

Responsibilities:

- Visitor ID assignment
- Trajectory maintenance
- Re-entry detection
- Dwell computation

Output:

- visitor_id
- trajectory history
- dwell timestamps

---

Zone Intelligence

Store layouts are divided into logical business zones.

Examples:

- Skincare
- Makeup
- Haircare
- Fragrance
- Billing

Zone Engine Responsibilities:

- Zone entry detection
- Zone exit detection
- Zone dwell calculation
- Heatmap generation

Generated Events:

- ZONE_ENTER
- ZONE_EXIT
- ZONE_DWELL

---

Billing Intelligence

Billing cameras monitor customer purchase intent.

Generated Events:

- BILLING_QUEUE_JOIN
- BILLING_QUEUE_ABANDON
- PURCHASE

Metrics:

- Queue depth
- Queue abandonment rate
- Conversion rate

---

Event Architecture

All camera outputs are normalized into a unified event schema.

Each event contains:

- event_id
- store_id
- camera_id
- visitor_id
- timestamp
- event_type
- zone_id
- dwell_ms
- confidence
- metadata

Events are stored in JSONL format and ingested into SQLite.

---

Staff Exclusion Strategy

Store staff can create significant noise in analytics.

The architecture supports:

- Uniform-based filtering
- Staff ID tagging
- Staff zone exclusion

Staff events are ignored when computing:

- Conversion
- Dwell
- Footfall
- Queue analytics

---

Re-Entry Handling

Visitors may temporarily leave and re-enter a zone.

The system generates:

- EXIT
- REENTRY

events when a tracked visitor returns within a configurable threshold.

This prevents duplicate visitor counting.

---

Edge Cases

The system handles:

- Occlusions
- Tracking interruptions
- Crowded scenes
- Multiple visitors
- Empty zones
- Queue overlap
- Staff movement
- Camera boundary ambiguity

---

AI-Assisted Decisions

AI tools were used for:

- Detection model comparison
- Event schema design evaluation
- API architecture review
- Documentation generation
- Development support and debugging

All final engineering decisions were manually reviewed and adapted to challenge constraints.

The final solution prioritizes maintainability, robustness, and production-readiness over unnecessary architectural complexity.