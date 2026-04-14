# F1-13 BCE Mapping

This document lists only the currently implemented fundraiser-management methods.

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

| BCE Class | File / Line | Methods / Line |
|---|---|---|
| `CampaignManagementPage` | `templates/campaign_create.html:91-124` | `AccessCampaignCreationPage()`, `EnterBasicCampaignInformation()`, `SubmitCampaignCreation()`, `DisplayCreationResult()` |
| `CampaignController` | `main.py:2042-2077` | `ValidateCampaignInformation()` `main.py:2042`, `CreateCampaign()` `main.py:2059`, `SaveCampaignDraft()` `main.py:2073` |
| `FundraisingCampaign` | `main.py:396-419` | `CreateCampaign()` `main.py:396`, `SaveCampaignDraft()` `main.py:415`, `GetCampaignDetails()` `main.py:419` |

## F2 Edit Fundraising Campaign

| BCE Class | File / Line | Methods / Line |
|---|---|---|
| `CampaignManagementPage` | `templates/campaign_create.html:126-162`, `templates/campaign_workflow.html:95-188` | `AccessCampaignManagementPage()`, `SelectExistingCampaign()`, `ViewCurrentCampaignDetails()`, `EditCampaignInformation()`, `SubmitCampaignUpdate()`, `DisplayUpdateResult()` |
| `CampaignController` | `main.py:2078-2109` | `GetCampaignDetails()` `main.py:2078`, `ValidateUpdatedInformation()` `main.py:2086`, `UpdateCampaign()` `main.py:2091`, `SaveCampaignChanges()` `main.py:2106` |
| `FundraisingCampaign` | `main.py:419-459` | `GetCampaignDetails()` `main.py:419`, `UpdateCampaign()` `main.py:448`, `SaveCampaignChanges()` `main.py:459` |

## F3 Delete Fundraising Campaign

| BCE Class | File / Line | Methods / Line |
|---|---|---|
| `CampaignManagementPage` | `templates/campaign_workflow.html:366-379` | `AccessCampaignManagementPage()`, `SelectCampaign()`, `ReviewCampaignDetails()`, `ConfirmCampaignDeletion()`, `DisplayDeletionResult()` |
| `CampaignController` | `main.py:2111-2120` | `DeleteCampaign()` `main.py:2111`, `RemoveCampaign()` `main.py:2120` |
| `FundraisingCampaign` | `main.py:469` | `DeleteCampaign()` `main.py:469` |

## F4 Set Fundraising Goal

| BCE Class | File / Line | Methods / Line |
|---|---|---|
| `CampaignGoalPage` | `templates/campaign_workflow.html:190-212` | `AccessCampaignGoalSection()`, `EnterGoalAmount()`, `SubmitGoalUpdate()`, `DisplayGoalUpdateResult()` |
| `CampaignGoalController` | `main.py:2138-2163` | `ValidateGoalInformation()` `main.py:2138`, `SetFundraisingGoal()` `main.py:2150`, `SaveFundraisingGoal()` `main.py:2163` |
| `CampaignGoal` | `main.py:636-650` | `SetGoal()` `main.py:636`, `SaveGoal()` `main.py:646`, `GetGoalDetails()` `main.py:650` |

## F5 Add Campaign Description

| BCE Class | File / Line | Methods / Line |
|---|---|---|
| `CampaignDescriptionPage` | `templates/campaign_workflow.html:214-236` | `AccessCampaignDescriptionSection()`, `EnterCampaignDescription()`, `SubmitDescriptionUpdate()`, `DisplayDescriptionUpdateResult()` |
| `CampaignDescriptionController` | `main.py:2171-2200` | `ValidateDescriptionContent()` `main.py:2171`, `AddCampaignDescription()` `main.py:2187`, `SaveCampaignDescription()` `main.py:2200` |
| `CampaignDescription` | `main.py:657-671` | `SetDescription()` `main.py:657`, `SaveDescription()` `main.py:667`, `GetDescriptionDetails()` `main.py:671` |

## F6 Upload Campaign Images

| BCE Class | File / Line | Methods / Line |
|---|---|---|
| `CampaignImagePage` | `templates/campaign_workflow.html:238-300` | `AccessCampaignImageSection()`, `SelectImageFiles()`, `UploadImages()`, `DisplayUploadResult()` |
| `CampaignImageController` | `main.py:2208-2309` | `ValidateImageFormatAndSize()` `main.py:2208`, `UploadCampaignImages()` `main.py:2252`, `SaveImageRecords()` `main.py:2298` |
| `CampaignImage` | `main.py:546-563` | `StoreImages()` `main.py:546`, `SaveImageRecords()` `main.py:559`, `GetImageDetails()` `main.py:563` |

## F7 Set Campaign Deadline

| BCE Class | File / Line | Methods / Line |
|---|---|---|
| `CampaignDeadlinePage` | `templates/campaign_workflow.html:302-324` | `AccessCampaignDeadlineSection()`, `SelectDeadlineDate()`, `SubmitDeadlineUpdate()`, `DisplayDeadlineUpdateResult()` |
| `CampaignDeadlineController` | `main.py:2335-2368` | `ValidateDeadline()` `main.py:2335`, `SetCampaignDeadline()` `main.py:2355`, `SaveCampaignDeadline()` `main.py:2368` |
| `CampaignDeadline` | `main.py:678-692` | `SetDeadline()` `main.py:678`, `SaveDeadline()` `main.py:688`, `GetDeadlineDetails()` `main.py:692` |

## F8 Submit Campaign for Approval

| BCE Class | File / Line | Methods / Line |
|---|---|---|
| `CampaignSubmissionPage` | `templates/campaign_workflow.html:326-364` | `AccessCampaignSubmissionPage()`, `ReviewCampaignInformation()`, `SubmitCampaign()`, `DisplaySubmissionResult()` |
| `CampaignApprovalController` | `main.py:2376-2415` | `ValidateSubmissionRequirements()` `main.py:2376`, `SubmitCampaignForApproval()` `main.py:2397`, `UpdateCampaignStatusToPending()` `main.py:2410` |
| `CampaignStatus` | `main.py:699-717` | `SetPending()` `main.py:699`, `GetStatus()` `main.py:717` |
| `FundraisingCampaign` | `main.py:419-514` | `GetCampaignDetails()` `main.py:419`, `UpdateCampaignStatus()` `main.py:514` |

## F9 View Approval Status of Campaign

| BCE Class | File / Line | Methods / Line |
|---|---|---|
| `CampaignSubmissionPage` | `templates/campaign_workflow.html:326-350` | `AccessCampaignManagementPage()`, `ViewApprovalStatusDetails()`, `RefreshApprovalStatus()` |
| `CampaignApprovalController` | `main.py:2416-2447` | `RetrieveCampaignStatus()` `main.py:2416`, `GetApprovalStatusDetails()` `main.py:2424` |
| `CampaignStatus` | `main.py:717-727` | `GetStatus()` `main.py:717`, `GetStatusDetails()` `main.py:721` |
| `FundraisingCampaign` | `main.py:419` | `GetCampaignDetails()` `main.py:419` |

## F1-9 Routes

| Route | File / Line | Purpose |
|---|---|---|
| `GET /projects/create-campaign` | `main.py:2891-2921` | Access fundraiser campaign entry page |
| `GET /projects/manage/{campaign_id}` | `main.py:2924-2971` | Open selected campaign workflow |
| `POST /projects/create` | `main.py:3089-3115` | Create a new fundraising campaign draft |
| `POST /projects/{campaign_id}/basic` | `main.py:3117-3145` | Update basic campaign information |
| `POST /projects/{campaign_id}/goal` | `main.py:3148-3175` | Set or update campaign goal |
| `POST /projects/{campaign_id}/description` | `main.py:3178-3205` | Set or update campaign description |
| `POST /projects/{campaign_id}/images` | `main.py:3208-3235` | Upload campaign images |
| `POST /projects/{campaign_id}/images/{image_id}/delete` | `main.py:3238-3265` | Delete a campaign image |
| `POST /projects/{campaign_id}/deadline` | `main.py:3268-3295` | Set or update campaign deadline |
| `POST /projects/{campaign_id}/submit` | `main.py:3298-3325` | Submit campaign for approval |
| `POST /projects/{campaign_id}/delete` | `main.py:3327-3352` | Delete a fundraiser-owned campaign |
