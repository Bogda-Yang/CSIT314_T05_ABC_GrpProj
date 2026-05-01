from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from urllib.parse import quote

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.config import (
    CAMPAIGN_CATEGORY_LABELS,
    LOCAL_CAMPAIGN_DATASET_ENABLED,
    LOCAL_CAMPAIGN_DATASET_XLSX,
    LOCAL_CAMPAIGN_IMAGE_DIR,
)
from models.campaign import CampaignProgress, FundraisingCampaign
from models.user import UserAccount
from scripts.import_mock_campaigns import (
    MOCK_USER_EMAIL_TEMPLATE,
    discover_campaign_images,
    read_mock_campaigns,
)


def use_local_campaign_dataset() -> bool:
    return (
        LOCAL_CAMPAIGN_DATASET_ENABLED
        and LOCAL_CAMPAIGN_DATASET_XLSX.exists()
        and LOCAL_CAMPAIGN_IMAGE_DIR.exists()
    )


def _image_url(image_path: Path) -> str:
    return f"/local-campaign-assets/{quote(image_path.name)}"


def _mock_writer_email(writer: str) -> str:
    return MOCK_USER_EMAIL_TEMPLATE.format(writer=writer.strip().lower())


def _deadline_status(deadline: str) -> str:
    return f"Runs until {deadline}" if deadline else "No deadline"


def _progress(goal_amount: int, amount_raised: int, deadline: str) -> dict[str, object]:
    progress_percentage = (
        min(100, round((amount_raised / goal_amount) * 100)) if goal_amount > 0 else 0
    )
    remaining_amount = max(goal_amount - amount_raised, 0) if goal_amount > 0 else None
    return {
        "amount_raised": amount_raised,
        "goal_amount": goal_amount,
        "progress_percentage": progress_percentage,
        "remaining_amount": remaining_amount,
        "funding_status": "Funding in progress",
        "is_completed": False,
        "deadline_status": _deadline_status(deadline),
    }


@lru_cache(maxsize=1)
def _load_local_campaign_summaries() -> tuple[dict[str, object], ...]:
    image_groups = discover_campaign_images(LOCAL_CAMPAIGN_IMAGE_DIR)
    summaries: list[dict[str, object]] = []

    for row in read_mock_campaigns(LOCAL_CAMPAIGN_DATASET_XLSX):
        image_urls = [_image_url(image_path) for image_path in image_groups.get(row.source_no, [])]
        amount_raised = 0
        category_label = CAMPAIGN_CATEGORY_LABELS.get(row.category, row.category.title())
        summaries.append(
            {
                "id": f"local-{row.source_no}",
                "source_no": row.source_no,
                "title": row.title,
                "category": row.category,
                "category_label": category_label,
                "goal_amount": row.goal_amount,
                "amount_raised": amount_raised,
                "description": row.description,
                "deadline": row.deadline,
                "published_at": row.published_at.strftime("%Y-%m-%d %H:%M"),
                "owner_username": row.writer,
                "owner_email": _mock_writer_email(row.writer),
                "image_count": len(image_urls),
                "cover_image_url": image_urls[0] if image_urls else None,
                "image_urls": image_urls,
                "is_favourite": False,
                "is_local_dataset": True,
                "actions_disabled": True,
                "progress": _progress(row.goal_amount, amount_raised, row.deadline),
            }
        )

    return tuple(summaries)


def _get_matching_persistent_campaigns(
    session: Session,
    campaigns: list[dict[str, object]],
) -> dict[tuple[str, str], FundraisingCampaign]:
    emails = {
        str(campaign["owner_email"])
        for campaign in campaigns
        if str(campaign.get("owner_email") or "").strip()
    }
    titles = {
        str(campaign["title"])
        for campaign in campaigns
        if str(campaign.get("title") or "").strip()
    }
    if not emails or not titles:
        return {}

    statement = (
        select(FundraisingCampaign, UserAccount.email)
        .join(UserAccount, FundraisingCampaign.owner_id == UserAccount.id)
        .where(
            UserAccount.email.in_(emails),
            FundraisingCampaign.title.in_(titles),
            FundraisingCampaign.status == "published",
        )
    )
    matching_campaigns: dict[tuple[str, str], FundraisingCampaign] = {}
    for persistent_campaign, owner_email in session.execute(statement).all():
        matching_campaigns[(owner_email, persistent_campaign.title)] = persistent_campaign
    return matching_campaigns


def _attach_persistent_campaign_data(
    session: Session | None,
    campaigns: list[dict[str, object]],
    favourite_campaign_ids: set[int],
) -> list[dict[str, object]]:
    if session is None:
        return campaigns

    matching_campaigns = _get_matching_persistent_campaigns(session, campaigns)
    hydrated_campaigns: list[dict[str, object]] = []
    for campaign in campaigns:
        persistent_campaign = matching_campaigns.get(
            (str(campaign.get("owner_email") or ""), str(campaign.get("title") or ""))
        )
        if persistent_campaign is None:
            hydrated_campaigns.append(campaign)
            continue

        hydrated_campaign = dict(campaign)
        hydrated_campaign["id"] = persistent_campaign.id
        hydrated_campaign["amount_raised"] = int(persistent_campaign.amount_raised or 0)
        hydrated_campaign["is_favourite"] = persistent_campaign.id in favourite_campaign_ids
        hydrated_campaign["actions_disabled"] = False
        hydrated_campaign["progress"] = CampaignProgress.GetCampaignProgress(
            session,
            persistent_campaign.id,
        )
        if persistent_campaign.published_at:
            hydrated_campaign["published_at"] = persistent_campaign.published_at.strftime(
                "%Y-%m-%d %H:%M"
            )
        hydrated_campaigns.append(hydrated_campaign)

    return hydrated_campaigns


def get_local_campaign_summaries(
    selected_category: str | None,
    search_query: str,
    selected_sort: str,
    session: Session | None = None,
    favourite_campaign_ids: set[int] | None = None,
) -> list[dict[str, object]]:
    clean_query = search_query.strip().lower()
    campaigns = list(_load_local_campaign_summaries())
    favourite_campaign_ids = favourite_campaign_ids or set()
    campaigns = _attach_persistent_campaign_data(session, campaigns, favourite_campaign_ids)

    if selected_category:
        campaigns = [
            campaign for campaign in campaigns if campaign["category"] == selected_category
        ]

    if clean_query:
        campaigns = [
            campaign
            for campaign in campaigns
            if clean_query in str(campaign["title"]).lower()
            or clean_query in str(campaign["description"]).lower()
            or clean_query in str(campaign["category_label"]).lower()
            or clean_query in str(campaign["owner_username"]).lower()
        ]

    if selected_sort == "published_asc":
        campaigns.sort(key=lambda campaign: str(campaign["published_at"]))
    elif selected_sort == "goal_desc":
        campaigns.sort(key=lambda campaign: int(campaign["goal_amount"] or 0), reverse=True)
    elif selected_sort == "goal_asc":
        campaigns.sort(key=lambda campaign: int(campaign["goal_amount"] or 0))
    else:
        campaigns.sort(key=lambda campaign: str(campaign["published_at"]), reverse=True)

    return campaigns
