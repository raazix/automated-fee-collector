"""
Reads member data from Excel and returns a clean DataFrame.
"""
import logging
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

logger = logging.getLogger(__name__)


def load_members():
    logger.info(f"Loading: {config.EXCEL_PATH}")
    df = pd.read_excel(
        config.EXCEL_PATH,
        sheet_name=config.SHEET_NAME,
        dtype=str
    )
    return _clean(df)


def _clean(df):
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    # Check required columns exist
    required = [config.COL_NAME, config.COL_PHONE, config.COL_MONTHLY_FEE]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in Excel: {missing}\nFound: {list(df.columns)}")

    missing_months = [m for m in config.MONTH_COLUMNS if m not in df.columns]
    if missing_months:
        raise ValueError(f"Missing month columns: {missing_months}")

    # Clean string columns
    for col in [config.COL_NAME, config.COL_PHONE]:
        df[col] = df[col].astype(str).str.strip()

    # Convert to numbers
    df[config.COL_MONTHLY_FEE] = pd.to_numeric(
        df[config.COL_MONTHLY_FEE], errors="coerce"
    ).fillna(0)
    for m in config.MONTH_COLUMNS:
        df[m] = pd.to_numeric(df[m], errors="coerce").fillna(0)

    # Drop rows with no name or phone
    df = df[df[config.COL_NAME].str.len() > 0]
    df = df[df[config.COL_PHONE].str.len() > 0]

    # Normalise phone numbers
    df[config.COL_PHONE] = df[config.COL_PHONE].apply(_normalise)

    logger.info(f"Loaded {len(df)} members.")
    return df.reset_index(drop=True)


def _normalise(raw):
    """Strip non-digits, prepend country code if needed."""
    clean = "".join(c for c in str(raw) if c.isdigit())
    code  = config.COUNTRY_CODE.lstrip("+")
    if not clean:
        return ""
    if clean.startswith(code) and len(clean) > len(code) + 5:
        return clean
    if len(clean) == 10:
        return code + clean
    return clean