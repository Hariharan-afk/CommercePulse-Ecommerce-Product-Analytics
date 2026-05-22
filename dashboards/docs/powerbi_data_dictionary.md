# CommercePulse Power BI Data Dictionary

This document describes the CSV files exported for the CommercePulse Power BI dashboard.

---

## 1. `monthly_kpis.csv`

**Source Mart:** `mart_monthly_kpis`

**Purpose:**  
Executive-level monthly platform performance comparison.

**Core fields:**
- `event_month`
- `total_events`
- `active_users`
- `active_sessions`
- `purchase_events`
- `purchase_revenue`
- `avg_purchase_price`
- `session_view_to_cart_rate_pct`
- `session_view_to_purchase_rate_pct`
- `session_cart_to_purchase_rate_pct`
- `strict_session_funnel_completion_rate_pct`

**Primary dashboard use:**
- KPI cards
- Monthly revenue comparison
- Monthly funnel comparison

---

## 2. `monthly_category_performance.csv`

**Source Mart:** `mart_monthly_category_performance`

**Purpose:**  
Category-level monthly performance and funnel metrics.

**Core fields:**
- `event_month`
- `category_l1`
- `purchase_revenue`
- `purchase_events`
- `active_users`
- `cart_events`
- `session_cart_to_purchase_rate_pct`

**Primary dashboard use:**
- Revenue by category
- Cart-to-purchase conversion by category
- Category-level October vs. November comparison

---

## 3. `category_mom_diagnostics.csv`

**Source Mart:** `mart_category_mom_diagnostics`

**Purpose:**  
Month-over-month category growth diagnostics.

**Core fields:**
- `category_l1`
- `oct_purchase_revenue`
- `nov_purchase_revenue`
- `revenue_delta`
- `revenue_growth_pct`
- `cart_to_purchase_rate_change_pp`

**Primary dashboard use:**
- Categories driving revenue growth
- Categories with declining conversion efficiency

---

## 4. `electronics_subcategory_mom_diagnostics.csv`

**Source Mart:** `mart_electronics_subcategory_mom_diagnostics`

**Purpose:**  
Subcategory diagnostics within electronics.

**Core fields:**
- `category_l2`
- `nov_purchase_revenue`
- `nov_electronics_revenue_share_pct`
- `revenue_delta`
- `revenue_growth_pct`
- `cart_to_purchase_rate_change_pp`

**Primary dashboard use:**
- Smartphone dominance in electronics
- Subcategories driving electronics growth
- Electronics subcategory conversion decline

---

## 5. `smartphone_brand_mom_diagnostics.csv`

**Source Mart:** `mart_smartphone_brand_mom_diagnostics`

**Purpose:**  
Brand-level smartphone growth and conversion diagnostics.

**Core fields:**
- `brand`
- `nov_purchase_revenue`
- `nov_smartphone_revenue_share_pct`
- `revenue_delta`
- `net_smartphone_revenue_growth_share_pct`
- `cart_to_purchase_rate_change_pp`

**Primary dashboard use:**
- Apple vs. Samsung growth comparison
- Top smartphone brands by revenue
- Brand-level conversion deterioration

---

## 6. `smartphone_price_band_mom_diagnostics.csv`

**Source Mart:** `mart_smartphone_price_band_mom_diagnostics`

**Purpose:**  
Smartphone growth and funnel behavior by price tier.

**Core fields:**
- `price_band_order`
- `price_band`
- `nov_purchase_revenue`
- `nov_smartphone_revenue_share_pct`
- `revenue_delta`
- `net_smartphone_revenue_growth_share_pct`
- `cart_to_purchase_rate_change_pp`

**Primary dashboard use:**
- Premium vs. mid-range vs. value growth
- Price bands contributing to revenue
- Price bands with declining funnel efficiency

---

## 7. `smartphone_brand_price_band_mom_diagnostics.csv`

**Source Mart:** `mart_smartphone_brand_price_band_mom_diagnostics`

**Purpose:**  
Detailed brand × price-band performance diagnostics.

**Core fields:**
- `brand`
- `price_band_order`
- `price_band`
- `nov_purchase_revenue`
- `revenue_delta`
- `net_smartphone_revenue_growth_share_pct`
- `cart_to_purchase_rate_change_pp`

**Primary dashboard use:**
- Opportunity matrix
- Highest-growth brand-price segments
- Highest-risk conversion-decline segments

---

## Modeling Notes

- Revenue values are based on purchase-event `price` totals.
- Conversion metrics are computed at the session level using ordered funnel logic.
- Growth-share percentages are relative to net growth; positive contributors may sum to more than 100% if other segments decline.
- `unknown` category/brand values represent missing source metadata retained for transparency.
