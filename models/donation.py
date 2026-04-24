from datetime import datetime, timedelta

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, delete, func, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from core.config import DEFAULT_DONATION_DATE_PERIOD
from core.security import now_dt
from models import Base
from models.campaign import FundraisingCampaign


class DonationRecord(Base):
    __tablename__ = "donation_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("fundraising_campaigns.id"), nullable=False, index=True
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    campaign_category: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    donated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    @staticmethod
    def CreateDonationRecord(
        user_id: int,
        campaign_id: int,
        amount: int,
        campaign_category: str,
    ) -> "DonationRecord":
        return DonationRecord(
            user_id=user_id,
            campaign_id=campaign_id,
            amount=int(amount),
            campaign_category=campaign_category,
            donated_at=now_dt(),
        )

    @staticmethod
    def SaveDonationRecord(session: Session, donation_record: "DonationRecord") -> None:
        session.add(donation_record)

    @staticmethod
    def GetDonationRecords(session: Session, user_id: int) -> list["DonationRecord"]:
        statement = (
            select(DonationRecord)
            .where(DonationRecord.user_id == user_id)
            .order_by(DonationRecord.donated_at.desc(), DonationRecord.id.desc())
        )
        return list(session.scalars(statement))

    @staticmethod
    def GetDonationById(
        session: Session, user_id: int, donation_id: int
    ) -> "DonationRecord | None":
        statement = select(DonationRecord).where(
            DonationRecord.user_id == user_id,
            DonationRecord.id == donation_id,
        )
        return session.scalar(statement)

    @staticmethod
    def FilterByCategory(
        session: Session,
        user_id: int,
        category: str | None,
        date_period: str = DEFAULT_DONATION_DATE_PERIOD,
    ) -> list["DonationRecord"]:
        return DonationRecord.GetFilteredDonations(
            session,
            user_id,
            category=category,
            date_period=date_period,
        )

    @staticmethod
    def FilterByDatePeriod(
        session: Session,
        user_id: int,
        date_period: str,
        category: str | None = None,
    ) -> list["DonationRecord"]:
        return DonationRecord.GetFilteredDonations(
            session,
            user_id,
            category=category,
            date_period=date_period,
        )

    @staticmethod
    def GetFilteredDonations(
        session: Session,
        user_id: int,
        category: str | None = None,
        date_period: str = DEFAULT_DONATION_DATE_PERIOD,
    ) -> list["DonationRecord"]:
        statement = select(DonationRecord).where(DonationRecord.user_id == user_id)
        if category:
            statement = statement.where(DonationRecord.campaign_category == category)

        period_start = DonationRecord._resolve_period_start(date_period)
        if period_start:
            statement = statement.where(DonationRecord.donated_at >= period_start)

        statement = statement.order_by(DonationRecord.donated_at.desc(), DonationRecord.id.desc())
        return list(session.scalars(statement))

    @staticmethod
    def GetSupportedCampaigns(session: Session, user_id: int) -> list[FundraisingCampaign]:
        latest_support_subquery = (
            select(
                DonationRecord.campaign_id,
                func.max(DonationRecord.donated_at).label("latest_donated_at"),
            )
            .where(DonationRecord.user_id == user_id)
            .group_by(DonationRecord.campaign_id)
            .subquery()
        )
        statement = (
            select(FundraisingCampaign)
            .join(
                latest_support_subquery,
                latest_support_subquery.c.campaign_id == FundraisingCampaign.id,
            )
            .order_by(latest_support_subquery.c.latest_donated_at.desc())
        )
        return list(session.scalars(statement))

    @staticmethod
    def GetTotalDonationAmount(session: Session, user_id: int) -> int:
        statement = select(func.coalesce(func.sum(DonationRecord.amount), 0)).where(
            DonationRecord.user_id == user_id
        )
        return int(session.scalar(statement) or 0)

    @staticmethod
    def DeleteUserDonationRecords(session: Session, user_id: int) -> None:
        session.execute(delete(DonationRecord).where(DonationRecord.user_id == user_id))

    @staticmethod
    def DeleteCampaignDonationRecords(session: Session, campaign_id: int) -> None:
        session.execute(delete(DonationRecord).where(DonationRecord.campaign_id == campaign_id))

    @staticmethod
    def _resolve_period_start(date_period: str | None) -> datetime | None:
        clean_period = (date_period or DEFAULT_DONATION_DATE_PERIOD).strip().lower()
        current_time = now_dt()
        if clean_period == "7d":
            return current_time - timedelta(days=7)
        if clean_period == "30d":
            return current_time - timedelta(days=30)
        if clean_period == "90d":
            return current_time - timedelta(days=90)
        if clean_period == "year":
            return current_time.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        return None


class FavouriteCampaign(Base):
    __tablename__ = "favourite_campaigns"
    __table_args__ = (
        UniqueConstraint("user_id", "campaign_id", name="uq_favourite_campaign_user_campaign"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("fundraising_campaigns.id"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @staticmethod
    def AddToFavourite(user_id: int, campaign_id: int) -> "FavouriteCampaign":
        return FavouriteCampaign(
            user_id=user_id,
            campaign_id=campaign_id,
            created_at=now_dt(),
        )

    @staticmethod
    def SaveFavouriteRecord(session: Session, favourite_record: "FavouriteCampaign") -> None:
        session.add(favourite_record)

    @staticmethod
    def GetFavouriteRecord(
        session: Session, user_id: int, campaign_id: int
    ) -> "FavouriteCampaign | None":
        statement = select(FavouriteCampaign).where(
            FavouriteCampaign.user_id == user_id,
            FavouriteCampaign.campaign_id == campaign_id,
        )
        return session.scalar(statement)

    @staticmethod
    def RemoveFromFavourite(
        session: Session, user_id: int, campaign_id: int
    ) -> "FavouriteCampaign | None":
        return FavouriteCampaign.GetFavouriteRecord(session, user_id, campaign_id)

    @staticmethod
    def DeleteFavouriteRecord(session: Session, favourite_record: "FavouriteCampaign") -> None:
        session.delete(favourite_record)

    @staticmethod
    def GetFavouriteCampaigns(session: Session, user_id: int) -> list[FundraisingCampaign]:
        statement = (
            select(FundraisingCampaign)
            .join(
                FavouriteCampaign,
                FavouriteCampaign.campaign_id == FundraisingCampaign.id,
            )
            .where(
                FavouriteCampaign.user_id == user_id,
                FundraisingCampaign.status == "published",
            )
            .order_by(FavouriteCampaign.created_at.desc(), FundraisingCampaign.published_at.desc())
        )
        return list(session.scalars(statement))

    @staticmethod
    def GetFavouriteCampaignById(
        session: Session, user_id: int, campaign_id: int
    ) -> FundraisingCampaign | None:
        statement = (
            select(FundraisingCampaign)
            .join(
                FavouriteCampaign,
                FavouriteCampaign.campaign_id == FundraisingCampaign.id,
            )
            .where(
                FavouriteCampaign.user_id == user_id,
                FavouriteCampaign.campaign_id == campaign_id,
                FundraisingCampaign.status == "published",
            )
        )
        return session.scalar(statement)

    @staticmethod
    def GetFavouriteCampaignIds(session: Session, user_id: int) -> set[int]:
        statement = select(FavouriteCampaign.campaign_id).where(FavouriteCampaign.user_id == user_id)
        return set(session.scalars(statement))

    @staticmethod
    def GetShortlistCount(session: Session, campaign_id: int) -> int:
        statement = select(func.count(FavouriteCampaign.id)).where(
            FavouriteCampaign.campaign_id == campaign_id
        )
        return int(session.scalar(statement) or 0)

    @staticmethod
    def GetShortlistStatistics(session: Session, owner_id: int) -> list[tuple[int, int]]:
        statement = (
            select(FundraisingCampaign.id, func.count(FavouriteCampaign.id))
            .join(FavouriteCampaign, FavouriteCampaign.campaign_id == FundraisingCampaign.id, isouter=True)
            .where(FundraisingCampaign.owner_id == owner_id)
            .group_by(FundraisingCampaign.id)
        )
        return [(campaign_id, int(count or 0)) for campaign_id, count in session.execute(statement).all()]

    @staticmethod
    def GetInterestDetails(session: Session, campaign_id: int) -> dict[str, object]:
        statement = (
            select(FavouriteCampaign)
            .where(FavouriteCampaign.campaign_id == campaign_id)
            .order_by(FavouriteCampaign.created_at.desc(), FavouriteCampaign.id.desc())
        )
        shortlist_records = list(session.scalars(statement))
        return {
            "shortlist_count": len(shortlist_records),
            "latest_shortlisted_at": shortlist_records[0].created_at.isoformat()
            if shortlist_records
            else None,
        }

    @staticmethod
    def DeleteUserFavouriteRecords(session: Session, user_id: int) -> None:
        session.execute(delete(FavouriteCampaign).where(FavouriteCampaign.user_id == user_id))

    @staticmethod
    def DeleteCampaignFavouriteRecords(session: Session, campaign_id: int) -> None:
        session.execute(delete(FavouriteCampaign).where(FavouriteCampaign.campaign_id == campaign_id))
