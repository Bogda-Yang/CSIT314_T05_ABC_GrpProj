import os

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from starlette.middleware.sessions import SessionMiddleware

from core.config import (
    BASE_DIR,
    CAMPAIGN_IMAGE_DIR,
    IS_RENDER,
    SUPABASE_AVATAR_BUCKET,
    SUPABASE_CAMPAIGN_BUCKET,
    USER_AVATAR_DIR,
)
from core.db import engine, get_session
from core.storage import SupabaseStorage
from models import Base
from routers import admin, donee, fundraiser, user
from services.user_service import ensure_default_admin_account, request_validation_exception_handler


app = FastAPI(title="FireflyFund")
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "fireflyfund-dev-secret"),
    same_site="lax",
    https_only=False,
)

USER_AVATAR_DIR.mkdir(parents=True, exist_ok=True)
CAMPAIGN_IMAGE_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.mount("/user-uploads", StaticFiles(directory=USER_AVATAR_DIR), name="user_uploads")
app.mount("/campaign-uploads", StaticFiles(directory=CAMPAIGN_IMAGE_DIR), name="campaign_uploads")

app.add_exception_handler(RequestValidationError, request_validation_exception_handler)

app.include_router(donee.router)
app.include_router(user.router)
app.include_router(fundraiser.router)
app.include_router(admin.router)


@app.on_event("startup")
def startup() -> None:
    if SupabaseStorage.IsConfigured():
        try:
            SupabaseStorage.EnsurePublicBucket(SUPABASE_AVATAR_BUCKET)
            SupabaseStorage.EnsurePublicBucket(SUPABASE_CAMPAIGN_BUCKET)
        except RuntimeError as error:
            print(f"Warning: unable to verify Supabase Storage buckets: {error}")

    if IS_RENDER:
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
        connection.execute(text("ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS age INTEGER"))
        connection.execute(
            text("ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS occupation VARCHAR(100)")
        )
        connection.execute(text("DELETE FROM authentication_tokens"))
        connection.execute(text("DELETE FROM user_sessions"))
    Base.metadata.create_all(bind=engine)
    with get_session() as session:
        ensure_default_admin_account(session)
