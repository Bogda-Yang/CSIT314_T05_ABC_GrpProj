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
| `CampaignManagementPage` | `campaign_create_page()` `routers/fundraiser.py:46`, `create_campaign()` `routers/fundraiser.py:215` |
| `CampaignController` | `ValidateCampaignInformation()` `services/campaign_service.py:381`, `CreateCampaign()` `services/campaign_service.py:397`, `SaveCampaignDraft()` `services/campaign_service.py:410` |
| `FundraisingCampaign` | `CreateCampaign()` `models/campaign.py:41`, `SaveCampaignDraft()` `models/campaign.py:62`, `GetCampaignDetails()` `models/campaign.py:66` |

## F2 Edit Fundraising Campaign

| BCE Class | Method definitions |
|---|---|
| `CampaignManagementPage` | `campaign_management_page()` `routers/fundraiser.py:166`, `update_campaign_basic_information()` `routers/fundraiser.py:243` |
| `CampaignController` | `GetCampaignDetails()` `services/campaign_service.py:414`, `ValidateUpdatedInformation()` `services/campaign_service.py:421`, `UpdateCampaign()` `services/campaign_service.py:425`, `SaveCampaignChanges()` `services/campaign_service.py:439` |
| `FundraisingCampaign` | `GetCampaignDetails()` `models/campaign.py:66`, `UpdateCampaign()` `models/campaign.py:259`, `SaveCampaignChanges()` `models/campaign.py:270` |

## F3 Delete Fundraising Campaign

| BCE Class | Method definitions |
|---|---|
| `CampaignManagementPage` | `campaign_management_page()` `routers/fundraiser.py:166`, `delete_campaign()` `routers/fundraiser.py:453` |
| `CampaignController` | `DeleteCampaign()` `services/campaign_service.py:443`, `RemoveCampaign()` `services/campaign_service.py:454` |
| `FundraisingCampaign` | `DeleteCampaign()` `models/campaign.py:280` |

## F4 Set Fundraising Goal

| BCE Class | Method definitions |
|---|---|
| `CampaignGoalPage` | `set_campaign_goal()` `routers/fundraiser.py:274` |
| `CampaignGoalController` | `ValidateGoalInformation()` `services/campaign_service.py:469`, `SetFundraisingGoal()` `services/campaign_service.py:480`, `SaveFundraisingGoal()` `services/campaign_service.py:492` |
| `CampaignGoal` | `SetGoal()` `models/campaign.py:528`, `SaveGoal()` `models/campaign.py:538`, `GetGoalDetails()` `models/campaign.py:542` |

## F5 Add Campaign Description

| BCE Class | Method definitions |
|---|---|
| `CampaignDescriptionPage` | `set_campaign_description()` `routers/fundraiser.py:304` |
| `CampaignDescriptionController` | `ValidateDescriptionContent()` `services/campaign_service.py:498`, `AddCampaignDescription()` `services/campaign_service.py:513`, `SaveCampaignDescription()` `services/campaign_service.py:525` |
| `CampaignDescription` | `SetDescription()` `models/campaign.py:548`, `SaveDescription()` `models/campaign.py:558`, `GetDescriptionDetails()` `models/campaign.py:562` |

## F6 Upload Campaign Images

| BCE Class | Method definitions |
|---|---|
| `CampaignImagePage` | `upload_campaign_images()` `routers/fundraiser.py:334`, `delete_campaign_image()` `routers/fundraiser.py:364` |
| `CampaignImageController` | `ValidateImageFormatAndSize()` `services/campaign_service.py:531`, `UploadCampaignImages()` `services/campaign_service.py:574`, `SaveImageRecords()` `services/campaign_service.py:619`, `DeleteCampaignImage()` `services/campaign_service.py:623` |
| `CampaignImage` | `StoreImages()` `models/campaign.py:389`, `SaveImageRecords()` `models/campaign.py:400`, `GetImageDetails()` `models/campaign.py:404` |

## F7 Set Campaign Deadline

| BCE Class | Method definitions |
|---|---|
| `CampaignDeadlinePage` | `set_campaign_deadline()` `routers/fundraiser.py:394` |
| `CampaignDeadlineController` | `ValidateDeadline()` `services/campaign_service.py:653`, `SetCampaignDeadline()` `services/campaign_service.py:672`, `SaveCampaignDeadline()` `services/campaign_service.py:684` |
| `CampaignDeadline` | `SetDeadline()` `models/campaign.py:568`, `SaveDeadline()` `models/campaign.py:578`, `GetDeadlineDetails()` `models/campaign.py:582` |

## F8 Submit Campaign for Approval

| BCE Class | Method definitions |
|---|---|
| `CampaignSubmissionPage` | `submit_campaign_for_approval()` `routers/fundraiser.py:424` |
| `CampaignApprovalController` | `ValidateSubmissionRequirements()` `services/campaign_service.py:690`, `SubmitCampaignForApproval()` `services/campaign_service.py:710`, `UpdateCampaignStatusToPending()` `services/campaign_service.py:722` |
| `CampaignStatus` | `SetPending()` `models/campaign.py:588`, `GetStatus()` `models/campaign.py:606` |
| `FundraisingCampaign` | `GetCampaignDetails()` `models/campaign.py:66`, `UpdateCampaignStatus()` `models/campaign.py:358` |

## F9 View Approval Status of Campaign

| BCE Class | Method definitions |
|---|---|
| `CampaignSubmissionPage` | `campaign_management_page()` `routers/fundraiser.py:166` |
| `CampaignApprovalController` | `RetrieveCampaignStatus()` `services/campaign_service.py:727`, `GetApprovalStatusDetails()` `services/campaign_service.py:734` |
| `CampaignStatus` | `GetStatus()` `models/campaign.py:606`, `GetStatusDetails()` `models/campaign.py:610` |
| `FundraisingCampaign` | `GetCampaignDetails()` `models/campaign.py:66` |

## F10 View Campaign Views

| BCE Class | Method definitions |
|---|---|
| `CampaignAnalyticsPage` | `your_fundraisers_page()` `routers/fundraiser.py:78` |
| `CampaignAnalyticsController` | `RetrieveViewStatistics()` `services/campaign_service.py:832`, `GetViewCount()` `services/campaign_service.py:848`, `GetDetailedExposureData()` `services/campaign_service.py:852` |
| `CampaignAnalytics` | `GetViewStatistics()` `models/campaign.py:627`, `GetViewCount()` `models/campaign.py:643`, `GetExposureDetails()` `models/campaign.py:648` |

## F11 View Campaign Shortlists

| BCE Class | Method definitions |
|---|---|
| `CampaignAnalyticsPage` | `your_fundraisers_page()` `routers/fundraiser.py:78` |
| `CampaignAnalyticsController` | `RetrieveShortlistStatistics()` `services/campaign_service.py:856`, `GetShortlistCount()` `services/campaign_service.py:872`, `GetDetailedInterestData()` `services/campaign_service.py:876` |
| `CampaignAnalytics` | `GetShortlistStatistics()` `models/campaign.py:661`, `GetShortlistCount()` `models/campaign.py:677`, `GetInterestDetails()` `models/campaign.py:683` |

## F12 View Completed Campaigns

| BCE Class | Method definitions |
|---|---|
| `CampaignHistoryPage` | `your_fundraisers_page()` `routers/fundraiser.py:78` |
| `CampaignHistoryController` | `RetrieveCompletedCampaignList()` `services/campaign_service.py:898`, `GetCompletedCampaignDetails()` `services/campaign_service.py:912`, `GetCampaignPerformance()` `services/campaign_service.py:921` |
| `CompletedCampaignRecord` | `GetCompletedCampaigns()` `models/campaign.py:691`, `GetCampaignById()` `models/campaign.py:707`, `GetPerformanceData()` `models/campaign.py:718` |

## F13 Filter Campaigns Using Selectable Criteria

| BCE Class | Method definitions |
|---|---|
| `CampaignAnalysisPage` | `your_fundraisers_page()` `routers/fundraiser.py:78` |
| `CampaignFilterController` | `FilterCampaigns()` `services/campaign_service.py:934`, `RetrieveFilteredCampaignResults()` `services/campaign_service.py:950` |
| `FundraisingCampaign` | `FilterCampaigns()` `models/campaign.py:130`, `GetFilteredCampaigns()` `models/campaign.py:144` |
