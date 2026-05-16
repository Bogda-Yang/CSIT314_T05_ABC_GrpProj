import hmac
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, delete, func, or_, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from core.security import hash_value, make_salt, now_dt
from models import Base


class UserAccount(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    salt: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    @staticmethod
    def CreateUser(username: str, email: str, password: str) -> "UserAccount":
        password_salt = make_salt()
        return UserAccount(
            username=username.strip(),
            email=email,
            password_hash=hash_value(password, password_salt),
            salt=password_salt,
            created_at=now_dt(),
            status="active",
            last_login_at=None,
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
    def GetAllAccounts(session: Session) -> list["UserAccount"]:
        statement = select(UserAccount).order_by(UserAccount.created_at.desc(), UserAccount.id.desc())
        return list(session.scalars(statement))

    @staticmethod
    def GetAccountById(session: Session, user_id: int) -> "UserAccount | None":
        return UserAccount.GetUserAccount(session, user_id)

    @staticmethod
    def SearchAccounts(session: Session, search_keywords: str) -> list["UserAccount"]:
        clean_keywords = search_keywords.strip().lower()
        if not clean_keywords:
            return UserAccount.GetAllAccounts(session)
        search_pattern = f"%{clean_keywords}%"
        statement = (
            select(UserAccount)
            .where(
                or_(
                    func.lower(UserAccount.username).like(search_pattern),
                    func.lower(UserAccount.email).like(search_pattern),
                )
            )
            .order_by(UserAccount.created_at.desc(), UserAccount.id.desc())
        )
        return list(session.scalars(statement))

    @staticmethod
    def FilterAccounts(session: Session, status: str | None = None) -> list["UserAccount"]:
        statement = select(UserAccount)
        if status:
            statement = statement.where(UserAccount.status == status)
        statement = statement.order_by(UserAccount.created_at.desc(), UserAccount.id.desc())
        return list(session.scalars(statement))

    @staticmethod
    def UpdateStatus(user_account: "UserAccount", status: str) -> None:
        user_account.status = status

    @staticmethod
    def MarkLastLogin(user_account: "UserAccount") -> None:
        user_account.last_login_at = now_dt()

    @staticmethod
    def DeleteUser(session: Session, user_account: "UserAccount") -> None:
        session.delete(user_account)


class VerificationCode(Base):
    __tablename__ = "verification_codes"

    email: Mapped[str] = mapped_column(String(255), primary_key=True)
    code_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    salt: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @staticmethod
    def FindVerificationRecord(session: Session, email: str) -> "VerificationCode | None":
        return session.get(VerificationCode, email)

    @staticmethod
    def DeleteVerificationRecord(session: Session, email: str) -> None:
        record = VerificationCode.FindVerificationRecord(session, email)
        if record:
            session.delete(record)


class PasswordResetCode(Base):
    __tablename__ = "password_reset_codes"

    email: Mapped[str] = mapped_column(String(255), primary_key=True)
    code_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    salt: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @staticmethod
    def FindPasswordResetRecord(session: Session, email: str) -> "PasswordResetCode | None":
        return session.get(PasswordResetCode, email)

    @staticmethod
    def DeletePasswordResetRecord(session: Session, email: str) -> None:
        record = PasswordResetCode.FindPasswordResetRecord(session, email)
        if record:
            session.delete(record)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    contact_details: Mapped[str] = mapped_column(Text, nullable=False, default="")
    avatar_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(30), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    occupation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    available_balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @staticmethod
    def GetProfileDetails(session: Session, user_id: int) -> "UserProfile | None":
        return session.get(UserProfile, user_id)

    @staticmethod
    def DeleteProfile(session: Session, user_id: int) -> None:
        profile = UserProfile.GetProfileDetails(session, user_id)
        if profile:
            session.delete(profile)

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
                available_balance=0,
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
    def GetOrCreateProfile(session: Session, user_id: int) -> "UserProfile":
        profile = UserProfile.GetProfileDetails(session, user_id)
        if profile:
            return profile

        profile = UserProfile(
            user_id=user_id,
            contact_details="",
            avatar_path=None,
            gender=None,
            age=None,
            occupation=None,
            available_balance=0,
            created_at=now_dt(),
            updated_at=now_dt(),
        )
        session.add(profile)
        return profile

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
                available_balance=0,
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
    def AddAvailableBalance(session: Session, user_id: int, amount: int) -> "UserProfile":
        profile = UserProfile.GetOrCreateProfile(session, user_id)
        profile.available_balance = int(profile.available_balance or 0) + int(amount)
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

    @staticmethod
    def GetPasswordHistoryRecords(session: Session, user_id: int) -> list["PasswordHistory"]:
        statement = select(PasswordHistory).where(PasswordHistory.user_id == user_id)
        return list(session.scalars(statement))

    @staticmethod
    def DeletePasswordHistoryRecord(session: Session, record: "PasswordHistory") -> None:
        session.delete(record)


class UserSession(Base):
    __tablename__ = "user_sessions"

    session_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    invalidated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    @staticmethod
    def CreateSession(user_id: int) -> "UserSession":
        import secrets

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
    def GetSessionsByUserId(session: Session, user_id: int) -> list["UserSession"]:
        statement = select(UserSession).where(UserSession.user_id == user_id)
        return list(session.scalars(statement))

    @staticmethod
    def InvalidateSession(user_session: "UserSession") -> None:
        user_session.invalidated_at = now_dt()

    @staticmethod
    def DeleteSessionRecord(session: Session, user_session: "UserSession") -> None:
        session.delete(user_session)


class AuthenticationToken(Base):
    __tablename__ = "authentication_tokens"

    token: Mapped[str] = mapped_column(String(80), primary_key=True)
    session_key: Mapped[str] = mapped_column(
        ForeignKey("user_sessions.session_key"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    @staticmethod
    def CreateToken(session_key: str) -> "AuthenticationToken":
        import secrets

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
    def GetTokensBySessionKey(session: Session, session_key: str) -> list["AuthenticationToken"]:
        statement = select(AuthenticationToken).where(
            AuthenticationToken.session_key == session_key
        )
        return list(session.scalars(statement))

    @staticmethod
    def RevokeToken(token: "AuthenticationToken") -> None:
        token.revoked_at = now_dt()

    @staticmethod
    def DeleteTokenRecord(session: Session, token: "AuthenticationToken") -> None:
        session.delete(token)


class UserActivityLog(Base):
    __tablename__ = "user_activity_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    details: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    @staticmethod
    def RecordActivity(
        session: Session, user_id: int, activity_type: str, details: str = ""
    ) -> "UserActivityLog":
        activity = UserActivityLog(
            user_id=user_id,
            activity_type=activity_type.strip(),
            details=details.strip(),
            created_at=now_dt(),
        )
        session.add(activity)
        return activity

    @staticmethod
    def GetUserActivity(
        session: Session, user_id: int, limit: int = 10
    ) -> list["UserActivityLog"]:
        statement = (
            select(UserActivityLog)
            .where(UserActivityLog.user_id == user_id)
            .order_by(UserActivityLog.created_at.desc(), UserActivityLog.id.desc())
            .limit(limit)
        )
        return list(session.scalars(statement))

    @staticmethod
    def GetLastLogin(session: Session, user_id: int) -> datetime | None:
        statement = (
            select(UserActivityLog.created_at)
            .where(
                UserActivityLog.user_id == user_id,
                UserActivityLog.activity_type == "login",
            )
            .order_by(UserActivityLog.created_at.desc(), UserActivityLog.id.desc())
            .limit(1)
        )
        return session.scalar(statement)

    @staticmethod
    def DeleteUserActivity(session: Session, user_id: int) -> None:
        session.execute(delete(UserActivityLog).where(UserActivityLog.user_id == user_id))


class AccountStatus:
    @staticmethod
    def SetInactive(user_account: UserAccount) -> None:
        UserAccount.UpdateStatus(user_account, "inactive")

    @staticmethod
    def GetStatus(user_account: UserAccount) -> str:
        return user_account.status or "active"
