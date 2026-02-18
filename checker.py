import requests
import json
import os
from datetime import date, timedelta

# ====== הגדרות ======
TOKEN = "d2e7bc5be23119a2dc9f7d3bda4077cf"
ORIGIN = "TLV"
DEST = "BUD"
DAYS_AHEAD = 21
DROP_THRESHOLD = 0.12

BASE_FILE = "baseline.json"
OUT_FILE = "latest_deal.json"

# ====== פונקציות ======
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
        "direct": "true",   # string lowercase
        "token": TOKEN
    }

    print("📌 Params:", params)
    print("📌 URL preview:", f"{url}?origin={ORIGIN}&destination={DEST}&departure_at={start}&return_at={end}")

    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("❌ HTTP ERROR:", e)
        print("Raw response:", r.text[:300])
        return []
    except Exception as e:
        print("❌ OTHER ERROR:", e)
        return []

    try:
        data = r.json()
    except Exception as e:
        print("❌ JSON ERROR:", e)
        print("Raw:", r.text[:300])
        return []

    if "data" not in data:
        print("❌ NO DATA FIELD:", data)
        return []

    return data["data"]

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

# ====== לוגיקה ראשית ======
def main():
    flights = search_flights()
    if not flights:
        print("⚠️ לא נמצאו טיסות")
        return

    cheapest = min(flights, key=lambda x: x.get("price", float('inf')))
    baseline = load_baseline()

    if baseline is None:
        save_baseline(cheapest)
        print("📌 נשמר מחיר בסיס:", cheapest.get("price"))
        return

    old = baseline.get("price", float('inf'))
    new = cheapest.get("price", float('inf'))
    drop = (old - new) / old

    print(f"בדיקה: מחיר קודם {old} → מחיר נוכחי {new}")

    if drop >= DROP_THRESHOLD:
        print("🔥 דיל! ירידה:", round(drop * 100, 1), "%")
        save_deal(cheapest)
    else:
        print("אין דיל עדיין")

# ====== הפעלה ======
if __name__ == "__main__":
    main()
