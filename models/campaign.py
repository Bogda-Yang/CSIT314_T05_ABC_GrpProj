from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, delete, func, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from core.config import (
    CAMPAIGN_IMAGE_DIR,
    DEFAULT_CAMPAIGN_CATEGORY,
    DEFAULT_DASHBOARD_REVIEW_SORT,
    SUPABASE_CAMPAIGN_BUCKET,
)
from core.security import now_dt
from core.storage import delete_uploaded_asset
from models import Base


class FundraisingCampaign(Base):
    __tablename__ = "fundraising_campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    category: Mapped[str] = mapped_column(
        String(40), nullable=False, default=DEFAULT_CAMPAIGN_CATEGORY, index=True
    )
    goal_amount: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    deadline: Mapped[str | None] = mapped_column(String(10), nullable=True)
    workflow_stage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    @staticmethod
    def CreateCampaign(owner_id: int, title: str, category: str) -> "FundraisingCampaign":
        clean_title = title.strip()
        return FundraisingCampaign(
            owner_id=owner_id,
            title=clean_title,
            category=category,
            goal_amount=None,
            description="",
            deadline=None,
            workflow_stage=0,
            status="draft",
            created_at=now_dt(),
            updated_at=now_dt(),
            submitted_at=None,
            reviewed_at=None,
            published_at=None,
        )

    @staticmethod
    def SaveCampaignDraft(session: Session, campaign: "FundraisingCampaign") -> None:
        session.add(campaign)

    @staticmethod
    def GetCampaignDetails(session: Session, campaign_id: int) -> "FundraisingCampaign | None":
        return session.get(FundraisingCampaign, campaign_id)

    @staticmethod
    def GetCampaignById(session: Session, campaign_id: int) -> "FundraisingCampaign | None":
        return session.get(FundraisingCampaign, campaign_id)

    @staticmethod
    def GetCampaignsByOwner(session: Session, owner_id: int) -> list["FundraisingCampaign"]:
        statement = (
            select(FundraisingCampaign)
            .where(FundraisingCampaign.owner_id == owner_id)
            .order_by(FundraisingCampaign.updated_at.desc(), FundraisingCampaign.created_at.desc())
        )
        return list(session.scalars(statement))

    @staticmethod
    def GetPublishedCampaigns(
        session: Session, category: str | None = None
    ) -> list["FundraisingCampaign"]:
        statement = select(FundraisingCampaign).where(FundraisingCampaign.status == "published")
        if category:
            statement = statement.where(FundraisingCampaign.category == category)
        statement = statement.order_by(
            FundraisingCampaign.published_at.desc(), FundraisingCampaign.updated_at.desc()
        )
        return list(session.scalars(statement))

    @staticmethod
    def UpdateCampaign(campaign: "FundraisingCampaign", title: str, category: str) -> None:
        campaign.title = title.strip()
        campaign.category = category
        campaign.updated_at = now_dt()
        if campaign.status != "draft":
            campaign.status = "draft"
            campaign.submitted_at = None
            campaign.reviewed_at = None
            campaign.published_at = None

    @staticmethod
    def SaveCampaignChanges(session: Session, campaign: "FundraisingCampaign") -> None:
        campaign.updated_at = now_dt()
        session.add(campaign)

    @staticmethod
    def AdvanceWorkflowStage(campaign: "FundraisingCampaign", stage: int) -> None:
        campaign.workflow_stage = max(campaign.workflow_stage or 0, stage)
        campaign.updated_at = now_dt()

    @staticmethod
    def DeleteCampaign(session: Session, campaign: "FundraisingCampaign") -> None:
        session.delete(campaign)

    @staticmethod
    def SubmitCampaign(campaign: "FundraisingCampaign") -> None:
        campaign.submitted_at = now_dt()
        campaign.updated_at = now_dt()

    @staticmethod
    def GetPendingCampaigns(
        session: Session,
        category: str | None = None,
        sort_order: str = DEFAULT_DASHBOARD_REVIEW_SORT,
    ) -> list["FundraisingCampaign"]:
        statement = select(FundraisingCampaign).where(FundraisingCampaign.status == "pending")
        if category:
            statement = statement.where(FundraisingCampaign.category == category)

        if sort_order == "time_desc":
            statement = statement.order_by(
                FundraisingCampaign.submitted_at.desc(),
                FundraisingCampaign.updated_at.desc(),
                FundraisingCampaign.created_at.desc(),
            )
        elif sort_order == "amount_asc":
            statement = statement.order_by(
                func.coalesce(FundraisingCampaign.goal_amount, 0).asc(),
                FundraisingCampaign.submitted_at.asc(),
                FundraisingCampaign.updated_at.asc(),
            )
        elif sort_order == "amount_desc":
            statement = statement.order_by(
                func.coalesce(FundraisingCampaign.goal_amount, 0).desc(),
                FundraisingCampaign.submitted_at.asc(),
                FundraisingCampaign.updated_at.asc(),
            )
        else:
            statement = statement.order_by(
                FundraisingCampaign.submitted_at.asc(),
                FundraisingCampaign.updated_at.asc(),
                FundraisingCampaign.created_at.asc(),
            )
        return list(session.scalars(statement))

    @staticmethod
    def UpdateCampaignStatus(session: Session, campaign: "FundraisingCampaign", status: str) -> None:
        campaign.status = status
        campaign.updated_at = now_dt()
        session.add(campaign)

    @staticmethod
    def PublishCampaign(session: Session, campaign: "FundraisingCampaign") -> None:
        campaign.published_at = now_dt()
        campaign.updated_at = now_dt()
        session.add(campaign)

    @staticmethod
    def GetStatusCounts(session: Session) -> dict[str, int]:
        statement = (
            select(FundraisingCampaign.status, func.count(FundraisingCampaign.id))
            .group_by(FundraisingCampaign.status)
        )
        return {status: count for status, count in session.execute(statement).all()}


class CampaignImage(Base):
    __tablename__ = "campaign_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("fundraising_campaigns.id"), nullable=False, index=True
    )
    image_path: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @staticmethod
    def StoreImages(campaign_id: int, image_paths: list[str]) -> list["CampaignImage"]:
        return [
            CampaignImage(
                campaign_id=campaign_id,
                image_path=image_path,
                created_at=now_dt(),
            )
            for image_path in image_paths
        ]

    @staticmethod
    def SaveImageRecords(session: Session, image_records: list["CampaignImage"]) -> None:
        session.add_all(image_records)

    @staticmethod
    def GetImageDetails(session: Session, campaign_id: int) -> list["CampaignImage"]:
        statement = (
            select(CampaignImage)
            .where(CampaignImage.campaign_id == campaign_id)
            .order_by(CampaignImage.created_at.asc(), CampaignImage.id.asc())
        )
        return list(session.scalars(statement))

    @staticmethod
    def DeleteImageRecords(session: Session, campaign_id: int) -> None:
        image_records = CampaignImage.GetImageDetails(session, campaign_id)
        for record in image_records:
            delete_uploaded_asset(
                SUPABASE_CAMPAIGN_BUCKET, CAMPAIGN_IMAGE_DIR, record.image_path
            )
        session.execute(delete(CampaignImage).where(CampaignImage.campaign_id == campaign_id))

    @staticmethod
    def GetImageRecord(
        session: Session, campaign_id: int, image_id: int
    ) -> "CampaignImage | None":
        statement = select(CampaignImage).where(
            CampaignImage.campaign_id == campaign_id,
            CampaignImage.id == image_id,
        )
        return session.scalar(statement)

    @staticmethod
    def DeleteImageRecord(session: Session, image_record: "CampaignImage") -> None:
        delete_uploaded_asset(
            SUPABASE_CAMPAIGN_BUCKET, CAMPAIGN_IMAGE_DIR, image_record.image_path
        )
        session.delete(image_record)


class RejectionRecord(Base):
    __tablename__ = "rejection_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("fundraising_campaigns.id"), nullable=False, index=True
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @staticmethod
    def SaveRejectionReason(session: Session, campaign_id: int, reason: str) -> "RejectionRecord":
        record = RejectionRecord(
            campaign_id=campaign_id,
            reason=reason.strip(),
            created_at=now_dt(),
        )
        session.add(record)
        return record

    @staticmethod
    def GetRejectionReason(session: Session, campaign_id: int) -> "RejectionRecord | None":
        statement = (
            select(RejectionRecord)
            .where(RejectionRecord.campaign_id == campaign_id)
            .order_by(RejectionRecord.created_at.desc(), RejectionRecord.id.desc())
        )
        return session.scalar(statement)

    @staticmethod
    def DeleteCampaignRejectionRecords(session: Session, campaign_id: int) -> None:
        session.execute(delete(RejectionRecord).where(RejectionRecord.campaign_id == campaign_id))


class CampaignGoal:
    @staticmethod
    def SetGoal(campaign: FundraisingCampaign, goal_amount: int) -> None:
        campaign.goal_amount = goal_amount
        campaign.updated_at = now_dt()
        if campaign.status != "draft":
            campaign.status = "draft"
            campaign.submitted_at = None
            campaign.reviewed_at = None
            campaign.published_at = None

    @staticmethod
    def SaveGoal(session: Session, campaign: FundraisingCampaign) -> None:
        session.add(campaign)

    @staticmethod
    def GetGoalDetails(campaign: FundraisingCampaign) -> dict[str, int | None]:
        return {"goal_amount": campaign.goal_amount}


class CampaignDescription:
    @staticmethod
    def SetDescription(campaign: FundraisingCampaign, description: str) -> None:
        campaign.description = description.strip()
        campaign.updated_at = now_dt()
        if campaign.status != "draft":
            campaign.status = "draft"
            campaign.submitted_at = None
            campaign.reviewed_at = None
            campaign.published_at = None

    @staticmethod
    def SaveDescription(session: Session, campaign: FundraisingCampaign) -> None:
        session.add(campaign)

    @staticmethod
    def GetDescriptionDetails(campaign: FundraisingCampaign) -> dict[str, str]:
        return {"description": campaign.description}


class CampaignDeadline:
    @staticmethod
    def SetDeadline(campaign: FundraisingCampaign, deadline: str) -> None:
        campaign.deadline = deadline
        campaign.updated_at = now_dt()
        if campaign.status != "draft":
            campaign.status = "draft"
            campaign.submitted_at = None
            campaign.reviewed_at = None
            campaign.published_at = None

    @staticmethod
    def SaveDeadline(session: Session, campaign: FundraisingCampaign) -> None:
        session.add(campaign)

    @staticmethod
    def GetDeadlineDetails(campaign: FundraisingCampaign) -> dict[str, str | None]:
        return {"deadline": campaign.deadline}


class CampaignStatus:
    @staticmethod
    def SetPending(campaign: FundraisingCampaign) -> None:
        campaign.status = "pending"
        campaign.submitted_at = now_dt()
        campaign.updated_at = now_dt()

    @staticmethod
    def SetApproved(campaign: FundraisingCampaign) -> None:
        campaign.status = "approved"
        campaign.reviewed_at = now_dt()
        campaign.updated_at = now_dt()

    @staticmethod
    def SetPublished(campaign: FundraisingCampaign) -> None:
        campaign.status = "published"
        campaign.published_at = now_dt()
        campaign.updated_at = now_dt()

    @staticmethod
    def GetStatus(campaign: FundraisingCampaign) -> str:
        return campaign.status

    @staticmethod
    def GetStatusDetails(
        session: Session, campaign: FundraisingCampaign
    ) -> dict[str, str | None]:
        rejection_record = RejectionRecord.GetRejectionReason(session, campaign.id)
        return {
            "status": campaign.status,
            "submitted_at": campaign.submitted_at.isoformat() if campaign.submitted_at else None,
            "published_at": campaign.published_at.isoformat() if campaign.published_at else None,
            "reviewed_at": campaign.reviewed_at.isoformat() if campaign.reviewed_at else None,
            "rejection_reason": (
                rejection_record.reason if rejection_record and campaign.status == "rejected" else None
            ),
        }
