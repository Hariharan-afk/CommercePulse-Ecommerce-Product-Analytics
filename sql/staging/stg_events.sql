CREATE OR REPLACE VIEW stg_events AS
SELECT
    event_ts,
    event_date,
    event_month,
    event_day,
    event_hour,
    event_type,

    product_id,
    category_id,
    category_code,

    SPLIT_PART(category_code, '.', 1) AS category_l1,
    NULLIF(SPLIT_PART(category_code, '.', 2), '') AS category_l2,
    NULLIF(SPLIT_PART(category_code, '.', 3), '') AS category_l3,
    NULLIF(SPLIT_PART(category_code, '.', 4), '') AS category_l4,

    brand,
    price,

    user_id,
    user_session,
    source_file

FROM read_parquet(
    '__EVENTS_PARQUET_GLOB__',
    hive_partitioning = true
);