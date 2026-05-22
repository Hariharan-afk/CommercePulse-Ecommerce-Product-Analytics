from __future__ import annotations

import sys
from pathlib import Path

import duckdb
from rich.console import Console
from rich.table import Table

console = Console()


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run_query(con: duckdb.DuckDBPyConnection, query: str):
    return con.execute(query).fetchall()


def print_overview(con: duckdb.DuckDBPyConnection, parquet_glob: str) -> None:
    query = f"""
    SELECT
        COUNT(*) AS total_rows,
        MIN(event_ts) AS min_event_ts,
        MAX(event_ts) AS max_event_ts,
        COUNT(DISTINCT user_id) AS unique_users,
        COUNT(DISTINCT user_session) AS unique_sessions,
        COUNT(DISTINCT product_id) AS unique_products,
        COUNT(DISTINCT category_id) AS unique_categories,
        COUNT(DISTINCT brand) AS unique_brands
    FROM read_parquet('{parquet_glob}', hive_partitioning = true);
    """

    row = run_query(con, query)[0]

    table = Table(title="Clean Events Dataset Overview")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    metrics = [
        ("Total rows", f"{row[0]:,}"),
        ("Minimum event timestamp", str(row[1])),
        ("Maximum event timestamp", str(row[2])),
        ("Unique users", f"{row[3]:,}"),
        ("Unique sessions", f"{row[4]:,}"),
        ("Unique products", f"{row[5]:,}"),
        ("Unique categories", f"{row[6]:,}"),
        ("Unique brands", f"{row[7]:,}"),
    ]

    for metric, value in metrics:
        table.add_row(metric, value)

    console.print(table)


def print_event_type_summary(
    con: duckdb.DuckDBPyConnection,
    parquet_glob: str,
) -> None:
    query = f"""
    SELECT
        event_month,
        event_type,
        COUNT(*) AS event_count,
        ROUND(
            COUNT(*) * 100.0
            / SUM(COUNT(*)) OVER (PARTITION BY event_month),
            2
        ) AS pct_within_month
    FROM read_parquet('{parquet_glob}', hive_partitioning = true)
    GROUP BY event_month, event_type
    ORDER BY event_month, event_count DESC;
    """

    rows = run_query(con, query)

    table = Table(title="Event Type Distribution by Month")
    table.add_column("Month", style="cyan")
    table.add_column("Event Type", style="magenta")
    table.add_column("Count", justify="right")
    table.add_column("% Within Month", justify="right")

    for month, event_type, count, pct in rows:
        table.add_row(
            str(month),
            str(event_type),
            f"{count:,}",
            f"{pct:.2f}%",
        )

    console.print(table)


def print_missingness_summary(
    con: duckdb.DuckDBPyConnection,
    parquet_glob: str,
) -> None:
    query = f"""
    SELECT
        COUNT(*) AS total_rows,
        SUM(CASE WHEN category_code IS NULL THEN 1 ELSE 0 END) AS missing_category_code,
        SUM(CASE WHEN brand IS NULL THEN 1 ELSE 0 END) AS missing_brand,
        SUM(CASE WHEN user_session IS NULL THEN 1 ELSE 0 END) AS missing_user_session,
        SUM(CASE WHEN event_ts IS NULL THEN 1 ELSE 0 END) AS missing_event_ts
    FROM read_parquet('{parquet_glob}', hive_partitioning = true);
    """

    row = run_query(con, query)[0]
    total_rows = row[0]

    columns = [
        ("category_code", row[1]),
        ("brand", row[2]),
        ("user_session", row[3]),
        ("event_ts", row[4]),
    ]

    table = Table(title="Missingness Summary")
    table.add_column("Column", style="cyan")
    table.add_column("Missing Rows", justify="right")
    table.add_column("Missing %", justify="right")

    for column, missing in columns:
        missing_pct = (missing / total_rows * 100) if total_rows else 0.0
        table.add_row(
            column,
            f"{missing:,}",
            f"{missing_pct:.2f}%",
        )

    console.print(table)


def print_purchase_summary(
    con: duckdb.DuckDBPyConnection,
    parquet_glob: str,
) -> None:
    query = f"""
    SELECT
        event_month,
        COUNT(*) FILTER (WHERE event_type = 'purchase') AS purchase_events,
        ROUND(
            SUM(price) FILTER (WHERE event_type = 'purchase'),
            2
        ) AS purchase_revenue,
        ROUND(
            AVG(price) FILTER (WHERE event_type = 'purchase'),
            2
        ) AS avg_purchase_price
    FROM read_parquet('{parquet_glob}', hive_partitioning = true)
    GROUP BY event_month
    ORDER BY event_month;
    """

    rows = run_query(con, query)

    table = Table(title="Purchase Summary by Month")
    table.add_column("Month", style="cyan")
    table.add_column("Purchase Events", justify="right")
    table.add_column("Purchase Revenue", justify="right")
    table.add_column("Avg Purchase Price", justify="right")

    for month, purchase_events, purchase_revenue, avg_purchase_price in rows:
        table.add_row(
            str(month),
            f"{purchase_events:,}",
            f"${purchase_revenue:,.2f}" if purchase_revenue is not None else "$0.00",
            f"${avg_purchase_price:,.2f}" if avg_purchase_price is not None else "$0.00",
        )

    console.print(table)


def print_null_timestamp_check(
    con: duckdb.DuckDBPyConnection,
    parquet_glob: str,
) -> None:
    query = f"""
    SELECT COUNT(*)
    FROM read_parquet('{parquet_glob}', hive_partitioning = true)
    WHERE event_ts IS NULL;
    """

    null_count = run_query(con, query)[0][0]

    if null_count == 0:
        console.print(
            "[bold green]Timestamp parsing check passed: no null event_ts values.[/bold green]"
        )
    else:
        console.print(
            f"[bold red]Timestamp parsing issue: {null_count:,} rows have null event_ts.[/bold red]"
        )


def main() -> int:
    project_root = get_project_root()
    clean_dir = project_root / "data" / "interim" / "events_clean"
    parquet_glob = (clean_dir / "**" / "*.parquet").as_posix()

    console.print(f"[bold cyan]Project root:[/bold cyan] {project_root}")
    console.print(f"[bold cyan]Clean events directory:[/bold cyan] {clean_dir}")

    if not clean_dir.exists():
        console.print(
            "[bold red]Clean event dataset does not exist. Run prepare_events.py first.[/bold red]"
        )
        return 1

    con = duckdb.connect(database=":memory:")
    con.execute("PRAGMA threads=4;")
    con.execute("PRAGMA enable_progress_bar=true;")

    try:
        print_overview(con, parquet_glob)
        print_event_type_summary(con, parquet_glob)
        print_missingness_summary(con, parquet_glob)
        print_purchase_summary(con, parquet_glob)
        print_null_timestamp_check(con, parquet_glob)
    except Exception as exc:
        console.print(f"[bold red]Profiling failed:[/bold red] {exc}")
        return 1
    finally:
        con.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())