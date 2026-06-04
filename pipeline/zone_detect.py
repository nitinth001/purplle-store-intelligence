import cv2
from pathlib import Path
from ultralytics import YOLO

from pipeline.tracker import SimpleTracker
from pipeline.emit import make_event, save_event, frame_to_timestamp


STORE_ID = "STORE_PURPLLE_001"
EVENTS_FILE = Path("data/events.jsonl")

CAMERA_CONFIG = {
    "CAM1": {
        "input": "data/videos/CAM 1.mp4",
        "output": "data/outputs/cam1_zone_events.mp4",
        "zone_id": "SKINCARE"
    },
    "CAM2": {
        "input": "data/videos/CAM 2.mp4",
        "output": "data/outputs/cam2_zone_events.mp4",
        "zone_id": "MAKEUP"
    }
}

model = YOLO("yolov8n.pt")


def process_camera(camera_id):
    config = CAMERA_CONFIG[camera_id]

    input_video = Path(config["input"])
    output_video = Path(config["output"])
    zone_id = config["zone_id"]

    if not input_video.exists():
        raise FileNotFoundError(f"Video not found: {input_video}")

    tracker = SimpleTracker(max_distance=90, max_missing=25)

    cap = cv2.VideoCapture(str(input_video))

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 15

    output_video.parent.mkdir(parents=True, exist_ok=True)

    writer = cv2.VideoWriter(
        str(output_video),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height)
    )

    # large browsing zone covering most customer-visible shelf area
    zone_box = [
        int(width * 0.05),
        int(height * 0.12),
        int(width * 0.95),
        int(height * 0.92)
    ]

    visitor_inside = {}
    visitor_start_frame = {}

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

        zx1, zy1, zx2, zy2 = zone_box

        cv2.rectangle(frame, (zx1, zy1), (zx2, zy2), (0, 255, 255), 3)
        cv2.putText(
            frame,
            zone_id,
            (zx1, zy1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 255),
            2
        )

        for track in tracks:
            x1, y1, x2, y2 = track["bbox"]
            track_id = track["track_id"]
            cx, cy = track["centroid"]

            visitor_id = f"VIS_{camera_id}_{track_id:04d}"

            inside_zone = zx1 <= cx <= zx2 and zy1 <= cy <= zy2
            was_inside = visitor_inside.get(track_id, False)

            timestamp = frame_to_timestamp(frame_count, fps)

            if inside_zone and not was_inside:
                visitor_inside[track_id] = True
                visitor_start_frame[track_id] = frame_count

                event = make_event(
                    store_id=STORE_ID,
                    camera_id=camera_id,
                    visitor_id=visitor_id,
                    event_type="ZONE_ENTER",
                    timestamp=timestamp,
                    zone_id=zone_id,
                    dwell_ms=0,
                    is_staff=False,
                    confidence=0.85,
                    metadata={
                        "track_id": track_id,
                        "zone": zone_id
                    }
                )

                save_event(event, EVENTS_FILE)
                print("EVENT:", "ZONE_ENTER", visitor_id, zone_id)

            elif inside_zone and was_inside:
                start_frame = visitor_start_frame.get(track_id, frame_count)
                dwell_ms = int(((frame_count - start_frame) / fps) * 1000)

                if dwell_ms >= 10000 and frame_count % 150 == 0:
                    event = make_event(
                        store_id=STORE_ID,
                        camera_id=camera_id,
                        visitor_id=visitor_id,
                        event_type="ZONE_DWELL",
                        timestamp=timestamp,
                        zone_id=zone_id,
                        dwell_ms=dwell_ms,
                        is_staff=False,
                        confidence=0.82,
                        metadata={
                            "track_id": track_id,
                            "zone": zone_id
                        }
                    )

                    save_event(event, EVENTS_FILE)
                    print("EVENT:", "ZONE_DWELL", visitor_id, zone_id, dwell_ms)

            elif not inside_zone and was_inside:
                visitor_inside[track_id] = False

                start_frame = visitor_start_frame.get(track_id, frame_count)
                dwell_ms = int(((frame_count - start_frame) / fps) * 1000)

                event = make_event(
                    store_id=STORE_ID,
                    camera_id=camera_id,
                    visitor_id=visitor_id,
                    event_type="ZONE_EXIT",
                    timestamp=timestamp,
                    zone_id=zone_id,
                    dwell_ms=dwell_ms,
                    is_staff=False,
                    confidence=0.80,
                    metadata={
                        "track_id": track_id,
                        "zone": zone_id
                    }
                )

                save_event(event, EVENTS_FILE)
                print("EVENT:", "ZONE_EXIT", visitor_id, zone_id)

            color = (0, 255, 0) if inside_zone else (255, 0, 0)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

            cv2.putText(
                frame,
                visitor_id,
                (x1, max(30, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

        writer.write(frame)

        if frame_count % 30 == 0:
            print(f"{camera_id}: Processed {frame_count} frames")

    cap.release()
    writer.release()

    print(f"{camera_id} complete")
    print(f"Saved: {output_video}")


if __name__ == "__main__":
    process_camera("CAM1")
    process_camera("CAM2")