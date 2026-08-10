import polars as pl
from unittest.mock import patch

def test_generate_report_success():
    with patch('utils.pdf_gen.RiskReport') as mock_cls:
        mock_cls.return_value.output.return_value = b'%PDF-1.4 mock'
        df = pl.DataFrame({"supplier": ["Test Corp"], "region": ["Global"],
                           "risk_score": [75.0]})
        from utils.pdf_gen import generate_report
        assert generate_report(df, "Test summary") == b'%PDF-1.4 mock'
