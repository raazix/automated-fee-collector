# WhatsApp Fee Collector Automator

An automated Python script designed to manage club or organization fee collections. It reads a list of members from an Excel spreadsheet, calculates who owes money based on the current month, and uses an undetected Selenium WebDriver to automatically send personalized WhatsApp messages with a QR code payment image attached.

## Features
- **Dynamic Dues Breakdown**: Intelligently detects if a member has a previous year outstanding balance. If yes, it displays a complete breakdown (**Previous Year Pending**, **This Year Dues**, and **Total Outstanding**). If already paid, it displays a simplified, clean monthly dues message.
- **Automated Dues Calculation**: Reads a `members.xlsx` file and calculates outstanding balances dynamically based on the current month.
- **Preserved Multi-line Layouts**: Formats messages with elegant double-newline spacing. The automation programmatically types each line and utilizes native `Shift+Enter` keystrokes to ensure WhatsApp Web preserves line breaks in the single-image caption block without squishing text.
- **Image & Text in a Single Message**: Uses advanced DOM interception to bypass WhatsApp Web's restrictive file-upload dialogues, ensuring the QR code image and text are sent natively together as a single captioned image.
- **Anti-Bot Evasion**: Utilizes `undetected-chromedriver` to bypass WhatsApp's automated bot detection systems.
- **Failed Message Retries**: Automatically retries sending if the browser gets stuck or the network fails.
- **Automatic Summary Reports**: Exports a `.csv` log of failed sends and optionally sends a summary message to an Admin/Treasurer phone number.
- **Scheduled Runs**: Includes a `scheduler.py` script that can be run on a server to automatically fire off messages on the 1st of every month at a specific time.

## Prerequisites
- Python 3.9 or higher
- Google Chrome browser installed

## Setup & Installation

**1. Clone the repository:**
```bash
git clone https://github.com/yourusername/wa_fee_collector.git
cd wa_fee_collector
```

**2. Install required Python packages:**
```bash
pip install -r requirements.txt
```

**3. Configure your Environment Variables:**
Copy the example environment file and create your own `.env` file:
```bash
cp .env.example .env
```
Open `.env` and configure your `COUNTRY_CODE` and `ADMIN_PHONE` (the number that receives the completion report).

**4. Set up your Data & Assets:**
- **Database**: Add your members to `data/members.xlsx`. It must contain the columns: `Name`, `Phone Number`, `Monthly Fee`, and boolean columns for months (e.g., `January`, `February`).
- **QR Code**: Place your payment QR code image at `assets/qr_payment.png`.

**5. Adjust Settings (Optional):**
Open `config.py` to customize the `MESSAGE_TEMPLATE`, set delays between messages to mimic human behavior, or change the `SCHEDULE_DAY`.

## Usage

### Manual Run
To manually start the bot and send out all pending dues messages immediately:
```bash
python main.py
```
*Note: On the very first run, a Chrome window will open asking you to scan the WhatsApp Web QR code. Once scanned, the script saves the session to `.chrome_wa_profile/` so you do not need to scan it again on future runs.*

### Scheduled Auto-Run
To leave the script running in the background and have it automatically trigger on the specified day of the month (configured in `config.py`):
```bash
python scheduler.py
```

## For Developers
If you are a developer looking to understand how the WhatsApp Web File Upload Intercept was engineered, or if you want to modify the core automation engine, please refer to the [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) and the `research_scripts/` directory for detailed explanations of the code's logic.


## Disclaimer
This script is for educational purposes. Excessive or spam messaging may result in your WhatsApp account being banned by Meta. Use responsible delays between messages and only message contacts who have opted in.
