from datetime import timedelta

from core.config import DEFAULT_DONATION_DATE_PERIOD
from core.security import now_dt
from models.admin import Category
from models.campaign import CampaignImage, FundraisingCampaign, RejectionRecord
from models.donation import DonationRecord
from models.user import UserAccount, UserProfile
from tests.test_data import DONATION_FILTER_RECORDS, VALID_PASSWORD


class FakeSession:
    def __init__(self):
        self.added = []
        self.deleted = []
        self.commits = 0
        self._next_id = 1

    def add(self, record):
        if hasattr(record, "id") and getattr(record, "id", None) is None:
            record.id = self._next_id
            self._next_id += 1
        self.added.append(record)

    def add_all(self, records):
        for record in records:
            self.add(record)

    def flush(self):
        return None

    def commit(self):
        self.commits += 1

    def refresh(self, _record):
        return None

    def delete(self, record):
        self.deleted.append(record)


def make_user(username="Test User", email="user@example.com", user_id=1, status="active", password=VALID_PASSWORD):
    user = UserAccount.CreateUser(username, email, password)
    user.id = user_id
    user.status = status
    return user


def make_profile(user_id):
    return UserProfile(
        user_id=user_id,
        contact_details="",
        avatar_path=None,
        gender=None,
        age=None,
        occupation=None,
        available_balance=0,
        created_at=now_dt(),
        updated_at=now_dt(),
    )


def make_campaign(data, **overrides):
    merged = {**data, **overrides}
    return FundraisingCampaign(
        id=merged["id"],
        owner_id=merged["owner_id"],
        title=merged["title"],
        category=merged["category"],
        goal_amount=merged.get("goal_amount"),
        amount_raised=merged.get("amount_raised", 0),
        view_count=0,
        description=merged.get("description", ""),
        deadline=(
            (now_dt() + timedelta(days=merged["deadline_days_from_now"])).date().isoformat()
            if merged.get("deadline_days_from_now") is not None
            else None
        ),
        workflow_stage=merged.get("workflow_stage", 0),
        status=merged.get("status", "draft"),
        created_at=now_dt(),
        updated_at=now_dt(),
        submitted_at=now_dt() if merged.get("status") == "pending" else None,
        reviewed_at=None,
        published_at=now_dt() if merged.get("status") == "published" else None,
    )


def make_image_record(campaign_id):
    return CampaignImage(
        id=1,
        campaign_id=campaign_id,
        image_path="campaigns/test-image.jpg",
        created_at=now_dt(),
    )


def patch_approval_storage(monkeypatch, campaign, *, has_image=True):
    monkeypatch.setattr(
        CampaignImage,
        "GetImageDetails",
        staticmethod(
            lambda _session, campaign_id: [make_image_record(campaign_id)]
            if has_image and campaign_id == campaign.id
            else []
        ),
    )
    monkeypatch.setattr(
        FundraisingCampaign,
        "GetCampaignById",
        staticmethod(lambda _session, campaign_id: campaign if campaign_id == campaign.id else None),
    )
    monkeypatch.setattr(
        RejectionRecord,
        "DeleteCampaignRejectionRecords",
        staticmethod(lambda _session, _campaign_id: None),
    )
    monkeypatch.setattr(
        RejectionRecord,
        "GetRejectionReason",
        staticmethod(lambda _session, _campaign_id: None),
    )


def make_donation_record(record_data):
    return DonationRecord(
        id=record_data["id"],
        user_id=record_data["user_id"],
        campaign_id=record_data["campaign_id"],
        amount=record_data["amount"],
        campaign_category=record_data["category"],
        donated_at=now_dt() - timedelta(days=record_data["days_ago"]),
    )


def filter_hardcoded_donations(_session, user_id, category=None, date_period=DEFAULT_DONATION_DATE_PERIOD):
    records = [make_donation_record(record_data) for record_data in DONATION_FILTER_RECORDS]
    records = [record for record in records if record.user_id == user_id]
    if category:
        records = [record for record in records if record.campaign_category == category]
    period_start = DonationRecord._resolve_period_start(date_period)
    if period_start:
        records = [record for record in records if record.donated_at >= period_start]
    return sorted(records, key=lambda record: (record.donated_at, record.id), reverse=True)


def make_category(name="Education", description="Education campaigns", status="active", category_id=1):
    category = Category.CreateCategory(name, description)
    category.id = category_id
    category.status = status
    return category
