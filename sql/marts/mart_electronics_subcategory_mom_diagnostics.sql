CREATE OR REPLACE TABLE mart_electronics_subcategory_mom_diagnostics AS

WITH october AS (
    SELECT *
    FROM mart_monthly_subcategory_performance
    WHERE event_month = '2019-10'
      AND category_l1 = 'electronics'
),

november AS (
    SELECT *
    FROM mart_monthly_subcategory_performance
    WHERE event_month = '2019-11'
      AND category_l1 = 'electronics'
),

joined AS (
    SELECT
        'electronics' AS category_l1,
        COALESCE(o.category_l2, n.category_l2) AS category_l2,

        COALESCE(o.purchase_revenue, 0) AS oct_purchase_revenue,
        COALESCE(n.purchase_revenue, 0) AS nov_purchase_revenue,

        COALESCE(o.purchase_events, 0) AS oct_purchase_events,
        COALESCE(n.purchase_events, 0) AS nov_purchase_events,

        COALESCE(o.cart_events, 0) AS oct_cart_events,
        COALESCE(n.cart_events, 0) AS nov_cart_events,

        COALESCE(o.active_users, 0) AS oct_active_users,
        COALESCE(n.active_users, 0) AS nov_active_users,

        o.session_view_to_cart_rate_pct AS oct_view_to_cart_rate_pct,
        n.session_view_to_cart_rate_pct AS nov_view_to_cart_rate_pct,

        o.session_view_to_purchase_rate_pct AS oct_view_to_purchase_rate_pct,
        n.session_view_to_purchase_rate_pct AS nov_view_to_purchase_rate_pct,

        o.session_cart_to_purchase_rate_pct AS oct_cart_to_purchase_rate_pct,
        n.session_cart_to_purchase_rate_pct AS nov_cart_to_purchase_rate_pct,

        o.strict_session_funnel_completion_rate_pct AS oct_strict_funnel_rate_pct,
        n.strict_session_funnel_completion_rate_pct AS nov_strict_funnel_rate_pct

    FROM october o
    FULL OUTER JOIN november n
        ON o.category_l2 = n.category_l2
),

diagnostics_base AS (
    SELECT
        category_l1,
        category_l2,

        oct_purchase_revenue,
        nov_purchase_revenue,
        ROUND(nov_purchase_revenue - oct_purchase_revenue, 2) AS revenue_delta,

        ROUND(
            100.0 * (nov_purchase_revenue - oct_purchase_revenue)
            / NULLIF(oct_purchase_revenue, 0),
            2
        ) AS revenue_growth_pct,

        oct_purchase_events,
        nov_purchase_events,
        nov_purchase_events - oct_purchase_events AS purchase_event_delta,

        ROUND(
            100.0 * (nov_purchase_events - oct_purchase_events)
            / NULLIF(oct_purchase_events, 0),
            2
        ) AS purchase_event_growth_pct,

        oct_cart_events,
        nov_cart_events,
        nov_cart_events - oct_cart_events AS cart_event_delta,

        ROUND(
            100.0 * (nov_cart_events - oct_cart_events)
            / NULLIF(oct_cart_events, 0),
            2
        ) AS cart_event_growth_pct,

        oct_active_users,
        nov_active_users,
        nov_active_users - oct_active_users AS active_user_delta,

        ROUND(
            100.0 * (nov_active_users - oct_active_users)
            / NULLIF(oct_active_users, 0),
            2
        ) AS active_user_growth_pct,

        oct_view_to_cart_rate_pct,
        nov_view_to_cart_rate_pct,
        ROUND(
            nov_view_to_cart_rate_pct - oct_view_to_cart_rate_pct,
            2
        ) AS view_to_cart_rate_change_pp,

        oct_view_to_purchase_rate_pct,
        nov_view_to_purchase_rate_pct,
        ROUND(
            nov_view_to_purchase_rate_pct - oct_view_to_purchase_rate_pct,
            2
        ) AS view_to_purchase_rate_change_pp,

        oct_cart_to_purchase_rate_pct,
        nov_cart_to_purchase_rate_pct,
        ROUND(
            nov_cart_to_purchase_rate_pct - oct_cart_to_purchase_rate_pct,
            2
        ) AS cart_to_purchase_rate_change_pp,

        oct_strict_funnel_rate_pct,
        nov_strict_funnel_rate_pct,
        ROUND(
            nov_strict_funnel_rate_pct - oct_strict_funnel_rate_pct,
            2
        ) AS strict_funnel_rate_change_pp

    FROM joined
)

SELECT
    *,
    ROUND(
        100.0 * nov_purchase_revenue
        / NULLIF(SUM(nov_purchase_revenue) OVER (), 0),
        2
    ) AS nov_electronics_revenue_share_pct

FROM diagnostics_base

ORDER BY revenue_delta DESC;