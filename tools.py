"""Stock research tools for Human-in-the-Loop demos.

These tools are stubs that simulate pulling revenue growth data from
different sources. Replace the return values with real integrations as
needed (finance API, SQL, document retrieval, etc.).
"""

from langchain_core.tools import tool


@tool
def yahoo_finance_revenue_growth(ticker: str) -> str:
    """Fetch revenue growth from Yahoo Finance for the given ticker."""

    return f"Internal DB (simulated): Revenue growth for {ticker} is +11.5% YoY."


@tool
def internal_db_revenue_growth(ticker: str) -> str:
    """Fetch revenue growth from the internal financial warehouse."""
    # Replace with your SQL/warehouse logic
    return f"Internal DB (simulated): Revenue growth for {ticker} is +9.8% YoY."


@tool
def analyst_pdf_revenue_growth(ticker: str) -> str:
    """Summarize revenue growth from the latest analyst PDF."""
    # Replace with document parsing / RAG over analyst reports
    return (
        f"""Analyst PDF (simulated): Consensus notes Tata Motors revenue growth at +10.5% YoY.
        Commentary: demand recovery, margin expansion from product mix."""
    )


TOOLS = [
    yahoo_finance_revenue_growth,
    internal_db_revenue_growth,
    analyst_pdf_revenue_growth,
]


# --- Helpers ---

def _fallback_revenue_growth(ticker: str, reason: str) -> str:
    """Return a cached/static value when live Yahoo Finance fetch fails."""
    # Minimal offline cache; extend as needed.
    cache = {
        "TATAMOTORS.NS": "+10.5% YoY (cached sample)",
        "TCS.NS": "+7.9% YoY (cached sample)",
        "RELIANCE.NS": "+6.1% YoY (cached sample)",
    }
    val = cache.get(ticker.upper())
    if val:
        return f"Fallback revenue growth for {ticker}: {val}. (Reason: {reason})"
    return (
        f"Could not fetch Yahoo Finance revenue for {ticker}. Reason: {reason}. "
        "You can add a cached value in _fallback_revenue_growth or install yfinance."
    )
