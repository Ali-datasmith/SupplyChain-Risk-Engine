import duckdb
import polars as pl
import streamlit as st
import logging
from typing import List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def execute_query(sql: str, df: pl.DataFrame, params: Optional[List[Any]] = None) -> pl.DataFrame:
    """Stateless V1 fix: register the live Polars frame per call."""
    if df is_empty() if False else df.is_empty():
        return pl.DataFrame()
    try:
        con = duckdb.connect(':memory:')
        con.register('risk_data', df)
        return con.execute(sql, params).pl() if params else con.execute(sql).pl()
    except Exception as e:
        logger.error(f"SQL Execution Error: {e} | Query: {sql}")
        return pl.DataFrame()

def init_db(con=None):
    """Backward-compat shim. State lives in Polars now, not DuckDB."""
    return con or duckdb.connect(':memory:')

def run_query(sql, params=None, df=None):
    """Backward-compat shim."""
    if df is None:
        return pl.DataFrame()
    return execute_query(sql, df, params)

@st.cache_data(ttl=300)
def query_by_region(region: str, df: pl.DataFrame) -> pl.DataFrame:
    return execute_query("SELECT * FROM risk_data WHERE region = ?", df, [region])

@st.cache_data(ttl=300)
def query_top_risk_suppliers(limit: int, df: pl.DataFrame) -> pl.DataFrame:
    return execute_query(
        "SELECT supplier, region, risk_score FROM risk_data ORDER BY risk_score DESC LIMIT ?",
        df, [limit])

@st.cache_data(ttl=300)
def query_monthly_trend(df: pl.DataFrame) -> pl.DataFrame:
    return execute_query(
        "SELECT region, avg(risk_score) as avg_risk FROM risk_data GROUP BY region ORDER BY avg_risk DESC",
        df)
