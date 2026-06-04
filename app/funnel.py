from sqlalchemy.orm import Session

from app.database import EventDB


def get_store_funnel(store_id: str, db: Session):
    events = db.query(EventDB).filter(
        EventDB.store_id == store_id,
        EventDB.is_staff == False
    ).all()

    sessions = {}

    for event in events:
        sessions.setdefault(event.visitor_id, {
            "entry": False,
            "zone_visit": False,
            "billing_queue": False,
            "purchase": False
        })

        if event.event_type in ["ENTRY", "REENTRY"]:
            sessions[event.visitor_id]["entry"] = True

        if event.event_type in ["ZONE_ENTER", "ZONE_DWELL", "ZONE_EXIT"]:
            sessions[event.visitor_id]["zone_visit"] = True

        if event.event_type == "BILLING_QUEUE_JOIN":
            sessions[event.visitor_id]["billing_queue"] = True

        if event.event_type == "PURCHASE":
            sessions[event.visitor_id]["purchase"] = True

    entry_count = sum(1 for s in sessions.values() if s["entry"])
    zone_visit_count = sum(1 for s in sessions.values() if s["zone_visit"])
    billing_queue_count = sum(1 for s in sessions.values() if s["billing_queue"])
    purchase_count = sum(1 for s in sessions.values() if s["purchase"])

    # Fallback for MVP: if no explicit PURCHASE event exists,
    # use billing queue as purchase proxy so older generated events still work.
    if purchase_count == 0 and billing_queue_count > 0:
        purchase_count = billing_queue_count

    def dropoff(previous, current):
        if previous == 0:
            return 0
        return round(((previous - current) / previous) * 100, 2)

    return {
        "store_id": store_id,
        "funnel": {
            "entry": entry_count,
            "zone_visit": zone_visit_count,
            "billing_queue": billing_queue_count,
            "purchase": purchase_count
        },
        "dropoff_percent": {
            "entry_to_zone": dropoff(entry_count, zone_visit_count),
            "zone_to_billing": dropoff(zone_visit_count, billing_queue_count),
            "billing_to_purchase": dropoff(billing_queue_count, purchase_count)
        },
        "session_count": len(sessions)
    }