import os
from fastapi import FastAPI, HTTPException
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(
    title="Alberta Energy API",
    description="REST API for Alberta electricity pool price data sourced from AESO",
    version="1.0.0"
)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "Alberta Energy API",
        "version": "1.0.0"
    }

@app.get("/records")
def get_records():
    response = (
        supabase.table("pool_prices")
        .select("*")
        .order("begin_datetime_utc", desc=True)
        .limit(50)
        .execute()
    )
    return response.data

# bug: no pagination - returns ALL matching records at once
@app.get("/records/range")
def get_by_date_range(start: str, end: str):
    response = (
        supabase.table("pool_prices")
        .select("*")
        .gte("begin_datetime_utc", start)
        .lte("begin_datetime_utc", end)
        .order("begin_datetime_utc", desc=False)
        .execute()
    )
    return response.data

@app.get("/records/latest")
def get_latest():
    response = (
        supabase.table("pool_prices")
        .select("*")
        .order("begin_datetime_utc", desc=True)
        .limit(24)
        .execute()
    )
    return response.data