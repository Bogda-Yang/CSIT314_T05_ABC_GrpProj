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
| `CampaignApprovalController` | `ValidateSubmissionRequirements()` `services/campaign_service.py:613`, `SubmitCampaignForApproval()` `services/campaign_service.py:633`, `UpdateCampaignStatusToPending()` `services/campaign_service.py:645`, `RetrieveCampaignStatus()` `services/campaign_service.py:650`, `GetApprovalStatusDetails()` `services/campaign_service.py:657`, `GetPendingCampaigns()` `services/campaign_service.py:662`, `GetCampaignDetails()` `services/campaign_service.py:674`, `ValidateCampaign()` `services/campaign_service.py:678`, `ApproveCampaign()` `services/campaign_service.py:686`, `PublishCampaign()` `services/campaign_service.py:697` |
| `FundraisingCampaign` | `GetCampaignDetails()` `models/campaign.py:61`, `GetPendingCampaigns()` `models/campaign.py:120`, `UpdateCampaignStatus()` `models/campaign.py:156`, `PublishCampaign()` `models/campaign.py:162` |
| `CampaignStatus` | `SetApproved()` `models/campaign.py:339`, `SetPublished()` `models/campaign.py:345`, `GetStatus()` `models/campaign.py:351` |

## A5 Reject Fundraising Campaign

| BCE Class | Method definitions |
|---|---|
| `CampaignReviewPage` | `dashboard_page()` `routers/admin.py:29`, `reject_campaign()` `routers/admin.py:187` |
| `CampaignRejectionController` | `GetPendingCampaigns()` `services/campaign_service.py:704`, `GetCampaignDetails()` `services/campaign_service.py:716`, `ValidateCampaign()` `services/campaign_service.py:720`, `RejectCampaign()` `services/campaign_service.py:729`, `RecordRejectionReason()` `services/campaign_service.py:749` |
| `FundraisingCampaign` | `GetCampaignDetails()` `models/campaign.py:61`, `GetPendingCampaigns()` `models/campaign.py:120`, `UpdateCampaignStatus()` `models/campaign.py:156` |
| `RejectionRecord` | `SaveRejectionReason()` `models/campaign.py:248`, `GetRejectionReason()` `models/campaign.py:258` |
