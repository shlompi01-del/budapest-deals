import requests
import json
import os
from datetime import date, timedelta

TOKEN = "d2e7bc5be23119a2dc9f7d3bda4077cf"

ORIGIN = "TLV"
DEST = "BUD"
DAYS_AHEAD = 21
DROP_THRESHOLD = 0.12

BASE_FILE = "baseline.json"
OUT_FILE = "latest_deal.json"

def get_dates():
    start = date.today() + timedelta(days=DAYS_AHEAD)
    end = start + timedelta(days=3)
    return start.isoformat(), end.isoformat()

def search_flights():
    start, end = get_dates()
    url = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
    params = {
        "origin": ORIGIN,
        "destination": DEST,
        "departure_at": start,
        "return_at": end,
        "currency": "USD",
        "direct": True,
        "token": TOKEN
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data.get("data", [])

def load_baseline():
    if not os.path.exists(BASE_FILE):
        return None
    with open(BASE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_baseline(obj):
    with open(BASE_FILE, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def save_deal(obj):
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def main():
    flights = search_flights()
    if not flights:
        print("⚠️ לא נמצאו טיסות")
        return

    cheapest = min(flights, key=lambda x: x["price"])
    baseline = load_baseline()

    if baseline is None:
        save_baseline(cheapest)
        print("📌 נשמר מחיר בסיס:", cheapest["price"])
        return

    old = baseline["price"]
    new = cheapest["price"]
    drop = (old - new) / old

    print(f"בדיקה: מחיר קודם {old} → מחיר נוכחי {new}")

    if drop >= DROP_THRESHOLD:
        print("🔥 דיל! ירידה:", round(drop * 100, 1), "%")
        save_deal(cheapest)
    else:
        print("אין דיל עדיין")

if __name__ == "__main__":
    main()
