import hmac
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, select
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
    __tablename__ = "verification_codes"

    email: Mapped[str] = mapped_column(String(255), primary_key=True)
    code_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    salt: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class PasswordResetCode(Base):
    __tablename__ = "password_reset_codes"

    email: Mapped[str] = mapped_column(String(255), primary_key=True)
    code_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    salt: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


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
    def InvalidateSession(user_session: "UserSession") -> None:
        user_session.invalidated_at = now_dt()


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
    def RevokeToken(token: "AuthenticationToken") -> None:
        token.revoked_at = now_dt()
