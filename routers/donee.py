import re

from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel, Field

from core.config import (
    BASE_DIR,
    DEFAULT_DONEE_CAMPAIGN_SORT,
    DEFAULT_DONATION_DATE_PERIOD,
    PROJECTS_PAGE_SIZE,
)
from core.storage import build_avatar_url
from core.db import get_session
from core.ui import templates
from models.user import UserProfile
from services.campaign_service import (
    CampaignAnalyticsController,
    build_projects_url,
    normalize_campaign_category,
)
from services.donation_service import (
    CampaignProgressController,
    CampaignSummaryService,
    DonationRecordSerializer,
    DonationFilterController,
    DonationHistoryController,
    DonationSupportController,
    FavouriteController,
    ImpactController,
    get_donation_category_filters,
    get_donation_date_filters,
    get_projects_category_filters,
    get_projects_sort_filters,
    get_results_summary,
    get_selected_date_period_label,
    get_selected_category_label,
    get_selected_sort_label,
    get_supported_campaign_summaries,
    get_public_donation_ledger,
    get_home_community_comments,
    normalize_projects_sort,
    normalize_transparency_donation_sort,
    get_transparency_category_filters,
    get_transparency_period_filters,
    get_transparency_sort_filters,
    get_transparency_summary,
    normalize_transparency_donation_period,
)
from services.user_service import (
    get_authenticated_user,
    get_template_user_context,
    is_admin_email,
    pop_flash_message,
    set_flash_message,
    should_redirect_direct_visit_to_home,
)


router = APIRouter()


class RechargeBalancePayload(BaseModel):
    amount: int = Field(ge=1, le=100000)


def normalize_projects_request(
    category: str | None, search_query: str, sort_order: str
) -> tuple[str | None, str, str]:
    requested_category = (category or "").strip().lower()
    selected_category = None
    if requested_category and requested_category != "all":
        selected_category = normalize_campaign_category(requested_category)
    return selected_category, search_query.strip(), normalize_projects_sort(sort_order)


def clamp_projects_page_limit(limit: int) -> int:
    return min(max(limit, 1), 50)


def render_public_campaign_cards(campaigns: list[dict[str, object]]) -> str:
    card_template = templates.env.get_template("_public_campaign_card.html")
    return "\n".join(card_template.render(campaign=campaign) for campaign in campaigns)


@router.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    with get_session() as session:
        impact_overview = ImpactController.GetHomeImpactOverview(session)
        latest_campaign_notes = ImpactController.GetLatestCampaignNotes(session, limit=8)

    user_context = get_template_user_context(request)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "impact_overview": impact_overview,
            "latest_campaign_notes": latest_campaign_notes,
            "community_comments": get_home_community_comments(),
            **user_context,
        },
    )


@router.get("/about", response_class=HTMLResponse)
def about_page(request: Request) -> HTMLResponse:
    if should_redirect_direct_visit_to_home(request):
        return RedirectResponse(url="/", status_code=303)

    user_context = get_template_user_context(request)
    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context={
            "request": request,
            **user_context,
        },
    )


@router.get("/transparency", response_class=HTMLResponse)
def transparency_page(
    request: Request,
    category: str | None = Query(default=None),
    sort: str = Query(default="time_desc"),
    period: str = Query(default="all"),
) -> HTMLResponse:
    if should_redirect_direct_visit_to_home(request):
        return RedirectResponse(url="/", status_code=303)

    requested_category = (category or "").strip().lower()
    selected_category = None
    if requested_category and requested_category != "all":
        selected_category = normalize_campaign_category(requested_category)
    selected_sort = normalize_transparency_donation_sort(sort)
    selected_period = normalize_transparency_donation_period(period)

    with get_session() as session:
        donation_ledger = get_public_donation_ledger(
            session,
            selected_category,
            selected_sort,
            selected_period,
        )

    user_context = get_template_user_context(request)
    return templates.TemplateResponse(
        request=request,
        name="transparency.html",
        context={
            "request": request,
            "title": "Transparency",
            "selected_category": selected_category,
            "selected_sort": selected_sort,
            "selected_period": selected_period,
            "category_filters": get_transparency_category_filters(
                selected_category,
                selected_sort,
                selected_period,
            ),
            "sort_filters": get_transparency_sort_filters(
                selected_category,
                selected_sort,
                selected_period,
            ),
            "period_filters": get_transparency_period_filters(
                selected_category,
                selected_sort,
                selected_period,
            ),
            "donation_ledger": donation_ledger,
            "ledger_summary": get_transparency_summary(
                donation_ledger,
                selected_category,
                selected_period,
            ),
            **user_context,
        },
    )


@router.get("/projects", response_class=HTMLResponse)
def projects_page(
    request: Request,
    category: str | None = Query(default=None),
    q: str = Query(default=""),
    sort: str = Query(default=DEFAULT_DONEE_CAMPAIGN_SORT),
) -> HTMLResponse:
    return CampaignSearchPage.ViewCampaigns(request, category, q, sort)


@router.get("/api/projects")
def projects_page_batch(
    request: Request,
    category: str | None = Query(default=None),
    q: str = Query(default=""),
    sort: str = Query(default=DEFAULT_DONEE_CAMPAIGN_SORT),
    limit: int = Query(default=PROJECTS_PAGE_SIZE, ge=1),
    offset: int = Query(default=0, ge=0),
) -> JSONResponse:
    return CampaignSearchPage.LoadMoreCampaigns(
        request, category, q, sort, limit, offset
    )


@router.get("/wallet", response_class=HTMLResponse)
def wallet_page(request: Request) -> HTMLResponse:
    if should_redirect_direct_visit_to_home(request):
        return RedirectResponse(url="/", status_code=303)

    with get_session() as session:
        try:
            user = get_authenticated_user(request, session)
        except HTTPException:
            return RedirectResponse(url="/auth?mode=login", status_code=303)

        profile = UserProfile.GetProfileDetails(session, user.id)
        available_balance = ImpactController.GetAvailableBalance(session, user.id)
        flash_message = pop_flash_message(request)

    return templates.TemplateResponse(
        request=request,
        name="wallet.html",
        context={
            "request": request,
            "title": "Wallet",
            "username": user.username,
            "user_email": user.email,
            "avatar_url": build_avatar_url(profile.avatar_path) if profile else None,
            "is_admin": is_admin_email(user.email),
            "flash_message": flash_message,
            "available_balance": available_balance,
        },
    )


@router.get("/your-impact", response_class=HTMLResponse)
def your_impact_page(
    request: Request,
    donation_category: str | None = Query(default=None),
    date_period: str = Query(default=DEFAULT_DONATION_DATE_PERIOD),
) -> HTMLResponse:
    return DonationHistoryPage.ViewDonationHistory(
        request, donation_category, date_period
    )


@router.post("/api/impact/recharge")
def recharge_balance(payload: RechargeBalancePayload, request: Request) -> JSONResponse:
    with get_session() as session:
        user = get_authenticated_user(request, session)
        updated_balance = ImpactController.RechargeBalance(session, user.id, payload.amount)

    return JSONResponse(
        {
            "message": f"${payload.amount:,} has been added to your balance.",
            "balance": updated_balance,
        }
    )


@router.post("/api/projects/{campaign_id}/view")
def register_campaign_view(campaign_id: int, request: Request) -> JSONResponse:
    with get_session() as session:
        try:
            user = get_authenticated_user(request, session)
            viewer_user_id = user.id
        except HTTPException:
            viewer_user_id = None
        analytics_data = CampaignAnalyticsController.RegisterCampaignView(
            session, campaign_id, viewer_user_id
        )

    return JSONResponse(analytics_data)


@router.post("/projects/{campaign_id}/support")
def support_campaign(
    campaign_id: int,
    request: Request,
    amount: int = Form(...),
    category: str = Form(default=""),
    q: str = Form(default=""),
    sort: str = Form(default=DEFAULT_DONEE_CAMPAIGN_SORT),
    return_to: str = Form(default="projects"),
) -> RedirectResponse:
    selected_category = None
    requested_category = category.strip().lower()
    if requested_category and requested_category != "all":
        selected_category = normalize_campaign_category(requested_category)
    selected_sort = normalize_projects_sort(sort)
    search_query = q.strip()

    with get_session() as session:
        try:
            user = get_authenticated_user(request, session)
        except HTTPException:
            return RedirectResponse(url="/auth?mode=login", status_code=303)

        try:
            DonationSupportController.SupportCampaign(session, user.id, campaign_id, amount)
        except HTTPException as error:
            set_flash_message(
                request,
                error.detail if isinstance(error.detail, str) else "Unable to support campaign.",
                "error",
            )
            if return_to == "impact":
                return RedirectResponse(url="/your-impact#impact-library", status_code=303)
            return RedirectResponse(
                url=build_projects_url(
                    campaign_id=campaign_id,
                    selected_category=selected_category,
                    search_query=search_query or None,
                    selected_sort=selected_sort,
                    anchor="published-projects",
                ),
                status_code=303,
            )

    set_flash_message(request, "Campaign supported successfully.", "success")
    if return_to == "impact":
        return RedirectResponse(url="/your-impact#impact-library", status_code=303)
    return RedirectResponse(
        url=build_projects_url(
            campaign_id=campaign_id,
            selected_category=selected_category,
            search_query=search_query or None,
            selected_sort=selected_sort,
            anchor="published-projects",
        ),
        status_code=303,
    )


@router.post("/projects/{campaign_id}/favourites/save")
def save_campaign_to_favourite_list(
    campaign_id: int,
    request: Request,
    category: str = Form(default=""),
    q: str = Form(default=""),
    sort: str = Form(default=DEFAULT_DONEE_CAMPAIGN_SORT),
    return_to: str = Form(default="projects"),
) -> RedirectResponse:
    return FavouriteListPage.SaveCampaignToFavouriteList(
        campaign_id, request, category, q, sort, return_to
    )


@router.post("/projects/{campaign_id}/favourites/remove")
def remove_campaign_from_favourite_list(
    campaign_id: int,
    request: Request,
    category: str = Form(default=""),
    q: str = Form(default=""),
    sort: str = Form(default=DEFAULT_DONEE_CAMPAIGN_SORT),
    return_to: str = Form(default="projects"),
) -> RedirectResponse:
    return FavouriteListPage.RemoveCampaignFromFavouriteList(
        campaign_id, request, category, q, sort, return_to
    )


class CampaignSearchPage:
    """BCE boundary class for D1-D2 campaign search and filtering."""

    @staticmethod
    def SelectSearchCriteria(
        category: str | None,
        search_query: str,
        sort_order: str,
    ) -> tuple[str | None, str, str]:
        return normalize_projects_request(category, search_query, sort_order)

    @staticmethod
    def SearchFundraisingCampaigns(
        session,
        selected_category: str | None,
        search_query: str,
        selected_sort: str,
        favourite_campaign_ids: set[int] | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, object]]:
        return CampaignSummaryService.GetPublishedCampaignSummaries(
            session,
            selected_category,
            search_query,
            selected_sort,
            favourite_campaign_ids=favourite_campaign_ids,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def FilterCampaigns(
        session,
        selected_category: str | None,
        selected_sort: str,
        favourite_campaign_ids: set[int] | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, object]]:
        return CampaignSummaryService.GetPublishedCampaignSummaries(
            session,
            selected_category,
            "",
            selected_sort,
            favourite_campaign_ids=favourite_campaign_ids,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def ViewCampaigns(
        request: Request,
        category: str | None = None,
        q: str = "",
        sort: str = DEFAULT_DONEE_CAMPAIGN_SORT,
    ) -> HTMLResponse:
        if should_redirect_direct_visit_to_home(request):
            return RedirectResponse(url="/", status_code=303)

        selected_category, search_query, selected_sort = CampaignSearchPage.SelectSearchCriteria(
            category, q, sort
        )

        with get_session() as session:
            favourite_campaign_ids: set[int] = set()
            try:
                user = get_authenticated_user(request, session)
            except HTTPException:
                user = None

            if user:
                favourite_campaign_ids = FavouriteController.GetFavouriteCampaignIds(session, user.id)

            if search_query:
                published_campaigns = CampaignSearchPage.SearchFundraisingCampaigns(
                    session,
                    selected_category,
                    search_query,
                    selected_sort,
                    favourite_campaign_ids=favourite_campaign_ids,
                    limit=PROJECTS_PAGE_SIZE,
                    offset=0,
                )
            else:
                published_campaigns = CampaignSearchPage.FilterCampaigns(
                    session,
                    selected_category,
                    selected_sort,
                    favourite_campaign_ids=favourite_campaign_ids,
                    limit=PROJECTS_PAGE_SIZE,
                    offset=0,
                )
            published_campaigns = [
                CampaignDetailPage.ViewCampaignDetails(campaign_summary)
                for campaign_summary in published_campaigns
            ]
            project_total_count = CampaignSummaryService.GetPublishedCampaignCount(
                session, selected_category, search_query
            )
            primary_category_filters, overflow_category_filters = get_projects_category_filters(
                selected_category,
                search_query=search_query,
                selected_sort=selected_sort,
            )
            sort_filters = get_projects_sort_filters(selected_sort)

        user_context = get_template_user_context(request)
        flash_message = pop_flash_message(request)
        return CampaignSearchPage.DisplayCampaignResults(
            request,
            flash_message,
            search_query,
            selected_category,
            selected_sort,
            primary_category_filters,
            overflow_category_filters,
            sort_filters,
            published_campaigns,
            project_total_count,
            user_context,
        )

    @staticmethod
    def LoadMoreCampaigns(
        request: Request,
        category: str | None = None,
        q: str = "",
        sort: str = DEFAULT_DONEE_CAMPAIGN_SORT,
        limit: int = PROJECTS_PAGE_SIZE,
        offset: int = 0,
    ) -> JSONResponse:
        selected_category, search_query, selected_sort = CampaignSearchPage.SelectSearchCriteria(
            category, q, sort
        )
        clean_limit = clamp_projects_page_limit(limit)

        with get_session() as session:
            favourite_campaign_ids: set[int] = set()
            try:
                user = get_authenticated_user(request, session)
            except HTTPException:
                user = None

            if user:
                favourite_campaign_ids = FavouriteController.GetFavouriteCampaignIds(session, user.id)

            if search_query:
                published_campaigns = CampaignSearchPage.SearchFundraisingCampaigns(
                    session,
                    selected_category,
                    search_query,
                    selected_sort,
                    favourite_campaign_ids=favourite_campaign_ids,
                    limit=clean_limit,
                    offset=offset,
                )
            else:
                published_campaigns = CampaignSearchPage.FilterCampaigns(
                    session,
                    selected_category,
                    selected_sort,
                    favourite_campaign_ids=favourite_campaign_ids,
                    limit=clean_limit,
                    offset=offset,
                )
            published_campaigns = [
                CampaignDetailPage.ViewCampaignDetails(campaign_summary)
                for campaign_summary in published_campaigns
            ]
            project_total_count = CampaignSummaryService.GetPublishedCampaignCount(
                session, selected_category, search_query
            )

        return CampaignSearchPage.DisplayCampaignBatch(
            published_campaigns,
            selected_category,
            search_query,
            project_total_count,
            offset,
        )

    @staticmethod
    def DisplayCampaignResults(
        request: Request,
        flash_message,
        search_query: str,
        selected_category: str | None,
        selected_sort: str,
        primary_category_filters: list[dict[str, object]],
        overflow_category_filters: list[dict[str, object]],
        sort_filters: list[dict[str, object]],
        published_campaigns: list[dict[str, object]],
        project_total_count: int,
        user_context: dict[str, object],
    ) -> HTMLResponse:
        return templates.TemplateResponse(
            request=request,
            name="projects.html",
            context={
                "request": request,
                "title": "Projects",
                "flash_message": flash_message,
                "search_query": search_query,
                "selected_category": selected_category,
                "selected_category_label": get_selected_category_label(selected_category),
                "selected_sort": selected_sort,
                "selected_sort_label": get_selected_sort_label(selected_sort),
                "primary_category_filters": primary_category_filters,
                "overflow_category_filters": overflow_category_filters,
                "sort_filters": sort_filters,
                "results_summary": get_results_summary(
                    published_campaigns, selected_category, search_query, project_total_count
                ),
                "published_campaigns": published_campaigns,
                "project_page_size": PROJECTS_PAGE_SIZE,
                "project_total_count": project_total_count,
                "project_next_offset": len(published_campaigns),
                "project_has_more": len(published_campaigns) < project_total_count,
                **user_context,
            },
        )

    @staticmethod
    def DisplayCampaignBatch(
        published_campaigns: list[dict[str, object]],
        selected_category: str | None,
        search_query: str,
        project_total_count: int,
        offset: int,
    ) -> JSONResponse:
        next_offset = offset + len(published_campaigns)
        return JSONResponse(
            {
                "html": CampaignDetailPage.RenderCampaignCards(published_campaigns),
                "count": len(published_campaigns),
                "total": project_total_count,
                "next_offset": next_offset,
                "has_more": next_offset < project_total_count,
                "summary": get_results_summary(
                    published_campaigns,
                    selected_category,
                    search_query,
                    project_total_count,
                ),
            }
        )


class CampaignDetailPage:
    """BCE boundary class for D3-D4 and D11 campaign detail display."""

    @staticmethod
    def ViewCampaignDetails(campaign_summary: dict[str, object]) -> dict[str, object]:
        CampaignDetailPage.ViewCampaignImages(campaign_summary)
        CampaignDetailPage.ViewCampaignProgress(campaign_summary)
        return campaign_summary

    @staticmethod
    def ViewCampaignImages(campaign_summary: dict[str, object]) -> list[str]:
        return list(campaign_summary.get("image_urls") or [])

    @staticmethod
    def ViewCampaignProgress(campaign_summary: dict[str, object]) -> dict[str, object]:
        return dict(campaign_summary.get("progress") or {})

    @staticmethod
    def RetrieveCampaignProgressData(session, campaign_id: int) -> dict[str, object]:
        return CampaignProgressController.GetCampaignProgress(session, campaign_id)

    @staticmethod
    def RenderCampaignCards(campaigns: list[dict[str, object]]) -> str:
        detailed_campaigns = [
            CampaignDetailPage.ViewCampaignDetails(campaign) for campaign in campaigns
        ]
        return render_public_campaign_cards(detailed_campaigns)


class FavouriteListPage:
    """BCE boundary class for D5-D7 favourite-list actions."""

    @staticmethod
    def SelectFavouriteReturnLocation(
        category: str,
        q: str,
        sort: str,
    ) -> tuple[str | None, str, str]:
        selected_category = None
        requested_category = category.strip().lower()
        if requested_category and requested_category != "all":
            selected_category = normalize_campaign_category(requested_category)
        selected_sort = normalize_projects_sort(sort)
        search_query = q.strip()
        return selected_category, search_query, selected_sort

    @staticmethod
    def SaveCampaignToFavouriteList(
        campaign_id: int,
        request: Request,
        category: str = "",
        q: str = "",
        sort: str = DEFAULT_DONEE_CAMPAIGN_SORT,
        return_to: str = "projects",
    ) -> RedirectResponse:
        selected_category, search_query, selected_sort = (
            FavouriteListPage.SelectFavouriteReturnLocation(category, q, sort)
        )

        with get_session() as session:
            try:
                user = get_authenticated_user(request, session)
            except HTTPException:
                return RedirectResponse(url="/auth?mode=login", status_code=303)
            FavouriteController.SaveCampaignToFavouriteList(session, user.id, campaign_id)

        return FavouriteListPage.DisplayFavouriteSaveResult(
            request,
            campaign_id,
            selected_category,
            search_query,
            selected_sort,
            return_to,
        )

    @staticmethod
    def RemoveCampaignFromFavouriteList(
        campaign_id: int,
        request: Request,
        category: str = "",
        q: str = "",
        sort: str = DEFAULT_DONEE_CAMPAIGN_SORT,
        return_to: str = "projects",
    ) -> RedirectResponse:
        selected_category, search_query, selected_sort = (
            FavouriteListPage.SelectFavouriteReturnLocation(category, q, sort)
        )

        with get_session() as session:
            try:
                user = get_authenticated_user(request, session)
            except HTTPException:
                return RedirectResponse(url="/auth?mode=login", status_code=303)
            FavouriteController.RemoveCampaignFromFavouriteList(session, user.id, campaign_id)

        return FavouriteListPage.DisplayFavouriteRemovalResult(
            request,
            campaign_id,
            selected_category,
            search_query,
            selected_sort,
            return_to,
        )

    @staticmethod
    def ViewFavouriteCampaigns(session, user_id: int):
        return FavouriteController.RetrieveFavouriteCampaigns(session, user_id)

    @staticmethod
    def SerializeFavouriteCampaigns(session, favourite_campaigns) -> list[dict[str, object]]:
        serialized_favourite_campaigns = []
        for campaign in favourite_campaigns:
            favourite_summary = CampaignSummaryService.SerializeCampaignSummary(session, campaign)
            favourite_summary["detail_url"] = build_projects_url(
                campaign_id=campaign.id,
                anchor="published-projects",
            )
            serialized_favourite_campaigns.append(favourite_summary)
        return serialized_favourite_campaigns

    @staticmethod
    def DisplayFavouriteSaveResult(
        request: Request,
        campaign_id: int,
        selected_category: str | None,
        search_query: str,
        selected_sort: str,
        return_to: str,
    ) -> RedirectResponse:
        set_flash_message(request, "Campaign saved to favourites.", "success")
        return FavouriteListPage.RedirectAfterFavouriteChange(
            campaign_id, selected_category, search_query, selected_sort, return_to
        )

    @staticmethod
    def DisplayFavouriteRemovalResult(
        request: Request,
        campaign_id: int,
        selected_category: str | None,
        search_query: str,
        selected_sort: str,
        return_to: str,
    ) -> RedirectResponse:
        set_flash_message(request, "Campaign removed from favourites.", "success")
        return FavouriteListPage.RedirectAfterFavouriteChange(
            campaign_id, selected_category, search_query, selected_sort, return_to
        )

    @staticmethod
    def RedirectAfterFavouriteChange(
        campaign_id: int,
        selected_category: str | None,
        search_query: str,
        selected_sort: str,
        return_to: str,
    ) -> RedirectResponse:
        if return_to in {"impact", "profile"}:
            return RedirectResponse(url="/your-impact#impact-library", status_code=303)
        return RedirectResponse(
            url=build_projects_url(
                campaign_id=campaign_id,
                selected_category=selected_category,
                search_query=search_query or None,
                selected_sort=selected_sort,
                anchor="published-projects",
            ),
            status_code=303,
        )


class DonationHistoryPage:
    """BCE boundary class for D8-D10 donation-history actions."""

    @staticmethod
    def SelectDonationFilters(
        donation_category: str | None,
        date_period: str,
    ) -> tuple[str | None, str]:
        requested_category = (donation_category or "").strip().lower()
        selected_donation_category = None
        if requested_category and requested_category != "all":
            selected_donation_category = normalize_campaign_category(requested_category)
        selected_date_period = (date_period or DEFAULT_DONATION_DATE_PERIOD).strip().lower()
        return selected_donation_category, selected_date_period

    @staticmethod
    def RetrieveDonationRecords(session, user_id: int):
        return DonationHistoryController.RetrieveDonationRecords(session, user_id)

    @staticmethod
    def FilterDonationsByCategory(
        session,
        user_id: int,
        category: str,
        date_period: str,
    ):
        return DonationFilterController.RetrieveFilteredDonationRecords(
            session,
            user_id,
            category=category,
            date_period=date_period,
        )

    @staticmethod
    def FilterDonationsByDatePeriod(
        session,
        user_id: int,
        date_period: str,
        category: str | None = None,
    ):
        return DonationFilterController.RetrieveFilteredDonationRecords(
            session,
            user_id,
            category=category,
            date_period=date_period,
        )

    @staticmethod
    def ViewDonationHistory(
        request: Request,
        donation_category: str | None = None,
        date_period: str = DEFAULT_DONATION_DATE_PERIOD,
    ) -> HTMLResponse:
        if should_redirect_direct_visit_to_home(request):
            return RedirectResponse(url="/", status_code=303)

        selected_donation_category, selected_date_period = DonationHistoryPage.SelectDonationFilters(
            donation_category, date_period
        )

        with get_session() as session:
            try:
                user = get_authenticated_user(request, session)
            except HTTPException:
                return RedirectResponse(url="/auth?mode=login", status_code=303)

            profile = UserProfile.GetProfileDetails(session, user.id)
            favourite_campaigns = FavouriteListPage.ViewFavouriteCampaigns(session, user.id)
            all_donation_records = DonationHistoryPage.RetrieveDonationRecords(session, user.id)
            if selected_donation_category:
                donation_records = DonationHistoryPage.FilterDonationsByCategory(
                    session,
                    user.id,
                    selected_donation_category,
                    selected_date_period,
                )
            elif selected_date_period != DEFAULT_DONATION_DATE_PERIOD:
                donation_records = DonationHistoryPage.FilterDonationsByDatePeriod(
                    session,
                    user.id,
                    selected_date_period,
                )
            else:
                donation_records = all_donation_records
            serialized_donations = [
                DonationRecordSerializer.SerializeDonationRecord(session, donation_record)
                for donation_record in donation_records
            ]
            supported_campaigns = get_supported_campaign_summaries(session, user.id)
            supported_fundraiser_ids = {
                campaign["owner_email"] for campaign in supported_campaigns if campaign.get("owner_email")
            }
            total_donated_amount = sum(donation.amount for donation in all_donation_records)
            serialized_favourite_campaigns = FavouriteListPage.SerializeFavouriteCampaigns(
                session, favourite_campaigns
            )
            flash_message = pop_flash_message(request)

        return DonationHistoryPage.DisplayDonationHistory(
            request,
            user,
            profile,
            flash_message,
            total_donated_amount,
            supported_fundraiser_ids,
            all_donation_records,
            selected_donation_category,
            selected_date_period,
            serialized_donations,
            supported_campaigns,
            serialized_favourite_campaigns,
        )

    @staticmethod
    def DisplayDonationHistory(
        request: Request,
        user,
        profile,
        flash_message,
        total_donated_amount: int,
        supported_fundraiser_ids: set[str],
        all_donation_records,
        selected_donation_category: str | None,
        selected_date_period: str,
        serialized_donations: list[dict[str, object]],
        supported_campaigns: list[dict[str, object]],
        serialized_favourite_campaigns: list[dict[str, object]],
    ) -> HTMLResponse:
        return templates.TemplateResponse(
            request=request,
            name="your_impact.html",
            context={
                "request": request,
                "title": "Your Impact",
                "username": user.username,
                "user_email": user.email,
                "avatar_url": build_avatar_url(profile.avatar_path) if profile else None,
                "is_admin": is_admin_email(user.email),
                "flash_message": flash_message,
                "impact_summary": {
                    "total_amount": total_donated_amount,
                    "fundraisers_supported": len(supported_fundraiser_ids),
                    "people_inspired": len(all_donation_records),
                },
                "selected_donation_category": selected_donation_category,
                "selected_date_period": selected_date_period,
                "donation_category_filters": get_donation_category_filters(selected_donation_category),
                "donation_date_filters": get_donation_date_filters(selected_date_period),
                "selected_date_period_label": get_selected_date_period_label(selected_date_period),
                "donation_history": serialized_donations,
                "supported_campaigns": supported_campaigns,
                "favourite_campaigns": serialized_favourite_campaigns,
            },
        )


@router.get("/assets/{asset_name}")
def asset(asset_name: str) -> FileResponse:
    image_dir = BASE_DIR / "assets" / "images"
    allowed = {
        "logo": image_dir / "logo0.jpg",
        "login": image_dir / "login.jpg",
        "about": image_dir / "aboutus.jpg",
        "qidao": image_dir / "qidao.jpg",
        "qidao1": image_dir / "qidao1.jpg",
        "gtq": image_dir / "gtq.jpg",
        "br": image_dir / "br.jpg",
        "dz": image_dir / "dz.jpg",
        "yyh": image_dir / "yyh.jpg",
        "yyh1": image_dir / "yyh1.jpg",
        "sgy": image_dir / "sgy.jpg",
        "xhy": image_dir / "xhy.jpg",
        "xwb": image_dir / "xwb.jpg",
        "zqh": image_dir / "zqh.jpg",
        "zqh1": image_dir / "zqh1.jpg",
        "paynow": image_dir / "Paynow.jpg",
        "pawnow": image_dir / "Paynow.jpg",
        "testimonial-elon-musk": image_dir / "Elon Musk.png",
        "testimonial-mrbeast": image_dir / "MrBeast.png",
        "testimonial-bill-gates": image_dir / "Bill Gates.png",
        "testimonial-donald-trump": image_dir / "Donald Trump.png",
        "testimonial-warren-buffett": image_dir / "Warren Buffett.png",
        "testimonial-han-hong": image_dir / "韩红.png",
        "testimonial-zhao-qiheng": image_dir / "赵启恒.jpg",
        "testimonial-xu-weibin": image_dir / "许炜彬.png",
        "testimonial-jeff-bezos": image_dir / "Jeff Bezos.png",
        "testimonial-wang-sicong": image_dir / "王思聪.png",
        "testimonial-einstein": image_dir / "Einstein.png",
        "testimonial-hawking": image_dir / "霍金.png",
        "testimonial-ma-yun": image_dir / "马云.png",
        "testimonial-habao": image_dir / "哈宝.jpg",
    }
    file_path = allowed.get(asset_name)
    if file_path is None and re.fullmatch(r"\d+(?:[.-]\d+)?\.(?:jpe?g|png|webp)", asset_name, re.IGNORECASE):
        file_path = image_dir / asset_name
    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="Asset not found.")
    return FileResponse(file_path)
