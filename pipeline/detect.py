import cv2
from pathlib import Path
from ultralytics import YOLO

from pipeline.tracker import SimpleTracker
from pipeline.emit import make_event, save_event, frame_to_timestamp


INPUT_VIDEO = Path("data/videos/CAM 3.mp4")
OUTPUT_VIDEO = Path("data/outputs/cam3_events.mp4")
EVENTS_FILE = Path("data/events.jsonl")

STORE_ID = "STORE_PURPLLE_001"
CAMERA_ID = "CAM3"

model = YOLO("yolov8n.pt")
tracker = SimpleTracker(max_distance=90, max_missing=25)

cap = cv2.VideoCapture(str(INPUT_VIDEO))

if not cap.isOpened():
    raise RuntimeError(f"Could not open video: {INPUT_VIDEO}")

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS)) or 15

writer = cv2.VideoWriter(
    str(OUTPUT_VIDEO),
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (width, height)
)

EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)

if EVENTS_FILE.exists():
    EVENTS_FILE.unlink()

# IMPORTANT:
# This line is approximate.
# For CAM3, adjust after watching output video.
ENTRY_EXIT_LINE_Y = int(height * 0.58)

track_side = {}
entry_exit_done = set()

frame_count = 0
max_frames = 600

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

    cv2.line(
        frame,
        (0, ENTRY_EXIT_LINE_Y),
        (width, ENTRY_EXIT_LINE_Y),
        (0, 255, 255),
        3
    )

    cv2.putText(
        frame,
        "ENTRY / EXIT LINE",
        (30, ENTRY_EXIT_LINE_Y - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )

    for track in tracks:
        x1, y1, x2, y2 = track["bbox"]
        track_id = track["track_id"]
        cx, cy = track["centroid"]

        visitor_id = f"VIS_{track_id:04d}"

        current_side = "INSIDE" if cy < ENTRY_EXIT_LINE_Y else "OUTSIDE"
        previous_side = track_side.get(track_id)

        if previous_side is None:
            track_side[track_id] = current_side

        elif previous_side != current_side:
            timestamp = frame_to_timestamp(frame_count, fps)

            if previous_side == "OUTSIDE" and current_side == "INSIDE":
                event_type = "ENTRY"
            elif previous_side == "INSIDE" and current_side == "OUTSIDE":
                event_type = "EXIT"
            else:
                event_type = None

            if event_type:
                event_key = (track_id, event_type)

                if event_key not in entry_exit_done:
                    event = make_event(
                        store_id=STORE_ID,
                        camera_id=CAMERA_ID,
                        visitor_id=visitor_id,
                        event_type=event_type,
                        timestamp=timestamp,
                        zone_id=None,
                        dwell_ms=0,
                        is_staff=False,
                        confidence=0.85,
                        metadata={
                            "track_id": track_id,
                            "line_y": ENTRY_EXIT_LINE_Y,
                            "previous_side": previous_side,
                            "current_side": current_side
                        }
                    )

                    save_event(event, EVENTS_FILE)

                    print("EVENT:", event_type, visitor_id, timestamp)

                    entry_exit_done.add(event_key)

            track_side[track_id] = current_side

        color = (0, 255, 0)

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            color,
            2
        )

        cv2.putText(
            frame,
            f"{visitor_id} {current_side}",
            (x1, max(30, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2
        )

        cv2.circle(
            frame,
            (cx, cy),
            5,
            (0, 0, 255),
            -1
        )

    cv2.putText(
        frame,
        f"Active Visitors: {len(tracks)}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255),
        2
    )

    writer.write(frame)

    if frame_count % 30 == 0:
        print(f"Processed {frame_count} frames")

cap.release()
writer.release()

print("Event generation complete")
print(f"Video saved: {OUTPUT_VIDEO}")
print(f"Events saved: {EVENTS_FILE}")