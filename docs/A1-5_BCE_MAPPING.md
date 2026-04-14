# A1-5 BCE Mapping

This document lists only the currently implemented administrator review methods.

Scope:

- `A4 Approve Fundraising Campaign`
- `A5 Reject Fundraising Campaign`

`A1-3` are intentionally excluded because they are not part of the current implemented scope.

## A4 Approve Fundraising Campaign

| BCE Class | File / Line | Methods / Line |
|---|---|---|
| `CampaignReviewPage` | `templates/dashboard.html:114-166`, `templates/dashboard.html:169-190`, `templates/dashboard.html:226-283` | `ViewPendingCampaigns()`, `ReviewCampaignDetails()`, `ApproveCampaign()`, `DisplayApprovalResult()` |
| `CampaignApprovalController` | `main.py:2376-2475` | `ValidateSubmissionRequirements()` `main.py:2376`, `SubmitCampaignForApproval()` `main.py:2397`, `UpdateCampaignStatusToPending()` `main.py:2410`, `RetrieveCampaignStatus()` `main.py:2416`, `GetApprovalStatusDetails()` `main.py:2424`, `GetPendingCampaigns()` `main.py:2430`, `GetCampaignDetails()` `main.py:2443`, `ValidateCampaign()` `main.py:2448`, `ApproveCampaign()` `main.py:2457`, `PublishCampaign()` `main.py:2469` |
| `FundraisingCampaign` | `main.py:419-526` | `GetCampaignDetails()` `main.py:419`, `GetPendingCampaigns()` `main.py:478`, `UpdateCampaignStatus()` `main.py:514`, `PublishCampaign()` `main.py:520` |
| `CampaignStatus` | `main.py:699-727` | `SetApproved()` `main.py:705`, `SetPublished()` `main.py:711`, `GetStatus()` `main.py:717` |

## A5 Reject Fundraising Campaign

| BCE Class | File / Line | Methods / Line |
|---|---|---|
| `CampaignReviewPage` | `templates/dashboard.html:114-166`, `templates/dashboard.html:193-221`, `templates/dashboard.html:226-283` | `ViewPendingCampaigns()`, `ReviewCampaignDetails()`, `EnterRejectionReason()`, `RejectCampaign()`, `DisplayRejectionResult()` |
| `CampaignRejectionController` | `main.py:2478-2530` | `GetPendingCampaigns()` `main.py:2478`, `GetCampaignDetails()` `main.py:2491`, `ValidateCampaign()` `main.py:2496`, `RejectCampaign()` `main.py:2506`, `RecordRejectionReason()` `main.py:2527` |
| `FundraisingCampaign` | `main.py:419-514` | `GetCampaignDetails()` `main.py:419`, `GetPendingCampaigns()` `main.py:478`, `UpdateCampaignStatus()` `main.py:514` |
| `RejectionRecord` | `main.py:610-620` | `SaveRejectionReason()` `main.py:610`, `GetRejectionReason()` `main.py:620` |

## A4-5 Routes

| Route | File / Line | Purpose |
|---|---|---|
| `GET /dashboard` | `main.py:2974-3086` | Show administrator review boundary page |
| `POST /projects/review/{campaign_id}/approve` | `main.py:3355-3397` | Approve and publish a pending fundraising campaign |
| `POST /projects/review/{campaign_id}/reject` | `main.py:3399-3441` | Reject a pending fundraising campaign and store a rejection reason |
