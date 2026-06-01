"""
core/calculator.py

Due = Previous Balance + (Monthly Fee x active months) - Paid this year
"""

import logging
import os
import sys
from datetime import datetime

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

logger = logging.getLogger(__name__)


def get_active_months(ref=None):
    ref = ref or datetime.now()
    return config.MONTH_COLUMNS[:ref.month]


def calculate_dues(df, ref=None):
    ref    = ref or datetime.now()
    active = get_active_months(ref)
    n      = len(active)

    # Check if Previous Balance column exists
    has_prev = (
        hasattr(config, "COL_PREV_BALANCE")
        and config.COL_PREV_BALANCE in df.columns
    )

    if has_prev:
        logger.info("Previous Balance column detected — included in dues.")
    else:
        logger.info("No Previous Balance column — current year only.")

    rows = []
    for _, row in df.iterrows():
        fee      = float(row[config.COL_MONTHLY_FEE])
        expected = fee * n
        paid     = sum(float(row[m]) for m in active)

        # Get previous year balance
        prev = 0.0
        if has_prev:
            try:
                prev = float(row[config.COL_PREV_BALANCE])
            except (ValueError, TypeError):
                prev = 0.0

        # Total due includes last year pending
        due = round(max(0.0, prev + expected - paid), 2)

        rows.append({
            "name":           row[config.COL_NAME],
            "phone":          row[config.COL_PHONE],
            "monthly_fee":    fee,
            "prev_balance":   round(prev, 2),
            "active_months":  n,
            "expected_total": round(expected, 2),
            "paid_total":     round(paid, 2),
            "due_amount":     due,
            "has_due":        due > 0,
        })

    result = pd.DataFrame(rows)
    logger.info(
        f"Dues calculated | {result['has_due'].sum()} pending | "
        f"Total: INR {result['due_amount'].sum():,.2f}"
    )
    return result


def get_pending_members(df, ref=None):
    return calculate_dues(df, ref)[lambda d: d["has_due"]].reset_index(drop=True)