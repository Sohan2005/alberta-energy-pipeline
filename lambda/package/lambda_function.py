import os
from fetch import fetch_pool_prices
from transform import transform_records
from db import insert_records

def lambda_handler(event, context):
    print("Starting Alberta Energy Pipeline...")

    raw = fetch_pool_prices()

    if not raw:
        print("No records fetched - exiting")
        return {
            "statusCode": 200,
            "body": "No new records to insert"
        }

    cleaned = transform_records(raw)
    result = insert_records(cleaned)

    print(f"Pipeline complete. Processed {len(cleaned)} records.")

    return {
        "statusCode": 200,
        "body": f"Successfully processed {len(cleaned)} records"
    }