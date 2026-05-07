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
| `CampaignController` | `ValidateCampaignInformation()` `services/campaign_service.py:618`, `CreateCampaign()` `services/campaign_service.py:634`, `SaveCampaignDraft()` `services/campaign_service.py:647` |
| `FundraisingCampaign` | `CreateCampaign()` `models/campaign.py:42`, `SaveCampaignDraft()` `models/campaign.py:63`, `GetCampaignDetails()` `models/campaign.py:67` |

## F2 Edit Fundraising Campaign

| BCE Class | Method definitions |
|---|---|
| `CampaignManagementPage` | `campaign_management_page()` `routers/fundraiser.py:173`, `update_campaign_basic_information()` `routers/fundraiser.py:253` |
| `CampaignController` | `GetCampaignDetails()` `services/campaign_service.py:651`, `ValidateUpdatedInformation()` `services/campaign_service.py:658`, `UpdateCampaign()` `services/campaign_service.py:662`, `SaveCampaignChanges()` `services/campaign_service.py:676` |
| `FundraisingCampaign` | `GetCampaignDetails()` `models/campaign.py:67`, `UpdateCampaign()` `models/campaign.py:305`, `SaveCampaignChanges()` `models/campaign.py:316` |

## F3 Delete Fundraising Campaign

| BCE Class | Method definitions |
|---|---|
| `CampaignManagementPage` | `campaign_management_page()` `routers/fundraiser.py:173`, `delete_campaign()` `routers/fundraiser.py:463` |
| `CampaignController` | `DeleteCampaign()` `services/campaign_service.py:680`, `RemoveCampaign()` `services/campaign_service.py:695` |
| `FundraisingCampaign` | `DeleteCampaign()` `models/campaign.py:326` |

## F4 Set Fundraising Goal

| BCE Class | Method definitions |
|---|---|
| `CampaignGoalPage` | `set_campaign_goal()` `routers/fundraiser.py:284` |
| `CampaignGoalController` | `ValidateGoalInformation()` `services/campaign_service.py:710`, `SetFundraisingGoal()` `services/campaign_service.py:721`, `SaveFundraisingGoal()` `services/campaign_service.py:733` |
| `CampaignGoal` | `SetGoal()` `models/campaign.py:605`, `SaveGoal()` `models/campaign.py:615`, `GetGoalDetails()` `models/campaign.py:619` |

## F5 Add Campaign Description

| BCE Class | Method definitions |
|---|---|
| `CampaignDescriptionPage` | `set_campaign_description()` `routers/fundraiser.py:314` |
| `CampaignDescriptionController` | `ValidateDescriptionContent()` `services/campaign_service.py:739`, `AddCampaignDescription()` `services/campaign_service.py:754`, `SaveCampaignDescription()` `services/campaign_service.py:766` |
| `CampaignDescription` | `SetDescription()` `models/campaign.py:625`, `SaveDescription()` `models/campaign.py:635`, `GetDescriptionDetails()` `models/campaign.py:639` |

## F6 Upload Campaign Images

| BCE Class | Method definitions |
|---|---|
| `CampaignImagePage` | `upload_campaign_images()` `routers/fundraiser.py:344`, `delete_campaign_image()` `routers/fundraiser.py:374` |
| `CampaignImageController` | `ValidateImageFormatAndSize()` `services/campaign_service.py:772`, `UploadCampaignImages()` `services/campaign_service.py:815`, `SaveImageRecords()` `services/campaign_service.py:860`, `DeleteCampaignImage()` `services/campaign_service.py:864` |
| `CampaignImage` | `StoreImages()` `models/campaign.py:455`, `SaveImageRecords()` `models/campaign.py:466`, `GetImageDetails()` `models/campaign.py:470` |

## F7 Set Campaign Deadline

| BCE Class | Method definitions |
|---|---|
| `CampaignDeadlinePage` | `set_campaign_deadline()` `routers/fundraiser.py:404` |
| `CampaignDeadlineController` | `ValidateDeadline()` `services/campaign_service.py:894`, `SetCampaignDeadline()` `services/campaign_service.py:913`, `SaveCampaignDeadline()` `services/campaign_service.py:925` |
| `CampaignDeadline` | `SetDeadline()` `models/campaign.py:645`, `SaveDeadline()` `models/campaign.py:655`, `GetDeadlineDetails()` `models/campaign.py:659` |

## F8 Submit Campaign for Approval

| BCE Class | Method definitions |
|---|---|
| `CampaignSubmissionPage` | `submit_campaign_for_approval()` `routers/fundraiser.py:434` |
| `CampaignApprovalController` | `ValidateSubmissionRequirements()` `services/campaign_service.py:931`, `SubmitCampaignForApproval()` `services/campaign_service.py:951`, `UpdateCampaignStatusToPending()` `services/campaign_service.py:963` |
| `CampaignStatus` | `SetPending()` `models/campaign.py:665`, `GetStatus()` `models/campaign.py:683` |
| `FundraisingCampaign` | `GetCampaignDetails()` `models/campaign.py:67`, `UpdateCampaignStatus()` `models/campaign.py:424` |

## F9 View Approval Status of Campaign

| BCE Class | Method definitions |
|---|---|
| `CampaignSubmissionPage` | `campaign_management_page()` `routers/fundraiser.py:173` |
| `CampaignApprovalController` | `RetrieveCampaignStatus()` `services/campaign_service.py:968`, `GetApprovalStatusDetails()` `services/campaign_service.py:975` |
| `CampaignStatus` | `GetStatus()` `models/campaign.py:683`, `GetStatusDetails()` `models/campaign.py:687` |
| `FundraisingCampaign` | `GetCampaignDetails()` `models/campaign.py:67` |

## F10 View Campaign Views

| BCE Class | Method definitions |
|---|---|
| `CampaignAnalyticsPage` | `your_fundraisers_page()` `routers/fundraiser.py:82` |
| `CampaignAnalyticsController` | `RetrieveViewStatistics()` `services/campaign_service.py:1073`, `GetViewCount()` `services/campaign_service.py:1089`, `GetDetailedExposureData()` `services/campaign_service.py:1093` |
| `CampaignAnalytics` | `GetViewStatistics()` `models/campaign.py:704`, `GetViewCount()` `models/campaign.py:720`, `GetExposureDetails()` `models/campaign.py:725` |

## F11 View Campaign Shortlists

| BCE Class | Method definitions |
|---|---|
| `CampaignAnalyticsPage` | `your_fundraisers_page()` `routers/fundraiser.py:82` |
| `CampaignAnalyticsController` | `RetrieveShortlistStatistics()` `services/campaign_service.py:1097`, `GetShortlistCount()` `services/campaign_service.py:1113`, `GetDetailedInterestData()` `services/campaign_service.py:1117` |
| `CampaignAnalytics` | `GetShortlistStatistics()` `models/campaign.py:738`, `GetShortlistCount()` `models/campaign.py:754`, `GetInterestDetails()` `models/campaign.py:760` |

## F12 View Completed Campaigns

| BCE Class | Method definitions |
|---|---|
| `CampaignHistoryPage` | `your_fundraisers_page()` `routers/fundraiser.py:82` |
| `CampaignHistoryController` | `RetrieveCompletedCampaignList()` `services/campaign_service.py:1139`, `GetCompletedCampaignDetails()` `services/campaign_service.py:1153`, `GetCampaignPerformance()` `services/campaign_service.py:1162` |
| `CompletedCampaignRecord` | `GetCompletedCampaigns()` `models/campaign.py:768`, `GetCampaignById()` `models/campaign.py:784`, `GetPerformanceData()` `models/campaign.py:795` |

## F13 Filter Campaigns Using Selectable Criteria

| BCE Class | Method definitions |
|---|---|
| `CampaignAnalysisPage` | `your_fundraisers_page()` `routers/fundraiser.py:82` |
| `CampaignFilterController` | `FilterCampaigns()` `services/campaign_service.py:1175`, `RetrieveFilteredCampaignResults()` `services/campaign_service.py:1191` |
| `FundraisingCampaign` | `FilterCampaigns()` `models/campaign.py:145`, `GetFilteredCampaigns()` `models/campaign.py:163` |
