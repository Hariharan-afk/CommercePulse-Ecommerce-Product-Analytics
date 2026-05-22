# CommercePulse Data Dictionary

## Overview

This document describes the main datasets, exported dashboard tables, warehouse marts, and metrics used in the CommercePulse project.

CommercePulse analyzes October–November 2019 e-commerce event data to diagnose revenue growth, funnel deterioration, category performance, and smartphone segment dynamics.

---

## Raw Dataset

### Source Files

```text
data/raw/2019-Oct.csv
data/raw/2019-Nov.csv
```

### Raw Event Columns

| Column | Description |
|---|---|
| `event_time` | Timestamp of the event |
| `event_type` | Type of user event: view, cart, or purchase |
| `product_id` | Product identifier |
| `category_id` | Numeric category identifier |
| `category_code` | Hierarchical category path, such as electronics.smartphone |
| `brand` | Product brand |
| `price` | Product price at event time |
| `user_id` | User identifier |
| `user_session` | Session identifier |

---

## Cleaned Event Layer

### Location

```text
data/interim/events_clean/
```

### Description

The cleaned event layer is generated from raw CSV files and stored as partitioned Parquet files.

### Cleaned Columns

| Column | Description |
|---|---|
| `event_ts` | Parsed event timestamp |
| `event_date` | Event date |
| `event_month` | Event month in YYYY-MM format |
| `event_day` | Event day |
| `event_hour` | Hour of day |
| `event_type` | Lowercase event type |
| `product_id` | Product identifier |
| `category_id` | Category identifier |
| `category_code` | Original hierarchical category code |
| `brand` | Lowercase cleaned brand |
| `price` | Product price |
| `user_id` | User identifier |
| `user_session` | Session identifier |
| `source_file` | Source CSV file path |

---

## Staging View

### `stg_events`

The staging view reads from cleaned Parquet files and adds parsed category levels.

| Column | Description |
|---|---|
| `event_ts` | Event timestamp |
| `event_date` | Event date |
| `event_month` | Event month |
| `event_day` | Event day |
| `event_hour` | Event hour |
| `event_type` | Event type |
| `product_id` | Product identifier |
| `category_id` | Category identifier |
| `category_code` | Full category code |
| `category_l1` | Top-level category |
| `category_l2` | Second-level category |
| `category_l3` | Third-level category |
| `category_l4` | Fourth-level category |
| `brand` | Product brand |
| `price` | Product price |
| `user_id` | User identifier |
| `user_session` | User session |
| `source_file` | Source file |

---

## Warehouse Marts

### 1. `mart_monthly_kpis`

Platform-level monthly KPI table.

| Column | Description |
|---|---|
| `event_month` | Month |
| `total_events` | Total number of events |
| `view_events` | Number of view events |
| `cart_events` | Number of cart events |
| `purchase_events` | Number of purchase events |
| `active_users` | Number of unique users |
| `active_sessions` | Number of unique sessions |
| `active_products` | Number of unique products |
| `purchasing_users` | Number of users with purchase events |
| `purchase_revenue` | Sum of purchase-event prices |
| `avg_purchase_price` | Average price for purchase events |
| `sessions_with_view` | Sessions with at least one view |
| `sessions_cart_after_view` | Sessions where cart occurred after view |
| `sessions_purchase_after_view` | Sessions where purchase occurred after view |
| `sessions_purchase_after_cart` | Sessions where purchase occurred after cart |
| `strict_funnel_complete_sessions` | Sessions with ordered view → cart → purchase |
| `session_view_to_cart_rate_pct` | Session-level view-to-cart rate |
| `session_view_to_purchase_rate_pct` | Session-level view-to-purchase rate |
| `session_cart_to_purchase_rate_pct` | Session-level cart-to-purchase rate |
| `strict_session_funnel_completion_rate_pct` | Ordered view → cart → purchase completion rate |
| `event_view_to_cart_rate_pct` | Event-level cart/view ratio |
| `event_view_to_purchase_rate_pct` | Event-level purchase/view ratio |

---

### 2. `mart_monthly_category_performance`

Monthly category-level performance table.

| Column | Description |
|---|---|
| `event_month` | Month |
| `category_l1` | Top-level category |
| `total_events` | Total events in category |
| `view_events` | View events in category |
| `cart_events` | Cart events in category |
| `purchase_events` | Purchase events in category |
| `active_users` | Unique active users |
| `active_sessions` | Unique active sessions |
| `active_products` | Unique active products |
| `purchasing_users` | Unique purchasing users |
| `purchase_revenue` | Purchase revenue |
| `avg_purchase_price` | Average purchase price |
| `session_view_to_cart_rate_pct` | View-to-cart session rate |
| `session_view_to_purchase_rate_pct` | View-to-purchase session rate |
| `session_cart_to_purchase_rate_pct` | Cart-to-purchase session rate |
| `strict_session_funnel_completion_rate_pct` | Strict ordered funnel completion rate |

---

### 3. `mart_category_mom_diagnostics`

Month-over-month category diagnostics table.

| Column | Description |
|---|---|
| `category_l1` | Top-level category |
| `oct_purchase_revenue` | October purchase revenue |
| `nov_purchase_revenue` | November purchase revenue |
| `revenue_delta` | November revenue minus October revenue |
| `revenue_growth_pct` | Revenue growth percentage |
| `oct_purchase_events` | October purchase events |
| `nov_purchase_events` | November purchase events |
| `purchase_event_delta` | Change in purchase events |
| `purchase_event_growth_pct` | Purchase event growth percentage |
| `oct_cart_events` | October cart events |
| `nov_cart_events` | November cart events |
| `cart_event_delta` | Change in cart events |
| `cart_event_growth_pct` | Cart event growth percentage |
| `oct_active_users` | October active users |
| `nov_active_users` | November active users |
| `active_user_delta` | Change in active users |
| `active_user_growth_pct` | Active user growth percentage |
| `oct_view_to_cart_rate_pct` | October view-to-cart rate |
| `nov_view_to_cart_rate_pct` | November view-to-cart rate |
| `view_to_cart_rate_change_pp` | View-to-cart percentage-point change |
| `oct_view_to_purchase_rate_pct` | October view-to-purchase rate |
| `nov_view_to_purchase_rate_pct` | November view-to-purchase rate |
| `view_to_purchase_rate_change_pp` | View-to-purchase percentage-point change |
| `oct_cart_to_purchase_rate_pct` | October cart-to-purchase rate |
| `nov_cart_to_purchase_rate_pct` | November cart-to-purchase rate |
| `cart_to_purchase_rate_change_pp` | Cart-to-purchase percentage-point change |
| `oct_strict_funnel_rate_pct` | October strict funnel completion |
| `nov_strict_funnel_rate_pct` | November strict funnel completion |
| `strict_funnel_rate_change_pp` | Strict funnel percentage-point change |

---

### 4. `mart_monthly_subcategory_performance`

Monthly subcategory-level performance table.

| Column | Description |
|---|---|
| `event_month` | Month |
| `category_l1` | Top-level category |
| `category_l2` | Second-level subcategory |
| `total_events` | Total events |
| `view_events` | View events |
| `cart_events` | Cart events |
| `purchase_events` | Purchase events |
| `active_users` | Unique users |
| `active_sessions` | Unique sessions |
| `active_products` | Unique products |
| `purchasing_users` | Unique purchasing users |
| `purchase_revenue` | Purchase revenue |
| `avg_purchase_price` | Average purchase price |
| `session_view_to_cart_rate_pct` | View-to-cart session rate |
| `session_view_to_purchase_rate_pct` | View-to-purchase session rate |
| `session_cart_to_purchase_rate_pct` | Cart-to-purchase session rate |
| `strict_session_funnel_completion_rate_pct` | Strict funnel completion rate |

---

### 5. `mart_electronics_subcategory_mom_diagnostics`

Month-over-month diagnostics for electronics subcategories.

| Column | Description |
|---|---|
| `category_l1` | Always electronics |
| `category_l2` | Electronics subcategory |
| `oct_purchase_revenue` | October revenue |
| `nov_purchase_revenue` | November revenue |
| `revenue_delta` | Revenue change |
| `revenue_growth_pct` | Revenue growth percentage |
| `cart_to_purchase_rate_change_pp` | Cart-to-purchase change |
| `nov_electronics_revenue_share_pct` | Share of November electronics revenue |

---

### 6. `mart_monthly_smartphone_brand_performance`

Monthly brand-level performance for smartphones.

| Column | Description |
|---|---|
| `event_month` | Month |
| `brand` | Smartphone brand |
| `total_events` | Total events |
| `view_events` | View events |
| `cart_events` | Cart events |
| `purchase_events` | Purchase events |
| `active_users` | Unique users |
| `active_sessions` | Unique sessions |
| `active_products` | Unique products |
| `purchase_revenue` | Purchase revenue |
| `avg_purchase_price` | Average purchase price |
| `session_view_to_cart_rate_pct` | View-to-cart session rate |
| `session_view_to_purchase_rate_pct` | View-to-purchase session rate |
| `session_cart_to_purchase_rate_pct` | Cart-to-purchase session rate |
| `strict_session_funnel_completion_rate_pct` | Strict funnel completion rate |

---

### 7. `mart_smartphone_brand_mom_diagnostics`

Month-over-month diagnostics for smartphone brands.

| Column | Description |
|---|---|
| `brand` | Smartphone brand |
| `oct_purchase_revenue` | October smartphone revenue |
| `nov_purchase_revenue` | November smartphone revenue |
| `revenue_delta` | Revenue change |
| `revenue_growth_pct` | Revenue growth percentage |
| `oct_purchase_events` | October purchase events |
| `nov_purchase_events` | November purchase events |
| `purchase_event_delta` | Purchase event change |
| `oct_cart_events` | October cart events |
| `nov_cart_events` | November cart events |
| `cart_event_delta` | Cart event change |
| `oct_active_users` | October active users |
| `nov_active_users` | November active users |
| `active_user_delta` | Active user change |
| `oct_avg_purchase_price` | October average purchase price |
| `nov_avg_purchase_price` | November average purchase price |
| `avg_purchase_price_delta` | Average purchase price change |
| `cart_to_purchase_rate_change_pp` | Cart-to-purchase change |
| `nov_smartphone_revenue_share_pct` | Share of November smartphone revenue |
| `net_smartphone_revenue_growth_share_pct` | Share of net smartphone revenue growth |

---

### 8. `mart_monthly_smartphone_price_band_performance`

Monthly smartphone price-band performance.

| Column | Description |
|---|---|
| `event_month` | Month |
| `price_band_order` | Numeric sorting key for price band |
| `price_band` | Smartphone price band |
| `total_events` | Total events |
| `view_events` | View events |
| `cart_events` | Cart events |
| `purchase_events` | Purchase events |
| `active_users` | Unique users |
| `active_sessions` | Unique sessions |
| `active_products` | Unique products |
| `purchase_revenue` | Purchase revenue |
| `avg_purchase_price` | Average purchase price |
| `session_cart_to_purchase_rate_pct` | Cart-to-purchase session rate |

---

### 9. `mart_smartphone_price_band_mom_diagnostics`

Month-over-month diagnostics by smartphone price band.

| Column | Description |
|---|---|
| `price_band_order` | Numeric sorting key |
| `price_band` | Price band |
| `oct_purchase_revenue` | October revenue |
| `nov_purchase_revenue` | November revenue |
| `revenue_delta` | Revenue change |
| `revenue_growth_pct` | Revenue growth percentage |
| `cart_to_purchase_rate_change_pp` | Cart-to-purchase change |
| `nov_smartphone_revenue_share_pct` | Share of November smartphone revenue |
| `net_smartphone_revenue_growth_share_pct` | Share of net smartphone revenue growth |

---

### 10. `mart_monthly_smartphone_brand_price_band_performance`

Monthly performance by smartphone brand and price band.

| Column | Description |
|---|---|
| `event_month` | Month |
| `brand` | Smartphone brand |
| `price_band_order` | Numeric price-band sorting key |
| `price_band` | Price band |
| `total_events` | Total events |
| `view_events` | View events |
| `cart_events` | Cart events |
| `purchase_events` | Purchase events |
| `active_users` | Unique users |
| `active_sessions` | Unique sessions |
| `active_products` | Unique products |
| `purchase_revenue` | Purchase revenue |
| `avg_purchase_price` | Average purchase price |
| `session_cart_to_purchase_rate_pct` | Cart-to-purchase session rate |

---

### 11. `mart_smartphone_brand_price_band_mom_diagnostics`

Month-over-month diagnostics by smartphone brand × price band.

| Column | Description |
|---|---|
| `brand` | Smartphone brand |
| `price_band_order` | Numeric price-band sorting key |
| `price_band` | Price band |
| `oct_purchase_revenue` | October revenue |
| `nov_purchase_revenue` | November revenue |
| `revenue_delta` | Revenue change |
| `revenue_growth_pct` | Revenue growth percentage |
| `cart_to_purchase_rate_change_pp` | Cart-to-purchase change |
| `nov_smartphone_revenue_share_pct` | Share of November smartphone revenue |
| `net_smartphone_revenue_growth_share_pct` | Share of net smartphone revenue growth |

---

## Dashboard CSV Exports

Power BI uses CSV files exported from DuckDB marts.

### Export Location

```text
dashboards/data/
```

### Exported Files

| CSV File | Source Mart |
|---|---|
| `monthly_kpis.csv` | `mart_monthly_kpis` |
| `monthly_category_performance.csv` | `mart_monthly_category_performance` |
| `category_mom_diagnostics.csv` | `mart_category_mom_diagnostics` |
| `electronics_subcategory_mom_diagnostics.csv` | `mart_electronics_subcategory_mom_diagnostics` |
| `smartphone_brand_mom_diagnostics.csv` | `mart_smartphone_brand_mom_diagnostics` |
| `smartphone_price_band_mom_diagnostics.csv` | `mart_smartphone_price_band_mom_diagnostics` |
| `smartphone_brand_price_band_mom_diagnostics.csv` | `mart_smartphone_brand_price_band_mom_diagnostics` |

---

## Price Bands

| Price Band | Definition |
|---|---|
| Non-positive / Unknown | Missing, zero, or negative price |
| Under $100 | 0 < price < 100 |
| $100–$249 | 100 ≤ price < 250 |
| $250–$499 | 250 ≤ price < 500 |
| $500–$799 | 500 ≤ price < 800 |
| $800–$1199 | 800 ≤ price < 1200 |
| $1200+ | price ≥ 1200 |

---

## Metric Definitions

### Purchase Revenue

Sum of `price` for purchase events.

```text
Purchase Revenue = SUM(price) where event_type = 'purchase'
```

---

### Revenue Delta

Difference between November and October purchase revenue.

```text
Revenue Delta = November Purchase Revenue - October Purchase Revenue
```

---

### Revenue Growth %

Percentage change in purchase revenue.

```text
Revenue Growth % = Revenue Delta / October Purchase Revenue
```

---

### View → Cart Rate

Percentage of sessions with a cart event after a view event.

```text
View → Cart Rate = Sessions with cart after view / Sessions with view
```

---

### View → Purchase Rate

Percentage of sessions with a purchase event after a view event.

```text
View → Purchase Rate = Sessions with purchase after view / Sessions with view
```

---

### Cart → Purchase Rate

Percentage of sessions with a purchase event after a cart event.

```text
Cart → Purchase Rate = Sessions with purchase after cart / Sessions with cart after view
```

---

### Cart → Purchase Change pp

Difference between November and October cart-to-purchase rate.

```text
Cart → Purchase Change pp = November Cart → Purchase Rate - October Cart → Purchase Rate
```

The unit is percentage points.

---

### Net Smartphone Revenue Growth Share %

Share of total net smartphone revenue growth contributed by a segment.

```text
Net Smartphone Revenue Growth Share % =
Segment Revenue Delta / Total Net Smartphone Revenue Delta
```

Positive contributors may sum to more than 100% if other segments have negative revenue deltas.

---

## Missing Data Handling

### Unknown Category

Rows with missing `category_code` are grouped as:

```text
unknown
```

This preserves financially meaningful uncategorized activity instead of dropping it.

### Unknown Brand

Rows with missing `brand` are grouped as:

```text
unknown
```

This allows dashboards to expose missing metadata as a visible data-quality segment.

---

## Notes

- Funnel metrics are session-level metrics.
- Funnel logic respects event order where applicable.
- Revenue metrics use purchase events only.
- Price bands are derived from event-level price.
- Growth-share values are relative to net growth and may exceed 100% in aggregate if other groups decline.