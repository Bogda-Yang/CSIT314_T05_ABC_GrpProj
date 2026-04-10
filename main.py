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

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, create_engine, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from starlette.middleware.sessions import SessionMiddleware


BASE_DIR = Path(__file__).resolve().parent
SINGAPORE_TZ = timezone(timedelta(hours=8))
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PASSWORD_MIN_LENGTH = 6
USER_AVATAR_DIR = BASE_DIR / "uploads" / "avatars"

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
app.mount("/user-uploads", StaticFiles(directory=USER_AVATAR_DIR), name="user_uploads")
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


def get_template_user_context(request: Request) -> dict[str, str | None]:
    # 获取模板使用的当前登录上下文，仅当数据库会话仍然有效时才返回用户信息
    with get_session() as session:
        try:
            user_account = get_authenticated_user(request, session)
            profile = UserProfile.GetProfileDetails(session, user_account.id)
        except HTTPException:
            return {
                "user_email": None,
                "username": None,
                "avatar_url": None,
            }

    return {
        "user_email": user_account.email,
        "username": user_account.username,
        "avatar_url": build_avatar_url(profile.avatar_path) if profile else None,
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


@app.on_event("startup")
def startup() -> None:
    # 启动应用并自动建表
    with engine.begin() as connection:
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
def projects_page(request: Request) -> HTMLResponse:
    # 公益项目页面
    user_context = get_template_user_context(request)
    return templates.TemplateResponse(
        request=request,
        name="placeholder.html",
        context={
            "request": request,
            "title": "Projects",
            "description": "Projects page content is reserved for future updates.",
            **user_context,
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
        request=request,
        name="profile.html",
        context={
            "request": request,
            "title": "Profile",
            "username": profile["username"],
            "user_email": profile["email"],
            "gender": profile["gender"],
            "age": profile["age"],
            "occupation": profile["occupation"],
            "contact_details": profile["contact_details"],
            "avatar_url": profile["avatar_url"],
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
        request=request,
        name="settings.html",
        context={
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
