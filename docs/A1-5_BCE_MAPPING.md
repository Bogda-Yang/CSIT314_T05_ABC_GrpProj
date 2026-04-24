# A1-5 BCE Mapping

This version lists only real method/function definition lines.

Scope:

- `A4 Approve Fundraising Campaign`
- `A5 Reject Fundraising Campaign`

`A1-3` are intentionally excluded because they are not part of the current implemented scope.

## A4 Approve Fundraising Campaign

| BCE Class | Method definitions |
|---|---|
| `CampaignReviewPage` | `dashboard_page()` `routers/admin.py:29`, `approve_campaign()` `routers/admin.py:143` |
| `CampaignApprovalController` | `ValidateSubmissionRequirements()` `services/campaign_service.py:690`, `SubmitCampaignForApproval()` `services/campaign_service.py:710`, `UpdateCampaignStatusToPending()` `services/campaign_service.py:722`, `RetrieveCampaignStatus()` `services/campaign_service.py:727`, `GetApprovalStatusDetails()` `services/campaign_service.py:734`, `GetPendingCampaigns()` `services/campaign_service.py:739`, `GetCampaignDetails()` `services/campaign_service.py:751`, `ValidateCampaign()` `services/campaign_service.py:755`, `ApproveCampaign()` `services/campaign_service.py:763`, `PublishCampaign()` `services/campaign_service.py:774` |
| `FundraisingCampaign` | `GetCampaignDetails()` `models/campaign.py:66`, `GetPendingCampaigns()` `models/campaign.py:322`, `UpdateCampaignStatus()` `models/campaign.py:358`, `PublishCampaign()` `models/campaign.py:364` |
| `CampaignStatus` | `SetApproved()` `models/campaign.py:594`, `SetPublished()` `models/campaign.py:600`, `GetStatus()` `models/campaign.py:606` |

## A5 Reject Fundraising Campaign

| BCE Class | Method definitions |
|---|---|
| `CampaignReviewPage` | `dashboard_page()` `routers/admin.py:29`, `reject_campaign()` `routers/admin.py:187` |
| `CampaignRejectionController` | `GetPendingCampaigns()` `services/campaign_service.py:781`, `GetCampaignDetails()` `services/campaign_service.py:793`, `ValidateCampaign()` `services/campaign_service.py:797`, `RejectCampaign()` `services/campaign_service.py:806`, `RecordRejectionReason()` `services/campaign_service.py:826` |
| `FundraisingCampaign` | `GetCampaignDetails()` `models/campaign.py:66`, `GetPendingCampaigns()` `models/campaign.py:322`, `UpdateCampaignStatus()` `models/campaign.py:358` |
| `RejectionRecord` | `SaveRejectionReason()` `models/campaign.py:503`, `GetRejectionReason()` `models/campaign.py:513` |
