from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.table import Table

console = Console()


def get_project_root() -> Path:
    """
    Returns the project root assuming this file lives at:
    src/data/inspect_raw_dataset.py
    """
    return Path(__file__).resolve().parents[2]


def find_raw_files(raw_dir: Path) -> list[Path]:
    """
    Finds supported raw files in the data/raw directory.
    """
    supported_suffixes = {".csv", ".parquet"}
    return sorted(
        [
            path
            for path in raw_dir.iterdir()
            if path.is_file() and path.suffix.lower() in supported_suffixes
        ]
    )


def read_sample(file_path: Path, sample_rows: int) -> pd.DataFrame:
    """
    Reads only a small sample of the raw file for fast schema inspection.
    """
    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(file_path, nrows=sample_rows, low_memory=False)

    if suffix == ".parquet":
        return pd.read_parquet(file_path).head(sample_rows)

    raise ValueError(f"Unsupported file type: {suffix}")


def print_file_overview(file_path: Path) -> None:
    size_mb = file_path.stat().st_size / (1024 * 1024)
    console.print(f"\n[bold cyan]File:[/bold cyan] {file_path.name}")
    console.print(f"[bold cyan]Size:[/bold cyan] {size_mb:,.2f} MB")


def print_column_summary(df: pd.DataFrame) -> None:
    table = Table(title="Column Summary")
    table.add_column("Column", style="cyan")
    table.add_column("Data Type", style="magenta")
    table.add_column("Non-Null", justify="right")
    table.add_column("Missing", justify="right")
    table.add_column("Missing %", justify="right")

    total_rows = len(df)

    for column in df.columns:
        non_null = int(df[column].notna().sum())
        missing = int(df[column].isna().sum())
        missing_pct = (missing / total_rows * 100) if total_rows else 0.0

        table.add_row(
            str(column),
            str(df[column].dtype),
            f"{non_null:,}",
            f"{missing:,}",
            f"{missing_pct:.2f}%",
        )

    console.print(table)


def print_candidate_field_values(df: pd.DataFrame) -> None:
    """
    Prints a quick view of likely business-critical fields if they exist.
    """
    candidate_columns = [
        "event_type",
        "event_name",
        "user_id",
        "user_session",
        "product_id",
        "category_id",
        "category_code",
        "brand",
    ]

    existing = [column for column in candidate_columns if column in df.columns]

    if not existing:
        console.print(
            "\n[yellow]No expected candidate analytics columns were found by name. "
            "That is fine; we will inspect the printed schema manually.[/yellow]"
        )
        return

    console.print("\n[bold green]Candidate Analytics Fields Detected[/bold green]")

    for column in existing:
        series = df[column]
        console.print(f"\n[bold]{column}[/bold]")
        console.print(f"Unique values in sample: {series.nunique(dropna=True):,}")

        if series.dtype == "object" or series.nunique(dropna=True) <= 20:
            value_counts = series.astype(str).value_counts(dropna=False).head(10)
            for value, count in value_counts.items():
                console.print(f"  - {value}: {count}")


def print_sample_rows(df: pd.DataFrame, row_count: int = 5) -> None:
    console.print("\n[bold blue]Sample Rows[/bold blue]")
    with pd.option_context("display.max_columns", None, "display.width", 200):
        console.print(df.head(row_count).to_string(index=False))


def inspect_file(file_path: Path, sample_rows: int) -> None:
    print_file_overview(file_path)

    try:
        df = read_sample(file_path, sample_rows)
    except Exception as exc:
        console.print(f"[bold red]Failed to read {file_path.name}: {exc}[/bold red]")
        return

    console.print(f"[bold cyan]Sample rows loaded:[/bold cyan] {len(df):,}")
    console.print(f"[bold cyan]Number of columns:[/bold cyan] {len(df.columns):,}")

    print_column_summary(df)
    print_candidate_field_values(df)
    print_sample_rows(df)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect raw CommercePulse dataset files."
    )
    parser.add_argument(
        "--sample-rows",
        type=int,
        default=5000,
        help="Number of rows to read from each raw file for schema inspection.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    project_root = get_project_root()
    raw_dir = project_root / "data" / "raw"

    console.print(f"[bold cyan]Project root:[/bold cyan] {project_root}")
    console.print(f"[bold cyan]Raw data directory:[/bold cyan] {raw_dir}")

    if not raw_dir.exists():
        console.print("[bold red]data/raw directory does not exist.[/bold red]")
        return 1

    raw_files = find_raw_files(raw_dir)

    if not raw_files:
        console.print(
            "[bold yellow]No CSV or Parquet files found in data/raw.[/bold yellow]"
        )
        console.print(
            "Download the dataset, extract it, and place the raw files inside data/raw/."
        )
        return 1

    console.print(f"[bold green]Found {len(raw_files)} raw file(s).[/bold green]")

    for file_path in raw_files:
        inspect_file(file_path, args.sample_rows)

    return 0


if __name__ == "__main__":
    sys.exit(main())