# CommercePulse Project Summary

## One-Line Summary

CommercePulse is a product analytics and business intelligence project that analyzes **109M+ e-commerce behavior events** to diagnose November revenue growth, funnel deterioration, and smartphone segment performance across category, brand, price-band, and brand × price-band dimensions.

---

## Project Objective

The platform showed strong November growth in traffic, sessions, purchases, and revenue. However, downstream funnel quality weakened because cart-to-purchase conversion declined sharply.

The project investigates the following business question:

> Why did November revenue and cart activity increase while cart-to-purchase conversion declined?

The analysis follows a layered diagnostic approach:

```text
Platform → Category → Subcategory → Brand → Price Band → Brand × Price Band
```

---

## Business Problem

Between October and November 2019, the e-commerce platform experienced strong growth in:

- Total events
- Active users
- Sessions
- Purchase events
- Purchase revenue
- View-to-cart activity

However, the session-level cart-to-purchase rate declined from **49.17%** to **37.10%**, a drop of **-12.07 percentage points**.

This created an important product analytics question:

> Was the conversion decline broad-based, or was it concentrated in specific commercial segments?

---

## Dataset

The project uses the **E-Commerce Behavior Data from Multi-Category Store** dataset.

Raw files used:

```text
2019-Oct.csv
2019-Nov.csv
```

Cleaned event volume:

```text
109,950,743 rows
```

Cleaned dataset profile:

| Metric | Value |
|---|---:|
| Total Events | 109,950,743 |
| Unique Users | 5,316,649 |
| Unique Sessions | 23,016,650 |
| Unique Products | 206,876 |
| Unique Categories | 691 |
| Unique Brands | 4,303 |

---

## Technical Approach

CommercePulse uses an analytics engineering workflow:

1. Raw CSV ingestion
2. Event cleaning and timestamp parsing
3. Clean Parquet generation
4. DuckDB warehouse construction
5. SQL mart creation
6. Month-over-month KPI diagnostics
7. Category, subcategory, brand, and price-band analysis
8. Markdown diagnostic report generation
9. Power BI dashboard export
10. Six-page executive dashboard creation

---

## Tools Used

| Area | Tools |
|---|---|
| Data Processing | Python, Pandas |
| Analytics Warehouse | DuckDB |
| Query Layer | SQL |
| Data Storage | Parquet, CSV |
| Reporting | Markdown |
| Dashboarding | Power BI |
| CLI Formatting | Rich |
| Version Control | Git, GitHub |

---

## Key Platform-Level Findings

| Metric | October 2019 | November 2019 | Change |
|---|---:|---:|---:|
| Total Events | 42.45M | 67.50M | Increased |
| Active Users | 3.02M | 3.70M | Increased |
| Sessions | 9.24M | 13.78M | Increased |
| Purchase Events | 742.85K | 916.94K | Increased |
| Purchase Revenue | $229.96M | $275.19M | +19.67% |
| View → Cart Rate | 6.18% | 12.57% | +6.39 pp |
| Cart → Purchase Rate | 49.17% | 37.10% | -12.07 pp |

November generated stronger activity and revenue, but the downstream funnel became less efficient.

---

## Analytical Findings

### 1. Category-Level Finding

Electronics was the largest category-level growth driver.

| Category Signal | Value |
|---|---:|
| Electronics November Revenue | $205.25M |
| Electronics Revenue Delta | +$28.79M |
| Electronics Cart → Purchase Change | -11.35 pp |

Electronics was both the largest growth contributor and a major conversion-risk category.

---

### 2. Subcategory-Level Finding

Within electronics, smartphones dominated revenue and growth.

| Metric | Value |
|---|---:|
| Smartphone November Revenue | $177.82M |
| Smartphone Share of Electronics Revenue | 86.64% |
| Smartphone Revenue Delta | +$20.77M |
| Smartphone Cart → Purchase Change | -11.65 pp |

Smartphones became the key subcategory for deeper analysis.

---

### 3. Brand-Level Finding

Apple and Samsung drove most smartphone revenue and revenue growth.

| Brand | November Revenue | Revenue Share | Revenue Delta | Cart → Purchase Change |
|---|---:|---:|---:|---:|
| Apple | $115.26M | 64.82% | +$12.71M | -12.07 pp |
| Samsung | $42.71M | 24.02% | +$5.34M | -10.97 pp |

Apple was the highest-priority brand because it combined the largest revenue base, largest revenue growth, and a major cart-to-purchase decline.

---

### 4. Price-Band-Level Finding

Premium smartphone tiers drove much of November growth.

| Price Band | November Revenue | Revenue Delta | Net Growth Share | Cart → Purchase Change |
|---|---:|---:|---:|---:|
| $800–$1199 | $50.91M | +$9.15M | 44.06% | -13.53 pp |
| $1200+ | $39.80M | +$5.90M | 28.38% | Negative |
| $100–$249 | $30.14M | +$6.29M | 30.29% | Negative |

The $800–$1199 band was the strongest growth-and-risk segment because it contributed the largest revenue lift while also showing a major conversion decline.

---

### 5. Brand × Price-Band Finding

The final diagnostic layer identified the exact brand-price segments driving growth.

| Segment | Revenue Delta | Interpretation |
|---|---:|---|
| Apple $800–$1199 | +$7.70M | Largest smartphone growth contributor |
| Apple $1200+ | +$6.10M | Major premium growth contributor |
| Samsung $100–$249 | +$4.71M | Major value-tier growth pocket |
| Samsung $250–$499 | Negative revenue and sharp conversion decline | Underperformance segment |

This showed that smartphone growth was not just brand-driven or price-band-driven. It was concentrated in specific brand-price combinations.

---

## Final Analytical Story

```text
Platform Level
November traffic, sessions, purchases, and revenue increased,
but cart-to-purchase conversion declined.

↓
Category Level
Electronics drove the largest revenue growth and showed a major conversion decline.

↓
Subcategory Level
Smartphones dominated electronics revenue and growth.

↓
Brand Level
Apple and Samsung drove most smartphone expansion.

↓
Price-Band Level
Premium smartphones and the $100–$249 value band drove growth.

↓
Brand × Price-Band Level
Apple $800–$1199, Apple $1200+, and Samsung $100–$249 explained most smartphone revenue growth.
```

---

## Power BI Dashboard

The final Power BI dashboard contains six pages:

1. **Executive Overview**
2. **Category Growth Diagnostics**
3. **Electronics → Smartphone Drill-Down**
4. **Smartphone Brand Diagnostics**
5. **Smartphone Price-Band Diagnostics**
6. **Brand × Price-Band Opportunity Matrix**

Each page answers a specific business question and moves progressively deeper into the root-cause analysis.

---

## Dashboard Page Summary

### Page 1 — Executive Overview

Shows November revenue, sessions, active users, purchases, revenue growth, view-to-cart change, and cart-to-purchase change.

Main insight:

> November revenue and activity increased sharply, but downstream funnel quality weakened.

---

### Page 2 — Category Growth Diagnostics

Shows which categories drove growth and where cart-to-purchase efficiency declined.

Main insight:

> Electronics was the largest revenue growth driver and a major conversion-risk category.

---

### Page 3 — Electronics → Smartphone Drill-Down

Shows electronics subcategory performance.

Main insight:

> Smartphones generated the majority of electronics revenue and were the most important subcategory for deeper diagnostics.

---

### Page 4 — Smartphone Brand Diagnostics

Shows smartphone performance by brand.

Main insight:

> Apple and Samsung dominated smartphone revenue growth, while Apple was the highest-priority brand due to scale, growth, and conversion deterioration.

---

### Page 5 — Smartphone Price-Band Diagnostics

Shows smartphone performance by price tier.

Main insight:

> Premium smartphone tiers, especially $800–$1199 and $1200+, drove much of November growth.

---

### Page 6 — Brand × Price-Band Opportunity Matrix

Shows the exact brand-price combinations driving growth and conversion risk.

Main insight:

> Apple premium tiers and Samsung value-tier segments explained most smartphone growth, while Samsung $250–$499 showed underperformance.

---

## Business Interpretation

November growth was commercially strong but operationally mixed. The platform attracted more users and generated more cart activity, but the quality of downstream conversion weakened.

The most important issue was not platform-wide randomness. The decline was especially important in commercially meaningful smartphone segments, particularly:

- Apple premium tiers
- Samsung value-tier growth
- Samsung mid-range underperformance
- Premium smartphone cart abandonment behavior

---

