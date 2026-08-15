import duckdb
import polars as pl
import logging
from typing import List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WHY THERE IS NO @st.cache_data HERE (do not re-add):
# 1. st.cache_data must hash every argument; Polars DataFrames are not
#    hashable -> UnhashableParamError in production Streamlit.
# 2. The suggested `_df` underscore workaround removes the data from the
#    cache key. In a public multi-session demo that serves one visitor's
#    cached results to another visitor for up to ttl seconds.
# 3. These are in-memory DuckDB aggregations (millisecond-fast).
#    Caching buys nothing and risks correctness.

def execute_query(sql: str, df: pl.DataFrame, params: Optional[List[Any]] = None) -> pl.DataFrame:
    """Stateless V1 DuckDB layer: register the live Polars frame per call."""
    if df.is_empty():
        return pl.DataFrame()
    try:
        con = duckdb.connect(':memory:')
        con.register('risk_data', df)
        if params:
            return con.execute(sql, params).pl()
        return con.execute(sql).pl()
    except Exception as e:
        logger.error(f"SQL Execution Error: {e} | Query: {sql}")
        return pl.DataFrame()

def init_db(con=None):
    """Backward-compat shim; state now lives in Polars, not DuckDB."""
    return con or duckdb.connect(':memory:')

def run_query(sql, params=None, df=None):
    """Backward-compat shim."""
    if df is None:
        return pl.DataFrame()
    return execute_query(sql, df, params)

def query_by_region(region: str, df: pl.DataFrame) -> pl.DataFrame:
    return execute_query("SELECT * FROM risk_data WHERE region = ?", df, [region])

def query_top_risk_suppliers(limit: int, df: pl.DataFrame) -> pl.DataFrame:
    return execute_query(
        "SELECT supplier, region, risk_score FROM risk_data "
        "ORDER BY risk_score DESC LIMIT ?",
        df, [limit])

def query_monthly_trend(df: pl.DataFrame) -> pl.DataFrame:
    return execute_query(
        "SELECT region, avg(risk_score) AS avg_risk FROM risk_data "
        "GROUP BY region ORDER BY avg_risk DESC",
        df)
