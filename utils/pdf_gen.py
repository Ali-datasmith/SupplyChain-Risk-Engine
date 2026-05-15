import os
import logging
from datetime import datetime
from typing import Optional
import polars as pl
import streamlit as st
from fpdf import FPDF

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskReport(FPDF):
    """Custom FPDF class for Supply Chain Risk reporting."""

    def header(self) -> None:
        try:
            self.set_font("helvetica", "B", 16)
            self.cell(0, 10, "SupplyChain-Risk-Engine Report", ln=True, align="C")
            self.set_font("helvetica", "I", 10)
            self.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                      ln=True, align="C")
            self.ln(10)
        except Exception as e:
            logger.error(f"Header rendering failed: {e}")

    def footer(self) -> None:
        try:
            self.set_y(-15)
            self.set_font("helvetica", "I", 8)
            self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")
        except Exception as e:
            logger.error(f"Footer rendering failed: {e}")


def add_summary_section(pdf: FPDF, summary_text: str) -> None:
    try:
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, "Executive Summary", ln=True)
        pdf.set_font("helvetica", "", 10)
        pdf.multi_cell(0, 5, summary_text)
        pdf.ln(5)
    except Exception as e:
        logger.error(f"Error adding summary section: {e}")


def add_supplier_table(pdf: FPDF, df: pl.DataFrame) -> None:
    try:
        pdf.set_font("helvetica", "B", 11)
        pdf.cell(0, 10, "Critical Supplier Overview", ln=True)
        pdf.set_font("helvetica", "B", 9)
        pdf.set_fill_color(240, 240, 240)

        # Detect correct column names flexibly
        sup_col = next((c for c in ["supplier_name", "supplier", "vendor", "name"]
                        if c in df.columns), df.columns[0])
        region_col = next((c for c in ["region", "supplier_region", "country", "area"]
                           if c in df.columns), None)
        score_col = next((c for c in ["risk_score", "risk", "score", "rating"]
                          if c in df.columns), None)

        cols   = ["Supplier", "Region", "Risk Score"]
        widths = [80, 60, 40]

        for i, col in enumerate(cols):
            pdf.cell(widths[i], 8, col, border=1, fill=True)
        pdf.ln()

        pdf.set_font("helvetica", "", 9)
        for row in df.iter_rows(named=True):
            pdf.cell(widths[0], 7, str(row.get(sup_col, "")),    border=1)
            pdf.cell(widths[1], 7, str(row.get(region_col, "")) if region_col else "N/A", border=1)
            score = row.get(score_col, 0) if score_col else 0
            pdf.cell(widths[2], 7, f"{float(score):.2f}", border=1)
            pdf.ln()
    except Exception as e:
        logger.error(f"Error adding supplier table: {e}")


# ── FIX: '_data' prefix tells st.cache_data NOT to hash this Polars DataFrame ──
@st.cache_data(ttl=300)
def generate_report(_data: pl.DataFrame, summary: str) -> bytes:
    """Orchestrates PDF creation and returns binary content.

    Args:
        _data:   Polars DataFrame of supplier risk data.
                 Leading underscore prevents st.cache_data from trying to hash it.
        summary: Executive summary text for the report.

    Returns:
        bytes: Raw PDF binary, or empty bytes on failure.
    """
    try:
        pdf = RiskReport()
        pdf.alias_nb_pages()
        pdf.add_page()

        add_summary_section(pdf, summary)

        # Filter high-risk suppliers (score > 50)
        if "risk_score" in _data.columns:
            high_risk = _data.lazy().filter(pl.col("risk_score") > 50).collect()
        else:
            high_risk = _data

        if not high_risk.is_empty():
            add_supplier_table(pdf, high_risk)

        return bytes(pdf.output())
    except Exception as e:
        logger.error(f"Failed to generate PDF: {e}")
        return b""


if __name__ == "__main__":
    test_df = pl.DataFrame({
        "supplier":   ["Test Corp"],
        "region":     ["Global"],
        "risk_score": [75.0],
    })
    result = generate_report(test_df, "Test summary")
    print(f"Generated PDF Size: {len(result)} bytes")