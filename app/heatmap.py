from sqlalchemy.orm import Session
from app.database import EventDB


def get_store_heatmap(store_id: str, db: Session):
    events = db.query(EventDB).filter(
        EventDB.store_id == store_id,
        EventDB.is_staff == False
    ).all()

    zone_data = {}
    sessions = set()

    for event in events:
        sessions.add(event.visitor_id)

        if event.zone_id is None:
            continue

        if event.zone_id not in zone_data:
            zone_data[event.zone_id] = {
                "visit_count": 0,
                "dwell_values": []
            }

        if event.event_type in ["ZONE_ENTER", "ZONE_DWELL"]:
            zone_data[event.zone_id]["visit_count"] += 1

        if event.event_type == "ZONE_DWELL":
            zone_data[event.zone_id]["dwell_values"].append(event.dwell_ms)

    max_visits = max(
        [z["visit_count"] for z in zone_data.values()],
        default=1
    )

    heatmap = []

    for zone_id, data in zone_data.items():
        avg_dwell = 0

        if data["dwell_values"]:
            avg_dwell = round(
                sum(data["dwell_values"]) / len(data["dwell_values"]),
                2
            )

        normalized_score = round(
            (data["visit_count"] / max_visits) * 100,
            2
        )

        heatmap.append({
            "zone_id": zone_id,
            "visit_count": data["visit_count"],
            "avg_dwell_ms": avg_dwell,
            "normalized_score": normalized_score
        })

    data_confidence = "LOW" if len(sessions) < 20 else "HIGH"

    return {
        "store_id": store_id,
        "session_count": len(sessions),
        "data_confidence": data_confidence,
        "heatmap": heatmap
    }