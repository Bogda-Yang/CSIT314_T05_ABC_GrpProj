import hashlib
import hmac
import os
import random
import re
import secrets
import smtplib
import uuid
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path
from urllib.parse import urlencode

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    delete,
    func,
    select,
    text,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from starlette.middleware.sessions import SessionMiddleware


BASE_DIR = Path(__file__).resolve().parent
SINGAPORE_TZ = timezone(timedelta(hours=8))
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PASSWORD_MIN_LENGTH = 6
USER_AVATAR_DIR = BASE_DIR / "uploads" / "avatars"
CAMPAIGN_IMAGE_DIR = BASE_DIR / "uploads" / "campaigns"
DEFAULT_ADMIN_USERNAME = (
    os.getenv("ADMIN_USERNAME", "FireflyFund Admin").strip() or "FireflyFund Admin"
)
DEFAULT_ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@fireflyfund.com").strip().lower()
DEFAULT_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin123")
DEFAULT_CAMPAIGN_CATEGORY = "other"
CAMPAIGN_CATEGORY_OPTIONS = (
    ("education", "Education"),
    ("medical", "Medical"),
    ("family", "Family"),
    ("emergencies", "Emergencies"),
    ("animal", "Animal"),
    ("environment", "Environment"),
    ("culture", "Culture"),
    ("disaster", "Disaster"),
    ("mental_health", "Mental Health"),
    ("relief", "Relief"),
    ("community", "Community"),
    ("other", "Other"),
)
CAMPAIGN_PUBLIC_FILTER_OPTIONS = (("all", "All"),) + CAMPAIGN_CATEGORY_OPTIONS
CAMPAIGN_CATEGORY_LABELS = dict(CAMPAIGN_CATEGORY_OPTIONS)
PROJECTS_PRIMARY_CATEGORY_FILTER_VALUES = (
    "all",
    "education",
    "medical",
    "family",
    "emergencies",
    "other",
)
DEFAULT_DASHBOARD_REVIEW_SORT = "time_asc"
DASHBOARD_REVIEW_SORT_OPTIONS = (
    ("time_desc", "Time: Desc"),
    ("time_asc", "Time: Asc"),
    ("amount_desc", "Amount: Desc"),
    ("amount_asc", "Amount: Asc"),
)
DASHBOARD_REVIEW_SORT_LABELS = dict(DASHBOARD_REVIEW_SORT_OPTIONS)

load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is required. Configure a Supabase Postgres connection string in .env."
    )
IS_RENDER = os.getenv("RENDER", "").strip().lower() == "true"


class Base(DeclarativeBase):
    pass


class UserAccount(Base):
    # 用户账号实体
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    salt: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @staticmethod
    def CreateUser(username: str, email: str, password: str) -> "UserAccount":
        password_salt = make_salt()
        return UserAccount(
            username=username.strip(),
            email=email,
            password_hash=hash_value(password, password_salt),
            salt=password_salt,
            created_at=now_dt(),
        )

    @staticmethod
    def SaveUser(session: Session, user: "UserAccount") -> None:
        session.add(user)

    @staticmethod
    def GetUserByEmail(session: Session, email: str) -> "UserAccount | None":
        return session.scalar(select(UserAccount).where(UserAccount.email == email))

    @staticmethod
    def CheckEmail(session: Session, email: str) -> bool:
        return UserAccount.GetUserByEmail(session, email) is None

    @staticmethod
    def CheckPassword(user: "UserAccount", password: str) -> bool:
        candidate_hash = hash_value(password, user.salt)
        return hmac.compare_digest(candidate_hash, user.password_hash)

    @staticmethod
    def GetUserAccount(session: Session, user_id: int) -> "UserAccount | None":
        return session.get(UserAccount, user_id)

    @staticmethod
    def DeleteUser(session: Session, user_account: "UserAccount") -> None:
        session.delete(user_account)


class VerificationCode(Base):
    # 注册验证码实体
    __tablename__ = "verification_codes"

    email: Mapped[str] = mapped_column(String(255), primary_key=True)
    code_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    salt: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class PasswordResetCode(Base):
    # 忘记密码验证码实体
    __tablename__ = "password_reset_codes"

    email: Mapped[str] = mapped_column(String(255), primary_key=True)
    code_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    salt: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class UserProfile(Base):
    # 用户个人信息实体
    __tablename__ = "user_profiles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    contact_details: Mapped[str] = mapped_column(Text, nullable=False, default="")
    avatar_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(30), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    occupation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @staticmethod
    def GetProfileDetails(session: Session, user_id: int) -> "UserProfile | None":
        return session.get(UserProfile, user_id)

    @staticmethod
    def UpdateProfileDetails(
        session: Session,
        user_id: int,
        username: str,
        contact_details: str,
        gender: str | None,
        age: int | None,
        occupation: str | None,
    ) -> tuple["UserAccount", "UserProfile"]:
        user_account = UserAccount.GetUserAccount(session, user_id)
        if not user_account:
            raise HTTPException(status_code=404, detail="Account not found.")

        profile = UserProfile.GetProfileDetails(session, user_id)
        if not profile:
            profile = UserProfile(
                user_id=user_id,
                contact_details="",
                avatar_path=None,
                gender=None,
                age=None,
                occupation=None,
                created_at=now_dt(),
                updated_at=now_dt(),
            )
            session.add(profile)

        user_account.username = username.strip()
        profile.contact_details = contact_details.strip()
        profile.gender = gender
        profile.age = age
        profile.occupation = occupation
        profile.updated_at = now_dt()
        return user_account, profile

    @staticmethod
    def SaveProfile(session: Session, profile: "UserProfile") -> None:
        session.add(profile)

    @staticmethod
    def UpdateAvatarPath(session: Session, user_id: int, avatar_path: str) -> "UserProfile":
        profile = UserProfile.GetProfileDetails(session, user_id)
        if not profile:
            profile = UserProfile(
                user_id=user_id,
                contact_details="",
                avatar_path=avatar_path,
                gender=None,
                age=None,
                occupation=None,
                created_at=now_dt(),
                updated_at=now_dt(),
            )
            session.add(profile)
            return profile

        profile.avatar_path = avatar_path
        profile.updated_at = now_dt()
        session.add(profile)
        return profile

    @staticmethod
    def GetPasswordHash(user_account: "UserAccount") -> str:
        return user_account.password_hash

    @staticmethod
    def UpdatePasswordHash(user_account: "UserAccount", password: str) -> None:
        new_salt = make_salt()
        user_account.salt = new_salt
        user_account.password_hash = hash_value(password, new_salt)


class PasswordHistory(Base):
    # 历史密码实体
    __tablename__ = "password_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    salt: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @staticmethod
    def StorePasswordHistory(session: Session, user_account: UserAccount) -> None:
        session.add(
            PasswordHistory(
                user_id=user_account.id,
                password_hash=user_account.password_hash,
                salt=user_account.salt,
                created_at=now_dt(),
            )
        )

    @staticmethod
    def GetPreviousPasswords(session: Session, user_id: int) -> list["PasswordHistory"]:
        statement = (
            select(PasswordHistory)
            .where(PasswordHistory.user_id == user_id)
            .order_by(PasswordHistory.created_at.desc())
            .limit(5)
        )
        return list(session.scalars(statement))


class UserSession(Base):
    # 用户会话实体
    __tablename__ = "user_sessions"

    session_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    invalidated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    @staticmethod
    def CreateSession(user_id: int) -> "UserSession":
        return UserSession(
            session_key=secrets.token_urlsafe(24),
            user_id=user_id,
            created_at=now_dt(),
            invalidated_at=None,
        )

    @staticmethod
    def StoreSession(session: Session, user_session: "UserSession") -> None:
        session.add(user_session)

    @staticmethod
    def FindSession(session: Session, session_key: str | None) -> "UserSession | None":
        if not session_key:
            return None
        return session.get(UserSession, session_key)

    @staticmethod
    def InvalidateSession(user_session: "UserSession") -> None:
        user_session.invalidated_at = now_dt()


class AuthenticationToken(Base):
    # 认证令牌实体
    __tablename__ = "authentication_tokens"

    token: Mapped[str] = mapped_column(String(80), primary_key=True)
    session_key: Mapped[str] = mapped_column(
        ForeignKey("user_sessions.session_key"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    @staticmethod
    def CreateToken(session_key: str) -> "AuthenticationToken":
        return AuthenticationToken(
            token=secrets.token_urlsafe(32),
            session_key=session_key,
            created_at=now_dt(),
            revoked_at=None,
        )

    @staticmethod
    def FindToken(session: Session, token_value: str | None) -> "AuthenticationToken | None":
        if not token_value:
            return None
        return session.get(AuthenticationToken, token_value)

    @staticmethod
    def RevokeToken(token: "AuthenticationToken") -> None:
        token.revoked_at = now_dt()


class FundraisingCampaign(Base):
    # 筹款项目实体
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
    # 筹款图片实体
    __tablename__ = "campaign_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("fundraising_campaigns.id"), nullable=False, index=True
    )
    image_path: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @staticmethod
    def StoreImages(
        campaign_id: int, image_paths: list[str]
    ) -> list["CampaignImage"]:
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
            image_file_path = CAMPAIGN_IMAGE_DIR / record.image_path
            if image_file_path.exists():
                image_file_path.unlink()
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
        image_file_path = CAMPAIGN_IMAGE_DIR / image_record.image_path
        if image_file_path.exists():
            image_file_path.unlink()
        session.delete(image_record)


class RejectionRecord(Base):
    # 驳回记录实体
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
    # 筹款目标实体
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
    # 筹款描述实体
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
    # 筹款截止日期实体
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
    # 项目审核状态实体
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


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

app = FastAPI(title="FireflyFund")
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "fireflyfund-dev-secret"),
    same_site="lax",
    https_only=False,
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
USER_AVATAR_DIR.mkdir(parents=True, exist_ok=True)
CAMPAIGN_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/user-uploads", StaticFiles(directory=USER_AVATAR_DIR), name="user_uploads")
app.mount("/campaign-uploads", StaticFiles(directory=CAMPAIGN_IMAGE_DIR), name="campaign_uploads")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    # 统一格式化请求参数校验错误
    messages: list[str] = []
    for error in exc.errors():
        message = str(error.get("msg", "")).strip()
        if message.startswith("Value error, "):
            message = message.replace("Value error, ", "", 1)
        if message == "Enter a valid email address.":
            message = "Please enter a valid email address."
        if message:
            messages.append(message)

    if not messages:
        messages = ["Invalid request data."]

    return JSONResponse(status_code=422, content={"detail": messages})


class SendCodePayload(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not EMAIL_PATTERN.match(value):
            raise ValueError("Enter a valid email address.")
        return value


class RegisterPayload(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    email: str
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=128)
    code: str = Field(min_length=6, max_length=6)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not EMAIL_PATTERN.match(value):
            raise ValueError("Enter a valid email address.")
        return value


class LoginPayload(BaseModel):
    email: str
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not EMAIL_PATTERN.match(value):
            raise ValueError("Enter a valid email address.")
        return value


class VerifyResetCodePayload(BaseModel):
    email: str
    code: str = Field(min_length=6, max_length=6)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not EMAIL_PATTERN.match(value):
            raise ValueError("Enter a valid email address.")
        return value


class ResetPasswordPayload(BaseModel):
    email: str
    code: str = Field(min_length=6, max_length=6)
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not EMAIL_PATTERN.match(value):
            raise ValueError("Enter a valid email address.")
        return value


class ProfileUpdatePayload(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    gender: str = Field(default="", max_length=30)
    age: int | None = Field(default=None, ge=0, le=130)
    occupation: str = Field(default="", max_length=100)
    contact_details: str = Field(max_length=500)


class ChangePasswordPayload(BaseModel):
    current_password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=128)
    new_password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=128)
    confirm_new_password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=128)


class DeleteAccountPayload(BaseModel):
    current_password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=128)


def now_dt() -> datetime:
    return datetime.now(SINGAPORE_TZ)


def build_avatar_url(avatar_path: str | None) -> str | None:
    if not avatar_path:
        return None
    return f"/user-uploads/{avatar_path}"


def build_campaign_image_url(image_path: str | None) -> str | None:
    if not image_path:
        return None
    return f"/campaign-uploads/{image_path}"


def hash_value(value: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", value.encode("utf-8"), salt.encode("utf-8"), 120_000
    ).hex()


def make_salt() -> str:
    return os.urandom(16).hex()


def get_session() -> Session:
    return SessionLocal()


def get_admin_emails() -> set[str]:
    admin_emails = {DEFAULT_ADMIN_EMAIL} if DEFAULT_ADMIN_EMAIL else set()
    admin_emails.update(
        {
            email.strip().lower()
            for email in os.getenv("ADMIN_EMAILS", "").split(",")
            if email.strip()
        }
    )
    return admin_emails


def is_admin_email(email: str | None) -> bool:
    if not email:
        return False
    return email.strip().lower() in get_admin_emails()


def ensure_default_admin_account(session: Session) -> None:
    # 确保系统内存在一个可登录的默认管理员账号
    if not DEFAULT_ADMIN_EMAIL or not DEFAULT_ADMIN_PASSWORD:
        return

    admin_user = UserAccount.GetUserByEmail(session, DEFAULT_ADMIN_EMAIL)
    should_commit = False

    if not admin_user:
        admin_user = UserAccount.CreateUser(
            DEFAULT_ADMIN_USERNAME,
            DEFAULT_ADMIN_EMAIL,
            DEFAULT_ADMIN_PASSWORD,
        )
        UserAccount.SaveUser(session, admin_user)
        session.flush()
        should_commit = True

    admin_profile = UserProfile.GetProfileDetails(session, admin_user.id)
    if not admin_profile:
        session.add(
            UserProfile(
                user_id=admin_user.id,
                contact_details="Administrator account for campaign review and publication.",
                avatar_path=None,
                gender=None,
                age=None,
                occupation="Administrator",
                created_at=now_dt(),
                updated_at=now_dt(),
            )
        )
        should_commit = True

    if should_commit:
        session.commit()


def build_projects_url(
    campaign_id: int | None = None,
    review_campaign_id: int | None = None,
    selected_category: str | None = None,
    anchor: str | None = None,
) -> str:
    query_pairs: list[tuple[str, str]] = []
    if selected_category:
        query_pairs.append(("category", selected_category))
    if campaign_id is not None:
        query_pairs.append(("campaign_id", str(campaign_id)))
    if review_campaign_id is not None:
        query_pairs.append(("review_campaign_id", str(review_campaign_id)))

    url = "/projects"
    if query_pairs:
        url = f"{url}?{urlencode(query_pairs)}"
    if anchor:
        url = f"{url}#{anchor}"
    return url


def build_dashboard_url(
    review_campaign_id: int | None = None,
    selected_category: str | None = None,
    selected_sort: str | None = None,
    modal: str | None = None,
    anchor: str | None = None,
) -> str:
    query_pairs: list[tuple[str, str]] = []
    if selected_category:
        query_pairs.append(("category", selected_category))
    if selected_sort:
        query_pairs.append(("sort", selected_sort))
    if review_campaign_id is not None:
        query_pairs.append(("review_campaign_id", str(review_campaign_id)))
    if modal:
        query_pairs.append(("modal", modal))

    url = "/dashboard"
    if query_pairs:
        url = f"{url}?{urlencode(query_pairs)}"
    if anchor:
        url = f"{url}#{anchor}"
    return url


def build_settings_url(anchor: str | None = None) -> str:
    url = "/settings"
    if anchor:
        url = f"{url}#{anchor}"
    return url


def build_campaign_create_url(anchor: str | None = None) -> str:
    url = "/projects/create-campaign"
    if anchor:
        url = f"{url}#{anchor}"
    return url


def build_campaign_management_url(campaign_id: int, anchor: str | None = None) -> str:
    url = f"/projects/manage/{campaign_id}"
    if anchor:
        url = f"{url}#{anchor}"
    return url


def set_flash_message(request: Request, message: str, kind: str = "success") -> None:
    request.session["_flash_message"] = {
        "message": message,
        "kind": kind,
    }


def pop_flash_message(request: Request) -> dict[str, str] | None:
    flash_message = request.session.pop("_flash_message", None)
    if not isinstance(flash_message, dict):
        return None
    return flash_message


def redirect_with_flash(
    request: Request,
    url: str,
    message: str,
    kind: str = "success",
) -> RedirectResponse:
    set_flash_message(request, message, kind)
    return RedirectResponse(url=url, status_code=303)


def redirect_with_projects_flash(
    request: Request,
    message: str,
    kind: str = "success",
    campaign_id: int | None = None,
    review_campaign_id: int | None = None,
    selected_category: str | None = None,
    anchor: str | None = None,
) -> RedirectResponse:
    set_flash_message(request, message, kind)
    return RedirectResponse(
        url=build_projects_url(
            campaign_id=campaign_id,
            review_campaign_id=review_campaign_id,
            selected_category=selected_category,
            anchor=anchor,
        ),
        status_code=303,
    )


def redirect_with_dashboard_flash(
    request: Request,
    message: str,
    kind: str = "success",
    review_campaign_id: int | None = None,
    selected_category: str | None = None,
    selected_sort: str | None = None,
    anchor: str | None = None,
) -> RedirectResponse:
    set_flash_message(request, message, kind)
    return RedirectResponse(
        url=build_dashboard_url(
            review_campaign_id=review_campaign_id,
            selected_category=selected_category,
            selected_sort=selected_sort,
            anchor=anchor,
        ),
        status_code=303,
    )


def redirect_with_settings_flash(
    request: Request,
    message: str,
    kind: str = "success",
    anchor: str | None = None,
) -> RedirectResponse:
    set_flash_message(request, message, kind)
    return RedirectResponse(url=build_settings_url(anchor=anchor), status_code=303)


def redirect_with_campaign_create_flash(
    request: Request,
    message: str,
    kind: str = "success",
    anchor: str | None = None,
) -> RedirectResponse:
    set_flash_message(request, message, kind)
    return RedirectResponse(url=build_campaign_create_url(anchor=anchor), status_code=303)


def redirect_with_campaign_management_flash(
    request: Request,
    campaign_id: int,
    message: str,
    kind: str = "success",
    anchor: str | None = None,
) -> RedirectResponse:
    set_flash_message(request, message, kind)
    return RedirectResponse(
        url=build_campaign_management_url(campaign_id=campaign_id, anchor=anchor),
        status_code=303,
    )


def send_email_code(receiver: str, code: str, purpose: str) -> None:
    # 发送邮箱验证码
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    if not smtp_user or not smtp_pass:
        raise HTTPException(
            status_code=500,
            detail="SMTP is not configured. Set SMTP_USER and SMTP_PASS first.",
        )

    message = EmailMessage()
    message["Subject"] = f"Your FireflyFund {purpose} code"
    message["From"] = smtp_user
    message["To"] = receiver
    message.set_content(
        f"Your FireflyFund {purpose} code is {code}. It expires in 10 minutes."
    )

    with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(message)


def send_notification_email(receiver: str, subject: str, content: str) -> None:
    # 发送功能通知邮件
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    if not smtp_user or not smtp_pass:
        raise HTTPException(
            status_code=500,
            detail="SMTP is not configured. Set SMTP_USER and SMTP_PASS first.",
        )

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = smtp_user
    message["To"] = receiver
    message.set_content(content)

    with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(message)


def get_authenticated_user(request: Request, session: Session) -> UserAccount:
    # 获取当前已登录用户
    user_email = request.session.get("user_email")
    session_key = request.session.get("session_key")
    auth_token = request.session.get("auth_token")

    if not user_email or not session_key or not auth_token:
        raise HTTPException(status_code=401, detail="Authentication required.")

    user_session = UserSession.FindSession(session, session_key)
    auth_record = AuthenticationToken.FindToken(session, auth_token)
    user_account = UserAccount.GetUserByEmail(session, user_email)

    if (
        not user_session
        or user_session.invalidated_at is not None
        or not auth_record
        or auth_record.revoked_at is not None
        or not user_account
        or user_session.user_id != user_account.id
        or auth_record.session_key != user_session.session_key
    ):
        raise HTTPException(status_code=401, detail="Authentication required.")

    return user_account


def get_template_user_context(request: Request) -> dict[str, str | bool | None]:
    # 获取模板使用的当前登录上下文，仅当数据库会话仍然有效时才返回用户信息
    if not (
        request.session.get("user_email")
        and request.session.get("session_key")
        and request.session.get("auth_token")
    ):
        return {
            "user_email": None,
            "username": None,
            "avatar_url": None,
            "is_admin": False,
        }

    with get_session() as session:
        try:
            user_account = get_authenticated_user(request, session)
            profile = UserProfile.GetProfileDetails(session, user_account.id)
        except HTTPException:
            return {
                "user_email": None,
                "username": None,
                "avatar_url": None,
                "is_admin": False,
            }

    return {
        "user_email": user_account.email,
        "username": user_account.username,
        "avatar_url": build_avatar_url(profile.avatar_path) if profile else None,
        "is_admin": is_admin_email(user_account.email),
    }


class EmailVerification:
    # 注册验证码控制实体
    @staticmethod
    def GenerateCode() -> str:
        return f"{random.randint(0, 999999):06d}"

    @staticmethod
    def StoreCode(session: Session, email: str, code: str) -> None:
        salt = make_salt()
        record = session.get(VerificationCode, email)
        if record:
            record.code_hash = hash_value(code, salt)
            record.salt = salt
            record.expires_at = now_dt() + timedelta(minutes=10)
            record.created_at = now_dt()
            return

        session.add(
            VerificationCode(
                email=email,
                code_hash=hash_value(code, salt),
                salt=salt,
                expires_at=now_dt() + timedelta(minutes=10),
                created_at=now_dt(),
            )
        )

    @staticmethod
    def CheckCode(session: Session, email: str, code: str) -> VerificationCode:
        record = session.get(VerificationCode, email)
        if not record:
            raise HTTPException(status_code=400, detail="Request a verification code first.")
        if record.expires_at < now_dt():
            raise HTTPException(status_code=400, detail="Verification code has expired.")

        candidate_hash = hash_value(code, record.salt)
        if not hmac.compare_digest(candidate_hash, record.code_hash):
            raise HTTPException(status_code=400, detail="Invalid verification code.")
        return record


class PasswordResetVerification:
    # 忘记密码验证码控制实体
    @staticmethod
    def GenerateCode() -> str:
        return f"{random.randint(0, 999999):06d}"

    @staticmethod
    def StoreCode(session: Session, email: str, code: str) -> None:
        salt = make_salt()
        record = session.get(PasswordResetCode, email)
        if record:
            record.code_hash = hash_value(code, salt)
            record.salt = salt
            record.expires_at = now_dt() + timedelta(minutes=10)
            record.created_at = now_dt()
            return

        session.add(
            PasswordResetCode(
                email=email,
                code_hash=hash_value(code, salt),
                salt=salt,
                expires_at=now_dt() + timedelta(minutes=10),
                created_at=now_dt(),
            )
        )

    @staticmethod
    def CheckCode(session: Session, email: str, code: str) -> PasswordResetCode:
        record = session.get(PasswordResetCode, email)
        if not record:
            raise HTTPException(status_code=400, detail="Request a reset code first.")
        if record.expires_at < now_dt():
            raise HTTPException(status_code=400, detail="Reset code has expired.")

        candidate_hash = hash_value(code, record.salt)
        if not hmac.compare_digest(candidate_hash, record.code_hash):
            raise HTTPException(status_code=400, detail="Invalid reset code.")
        return record


class AuthController:
    # 认证控制器
    @staticmethod
    def ValidateRegistrationInput(username: str, email: str, password: str) -> tuple[str, str, str]:
        # 校验注册输入
        clean_username = username.strip()
        clean_email = email.strip().lower()
        clean_password = password

        if len(clean_username) < 2:
            raise HTTPException(status_code=400, detail="Username must be at least 2 characters.")
        if len(clean_username) > 50:
            raise HTTPException(status_code=400, detail="Username must be 50 characters or fewer.")
        if not EMAIL_PATTERN.match(clean_email):
            raise HTTPException(status_code=400, detail="Enter a valid email address.")
        if len(clean_password) < PASSWORD_MIN_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Password must be at least {PASSWORD_MIN_LENGTH} characters.",
            )
        PasswordController.ValidatePasswordPolicy(clean_password)

        return clean_username, clean_email, clean_password

    @staticmethod
    def CheckEmail(session: Session, email: str) -> None:
        # 检查邮箱是否已存在
        if not UserAccount.CheckEmail(session, email):
            raise HTTPException(status_code=409, detail="This email is already registered.")

    @staticmethod
    def SendVerificationEmail(email: str, code: str) -> None:
        # 发送注册验证邮件
        send_email_code(email, code, "verification")

    @staticmethod
    def VerifyEmailAddress(session: Session, email: str, code: str) -> VerificationCode:
        # 验证邮箱验证码
        return AuthController.ValidationVerificationCode(session, email, code)

    @staticmethod
    def RequestVerificationCode(session: Session, email: str) -> None:
        # 请求注册验证码
        AuthController.CheckEmail(session, email)

        code = EmailVerification.GenerateCode()
        EmailVerification.StoreCode(session, email, code)
        session.commit()
        AuthController.SendVerificationEmail(email, code)

    @staticmethod
    def ValidationVerificationCode(session: Session, email: str, code: str) -> VerificationCode:
        # 校验注册验证码
        return EmailVerification.CheckCode(session, email, code)

    @staticmethod
    def CreateAccount(
        session: Session, username: str, email: str, password: str, code: str
    ) -> UserAccount:
        # 注册账号
        clean_username, clean_email, clean_password = AuthController.ValidateRegistrationInput(
            username, email, password
        )
        AuthController.CheckEmail(session, clean_email)

        record = AuthController.VerifyEmailAddress(session, clean_email, code)
        user = UserAccount.CreateUser(clean_username, clean_email, clean_password)
        UserAccount.SaveUser(session, user)
        session.flush()

        profile = UserProfile(
            user_id=user.id,
            contact_details="",
            created_at=now_dt(),
            updated_at=now_dt(),
        )
        UserProfile.SaveProfile(session, profile)
        session.delete(record)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=409, detail="This email is already registered.")
        return user

    @staticmethod
    def ValidateCredentials(session: Session, email: str, password: str) -> UserAccount:
        # 校验登录凭据
        user = UserAccount.GetUserByEmail(session, email)
        if not user or not UserAccount.CheckPassword(user, password):
            raise HTTPException(status_code=401, detail="Invalid email or password.")
        return user

    @staticmethod
    def CreateSession(request: Request, session: Session, user: UserAccount) -> None:
        # 创建登录会话
        user_session = UserSession.CreateSession(user.id)
        UserSession.StoreSession(session, user_session)

        # 先落库用户会话，再创建依赖该会话主键的认证令牌，避免外键约束报错
        session.flush()

        auth_token = AuthenticationToken.CreateToken(user_session.session_key)
        session.add(auth_token)
        session.commit()

        request.session["user_email"] = user.email
        request.session["username"] = user.username
        profile = UserProfile.GetProfileDetails(session, user.id)
        request.session["avatar_url"] = build_avatar_url(profile.avatar_path) if profile else None
        request.session["session_key"] = user_session.session_key
        request.session["auth_token"] = auth_token.token

    @staticmethod
    def Login(request: Request, session: Session, email: str, password: str) -> UserAccount:
        # 登录账号
        user = AuthController.ValidateCredentials(session, email, password)
        AuthController.CreateSession(request, session, user)
        return user


class SessionController:
    # 会话控制器
    @staticmethod
    def RequestLogout() -> bool:
        # 接收退出请求
        return True

    @staticmethod
    def Logout(request: Request, session: Session) -> None:
        # 退出登录
        SessionController.RequestLogout()
        SessionController.TerminateSession(request, session)
        SessionController.ClearAuthentication(request)

    @staticmethod
    def TerminateSession(request: Request, session: Session) -> None:
        # 终止数据库中的会话和令牌
        session_key = request.session.get("session_key")
        auth_token = request.session.get("auth_token")

        user_session = UserSession.FindSession(session, session_key)
        token_record = AuthenticationToken.FindToken(session, auth_token)

        if user_session and user_session.invalidated_at is None:
            UserSession.InvalidateSession(user_session)

        if token_record and token_record.revoked_at is None:
            AuthenticationToken.RevokeToken(token_record)

        session.commit()

    @staticmethod
    def ClearAuthentication(request: Request) -> None:
        # 清空浏览器会话
        request.session.clear()


class ProfileController:
    # 个人信息控制器
    @staticmethod
    def ViewCurrentProfile(session: Session, user_id: int) -> dict[str, str | None]:
        # 查看当前个人信息
        return ProfileController.GetProfile(session, user_id)

    @staticmethod
    def GetProfile(session: Session, user_id: int) -> dict[str, str | None]:
        # 获取个人信息
        user_account = UserAccount.GetUserAccount(session, user_id)
        if not user_account:
            raise HTTPException(status_code=404, detail="Account not found.")

        profile = UserProfile.GetProfileDetails(session, user_id)
        if not profile:
            profile = UserProfile(
                user_id=user_id,
                contact_details="",
                avatar_path=None,
                gender=None,
                age=None,
                occupation=None,
                created_at=now_dt(),
                updated_at=now_dt(),
            )
            UserProfile.SaveProfile(session, profile)
            session.commit()

        return {
            "username": user_account.username,
            "email": user_account.email,
            "gender": profile.gender or "",
            "age": profile.age,
            "occupation": profile.occupation or "",
            "contact_details": profile.contact_details,
            "avatar_url": build_avatar_url(profile.avatar_path),
        }

    @staticmethod
    def ValidateProfileInput(
        username: str,
        gender: str,
        age: int | None,
        occupation: str,
        contact_details: str,
    ) -> tuple[str, str, int | None, str, str]:
        # 校验个人信息输入
        username = username.strip()
        gender = gender.strip()
        occupation = occupation.strip()
        contact_details = contact_details.strip()
        allowed_genders = {"", "Male", "Female", "Other", "Prefer not to say"}

        if len(username) < 2:
            raise HTTPException(status_code=400, detail="Username must be at least 2 characters.")
        if len(username) > 50:
            raise HTTPException(status_code=400, detail="Username must be 50 characters or fewer.")
        if gender not in allowed_genders:
            raise HTTPException(status_code=400, detail="Choose a valid gender option.")
        if age is not None and (age < 0 or age > 130):
            raise HTTPException(status_code=400, detail="Age must be between 0 and 130.")
        if len(occupation) > 100:
            raise HTTPException(
                status_code=400, detail="Occupation must be 100 characters or fewer."
            )
        if len(contact_details) > 500:
            raise HTTPException(
                status_code=400, detail="Contact details must be 500 characters or fewer."
            )
        return username, gender, age, occupation, contact_details

    @staticmethod
    def UpdateProfile(
        session: Session,
        user_id: int,
        username: str,
        gender: str,
        age: int | None,
        occupation: str,
        contact_details: str,
    ) -> dict[str, str | None]:
        # 更新个人信息
        (
            clean_username,
            clean_gender,
            clean_age,
            clean_occupation,
            clean_contact_details,
        ) = ProfileController.ValidateProfileInput(
            username, gender, age, occupation, contact_details
        )
        user_account, profile = UserProfile.UpdateProfileDetails(
            session,
            user_id,
            clean_username,
            clean_contact_details,
            clean_gender or None,
            clean_age,
            clean_occupation or None,
        )
        UserProfile.SaveProfile(session, profile)
        session.commit()
        return {
            "username": user_account.username,
            "email": user_account.email,
            "gender": profile.gender or "",
            "age": profile.age,
            "occupation": profile.occupation or "",
            "contact_details": profile.contact_details,
            "avatar_url": build_avatar_url(profile.avatar_path),
        }

    @staticmethod
    def SaveProfileChanges(
        session: Session,
        user_id: int,
        username: str,
        gender: str,
        age: int | None,
        occupation: str,
        contact_details: str,
    ) -> dict[str, str | None]:
        # 保存个人信息修改
        return ProfileController.UpdateProfile(
            session, user_id, username, gender, age, occupation, contact_details
        )

    @staticmethod
    def UpdateAvatar(session: Session, user_id: int, upload_file: UploadFile) -> dict[str, str]:
        # 更新用户头像
        user_account = UserAccount.GetUserAccount(session, user_id)
        if not user_account:
            raise HTTPException(status_code=404, detail="Account not found.")

        if not upload_file.filename:
            raise HTTPException(status_code=400, detail="Choose an image file first.")

        content_type = (upload_file.content_type or "").lower()
        allowed_content_types = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
        }
        file_extension = allowed_content_types.get(content_type)
        if not file_extension:
            raise HTTPException(
                status_code=400,
                detail="Upload a JPG, PNG, or WEBP image.",
            )

        file_bytes = upload_file.file.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="The uploaded image is empty.")
        if len(file_bytes) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image must be 5 MB or smaller.")

        profile = UserProfile.GetProfileDetails(session, user_id)
        old_avatar_path = profile.avatar_path if profile and profile.avatar_path else None

        avatar_filename = f"user_{user_id}_{uuid.uuid4().hex}{file_extension}"
        avatar_file_path = USER_AVATAR_DIR / avatar_filename
        avatar_file_path.write_bytes(file_bytes)

        UserProfile.UpdateAvatarPath(session, user_id, avatar_filename)
        session.commit()

        if old_avatar_path:
            old_file_path = USER_AVATAR_DIR / old_avatar_path
            if old_file_path.exists():
                old_file_path.unlink()

        return {"avatar_url": build_avatar_url(avatar_filename) or ""}


class PasswordController:
    # 修改密码控制器
    @staticmethod
    def ValidationCurrentPassword(
        session: Session, user_id: int, current_password: str
    ) -> UserAccount:
        # 校验当前密码
        user_account = UserAccount.GetUserAccount(session, user_id)
        if not user_account:
            raise HTTPException(status_code=404, detail="Account not found.")
        if not UserAccount.CheckPassword(user_account, current_password):
            raise HTTPException(status_code=400, detail="Current password is incorrect.")
        return user_account

    @staticmethod
    def ValidateNewPassword(
        session: Session,
        user_id: int,
        new_password: str,
        confirm_new_password: str,
        current_password: str,
    ) -> None:
        # 校验新密码
        if new_password != confirm_new_password:
            raise HTTPException(status_code=400, detail="New passwords do not match.")
        if new_password == current_password:
            raise HTTPException(
                status_code=400,
                detail="New password must be different from the current password.",
            )
        if len(new_password) < PASSWORD_MIN_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"New password must be at least {PASSWORD_MIN_LENGTH} characters.",
            )

        for history in PasswordHistory.GetPreviousPasswords(session, user_id):
            if hmac.compare_digest(hash_value(new_password, history.salt), history.password_hash):
                raise HTTPException(
                    status_code=400,
                    detail="Choose a password that has not been used recently.",
                )

    @staticmethod
    def ValidatePasswordPolicy(new_password: str) -> None:
        # 校验密码策略
        if len(new_password) < PASSWORD_MIN_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Password must be at least {PASSWORD_MIN_LENGTH} characters.",
            )
        has_letter = any(character.isalpha() for character in new_password)
        has_digit = any(character.isdigit() for character in new_password)
        if not has_letter or not has_digit:
            raise HTTPException(
                status_code=400,
                detail="Password must contain both letters and numbers.",
            )

    @staticmethod
    def SendPasswordChangeNotification(user_account: UserAccount) -> None:
        # 发送密码修改通知
        send_notification_email(
            user_account.email,
            "Your FireflyFund password was changed",
            "Your FireflyFund password has been updated successfully. "
            "If this was not you, reset your password immediately.",
        )

    @staticmethod
    def UpdatePassword(
        session: Session,
        user_id: int,
        current_password: str,
        new_password: str,
        confirm_new_password: str,
    ) -> None:
        # 修改密码
        user_account = PasswordController.ValidationCurrentPassword(
            session, user_id, current_password
        )
        PasswordController.ValidateNewPassword(
            session, user_id, new_password, confirm_new_password, current_password
        )
        PasswordController.ValidatePasswordPolicy(new_password)
        PasswordHistory.StorePasswordHistory(session, user_account)
        UserProfile.UpdatePasswordHash(user_account, new_password)
        session.commit()
        PasswordController.SendPasswordChangeNotification(user_account)


class ForgotPasswordController:
    # 忘记密码控制器
    @staticmethod
    def ValidateResetPasswordInput(email: str, password: str) -> tuple[str, str]:
        # 校验忘记密码输入
        clean_email = email.strip().lower()
        if not EMAIL_PATTERN.match(clean_email):
            raise HTTPException(status_code=400, detail="Enter a valid email address.")
        if len(password) < PASSWORD_MIN_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Password must be at least {PASSWORD_MIN_LENGTH} characters.",
            )
        PasswordController.ValidatePasswordPolicy(password)
        return clean_email, password

    @staticmethod
    def RequestResetCode(session: Session, email: str) -> None:
        # 请求重置密码验证码
        user = UserAccount.GetUserByEmail(session, email)
        if not user:
            raise HTTPException(status_code=404, detail="No account found for this email.")

        code = PasswordResetVerification.GenerateCode()
        PasswordResetVerification.StoreCode(session, email, code)
        session.commit()
        send_email_code(email, code, "password reset")

    @staticmethod
    def ValidationResetCode(session: Session, email: str, code: str) -> PasswordResetCode:
        # 校验重置密码验证码
        return PasswordResetVerification.CheckCode(session, email, code)

    @staticmethod
    def ResetPassword(session: Session, email: str, code: str, password: str) -> None:
        # 通过验证码重置密码
        clean_email, clean_password = ForgotPasswordController.ValidateResetPasswordInput(
            email, password
        )
        user = UserAccount.GetUserByEmail(session, clean_email)
        if not user:
            raise HTTPException(status_code=404, detail="No account found for this email.")

        record = ForgotPasswordController.ValidationResetCode(session, clean_email, code)
        PasswordController.ValidatePasswordPolicy(clean_password)
        PasswordHistory.StorePasswordHistory(session, user)
        UserProfile.UpdatePasswordHash(user, clean_password)
        session.delete(record)
        session.commit()
        PasswordController.SendPasswordChangeNotification(user)


class DeleteAccountController:
    # 删除账号控制器
    @staticmethod
    def ValidationCurrentPassword(
        session: Session, user_id: int, current_password: str
    ) -> UserAccount:
        # 删除账号前校验当前密码
        return PasswordController.ValidationCurrentPassword(session, user_id, current_password)

    @staticmethod
    def DeleteAccount(session: Session, user_account: UserAccount) -> None:
        # 删除账号及关联数据
        DeleteAccountController.ClearUserProfile(session, user_account.id)
        DeleteAccountController.ClearPasswordHistory(session, user_account.id)
        DeleteAccountController.ClearUserSessions(session, user_account.id)
        DeleteAccountController.ClearVerificationRecords(session, user_account.email)

        # 先同步删除所有依赖表记录，再删除 users 主记录，避免外键约束报错
        session.flush()

        UserAccount.DeleteUser(session, user_account)
        session.commit()

    @staticmethod
    def ClearUserProfile(session: Session, user_id: int) -> None:
        # 清理个人信息
        profile = UserProfile.GetProfileDetails(session, user_id)
        if profile:
            if profile.avatar_path:
                avatar_file_path = USER_AVATAR_DIR / profile.avatar_path
                if avatar_file_path.exists():
                    avatar_file_path.unlink()
            session.delete(profile)

    @staticmethod
    def ClearPasswordHistory(session: Session, user_id: int) -> None:
        # 清理密码历史
        password_history_records = list(
            session.scalars(
                select(PasswordHistory).where(PasswordHistory.user_id == user_id)
            )
        )
        for record in password_history_records:
            session.delete(record)

    @staticmethod
    def ClearUserSessions(session: Session, user_id: int) -> None:
        # 清理会话和令牌
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

    @staticmethod
    def ClearVerificationRecords(session: Session, email: str) -> None:
        # 清理验证码记录
        verification_record = session.get(VerificationCode, email)
        if verification_record:
            session.delete(verification_record)

        password_reset_record = session.get(PasswordResetCode, email)
        if password_reset_record:
            session.delete(password_reset_record)


class CampaignController:
    # 筹款项目控制器
    @staticmethod
    def ValidateCampaignInformation(title: str, category: str) -> tuple[str, str]:
        # 校验创建项目时的基本信息
        clean_title = title.strip()
        if len(clean_title) < 4:
            raise HTTPException(
                status_code=400,
                detail="Campaign title must be at least 4 characters.",
            )
        if len(clean_title) > 160:
            raise HTTPException(
                status_code=400,
                detail="Campaign title must be 160 characters or fewer.",
            )
        clean_category = normalize_campaign_category(category)
        return clean_title, clean_category

    @staticmethod
    def CreateCampaign(
        session: Session, owner_id: int, title: str, category: str
    ) -> FundraisingCampaign:
        # 创建筹款项目
        clean_title, clean_category = CampaignController.ValidateCampaignInformation(
            title, category
        )
        campaign = FundraisingCampaign.CreateCampaign(owner_id, clean_title, clean_category)
        CampaignController.SaveCampaignDraft(session, campaign)
        session.commit()
        session.refresh(campaign)
        return campaign

    @staticmethod
    def SaveCampaignDraft(session: Session, campaign: FundraisingCampaign) -> None:
        # 保存项目草稿
        FundraisingCampaign.SaveCampaignDraft(session, campaign)

    @staticmethod
    def GetCampaignDetails(session: Session, campaign_id: int) -> dict[str, object]:
        # 获取项目详情
        campaign = FundraisingCampaign.GetCampaignDetails(session, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found.")
        return serialize_campaign_detail(session, campaign)

    @staticmethod
    def ValidateUpdatedInformation(title: str, category: str) -> tuple[str, str]:
        # 校验更新后的基本信息
        return CampaignController.ValidateCampaignInformation(title, category)

    @staticmethod
    def UpdateCampaign(
        session: Session, campaign: FundraisingCampaign, title: str, category: str
    ) -> FundraisingCampaign:
        # 更新项目基本信息
        clean_title, clean_category = CampaignController.ValidateUpdatedInformation(
            title, category
        )
        FundraisingCampaign.UpdateCampaign(campaign, clean_title, clean_category)
        FundraisingCampaign.AdvanceWorkflowStage(campaign, 1)
        CampaignController.SaveCampaignChanges(session, campaign)
        session.commit()
        session.refresh(campaign)
        return campaign

    @staticmethod
    def SaveCampaignChanges(session: Session, campaign: FundraisingCampaign) -> None:
        # 保存项目修改
        FundraisingCampaign.SaveCampaignChanges(session, campaign)

    @staticmethod
    def DeleteCampaign(session: Session, campaign: FundraisingCampaign) -> None:
        # 删除项目
        CampaignImage.DeleteImageRecords(session, campaign.id)
        RejectionRecord.DeleteCampaignRejectionRecords(session, campaign.id)
        session.flush()
        CampaignController.RemoveCampaign(session, campaign)
        session.commit()

    @staticmethod
    def RemoveCampaign(session: Session, campaign: FundraisingCampaign) -> None:
        # 彻底移除项目记录
        FundraisingCampaign.DeleteCampaign(session, campaign)

    @staticmethod
    def ValidateWorkflowStage(campaign: FundraisingCampaign, required_stage: int) -> None:
        # 校验项目流程是否到达指定阶段
        current_stage = campaign.workflow_stage or 0
        if current_stage < required_stage:
            raise HTTPException(
                status_code=400,
                detail="Complete the previous campaign step before continuing.",
            )


class CampaignGoalController:
    # 筹款目标控制器
    @staticmethod
    def ValidateGoalInformation(goal_amount: int) -> int:
        # 校验筹款目标金额
        if goal_amount <= 0:
            raise HTTPException(status_code=400, detail="Fundraising goal must be greater than 0.")
        if goal_amount > 1_000_000_000:
            raise HTTPException(
                status_code=400,
                detail="Fundraising goal is too large for this demo platform.",
            )
        return goal_amount

    @staticmethod
    def SetFundraisingGoal(
        session: Session, campaign: FundraisingCampaign, goal_amount: int
    ) -> dict[str, int | None]:
        # 设置筹款目标
        CampaignController.ValidateWorkflowStage(campaign, 1)
        clean_goal_amount = CampaignGoalController.ValidateGoalInformation(goal_amount)
        CampaignGoal.SetGoal(campaign, clean_goal_amount)
        FundraisingCampaign.AdvanceWorkflowStage(campaign, 2)
        CampaignGoalController.SaveFundraisingGoal(session, campaign)
        session.commit()
        return CampaignGoal.GetGoalDetails(campaign)

    @staticmethod
    def SaveFundraisingGoal(session: Session, campaign: FundraisingCampaign) -> None:
        # 保存筹款目标
        CampaignGoal.SaveGoal(session, campaign)


class CampaignDescriptionController:
    # 项目描述控制器
    @staticmethod
    def ValidateDescriptionContent(description: str) -> str:
        # 校验项目描述
        clean_description = description.strip()
        if len(clean_description) < 20:
            raise HTTPException(
                status_code=400,
                detail="Campaign description must be at least 20 characters.",
            )
        if len(clean_description) > 5000:
            raise HTTPException(
                status_code=400,
                detail="Campaign description must be 5000 characters or fewer.",
            )
        return clean_description

    @staticmethod
    def AddCampaignDescription(
        session: Session, campaign: FundraisingCampaign, description: str
    ) -> dict[str, str]:
        # 添加项目描述
        CampaignController.ValidateWorkflowStage(campaign, 2)
        clean_description = CampaignDescriptionController.ValidateDescriptionContent(description)
        CampaignDescription.SetDescription(campaign, clean_description)
        FundraisingCampaign.AdvanceWorkflowStage(campaign, 3)
        CampaignDescriptionController.SaveCampaignDescription(session, campaign)
        session.commit()
        return CampaignDescription.GetDescriptionDetails(campaign)

    @staticmethod
    def SaveCampaignDescription(session: Session, campaign: FundraisingCampaign) -> None:
        # 保存项目描述
        CampaignDescription.SaveDescription(session, campaign)


class CampaignImageController:
    # 项目图片控制器
    @staticmethod
    def ValidateImageFormatAndSize(
        upload_files: list[UploadFile],
    ) -> list[tuple[bytes, str]]:
        # 校验图片格式与大小
        if not upload_files:
            raise HTTPException(status_code=400, detail="Choose at least one campaign image.")

        allowed_content_types = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
        }

        validated_files: list[tuple[bytes, str]] = []
        for upload_file in upload_files:
            if not upload_file.filename:
                continue

            content_type = (upload_file.content_type or "").lower()
            file_extension = allowed_content_types.get(content_type)
            if not file_extension:
                raise HTTPException(
                    status_code=400,
                    detail="Campaign images must be JPG, PNG, or WEBP.",
                )

            file_bytes = upload_file.file.read()
            if not file_bytes:
                raise HTTPException(status_code=400, detail="One of the uploaded images is empty.")
            if len(file_bytes) > 5 * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail="Each campaign image must be 5 MB or smaller.",
                )

            validated_files.append((file_bytes, file_extension))

        if not validated_files:
            raise HTTPException(status_code=400, detail="Choose at least one campaign image.")

        return validated_files

    @staticmethod
    def UploadCampaignImages(
        session: Session, campaign: FundraisingCampaign, upload_files: list[UploadFile]
    ) -> list[CampaignImage]:
        # 上传项目图片
        CampaignController.ValidateWorkflowStage(campaign, 3)
        validated_files = CampaignImageController.ValidateImageFormatAndSize(upload_files)
        existing_image_records = CampaignImage.GetImageDetails(session, campaign.id)
        if len(existing_image_records) + len(validated_files) > 5:
            raise HTTPException(
                status_code=400,
                detail="Each campaign can include up to 5 images.",
            )

        image_paths: list[str] = []
        for file_bytes, file_extension in validated_files:
            image_filename = f"campaign_{campaign.id}_{uuid.uuid4().hex}{file_extension}"
            image_file_path = CAMPAIGN_IMAGE_DIR / image_filename
            image_file_path.write_bytes(file_bytes)
            image_paths.append(image_filename)

        if campaign.status != "draft":
            campaign.status = "draft"
            campaign.submitted_at = None
            campaign.reviewed_at = None
            campaign.published_at = None
        campaign.updated_at = now_dt()
        FundraisingCampaign.AdvanceWorkflowStage(campaign, 4)
        session.add(campaign)

        image_records = CampaignImage.StoreImages(campaign.id, image_paths)
        CampaignImageController.SaveImageRecords(session, image_records)
        session.commit()
        return image_records

    @staticmethod
    def SaveImageRecords(session: Session, image_records: list[CampaignImage]) -> None:
        # 保存图片记录
        CampaignImage.SaveImageRecords(session, image_records)

    @staticmethod
    def DeleteCampaignImage(
        session: Session, campaign: FundraisingCampaign, image_id: int
    ) -> None:
        # 删除单张项目图片
        CampaignController.ValidateWorkflowStage(campaign, 3)
        image_record = CampaignImage.GetImageRecord(session, campaign.id, image_id)
        if image_record is None:
            raise HTTPException(status_code=404, detail="Campaign image was not found.")

        CampaignImage.DeleteImageRecord(session, image_record)

        remaining_image_records = [
            record for record in CampaignImage.GetImageDetails(session, campaign.id)
            if record.id != image_id
        ]
        if not remaining_image_records and (campaign.workflow_stage or 0) > 3:
            campaign.workflow_stage = 3

        if campaign.status != "draft":
            campaign.status = "draft"
            campaign.submitted_at = None
            campaign.reviewed_at = None
            campaign.published_at = None

        campaign.updated_at = now_dt()
        session.add(campaign)
        session.commit()


class CampaignDeadlineController:
    # 项目截止日期控制器
    @staticmethod
    def ValidateDeadline(deadline: str) -> str:
        # 校验截止日期
        clean_deadline = deadline.strip()
        if not clean_deadline:
            raise HTTPException(status_code=400, detail="Choose a campaign deadline.")

        try:
            deadline_date = datetime.strptime(clean_deadline, "%Y-%m-%d").date()
        except ValueError as error:
            raise HTTPException(status_code=400, detail="Choose a valid campaign deadline.") from error

        if deadline_date <= now_dt().date():
            raise HTTPException(
                status_code=400,
                detail="Campaign deadline must be a future date.",
            )

        return clean_deadline

    @staticmethod
    def SetCampaignDeadline(
        session: Session, campaign: FundraisingCampaign, deadline: str
    ) -> dict[str, str | None]:
        # 设置截止日期
        CampaignController.ValidateWorkflowStage(campaign, 4)
        clean_deadline = CampaignDeadlineController.ValidateDeadline(deadline)
        CampaignDeadline.SetDeadline(campaign, clean_deadline)
        FundraisingCampaign.AdvanceWorkflowStage(campaign, 5)
        CampaignDeadlineController.SaveCampaignDeadline(session, campaign)
        session.commit()
        return CampaignDeadline.GetDeadlineDetails(campaign)

    @staticmethod
    def SaveCampaignDeadline(session: Session, campaign: FundraisingCampaign) -> None:
        # 保存截止日期
        CampaignDeadline.SaveDeadline(session, campaign)


class CampaignApprovalController:
    # 项目审核控制器
    @staticmethod
    def ValidateSubmissionRequirements(
        session: Session, campaign: FundraisingCampaign
    ) -> None:
        # 校验提审前必填信息
        CampaignController.ValidateCampaignInformation(campaign.title, campaign.category)
        if not campaign.goal_amount or campaign.goal_amount <= 0:
            raise HTTPException(status_code=400, detail="Set a fundraising goal before submission.")
        CampaignDescriptionController.ValidateDescriptionContent(campaign.description)
        if not campaign.deadline:
            raise HTTPException(
                status_code=400,
                detail="Set a campaign deadline before submission.",
            )
        CampaignDeadlineController.ValidateDeadline(campaign.deadline)
        if not CampaignImage.GetImageDetails(session, campaign.id):
            raise HTTPException(
                status_code=400,
                detail="Upload at least one campaign image before submission.",
            )

    @staticmethod
    def SubmitCampaignForApproval(
        session: Session, campaign: FundraisingCampaign
    ) -> dict[str, str | None]:
        # 提交项目审核
        CampaignController.ValidateWorkflowStage(campaign, 5)
        CampaignApprovalController.ValidateSubmissionRequirements(session, campaign)
        RejectionRecord.DeleteCampaignRejectionRecords(session, campaign.id)
        FundraisingCampaign.SubmitCampaign(campaign)
        CampaignApprovalController.UpdateCampaignStatusToPending(session, campaign)
        session.commit()
        return CampaignApprovalController.GetApprovalStatusDetails(session, campaign.id)

    @staticmethod
    def UpdateCampaignStatusToPending(session: Session, campaign: FundraisingCampaign) -> None:
        # 更新状态为待审核
        CampaignStatus.SetPending(campaign)
        FundraisingCampaign.UpdateCampaignStatus(session, campaign, CampaignStatus.GetStatus(campaign))

    @staticmethod
    def RetrieveCampaignStatus(session: Session, campaign_id: int) -> FundraisingCampaign:
        # 读取项目审核状态
        campaign = FundraisingCampaign.GetCampaignById(session, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found.")
        return campaign

    @staticmethod
    def GetApprovalStatusDetails(session: Session, campaign_id: int) -> dict[str, str | None]:
        # 获取审核状态详情
        campaign = CampaignApprovalController.RetrieveCampaignStatus(session, campaign_id)
        return CampaignStatus.GetStatusDetails(session, campaign)

    @staticmethod
    def GetPendingCampaigns(
        session: Session,
        category: str | None = None,
        sort_order: str = DEFAULT_DASHBOARD_REVIEW_SORT,
    ) -> list[FundraisingCampaign]:
        # 读取待审核项目列表
        return FundraisingCampaign.GetPendingCampaigns(
            session,
            category=category,
            sort_order=sort_order,
        )

    @staticmethod
    def GetCampaignDetails(session: Session, campaign_id: int) -> dict[str, object]:
        # 管理员读取项目详情
        return CampaignController.GetCampaignDetails(session, campaign_id)

    @staticmethod
    def ValidateCampaign(session: Session, campaign_id: int) -> FundraisingCampaign:
        # 校验待审核项目
        campaign = CampaignApprovalController.RetrieveCampaignStatus(session, campaign_id)
        if campaign.status != "pending":
            raise HTTPException(status_code=400, detail="Only pending campaigns can be reviewed.")
        CampaignApprovalController.ValidateSubmissionRequirements(session, campaign)
        return campaign

    @staticmethod
    def ApproveCampaign(
        session: Session, campaign: FundraisingCampaign
    ) -> dict[str, str | None]:
        # 审核通过项目
        CampaignStatus.SetApproved(campaign)
        FundraisingCampaign.UpdateCampaignStatus(session, campaign, CampaignStatus.GetStatus(campaign))
        CampaignApprovalController.PublishCampaign(session, campaign)
        RejectionRecord.DeleteCampaignRejectionRecords(session, campaign.id)
        session.commit()
        return CampaignApprovalController.GetApprovalStatusDetails(session, campaign.id)

    @staticmethod
    def PublishCampaign(session: Session, campaign: FundraisingCampaign) -> None:
        # 发布项目
        CampaignStatus.SetPublished(campaign)
        FundraisingCampaign.PublishCampaign(session, campaign)


class CampaignRejectionController:
    # 项目驳回控制器
    @staticmethod
    def GetPendingCampaigns(
        session: Session,
        category: str | None = None,
        sort_order: str = DEFAULT_DASHBOARD_REVIEW_SORT,
    ) -> list[FundraisingCampaign]:
        # 读取待审核项目列表
        return FundraisingCampaign.GetPendingCampaigns(
            session,
            category=category,
            sort_order=sort_order,
        )

    @staticmethod
    def GetCampaignDetails(session: Session, campaign_id: int) -> dict[str, object]:
        # 读取驳回项目详情
        return CampaignController.GetCampaignDetails(session, campaign_id)

    @staticmethod
    def ValidateCampaign(session: Session, campaign_id: int) -> FundraisingCampaign:
        # 校验待驳回项目
        campaign = FundraisingCampaign.GetCampaignById(session, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found.")
        if campaign.status != "pending":
            raise HTTPException(status_code=400, detail="Only pending campaigns can be rejected.")
        return campaign

    @staticmethod
    def RejectCampaign(
        session: Session, campaign: FundraisingCampaign, reason: str
    ) -> dict[str, str | None]:
        # 驳回项目
        clean_reason = reason.strip()
        if len(clean_reason) < 10:
            raise HTTPException(
                status_code=400,
                detail="Rejection reason must be at least 10 characters.",
            )

        CampaignRejectionController.RecordRejectionReason(session, campaign.id, clean_reason)
        campaign.status = "rejected"
        campaign.reviewed_at = now_dt()
        campaign.updated_at = now_dt()
        campaign.published_at = None
        session.add(campaign)
        session.commit()
        return CampaignStatus.GetStatusDetails(session, campaign)

    @staticmethod
    def RecordRejectionReason(session: Session, campaign_id: int, reason: str) -> None:
        # 记录驳回原因
        RejectionRecord.SaveRejectionReason(session, campaign_id, reason)


def ensure_campaign_owner(
    session: Session, user_id: int, campaign_id: int
) -> FundraisingCampaign:
    # 校验当前用户是否拥有该项目
    campaign = FundraisingCampaign.GetCampaignById(session, campaign_id)
    if not campaign or campaign.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    return campaign


def ensure_admin_user(user: UserAccount) -> None:
    # 校验当前用户是否具备管理员权限
    if not is_admin_email(user.email):
        raise HTTPException(status_code=403, detail="Administrator access is required.")


def humanize_campaign_status(status: str) -> str:
    # 将状态值转为界面可读文本
    return {
        "draft": "Draft",
        "pending": "Pending Review",
        "approved": "Approved",
        "published": "Published",
        "rejected": "Rejected",
    }.get(status, status.title())


def humanize_campaign_category(category: str | None) -> str:
    # 将分类值转为界面可读文本
    if not category:
        return CAMPAIGN_CATEGORY_LABELS[DEFAULT_CAMPAIGN_CATEGORY]
    return CAMPAIGN_CATEGORY_LABELS.get(category, category.title())


def normalize_campaign_category(category: str | None) -> str:
    # 规范化项目分类
    clean_category = (category or "").strip().lower()
    if clean_category not in CAMPAIGN_CATEGORY_LABELS:
        raise HTTPException(status_code=400, detail="Choose a valid campaign category.")
    return clean_category


def normalize_dashboard_review_sort(sort_order: str | None) -> str:
    # 规范化管理员审核排序方式
    clean_sort_order = (sort_order or "").strip().lower()
    if clean_sort_order not in DASHBOARD_REVIEW_SORT_LABELS:
        return DEFAULT_DASHBOARD_REVIEW_SORT
    return clean_sort_order


def humanize_campaign_workflow_stage(stage: int) -> str:
    # 将流程阶段值转为界面可读文本
    return {
        0: "Draft created",
        1: "Basic information saved",
        2: "Fundraising goal saved",
        3: "Description saved",
        4: "Images uploaded",
        5: "Deadline saved",
    }.get(stage, "Ready for submission")


def serialize_campaign_summary(
    session: Session, campaign: FundraisingCampaign
) -> dict[str, object]:
    # 序列化项目列表摘要
    owner_account = UserAccount.GetUserAccount(session, campaign.owner_id)
    image_records = CampaignImage.GetImageDetails(session, campaign.id)
    image_urls = [
        build_campaign_image_url(record.image_path)
        for record in image_records
        if build_campaign_image_url(record.image_path)
    ]
    first_image_url = image_urls[0] if image_urls else None
    return {
        "id": campaign.id,
        "owner_username": owner_account.username if owner_account else "Unknown",
        "owner_email": owner_account.email if owner_account else None,
        "title": campaign.title,
        "category": campaign.category or DEFAULT_CAMPAIGN_CATEGORY,
        "category_label": humanize_campaign_category(campaign.category),
        "description": campaign.description.strip() if campaign.description else None,
        "description_excerpt": (
            f"{campaign.description.strip()[:180]}..."
            if campaign.description and len(campaign.description.strip()) > 180
            else campaign.description.strip()
        ),
        "goal_amount": campaign.goal_amount,
        "workflow_stage": campaign.workflow_stage or 0,
        "workflow_stage_label": humanize_campaign_workflow_stage(campaign.workflow_stage or 0),
        "status": campaign.status,
        "status_label": humanize_campaign_status(campaign.status),
        "deadline": campaign.deadline,
        "updated_at": campaign.updated_at.strftime("%Y-%m-%d %H:%M"),
        "published_at": campaign.published_at.strftime("%Y-%m-%d %H:%M")
        if campaign.published_at
        else None,
        "image_count": len(image_records),
        "cover_image_url": first_image_url,
        "image_urls": image_urls,
    }


def serialize_campaign_detail(
    session: Session, campaign: FundraisingCampaign
) -> dict[str, object]:
    # 序列化完整项目详情
    owner_account = UserAccount.GetUserAccount(session, campaign.owner_id)
    image_records = CampaignImage.GetImageDetails(session, campaign.id)
    status_details = CampaignStatus.GetStatusDetails(session, campaign)
    return {
        "id": campaign.id,
        "owner_id": campaign.owner_id,
        "owner_username": owner_account.username if owner_account else "Unknown",
        "owner_email": owner_account.email if owner_account else None,
        "title": campaign.title,
        "category": campaign.category or DEFAULT_CAMPAIGN_CATEGORY,
        "category_label": humanize_campaign_category(campaign.category),
        "goal_amount": campaign.goal_amount,
        "description": campaign.description,
        "deadline": campaign.deadline,
        "workflow_stage": campaign.workflow_stage or 0,
        "workflow_stage_label": humanize_campaign_workflow_stage(campaign.workflow_stage or 0),
        "status": campaign.status,
        "status_label": humanize_campaign_status(campaign.status),
        "created_at": campaign.created_at.strftime("%Y-%m-%d %H:%M"),
        "updated_at": campaign.updated_at.strftime("%Y-%m-%d %H:%M"),
        "submitted_at": status_details["submitted_at"],
        "published_at": status_details["published_at"],
        "reviewed_at": status_details["reviewed_at"],
        "rejection_reason": status_details["rejection_reason"],
        "image_count": len(image_records),
        "images": [
            {
                "id": record.id,
                "url": build_campaign_image_url(record.image_path),
            }
            for record in image_records
            if build_campaign_image_url(record.image_path)
        ],
        "image_urls": [
            build_campaign_image_url(record.image_path)
            for record in image_records
            if build_campaign_image_url(record.image_path)
        ],
    }


@app.on_event("startup")
def startup() -> None:
    # 启动应用并自动建表
    if IS_RENDER:
        # Render 免费实例会频繁冷启动，线上环境尽量减少启动阶段的数据库写操作。
        Base.metadata.create_all(bind=engine)
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE fundraising_campaigns "
                    "ADD COLUMN IF NOT EXISTS category VARCHAR(40) DEFAULT 'other'"
                )
            )
            connection.execute(
                text(
                    "ALTER TABLE fundraising_campaigns "
                    "ADD COLUMN IF NOT EXISTS workflow_stage INTEGER DEFAULT 0"
                )
            )
            connection.execute(
                text(
                    "UPDATE fundraising_campaigns "
                    "SET category = 'other' "
                    "WHERE category IS NULL OR TRIM(category) = ''"
                )
            )
            connection.execute(
                text(
                    "UPDATE fundraising_campaigns "
                    "SET workflow_stage = 0 "
                    "WHERE workflow_stage IS NULL"
                )
            )
        with get_session() as session:
            ensure_default_admin_account(session)
        return

    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE fundraising_campaigns "
                "ADD COLUMN IF NOT EXISTS category VARCHAR(40) DEFAULT 'other'"
            )
        )
        connection.execute(
            text(
                "ALTER TABLE fundraising_campaigns "
                "ADD COLUMN IF NOT EXISTS workflow_stage INTEGER DEFAULT 0"
            )
        )
        connection.execute(
            text(
                "UPDATE fundraising_campaigns "
                "SET category = 'other' "
                "WHERE category IS NULL OR TRIM(category) = ''"
            )
        )
        connection.execute(
            text(
                "UPDATE fundraising_campaigns "
                "SET workflow_stage = 0 "
                "WHERE workflow_stage IS NULL"
            )
        )
        connection.execute(
            text("ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS avatar_path TEXT")
        )
        connection.execute(
            text("ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS gender VARCHAR(30)")
        )
        connection.execute(
            text("ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS age INTEGER")
        )
        connection.execute(
            text("ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS occupation VARCHAR(100)")
        )
        connection.execute(text("DELETE FROM authentication_tokens"))
        connection.execute(text("DELETE FROM user_sessions"))
    Base.metadata.create_all(bind=engine)
    with get_session() as session:
        ensure_default_admin_account(session)


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    # 首页
    user_context = get_template_user_context(request)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            **user_context,
        },
    )


@app.get("/about", response_class=HTMLResponse)
def about_page(request: Request) -> HTMLResponse:
    # 关于我们页面
    user_context = get_template_user_context(request)
    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context={
            "request": request,
            **user_context,
        },
    )


@app.get("/transparency", response_class=HTMLResponse)
def transparency_page(request: Request) -> HTMLResponse:
    # 信息公开页面
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


@app.get("/projects", response_class=HTMLResponse)
def projects_page(
    request: Request,
    category: str | None = Query(default=None),
) -> HTMLResponse:
    # 筹款项目公开浏览页面
    requested_category = (category or "").strip().lower()
    selected_category = None
    if requested_category and requested_category != "all":
        selected_category = normalize_campaign_category(requested_category)
    with get_session() as session:
        published_campaigns = [
            serialize_campaign_summary(session, campaign)
            for campaign in FundraisingCampaign.GetPublishedCampaigns(session, selected_category)
        ]

        user: UserAccount | None = None
        user_profile: UserProfile | None = None
        is_admin = False

        try:
            user = get_authenticated_user(request, session)
        except HTTPException:
            user = None

        if user:
            user_profile = UserProfile.GetProfileDetails(session, user.id)
            is_admin = is_admin_email(user.email)

        flash_message = pop_flash_message(request)
        category_filters = [
            {
                "value": option_value,
                "label": option_label,
                "is_active": (
                    selected_category is None
                    if option_value == "all"
                    else selected_category == option_value
                ),
                "url": build_projects_url(
                    selected_category=None if option_value == "all" else option_value,
                    anchor="published-projects",
                ),
            }
            for option_value, option_label in CAMPAIGN_PUBLIC_FILTER_OPTIONS
        ]
        primary_category_filters = [
            category_filter
            for category_filter in category_filters
            if category_filter["value"] in PROJECTS_PRIMARY_CATEGORY_FILTER_VALUES
        ]
        overflow_category_filters = [
            category_filter
            for category_filter in category_filters
            if category_filter["value"] not in PROJECTS_PRIMARY_CATEGORY_FILTER_VALUES
        ]

    return templates.TemplateResponse(
        request=request,
        name="projects.html",
        context={
            "request": request,
            "title": "Projects",
            "user_email": user.email if user else None,
            "username": user.username if user else None,
            "avatar_url": build_avatar_url(user_profile.avatar_path) if user_profile else None,
            "is_admin": is_admin,
            "flash_message": flash_message,
            "selected_category": selected_category,
            "selected_category_label": humanize_campaign_category(selected_category),
            "primary_category_filters": primary_category_filters,
            "overflow_category_filters": overflow_category_filters,
            "published_campaigns": published_campaigns,
        },
    )


@app.get("/projects/create-campaign", response_class=HTMLResponse)
def campaign_create_page(request: Request) -> HTMLResponse:
    # 独立创建筹款项目入口页面
    with get_session() as session:
        try:
            user = get_authenticated_user(request, session)
        except HTTPException:
            return RedirectResponse(url="/auth?mode=login", status_code=303)

        profile = ProfileController.GetProfile(session, user.id)
        own_campaigns = FundraisingCampaign.GetCampaignsByOwner(session, user.id)
        serialized_campaigns = [
            serialize_campaign_summary(session, own_campaign) for own_campaign in own_campaigns
        ]
        flash_message = pop_flash_message(request)

    return templates.TemplateResponse(
        request=request,
        name="campaign_create.html",
        context={
            "request": request,
            "title": "Create Campaign",
            "username": profile["username"],
            "user_email": profile["email"],
            "avatar_url": profile["avatar_url"],
            "is_admin": is_admin_email(profile["email"]),
            "flash_message": flash_message,
            "category_options": CAMPAIGN_CATEGORY_OPTIONS,
            "campaigns": serialized_campaigns,
        },
    )


@app.get("/projects/manage/{campaign_id}", response_class=HTMLResponse)
def campaign_management_page(
    request: Request,
    campaign_id: int,
) -> HTMLResponse:
    # 筹款项目流程页面
    with get_session() as session:
        try:
            user = get_authenticated_user(request, session)
        except HTTPException:
            return RedirectResponse(url="/auth?mode=login", status_code=303)

        campaign = ensure_campaign_owner(session, user.id, campaign_id)
        user_profile = UserProfile.GetProfileDetails(session, user.id)
        own_campaigns = FundraisingCampaign.GetCampaignsByOwner(session, user.id)
        serialized_campaigns = [
            serialize_campaign_summary(session, own_campaign) for own_campaign in own_campaigns
        ]
        selected_campaign = serialize_campaign_detail(session, campaign)
        flash_message = pop_flash_message(request)

        workflow_stage = selected_campaign["workflow_stage"]
        workflow_access = {
            "basic": True,
            "goal": workflow_stage >= 1,
            "description": workflow_stage >= 2,
            "images": workflow_stage >= 3,
            "deadline": workflow_stage >= 4,
            "submit": workflow_stage >= 5,
        }

    return templates.TemplateResponse(
        request=request,
        name="campaign_workflow.html",
        context={
            "request": request,
            "title": "Campaign Workflow",
            "user_email": user.email,
            "username": user.username,
            "avatar_url": build_avatar_url(user_profile.avatar_path) if user_profile else None,
            "is_admin": is_admin_email(user.email),
            "flash_message": flash_message,
            "campaigns": serialized_campaigns,
            "selected_campaign": selected_campaign,
            "workflow_access": workflow_access,
            "category_options": CAMPAIGN_CATEGORY_OPTIONS,
        },
    )


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(
    request: Request,
    category: str | None = Query(default=None),
    sort: str = Query(default=DEFAULT_DASHBOARD_REVIEW_SORT),
    review_campaign_id: int | None = Query(default=None, ge=1),
    modal: str | None = Query(default=None),
) -> HTMLResponse:
    # 管理员审核仪表盘页面
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


@app.post("/projects/create")
def create_campaign(
    request: Request,
    title: str = Form(...),
    category: str = Form(DEFAULT_CAMPAIGN_CATEGORY),
) -> RedirectResponse:
    # 创建筹款项目
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            campaign = CampaignController.CreateCampaign(session, user.id, title, category)
    except HTTPException as error:
        return redirect_with_campaign_create_flash(
            request,
            error.detail if isinstance(error.detail, str) else "Unable to create campaign.",
            "error",
            anchor="campaign-create-form",
        )

    return redirect_with_campaign_management_flash(
        request,
        campaign.id,
        "Campaign draft created successfully. Save basic campaign information to unlock the next step.",
        "success",
        anchor="campaign-workflow",
    )


@app.post("/projects/{campaign_id}/basic")
def update_campaign_basic_information(
    campaign_id: int,
    request: Request,
    title: str = Form(...),
    category: str = Form(DEFAULT_CAMPAIGN_CATEGORY),
) -> RedirectResponse:
    # 更新项目基本信息
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            campaign = ensure_campaign_owner(session, user.id, campaign_id)
            CampaignController.UpdateCampaign(session, campaign, title, category)
    except HTTPException as error:
        return redirect_with_campaign_management_flash(
            request,
            campaign_id,
            error.detail if isinstance(error.detail, str) else "Unable to update campaign.",
            "error",
            anchor="campaign-workflow",
        )

    return redirect_with_campaign_management_flash(
        request,
        campaign_id,
        "Basic campaign information saved successfully.",
        "success",
        anchor="campaign-workflow",
    )


@app.post("/projects/{campaign_id}/goal")
def set_campaign_goal(
    campaign_id: int,
    request: Request,
    goal_amount: int = Form(...),
) -> RedirectResponse:
    # 设置筹款目标
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            campaign = ensure_campaign_owner(session, user.id, campaign_id)
            CampaignGoalController.SetFundraisingGoal(session, campaign, goal_amount)
    except HTTPException as error:
        return redirect_with_campaign_management_flash(
            request,
            campaign_id,
            error.detail if isinstance(error.detail, str) else "Unable to save fundraising goal.",
            "error",
            anchor="campaign-goal",
        )

    return redirect_with_campaign_management_flash(
        request,
        campaign_id,
        "Fundraising goal saved successfully.",
        "success",
        anchor="campaign-goal",
    )


@app.post("/projects/{campaign_id}/description")
def set_campaign_description(
    campaign_id: int,
    request: Request,
    description: str = Form(...),
) -> RedirectResponse:
    # 设置项目描述
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            campaign = ensure_campaign_owner(session, user.id, campaign_id)
            CampaignDescriptionController.AddCampaignDescription(session, campaign, description)
    except HTTPException as error:
        return redirect_with_campaign_management_flash(
            request,
            campaign_id,
            error.detail if isinstance(error.detail, str) else "Unable to save campaign description.",
            "error",
            anchor="campaign-description",
        )

    return redirect_with_campaign_management_flash(
        request,
        campaign_id,
        "Campaign description saved successfully.",
        "success",
        anchor="campaign-description",
    )


@app.post("/projects/{campaign_id}/images")
def upload_campaign_images(
    campaign_id: int,
    request: Request,
    images: list[UploadFile] = File(...),
) -> RedirectResponse:
    # 上传项目图片
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            campaign = ensure_campaign_owner(session, user.id, campaign_id)
            CampaignImageController.UploadCampaignImages(session, campaign, images)
    except HTTPException as error:
        return redirect_with_campaign_management_flash(
            request,
            campaign_id,
            error.detail if isinstance(error.detail, str) else "Unable to upload campaign images.",
            "error",
            anchor="campaign-images",
        )

    return redirect_with_campaign_management_flash(
        request,
        campaign_id,
        "Campaign images uploaded successfully.",
        "success",
        anchor="campaign-images",
    )


@app.post("/projects/{campaign_id}/images/{image_id}/delete")
def delete_campaign_image(
    campaign_id: int,
    image_id: int,
    request: Request,
) -> RedirectResponse:
    # 删除单张项目图片
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            campaign = ensure_campaign_owner(session, user.id, campaign_id)
            CampaignImageController.DeleteCampaignImage(session, campaign, image_id)
    except HTTPException as error:
        return redirect_with_campaign_management_flash(
            request,
            campaign_id,
            error.detail if isinstance(error.detail, str) else "Unable to delete campaign image.",
            "error",
            anchor="campaign-images",
        )

    return redirect_with_campaign_management_flash(
        request,
        campaign_id,
        "Campaign image deleted successfully.",
        "success",
        anchor="campaign-images",
    )


@app.post("/projects/{campaign_id}/deadline")
def set_campaign_deadline(
    campaign_id: int,
    request: Request,
    deadline: str = Form(...),
) -> RedirectResponse:
    # 设置项目截止日期
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            campaign = ensure_campaign_owner(session, user.id, campaign_id)
            CampaignDeadlineController.SetCampaignDeadline(session, campaign, deadline)
    except HTTPException as error:
        return redirect_with_campaign_management_flash(
            request,
            campaign_id,
            error.detail if isinstance(error.detail, str) else "Unable to save campaign deadline.",
            "error",
            anchor="campaign-deadline",
        )

    return redirect_with_campaign_management_flash(
        request,
        campaign_id,
        "Campaign deadline saved successfully.",
        "success",
        anchor="campaign-deadline",
    )


@app.post("/projects/{campaign_id}/submit")
def submit_campaign_for_approval(
    campaign_id: int,
    request: Request,
) -> RedirectResponse:
    # 提交项目审核
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            campaign = ensure_campaign_owner(session, user.id, campaign_id)
            CampaignApprovalController.SubmitCampaignForApproval(session, campaign)
    except HTTPException as error:
        return redirect_with_campaign_management_flash(
            request,
            campaign_id,
            error.detail if isinstance(error.detail, str) else "Unable to submit campaign for approval.",
            "error",
            anchor="campaign-submission",
        )

    return redirect_with_campaign_management_flash(
        request,
        campaign_id,
        "Campaign submitted for approval successfully.",
        "success",
        anchor="campaign-submission",
    )


@app.post("/projects/{campaign_id}/delete")
def delete_campaign(
    campaign_id: int,
    request: Request,
) -> RedirectResponse:
    # 删除项目
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            campaign = ensure_campaign_owner(session, user.id, campaign_id)
            CampaignController.DeleteCampaign(session, campaign)
    except HTTPException as error:
        return redirect_with_campaign_management_flash(
            request,
            campaign_id,
            error.detail if isinstance(error.detail, str) else "Unable to delete campaign.",
            "error",
            anchor="campaign-delete",
        )

    return redirect_with_flash(
        request,
        "/projects/create-campaign#campaign-library",
        "Campaign deleted successfully.",
        "success",
    )


@app.post("/projects/review/{campaign_id}/approve")
def approve_campaign(
    campaign_id: int,
    request: Request,
    category: str = Form("all"),
    sort: str = Form(DEFAULT_DASHBOARD_REVIEW_SORT),
) -> RedirectResponse:
    # 管理员审核通过项目
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
        return redirect_with_dashboard_flash(
            request,
            error.detail if isinstance(error.detail, str) else "Unable to approve campaign.",
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


@app.post("/projects/review/{campaign_id}/reject")
def reject_campaign(
    campaign_id: int,
    request: Request,
    reason: str = Form(...),
    category: str = Form("all"),
    sort: str = Form(DEFAULT_DASHBOARD_REVIEW_SORT),
) -> RedirectResponse:
    # 管理员驳回项目
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
        return redirect_with_dashboard_flash(
            request,
            error.detail if isinstance(error.detail, str) else "Unable to reject campaign.",
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


@app.get("/profile", response_class=HTMLResponse)
def profile_page(
    request: Request,
    campaign_view: str = Query(default="fundraiser", pattern="^(fundraiser|donee)$"),
) -> HTMLResponse:
    # 个人信息页面
    with get_session() as session:
        try:
            user = get_authenticated_user(request, session)
        except HTTPException:
            return RedirectResponse(url="/auth?mode=login", status_code=303)

        profile = ProfileController.GetProfile(session, user.id)
        own_campaigns = FundraisingCampaign.GetCampaignsByOwner(session, user.id)
        serialized_campaigns = [
            serialize_campaign_summary(session, campaign) for campaign in own_campaigns
        ]
        flash_message = pop_flash_message(request)

    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "request": request,
            "title": "Profile",
            "username": profile["username"],
            "user_email": profile["email"],
            "is_admin": is_admin_email(profile["email"]),
            "gender": profile["gender"],
            "age": profile["age"],
            "occupation": profile["occupation"],
            "contact_details": profile["contact_details"],
            "avatar_url": profile["avatar_url"],
            "campaign_view": campaign_view,
            "campaigns": serialized_campaigns,
            "flash_message": flash_message,
        },
    )


@app.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request) -> HTMLResponse:
    # 设置页面
    with get_session() as session:
        try:
            user = get_authenticated_user(request, session)
        except HTTPException:
            return RedirectResponse(url="/auth?mode=login", status_code=303)

        profile = ProfileController.GetProfile(session, user.id)
        flash_message = pop_flash_message(request)

    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={
            "request": request,
            "title": "Settings",
            "username": profile["username"],
            "user_email": profile["email"],
            "is_admin": is_admin_email(profile["email"]),
            "avatar_url": profile["avatar_url"],
            "flash_message": flash_message,
        },
    )


@app.get("/auth", response_class=HTMLResponse)
def auth_page(
    request: Request,
    mode: str = Query(default="login", pattern="^(login|register|forgot|reset)$"),
) -> HTMLResponse:
    # 登录注册页面
    user_context = get_template_user_context(request)
    return templates.TemplateResponse(
        request=request,
        name="auth.html",
        context={
            "request": request,
            "mode": mode,
            **user_context,
        },
    )


@app.get("/logout")
def logout(request: Request) -> RedirectResponse:
    # 登出账号
    with get_session() as session:
        SessionController.Logout(request, session)
    return RedirectResponse(url="/", status_code=303)


@app.get("/assets/{asset_name}")
def asset(asset_name: str) -> FileResponse:
    # 统一读取图片资源
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
    }
    file_path = allowed.get(asset_name)
    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="Asset not found.")
    return FileResponse(file_path)


@app.post("/api/auth/send-code")
def send_code(payload: SendCodePayload) -> JSONResponse:
    # 发送注册验证码
    with get_session() as session:
        AuthController.RequestVerificationCode(session, payload.email)
    return JSONResponse({"message": "Verification code sent."})


@app.post("/api/auth/register")
def register(payload: RegisterPayload, request: Request) -> JSONResponse:
    # 注册账号
    created_email = payload.email.strip().lower()

    with get_session() as session:
        AuthController.CreateAccount(
            session, payload.username, payload.email, payload.password, payload.code
        )

    with get_session() as session:
        fresh_user = UserAccount.GetUserByEmail(session, created_email)
        if not fresh_user:
            raise HTTPException(status_code=404, detail="Account not found after registration.")
        AuthController.CreateSession(request, session, fresh_user)

    return JSONResponse({"message": "Registration successful.", "redirect": "/"})


@app.post("/api/auth/login")
def login(payload: LoginPayload, request: Request) -> JSONResponse:
    # 登录账号
    with get_session() as session:
        AuthController.Login(request, session, payload.email, payload.password)
    return JSONResponse({"message": "Login successful.", "redirect": "/"})


@app.post("/api/auth/send-reset-code")
def send_reset_code(payload: SendCodePayload) -> JSONResponse:
    # 发送重置密码验证码
    with get_session() as session:
        ForgotPasswordController.RequestResetCode(session, payload.email)
    return JSONResponse({"message": "Password reset code sent."})


@app.post("/api/auth/verify-reset-code")
def verify_reset_code(payload: VerifyResetCodePayload) -> JSONResponse:
    # 校验重置密码验证码
    with get_session() as session:
        ForgotPasswordController.ValidationResetCode(session, payload.email, payload.code)

    return JSONResponse({"message": "Code verified.", "next_mode": "reset"})


@app.post("/api/auth/reset-password")
def reset_password(payload: ResetPasswordPayload) -> JSONResponse:
    # 重置密码
    with get_session() as session:
        ForgotPasswordController.ResetPassword(
            session, payload.email, payload.code, payload.password
        )

    return JSONResponse(
        {"message": "Password updated. You can log in now.", "redirect": "/auth?mode=login"}
    )


@app.post("/api/profile/update")
def update_profile(payload: ProfileUpdatePayload, request: Request) -> JSONResponse:
    # 更新个人信息
    with get_session() as session:
        user = get_authenticated_user(request, session)
        profile = ProfileController.UpdateProfile(
            session,
            user.id,
            payload.username,
            payload.gender,
            payload.age,
            payload.occupation,
            payload.contact_details,
        )

    request.session["username"] = profile["username"]
    return JSONResponse({"message": "Profile updated successfully.", "profile": profile})


@app.post("/api/profile/avatar")
def upload_profile_avatar(request: Request, avatar: UploadFile = File(...)) -> JSONResponse:
    # 上传个人头像
    with get_session() as session:
        user = get_authenticated_user(request, session)
        result = ProfileController.UpdateAvatar(session, user.id, avatar)

    request.session["avatar_url"] = result["avatar_url"]
    return JSONResponse({"message": "Avatar updated successfully.", **result})


@app.post("/api/settings/change-password")
def change_password(payload: ChangePasswordPayload, request: Request) -> JSONResponse:
    # 修改密码
    with get_session() as session:
        user = get_authenticated_user(request, session)
        PasswordController.UpdatePassword(
            session,
            user.id,
            payload.current_password,
            payload.new_password,
            payload.confirm_new_password,
        )

    return JSONResponse({"message": "Password changed successfully."})


@app.post("/api/settings/delete-account")
def delete_account(payload: DeleteAccountPayload, request: Request) -> JSONResponse:
    # 删除账号
    with get_session() as session:
        user = get_authenticated_user(request, session)
        user_account = DeleteAccountController.ValidationCurrentPassword(
            session, user.id, payload.current_password
        )
        DeleteAccountController.DeleteAccount(session, user_account)

    SessionController.ClearAuthentication(request)
    return JSONResponse(
        {
            "message": "Account deleted successfully. You can register again with the same email.",
            "redirect": "/auth?mode=register",
        }
    )
