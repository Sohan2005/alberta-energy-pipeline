# backfill.py
# One-time script to load 30 days of historical AESO pool price data

import requests
import os
import time
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

AESO_API_KEY = os.getenv("AESO_API_KEY")
BASE_URL = "https://apimgw.aeso.ca/public/poolprice-api/v1.1/price/poolPrice"

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def parse_float(value):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (ValueError, TypeError):
        return None

def fetch_range(start_date, end_date):
    headers = {"API-KEY": AESO_API_KEY}
    params = {"startDate": start_date, "endDate": end_date}
    response = requests.get(BASE_URL, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    return data["return"]["Pool Price Report"]

def backfill():
    today = datetime.now(timezone.utc)
    
    # Pull in 7-day chunks to avoid any API limits
    # Going back 30 days total
    all_records = []
    chunk_days = 7
    total_days = 30

    print(f"Starting backfill: {total_days} days of AESO pool price data")
    print("=" * 50)

    for i in range(0, total_days, chunk_days):
        end = today - timedelta(days=i)
        start = today - timedelta(days=i + chunk_days)
        
        start_str = start.strftime("%Y-%m-%d")
        end_str = end.strftime("%Y-%m-%d")
        
        print(f"Fetching {start_str} to {end_str}...")
        
        try:
            records = fetch_range(start_str, end_str)
            
            # Filter out unsettled future records (empty pool_price)
            settled = [r for r in records if r.get("pool_price", "") != ""]
            
            # Transform to database format
            cleaned = []
            for r in settled:
                cleaned.append({
                    "begin_datetime_utc": r.get("begin_datetime_utc"),
                    "begin_datetime_mpt": r.get("begin_datetime_mpt"),
                    "pool_price": parse_float(r.get("pool_price")),
                    "forecast_pool_price": parse_float(r.get("forecast_pool_price")),
                    "rolling_30day_avg": parse_float(r.get("rolling_30day_avg"))
                })
            
            all_records.extend(cleaned)
            print(f"  Got {len(settled)} settled records")
            
            # Be polite to the API
            time.sleep(1)
            
        except Exception as e:
            print(f"  Error fetching {start_str} to {end_str}: {e}")
            continue

    print(f"\nTotal records fetched: {len(all_records)}")
    print("Upserting to Supabase...")

    # Upsert in batches of 100
    batch_size = 100
    total_upserted = 0

    for i in range(0, len(all_records), batch_size):
        batch = all_records[i:i + batch_size]
        try:
            response = (
                supabase.table("pool_prices")
                .upsert(batch, on_conflict="begin_datetime_utc")
                .execute()
            )
            total_upserted += len(batch)
            print(f"  Upserted batch {i//batch_size + 1} ({total_upserted}/{len(all_records)})")
        except Exception as e:
            print(f"  Batch error: {e}")

    # Check final count
    count_response = supabase.table("pool_prices").select("id", count="exact").execute()
    print(f"\nBackfill complete!")
    print(f"Total records now in database: {count_response.count}")

if __name__ == "__main__":
    backfill()