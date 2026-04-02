import os
from fastapi import FastAPI
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Alberta Energy API",
    description="REST API for Alberta electricity pool price data",
    version="1.0.0"
)

@app.get("/health")
def health():
    # creating a new client on every request
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )
    return {"status": "ok"}

@app.get("/records")
def get_records():
    # creating a new client on every request
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )
    response = supabase.table("pool_prices").select("*").execute()
    return response.data