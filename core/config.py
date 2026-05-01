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

DEFAULT_DONEE_CAMPAIGN_SORT = "published_desc"
DONEE_CAMPAIGN_SORT_OPTIONS = (
    ("published_desc", "Latest published"),
    ("published_asc", "Oldest published"),
    ("goal_desc", "Goal: High to Low"),
    ("goal_asc", "Goal: Low to High"),
)
DONEE_CAMPAIGN_SORT_LABELS = dict(DONEE_CAMPAIGN_SORT_OPTIONS)

DEFAULT_FUNDRAISER_CAMPAIGN_SORT = "updated_desc"
FUNDRAISER_CAMPAIGN_SORT_OPTIONS = (
    ("updated_desc", "Updated: Desc"),
    ("updated_asc", "Updated: Asc"),
    ("views_desc", "Views: Desc"),
    ("shortlists_desc", "Shortlists: Desc"),
    ("raised_desc", "Raised: Desc"),
)
FUNDRAISER_CAMPAIGN_SORT_LABELS = dict(FUNDRAISER_CAMPAIGN_SORT_OPTIONS)

FUNDRAISER_CAMPAIGN_LIFECYCLE_OPTIONS = (
    ("all", "All"),
    ("draft", "Draft"),
    ("pending", "Pending Review"),
    ("published", "Published"),
    ("rejected", "Rejected"),
    ("completed", "Completed"),
)
FUNDRAISER_CAMPAIGN_LIFECYCLE_LABELS = dict(FUNDRAISER_CAMPAIGN_LIFECYCLE_OPTIONS)

DEFAULT_DONATION_DATE_PERIOD = "all"
DONATION_DATE_PERIOD_OPTIONS = (
    ("all", "All time"),
    ("7d", "Last 7 days"),
    ("30d", "Last 30 days"),
    ("90d", "Last 90 days"),
    ("year", "This year"),
)
DONATION_DATE_PERIOD_LABELS = dict(DONATION_DATE_PERIOD_OPTIONS)

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
LOCAL_CAMPAIGN_DATASET_ENABLED = (
    not IS_RENDER
    and os.getenv("LOCAL_CAMPAIGN_DATASET_ENABLED", "true").strip().lower()
    not in {"0", "false", "no", "off"}
)
LOCAL_CAMPAIGN_DATASET_XLSX = Path(
    os.getenv(
        "LOCAL_CAMPAIGN_DATASET_XLSX",
        str(Path.home() / "Desktop" / "模拟数据" / "Mock up data.xlsx"),
    )
).expanduser()
LOCAL_CAMPAIGN_IMAGE_DIR = Path(
    os.getenv("LOCAL_CAMPAIGN_IMAGE_DIR", str(BASE_DIR / "assets" / "images"))
).expanduser()
