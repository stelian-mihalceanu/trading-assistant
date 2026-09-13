"""Exchange and popular ticker metadata for the Trading Assistant dashboard."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Exchange:
    key: str
    name: str
    country: str


EXCHANGES = {
    "NYSE": Exchange("NYSE", "New York Stock Exchange", "United States"),
    "LSE": Exchange("LSE", "London Stock Exchange", "United Kingdom"),
    "GERMANY": Exchange("GERMANY", "German Exchanges", "Germany"),
    "SPAIN": Exchange("SPAIN", "Bolsa de Madrid", "Spain"),
    "FRANCE": Exchange("FRANCE", "Euronext Paris", "France"),
}

POPULAR_TICKERS = {
    "NYSE": {
        "CrowdStrike (CRWD)": "CRWD", "Coca-Cola (KO)": "KO", "Walmart (WMT)": "WMT",
        "Visa (V)": "V", "IBM (IBM)": "IBM", "JPMorgan (JPM)": "JPM",
    },
    "LSE": {
        "AstraZeneca (AZN.L)": "AZN.L", "HSBC (HSBA.L)": "HSBA.L",
        "Shell (SHEL.L)": "SHEL.L", "Unilever (ULVR.L)": "ULVR.L",
    },
    "GERMANY": {
        "SAP (SAP.DE)": "SAP.DE", "Siemens (SIE.DE)": "SIE.DE",
        "Allianz (ALV.DE)": "ALV.DE", "Deutsche Telekom (DTE.DE)": "DTE.DE",
    },
    "SPAIN": {
        "Inditex (ITX.MC)": "ITX.MC", "Iberdrola (IBE.MC)": "IBE.MC",
        "BBVA (BBVA.MC)": "BBVA.MC", "Santander (SAN.MC)": "SAN.MC",
    },
    "FRANCE": {
        "LVMH (MC.PA)": "MC.PA", "Airbus (AIR.PA)": "AIR.PA",
        "L'Oréal (OR.PA)": "OR.PA", "TotalEnergies (TTE.PA)": "TTE.PA",
    },
}
