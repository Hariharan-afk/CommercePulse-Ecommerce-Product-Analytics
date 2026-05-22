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
    src/analytics/generate_electronics_subcategory_report.py
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


def get_row(df: pd.DataFrame, subcategory: str) -> pd.Series | None:
    match = df[df["category_l2"] == subcategory]
    if match.empty:
        return None
    return match.iloc[0]


def safe_float(row: pd.Series | None, column: str) -> float:
    if row is None:
        return 0.0
    value = row[column]
    if pd.isna(value):
        return 0.0
    return float(value)


def build_revenue_leaders_table(df: pd.DataFrame, top_n: int = 10) -> str:
    top_df = (
        df.sort_values("nov_purchase_revenue", ascending=False)
        .head(top_n)
        .copy()
    )

    lines = [
        "| Subcategory | Nov Revenue | Electronics Revenue Share | Revenue Delta | Revenue Growth | Cart→Purchase Δ |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for _, row in top_df.iterrows():
        lines.append(
            "| "
            f"{row['category_l2']} | "
            f"{fmt_currency(row['nov_purchase_revenue'])} | "
            f"{fmt_pct(row['nov_electronics_revenue_share_pct'])} | "
            f"{fmt_currency(row['revenue_delta'])} | "
            f"{fmt_pct(row['revenue_growth_pct'])} | "
            f"{fmt_pp(row['cart_to_purchase_rate_change_pp'])} |"
        )

    return "\n".join(lines)


def build_growth_contributors_table(df: pd.DataFrame, top_n: int = 10) -> str:
    top_df = (
        df.sort_values("revenue_delta", ascending=False)
        .head(top_n)
        .copy()
    )

    lines = [
        "| Subcategory | Revenue Delta | Revenue Growth | Nov Revenue | Cart→Purchase Δ |",
        "|---|---:|---:|---:|---:|",
    ]

    for _, row in top_df.iterrows():
        lines.append(
            "| "
            f"{row['category_l2']} | "
            f"{fmt_currency(row['revenue_delta'])} | "
            f"{fmt_pct(row['revenue_growth_pct'])} | "
            f"{fmt_currency(row['nov_purchase_revenue'])} | "
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
        "| Subcategory | Oct Cart→Purchase | Nov Cart→Purchase | Change | Nov Revenue |",
        "|---|---:|---:|---:|---:|",
    ]

    for _, row in decline_df.iterrows():
        lines.append(
            "| "
            f"{row['category_l2']} | "
            f"{fmt_pct(row['oct_cart_to_purchase_rate_pct'])} | "
            f"{fmt_pct(row['nov_cart_to_purchase_rate_pct'])} | "
            f"{fmt_pp(row['cart_to_purchase_rate_change_pp'])} | "
            f"{fmt_currency(row['nov_purchase_revenue'])} |"
        )

    return "\n".join(lines)


def build_report(df: pd.DataFrame) -> str:
    smartphone = get_row(df, "smartphone")
    video = get_row(df, "video")
    audio = get_row(df, "audio")
    clocks = get_row(df, "clocks")
    tablet = get_row(df, "tablet")

    total_electronics_net_growth = float(df["revenue_delta"].sum())

    smartphone_growth = safe_float(smartphone, "revenue_delta")
    smartphone_growth_share = (
        100.0 * smartphone_growth / total_electronics_net_growth
        if total_electronics_net_growth != 0
        else 0.0
    )

    top_positive_growth = (
        df[df["revenue_delta"] > 0]
        .sort_values("revenue_delta", ascending=False)
        .head(4)["revenue_delta"]
        .sum()
    )

    revenue_leaders_table = build_revenue_leaders_table(df)
    growth_contributors_table = build_growth_contributors_table(df)
    decline_table = build_conversion_decline_table(df)

    report = f"""# CommercePulse Electronics Subcategory Diagnostics

## Objective

This report drills into the **electronics** category to identify:

1. Which electronics subcategories drove November revenue growth?
2. Which subcategories experienced the largest cart-to-purchase deterioration?
3. Whether the electronics funnel issue was concentrated or broad-based.

---

## Executive Summary

Electronics revenue growth in November was overwhelmingly driven by **smartphones**.

- **Smartphones generated {fmt_currency(safe_float(smartphone, 'nov_purchase_revenue'))}** in November revenue.
- They represented **{fmt_pct(safe_float(smartphone, 'nov_electronics_revenue_share_pct'))}** of all November electronics revenue.
- Smartphone revenue increased by **{fmt_currency(smartphone_growth)}** month over month.
- Smartphones alone accounted for approximately **{fmt_pct(smartphone_growth_share)}** of the net electronics revenue increase.

However, this growth came alongside weaker downstream conversion:

- Smartphone cart-to-purchase conversion declined by **{fmt_pp(safe_float(smartphone, 'cart_to_purchase_rate_change_pp'))}**.
- Tablet conversion declined even more sharply at **{fmt_pp(safe_float(tablet, 'cart_to_purchase_rate_change_pp'))}**, while tablet revenue also decreased.
- Video, audio, and clocks posted strong revenue growth but also suffered conversion deterioration.

---

## November Electronics Revenue Leaders

{revenue_leaders_table}

---

## Electronics Revenue Growth Contributors

{growth_contributors_table}

---

## Largest Electronics Cart-to-Purchase Efficiency Declines

{decline_table}

---

## Business Interpretation

### 1. Smartphone is the highest-priority diagnostic segment
Smartphones dominate electronics economics:

- Revenue scale: **{fmt_currency(safe_float(smartphone, 'nov_purchase_revenue'))}**
- Revenue delta: **{fmt_currency(smartphone_growth)}**
- Electronics revenue share: **{fmt_pct(safe_float(smartphone, 'nov_electronics_revenue_share_pct'))}**
- Cart-to-purchase change: **{fmt_pp(safe_float(smartphone, 'cart_to_purchase_rate_change_pp'))}**

This makes smartphone the most important subcategory for understanding the November funnel shift.

### 2. The conversion decline is not a single-subcategory anomaly
Every material electronics subcategory with meaningful cart activity experienced a cart-to-purchase decline. This suggests that the electronics funnel issue was broad-based rather than limited to one product group.

### 3. Fast-growing subcategories also became less efficient
Several subcategories grew substantially in revenue:

- Video: **{fmt_currency(safe_float(video, 'revenue_delta'))}**
- Audio: **{fmt_currency(safe_float(audio, 'revenue_delta'))}**
- Clocks: **{fmt_currency(safe_float(clocks, 'revenue_delta'))}**

Yet all three experienced meaningful cart-to-purchase rate declines.

### 4. Tablet deserves attention as a negative outlier
Tablet revenue declined by **{fmt_currency(safe_float(tablet, 'revenue_delta'))}**, and its cart-to-purchase rate deteriorated by **{fmt_pp(safe_float(tablet, 'cart_to_purchase_rate_change_pp'))}**.

Although tablets are not the largest revenue contributor, this combination of negative revenue growth and the sharpest conversion drop makes them a clear underperformance segment.

---

## Analytical Hypotheses to Test Next

These remain hypotheses rather than confirmed causes:

1. A few **smartphone brands** may be responsible for most revenue growth and most conversion deterioration.
2. November smartphone cart growth may be concentrated in **higher-priced devices** or promotional price bands.
3. Video and audio growth may reflect broader holiday-season shopping behavior, but with weaker purchasing commitment.
4. Tablet underperformance may be tied to lower demand, pricing dynamics, or product mix changes.

---

## Recommended Next Step

The next diagnostic layer should investigate:

### A. Smartphone brand performance
- Which brands drove smartphone revenue growth?
- Which brands saw the largest cart-to-purchase deterioration?

### B. Smartphone price-band behavior
- Did higher-priced or lower-priced smartphones drive cart expansion?
- Which price bands converted worse in November?

---

## Method Notes

- This analysis uses `category_l2` values nested under `category_l1 = 'electronics'`.
- Revenue is calculated as the sum of `price` for purchase events.
- Cart-to-purchase conversion is computed at the session level.
- Only subcategories with sufficient cart volume are included in the conversion-decline diagnostic table.
- The sum of the largest positive growth contributors slightly exceeds net electronics growth because some subcategories, such as tablets, experienced negative revenue deltas.
"""

    return report


def main() -> int:
    project_root = get_project_root()

    db_path = project_root / "data" / "processed" / "commercepulse.duckdb"

    diagnostics_csv_path = (
        project_root
        / "outputs"
        / "tables"
        / "mart_electronics_subcategory_mom_diagnostics.csv"
    )

    monthly_subcategory_csv_path = (
        project_root
        / "outputs"
        / "tables"
        / "mart_monthly_subcategory_performance.csv"
    )

    report_path = (
        project_root
        / "reports"
        / "electronics_subcategory_diagnostics.md"
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
        monthly_subcategory_csv_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)

        con = duckdb.connect(database=str(db_path), read_only=True)

        diagnostics_df = con.execute(
            """
            SELECT *
            FROM mart_electronics_subcategory_mom_diagnostics
            ORDER BY revenue_delta DESC;
            """
        ).df()

        monthly_subcategory_df = con.execute(
            """
            SELECT *
            FROM mart_monthly_subcategory_performance
            ORDER BY event_month, category_l1, purchase_revenue DESC;
            """
        ).df()

        con.close()

        if diagnostics_df.empty:
            raise ValueError(
                "mart_electronics_subcategory_mom_diagnostics returned no rows."
            )

        diagnostics_df.to_csv(diagnostics_csv_path, index=False)
        monthly_subcategory_df.to_csv(monthly_subcategory_csv_path, index=False)

        report_content = build_report(diagnostics_df)
        report_path.write_text(report_content, encoding="utf-8")

        console.print(
            f"[bold green]Electronics diagnostics CSV exported:[/bold green] {diagnostics_csv_path}"
        )
        console.print(
            f"[bold green]Monthly subcategory performance CSV exported:[/bold green] {monthly_subcategory_csv_path}"
        )
        console.print(
            f"[bold green]Electronics diagnostics report generated:[/bold green] {report_path}"
        )

        console.print(
            f"\n[bold cyan]Electronics diagnostic rows exported:[/bold cyan] {len(diagnostics_df)}"
        )
        console.print(
            f"[bold cyan]Monthly subcategory rows exported:[/bold cyan] {len(monthly_subcategory_df)}"
        )

    except Exception as exc:
        console.print(
            f"[bold red]Electronics subcategory report generation failed:[/bold red] {exc}"
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())