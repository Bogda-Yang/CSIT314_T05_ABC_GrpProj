import os
import re
from datetime import timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
SINGAPORE_TZ = timezone(timedelta(hours=8))
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PASSWORD_MIN_LENGTH = 6
USER_AVATAR_DIR = BASE_DIR / "uploads" / "avatars"
CAMPAIGN_IMAGE_DIR = BASE_DIR / "uploads" / "campaigns"

load_dotenv(BASE_DIR / ".env")

DEFAULT_ADMIN_USERNAME = (
    os.getenv("ADMIN_USERNAME", "FireflyFund Admin").strip() or "FireflyFund Admin"
)
DEFAULT_ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@fireflyfund.com").strip().lower()
DEFAULT_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin123")

DEFAULT_CAMPAIGN_CATEGORY = "other"
CAMPAIGN_CATEGORY_OPTIONS = (
    ("education", "Education"),
    ("medical", "Medical"),
    ("family", "Family"),
    ("emergencies", "Emergencies"),
    ("animal", "Animal"),
    ("environment", "Environment"),
    ("culture", "Culture"),
    ("disaster", "Disaster"),
    ("mental_health", "Mental Health"),
    ("relief", "Relief"),
    ("community", "Community"),
    ("other", "Other"),
)
CAMPAIGN_PUBLIC_FILTER_OPTIONS = (("all", "All"),) + CAMPAIGN_CATEGORY_OPTIONS
CAMPAIGN_CATEGORY_LABELS = dict(CAMPAIGN_CATEGORY_OPTIONS)
PROJECTS_PRIMARY_CATEGORY_FILTER_VALUES = (
    "all",
    "education",
    "medical",
    "family",
    "emergencies",
    "other",
)

DEFAULT_DASHBOARD_REVIEW_SORT = "time_asc"
DASHBOARD_REVIEW_SORT_OPTIONS = (
    ("time_desc", "Time: Desc"),
    ("time_asc", "Time: Asc"),
    ("amount_desc", "Amount: Desc"),
    ("amount_asc", "Amount: Asc"),
)
DASHBOARD_REVIEW_SORT_LABELS = dict(DASHBOARD_REVIEW_SORT_OPTIONS)

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is required. Configure a Supabase Postgres connection string in .env."
    )


def infer_supabase_url(database_url: str) -> str:
    project_match = re.search(r"postgres\.([a-z0-9]+):", database_url, re.IGNORECASE)
    if not project_match:
        return ""
    return f"https://{project_match.group(1).lower()}.supabase.co"


SUPABASE_URL = (
    os.getenv("SUPABASE_URL", "").strip().rstrip("/") or infer_supabase_url(DATABASE_URL)
)
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
SUPABASE_AVATAR_BUCKET = (
    os.getenv("SUPABASE_AVATAR_BUCKET", "user-avatars").strip() or "user-avatars"
)
SUPABASE_CAMPAIGN_BUCKET = (
    os.getenv("SUPABASE_CAMPAIGN_BUCKET", "campaign-images").strip() or "campaign-images"
)
SUPABASE_STORAGE_ENABLED = bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY)
IS_RENDER = os.getenv("RENDER", "").strip().lower() == "true"
