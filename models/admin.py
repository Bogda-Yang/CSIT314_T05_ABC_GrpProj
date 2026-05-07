from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint, delete, func, or_, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from core.config import CAMPAIGN_CATEGORY_OPTIONS
from core.security import now_dt
from models import Base
from models.campaign import CampaignViewRecord, FundraisingCampaign
from models.donation import DonationRecord, FavouriteCampaign
from models.user import UserAccount


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("value", name="uq_categories_value"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @staticmethod
    def NormalizeCategoryValue(name: str) -> str:
        clean_name = name.strip().lower()
        clean_name = re.sub(r"[^a-z0-9]+", "_", clean_name)
        clean_name = re.sub(r"_+", "_", clean_name).strip("_")
        return clean_name[:40]

    @staticmethod
    def CreateCategory(name: str, description: str = "") -> "Category":
        clean_name = name.strip()
        return Category(
            value=Category.NormalizeCategoryValue(clean_name),
            name=clean_name,
            description=description.strip(),
            status="active",
            created_at=now_dt(),
            updated_at=now_dt(),
        )

    @staticmethod
    def SaveCategory(session: Session, category: "Category") -> None:
        session.add(category)

    @staticmethod
    def GetCategoryDetails(category: "Category") -> dict[str, object]:
        return {
            "id": category.id,
            "value": category.value,
            "name": category.name,
            "description": category.description,
            "status": category.status,
            "created_at": category.created_at,
            "updated_at": category.updated_at,
        }

    @staticmethod
    def GetCategoryById(session: Session, category_id: int) -> "Category | None":
        return session.get(Category, category_id)

    @staticmethod
    def GetAllCategories(session: Session) -> list["Category"]:
        statement = select(Category).order_by(Category.name.asc())
        return list(session.scalars(statement))

    @staticmethod
    def SearchCategories(session: Session, search_keywords: str) -> list["Category"]:
        clean_keywords = search_keywords.strip().lower()
        if not clean_keywords:
            return Category.GetAllCategories(session)
        search_pattern = f"%{clean_keywords}%"
        statement = (
            select(Category)
            .where(
                or_(
                    func.lower(Category.name).like(search_pattern),
                    func.lower(Category.description).like(search_pattern),
                    func.lower(Category.value).like(search_pattern),
                )
            )
            .order_by(Category.name.asc())
        )
        return list(session.scalars(statement))

    @staticmethod
    def FilterCategories(session: Session, status: str | None = None) -> list["Category"]:
        statement = select(Category)
        if status:
            statement = statement.where(Category.status == status)
        statement = statement.order_by(Category.name.asc())
        return list(session.scalars(statement))

    @staticmethod
    def UpdateCategory(category: "Category", name: str, description: str, status: str) -> None:
        category.name = name.strip()
        category.description = description.strip()
        category.status = status
        category.updated_at = now_dt()

    @staticmethod
    def SaveCategoryChanges(session: Session, category: "Category") -> None:
        session.add(category)

    @staticmethod
    def DeleteCategory(session: Session, category: "Category") -> None:
        session.delete(category)

    @staticmethod
    def SeedDefaultCategories(session: Session) -> bool:
        existing_values = set(session.scalars(select(Category.value)))
        has_changes = False
        for value, name in CAMPAIGN_CATEGORY_OPTIONS:
            if value in existing_values:
                continue
            Category.SaveCategory(
                session,
                Category(
                    value=value,
                    name=name,
                    description=f"Default FireflyFund category for {name.lower()} campaigns.",
                    status="active",
                    created_at=now_dt(),
                    updated_at=now_dt(),
                ),
            )
            has_changes = True
        return has_changes


class PlatformActivity:
    @staticmethod
    def _period_start(selected_date: date) -> datetime:
        return datetime.combine(selected_date, time.min, tzinfo=now_dt().tzinfo)

    @staticmethod
    def _activity_data(session: Session, start_at: datetime, end_at: datetime) -> dict[str, object]:
        users_created = int(
            session.scalar(
                select(func.count(UserAccount.id)).where(
                    UserAccount.created_at >= start_at,
                    UserAccount.created_at < end_at,
                )
            )
            or 0
        )
        campaigns_created = int(
            session.scalar(
                select(func.count(FundraisingCampaign.id)).where(
                    FundraisingCampaign.created_at >= start_at,
                    FundraisingCampaign.created_at < end_at,
                )
            )
            or 0
        )
        campaigns_published = int(
            session.scalar(
                select(func.count(FundraisingCampaign.id)).where(
                    FundraisingCampaign.published_at >= start_at,
                    FundraisingCampaign.published_at < end_at,
                )
            )
            or 0
        )
        donations_count = int(
            session.scalar(
                select(func.count(DonationRecord.id)).where(
                    DonationRecord.donated_at >= start_at,
                    DonationRecord.donated_at < end_at,
                )
            )
            or 0
        )
        donation_amount = int(
            session.scalar(
                select(func.coalesce(func.sum(DonationRecord.amount), 0)).where(
                    DonationRecord.donated_at >= start_at,
                    DonationRecord.donated_at < end_at,
                )
            )
            or 0
        )
        favourites_count = int(
            session.scalar(
                select(func.count(FavouriteCampaign.id)).where(
                    FavouriteCampaign.created_at >= start_at,
                    FavouriteCampaign.created_at < end_at,
                )
            )
            or 0
        )
        views_count = int(
            session.scalar(
                select(func.count(CampaignViewRecord.id)).where(
                    CampaignViewRecord.viewed_at >= start_at,
                    CampaignViewRecord.viewed_at < end_at,
                )
            )
            or 0
        )
        return {
            "period_start": start_at,
            "period_end": end_at,
            "users_created": users_created,
            "campaigns_created": campaigns_created,
            "campaigns_published": campaigns_published,
            "donations_count": donations_count,
            "donation_amount": donation_amount,
            "favourites_count": favourites_count,
            "views_count": views_count,
        }

    @staticmethod
    def _donation_rows(
        session: Session, start_at: datetime, end_at: datetime
    ) -> list[tuple[DonationRecord, FundraisingCampaign | None]]:
        statement = (
            select(DonationRecord, FundraisingCampaign)
            .join(FundraisingCampaign, FundraisingCampaign.id == DonationRecord.campaign_id, isouter=True)
            .where(DonationRecord.donated_at >= start_at, DonationRecord.donated_at < end_at)
        )
        return list(session.execute(statement).all())

    @staticmethod
    def _top_donation_category(
        session: Session, start_at: datetime, end_at: datetime
    ) -> dict[str, object]:
        category_totals: dict[str, dict[str, int | str]] = {}
        for donation_record, _campaign in PlatformActivity._donation_rows(session, start_at, end_at):
            category = donation_record.campaign_category or "other"
            current = category_totals.setdefault(
                category, {"category": category, "donation_amount": 0, "donations_count": 0}
            )
            current["donation_amount"] = int(current["donation_amount"]) + int(donation_record.amount or 0)
            current["donations_count"] = int(current["donations_count"]) + 1
        if not category_totals:
            return {"category": "N/A", "donation_amount": 0, "donations_count": 0}
        return max(
            category_totals.values(),
            key=lambda item: (int(item["donation_amount"]), int(item["donations_count"])),
        )

    @staticmethod
    def _top_donation_campaign(
        session: Session, start_at: datetime, end_at: datetime
    ) -> dict[str, object]:
        campaign_totals: dict[int, dict[str, int | str]] = {}
        for donation_record, campaign in PlatformActivity._donation_rows(session, start_at, end_at):
            campaign_id = int(donation_record.campaign_id)
            current = campaign_totals.setdefault(
                campaign_id,
                {
                    "campaign_id": campaign_id,
                    "title": campaign.title if campaign else f"Campaign #{campaign_id}",
                    "donation_amount": 0,
                    "donations_count": 0,
                },
            )
            current["donation_amount"] = int(current["donation_amount"]) + int(donation_record.amount or 0)
            current["donations_count"] = int(current["donations_count"]) + 1
        if not campaign_totals:
            return {"campaign_id": None, "title": "N/A", "donation_amount": 0, "donations_count": 0}
        return max(
            campaign_totals.values(),
            key=lambda item: (int(item["donation_amount"]), int(item["donations_count"])),
        )

    @staticmethod
    def _most_viewed_campaign(
        session: Session, start_at: datetime, end_at: datetime
    ) -> dict[str, object]:
        statement = (
            select(FundraisingCampaign.title, func.count(CampaignViewRecord.id).label("view_total"))
            .join(FundraisingCampaign, FundraisingCampaign.id == CampaignViewRecord.campaign_id)
            .where(CampaignViewRecord.viewed_at >= start_at, CampaignViewRecord.viewed_at < end_at)
            .group_by(FundraisingCampaign.id, FundraisingCampaign.title)
            .order_by(func.count(CampaignViewRecord.id).desc(), FundraisingCampaign.title.asc())
            .limit(1)
        )
        row = session.execute(statement).first()
        if not row:
            return {"title": "N/A", "views_count": 0}
        return {"title": row[0], "views_count": int(row[1] or 0)}

    @staticmethod
    def _daily_trend_rows(
        session: Session, start_at: datetime, end_at: datetime
    ) -> list[dict[str, object]]:
        day_count = max(1, (end_at.date() - start_at.date()).days)
        rows: list[dict[str, object]] = []
        for day_offset in range(day_count):
            day_start = start_at + timedelta(days=day_offset)
            day_end = day_start + timedelta(days=1)
            day_data = PlatformActivity._activity_data(session, day_start, day_end)
            rows.append(
                {
                    "date": day_start.date().isoformat(),
                    "label": day_start.strftime("%a %m/%d"),
                    "donations_count": day_data["donations_count"],
                    "donation_amount": day_data["donation_amount"],
                    "views_count": day_data["views_count"],
                    "users_created": day_data["users_created"],
                }
            )
        return rows

    @staticmethod
    def _monthly_success_rate(session: Session, period_end: datetime) -> float:
        published_campaigns = list(
            session.scalars(
                select(FundraisingCampaign).where(
                    FundraisingCampaign.status == "published",
                    FundraisingCampaign.published_at < period_end,
                )
            )
        )
        if not published_campaigns:
            return 0.0
        successful_campaigns = [
            campaign
            for campaign in published_campaigns
            if campaign.goal_amount and int(campaign.amount_raised or 0) >= int(campaign.goal_amount)
        ]
        return round((len(successful_campaigns) / len(published_campaigns)) * 100, 1)

    @staticmethod
    def GetDailyActivityData(session: Session, selected_day: date | None = None) -> dict[str, object]:
        start_at = (
            PlatformActivity._period_start(selected_day)
            if selected_day
            else now_dt().replace(hour=0, minute=0, second=0, microsecond=0)
        )
        return PlatformActivity._activity_data(session, start_at, start_at + timedelta(days=1))

    @staticmethod
    def GetWeeklyActivityData(
        session: Session,
        selected_week_start: date | None = None,
        selected_week_end: date | None = None,
    ) -> dict[str, object]:
        start_at = (
            PlatformActivity._period_start(selected_week_start)
            if selected_week_start
            else (now_dt() - timedelta(days=now_dt().weekday())).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        )
        end_at = (
            PlatformActivity._period_start(selected_week_end) + timedelta(days=1)
            if selected_week_end
            else start_at + timedelta(days=7)
        )
        data = PlatformActivity._activity_data(session, start_at, end_at)
        data["daily_trend_rows"] = PlatformActivity._daily_trend_rows(session, start_at, end_at)
        data["best_performing_category"] = PlatformActivity._top_donation_category(session, start_at, end_at)
        data["most_viewed_campaign"] = PlatformActivity._most_viewed_campaign(session, start_at, end_at)
        return data

    @staticmethod
    def GetMonthlyPerformanceData(
        session: Session, selected_month_start: date | None = None
    ) -> dict[str, object]:
        start_at = (
            PlatformActivity._period_start(selected_month_start)
            if selected_month_start
            else now_dt().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        )
        if start_at.month == 12:
            end_at = start_at.replace(year=start_at.year + 1, month=1)
        else:
            end_at = start_at.replace(month=start_at.month + 1)
        data = PlatformActivity._activity_data(session, start_at, end_at)
        donations_count = int(data["donations_count"] or 0)
        donation_amount = int(data["donation_amount"] or 0)
        donor_participation = int(
            session.scalar(
                select(func.count(func.distinct(DonationRecord.user_id))).where(
                    DonationRecord.donated_at >= start_at,
                    DonationRecord.donated_at < end_at,
                )
            )
            or 0
        )
        supported_campaigns = int(
            session.scalar(
                select(func.count(func.distinct(DonationRecord.campaign_id))).where(
                    DonationRecord.donated_at >= start_at,
                    DonationRecord.donated_at < end_at,
                )
            )
            or 0
        )
        data["average_donation_amount"] = round(donation_amount / donations_count, 2) if donations_count else 0
        data["top_category_by_donation"] = PlatformActivity._top_donation_category(session, start_at, end_at)
        data["top_campaign_by_donation"] = PlatformActivity._top_donation_campaign(session, start_at, end_at)
        data["campaign_success_rate"] = PlatformActivity._monthly_success_rate(session, end_at)
        data["user_growth"] = data["users_created"]
        data["donor_participation"] = donor_participation
        data["supported_campaigns"] = supported_campaigns
        return data


@dataclass(frozen=True)
class GeneratedReport:
    report_type: str
    title: str
    data: dict[str, object]


class DailyReport:
    @staticmethod
    def GenerateReport(activity_data: dict[str, object]) -> GeneratedReport:
        return GeneratedReport("daily", "Daily Platform Activity Report", activity_data)

    @staticmethod
    def GetReport(report: GeneratedReport) -> GeneratedReport:
        return report

    @staticmethod
    def ExportReport(report: GeneratedReport) -> str:
        return _export_report_csv(report)


class WeeklyReport:
    @staticmethod
    def GenerateReport(activity_data: dict[str, object]) -> GeneratedReport:
        return GeneratedReport("weekly", "Weekly Platform Trend Report", activity_data)

    @staticmethod
    def GetReport(report: GeneratedReport) -> GeneratedReport:
        return report

    @staticmethod
    def ExportReport(report: GeneratedReport) -> str:
        return _export_report_csv(report)


class MonthlyReport:
    @staticmethod
    def GenerateReport(activity_data: dict[str, object]) -> GeneratedReport:
        return GeneratedReport("monthly", "Monthly Platform Performance Report", activity_data)

    @staticmethod
    def GetReport(report: GeneratedReport) -> GeneratedReport:
        return report

    @staticmethod
    def ExportReport(report: GeneratedReport) -> str:
        return _export_report_csv(report)


def _export_report_csv(report: GeneratedReport) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Report Type", report.report_type])
    writer.writerow(["Report Title", report.title])
    writer.writerow([])
    writer.writerow(["Metric", "Value"])
    for key, value in report.data.items():
        if isinstance(value, list):
            writer.writerow([])
            writer.writerow([key])
            if value and isinstance(value[0], dict):
                headers = list(value[0].keys())
                writer.writerow(headers)
                for item in value:
                    writer.writerow([item.get(header, "") for header in headers])
            else:
                for item in value:
                    writer.writerow([item])
            continue
        if isinstance(value, dict):
            writer.writerow([])
            writer.writerow([key])
            for nested_key, nested_value in value.items():
                writer.writerow([nested_key, nested_value])
            continue
        writer.writerow([key, value])
    return output.getvalue()
