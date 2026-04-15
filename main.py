# main.py
import os
import sys
from loader import load_and_store
from queries import (
    get_all_sales,
    get_top_performers,
    get_sales_by_region,
    get_sales_by_product,
    get_monthly_trend,
)
from analyzer import (
    summary_stats,
    rep_performance_breakdown,
    region_product_pivot,
    monthly_growth,
    underperformers,
)
from exporter import export_summary_report, export_single

# --- Constants ---
DEFAULT_CSV = "data/sales_data.csv"
DB_PATH = "db/sales.db"
DIVIDER = "=" * 55


def clear() -> None:
    """Clear terminal screen cross-platform."""
    os.system("cls" if os.name == "nt" else "clear")


def pause() -> None:
    """Hold output on screen until user is ready."""
    input("\nPress Enter to return to menu...")


def print_header() -> None:
    print(DIVIDER)
    print("     SALES PERFORMANCE TRACKER".center(55))
    print(DIVIDER)


def print_menu() -> None:
    print_header()
    print("""
  DATA
  ─────────────────────────────────────────────
  1. Load CSV data into database
  2. View all sales records

  ANALYSIS
  ─────────────────────────────────────────────
  3. Summary KPIs
  4. Top performers by revenue
  5. Rep performance breakdown
  6. Sales by region
  7. Sales by product
  8. Region × Product pivot table
  9. Monthly revenue trend
  10. Month-over-month growth
  11. Flag underperformers

  EXPORT
  ─────────────────────────────────────────────
  12. Export full summary report
  13. Export single view

  ─────────────────────────────────────────────
  0.  Exit
""")


def db_check() -> bool:
    """Warn user if DB doesn't exist yet."""
    if not os.path.exists(DB_PATH):
        print("\n  [!] No database found. Please run option 1 first.\n")
        pause()
        return False
    return True


# ── Menu Handlers ──────────────────────────────────────────


def handle_load() -> None:
    print(f"\n  Loading from: {DEFAULT_CSV}\n")
    try:
        load_and_store(DEFAULT_CSV)
    except FileNotFoundError as e:
        print(f"  [!] {e}")
    except Exception as e:
        print(f"  [!] Unexpected error: {e}")
    pause()


def handle_view_all() -> None:
    if not db_check():
        return
    df = get_all_sales()
    print(f"\n  {len(df)} records found:\n")
    print(df.to_string(index=False))
    pause()


def handle_summary_kpis() -> None:
    if not db_check():
        return
    print("\n  SUMMARY KPIs\n" + "─" * 35)
    print(summary_stats().to_string())
    pause()


def handle_top_performers() -> None:
    if not db_check():
        return
    try:
        n = int(input("\n  Show top how many reps? [default 5]: ").strip() or 5)
    except ValueError:
        n = 5
    print(f"\n  TOP {n} PERFORMERS\n" + "─" * 35)
    print(get_top_performers(limit=n).to_string(index=False))
    pause()


def handle_rep_breakdown() -> None:
    if not db_check():
        return
    print("\n  REP PERFORMANCE BREAKDOWN\n" + "─" * 35)
    print(rep_performance_breakdown().to_string(index=False))
    pause()


def handle_by_region() -> None:
    if not db_check():
        return
    print("\n  SALES BY REGION\n" + "─" * 35)
    print(get_sales_by_region().to_string(index=False))
    pause()


def handle_by_product() -> None:
    if not db_check():
        return
    print("\n  SALES BY PRODUCT\n" + "─" * 35)
    print(get_sales_by_product().to_string(index=False))
    pause()


def handle_pivot() -> None:
    if not db_check():
        return
    print("\n  REGION × PRODUCT PIVOT\n" + "─" * 35)
    print(region_product_pivot().to_string())
    pause()


def handle_monthly_trend() -> None:
    if not db_check():
        return
    print("\n  MONTHLY REVENUE TREND\n" + "─" * 35)
    print(get_monthly_trend().to_string(index=False))
    pause()


def handle_monthly_growth() -> None:
    if not db_check():
        return
    print("\n  MONTH-OVER-MONTH GROWTH\n" + "─" * 35)
    print(monthly_growth().to_string(index=False))
    pause()


def handle_underperformers() -> None:
    if not db_check():
        return
    try:
        pct = float(
            input("\n  Percentile threshold (0–1) [default 0.4]: ").strip() or 0.4
        )
        if not 0 < pct < 1:
            raise ValueError
    except ValueError:
        print("  [!] Invalid input. Using default 0.4.")
        pct = 0.4
    print(f"\n  UNDERPERFORMERS (bottom {int(pct*100)}%)\n" + "─" * 35)
    result = underperformers(threshold_percentile=pct)
    if result.empty:
        print("  No underperformers flagged at this threshold.")
    else:
        print(result.to_string(index=False))
    pause()


def handle_export_full() -> None:
    if not db_check():
        return
    print()
    export_summary_report()
    pause()


def handle_export_single() -> None:
    if not db_check():
        return

    options = {
        "1": ("summary_kpis",       summary_stats),
        "2": ("top_performers",     lambda: get_top_performers(5)),
        "3": ("rep_breakdown",      rep_performance_breakdown),
        "4": ("by_region",          get_sales_by_region),
        "5": ("by_product",         get_sales_by_product),
        "6": ("pivot_table",        region_product_pivot),
        "7": ("monthly_trend",      get_monthly_trend),
        "8": ("monthly_growth",     monthly_growth),
        "9": ("underperformers",    underperformers),
    }

    print("\n  Which view to export?")
    for key, (label, _) in options.items():
        print(f"  {key}. {label}")

    choice = input("\n  Enter number: ").strip()

    if choice not in options:
        print("  [!] Invalid choice.")
        pause()
        return

    label, fn = options[choice]
    print()
    export_single(label, fn())
    pause()


# ── Dispatch Table ──────────────────────────────────────────

MENU_ACTIONS = {
    "1":  handle_load,
    "2":  handle_view_all,
    "3":  handle_summary_kpis,
    "4":  handle_top_performers,
    "5":  handle_rep_breakdown,
    "6":  handle_by_region,
    "7":  handle_by_product,
    "8":  handle_pivot,
    "9":  handle_monthly_trend,
    "10": handle_monthly_growth,
    "11": handle_underperformers,
    "12": handle_export_full,
    "13": handle_export_single,
}


# ── Main Loop ───────────────────────────────────────────────

def main() -> None:
    while True:
        clear()
        print_menu()

        choice = input("  Select option: ").strip()

        if choice == "0":
            print("\n  Goodbye.\n")
            sys.exit(0)

        action = MENU_ACTIONS.get(choice)

        if action:
            clear()
            action()
        else:
            print("\n  [!] Invalid option. Try again.")
            pause()


if __name__ == "__main__":
    main()