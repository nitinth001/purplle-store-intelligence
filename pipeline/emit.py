import json
import uuid
from datetime import datetime, timezone


def make_event(
    store_id,
    camera_id,
    visitor_id,
    event_type,
    timestamp,
    zone_id=None,
    dwell_ms=0,
    is_staff=False,
    confidence=0.8,
    metadata=None
):
    return {
        "event_id": str(uuid.uuid4()),
        "store_id": store_id,
        "camera_id": camera_id,
        "visitor_id": visitor_id,
        "event_type": event_type,
        "timestamp": timestamp,
        "zone_id": zone_id,
        "dwell_ms": dwell_ms,
        "is_staff": is_staff,
        "confidence": confidence,
        "metadata": metadata or {}
    }


def save_event(event, output_path="data/events.jsonl"):
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def frame_to_timestamp(frame_no, fps, base_time="2026-04-10T20:10:00Z"):
    base_dt = datetime.fromisoformat(base_time.replace("Z", "+00:00"))
    seconds = frame_no / max(fps, 1)
    event_time = base_dt.timestamp() + seconds
    dt = datetime.fromtimestamp(event_time, tz=timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")