from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse

from core.db import get_session
from core.ui import templates
from models.campaign import FundraisingCampaign
from models.user import UserProfile
from services.campaign_service import (
    CampaignApprovalController,
    CampaignAnalyticsController,
    CampaignController,
    CampaignDeadlineController,
    CampaignDescriptionController,
    CampaignDetailSerializer,
    CampaignFilterController,
    CampaignGoalController,
    CampaignHistoryController,
    CampaignImageController,
    build_campaign_management_url,
    build_your_fundraisers_url,
    ensure_campaign_owner,
    get_campaign_category_options,
    get_fundraiser_category_filters,
    get_fundraiser_lifecycle_filters,
    get_fundraiser_sort_filters,
    normalize_campaign_category,
    normalize_fundraiser_campaign_sort,
    normalize_fundraiser_lifecycle,
    redirect_with_campaign_create_flash,
    redirect_with_campaign_management_flash,
    serialize_campaign_summary,
)
from services.user_service import (
    get_authenticated_user,
    is_admin_email,
    pop_flash_message,
    redirect_with_flash,
    should_redirect_direct_visit_to_home,
)
from core.storage import build_avatar_url


router = APIRouter()


@router.get("/projects/create-campaign", response_class=HTMLResponse)
def campaign_create_page(request: Request) -> HTMLResponse:
    return CampaignManagementPage.AccessCampaignCreationPage(request)


@router.get("/your-fundraisers", response_class=HTMLResponse)
def your_fundraisers_page(
    request: Request,
    category: str | None = Query(default=None),
    lifecycle: str = Query(default="all"),
    sort: str = Query(default="updated_desc"),
) -> HTMLResponse:
    return CampaignAnalysisPage.ViewFilteredCampaigns(request, category, lifecycle, sort)


@router.get("/projects/manage/{campaign_id}", response_class=HTMLResponse)
def campaign_management_page(
    request: Request,
    campaign_id: int,
) -> HTMLResponse:
    return CampaignManagementPage.AccessCampaignManagementPage(request, campaign_id)


@router.post("/projects/create")
def create_campaign(
    request: Request,
    title: str = Form(...),
    category: str = Form("other"),
) -> RedirectResponse:
    return CampaignManagementPage.SubmitCampaignCreation(request, title, category)


@router.post("/projects/{campaign_id}/basic")
def update_campaign_basic_information(
    campaign_id: int,
    request: Request,
    title: str = Form(...),
    category: str = Form("other"),
) -> RedirectResponse:
    return CampaignManagementPage.SubmitCampaignUpdate(
        campaign_id, request, title, category
    )


@router.post("/projects/{campaign_id}/goal")
def set_campaign_goal(
    campaign_id: int,
    request: Request,
    goal_amount: int = Form(...),
) -> RedirectResponse:
    return CampaignGoalPage.SubmitFundraisingGoal(campaign_id, request, goal_amount)


@router.post("/projects/{campaign_id}/description")
def set_campaign_description(
    campaign_id: int,
    request: Request,
    description: str = Form(...),
) -> RedirectResponse:
    return CampaignDescriptionPage.SubmitCampaignDescription(
        campaign_id, request, description
    )


@router.post("/projects/{campaign_id}/images")
def upload_campaign_images(
    campaign_id: int,
    request: Request,
    images: list[UploadFile] = File(...),
) -> RedirectResponse:
    return CampaignImagePage.UploadCampaignImages(campaign_id, request, images)


@router.post("/projects/{campaign_id}/images/{image_id}/delete")
def delete_campaign_image(
    campaign_id: int,
    image_id: int,
    request: Request,
) -> RedirectResponse:
    return CampaignImagePage.DeleteCampaignImage(campaign_id, image_id, request)


@router.post("/projects/{campaign_id}/deadline")
def set_campaign_deadline(
    campaign_id: int,
    request: Request,
    deadline: str = Form(...),
) -> RedirectResponse:
    return CampaignDeadlinePage.SubmitCampaignDeadline(campaign_id, request, deadline)


@router.post("/projects/{campaign_id}/submit")
def submit_campaign_for_approval(
    campaign_id: int,
    request: Request,
) -> RedirectResponse:
    return CampaignSubmissionPage.SubmitCampaignForApproval(campaign_id, request)


@router.post("/projects/{campaign_id}/delete")
def delete_campaign(
    campaign_id: int,
    request: Request,
) -> RedirectResponse:
    return CampaignManagementPage.ConfirmCampaignDeletion(campaign_id, request)


class CampaignManagementPage:
    """BCE boundary class for F1-F3 campaign-management actions."""

    @staticmethod
    def AccessCampaignCreationPage(request: Request) -> HTMLResponse:
        if should_redirect_direct_visit_to_home(request):
            return RedirectResponse(url="/", status_code=303)

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
            category_options = get_campaign_category_options(session)
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
                "category_options": category_options,
                "campaigns": serialized_campaigns,
            },
        )

    @staticmethod
    def AccessCampaignManagementPage(
        request: Request,
        campaign_id: int,
    ) -> HTMLResponse:
        if should_redirect_direct_visit_to_home(request):
            return RedirectResponse(url="/", status_code=303)

        with get_session() as session:
            try:
                user = get_authenticated_user(request, session)
            except HTTPException:
                return RedirectResponse(url="/auth?mode=login", status_code=303)

            campaign = CampaignManagementPage.SelectCampaign(session, user.id, campaign_id)
            user_profile = UserProfile.GetProfileDetails(session, user.id)
            own_campaigns = FundraisingCampaign.GetCampaignsByOwner(session, user.id)
            serialized_campaigns = [
                serialize_campaign_summary(session, own_campaign) for own_campaign in own_campaigns
            ]
            selected_campaign = CampaignDetailSerializer.SerializeCampaignDetail(session, campaign)
            selected_campaign["approval_status"] = CampaignSubmissionPage.ViewApprovalStatus(
                session, campaign_id
            )
            flash_message = pop_flash_message(request)
            category_options = get_campaign_category_options(session)

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
                "category_options": category_options,
            },
        )

    @staticmethod
    def EnterCampaignInformation(title: str, category: str) -> tuple[str, str]:
        return CampaignController.ValidateCampaignInformation(title, category)

    @staticmethod
    def SubmitCampaignCreation(
        request: Request,
        title: str,
        category: str,
    ) -> RedirectResponse:
        try:
            with get_session() as session:
                user = get_authenticated_user(request, session)
                CampaignManagementPage.EnterCampaignInformation(title, category)
                campaign = CampaignController.CreateCampaign(session, user.id, title, category)
        except HTTPException as error:
            detail = getattr(error, "detail", "Unable to create campaign.")
            return CampaignManagementPage.DisplayCreationResult(
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

    @staticmethod
    def DisplayCreationResult(
        request: Request,
        message: str,
        message_type: str = "success",
        anchor: str = "campaign-create-form",
    ) -> RedirectResponse:
        return redirect_with_campaign_create_flash(
            request,
            message,
            message_type,
            anchor=anchor,
        )

    @staticmethod
    def SelectCampaign(
        session,
        owner_id: int,
        campaign_id: int,
    ) -> FundraisingCampaign:
        return ensure_campaign_owner(session, owner_id, campaign_id)

    @staticmethod
    def ViewCurrentCampaignInformation(
        session,
        campaign: FundraisingCampaign,
    ) -> dict[str, object]:
        return CampaignDetailSerializer.SerializeCampaignDetail(session, campaign)

    @staticmethod
    def EditCampaignInformation(title: str, category: str) -> tuple[str, str]:
        return CampaignController.ValidateUpdatedInformation(title, category)

    @staticmethod
    def SubmitCampaignUpdate(
        campaign_id: int,
        request: Request,
        title: str,
        category: str,
    ) -> RedirectResponse:
        try:
            with get_session() as session:
                user = get_authenticated_user(request, session)
                campaign = CampaignManagementPage.SelectCampaign(session, user.id, campaign_id)
                CampaignManagementPage.EditCampaignInformation(title, category)
                CampaignController.UpdateCampaign(session, campaign, title, category)
        except HTTPException as error:
            detail = getattr(error, "detail", "Unable to update campaign.")
            return CampaignManagementPage.DisplayUpdateResult(
                request,
                campaign_id,
                detail if isinstance(detail, str) else "Unable to update campaign.",
                "error",
            )

        return CampaignManagementPage.DisplayUpdateResult(
            request,
            campaign_id,
            "Basic campaign information saved successfully.",
        )

    @staticmethod
    def DisplayUpdateResult(
        request: Request,
        campaign_id: int,
        message: str,
        message_type: str = "success",
    ) -> RedirectResponse:
        return redirect_with_campaign_management_flash(
            request,
            campaign_id,
            message,
            message_type,
            anchor="campaign-workflow",
        )

    @staticmethod
    def ReviewCampaignDetails(
        session,
        campaign: FundraisingCampaign,
    ) -> dict[str, object]:
        return CampaignManagementPage.ViewCurrentCampaignInformation(session, campaign)

    @staticmethod
    def ConfirmCampaignDeletion(
        campaign_id: int,
        request: Request,
    ) -> RedirectResponse:
        try:
            with get_session() as session:
                user = get_authenticated_user(request, session)
                campaign = CampaignManagementPage.SelectCampaign(session, user.id, campaign_id)
                CampaignController.DeleteCampaign(session, campaign)
        except HTTPException as error:
            detail = getattr(error, "detail", "Unable to delete campaign.")
            return CampaignManagementPage.DisplayDeletionResult(
                request,
                campaign_id,
                detail if isinstance(detail, str) else "Unable to delete campaign.",
                "error",
            )

        return redirect_with_flash(
            request,
            "/your-fundraisers#my-fundraisers",
            "Campaign deleted successfully.",
            "success",
        )

    @staticmethod
    def DisplayDeletionResult(
        request: Request,
        campaign_id: int,
        message: str,
        message_type: str = "success",
    ) -> RedirectResponse:
        return redirect_with_campaign_management_flash(
            request,
            campaign_id,
            message,
            message_type,
            anchor="campaign-delete",
        )


class CampaignGoalPage:
    """BCE boundary class for F4 fundraising-goal actions."""

    @staticmethod
    def AccessCampaignGoalStep(request: Request, campaign_id: int) -> HTMLResponse:
        return CampaignManagementPage.AccessCampaignManagementPage(request, campaign_id)

    @staticmethod
    def EnterGoalAmount(goal_amount: int) -> int:
        return CampaignGoalController.ValidateGoalInformation(goal_amount)

    @staticmethod
    def SubmitFundraisingGoal(
        campaign_id: int,
        request: Request,
        goal_amount: int,
    ) -> RedirectResponse:
        try:
            with get_session() as session:
                user = get_authenticated_user(request, session)
                campaign = CampaignManagementPage.SelectCampaign(session, user.id, campaign_id)
                CampaignGoalPage.EnterGoalAmount(goal_amount)
                CampaignGoalController.SetFundraisingGoal(session, campaign, goal_amount)
        except HTTPException as error:
            detail = getattr(error, "detail", "Unable to save fundraising goal.")
            return CampaignGoalPage.DisplayGoalResult(
                request,
                campaign_id,
                detail if isinstance(detail, str) else "Unable to save fundraising goal.",
                "error",
            )

        return CampaignGoalPage.DisplayGoalResult(
            request,
            campaign_id,
            "Fundraising goal saved successfully.",
        )

    @staticmethod
    def DisplayGoalResult(
        request: Request,
        campaign_id: int,
        message: str,
        message_type: str = "success",
    ) -> RedirectResponse:
        return redirect_with_campaign_management_flash(
            request,
            campaign_id,
            message,
            message_type,
            anchor="campaign-goal",
        )


class CampaignDescriptionPage:
    """BCE boundary class for F5 campaign-description actions."""

    @staticmethod
    def AccessCampaignDescriptionStep(request: Request, campaign_id: int) -> HTMLResponse:
        return CampaignManagementPage.AccessCampaignManagementPage(request, campaign_id)

    @staticmethod
    def EnterCampaignDescription(description: str) -> str:
        return CampaignDescriptionController.ValidateDescriptionContent(description)

    @staticmethod
    def SubmitCampaignDescription(
        campaign_id: int,
        request: Request,
        description: str,
    ) -> RedirectResponse:
        try:
            with get_session() as session:
                user = get_authenticated_user(request, session)
                campaign = CampaignManagementPage.SelectCampaign(session, user.id, campaign_id)
                CampaignDescriptionPage.EnterCampaignDescription(description)
                CampaignDescriptionController.AddCampaignDescription(session, campaign, description)
        except HTTPException as error:
            detail = getattr(error, "detail", "Unable to save campaign description.")
            return CampaignDescriptionPage.DisplayDescriptionResult(
                request,
                campaign_id,
                detail if isinstance(detail, str) else "Unable to save campaign description.",
                "error",
            )

        return CampaignDescriptionPage.DisplayDescriptionResult(
            request,
            campaign_id,
            "Campaign description saved successfully.",
        )

    @staticmethod
    def DisplayDescriptionResult(
        request: Request,
        campaign_id: int,
        message: str,
        message_type: str = "success",
    ) -> RedirectResponse:
        return redirect_with_campaign_management_flash(
            request,
            campaign_id,
            message,
            message_type,
            anchor="campaign-description",
        )


class CampaignImagePage:
    """BCE boundary class for F6 campaign-image actions."""

    @staticmethod
    def AccessCampaignImageStep(request: Request, campaign_id: int) -> HTMLResponse:
        return CampaignManagementPage.AccessCampaignManagementPage(request, campaign_id)

    @staticmethod
    def SelectCampaignImages(images: list[UploadFile]) -> list[UploadFile]:
        return images

    @staticmethod
    def UploadCampaignImages(
        campaign_id: int,
        request: Request,
        images: list[UploadFile],
    ) -> RedirectResponse:
        try:
            with get_session() as session:
                user = get_authenticated_user(request, session)
                campaign = CampaignManagementPage.SelectCampaign(session, user.id, campaign_id)
                selected_images = CampaignImagePage.SelectCampaignImages(images)
                CampaignImageController.UploadCampaignImages(session, campaign, selected_images)
        except HTTPException as error:
            detail = getattr(error, "detail", "Unable to upload campaign images.")
            return CampaignImagePage.DisplayImageResult(
                request,
                campaign_id,
                detail if isinstance(detail, str) else "Unable to upload campaign images.",
                "error",
            )

        return CampaignImagePage.DisplayImageResult(
            request,
            campaign_id,
            "Campaign images uploaded successfully.",
        )

    @staticmethod
    def DeleteCampaignImage(
        campaign_id: int,
        image_id: int,
        request: Request,
    ) -> RedirectResponse:
        try:
            with get_session() as session:
                user = get_authenticated_user(request, session)
                campaign = CampaignManagementPage.SelectCampaign(session, user.id, campaign_id)
                CampaignImageController.DeleteCampaignImage(session, campaign, image_id)
        except HTTPException as error:
            detail = getattr(error, "detail", "Unable to delete campaign image.")
            return CampaignImagePage.DisplayImageResult(
                request,
                campaign_id,
                detail if isinstance(detail, str) else "Unable to delete campaign image.",
                "error",
            )

        return CampaignImagePage.DisplayImageResult(
            request,
            campaign_id,
            "Campaign image deleted successfully.",
        )

    @staticmethod
    def DisplayImageResult(
        request: Request,
        campaign_id: int,
        message: str,
        message_type: str = "success",
    ) -> RedirectResponse:
        return redirect_with_campaign_management_flash(
            request,
            campaign_id,
            message,
            message_type,
            anchor="campaign-images",
        )


class CampaignDeadlinePage:
    """BCE boundary class for F7 campaign-deadline actions."""

    @staticmethod
    def AccessCampaignDeadlineStep(request: Request, campaign_id: int) -> HTMLResponse:
        return CampaignManagementPage.AccessCampaignManagementPage(request, campaign_id)

    @staticmethod
    def SelectCampaignDeadline(deadline: str) -> str:
        return CampaignDeadlineController.ValidateDeadline(deadline)

    @staticmethod
    def SubmitCampaignDeadline(
        campaign_id: int,
        request: Request,
        deadline: str,
    ) -> RedirectResponse:
        try:
            with get_session() as session:
                user = get_authenticated_user(request, session)
                campaign = CampaignManagementPage.SelectCampaign(session, user.id, campaign_id)
                CampaignDeadlinePage.SelectCampaignDeadline(deadline)
                CampaignDeadlineController.SetCampaignDeadline(session, campaign, deadline)
        except HTTPException as error:
            detail = getattr(error, "detail", "Unable to save campaign deadline.")
            return CampaignDeadlinePage.DisplayDeadlineResult(
                request,
                campaign_id,
                detail if isinstance(detail, str) else "Unable to save campaign deadline.",
                "error",
            )

        return CampaignDeadlinePage.DisplayDeadlineResult(
            request,
            campaign_id,
            "Campaign deadline saved successfully.",
        )

    @staticmethod
    def DisplayDeadlineResult(
        request: Request,
        campaign_id: int,
        message: str,
        message_type: str = "success",
    ) -> RedirectResponse:
        return redirect_with_campaign_management_flash(
            request,
            campaign_id,
            message,
            message_type,
            anchor="campaign-deadline",
        )


class CampaignSubmissionPage:
    """BCE boundary class for F8-F9 campaign-submission actions."""

    @staticmethod
    def AccessSubmissionStep(request: Request, campaign_id: int) -> HTMLResponse:
        return CampaignManagementPage.AccessCampaignManagementPage(request, campaign_id)

    @staticmethod
    def ReviewSubmissionRequirements(
        session,
        campaign: FundraisingCampaign,
    ) -> None:
        CampaignApprovalController.ValidateSubmissionRequirements(session, campaign)

    @staticmethod
    def SubmitCampaignForApproval(
        campaign_id: int,
        request: Request,
    ) -> RedirectResponse:
        try:
            with get_session() as session:
                user = get_authenticated_user(request, session)
                campaign = CampaignManagementPage.SelectCampaign(session, user.id, campaign_id)
                CampaignSubmissionPage.ReviewSubmissionRequirements(session, campaign)
                CampaignApprovalController.SubmitCampaignForApproval(session, campaign)
        except HTTPException as error:
            detail = getattr(error, "detail", "Unable to submit campaign for approval.")
            return CampaignSubmissionPage.DisplaySubmissionResult(
                request,
                campaign_id,
                detail if isinstance(detail, str) else "Unable to submit campaign for approval.",
                "error",
            )

        return CampaignSubmissionPage.DisplaySubmissionResult(
            request,
            campaign_id,
            "Campaign submitted for approval successfully.",
        )

    @staticmethod
    def DisplaySubmissionResult(
        request: Request,
        campaign_id: int,
        message: str,
        message_type: str = "success",
    ) -> RedirectResponse:
        return redirect_with_campaign_management_flash(
            request,
            campaign_id,
            message,
            message_type,
            anchor="campaign-submission",
        )

    @staticmethod
    def ViewApprovalStatus(session, campaign_id: int) -> dict[str, str | None]:
        return CampaignApprovalController.GetApprovalStatusDetails(session, campaign_id)

    @staticmethod
    def DisplayApprovalStatus(
        session,
        campaign: FundraisingCampaign,
    ) -> dict[str, object]:
        return CampaignDetailSerializer.SerializeCampaignDetail(session, campaign)


class CampaignAnalyticsPage:
    """BCE boundary class for F10-F11 campaign-analytics actions."""

    @staticmethod
    def AccessCampaignAnalyticsPage(
        request: Request,
        category: str | None = None,
        lifecycle: str = "all",
        sort: str = "updated_desc",
    ) -> HTMLResponse:
        return CampaignAnalysisPage.ViewFilteredCampaigns(request, category, lifecycle, sort)

    @staticmethod
    def ViewCampaignViews(session, campaign_id: int) -> int:
        return CampaignAnalyticsController.GetViewCount(session, campaign_id)

    @staticmethod
    def ViewDetailedExposureData(session, campaign_id: int) -> dict[str, object]:
        return CampaignAnalyticsController.GetDetailedExposureData(session, campaign_id)

    @staticmethod
    def ViewCampaignShortlists(session, campaign_id: int) -> int:
        return CampaignAnalyticsController.GetShortlistCount(session, campaign_id)

    @staticmethod
    def ViewDetailedInterestData(session, campaign_id: int) -> dict[str, object]:
        return CampaignAnalyticsController.GetDetailedInterestData(session, campaign_id)


class CampaignHistoryPage:
    """BCE boundary class for F12 completed-campaign actions."""

    @staticmethod
    def AccessCampaignHistoryPage(
        request: Request,
        category: str | None = None,
        lifecycle: str = "all",
        sort: str = "updated_desc",
    ) -> HTMLResponse:
        return CampaignAnalysisPage.ViewFilteredCampaigns(request, category, lifecycle, sort)

    @staticmethod
    def ViewCompletedCampaigns(
        session,
        owner_id: int,
        category: str | None = None,
        sort_order: str = "updated_desc",
    ) -> list[FundraisingCampaign]:
        return CampaignHistoryController.RetrieveCompletedCampaignList(
            session,
            owner_id,
            category=category,
            sort_order=sort_order,
        )

    @staticmethod
    def ViewCompletedCampaignDetails(
        session,
        owner_id: int,
        campaign_id: int,
    ) -> dict[str, object]:
        return CampaignHistoryController.GetCompletedCampaignDetails(
            session, owner_id, campaign_id
        )


class CampaignAnalysisPage:
    """BCE boundary class for F13 campaign filtering actions."""

    @staticmethod
    def SelectFilterCriteria(
        category: str | None,
        lifecycle: str,
        sort: str,
    ) -> tuple[str | None, str, str]:
        requested_category = (category or "").strip().lower()
        selected_category = None
        if requested_category and requested_category != "all":
            selected_category = normalize_campaign_category(requested_category)
        selected_lifecycle = normalize_fundraiser_lifecycle(lifecycle)
        selected_sort = normalize_fundraiser_campaign_sort(sort)
        return selected_category, selected_lifecycle, selected_sort

    @staticmethod
    def FilterCampaigns(
        session,
        owner_id: int,
        category: str | None,
        lifecycle: str,
        sort_order: str,
    ) -> list[FundraisingCampaign]:
        return CampaignFilterController.RetrieveFilteredCampaignResults(
            session,
            owner_id,
            category=category,
            lifecycle=lifecycle,
            sort_order=sort_order,
        )

    @staticmethod
    def ViewFilteredCampaigns(
        request: Request,
        category: str | None = None,
        lifecycle: str = "all",
        sort: str = "updated_desc",
    ) -> HTMLResponse:
        if should_redirect_direct_visit_to_home(request):
            return RedirectResponse(url="/", status_code=303)

        selected_category, selected_lifecycle, selected_sort = (
            CampaignAnalysisPage.SelectFilterCriteria(category, lifecycle, sort)
        )

        with get_session() as session:
            try:
                user = get_authenticated_user(request, session)
            except HTTPException:
                return RedirectResponse(url="/auth?mode=login", status_code=303)

            profile = UserProfile.GetProfileDetails(session, user.id)
            filtered_campaigns = CampaignAnalysisPage.FilterCampaigns(
                session,
                user.id,
                selected_category,
                selected_lifecycle,
                selected_sort,
            )
            completed_campaigns = CampaignHistoryPage.ViewCompletedCampaigns(
                session,
                user.id,
                category=selected_category,
                sort_order=selected_sort,
            )
            serialized_campaigns = [
                CampaignDetailSerializer.SerializeCampaignDetail(session, own_campaign)
                for own_campaign in filtered_campaigns
            ]
            serialized_completed_campaigns = [
                CampaignDetailSerializer.SerializeCampaignDetail(session, campaign)
                for campaign in completed_campaigns
            ]
            completed_count = len(serialized_completed_campaigns)
            if selected_lifecycle == "completed":
                serialized_completed_campaigns = []
            total_views = sum(
                CampaignAnalyticsPage.ViewCampaignViews(session, campaign.id)
                for campaign in filtered_campaigns
            )
            total_shortlists = sum(
                CampaignAnalyticsPage.ViewCampaignShortlists(session, campaign.id)
                for campaign in filtered_campaigns
            )
            flash_message = pop_flash_message(request)

        return CampaignAnalysisPage.DisplayFilteredCampaigns(
            request,
            user,
            profile,
            flash_message,
            selected_category,
            selected_lifecycle,
            selected_sort,
            serialized_campaigns,
            serialized_completed_campaigns,
            total_views,
            total_shortlists,
            completed_count,
        )

    @staticmethod
    def DisplayFilteredCampaigns(
        request: Request,
        user,
        profile,
        flash_message,
        selected_category: str | None,
        selected_lifecycle: str,
        selected_sort: str,
        serialized_campaigns: list[dict[str, object]],
        serialized_completed_campaigns: list[dict[str, object]],
        total_views: int,
        total_shortlists: int,
        completed_count: int,
    ) -> HTMLResponse:
        return templates.TemplateResponse(
            request=request,
            name="your_fundraisers.html",
            context={
                "request": request,
                "title": "Your Fundraisers",
                "username": user.username,
                "user_email": user.email,
                "avatar_url": build_avatar_url(profile.avatar_path) if profile else None,
                "is_admin": is_admin_email(user.email),
                "flash_message": flash_message,
                "selected_category": selected_category,
                "selected_lifecycle": selected_lifecycle,
                "selected_sort": selected_sort,
                "category_filters": get_fundraiser_category_filters(selected_category),
                "lifecycle_filters": get_fundraiser_lifecycle_filters(selected_lifecycle),
                "sort_filters": get_fundraiser_sort_filters(selected_sort),
                "analytics_summary": {
                    "campaign_count": len(serialized_campaigns),
                    "total_views": total_views,
                    "total_shortlists": total_shortlists,
                    "completed_count": completed_count,
                },
                "campaigns": serialized_campaigns,
                "completed_campaigns": serialized_completed_campaigns,
                "your_fundraisers_url": build_your_fundraisers_url(
                    selected_category=selected_category,
                    selected_lifecycle=selected_lifecycle,
                    selected_sort=selected_sort,
                    anchor="fundraiser-library",
                ),
            },
        )
