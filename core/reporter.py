"""
Logs a summary table and exports a pending-members CSV after each run.
"""
import logging
import os
import sys
from datetime import datetime

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

logger = logging.getLogger(__name__)


def generate_report(dues_df, sent_phones, failed_phones, ref=None):
    ref           = ref or datetime.now()
    total         = len(dues_df)
    no_due        = int((~dues_df["has_due"]).sum())
    sent          = len(sent_phones)
    failed        = len(failed_phones)
    total_pending = float(dues_df["due_amount"].sum())
    failed_names  = list(
        dues_df[dues_df["phone"].isin(failed_phones)]["name"]
    )

    sep = "-" * 46
    for line in [
        sep,
        f"REPORT  {ref.strftime('%B %Y')}",
        sep,
        f"Total members : {total}",
        f"Sent          : {sent}",
        f"No dues       : {no_due}",
        f"Failed        : {failed}",
        f"Total pending : INR {total_pending:,.2f}",
    ]:
        logger.info(line)

    if failed_names:
        logger.info("Failed: " + ", ".join(failed_names))
    logger.info(sep)

    _export_csv(dues_df[dues_df["has_due"]], ref)

    return dict(total=total, sent=sent, no_due=no_due,
                failed=failed, total_pending=total_pending,
                failed_names=failed_names)


def _export_csv(df, ref):
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    path = os.path.join(
        config.OUTPUT_DIR,
        f"pending_{ref.strftime('%Y%m')}.csv"
    )
    cols = [c for c in [
        "name", "phone", "monthly_fee",
        "expected_total", "paid_total", "due_amount"
    ] if c in df.columns]
    df[cols].to_csv(path, index=False)
    logger.info(f"CSV exported: {path}")