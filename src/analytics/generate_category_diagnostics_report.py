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
    src/analytics/generate_category_diagnostics_report.py
    """
    return Path(__file__).resolve().parents[2]


def fmt_currency(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"${float(value):,.2f}"


def fmt_int(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{int(value):,}"


def fmt_pct(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{float(value):.2f}%"


def fmt_pp(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    sign = "+" if float(value) >= 0 else ""
    return f"{sign}{float(value):.2f} pp"


def build_top_growth_table(df: pd.DataFrame, top_n: int = 10) -> str:
    top_df = (
        df.sort_values("revenue_delta", ascending=False)
        .head(top_n)
        .copy()
    )

    lines = [
        "| Category | Oct Revenue | Nov Revenue | Revenue Delta | Revenue Growth | Cart→Purchase Δ |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for _, row in top_df.iterrows():
        lines.append(
            "| "
            f"{row['category_l1']} | "
            f"{fmt_currency(row['oct_purchase_revenue'])} | "
            f"{fmt_currency(row['nov_purchase_revenue'])} | "
            f"{fmt_currency(row['revenue_delta'])} | "
            f"{fmt_pct(row['revenue_growth_pct'])} | "
            f"{fmt_pp(row['cart_to_purchase_rate_change_pp'])} |"
        )

    return "\n".join(lines)


def build_conversion_decline_table(df: pd.DataFrame, top_n: int = 10) -> str:
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
        "| Category | Oct Cart→Purchase | Nov Cart→Purchase | Change | Nov Revenue |",
        "|---|---:|---:|---:|---:|",
    ]

    for _, row in decline_df.iterrows():
        lines.append(
            "| "
            f"{row['category_l1']} | "
            f"{fmt_pct(row['oct_cart_to_purchase_rate_pct'])} | "
            f"{fmt_pct(row['nov_cart_to_purchase_rate_pct'])} | "
            f"{fmt_pp(row['cart_to_purchase_rate_change_pp'])} | "
            f"{fmt_currency(row['nov_purchase_revenue'])} |"
        )

    return "\n".join(lines)


def build_revenue_concentration_summary(df: pd.DataFrame) -> dict[str, float]:
    positive_growth_df = df[df["revenue_delta"] > 0].copy()

    total_positive_revenue_delta = float(positive_growth_df["revenue_delta"].sum())

    top_4_delta = float(
        positive_growth_df.sort_values("revenue_delta", ascending=False)
        .head(4)["revenue_delta"]
        .sum()
    )

    top_4_share_pct = (
        100.0 * top_4_delta / total_positive_revenue_delta
        if total_positive_revenue_delta != 0
        else 0.0
    )

    electronics_row = df[df["category_l1"] == "electronics"]
    unknown_row = df[df["category_l1"] == "unknown"]
    appliances_row = df[df["category_l1"] == "appliances"]
    computers_row = df[df["category_l1"] == "computers"]

    return {
        "total_positive_revenue_delta": total_positive_revenue_delta,
        "top_4_delta": top_4_delta,
        "top_4_share_pct": top_4_share_pct,
        "electronics_delta": (
            float(electronics_row.iloc[0]["revenue_delta"])
            if not electronics_row.empty
            else 0.0
        ),
        "unknown_delta": (
            float(unknown_row.iloc[0]["revenue_delta"])
            if not unknown_row.empty
            else 0.0
        ),
        "appliances_delta": (
            float(appliances_row.iloc[0]["revenue_delta"])
            if not appliances_row.empty
            else 0.0
        ),
        "computers_delta": (
            float(computers_row.iloc[0]["revenue_delta"])
            if not computers_row.empty
            else 0.0
        ),
    }


def get_category_row(df: pd.DataFrame, category: str) -> pd.Series | None:
    match = df[df["category_l1"] == category]
    if match.empty:
        return None
    return match.iloc[0]


def build_report(df: pd.DataFrame) -> str:
    concentration = build_revenue_concentration_summary(df)

    electronics = get_category_row(df, "electronics")
    unknown = get_category_row(df, "unknown")
    appliances = get_category_row(df, "appliances")
    computers = get_category_row(df, "computers")

    top_growth_table = build_top_growth_table(df)
    decline_table = build_conversion_decline_table(df)

    electronics_revenue = fmt_currency(
        electronics["nov_purchase_revenue"] if electronics is not None else None
    )
    electronics_delta = fmt_currency(
        electronics["revenue_delta"] if electronics is not None else None
    )
    electronics_cart_decline = fmt_pp(
        electronics["cart_to_purchase_rate_change_pp"]
        if electronics is not None
        else None
    )

    unknown_revenue = fmt_currency(
        unknown["nov_purchase_revenue"] if unknown is not None else None
    )
    unknown_delta = fmt_currency(
        unknown["revenue_delta"] if unknown is not None else None
    )
    unknown_cart_decline = fmt_pp(
        unknown["cart_to_purchase_rate_change_pp"]
        if unknown is not None
        else None
    )

    appliances_delta = fmt_currency(
        appliances["revenue_delta"] if appliances is not None else None
    )
    computers_delta = fmt_currency(
        computers["revenue_delta"] if computers is not None else None
    )

    report = f"""# CommercePulse Category Growth Diagnostics

## Objective

This report investigates the month-over-month category shifts between **2019-10** and **2019-11**, with special focus on:

1. Which categories drove November revenue growth?
2. Which categories experienced the largest deterioration in cart-to-purchase efficiency?
3. Whether November growth was broad-based or concentrated in a small number of categories.

---

## Executive Summary

November revenue growth was highly concentrated in a small set of category groups.

- The four largest positive category revenue contributors — **electronics, unknown, appliances, and computers** — generated **{fmt_currency(concentration['top_4_delta'])}** in combined positive revenue delta.
- These four categories accounted for **{fmt_pct(concentration['top_4_share_pct'])}** of all positive category-level revenue growth.
- **Electronics** was the dominant driver, contributing **{electronics_delta}** in revenue growth and reaching **{electronics_revenue}** in November purchase revenue.
- However, electronics also suffered a **{electronics_cart_decline}** decline in session-level cart-to-purchase conversion.
- The `unknown` category represented **{unknown_revenue}** in November revenue and grew by **{unknown_delta}**, making uncategorized product activity analytically material rather than negligible.

---

## Top Revenue Growth Categories

{top_growth_table}

---

## Categories with the Largest Cart-to-Purchase Efficiency Declines

{decline_table}

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
Electronics added **{electronics_delta}** in revenue, making it the largest month-over-month contributor. At the same time, its cart-to-purchase conversion declined by **{electronics_cart_decline}**.

This combination is important:

> Electronics created substantial incremental revenue, but a materially smaller share of carting sessions converted to purchases.

That pattern deserves deeper follow-up by subcategory, brand, and price band.

### 3. Appliances and computers show a similar pattern
Appliances and computers contributed **{appliances_delta}** and **{computers_delta}** in incremental revenue, respectively. Both also experienced major drops in cart-to-purchase efficiency.

This suggests the funnel deterioration was especially visible in several higher-ticket technology and home-product segments.

### 4. Uncategorized activity is financially significant
The `unknown` category is not a minor residual bucket. It generated **{unknown_revenue}** in November revenue and grew by **{unknown_delta}**.

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
"""

    return report


def main() -> int:
    project_root = get_project_root()

    db_path = project_root / "data" / "processed" / "commercepulse.duckdb"

    diagnostics_csv_path = (
        project_root / "outputs" / "tables" / "mart_category_mom_diagnostics.csv"
    )

    monthly_category_csv_path = (
        project_root / "outputs" / "tables" / "mart_monthly_category_performance.csv"
    )

    report_path = (
        project_root / "reports" / "category_growth_diagnostics.md"
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
        monthly_category_csv_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)

        con = duckdb.connect(database=str(db_path), read_only=True)

        diagnostics_df = con.execute(
            """
            SELECT *
            FROM mart_category_mom_diagnostics
            ORDER BY revenue_delta DESC;
            """
        ).df()

        monthly_category_df = con.execute(
            """
            SELECT *
            FROM mart_monthly_category_performance
            ORDER BY event_month, purchase_revenue DESC;
            """
        ).df()

        con.close()

        if diagnostics_df.empty:
            raise ValueError("mart_category_mom_diagnostics returned no rows.")

        diagnostics_df.to_csv(diagnostics_csv_path, index=False)
        monthly_category_df.to_csv(monthly_category_csv_path, index=False)

        report_content = build_report(diagnostics_df)
        report_path.write_text(report_content, encoding="utf-8")

        console.print(
            f"[bold green]Category diagnostics CSV exported:[/bold green] {diagnostics_csv_path}"
        )
        console.print(
            f"[bold green]Monthly category performance CSV exported:[/bold green] {monthly_category_csv_path}"
        )
        console.print(
            f"[bold green]Category diagnostics report generated:[/bold green] {report_path}"
        )

        console.print(
            f"\n[bold cyan]Diagnostic rows exported:[/bold cyan] {len(diagnostics_df)}"
        )
        console.print(
            f"[bold cyan]Monthly category rows exported:[/bold cyan] {len(monthly_category_df)}"
        )

    except Exception as exc:
        console.print(f"[bold red]Category report generation failed:[/bold red] {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())