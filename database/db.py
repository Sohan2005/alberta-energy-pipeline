import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_record_count():
    response = supabase.table("pool_prices").select("id", count="exact").execute()
    return response.count

def insert_records(records):
    # bug: checking count before and after doesn't tell us
    # how many were truly new vs updated
    before = get_record_count()

    response = (
        supabase.table("pool_prices")
        .upsert(records, on_conflict="begin_datetime_utc")
        .execute()
    )

    after = get_record_count()
    new_records = after - before
    print(f"New records inserted: {new_records}")
    print(f"Total records in database: {after}")

    return response