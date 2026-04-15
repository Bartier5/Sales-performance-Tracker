# exporter.py
import pandas as pd
import os
from datetime import datetime
from analyzer import (
    summary_stats,
    rep_performance_breakdown,
    region_product_pivot,
    monthly_growth,
    underperformers,
)

# --- Constants ---
OUTPUT_DIR = "output"


def _ensure_output_dir() -> None:
    """Create output/ directory if it doesn't exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def _timestamped_filename(label: str) -> str:
    """Generate a filename like: output/summary_report_2024-03-15_14-30.csv"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    return os.path.join(OUTPUT_DIR, f"{label}_{timestamp}.csv")


def _write_csv(df: pd.DataFrame, filepath: str) -> None:
    """Write DataFrame to CSV and confirm."""
    df.to_csv(filepath, index=True)
    print(f"[exporter] Saved → {filepath}")


def export_summary_report() -> None:
    """
    Export all five analysis sections into a single CSV,
    separated by labelled section headers.
    """
    _ensure_output_dir()
    filepath = _timestamped_filename("summary_report")

    sections = [
        ("SUMMARY KPIs", summary_stats()),
        ("REP PERFORMANCE BREAKDOWN", rep_performance_breakdown()),
        ("REGION x PRODUCT PIVOT", region_product_pivot()),
        ("MONTHLY GROWTH", monthly_growth()),
        ("UNDERPERFORMERS", underperformers()),
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        for label, df in sections:
            # Write section header as a comment row
            f.write(f"# {label}\n")
            df.to_csv(f, index=True)
            f.write("\n")  # Blank line between sections

    print(f"[exporter] Full report saved → {filepath}")


def export_single(label: str, df: pd.DataFrame) -> None:
    """
    Export any single DataFrame to its own timestamped CSV.
    Used for targeted exports from the CLI menu.
    """
    _ensure_output_dir()
    filepath = _timestamped_filename(label.lower().replace(" ", "_"))
    _write_csv(df, filepath)