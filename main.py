import hashlib
import hmac
import os
import random
import re
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from starlette.middleware.sessions import SessionMiddleware


BASE_DIR = Path(__file__).resolve().parent
SINGAPORE_TZ = timezone(timedelta(hours=8))
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is required. Configure a Supabase Postgres connection string in .env."
    )


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
    def CheckPassword(user: "UserAccount", password: str) -> bool:
        candidate_hash = hash_value(password, user.salt)
        return hmac.compare_digest(candidate_hash, user.password_hash)

    @staticmethod
    def GetUserAccount(session: Session, user_id: int) -> "UserAccount | None":
        return session.get(UserAccount, user_id)


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
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @staticmethod
    def GetProfileDetails(session: Session, user_id: int) -> "UserProfile | None":
        return session.get(UserProfile, user_id)

    @staticmethod
    def UpdateProfileDetails(
        session: Session, user_id: int, username: str, contact_details: str
    ) -> tuple["UserAccount", "UserProfile"]:
        user_account = UserAccount.GetUserAccount(session, user_id)
        if not user_account:
            raise HTTPException(status_code=404, detail="Account not found.")

        profile = UserProfile.GetProfileDetails(session, user_id)
        if not profile:
            profile = UserProfile(
                user_id=user_id,
                contact_details="",
                created_at=now_dt(),
                updated_at=now_dt(),
            )
            session.add(profile)

        user_account.username = username.strip()
        profile.contact_details = contact_details.strip()
        profile.updated_at = now_dt()
        return user_account, profile

    @staticmethod
    def SaveProfile(session: Session, profile: "UserProfile") -> None:
        session.add(profile)

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
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


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
    password: str = Field(min_length=8, max_length=128)
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
    password: str = Field(min_length=8, max_length=128)

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
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not EMAIL_PATTERN.match(value):
            raise ValueError("Enter a valid email address.")
        return value


class ProfileUpdatePayload(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    contact_details: str = Field(max_length=500)


class ChangePasswordPayload(BaseModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
    confirm_new_password: str = Field(min_length=8, max_length=128)


class DeleteAccountPayload(BaseModel):
    current_password: str = Field(min_length=8, max_length=128)


def now_dt() -> datetime:
    return datetime.now(SINGAPORE_TZ)


def hash_value(value: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", value.encode("utf-8"), salt.encode("utf-8"), 120_000
    ).hex()


def make_salt() -> str:
    return os.urandom(16).hex()


def get_session() -> Session:
    return SessionLocal()


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
    def RequestVerificationCode(session: Session, email: str) -> None:
        # 请求注册验证码
        existing_user = UserAccount.GetUserByEmail(session, email)
        if existing_user:
            raise HTTPException(status_code=409, detail="This email is already registered.")

        code = EmailVerification.GenerateCode()
        EmailVerification.StoreCode(session, email, code)
        session.commit()
        send_email_code(email, code, "verification")

    @staticmethod
    def ValidationVerificationCode(session: Session, email: str, code: str) -> VerificationCode:
        # 校验注册验证码
        return EmailVerification.CheckCode(session, email, code)

    @staticmethod
    def CreateAccount(
        session: Session, username: str, email: str, password: str, code: str
    ) -> UserAccount:
        # 注册账号
        if UserAccount.GetUserByEmail(session, email):
            raise HTTPException(status_code=409, detail="This email is already registered.")

        record = AuthController.ValidationVerificationCode(session, email, code)
        user = UserAccount.CreateUser(username, email, password)
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
        auth_token = AuthenticationToken.CreateToken(user_session.session_key)
        UserSession.StoreSession(session, user_session)
        session.add(auth_token)
        session.commit()

        request.session["user_email"] = user.email
        request.session["username"] = user.username
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
    def Logout(request: Request, session: Session) -> None:
        # 退出登录
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
    def GetProfile(session: Session, user_id: int) -> dict[str, str]:
        # 获取个人信息
        user_account = UserAccount.GetUserAccount(session, user_id)
        if not user_account:
            raise HTTPException(status_code=404, detail="Account not found.")

        profile = UserProfile.GetProfileDetails(session, user_id)
        if not profile:
            profile = UserProfile(
                user_id=user_id,
                contact_details="",
                created_at=now_dt(),
                updated_at=now_dt(),
            )
            UserProfile.SaveProfile(session, profile)
            session.commit()

        return {
            "username": user_account.username,
            "email": user_account.email,
            "contact_details": profile.contact_details,
        }

    @staticmethod
    def ValidateProfileInput(username: str, contact_details: str) -> tuple[str, str]:
        # 校验个人信息输入
        username = username.strip()
        contact_details = contact_details.strip()

        if len(username) < 2:
            raise HTTPException(status_code=400, detail="Username must be at least 2 characters.")
        if len(username) > 50:
            raise HTTPException(status_code=400, detail="Username must be 50 characters or fewer.")
        if len(contact_details) > 500:
            raise HTTPException(
                status_code=400, detail="Contact details must be 500 characters or fewer."
            )
        return username, contact_details

    @staticmethod
    def UpdateProfile(
        session: Session, user_id: int, username: str, contact_details: str
    ) -> dict[str, str]:
        # 更新个人信息
        clean_username, clean_contact_details = ProfileController.ValidateProfileInput(
            username, contact_details
        )
        user_account, profile = UserProfile.UpdateProfileDetails(
            session, user_id, clean_username, clean_contact_details
        )
        UserProfile.SaveProfile(session, profile)
        session.commit()
        return {
            "username": user_account.username,
            "email": user_account.email,
            "contact_details": profile.contact_details,
        }


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
        if len(new_password) < 8:
            raise HTTPException(
                status_code=400, detail="New password must be at least 8 characters."
            )

        for history in PasswordHistory.GetPreviousPasswords(session, user_id):
            if hmac.compare_digest(hash_value(new_password, history.salt), history.password_hash):
                raise HTTPException(
                    status_code=400,
                    detail="Choose a password that has not been used recently.",
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
        PasswordHistory.StorePasswordHistory(session, user_account)
        UserProfile.UpdatePasswordHash(user_account, new_password)
        session.commit()


class ForgotPasswordController:
    # 忘记密码控制器
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
        user = UserAccount.GetUserByEmail(session, email)
        if not user:
            raise HTTPException(status_code=404, detail="No account found for this email.")

        record = ForgotPasswordController.ValidationResetCode(session, email, code)
        PasswordHistory.StorePasswordHistory(session, user)
        UserProfile.UpdatePasswordHash(user, password)
        session.delete(record)
        session.commit()


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
        profile = UserProfile.GetProfileDetails(session, user_account.id)
        if profile:
            session.delete(profile)

        password_history_records = list(
            session.scalars(
                select(PasswordHistory).where(PasswordHistory.user_id == user_account.id)
            )
        )
        for record in password_history_records:
            session.delete(record)

        session_records = list(
            session.scalars(select(UserSession).where(UserSession.user_id == user_account.id))
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

        verification_record = session.get(VerificationCode, user_account.email)
        if verification_record:
            session.delete(verification_record)

        password_reset_record = session.get(PasswordResetCode, user_account.email)
        if password_reset_record:
            session.delete(password_reset_record)

        session.delete(user_account)
        session.commit()


@app.on_event("startup")
def startup() -> None:
    # 启动应用并自动建表
    Base.metadata.create_all(bind=engine)


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    # 首页
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user_email": request.session.get("user_email"),
            "username": request.session.get("username"),
        },
    )


@app.get("/about", response_class=HTMLResponse)
def about_page(request: Request) -> HTMLResponse:
    # 关于我们页面
    return templates.TemplateResponse(
        "about.html",
        {
            "request": request,
            "username": request.session.get("username"),
            "user_email": request.session.get("user_email"),
        },
    )


@app.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request) -> HTMLResponse:
    # 个人信息页面
    with get_session() as session:
        try:
            user = get_authenticated_user(request, session)
        except HTTPException:
            return RedirectResponse(url="/auth?mode=login", status_code=303)

        profile = ProfileController.GetProfile(session, user.id)

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "title": "Profile",
            "username": profile["username"],
            "user_email": profile["email"],
            "contact_details": profile["contact_details"],
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

    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "title": "Settings",
            "username": profile["username"],
            "user_email": profile["email"],
        },
    )


@app.get("/auth", response_class=HTMLResponse)
def auth_page(
    request: Request,
    mode: str = Query(default="login", pattern="^(login|register|forgot|reset)$"),
) -> HTMLResponse:
    # 登录注册页面
    return templates.TemplateResponse(
        "auth.html",
        {
            "request": request,
            "mode": mode,
            "user_email": request.session.get("user_email"),
            "username": request.session.get("username"),
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
    with get_session() as session:
        user = AuthController.CreateAccount(
            session, payload.username, payload.email, payload.password, payload.code
        )

    with get_session() as session:
        fresh_user = UserAccount.GetUserByEmail(session, user.email)
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
            session, user.id, payload.username, payload.contact_details
        )

    request.session["username"] = profile["username"]
    return JSONResponse({"message": "Profile updated successfully.", "profile": profile})


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
