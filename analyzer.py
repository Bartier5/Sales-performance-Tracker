# analyzer.py
import pandas as pd
from queries import (
    get_all_sales,
    get_top_performers,
    get_sales_by_region,
    get_sales_by_product,
    get_monthly_trend,
)

# --- Constants ---
REVENUE_COL = "total_value"
REP_COL = "rep_name"
REGION_COL = "region"
PRODUCT_COL = "product"


def summary_stats() -> pd.DataFrame:
    """High-level KPIs: total revenue, total sales, avg deal size, top rep."""
    df = get_all_sales()

    total_revenue = df[REVENUE_COL].sum()
    total_sales = len(df)
    avg_deal_size = df[REVENUE_COL].mean()
    top_rep = df.groupby(REP_COL)[REVENUE_COL].sum().idxmax()
    top_region = df.groupby(REGION_COL)[REVENUE_COL].sum().idxmax()
    best_product = df.groupby(PRODUCT_COL)[REVENUE_COL].sum().idxmax()

    summary = pd.DataFrame([{
        "Total Revenue":    f"${total_revenue:,.2f}",
        "Total Sales":      total_sales,
        "Avg Deal Size":    f"${avg_deal_size:,.2f}",
        "Top Rep":          top_rep,
        "Top Region":       top_region,
        "Best Product":     best_product,
    }]).T  # Transpose so KPIs read top-to-bottom

    summary.columns = ["Value"]
    summary.index.name = "Metric"
    return summary


def rep_performance_breakdown() -> pd.DataFrame:
    """
    Per-rep breakdown: revenue, sales count, avg deal size,
    best product, and revenue share %.
    """
    df = get_all_sales()

    breakdown = (
        df.groupby(REP_COL)
        .agg(
            total_revenue=(REVENUE_COL, "sum"),
            total_sales=("sale_id", "count"),
            avg_deal_size=(REVENUE_COL, "mean"),
        )
        .reset_index()
    )

    # Revenue share as a percentage of total
    total = breakdown["total_revenue"].sum()
    breakdown["revenue_share_%"] = (breakdown["total_revenue"] / total * 100).round(2)

    # Best product per rep using a groupby inside a transform
    best_product_per_rep = (
        df.groupby([REP_COL, PRODUCT_COL])[REVENUE_COL]
        .sum()
        .reset_index()
        .sort_values(REVENUE_COL, ascending=False)
        .drop_duplicates(subset=REP_COL)
        .set_index(REP_COL)[PRODUCT_COL]
    )
    breakdown["best_product"] = breakdown[REP_COL].map(best_product_per_rep)

    # Format currency columns
    breakdown["total_revenue"] = breakdown["total_revenue"].apply(lambda x: f"${x:,.2f}")
    breakdown["avg_deal_size"] = breakdown["avg_deal_size"].apply(lambda x: f"${x:,.2f}")

    return breakdown.sort_values("revenue_share_%", ascending=False)


def region_product_pivot() -> pd.DataFrame:
    """
    Pivot table: regions as rows, products as columns,
    total revenue as values.
    """
    df = get_all_sales()

    pivot = df.pivot_table(
        values=REVENUE_COL,
        index=REGION_COL,
        columns=PRODUCT_COL,
        aggfunc="sum",
        fill_value=0,
        margins=True,
        margins_name="TOTAL",
    )

    # Format all cells as currency
    return pivot.map(lambda x: f"${x:,.2f}")


def monthly_growth() -> pd.DataFrame:
    """
    Monthly revenue with month-over-month growth % column.
    """
    df = get_monthly_trend()

    df["revenue_growth_%"] = (
        df["total_revenue"]
        .pct_change()
        .mul(100)
        .round(2)
    )

    df["total_revenue"] = df["total_revenue"].apply(lambda x: f"${x:,.2f}")
    df["revenue_growth_%"] = df["revenue_growth_%"].apply(
        lambda x: f"{x:+.2f}%" if pd.notna(x) else "—"
    )

    return df


def underperformers(threshold_percentile: float = 0.4) -> pd.DataFrame:
    """
    Flag reps whose total revenue falls below the given percentile threshold.
    Default: bottom 40%.
    """
    df = get_all_sales()

    rep_revenue = (
        df.groupby(REP_COL)[REVENUE_COL]
        .sum()
        .reset_index()
        .rename(columns={REVENUE_COL: "total_revenue"})
    )

    cutoff = rep_revenue["total_revenue"].quantile(threshold_percentile)
    flagged = rep_revenue[rep_revenue["total_revenue"] <= cutoff].copy()
    flagged["status"] = "⚠ Below threshold"
    flagged["total_revenue"] = flagged["total_revenue"].apply(lambda x: f"${x:,.2f}")

    return flagged.sort_values("total_revenue")