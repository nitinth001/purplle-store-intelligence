import math


class SimpleTracker:
    def __init__(self, max_distance=80, max_missing=20):
        self.next_id = 1
        self.tracks = {}
        self.max_distance = max_distance
        self.max_missing = max_missing

    def centroid(self, box):
        x1, y1, x2, y2 = box
        return ((x1 + x2) // 2, (y1 + y2) // 2)

    def distance(self, p1, p2):
        return math.sqrt(
            (p1[0] - p2[0]) ** 2 +
            (p1[1] - p2[1]) ** 2
        )

    def update(self, detections):
        updated_tracks = []

        for track_id in list(self.tracks.keys()):
            self.tracks[track_id]["missing"] += 1

        for det in detections:
            det_centroid = self.centroid(det["bbox"])

            best_track_id = None
            best_distance = float("inf")

            for track_id, track in self.tracks.items():
                dist = self.distance(det_centroid, track["centroid"])

                if dist < best_distance and dist < self.max_distance:
                    best_distance = dist
                    best_track_id = track_id

            if best_track_id is None:
                track_id = self.next_id
                self.next_id += 1

                self.tracks[track_id] = {
                    "track_id": track_id,
                    "bbox": det["bbox"],
                    "centroid": det_centroid,
                    "missing": 0,
                    "path": [det_centroid]
                }
            else:
                track_id = best_track_id

                self.tracks[track_id]["bbox"] = det["bbox"]
                self.tracks[track_id]["centroid"] = det_centroid
                self.tracks[track_id]["missing"] = 0
                self.tracks[track_id]["path"].append(det_centroid)

            updated_tracks.append(self.tracks[track_id])

        for track_id in list(self.tracks.keys()):
            if self.tracks[track_id]["missing"] > self.max_missing:
                del self.tracks[track_id]

        return updated_tracks