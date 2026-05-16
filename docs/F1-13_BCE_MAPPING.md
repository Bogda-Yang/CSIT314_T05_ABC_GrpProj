# F1-13 BCE Mapping

This version maps each BCE class and method to the real implementation definition lines.

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

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CampaignManagementPage` | `class CampaignManagementPage` `routers/fundraiser.py:153` | `AccessCampaignCreationPage()` `routers/fundraiser.py:157`, `EnterCampaignInformation()` `routers/fundraiser.py:247`, `SubmitCampaignCreation()` `routers/fundraiser.py:251`, and `DisplayCreationResult()` `routers/fundraiser.py:279` |
| `CampaignController` | `class CampaignController` `services/campaign_service.py:624` | `ValidateCampaignInformation()` `services/campaign_service.py:626`, `CreateCampaign()` `services/campaign_service.py:642`, and `SaveCampaignDraft()` `services/campaign_service.py:655` |
| `FundraisingCampaign` | `class FundraisingCampaign` `models/campaign.py:19` | `CreateCampaign()` `models/campaign.py:42` and `SaveCampaignDraft()` `models/campaign.py:63` |

## F2 Edit Fundraising Campaign

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CampaignManagementPage` | `class CampaignManagementPage` `routers/fundraiser.py:153` | `AccessCampaignManagementPage()` `routers/fundraiser.py:192`, `SelectCampaign()` `routers/fundraiser.py:293`, `ViewCurrentCampaignInformation()` `routers/fundraiser.py:301`, `EditCampaignInformation()` `routers/fundraiser.py:308`, `SubmitCampaignUpdate()` `routers/fundraiser.py:312`, and `DisplayUpdateResult()` `routers/fundraiser.py:340` |
| `CampaignController` | `class CampaignController` `services/campaign_service.py:624` | `ValidateUpdatedInformation()` `services/campaign_service.py:666`, `UpdateCampaign()` `services/campaign_service.py:670`, and `SaveCampaignChanges()` `services/campaign_service.py:684` |
| `FundraisingCampaign` | `class FundraisingCampaign` `models/campaign.py:19` | `GetCampaignById()` `models/campaign.py:71`, `UpdateCampaign()` `models/campaign.py:305`, `AdvanceWorkflowStage()` `models/campaign.py:321`, and `SaveCampaignChanges()` `models/campaign.py:316` |

## F3 Delete Fundraising Campaign

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CampaignManagementPage` | `class CampaignManagementPage` `routers/fundraiser.py:153` | `AccessCampaignManagementPage()` `routers/fundraiser.py:192`, `SelectCampaign()` `routers/fundraiser.py:293`, `ReviewCampaignDetails()` `routers/fundraiser.py:355`, `ConfirmCampaignDeletion()` `routers/fundraiser.py:362`, and `DisplayDeletionResult()` `routers/fundraiser.py:388` |
| `CampaignController` | `class CampaignController` `services/campaign_service.py:624` | `DeleteCampaign()` `services/campaign_service.py:688` |
| `CampaignImage` | `class CampaignImage` `models/campaign.py:444` | `DeleteImageRecords()` `models/campaign.py:483` |
| `RejectionRecord` | `class RejectionRecord` `models/campaign.py:569` | `DeleteCampaignRejectionRecords()` `models/campaign.py:599` |
| `FavouriteCampaign` | `class FavouriteCampaign` `models/donation.py:235` | `DeleteCampaignFavouriteRecords()` `models/donation.py:356` |
| `FundraisingCampaign` | `class FundraisingCampaign` `models/campaign.py:19` | `GetCampaignById()` `models/campaign.py:71` and `MarkDeleted()` `models/campaign.py:330` |

## F4 Set Fundraising Goal

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CampaignGoalPage` | `class CampaignGoalPage` `routers/fundraiser.py:403` | `AccessCampaignGoalStep()` `routers/fundraiser.py:407`, `EnterGoalAmount()` `routers/fundraiser.py:411`, `SubmitFundraisingGoal()` `routers/fundraiser.py:415`, and `DisplayGoalResult()` `routers/fundraiser.py:442` |
| `CampaignController` | `class CampaignController` `services/campaign_service.py:624` | `ValidateWorkflowStage()` `services/campaign_service.py:707` |
| `CampaignGoalController` | `class CampaignGoalController` `services/campaign_service.py:716` | `ValidateGoalInformation()` `services/campaign_service.py:718`, `SetFundraisingGoal()` `services/campaign_service.py:729`, and `SaveFundraisingGoal()` `services/campaign_service.py:741` |
| `CampaignGoal` | `class CampaignGoal` `models/campaign.py:603` | `SetGoal()` `models/campaign.py:605`, `SaveGoal()` `models/campaign.py:615`, and `GetGoalDetails()` `models/campaign.py:619` |
| `FundraisingCampaign` | `class FundraisingCampaign` `models/campaign.py:19` | `AdvanceWorkflowStage()` `models/campaign.py:321` |

## F5 Add Campaign Description

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CampaignDescriptionPage` | `class CampaignDescriptionPage` `routers/fundraiser.py:457` | `AccessCampaignDescriptionStep()` `routers/fundraiser.py:461`, `EnterCampaignDescription()` `routers/fundraiser.py:465`, `SubmitCampaignDescription()` `routers/fundraiser.py:469`, and `DisplayDescriptionResult()` `routers/fundraiser.py:496` |
| `CampaignController` | `class CampaignController` `services/campaign_service.py:624` | `ValidateWorkflowStage()` `services/campaign_service.py:707` |
| `CampaignDescriptionController` | `class CampaignDescriptionController` `services/campaign_service.py:745` | `ValidateDescriptionContent()` `services/campaign_service.py:747`, `AddCampaignDescription()` `services/campaign_service.py:762`, and `SaveCampaignDescription()` `services/campaign_service.py:774` |
| `CampaignDescription` | `class CampaignDescription` `models/campaign.py:623` | `SetDescription()` `models/campaign.py:625`, `SaveDescription()` `models/campaign.py:635`, and `GetDescriptionDetails()` `models/campaign.py:639` |
| `FundraisingCampaign` | `class FundraisingCampaign` `models/campaign.py:19` | `AdvanceWorkflowStage()` `models/campaign.py:321` |

## F6 Upload Campaign Images

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CampaignImagePage` | `class CampaignImagePage` `routers/fundraiser.py:511` | `AccessCampaignImageStep()` `routers/fundraiser.py:515`, `SelectCampaignImages()` `routers/fundraiser.py:519`, `UploadCampaignImages()` `routers/fundraiser.py:523`, `DeleteCampaignImage()` `routers/fundraiser.py:550`, and `DisplayImageResult()` `routers/fundraiser.py:576` |
| `CampaignController` | `class CampaignController` `services/campaign_service.py:624` | `ValidateWorkflowStage()` `services/campaign_service.py:707` |
| `CampaignImageController` | `class CampaignImageController` `services/campaign_service.py:778` | `ValidateImageFormatAndSize()` `services/campaign_service.py:780`, `UploadCampaignImages()` `services/campaign_service.py:823`, `SaveImageRecords()` `services/campaign_service.py:868`, and `DeleteCampaignImage()` `services/campaign_service.py:872` |
| `CampaignImage` | `class CampaignImage` `models/campaign.py:444` | `StoreImages()` `models/campaign.py:455`, `SaveImageRecords()` `models/campaign.py:466`, `GetImageDetails()` `models/campaign.py:470`, `GetImageRecord()` `models/campaign.py:492`, and `DeleteImageRecord()` `models/campaign.py:506` |
| `FundraisingCampaign` | `class FundraisingCampaign` `models/campaign.py:19` | `AdvanceWorkflowStage()` `models/campaign.py:321` |

## F7 Set Campaign Deadline

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CampaignDeadlinePage` | `class CampaignDeadlinePage` `routers/fundraiser.py:591` | `AccessCampaignDeadlineStep()` `routers/fundraiser.py:595`, `SelectCampaignDeadline()` `routers/fundraiser.py:599`, `SubmitCampaignDeadline()` `routers/fundraiser.py:603`, and `DisplayDeadlineResult()` `routers/fundraiser.py:630` |
| `CampaignController` | `class CampaignController` `services/campaign_service.py:624` | `ValidateWorkflowStage()` `services/campaign_service.py:707` |
| `CampaignDeadlineController` | `class CampaignDeadlineController` `services/campaign_service.py:900` | `ValidateDeadline()` `services/campaign_service.py:902`, `SetCampaignDeadline()` `services/campaign_service.py:921`, and `SaveCampaignDeadline()` `services/campaign_service.py:933` |
| `CampaignDeadline` | `class CampaignDeadline` `models/campaign.py:643` | `SetDeadline()` `models/campaign.py:645`, `SaveDeadline()` `models/campaign.py:655`, and `GetDeadlineDetails()` `models/campaign.py:659` |
| `FundraisingCampaign` | `class FundraisingCampaign` `models/campaign.py:19` | `AdvanceWorkflowStage()` `models/campaign.py:321` |

## F8 Submit Campaign for Approval

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CampaignSubmissionPage` | `class CampaignSubmissionPage` `routers/fundraiser.py:645` | `AccessSubmissionStep()` `routers/fundraiser.py:649`, `ReviewSubmissionRequirements()` `routers/fundraiser.py:653`, `SubmitCampaignForApproval()` `routers/fundraiser.py:660`, and `DisplaySubmissionResult()` `routers/fundraiser.py:686` |
| `CampaignController` | `class CampaignController` `services/campaign_service.py:624` | `ValidateWorkflowStage()` `services/campaign_service.py:707` |
| `CampaignApprovalController` | `class CampaignApprovalController` `services/campaign_service.py:937` | `ValidateSubmissionRequirements()` `services/campaign_service.py:939`, `SubmitCampaignForApproval()` `services/campaign_service.py:959`, `UpdateCampaignStatusToPending()` `services/campaign_service.py:971`, and `GetApprovalStatusDetails()` `services/campaign_service.py:983` |
| `CampaignImage` | `class CampaignImage` `models/campaign.py:444` | `GetImageDetails()` `models/campaign.py:470` |
| `RejectionRecord` | `class RejectionRecord` `models/campaign.py:569` | `DeleteCampaignRejectionRecords()` `models/campaign.py:599` |
| `CampaignStatus` | `class CampaignStatus` `models/campaign.py:663` | `SetPending()` `models/campaign.py:665`, `GetStatus()` `models/campaign.py:683`, and `GetStatusDetails()` `models/campaign.py:687` |
| `FundraisingCampaign` | `class FundraisingCampaign` `models/campaign.py:19` | `SubmitCampaign()` `models/campaign.py:383` and `UpdateCampaignStatus()` `models/campaign.py:424` |

## F9 View Approval Status of Campaign

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CampaignSubmissionPage` | `class CampaignSubmissionPage` `routers/fundraiser.py:645` | `AccessSubmissionStep()` `routers/fundraiser.py:649`, `ViewApprovalStatus()` `routers/fundraiser.py:701`, and `DisplayApprovalStatus()` `routers/fundraiser.py:705` |
| `CampaignApprovalController` | `class CampaignApprovalController` `services/campaign_service.py:937` | `RetrieveCampaignStatus()` `services/campaign_service.py:976` and `GetApprovalStatusDetails()` `services/campaign_service.py:983` |
| `CampaignDetailSerializer` | `class CampaignDetailSerializer` `services/campaign_service.py:561` | `SerializeCampaignDetail()` `services/campaign_service.py:563` |
| `CampaignStatus` | `class CampaignStatus` `models/campaign.py:663` | `GetStatusDetails()` `models/campaign.py:687` |
| `FundraisingCampaign` | `class FundraisingCampaign` `models/campaign.py:19` | `GetCampaignById()` `models/campaign.py:71` |

## F10 View Campaign Views

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CampaignAnalyticsPage` | `class CampaignAnalyticsPage` `routers/fundraiser.py:712` | `AccessCampaignAnalyticsPage()` `routers/fundraiser.py:716`, `ViewCampaignViews()` `routers/fundraiser.py:725`, and `ViewDetailedExposureData()` `routers/fundraiser.py:729` |
| `CampaignDetailSerializer` | `class CampaignDetailSerializer` `services/campaign_service.py:561` | `SerializeCampaignDetail()` `services/campaign_service.py:563` |
| `CampaignAnalyticsController` | `class CampaignAnalyticsController` `services/campaign_service.py:1079` | `GetViewCount()` `services/campaign_service.py:1097` and `GetDetailedExposureData()` `services/campaign_service.py:1101` |
| `CampaignAnalytics` | `class CampaignAnalytics` `models/campaign.py:702` | `GetViewCount()` `models/campaign.py:720` and `GetExposureDetails()` `models/campaign.py:725` |

## F11 View Campaign Shortlists

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CampaignAnalyticsPage` | `class CampaignAnalyticsPage` `routers/fundraiser.py:712` | `AccessCampaignAnalyticsPage()` `routers/fundraiser.py:716`, `ViewCampaignShortlists()` `routers/fundraiser.py:733`, and `ViewDetailedInterestData()` `routers/fundraiser.py:737` |
| `CampaignDetailSerializer` | `class CampaignDetailSerializer` `services/campaign_service.py:561` | `SerializeCampaignDetail()` `services/campaign_service.py:563` |
| `CampaignAnalyticsController` | `class CampaignAnalyticsController` `services/campaign_service.py:1079` | `GetShortlistCount()` `services/campaign_service.py:1121` and `GetDetailedInterestData()` `services/campaign_service.py:1125` |
| `CampaignAnalytics` | `class CampaignAnalytics` `models/campaign.py:702` | `GetShortlistCount()` `models/campaign.py:754` and `GetInterestDetails()` `models/campaign.py:760` |

## F12 View Completed Campaigns

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CampaignHistoryPage` | `class CampaignHistoryPage` `routers/fundraiser.py:741` | `AccessCampaignHistoryPage()` `routers/fundraiser.py:745`, `ViewCompletedCampaigns()` `routers/fundraiser.py:754`, and `ViewCompletedCampaignDetails()` `routers/fundraiser.py:768` |
| `CampaignHistoryController` | `class CampaignHistoryController` `services/campaign_service.py:1145` | `RetrieveCompletedCampaignList()` `services/campaign_service.py:1147` and `GetCompletedCampaignDetails()` `services/campaign_service.py:1161` |
| `CompletedCampaignRecord` | `class CompletedCampaignRecord` `models/campaign.py:766` | `GetCompletedCampaigns()` `models/campaign.py:768` and `GetCampaignById()` `models/campaign.py:784` |
| `CampaignDetailSerializer` | `class CampaignDetailSerializer` `services/campaign_service.py:561` | `SerializeCampaignDetail()` `services/campaign_service.py:563` |

## F13 Filter Campaigns Using Selectable Criteria

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CampaignAnalysisPage` | `class CampaignAnalysisPage` `routers/fundraiser.py:778` | `SelectFilterCriteria()` `routers/fundraiser.py:782`, `FilterCampaigns()` `routers/fundraiser.py:796`, `ViewFilteredCampaigns()` `routers/fundraiser.py:812`, and `DisplayFilteredCampaigns()` `routers/fundraiser.py:882` |
| `CampaignFilterController` | `class CampaignFilterController` `services/campaign_service.py:1181` | `FilterCampaigns()` `services/campaign_service.py:1183` and `RetrieveFilteredCampaignResults()` `services/campaign_service.py:1199` |
| `FundraisingCampaign` | `class FundraisingCampaign` `models/campaign.py:19` | `GetFilteredCampaigns()` `models/campaign.py:163` |
