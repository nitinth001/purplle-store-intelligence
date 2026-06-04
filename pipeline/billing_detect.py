import cv2
from pathlib import Path
from ultralytics import YOLO

from pipeline.tracker import SimpleTracker
from pipeline.emit import make_event, save_event, frame_to_timestamp
from pipeline.billing import in_queue, in_billing


STORE_ID = "STORE_PURPLLE_001"
CAMERA_ID = "CAM5"

INPUT_VIDEO = Path("data/videos/CAM 5.mp4")
OUTPUT_VIDEO = Path("data/outputs/cam5_billing_events.mp4")
EVENTS_FILE = Path("data/events.jsonl")

model = YOLO("yolov8n.pt")
tracker = SimpleTracker(max_distance=90, max_missing=25)


def main():
    if not INPUT_VIDEO.exists():
        raise FileNotFoundError(f"Video not found: {INPUT_VIDEO}")

    cap = cv2.VideoCapture(str(INPUT_VIDEO))

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 15

    OUTPUT_VIDEO.parent.mkdir(parents=True, exist_ok=True)

    writer = cv2.VideoWriter(
        str(OUTPUT_VIDEO),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height)
    )

    visitor_state = {}
    visitor_queue_start = {}

    frame_count = 0
    max_frames = 900

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame_count += 1

        if frame_count > max_frames:
            break

        results = model(frame, conf=0.35, verbose=False)

        detections = []

        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0])
                confidence = float(box.conf[0])

                if cls != 0:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                detections.append({
                    "bbox": [x1, y1, x2, y2],
                    "confidence": confidence
                })

        tracks = tracker.update(detections)

        # Draw approximate zones
        cv2.rectangle(frame, (650, 120), (980, 760), (0, 255, 255), 3)
        cv2.putText(frame, "QUEUE_ZONE", (650, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        cv2.rectangle(frame, (250, 180), (650, 760), (255, 0, 255), 3)
        cv2.putText(frame, "BILLING_ZONE", (250, 170),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)

        queue_depth = 0

        for track in tracks:
            x1, y1, x2, y2 = track["bbox"]
            track_id = track["track_id"]
            cx, cy = track["centroid"]

            visitor_id = f"VIS_CAM5_{track_id:04d}"
            timestamp = frame_to_timestamp(frame_count, fps)

            is_in_queue = in_queue(cx, cy)
            is_in_billing = in_billing(cx, cy)

            if is_in_queue:
                queue_depth += 1

            previous_state = visitor_state.get(track_id, "NONE")

            if is_in_queue and previous_state != "QUEUE":
                visitor_state[track_id] = "QUEUE"
                visitor_queue_start[track_id] = frame_count

                event = make_event(
                    store_id=STORE_ID,
                    camera_id=CAMERA_ID,
                    visitor_id=visitor_id,
                    event_type="BILLING_QUEUE_JOIN",
                    timestamp=timestamp,
                    zone_id="BILLING",
                    dwell_ms=0,
                    is_staff=False,
                    confidence=0.84,
                    metadata={
                        "track_id": track_id,
                        "queue_depth": queue_depth
                    }
                )

                save_event(event, EVENTS_FILE)
                print("EVENT: BILLING_QUEUE_JOIN", visitor_id)

            elif is_in_billing and previous_state == "QUEUE":
                visitor_state[track_id] = "BILLING"

                start_frame = visitor_queue_start.get(track_id, frame_count)
                wait_ms = int(((frame_count - start_frame) / fps) * 1000)

                event = make_event(
                    store_id=STORE_ID,
                    camera_id=CAMERA_ID,
                    visitor_id=visitor_id,
                    event_type="ZONE_DWELL",
                    timestamp=timestamp,
                    zone_id="BILLING",
                    dwell_ms=wait_ms,
                    is_staff=False,
                    confidence=0.82,
                    metadata={
                        "track_id": track_id,
                        "billing_wait_ms": wait_ms,
                        "converted": True
                    }
                )

                save_event(event, EVENTS_FILE)
                print("EVENT: BILLING_SERVICE", visitor_id, wait_ms)

            elif not is_in_queue and not is_in_billing and previous_state == "QUEUE":
                visitor_state[track_id] = "ABANDONED"

                start_frame = visitor_queue_start.get(track_id, frame_count)
                wait_ms = int(((frame_count - start_frame) / fps) * 1000)

                event = make_event(
                    store_id=STORE_ID,
                    camera_id=CAMERA_ID,
                    visitor_id=visitor_id,
                    event_type="BILLING_QUEUE_ABANDON",
                    timestamp=timestamp,
                    zone_id="BILLING",
                    dwell_ms=wait_ms,
                    is_staff=False,
                    confidence=0.75,
                    metadata={
                        "track_id": track_id,
                        "wait_ms": wait_ms
                    }
                )

                save_event(event, EVENTS_FILE)
                print("EVENT: BILLING_QUEUE_ABANDON", visitor_id)

            color = (0, 255, 255) if is_in_queue else (255, 0, 255) if is_in_billing else (0, 255, 0)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            cv2.putText(frame, visitor_id, (x1, max(30, y1 - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        cv2.putText(frame, f"Queue Depth: {queue_depth}", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        writer.write(frame)

        if frame_count % 30 == 0:
            print(f"CAM5: Processed {frame_count} frames")

    cap.release()
    writer.release()

    print("CAM5 billing processing complete")
    print(f"Saved: {OUTPUT_VIDEO}")


if __name__ == "__main__":
    main()