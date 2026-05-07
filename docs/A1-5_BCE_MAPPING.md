# A1-5 BCE Mapping

This version lists only real method/function definition lines.

Scope:

- `A1 View User Accounts`
- `A2 Deactivate Account`
- `A3 Delete Account`
- `A4 Approve Fundraising Campaign`
- `A5 Reject Fundraising Campaign`

## A1 View User Accounts

| BCE Class | Method definitions |
|---|---|
| `AdminDashboardPage` | `ViewUserAccounts()`, `SearchUserAccounts()`, `FilterUserAccounts()`, and `ViewAccountDetails()` are handled by `dashboard_page()` `routers/admin.py:51` |
| `UserAccountController` | `GetUserAccountList()` `services/admin_service.py:200`, `SearchAccounts()` `services/admin_service.py:204`, `FilterAccounts()` `services/admin_service.py:208`, `GetAccountDetails()` `services/admin_service.py:212`, `GetFilteredAccountList()` `services/admin_service.py:225` |
| `UserAccount` | `GetAllAccounts()` `models/user.py:59`, `GetAccountById()` `models/user.py:64`, `SearchAccounts()` `models/user.py:68`, `FilterAccounts()` `models/user.py:86` |
| `UserActivityLog` | `GetUserActivity()` `models/user.py:372`, `GetLastLogin()` `models/user.py:384` |

## A2 Deactivate Account

| BCE Class | Method definitions |
|---|---|
| `AccountManagementPage` | `SelectUserAccount()` and `ViewAccountStatus()` are handled by `dashboard_page()` `routers/admin.py:51`; `ConfirmDeactivation()` and `DisplayDeactivationResult()` are handled by `deactivate_account()` `routers/admin.py:271` |
| `AccountStatusController` | `GetAccountStatus()` `services/admin_service.py:240`, `DeactivateAccount()` `services/admin_service.py:247`, `UpdateAccountStatus()` `services/admin_service.py:263`, `ClearAccountSessions()` `services/admin_service.py:267` |
| `UserAccount` | `GetAccountById()` `models/user.py:64`, `UpdateStatus()` `models/user.py:94` |
| `AccountStatus` | `SetInactive()` `models/user.py:403`, `GetStatus()` `models/user.py:407` |

## A3 Delete Account

| BCE Class | Method definitions |
|---|---|
| `AccountManagementPage` | `SelectUserAccount()` and `ReviewAccountDetails()` are handled by `dashboard_page()` `routers/admin.py:51`; `ConfirmDeletion()` and `DisplayDeletionResult()` are handled by `delete_account()` `routers/admin.py:295` |
| `AccountRemovalController` | `GetAccountDetails()` `services/admin_service.py:286`, `DeleteAccount()` `services/admin_service.py:290`, `RemoveAccountRecord()` `services/admin_service.py:301` |
| `UserAccount` | `GetAccountById()` `models/user.py:64`, `DeleteUser()` `models/user.py:102` |
| `UserProfile` | `DeleteProfile()` `models/user.py:144` |

## A4 Approve Fundraising Campaign

| BCE Class | Method definitions |
|---|---|
| `CampaignReviewPage` | `dashboard_page()` `routers/admin.py:51`, `approve_campaign()` `routers/admin.py:451` |
| `CampaignApprovalController` | `ValidateSubmissionRequirements()` `services/campaign_service.py:931`, `SubmitCampaignForApproval()` `services/campaign_service.py:951`, `UpdateCampaignStatusToPending()` `services/campaign_service.py:963`, `RetrieveCampaignStatus()` `services/campaign_service.py:968`, `GetApprovalStatusDetails()` `services/campaign_service.py:975`, `GetPendingCampaigns()` `services/campaign_service.py:980`, `GetCampaignDetails()` `services/campaign_service.py:992`, `ValidateCampaign()` `services/campaign_service.py:996`, `ApproveCampaign()` `services/campaign_service.py:1004`, `PublishCampaign()` `services/campaign_service.py:1015` |
| `FundraisingCampaign` | `GetCampaignDetails()` `models/campaign.py:67`, `GetPendingCampaigns()` `models/campaign.py:388`, `UpdateCampaignStatus()` `models/campaign.py:424`, `PublishCampaign()` `models/campaign.py:430` |
| `CampaignStatus` | `SetApproved()` `models/campaign.py:671`, `SetPublished()` `models/campaign.py:677`, `GetStatus()` `models/campaign.py:683` |

## A5 Reject Fundraising Campaign

| BCE Class | Method definitions |
|---|---|
| `CampaignReviewPage` | `dashboard_page()` `routers/admin.py:51`, `reject_campaign()` `routers/admin.py:495` |
| `CampaignRejectionController` | `GetPendingCampaigns()` `services/campaign_service.py:1022`, `GetCampaignDetails()` `services/campaign_service.py:1034`, `ValidateCampaign()` `services/campaign_service.py:1038`, `RejectCampaign()` `services/campaign_service.py:1047`, `RecordRejectionReason()` `services/campaign_service.py:1067` |
| `FundraisingCampaign` | `GetCampaignDetails()` `models/campaign.py:67`, `GetPendingCampaigns()` `models/campaign.py:388`, `UpdateCampaignStatus()` `models/campaign.py:424` |
| `RejectionRecord` | `SaveRejectionReason()` `models/campaign.py:580`, `GetRejectionReason()` `models/campaign.py:590` |
