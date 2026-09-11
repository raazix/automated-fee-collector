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

import gspread
from google.oauth2.service_account import Credentials

def load_members():
    if config.GOOGLE_SHEET_URL:
        logger.info(f"Loading from Google Sheet: {config.GOOGLE_SHEET_URL}")
        try:
            # Set up the credentials
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = Credentials.from_service_account_file(config.GOOGLE_CREDENTIALS_PATH, scopes=scopes)
            client = gspread.authorize(creds)
            
            # Open the sheet
            sheet = client.open_by_url(config.GOOGLE_SHEET_URL).worksheet(config.SHEET_NAME)
            
            # Get all records
            data = sheet.get_all_records(value_render_option='UNFORMATTED_VALUE')
            df = pd.DataFrame(data)
            
            # Convert all to string for consistent cleaning
            df = df.astype(str)
            return _clean(df)
        except Exception as e:
            logger.error(f"Failed to load from Google Sheets: {e}")
            logger.info("Falling back to local Excel file...")
    
    logger.info(f"Loading: {config.EXCEL_PATH}")
    df = pd.read_excel(
        config.EXCEL_PATH,
        sheet_name=config.SHEET_NAME,
        dtype=str
    )
    return _clean(df)


def update_gsheet_status(phone, current_month):
    """Updates the Last Reminder Sent column in Google Sheets for a specific phone number."""
    if not config.GOOGLE_SHEET_URL:
        return False
        
    try:
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = Credentials.from_service_account_file(config.GOOGLE_CREDENTIALS_PATH, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_url(config.GOOGLE_SHEET_URL).worksheet(config.SHEET_NAME)
        
        # Find the row with the matching phone number
        # We fetch all values to find the row index
        records = sheet.get_all_records()
        row_idx = None
        for i, row in enumerate(records):
            raw_phone = str(row.get(config.COL_PHONE, ""))
            if _normalise(raw_phone) == phone:
                row_idx = i + 2  # +2 because records are 0-indexed but sheet is 1-indexed and has header
                break
                
        if row_idx is None:
            logger.warning(f"Could not find phone {phone} in Google Sheet to update status.")
            return False
            
        # Find the column index for Last Reminder Sent
        header = sheet.row_values(1)
        if config.COL_LAST_REMINDER not in header:
            # Add the column if it doesn't exist
            col_idx = len(header) + 1
            sheet.update_cell(1, col_idx, config.COL_LAST_REMINDER)
        else:
            col_idx = header.index(config.COL_LAST_REMINDER) + 1
            
        # Update the cell
        sheet.update_cell(row_idx, col_idx, current_month)
        return True
    except Exception as e:
        logger.error(f"Failed to update Google Sheet status: {e}")
        return False


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

    # Convert to numbers (but preserve 'NA' for months)
    df[config.COL_MONTHLY_FEE] = pd.to_numeric(
        df[config.COL_MONTHLY_FEE], errors="coerce"
    ).fillna(0)
    
    for m in config.MONTH_COLUMNS:
        # Strip and convert to uppercase to easily check for NA
        df[m] = df[m].astype(str).str.strip().str.upper()
        # Create a mask for values that are NOT explicitly NA
        # We handle NaN strings (pandas representation of empty) as well
        not_na_mask = ~df[m].isin(['NA', 'N/A', '-', 'NOT APPLICABLE'])
        
        # Coerce only the cells that are not NA
        # Empty strings or spaces will become NaN, which we fill with 0
        df.loc[not_na_mask, m] = pd.to_numeric(df.loc[not_na_mask, m], errors="coerce").fillna(0)
        
        # The 'NA' strings remain as 'NA' in the DataFrame

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