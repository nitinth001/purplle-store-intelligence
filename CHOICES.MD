
Decision 1 – Detection Model Selection:

Options Considered-

- YOLOv8
- RT-DETR
- MediaPipe
- Custom OpenCV Pipeline

AI Suggestion

AI tools suggested YOLOv8 and RT-DETR as the strongest candidates due to their balance of accuracy and ease of deployment.

Final Choice

YOLOv8

Reasoning

YOLOv8 provides:

- Strong real-time performance
- Mature ecosystem
- Easy integration
- Reliable person detection

For this challenge, engineering speed and robustness were more valuable than marginal accuracy improvements.

---

Decision 2 – Event Schema Design

Options Considered

1. Store raw detections only
2. Store tracking trajectories
3. Store structured business events

AI Suggestion

AI tools recommended moving from raw detections to structured events because analytics APIs become significantly simpler.

Final Choice

Structured Event Architecture

Reasoning

The chosen schema captures:

- ENTRY
- EXIT
- REENTRY
- ZONE_ENTER
- ZONE_EXIT
- ZONE_DWELL
- BILLING_QUEUE_JOIN
- BILLING_QUEUE_ABANDON
- PURCHASE

Benefits:

- Analytics becomes query-driven
- Storage remains compact
- New metrics can be added easily
- Supports future streaming systems

---

Decision 3 – API Architecture

Options Considered

- Flask
- FastAPI
- Django REST Framework

AI Suggestion

FastAPI was recommended because of automatic documentation, validation, and asynchronous support.

Final Choice

FastAPI

Reasoning

Advantages:

- Automatic Swagger documentation
- Pydantic validation
- High performance
- Production-ready design

FastAPI reduced development complexity while maintaining scalability.

---

Storage Decision

Options Considered

- SQLite
- PostgreSQL
- MongoDB

 Choice :

SQLite

Reasoning

The challenge dataset size is relatively small.

SQLite provides:

- Zero configuration
- Simple deployment
- Easy local testing

For production scale, PostgreSQL would replace SQLite.

---

Dashboard Decision

Options Considered

- React
- Streamlit
- Dash

Final Choice

Streamlit

Reasoning

The objective was rapid visualization of analytics.

Streamlit allowed:

- Fast development
- Easy deployment
- Direct Python integration

without introducing frontend complexity.

---

Multi-Camera Design Decision

The challenge provides Entry, Zone, and Billing cameras.

Instead of building one monolithic detector, the architecture assigns responsibilities:

Entry Cameras:
Footfall and direction

Zone Cameras:
Dwell and engagement

Billing Cameras:
Queue and conversion

This design is easier to scale across stores.

---

AI-Assisted Decisions

AI tools were used for:

1. Comparing detection architectures
2. Evaluating event schema alternatives
3. Reviewing API architecture choices

Several suggestions were accepted, while others were overridden after considering deployment simplicity, challenge constraints, and maintainability.

The final architecture prioritizes clarity, robustness, and production-readiness over unnecessary complexity.

---

Decision 4 – JSONL Event Log Format

Options Considered

- CSV
- JSON
- JSONL

AI Suggestion

JSONL was recommended because it naturally supports streaming systems and event-driven architectures.

Final Choice

JSONL

Reasoning

Benefits:

- One event per line
- Easy ingestion
- Stream-friendly
- Scales to Kafka-style architectures
- Compatible with challenge requirements

JSONL also simplifies debugging and analytics generation.