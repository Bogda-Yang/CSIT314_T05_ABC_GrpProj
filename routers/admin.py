from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.orm import Session

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
    return AdminDashboardPage.ViewUserAccounts(
        request=request,
        category=category,
        sort=sort,
        review_campaign_id=review_campaign_id,
        modal=modal,
        account_q=account_q,
        account_status=account_status,
        account_id=account_id,
        category_q=category_q,
        category_status=category_status,
        category_id=category_id,
        report_type=report_type,
        report_date=report_date,
        report_week=report_week,
        report_week_start=report_week_start,
        report_week_end=report_week_end,
        report_month=report_month,
    )


@router.post("/admin/accounts/{account_id}/deactivate")
def deactivate_account(account_id: int, request: Request) -> RedirectResponse:
    return AccountManagementPage.ConfirmDeactivation(account_id, request)


@router.post("/admin/accounts/{account_id}/delete")
def delete_account(account_id: int, request: Request) -> RedirectResponse:
    return AccountManagementPage.ConfirmDeletion(account_id, request)


@router.post("/admin/categories/create")
def create_category(
    request: Request,
    name: str = Form(...),
    description: str = Form(default=""),
) -> RedirectResponse:
    return CategoryManagementPage.SubmitCategoryCreation(request, name, description)


@router.post("/admin/categories/{category_id}/update")
def update_category(
    category_id: int,
    request: Request,
    name: str = Form(...),
    description: str = Form(default=""),
    status: str = Form(default="active"),
) -> RedirectResponse:
    return CategoryManagementPage.SubmitCategoryUpdate(
        category_id,
        request,
        name,
        description,
        status,
    )


@router.post("/admin/categories/{category_id}/delete")
def delete_category(category_id: int, request: Request) -> RedirectResponse:
    return CategoryManagementPage.ConfirmCategoryDeletion(category_id, request)


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
    return ReportManagementPage.ExportReport(
        report_type,
        request,
        report_date,
        report_week,
        report_week_start,
        report_week_end,
        report_month,
    )


@router.post("/projects/review/{campaign_id}/approve")
def approve_campaign(
    campaign_id: int,
    request: Request,
    category: str = Form("all"),
    sort: str = Form("time_asc"),
) -> RedirectResponse:
    return CampaignReviewPage.ApproveCampaign(campaign_id, request, category, sort)


@router.post("/projects/review/{campaign_id}/reject")
def reject_campaign(
    campaign_id: int,
    request: Request,
    reason: str = Form(...),
    category: str = Form("all"),
    sort: str = Form("time_asc"),
) -> RedirectResponse:
    return CampaignReviewPage.RejectCampaign(campaign_id, request, reason, category, sort)


class AdminDashboardPage:
    """BCE boundary wrapper for A1 account-list dashboard actions."""

    @staticmethod
    def ViewUserAccounts(
        request: Request,
        category: str | None = None,
        sort: str = "time_asc",
        review_campaign_id: int | None = None,
        modal: str | None = None,
        account_q: str = "",
        account_status: str = "all",
        account_id: int | None = None,
        category_q: str = "",
        category_status: str = "all",
        category_id: int | None = None,
        report_type: str = "daily",
        report_date: str | None = None,
        report_week: str | None = None,
        report_week_start: str | None = None,
        report_week_end: str | None = None,
        report_month: str | None = None,
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
            categories = CategoryManagementPage.ViewAllCategories(
                session,
                search_keywords=category_search_query,
                status=selected_category_status,
            )
            serialized_categories = serialize_category_summaries(session, categories)
            selected_category_data = None
            if category_id is not None:
                try:
                    selected_category_data = CategoryManagementPage.ViewCategoryDetails(
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
            if selected_report_type == "weekly":
                report = ReportManagementPage.ViewWeeklyReport(session, selected_report_period)
            elif selected_report_type == "monthly":
                report = ReportManagementPage.ViewMonthlyReport(session, selected_report_period)
            else:
                report = ReportManagementPage.ViewDailyReport(session, selected_report_period)
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
                "account_selected_status": account_status
                if account_status in {"all", "active", "inactive"}
                else "all",
                "account_status_options": ACCOUNT_STATUS_OPTIONS,
                "accounts": serialized_accounts,
                "selected_account": selected_account_data,
                "account_modal_open": account_modal_open,
                "category_search_query": category_search_query,
                "category_selected_status": category_status
                if category_status in {"all", "active", "inactive"}
                else "all",
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

    @staticmethod
    def SearchUserAccounts(request: Request, search_keywords: str) -> HTMLResponse:
        return AdminDashboardPage.ViewUserAccounts(request, account_q=search_keywords)

    @staticmethod
    def FilterUserAccounts(request: Request, account_status: str) -> HTMLResponse:
        return AdminDashboardPage.ViewUserAccounts(request, account_status=account_status)

    @staticmethod
    def ViewAccountDetails(request: Request, account_id: int) -> HTMLResponse:
        return AdminDashboardPage.ViewUserAccounts(
            request,
            modal="account-details",
            account_id=account_id,
        )


class AccountManagementPage:
    """BCE boundary wrapper for A2 and A3 account-management actions."""

    @staticmethod
    def SelectUserAccount(session: Session, account_id: int) -> dict[str, object]:
        return UserAccountController.GetAccountDetails(session, account_id)

    @staticmethod
    def ReviewAccountDetails(session: Session, account_id: int) -> dict[str, object]:
        return UserAccountController.GetAccountDetails(session, account_id)

    @staticmethod
    def ViewAccountStatus(session: Session, account_id: int) -> str:
        return AccountStatusController.GetAccountStatus(session, account_id)

    @staticmethod
    def ConfirmDeactivation(account_id: int, request: Request) -> RedirectResponse:
        try:
            with get_session() as session:
                user = get_authenticated_user(request, session)
                ensure_admin_user(user)
                AccountStatusController.DeactivateAccount(session, account_id, user.id)
        except HTTPException as error:
            detail = getattr(error, "detail", "Unable to deactivate account.")
            return AccountManagementPage.DisplayDeactivationResult(
                request,
                detail if isinstance(detail, str) else "Unable to deactivate account.",
                "error",
            )

        return AccountManagementPage.DisplayDeactivationResult(request)

    @staticmethod
    def DisplayDeactivationResult(
        request: Request,
        message: str = "Account deactivated successfully.",
        message_type: str = "success",
    ) -> RedirectResponse:
        return redirect_with_dashboard_flash(
            request,
            message,
            message_type,
            anchor="admin-accounts",
        )

    @staticmethod
    def ConfirmDeletion(account_id: int, request: Request) -> RedirectResponse:
        try:
            with get_session() as session:
                user = get_authenticated_user(request, session)
                ensure_admin_user(user)
                AccountRemovalController.DeleteAccount(session, account_id, user.id)
        except HTTPException as error:
            detail = getattr(error, "detail", "Unable to delete account.")
            return AccountManagementPage.DisplayDeletionResult(
                request,
                detail if isinstance(detail, str) else "Unable to delete account.",
                "error",
            )

        return AccountManagementPage.DisplayDeletionResult(request)

    @staticmethod
    def DisplayDeletionResult(
        request: Request,
        message: str = "Account deleted successfully.",
        message_type: str = "success",
    ) -> RedirectResponse:
        return redirect_with_dashboard_flash(
            request,
            message,
            message_type,
            anchor="admin-accounts",
        )


class CampaignReviewPage:
    """BCE boundary wrapper for A4 and A5 campaign-review actions."""

    @staticmethod
    def ViewPendingCampaigns(
        session: Session,
        category: str | None = None,
        sort_order: str = "time_asc",
    ) -> list[FundraisingCampaign]:
        return CampaignApprovalController.GetPendingCampaigns(
            session,
            category=category,
            sort_order=sort_order,
        )

    @staticmethod
    def ReviewCampaignDetails(session: Session, campaign_id: int) -> dict[str, object]:
        campaign = CampaignApprovalController.RetrieveCampaignStatus(session, campaign_id)
        return serialize_campaign_detail(session, campaign)

    @staticmethod
    def ApproveCampaign(
        campaign_id: int,
        request: Request,
        category: str = "all",
        sort: str = "time_asc",
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
            return CampaignReviewPage.DisplayApprovalResult(
                request,
                campaign_id,
                detail if isinstance(detail, str) else "Unable to approve campaign.",
                "error",
                selected_category,
                selected_sort,
            )

        return CampaignReviewPage.DisplayApprovalResult(
            request,
            campaign_id,
            category=selected_category,
            sort=selected_sort,
        )

    @staticmethod
    def DisplayApprovalResult(
        request: Request,
        campaign_id: int,
        message: str = "Campaign approved and published successfully.",
        message_type: str = "success",
        category: str | None = None,
        sort: str = "time_asc",
    ) -> RedirectResponse:
        return redirect_with_dashboard_flash(
            request,
            message,
            message_type,
            review_campaign_id=campaign_id,
            selected_category=category,
            selected_sort=sort,
            anchor="admin-review",
        )

    @staticmethod
    def EnterRejectionReason(reason: str) -> str:
        clean_reason = reason.strip()
        if len(clean_reason) < 10:
            raise HTTPException(
                status_code=400,
                detail="Rejection reason must be at least 10 characters.",
            )
        return clean_reason

    @staticmethod
    def RejectCampaign(
        campaign_id: int,
        request: Request,
        reason: str,
        category: str = "all",
        sort: str = "time_asc",
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
            clean_reason = CampaignReviewPage.EnterRejectionReason(reason)
            with get_session() as session:
                user = get_authenticated_user(request, session)
                ensure_admin_user(user)
                campaign = CampaignRejectionController.ValidateCampaign(session, campaign_id)
                CampaignRejectionController.RejectCampaign(session, campaign, clean_reason)
        except HTTPException as error:
            detail = getattr(error, "detail", "Unable to reject campaign.")
            return CampaignReviewPage.DisplayRejectionResult(
                request,
                campaign_id,
                detail if isinstance(detail, str) else "Unable to reject campaign.",
                "error",
                selected_category,
                selected_sort,
            )

        return CampaignReviewPage.DisplayRejectionResult(
            request,
            campaign_id,
            category=selected_category,
            sort=selected_sort,
        )

    @staticmethod
    def DisplayRejectionResult(
        request: Request,
        campaign_id: int,
        message: str = "Campaign rejected successfully.",
        message_type: str = "success",
        category: str | None = None,
        sort: str = "time_asc",
    ) -> RedirectResponse:
        return redirect_with_dashboard_flash(
            request,
            message,
            message_type,
            review_campaign_id=campaign_id,
            selected_category=category,
            selected_sort=sort,
            anchor="admin-review",
        )


class CategoryManagementPage:
    """BCE boundary class for P1-P4 category-management actions."""

    @staticmethod
    def AccessCategoryManagementPage(request: Request) -> HTMLResponse:
        return AdminDashboardPage.ViewUserAccounts(
            request=request,
            modal="create-category",
        )

    @staticmethod
    def EnterCategoryDetails(name: str, description: str = "") -> tuple[str, str]:
        return CategoryController.ValidateCategoryInformation(name, description)

    @staticmethod
    def SubmitCategoryCreation(
        request: Request,
        name: str,
        description: str = "",
    ) -> RedirectResponse:
        try:
            with get_session() as session:
                user = get_authenticated_user(request, session)
                ensure_admin_user(user)
                CategoryManagementPage.EnterCategoryDetails(name, description)
                CategoryController.CreateCategory(session, name, description)
        except HTTPException as error:
            detail = getattr(error, "detail", "Unable to create category.")
            return CategoryManagementPage.DisplayCreationResult(
                request,
                detail if isinstance(detail, str) else "Unable to create category.",
                "error",
            )

        return CategoryManagementPage.DisplayCreationResult(request)

    @staticmethod
    def DisplayCreationResult(
        request: Request,
        message: str = "Category created successfully.",
        message_type: str = "success",
    ) -> RedirectResponse:
        return redirect_with_dashboard_flash(
            request,
            message,
            message_type,
            anchor="admin-categories",
        )

    @staticmethod
    def SelectExistingCategory(session: Session, category_id: int) -> dict[str, object]:
        return CategoryController.GetCategoryDetails(session, category_id)

    @staticmethod
    def ViewCurrentCategoryDetails(session: Session, category_id: int) -> dict[str, object]:
        return CategoryController.GetCategoryDetails(session, category_id)

    @staticmethod
    def EditCategoryDetails(name: str, description: str, status: str) -> tuple[str, str, str]:
        return CategoryController.ValidateUpdatedInformation(name, description, status)

    @staticmethod
    def SubmitCategoryUpdate(
        category_id: int,
        request: Request,
        name: str,
        description: str = "",
        status: str = "active",
    ) -> RedirectResponse:
        try:
            with get_session() as session:
                user = get_authenticated_user(request, session)
                ensure_admin_user(user)
                CategoryManagementPage.EditCategoryDetails(name, description, status)
                CategoryController.UpdateCategory(session, category_id, name, description, status)
        except HTTPException as error:
            detail = getattr(error, "detail", "Unable to update category.")
            return CategoryManagementPage.DisplayUpdateResult(
                request,
                detail if isinstance(detail, str) else "Unable to update category.",
                "error",
            )

        return CategoryManagementPage.DisplayUpdateResult(request)

    @staticmethod
    def DisplayUpdateResult(
        request: Request,
        message: str = "Category updated successfully.",
        message_type: str = "success",
    ) -> RedirectResponse:
        return redirect_with_dashboard_flash(
            request,
            message,
            message_type,
            anchor="admin-categories",
        )

    @staticmethod
    def SelectCategory(session: Session, category_id: int) -> dict[str, object]:
        return CategoryController.GetCategoryDetails(session, category_id)

    @staticmethod
    def ReviewCategoryDetails(session: Session, category_id: int) -> dict[str, object]:
        return CategoryController.GetCategoryDetails(session, category_id)

    @staticmethod
    def ConfirmCategoryDeletion(category_id: int, request: Request) -> RedirectResponse:
        try:
            with get_session() as session:
                user = get_authenticated_user(request, session)
                ensure_admin_user(user)
                CategoryController.DeleteCategory(session, category_id)
        except HTTPException as error:
            detail = getattr(error, "detail", "Unable to delete category.")
            return CategoryManagementPage.DisplayDeletionResult(
                request,
                detail if isinstance(detail, str) else "Unable to delete category.",
                "error",
            )

        return CategoryManagementPage.DisplayDeletionResult(request)

    @staticmethod
    def DisplayDeletionResult(
        request: Request,
        message: str = "Category deleted successfully.",
        message_type: str = "success",
    ) -> RedirectResponse:
        return redirect_with_dashboard_flash(
            request,
            message,
            message_type,
            anchor="admin-categories",
        )

    @staticmethod
    def ViewAllCategories(
        session: Session,
        search_keywords: str = "",
        status: str | None = None,
    ) -> list[object]:
        return CategoryController.GetCategoryList(
            session,
            search_keywords=search_keywords,
            status=status,
        )

    @staticmethod
    def SearchCategories(session: Session, search_keywords: str) -> list[object]:
        return CategoryController.SearchCategories(session, search_keywords)

    @staticmethod
    def FilterCategories(session: Session, status: str | None = None) -> list[object]:
        return CategoryController.FilterCategories(session, status)

    @staticmethod
    def ViewCategoryDetails(session: Session, category_id: int) -> dict[str, object]:
        return CategoryController.GetCategoryDetails(session, category_id)


class ReportManagementPage:
    """BCE boundary class for P5-P7 report-management actions."""

    @staticmethod
    def AccessReportManagementPage(
        request: Request,
        report_type: str = "daily",
    ) -> HTMLResponse:
        return AdminDashboardPage.ViewUserAccounts(
            request=request,
            report_type=report_type,
        )

    @staticmethod
    def SelectDailyReportType() -> str:
        return "daily"

    @staticmethod
    def SelectWeeklyReportType() -> str:
        return "weekly"

    @staticmethod
    def SelectMonthlyReportType() -> str:
        return "monthly"

    @staticmethod
    def GenerateDailyReport(session: Session, selected_day=None):
        return ReportController.GenerateDailyReport(session, selected_day)

    @staticmethod
    def GenerateWeeklyReport(session: Session, selected_period=None):
        if isinstance(selected_period, tuple):
            return ReportController.GenerateWeeklyReport(session, selected_period[0], selected_period[1])
        return ReportController.GenerateWeeklyReport(session, selected_period)

    @staticmethod
    def GenerateMonthlyReport(session: Session, selected_month=None):
        return ReportController.GenerateMonthlyReport(session, selected_month)

    @staticmethod
    def ViewDailyReport(session: Session, selected_day=None):
        return ReportController.GetDailyReport(session, selected_day)

    @staticmethod
    def ViewWeeklyReport(session: Session, selected_period=None):
        if isinstance(selected_period, tuple):
            return ReportController.GetWeeklyReport(session, selected_period[0], selected_period[1])
        return ReportController.GetWeeklyReport(session, selected_period)

    @staticmethod
    def ViewMonthlyReport(session: Session, selected_month=None):
        return ReportController.GetMonthlyReport(session, selected_month)

    @staticmethod
    def ExportDailyReport(
        request: Request,
        report_date: str | None = None,
    ) -> Response:
        return ReportManagementPage.ExportReport(
            ReportManagementPage.SelectDailyReportType(),
            request,
            report_date=report_date,
        )

    @staticmethod
    def ExportWeeklyReport(
        request: Request,
        report_week: str | None = None,
        report_week_start: str | None = None,
        report_week_end: str | None = None,
    ) -> Response:
        return ReportManagementPage.ExportReport(
            ReportManagementPage.SelectWeeklyReportType(),
            request,
            report_week=report_week,
            report_week_start=report_week_start,
            report_week_end=report_week_end,
        )

    @staticmethod
    def ExportMonthlyReport(
        request: Request,
        report_month: str | None = None,
    ) -> Response:
        return ReportManagementPage.ExportReport(
            ReportManagementPage.SelectMonthlyReportType(),
            request,
            report_month=report_month,
        )

    @staticmethod
    def ExportReport(
        report_type: str,
        request: Request,
        report_date: str | None = None,
        report_week: str | None = None,
        report_week_start: str | None = None,
        report_week_end: str | None = None,
        report_month: str | None = None,
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
