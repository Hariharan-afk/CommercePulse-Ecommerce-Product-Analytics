from __future__ import annotations

import sys
from pathlib import Path

import duckdb
from rich.console import Console
from rich.table import Table

console = Console()


def get_project_root() -> Path:
    """
    Returns the project root assuming this file lives at:
    src/analytics/export_powerbi_datasets.py
    """
    return Path(__file__).resolve().parents[2]


def export_table_to_csv(
    con: duckdb.DuckDBPyConnection,
    table_name: str,
    output_path: Path,
    order_by: str | None = None,
) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    order_clause = f" ORDER BY {order_by}" if order_by else ""

    df = con.execute(
        f"""
        SELECT *
        FROM {table_name}
        {order_clause};
        """
    ).df()

    df.to_csv(output_path, index=False)
    return len(df)


def build_export_manifest(rows: list[tuple[str, str, int]]) -> None:
    table = Table(title="Power BI Dataset Export Manifest")
    table.add_column("Warehouse Table", style="cyan")
    table.add_column("CSV File", style="magenta")
    table.add_column("Rows Exported", justify="right")

    for table_name, file_name, row_count in rows:
        table.add_row(
            table_name,
            file_name,
            f"{row_count:,}",
        )

    console.print(table)


def write_powerbi_data_dictionary(output_path: Path) -> None:
    content = """# CommercePulse Power BI Data Dictionary

This document describes the CSV files exported for the CommercePulse Power BI dashboard.

---

## 1. `monthly_kpis.csv`

**Source Mart:** `mart_monthly_kpis`

**Purpose:**  
Executive-level monthly platform performance comparison.

**Core fields:**
- `event_month`
- `total_events`
- `active_users`
- `active_sessions`
- `purchase_events`
- `purchase_revenue`
- `avg_purchase_price`
- `session_view_to_cart_rate_pct`
- `session_view_to_purchase_rate_pct`
- `session_cart_to_purchase_rate_pct`
- `strict_session_funnel_completion_rate_pct`

**Primary dashboard use:**
- KPI cards
- Monthly revenue comparison
- Monthly funnel comparison

---

## 2. `monthly_category_performance.csv`

**Source Mart:** `mart_monthly_category_performance`

**Purpose:**  
Category-level monthly performance and funnel metrics.

**Core fields:**
- `event_month`
- `category_l1`
- `purchase_revenue`
- `purchase_events`
- `active_users`
- `cart_events`
- `session_cart_to_purchase_rate_pct`

**Primary dashboard use:**
- Revenue by category
- Cart-to-purchase conversion by category
- Category-level October vs. November comparison

---

## 3. `category_mom_diagnostics.csv`

**Source Mart:** `mart_category_mom_diagnostics`

**Purpose:**  
Month-over-month category growth diagnostics.

**Core fields:**
- `category_l1`
- `oct_purchase_revenue`
- `nov_purchase_revenue`
- `revenue_delta`
- `revenue_growth_pct`
- `cart_to_purchase_rate_change_pp`

**Primary dashboard use:**
- Categories driving revenue growth
- Categories with declining conversion efficiency

---

## 4. `electronics_subcategory_mom_diagnostics.csv`

**Source Mart:** `mart_electronics_subcategory_mom_diagnostics`

**Purpose:**  
Subcategory diagnostics within electronics.

**Core fields:**
- `category_l2`
- `nov_purchase_revenue`
- `nov_electronics_revenue_share_pct`
- `revenue_delta`
- `revenue_growth_pct`
- `cart_to_purchase_rate_change_pp`

**Primary dashboard use:**
- Smartphone dominance in electronics
- Subcategories driving electronics growth
- Electronics subcategory conversion decline

---

## 5. `smartphone_brand_mom_diagnostics.csv`

**Source Mart:** `mart_smartphone_brand_mom_diagnostics`

**Purpose:**  
Brand-level smartphone growth and conversion diagnostics.

**Core fields:**
- `brand`
- `nov_purchase_revenue`
- `nov_smartphone_revenue_share_pct`
- `revenue_delta`
- `net_smartphone_revenue_growth_share_pct`
- `cart_to_purchase_rate_change_pp`

**Primary dashboard use:**
- Apple vs. Samsung growth comparison
- Top smartphone brands by revenue
- Brand-level conversion deterioration

---

## 6. `smartphone_price_band_mom_diagnostics.csv`

**Source Mart:** `mart_smartphone_price_band_mom_diagnostics`

**Purpose:**  
Smartphone growth and funnel behavior by price tier.

**Core fields:**
- `price_band_order`
- `price_band`
- `nov_purchase_revenue`
- `nov_smartphone_revenue_share_pct`
- `revenue_delta`
- `net_smartphone_revenue_growth_share_pct`
- `cart_to_purchase_rate_change_pp`

**Primary dashboard use:**
- Premium vs. mid-range vs. value growth
- Price bands contributing to revenue
- Price bands with declining funnel efficiency

---

## 7. `smartphone_brand_price_band_mom_diagnostics.csv`

**Source Mart:** `mart_smartphone_brand_price_band_mom_diagnostics`

**Purpose:**  
Detailed brand × price-band performance diagnostics.

**Core fields:**
- `brand`
- `price_band_order`
- `price_band`
- `nov_purchase_revenue`
- `revenue_delta`
- `net_smartphone_revenue_growth_share_pct`
- `cart_to_purchase_rate_change_pp`

**Primary dashboard use:**
- Opportunity matrix
- Highest-growth brand-price segments
- Highest-risk conversion-decline segments

---

## Modeling Notes

- Revenue values are based on purchase-event `price` totals.
- Conversion metrics are computed at the session level using ordered funnel logic.
- Growth-share percentages are relative to net growth; positive contributors may sum to more than 100% if other segments decline.
- `unknown` category/brand values represent missing source metadata retained for transparency.
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def write_powerbi_build_guide(output_path: Path) -> None:
    content = """# CommercePulse Power BI Dashboard Build Guide

## Dashboard Objective

Build an executive-friendly product analytics dashboard that explains:

1. What changed from October to November?
2. Which categories drove growth?
3. Why did cart-to-purchase efficiency deteriorate?
4. Which electronics, smartphone, brand, and price-band segments matter most?

---

## Recommended Dashboard Pages

### Page 1 — Executive Overview
**Data source:** `monthly_kpis.csv`

Suggested visuals:
- KPI cards:
  - Total Events
  - Active Users
  - Sessions
  - Purchase Revenue
  - Purchase Events
- Clustered column:
  - October vs. November revenue
- KPI cards or arrows:
  - View → Cart
  - View → Purchase
  - Cart → Purchase
- Text callout:
  - “November revenue grew, but cart-to-purchase efficiency declined.”

---

### Page 2 — Category Growth Diagnostics
**Data sources:**
- `monthly_category_performance.csv`
- `category_mom_diagnostics.csv`

Suggested visuals:
- Bar chart:
  - Revenue delta by category
- Bar chart:
  - Cart-to-purchase rate change by category
- Scatter plot:
  - X = revenue delta
  - Y = cart-to-purchase rate change
  - Size = November revenue
- Highlight electronics as both:
  - top growth driver
  - largest major conversion decline

---

### Page 3 — Electronics Subcategory Drill-Down
**Data source:** `electronics_subcategory_mom_diagnostics.csv`

Suggested visuals:
- Treemap or bar chart:
  - November electronics revenue by subcategory
- Bar chart:
  - Revenue delta by electronics subcategory
- Bar chart:
  - Cart-to-purchase decline by subcategory
- Callout:
  - Smartphones generated the overwhelming share of electronics revenue.

---

### Page 4 — Smartphone Brand Diagnostics
**Data source:** `smartphone_brand_mom_diagnostics.csv`

Suggested visuals:
- Revenue share bar chart:
  - Apple, Samsung, Xiaomi, etc.
- Growth contribution bar chart:
  - Revenue delta by brand
- Decline chart:
  - Cart-to-purchase rate change by brand
- Highlight:
  - Apple and Samsung dominate smartphone growth.

---

### Page 5 — Smartphone Price-Band Diagnostics
**Data source:** `smartphone_price_band_mom_diagnostics.csv`

Suggested visuals:
- Revenue by price band
- Revenue delta by price band
- Cart-to-purchase conversion change by price band
- Key insight callout:
  - Premium bands drove the largest share of revenue growth.

---

### Page 6 — Brand × Price-Band Opportunity Matrix
**Data source:** `smartphone_brand_price_band_mom_diagnostics.csv`

Suggested visuals:
- Scatter plot:
  - X = revenue delta
  - Y = cart-to-purchase rate change
  - Size = November revenue
  - Detail = brand + price band
- Matrix table:
  - Brand rows
  - Price-band columns
  - Values = revenue delta or conversion change
- Highlight:
  - Apple `$800-$1199`
  - Apple `$1200+`
  - Samsung `$100-$249`
  - Samsung `$250-$499`

---

## Recommended Slicers

- Category
- Subcategory
- Brand
- Price Band

Use slicers selectively; do not overload every page.

---

## Visual Storyline

The dashboard should guide the reader through this sequence:

1. November grew materially in traffic and revenue.
2. Funnel quality weakened after carting.
3. Electronics drove most growth and much of the conversion deterioration.
4. Smartphones explain most electronics growth.
5. Apple and Samsung dominate smartphone expansion.
6. Premium Apple and selected Samsung segments explain the most actionable commercial shifts.

---

## Design Guidance

- Use a clean executive/business style.
- Prefer:
  - KPI cards
  - horizontal bars
  - scatter plots
  - matrix tables
- Avoid overly decorative visuals.
- Keep every page to one main question.
- Add short text annotations explaining the “so what.”
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def main() -> int:
    project_root = get_project_root()

    db_path = project_root / "data" / "processed" / "commercepulse.duckdb"
    dashboards_data_dir = project_root / "dashboards" / "data"
    dashboards_docs_dir = project_root / "dashboards" / "docs"

    data_dictionary_path = dashboards_docs_dir / "powerbi_data_dictionary.md"
    build_guide_path = dashboards_docs_dir / "powerbi_dashboard_build_guide.md"

    console.print(f"[bold cyan]Project root:[/bold cyan] {project_root}")
    console.print(f"[bold cyan]DuckDB warehouse:[/bold cyan] {db_path}")
    console.print(f"[bold cyan]Power BI data export directory:[/bold cyan] {dashboards_data_dir}")

    if not db_path.exists():
        console.print(
            "[bold red]DuckDB warehouse not found. "
            "Run build_warehouse.py first.[/bold red]"
        )
        return 1

    export_specs = [
        (
            "mart_monthly_kpis",
            dashboards_data_dir / "monthly_kpis.csv",
            "event_month",
        ),
        (
            "mart_monthly_category_performance",
            dashboards_data_dir / "monthly_category_performance.csv",
            "event_month, purchase_revenue DESC",
        ),
        (
            "mart_category_mom_diagnostics",
            dashboards_data_dir / "category_mom_diagnostics.csv",
            "revenue_delta DESC",
        ),
        (
            "mart_electronics_subcategory_mom_diagnostics",
            dashboards_data_dir / "electronics_subcategory_mom_diagnostics.csv",
            "revenue_delta DESC",
        ),
        (
            "mart_smartphone_brand_mom_diagnostics",
            dashboards_data_dir / "smartphone_brand_mom_diagnostics.csv",
            "revenue_delta DESC",
        ),
        (
            "mart_smartphone_price_band_mom_diagnostics",
            dashboards_data_dir / "smartphone_price_band_mom_diagnostics.csv",
            "price_band_order",
        ),
        (
            "mart_smartphone_brand_price_band_mom_diagnostics",
            dashboards_data_dir / "smartphone_brand_price_band_mom_diagnostics.csv",
            "revenue_delta DESC",
        ),
    ]

    exported_rows: list[tuple[str, str, int]] = []

    try:
        con = duckdb.connect(database=str(db_path), read_only=True)

        for table_name, output_path, order_by in export_specs:
            row_count = export_table_to_csv(
                con=con,
                table_name=table_name,
                output_path=output_path,
                order_by=order_by,
            )

            exported_rows.append(
                (
                    table_name,
                    output_path.name,
                    row_count,
                )
            )

        con.close()

        write_powerbi_data_dictionary(data_dictionary_path)
        write_powerbi_build_guide(build_guide_path)

        build_export_manifest(exported_rows)

        console.print(
            f"\n[bold green]Power BI data dictionary generated:[/bold green] {data_dictionary_path}"
        )
        console.print(
            f"[bold green]Power BI dashboard build guide generated:[/bold green] {build_guide_path}"
        )
        console.print(
            "\n[bold green]Power BI dashboard export package completed successfully.[/bold green]"
        )

    except Exception as exc:
        console.print(
            f"[bold red]Power BI dataset export failed:[/bold red] {exc}"
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())