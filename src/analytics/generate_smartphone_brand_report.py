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
    src/analytics/generate_smartphone_brand_report.py
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


def get_row(df: pd.DataFrame, brand: str) -> pd.Series | None:
    match = df[df["brand"] == brand]

    if match.empty:
        return None

    return match.iloc[0]


def build_revenue_leaders_table(df: pd.DataFrame, top_n: int = 12) -> str:
    top_df = (
        df.sort_values("nov_purchase_revenue", ascending=False)
        .head(top_n)
        .copy()
    )

    lines = [
        "| Brand | Nov Revenue | Smartphone Revenue Share | Revenue Delta | Revenue Growth | Cart→Purchase Δ |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for _, row in top_df.iterrows():
        lines.append(
            "| "
            f"{row['brand']} | "
            f"{fmt_currency(row['nov_purchase_revenue'])} | "
            f"{fmt_pct(row['nov_smartphone_revenue_share_pct'])} | "
            f"{fmt_currency(row['revenue_delta'])} | "
            f"{fmt_pct(row['revenue_growth_pct'])} | "
            f"{fmt_pp(row['cart_to_purchase_rate_change_pp'])} |"
        )

    return "\n".join(lines)


def build_growth_contributors_table(df: pd.DataFrame, top_n: int = 12) -> str:
    top_df = (
        df.sort_values("revenue_delta", ascending=False)
        .head(top_n)
        .copy()
    )

    lines = [
        "| Brand | Revenue Delta | Net Growth Share | Revenue Growth | Nov Revenue | Cart→Purchase Δ |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for _, row in top_df.iterrows():
        lines.append(
            "| "
            f"{row['brand']} | "
            f"{fmt_currency(row['revenue_delta'])} | "
            f"{fmt_pct(row['net_smartphone_revenue_growth_share_pct'])} | "
            f"{fmt_pct(row['revenue_growth_pct'])} | "
            f"{fmt_currency(row['nov_purchase_revenue'])} | "
            f"{fmt_pp(row['cart_to_purchase_rate_change_pp'])} |"
        )

    return "\n".join(lines)


def build_conversion_decline_table(df: pd.DataFrame, top_n: int = 12) -> str:
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
        "| Brand | Oct Cart→Purchase | Nov Cart→Purchase | Change | Nov Revenue |",
        "|---|---:|---:|---:|---:|",
    ]

    for _, row in decline_df.iterrows():
        lines.append(
            "| "
            f"{row['brand']} | "
            f"{fmt_pct(row['oct_cart_to_purchase_rate_pct'])} | "
            f"{fmt_pct(row['nov_cart_to_purchase_rate_pct'])} | "
            f"{fmt_pp(row['cart_to_purchase_rate_change_pp'])} | "
            f"{fmt_currency(row['nov_purchase_revenue'])} |"
        )

    return "\n".join(lines)


def build_report(df: pd.DataFrame) -> str:
    apple = get_row(df, "apple")
    samsung = get_row(df, "samsung")
    xiaomi = get_row(df, "xiaomi")
    oppo = get_row(df, "oppo")
    huawei = get_row(df, "huawei")

    apple_revenue_share = safe_float(
        apple,
        "nov_smartphone_revenue_share_pct",
    )
    samsung_revenue_share = safe_float(
        samsung,
        "nov_smartphone_revenue_share_pct",
    )
    apple_samsung_revenue_share = apple_revenue_share + samsung_revenue_share

    apple_growth_share = safe_float(
        apple,
        "net_smartphone_revenue_growth_share_pct",
    )
    samsung_growth_share = safe_float(
        samsung,
        "net_smartphone_revenue_growth_share_pct",
    )
    apple_samsung_growth_share = apple_growth_share + samsung_growth_share

    revenue_leaders_table = build_revenue_leaders_table(df)
    growth_contributors_table = build_growth_contributors_table(df)
    conversion_decline_table = build_conversion_decline_table(df)

    report = f"""# CommercePulse Smartphone Brand Diagnostics

## Objective

This report investigates brand-level behavior within the **electronics → smartphone** segment to answer:

1. Which smartphone brands drove November revenue growth?
2. Which brands contributed most to weaker cart-to-purchase conversion?
3. Whether the smartphone funnel deterioration was concentrated among major revenue-generating brands.

---

## Executive Summary

Smartphone revenue in November was heavily concentrated in two brands:

- **Apple** generated **{fmt_currency(safe_float(apple, 'nov_purchase_revenue'))}**, representing **{fmt_pct(apple_revenue_share)}** of smartphone revenue.
- **Samsung** generated **{fmt_currency(safe_float(samsung, 'nov_purchase_revenue'))}**, representing **{fmt_pct(samsung_revenue_share)}** of smartphone revenue.
- Together, Apple and Samsung contributed **{fmt_pct(apple_samsung_revenue_share)}** of all November smartphone revenue.

They also dominated month-over-month smartphone revenue growth:

- Apple added **{fmt_currency(safe_float(apple, 'revenue_delta'))}**, representing **{fmt_pct(apple_growth_share)}** of net smartphone revenue growth.
- Samsung added **{fmt_currency(safe_float(samsung, 'revenue_delta'))}**, representing **{fmt_pct(samsung_growth_share)}** of net smartphone revenue growth.
- Combined, Apple and Samsung accounted for **{fmt_pct(apple_samsung_growth_share)}** of net smartphone revenue expansion.

However, both brands experienced significant downstream funnel deterioration:

- Apple cart-to-purchase conversion changed by **{fmt_pp(safe_float(apple, 'cart_to_purchase_rate_change_pp'))}**.
- Samsung cart-to-purchase conversion changed by **{fmt_pp(safe_float(samsung, 'cart_to_purchase_rate_change_pp'))}**.

This means the brands driving smartphone growth were also major contributors to weaker purchase efficiency after carting.

---

## Smartphone Revenue Leaders

{revenue_leaders_table}

---

## Smartphone Revenue Growth Contributors

{growth_contributors_table}

---

## Largest Cart-to-Purchase Efficiency Declines

{conversion_decline_table}

---

## Business Interpretation

### 1. Apple is the highest-priority brand diagnostic
Apple is the dominant smartphone brand by every major scale indicator:

- November revenue: **{fmt_currency(safe_float(apple, 'nov_purchase_revenue'))}**
- Revenue growth: **{fmt_currency(safe_float(apple, 'revenue_delta'))}**
- Smartphone revenue share: **{fmt_pct(apple_revenue_share)}**
- Net growth share: **{fmt_pct(apple_growth_share)}**
- Cart-to-purchase change: **{fmt_pp(safe_float(apple, 'cart_to_purchase_rate_change_pp'))}**

Because Apple combines the largest revenue base, the largest revenue lift, and a major conversion decline, it should be the first brand-level diagnostic priority.

### 2. Samsung is the second major growth-and-efficiency story
Samsung added **{fmt_currency(safe_float(samsung, 'revenue_delta'))}** in revenue and represents **{fmt_pct(samsung_revenue_share)}** of smartphone revenue. Its cart-to-purchase conversion also declined by **{fmt_pp(safe_float(samsung, 'cart_to_purchase_rate_change_pp'))}**.

This shows the broader smartphone pattern was not only an Apple-specific issue.

### 3. Xiaomi and Oppo expanded rapidly but converted less efficiently
- Xiaomi revenue increased by **{fmt_currency(safe_float(xiaomi, 'revenue_delta'))}** with a cart-to-purchase change of **{fmt_pp(safe_float(xiaomi, 'cart_to_purchase_rate_change_pp'))}**.
- Oppo revenue increased by **{fmt_currency(safe_float(oppo, 'revenue_delta'))}** with a cart-to-purchase change of **{fmt_pp(safe_float(oppo, 'cart_to_purchase_rate_change_pp'))}**.

These brands may represent growing interest in lower-cost or alternative smartphone segments, but their funnel quality weakened in November.

### 4. Huawei is a modest but important negative-growth signal
Huawei revenue declined by **{fmt_currency(safe_float(huawei, 'revenue_delta'))}** while its cart-to-purchase rate changed by **{fmt_pp(safe_float(huawei, 'cart_to_purchase_rate_change_pp'))}**.

This does not dominate platform economics, but it is a clear underperformance case worth retaining in the diagnostic narrative.

---

## Analytical Hypotheses to Test Next

These are hypotheses, not confirmed causes:

1. Apple and Samsung may have experienced stronger top-of-funnel shopping activity due to seasonal demand or promotions.
2. The cart-to-purchase decline may be concentrated in specific **price bands** rather than across all smartphone prices.
3. Higher-priced smartphone tiers may show greater comparison-shopping and lower checkout completion.
4. Some brands may have expanded cart volume much faster than purchase volume, indicating weaker conversion quality.

---

## Recommended Next Step

The next diagnostic layer should analyze **smartphone price bands** to answer:

1. Which price tiers drove revenue growth?
2. Which price tiers experienced the largest cart-to-purchase deterioration?
3. Whether premium or mid-range smartphones explain the November conversion shift.

---

## Method Notes

- This analysis is restricted to `category_l1 = 'electronics'` and `category_l2 = 'smartphone'`.
- Missing brand values are grouped under `unknown`.
- Revenue is calculated as the sum of `price` for purchase events.
- Cart-to-purchase conversion is computed at the session level.
- Growth-share percentages are calculated relative to net smartphone revenue growth; categories with negative revenue deltas can cause the total share of positive contributors to exceed 100%.
"""

    return report


def main() -> int:
    project_root = get_project_root()

    db_path = project_root / "data" / "processed" / "commercepulse.duckdb"

    diagnostics_csv_path = (
        project_root
        / "outputs"
        / "tables"
        / "mart_smartphone_brand_mom_diagnostics.csv"
    )

    monthly_brand_csv_path = (
        project_root
        / "outputs"
        / "tables"
        / "mart_monthly_smartphone_brand_performance.csv"
    )

    report_path = (
        project_root
        / "reports"
        / "smartphone_brand_diagnostics.md"
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
        monthly_brand_csv_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)

        con = duckdb.connect(database=str(db_path), read_only=True)

        diagnostics_df = con.execute(
            """
            SELECT *
            FROM mart_smartphone_brand_mom_diagnostics
            ORDER BY revenue_delta DESC;
            """
        ).df()

        monthly_brand_df = con.execute(
            """
            SELECT *
            FROM mart_monthly_smartphone_brand_performance
            ORDER BY event_month, purchase_revenue DESC;
            """
        ).df()

        con.close()

        if diagnostics_df.empty:
            raise ValueError(
                "mart_smartphone_brand_mom_diagnostics returned no rows."
            )

        diagnostics_df.to_csv(diagnostics_csv_path, index=False)
        monthly_brand_df.to_csv(monthly_brand_csv_path, index=False)

        report_content = build_report(diagnostics_df)
        report_path.write_text(report_content, encoding="utf-8")

        console.print(
            f"[bold green]Smartphone brand diagnostics CSV exported:[/bold green] {diagnostics_csv_path}"
        )
        console.print(
            f"[bold green]Monthly smartphone brand performance CSV exported:[/bold green] {monthly_brand_csv_path}"
        )
        console.print(
            f"[bold green]Smartphone brand report generated:[/bold green] {report_path}"
        )

        console.print(
            f"\n[bold cyan]Smartphone brand diagnostic rows exported:[/bold cyan] {len(diagnostics_df)}"
        )
        console.print(
            f"[bold cyan]Monthly smartphone brand rows exported:[/bold cyan] {len(monthly_brand_df)}"
        )

    except Exception as exc:
        console.print(
            f"[bold red]Smartphone brand report generation failed:[/bold red] {exc}"
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())