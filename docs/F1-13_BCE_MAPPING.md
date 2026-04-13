# F1-13 BCE Mapping

This file maps the current strict BCE-aligned implementation for fundraiser campaign management.

Scope note:

- The currently aligned strict scope is `F1-9`.
- `F10-13` remain unimplemented and are intentionally left out of the strict mapping below.
- Public campaign browsing on `/projects` is outside the fundraiser-management BCE scope documented here.

## F1 Create Fundraising Campaign

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `CampaignManagementPage` | [templates/campaign_create.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/campaign_create.html) | `AccessCampaignCreationPage()`, `EnterBasicCampaignInformation()`, `SubmitCampaignCreation()`, `DisplayCreationResult()` |
| `CampaignController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `ValidateCampaignInformation()`, `CreateCampaign()`, `SaveCampaignDraft()` |
| `FundraisingCampaign` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `CreateCampaign()`, `SaveCampaignDraft()`, `GetCampaignDetails()` |

## F2 Edit Fundraising Campaign

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `CampaignManagementPage` | [templates/campaign_create.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/campaign_create.html), [templates/campaign_workflow.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/campaign_workflow.html) | `AccessCampaignManagementPage()`, `SelectExistingCampaign()`, `ViewCurrentCampaignDetails()`, `EditCampaignInformation()`, `SubmitCampaignUpdate()`, `DisplayUpdateResult()` |
| `CampaignController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetCampaignDetails()`, `ValidateUpdatedInformation()`, `UpdateCampaign()`, `SaveCampaignChanges()` |
| `FundraisingCampaign` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetCampaignById()`, `GetCampaignDetails()`, `UpdateCampaign()`, `SaveCampaignChanges()` |

## F3 Delete Fundraising Campaign

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `CampaignManagementPage` | [templates/campaign_create.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/campaign_create.html), [templates/campaign_workflow.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/campaign_workflow.html) | `AccessCampaignManagementPage()`, `SelectCampaign()`, `ReviewCampaignDetails()`, `ConfirmCampaignDeletion()`, `DisplayDeletionResult()` |
| `CampaignController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetCampaignDetails()`, `DeleteCampaign()`, `RemoveCampaign()` |
| `FundraisingCampaign` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetCampaignById()`, `GetCampaignDetails()`, `DeleteCampaign()` |

## F4 Set Fundraising Goal

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `CampaignGoalPage` | [templates/campaign_workflow.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/campaign_workflow.html) | `AccessCampaignGoalSection()`, `EnterGoalAmount()`, `SubmitGoalUpdate()`, `DisplayGoalUpdateResult()` |
| `CampaignGoalController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `ValidateGoalInformation()`, `SetFundraisingGoal()`, `SaveFundraisingGoal()` |
| `CampaignGoal` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `SetGoal()`, `SaveGoal()`, `GetGoalDetails()` |

## F5 Add Campaign Description

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `CampaignDescriptionPage` | [templates/campaign_workflow.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/campaign_workflow.html) | `AccessCampaignDescriptionSection()`, `EnterCampaignDescription()`, `SubmitDescriptionUpdate()`, `DisplayDescriptionUpdateResult()` |
| `CampaignDescriptionController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `ValidateDescriptionContent()`, `AddCampaignDescription()`, `SaveCampaignDescription()` |
| `CampaignDescription` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `SetDescription()`, `SaveDescription()`, `GetDescriptionDetails()` |

## F6 Upload Campaign Images

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `CampaignImagePage` | [templates/campaign_workflow.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/campaign_workflow.html) | `AccessCampaignImageSection()`, `SelectImageFiles()`, `UploadImages()`, `DisplayUploadResult()` |
| `CampaignImageController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `ValidateImageFormatAndSize()`, `UploadCampaignImages()`, `SaveImageRecords()` |
| `CampaignImage` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `StoreImages()`, `SaveImageRecords()`, `GetImageDetails()` |

## F7 Set Campaign Deadline

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `CampaignDeadlinePage` | [templates/campaign_workflow.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/campaign_workflow.html) | `AccessCampaignDeadlineSection()`, `SelectDeadlineDate()`, `SubmitDeadlineUpdate()`, `DisplayDeadlineUpdateResult()` |
| `CampaignDeadlineController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `ValidateDeadline()`, `SetCampaignDeadline()`, `SaveCampaignDeadline()` |
| `CampaignDeadline` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `SetDeadline()`, `SaveDeadline()`, `GetDeadlineDetails()` |

## F8 Submit Campaign for Approval

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `CampaignSubmissionPage` | [templates/campaign_workflow.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/campaign_workflow.html) | `AccessCampaignSubmissionPage()`, `ReviewCampaignInformation()`, `SubmitCampaign()`, `DisplaySubmissionResult()` |
| `CampaignApprovalController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `ValidateSubmissionRequirements()`, `SubmitCampaignForApproval()`, `UpdateCampaignStatusToPending()` |
| `FundraisingCampaign` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetCampaignDetails()`, `SubmitCampaign()` |
| `CampaignStatus` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `SetPending()`, `GetStatus()` |

## F9 View Approval Status of Campaign

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `CampaignSubmissionPage` | [templates/campaign_workflow.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/campaign_workflow.html) | `AccessCampaignManagementPage()`, `ViewApprovalStatusDetails()`, `RefreshApprovalStatus()` |
| `CampaignApprovalController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `RetrieveCampaignStatus()`, `GetApprovalStatusDetails()` |
| `CampaignStatus` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetStatus()`, `GetStatusDetails()` |
| `FundraisingCampaign` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetCampaignById()` |

## Strict F1-9 Routes

| Route | Purpose |
|---|---|
| `GET /projects/create-campaign` | Access fundraiser campaign management entry page |
| `GET /projects/manage/{campaign_id}` | Open selected campaign workflow |
| `POST /projects/create` | Create a new fundraising campaign draft |
| `POST /projects/{campaign_id}/basic` | Update basic campaign information |
| `POST /projects/{campaign_id}/goal` | Set or update campaign goal |
| `POST /projects/{campaign_id}/description` | Set or update campaign description |
| `POST /projects/{campaign_id}/images` | Upload campaign images |
| `POST /projects/{campaign_id}/images/{image_id}/delete` | Delete a campaign image |
| `POST /projects/{campaign_id}/deadline` | Set or update campaign deadline |
| `POST /projects/{campaign_id}/submit` | Submit campaign for approval |
| `POST /projects/{campaign_id}/delete` | Delete a fundraiser-owned campaign |
