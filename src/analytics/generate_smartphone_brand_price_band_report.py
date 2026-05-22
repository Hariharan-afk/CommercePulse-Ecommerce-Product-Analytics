from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import pandas as pd
from rich.console import Console

console = Console()


def get_project_root() -> Path:
    """
    Returns the project root assuming this file lives at:
    src/analytics/generate_smartphone_brand_price_band_report.py
    """
    return Path(__file__).resolve().parents[2]


def fmt_currency(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"${float(value):,.2f}"


def fmt_pct(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{float(value):.2f}%"


def fmt_pp(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    sign = "+" if float(value) >= 0 else ""
    return f"{sign}{float(value):.2f} pp"


def safe_float(row: pd.Series | None, column: str) -> float:
    if row is None:
        return 0.0

    value = row[column]

    if pd.isna(value):
        return 0.0

    return float(value)


def get_segment_row(
    df: pd.DataFrame,
    brand: str,
    price_band: str,
) -> pd.Series | None:
    match = df[
        (df["brand"] == brand)
        & (df["price_band"] == price_band)
    ]

    if match.empty:
        return None

    return match.iloc[0]


def build_revenue_leaders_table(df: pd.DataFrame, top_n: int = 15) -> str:
    top_df = (
        df.sort_values("nov_purchase_revenue", ascending=False)
        .head(top_n)
        .copy()
    )

    lines = [
        "| Brand | Price Band | Nov Revenue | Smartphone Revenue Share | Revenue Delta | Revenue Growth | Cart→Purchase Δ |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]

    for _, row in top_df.iterrows():
        lines.append(
            "| "
            f"{row['brand']} | "
            f"{row['price_band']} | "
            f"{fmt_currency(row['nov_purchase_revenue'])} | "
            f"{fmt_pct(row['nov_smartphone_revenue_share_pct'])} | "
            f"{fmt_currency(row['revenue_delta'])} | "
            f"{fmt_pct(row['revenue_growth_pct'])} | "
            f"{fmt_pp(row['cart_to_purchase_rate_change_pp'])} |"
        )

    return "\n".join(lines)


def build_growth_contributors_table(df: pd.DataFrame, top_n: int = 15) -> str:
    top_df = (
        df.sort_values("revenue_delta", ascending=False)
        .head(top_n)
        .copy()
    )

    lines = [
        "| Brand | Price Band | Revenue Delta | Net Growth Share | Revenue Growth | Nov Revenue | Cart→Purchase Δ |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]

    for _, row in top_df.iterrows():
        lines.append(
            "| "
            f"{row['brand']} | "
            f"{row['price_band']} | "
            f"{fmt_currency(row['revenue_delta'])} | "
            f"{fmt_pct(row['net_smartphone_revenue_growth_share_pct'])} | "
            f"{fmt_pct(row['revenue_growth_pct'])} | "
            f"{fmt_currency(row['nov_purchase_revenue'])} | "
            f"{fmt_pp(row['cart_to_purchase_rate_change_pp'])} |"
        )

    return "\n".join(lines)


def build_conversion_decline_table(df: pd.DataFrame, top_n: int = 15) -> str:
    eligible = df[
        (df["oct_cart_events"] >= 1000)
        & (df["nov_cart_events"] >= 1000)
        & (df["cart_to_purchase_rate_change_pp"].notna())
    ].copy()

    decline_df = (
        eligible.sort_values("cart_to_purchase_rate_change_pp", ascending=True)
        .head(top_n)
        .copy()
    )

    lines = [
        "| Brand | Price Band | Oct Cart→Purchase | Nov Cart→Purchase | Change | Nov Revenue |",
        "|---|---|---:|---:|---:|---:|",
    ]

    for _, row in decline_df.iterrows():
        lines.append(
            "| "
            f"{row['brand']} | "
            f"{row['price_band']} | "
            f"{fmt_pct(row['oct_cart_to_purchase_rate_pct'])} | "
            f"{fmt_pct(row['nov_cart_to_purchase_rate_pct'])} | "
            f"{fmt_pp(row['cart_to_purchase_rate_change_pp'])} | "
            f"{fmt_currency(row['nov_purchase_revenue'])} |"
        )

    return "\n".join(lines)


def build_report(df: pd.DataFrame) -> str:
    apple_800_1199 = get_segment_row(df, "apple", "$800-$1199")
    apple_1200_plus = get_segment_row(df, "apple", "$1200+")
    samsung_100_249 = get_segment_row(df, "samsung", "$100-$249")
    samsung_250_499 = get_segment_row(df, "samsung", "$250-$499")
    samsung_500_799 = get_segment_row(df, "samsung", "$500-$799")
    samsung_800_1199 = get_segment_row(df, "samsung", "$800-$1199")

    top_three_growth_share = (
        safe_float(
            apple_800_1199,
            "net_smartphone_revenue_growth_share_pct",
        )
        + safe_float(
            apple_1200_plus,
            "net_smartphone_revenue_growth_share_pct",
        )
        + safe_float(
            samsung_100_249,
            "net_smartphone_revenue_growth_share_pct",
        )
    )

    apple_premium_growth_share = (
        safe_float(
            apple_800_1199,
            "net_smartphone_revenue_growth_share_pct",
        )
        + safe_float(
            apple_1200_plus,
            "net_smartphone_revenue_growth_share_pct",
        )
    )

    apple_premium_revenue = (
        safe_float(apple_800_1199, "nov_purchase_revenue")
        + safe_float(apple_1200_plus, "nov_purchase_revenue")
    )

    apple_premium_revenue_delta = (
        safe_float(apple_800_1199, "revenue_delta")
        + safe_float(apple_1200_plus, "revenue_delta")
    )

    revenue_leaders_table = build_revenue_leaders_table(df)
    growth_contributors_table = build_growth_contributors_table(df)
    conversion_decline_table = build_conversion_decline_table(df)

    report = f"""# CommercePulse Smartphone Brand × Price-Band Diagnostics

## Objective

This report combines **brand** and **price-band** dimensions to isolate the exact smartphone segments driving November revenue growth and cart-to-purchase deterioration.

It answers:

1. Which brand-price combinations drove the largest revenue growth?
2. Which brand-price combinations saw the largest funnel deterioration?
3. Whether Apple and Samsung growth patterns were concentrated in specific pricing tiers.

---

## Executive Summary

November smartphone growth was highly concentrated in three brand-price segments:

1. **Apple $800-$1199**
2. **Apple $1200+**
3. **Samsung $100-$249**

Together, these segments accounted for **{fmt_pct(top_three_growth_share)}** of net smartphone revenue growth.

### The headline segment: Apple $800-$1199

- November revenue: **{fmt_currency(safe_float(apple_800_1199, 'nov_purchase_revenue'))}**
- Revenue growth: **{fmt_currency(safe_float(apple_800_1199, 'revenue_delta'))}**
- Net smartphone growth share: **{fmt_pct(safe_float(apple_800_1199, 'net_smartphone_revenue_growth_share_pct'))}**
- Cart-to-purchase change: **{fmt_pp(safe_float(apple_800_1199, 'cart_to_purchase_rate_change_pp'))}**

This segment was the **largest growth contributor** and also one of the **largest high-value conversion deterioration segments**.

### Apple premium tiers dominate growth

The combined **Apple $800-$1199** and **Apple $1200+** segments generated:

- **{fmt_currency(apple_premium_revenue)}** in November revenue
- **{fmt_currency(apple_premium_revenue_delta)}** in incremental revenue
- **{fmt_pct(apple_premium_growth_share)}** of net smartphone revenue growth

---

## Revenue Leaders by Brand × Price Band

{revenue_leaders_table}

---

## Net Smartphone Revenue Growth Contributors

{growth_contributors_table}

---

## Largest Cart-to-Purchase Efficiency Declines

{conversion_decline_table}

---

## Business Interpretation

### 1. Apple premium smartphones are the clearest growth-and-friction story
The **Apple $800-$1199** and **Apple $1200+** segments together dominate both scale and revenue expansion. However, both tiers experienced meaningful cart-to-purchase deterioration.

This suggests a critical product analytics question:

> Were premium Apple shoppers showing stronger browsing and cart intent in November, but hesitating at the final purchase step?

### 2. Samsung’s growth is concentrated in different price tiers
Samsung’s strongest positive-growth segments were:

- **$100-$249:** {fmt_currency(safe_float(samsung_100_249, 'revenue_delta'))}
- **$500-$799:** {fmt_currency(safe_float(samsung_500_799, 'revenue_delta'))}
- **$800-$1199:** {fmt_currency(safe_float(samsung_800_1199, 'revenue_delta'))}

This indicates Samsung’s growth profile was more distributed across value and mid-premium tiers than Apple’s premium-heavy pattern.

### 3. Samsung $250-$499 is a clear underperformance segment
The **Samsung $250-$499** segment showed:

- Revenue delta: **{fmt_currency(safe_float(samsung_250_499, 'revenue_delta'))}**
- Cart-to-purchase conversion change: **{fmt_pp(safe_float(samsung_250_499, 'cart_to_purchase_rate_change_pp'))}**

This is one of the clearest examples of a segment that both:
- lost revenue,
- and deteriorated sharply in funnel efficiency.

### 4. Growth and conversion quality diverged
Several of the strongest growth segments also showed substantial cart-to-purchase declines:

- Apple $800-$1199
- Apple $1200+
- Samsung $100-$249
- Samsung $500-$799
- Samsung $800-$1199

This reinforces the broader project conclusion:

> November revenue growth was strong, but it came with weaker conversion efficiency in several commercially important smartphone segments.

---

## Analytical Hypotheses to Test Next

These are hypotheses, not confirmed causes:

1. Apple premium growth may reflect seasonal upgrade shopping, promotional visibility, or higher top-of-funnel demand.
2. The conversion deterioration could signal increased comparison-shopping or delayed purchase decisions.
3. Samsung’s mid-range decline may reflect weaker relative demand, price positioning, or competition from other brands/tiers.
4. Some high-growth segments may have received more cart activity without equivalent checkout completion.

---

## Recommended Next Step

At this point, the **business diagnosis path is mature enough**. The next strongest addition is not another finer drill-down, but a **dashboard layer** that converts the warehouse marts and reports into a visual executive analytics product.

Recommended next build:

### Power BI Dashboard Pages
1. Executive overview
2. Monthly funnel shift
3. Category growth diagnostics
4. Electronics → Smartphone drill-down
5. Brand diagnostics
6. Brand × Price-Band opportunity matrix

---

## Method Notes

- This analysis is restricted to:
  - `category_l1 = 'electronics'`
  - `category_l2 = 'smartphone'`
- Price bands are created from observed event-level `price`.
- Missing brands are grouped under `unknown`.
- Revenue is calculated as the sum of purchase-event prices.
- Cart-to-purchase rates are computed at the session level using ordered funnel logic.
- Growth-share percentages are computed relative to net smartphone revenue growth; some positive shares can collectively exceed 100% because other segments have negative revenue deltas.
"""

    return report


def main() -> int:
    project_root = get_project_root()

    db_path = project_root / "data" / "processed" / "commercepulse.duckdb"

    diagnostics_csv_path = (
        project_root
        / "outputs"
        / "tables"
        / "mart_smartphone_brand_price_band_mom_diagnostics.csv"
    )

    monthly_segment_csv_path = (
        project_root
        / "outputs"
        / "tables"
        / "mart_monthly_smartphone_brand_price_band_performance.csv"
    )

    report_path = (
        project_root
        / "reports"
        / "smartphone_brand_price_band_diagnostics.md"
    )

    console.print(f"[bold cyan]Project root:[/bold cyan] {project_root}")
    console.print(f"[bold cyan]DuckDB warehouse:[/bold cyan] {db_path}")

    if not db_path.exists():
        console.print(
            "[bold red]DuckDB warehouse not found. "
            "Run build_warehouse.py first.[/bold red]"
        )
        return 1

    try:
        diagnostics_csv_path.parent.mkdir(parents=True, exist_ok=True)
        monthly_segment_csv_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)

        con = duckdb.connect(database=str(db_path), read_only=True)

        diagnostics_df = con.execute(
            """
            SELECT *
            FROM mart_smartphone_brand_price_band_mom_diagnostics
            ORDER BY revenue_delta DESC;
            """
        ).df()

        monthly_segment_df = con.execute(
            """
            SELECT *
            FROM mart_monthly_smartphone_brand_price_band_performance
            ORDER BY event_month, purchase_revenue DESC;
            """
        ).df()

        con.close()

        if diagnostics_df.empty:
            raise ValueError(
                "mart_smartphone_brand_price_band_mom_diagnostics returned no rows."
            )

        diagnostics_df.to_csv(diagnostics_csv_path, index=False)
        monthly_segment_df.to_csv(monthly_segment_csv_path, index=False)

        report_content = build_report(diagnostics_df)
        report_path.write_text(report_content, encoding="utf-8")

        console.print(
            f"[bold green]Smartphone brand × price-band diagnostics CSV exported:[/bold green] {diagnostics_csv_path}"
        )
        console.print(
            f"[bold green]Monthly smartphone brand × price-band performance CSV exported:[/bold green] {monthly_segment_csv_path}"
        )
        console.print(
            f"[bold green]Smartphone brand × price-band report generated:[/bold green] {report_path}"
        )

        console.print(
            f"\n[bold cyan]Brand × price-band diagnostic rows exported:[/bold cyan] {len(diagnostics_df)}"
        )
        console.print(
            f"[bold cyan]Monthly brand × price-band rows exported:[/bold cyan] {len(monthly_segment_df)}"
        )

    except Exception as exc:
        console.print(
            f"[bold red]Smartphone brand × price-band report generation failed:[/bold red] {exc}"
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())