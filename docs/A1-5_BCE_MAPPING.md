# A1-5 BCE Mapping

This version maps BCE methods to real implementation function definition lines.

Scope:

- `A1 View User Accounts`
- `A2 Deactivate Account`
- `A3 Delete Account`
- `A4 Approve Fundraising Campaign`
- `A5 Reject Fundraising Campaign`

## A1 View User Accounts

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `AdminDashboardPage` | `class AdminDashboardPage` `routers/admin.py:175` | `ViewUserAccounts()` `routers/admin.py:179`, `SearchUserAccounts()` `routers/admin.py:407`, `FilterUserAccounts()` `routers/admin.py:411`, and `ViewAccountDetails()` `routers/admin.py:415` |
| `UserAccountController` | `class UserAccountController` `services/admin_service.py:198` | `GetUserAccountList()` `services/admin_service.py:200`, `SearchAccounts()` `services/admin_service.py:204`, `GetAccountDetails()` `services/admin_service.py:212`, `GetFilteredAccountList()` `services/admin_service.py:225` |
| `UserAccount` | `class UserAccount` `models/user.py:12` | `GetAllAccounts()` `models/user.py:59`, `GetAccountById()` `models/user.py:64`, `SearchAccounts()` `models/user.py:68` |
| `UserActivityLog` | `class UserActivityLog` `models/user.py:398` | `GetUserActivity()` `models/user.py:421`, `GetLastLogin()` `models/user.py:433` |

## A2 Deactivate Account

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `AccountManagementPage` | `class AccountManagementPage` `routers/admin.py:423` | `SelectUserAccount()` `routers/admin.py:427`, `ReviewAccountDetails()` `routers/admin.py:431`, `ViewAccountStatus()` `routers/admin.py:435`, `ConfirmDeactivation()` `routers/admin.py:439`, and `DisplayDeactivationResult()` `routers/admin.py:456` |
| `UserAccountController` | `class UserAccountController` `services/admin_service.py:198` | `GetAccountDetails()` `services/admin_service.py:212` |
| `AccountStatusController` | `class AccountStatusController` `services/admin_service.py:238` | `DeactivateAccount()` `services/admin_service.py:247`, `UpdateAccountStatus()` `services/admin_service.py:263`, `ClearAccountSessions()` `services/admin_service.py:267` |
| `UserAccount` | `class UserAccount` `models/user.py:12` | `GetAccountById()` `models/user.py:64`, `UpdateStatus()` `models/user.py:94` |
| `AccountStatus` | `class AccountStatus` `models/user.py:450` | `SetInactive()` `models/user.py:452` |
| `UserActivityLog` | `class UserActivityLog` `models/user.py:398` | `RecordActivity()` `models/user.py:408` |
| `UserSession` | `class UserSession` `models/user.py:312` | `GetSessionsByUserId()` `models/user.py:342`, `DeleteSessionRecord()` `models/user.py:351` |
| `AuthenticationToken` | `class AuthenticationToken` `models/user.py:355` | `GetTokensBySessionKey()` `models/user.py:383`, `DeleteTokenRecord()` `models/user.py:394` |

## A3 Delete Account

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `AccountManagementPage` | `class AccountManagementPage` `routers/admin.py:423` | `SelectUserAccount()` `routers/admin.py:427`, `ReviewAccountDetails()` `routers/admin.py:431`, `ConfirmDeletion()` `routers/admin.py:469`, and `DisplayDeletionResult()` `routers/admin.py:486` |
| `UserAccountController` | `class UserAccountController` `services/admin_service.py:198` | `GetAccountDetails()` `services/admin_service.py:212` |
| `AccountRemovalController` | `class AccountRemovalController` `services/admin_service.py:278` | `GetAccountDetails()` `services/admin_service.py:280`, `DeleteAccount()` `services/admin_service.py:284`, `RemoveAccountRecord()` `services/admin_service.py:295` |
| `DeleteAccountController` | `class DeleteAccountController` `services/user_service.py:947` | `GetDeletedAccountPlaceholder()` `services/user_service.py:949`, `DeleteAccount()` `services/user_service.py:971`, `ClearOwnedCampaigns()` `services/user_service.py:998`, `AnonymizeUserDonations()` `services/user_service.py:1014`, `AnonymizeUserViewRecords()` `services/user_service.py:1020`, `ClearUserProfile()` `services/user_service.py:1024`, `ClearPasswordHistory()` `services/user_service.py:1034`, `ClearUserFavourites()` `services/user_service.py:1040`, `ClearUserSessions()` `services/user_service.py:1053`, `ClearVerificationRecords()` `services/user_service.py:1064` |
| `UserAccount` | `class UserAccount` `models/user.py:12` | `GetAccountById()` `models/user.py:64`, `GetUserByEmail()` `models/user.py:42`, `CreateUser()` `models/user.py:25`, `SaveUser()` `models/user.py:38`, `DeleteUser()` `models/user.py:102` |
| `FundraisingCampaign` | `class FundraisingCampaign` `models/campaign.py:19` | `MarkDeleted()` `models/campaign.py:330` |
| `CampaignImage` | `class CampaignImage` `models/campaign.py:444` | `DeleteImageRecords()` `models/campaign.py:483` |
| `RejectionRecord` | `class RejectionRecord` `models/campaign.py:569` | `DeleteCampaignRejectionRecords()` `models/campaign.py:599` |
| `DonationRecord` | `class DonationRecord` `models/donation.py:13` | `ReassignUserDonationRecords()` `models/donation.py:142` |
| `CampaignViewRecord` | `class CampaignViewRecord` `models/campaign.py:513` | `AnonymizeUserViewRecords()` `models/campaign.py:558` |
| `FavouriteCampaign` | `class FavouriteCampaign` `models/donation.py:235` | `DeleteCampaignFavouriteRecords()` `models/donation.py:356`, `DeleteUserFavouriteRecords()` `models/donation.py:352` |
| `UserProfile` | `class UserProfile` `models/user.py:146` | `GetProfileDetails()` `models/user.py:160`, `DeleteProfile()` `models/user.py:164` |
| `PasswordHistory` | `class PasswordHistory` `models/user.py:272` | `GetPasswordHistoryRecords()` `models/user.py:303`, `DeletePasswordHistoryRecord()` `models/user.py:308` |
| `UserSession` | `class UserSession` `models/user.py:312` | `GetSessionsByUserId()` `models/user.py:342`, `DeleteSessionRecord()` `models/user.py:351` |
| `AuthenticationToken` | `class AuthenticationToken` `models/user.py:355` | `GetTokensBySessionKey()` `models/user.py:383`, `DeleteTokenRecord()` `models/user.py:394` |
| `VerificationCode` | `class VerificationCode` `models/user.py:106` | `FindVerificationRecord()` `models/user.py:116`, `DeleteVerificationRecord()` `models/user.py:120` |
| `PasswordResetCode` | `class PasswordResetCode` `models/user.py:126` | `FindPasswordResetRecord()` `models/user.py:136`, `DeletePasswordResetRecord()` `models/user.py:140` |
| `UserActivityLog` | `class UserActivityLog` `models/user.py:398` | `DeleteUserActivity()` `models/user.py:446` |

## A4 Approve Fundraising Campaign

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CampaignReviewPage` | `class CampaignReviewPage` `routers/admin.py:499` | `ViewPendingCampaigns()` `routers/admin.py:503`, `ReviewCampaignDetails()` `routers/admin.py:515`, `ApproveCampaign()` `routers/admin.py:520`, and `DisplayApprovalResult()` `routers/admin.py:559` |
| `CampaignApprovalController` | `class CampaignApprovalController` `services/campaign_service.py:937` | `GetPendingCampaigns()` `services/campaign_service.py:988`, `RetrieveCampaignStatus()` `services/campaign_service.py:976`, `ValidateSubmissionRequirements()` `services/campaign_service.py:939`, `ValidateCampaign()` `services/campaign_service.py:1004`, `ApproveCampaign()` `services/campaign_service.py:1012`, `PublishCampaign()` `services/campaign_service.py:1023`, `GetApprovalStatusDetails()` `services/campaign_service.py:983` |
| `CampaignController` | `class CampaignController` `services/campaign_service.py:624` | `ValidateCampaignInformation()` `services/campaign_service.py:626` |
| `CampaignDescriptionController` | `class CampaignDescriptionController` `services/campaign_service.py:745` | `ValidateDescriptionContent()` `services/campaign_service.py:747` |
| `CampaignDeadlineController` | `class CampaignDeadlineController` `services/campaign_service.py:900` | `ValidateDeadline()` `services/campaign_service.py:902` |
| `FundraisingCampaign` | `class FundraisingCampaign` `models/campaign.py:19` | `GetPendingCampaigns()` `models/campaign.py:388`, `GetCampaignById()` `models/campaign.py:71`, `UpdateCampaignStatus()` `models/campaign.py:424`, `PublishCampaign()` `models/campaign.py:430` |
| `CampaignImage` | `class CampaignImage` `models/campaign.py:444` | `GetImageDetails()` `models/campaign.py:470` |
| `CampaignStatus` | `class CampaignStatus` `models/campaign.py:663` | `SetApproved()` `models/campaign.py:671`, `SetPublished()` `models/campaign.py:677`, `GetStatus()` `models/campaign.py:683`, `GetStatusDetails()` `models/campaign.py:687` |
| `RejectionRecord` | `class RejectionRecord` `models/campaign.py:569` | `DeleteCampaignRejectionRecords()` `models/campaign.py:599` |

## A5 Reject Fundraising Campaign

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CampaignReviewPage` | `class CampaignReviewPage` `routers/admin.py:499` | `ViewPendingCampaigns()` `routers/admin.py:503`, `ReviewCampaignDetails()` `routers/admin.py:515`, `EnterRejectionReason()` `routers/admin.py:578`, `RejectCampaign()` `routers/admin.py:588`, and `DisplayRejectionResult()` `routers/admin.py:629` |
| `CampaignApprovalController` | `class CampaignApprovalController` `services/campaign_service.py:937` | `GetPendingCampaigns()` `services/campaign_service.py:988` |
| `CampaignRejectionController` | `class CampaignRejectionController` `services/campaign_service.py:1028` | `ValidateCampaign()` `services/campaign_service.py:1046`, `RejectCampaign()` `services/campaign_service.py:1055`, `RecordRejectionReason()` `services/campaign_service.py:1075` |
| `FundraisingCampaign` | `class FundraisingCampaign` `models/campaign.py:19` | `GetPendingCampaigns()` `models/campaign.py:388`, `GetCampaignById()` `models/campaign.py:71` |
| `CampaignStatus` | `class CampaignStatus` `models/campaign.py:663` | `GetStatusDetails()` `models/campaign.py:687` |
| `RejectionRecord` | `class RejectionRecord` `models/campaign.py:569` | `SaveRejectionReason()` `models/campaign.py:580`, `GetRejectionReason()` `models/campaign.py:590` |
