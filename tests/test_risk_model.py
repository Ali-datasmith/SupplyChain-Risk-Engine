import polars as pl
import numpy as np
from engine.risk_model import (normalize_scores, score_geo_risk, score_delay_risk,
                               score_financial_risk, compute_risk_score)

def test_normalize_scores_basic():
    normed = normalize_scores(np.array([0.0, 50.0, 100.0]))
    assert normed[0] == 0.0 and normed[2] == 100.0

def test_normalize_scores_all_same():
    assert np.all(normalize_scores(np.array([42.0, 42.0, 42.0])) == 0.0)

def test_score_geo_risk():
    assert 0.0 <= score_geo_risk(region_impact=1.0, event_density=10) <= 100.0

def test_score_delay_risk():
    assert 0.0 <= score_delay_risk(lead_time_days=30, variance=5.0) <= 100.0

def test_score_financial_risk():
    assert 0.0 <= score_financial_risk(revenue_at_risk=1000000, supplier_rating=0.2) <= 100.0

def test_compute_risk_score():
    df = pl.DataFrame({"geo_risk": [50.0], "delay_risk": [50.0], "financial_risk": [50.0]})
    res = compute_risk_score(df)
    assert "total_risk_score" in res.columns
    assert res["total_risk_score"][0] == 50.0
