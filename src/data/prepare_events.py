from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import duckdb
from rich.console import Console

console = Console()


def get_project_root() -> Path:
    """
    Returns the project root assuming this file lives at:
    src/data/prepare_events.py
    """
    return Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare clean CommercePulse e-commerce event data."
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Delete and recreate the existing clean events output directory.",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=4,
        help="Number of DuckDB threads to use. Default: 4.",
    )
    parser.add_argument(
        "--memory-limit",
        type=str,
        default="8GB",
        help="DuckDB memory limit. Default: 8GB.",
    )
    return parser.parse_args()


def ensure_raw_files_exist(raw_dir: Path) -> list[Path]:
    raw_files = sorted(raw_dir.glob("*.csv"))

    if not raw_files:
        raise FileNotFoundError(
            f"No CSV files found in raw directory: {raw_dir}"
        )

    return raw_files


def prepare_output_dir(output_dir: Path, overwrite: bool) -> None:
    if output_dir.exists():
        if overwrite:
            console.print(
                f"[yellow]Removing existing output directory:[/yellow] {output_dir}"
            )
            shutil.rmtree(output_dir)
        else:
            raise FileExistsError(
                f"Output directory already exists: {output_dir}\n"
                "Run again with --overwrite if you want to regenerate it."
            )

    output_dir.mkdir(parents=True, exist_ok=True)


def build_clean_events(
    raw_files: list[Path],
    output_dir: Path,
    threads: int,
    memory_limit: str,
) -> None:
    raw_file_paths_sql = ", ".join(
        [f"'{path.as_posix()}'" for path in raw_files]
    )

    output_dir_sql = output_dir.as_posix()

    console.print("[bold cyan]Raw files detected:[/bold cyan]")
    for path in raw_files:
        size_gb = path.stat().st_size / (1024 ** 3)
        console.print(f"  - {path.name} ({size_gb:.2f} GB)")

    console.print("\n[bold cyan]Starting DuckDB transformation...[/bold cyan]")

    con = duckdb.connect(database=":memory:")
    con.execute(f"PRAGMA threads={threads};")
    con.execute(f"PRAGMA memory_limit='{memory_limit}';")
    con.execute("PRAGMA enable_progress_bar=true;")

    clean_sql = f"""
    COPY (
        WITH raw_events AS (
            SELECT
                *,
                TRY_CAST(
                    REPLACE(CAST(event_time AS VARCHAR), ' UTC', '')
                    AS TIMESTAMP
                ) AS parsed_event_ts
            FROM read_csv(
                [{raw_file_paths_sql}],
                header = true,
                union_by_name = true,
                filename = true,
                all_varchar = false,
                sample_size = -1
            )
        )

        SELECT
            parsed_event_ts AS event_ts,
            CAST(parsed_event_ts AS DATE) AS event_date,
            STRFTIME(parsed_event_ts, '%Y-%m') AS event_month,
            STRFTIME(parsed_event_ts, '%Y-%m-%d') AS event_day,
            EXTRACT(HOUR FROM parsed_event_ts)::INTEGER AS event_hour,

            LOWER(TRIM(CAST(event_type AS VARCHAR))) AS event_type,

            product_id::BIGINT AS product_id,
            category_id::BIGINT AS category_id,
            NULLIF(TRIM(CAST(category_code AS VARCHAR)), '') AS category_code,
            NULLIF(LOWER(TRIM(CAST(brand AS VARCHAR))), '') AS brand,
            price::DOUBLE AS price,

            user_id::BIGINT AS user_id,
            NULLIF(TRIM(CAST(user_session AS VARCHAR)), '') AS user_session,

            filename AS source_file

        FROM raw_events
        WHERE
            parsed_event_ts IS NOT NULL
            AND event_type IS NOT NULL
            AND user_id IS NOT NULL
            AND product_id IS NOT NULL
    )
    TO '{output_dir_sql}'
    (
        FORMAT PARQUET,
        PARTITION_BY (event_month),
        COMPRESSION ZSTD,
        OVERWRITE_OR_IGNORE TRUE
    );
    """

    con.execute(clean_sql)
    con.close()

    console.print(
        f"\n[bold green]Clean events written successfully to:[/bold green] {output_dir}"
    )


def main() -> int:
    args = parse_args()

    project_root = get_project_root()
    raw_dir = project_root / "data" / "raw"
    output_dir = project_root / "data" / "interim" / "events_clean"

    console.print(f"[bold cyan]Project root:[/bold cyan] {project_root}")
    console.print(f"[bold cyan]Raw directory:[/bold cyan] {raw_dir}")
    console.print(f"[bold cyan]Output directory:[/bold cyan] {output_dir}")

    try:
        raw_files = ensure_raw_files_exist(raw_dir)
        prepare_output_dir(output_dir, overwrite=args.overwrite)
        build_clean_events(
            raw_files=raw_files,
            output_dir=output_dir,
            threads=args.threads,
            memory_limit=args.memory_limit,
        )
    except Exception as exc:
        console.print(f"\n[bold red]Preparation failed:[/bold red] {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())