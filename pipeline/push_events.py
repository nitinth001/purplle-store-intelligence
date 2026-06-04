import json
import requests
from pathlib import Path

EVENTS_FILE = Path("data/events.jsonl")
API_URL = "https://purplle-store-intelligence-h03m.onrender.com/events/ingest"


def main():
    if not EVENTS_FILE.exists():
        raise FileNotFoundError("data/events.jsonl not found. Run detection first.")

    events = []

    with open(EVENTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))

    if not events:
        print("No events found.")
        return

    payload = {"events": events}

    response = requests.post(API_URL, json=payload)

    print("Status Code:", response.status_code)
    print(response.json())


if __name__ == "__main__":
    main()