CREATE OR REPLACE TABLE mart_monthly_subcategory_performance AS

WITH subcategory_events AS (
    SELECT
        event_month,

        COALESCE(category_l1, 'unknown') AS category_l1,

        CASE
            WHEN category_l1 IS NULL THEN 'unknown'
            ELSE COALESCE(category_l2, 'unspecified')
        END AS category_l2,

        COUNT(*) AS total_events,

        COUNT(*) FILTER (WHERE event_type = 'view') AS view_events,
        COUNT(*) FILTER (WHERE event_type = 'cart') AS cart_events,
        COUNT(*) FILTER (WHERE event_type = 'purchase') AS purchase_events,

        COUNT(DISTINCT user_id) AS active_users,
        COUNT(DISTINCT user_session) AS active_sessions,
        COUNT(DISTINCT product_id) AS active_products,

        COUNT(DISTINCT user_id)
            FILTER (WHERE event_type = 'purchase') AS purchasing_users,

        SUM(price)
            FILTER (WHERE event_type = 'purchase') AS purchase_revenue,

        AVG(price)
            FILTER (WHERE event_type = 'purchase') AS avg_purchase_price

    FROM stg_events
    GROUP BY
        event_month,
        COALESCE(category_l1, 'unknown'),
        CASE
            WHEN category_l1 IS NULL THEN 'unknown'
            ELSE COALESCE(category_l2, 'unspecified')
        END
),

subcategory_session_steps AS (
    SELECT
        event_month,

        COALESCE(category_l1, 'unknown') AS category_l1,

        CASE
            WHEN category_l1 IS NULL THEN 'unknown'
            ELSE COALESCE(category_l2, 'unspecified')
        END AS category_l2,

        user_session,

        MIN(event_ts)
            FILTER (WHERE event_type = 'view') AS first_view_ts,

        MIN(event_ts)
            FILTER (WHERE event_type = 'cart') AS first_cart_ts,

        MIN(event_ts)
            FILTER (WHERE event_type = 'purchase') AS first_purchase_ts

    FROM stg_events
    WHERE user_session IS NOT NULL
    GROUP BY
        event_month,
        COALESCE(category_l1, 'unknown'),
        CASE
            WHEN category_l1 IS NULL THEN 'unknown'
            ELSE COALESCE(category_l2, 'unspecified')
        END,
        user_session
),

subcategory_funnel AS (
    SELECT
        event_month,
        category_l1,
        category_l2,

        COUNT(*) FILTER (
            WHERE first_view_ts IS NOT NULL
        ) AS sessions_with_view,

        COUNT(*) FILTER (
            WHERE first_view_ts IS NOT NULL
              AND first_cart_ts IS NOT NULL
              AND first_cart_ts >= first_view_ts
        ) AS sessions_cart_after_view,

        COUNT(*) FILTER (
            WHERE first_view_ts IS NOT NULL
              AND first_purchase_ts IS NOT NULL
              AND first_purchase_ts >= first_view_ts
        ) AS sessions_purchase_after_view,

        COUNT(*) FILTER (
            WHERE first_cart_ts IS NOT NULL
              AND first_purchase_ts IS NOT NULL
              AND first_purchase_ts >= first_cart_ts
        ) AS sessions_purchase_after_cart,

        COUNT(*) FILTER (
            WHERE first_view_ts IS NOT NULL
              AND first_cart_ts IS NOT NULL
              AND first_purchase_ts IS NOT NULL
              AND first_cart_ts >= first_view_ts
              AND first_purchase_ts >= first_cart_ts
        ) AS strict_funnel_complete_sessions

    FROM subcategory_session_steps
    GROUP BY
        event_month,
        category_l1,
        category_l2
)

SELECT
    e.event_month,
    e.category_l1,
    e.category_l2,

    e.total_events,
    e.view_events,
    e.cart_events,
    e.purchase_events,

    e.active_users,
    e.active_sessions,
    e.active_products,
    e.purchasing_users,

    ROUND(COALESCE(e.purchase_revenue, 0), 2) AS purchase_revenue,
    ROUND(e.avg_purchase_price, 2) AS avg_purchase_price,

    f.sessions_with_view,
    f.sessions_cart_after_view,
    f.sessions_purchase_after_view,
    f.sessions_purchase_after_cart,
    f.strict_funnel_complete_sessions,

    ROUND(
        100.0 * f.sessions_cart_after_view
        / NULLIF(f.sessions_with_view, 0),
        2
    ) AS session_view_to_cart_rate_pct,

    ROUND(
        100.0 * f.sessions_purchase_after_view
        / NULLIF(f.sessions_with_view, 0),
        2
    ) AS session_view_to_purchase_rate_pct,

    ROUND(
        100.0 * f.sessions_purchase_after_cart
        / NULLIF(f.sessions_cart_after_view, 0),
        2
    ) AS session_cart_to_purchase_rate_pct,

    ROUND(
        100.0 * f.strict_funnel_complete_sessions
        / NULLIF(f.sessions_with_view, 0),
        2
    ) AS strict_session_funnel_completion_rate_pct

FROM subcategory_events e
LEFT JOIN subcategory_funnel f
    ON e.event_month = f.event_month
   AND e.category_l1 = f.category_l1
   AND e.category_l2 = f.category_l2

ORDER BY
    e.event_month,
    e.category_l1,
    purchase_revenue DESC;