def clean_record(raw):
    return {
        "begin_datetime_utc": raw.get("begin_datetime_utc"),
        "begin_datetime_mpt": raw.get("begin_datetime_mpt"),
        "pool_price": raw.get("pool_price"),
        "forecast_pool_price": raw.get("forecast_pool_price"),
        "rolling_30day_avg": raw.get("rolling_30day_avg")
    }

def transform_records(raw_records):
    cleaned = []
    for record in raw_records:
        try:
            cleaned.append(clean_record(record))
        except Exception as e:
            print(f"Skipping bad record: {e}")
    print(f"Transformed {len(cleaned)} records")
    return cleaned