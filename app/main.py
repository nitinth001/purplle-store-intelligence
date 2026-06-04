from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.metrics import get_store_metrics
from app.models import EventBatch
from app.heatmap import get_store_heatmap
from app.database import init_db, get_db
from app.ingestion import ingest_events
from app.health import get_health_status
from app.funnel import get_store_funnel
from app.anomalies import get_store_anomalies

app = FastAPI(
    title="Purplle Store Intelligence",
    version="1.0"
)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def home():
    return {
        "message": "Store Intelligence API Running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/events/ingest")
def ingest(
    batch: EventBatch,
    db: Session = Depends(get_db)
):
    result = ingest_events(batch.events, db)

    return {
        "status": "success",
        **result
    }
@app.get("/stores/{store_id}/metrics")
def metrics(
    store_id: str,
    db: Session = Depends(get_db)
):
    return get_store_metrics(store_id, db)
@app.get("/stores/{store_id}/funnel")
def funnel(
    store_id: str,
    db: Session = Depends(get_db)
):
    return get_store_funnel(store_id, db)

@app.get("/stores/{store_id}/heatmap")
def heatmap(
    store_id: str,
    db: Session = Depends(get_db)
):
    return get_store_heatmap(store_id, db)
@app.get("/stores/{store_id}/anomalies")
def anomalies(
    store_id: str,
    db: Session = Depends(get_db)
):
    return get_store_anomalies(store_id, db)
@app.get("/health")
def health(db: Session = Depends(get_db)):
    return get_health_status(db)