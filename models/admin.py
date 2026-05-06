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
    def SeedDefaultCategories(session: Session) -> None:
        existing_values = set(session.scalars(select(Category.value)))
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
        return PlatformActivity._activity_data(session, start_at, end_at)

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
        return PlatformActivity._activity_data(session, start_at, end_at)


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
        writer.writerow([key, value])
    return output.getvalue()
