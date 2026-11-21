import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    load_dotenv()

# Media directories
MEDIA_DIR = BASE_DIR / "generated_media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

# Retention policy (keep files for 48 hours / 2 days)
RETENTION_HOURS = int(os.getenv("RETENTION_HOURS", "48"))

# API Keys & Meta Credentials (auto-stripped to prevent newline/whitespace errors)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
META_PAGE_ACCESS_TOKEN = os.getenv("META_PAGE_ACCESS_TOKEN", "").strip()
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "").strip()
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "").strip()
THREADS_USER_ID = os.getenv("THREADS_USER_ID", "").strip()
THREADS_ACCESS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN", "").strip()
THREADS_APP_ID = os.getenv("THREADS_APP_ID", "").strip()
THREADS_APP_SECRET = os.getenv("THREADS_APP_SECRET", "").strip()

# Engagement Polling
COMMENT_CHECK_INTERVAL_MINUTES = int(os.getenv("COMMENT_CHECK_INTERVAL_MINUTES", "15"))

# Known By Digital Brand Kit
BRAND = {
    "name": "Known By Digital",
    "handle": "@knownbydigital",
    "website": "https://knownbydigital.com",
    "email": "hello@knownbydigital.com",
    "tagline": "Your Brand. Ready for the age of AI.",
    "primary_dark": (10, 10, 10),      # #0A0A0A
    "card_dark": (23, 23, 23),         # #171717
    "accent_orange": (249, 115, 22),   # #F97316
    "accent_orange_dark": (234, 88, 12), # #EA580C
    "text_white": (255, 255, 255),     # #FFFFFF
    "text_muted": (163, 163, 163),     # #A3A3A3
    "cta_triggers": ["SCALE", "AUDIT", "GROWTH", "SYSTEM", "AI"],
    "target_niches": [
        "Shopify & E-commerce Brands",
        "B2B SaaS & Tech Startups",
        "High-Ticket US Local Service Businesses"
    ]
}
