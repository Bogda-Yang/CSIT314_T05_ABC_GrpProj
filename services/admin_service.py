from __future__ import annotations

import calendar
from datetime import date, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.admin import Category, DailyReport, MonthlyReport, PlatformActivity, WeeklyReport
from models.campaign import FundraisingCampaign
from models.user import (
    AccountStatus,
    AuthenticationToken,
    UserAccount,
    UserActivityLog,
    UserSession,
)
from core.security import now_dt
from services.campaign_service import humanize_campaign_category
from services.user_service import DeleteAccountController, is_admin_email


ACCOUNT_STATUS_OPTIONS = (
    ("all", "All"),
    ("active", "Active"),
    ("inactive", "Inactive"),
)
CATEGORY_STATUS_OPTIONS = (
    ("all", "All"),
    ("active", "Active"),
    ("inactive", "Inactive"),
)
REPORT_TYPE_OPTIONS = (
    ("daily", "Daily"),
    ("weekly", "Weekly"),
    ("monthly", "Monthly"),
)


def normalize_account_status(status: str | None) -> str | None:
    clean_status = (status or "all").strip().lower()
    if clean_status == "all":
        return None
    if clean_status not in {"active", "inactive"}:
        raise HTTPException(status_code=400, detail="Choose a valid account status.")
    return clean_status


def normalize_category_status(status: str | None) -> str | None:
    clean_status = (status or "all").strip().lower()
    if clean_status == "all":
        return None
    if clean_status not in {"active", "inactive"}:
        raise HTTPException(status_code=400, detail="Choose a valid category status.")
    return clean_status


def normalize_report_type(report_type: str | None) -> str:
    clean_type = (report_type or "daily").strip().lower()
    if clean_type not in {"daily", "weekly", "monthly"}:
        raise HTTPException(status_code=400, detail="Choose a valid report type.")
    return clean_type


def normalize_report_date(report_date: str | None) -> date:
    clean_date = (report_date or "").strip()
    if not clean_date:
        return now_dt().date()
    try:
        return date.fromisoformat(clean_date)
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Choose a valid report date.") from error


def normalize_report_week_range(
    report_week_start: str | None, report_week_end: str | None
) -> tuple[date, date]:
    clean_start = (report_week_start or "").strip()
    clean_end = (report_week_end or "").strip()
    if not clean_start:
        today = now_dt().date()
        selected_start = today - timedelta(days=today.weekday())
    else:
        try:
            selected_start = date.fromisoformat(clean_start)
        except ValueError as error:
            raise HTTPException(status_code=400, detail="Choose a valid weekly start date.") from error

    if not clean_end:
        selected_end = selected_start + timedelta(days=6)
    else:
        try:
            selected_end = date.fromisoformat(clean_end)
        except ValueError as error:
            raise HTTPException(status_code=400, detail="Choose a valid weekly end date.") from error

    if selected_end < selected_start:
        raise HTTPException(status_code=400, detail="Weekly end date cannot be before start date.")
    return selected_start, selected_end


def normalize_report_week(report_week: str | None) -> date:
    clean_week = (report_week or "").strip()
    if not clean_week:
        return normalize_report_week_range(None, None)[0]
    try:
        selected_year, selected_week = clean_week.split("-W", 1)
        return date.fromisocalendar(int(selected_year), int(selected_week), 1)
    except (ValueError, TypeError) as error:
        raise HTTPException(status_code=400, detail="Choose a valid report week.") from error


def normalize_report_month(report_month: str | None) -> date:
    clean_month = (report_month or "").strip()
    if not clean_month:
        today = now_dt().date()
        return today.replace(day=1)
    try:
        return datetime.strptime(clean_month, "%Y-%m").date().replace(day=1)
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Choose a valid report month.") from error


def normalize_report_period(
    report_type: str,
    report_date: str | None,
    report_week: str | None,
    report_month: str | None,
    report_week_start: str | None = None,
    report_week_end: str | None = None,
) -> date | tuple[date, date]:
    clean_type = normalize_report_type(report_type)
    if clean_type == "weekly":
        if report_week_start or report_week_end:
            return normalize_report_week_range(report_week_start, report_week_end)
        selected_start = normalize_report_week(report_week)
        return selected_start, selected_start + timedelta(days=6)
    if clean_type == "monthly":
        return normalize_report_month(report_month)
    return normalize_report_date(report_date)


def format_report_period_value(report_type: str, selected_period: date) -> str:
    clean_type = normalize_report_type(report_type)
    if clean_type == "weekly":
        return selected_period.isoformat()
    if clean_type == "monthly":
        return selected_period.strftime("%Y-%m")
    return selected_period.isoformat()


def format_report_date_label(selected_date: date) -> str:
    return f"{calendar.month_name[selected_date.month]} {selected_date.day}, {selected_date.year}"


def format_report_month_label(selected_month: date) -> str:
    return f"{calendar.month_name[selected_month.month]} {selected_month.year}"


def format_report_period_label(report_type: str, selected_period: date | tuple[date, date]) -> str:
    clean_type = normalize_report_type(report_type)
    if clean_type == "weekly":
        start_date, end_date = selected_period if isinstance(selected_period, tuple) else (
            selected_period,
            selected_period + timedelta(days=6),
        )
        return f"{format_report_date_label(start_date)} to {format_report_date_label(end_date)}"
    if clean_type == "monthly":
        month_date = selected_period[0] if isinstance(selected_period, tuple) else selected_period
        return format_report_month_label(month_date)
    day_date = selected_period[0] if isinstance(selected_period, tuple) else selected_period
    return format_report_date_label(day_date)


def get_report_month_options(selected_month: date) -> list[dict[str, str | bool]]:
    options: list[dict[str, str | bool]] = []
    selected_value = selected_month.strftime("%Y-%m")
    for year in range(2025, 2031):
        for month in range(1, 13):
            value = f"{year}-{month:02d}"
            options.append(
                {
                    "value": value,
                    "label": f"{calendar.month_abbr[month]} {year}",
                    "is_active": value == selected_value,
                }
            )
    return options


def ensure_default_categories(session: Session) -> None:
    if Category.SeedDefaultCategories(session):
        session.commit()


class UserAccountController:
    @staticmethod
    def GetUserAccountList(session: Session) -> list[UserAccount]:
        return UserAccount.GetAllAccounts(session)

    @staticmethod
    def SearchAccounts(session: Session, search_keywords: str) -> list[UserAccount]:
        return UserAccount.SearchAccounts(session, search_keywords)

    @staticmethod
    def FilterAccounts(session: Session, status: str | None = None) -> list[UserAccount]:
        return UserAccount.FilterAccounts(session, status)

    @staticmethod
    def GetAccountDetails(session: Session, user_id: int) -> dict[str, object]:
        account = UserAccount.GetAccountById(session, user_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found.")
        activity_data = UserActivityLog.GetUserActivity(session, user_id)
        last_login = UserActivityLog.GetLastLogin(session, user_id) or account.last_login_at
        return {
            "account": account,
            "activity_data": activity_data,
            "last_login": last_login,
        }

    @staticmethod
    def GetFilteredAccountList(
        session: Session, search_keywords: str = "", status: str | None = None
    ) -> list[UserAccount]:
        accounts = (
            UserAccountController.SearchAccounts(session, search_keywords)
            if search_keywords.strip()
            else UserAccountController.GetUserAccountList(session)
        )
        if status:
            accounts = [account for account in accounts if (account.status or "active") == status]
        return accounts


class AccountStatusController:
    @staticmethod
    def GetAccountStatus(session: Session, user_id: int) -> str:
        account = UserAccount.GetAccountById(session, user_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found.")
        return AccountStatus.GetStatus(account)

    @staticmethod
    def DeactivateAccount(session: Session, user_id: int, current_admin_id: int) -> UserAccount:
        account = UserAccount.GetAccountById(session, user_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found.")
        if account.id == current_admin_id:
            raise HTTPException(status_code=400, detail="You cannot deactivate your own account.")
        if is_admin_email(account.email):
            raise HTTPException(status_code=400, detail="Administrator accounts cannot be deactivated.")
        AccountStatus.SetInactive(account)
        AccountStatusController.UpdateAccountStatus(session, account)
        AccountStatusController.ClearAccountSessions(session, account.id)
        UserActivityLog.RecordActivity(session, account.id, "account_deactivated", "Account deactivated by administrator.")
        session.commit()
        return account

    @staticmethod
    def UpdateAccountStatus(session: Session, account: UserAccount) -> None:
        session.add(account)

    @staticmethod
    def ClearAccountSessions(session: Session, user_id: int) -> None:
        session_records = list(
            session.scalars(select(UserSession).where(UserSession.user_id == user_id))
        )
        for user_session in session_records:
            linked_tokens = list(
                session.scalars(
                    select(AuthenticationToken).where(
                        AuthenticationToken.session_key == user_session.session_key
                    )
                )
            )
            for token in linked_tokens:
                session.delete(token)
            session.delete(user_session)


class AccountRemovalController:
    @staticmethod
    def GetAccountDetails(session: Session, user_id: int) -> dict[str, object]:
        return UserAccountController.GetAccountDetails(session, user_id)

    @staticmethod
    def DeleteAccount(session: Session, user_id: int, current_admin_id: int) -> None:
        account = UserAccount.GetAccountById(session, user_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found.")
        if account.id == current_admin_id:
            raise HTTPException(status_code=400, detail="You cannot delete your own account.")
        if is_admin_email(account.email):
            raise HTTPException(status_code=400, detail="Administrator accounts cannot be deleted.")
        AccountRemovalController.RemoveAccountRecord(session, account)

    @staticmethod
    def RemoveAccountRecord(session: Session, account: UserAccount) -> None:
        DeleteAccountController.DeleteAccount(session, account)


class CategoryController:
    @staticmethod
    def ValidateCategoryInformation(name: str, description: str = "") -> tuple[str, str]:
        clean_name = name.strip()
        clean_description = description.strip()
        if len(clean_name) < 2:
            raise HTTPException(status_code=400, detail="Category name must be at least 2 characters.")
        if len(clean_name) > 80:
            raise HTTPException(status_code=400, detail="Category name must be 80 characters or fewer.")
        if len(clean_description) > 300:
            raise HTTPException(status_code=400, detail="Category description must be 300 characters or fewer.")
        return clean_name, clean_description

    @staticmethod
    def ValidateUpdatedInformation(name: str, description: str, status: str) -> tuple[str, str, str]:
        clean_name, clean_description = CategoryController.ValidateCategoryInformation(name, description)
        clean_status = (status or "active").strip().lower()
        if clean_status not in {"active", "inactive"}:
            raise HTTPException(status_code=400, detail="Choose a valid category status.")
        return clean_name, clean_description, clean_status

    @staticmethod
    def CreateCategory(session: Session, name: str, description: str = "") -> Category:
        clean_name, clean_description = CategoryController.ValidateCategoryInformation(name, description)
        category = Category.CreateCategory(clean_name, clean_description)
        CategoryController.SaveCategory(session, category)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=409, detail="This category already exists.")
        session.refresh(category)
        return category

    @staticmethod
    def SaveCategory(session: Session, category: Category) -> None:
        Category.SaveCategory(session, category)

    @staticmethod
    def GetCategoryList(
        session: Session, search_keywords: str = "", status: str | None = None
    ) -> list[Category]:
        categories = (
            CategoryController.SearchCategories(session, search_keywords)
            if search_keywords.strip()
            else Category.GetAllCategories(session)
        )
        if status:
            categories = [category for category in categories if category.status == status]
        return categories

    @staticmethod
    def SearchCategories(session: Session, search_keywords: str) -> list[Category]:
        return Category.SearchCategories(session, search_keywords)

    @staticmethod
    def FilterCategories(session: Session, status: str | None = None) -> list[Category]:
        return Category.FilterCategories(session, status)

    @staticmethod
    def GetCategoryDetails(session: Session, category_id: int) -> dict[str, object]:
        category = Category.GetCategoryById(session, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found.")
        details = Category.GetCategoryDetails(category)
        details["campaign_count"] = CategoryController.GetCategoryCampaignCount(session, category.value)
        return details

    @staticmethod
    def UpdateCategory(
        session: Session, category_id: int, name: str, description: str, status: str
    ) -> Category:
        category = Category.GetCategoryById(session, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found.")
        clean_name, clean_description, clean_status = CategoryController.ValidateUpdatedInformation(
            name, description, status
        )
        Category.UpdateCategory(category, clean_name, clean_description, clean_status)
        CategoryController.SaveCategoryChanges(session, category)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=409, detail="This category already exists.")
        session.refresh(category)
        return category

    @staticmethod
    def SaveCategoryChanges(session: Session, category: Category) -> None:
        Category.SaveCategoryChanges(session, category)

    @staticmethod
    def DeleteCategory(session: Session, category_id: int) -> None:
        category = Category.GetCategoryById(session, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found.")
        campaign_count = CategoryController.GetCategoryCampaignCount(session, category.value)
        if campaign_count:
            raise HTTPException(status_code=400, detail="Only unused categories can be deleted.")
        CategoryController.RemoveCategory(session, category)
        session.commit()

    @staticmethod
    def RemoveCategory(session: Session, category: Category) -> None:
        Category.DeleteCategory(session, category)

    @staticmethod
    def GetCategoryCampaignCount(session: Session, category_value: str) -> int:
        return int(
            session.scalar(
                select(func.count(FundraisingCampaign.id)).where(
                    FundraisingCampaign.category == category_value,
                    FundraisingCampaign.status != "deleted",
                )
            )
            or 0
        )


class ReportController:
    @staticmethod
    def CollectDailyActivityData(session: Session, selected_day: date | None = None) -> dict[str, object]:
        return PlatformActivity.GetDailyActivityData(session, selected_day)

    @staticmethod
    def CollectWeeklyActivityData(
        session: Session,
        selected_week_start: date | None = None,
        selected_week_end: date | None = None,
    ) -> dict[str, object]:
        return PlatformActivity.GetWeeklyActivityData(
            session, selected_week_start, selected_week_end
        )

    @staticmethod
    def CollectMonthlyPerformanceData(
        session: Session, selected_month_start: date | None = None
    ) -> dict[str, object]:
        return PlatformActivity.GetMonthlyPerformanceData(session, selected_month_start)

    @staticmethod
    def GenerateDailyReport(session: Session, selected_day: date | None = None):
        return DailyReport.GenerateReport(ReportController.CollectDailyActivityData(session, selected_day))

    @staticmethod
    def GenerateWeeklyReport(
        session: Session,
        selected_week_start: date | None = None,
        selected_week_end: date | None = None,
    ):
        return WeeklyReport.GenerateReport(
            ReportController.CollectWeeklyActivityData(
                session, selected_week_start, selected_week_end
            )
        )

    @staticmethod
    def GenerateMonthlyReport(session: Session, selected_month_start: date | None = None):
        return MonthlyReport.GenerateReport(
            ReportController.CollectMonthlyPerformanceData(session, selected_month_start)
        )

    @staticmethod
    def GetDailyReport(session: Session, selected_day: date | None = None):
        return DailyReport.GetReport(ReportController.GenerateDailyReport(session, selected_day))

    @staticmethod
    def GetWeeklyReport(
        session: Session,
        selected_week_start: date | None = None,
        selected_week_end: date | None = None,
    ):
        return WeeklyReport.GetReport(
            ReportController.GenerateWeeklyReport(session, selected_week_start, selected_week_end)
        )

    @staticmethod
    def GetMonthlyReport(session: Session, selected_month_start: date | None = None):
        return MonthlyReport.GetReport(
            ReportController.GenerateMonthlyReport(session, selected_month_start)
        )

    @staticmethod
    def GetReport(session: Session, report_type: str, selected_period: date | tuple[date, date] | None = None):
        clean_type = normalize_report_type(report_type)
        if clean_type == "weekly":
            if isinstance(selected_period, tuple):
                return ReportController.GetWeeklyReport(session, selected_period[0], selected_period[1])
            return ReportController.GetWeeklyReport(session, selected_period)
        if clean_type == "monthly":
            return ReportController.GetMonthlyReport(session, selected_period)
        return ReportController.GetDailyReport(session, selected_period)

    @staticmethod
    def ExportReport(session: Session, report_type: str, selected_period: date | tuple[date, date] | None = None) -> str:
        clean_type = normalize_report_type(report_type)
        report = ReportController.GetReport(session, clean_type, selected_period)
        if clean_type == "weekly":
            return WeeklyReport.ExportReport(report)
        if clean_type == "monthly":
            return MonthlyReport.ExportReport(report)
        return DailyReport.ExportReport(report)


def serialize_account_summary(account: UserAccount, last_login) -> dict[str, object]:
    return {
        "id": account.id,
        "username": account.username,
        "email": account.email,
        "status": account.status or "active",
        "status_label": (account.status or "active").title(),
        "created_at": account.created_at.strftime("%Y-%m-%d %H:%M") if account.created_at else "N/A",
        "last_login_at": last_login.strftime("%Y-%m-%d %H:%M") if last_login else "Never",
        "is_admin_account": is_admin_email(account.email),
    }


def serialize_account_detail(details: dict[str, object]) -> dict[str, object]:
    account = details["account"]
    activity_data = details["activity_data"]
    return {
        **serialize_account_summary(account, details["last_login"]),
        "activity_data": [
            {
                "activity_type": activity.activity_type,
                "details": activity.details,
                "created_at": activity.created_at.strftime("%Y-%m-%d %H:%M"),
            }
            for activity in activity_data
        ],
    }


def serialize_category_summary(session: Session, category: Category) -> dict[str, object]:
    return {
        "id": category.id,
        "value": category.value,
        "name": category.name,
        "description": category.description,
        "status": category.status,
        "status_label": category.status.title(),
        "campaign_count": CategoryController.GetCategoryCampaignCount(session, category.value),
    }


def serialize_category_summaries(
    session: Session, categories: list[Category]
) -> list[dict[str, object]]:
    if not categories:
        return []

    category_values = [category.value for category in categories]
    count_rows = session.execute(
        select(FundraisingCampaign.category, func.count(FundraisingCampaign.id))
        .where(
            FundraisingCampaign.category.in_(category_values),
            FundraisingCampaign.status != "deleted",
        )
        .group_by(FundraisingCampaign.category)
    ).all()
    count_lookup = {category_value: int(count or 0) for category_value, count in count_rows}

    return [
        {
            "id": category.id,
            "value": category.value,
            "name": category.name,
            "description": category.description,
            "status": category.status,
            "status_label": category.status.title(),
            "campaign_count": count_lookup.get(category.value, 0),
        }
        for category in categories
    ]


def serialize_report(report) -> dict[str, object]:
    data = report.data
    period_start = data["period_start"]
    period_end = data["period_end"]
    if report.report_type == "weekly":
        period_label = format_report_period_label(
            report.report_type,
            (period_start.date(), (period_end - timedelta(days=1)).date()),
        )
    else:
        period_label = format_report_period_label(report.report_type, period_start.date())

    def money(value: object) -> str:
        return f"${int(float(value or 0)):,}"

    def category_summary(category_data: dict[str, object]) -> str:
        category = str(category_data.get("category") or "N/A")
        if category == "N/A":
            return "N/A"
        return (
            f"{humanize_campaign_category(category)} "
            f"({money(category_data.get('donation_amount'))})"
        )

    def campaign_summary(campaign_data: dict[str, object], value_key: str) -> str:
        title = str(campaign_data.get("title") or "N/A")
        if title == "N/A":
            return "N/A"
        value = campaign_data.get(value_key)
        if value_key == "donation_amount":
            return f"{title} ({money(value)})"
        return f"{title} ({int(value or 0):,} views)"

    if report.report_type == "weekly":
        trend_rows = [
            {
                "label": row["label"],
                "donations_count": row["donations_count"],
                "donation_amount": money(row["donation_amount"]),
                "views_count": row["views_count"],
                "users_created": row["users_created"],
            }
            for row in data.get("daily_trend_rows", [])
        ]
        metrics = [
            ("Total Donations This Week", data["donations_count"]),
            ("Total Donation Amount This Week", money(data["donation_amount"])),
            ("Campaign Views This Week", data["views_count"]),
            ("New Users This Week", data["users_created"]),
            ("Best Performing Category", category_summary(data["best_performing_category"])),
            (
                "Most Viewed Campaign",
                campaign_summary(data["most_viewed_campaign"], "views_count"),
            ),
        ]
    elif report.report_type == "monthly":
        trend_rows = []
        metrics = [
            ("Total Monthly Donation Amount", money(data["donation_amount"])),
            ("Total Monthly Donations", data["donations_count"]),
            ("Published Campaigns", data["campaigns_published"]),
            ("Average Donation Amount", money(data["average_donation_amount"])),
            ("Top Category by Donation Amount", category_summary(data["top_category_by_donation"])),
            (
                "Top Campaign by Donation Amount",
                campaign_summary(data["top_campaign_by_donation"], "donation_amount"),
            ),
            ("Campaign Success Rate", f"{float(data['campaign_success_rate']):.1f}%"),
            ("User Growth", data["user_growth"]),
            ("Donor Participation", data["donor_participation"]),
            ("Supported Campaigns", data["supported_campaigns"]),
        ]
    else:
        trend_rows = []
        metrics = [
            ("Users Created", data["users_created"]),
            ("Campaigns Created", data["campaigns_created"]),
            ("Campaigns Published", data["campaigns_published"]),
            ("Donation Count", data["donations_count"]),
            ("Donation Amount", money(data["donation_amount"])),
            ("Favourites Added", data["favourites_count"]),
            ("Campaign Views", data["views_count"]),
        ]

    return {
        "type": report.report_type,
        "title": report.title,
        "period_label": period_label,
        "period_start": period_start.strftime("%Y-%m-%d %H:%M"),
        "period_end": period_end.strftime("%Y-%m-%d %H:%M"),
        "metrics": metrics,
        "trend_rows": trend_rows,
    }


def category_options_for_templates(session: Session) -> tuple[tuple[str, str], ...]:
    active_categories = [
        category for category in Category.GetAllCategories(session) if category.status == "active"
    ]
    if not active_categories:
        return tuple()
    return tuple((category.value, category.name) for category in active_categories)


def humanize_admin_category(category_value: str) -> str:
    return humanize_campaign_category(category_value)
