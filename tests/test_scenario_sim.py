import polars as pl
from engine.scenario_sim import (simulate_disruption, calc_inventory_impact,
                                 project_lead_time_change)

def test_simulate_disruption():
    df = pl.DataFrame({"supplier": ["A", "B"], "region": ["APAC", "EMEA"],
                       "risk_score": [20.0, 30.0]})
    sim = simulate_disruption(df, 2.0, ["APAC"])
    assert sim.filter(pl.col("supplier") == "A")["simulated_risk_score"][0] == 40.0
    assert sim.filter(pl.col("supplier") == "B")["simulated_risk_score"][0] == 30.0

def test_calc_inventory_impact_safe():
    res = calc_inventory_impact(1000.0, 100.0, 5)
    assert res["days_cover"] == 10.0 and res["shortfall_probability"] < 0.5

def test_calc_inventory_impact_risky():
    res = calc_inventory_impact(100.0, 100.0, 20)
    assert res["days_cover"] == 1.0 and res["shortfall_probability"] > 0.5

def test_project_lead_time_change_no_strike():
    assert project_lead_time_change(10.0, 1.5, False) == 15.0

def test_project_lead_time_change_strike():
    assert project_lead_time_change(10.0, 1.5, True) == 21.0
