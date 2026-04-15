# F1-13 BCE Mapping

This version lists only real method/function definition lines.

Scope:

- `F1 Create Fundraising Campaign`
- `F2 Edit Fundraising Campaign`
- `F3 Delete Fundraising Campaign`
- `F4 Set Fundraising Goal`
- `F5 Add Campaign Description`
- `F6 Upload Campaign Images`
- `F7 Set Campaign Deadline`
- `F8 Submit Campaign for Approval`
- `F9 View Approval Status of Campaign`

`F10-13` are intentionally excluded because they are not part of the current implemented scope.

## F1 Create Fundraising Campaign

| BCE Class | Method definitions |
|---|---|
| `CampaignManagementPage` | `campaign_create_page()` `routers/fundraiser.py:36`, `create_campaign()` `routers/fundraiser.py:117` |
| `CampaignController` | `ValidateCampaignInformation()` `services/campaign_service.py:307`, `CreateCampaign()` `services/campaign_service.py:323`, `SaveCampaignDraft()` `services/campaign_service.py:336` |
| `FundraisingCampaign` | `CreateCampaign()` `models/campaign.py:38`, `SaveCampaignDraft()` `models/campaign.py:57`, `GetCampaignDetails()` `models/campaign.py:61` |

## F2 Edit Fundraising Campaign

| BCE Class | Method definitions |
|---|---|
| `CampaignManagementPage` | `campaign_management_page()` `routers/fundraiser.py:68`, `update_campaign_basic_information()` `routers/fundraiser.py:145` |
| `CampaignController` | `GetCampaignDetails()` `services/campaign_service.py:340`, `ValidateUpdatedInformation()` `services/campaign_service.py:347`, `UpdateCampaign()` `services/campaign_service.py:351`, `SaveCampaignChanges()` `services/campaign_service.py:365` |
| `FundraisingCampaign` | `GetCampaignDetails()` `models/campaign.py:61`, `UpdateCampaign()` `models/campaign.py:90`, `SaveCampaignChanges()` `models/campaign.py:101` |

## F3 Delete Fundraising Campaign

| BCE Class | Method definitions |
|---|---|
| `CampaignManagementPage` | `campaign_management_page()` `routers/fundraiser.py:68`, `delete_campaign()` `routers/fundraiser.py:355` |
| `CampaignController` | `DeleteCampaign()` `services/campaign_service.py:369`, `RemoveCampaign()` `services/campaign_service.py:377` |
| `FundraisingCampaign` | `DeleteCampaign()` `models/campaign.py:111` |

## F4 Set Fundraising Goal

| BCE Class | Method definitions |
|---|---|
| `CampaignGoalPage` | `set_campaign_goal()` `routers/fundraiser.py:176` |
| `CampaignGoalController` | `ValidateGoalInformation()` `services/campaign_service.py:392`, `SetFundraisingGoal()` `services/campaign_service.py:403`, `SaveFundraisingGoal()` `services/campaign_service.py:415` |
| `CampaignGoal` | `SetGoal()` `models/campaign.py:273`, `SaveGoal()` `models/campaign.py:283`, `GetGoalDetails()` `models/campaign.py:287` |

## F5 Add Campaign Description

| BCE Class | Method definitions |
|---|---|
| `CampaignDescriptionPage` | `set_campaign_description()` `routers/fundraiser.py:206` |
| `CampaignDescriptionController` | `ValidateDescriptionContent()` `services/campaign_service.py:421`, `AddCampaignDescription()` `services/campaign_service.py:436`, `SaveCampaignDescription()` `services/campaign_service.py:448` |
| `CampaignDescription` | `SetDescription()` `models/campaign.py:293`, `SaveDescription()` `models/campaign.py:303`, `GetDescriptionDetails()` `models/campaign.py:307` |

## F6 Upload Campaign Images

| BCE Class | Method definitions |
|---|---|
| `CampaignImagePage` | `upload_campaign_images()` `routers/fundraiser.py:236`, `delete_campaign_image()` `routers/fundraiser.py:266` |
| `CampaignImageController` | `ValidateImageFormatAndSize()` `services/campaign_service.py:454`, `UploadCampaignImages()` `services/campaign_service.py:497`, `SaveImageRecords()` `services/campaign_service.py:542`, `DeleteCampaignImage()` `services/campaign_service.py:546` |
| `CampaignImage` | `StoreImages()` `models/campaign.py:187`, `SaveImageRecords()` `models/campaign.py:198`, `GetImageDetails()` `models/campaign.py:202` |

## F7 Set Campaign Deadline

| BCE Class | Method definitions |
|---|---|
| `CampaignDeadlinePage` | `set_campaign_deadline()` `routers/fundraiser.py:296` |
| `CampaignDeadlineController` | `ValidateDeadline()` `services/campaign_service.py:576`, `SetCampaignDeadline()` `services/campaign_service.py:595`, `SaveCampaignDeadline()` `services/campaign_service.py:607` |
| `CampaignDeadline` | `SetDeadline()` `models/campaign.py:313`, `SaveDeadline()` `models/campaign.py:323`, `GetDeadlineDetails()` `models/campaign.py:327` |

## F8 Submit Campaign for Approval

| BCE Class | Method definitions |
|---|---|
| `CampaignSubmissionPage` | `submit_campaign_for_approval()` `routers/fundraiser.py:326` |
| `CampaignApprovalController` | `ValidateSubmissionRequirements()` `services/campaign_service.py:613`, `SubmitCampaignForApproval()` `services/campaign_service.py:633`, `UpdateCampaignStatusToPending()` `services/campaign_service.py:645` |
| `CampaignStatus` | `SetPending()` `models/campaign.py:333`, `GetStatus()` `models/campaign.py:351` |
| `FundraisingCampaign` | `GetCampaignDetails()` `models/campaign.py:61`, `UpdateCampaignStatus()` `models/campaign.py:156` |

## F9 View Approval Status of Campaign

| BCE Class | Method definitions |
|---|---|
| `CampaignSubmissionPage` | `campaign_management_page()` `routers/fundraiser.py:68` |
| `CampaignApprovalController` | `RetrieveCampaignStatus()` `services/campaign_service.py:650`, `GetApprovalStatusDetails()` `services/campaign_service.py:657` |
| `CampaignStatus` | `GetStatus()` `models/campaign.py:351`, `GetStatusDetails()` `models/campaign.py:355` |
| `FundraisingCampaign` | `GetCampaignDetails()` `models/campaign.py:61` |
