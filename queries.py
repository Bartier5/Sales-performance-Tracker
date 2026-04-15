import pandas as pd
import sqlite3
import os

DB_PATH = "db/sales.db"
TABLE_NAME = "sales"

def _get_connection() -> sqlite3.Connection:
    """Return a live SQLite connection. Raises cleanly if DB doesn't exist."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"Database not found at '{DB_PATH}'. Run option 1 first to load data."
        )
    return sqlite3.connect(DB_PATH)

def get_all_sales() -> pd.DataFrame:
    """Return every row in the sales table."""
    conn = _get_connection()
    try:
        df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
        return df
    finally:
        conn.close()
        
def get_top_performers(limit: int = 5) -> pd.DataFrame:
    """Return top N reps ranked by total revenue generated."""
    conn = _get_connection()
    try:
        query = f"""
            SELECT
                rep_name,
                COUNT(sale_id)      AS total_sales,
                SUM(total_value)    AS total_revenue
            FROM {TABLE_NAME}
            GROUP BY rep_name
            ORDER BY total_revenue DESC
            LIMIT ?
        """
        df = pd.read_sql_query(query, conn, params=(limit,))
        return df
    finally:
        conn.close()
def get_sales_by_region() -> pd.DataFrame:
    """Return revenue and sale count broken down by region."""
    conn = _get_connection()
    try:
        query = f"""
            SELECT
                region,
                COUNT(sale_id)      AS total_sales,
                SUM(quantity)       AS units_sold,
                SUM(total_value)    AS total_revenue
            FROM {TABLE_NAME}
            GROUP BY region
            ORDER BY total_revenue DESC
        """
        df = pd.read_sql_query(query, conn)
        return df
    finally:
        conn.close()


def get_sales_by_product() -> pd.DataFrame:
    """Return revenue, units sold, and avg deal size per product."""
    conn = _get_connection()
    try:
        query = f"""
            SELECT
                product,
                COUNT(sale_id)          AS total_sales,
                SUM(quantity)           AS units_sold,
                SUM(total_value)        AS total_revenue,
                AVG(total_value)        AS avg_deal_size
            FROM {TABLE_NAME}
            GROUP BY product
            ORDER BY total_revenue DESC
        """
        df = pd.read_sql_query(query, conn)
        return df
    finally:
        conn.close()


def get_monthly_trend() -> pd.DataFrame:
    """Return total revenue per month, ordered chronologically."""
    conn = _get_connection()
    try:
        query = f"""
            SELECT
                strftime('%Y-%m', sale_date)    AS month,
                COUNT(sale_id)                  AS total_sales,
                SUM(total_value)                AS total_revenue
            FROM {TABLE_NAME}
            GROUP BY month
            ORDER BY month ASC
        """
        df = pd.read_sql_query(query, conn)
        return df
    finally:
        conn.close()