"""
scheduler.py — Runs automatically on SCHEDULE_DAY each month.

Usage:
    python scheduler.py

Keep this running in the background.
On Windows: use Task Scheduler.
On Mac/Linux: use cron or screen.
"""

import logging
import time
from datetime import datetime

import schedule
import config
from main import run

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


def _job():
    if datetime.now().day == config.SCHEDULE_DAY:
        logger.info("Monthly job triggered.")
        run()
    else:
        logger.debug(f"Not day {config.SCHEDULE_DAY}. Skipping.")


schedule.every().day.at(config.SCHEDULE_TIME).do(_job)
logger.info(
    f"Scheduler running. Will execute on day {config.SCHEDULE_DAY} "
    f"at {config.SCHEDULE_TIME} each month."
)

while True:
    schedule.run_pending()
    time.sleep(60)