# Alberta Energy Pipeline

A cloud-native serverless data pipeline that automatically captures Alberta
electricity pool prices from the AESO API daily, stores them in PostgreSQL,
and exposes them through a live REST API with a real-time visualization dashboard.

## 🚀 Live Demo

👉 **https://alberta-energy-pipeline.onrender.com**

📖 API Docs: https://alberta-energy-pipeline.onrender.com/docs

---

## Why This Exists

The AESO (Alberta Electric System Operator) publishes real-time electricity
pool prices - the wholesale price paid to generators every hour. These prices
are volatile and economically significant: on March 30, 2026 prices spiked to
**$322/MWh**, and on April 2, 2026 they dropped to **$0/MWh** due to excess
renewable generation. Both events are captured in this dataset.

The problem: the AESO's public API only retains approximately 30 days of data.
Once a record ages out, it's gone from the API permanently.

This pipeline solves that by running automatically every morning, capturing
the previous day's settled prices, and writing them to a structured PostgreSQL
database that grows indefinitely. What started as 24 records is now a
queryable historical archive - and it adds ~24 new records every day without
any manual intervention.

---

## Architecture

```
AESO Pool Price API
        ↓
AWS Lambda (Python 3.11)         - fetches and cleans daily price data
        ↓
Amazon EventBridge               - fires Lambda every day at 10:00 AM UTC
        ↓
Supabase (PostgreSQL)            - structured, indexed, queryable storage
        ↓
FastAPI REST API                 - public endpoints for querying the data
        ↓
Render                           - live cloud deployment
        ↓
https://alberta-energy-pipeline.onrender.com
```

Every component runs in the cloud. Nothing depends on a local machine being on.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Serverless compute | AWS Lambda (Python 3.11) |
| Scheduling | Amazon EventBridge (`cron(0 10 * * ? *)`) |
| Database | Supabase (PostgreSQL) |
| API framework | FastAPI + Uvicorn |
| Deployment | Render |
| Data source | AESO Public Pool Price API |
| Frontend | Vanilla JS + Chart.js |

---

## What the Data Shows

Each record represents one hour of Alberta's electricity market.

**Sample record (JSON):**

```json
{
  "begin_datetime_utc": "2026-03-30T17:00:00",
  "begin_datetime_mpt": "2026-03-30T11:00:00",
  "pool_price": 322.74,
  "forecast_pool_price": 602.13,
  "rolling_30day_avg": 34.14
}
```

**Field reference:**

| Field | Description |
|---|---|
| `begin_datetime_utc` | Hour start time in UTC |
| `begin_datetime_mpt` | Hour start time in Mountain Time |
| `pool_price` | Actual settled price paid to Alberta generators ($/MWh) |
| `forecast_pool_price` | Market forecast price for that hour ($/MWh) |
| `rolling_30day_avg` | 30-day rolling average price for trend context ($/MWh) |

Records where `pool_price` is `0` are real - they occur when excess wind or
solar generation causes prices to clear at zero. This is an increasingly
common event in Alberta's grid.

---

## Key Design Decisions

**Upsert instead of insert** - The pipeline uses upsert logic on
`begin_datetime_utc` as the unique key. Running the pipeline twice on the same
day updates records rather than creating duplicates. This makes the system safe
to re-run at any time.

**Fail fast on bad data** - If the API returns unsettled future hours
(empty `pool_price`), the pipeline filters them out before any database write.
No bad data reaches storage and no API credits are wasted.

**Pinned Lambda runtime** - Dependencies are compiled against Amazon Linux
using the official AWS Lambda Docker image. Building on Windows and uploading
Windows binaries to Lambda causes silent `ELF` architecture errors -
this pipeline avoids that by building in the correct environment.

**Indexed schema** - The `pool_prices` table has indexes on
`begin_datetime_utc`, `begin_datetime_mpt`, and `pool_price` so range queries
and stat aggregations stay fast as the dataset grows.

---

## Pipeline Schedule

The pipeline runs automatically at **10:00 AM UTC (4:00 AM Mountain)** every day.
AESO settles the previous day's prices overnight, so the 10 AM UTC trigger
gives enough buffer for all hours to be finalized before the pipeline runs.
