from datetime import datetime
from pathlib import Path

import duckdb

DB_PATH = Path(__file__).resolve().parent / "data" / "dashboard.duckdb"


def _query(snapshot_month, dimension, alias, order_by="total_cost_usd"):
    sql = f"""
        SELECT snapshot_month,
               dimension_value AS {alias},
               record_count,
               total_cost_usd
        FROM dbt_dev.fct_records_by_snapshot
        WHERE snapshot_month = ?
          AND dimension_type = ?
        ORDER BY {order_by} DESC
    """
    try:
        with duckdb.connect(str(DB_PATH), read_only=True) as conn:
            return conn.execute(sql, [snapshot_month, dimension]).df()
    except Exception as exc:
        raise RuntimeError(f"Unable to load local dashboard data: {exc}") from exc


def get_top_beneficiary_countries(snapshot_month):
    df = _query(snapshot_month, "beneficiary_country", "dimension_value")
    df.insert(1, "dimension_type", "beneficiary_country")
    return df[["snapshot_month", "dimension_type", "dimension_value",
               "record_count", "total_cost_usd"]]


def get_aid_by_sector(snapshot_month):
    return _query(snapshot_month, "project_sector", "project_sector")


def get_aid_by_donor(snapshot_month):
    return _query(snapshot_month, "project_donor", "project_donor")


def get_project_status(snapshot_month):
    return _query(snapshot_month, "project_status", "project_status", "record_count")


def get_data_last_updated():
    return datetime.fromtimestamp(DB_PATH.stat().st_mtime)


def get_mart_last_modified():
    return get_data_last_updated()
