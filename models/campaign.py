from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, delete, func, or_, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from core.config import (
    CAMPAIGN_IMAGE_DIR,
    DEFAULT_CAMPAIGN_CATEGORY,
    DEFAULT_DONEE_CAMPAIGN_SORT,
    DEFAULT_DASHBOARD_REVIEW_SORT,
    DEFAULT_FUNDRAISER_CAMPAIGN_SORT,
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
    amount_raised: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
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
            amount_raised=0,
            view_count=0,
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
            .where(
                FundraisingCampaign.owner_id == owner_id,
                FundraisingCampaign.status != "deleted",
            )
            .order_by(FundraisingCampaign.updated_at.desc(), FundraisingCampaign.created_at.desc())
        )
        return list(session.scalars(statement))

    @staticmethod
    def GetPublishedCampaigns(
        session: Session,
        category: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list["FundraisingCampaign"]:
        statement = FundraisingCampaign._build_donee_campaigns_statement(
            category=category,
            sort_order=DEFAULT_DONEE_CAMPAIGN_SORT,
        )
        statement = FundraisingCampaign._apply_pagination(statement, limit, offset)
        return list(session.scalars(statement))

    @staticmethod
    def SearchCampaigns(
        session: Session,
        search_keywords: str,
        category: str | None = None,
        sort_order: str = DEFAULT_DONEE_CAMPAIGN_SORT,
        limit: int | None = None,
        offset: int = 0,
    ) -> list["FundraisingCampaign"]:
        return FundraisingCampaign.GetMatchingCampaigns(
            session,
            search_keywords,
            category=category,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def GetMatchingCampaigns(
        session: Session,
        search_keywords: str,
        category: str | None = None,
        sort_order: str = DEFAULT_DONEE_CAMPAIGN_SORT,
        limit: int | None = None,
        offset: int = 0,
    ) -> list["FundraisingCampaign"]:
        clean_keywords = (search_keywords or "").strip().lower()
        statement = FundraisingCampaign._build_donee_campaigns_statement(
            category=category,
            sort_order=sort_order,
        )
        if clean_keywords:
            search_pattern = f"%{clean_keywords}%"
            statement = statement.where(
                or_(
                    func.lower(FundraisingCampaign.title).like(search_pattern),
                    func.lower(FundraisingCampaign.description).like(search_pattern),
                    func.lower(FundraisingCampaign.category).like(search_pattern),
                )
            )
        statement = FundraisingCampaign._apply_pagination(statement, limit, offset)
        return list(session.scalars(statement))

    @staticmethod
    def FilterCampaigns(
        session: Session,
        category: str | None = None,
        sort_order: str = DEFAULT_DONEE_CAMPAIGN_SORT,
        search_keywords: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list["FundraisingCampaign"]:
        return FundraisingCampaign.GetFilteredCampaigns(
            session,
            category=category,
            sort_order=sort_order,
            search_keywords=search_keywords,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def GetFilteredCampaigns(
        session: Session,
        category: str | None = None,
        sort_order: str = DEFAULT_DONEE_CAMPAIGN_SORT,
        search_keywords: str | None = None,
        owner_id: int | None = None,
        lifecycle: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list["FundraisingCampaign"]:
        if owner_id is not None:
            campaigns = FundraisingCampaign.GetCampaignsByOwner(session, owner_id)
            if category:
                campaigns = [campaign for campaign in campaigns if campaign.category == category]
            if search_keywords and search_keywords.strip():
                search_pattern = search_keywords.strip().lower()
                campaigns = [
                    campaign
                    for campaign in campaigns
                    if search_pattern in campaign.title.lower()
                    or search_pattern in campaign.description.lower()
                    or search_pattern in campaign.category.lower()
                ]
            if lifecycle and lifecycle != "all":
                campaigns = [
                    campaign
                    for campaign in campaigns
                    if FundraisingCampaign.MatchesLifecycle(campaign, lifecycle)
                ]
            return FundraisingCampaign.SortOwnerCampaigns(session, campaigns, sort_order)

        clean_keywords = (search_keywords or "").strip().lower()
        statement = FundraisingCampaign._build_donee_campaigns_statement(
            category=category,
            sort_order=sort_order,
        )
        if clean_keywords:
            search_pattern = f"%{clean_keywords}%"
            statement = statement.where(
                or_(
                    func.lower(FundraisingCampaign.title).like(search_pattern),
                    func.lower(FundraisingCampaign.description).like(search_pattern),
                    func.lower(FundraisingCampaign.category).like(search_pattern),
                )
            )
        statement = FundraisingCampaign._apply_pagination(statement, limit, offset)
        return list(session.scalars(statement))

    @staticmethod
    def CountDoneeCampaigns(
        session: Session,
        category: str | None = None,
        search_keywords: str | None = None,
    ) -> int:
        statement = select(func.count(FundraisingCampaign.id)).where(
            FundraisingCampaign.status == "published"
        )
        if category:
            statement = statement.where(FundraisingCampaign.category == category)

        clean_keywords = (search_keywords or "").strip().lower()
        if clean_keywords:
            search_pattern = f"%{clean_keywords}%"
            statement = statement.where(
                or_(
                    func.lower(FundraisingCampaign.title).like(search_pattern),
                    func.lower(FundraisingCampaign.description).like(search_pattern),
                    func.lower(FundraisingCampaign.category).like(search_pattern),
                )
            )
        return int(session.scalar(statement) or 0)

    @staticmethod
    def RegisterCampaignView(campaign: "FundraisingCampaign") -> None:
        campaign.view_count = int(campaign.view_count or 0) + 1

    @staticmethod
    def AddRaisedAmount(campaign: "FundraisingCampaign", amount: int) -> None:
        campaign.amount_raised = int(campaign.amount_raised or 0) + int(amount)
        campaign.updated_at = now_dt()

    @staticmethod
    def IsCompleted(campaign: "FundraisingCampaign") -> bool:
        goal_reached = bool(campaign.goal_amount and campaign.amount_raised >= campaign.goal_amount)
        deadline_passed = False
        if campaign.deadline:
            try:
                deadline_passed = datetime.strptime(campaign.deadline, "%Y-%m-%d").date() < now_dt().date()
            except ValueError:
                deadline_passed = False
        return campaign.status == "published" and (goal_reached or deadline_passed)

    @staticmethod
    def MatchesLifecycle(campaign: "FundraisingCampaign", lifecycle: str) -> bool:
        if lifecycle == "completed":
            return FundraisingCampaign.IsCompleted(campaign)
        return campaign.status == lifecycle

    @staticmethod
    def SortOwnerCampaigns(
        session: Session,
        campaigns: list["FundraisingCampaign"],
        sort_order: str = DEFAULT_FUNDRAISER_CAMPAIGN_SORT,
    ) -> list["FundraisingCampaign"]:
        if sort_order == "updated_asc":
            return sorted(campaigns, key=lambda campaign: (campaign.updated_at, campaign.created_at))
        if sort_order == "views_desc":
            return sorted(
                campaigns,
                key=lambda campaign: (int(campaign.view_count or 0), campaign.updated_at, campaign.created_at),
                reverse=True,
            )
        if sort_order == "shortlists_desc":
            from models.donation import FavouriteCampaign

            shortlist_lookup = dict(FavouriteCampaign.GetShortlistStatistics(session, campaigns[0].owner_id)) if campaigns else {}
            return sorted(
                campaigns,
                key=lambda campaign: (
                    int(shortlist_lookup.get(campaign.id, 0)),
                    campaign.updated_at,
                    campaign.created_at,
                ),
                reverse=True,
            )
        if sort_order == "raised_desc":
            return sorted(
                campaigns,
                key=lambda campaign: (
                    int(campaign.amount_raised or 0),
                    campaign.updated_at,
                    campaign.created_at,
                ),
                reverse=True,
            )
        return sorted(
            campaigns,
            key=lambda campaign: (campaign.updated_at, campaign.created_at),
            reverse=True,
        )

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
    def MarkDeleted(
        campaign: "FundraisingCampaign", replacement_owner_id: int | None = None
    ) -> None:
        if replacement_owner_id is not None:
            campaign.owner_id = replacement_owner_id
        campaign.status = "deleted"
        campaign.submitted_at = None
        campaign.reviewed_at = None
        campaign.published_at = None
        campaign.updated_at = now_dt()

    @staticmethod
    def _build_donee_campaigns_statement(
        category: str | None = None,
        sort_order: str = DEFAULT_DONEE_CAMPAIGN_SORT,
    ):
        statement = select(FundraisingCampaign).where(FundraisingCampaign.status == "published")
        if category:
            statement = statement.where(FundraisingCampaign.category == category)

        if sort_order == "published_asc":
            statement = statement.order_by(
                FundraisingCampaign.published_at.asc(),
                FundraisingCampaign.updated_at.asc(),
                FundraisingCampaign.created_at.asc(),
            )
        elif sort_order == "goal_desc":
            statement = statement.order_by(
                func.coalesce(FundraisingCampaign.goal_amount, 0).desc(),
                FundraisingCampaign.published_at.desc(),
            )
        elif sort_order == "goal_asc":
            statement = statement.order_by(
                func.coalesce(FundraisingCampaign.goal_amount, 0).asc(),
                FundraisingCampaign.published_at.desc(),
            )
        else:
            statement = statement.order_by(
                FundraisingCampaign.published_at.desc(),
                FundraisingCampaign.updated_at.desc(),
                FundraisingCampaign.created_at.desc(),
            )
        return statement

    @staticmethod
    def _apply_pagination(statement, limit: int | None = None, offset: int = 0):
        if offset and offset > 0:
            statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        return statement

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
    def GetCampaignImages(session: Session, campaign_id: int) -> list["CampaignImage"]:
        return CampaignImage.GetImageDetails(session, campaign_id)

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
    def GetImageById(session: Session, image_id: int) -> "CampaignImage | None":
        return session.get(CampaignImage, image_id)

    @staticmethod
    def DeleteImageRecord(session: Session, image_record: "CampaignImage") -> None:
        delete_uploaded_asset(
            SUPABASE_CAMPAIGN_BUCKET, CAMPAIGN_IMAGE_DIR, image_record.image_path
        )
        session.delete(image_record)


class CampaignViewRecord(Base):
    __tablename__ = "campaign_view_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("fundraising_campaigns.id"), nullable=False, index=True
    )
    viewer_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    viewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    @staticmethod
    def RecordCampaignView(
        session: Session, campaign_id: int, viewer_user_id: int | None = None
    ) -> "CampaignViewRecord":
        record = CampaignViewRecord(
            campaign_id=campaign_id,
            viewer_user_id=viewer_user_id,
            viewed_at=now_dt(),
        )
        session.add(record)
        return record

    @staticmethod
    def GetCampaignViews(session: Session, campaign_id: int) -> list["CampaignViewRecord"]:
        statement = (
            select(CampaignViewRecord)
            .where(CampaignViewRecord.campaign_id == campaign_id)
            .order_by(CampaignViewRecord.viewed_at.desc(), CampaignViewRecord.id.desc())
        )
        return list(session.scalars(statement))

    @staticmethod
    def GetCampaignViewCount(session: Session, campaign_id: int) -> int:
        statement = select(func.count(CampaignViewRecord.id)).where(
            CampaignViewRecord.campaign_id == campaign_id
        )
        return int(session.scalar(statement) or 0)

    @staticmethod
    def DeleteCampaignViewRecords(session: Session, campaign_id: int) -> None:
        session.execute(delete(CampaignViewRecord).where(CampaignViewRecord.campaign_id == campaign_id))

    @staticmethod
    def AnonymizeUserViewRecords(session: Session, user_id: int) -> None:
        view_records = list(
            session.scalars(
                select(CampaignViewRecord).where(CampaignViewRecord.viewer_user_id == user_id)
            )
        )
        for record in view_records:
            record.viewer_user_id = None
            session.add(record)


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


class CampaignAnalytics:
    @staticmethod
    def GetViewStatistics(
        session: Session,
        owner_id: int,
        category: str | None = None,
        lifecycle: str | None = None,
        sort_order: str = DEFAULT_FUNDRAISER_CAMPAIGN_SORT,
    ) -> list[FundraisingCampaign]:
        return FundraisingCampaign.GetFilteredCampaigns(
            session,
            owner_id=owner_id,
            category=category,
            lifecycle=lifecycle,
            sort_order=sort_order,
        )

    @staticmethod
    def GetViewCount(session: Session, campaign_id: int) -> int:
        campaign = FundraisingCampaign.GetCampaignById(session, campaign_id)
        return int(campaign.view_count or 0) if campaign else 0

    @staticmethod
    def GetExposureDetails(session: Session, campaign_id: int) -> dict[str, object]:
        campaign = FundraisingCampaign.GetCampaignById(session, campaign_id)
        view_records = CampaignViewRecord.GetCampaignViews(session, campaign_id)
        total_view_count = max(len(view_records), int(campaign.view_count or 0) if campaign else 0)
        return {
            "view_count": total_view_count,
            "latest_viewed_at": view_records[0].viewed_at.isoformat() if view_records else None,
            "recent_view_timestamps": [
                record.viewed_at.isoformat() for record in view_records[:5]
            ],
        }

    @staticmethod
    def GetShortlistStatistics(
        session: Session,
        owner_id: int,
        category: str | None = None,
        lifecycle: str | None = None,
        sort_order: str = DEFAULT_FUNDRAISER_CAMPAIGN_SORT,
    ) -> list[FundraisingCampaign]:
        return CampaignAnalytics.GetViewStatistics(
            session,
            owner_id,
            category=category,
            lifecycle=lifecycle,
            sort_order=sort_order,
        )

    @staticmethod
    def GetShortlistCount(session: Session, campaign_id: int) -> int:
        from models.donation import FavouriteCampaign

        return FavouriteCampaign.GetShortlistCount(session, campaign_id)

    @staticmethod
    def GetInterestDetails(session: Session, campaign_id: int) -> dict[str, object]:
        from models.donation import FavouriteCampaign

        return FavouriteCampaign.GetInterestDetails(session, campaign_id)


class CompletedCampaignRecord:
    @staticmethod
    def GetCompletedCampaigns(
        session: Session,
        owner_id: int,
        category: str | None = None,
        sort_order: str = DEFAULT_FUNDRAISER_CAMPAIGN_SORT,
    ) -> list[FundraisingCampaign]:
        campaigns = FundraisingCampaign.GetFilteredCampaigns(
            session,
            owner_id=owner_id,
            category=category,
            lifecycle="completed",
            sort_order=sort_order,
        )
        return campaigns

    @staticmethod
    def GetCampaignById(
        session: Session, owner_id: int, campaign_id: int
    ) -> FundraisingCampaign | None:
        campaign = FundraisingCampaign.GetCampaignById(session, campaign_id)
        if not campaign or campaign.owner_id != owner_id:
            return None
        if not FundraisingCampaign.IsCompleted(campaign):
            return None
        return campaign

    @staticmethod
    def GetPerformanceData(
        session: Session, owner_id: int, campaign_id: int
    ) -> dict[str, object] | None:
        campaign = CompletedCampaignRecord.GetCampaignById(session, owner_id, campaign_id)
        if not campaign:
            return None
        progress_data = CampaignProgress.GetCampaignProgress(session, campaign_id)
        return {
            "campaign_id": campaign.id,
            "view_count": CampaignAnalytics.GetViewCount(session, campaign.id),
            "shortlist_count": CampaignAnalytics.GetShortlistCount(session, campaign.id),
            **progress_data,
        }


class CampaignProgress:
    @staticmethod
    def GetCampaignProgress(session: Session, campaign_id: int) -> dict[str, object]:
        campaign = FundraisingCampaign.GetCampaignById(session, campaign_id)
        if not campaign:
            return {
                "amount_raised": 0,
                "goal_amount": None,
                "progress_percentage": 0,
                "remaining_amount": None,
            }

        goal_amount = int(campaign.goal_amount or 0)
        amount_raised = int(campaign.amount_raised or 0)
        progress_percentage = (
            min(100, round((amount_raised / goal_amount) * 100)) if goal_amount > 0 else 0
        )
        remaining_amount = max(goal_amount - amount_raised, 0) if goal_amount > 0 else None
        return {
            "amount_raised": amount_raised,
            "goal_amount": campaign.goal_amount,
            "progress_percentage": progress_percentage,
            "remaining_amount": remaining_amount,
        }

    @staticmethod
    def GetFundingStatusDetails(session: Session, campaign_id: int) -> dict[str, object]:
        campaign = FundraisingCampaign.GetCampaignById(session, campaign_id)
        if not campaign:
            return {
                "funding_status": "Unavailable",
                "is_completed": False,
                "deadline_status": "Unavailable",
            }

        deadline_status = "No deadline"
        if campaign.deadline:
            try:
                deadline_passed = datetime.strptime(campaign.deadline, "%Y-%m-%d").date() < now_dt().date()
                deadline_status = "Ended" if deadline_passed else f"Runs until {campaign.deadline}"
            except ValueError:
                deadline_status = "Deadline unavailable"

        goal_reached = bool(campaign.goal_amount and campaign.amount_raised >= campaign.goal_amount)
        if goal_reached:
            funding_status = "Goal reached"
        elif campaign.status == "published":
            funding_status = "Funding in progress"
        else:
            funding_status = campaign.status.title()

        return {
            "funding_status": funding_status,
            "is_completed": FundraisingCampaign.IsCompleted(campaign),
            "deadline_status": deadline_status,
            **CampaignProgress.GetCampaignProgress(session, campaign_id),
        }
