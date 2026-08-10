import polars as pl
from components.alerts import detect_anomalies, get_critical_suppliers

def test_detect_anomalies_flags_outlier():
    # 9 tight inliers + 1 extreme outlier -> z ~ 2.84 (ddof=1), clears 1.5.
    df = pl.DataFrame({
        "supplier_name": [f"S{i}" for i in range(1, 10)] + ["OUTLIER"],
        "risk_score": [10.0, 12.0, 11.0, 10.0, 12.0, 11.0, 10.0, 12.0, 11.0, 95.0],
    })
    anomalies = detect_anomalies(df, threshold=1.5)
    assert anomalies.height == 1
    assert anomalies["supplier_name"][0] == "OUTLIER"
    assert anomalies["z_score"][0] > 1.5

def test_detect_anomalies_clean_data_no_flags():
    df = pl.DataFrame({"supplier_name": ["A", "B", "C", "D"],
                       "risk_score": [10.0, 11.0, 10.5, 11.5]})
    assert detect_anomalies(df, threshold=1.5).height == 0

def test_get_critical_suppliers():
    df = pl.DataFrame({"supplier_name": ["A", "B", "C"], "risk_score": [50.0, 85.0, 92.0]})
    criticals = get_critical_suppliers(df, risk_cutoff=80.0)
    assert "B" in criticals and "C" in criticals and "A" not in criticals
