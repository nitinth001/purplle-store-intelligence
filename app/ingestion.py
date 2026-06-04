from sqlalchemy.orm import Session

from app.database import EventDB, event_to_db


EVENT_NAME_MAP = {
    "entry": "ENTRY",
    "exit": "EXIT",

    "zone_entered": "ZONE_ENTER",
    "zone_enter": "ZONE_ENTER",
    "zone_exited": "ZONE_EXIT",
    "zone_exit": "ZONE_EXIT",
    "zone_dwell": "ZONE_DWELL",
    "zone_visit": "ZONE_DWELL",

    "billing_queue_join": "BILLING_QUEUE_JOIN",
    "queue_joined": "BILLING_QUEUE_JOIN",
    "queue_join": "BILLING_QUEUE_JOIN",

    "billing_queue_abandon": "BILLING_QUEUE_ABANDON",
    "queue_abandoned": "BILLING_QUEUE_ABANDON",
    "queue_abandon": "BILLING_QUEUE_ABANDON",

    "queue_completed": "PURCHASE",
    "billing_completed": "PURCHASE",
    "purchase": "PURCHASE",

    "reentry": "REENTRY",
}


def normalize_event_type(event_type):
    raw = str(event_type)

    if "." in raw:
        raw = raw.split(".")[-1]

    raw = raw.replace('"', "").replace("'", "").strip()
    key = raw.lower()

    return EVENT_NAME_MAP.get(key, raw.upper())


def ingest_events(events, db: Session):
    inserted = 0
    duplicates = 0
    errors = []

    for event in events:
        try:
            normalized_type = normalize_event_type(event.event_type)
            event.event_type = normalized_type

            existing = db.query(EventDB).filter(
                EventDB.event_id == event.event_id
            ).first()

            if existing:
                duplicates += 1
                continue

            db_event = event_to_db(event)
            db.add(db_event)
            inserted += 1

        except Exception as e:
            errors.append({
                "event_id": getattr(event, "event_id", None),
                "error": str(e)
            })

    db.commit()

    return {
        "inserted": inserted,
        "duplicates": duplicates,
        "errors": errors,
        "accepted": inserted + duplicates,
        "failed": len(errors)
    }