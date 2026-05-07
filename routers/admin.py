from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from core.db import get_session
from core.storage import build_avatar_url
from core.ui import templates
from models.campaign import FundraisingCampaign
from models.user import UserProfile
from services.admin_service import (
    ACCOUNT_STATUS_OPTIONS,
    CATEGORY_STATUS_OPTIONS,
    REPORT_TYPE_OPTIONS,
    AccountRemovalController,
    AccountStatusController,
    CategoryController,
    ReportController,
    UserAccountController,
    format_report_period_label,
    normalize_account_status,
    normalize_category_status,
    normalize_report_period,
    normalize_report_type,
    format_report_period_value,
    get_report_month_options,
    serialize_account_detail,
    serialize_account_summary,
    serialize_category_summaries,
    serialize_report,
)
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
    serialize_campaign_summaries,
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
    account_q: str = Query(default=""),
    account_status: str = Query(default="all"),
    account_id: int | None = Query(default=None, ge=1),
    category_q: str = Query(default=""),
    category_status: str = Query(default="all"),
    category_id: int | None = Query(default=None, ge=1),
    report_type: str = Query(default="daily"),
    report_date: str | None = Query(default=None),
    report_week: str | None = Query(default=None),
    report_week_start: str | None = Query(default=None),
    report_week_end: str | None = Query(default=None),
    report_month: str | None = Query(default=None),
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
        selected_account_status = normalize_account_status(account_status)
        account_search_query = account_q.strip()
        accounts = UserAccountController.GetFilteredAccountList(
            session,
            search_keywords=account_search_query,
            status=selected_account_status,
        )
        serialized_accounts = [
            serialize_account_summary(account, account.last_login_at) for account in accounts
        ]
        selected_account_data = None
        if account_id is not None:
            try:
                selected_account_data = serialize_account_detail(
                    UserAccountController.GetAccountDetails(session, account_id)
                )
            except HTTPException:
                selected_account_data = None

        selected_category_status = normalize_category_status(category_status)
        category_search_query = category_q.strip()
        categories = CategoryController.GetCategoryList(
            session,
            search_keywords=category_search_query,
            status=selected_category_status,
        )
        serialized_categories = serialize_category_summaries(session, categories)
        selected_category_data = None
        if category_id is not None:
            try:
                selected_category_data = CategoryController.GetCategoryDetails(
                    session, category_id
                )
            except HTTPException:
                selected_category_data = None

        selected_report_type = normalize_report_type(report_type)
        selected_report_period = normalize_report_period(
            selected_report_type,
            report_date,
            report_week,
            report_month,
            report_week_start,
            report_week_end,
        )
        selected_report_period_start = (
            selected_report_period[0]
            if isinstance(selected_report_period, tuple)
            else selected_report_period
        )
        selected_report_period_end = (
            selected_report_period[1]
            if isinstance(selected_report_period, tuple)
            else selected_report_period
        )
        selected_report_period_value = format_report_period_value(
            selected_report_type, selected_report_period_start
        )
        selected_report_period_label = format_report_period_label(
            selected_report_type, selected_report_period
        )
        report_month_options = get_report_month_options(selected_report_period_start)
        report = ReportController.GetReport(session, selected_report_type, selected_report_period)
        serialized_report = serialize_report(report)
        account_modal_open = modal == "account-details" and selected_account_data is not None
        category_create_modal_open = modal == "create-category"
        category_modal_open = modal == "category-details" and selected_category_data is not None

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
        for campaign, campaign_summary in zip(
            pending_campaigns,
            serialize_campaign_summaries(session, pending_campaigns),
        ):
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
            "account_search_query": account_search_query,
            "account_selected_status": account_status if account_status in {"all", "active", "inactive"} else "all",
            "account_status_options": ACCOUNT_STATUS_OPTIONS,
            "accounts": serialized_accounts,
            "selected_account": selected_account_data,
            "account_modal_open": account_modal_open,
            "category_search_query": category_search_query,
            "category_selected_status": category_status if category_status in {"all", "active", "inactive"} else "all",
            "category_status_options": CATEGORY_STATUS_OPTIONS,
            "categories": serialized_categories,
            "selected_category_record": selected_category_data,
            "category_create_modal_open": category_create_modal_open,
            "category_modal_open": category_modal_open,
            "report_type_options": REPORT_TYPE_OPTIONS,
            "selected_report_type": selected_report_type,
            "selected_report_period_value": selected_report_period_value,
            "selected_report_period_label": selected_report_period_label,
            "selected_report_week_start_value": selected_report_period_start.isoformat(),
            "selected_report_week_end_value": selected_report_period_end.isoformat(),
            "report_month_options": report_month_options,
            "platform_report": serialized_report,
        },
    )


@router.post("/admin/accounts/{account_id}/deactivate")
def deactivate_account(account_id: int, request: Request) -> RedirectResponse:
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            ensure_admin_user(user)
            AccountStatusController.DeactivateAccount(session, account_id, user.id)
    except HTTPException as error:
        detail = getattr(error, "detail", "Unable to deactivate account.")
        return redirect_with_dashboard_flash(
            request,
            detail if isinstance(detail, str) else "Unable to deactivate account.",
            "error",
            anchor="admin-accounts",
        )

    return redirect_with_dashboard_flash(
        request,
        "Account deactivated successfully.",
        "success",
        anchor="admin-accounts",
    )


@router.post("/admin/accounts/{account_id}/delete")
def delete_account(account_id: int, request: Request) -> RedirectResponse:
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            ensure_admin_user(user)
            AccountRemovalController.DeleteAccount(session, account_id, user.id)
    except HTTPException as error:
        detail = getattr(error, "detail", "Unable to delete account.")
        return redirect_with_dashboard_flash(
            request,
            detail if isinstance(detail, str) else "Unable to delete account.",
            "error",
            anchor="admin-accounts",
        )

    return redirect_with_dashboard_flash(
        request,
        "Account deleted successfully.",
        "success",
        anchor="admin-accounts",
    )


@router.post("/admin/categories/create")
def create_category(
    request: Request,
    name: str = Form(...),
    description: str = Form(default=""),
) -> RedirectResponse:
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            ensure_admin_user(user)
            CategoryController.CreateCategory(session, name, description)
    except HTTPException as error:
        detail = getattr(error, "detail", "Unable to create category.")
        return redirect_with_dashboard_flash(
            request,
            detail if isinstance(detail, str) else "Unable to create category.",
            "error",
            anchor="admin-categories",
        )

    return redirect_with_dashboard_flash(
        request,
        "Category created successfully.",
        "success",
        anchor="admin-categories",
    )


@router.post("/admin/categories/{category_id}/update")
def update_category(
    category_id: int,
    request: Request,
    name: str = Form(...),
    description: str = Form(default=""),
    status: str = Form(default="active"),
) -> RedirectResponse:
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            ensure_admin_user(user)
            CategoryController.UpdateCategory(session, category_id, name, description, status)
    except HTTPException as error:
        detail = getattr(error, "detail", "Unable to update category.")
        return redirect_with_dashboard_flash(
            request,
            detail if isinstance(detail, str) else "Unable to update category.",
            "error",
            anchor="admin-categories",
        )

    return redirect_with_dashboard_flash(
        request,
        "Category updated successfully.",
        "success",
        anchor="admin-categories",
    )


@router.post("/admin/categories/{category_id}/delete")
def delete_category(category_id: int, request: Request) -> RedirectResponse:
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            ensure_admin_user(user)
            CategoryController.DeleteCategory(session, category_id)
    except HTTPException as error:
        detail = getattr(error, "detail", "Unable to delete category.")
        return redirect_with_dashboard_flash(
            request,
            detail if isinstance(detail, str) else "Unable to delete category.",
            "error",
            anchor="admin-categories",
        )

    return redirect_with_dashboard_flash(
        request,
        "Category deleted successfully.",
        "success",
        anchor="admin-categories",
    )


@router.get("/admin/reports/{report_type}/export")
def export_report(
    report_type: str,
    request: Request,
    report_date: str | None = Query(default=None),
    report_week: str | None = Query(default=None),
    report_week_start: str | None = Query(default=None),
    report_week_end: str | None = Query(default=None),
    report_month: str | None = Query(default=None),
) -> Response:
    with get_session() as session:
        try:
            user = get_authenticated_user(request, session)
            ensure_admin_user(user)
        except HTTPException:
            return RedirectResponse(url="/auth?mode=login", status_code=303)
        clean_report_type = normalize_report_type(report_type)
        selected_report_period = normalize_report_period(
            clean_report_type,
            report_date,
            report_week,
            report_month,
            report_week_start,
            report_week_end,
        )
        selected_report_period_start = (
            selected_report_period[0]
            if isinstance(selected_report_period, tuple)
            else selected_report_period
        )
        selected_report_period_value = (
            f"{selected_report_period[0].isoformat()}-to-{selected_report_period[1].isoformat()}"
            if isinstance(selected_report_period, tuple)
            else format_report_period_value(clean_report_type, selected_report_period_start)
        )
        csv_text = ReportController.ExportReport(
            session, clean_report_type, selected_report_period
        )
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                f"attachment; filename=fireflyfund-{clean_report_type}-"
                f"{selected_report_period_value}-report.csv"
            )
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
