import requests
import os
from dotenv import load_dotenv

load_dotenv()

AESO_API_KEY = os.getenv("AESO_API_KEY")
BASE_URL = "https://apimgw.aeso.ca/public/poolprice-api/v1.1/price/poolPrice"

def fetch_pool_prices():
    params = {
        "startDate": "2026-03-30",
        "endDate": "2026-03-31"
    }

    headers = {
        "API-KEY": AESO_API_KEY
    }

    response = requests.get(BASE_URL, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()
    records = data["return"]["Pool Price Report"]

    print(f"Fetched {len(records)} records")
    for record in records[:3]:
        print(record)

    return records

if __name__ == "__main__":
    fetch_pool_prices()