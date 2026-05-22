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
    src/analytics/generate_smartphone_price_band_report.py
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


def get_row(df: pd.DataFrame, price_band: str) -> pd.Series | None:
    match = df[df["price_band"] == price_band]

    if match.empty:
        return None

    return match.iloc[0]


def build_revenue_table(df: pd.DataFrame) -> str:
    ordered_df = (
        df.sort_values("nov_purchase_revenue", ascending=False)
        .copy()
    )

    lines = [
        "| Price Band | Nov Revenue | Smartphone Revenue Share | Revenue Delta | Revenue Growth | Cart→Purchase Δ |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for _, row in ordered_df.iterrows():
        lines.append(
            "| "
            f"{row['price_band']} | "
            f"{fmt_currency(row['nov_purchase_revenue'])} | "
            f"{fmt_pct(row['nov_smartphone_revenue_share_pct'])} | "
            f"{fmt_currency(row['revenue_delta'])} | "
            f"{fmt_pct(row['revenue_growth_pct'])} | "
            f"{fmt_pp(row['cart_to_purchase_rate_change_pp'])} |"
        )

    return "\n".join(lines)


def build_growth_table(df: pd.DataFrame) -> str:
    ordered_df = (
        df.sort_values("revenue_delta", ascending=False)
        .copy()
    )

    lines = [
        "| Price Band | Revenue Delta | Net Growth Share | Revenue Growth | Nov Revenue | Cart→Purchase Δ |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for _, row in ordered_df.iterrows():
        lines.append(
            "| "
            f"{row['price_band']} | "
            f"{fmt_currency(row['revenue_delta'])} | "
            f"{fmt_pct(row['net_smartphone_revenue_growth_share_pct'])} | "
            f"{fmt_pct(row['revenue_growth_pct'])} | "
            f"{fmt_currency(row['nov_purchase_revenue'])} | "
            f"{fmt_pp(row['cart_to_purchase_rate_change_pp'])} |"
        )

    return "\n".join(lines)


def build_conversion_table(df: pd.DataFrame) -> str:
    ordered_df = (
        df[df["cart_to_purchase_rate_change_pp"].notna()]
        .sort_values("cart_to_purchase_rate_change_pp", ascending=True)
        .copy()
    )

    lines = [
        "| Price Band | Oct Cart→Purchase | Nov Cart→Purchase | Change | Nov Revenue |",
        "|---|---:|---:|---:|---:|",
    ]

    for _, row in ordered_df.iterrows():
        lines.append(
            "| "
            f"{row['price_band']} | "
            f"{fmt_pct(row['oct_cart_to_purchase_rate_pct'])} | "
            f"{fmt_pct(row['nov_cart_to_purchase_rate_pct'])} | "
            f"{fmt_pp(row['cart_to_purchase_rate_change_pp'])} | "
            f"{fmt_currency(row['nov_purchase_revenue'])} |"
        )

    return "\n".join(lines)


def build_report(df: pd.DataFrame) -> str:
    band_800_1199 = get_row(df, "$800-$1199")
    band_1200_plus = get_row(df, "$1200+")
    band_100_249 = get_row(df, "$100-$249")
    band_250_499 = get_row(df, "$250-$499")
    band_500_799 = get_row(df, "$500-$799")

    premium_revenue = (
        safe_float(band_800_1199, "nov_purchase_revenue")
        + safe_float(band_1200_plus, "nov_purchase_revenue")
    )

    premium_revenue_share = (
        safe_float(band_800_1199, "nov_smartphone_revenue_share_pct")
        + safe_float(band_1200_plus, "nov_smartphone_revenue_share_pct")
    )

    premium_growth_share = (
        safe_float(band_800_1199, "net_smartphone_revenue_growth_share_pct")
        + safe_float(band_1200_plus, "net_smartphone_revenue_growth_share_pct")
    )

    primary_growth_triplet_share = (
        safe_float(band_800_1199, "net_smartphone_revenue_growth_share_pct")
        + safe_float(band_100_249, "net_smartphone_revenue_growth_share_pct")
        + safe_float(band_1200_plus, "net_smartphone_revenue_growth_share_pct")
    )

    revenue_table = build_revenue_table(df)
    growth_table = build_growth_table(df)
    conversion_table = build_conversion_table(df)

    report = f"""# CommercePulse Smartphone Price-Band Diagnostics

## Objective

This report examines smartphone performance by price band to answer:

1. Which smartphone price tiers drove November revenue growth?
2. Which price tiers suffered the largest cart-to-purchase deterioration?
3. Whether the smartphone growth-and-efficiency tradeoff was concentrated in premium, mid-range, or budget segments.

---

## Executive Summary

Smartphone revenue growth in November was concentrated in a small set of price bands.

- The **$800-$1199** band generated **{fmt_currency(safe_float(band_800_1199, 'nov_purchase_revenue'))}** in November revenue and contributed **{fmt_currency(safe_float(band_800_1199, 'revenue_delta'))}** in incremental revenue.
- The **$1200+** band generated **{fmt_currency(safe_float(band_1200_plus, 'nov_purchase_revenue'))}** and added **{fmt_currency(safe_float(band_1200_plus, 'revenue_delta'))}** in revenue.
- Together, those premium bands generated **{fmt_currency(premium_revenue)}**, representing **{fmt_pct(premium_revenue_share)}** of all smartphone revenue.
- Their combined contribution represented **{fmt_pct(premium_growth_share)}** of net smartphone revenue growth.

A third major growth contributor was the **$100-$249** value segment:

- It added **{fmt_currency(safe_float(band_100_249, 'revenue_delta'))}** in revenue.
- It represented **{fmt_pct(safe_float(band_100_249, 'net_smartphone_revenue_growth_share_pct'))}** of net smartphone growth.

Together, the three leading positive-growth bands — **$800-$1199**, **$100-$249**, and **$1200+** — explain **{fmt_pct(primary_growth_triplet_share)}** of net smartphone revenue growth, before offsetting declines in other bands.

---

## Smartphone Revenue by Price Band

{revenue_table}

---

## Smartphone Revenue Growth Contributors

{growth_table}

---

## Smartphone Cart-to-Purchase Conversion by Price Band

{conversion_table}

---

## Business Interpretation

### 1. Premium smartphone tiers were the largest revenue engine
The **$800-$1199** and **$1200+** bands together generated more than half of November smartphone revenue. This means the smartphone growth story was materially influenced by premium-product demand.

### 2. The $800-$1199 tier is the highest-priority price diagnostic
This band combined:

- The largest positive revenue delta: **{fmt_currency(safe_float(band_800_1199, 'revenue_delta'))}**
- The largest net growth share: **{fmt_pct(safe_float(band_800_1199, 'net_smartphone_revenue_growth_share_pct'))}**
- A major cart-to-purchase decline: **{fmt_pp(safe_float(band_800_1199, 'cart_to_purchase_rate_change_pp'))}**

That combination makes it one of the most important price segments to investigate further.

### 3. The $100-$249 band grew strongly, showing a second growth pocket
The **$100-$249** band contributed **{fmt_currency(safe_float(band_100_249, 'revenue_delta'))}** in additional revenue. This indicates that November smartphone growth was not exclusively premium-led; the lower-price value segment also expanded meaningfully.

### 4. The mid-range segments underperformed
The **$250-$499** and **$500-$799** bands both showed negative revenue deltas:

- **$250-$499:** {fmt_currency(safe_float(band_250_499, 'revenue_delta'))}
- **$500-$799:** {fmt_currency(safe_float(band_500_799, 'revenue_delta'))}

The **$250-$499** band also experienced the sharpest cart-to-purchase decline at **{fmt_pp(safe_float(band_250_499, 'cart_to_purchase_rate_change_pp'))}**.

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
"""

    return report


def main() -> int:
    project_root = get_project_root()

    db_path = project_root / "data" / "processed" / "commercepulse.duckdb"

    diagnostics_csv_path = (
        project_root
        / "outputs"
        / "tables"
        / "mart_smartphone_price_band_mom_diagnostics.csv"
    )

    monthly_price_band_csv_path = (
        project_root
        / "outputs"
        / "tables"
        / "mart_monthly_smartphone_price_band_performance.csv"
    )

    report_path = (
        project_root
        / "reports"
        / "smartphone_price_band_diagnostics.md"
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
        monthly_price_band_csv_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)

        con = duckdb.connect(database=str(db_path), read_only=True)

        diagnostics_df = con.execute(
            """
            SELECT *
            FROM mart_smartphone_price_band_mom_diagnostics
            ORDER BY price_band_order;
            """
        ).df()

        monthly_price_band_df = con.execute(
            """
            SELECT *
            FROM mart_monthly_smartphone_price_band_performance
            ORDER BY event_month, price_band_order;
            """
        ).df()

        con.close()

        if diagnostics_df.empty:
            raise ValueError(
                "mart_smartphone_price_band_mom_diagnostics returned no rows."
            )

        diagnostics_df.to_csv(diagnostics_csv_path, index=False)
        monthly_price_band_df.to_csv(monthly_price_band_csv_path, index=False)

        report_content = build_report(diagnostics_df)
        report_path.write_text(report_content, encoding="utf-8")

        console.print(
            f"[bold green]Smartphone price-band diagnostics CSV exported:[/bold green] {diagnostics_csv_path}"
        )
        console.print(
            f"[bold green]Monthly smartphone price-band performance CSV exported:[/bold green] {monthly_price_band_csv_path}"
        )
        console.print(
            f"[bold green]Smartphone price-band report generated:[/bold green] {report_path}"
        )

        console.print(
            f"\n[bold cyan]Smartphone price-band diagnostic rows exported:[/bold cyan] {len(diagnostics_df)}"
        )
        console.print(
            f"[bold cyan]Monthly smartphone price-band rows exported:[/bold cyan] {len(monthly_price_band_df)}"
        )

    except Exception as exc:
        console.print(
            f"[bold red]Smartphone price-band report generation failed:[/bold red] {exc}"
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())