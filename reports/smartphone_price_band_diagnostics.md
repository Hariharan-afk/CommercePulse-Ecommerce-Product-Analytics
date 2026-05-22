# CommercePulse Smartphone Price-Band Diagnostics

## Objective

This report examines smartphone performance by price band to answer:

1. Which smartphone price tiers drove November revenue growth?
2. Which price tiers suffered the largest cart-to-purchase deterioration?
3. Whether the smartphone growth-and-efficiency tradeoff was concentrated in premium, mid-range, or budget segments.

---

## Executive Summary

Smartphone revenue growth in November was concentrated in a small set of price bands.

- The **$800-$1199** band generated **$50,909,997.47** in November revenue and contributed **$9,151,272.62** in incremental revenue.
- The **$1200+** band generated **$39,798,572.22** and added **$5,895,408.50** in revenue.
- Together, those premium bands generated **$90,708,569.69**, representing **51.01%** of all smartphone revenue.
- Their combined contribution represented **72.44%** of net smartphone revenue growth.

A third major growth contributor was the **$100-$249** value segment:

- It added **$6,291,714.96** in revenue.
- It represented **30.29%** of net smartphone growth.

Together, the three leading positive-growth bands — **$800-$1199**, **$100-$249**, and **$1200+** — explain **102.73%** of net smartphone revenue growth, before offsetting declines in other bands.

---

## Smartphone Revenue by Price Band

| Price Band | Nov Revenue | Smartphone Revenue Share | Revenue Delta | Revenue Growth | Cart→Purchase Δ |
|---|---:|---:|---:|---:|---:|
| $800-$1199 | $50,909,997.47 | 28.63% | $9,151,272.62 | 21.91% | -13.53 pp |
| $1200+ | $39,798,572.22 | 22.38% | $5,895,408.50 | 17.39% | -10.61 pp |
| $500-$799 | $30,597,935.23 | 17.21% | $-192,898.41 | -0.63% | -11.74 pp |
| $100-$249 | $30,137,494.27 | 16.95% | $6,291,714.96 | 26.39% | -10.27 pp |
| $250-$499 | $25,404,647.97 | 14.29% | $-287,801.80 | -1.12% | -13.98 pp |
| Under $100 | $973,014.45 | 0.55% | $-85,657.63 | -8.09% | -8.95 pp |
| Non-positive / Unknown | $0.00 | 0.00% | $0.00 | N/A | +0.00 pp |

---

## Smartphone Revenue Growth Contributors

| Price Band | Revenue Delta | Net Growth Share | Revenue Growth | Nov Revenue | Cart→Purchase Δ |
|---|---:|---:|---:|---:|---:|
| $800-$1199 | $9,151,272.62 | 44.06% | 21.91% | $50,909,997.47 | -13.53 pp |
| $100-$249 | $6,291,714.96 | 30.29% | 26.39% | $30,137,494.27 | -10.27 pp |
| $1200+ | $5,895,408.50 | 28.38% | 17.39% | $39,798,572.22 | -10.61 pp |
| Non-positive / Unknown | $0.00 | 0.00% | N/A | $0.00 | +0.00 pp |
| Under $100 | $-85,657.63 | -0.41% | -8.09% | $973,014.45 | -8.95 pp |
| $500-$799 | $-192,898.41 | -0.93% | -0.63% | $30,597,935.23 | -11.74 pp |
| $250-$499 | $-287,801.80 | -1.39% | -1.12% | $25,404,647.97 | -13.98 pp |

---

## Smartphone Cart-to-Purchase Conversion by Price Band

| Price Band | Oct Cart→Purchase | Nov Cart→Purchase | Change | Nov Revenue |
|---|---:|---:|---:|---:|
| $250-$499 | 54.59% | 40.61% | -13.98 pp | $25,404,647.97 |
| $800-$1199 | 51.84% | 38.31% | -13.53 pp | $50,909,997.47 |
| $500-$799 | 52.19% | 40.45% | -11.74 pp | $30,597,935.23 |
| $1200+ | 51.09% | 40.48% | -10.61 pp | $39,798,572.22 |
| $100-$249 | 55.95% | 45.68% | -10.27 pp | $30,137,494.27 |
| Under $100 | 52.27% | 43.32% | -8.95 pp | $973,014.45 |
| Non-positive / Unknown | 0.00% | 0.00% | +0.00 pp | $0.00 |

---

## Business Interpretation

### 1. Premium smartphone tiers were the largest revenue engine
The **$800-$1199** and **$1200+** bands together generated more than half of November smartphone revenue. This means the smartphone growth story was materially influenced by premium-product demand.

### 2. The $800-$1199 tier is the highest-priority price diagnostic
This band combined:

- The largest positive revenue delta: **$9,151,272.62**
- The largest net growth share: **44.06%**
- A major cart-to-purchase decline: **-13.53 pp**

That combination makes it one of the most important price segments to investigate further.

### 3. The $100-$249 band grew strongly, showing a second growth pocket
The **$100-$249** band contributed **$6,291,714.96** in additional revenue. This indicates that November smartphone growth was not exclusively premium-led; the lower-price value segment also expanded meaningfully.

### 4. The mid-range segments underperformed
The **$250-$499** and **$500-$799** bands both showed negative revenue deltas:

- **$250-$499:** $-287,801.80
- **$500-$799:** $-192,898.41

The **$250-$499** band also experienced the sharpest cart-to-purchase decline at **-13.98 pp**.

This suggests that the mid-range smartphone segment may have been comparatively weaker in November.

---

## Analytical Hypotheses to Test Next

These are hypotheses, not confirmed causes:

1. Apple and Samsung growth may have been concentrated in premium price bands.
2. The **$800-$1199** decline could reflect high-intent carting combined with more comparison-shopping before purchase.
3. The **$250-$499** band may indicate a weaker mid-range market segment during November.
4. Price-band behavior may interact with brand-level behavior, especially for Apple, Samsung, and Xiaomi.

---

## Recommended Next Step

The next high-value analysis should combine:

### Brand × Price Band

This will answer:

1. Which brands dominate the **$800-$1199** and **$1200+** segments?
2. Whether Apple’s revenue growth is concentrated in premium prices.
3. Whether Samsung, Xiaomi, or Oppo behave differently by price tier.
4. Which specific brand-price combinations drove growth while conversion weakened.

---

## Method Notes

- This analysis is restricted to smartphone events:
  - `category_l1 = 'electronics'`
  - `category_l2 = 'smartphone'`
- Price bands are based on observed event-level `price`.
- Revenue is calculated as the sum of `price` for purchase events.
- Cart-to-purchase conversion is computed at the session level.
- Growth-share percentages are calculated relative to net smartphone revenue growth, so positive contributors can exceed 100% in aggregate when some price bands have negative revenue deltas.
