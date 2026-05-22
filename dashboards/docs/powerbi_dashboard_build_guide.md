# CommercePulse Power BI Dashboard Build Guide

## Dashboard Objective

Build an executive-friendly product analytics dashboard that explains:

1. What changed from October to November?
2. Which categories drove growth?
3. Why did cart-to-purchase efficiency deteriorate?
4. Which electronics, smartphone, brand, and price-band segments matter most?

---

## Recommended Dashboard Pages

### Page 1 — Executive Overview
**Data source:** `monthly_kpis.csv`

Suggested visuals:
- KPI cards:
  - Total Events
  - Active Users
  - Sessions
  - Purchase Revenue
  - Purchase Events
- Clustered column:
  - October vs. November revenue
- KPI cards or arrows:
  - View → Cart
  - View → Purchase
  - Cart → Purchase
- Text callout:
  - “November revenue grew, but cart-to-purchase efficiency declined.”

---

### Page 2 — Category Growth Diagnostics
**Data sources:**
- `monthly_category_performance.csv`
- `category_mom_diagnostics.csv`

Suggested visuals:
- Bar chart:
  - Revenue delta by category
- Bar chart:
  - Cart-to-purchase rate change by category
- Scatter plot:
  - X = revenue delta
  - Y = cart-to-purchase rate change
  - Size = November revenue
- Highlight electronics as both:
  - top growth driver
  - largest major conversion decline

---

### Page 3 — Electronics Subcategory Drill-Down
**Data source:** `electronics_subcategory_mom_diagnostics.csv`

Suggested visuals:
- Treemap or bar chart:
  - November electronics revenue by subcategory
- Bar chart:
  - Revenue delta by electronics subcategory
- Bar chart:
  - Cart-to-purchase decline by subcategory
- Callout:
  - Smartphones generated the overwhelming share of electronics revenue.

---

### Page 4 — Smartphone Brand Diagnostics
**Data source:** `smartphone_brand_mom_diagnostics.csv`

Suggested visuals:
- Revenue share bar chart:
  - Apple, Samsung, Xiaomi, etc.
- Growth contribution bar chart:
  - Revenue delta by brand
- Decline chart:
  - Cart-to-purchase rate change by brand
- Highlight:
  - Apple and Samsung dominate smartphone growth.

---

### Page 5 — Smartphone Price-Band Diagnostics
**Data source:** `smartphone_price_band_mom_diagnostics.csv`

Suggested visuals:
- Revenue by price band
- Revenue delta by price band
- Cart-to-purchase conversion change by price band
- Key insight callout:
  - Premium bands drove the largest share of revenue growth.

---

### Page 6 — Brand × Price-Band Opportunity Matrix
**Data source:** `smartphone_brand_price_band_mom_diagnostics.csv`

Suggested visuals:
- Scatter plot:
  - X = revenue delta
  - Y = cart-to-purchase rate change
  - Size = November revenue
  - Detail = brand + price band
- Matrix table:
  - Brand rows
  - Price-band columns
  - Values = revenue delta or conversion change
- Highlight:
  - Apple `$800-$1199`
  - Apple `$1200+`
  - Samsung `$100-$249`
  - Samsung `$250-$499`

---

## Recommended Slicers

- Category
- Subcategory
- Brand
- Price Band

Use slicers selectively; do not overload every page.

---

## Visual Storyline

The dashboard should guide the reader through this sequence:

1. November grew materially in traffic and revenue.
2. Funnel quality weakened after carting.
3. Electronics drove most growth and much of the conversion deterioration.
4. Smartphones explain most electronics growth.
5. Apple and Samsung dominate smartphone expansion.
6. Premium Apple and selected Samsung segments explain the most actionable commercial shifts.

---

## Design Guidance

- Use a clean executive/business style.
- Prefer:
  - KPI cards
  - horizontal bars
  - scatter plots
  - matrix tables
- Avoid overly decorative visuals.
- Keep every page to one main question.
- Add short text annotations explaining the “so what.”
