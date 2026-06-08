import json
import gspread
from google.oauth2.service_account import Credentials
from scrapers.base import JobListing
import config


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def _get_client() -> gspread.Client:
    """
    Authenticate with Google Sheets API.
    Supports two modes:
      - Local dev: GOOGLE_SERVICE_ACCOUNT_JSON is a file path
      - GitHub Actions: GOOGLE_SERVICE_ACCOUNT_JSON is a JSON string (stored as a secret)
    """
    cred_value = config.GOOGLE_SERVICE_ACCOUNT_JSON

    try:
        # Try parsing as JSON string first (GitHub Actions mode)
        cred_info = json.loads(cred_value)
        credentials = Credentials.from_service_account_info(cred_info, scopes=SCOPES)
    except (json.JSONDecodeError, TypeError):
        # Fall back to treating it as a file path (local dev mode)
        credentials = Credentials.from_service_account_file(cred_value, scopes=SCOPES)

    return gspread.authorize(credentials)


def get_sheet() -> gspread.Worksheet:
    """Open the target worksheet, creating headers if it's empty."""
    client = _get_client()
    spreadsheet = client.open_by_key(config.GOOGLE_SHEET_ID)

    try:
        sheet = spreadsheet.worksheet(config.GOOGLE_SHEET_NAME)
    except gspread.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(
            title=config.GOOGLE_SHEET_NAME, rows=1000, cols=20
        )

    # Add headers if sheet is empty
    if not sheet.get_all_values():
        sheet.append_row(JobListing.headers())

    return sheet


def get_existing_urls(sheet: gspread.Worksheet) -> set[str]:
    """
    Return all job URLs already in the sheet.
    Used by the deduplicator to skip already-seen jobs.
    """
    records = sheet.get_all_records()
    return {row["URL"] for row in records if row.get("URL")}


def append_jobs(sheet: gspread.Worksheet, jobs: list[JobListing]) -> int:
    """
    Append new job rows to the sheet.
    Returns the number of rows inserted.
    """
    if not jobs:
        return 0

    rows = [job.to_row() for job in jobs]

    # Batch insert — one API call instead of one per row
    sheet.append_rows(rows, value_input_option="USER_ENTERED")

    print(f"[Sheets] Inserted {len(rows)} new jobs.")
    return len(rows)
