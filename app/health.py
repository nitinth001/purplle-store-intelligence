from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.database import EventDB


def parse_timestamp(ts: str):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def get_health_status(db: Session):
    try:
        events = db.query(EventDB).all()
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "unavailable",
            "error": str(e)
        }

    if not events:
        return {
            "status": "healthy",
            "database": "connected",
            "message": "No events ingested yet",
            "stores": []
        }

    latest_by_store = {}

    for event in events:
        store_id = event.store_id

        if store_id not in latest_by_store:
            latest_by_store[store_id] = event.timestamp
        elif event.timestamp > latest_by_store[store_id]:
            latest_by_store[store_id] = event.timestamp

    now = datetime.now(timezone.utc)
    stores = []

    for store_id, last_timestamp in latest_by_store.items():
        try:
            last_dt = parse_timestamp(last_timestamp)
            lag_minutes = round((now - last_dt).total_seconds() / 60, 2)

            feed_status = "OK"
            warning = None

            if lag_minutes > 10:
                feed_status = "STALE_FEED"
                warning = "No event received in the last 10 minutes"

        except Exception:
            lag_minutes = None
            feed_status = "UNKNOWN"
            warning = "Invalid timestamp format"

        stores.append({
            "store_id": store_id,
            "last_event_timestamp": last_timestamp,
            "lag_minutes": lag_minutes,
            "feed_status": feed_status,
            "warning": warning
        })

    overall_status = "healthy"

    if any(store["feed_status"] == "STALE_FEED" for store in stores):
        overall_status = "degraded"

    return {
        "status": overall_status,
        "database": "connected",
        "stores": stores
    }