CREATE TABLE pool_prices (
    id SERIAL PRIMARY KEY,
    begin_datetime_utc TIMESTAMP NOT NULL,
    begin_datetime_mpt TIMESTAMP NOT NULL,
    pool_price NUMERIC(10, 4),
    forecast_pool_price NUMERIC(10, 4),
    rolling_30day_avg NUMERIC(10, 4),
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_pool_price_record
        UNIQUE (begin_datetime_utc)
);