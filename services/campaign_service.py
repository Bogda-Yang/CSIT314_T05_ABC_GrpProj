import uuid
from datetime import datetime

from fastapi import HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from core.config import (
    CAMPAIGN_CATEGORY_LABELS,
    CAMPAIGN_CATEGORY_OPTIONS,
    CAMPAIGN_IMAGE_DIR,
    CAMPAIGN_PUBLIC_FILTER_OPTIONS,
    DASHBOARD_REVIEW_SORT_LABELS,
    DASHBOARD_REVIEW_SORT_OPTIONS,
    DEFAULT_CAMPAIGN_CATEGORY,
    DEFAULT_DASHBOARD_REVIEW_SORT,
    PROJECTS_PRIMARY_CATEGORY_FILTER_VALUES,
    SUPABASE_CAMPAIGN_BUCKET,
)
from core.security import now_dt
from core.storage import build_campaign_image_url, store_uploaded_asset
from models.campaign import (
    CampaignDeadline,
    CampaignDescription,
    CampaignGoal,
    CampaignImage,
    CampaignStatus,
    FundraisingCampaign,
    RejectionRecord,
)
from models.user import UserAccount
from services.user_service import is_admin_email, set_flash_message


def build_projects_url(
    campaign_id: int | None = None,
    review_campaign_id: int | None = None,
    selected_category: str | None = None,
    anchor: str | None = None,
) -> str:
    from urllib.parse import urlencode

    query_pairs: list[tuple[str, str]] = []
    if selected_category:
        query_pairs.append(("category", selected_category))
    if campaign_id is not None:
        query_pairs.append(("campaign_id", str(campaign_id)))
    if review_campaign_id is not None:
        query_pairs.append(("review_campaign_id", str(review_campaign_id)))

    url = "/projects"
    if query_pairs:
        url = f"{url}?{urlencode(query_pairs)}"
    if anchor:
        url = f"{url}#{anchor}"
    return url


def build_dashboard_url(
    review_campaign_id: int | None = None,
    selected_category: str | None = None,
    selected_sort: str | None = None,
    modal: str | None = None,
    anchor: str | None = None,
) -> str:
    from urllib.parse import urlencode

    query_pairs: list[tuple[str, str]] = []
    if selected_category:
        query_pairs.append(("category", selected_category))
    if selected_sort:
        query_pairs.append(("sort", selected_sort))
    if review_campaign_id is not None:
        query_pairs.append(("review_campaign_id", str(review_campaign_id)))
    if modal:
        query_pairs.append(("modal", modal))

    url = "/dashboard"
    if query_pairs:
        url = f"{url}?{urlencode(query_pairs)}"
    if anchor:
        url = f"{url}#{anchor}"
    return url


def build_campaign_create_url(anchor: str | None = None) -> str:
    url = "/projects/create-campaign"
    if anchor:
        url = f"{url}#{anchor}"
    return url


def build_campaign_management_url(campaign_id: int, anchor: str | None = None) -> str:
    url = f"/projects/manage/{campaign_id}"
    if anchor:
        url = f"{url}#{anchor}"
    return url


def redirect_with_projects_flash(
    request: Request,
    message: str,
    kind: str = "success",
    campaign_id: int | None = None,
    review_campaign_id: int | None = None,
    selected_category: str | None = None,
    anchor: str | None = None,
) -> RedirectResponse:
    set_flash_message(request, message, kind)
    return RedirectResponse(
        url=build_projects_url(
            campaign_id=campaign_id,
            review_campaign_id=review_campaign_id,
            selected_category=selected_category,
            anchor=anchor,
        ),
        status_code=303,
    )


def redirect_with_dashboard_flash(
    request: Request,
    message: str,
    kind: str = "success",
    review_campaign_id: int | None = None,
    selected_category: str | None = None,
    selected_sort: str | None = None,
    anchor: str | None = None,
) -> RedirectResponse:
    set_flash_message(request, message, kind)
    return RedirectResponse(
        url=build_dashboard_url(
            review_campaign_id=review_campaign_id,
            selected_category=selected_category,
            selected_sort=selected_sort,
            anchor=anchor,
        ),
        status_code=303,
    )


def redirect_with_campaign_create_flash(
    request: Request,
    message: str,
    kind: str = "success",
    anchor: str | None = None,
) -> RedirectResponse:
    set_flash_message(request, message, kind)
    return RedirectResponse(url=build_campaign_create_url(anchor=anchor), status_code=303)


def redirect_with_campaign_management_flash(
    request: Request,
    campaign_id: int,
    message: str,
    kind: str = "success",
    anchor: str | None = None,
) -> RedirectResponse:
    set_flash_message(request, message, kind)
    return RedirectResponse(
        url=build_campaign_management_url(campaign_id=campaign_id, anchor=anchor),
        status_code=303,
    )


def humanize_campaign_status(status: str) -> str:
    return {
        "draft": "Draft",
        "pending": "Pending Review",
        "approved": "Approved",
        "published": "Published",
        "rejected": "Rejected",
    }.get(status, status.title())


def humanize_campaign_category(category: str | None) -> str:
    if not category:
        return CAMPAIGN_CATEGORY_LABELS[DEFAULT_CAMPAIGN_CATEGORY]
    return CAMPAIGN_CATEGORY_LABELS.get(category, category.title())


def normalize_campaign_category(category: str | None) -> str:
    clean_category = (category or "").strip().lower()
    if clean_category not in CAMPAIGN_CATEGORY_LABELS:
        raise HTTPException(status_code=400, detail="Choose a valid campaign category.")
    return clean_category


def normalize_dashboard_review_sort(sort_order: str | None) -> str:
    clean_sort_order = (sort_order or "").strip().lower()
    if clean_sort_order not in DASHBOARD_REVIEW_SORT_LABELS:
        return DEFAULT_DASHBOARD_REVIEW_SORT
    return clean_sort_order


def humanize_campaign_workflow_stage(stage: int) -> str:
    return {
        0: "Draft created",
        1: "Basic information saved",
        2: "Fundraising goal saved",
        3: "Description saved",
        4: "Images uploaded",
        5: "Deadline saved",
    }.get(stage, "Ready for submission")


def ensure_campaign_owner(
    session: Session, user_id: int, campaign_id: int
) -> FundraisingCampaign:
    campaign = FundraisingCampaign.GetCampaignById(session, campaign_id)
    if not campaign or campaign.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    return campaign


def ensure_admin_user(user: UserAccount) -> None:
    if not is_admin_email(user.email):
        raise HTTPException(status_code=403, detail="Administrator access is required.")


def serialize_campaign_summary(
    session: Session, campaign: FundraisingCampaign
) -> dict[str, object]:
    owner_account = UserAccount.GetUserAccount(session, campaign.owner_id)
    image_records = CampaignImage.GetImageDetails(session, campaign.id)
    image_urls = [
        build_campaign_image_url(record.image_path)
        for record in image_records
        if build_campaign_image_url(record.image_path)
    ]
    first_image_url = image_urls[0] if image_urls else None
    return {
        "id": campaign.id,
        "owner_username": owner_account.username if owner_account else "Unknown",
        "owner_email": owner_account.email if owner_account else None,
        "title": campaign.title,
        "category": campaign.category or DEFAULT_CAMPAIGN_CATEGORY,
        "category_label": humanize_campaign_category(campaign.category),
        "description": campaign.description.strip() if campaign.description else None,
        "description_excerpt": (
            f"{campaign.description.strip()[:180]}..."
            if campaign.description and len(campaign.description.strip()) > 180
            else campaign.description.strip()
        ),
        "goal_amount": campaign.goal_amount,
        "workflow_stage": campaign.workflow_stage or 0,
        "workflow_stage_label": humanize_campaign_workflow_stage(campaign.workflow_stage or 0),
        "status": campaign.status,
        "status_label": humanize_campaign_status(campaign.status),
        "deadline": campaign.deadline,
        "updated_at": campaign.updated_at.strftime("%Y-%m-%d %H:%M"),
        "published_at": campaign.published_at.strftime("%Y-%m-%d %H:%M")
        if campaign.published_at
        else None,
        "image_count": len(image_records),
        "cover_image_url": first_image_url,
        "image_urls": image_urls,
    }


def serialize_campaign_detail(
    session: Session, campaign: FundraisingCampaign
) -> dict[str, object]:
    owner_account = UserAccount.GetUserAccount(session, campaign.owner_id)
    image_records = CampaignImage.GetImageDetails(session, campaign.id)
    status_details = CampaignStatus.GetStatusDetails(session, campaign)
    return {
        "id": campaign.id,
        "owner_id": campaign.owner_id,
        "owner_username": owner_account.username if owner_account else "Unknown",
        "owner_email": owner_account.email if owner_account else None,
        "title": campaign.title,
        "category": campaign.category or DEFAULT_CAMPAIGN_CATEGORY,
        "category_label": humanize_campaign_category(campaign.category),
        "goal_amount": campaign.goal_amount,
        "description": campaign.description,
        "deadline": campaign.deadline,
        "workflow_stage": campaign.workflow_stage or 0,
        "workflow_stage_label": humanize_campaign_workflow_stage(campaign.workflow_stage or 0),
        "status": campaign.status,
        "status_label": humanize_campaign_status(campaign.status),
        "created_at": campaign.created_at.strftime("%Y-%m-%d %H:%M"),
        "updated_at": campaign.updated_at.strftime("%Y-%m-%d %H:%M"),
        "submitted_at": status_details["submitted_at"],
        "published_at": status_details["published_at"],
        "reviewed_at": status_details["reviewed_at"],
        "rejection_reason": status_details["rejection_reason"],
        "image_count": len(image_records),
        "images": [
            {
                "id": record.id,
                "url": build_campaign_image_url(record.image_path),
            }
            for record in image_records
            if build_campaign_image_url(record.image_path)
        ],
        "image_urls": [
            build_campaign_image_url(record.image_path)
            for record in image_records
            if build_campaign_image_url(record.image_path)
        ],
    }


class CampaignController:
    @staticmethod
    def ValidateCampaignInformation(title: str, category: str) -> tuple[str, str]:
        clean_title = title.strip()
        if len(clean_title) < 4:
            raise HTTPException(
                status_code=400,
                detail="Campaign title must be at least 4 characters.",
            )
        if len(clean_title) > 160:
            raise HTTPException(
                status_code=400,
                detail="Campaign title must be 160 characters or fewer.",
            )
        clean_category = normalize_campaign_category(category)
        return clean_title, clean_category

    @staticmethod
    def CreateCampaign(
        session: Session, owner_id: int, title: str, category: str
    ) -> FundraisingCampaign:
        clean_title, clean_category = CampaignController.ValidateCampaignInformation(
            title, category
        )
        campaign = FundraisingCampaign.CreateCampaign(owner_id, clean_title, clean_category)
        CampaignController.SaveCampaignDraft(session, campaign)
        session.commit()
        session.refresh(campaign)
        return campaign

    @staticmethod
    def SaveCampaignDraft(session: Session, campaign: FundraisingCampaign) -> None:
        FundraisingCampaign.SaveCampaignDraft(session, campaign)

    @staticmethod
    def GetCampaignDetails(session: Session, campaign_id: int) -> dict[str, object]:
        campaign = FundraisingCampaign.GetCampaignDetails(session, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found.")
        return serialize_campaign_detail(session, campaign)

    @staticmethod
    def ValidateUpdatedInformation(title: str, category: str) -> tuple[str, str]:
        return CampaignController.ValidateCampaignInformation(title, category)

    @staticmethod
    def UpdateCampaign(
        session: Session, campaign: FundraisingCampaign, title: str, category: str
    ) -> FundraisingCampaign:
        clean_title, clean_category = CampaignController.ValidateUpdatedInformation(
            title, category
        )
        FundraisingCampaign.UpdateCampaign(campaign, clean_title, clean_category)
        FundraisingCampaign.AdvanceWorkflowStage(campaign, 1)
        CampaignController.SaveCampaignChanges(session, campaign)
        session.commit()
        session.refresh(campaign)
        return campaign

    @staticmethod
    def SaveCampaignChanges(session: Session, campaign: FundraisingCampaign) -> None:
        FundraisingCampaign.SaveCampaignChanges(session, campaign)

    @staticmethod
    def DeleteCampaign(session: Session, campaign: FundraisingCampaign) -> None:
        CampaignImage.DeleteImageRecords(session, campaign.id)
        RejectionRecord.DeleteCampaignRejectionRecords(session, campaign.id)
        session.flush()
        CampaignController.RemoveCampaign(session, campaign)
        session.commit()

    @staticmethod
    def RemoveCampaign(session: Session, campaign: FundraisingCampaign) -> None:
        FundraisingCampaign.DeleteCampaign(session, campaign)

    @staticmethod
    def ValidateWorkflowStage(campaign: FundraisingCampaign, required_stage: int) -> None:
        current_stage = campaign.workflow_stage or 0
        if current_stage < required_stage:
            raise HTTPException(
                status_code=400,
                detail="Complete the previous campaign step before continuing.",
            )


class CampaignGoalController:
    @staticmethod
    def ValidateGoalInformation(goal_amount: int) -> int:
        if goal_amount <= 0:
            raise HTTPException(status_code=400, detail="Fundraising goal must be greater than 0.")
        if goal_amount > 1_000_000_000:
            raise HTTPException(
                status_code=400,
                detail="Fundraising goal is too large for this demo platform.",
            )
        return goal_amount

    @staticmethod
    def SetFundraisingGoal(
        session: Session, campaign: FundraisingCampaign, goal_amount: int
    ) -> dict[str, int | None]:
        CampaignController.ValidateWorkflowStage(campaign, 1)
        clean_goal_amount = CampaignGoalController.ValidateGoalInformation(goal_amount)
        CampaignGoal.SetGoal(campaign, clean_goal_amount)
        FundraisingCampaign.AdvanceWorkflowStage(campaign, 2)
        CampaignGoalController.SaveFundraisingGoal(session, campaign)
        session.commit()
        return CampaignGoal.GetGoalDetails(campaign)

    @staticmethod
    def SaveFundraisingGoal(session: Session, campaign: FundraisingCampaign) -> None:
        CampaignGoal.SaveGoal(session, campaign)


class CampaignDescriptionController:
    @staticmethod
    def ValidateDescriptionContent(description: str) -> str:
        clean_description = description.strip()
        if len(clean_description) < 20:
            raise HTTPException(
                status_code=400,
                detail="Campaign description must be at least 20 characters.",
            )
        if len(clean_description) > 5000:
            raise HTTPException(
                status_code=400,
                detail="Campaign description must be 5000 characters or fewer.",
            )
        return clean_description

    @staticmethod
    def AddCampaignDescription(
        session: Session, campaign: FundraisingCampaign, description: str
    ) -> dict[str, str]:
        CampaignController.ValidateWorkflowStage(campaign, 2)
        clean_description = CampaignDescriptionController.ValidateDescriptionContent(description)
        CampaignDescription.SetDescription(campaign, clean_description)
        FundraisingCampaign.AdvanceWorkflowStage(campaign, 3)
        CampaignDescriptionController.SaveCampaignDescription(session, campaign)
        session.commit()
        return CampaignDescription.GetDescriptionDetails(campaign)

    @staticmethod
    def SaveCampaignDescription(session: Session, campaign: FundraisingCampaign) -> None:
        CampaignDescription.SaveDescription(session, campaign)


class CampaignImageController:
    @staticmethod
    def ValidateImageFormatAndSize(
        upload_files: list[UploadFile],
    ) -> list[tuple[bytes, str]]:
        if not upload_files:
            raise HTTPException(status_code=400, detail="Choose at least one campaign image.")

        allowed_content_types = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
        }

        validated_files: list[tuple[bytes, str]] = []
        for upload_file in upload_files:
            if not upload_file.filename:
                continue

            content_type = (upload_file.content_type or "").lower()
            file_extension = allowed_content_types.get(content_type)
            if not file_extension:
                raise HTTPException(
                    status_code=400,
                    detail="Campaign images must be JPG, PNG, or WEBP.",
                )

            file_bytes = upload_file.file.read()
            if not file_bytes:
                raise HTTPException(status_code=400, detail="One of the uploaded images is empty.")
            if len(file_bytes) > 5 * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail="Each campaign image must be 5 MB or smaller.",
                )

            validated_files.append((file_bytes, file_extension))

        if not validated_files:
            raise HTTPException(status_code=400, detail="Choose at least one campaign image.")

        return validated_files

    @staticmethod
    def UploadCampaignImages(
        session: Session, campaign: FundraisingCampaign, upload_files: list[UploadFile]
    ) -> list[CampaignImage]:
        CampaignController.ValidateWorkflowStage(campaign, 3)
        validated_files = CampaignImageController.ValidateImageFormatAndSize(upload_files)
        existing_image_records = CampaignImage.GetImageDetails(session, campaign.id)
        if len(existing_image_records) + len(validated_files) > 5:
            raise HTTPException(
                status_code=400,
                detail="Each campaign can include up to 5 images.",
            )

        image_paths: list[str] = []
        for file_bytes, file_extension in validated_files:
            image_filename = f"{uuid.uuid4().hex}{file_extension}"
            image_storage_path = f"campaigns/{campaign.id}/{image_filename}"
            content_type = {
                ".jpg": "image/jpeg",
                ".png": "image/png",
                ".webp": "image/webp",
            }.get(file_extension, "application/octet-stream")
            store_uploaded_asset(
                SUPABASE_CAMPAIGN_BUCKET,
                CAMPAIGN_IMAGE_DIR,
                image_storage_path,
                file_bytes,
                content_type,
            )
            image_paths.append(image_storage_path)

        if campaign.status != "draft":
            campaign.status = "draft"
            campaign.submitted_at = None
            campaign.reviewed_at = None
            campaign.published_at = None
        campaign.updated_at = now_dt()
        FundraisingCampaign.AdvanceWorkflowStage(campaign, 4)
        session.add(campaign)

        image_records = CampaignImage.StoreImages(campaign.id, image_paths)
        CampaignImageController.SaveImageRecords(session, image_records)
        session.commit()
        return image_records

    @staticmethod
    def SaveImageRecords(session: Session, image_records: list[CampaignImage]) -> None:
        CampaignImage.SaveImageRecords(session, image_records)

    @staticmethod
    def DeleteCampaignImage(
        session: Session, campaign: FundraisingCampaign, image_id: int
    ) -> None:
        CampaignController.ValidateWorkflowStage(campaign, 3)
        image_record = CampaignImage.GetImageRecord(session, campaign.id, image_id)
        if image_record is None:
            raise HTTPException(status_code=404, detail="Campaign image was not found.")

        CampaignImage.DeleteImageRecord(session, image_record)

        remaining_image_records = [
            record for record in CampaignImage.GetImageDetails(session, campaign.id)
            if record.id != image_id
        ]
        if not remaining_image_records and (campaign.workflow_stage or 0) > 3:
            campaign.workflow_stage = 3

        if campaign.status != "draft":
            campaign.status = "draft"
            campaign.submitted_at = None
            campaign.reviewed_at = None
            campaign.published_at = None

        campaign.updated_at = now_dt()
        session.add(campaign)
        session.commit()


class CampaignDeadlineController:
    @staticmethod
    def ValidateDeadline(deadline: str) -> str:
        clean_deadline = deadline.strip()
        if not clean_deadline:
            raise HTTPException(status_code=400, detail="Choose a campaign deadline.")

        try:
            deadline_date = datetime.strptime(clean_deadline, "%Y-%m-%d").date()
        except ValueError as error:
            raise HTTPException(status_code=400, detail="Choose a valid campaign deadline.") from error

        if deadline_date <= now_dt().date():
            raise HTTPException(
                status_code=400,
                detail="Campaign deadline must be a future date.",
            )

        return clean_deadline

    @staticmethod
    def SetCampaignDeadline(
        session: Session, campaign: FundraisingCampaign, deadline: str
    ) -> dict[str, str | None]:
        CampaignController.ValidateWorkflowStage(campaign, 4)
        clean_deadline = CampaignDeadlineController.ValidateDeadline(deadline)
        CampaignDeadline.SetDeadline(campaign, clean_deadline)
        FundraisingCampaign.AdvanceWorkflowStage(campaign, 5)
        CampaignDeadlineController.SaveCampaignDeadline(session, campaign)
        session.commit()
        return CampaignDeadline.GetDeadlineDetails(campaign)

    @staticmethod
    def SaveCampaignDeadline(session: Session, campaign: FundraisingCampaign) -> None:
        CampaignDeadline.SaveDeadline(session, campaign)


class CampaignApprovalController:
    @staticmethod
    def ValidateSubmissionRequirements(
        session: Session, campaign: FundraisingCampaign
    ) -> None:
        CampaignController.ValidateCampaignInformation(campaign.title, campaign.category)
        if not campaign.goal_amount or campaign.goal_amount <= 0:
            raise HTTPException(status_code=400, detail="Set a fundraising goal before submission.")
        CampaignDescriptionController.ValidateDescriptionContent(campaign.description)
        if not campaign.deadline:
            raise HTTPException(
                status_code=400,
                detail="Set a campaign deadline before submission.",
            )
        CampaignDeadlineController.ValidateDeadline(campaign.deadline)
        if not CampaignImage.GetImageDetails(session, campaign.id):
            raise HTTPException(
                status_code=400,
                detail="Upload at least one campaign image before submission.",
            )

    @staticmethod
    def SubmitCampaignForApproval(
        session: Session, campaign: FundraisingCampaign
    ) -> dict[str, str | None]:
        CampaignController.ValidateWorkflowStage(campaign, 5)
        CampaignApprovalController.ValidateSubmissionRequirements(session, campaign)
        RejectionRecord.DeleteCampaignRejectionRecords(session, campaign.id)
        FundraisingCampaign.SubmitCampaign(campaign)
        CampaignApprovalController.UpdateCampaignStatusToPending(session, campaign)
        session.commit()
        return CampaignApprovalController.GetApprovalStatusDetails(session, campaign.id)

    @staticmethod
    def UpdateCampaignStatusToPending(session: Session, campaign: FundraisingCampaign) -> None:
        CampaignStatus.SetPending(campaign)
        FundraisingCampaign.UpdateCampaignStatus(session, campaign, CampaignStatus.GetStatus(campaign))

    @staticmethod
    def RetrieveCampaignStatus(session: Session, campaign_id: int) -> FundraisingCampaign:
        campaign = FundraisingCampaign.GetCampaignById(session, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found.")
        return campaign

    @staticmethod
    def GetApprovalStatusDetails(session: Session, campaign_id: int) -> dict[str, str | None]:
        campaign = CampaignApprovalController.RetrieveCampaignStatus(session, campaign_id)
        return CampaignStatus.GetStatusDetails(session, campaign)

    @staticmethod
    def GetPendingCampaigns(
        session: Session,
        category: str | None = None,
        sort_order: str = DEFAULT_DASHBOARD_REVIEW_SORT,
    ) -> list[FundraisingCampaign]:
        return FundraisingCampaign.GetPendingCampaigns(
            session,
            category=category,
            sort_order=sort_order,
        )

    @staticmethod
    def GetCampaignDetails(session: Session, campaign_id: int) -> dict[str, object]:
        return CampaignController.GetCampaignDetails(session, campaign_id)

    @staticmethod
    def ValidateCampaign(session: Session, campaign_id: int) -> FundraisingCampaign:
        campaign = CampaignApprovalController.RetrieveCampaignStatus(session, campaign_id)
        if campaign.status != "pending":
            raise HTTPException(status_code=400, detail="Only pending campaigns can be reviewed.")
        CampaignApprovalController.ValidateSubmissionRequirements(session, campaign)
        return campaign

    @staticmethod
    def ApproveCampaign(
        session: Session, campaign: FundraisingCampaign
    ) -> dict[str, str | None]:
        CampaignStatus.SetApproved(campaign)
        FundraisingCampaign.UpdateCampaignStatus(session, campaign, CampaignStatus.GetStatus(campaign))
        CampaignApprovalController.PublishCampaign(session, campaign)
        RejectionRecord.DeleteCampaignRejectionRecords(session, campaign.id)
        session.commit()
        return CampaignApprovalController.GetApprovalStatusDetails(session, campaign.id)

    @staticmethod
    def PublishCampaign(session: Session, campaign: FundraisingCampaign) -> None:
        CampaignStatus.SetPublished(campaign)
        FundraisingCampaign.PublishCampaign(session, campaign)


class CampaignRejectionController:
    @staticmethod
    def GetPendingCampaigns(
        session: Session,
        category: str | None = None,
        sort_order: str = DEFAULT_DASHBOARD_REVIEW_SORT,
    ) -> list[FundraisingCampaign]:
        return FundraisingCampaign.GetPendingCampaigns(
            session,
            category=category,
            sort_order=sort_order,
        )

    @staticmethod
    def GetCampaignDetails(session: Session, campaign_id: int) -> dict[str, object]:
        return CampaignController.GetCampaignDetails(session, campaign_id)

    @staticmethod
    def ValidateCampaign(session: Session, campaign_id: int) -> FundraisingCampaign:
        campaign = FundraisingCampaign.GetCampaignById(session, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found.")
        if campaign.status != "pending":
            raise HTTPException(status_code=400, detail="Only pending campaigns can be rejected.")
        return campaign

    @staticmethod
    def RejectCampaign(
        session: Session, campaign: FundraisingCampaign, reason: str
    ) -> dict[str, str | None]:
        clean_reason = reason.strip()
        if len(clean_reason) < 10:
            raise HTTPException(
                status_code=400,
                detail="Rejection reason must be at least 10 characters.",
            )

        CampaignRejectionController.RecordRejectionReason(session, campaign.id, clean_reason)
        campaign.status = "rejected"
        campaign.reviewed_at = now_dt()
        campaign.updated_at = now_dt()
        campaign.published_at = None
        session.add(campaign)
        session.commit()
        return CampaignStatus.GetStatusDetails(session, campaign)

    @staticmethod
    def RecordRejectionReason(session: Session, campaign_id: int, reason: str) -> None:
        RejectionRecord.SaveRejectionReason(session, campaign_id, reason)
