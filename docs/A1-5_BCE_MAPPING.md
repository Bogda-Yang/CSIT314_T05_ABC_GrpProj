# A1-5 BCE Mapping

This file maps the current strict BCE-aligned implementation for the administrator campaign-review scope.

Scope note:

- The currently aligned strict scope is `A4-5`.
- `A1-3` remain unimplemented and are intentionally excluded from the strict mapping below.
- Administrator review has been isolated to the dedicated `/dashboard` boundary page.

## A4 Approve Fundraising Campaign

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `CampaignReviewPage` | [templates/dashboard.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/dashboard.html) | `ViewPendingCampaigns()`, `ReviewCampaignDetails()`, `ApproveCampaign()`, `DisplayApprovalResult()` |
| `CampaignApprovalController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetPendingCampaigns()`, `GetCampaignDetails()`, `ValidateCampaign()`, `ApproveCampaign()`, `PublishCampaign()` |
| `FundraisingCampaign` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetPendingCampaigns()`, `GetCampaignById()`, `UpdateCampaignStatus()`, `PublishCampaign()` |
| `CampaignStatus` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `SetApproved()`, `SetPublished()`, `GetStatus()` |

## A5 Reject Fundraising Campaign

| BCE Class | File | Methods / Implementation |
|---|---|---|
| `CampaignReviewPage` | [templates/dashboard.html](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/templates/dashboard.html) | `ViewPendingCampaigns()`, `ReviewCampaignDetails()`, `EnterRejectionReason()`, `RejectCampaign()`, `DisplayRejectionResult()` |
| `CampaignRejectionController` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetPendingCampaigns()`, `GetCampaignDetails()`, `ValidateCampaign()`, `RejectCampaign()`, `RecordRejectionReason()` |
| `FundraisingCampaign` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `GetPendingCampaigns()`, `GetCampaignById()`, `UpdateCampaignStatus()` |
| `RejectionRecord` | [main.py](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/main.py) | `SaveRejectionReason()`, `GetRejectionReason()` |

## Strict A4-5 Routes

| Route | Purpose |
|---|---|
| `GET /dashboard` | Show administrator review boundary page |
| `POST /projects/review/{campaign_id}/approve` | Approve and publish a pending fundraising campaign |
| `POST /projects/review/{campaign_id}/reject` | Reject a pending fundraising campaign and store a rejection reason |
