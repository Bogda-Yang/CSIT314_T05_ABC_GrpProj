from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse

from core.config import BASE_DIR
from core.db import get_session
from core.ui import templates
from services.campaign_service import normalize_campaign_category
from services.donation_service import (
    get_projects_category_filters,
    get_published_campaign_summaries,
    get_selected_category_label,
)
from services.user_service import get_template_user_context, pop_flash_message


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    user_context = get_template_user_context(request)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            **user_context,
        },
    )


@router.get("/about", response_class=HTMLResponse)
def about_page(request: Request) -> HTMLResponse:
    user_context = get_template_user_context(request)
    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context={
            "request": request,
            **user_context,
        },
    )


@router.get("/transparency", response_class=HTMLResponse)
def transparency_page(request: Request) -> HTMLResponse:
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


@router.get("/projects", response_class=HTMLResponse)
def projects_page(
    request: Request,
    category: str | None = Query(default=None),
) -> HTMLResponse:
    requested_category = (category or "").strip().lower()
    selected_category = None
    if requested_category and requested_category != "all":
        selected_category = normalize_campaign_category(requested_category)

    with get_session() as session:
        published_campaigns = get_published_campaign_summaries(session, selected_category)
        primary_category_filters, overflow_category_filters = get_projects_category_filters(
            selected_category
        )

    user_context = get_template_user_context(request)
    flash_message = pop_flash_message(request)
    return templates.TemplateResponse(
        request=request,
        name="projects.html",
        context={
            "request": request,
            "title": "Projects",
            "flash_message": flash_message,
            "selected_category": selected_category,
            "selected_category_label": get_selected_category_label(selected_category),
            "primary_category_filters": primary_category_filters,
            "overflow_category_filters": overflow_category_filters,
            "published_campaigns": published_campaigns,
            **user_context,
        },
    )


@router.get("/assets/{asset_name}")
def asset(asset_name: str) -> FileResponse:
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
