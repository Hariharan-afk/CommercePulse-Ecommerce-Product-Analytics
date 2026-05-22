# CommercePulse Dashboard Walkthrough

## Overview

The CommercePulse Power BI dashboard is a six-page executive analytics dashboard built to explain why November 2019 revenue and cart activity increased while cart-to-purchase conversion declined.

The dashboard follows a layered diagnostic path:

```text
Executive KPIs
↓
Category Growth
↓
Electronics Subcategories
↓
Smartphone Brands
↓
Smartphone Price Bands
↓
Brand × Price-Band Opportunity Matrix
```

Each page answers one specific business question and progressively narrows the analysis from platform-level trends to specific commercial segments.

---

## Page 1 — Executive Overview

### Business Question

What changed between October and November 2019 at the overall platform level?

### Purpose

This page provides a high-level summary of platform growth, revenue movement, and funnel performance.

### Key Visuals

- November Purchase Revenue KPI
- November Sessions KPI
- November Active Users KPI
- November Purchase Events KPI
- Revenue Growth vs. October
- View → Cart Change
- Cart → Purchase Change
- Purchase Revenue by Month
- Session Funnel Rates by Month

### Key Metrics

| Metric | October 2019 | November 2019 | Change |
|---|---:|---:|---:|
| Purchase Revenue | $229.96M | $275.19M | +19.67% |
| Sessions | 9.24M | 13.78M | Increased |
| Active Users | 3.02M | 3.70M | Increased |
| Purchase Events | 742.85K | 916.94K | Increased |
| View → Cart Rate | 6.18% | 12.57% | +6.39 pp |
| Cart → Purchase Rate | 49.17% | 37.10% | -12.07 pp |

### Main Insight

November revenue and activity increased sharply, but downstream funnel quality weakened. Users added products to carts at a higher rate, while cart-to-purchase conversion declined.

### Interpretation

This page establishes the central business problem. The platform performed better in terms of traffic and revenue, but the conversion path after carting became weaker. This motivates the deeper diagnostic pages.

---

## Page 2 — Category Growth Diagnostics

### Business Question

Which top-level categories drove November revenue growth, and where did cart-to-purchase efficiency weaken?

### Purpose

This page identifies the category-level drivers of growth and conversion risk.

### Key Visuals

- Electronics Revenue Delta KPI
- Electronics Cart → Purchase Change KPI
- Unknown Revenue Delta KPI
- Top Category Revenue Growth Drivers
- Largest Cart → Purchase Declines by Category
- Growth vs. Conversion Risk by Category scatter plot

### Main Findings

| Category | Revenue Delta | Cart → Purchase Change |
|---|---:|---:|
| Electronics | +$28.79M | -11.35 pp |
| Unknown | +$6.96M | Negative |
| Appliances | +$5.06M | Negative |
| Computers | +$2.62M | Negative |

### Main Insight

November revenue growth was concentrated in a small number of categories. Electronics was the largest growth driver, but it also experienced a major cart-to-purchase decline.

### Interpretation

Electronics is both a growth opportunity and a conversion-risk segment. It should be prioritized for deeper diagnostics because it has the largest commercial impact.

---

## Page 3 — Electronics → Smartphone Drill-Down

### Business Question

Within electronics, which subcategories drove growth and conversion deterioration?

### Purpose

This page narrows the category-level analysis into electronics subcategories.

### Key Visuals

- Smartphone November Revenue KPI
- Smartphone Electronics Revenue Share KPI
- Smartphone Revenue Delta KPI
- Smartphone Cart → Purchase Change KPI
- Electronics Revenue Concentration by Subcategory
- Electronics Revenue Growth by Subcategory
- Cart → Purchase Change by Electronics Subcategory

### Key Metrics

| Metric | Value |
|---|---:|
| Smartphone November Revenue | $177.82M |
| Smartphone Share of Electronics Revenue | 86.64% |
| Smartphone Revenue Delta | +$20.77M |
| Smartphone Cart → Purchase Change | -11.65 pp |

### Main Insight

Smartphones generated the majority of electronics revenue and contributed the largest electronics revenue increase. However, smartphone cart-to-purchase conversion also declined sharply.

### Interpretation

The electronics story is primarily a smartphone story. Smartphones become the most important subcategory for deeper brand and price-band analysis.

---

## Page 4 — Smartphone Brand Diagnostics

### Business Question

Which smartphone brands drove November growth, and which brands experienced weaker cart-to-purchase conversion?

### Purpose

This page identifies the smartphone brands responsible for growth and conversion risk.

### Key Visuals

- Apple November Revenue KPI
- Apple Smartphone Revenue Share KPI
- Apple Revenue Delta KPI
- Apple Cart → Purchase Change KPI
- November Smartphone Revenue by Brand
- Smartphone Revenue Growth by Brand
- Cart → Purchase Change by Smartphone Brand

### Key Metrics

| Brand | November Revenue | Revenue Share | Revenue Delta | Cart → Purchase Change |
|---|---:|---:|---:|---:|
| Apple | $115.26M | 64.82% | +$12.71M | -12.07 pp |
| Samsung | $42.71M | 24.02% | +$5.34M | -10.97 pp |
| Xiaomi | $9.84M | 5.54% | Positive | Negative |

### Main Insight

Apple and Samsung dominated smartphone revenue and accounted for most smartphone revenue growth. Apple was the highest-priority brand because it combined the largest revenue base, largest revenue increase, and a major cart-to-purchase decline.

### Interpretation

The smartphone funnel issue is not evenly distributed across brands. Apple is the most commercially important diagnostic target, followed by Samsung.

---

## Page 5 — Smartphone Price-Band Diagnostics

### Business Question

Were smartphone growth and funnel deterioration concentrated in premium, mid-range, or budget price tiers?

### Purpose

This page investigates smartphone performance by price band.

### Key Visuals

- $800–$1199 Revenue Delta KPI
- $800–$1199 Growth Share KPI
- $800–$1199 Cart → Purchase Change KPI
- $1200+ Revenue Delta KPI
- November Smartphone Revenue by Price Band
- Smartphone Revenue Growth by Price Band
- Cart → Purchase Change by Smartphone Price Band

### Key Metrics

| Price Band | November Revenue | Revenue Delta | Net Growth Share | Cart → Purchase Change |
|---|---:|---:|---:|---:|
| $800–$1199 | $50.91M | +$9.15M | 44.06% | -13.53 pp |
| $1200+ | $39.80M | +$5.90M | 28.38% | Negative |
| $100–$249 | $30.14M | +$6.29M | 30.29% | Negative |
| $250–$499 | Declined | Negative | Negative | Sharp decline |

### Main Insight

Premium smartphone tiers drove much of November growth, especially $800–$1199 and $1200+. The $100–$249 value band also expanded meaningfully.

### Interpretation

The $800–$1199 band was the most important price segment because it had the largest revenue lift while also showing a major cart-to-purchase decline.

---

## Page 6 — Brand × Price-Band Opportunity Matrix

### Business Question

Which exact brand-price combinations drove smartphone growth and conversion deterioration?

### Purpose

This page combines brand and price-band dimensions to isolate the most actionable commercial segments.

### Key Visuals

- Apple $800–$1199 Revenue Delta KPI
- Apple $1200+ Revenue Delta KPI
- Samsung $100–$249 Revenue Delta KPI
- Samsung $250–$499 Cart → Purchase Change KPI
- Revenue Growth by Brand × Price Band
- Cart → Purchase Change by Brand × Price Band
- Growth vs. Conversion Risk by Brand × Price Band scatter plot

### Key Segments

| Segment | Signal |
|---|---|
| Apple $800–$1199 | Largest smartphone growth contributor |
| Apple $1200+ | Major premium growth contributor |
| Samsung $100–$249 | Major value-tier growth pocket |
| Samsung $250–$499 | Underperformance segment |

### Main Insight

Smartphone growth was concentrated in a few brand-price segments. Apple premium tiers and Samsung value-tier segments explained most smartphone growth, while Samsung $250–$499 stood out as an underperformance segment.

### Interpretation

This page provides the most actionable diagnostic layer. It shows that the November shift was not only category-driven or brand-driven. It was concentrated in specific commercial combinations.

---

## Final Dashboard Story

The dashboard reveals a clear business pattern:

1. November platform activity and revenue increased.
2. Carting activity rose sharply.
3. Cart-to-purchase conversion declined.
4. Electronics drove most revenue growth.
5. Smartphones dominated electronics.
6. Apple and Samsung drove smartphone growth.
7. Premium smartphone tiers were major growth drivers.
8. Apple premium tiers and Samsung value-tier segments explained the most important growth pockets.
9. Samsung $250–$499 showed a clear underperformance signal.

---

## Recommended Business Actions

Based on the dashboard, the business should investigate:

1. Premium Apple smartphone sessions
2. Samsung value-tier growth behavior
3. Samsung mid-range underperformance
4. Cart abandonment in high-value smartphone sessions
5. Product-level pricing, promotion, and availability patterns
6. Checkout friction for premium smartphone buyers

---

## Portfolio Value

This dashboard demonstrates:

- KPI design
- Funnel analysis
- Product analytics storytelling
- Category segmentation
- Brand and price-band diagnostics
- Executive dashboard design
- Power BI report building
- Business recommendation development