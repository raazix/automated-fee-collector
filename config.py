import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH      = os.path.join(BASE_DIR, "data", "members.xlsx")
QR_IMAGE_PATH   = os.path.join(BASE_DIR, "assets", "qr_payment.png")
LOGS_DIR        = os.path.join(BASE_DIR, "logs")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
OUTPUT_DIR      = os.path.join(BASE_DIR, "output")

SHEET_NAME      = "Sheet1"
COL_NAME        = "Name"
COL_PHONE       = "Phone Number"
COL_MONTHLY_FEE = "Monthly Fee"
COL_PREV_BALANCE = "Previous Balance"
MONTH_COLUMNS   = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]

# Google Sheets Integration
GOOGLE_SHEET_URL = os.environ.get("GOOGLE_SHEET_URL", "")
GOOGLE_CREDENTIALS_PATH = os.environ.get("GOOGLE_CREDENTIALS_PATH", "credentials.json")
COL_LAST_REMINDER = "Last Reminder Sent"

# Change to your country code — India is 91
COUNTRY_CODE    = os.environ.get("COUNTRY_CODE", "91")

# Seconds to wait between messages (keeps it human-looking)
SEND_DELAY_MIN  = 2
SEND_DELAY_MAX  = 4

# Seconds to wait for WhatsApp Web to load
WA_LOAD_TIMEOUT = 60

# How many times to retry a failed message
MAX_RETRIES     = 2

# Treasurer's number — gets a summary after all sends
# Leave as "" to skip
ADMIN_PHONE     = os.environ.get("ADMIN_PHONE", "")

# Message sent to each member
# {name}, {month}, {due} are replaced automatically
MESSAGE_TEMPLATE = (
    "السَّلَامُ عَلَيْكُمْ وَرَحْمَةُ ٱللَّهِ وَبَرَكاتُهُ"
    "Hi {name} \U0001f44b\n\n"
    "Your total monthly SSF due till *{month}* is *\u20b9{due}*.\n\n"
    "Please pay using the QR scanner above and send the "
    "payment screenshot once done.\n\n"
    "Thank you"
)

SCHEDULE_DAY  = 1       # day of month to auto-run
SCHEDULE_TIME = "09:00" # 24h format