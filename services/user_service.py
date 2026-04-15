import hmac
import os
import random
import smtplib
from datetime import timedelta
from email.message import EmailMessage

from fastapi import HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.config import (
    DEFAULT_ADMIN_EMAIL,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_USERNAME,
    EMAIL_PATTERN,
    PASSWORD_MIN_LENGTH,
    SUPABASE_AVATAR_BUCKET,
    USER_AVATAR_DIR,
)
from core.db import get_session
from core.security import hash_value, make_salt, now_dt
from core.storage import build_avatar_url, delete_uploaded_asset, store_uploaded_asset
from models.user import (
    AuthenticationToken,
    PasswordHistory,
    PasswordResetCode,
    UserAccount,
    UserProfile,
    UserSession,
    VerificationCode,
)


def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
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


def build_settings_url(anchor: str | None = None) -> str:
    url = "/settings"
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


def redirect_with_settings_flash(
    request: Request,
    message: str,
    kind: str = "success",
    anchor: str | None = None,
) -> RedirectResponse:
    set_flash_message(request, message, kind)
    return RedirectResponse(url=build_settings_url(anchor=anchor), status_code=303)


def send_email_code(receiver: str, code: str, purpose: str) -> None:
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


def get_authenticated_user(request: Request, session: Session) -> UserAccount:
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
    @staticmethod
    def ValidateRegistrationInput(username: str, email: str, password: str) -> tuple[str, str, str]:
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
        if not UserAccount.CheckEmail(session, email):
            raise HTTPException(status_code=409, detail="This email is already registered.")

    @staticmethod
    def SendVerificationEmail(email: str, code: str) -> None:
        send_email_code(email, code, "verification")

    @staticmethod
    def VerifyEmailAddress(session: Session, email: str, code: str) -> VerificationCode:
        return AuthController.ValidationVerificationCode(session, email, code)

    @staticmethod
    def RequestVerificationCode(session: Session, email: str) -> None:
        AuthController.CheckEmail(session, email)
        code = EmailVerification.GenerateCode()
        EmailVerification.StoreCode(session, email, code)
        session.commit()
        AuthController.SendVerificationEmail(email, code)

    @staticmethod
    def ValidationVerificationCode(session: Session, email: str, code: str) -> VerificationCode:
        return EmailVerification.CheckCode(session, email, code)

    @staticmethod
    def CreateAccount(
        session: Session, username: str, email: str, password: str, code: str
    ) -> UserAccount:
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
        user = UserAccount.GetUserByEmail(session, email)
        if not user or not UserAccount.CheckPassword(user, password):
            raise HTTPException(status_code=401, detail="Invalid email or password.")
        return user

    @staticmethod
    def CreateSession(request: Request, session: Session, user: UserAccount) -> None:
        user_session = UserSession.CreateSession(user.id)
        UserSession.StoreSession(session, user_session)
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
        user = AuthController.ValidateCredentials(session, email, password)
        AuthController.CreateSession(request, session, user)
        return user


class SessionController:
    @staticmethod
    def RequestLogout() -> bool:
        return True

    @staticmethod
    def Logout(request: Request, session: Session) -> None:
        SessionController.RequestLogout()
        SessionController.TerminateSession(request, session)
        SessionController.ClearAuthentication(request)

    @staticmethod
    def TerminateSession(request: Request, session: Session) -> None:
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
        request.session.clear()


class ProfileController:
    @staticmethod
    def ViewCurrentProfile(session: Session, user_id: int) -> dict[str, str | None]:
        return ProfileController.GetProfile(session, user_id)

    @staticmethod
    def GetProfile(session: Session, user_id: int) -> dict[str, str | None]:
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
        return ProfileController.UpdateProfile(
            session, user_id, username, gender, age, occupation, contact_details
        )

    @staticmethod
    def UpdateAvatar(session: Session, user_id: int, upload_file: UploadFile) -> dict[str, str]:
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

        import uuid

        avatar_filename = f"{uuid.uuid4().hex}{file_extension}"
        avatar_storage_path = f"users/{user_id}/{avatar_filename}"
        store_uploaded_asset(
            SUPABASE_AVATAR_BUCKET,
            USER_AVATAR_DIR,
            avatar_storage_path,
            file_bytes,
            content_type,
        )

        UserProfile.UpdateAvatarPath(session, user_id, avatar_storage_path)
        session.commit()

        if old_avatar_path:
            delete_uploaded_asset(SUPABASE_AVATAR_BUCKET, USER_AVATAR_DIR, old_avatar_path)

        return {"avatar_url": build_avatar_url(avatar_storage_path) or ""}


class PasswordController:
    @staticmethod
    def ValidationCurrentPassword(
        session: Session, user_id: int, current_password: str
    ) -> UserAccount:
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
    @staticmethod
    def ValidateResetPasswordInput(email: str, password: str) -> tuple[str, str]:
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
        user = UserAccount.GetUserByEmail(session, email)
        if not user:
            raise HTTPException(status_code=404, detail="No account found for this email.")

        code = PasswordResetVerification.GenerateCode()
        PasswordResetVerification.StoreCode(session, email, code)
        session.commit()
        send_email_code(email, code, "password reset")

    @staticmethod
    def ValidationResetCode(session: Session, email: str, code: str) -> PasswordResetCode:
        return PasswordResetVerification.CheckCode(session, email, code)

    @staticmethod
    def ResetPassword(session: Session, email: str, code: str, password: str) -> None:
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
    @staticmethod
    def ValidationCurrentPassword(
        session: Session, user_id: int, current_password: str
    ) -> UserAccount:
        return PasswordController.ValidationCurrentPassword(session, user_id, current_password)

    @staticmethod
    def DeleteAccount(session: Session, user_account: UserAccount) -> None:
        DeleteAccountController.ClearUserProfile(session, user_account.id)
        DeleteAccountController.ClearPasswordHistory(session, user_account.id)
        DeleteAccountController.ClearUserSessions(session, user_account.id)
        DeleteAccountController.ClearVerificationRecords(session, user_account.email)
        session.flush()
        UserAccount.DeleteUser(session, user_account)
        session.commit()

    @staticmethod
    def ClearUserProfile(session: Session, user_id: int) -> None:
        profile = UserProfile.GetProfileDetails(session, user_id)
        if profile:
            if profile.avatar_path:
                delete_uploaded_asset(
                    SUPABASE_AVATAR_BUCKET, USER_AVATAR_DIR, profile.avatar_path
                )
            session.delete(profile)

    @staticmethod
    def ClearPasswordHistory(session: Session, user_id: int) -> None:
        password_history_records = list(
            session.scalars(select(PasswordHistory).where(PasswordHistory.user_id == user_id))
        )
        for record in password_history_records:
            session.delete(record)

    @staticmethod
    def ClearUserSessions(session: Session, user_id: int) -> None:
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
        verification_record = session.get(VerificationCode, email)
        if verification_record:
            session.delete(verification_record)

        password_reset_record = session.get(PasswordResetCode, email)
        if password_reset_record:
            session.delete(password_reset_record)
