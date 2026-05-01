from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel, Field

from core.config import (
    BASE_DIR,
    DEFAULT_DONEE_CAMPAIGN_SORT,
    DEFAULT_DONATION_DATE_PERIOD,
)
from core.storage import build_avatar_url
from core.db import get_session
from core.ui import templates
from models.user import UserProfile
from services.campaign_service import (
    CampaignAnalyticsController,
    build_projects_url,
    normalize_campaign_category,
    serialize_campaign_summary,
)
from services.donation_service import (
    CampaignProgressController,
    DonationFilterController,
    DonationHistoryController,
    DonationSupportController,
    FavouriteController,
    ImpactController,
    get_donation_category_filters,
    get_donation_date_filters,
    get_projects_category_filters,
    get_projects_sort_filters,
    get_published_campaign_summaries,
    get_results_summary,
    get_selected_date_period_label,
    get_selected_category_label,
    get_selected_sort_label,
    get_supported_campaign_summaries,
    normalize_projects_sort,
    serialize_donation_record,
)
from services.local_campaign_dataset import (
    get_local_campaign_summaries,
    use_local_campaign_dataset,
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


@router.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    user_context = get_template_user_context(request)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
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
def transparency_page(request: Request) -> HTMLResponse:
    if should_redirect_direct_visit_to_home(request):
        return RedirectResponse(url="/", status_code=303)

    user_context = get_template_user_context(request)
    return templates.TemplateResponse(
        request=request,
        name="placeholder.html",
        context={
            "request": request,
            "title": "Transparency",
            "description": "Transparency page content is reserved for future updates.",
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
    if should_redirect_direct_visit_to_home(request):
        return RedirectResponse(url="/", status_code=303)

    requested_category = (category or "").strip().lower()
    selected_category = None
    if requested_category and requested_category != "all":
        selected_category = normalize_campaign_category(requested_category)
    selected_sort = normalize_projects_sort(sort)
    search_query = q.strip()

    if use_local_campaign_dataset():
        favourite_campaign_ids: set[int] = set()
        try:
            with get_session() as session:
                try:
                    user = get_authenticated_user(request, session)
                except HTTPException:
                    user = None

                if user:
                    favourite_campaign_ids = FavouriteController.GetFavouriteCampaignIds(
                        session,
                        user.id,
                    )

                published_campaigns = get_local_campaign_summaries(
                    selected_category,
                    search_query,
                    selected_sort,
                    session=session,
                    favourite_campaign_ids=favourite_campaign_ids,
                )
        except Exception as error:
            print(f"Warning: unable to attach local campaigns to database records: {error}")
            published_campaigns = get_local_campaign_summaries(
                selected_category,
                search_query,
                selected_sort,
                session=None,
                favourite_campaign_ids=favourite_campaign_ids,
            )
        primary_category_filters, overflow_category_filters = get_projects_category_filters(
            selected_category,
            search_query=search_query,
            selected_sort=selected_sort,
        )
        sort_filters = get_projects_sort_filters(selected_sort)
    else:
        with get_session() as session:
            favourite_campaign_ids: set[int] = set()
            try:
                user = get_authenticated_user(request, session)
            except HTTPException:
                user = None

            if user:
                favourite_campaign_ids = FavouriteController.GetFavouriteCampaignIds(session, user.id)

            published_campaigns = get_published_campaign_summaries(
                session,
                selected_category,
                search_query,
                selected_sort,
                favourite_campaign_ids=favourite_campaign_ids,
            )
            primary_category_filters, overflow_category_filters = get_projects_category_filters(
                selected_category,
                search_query=search_query,
                selected_sort=selected_sort,
            )
            sort_filters = get_projects_sort_filters(selected_sort)

    user_context = get_template_user_context(request)
    flash_message = pop_flash_message(request)
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
                published_campaigns, selected_category, search_query
            ),
            "published_campaigns": published_campaigns,
            **user_context,
        },
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
    if should_redirect_direct_visit_to_home(request):
        return RedirectResponse(url="/", status_code=303)

    requested_category = (donation_category or "").strip().lower()
    selected_donation_category = None
    if requested_category and requested_category != "all":
        selected_donation_category = normalize_campaign_category(requested_category)
    selected_date_period = (date_period or DEFAULT_DONATION_DATE_PERIOD).strip().lower()

    with get_session() as session:
        try:
            user = get_authenticated_user(request, session)
        except HTTPException:
            return RedirectResponse(url="/auth?mode=login", status_code=303)

        profile = UserProfile.GetProfileDetails(session, user.id)
        favourite_campaigns = FavouriteController.RetrieveFavouriteCampaigns(session, user.id)
        all_donation_records = DonationHistoryController.RetrieveDonationRecords(session, user.id)
        donation_records = DonationHistoryController.RetrieveDonationRecords(
            session,
            user.id,
            category=selected_donation_category,
            date_period=selected_date_period,
        )
        serialized_donations = [
            serialize_donation_record(session, donation_record)
            for donation_record in donation_records
        ]
        supported_campaigns = get_supported_campaign_summaries(session, user.id)
        supported_fundraiser_ids = {
            campaign["owner_email"] for campaign in supported_campaigns if campaign.get("owner_email")
        }
        total_donated_amount = sum(donation.amount for donation in all_donation_records)
        serialized_favourite_campaigns = []
        for campaign in favourite_campaigns:
            favourite_summary = serialize_campaign_summary(session, campaign)
            favourite_summary["detail_url"] = build_projects_url(
                campaign_id=campaign.id,
                anchor="published-projects",
            )
            serialized_favourite_campaigns.append(favourite_summary)
        flash_message = pop_flash_message(request)

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
        FavouriteController.SaveCampaignToFavouriteList(session, user.id, campaign_id)

    set_flash_message(request, "Campaign saved to favourites.", "success")
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


@router.post("/projects/{campaign_id}/favourites/remove")
def remove_campaign_from_favourite_list(
    campaign_id: int,
    request: Request,
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
        FavouriteController.RemoveCampaignFromFavouriteList(session, user.id, campaign_id)

    set_flash_message(request, "Campaign removed from favourites.", "success")
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
    }
    file_path = allowed.get(asset_name)
    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="Asset not found.")
    return FileResponse(file_path)
