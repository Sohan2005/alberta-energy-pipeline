def parse_float(value):
    """
    Safely convert a string value to float.
    Returns None if value is missing or cannot be converted.
    """
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (ValueError, TypeError):
        return None


def clean_record(raw):
    return {
        "begin_datetime_utc": raw.get("begin_datetime_utc"),
        "begin_datetime_mpt": raw.get("begin_datetime_mpt"),
        "pool_price": parse_float(raw.get("pool_price")),
        "forecast_pool_price": parse_float(raw.get("forecast_pool_price")),
        "rolling_30day_avg": parse_float(raw.get("rolling_30day_avg"))
    }


def transform_records(raw_records):
    cleaned = []
    skipped = 0

    for record in raw_records:
        try:
            cleaned.append(clean_record(record))
        except Exception as e:
            print(f"Skipping bad record: {e}")
            skipped += 1

    if skipped > 0:
        print(f"Warning: skipped {skipped} records during transformation")

    print(f"Transformed {len(cleaned)} records successfully")
    return cleaned