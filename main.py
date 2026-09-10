"""
main.py — Run this to start the fee collection.

Commands:
    python main.py              # sends WhatsApp messages
    python main.py --dry-run    # previews dues, no messages sent
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime

import config
from core.data_loader     import load_members
from core.calculator      import calculate_dues
from core.message_builder import build_message, build_admin_summary
from core.reporter        import generate_report

# ── Logging: writes to both console and a log file ──────────────────────────
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

os.makedirs(config.LOGS_DIR, exist_ok=True)
LOG_FILE = os.path.join(
    config.LOGS_DIR,
    f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# ── Progress file: tracks who was already sent this month ───────────────────
PROGRESS_FILE = os.path.join(config.OUTPUT_DIR, "progress.json")


def _load_progress():
    """Returns set of phone numbers already messaged this month."""
    if not os.path.exists(PROGRESS_FILE):
        return set()
    try:
        with open(PROGRESS_FILE) as f:
            data = json.load(f)
        if data.get("month") == datetime.now().strftime("%Y-%m"):
            return set(data.get("sent", []))
    except Exception:
        pass
    return set()


def _save_progress(sent_phones):
    """Saves progress to disk after every successful send."""
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump({
            "month": datetime.now().strftime("%Y-%m"),
            "sent":  list(sent_phones)
        }, f)


def run(dry_run=False, reset=False):
    ref = datetime.now()
    logger.info(f"=== WA Fee Collector | {ref.strftime('%d %b %Y %H:%M')} ===")

    if reset and os.path.exists(PROGRESS_FILE):
        try:
            os.remove(PROGRESS_FILE)
            logger.info("Progress reset: cleared previous sent history.")
        except Exception as e:
            logger.warning(f"Could not remove progress file: {e}")

    # 1. Load member data from Excel
    df = load_members()

    # 2. Calculate dues for all members
    dues_df = calculate_dues(df, ref)
    pending = dues_df[dues_df["has_due"]].reset_index(drop=True)
    logger.info(f"Members with pending dues: {len(pending)}")

    if pending.empty:
        logger.info("No pending dues found. Nothing to send.")
        return

    # 3. Dry run — just print, no WhatsApp
    if dry_run:
        logger.info("DRY RUN — no messages will be sent.\n")
        for _, row in pending.iterrows():
            msg = build_message(
                name=row["name"],
                due_amount=row["due_amount"],
                ref=ref,
                prev_balance=row["prev_balance"],
                expected_total=row["expected_total"] - row["paid_total"]
            )
            logger.info(
                f"  {row['name']:<22} {row['phone']}  "
                f"INR {row['due_amount']:.2f}"
            )
            logger.info(f"  Preview message:\n{msg}\n")
        return

    # 4. Load progress (resume if crashed mid-run)
    already_sent  = _load_progress()
    sent_phones   = list(already_sent)
    failed_phones = []

    if already_sent:
        logger.info(
            f"Resuming — {len(already_sent)} already sent this month, skipping them."
        )

    # 5. Open WhatsApp Web and send
    from core.whatsapp_sender import WhatsAppSender

    with WhatsAppSender() as wa:
        total = len(pending)
        for i, row in pending.iterrows():
            name  = row["name"]
            phone = row["phone"]
            due   = row["due_amount"]

            # Skip if already sent this month
            if phone in already_sent:
                logger.info(f"  [SKIP] {name} — already sent this month")
                continue

            logger.info(f"[{i+1}/{total}] Sending to {name} ({phone}) — INR {due:.2f}")

            message = build_message(
                name=name,
                due_amount=due,
                ref=ref,
                prev_balance=row["prev_balance"],
                expected_total=row["expected_total"] - row["paid_total"]
            )
            ok = wa.send(
                phone=phone,
                message=message,
                qr_path=config.QR_IMAGE_PATH,
                name=name,
            )

            if ok:
                sent_phones.append(phone)
                _save_progress(sent_phones)  # save after every success
            else:
                failed_phones.append(phone)

            wa.random_delay()

        # 6. Send summary to treasurer (optional)
        if config.ADMIN_PHONE:
            failed_names = list(
                dues_df[dues_df["phone"].isin(failed_phones)]["name"]
            )
            pending_list = [
                (row["name"], row["due_amount"])
                for _, row in dues_df[dues_df["due_amount"] > 0].iterrows()
            ]
            summary = build_admin_summary(
                total=len(dues_df),
                sent=len(sent_phones),
                no_due=int((~dues_df["has_due"]).sum()),
                failed=len(failed_phones),
                total_pending=float(dues_df["due_amount"].sum()),
                failed_names=failed_names,
                pending_list=pending_list,
                ref=ref,
            )
            wa.send(
                phone=config.ADMIN_PHONE,
                message=summary,
                qr_path="",
                name="ADMIN",
            )

    # 7. Generate final report + CSV
    generate_report(dues_df, sent_phones, failed_phones, ref)
    logger.info("=== Run complete ===")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WA Fee Collector")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview dues without opening WhatsApp"
    )
    parser.add_argument(
        "--reset", action="store_true",
        help="Clear progress and reset sent tracking"
    )
    args = parser.parse_args()
    run(dry_run=args.dry_run, reset=args.reset)