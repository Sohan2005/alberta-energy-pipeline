import os
from fastapi import FastAPI, HTTPException, Query
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

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
def get_records(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0)
):
    """
    Get pool price records with pagination.
    - limit: number of records to return (1-200, default 50)
    - offset: number of records to skip (default 0)
    """
    response = (
        supabase.table("pool_prices")
        .select("*")
        .order("begin_datetime_utc", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return {
        "count": len(response.data),
        "offset": offset,
        "limit": limit,
        "data": response.data
    }


@app.get("/records/latest")
def get_latest():
    """
    Get the most recent 24 hours of pool prices.
    """
    response = (
        supabase.table("pool_prices")
        .select("*")
        .order("begin_datetime_utc", desc=True)
        .limit(24)
        .execute()
    )
    return {
        "count": len(response.data),
        "data": response.data
    }


@app.get("/records/range")
def get_by_date_range(
    start: str = Query(..., description="Start datetime (YYYY-MM-DD or YYYY-MM-DD HH:MM)"),
    end: str = Query(..., description="End datetime (YYYY-MM-DD or YYYY-MM-DD HH:MM)"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0)
):
    """
    Get pool prices within a date range with pagination.
    - start: start datetime e.g. 2026-04-01
    - end: end datetime e.g. 2026-04-02
    """
    # validate start is before end
    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        if start_dt >= end_dt:
            raise HTTPException(
                status_code=400,
                detail="start must be before end"
            )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS"
        )

    response = (
        supabase.table("pool_prices")
        .select("*")
        .gte("begin_datetime_utc", start)
        .lte("begin_datetime_utc", end)
        .order("begin_datetime_utc", desc=False)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return {
        "count": len(response.data),
        "start": start,
        "end": end,
        "offset": offset,
        "limit": limit,
        "data": response.data
    }


@app.get("/stats")
def get_stats():
    """
    Get summary statistics for all pool price data.
    """
    response = (
        supabase.table("pool_prices")
        .select("pool_price, rolling_30day_avg, begin_datetime_utc")
        .order("begin_datetime_utc", desc=False)
        .execute()
    )

    records = response.data

    if not records:
        raise HTTPException(status_code=404, detail="No data available")

    prices = [
        r["pool_price"] for r in records
        if r["pool_price"] is not None and r["pool_price"] > 0
    ]

    if not prices:
        raise HTTPException(status_code=404, detail="No valid price data available")

    return {
        "total_records": len(records),
        "valid_price_records": len(prices),
        "average_price": round(sum(prices) / len(prices), 4),
        "min_price": round(min(prices), 4),
        "max_price": round(max(prices), 4),
        "latest_record": records[-1]["begin_datetime_utc"],
        "earliest_record": records[0]["begin_datetime_utc"],
        "latest_30day_avg": records[-1]["rolling_30day_avg"]
    }