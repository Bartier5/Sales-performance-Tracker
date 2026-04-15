import pandas as pd
import sqlite3
import os

DB_PATH = "db/sales.db"
TABLE_NAME = "sales"

REQUIRED_COLUMNS = {"sale_id","rep_name","region","product","quantity","unit_price","sale_date"}
def load_csv(filepath: str) -> pd.DataFrame:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    df = pd.read_csv(filepath)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing columns: {missing}")
    df["sale_date"] = pd.to_datetime(df["sale_date"])
    df["quantity"] = df["quantity"].astype(int)
    df["unit_price"] = df["unit_price"].astype(float)
    
    df["total_value"] = df["quantity"] * df["unit_price"]

    print(f"[loader] Loaded {len(df)} records from '{filepath}'")
    return df
def push_to_db(df: pd.DataFrame, db_path: str = DB_PATH) -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        df.to_sql(TABLE_NAME,conn, if_exists="replace", index=False)
        print(f"[loader] pushed {len(df)} records to '{db_path}' -> table {TABLE_NAME}")
    finally:
        conn.close()
def load_and_store(filepath: str) -> None:
    df = load_csv(filepath)
    push_to_db(df)
    print("[loader] Done. Database is ready.")
    