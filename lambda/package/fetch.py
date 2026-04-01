import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from transform import transform_records
from db import insert_records

load_dotenv()

AESO_API_KEY = os.getenv("AESO_API_KEY")
BASE_URL = "https://apimgw.aeso.ca/public/poolprice-api/v1.1/price/poolPrice"

def fetch_pool_prices():
    # always fetch yesterday's settled data
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    print(f"Fetching AESO pool prices from {yesterday} to {today}...")

    headers = {
        "API-KEY": AESO_API_KEY
    }

    params = {
        "startDate": yesterday,
        "endDate": today
    }

    response = requests.get(BASE_URL, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()
    all_records = data["return"]["Pool Price Report"]

    # filter out future hours where pool_price is empty string
    # these are hours where the price hasn't settled yet
    settled_records = [
        r for r in all_records
        if r.get("pool_price", "") != ""
    ]

    skipped = len(all_records) - len(settled_records)
    if skipped > 0:
        print(f"Skipped {skipped} unsettled future records")

    print(f"Fetched {len(settled_records)} settled records")
    for record in settled_records[:3]:
        print(record)

    return settled_records

if __name__ == "__main__":
    raw = fetch_pool_prices()
    cleaned = transform_records(raw)
    print("\nInserting into Supabase...")
    result = insert_records(cleaned)
    print(f"Done. Upserted {len(cleaned)} records.")