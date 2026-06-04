from sqlalchemy.orm import Session

from app.database import EventDB


def get_store_anomalies(store_id: str, db: Session):
    events = db.query(EventDB).filter(
        EventDB.store_id == store_id,
        EventDB.is_staff == False
    ).all()

    anomalies = []

    queue_count = 0
    zone_visits = {}
    visitors = set()
    billing_visitors = set()

    for event in events:
        visitors.add(event.visitor_id)

        if event.event_type == "BILLING_QUEUE_JOIN":
            queue_count += 1
            billing_visitors.add(event.visitor_id)

        if event.event_type in ["ZONE_ENTER", "ZONE_DWELL"] and event.zone_id:
            zone_visits[event.zone_id] = zone_visits.get(event.zone_id, 0) + 1

    if queue_count >= 3:
        anomalies.append({
            "type": "BILLING_QUEUE_SPIKE",
            "severity": "WARN",
            "message": "Billing queue activity is high.",
            "suggested_action": "Assign an additional staff member to the billing counter."
        })

    conversion_rate = 0
    if visitors:
        conversion_rate = len(billing_visitors) / len(visitors)

    if visitors and conversion_rate < 0.3:
        anomalies.append({
            "type": "CONVERSION_DROP",
            "severity": "WARN",
            "message": "Conversion rate is below expected threshold.",
            "suggested_action": "Check customer assistance, billing delays, and product availability."
        })

    important_zones = ["SKINCARE", "MAKEUP"]

    for zone in important_zones:
        if zone_visits.get(zone, 0) == 0:
            anomalies.append({
                "type": "DEAD_ZONE",
                "severity": "INFO",
                "message": f"No customer activity detected in {zone}.",
                "suggested_action": f"Review product placement or offers in {zone}."
            })

    return {
        "store_id": store_id,
        "active_anomalies": anomalies,
        "anomaly_count": len(anomalies)
    }