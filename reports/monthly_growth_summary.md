# CommercePulse Monthly Growth Summary

## Comparison Window

This report compares **2019-10** against **2019-11** using the `mart_monthly_kpis` warehouse table.

---

## Executive Summary

Between **2019-10** and **2019-11**:

- Total event volume increased by **+59.02%**.
- Active users increased by **+22.30%**.
- Active sessions increased by **+49.02%**.
- Purchase events increased by **+23.44%**.
- Purchase revenue increased by **+19.67%**.
- Average purchase price changed by **-3.05%**.

The strongest behavioral shift was in the shopping funnel:

- Session **View → Cart** rate increased by **+6.39 pp**.
- Session **View → Purchase** rate changed by **-1.25 pp**.
- Session **Cart → Purchase** rate changed by **-12.07 pp**.
- Strict **View → Cart → Purchase** funnel completion changed by **+1.59 pp**.

---

## Monthly KPI Comparison

| Metric | Earlier Month | Later Month | Change |
|---|---:|---:|---:|
| Total events | 42,448,764 | 67,501,979 | +59.02% |
| Active users | 3,022,290 | 3,696,117 | +22.30% |
| Active sessions | 9,244,421 | 13,776,050 | +49.02% |
| Active products | 166,794 | 190,662 | +14.31% |
| Purchase events | 742,849 | 916,939 | +23.44% |
| Purchasing users | 347,118 | 441,638 | +27.23% |
| Purchase revenue | $229,957,502.27 | $275,194,890.50 | +19.67% |
| Average purchase price | $309.56 | $300.12 | -3.05% |

---

## Funnel Comparison

| Funnel Metric | Earlier Month | Later Month | Change |
|---|---:|---:|---:|
| Session View → Cart Rate | 6.18% | 12.57% | +6.39 pp |
| Session View → Purchase Rate | 6.79% | 5.54% | -1.25 pp |
| Session Cart → Purchase Rate | 49.17% | 37.10% | -12.07 pp |
| Strict Session Funnel Completion Rate | 3.03% | 4.62% | +1.59 pp |
| Event View → Cart Rate | 2.27% | 4.77% | +2.50 pp |
| Event View → Purchase Rate | 1.82% | 1.44% | -0.38 pp |

---

## Initial Business Interpretation

### 1. Platform activity expanded significantly
The later month shows materially higher event volume, user activity, and session volume. This indicates stronger overall platform engagement and a larger pool of users entering the product funnel.

### 2. Carting behavior rose sharply
The session-level **View → Cart** rate increased substantially. This suggests that product discovery or purchase intent became stronger in the later month.

### 3. Purchase efficiency weakened relative to cart growth
Despite more users adding products to cart, the **Cart → Purchase** rate declined. This indicates that the later month generated more high-intent activity, but a smaller share of cart sessions ultimately converted to purchases.

### 4. Revenue still increased
Revenue rose because overall session and purchase volume grew enough to offset weaker downstream funnel efficiency and a lower average purchase price.

---

## Product Analytics Questions to Investigate Next

1. Which product categories drove the sharp increase in carting activity?
2. Did specific categories experience unusually high cart abandonment?
3. Did traffic growth come from lower-converting users, categories, or price bands?
4. Were higher-volume November categories associated with lower average price points?
5. Which category or brand segments contributed most to the revenue increase?

---

## Method Notes

- Funnel metrics are computed at the **session level**.
- The strict funnel completion metric requires:
  - a view event,
  - followed by a cart event,
  - followed by a purchase event,
  - all within the same user session.
- Purchase revenue is calculated as the sum of `price` for purchase events.
