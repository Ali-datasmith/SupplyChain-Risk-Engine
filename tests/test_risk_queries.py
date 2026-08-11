import polars as pl
from database.risk_queries import (execute_query, query_by_region,
                                   query_top_risk_suppliers, query_monthly_trend)

DF = pl.DataFrame({
    "supplier": ["A", "B", "C"],
    "region": ["EU", "US", "EU"],
    "risk_score": [80.0, 30.0, 55.0],
})

def test_execute_query_orders_desc():
    res = execute_query("SELECT supplier, risk_score FROM risk_data ORDER BY risk_score DESC", DF)
    assert res.height == 3
    assert res["supplier"][0] == "A"

def test_query_top_risk_suppliers_limit():
    assert query_top_risk_suppliers(2, DF).height == 2

def test_query_by_region_filters():
    res = query_by_region("EU", DF)
    assert res.height == 2
    assert set(res["supplier"].to_list()) == {"A", "C"}

def test_query_monthly_trend_aggregates():
    res = query_monthly_trend(DF)
    assert res.height == 2

def test_empty_df_returns_empty():
    assert execute_query("SELECT 1", pl.DataFrame()).is_empty()
