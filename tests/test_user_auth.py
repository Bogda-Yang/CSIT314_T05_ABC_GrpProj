import pytest
from fastapi import HTTPException

from models.user import UserAccount, UserProfile
from services.user_service import AuthController

from tests.helpers import FakeSession, make_profile, make_user
from tests.test_data import (
    LOGIN_CASES,
    LOGIN_REJECTION_CASES,
    REGISTER_CASES,
    REGISTRATION_VALIDATION_CASES,
)


@pytest.mark.parametrize("register_data", REGISTER_CASES)
def test_create_account_uses_hardcoded_registration_data(monkeypatch, register_data):
    session = FakeSession()
    verification_record = object()
    monkeypatch.setattr(AuthController, "CheckEmail", staticmethod(lambda _session, _email: None))
    monkeypatch.setattr(
        AuthController,
        "VerifyEmailAddress",
        staticmethod(lambda _session, _email, _code: verification_record),
    )

    user = AuthController.CreateAccount(
        session,
        register_data["username"],
        register_data["email"],
        register_data["password"],
        register_data["code"],
    )

    assert user.username == register_data["username"]
    assert user.email == register_data["email"]
    assert verification_record in session.deleted
    assert session.commits == 1


@pytest.mark.parametrize("username,email,password,expected_status", REGISTRATION_VALIDATION_CASES)
def test_validate_registration_input(username, email, password, expected_status):
    if expected_status is None:
        clean_username, clean_email, clean_password = AuthController.ValidateRegistrationInput(
            username, email, password
        )
        assert clean_username == username.strip()
        assert clean_email == email.strip().lower()
        assert clean_password == password
        return

    with pytest.raises(HTTPException) as error:
        AuthController.ValidateRegistrationInput(username, email, password)
    assert error.value.status_code == expected_status


@pytest.mark.parametrize("login_data", LOGIN_CASES)
def test_login_success_creates_session(monkeypatch, dummy_request, login_data):
    session = FakeSession()
    user = make_user(login_data["username"], login_data["email"], user_id=2, password=login_data["password"])
    profile = make_profile(user.id)
    monkeypatch.setattr(
        UserAccount,
        "GetUserByEmail",
        staticmethod(lambda _session, email: user if email == login_data["email"] else None),
    )
    monkeypatch.setattr(
        UserProfile,
        "GetProfileDetails",
        staticmethod(lambda _session, user_id: profile if user_id == user.id else None),
    )

    logged_in_user = AuthController.Login(dummy_request, session, login_data["email"], login_data["password"])

    assert logged_in_user.id == user.id
    assert dummy_request.session["user_email"] == login_data["email"]
    assert dummy_request.session["session_key"]
    assert dummy_request.session["auth_token"]


@pytest.mark.parametrize("email,password,status,expected_status", LOGIN_REJECTION_CASES)
def test_login_rejects_invalid_credentials(monkeypatch, dummy_request, email, password, status, expected_status):
    session = FakeSession()
    user = make_user("Login User", "login.user@example.com", user_id=3, status=status)
    monkeypatch.setattr(
        UserAccount,
        "GetUserByEmail",
        staticmethod(lambda _session, candidate_email: user if candidate_email == user.email else None),
    )

    with pytest.raises(HTTPException) as error:
        AuthController.Login(dummy_request, session, email, password)
    assert error.value.status_code == expected_status
