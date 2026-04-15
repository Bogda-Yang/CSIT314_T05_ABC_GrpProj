from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse

from core.db import get_session
from core.ui import templates
from models.campaign import FundraisingCampaign
from models.user import UserProfile
from services.campaign_service import (
    CAMPAIGN_CATEGORY_OPTIONS,
    CampaignApprovalController,
    CampaignController,
    CampaignDeadlineController,
    CampaignDescriptionController,
    CampaignGoalController,
    CampaignImageController,
    build_campaign_management_url,
    ensure_campaign_owner,
    redirect_with_campaign_create_flash,
    redirect_with_campaign_management_flash,
    serialize_campaign_detail,
    serialize_campaign_summary,
)
from services.user_service import (
    get_authenticated_user,
    is_admin_email,
    pop_flash_message,
    redirect_with_flash,
)
from core.storage import build_avatar_url


router = APIRouter()


@router.get("/projects/create-campaign", response_class=HTMLResponse)
def campaign_create_page(request: Request) -> HTMLResponse:
    with get_session() as session:
        try:
            user = get_authenticated_user(request, session)
        except HTTPException:
            return RedirectResponse(url="/auth?mode=login", status_code=303)

        profile = UserProfile.GetProfileDetails(session, user.id)
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
            "username": user.username,
            "user_email": user.email,
            "avatar_url": build_avatar_url(profile.avatar_path) if profile else None,
            "is_admin": is_admin_email(user.email),
            "flash_message": flash_message,
            "category_options": CAMPAIGN_CATEGORY_OPTIONS,
            "campaigns": serialized_campaigns,
        },
    )


@router.get("/projects/manage/{campaign_id}", response_class=HTMLResponse)
def campaign_management_page(
    request: Request,
    campaign_id: int,
) -> HTMLResponse:
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


@router.post("/projects/create")
def create_campaign(
    request: Request,
    title: str = Form(...),
    category: str = Form("other"),
) -> RedirectResponse:
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            campaign = CampaignController.CreateCampaign(session, user.id, title, category)
    except HTTPException as error:
        detail = getattr(error, "detail", "Unable to create campaign.")
        return redirect_with_campaign_create_flash(
            request,
            detail if isinstance(detail, str) else "Unable to create campaign.",
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


@router.post("/projects/{campaign_id}/basic")
def update_campaign_basic_information(
    campaign_id: int,
    request: Request,
    title: str = Form(...),
    category: str = Form("other"),
) -> RedirectResponse:
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            campaign = ensure_campaign_owner(session, user.id, campaign_id)
            CampaignController.UpdateCampaign(session, campaign, title, category)
    except HTTPException as error:
        detail = getattr(error, "detail", "Unable to update campaign.")
        return redirect_with_campaign_management_flash(
            request,
            campaign_id,
            detail if isinstance(detail, str) else "Unable to update campaign.",
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


@router.post("/projects/{campaign_id}/goal")
def set_campaign_goal(
    campaign_id: int,
    request: Request,
    goal_amount: int = Form(...),
) -> RedirectResponse:
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            campaign = ensure_campaign_owner(session, user.id, campaign_id)
            CampaignGoalController.SetFundraisingGoal(session, campaign, goal_amount)
    except HTTPException as error:
        detail = getattr(error, "detail", "Unable to save fundraising goal.")
        return redirect_with_campaign_management_flash(
            request,
            campaign_id,
            detail if isinstance(detail, str) else "Unable to save fundraising goal.",
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


@router.post("/projects/{campaign_id}/description")
def set_campaign_description(
    campaign_id: int,
    request: Request,
    description: str = Form(...),
) -> RedirectResponse:
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            campaign = ensure_campaign_owner(session, user.id, campaign_id)
            CampaignDescriptionController.AddCampaignDescription(session, campaign, description)
    except HTTPException as error:
        detail = getattr(error, "detail", "Unable to save campaign description.")
        return redirect_with_campaign_management_flash(
            request,
            campaign_id,
            detail if isinstance(detail, str) else "Unable to save campaign description.",
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


@router.post("/projects/{campaign_id}/images")
def upload_campaign_images(
    campaign_id: int,
    request: Request,
    images: list[UploadFile] = File(...),
) -> RedirectResponse:
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            campaign = ensure_campaign_owner(session, user.id, campaign_id)
            CampaignImageController.UploadCampaignImages(session, campaign, images)
    except HTTPException as error:
        detail = getattr(error, "detail", "Unable to upload campaign images.")
        return redirect_with_campaign_management_flash(
            request,
            campaign_id,
            detail if isinstance(detail, str) else "Unable to upload campaign images.",
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


@router.post("/projects/{campaign_id}/images/{image_id}/delete")
def delete_campaign_image(
    campaign_id: int,
    image_id: int,
    request: Request,
) -> RedirectResponse:
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            campaign = ensure_campaign_owner(session, user.id, campaign_id)
            CampaignImageController.DeleteCampaignImage(session, campaign, image_id)
    except HTTPException as error:
        detail = getattr(error, "detail", "Unable to delete campaign image.")
        return redirect_with_campaign_management_flash(
            request,
            campaign_id,
            detail if isinstance(detail, str) else "Unable to delete campaign image.",
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


@router.post("/projects/{campaign_id}/deadline")
def set_campaign_deadline(
    campaign_id: int,
    request: Request,
    deadline: str = Form(...),
) -> RedirectResponse:
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            campaign = ensure_campaign_owner(session, user.id, campaign_id)
            CampaignDeadlineController.SetCampaignDeadline(session, campaign, deadline)
    except HTTPException as error:
        detail = getattr(error, "detail", "Unable to save campaign deadline.")
        return redirect_with_campaign_management_flash(
            request,
            campaign_id,
            detail if isinstance(detail, str) else "Unable to save campaign deadline.",
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


@router.post("/projects/{campaign_id}/submit")
def submit_campaign_for_approval(
    campaign_id: int,
    request: Request,
) -> RedirectResponse:
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            campaign = ensure_campaign_owner(session, user.id, campaign_id)
            CampaignApprovalController.SubmitCampaignForApproval(session, campaign)
    except HTTPException as error:
        detail = getattr(error, "detail", "Unable to submit campaign for approval.")
        return redirect_with_campaign_management_flash(
            request,
            campaign_id,
            detail if isinstance(detail, str) else "Unable to submit campaign for approval.",
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


@router.post("/projects/{campaign_id}/delete")
def delete_campaign(
    campaign_id: int,
    request: Request,
) -> RedirectResponse:
    try:
        with get_session() as session:
            user = get_authenticated_user(request, session)
            campaign = ensure_campaign_owner(session, user.id, campaign_id)
            CampaignController.DeleteCampaign(session, campaign)
    except HTTPException as error:
        detail = getattr(error, "detail", "Unable to delete campaign.")
        return redirect_with_campaign_management_flash(
            request,
            campaign_id,
            detail if isinstance(detail, str) else "Unable to delete campaign.",
            "error",
            anchor="campaign-delete",
        )

    return redirect_with_flash(
        request,
        "/profile?campaign_view=fundraiser#my-campaigns",
        "Campaign deleted successfully.",
        "success",
    )
