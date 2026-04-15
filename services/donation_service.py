from sqlalchemy.orm import Session

from core.config import (
    CAMPAIGN_PUBLIC_FILTER_OPTIONS,
    PROJECTS_PRIMARY_CATEGORY_FILTER_VALUES,
)
from models.campaign import FundraisingCampaign
from services.campaign_service import (
    build_projects_url,
    humanize_campaign_category,
    serialize_campaign_summary,
)


def get_projects_category_filters(selected_category: str | None) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    category_filters = [
        {
            "value": option_value,
            "label": option_label,
            "is_active": (
                selected_category is None if option_value == "all" else selected_category == option_value
            ),
            "url": build_projects_url(
                selected_category=None if option_value == "all" else option_value,
                anchor="published-projects",
            ),
        }
        for option_value, option_label in CAMPAIGN_PUBLIC_FILTER_OPTIONS
    ]
    primary_category_filters = [
        category_filter
        for category_filter in category_filters
        if category_filter["value"] in PROJECTS_PRIMARY_CATEGORY_FILTER_VALUES
    ]
    overflow_category_filters = [
        category_filter
        for category_filter in category_filters
        if category_filter["value"] not in PROJECTS_PRIMARY_CATEGORY_FILTER_VALUES
    ]
    return primary_category_filters, overflow_category_filters


def get_published_campaign_summaries(
    session: Session, selected_category: str | None
) -> list[dict[str, object]]:
    return [
        serialize_campaign_summary(session, campaign)
        for campaign in FundraisingCampaign.GetPublishedCampaigns(session, selected_category)
    ]


def get_selected_category_label(selected_category: str | None) -> str:
    return humanize_campaign_category(selected_category)
