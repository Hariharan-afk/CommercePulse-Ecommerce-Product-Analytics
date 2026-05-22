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
    src/analytics/generate_monthly_kpi_report.py
    """
    return Path(__file__).resolve().parents[2]


def pct_change(old: float, new: float) -> float:
    if old == 0:
        return 0.0
    return ((new - old) / old) * 100.0


def pp_change(old: float, new: float) -> float:
    return new - old


def fmt_int(value: float | int) -> str:
    return f"{int(value):,}"


def fmt_currency(value: float) -> str:
    return f"${value:,.2f}"


def fmt_pct(value: float) -> str:
    return f"{value:.2f}%"


def fmt_delta_pct(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"


def fmt_delta_pp(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f} pp"


def build_kpi_comparison_table(old_row: pd.Series, new_row: pd.Series) -> str:
    metrics = [
        ("Total events", "total_events", fmt_int, "pct"),
        ("Active users", "active_users", fmt_int, "pct"),
        ("Active sessions", "active_sessions", fmt_int, "pct"),
        ("Active products", "active_products", fmt_int, "pct"),
        ("Purchase events", "purchase_events", fmt_int, "pct"),
        ("Purchasing users", "purchasing_users", fmt_int, "pct"),
        ("Purchase revenue", "purchase_revenue", fmt_currency, "pct"),
        ("Average purchase price", "avg_purchase_price", fmt_currency, "pct"),
    ]

    lines = [
        "| Metric | Earlier Month | Later Month | Change |",
        "|---|---:|---:|---:|",
    ]

    for label, column, formatter, _change_type in metrics:
        old_value = float(old_row[column])
        new_value = float(new_row[column])
        change = pct_change(old_value, new_value)

        lines.append(
            f"| {label} | {formatter(old_value)} | {formatter(new_value)} | {fmt_delta_pct(change)} |"
        )

    return "\n".join(lines)


def build_funnel_comparison_table(old_row: pd.Series, new_row: pd.Series) -> str:
    metrics = [
        ("Session View → Cart Rate", "session_view_to_cart_rate_pct"),
        ("Session View → Purchase Rate", "session_view_to_purchase_rate_pct"),
        ("Session Cart → Purchase Rate", "session_cart_to_purchase_rate_pct"),
        (
            "Strict Session Funnel Completion Rate",
            "strict_session_funnel_completion_rate_pct",
        ),
        ("Event View → Cart Rate", "event_view_to_cart_rate_pct"),
        ("Event View → Purchase Rate", "event_view_to_purchase_rate_pct"),
    ]

    lines = [
        "| Funnel Metric | Earlier Month | Later Month | Change |",
        "|---|---:|---:|---:|",
    ]

    for label, column in metrics:
        old_value = float(old_row[column])
        new_value = float(new_row[column])
        change = pp_change(old_value, new_value)

        lines.append(
            f"| {label} | {fmt_pct(old_value)} | {fmt_pct(new_value)} | {fmt_delta_pp(change)} |"
        )

    return "\n".join(lines)


def build_markdown_report(df: pd.DataFrame) -> str:
    if len(df) < 2:
        raise ValueError(
            "At least two monthly rows are required to generate a comparison report."
        )

    df = df.sort_values("event_month").reset_index(drop=True)

    old_row = df.iloc[0]
    new_row = df.iloc[-1]

    old_month = str(old_row["event_month"])
    new_month = str(new_row["event_month"])

    total_events_change = pct_change(
        float(old_row["total_events"]),
        float(new_row["total_events"]),
    )
    active_users_change = pct_change(
        float(old_row["active_users"]),
        float(new_row["active_users"]),
    )
    sessions_change = pct_change(
        float(old_row["active_sessions"]),
        float(new_row["active_sessions"]),
    )
    purchases_change = pct_change(
        float(old_row["purchase_events"]),
        float(new_row["purchase_events"]),
    )
    revenue_change = pct_change(
        float(old_row["purchase_revenue"]),
        float(new_row["purchase_revenue"]),
    )
    avg_price_change = pct_change(
        float(old_row["avg_purchase_price"]),
        float(new_row["avg_purchase_price"]),
    )

    view_cart_pp = pp_change(
        float(old_row["session_view_to_cart_rate_pct"]),
        float(new_row["session_view_to_cart_rate_pct"]),
    )
    view_purchase_pp = pp_change(
        float(old_row["session_view_to_purchase_rate_pct"]),
        float(new_row["session_view_to_purchase_rate_pct"]),
    )
    cart_purchase_pp = pp_change(
        float(old_row["session_cart_to_purchase_rate_pct"]),
        float(new_row["session_cart_to_purchase_rate_pct"]),
    )
    strict_funnel_pp = pp_change(
        float(old_row["strict_session_funnel_completion_rate_pct"]),
        float(new_row["strict_session_funnel_completion_rate_pct"]),
    )

    kpi_table = build_kpi_comparison_table(old_row, new_row)
    funnel_table = build_funnel_comparison_table(old_row, new_row)

    report = f"""# CommercePulse Monthly Growth Summary

## Comparison Window

This report compares **{old_month}** against **{new_month}** using the `mart_monthly_kpis` warehouse table.

---

## Executive Summary

Between **{old_month}** and **{new_month}**:

- Total event volume increased by **{fmt_delta_pct(total_events_change)}**.
- Active users increased by **{fmt_delta_pct(active_users_change)}**.
- Active sessions increased by **{fmt_delta_pct(sessions_change)}**.
- Purchase events increased by **{fmt_delta_pct(purchases_change)}**.
- Purchase revenue increased by **{fmt_delta_pct(revenue_change)}**.
- Average purchase price changed by **{fmt_delta_pct(avg_price_change)}**.

The strongest behavioral shift was in the shopping funnel:

- Session **View → Cart** rate increased by **{fmt_delta_pp(view_cart_pp)}**.
- Session **View → Purchase** rate changed by **{fmt_delta_pp(view_purchase_pp)}**.
- Session **Cart → Purchase** rate changed by **{fmt_delta_pp(cart_purchase_pp)}**.
- Strict **View → Cart → Purchase** funnel completion changed by **{fmt_delta_pp(strict_funnel_pp)}**.

---

## Monthly KPI Comparison

{kpi_table}

---

## Funnel Comparison

{kpi_table if False else funnel_table}

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
"""
    return report


def main() -> int:
    project_root = get_project_root()

    db_path = project_root / "data" / "processed" / "commercepulse.duckdb"
    output_csv_path = (
        project_root / "outputs" / "tables" / "mart_monthly_kpis.csv"
    )
    output_report_path = (
        project_root / "reports" / "monthly_growth_summary.md"
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
        output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        output_report_path.parent.mkdir(parents=True, exist_ok=True)

        con = duckdb.connect(database=str(db_path), read_only=True)

        df = con.execute(
            """
            SELECT *
            FROM mart_monthly_kpis
            ORDER BY event_month;
            """
        ).df()

        con.close()

        if df.empty:
            raise ValueError("mart_monthly_kpis returned no rows.")

        df.to_csv(output_csv_path, index=False)

        markdown_report = build_markdown_report(df)
        output_report_path.write_text(markdown_report, encoding="utf-8")

        console.print(
            f"[bold green]Monthly KPI CSV exported:[/bold green] {output_csv_path}"
        )
        console.print(
            f"[bold green]Monthly growth report generated:[/bold green] {output_report_path}"
        )

        console.print("\n[bold cyan]Rows exported:[/bold cyan]", len(df))
        console.print("[bold cyan]Months covered:[/bold cyan]", ", ".join(df["event_month"].astype(str)))

    except Exception as exc:
        console.print(f"[bold red]Report generation failed:[/bold red] {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())