import pytest
from fastapi import HTTPException

from services.campaign_service import (
    CampaignApprovalController,
    CampaignController,
    CampaignDeadlineController,
    CampaignDescriptionController,
    CampaignGoalController,
)

from tests.helpers import FakeSession, make_campaign, patch_approval_storage
from tests.test_data import (
    CAMPAIGN_SUBMISSION_CASES,
    FUNDRAISER_VALIDATOR_CASES,
    INCOMPLETE_CAMPAIGN_SUBMISSION_CASES,
    INVALID_CAMPAIGN_CATEGORIES,
    VALID_CAMPAIGN_INFORMATION_CASES,
    WORKFLOW_STAGE_CASES,
)


VALIDATORS = {
    "goal": CampaignGoalController.ValidateGoalInformation,
    "description": CampaignDescriptionController.ValidateDescriptionContent,
    "deadline": CampaignDeadlineController.ValidateDeadline,
    "campaign_information": CampaignController.ValidateCampaignInformation,
}


@pytest.mark.parametrize("campaign_data", CAMPAIGN_SUBMISSION_CASES)
def test_submit_complete_campaign_for_approval(monkeypatch, campaign_data):
    session = FakeSession()
    campaign = make_campaign(campaign_data)
    patch_approval_storage(monkeypatch, campaign)

    status_details = CampaignApprovalController.SubmitCampaignForApproval(session, campaign)

    assert campaign.status == "pending"
    assert campaign.submitted_at is not None
    assert status_details["status"] == "pending"
    assert session.commits == 1


@pytest.mark.parametrize("overrides,has_image,expected_message", INCOMPLETE_CAMPAIGN_SUBMISSION_CASES)
def test_submit_rejects_incomplete_campaign(monkeypatch, overrides, has_image, expected_message):
    session = FakeSession()
    campaign = make_campaign(CAMPAIGN_SUBMISSION_CASES[0], **overrides)
    patch_approval_storage(monkeypatch, campaign, has_image=has_image)

    with pytest.raises(HTTPException) as error:
        CampaignApprovalController.SubmitCampaignForApproval(session, campaign)
    assert error.value.detail == expected_message


@pytest.mark.parametrize("workflow_stage,required_stage,should_pass", WORKFLOW_STAGE_CASES)
def test_validate_workflow_stage(workflow_stage, required_stage, should_pass):
    campaign = make_campaign(CAMPAIGN_SUBMISSION_CASES[0], workflow_stage=workflow_stage)
    if should_pass:
        CampaignController.ValidateWorkflowStage(campaign, required_stage)
        return

    with pytest.raises(HTTPException) as error:
        CampaignController.ValidateWorkflowStage(campaign, required_stage)
    assert error.value.status_code == 400


@pytest.mark.parametrize("title,category,expected_category", VALID_CAMPAIGN_INFORMATION_CASES)
def test_validate_campaign_information_accepts_valid_data(title, category, expected_category):
    clean_title, clean_category = CampaignController.ValidateCampaignInformation(title, category)
    assert clean_title == title.strip()
    assert clean_category == expected_category


@pytest.mark.parametrize("category", INVALID_CAMPAIGN_CATEGORIES)
def test_validate_campaign_information_rejects_invalid_category(category):
    with pytest.raises(HTTPException) as error:
        CampaignController.ValidateCampaignInformation("Community Help", category)
    assert error.value.status_code == 400


@pytest.mark.parametrize("validator_name,value", FUNDRAISER_VALIDATOR_CASES)
def test_fundraiser_validators_accept_good_values(validator_name, value):
    validator = VALIDATORS[validator_name]
    if isinstance(value, tuple):
        result = validator(*value)
    else:
        result = validator(value)
    assert result is not None
