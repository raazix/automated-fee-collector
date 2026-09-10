"""
core/message_builder.py
Builds personalised message showing previous balance breakdown.
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


def _fmt(amount):
    """Format amount — show as integer if whole number."""
    return str(int(amount)) if amount == int(amount) else f"{amount:.2f}"


def build_message(name, due_amount, ref=None,
                  prev_balance=0.0, expected_total=0.0):
    ref = ref or datetime.now()

    # Current year dues only (excluding previous balance)
    current_due = round(max(0.0, expected_total), 2)

    parts = [
        "السَّلَامُ عَلَيْكُمْ وَرَحْمَةُ ٱللَّهِ وَبَرَكاتُهُ\n"
        f"Hi {name.strip().title()} \U0001f44b"
    ]

    if prev_balance > 0.0:
        breakdown = (
            f"Previous Year Pending: \u20b9{_fmt(prev_balance)}\n"
            f"This Year Dues (till {ref.strftime('%B')}): \u20b9{_fmt(current_due)}\n\n"
            f"*Total Outstanding till {ref.strftime('%B %Y')}:* \u20b9{_fmt(due_amount)}"
        )
        parts.append(breakdown)
    else:
        parts.append(f"*Your monthly SSF due till {ref.strftime('%B %Y')} is \u20b9{_fmt(due_amount)}*")

    parts.extend([
        "Please pay using the QR scanner above and send the payment screenshot once done.",
        "Thank you"
    ])

    return "\n\n".join(parts)


def build_admin_summary(total, sent, no_due, failed,
                        total_pending, failed_names, pending_list=None, ref=None):
    ref = ref or datetime.now()
    fn = ""
    if failed_names:
        fn = "\n\nFailed:\n" + "\n".join(f"  - {n}" for n in failed_names)
        
    pl = ""
    if pending_list:
        pl = "\n\nPending Members:\n" + "\n".join(f"  - {n}: \u20b9{_fmt(amt)}" for n, amt in pending_list)

    return (
        f"Fee Collection Summary - {ref.strftime('%B %Y')}\n\n"
        f"Total members : {total}\n"
        f"Sent          : {sent}\n"
        f"No dues       : {no_due}\n"
        f"Failed        : {failed}\n"
        f"Total pending : INR {total_pending:,.2f}"
        f"{fn}"
        f"{pl}"
    )