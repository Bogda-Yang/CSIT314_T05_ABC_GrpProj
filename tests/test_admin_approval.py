import pytest
from fastapi import HTTPException

from models.campaign import CampaignStatus
from services.campaign_service import CampaignApprovalController

from tests.helpers import FakeSession, make_campaign, patch_approval_storage
from tests.test_data import (
    ADMIN_APPROVAL_CASES,
    APPROVAL_STATUS_CASES,
    MISSING_SUBMISSION_REQUIREMENT_CASES,
    NON_PENDING_CAMPAIGN_STATUSES,
    STATUS_HELPER_INITIAL_STATUSES,
)


@pytest.mark.parametrize("campaign_data", ADMIN_APPROVAL_CASES)
def test_validate_campaign_accepts_pending_complete_campaign(monkeypatch, campaign_data):
    session = FakeSession()
    campaign = make_campaign(campaign_data)
    patch_approval_storage(monkeypatch, campaign)

    validated_campaign = CampaignApprovalController.ValidateCampaign(session, campaign.id)

    assert validated_campaign is campaign


@pytest.mark.parametrize("status", NON_PENDING_CAMPAIGN_STATUSES)
def test_validate_campaign_rejects_non_pending_status(monkeypatch, status):
    session = FakeSession()
    campaign = make_campaign(ADMIN_APPROVAL_CASES[0], status=status)
    patch_approval_storage(monkeypatch, campaign)

    with pytest.raises(HTTPException) as error:
        CampaignApprovalController.ValidateCampaign(session, campaign.id)
    assert error.value.status_code == 400


@pytest.mark.parametrize("campaign_data", ADMIN_APPROVAL_CASES)
def test_approve_campaign_publishes_pending_campaign(monkeypatch, campaign_data):
    session = FakeSession()
    campaign = make_campaign(campaign_data)
    patch_approval_storage(monkeypatch, campaign)

    status_details = CampaignApprovalController.ApproveCampaign(session, campaign)

    assert campaign.status == "published"
    assert campaign.published_at is not None
    assert status_details["status"] == "published"
    assert session.commits == 1


@pytest.mark.parametrize("overrides,has_image", MISSING_SUBMISSION_REQUIREMENT_CASES)
def test_validate_campaign_rejects_missing_submission_requirements(monkeypatch, overrides, has_image):
    session = FakeSession()
    campaign = make_campaign(ADMIN_APPROVAL_CASES[0], **overrides)
    patch_approval_storage(monkeypatch, campaign, has_image=has_image)

    with pytest.raises(HTTPException):
        CampaignApprovalController.ValidateCampaign(session, campaign.id)


@pytest.mark.parametrize("status", APPROVAL_STATUS_CASES)
def test_get_approval_status_details_returns_status(monkeypatch, status):
    session = FakeSession()
    campaign = make_campaign(ADMIN_APPROVAL_CASES[0], status=status)
    patch_approval_storage(monkeypatch, campaign)

    status_details = CampaignApprovalController.GetApprovalStatusDetails(session, campaign.id)

    assert status_details["status"] == status


@pytest.mark.parametrize("campaign_data", ADMIN_APPROVAL_CASES)
def test_publish_campaign_sets_published_status(campaign_data):
    session = FakeSession()
    campaign = make_campaign(campaign_data)

    CampaignApprovalController.PublishCampaign(session, campaign)

    assert campaign.status == "published"
    assert campaign.published_at is not None
    assert campaign in session.added


@pytest.mark.parametrize("initial_status", STATUS_HELPER_INITIAL_STATUSES)
def test_campaign_status_helpers_update_status(initial_status):
    campaign = make_campaign(ADMIN_APPROVAL_CASES[0], status=initial_status)

    CampaignStatus.SetApproved(campaign)
    assert CampaignStatus.GetStatus(campaign) == "approved"

    CampaignStatus.SetPublished(campaign)
    assert CampaignStatus.GetStatus(campaign) == "published"
