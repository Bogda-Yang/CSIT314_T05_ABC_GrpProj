from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from core.db import get_session
from core.storage import build_avatar_url
from core.ui import templates
from models.campaign import FundraisingCampaign
from models.user import UserProfile
from services.campaign_service import (
    CAMPAIGN_PUBLIC_FILTER_OPTIONS,
    DASHBOARD_REVIEW_SORT_OPTIONS,
    CampaignApprovalController,
    CampaignRejectionController,
    build_dashboard_url,
    ensure_admin_user,
    normalize_campaign_category,
    normalize_dashboard_review_sort,
    redirect_with_dashboard_flash,
    serialize_campaign_detail,
    serialize_campaign_summary,
)
from services.user_service import get_authenticated_user, pop_flash_message
from services.user_service import should_redirect_direct_visit_to_home


router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(
    request: Request,
    category: str | None = Query(default=None),
    sort: str = Query(default="time_asc"),
    review_campaign_id: int | None = Query(default=None, ge=1),
    modal: str | None = Query(default=None),
) -> HTMLResponse:
    if should_redirect_direct_visit_to_home(request):
        return RedirectResponse(url="/", status_code=303)

    with get_session() as session:
        try:
            user = get_authenticated_user(request, session)
        except HTTPException:
            return RedirectResponse(url="/auth?mode=login", status_code=303)

        try:
            ensure_admin_user(user)
        except HTTPException:
            return RedirectResponse(url="/", status_code=303)

        user_profile = UserProfile.GetProfileDetails(session, user.id)
        requested_category = (category or "").strip().lower()
        selected_category = None
        if requested_category and requested_category != "all":
            selected_category = normalize_campaign_category(requested_category)
        selected_sort = normalize_dashboard_review_sort(sort)
        pending_campaigns = CampaignApprovalController.GetPendingCampaigns(
            session,
            category=selected_category,
            sort_order=selected_sort,
        )
        status_counts = FundraisingCampaign.GetStatusCounts(session)
        selected_review_campaign = None
        if review_campaign_id is not None:
            selected_review_campaign = next(
                (campaign for campaign in pending_campaigns if campaign.id == review_campaign_id),
                None,
            )

        flash_message = pop_flash_message(request)
        serialized_pending_campaigns = []
        for campaign in pending_campaigns:
            campaign_summary = serialize_campaign_summary(session, campaign)
            campaign_summary["review_url"] = build_dashboard_url(
                review_campaign_id=campaign.id,
                selected_category=selected_category,
                selected_sort=selected_sort,
                modal="details",
                anchor="admin-review",
            )
            serialized_pending_campaigns.append(campaign_summary)
        selected_review_campaign_data = (
            serialize_campaign_detail(session, selected_review_campaign)
            if selected_review_campaign
            else None
        )
        if selected_review_campaign_data is not None:
            selected_review_campaign_data["close_review_url"] = build_dashboard_url(
                review_campaign_id=selected_review_campaign.id,
                selected_category=selected_category,
                selected_sort=selected_sort,
                anchor="admin-review",
            )
        review_modal_open = modal == "details" and selected_review_campaign_data is not None
        pending_count = status_counts.get("pending", 0)
        approved_count = status_counts.get("approved", 0) + status_counts.get("published", 0)
        rejected_count = status_counts.get("rejected", 0)
        processed_count = approved_count + rejected_count
        review_category_filters = [
            {
                "value": option_value,
                "label": option_label,
                "is_active": (
                    selected_category is None
                    if option_value == "all"
                    else selected_category == option_value
                ),
            }
            for option_value, option_label in CAMPAIGN_PUBLIC_FILTER_OPTIONS
        ]
        review_sort_filters = [
            {
                "value": option_value,
                "label": option_label,
                "is_active": selected_sort == option_value,
            }
            for option_value, option_label in DASHBOARD_REVIEW_SORT_OPTIONS
        ]

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "title": "Dashboard",
            "user_email": user.email,
            "username": user.username,
            "avatar_url": build_avatar_url(user_profile.avatar_path) if user_profile else None,
            "is_admin": True,
            "flash_message": flash_message,
            "pending_campaigns": serialized_pending_campaigns,
            "selected_review_campaign": selected_review_campaign_data,
            "review_modal_open": review_modal_open,
            "pending_count": pending_count,
            "processed_count": processed_count,
            "approved_count": approved_count,
            "rejected_count": rejected_count,
            "review_selected_category": selected_category,
            "review_selected_sort": selected_sort,
            "review_category_filters": review_category_filters,
            "review_sort_filters": review_sort_filters,
        },
    )


@router.post("/projects/review/{campaign_id}/approve")
def approve_campaign(
    campaign_id: int,
    request: Request,
    category: str = Form("all"),
    sort: str = Form("time_asc"),
) -> RedirectResponse:
    selected_category = None
    requested_category = (category or "").strip().lower()
    if requested_category and requested_category != "all":
        try:
            selected_category = normalize_campaign_category(requested_category)
        except HTTPException:
            selected_category = None
    selected_sort = normalize_dashboard_review_sort(sort)
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            ensure_admin_user(user)
            campaign = CampaignApprovalController.ValidateCampaign(session, campaign_id)
            CampaignApprovalController.ApproveCampaign(session, campaign)
    except HTTPException as error:
        detail = getattr(error, "detail", "Unable to approve campaign.")
        return redirect_with_dashboard_flash(
            request,
            detail if isinstance(detail, str) else "Unable to approve campaign.",
            "error",
            review_campaign_id=campaign_id,
            selected_category=selected_category,
            selected_sort=selected_sort,
            anchor="admin-review",
        )

    return redirect_with_dashboard_flash(
        request,
        "Campaign approved and published successfully.",
        "success",
        review_campaign_id=campaign_id,
        selected_category=selected_category,
        selected_sort=selected_sort,
        anchor="admin-review",
    )


@router.post("/projects/review/{campaign_id}/reject")
def reject_campaign(
    campaign_id: int,
    request: Request,
    reason: str = Form(...),
    category: str = Form("all"),
    sort: str = Form("time_asc"),
) -> RedirectResponse:
    selected_category = None
    requested_category = (category or "").strip().lower()
    if requested_category and requested_category != "all":
        try:
            selected_category = normalize_campaign_category(requested_category)
        except HTTPException:
            selected_category = None
    selected_sort = normalize_dashboard_review_sort(sort)
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            ensure_admin_user(user)
            campaign = CampaignRejectionController.ValidateCampaign(session, campaign_id)
            CampaignRejectionController.RejectCampaign(session, campaign, reason)
    except HTTPException as error:
        detail = getattr(error, "detail", "Unable to reject campaign.")
        return redirect_with_dashboard_flash(
            request,
            detail if isinstance(detail, str) else "Unable to reject campaign.",
            "error",
            review_campaign_id=campaign_id,
            selected_category=selected_category,
            selected_sort=selected_sort,
            anchor="admin-review",
        )

    return redirect_with_dashboard_flash(
        request,
        "Campaign rejected successfully.",
        "success",
        review_campaign_id=campaign_id,
        selected_category=selected_category,
        selected_sort=selected_sort,
        anchor="admin-review",
    )
