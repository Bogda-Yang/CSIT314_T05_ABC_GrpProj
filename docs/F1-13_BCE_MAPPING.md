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
- `F10 View Campaign Views`
- `F11 View Campaign Shortlists`
- `F12 View Completed Campaigns`
- `F13 Filter Campaigns Using Selectable Criteria`

## F1 Create Fundraising Campaign

| BCE Class | Method definitions |
|---|---|
| `CampaignManagementPage` | `campaign_create_page()` `routers/fundraiser.py:47`, `create_campaign()` `routers/fundraiser.py:225` |
| `CampaignController` | `ValidateCampaignInformation()` `services/campaign_service.py:508`, `CreateCampaign()` `services/campaign_service.py:524`, `SaveCampaignDraft()` `services/campaign_service.py:537` |
| `FundraisingCampaign` | `CreateCampaign()` `models/campaign.py:42`, `SaveCampaignDraft()` `models/campaign.py:63`, `GetCampaignDetails()` `models/campaign.py:67` |

## F2 Edit Fundraising Campaign

| BCE Class | Method definitions |
|---|---|
| `CampaignManagementPage` | `campaign_management_page()` `routers/fundraiser.py:173`, `update_campaign_basic_information()` `routers/fundraiser.py:253` |
| `CampaignController` | `GetCampaignDetails()` `services/campaign_service.py:541`, `ValidateUpdatedInformation()` `services/campaign_service.py:548`, `UpdateCampaign()` `services/campaign_service.py:552`, `SaveCampaignChanges()` `services/campaign_service.py:566` |
| `FundraisingCampaign` | `GetCampaignDetails()` `models/campaign.py:67`, `UpdateCampaign()` `models/campaign.py:263`, `SaveCampaignChanges()` `models/campaign.py:274` |

## F3 Delete Fundraising Campaign

| BCE Class | Method definitions |
|---|---|
| `CampaignManagementPage` | `campaign_management_page()` `routers/fundraiser.py:173`, `delete_campaign()` `routers/fundraiser.py:463` |
| `CampaignController` | `DeleteCampaign()` `services/campaign_service.py:570`, `RemoveCampaign()` `services/campaign_service.py:585` |
| `FundraisingCampaign` | `DeleteCampaign()` `models/campaign.py:284` |

## F4 Set Fundraising Goal

| BCE Class | Method definitions |
|---|---|
| `CampaignGoalPage` | `set_campaign_goal()` `routers/fundraiser.py:284` |
| `CampaignGoalController` | `ValidateGoalInformation()` `services/campaign_service.py:600`, `SetFundraisingGoal()` `services/campaign_service.py:611`, `SaveFundraisingGoal()` `services/campaign_service.py:623` |
| `CampaignGoal` | `SetGoal()` `models/campaign.py:555`, `SaveGoal()` `models/campaign.py:565`, `GetGoalDetails()` `models/campaign.py:569` |

## F5 Add Campaign Description

| BCE Class | Method definitions |
|---|---|
| `CampaignDescriptionPage` | `set_campaign_description()` `routers/fundraiser.py:314` |
| `CampaignDescriptionController` | `ValidateDescriptionContent()` `services/campaign_service.py:629`, `AddCampaignDescription()` `services/campaign_service.py:644`, `SaveCampaignDescription()` `services/campaign_service.py:656` |
| `CampaignDescription` | `SetDescription()` `models/campaign.py:575`, `SaveDescription()` `models/campaign.py:585`, `GetDescriptionDetails()` `models/campaign.py:589` |

## F6 Upload Campaign Images

| BCE Class | Method definitions |
|---|---|
| `CampaignImagePage` | `upload_campaign_images()` `routers/fundraiser.py:344`, `delete_campaign_image()` `routers/fundraiser.py:374` |
| `CampaignImageController` | `ValidateImageFormatAndSize()` `services/campaign_service.py:662`, `UploadCampaignImages()` `services/campaign_service.py:705`, `SaveImageRecords()` `services/campaign_service.py:750`, `DeleteCampaignImage()` `services/campaign_service.py:754` |
| `CampaignImage` | `StoreImages()` `models/campaign.py:405`, `SaveImageRecords()` `models/campaign.py:416`, `GetImageDetails()` `models/campaign.py:420` |

## F7 Set Campaign Deadline

| BCE Class | Method definitions |
|---|---|
| `CampaignDeadlinePage` | `set_campaign_deadline()` `routers/fundraiser.py:404` |
| `CampaignDeadlineController` | `ValidateDeadline()` `services/campaign_service.py:784`, `SetCampaignDeadline()` `services/campaign_service.py:803`, `SaveCampaignDeadline()` `services/campaign_service.py:815` |
| `CampaignDeadline` | `SetDeadline()` `models/campaign.py:595`, `SaveDeadline()` `models/campaign.py:605`, `GetDeadlineDetails()` `models/campaign.py:609` |

## F8 Submit Campaign for Approval

| BCE Class | Method definitions |
|---|---|
| `CampaignSubmissionPage` | `submit_campaign_for_approval()` `routers/fundraiser.py:434` |
| `CampaignApprovalController` | `ValidateSubmissionRequirements()` `services/campaign_service.py:821`, `SubmitCampaignForApproval()` `services/campaign_service.py:841`, `UpdateCampaignStatusToPending()` `services/campaign_service.py:853` |
| `CampaignStatus` | `SetPending()` `models/campaign.py:615`, `GetStatus()` `models/campaign.py:633` |
| `FundraisingCampaign` | `GetCampaignDetails()` `models/campaign.py:67`, `UpdateCampaignStatus()` `models/campaign.py:374` |

## F9 View Approval Status of Campaign

| BCE Class | Method definitions |
|---|---|
| `CampaignSubmissionPage` | `campaign_management_page()` `routers/fundraiser.py:173` |
| `CampaignApprovalController` | `RetrieveCampaignStatus()` `services/campaign_service.py:858`, `GetApprovalStatusDetails()` `services/campaign_service.py:865` |
| `CampaignStatus` | `GetStatus()` `models/campaign.py:633`, `GetStatusDetails()` `models/campaign.py:637` |
| `FundraisingCampaign` | `GetCampaignDetails()` `models/campaign.py:67` |

## F10 View Campaign Views

| BCE Class | Method definitions |
|---|---|
| `CampaignAnalyticsPage` | `your_fundraisers_page()` `routers/fundraiser.py:82` |
| `CampaignAnalyticsController` | `RetrieveViewStatistics()` `services/campaign_service.py:963`, `GetViewCount()` `services/campaign_service.py:979`, `GetDetailedExposureData()` `services/campaign_service.py:983` |
| `CampaignAnalytics` | `GetViewStatistics()` `models/campaign.py:654`, `GetViewCount()` `models/campaign.py:670`, `GetExposureDetails()` `models/campaign.py:675` |

## F11 View Campaign Shortlists

| BCE Class | Method definitions |
|---|---|
| `CampaignAnalyticsPage` | `your_fundraisers_page()` `routers/fundraiser.py:82` |
| `CampaignAnalyticsController` | `RetrieveShortlistStatistics()` `services/campaign_service.py:987`, `GetShortlistCount()` `services/campaign_service.py:1003`, `GetDetailedInterestData()` `services/campaign_service.py:1007` |
| `CampaignAnalytics` | `GetShortlistStatistics()` `models/campaign.py:688`, `GetShortlistCount()` `models/campaign.py:704`, `GetInterestDetails()` `models/campaign.py:710` |

## F12 View Completed Campaigns

| BCE Class | Method definitions |
|---|---|
| `CampaignHistoryPage` | `your_fundraisers_page()` `routers/fundraiser.py:82` |
| `CampaignHistoryController` | `RetrieveCompletedCampaignList()` `services/campaign_service.py:1029`, `GetCompletedCampaignDetails()` `services/campaign_service.py:1043`, `GetCampaignPerformance()` `services/campaign_service.py:1052` |
| `CompletedCampaignRecord` | `GetCompletedCampaigns()` `models/campaign.py:718`, `GetCampaignById()` `models/campaign.py:734`, `GetPerformanceData()` `models/campaign.py:745` |

## F13 Filter Campaigns Using Selectable Criteria

| BCE Class | Method definitions |
|---|---|
| `CampaignAnalysisPage` | `your_fundraisers_page()` `routers/fundraiser.py:82` |
| `CampaignFilterController` | `FilterCampaigns()` `services/campaign_service.py:1065`, `RetrieveFilteredCampaignResults()` `services/campaign_service.py:1081` |
| `FundraisingCampaign` | `FilterCampaigns()` `models/campaign.py:134`, `GetFilteredCampaigns()` `models/campaign.py:148` |
