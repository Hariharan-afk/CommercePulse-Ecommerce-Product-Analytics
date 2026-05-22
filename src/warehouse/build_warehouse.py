from __future__ import annotations

import argparse
import sys
from pathlib import Path

import duckdb
from rich.console import Console
from rich.table import Table

console = Console()


def get_project_root() -> Path:
    """
    Returns the project root assuming this file lives at:
    src/warehouse/build_warehouse.py
    """
    return Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the CommercePulse DuckDB analytics warehouse."
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Delete and rebuild the DuckDB warehouse database.",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=4,
        help="DuckDB threads to use. Default: 4.",
    )
    parser.add_argument(
        "--memory-limit",
        type=str,
        default="8GB",
        help="DuckDB memory limit. Default: 8GB.",
    )
    return parser.parse_args()


def read_sql_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"SQL file not found: {path}")

    return path.read_text(encoding="utf-8")


def render_staging_sql(sql_text: str, parquet_glob: str) -> str:
    escaped_glob = parquet_glob.replace("'", "''")
    return sql_text.replace("__EVENTS_PARQUET_GLOB__", escaped_glob)


def prepare_database_path(db_path: Path, overwrite: bool) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if db_path.exists() and overwrite:
        console.print(f"[yellow]Removing existing DuckDB database:[/yellow] {db_path}")
        db_path.unlink()


def create_monthly_kpis_preview(con: duckdb.DuckDBPyConnection) -> None:
    rows = con.execute(
        """
        SELECT
            event_month,
            total_events,
            active_users,
            active_sessions,
            purchase_events,
            purchase_revenue,
            session_view_to_cart_rate_pct,
            session_view_to_purchase_rate_pct,
            session_cart_to_purchase_rate_pct,
            strict_session_funnel_completion_rate_pct
        FROM mart_monthly_kpis
        ORDER BY event_month;
        """
    ).fetchall()

    table = Table(title="CommercePulse Monthly KPI Mart Preview")

    table.add_column("Month", style="cyan")
    table.add_column("Total Events", justify="right")
    table.add_column("Active Users", justify="right")
    table.add_column("Sessions", justify="right")
    table.add_column("Purchases", justify="right")
    table.add_column("Revenue", justify="right")
    table.add_column("View→Cart %", justify="right")
    table.add_column("View→Purchase %", justify="right")
    table.add_column("Cart→Purchase %", justify="right")
    table.add_column("Strict Funnel %", justify="right")

    for row in rows:
        (
            event_month,
            total_events,
            active_users,
            active_sessions,
            purchase_events,
            purchase_revenue,
            view_to_cart_pct,
            view_to_purchase_pct,
            cart_to_purchase_pct,
            strict_funnel_pct,
        ) = row

        table.add_row(
            str(event_month),
            f"{total_events:,}",
            f"{active_users:,}",
            f"{active_sessions:,}",
            f"{purchase_events:,}",
            f"${purchase_revenue:,.2f}",
            f"{view_to_cart_pct:.2f}%",
            f"{view_to_purchase_pct:.2f}%",
            f"{cart_to_purchase_pct:.2f}%",
            f"{strict_funnel_pct:.2f}%",
        )

    console.print(table)


def print_warehouse_objects(con: duckdb.DuckDBPyConnection) -> None:
    rows = con.execute(
        """
        SELECT
            table_name,
            table_type
        FROM information_schema.tables
        WHERE table_schema = 'main'
        ORDER BY table_type, table_name;
        """
    ).fetchall()

    table = Table(title="Warehouse Objects Created")
    table.add_column("Object Name", style="cyan")
    table.add_column("Object Type", style="green")

    for table_name, table_type in rows:
        table.add_row(str(table_name), str(table_type))

    console.print(table)

def create_category_diagnostics_preview(
    con: duckdb.DuckDBPyConnection,
) -> None:
    console.print("\n[bold cyan]Top Categories by November Purchase Revenue[/bold cyan]")

    top_revenue_rows = con.execute(
        """
        SELECT
            category_l1,
            nov_purchase_revenue,
            revenue_delta,
            revenue_growth_pct,
            nov_cart_to_purchase_rate_pct,
            cart_to_purchase_rate_change_pp
        FROM mart_category_mom_diagnostics
        ORDER BY nov_purchase_revenue DESC
        LIMIT 10;
        """
    ).fetchall()

    revenue_table = Table(title="Top November Revenue Categories")
    revenue_table.add_column("Category", style="cyan")
    revenue_table.add_column("Nov Revenue", justify="right")
    revenue_table.add_column("Revenue Delta", justify="right")
    revenue_table.add_column("Revenue Growth %", justify="right")
    revenue_table.add_column("Nov Cart→Purchase %", justify="right")
    revenue_table.add_column("Cart→Purchase Δ pp", justify="right")

    for row in top_revenue_rows:
        (
            category_l1,
            nov_purchase_revenue,
            revenue_delta,
            revenue_growth_pct,
            nov_cart_to_purchase_rate_pct,
            cart_to_purchase_rate_change_pp,
        ) = row

        revenue_table.add_row(
            str(category_l1),
            f"${nov_purchase_revenue:,.2f}",
            f"${revenue_delta:,.2f}",
            "N/A" if revenue_growth_pct is None else f"{revenue_growth_pct:.2f}%",
            (
                "N/A"
                if nov_cart_to_purchase_rate_pct is None
                else f"{nov_cart_to_purchase_rate_pct:.2f}%"
            ),
            (
                "N/A"
                if cart_to_purchase_rate_change_pp is None
                else f"{cart_to_purchase_rate_change_pp:.2f} pp"
            ),
        )

    console.print(revenue_table)

    console.print(
        "\n[bold cyan]Categories with Largest Cart→Purchase Rate Declines[/bold cyan]"
    )

    decline_rows = con.execute(
        """
        SELECT
            category_l1,
            oct_cart_to_purchase_rate_pct,
            nov_cart_to_purchase_rate_pct,
            cart_to_purchase_rate_change_pp,
            nov_purchase_revenue
        FROM mart_category_mom_diagnostics
        WHERE
            cart_to_purchase_rate_change_pp IS NOT NULL
            AND oct_cart_events >= 1000
            AND nov_cart_events >= 1000
        ORDER BY cart_to_purchase_rate_change_pp ASC
        LIMIT 10;
        """
    ).fetchall()

    decline_table = Table(title="Largest Cart→Purchase Efficiency Declines")
    decline_table.add_column("Category", style="cyan")
    decline_table.add_column("Oct Cart→Purchase %", justify="right")
    decline_table.add_column("Nov Cart→Purchase %", justify="right")
    decline_table.add_column("Change", justify="right")
    decline_table.add_column("Nov Revenue", justify="right")

    for row in decline_rows:
        (
            category_l1,
            oct_rate,
            nov_rate,
            rate_change,
            nov_revenue,
        ) = row

        decline_table.add_row(
            str(category_l1),
            f"{oct_rate:.2f}%",
            f"{nov_rate:.2f}%",
            f"{rate_change:.2f} pp",
            f"${nov_revenue:,.2f}",
        )

    console.print(decline_table)

def create_electronics_subcategory_preview(
    con: duckdb.DuckDBPyConnection,
) -> None:
    console.print(
        "\n[bold cyan]Top Electronics Subcategories by November Revenue[/bold cyan]"
    )

    revenue_rows = con.execute(
        """
        SELECT
            category_l2,
            nov_purchase_revenue,
            nov_electronics_revenue_share_pct,
            revenue_delta,
            revenue_growth_pct,
            nov_cart_to_purchase_rate_pct,
            cart_to_purchase_rate_change_pp
        FROM mart_electronics_subcategory_mom_diagnostics
        ORDER BY nov_purchase_revenue DESC
        LIMIT 12;
        """
    ).fetchall()

    revenue_table = Table(title="Electronics Subcategories — November Revenue Leaders")
    revenue_table.add_column("Subcategory", style="cyan")
    revenue_table.add_column("Nov Revenue", justify="right")
    revenue_table.add_column("Revenue Share", justify="right")
    revenue_table.add_column("Revenue Delta", justify="right")
    revenue_table.add_column("Revenue Growth %", justify="right")
    revenue_table.add_column("Nov Cart→Purchase %", justify="right")
    revenue_table.add_column("Cart→Purchase Δ pp", justify="right")

    for row in revenue_rows:
        (
            category_l2,
            nov_revenue,
            revenue_share,
            revenue_delta,
            revenue_growth,
            nov_cart_purchase,
            cart_purchase_delta,
        ) = row

        revenue_table.add_row(
            str(category_l2),
            f"${nov_revenue:,.2f}",
            "N/A" if revenue_share is None else f"{revenue_share:.2f}%",
            f"${revenue_delta:,.2f}",
            "N/A" if revenue_growth is None else f"{revenue_growth:.2f}%",
            (
                "N/A"
                if nov_cart_purchase is None
                else f"{nov_cart_purchase:.2f}%"
            ),
            (
                "N/A"
                if cart_purchase_delta is None
                else f"{cart_purchase_delta:.2f} pp"
            ),
        )

    console.print(revenue_table)

    console.print(
        "\n[bold cyan]Electronics Subcategories Driving Revenue Growth[/bold cyan]"
    )

    growth_rows = con.execute(
        """
        SELECT
            category_l2,
            revenue_delta,
            revenue_growth_pct,
            nov_purchase_revenue,
            cart_to_purchase_rate_change_pp
        FROM mart_electronics_subcategory_mom_diagnostics
        ORDER BY revenue_delta DESC
        LIMIT 12;
        """
    ).fetchall()

    growth_table = Table(title="Electronics Revenue Growth Contributors")
    growth_table.add_column("Subcategory", style="cyan")
    growth_table.add_column("Revenue Delta", justify="right")
    growth_table.add_column("Revenue Growth %", justify="right")
    growth_table.add_column("Nov Revenue", justify="right")
    growth_table.add_column("Cart→Purchase Δ pp", justify="right")

    for row in growth_rows:
        (
            category_l2,
            revenue_delta,
            revenue_growth,
            nov_revenue,
            cart_purchase_delta,
        ) = row

        growth_table.add_row(
            str(category_l2),
            f"${revenue_delta:,.2f}",
            "N/A" if revenue_growth is None else f"{revenue_growth:.2f}%",
            f"${nov_revenue:,.2f}",
            (
                "N/A"
                if cart_purchase_delta is None
                else f"{cart_purchase_delta:.2f} pp"
            ),
        )

    console.print(growth_table)

    console.print(
        "\n[bold cyan]Electronics Subcategories with Largest Cart→Purchase Declines[/bold cyan]"
    )

    decline_rows = con.execute(
        """
        SELECT
            category_l2,
            oct_cart_to_purchase_rate_pct,
            nov_cart_to_purchase_rate_pct,
            cart_to_purchase_rate_change_pp,
            nov_purchase_revenue
        FROM mart_electronics_subcategory_mom_diagnostics
        WHERE
            cart_to_purchase_rate_change_pp IS NOT NULL
            AND oct_cart_events >= 1000
            AND nov_cart_events >= 1000
        ORDER BY cart_to_purchase_rate_change_pp ASC
        LIMIT 12;
        """
    ).fetchall()

    decline_table = Table(
        title="Electronics Subcategories — Largest Cart→Purchase Efficiency Declines"
    )
    decline_table.add_column("Subcategory", style="cyan")
    decline_table.add_column("Oct Cart→Purchase %", justify="right")
    decline_table.add_column("Nov Cart→Purchase %", justify="right")
    decline_table.add_column("Change", justify="right")
    decline_table.add_column("Nov Revenue", justify="right")

    for row in decline_rows:
        (
            category_l2,
            oct_rate,
            nov_rate,
            rate_change,
            nov_revenue,
        ) = row

        decline_table.add_row(
            str(category_l2),
            f"{oct_rate:.2f}%",
            f"{nov_rate:.2f}%",
            f"{rate_change:.2f} pp",
            f"${nov_revenue:,.2f}",
        )

    console.print(decline_table)

def create_smartphone_brand_preview(
    con: duckdb.DuckDBPyConnection,
) -> None:
    console.print(
        "\n[bold cyan]Top Smartphone Brands by November Revenue[/bold cyan]"
    )

    top_revenue_rows = con.execute(
        """
        SELECT
            brand,
            nov_purchase_revenue,
            nov_smartphone_revenue_share_pct,
            revenue_delta,
            revenue_growth_pct,
            nov_cart_to_purchase_rate_pct,
            cart_to_purchase_rate_change_pp
        FROM mart_smartphone_brand_mom_diagnostics
        ORDER BY nov_purchase_revenue DESC
        LIMIT 12;
        """
    ).fetchall()

    revenue_table = Table(title="Smartphone Brands — November Revenue Leaders")
    revenue_table.add_column("Brand", style="cyan")
    revenue_table.add_column("Nov Revenue", justify="right")
    revenue_table.add_column("Revenue Share", justify="right")
    revenue_table.add_column("Revenue Delta", justify="right")
    revenue_table.add_column("Revenue Growth %", justify="right")
    revenue_table.add_column("Nov Cart→Purchase %", justify="right")
    revenue_table.add_column("Cart→Purchase Δ pp", justify="right")

    for row in top_revenue_rows:
        (
            brand,
            nov_revenue,
            revenue_share,
            revenue_delta,
            revenue_growth,
            nov_cart_purchase,
            cart_purchase_delta,
        ) = row

        revenue_table.add_row(
            str(brand),
            f"${nov_revenue:,.2f}",
            "N/A" if revenue_share is None else f"{revenue_share:.2f}%",
            f"${revenue_delta:,.2f}",
            "N/A" if revenue_growth is None else f"{revenue_growth:.2f}%",
            (
                "N/A"
                if nov_cart_purchase is None
                else f"{nov_cart_purchase:.2f}%"
            ),
            (
                "N/A"
                if cart_purchase_delta is None
                else f"{cart_purchase_delta:.2f} pp"
            ),
        )

    console.print(revenue_table)

    console.print(
        "\n[bold cyan]Smartphone Brands Driving Net Revenue Growth[/bold cyan]"
    )

    growth_rows = con.execute(
        """
        SELECT
            brand,
            revenue_delta,
            net_smartphone_revenue_growth_share_pct,
            revenue_growth_pct,
            nov_purchase_revenue,
            cart_to_purchase_rate_change_pp
        FROM mart_smartphone_brand_mom_diagnostics
        ORDER BY revenue_delta DESC
        LIMIT 12;
        """
    ).fetchall()

    growth_table = Table(title="Smartphone Revenue Growth Contributors")
    growth_table.add_column("Brand", style="cyan")
    growth_table.add_column("Revenue Delta", justify="right")
    growth_table.add_column("Growth Share", justify="right")
    growth_table.add_column("Revenue Growth %", justify="right")
    growth_table.add_column("Nov Revenue", justify="right")
    growth_table.add_column("Cart→Purchase Δ pp", justify="right")

    for row in growth_rows:
        (
            brand,
            revenue_delta,
            growth_share,
            revenue_growth,
            nov_revenue,
            cart_purchase_delta,
        ) = row

        growth_table.add_row(
            str(brand),
            f"${revenue_delta:,.2f}",
            "N/A" if growth_share is None else f"{growth_share:.2f}%",
            "N/A" if revenue_growth is None else f"{revenue_growth:.2f}%",
            f"${nov_revenue:,.2f}",
            (
                "N/A"
                if cart_purchase_delta is None
                else f"{cart_purchase_delta:.2f} pp"
            ),
        )

    console.print(growth_table)

    console.print(
        "\n[bold cyan]Smartphone Brands with Largest Cart→Purchase Declines[/bold cyan]"
    )

    decline_rows = con.execute(
        """
        SELECT
            brand,
            oct_cart_to_purchase_rate_pct,
            nov_cart_to_purchase_rate_pct,
            cart_to_purchase_rate_change_pp,
            nov_purchase_revenue
        FROM mart_smartphone_brand_mom_diagnostics
        WHERE
            cart_to_purchase_rate_change_pp IS NOT NULL
            AND oct_cart_events >= 1000
            AND nov_cart_events >= 1000
        ORDER BY cart_to_purchase_rate_change_pp ASC
        LIMIT 12;
        """
    ).fetchall()

    decline_table = Table(
        title="Smartphone Brands — Largest Cart→Purchase Efficiency Declines"
    )
    decline_table.add_column("Brand", style="cyan")
    decline_table.add_column("Oct Cart→Purchase %", justify="right")
    decline_table.add_column("Nov Cart→Purchase %", justify="right")
    decline_table.add_column("Change", justify="right")
    decline_table.add_column("Nov Revenue", justify="right")

    for row in decline_rows:
        (
            brand,
            oct_rate,
            nov_rate,
            rate_change,
            nov_revenue,
        ) = row

        decline_table.add_row(
            str(brand),
            f"{oct_rate:.2f}%",
            f"{nov_rate:.2f}%",
            f"{rate_change:.2f} pp",
            f"${nov_revenue:,.2f}",
        )

    console.print(decline_table)

def create_smartphone_price_band_preview(
    con: duckdb.DuckDBPyConnection,
) -> None:
    console.print(
        "\n[bold cyan]Smartphone Price Bands by November Revenue[/bold cyan]"
    )

    revenue_rows = con.execute(
        """
        SELECT
            price_band,
            nov_purchase_revenue,
            nov_smartphone_revenue_share_pct,
            revenue_delta,
            revenue_growth_pct,
            nov_cart_to_purchase_rate_pct,
            cart_to_purchase_rate_change_pp
        FROM mart_smartphone_price_band_mom_diagnostics
        ORDER BY nov_purchase_revenue DESC;
        """
    ).fetchall()

    revenue_table = Table(title="Smartphone Price Bands — November Revenue")
    revenue_table.add_column("Price Band", style="cyan")
    revenue_table.add_column("Nov Revenue", justify="right")
    revenue_table.add_column("Revenue Share", justify="right")
    revenue_table.add_column("Revenue Delta", justify="right")
    revenue_table.add_column("Revenue Growth %", justify="right")
    revenue_table.add_column("Nov Cart→Purchase %", justify="right")
    revenue_table.add_column("Cart→Purchase Δ pp", justify="right")

    for row in revenue_rows:
        (
            price_band,
            nov_revenue,
            revenue_share,
            revenue_delta,
            revenue_growth,
            nov_cart_purchase,
            cart_purchase_delta,
        ) = row

        revenue_table.add_row(
            str(price_band),
            f"${nov_revenue:,.2f}",
            "N/A" if revenue_share is None else f"{revenue_share:.2f}%",
            f"${revenue_delta:,.2f}",
            "N/A" if revenue_growth is None else f"{revenue_growth:.2f}%",
            (
                "N/A"
                if nov_cart_purchase is None
                else f"{nov_cart_purchase:.2f}%"
            ),
            (
                "N/A"
                if cart_purchase_delta is None
                else f"{cart_purchase_delta:.2f} pp"
            ),
        )

    console.print(revenue_table)

    console.print(
        "\n[bold cyan]Smartphone Price Bands Driving Net Revenue Growth[/bold cyan]"
    )

    growth_rows = con.execute(
        """
        SELECT
            price_band,
            revenue_delta,
            net_smartphone_revenue_growth_share_pct,
            revenue_growth_pct,
            nov_purchase_revenue,
            cart_to_purchase_rate_change_pp
        FROM mart_smartphone_price_band_mom_diagnostics
        ORDER BY revenue_delta DESC;
        """
    ).fetchall()

    growth_table = Table(title="Smartphone Price Bands — Growth Contributors")
    growth_table.add_column("Price Band", style="cyan")
    growth_table.add_column("Revenue Delta", justify="right")
    growth_table.add_column("Growth Share", justify="right")
    growth_table.add_column("Revenue Growth %", justify="right")
    growth_table.add_column("Nov Revenue", justify="right")
    growth_table.add_column("Cart→Purchase Δ pp", justify="right")

    for row in growth_rows:
        (
            price_band,
            revenue_delta,
            growth_share,
            revenue_growth,
            nov_revenue,
            cart_purchase_delta,
        ) = row

        growth_table.add_row(
            str(price_band),
            f"${revenue_delta:,.2f}",
            "N/A" if growth_share is None else f"{growth_share:.2f}%",
            "N/A" if revenue_growth is None else f"{revenue_growth:.2f}%",
            f"${nov_revenue:,.2f}",
            (
                "N/A"
                if cart_purchase_delta is None
                else f"{cart_purchase_delta:.2f} pp"
            ),
        )

    console.print(growth_table)

    console.print(
        "\n[bold cyan]Smartphone Price Bands with Cart→Purchase Changes[/bold cyan]"
    )

    decline_rows = con.execute(
        """
        SELECT
            price_band,
            oct_cart_to_purchase_rate_pct,
            nov_cart_to_purchase_rate_pct,
            cart_to_purchase_rate_change_pp,
            nov_purchase_revenue
        FROM mart_smartphone_price_band_mom_diagnostics
        WHERE cart_to_purchase_rate_change_pp IS NOT NULL
        ORDER BY cart_to_purchase_rate_change_pp ASC;
        """
    ).fetchall()

    decline_table = Table(title="Smartphone Price Bands — Conversion Change")
    decline_table.add_column("Price Band", style="cyan")
    decline_table.add_column("Oct Cart→Purchase %", justify="right")
    decline_table.add_column("Nov Cart→Purchase %", justify="right")
    decline_table.add_column("Change", justify="right")
    decline_table.add_column("Nov Revenue", justify="right")

    for row in decline_rows:
        (
            price_band,
            oct_rate,
            nov_rate,
            rate_change,
            nov_revenue,
        ) = row

        decline_table.add_row(
            str(price_band),
            f"{oct_rate:.2f}%",
            f"{nov_rate:.2f}%",
            f"{rate_change:.2f} pp",
            f"${nov_revenue:,.2f}",
        )

    console.print(decline_table)

def create_smartphone_brand_price_band_preview(
    con: duckdb.DuckDBPyConnection,
) -> None:
    console.print(
        "\n[bold cyan]Top Smartphone Brand × Price-Band Segments by November Revenue[/bold cyan]"
    )

    revenue_rows = con.execute(
        """
        SELECT
            brand,
            price_band,
            nov_purchase_revenue,
            nov_smartphone_revenue_share_pct,
            revenue_delta,
            revenue_growth_pct,
            nov_cart_to_purchase_rate_pct,
            cart_to_purchase_rate_change_pp
        FROM mart_smartphone_brand_price_band_mom_diagnostics
        ORDER BY nov_purchase_revenue DESC
        LIMIT 15;
        """
    ).fetchall()

    revenue_table = Table(
        title="Smartphone Brand × Price Band — November Revenue Leaders"
    )
    revenue_table.add_column("Brand", style="cyan")
    revenue_table.add_column("Price Band", style="magenta")
    revenue_table.add_column("Nov Revenue", justify="right")
    revenue_table.add_column("Revenue Share", justify="right")
    revenue_table.add_column("Revenue Delta", justify="right")
    revenue_table.add_column("Revenue Growth %", justify="right")
    revenue_table.add_column("Nov Cart→Purchase %", justify="right")
    revenue_table.add_column("Cart→Purchase Δ pp", justify="right")

    for row in revenue_rows:
        (
            brand,
            price_band,
            nov_revenue,
            revenue_share,
            revenue_delta,
            revenue_growth,
            nov_cart_purchase,
            cart_purchase_delta,
        ) = row

        revenue_table.add_row(
            str(brand),
            str(price_band),
            f"${nov_revenue:,.2f}",
            "N/A" if revenue_share is None else f"{revenue_share:.2f}%",
            f"${revenue_delta:,.2f}",
            "N/A" if revenue_growth is None else f"{revenue_growth:.2f}%",
            (
                "N/A"
                if nov_cart_purchase is None
                else f"{nov_cart_purchase:.2f}%"
            ),
            (
                "N/A"
                if cart_purchase_delta is None
                else f"{cart_purchase_delta:.2f} pp"
            ),
        )

    console.print(revenue_table)

    console.print(
        "\n[bold cyan]Brand × Price-Band Segments Driving Net Smartphone Revenue Growth[/bold cyan]"
    )

    growth_rows = con.execute(
        """
        SELECT
            brand,
            price_band,
            revenue_delta,
            net_smartphone_revenue_growth_share_pct,
            revenue_growth_pct,
            nov_purchase_revenue,
            cart_to_purchase_rate_change_pp
        FROM mart_smartphone_brand_price_band_mom_diagnostics
        ORDER BY revenue_delta DESC
        LIMIT 15;
        """
    ).fetchall()

    growth_table = Table(
        title="Smartphone Brand × Price Band — Revenue Growth Contributors"
    )
    growth_table.add_column("Brand", style="cyan")
    growth_table.add_column("Price Band", style="magenta")
    growth_table.add_column("Revenue Delta", justify="right")
    growth_table.add_column("Growth Share", justify="right")
    growth_table.add_column("Revenue Growth %", justify="right")
    growth_table.add_column("Nov Revenue", justify="right")
    growth_table.add_column("Cart→Purchase Δ pp", justify="right")

    for row in growth_rows:
        (
            brand,
            price_band,
            revenue_delta,
            growth_share,
            revenue_growth,
            nov_revenue,
            cart_purchase_delta,
        ) = row

        growth_table.add_row(
            str(brand),
            str(price_band),
            f"${revenue_delta:,.2f}",
            "N/A" if growth_share is None else f"{growth_share:.2f}%",
            "N/A" if revenue_growth is None else f"{revenue_growth:.2f}%",
            f"${nov_revenue:,.2f}",
            (
                "N/A"
                if cart_purchase_delta is None
                else f"{cart_purchase_delta:.2f} pp"
            ),
        )

    console.print(growth_table)

    console.print(
        "\n[bold cyan]Brand × Price-Band Segments with Largest Cart→Purchase Declines[/bold cyan]"
    )

    decline_rows = con.execute(
        """
        SELECT
            brand,
            price_band,
            oct_cart_to_purchase_rate_pct,
            nov_cart_to_purchase_rate_pct,
            cart_to_purchase_rate_change_pp,
            nov_purchase_revenue
        FROM mart_smartphone_brand_price_band_mom_diagnostics
        WHERE
            cart_to_purchase_rate_change_pp IS NOT NULL
            AND oct_cart_events >= 1000
            AND nov_cart_events >= 1000
        ORDER BY cart_to_purchase_rate_change_pp ASC
        LIMIT 15;
        """
    ).fetchall()

    decline_table = Table(
        title="Smartphone Brand × Price Band — Largest Cart→Purchase Efficiency Declines"
    )
    decline_table.add_column("Brand", style="cyan")
    decline_table.add_column("Price Band", style="magenta")
    decline_table.add_column("Oct Cart→Purchase %", justify="right")
    decline_table.add_column("Nov Cart→Purchase %", justify="right")
    decline_table.add_column("Change", justify="right")
    decline_table.add_column("Nov Revenue", justify="right")

    for row in decline_rows:
        (
            brand,
            price_band,
            oct_rate,
            nov_rate,
            rate_change,
            nov_revenue,
        ) = row

        decline_table.add_row(
            str(brand),
            str(price_band),
            f"{oct_rate:.2f}%",
            f"{nov_rate:.2f}%",
            f"{rate_change:.2f} pp",
            f"${nov_revenue:,.2f}",
        )

    console.print(decline_table)

def main() -> int:
    args = parse_args()

    project_root = get_project_root()

    clean_events_dir = project_root / "data" / "interim" / "events_clean"
    parquet_glob = (clean_events_dir / "**" / "*.parquet").as_posix()

    db_path = project_root / "data" / "processed" / "commercepulse.duckdb"

    staging_sql_path = project_root / "sql" / "staging" / "stg_events.sql"
    monthly_kpis_sql_path = (
        project_root / "sql" / "marts" / "mart_monthly_kpis.sql"
    )

    monthly_category_performance_sql_path = (
        project_root / "sql" / "marts" / "mart_monthly_category_performance.sql"
    )

    category_mom_diagnostics_sql_path = (
        project_root / "sql" / "marts" / "mart_category_mom_diagnostics.sql"
    )

    monthly_subcategory_performance_sql_path = (
        project_root / "sql" / "marts" / "mart_monthly_subcategory_performance.sql"
    )

    electronics_subcategory_mom_diagnostics_sql_path = (
        project_root
        / "sql"
        / "marts"
        / "mart_electronics_subcategory_mom_diagnostics.sql"
    )

    monthly_smartphone_brand_performance_sql_path = (
        project_root
        / "sql"
        / "marts"
        / "mart_monthly_smartphone_brand_performance.sql"
    )

    smartphone_brand_mom_diagnostics_sql_path = (
        project_root
        / "sql"
        / "marts"
        / "mart_smartphone_brand_mom_diagnostics.sql"
    )

    monthly_smartphone_price_band_performance_sql_path = (
        project_root
        / "sql"
        / "marts"
        / "mart_monthly_smartphone_price_band_performance.sql"
    )

    smartphone_price_band_mom_diagnostics_sql_path = (
        project_root
        / "sql"
        / "marts"
        / "mart_smartphone_price_band_mom_diagnostics.sql"
    )

    monthly_smartphone_brand_price_band_performance_sql_path = (
        project_root
        / "sql"
        / "marts"
        / "mart_monthly_smartphone_brand_price_band_performance.sql"
    )

    smartphone_brand_price_band_mom_diagnostics_sql_path = (
        project_root
        / "sql"
        / "marts"
        / "mart_smartphone_brand_price_band_mom_diagnostics.sql"
    )

    console.print(f"[bold cyan]Project root:[/bold cyan] {project_root}")
    console.print(f"[bold cyan]Clean event parquet glob:[/bold cyan] {parquet_glob}")
    console.print(f"[bold cyan]DuckDB warehouse:[/bold cyan] {db_path}")

    if not clean_events_dir.exists():
        console.print(
            "[bold red]Clean event dataset not found. "
            "Run prepare_events.py first.[/bold red]"
        )
        return 1

    try:
        prepare_database_path(db_path, overwrite=args.overwrite)

        staging_sql_template = read_sql_file(staging_sql_path)
        staging_sql = render_staging_sql(
            staging_sql_template,
            parquet_glob=parquet_glob,
        )

        monthly_kpis_sql = read_sql_file(monthly_kpis_sql_path)

        monthly_category_performance_sql = read_sql_file(
            monthly_category_performance_sql_path
        )

        category_mom_diagnostics_sql = read_sql_file(
            category_mom_diagnostics_sql_path
        )

        monthly_subcategory_performance_sql = read_sql_file(
            monthly_subcategory_performance_sql_path
        )

        electronics_subcategory_mom_diagnostics_sql = read_sql_file(
            electronics_subcategory_mom_diagnostics_sql_path
        )

        monthly_smartphone_brand_performance_sql = read_sql_file(
            monthly_smartphone_brand_performance_sql_path
        )

        smartphone_brand_mom_diagnostics_sql = read_sql_file(
            smartphone_brand_mom_diagnostics_sql_path
        )

        monthly_smartphone_price_band_performance_sql = read_sql_file(
            monthly_smartphone_price_band_performance_sql_path
        )

        smartphone_price_band_mom_diagnostics_sql = read_sql_file(
            smartphone_price_band_mom_diagnostics_sql_path
        )

        monthly_smartphone_brand_price_band_performance_sql = read_sql_file(
            monthly_smartphone_brand_price_band_performance_sql_path
        )

        smartphone_brand_price_band_mom_diagnostics_sql = read_sql_file(
            smartphone_brand_price_band_mom_diagnostics_sql_path
        )

        con = duckdb.connect(database=str(db_path))
        con.execute(f"PRAGMA threads={args.threads};")
        con.execute(f"PRAGMA memory_limit='{args.memory_limit}';")
        con.execute("PRAGMA enable_progress_bar=true;")

        console.print("\n[bold cyan]Creating staging view: stg_events[/bold cyan]")
        con.execute(staging_sql)

        console.print("[bold cyan]Building mart: mart_monthly_kpis[/bold cyan]")
        con.execute(monthly_kpis_sql)

        console.print(
            "[bold cyan]Building mart: mart_monthly_category_performance[/bold cyan]"
        )
        con.execute(monthly_category_performance_sql)

        console.print(
            "[bold cyan]Building mart: mart_category_mom_diagnostics[/bold cyan]"
        )
        con.execute(category_mom_diagnostics_sql)

        console.print(
            "[bold cyan]Building mart: mart_monthly_subcategory_performance[/bold cyan]"
        )
        con.execute(monthly_subcategory_performance_sql)

        console.print(
            "[bold cyan]Building mart: mart_electronics_subcategory_mom_diagnostics[/bold cyan]"
        )
        con.execute(electronics_subcategory_mom_diagnostics_sql)

        console.print(
            "[bold cyan]Building mart: mart_monthly_smartphone_brand_performance[/bold cyan]"
        )
        con.execute(monthly_smartphone_brand_performance_sql)

        console.print(
            "[bold cyan]Building mart: mart_smartphone_brand_mom_diagnostics[/bold cyan]"
        )
        con.execute(smartphone_brand_mom_diagnostics_sql)

        console.print(
            "[bold cyan]Building mart: mart_monthly_smartphone_price_band_performance[/bold cyan]"
        )
        con.execute(monthly_smartphone_price_band_performance_sql)

        console.print(
            "[bold cyan]Building mart: mart_smartphone_price_band_mom_diagnostics[/bold cyan]"
        )
        con.execute(smartphone_price_band_mom_diagnostics_sql)

        console.print(
            "[bold cyan]Building mart: mart_monthly_smartphone_brand_price_band_performance[/bold cyan]"
        )
        con.execute(monthly_smartphone_brand_price_band_performance_sql)

        console.print(
            "[bold cyan]Building mart: mart_smartphone_brand_price_band_mom_diagnostics[/bold cyan]"
        )
        con.execute(smartphone_brand_price_band_mom_diagnostics_sql)

        print_warehouse_objects(con)
        create_monthly_kpis_preview(con)
        create_category_diagnostics_preview(con)
        create_electronics_subcategory_preview(con)
        create_smartphone_brand_preview(con)
        create_smartphone_price_band_preview(con)
        create_smartphone_brand_price_band_preview(con)

        con.close()

    except Exception as exc:
        console.print(f"\n[bold red]Warehouse build failed:[/bold red] {exc}")
        return 1

    console.print(
        "\n[bold green]Warehouse build completed successfully.[/bold green]"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())