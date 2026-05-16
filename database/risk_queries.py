import duckdb
import polars as pl
import streamlit as st
import logging
from typing import List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(con: duckdb.DuckDBPyConnection) -> None:
    """Initializes the in-memory DuckDB schema for supply chain risks.

    Args:
        con: Active DuckDB connection object.
    """
    try:
        con.execute("""
            CREATE TABLE IF NOT EXISTS risk_data (
                supplier_id VARCHAR,
                supplier_name VARCHAR,
                region VARCHAR,
                risk_score FLOAT,
                risk_category VARCHAR,
                recorded_at TIMESTAMP
            )
        """)
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        st.warning("Database layer failed to initialize.")

@st.cache_data(ttl=300)
def query_by_region(region: str) -> pl.DataFrame:
    """Retrieves risk records filtered by a specific geographical region.

    Args:
        region: The region string to filter by.

    Returns:
        pl.DataFrame: Polars DataFrame containing regional risk data.
    """
    query = "SELECT * FROM risk_data WHERE region = ?"
    return run_query(query, [region])

@st.cache_data(ttl=300)
def query_top_risk_suppliers(limit: int = 10) -> pl.DataFrame:
    """Fetches the suppliers with the highest risk scores.

    Args:
        limit: Maximum number of records to return.

    Returns:
        pl.DataFrame: Polars DataFrame of high-risk suppliers.
    """
    query = "SELECT supplier_name, risk_score, risk_category FROM risk_data ORDER BY risk_score DESC LIMIT ?"
    return run_query(query, [limit])

@st.cache_data(ttl=300)
def query_monthly_trend() -> pl.DataFrame:
    """Aggregates average risk scores on a monthly basis.

    Returns:
        pl.DataFrame: Time-series risk trend data.
    """
    query = """
        SELECT
            date_trunc('month', recorded_at) as month,
            avg(risk_score) as avg_risk
        FROM risk_data
        GROUP BY 1
        ORDER BY 1
    """
    return run_query(query)

def run_query(sql: str, params: Optional[List[Any]] = None) -> pl.DataFrame:
    """Executes a parameterized DuckDB query and returns results as Polars.

    Args:
        sql: The SQL query string using '?' for parameters.
        params: Optional list of values to bind to the query.

    Returns:
        pl.DataFrame: Query results. Uses lazy execution for large datasets.
    """
    try:
        # In Streamlit Cloud, we use a shared memory connection
        con = duckdb.connect(':memory:')

        if params:
            res = con.execute(sql, params).pl()
        else:
            res = con.execute(sql).pl()

        # Rule 6: Handle large result sets using LazyFrames
        if len(res) > 10000:
            return res.lazy().collect()

        return res
    except Exception as e:
        logger.error(f"SQL Execution Error: {e} | Query: {sql}")
        st.warning("Data retrieval error. Please check logs.")
        return pl.DataFrame()

if __name__ == "__main__":
    # Smoke Test
    test_conn = duckdb.connect(':memory:')
    init_db(test_conn)

    # Mock Data Injection
    test_conn.execute("INSERT INTO risk_data VALUES ('S1', 'Acme Corp', 'EU', 85.5, 'Logistics', '2023-01-15')")
    test_conn.execute("INSERT INTO risk_data VALUES ('S2', 'Cyberdyne', 'US', 92.1, 'Cyber', '2023-02-20')")

    # Run test queries
    print("Testing Regional Query (EU):")
    print(query_by_region("EU"))

    print("\nTesting Monthly Trend Query:")
    print(query_monthly_trend())