from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console

console = Console()


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    console.print(f"[green]Generated:[/green] {path}")


def build_readme() -> str:
    return r"""
# CommercePulse: E-Commerce Product Analytics & Funnel Diagnostics

CommercePulse is an end-to-end data analytics project built on 109M+ e-commerce behavior events from a multi-category online store. The project analyzes October–November 2019 customer behavior to understand revenue growth, funnel shifts, category performance, and smartphone segment dynamics.

The project uses a reproducible analytics engineering workflow:

- Raw event ingestion
- DuckDB-based warehouse modeling
- SQL marts for business KPIs
- Month-over-month diagnostics
- Product/category funnel analysis
- Power BI executive dashboard
- Written business insight reports

---

## Business Problem

November showed strong growth in platform activity and revenue, but downstream funnel quality weakened.

The core question investigated in this project:

> Why did November revenue and cart activity increase while cart-to-purchase conversion declined?

---

## Key Results

Between October and November 2019:

- Total events increased from 42.45M to 67.50M.
- Active users increased from 3.02M to 3.70M.
- Purchase revenue increased from $229.96M to $275.19M.
- Session View → Cart rate increased from 6.18% to 12.57%.
- Session Cart → Purchase rate declined from 49.17% to 37.10%.

The analysis found that:

- Electronics was the largest revenue growth driver.
- Smartphones dominated electronics revenue growth.
- Apple and Samsung drove most smartphone growth.
- Premium smartphone tiers, especially $800–$1199 and $1200+, were major growth contributors.
- Apple $800–$1199, Apple $1200+, and Samsung $100–$249 explained most smartphone revenue growth.
- Several high-value segments suffered meaningful cart-to-purchase deterioration.

---

## Final Analytical Story

```text
Platform Level
November traffic, carting, and revenue rose — but cart-to-purchase efficiency fell.

↓
Category Level
Electronics drove the largest revenue growth and conversion deterioration.

↓
Subcategory Level
Smartphones dominated electronics growth.

↓
Brand Level
Apple and Samsung drove most smartphone expansion.

↓
Price Band Level
Premium smartphones and the $100–$249 band drove growth.

↓
Brand × Price Band Level
Apple $800–$1199, Apple $1200+, and Samsung $100–$249 explained the strongest smartphone revenue growth.
"""