from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from core.db import get_session
from core.ui import templates
from models.campaign import FundraisingCampaign
from models.user import UserAccount
from services.campaign_service import build_projects_url, serialize_campaign_summary
from services.donation_service import FavouriteController
from services.user_service import (
    AuthController,
    ChangePasswordPayload,
    DeleteAccountController,
    DeleteAccountPayload,
    ForgotPasswordController,
    LoginPayload,
    PasswordController,
    ProfileController,
    ProfileUpdatePayload,
    RegisterPayload,
    ResetPasswordPayload,
    SendCodePayload,
    SessionController,
    VerifyResetCodePayload,
    get_authenticated_user,
    is_admin_email,
    pop_flash_message,
    should_redirect_direct_visit_to_home,
)


router = APIRouter()


@router.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request) -> HTMLResponse:
    if should_redirect_direct_visit_to_home(request):
        return RedirectResponse(url="/", status_code=303)

    with get_session() as session:
        try:
            user = get_authenticated_user(request, session)
        except HTTPException:
            return RedirectResponse(url="/auth?mode=login", status_code=303)

        profile = ProfileController.GetProfile(session, user.id)
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
            "flash_message": flash_message,
        },
    )


@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request) -> HTMLResponse:
    if should_redirect_direct_visit_to_home(request):
        return RedirectResponse(url="/", status_code=303)

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


@router.get("/auth", response_class=HTMLResponse)
def auth_page(
    request: Request,
    mode: str = Query(default="login", pattern="^(login|register|forgot|reset)$"),
) -> HTMLResponse:
    if should_redirect_direct_visit_to_home(request):
        return RedirectResponse(url="/", status_code=303)

    from services.user_service import get_template_user_context

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


@router.get("/logout")
def logout(request: Request) -> RedirectResponse:
    with get_session() as session:
        SessionController.Logout(request, session)
    return RedirectResponse(url="/", status_code=303)


@router.post("/api/auth/send-code")
def send_code(payload: SendCodePayload) -> JSONResponse:
    with get_session() as session:
        AuthController.RequestVerificationCode(session, payload.email)
    return JSONResponse({"message": "Verification code sent."})


@router.post("/api/auth/register")
def register(payload: RegisterPayload, request: Request) -> JSONResponse:
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


@router.post("/api/auth/login")
def login(payload: LoginPayload, request: Request) -> JSONResponse:
    with get_session() as session:
        AuthController.Login(request, session, payload.email, payload.password)
    return JSONResponse({"message": "Login successful.", "redirect": "/"})


@router.post("/api/auth/send-reset-code")
def send_reset_code(payload: SendCodePayload) -> JSONResponse:
    with get_session() as session:
        ForgotPasswordController.RequestResetCode(session, payload.email)
    return JSONResponse({"message": "Password reset code sent."})


@router.post("/api/auth/verify-reset-code")
def verify_reset_code(payload: VerifyResetCodePayload) -> JSONResponse:
    with get_session() as session:
        ForgotPasswordController.ValidationResetCode(session, payload.email, payload.code)

    return JSONResponse({"message": "Code verified.", "next_mode": "reset"})


@router.post("/api/auth/reset-password")
def reset_password(payload: ResetPasswordPayload) -> JSONResponse:
    with get_session() as session:
        ForgotPasswordController.ResetPassword(
            session, payload.email, payload.code, payload.password
        )

    return JSONResponse(
        {"message": "Password updated. You can log in now.", "redirect": "/auth?mode=login"}
    )


@router.post("/api/profile/update")
def update_profile(payload: ProfileUpdatePayload, request: Request) -> JSONResponse:
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


@router.post("/api/profile/avatar")
def upload_profile_avatar(request: Request, avatar: UploadFile = File(...)) -> JSONResponse:
    with get_session() as session:
        user = get_authenticated_user(request, session)
        result = ProfileController.UpdateAvatar(session, user.id, avatar)

    request.session["avatar_url"] = result["avatar_url"]
    return JSONResponse({"message": "Avatar updated successfully.", **result})


@router.post("/api/settings/change-password")
def change_password(payload: ChangePasswordPayload, request: Request) -> JSONResponse:
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


@router.post("/api/settings/delete-account")
def delete_account(payload: DeleteAccountPayload, request: Request) -> JSONResponse:
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
