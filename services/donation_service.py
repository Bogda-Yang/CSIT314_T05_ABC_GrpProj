from fastapi import HTTPException
from sqlalchemy import case, distinct, func, select
from sqlalchemy.orm import Session
from urllib.parse import urlencode

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
from core.security import ensure_aware_dt, now_dt
from services.campaign_service import (
    build_projects_url,
    humanize_campaign_category,
    normalize_donee_campaign_sort,
    serialize_campaign_detail,
    serialize_campaign_summary,
    serialize_campaign_summaries,
)


class CampaignSearchController:
    @staticmethod
    def SearchFundraisingCampaigns(
        session: Session,
        search_keywords: str,
        category: str | None = None,
        sort_order: str = DEFAULT_DONEE_CAMPAIGN_SORT,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[FundraisingCampaign]:
        return CampaignSearchController.RetrieveMatchingCampaigns(
            session,
            search_keywords,
            category=category,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def RetrieveMatchingCampaigns(
        session: Session,
        search_keywords: str,
        category: str | None = None,
        sort_order: str = DEFAULT_DONEE_CAMPAIGN_SORT,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[FundraisingCampaign]:
        return FundraisingCampaign.GetMatchingCampaigns(
            session,
            search_keywords,
            category=category,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )


class CampaignFilterController:
    @staticmethod
    def FilterCampaigns(
        session: Session,
        category: str | None = None,
        sort_order: str = DEFAULT_DONEE_CAMPAIGN_SORT,
        search_keywords: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[FundraisingCampaign]:
        return CampaignFilterController.RetrieveFilteredCampaigns(
            session,
            category=category,
            sort_order=sort_order,
            search_keywords=search_keywords,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def RetrieveFilteredCampaigns(
        session: Session,
        category: str | None = None,
        sort_order: str = DEFAULT_DONEE_CAMPAIGN_SORT,
        search_keywords: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[FundraisingCampaign]:
        return FundraisingCampaign.GetFilteredCampaigns(
            session,
            category=category,
            sort_order=sort_order,
            search_keywords=search_keywords,
            limit=limit,
            offset=offset,
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

    @staticmethod
    def GetHomeImpactOverview(session: Session) -> dict[str, object]:
        return build_home_impact_overview(session)

    @staticmethod
    def GetLatestCampaignNotes(session: Session, limit: int = 3) -> list[dict[str, object]]:
        return get_latest_campaign_notes(session, limit)


def format_compact_count(value: int) -> str:
    if value >= 1_000_000:
        compact_value = value / 1_000_000
        return f"{compact_value:.1f}M+".replace(".0M", "M")
    if value >= 1_000:
        compact_value = value / 1_000
        return f"{compact_value:.1f}K+".replace(".0K", "K")
    return str(value)


def format_duration_hours(hours: float | None) -> str:
    if hours is None:
        return "N/A"
    if hours < 1:
        return f"{max(1, round(hours * 60))} min"
    if hours < 24:
        return f"{hours:.1f} hrs".replace(".0 hrs", " hrs")
    days = hours / 24
    return f"{days:.1f} days".replace(".0 days", " days")


def calculate_average_time_to_first_donation(session: Session) -> float | None:
    first_donation_subquery = (
        select(
            DonationRecord.campaign_id,
            func.min(DonationRecord.donated_at).label("first_donated_at"),
        )
        .group_by(DonationRecord.campaign_id)
        .subquery()
    )
    rows = session.execute(
        select(FundraisingCampaign, first_donation_subquery.c.first_donated_at)
        .join(
            first_donation_subquery,
            first_donation_subquery.c.campaign_id == FundraisingCampaign.id,
        )
        .where(FundraisingCampaign.status != "deleted")
    ).all()

    durations: list[float] = []
    for campaign, first_donated_at in rows:
        baseline = campaign.published_at or campaign.created_at
        if not baseline or not first_donated_at:
            continue
        baseline_dt = ensure_aware_dt(baseline)
        first_donated_dt = ensure_aware_dt(first_donated_at)
        duration_hours = (first_donated_dt - baseline_dt).total_seconds() / 3600
        if duration_hours >= 0:
            durations.append(duration_hours)

    if not durations:
        return None
    return sum(durations) / len(durations)


def calculate_transparency_score(session: Session) -> int:
    rows = session.execute(
        select(
            FundraisingCampaign.goal_amount,
            FundraisingCampaign.description,
            FundraisingCampaign.deadline,
            func.count(CampaignImage.id).label("image_count"),
        )
        .outerjoin(CampaignImage, CampaignImage.campaign_id == FundraisingCampaign.id)
        .where(FundraisingCampaign.status == "published")
        .group_by(
            FundraisingCampaign.id,
            FundraisingCampaign.goal_amount,
            FundraisingCampaign.description,
            FundraisingCampaign.deadline,
        )
    ).all()
    if not rows:
        return 0

    complete_count = 0
    for goal_amount, description, deadline, image_count in rows:
        has_required_details = all(
            [
                goal_amount and int(goal_amount) > 0,
                (description or "").strip(),
                (deadline or "").strip(),
                int(image_count or 0) > 0,
            ]
        )
        if has_required_details:
            complete_count += 1

    return round((complete_count / len(rows)) * 100)


def build_home_impact_overview(session: Session) -> dict[str, object]:
    year_start = now_dt().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    (
        total_support,
        donation_count,
        donor_count,
        supported_campaigns_this_year,
    ) = session.execute(
        select(
            func.coalesce(func.sum(DonationRecord.amount), 0),
            func.count(DonationRecord.id),
            func.count(distinct(DonationRecord.user_id)),
            func.count(
                distinct(
                    case(
                        (
                            DonationRecord.donated_at >= year_start,
                            DonationRecord.campaign_id,
                        )
                    )
                )
            ),
        )
    ).one()
    total_support = int(total_support or 0)
    donation_count = int(donation_count or 0)
    donor_count = int(donor_count or 0)
    supported_campaigns_this_year = int(supported_campaigns_this_year or 0)
    average_first_donation_hours = calculate_average_time_to_first_donation(session)
    transparency_score = calculate_transparency_score(session)

    return {
        "total_support_label": f"${total_support:,}",
        "total_support_copy": (
            f"Calculated from {donation_count:,} donation records across simulated and real support activity."
        ),
        "campaigns_helped_label": format_compact_count(supported_campaigns_this_year),
        "campaigns_helped_copy": (
            "Distinct campaigns that received at least one donation during the current year."
        ),
        "average_first_donation_label": format_duration_hours(average_first_donation_hours),
        "average_first_donation_copy": (
            "Average time from campaign publication to its first recorded donation."
        ),
        "transparency_score_label": f"{transparency_score}/100",
        "transparency_score_copy": (
            f"Based on published campaigns with goals, descriptions, deadlines, and images. "
            f"{donor_count:,} unique donors are reflected in the ledger."
        ),
    }


def get_latest_campaign_notes(session: Session, limit: int = 3) -> list[dict[str, object]]:
    rows = DonationRecord.GetPublicDonationLedger(
        session,
        sort_order="time_desc",
        limit=limit,
    )
    notes: list[dict[str, object]] = []
    for donation_record, user_account, campaign in rows:
        donation = serialize_public_donation_ledger_item(donation_record, user_account, campaign)
        notes.append(
            {
                "time_label": donation["donated_at"],
                "donor_name": donation["donor_name"],
                "campaign_title": donation["campaign_title"],
                "amount_label": donation["amount_label"],
                "campaign_url": donation["campaign_url"],
                "description": (
                    f"{donation['donor_name']} donated {donation['amount_label']} "
                    f"to {donation['campaign_title']}."
                ),
            }
        )
    return notes


def get_comment_avatar_initials(name: str) -> str:
    parts = name.strip().split()
    if len(parts) >= 2 and all(part[:1].isascii() for part in parts[:2]):
        return f"{parts[0][0]}{parts[1][0]}".upper()
    return name.strip()[:2].upper()


def get_home_community_comments() -> list[dict[str, str]]:
    comments = [
        {
            "name": "Elon Musk",
            "comment": "I just redirected the Mars colonization budget to this platform. Earthlings first.",
            "avatar_asset": "testimonial-elon-musk",
        },
        {
            "name": "MrBeast",
            "comment": "I'm willing to fund every single project on this website!",
            "avatar_asset": "testimonial-mrbeast",
        },
        {
            "name": "Bill Gates",
            "comment": "Naked donation, no explanation.",
            "avatar_asset": "testimonial-bill-gates",
        },
        {
            "name": "Donald Trump",
            "comment": 'I\'m gonna rename this platform "Trump Donate". It’s gonna be huge, believe me!',
            "avatar_asset": "testimonial-donald-trump",
        },
        {
            "name": "Warren Buffett",
            "comment": "The best investment of my life is throwing money into this website.",
            "avatar_asset": "testimonial-warren-buffett",
        },
        {
            "name": "韩红",
            "comment": "我碰到这个网站之前简直是白捐了！",
            "avatar_asset": "testimonial-han-hong",
        },
        {
            "name": "赵启恒",
            "comment": "我超，这个网站是真nb！",
            "avatar_asset": "testimonial-zhao-qiheng",
        },
        {
            "name": "许炜彬",
            "comment": "我以前捐款是小丑，现在我是小丑他爹。",
            "avatar_asset": "testimonial-xu-weibin",
        },
        {
            "name": "Jeff Bezos",
            "comment": "I canceled the rocket and donated all the money here instead.",
            "avatar_asset": "testimonial-jeff-bezos",
        },
        {
            "name": "王思聪",
            "comment": "我投了几个亿，感觉终于找到正经花钱的地方了。",
            "avatar_asset": "testimonial-wang-sicong",
        },
        {
            "name": "Einstein",
            "comment": (
                "I have studied the universe for half my life and found that the most "
                "meaningful energy conversion is donating money to this platform."
            ),
            "avatar_asset": "testimonial-einstein",
        },
        {
            "name": "霍金",
            "comment": "My voice is synthesized, but my donations are real.",
            "avatar_asset": "testimonial-hawking",
        },
        {
            "name": "马云",
            "comment": "阿里巴巴上市前我没这么激动，现在看到这个平台我比上市还激动。",
            "avatar_asset": "testimonial-ma-yun",
        },
        {
            "name": "哈宝",
            "comment": (
                "天不生此萤火筹，筹款万古如长夜. If heaven had not birthed this website, "
                "donations would be in eternal night."
            ),
            "avatar_asset": "testimonial-habao",
        },
    ]
    heat_labels = (
        "9999+",
        "8888+",
        "7777+",
        "6666+",
        "5555+",
        "4999+",
        "4560+",
        "4218+",
        "3999+",
        "3568+",
        "3201+",
        "2888+",
        "2333+",
        "1888+",
    )
    for index, comment in enumerate(comments):
        comment["avatar_initials"] = get_comment_avatar_initials(comment["name"])
        comment["avatar_url"] = f"/assets/{comment['avatar_asset']}"
        comment["heat_label"] = heat_labels[index % len(heat_labels)]
        comment["tone_class"] = f"tone-{(index % 6) + 1}"
    return comments


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


TRANSPARENCY_DONATION_SORT_OPTIONS = (
    ("time_desc", "Newest donations"),
    ("time_asc", "Oldest donations"),
    ("amount_desc", "Highest amount"),
    ("amount_asc", "Lowest amount"),
)
TRANSPARENCY_DONATION_SORT_LABELS = dict(TRANSPARENCY_DONATION_SORT_OPTIONS)
TRANSPARENCY_DONATION_PERIOD_OPTIONS = (
    ("all", "All time"),
    ("1d", "Past day"),
    ("7d", "Past week"),
    ("30d", "Past month"),
    ("90d", "Past 3 months"),
    ("180d", "Past 6 months"),
    ("365d", "Past year"),
)
TRANSPARENCY_DONATION_PERIOD_LABELS = dict(TRANSPARENCY_DONATION_PERIOD_OPTIONS)


def normalize_transparency_donation_sort(sort_order: str | None) -> str:
    clean_sort_order = (sort_order or "time_desc").strip().lower()
    if clean_sort_order in TRANSPARENCY_DONATION_SORT_LABELS:
        return clean_sort_order
    return "time_desc"


def normalize_transparency_donation_period(date_period: str | None) -> str:
    clean_period = (date_period or "all").strip().lower()
    if clean_period in TRANSPARENCY_DONATION_PERIOD_LABELS:
        return clean_period
    return "all"


def build_transparency_url(
    selected_category: str | None = None,
    selected_sort: str | None = None,
    selected_period: str | None = None,
    anchor: str | None = "donation-ledger",
) -> str:
    query_pairs: list[tuple[str, str]] = []
    if selected_category:
        query_pairs.append(("category", selected_category))
    if selected_sort and selected_sort != "time_desc":
        query_pairs.append(("sort", selected_sort))
    if selected_period and selected_period != "all":
        query_pairs.append(("period", selected_period))

    url = "/transparency"
    if query_pairs:
        url = f"{url}?{urlencode(query_pairs)}"
    if anchor:
        url = f"{url}#{anchor}"
    return url


def get_transparency_category_filters(
    selected_category: str | None,
    selected_sort: str,
    selected_period: str,
) -> list[dict[str, object]]:
    return [
        {
            "value": option_value,
            "label": option_label,
            "is_active": (
                selected_category is None if option_value == "all" else selected_category == option_value
            ),
            "url": build_transparency_url(
                selected_category=None if option_value == "all" else option_value,
                selected_sort=selected_sort,
                selected_period=selected_period,
            ),
        }
        for option_value, option_label in CAMPAIGN_PUBLIC_FILTER_OPTIONS
    ]


def get_transparency_sort_filters(
    selected_category: str | None,
    selected_sort: str,
    selected_period: str,
) -> list[dict[str, object]]:
    return [
        {
            "value": option_value,
            "label": option_label,
            "is_active": option_value == selected_sort,
            "url": build_transparency_url(
                selected_category=selected_category,
                selected_sort=option_value,
                selected_period=selected_period,
            ),
        }
        for option_value, option_label in TRANSPARENCY_DONATION_SORT_OPTIONS
    ]


def get_transparency_period_filters(
    selected_category: str | None,
    selected_sort: str,
    selected_period: str,
) -> list[dict[str, object]]:
    return [
        {
            "value": option_value,
            "label": option_label,
            "is_active": option_value == selected_period,
            "url": build_transparency_url(
                selected_category=selected_category,
                selected_sort=selected_sort,
                selected_period=option_value,
            ),
        }
        for option_value, option_label in TRANSPARENCY_DONATION_PERIOD_OPTIONS
    ]


def serialize_public_donation_ledger_item(
    donation_record: DonationRecord,
    user_account,
    campaign,
) -> dict[str, object]:
    donated_at = ensure_aware_dt(donation_record.donated_at)
    return {
        "id": donation_record.id,
        "donor_name": user_account.username if user_account else "Unknown donor",
        "donor_email": user_account.email if user_account else "",
        "amount": int(donation_record.amount),
        "amount_label": f"${int(donation_record.amount):,}",
        "category": donation_record.campaign_category,
        "category_label": humanize_campaign_category(donation_record.campaign_category),
        "donated_at": donated_at.strftime("%Y-%m-%d %H:%M"),
        "campaign_id": donation_record.campaign_id,
        "campaign_title": campaign.title if campaign else "Removed campaign",
        "campaign_status": campaign.status if campaign else "removed",
        "campaign_url": (
            build_projects_url(campaign_id=campaign.id, anchor="published-projects")
            if campaign and campaign.status == "published"
            else None
        ),
    }


def get_public_donation_ledger(
    session: Session,
    selected_category: str | None,
    selected_sort: str,
    selected_period: str = "all",
) -> list[dict[str, object]]:
    rows = DonationRecord.GetPublicDonationLedger(
        session,
        category=selected_category,
        sort_order=selected_sort,
        date_period=selected_period,
    )
    return [
        serialize_public_donation_ledger_item(donation_record, user_account, campaign)
        for donation_record, user_account, campaign in rows
    ]


def get_transparency_summary(
    donation_ledger: list[dict[str, object]],
    selected_category: str | None,
    selected_period: str = "all",
) -> str:
    count = len(donation_ledger)
    total_amount = sum(int(record["amount"]) for record in donation_ledger)
    category_label = humanize_campaign_category(selected_category).lower()
    period_label = TRANSPARENCY_DONATION_PERIOD_LABELS.get(selected_period, "All time").lower()
    donation_label = "donation" if count == 1 else "donations"
    if selected_category:
        return (
            f"Showing {count} {category_label} {donation_label} for {period_label}, "
            f"total ${total_amount:,}."
        )
    return f"Showing {count} {donation_label} for {period_label}, total ${total_amount:,}."


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
    serialized_campaigns = serialize_campaign_summaries(session, supported_campaigns)
    for campaign, campaign_summary in zip(supported_campaigns, serialized_campaigns):
        campaign_summary["detail_url"] = build_projects_url(
            campaign_id=campaign.id,
            anchor="published-projects",
        )
    return serialized_campaigns


def get_published_campaign_summaries(
    session: Session,
    selected_category: str | None,
    search_query: str,
    selected_sort: str,
    favourite_campaign_ids: set[int] | None = None,
    limit: int | None = None,
    offset: int = 0,
) -> list[dict[str, object]]:
    clean_search_query = search_query.strip()
    favourite_campaign_ids = favourite_campaign_ids or set()

    if clean_search_query:
        campaigns = CampaignSearchController.SearchFundraisingCampaigns(
            session,
            clean_search_query,
            category=selected_category,
            sort_order=selected_sort,
            limit=limit,
            offset=offset,
        )
    else:
        campaigns = CampaignFilterController.FilterCampaigns(
            session,
            category=selected_category,
            sort_order=selected_sort,
            limit=limit,
            offset=offset,
        )

    serialized_campaigns = serialize_campaign_summaries(session, campaigns)
    for campaign_summary in serialized_campaigns:
        campaign_summary["is_favourite"] = campaign_summary["id"] in favourite_campaign_ids
    return serialized_campaigns


def get_published_campaign_count(
    session: Session,
    selected_category: str | None,
    search_query: str,
) -> int:
    return FundraisingCampaign.CountDoneeCampaigns(
        session,
        category=selected_category,
        search_keywords=search_query,
    )


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
    total_count: int | None = None,
) -> str:
    count = len(published_campaigns) if total_count is None else total_count
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
