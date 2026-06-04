from sqlalchemy.orm import Session

from app.database import EventDB


def get_store_metrics(store_id: str, db: Session):
    events = db.query(EventDB).filter(
        EventDB.store_id == store_id,
        EventDB.is_staff == False
    ).all()

    if not events:
        return {
            "store_id": store_id,
            "unique_visitors": 0,
            "entry_count": 0,
            "exit_count": 0,
            "conversion_rate": 0,
            "avg_dwell_per_zone": {},
            "current_queue_depth": 0,
            "abandonment_rate": 0
        }

    unique_visitors = set()
    entry_visitors = set()
    exit_visitors = set()
    billing_visitors = set()
    purchase_visitors = set()

    dwell_by_zone = {}
    queue_join_count = 0
    queue_abandon_count = 0
    queue_depth = 0

    for event in events:
        unique_visitors.add(event.visitor_id)

        if event.event_type in ["ENTRY", "REENTRY"]:
            entry_visitors.add(event.visitor_id)

        elif event.event_type == "EXIT":
            exit_visitors.add(event.visitor_id)

        elif event.event_type == "BILLING_QUEUE_JOIN":
            billing_visitors.add(event.visitor_id)
            queue_join_count += 1
            queue_depth += 1

        elif event.event_type == "BILLING_QUEUE_ABANDON":
            queue_abandon_count += 1
            queue_depth = max(0, queue_depth - 1)

        elif event.event_type == "PURCHASE":
            purchase_visitors.add(event.visitor_id)
            queue_depth = max(0, queue_depth - 1)

        if event.event_type == "ZONE_DWELL" and event.zone_id:
            dwell_by_zone.setdefault(event.zone_id, [])
            dwell_by_zone[event.zone_id].append(event.dwell_ms)

    avg_dwell_per_zone = {
        zone: round(sum(values) / len(values), 2)
        for zone, values in dwell_by_zone.items()
        if values
    }

    denominator = len(entry_visitors) if entry_visitors else len(unique_visitors)

    conversion_rate = 0
    if denominator > 0:
        if purchase_visitors:
            conversion_rate = round(len(purchase_visitors) / denominator, 2)
        else:
            conversion_rate = round(len(billing_visitors) / denominator, 2)

    abandonment_rate = 0
    if queue_join_count > 0:
        abandonment_rate = round(queue_abandon_count / queue_join_count, 2)

    return {
        "store_id": store_id,
        "unique_visitors": len(unique_visitors),
        "entry_count": len(entry_visitors),
        "exit_count": len(exit_visitors),
        "conversion_rate": conversion_rate,
        "avg_dwell_per_zone": avg_dwell_per_zone,
        "current_queue_depth": queue_depth,
        "abandonment_rate": abandonment_rate
    }