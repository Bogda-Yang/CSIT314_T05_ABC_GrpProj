from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.config import (
    CAMPAIGN_PUBLIC_FILTER_OPTIONS,
    DEFAULT_DONEE_CAMPAIGN_SORT,
    DEFAULT_DONATION_DATE_PERIOD,
    DONATION_DATE_PERIOD_LABELS,
    DONATION_DATE_PERIOD_OPTIONS,
    DONEE_CAMPAIGN_SORT_OPTIONS,
    PROJECTS_PRIMARY_CATEGORY_FILTER_VALUES,
)
from models.campaign import CampaignImage, CampaignProgress, FundraisingCampaign
from models.donation import DonationRecord, FavouriteCampaign
from models.user import UserProfile
from services.campaign_service import (
    build_projects_url,
    humanize_campaign_category,
    normalize_donee_campaign_sort,
    serialize_campaign_detail,
    serialize_campaign_summary,
)


class CampaignSearchController:
    @staticmethod
    def SearchFundraisingCampaigns(
        session: Session,
        search_keywords: str,
        category: str | None = None,
        sort_order: str = DEFAULT_DONEE_CAMPAIGN_SORT,
    ) -> list[FundraisingCampaign]:
        return CampaignSearchController.RetrieveMatchingCampaigns(
            session,
            search_keywords,
            category=category,
            sort_order=sort_order,
        )

    @staticmethod
    def RetrieveMatchingCampaigns(
        session: Session,
        search_keywords: str,
        category: str | None = None,
        sort_order: str = DEFAULT_DONEE_CAMPAIGN_SORT,
    ) -> list[FundraisingCampaign]:
        return FundraisingCampaign.GetMatchingCampaigns(
            session,
            search_keywords,
            category=category,
            sort_order=sort_order,
        )


class CampaignFilterController:
    @staticmethod
    def FilterCampaigns(
        session: Session,
        category: str | None = None,
        sort_order: str = DEFAULT_DONEE_CAMPAIGN_SORT,
        search_keywords: str | None = None,
    ) -> list[FundraisingCampaign]:
        return CampaignFilterController.RetrieveFilteredCampaigns(
            session,
            category=category,
            sort_order=sort_order,
            search_keywords=search_keywords,
        )

    @staticmethod
    def RetrieveFilteredCampaigns(
        session: Session,
        category: str | None = None,
        sort_order: str = DEFAULT_DONEE_CAMPAIGN_SORT,
        search_keywords: str | None = None,
    ) -> list[FundraisingCampaign]:
        return FundraisingCampaign.GetFilteredCampaigns(
            session,
            category=category,
            sort_order=sort_order,
            search_keywords=search_keywords,
        )


class CampaignDetailController:
    @staticmethod
    def RetrieveCampaignInformation(
        session: Session, campaign_id: int
    ) -> FundraisingCampaign:
        campaign = FundraisingCampaign.GetCampaignById(session, campaign_id)
        if not campaign or campaign.status != "published":
            raise HTTPException(status_code=404, detail="Campaign not found.")
        return campaign

    @staticmethod
    def GetCampaignDetails(session: Session, campaign_id: int) -> dict[str, object]:
        campaign = CampaignDetailController.RetrieveCampaignInformation(session, campaign_id)
        return serialize_campaign_detail(session, campaign)


class CampaignImageController:
    @staticmethod
    def RetrieveCampaignImages(session: Session, campaign_id: int) -> list[CampaignImage]:
        return CampaignImageController.GetCampaignImages(session, campaign_id)

    @staticmethod
    def GetCampaignImages(session: Session, campaign_id: int) -> list[CampaignImage]:
        return CampaignImage.GetCampaignImages(session, campaign_id)


class FavouriteController:
    @staticmethod
    def SaveCampaignToFavouriteList(
        session: Session, user_id: int, campaign_id: int
    ) -> FavouriteCampaign:
        campaign = CampaignDetailController.RetrieveCampaignInformation(session, campaign_id)
        return FavouriteController.AddCampaignToFavouriteList(session, user_id, campaign.id)

    @staticmethod
    def AddCampaignToFavouriteList(
        session: Session, user_id: int, campaign_id: int
    ) -> FavouriteCampaign:
        existing_record = FavouriteCampaign.GetFavouriteRecord(session, user_id, campaign_id)
        if existing_record:
            return existing_record
        favourite_record = FavouriteCampaign.AddToFavourite(user_id, campaign_id)
        FavouriteCampaign.SaveFavouriteRecord(session, favourite_record)
        session.commit()
        session.refresh(favourite_record)
        return favourite_record

    @staticmethod
    def RemoveCampaignFromFavouriteList(
        session: Session, user_id: int, campaign_id: int
    ) -> None:
        favourite_record = FavouriteCampaign.RemoveFromFavourite(session, user_id, campaign_id)
        if not favourite_record:
            raise HTTPException(status_code=404, detail="Favourite campaign not found.")
        FavouriteCampaign.DeleteFavouriteRecord(session, favourite_record)
        session.commit()

    @staticmethod
    def RetrieveFavouriteCampaigns(session: Session, user_id: int) -> list[FundraisingCampaign]:
        return FavouriteCampaign.GetFavouriteCampaigns(session, user_id)

    @staticmethod
    def GetFavouriteCampaignDetails(
        session: Session, user_id: int, campaign_id: int
    ) -> dict[str, object]:
        campaign = FavouriteCampaign.GetFavouriteCampaignById(session, user_id, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Favourite campaign not found.")
        return serialize_campaign_detail(session, campaign)

    @staticmethod
    def GetFavouriteCampaignIds(session: Session, user_id: int) -> set[int]:
        return FavouriteCampaign.GetFavouriteCampaignIds(session, user_id)


class DonationHistoryController:
    @staticmethod
    def RetrieveDonationRecords(
        session: Session,
        user_id: int,
        category: str | None = None,
        date_period: str = DEFAULT_DONATION_DATE_PERIOD,
    ) -> list[DonationRecord]:
        return DonationFilterController.RetrieveFilteredDonationRecords(
            session,
            user_id,
            category=category,
            date_period=date_period,
        )

    @staticmethod
    def GetDonationDetails(
        session: Session, user_id: int, donation_id: int
    ) -> dict[str, object]:
        donation_record = DonationRecord.GetDonationById(session, user_id, donation_id)
        if not donation_record:
            raise HTTPException(status_code=404, detail="Donation record not found.")
        campaign = FundraisingCampaign.GetCampaignById(session, donation_record.campaign_id)
        campaign_summary = serialize_campaign_summary(session, campaign) if campaign else None
        progress_data = CampaignProgress.GetFundingStatusDetails(session, donation_record.campaign_id)
        return {
            "id": donation_record.id,
            "amount": int(donation_record.amount),
            "category": donation_record.campaign_category,
            "category_label": humanize_campaign_category(donation_record.campaign_category),
            "donated_at": donation_record.donated_at.isoformat(),
            "campaign": campaign_summary,
            "progress": progress_data,
        }


class DonationFilterController:
    @staticmethod
    def FilterDonationsByCategory(
        session: Session,
        user_id: int,
        category: str | None,
        date_period: str = DEFAULT_DONATION_DATE_PERIOD,
    ) -> list[DonationRecord]:
        return DonationRecord.FilterByCategory(
            session,
            user_id,
            category,
            date_period=date_period,
        )

    @staticmethod
    def FilterDonationsByDatePeriod(
        session: Session,
        user_id: int,
        date_period: str,
        category: str | None = None,
    ) -> list[DonationRecord]:
        return DonationRecord.FilterByDatePeriod(
            session,
            user_id,
            date_period,
            category=category,
        )

    @staticmethod
    def RetrieveFilteredDonationRecords(
        session: Session,
        user_id: int,
        category: str | None = None,
        date_period: str = DEFAULT_DONATION_DATE_PERIOD,
    ) -> list[DonationRecord]:
        return DonationRecord.GetFilteredDonations(
            session,
            user_id,
            category=category,
            date_period=date_period,
        )


class CampaignProgressController:
    @staticmethod
    def RetrieveCampaignProgressData(session: Session, campaign_id: int) -> dict[str, object]:
        return CampaignProgressController.GetCampaignProgress(session, campaign_id)

    @staticmethod
    def GetCampaignProgress(session: Session, campaign_id: int) -> dict[str, object]:
        return CampaignProgress.GetFundingStatusDetails(session, campaign_id)


class DonationSupportController:
    @staticmethod
    def SupportCampaign(
        session: Session, user_id: int, campaign_id: int, amount: int
    ) -> DonationRecord:
        clean_amount = int(amount)
        if clean_amount < 1:
            raise HTTPException(status_code=400, detail="Donation amount must be at least 1.")

        campaign = CampaignDetailController.RetrieveCampaignInformation(session, campaign_id)
        if campaign.owner_id == user_id:
            raise HTTPException(status_code=400, detail="You cannot support your own campaign.")

        profile = UserProfile.GetOrCreateProfile(session, user_id)
        available_balance = int(profile.available_balance or 0)
        if available_balance < clean_amount:
            raise HTTPException(status_code=400, detail="Insufficient balance for this donation.")

        donation_record = DonationRecord.CreateDonationRecord(
            user_id,
            campaign.id,
            clean_amount,
            campaign.category,
        )
        DonationRecord.SaveDonationRecord(session, donation_record)
        UserProfile.AddAvailableBalance(session, user_id, -clean_amount)
        FundraisingCampaign.AddRaisedAmount(campaign, clean_amount)
        session.add(campaign)
        session.commit()
        session.refresh(donation_record)
        return donation_record


class ImpactController:
    @staticmethod
    def GetAvailableBalance(session: Session, user_id: int) -> int:
        profile = UserProfile.GetOrCreateProfile(session, user_id)
        return int(profile.available_balance or 0)

    @staticmethod
    def RechargeBalance(session: Session, user_id: int, amount: int) -> int:
        if amount < 1:
            raise HTTPException(status_code=400, detail="Recharge amount must be at least 1.")
        profile = UserProfile.AddAvailableBalance(session, user_id, amount)
        session.commit()
        return int(profile.available_balance or 0)


def serialize_donation_record(
    session: Session, donation_record: DonationRecord
) -> dict[str, object]:
    campaign = FundraisingCampaign.GetCampaignById(session, donation_record.campaign_id)
    progress = CampaignProgressController.GetCampaignProgress(session, donation_record.campaign_id)
    return {
        "id": donation_record.id,
        "campaign_id": donation_record.campaign_id,
        "amount": int(donation_record.amount),
        "amount_label": f"${int(donation_record.amount):,}",
        "category": donation_record.campaign_category,
        "category_label": humanize_campaign_category(donation_record.campaign_category),
        "donated_at": donation_record.donated_at.strftime("%Y-%m-%d %H:%M"),
        "campaign_title": campaign.title if campaign else "Removed campaign",
        "fundraiser_name": campaign and serialize_campaign_summary(session, campaign)["owner_username"] or "Unknown",
        "detail_url": campaign and build_projects_url(campaign_id=campaign.id, anchor="published-projects") or None,
        "progress": progress,
    }


def get_projects_category_filters(
    selected_category: str | None,
    search_query: str = "",
    selected_sort: str = DEFAULT_DONEE_CAMPAIGN_SORT,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    category_filters = [
        {
            "value": option_value,
            "label": option_label,
            "is_active": (
                selected_category is None if option_value == "all" else selected_category == option_value
            ),
            "url": build_projects_url(
                selected_category=None if option_value == "all" else option_value,
                search_query=search_query or None,
                selected_sort=selected_sort,
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


def get_projects_sort_filters(selected_sort: str) -> list[dict[str, object]]:
    return [
        {
            "value": option_value,
            "label": option_label,
            "is_active": option_value == selected_sort,
        }
        for option_value, option_label in DONEE_CAMPAIGN_SORT_OPTIONS
    ]


def get_donation_category_filters(selected_category: str | None) -> list[dict[str, object]]:
    return [
        {
            "value": option_value,
            "label": option_label,
            "is_active": (
                selected_category is None if option_value == "all" else selected_category == option_value
            ),
        }
        for option_value, option_label in CAMPAIGN_PUBLIC_FILTER_OPTIONS
    ]


def get_donation_date_filters(selected_date_period: str) -> list[dict[str, object]]:
    return [
        {
            "value": option_value,
            "label": option_label,
            "is_active": option_value == selected_date_period,
        }
        for option_value, option_label in DONATION_DATE_PERIOD_OPTIONS
    ]


def get_supported_campaign_summaries(
    session: Session, user_id: int
) -> list[dict[str, object]]:
    supported_campaigns = DonationRecord.GetSupportedCampaigns(session, user_id)
    serialized_campaigns: list[dict[str, object]] = []
    for campaign in supported_campaigns:
        campaign_summary = serialize_campaign_summary(session, campaign)
        campaign_summary["detail_url"] = build_projects_url(
            campaign_id=campaign.id,
            anchor="published-projects",
        )
        campaign_summary["progress"] = CampaignProgressController.GetCampaignProgress(
            session, campaign.id
        )
        serialized_campaigns.append(campaign_summary)
    return serialized_campaigns


def get_published_campaign_summaries(
    session: Session,
    selected_category: str | None,
    search_query: str,
    selected_sort: str,
    favourite_campaign_ids: set[int] | None = None,
) -> list[dict[str, object]]:
    clean_search_query = search_query.strip()
    favourite_campaign_ids = favourite_campaign_ids or set()

    if clean_search_query:
        campaigns = CampaignSearchController.SearchFundraisingCampaigns(
            session,
            clean_search_query,
            category=selected_category,
            sort_order=selected_sort,
        )
    else:
        campaigns = CampaignFilterController.FilterCampaigns(
            session,
            category=selected_category,
            sort_order=selected_sort,
        )

    serialized_campaigns: list[dict[str, object]] = []
    for campaign in campaigns:
        campaign_summary = serialize_campaign_summary(session, campaign)
        campaign_summary["is_favourite"] = campaign.id in favourite_campaign_ids
        campaign_summary["progress"] = CampaignProgressController.GetCampaignProgress(
            session, campaign.id
        )
        serialized_campaigns.append(campaign_summary)
    return serialized_campaigns


def get_selected_category_label(selected_category: str | None) -> str:
    return humanize_campaign_category(selected_category)


def get_selected_sort_label(selected_sort: str) -> str:
    return next(
        (option_label for option_value, option_label in DONEE_CAMPAIGN_SORT_OPTIONS if option_value == selected_sort),
        DONEE_CAMPAIGN_SORT_OPTIONS[0][1],
    )


def get_selected_date_period_label(selected_date_period: str) -> str:
    return DONATION_DATE_PERIOD_LABELS.get(selected_date_period, DONATION_DATE_PERIOD_OPTIONS[0][1])


def get_results_summary(
    published_campaigns: list[dict[str, object]],
    selected_category: str | None,
    search_query: str,
) -> str:
    count = len(published_campaigns)
    campaign_label = "campaign" if count == 1 else "campaigns"
    selected_category_label = humanize_campaign_category(selected_category).lower()
    if search_query.strip() and selected_category:
        return (
            f'Showing {count} approved {selected_category_label} {campaign_label} '
            f'matching "{search_query.strip()}".'
        )
    if search_query.strip():
        return f'Showing {count} approved {campaign_label} matching "{search_query.strip()}".'
    if selected_category:
        return f"Showing {count} approved {selected_category_label} {campaign_label}."
    return f"Showing {count} approved {campaign_label}."


def normalize_projects_sort(sort_order: str | None) -> str:
    return normalize_donee_campaign_sort(sort_order)
