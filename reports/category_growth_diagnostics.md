# CommercePulse Category Growth Diagnostics

## Objective

This report investigates the month-over-month category shifts between **2019-10** and **2019-11**, with special focus on:

1. Which categories drove November revenue growth?
2. Which categories experienced the largest deterioration in cart-to-purchase efficiency?
3. Whether November growth was broad-based or concentrated in a small number of categories.

---

## Executive Summary

November revenue growth was highly concentrated in a small set of category groups.

- The four largest positive category revenue contributors — **electronics, unknown, appliances, and computers** — generated **$43,414,355.19** in combined positive revenue delta.
- These four categories accounted for **95.96%** of all positive category-level revenue growth.
- **Electronics** was the dominant driver, contributing **$28,785,949.85** in revenue growth and reaching **$205,250,118.21** in November purchase revenue.
- However, electronics also suffered a **-11.35 pp** decline in session-level cart-to-purchase conversion.
- The `unknown` category represented **$29,880,506.68** in November revenue and grew by **$6,955,569.55**, making uncategorized product activity analytically material rather than negligible.

---

## Top Revenue Growth Categories

| Category | Oct Revenue | Nov Revenue | Revenue Delta | Revenue Growth | Cart→Purchase Δ |
|---|---:|---:|---:|---:|---:|
| electronics | $176,464,168.36 | $205,250,118.21 | $28,785,949.85 | 16.31% | -11.35 pp |
| unknown | $22,924,937.13 | $29,880,506.68 | $6,955,569.55 | 30.34% | -6.63 pp |
| appliances | $13,583,121.92 | $18,640,501.67 | $5,057,379.75 | 37.23% | -9.34 pp |
| computers | $11,378,874.65 | $13,994,330.69 | $2,615,456.04 | 22.99% | -10.13 pp |
| furniture | $1,673,728.99 | $2,543,251.02 | $869,522.03 | 51.95% | -9.56 pp |
| apparel | $624,937.75 | $1,181,025.12 | $556,087.37 | 88.98% | -8.34 pp |
| construction | $932,995.02 | $1,080,390.70 | $147,395.68 | 15.80% | -11.06 pp |
| auto | $1,274,031.65 | $1,375,004.82 | $100,973.17 | 7.93% | -10.47 pp |
| sport | $322,559.00 | $395,692.75 | $73,133.75 | 22.67% | -1.92 pp |
| kids | $678,140.67 | $723,763.26 | $45,622.59 | 6.73% | -2.76 pp |

---

## Categories with the Largest Cart-to-Purchase Efficiency Declines

| Category | Oct Cart→Purchase | Nov Cart→Purchase | Change | Nov Revenue |
|---|---:|---:|---:|---:|
| electronics | 52.48% | 41.13% | -11.35 pp | $205,250,118.21 |
| construction | 42.21% | 31.15% | -11.06 pp | $1,080,390.70 |
| auto | 44.76% | 34.29% | -10.47 pp | $1,375,004.82 |
| computers | 42.68% | 32.55% | -10.13 pp | $13,994,330.69 |
| furniture | 38.81% | 29.25% | -9.56 pp | $2,543,251.02 |
| appliances | 44.51% | 35.17% | -9.34 pp | $18,640,501.67 |
| unknown | 38.93% | 32.30% | -6.63 pp | $29,880,506.68 |
| kids | 35.65% | 32.89% | -2.76 pp | $723,763.26 |
| sport | 32.05% | 30.13% | -1.92 pp | $395,692.75 |

---

## Business Interpretation

### 1. November growth was concentrated, not evenly distributed
The majority of positive revenue growth came from a small number of category groups, especially:

- **Electronics**
- **Unknown / uncategorized**
- **Appliances**
- **Computers**

This indicates that November platform growth was driven disproportionately by higher-value product categories rather than uniform growth across the catalog.

### 2. Electronics is both the growth engine and the key diagnostic risk
Electronics added **$28,785,949.85** in revenue, making it the largest month-over-month contributor. At the same time, its cart-to-purchase conversion declined by **-11.35 pp**.

This combination is important:

> Electronics created substantial incremental revenue, but a materially smaller share of carting sessions converted to purchases.

That pattern deserves deeper follow-up by subcategory, brand, and price band.

### 3. Appliances and computers show a similar pattern
Appliances and computers contributed **$5,057,379.75** and **$2,615,456.04** in incremental revenue, respectively. Both also experienced major drops in cart-to-purchase efficiency.

This suggests the funnel deterioration was especially visible in several higher-ticket technology and home-product segments.

### 4. Uncategorized activity is financially significant
The `unknown` category is not a minor residual bucket. It generated **$29,880,506.68** in November revenue and grew by **$6,955,569.55**.

Since `unknown` comes from rows with missing `category_code`, it should be:
- tracked explicitly in dashboards,
- excluded from category-specific root-cause claims when necessary,
- and considered in data-quality discussions.

---

## Hypotheses to Investigate Next

These are hypotheses, not conclusions:

1. **Higher promotional browsing in November** may have increased carts without proportional purchasing.
2. **Higher-ticket categories** may show more comparison-shopping and longer consideration cycles.
3. **Specific subcategories within electronics** may explain most of the efficiency decline.
4. **Brand-level concentration** may reveal whether a few high-traffic brands drove disproportionate cart growth.
5. **Price bands** may help determine whether lower or higher-priced products were responsible for the weaker cart-to-purchase rate.

---

## Recommended Next Analytical Step

The next diagnostic layer should break down category performance by:

1. `category_l2` subcategory,
2. top brands,
3. product price bands.

This will help identify whether the electronics decline is broad-based or concentrated in specific product types.

---

## Method Notes

- All revenue metrics are based on the sum of `price` for purchase events.
- Category grouping uses the top-level category parsed from `category_code`.
- Missing top-level category values are grouped into `unknown`.
- Cart-to-purchase metrics are computed at the session level using ordered funnel logic:
  - cart event occurs before purchase event,
  - both within the same session.
