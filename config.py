import os
from dotenv import load_dotenv

load_dotenv()


# --- Google Sheets ---
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Jobs")
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")  # Path to credentials file
                                                                          # OR JSON string (for GitHub Actions)

# --- Search ---
SEARCH_KEYWORDS = os.getenv("SEARCH_KEYWORDS", "python,automation,remote").split(",")

# --- Notifiers ---
# Email
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")      # Use Gmail App Password, not your real password
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")

# Slack
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def validate():
    """
    Call at startup to catch missing config early.
    Raises ValueError listing all missing variables.
    """
    required = {
        "GOOGLE_SHEET_ID": GOOGLE_SHEET_ID,
        "GOOGLE_SERVICE_ACCOUNT_JSON": GOOGLE_SERVICE_ACCOUNT_JSON,
        "SMTP_USER": SMTP_USER,
        "SMTP_PASSWORD": SMTP_PASSWORD,
        "EMAIL_RECIPIENT": EMAIL_RECIPIENT,
        "SLACK_WEBHOOK_URL": SLACK_WEBHOOK_URL,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
