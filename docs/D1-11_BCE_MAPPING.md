# D1-11 BCE Mapping

This version maps each BCE class and method to the real implementation definition lines.

Scope:

- `D1 Search Fundraising Campaigns`
- `D2 Filter Campaigns Using Selectable Criteria`
- `D3 View Campaign Details`
- `D4 View Campaign Images`
- `D5 Save Campaigns to Favourite List`
- `D6 Remove Campaigns from Favourite List`
- `D7 View Favourite Campaigns`
- `D8 View Donation History`
- `D9 Filter Donations by Category`
- `D10 Filter Donations by Date Period`
- `D11 View Campaign Progress`

## D1 Search Fundraising Campaigns

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CampaignSearchPage` | `class CampaignSearchPage` `routers/donee.py:365` | `SelectSearchCriteria()` `routers/donee.py:369`, `SearchFundraisingCampaigns()` `routers/donee.py:377`, `ViewCampaigns()` `routers/donee.py:416`, `LoadMoreCampaigns()` `routers/donee.py:489`, `DisplayCampaignResults()` `routers/donee.py:548`, and `DisplayCampaignBatch()` `routers/donee.py:589` |
| `CampaignSearchController` | `class CampaignSearchController` `services/donation_service.py:29` | `SearchFundraisingCampaigns()` `services/donation_service.py:31` and `RetrieveMatchingCampaigns()` `services/donation_service.py:49` |
| `CampaignSummaryService` | `class CampaignSummaryService` `services/donation_service.py:973` | `GetPublishedCampaignSummaries()` `services/donation_service.py:975` and `GetPublishedCampaignCount()` `services/donation_service.py:995` |
| `FundraisingCampaign` | `class FundraisingCampaign` `models/campaign.py:19` | `GetMatchingCampaigns()` `models/campaign.py:119` and `CountDoneeCampaigns()` `models/campaign.py:212` |

## D2 Filter Campaigns Using Selectable Criteria

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CampaignSearchPage` | `class CampaignSearchPage` `routers/donee.py:365` | `SelectSearchCriteria()` `routers/donee.py:369`, `FilterCampaigns()` `routers/donee.py:397`, `ViewCampaigns()` `routers/donee.py:416`, `LoadMoreCampaigns()` `routers/donee.py:489`, `DisplayCampaignResults()` `routers/donee.py:548`, and `DisplayCampaignBatch()` `routers/donee.py:589` |
| `CampaignFilterController` | `class CampaignFilterController` `services/donation_service.py:67` | `FilterCampaigns()` `services/donation_service.py:69` and `RetrieveFilteredCampaigns()` `services/donation_service.py:87` |
| `CampaignSummaryService` | `class CampaignSummaryService` `services/donation_service.py:973` | `GetPublishedCampaignSummaries()` `services/donation_service.py:975` and `GetPublishedCampaignCount()` `services/donation_service.py:995` |
| `FundraisingCampaign` | `class FundraisingCampaign` `models/campaign.py:19` | `GetFilteredCampaigns()` `models/campaign.py:163` and `CountDoneeCampaigns()` `models/campaign.py:212` |

## D3 View Campaign Details

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CampaignDetailPage` | `class CampaignDetailPage` `routers/donee.py:614` | `ViewCampaignDetails()` `routers/donee.py:618` and `RenderCampaignCards()` `routers/donee.py:636` |
| `CampaignSummaryService` | `class CampaignSummaryService` `services/donation_service.py:973` | `GetPublishedCampaignSummaries()` `services/donation_service.py:975`, `SerializeCampaignSummary()` `services/donation_service.py:1003`, `SerializeCampaignSummaries()` `services/donation_service.py:1009`, and `BuildCampaignSummaryPayload()` `services/donation_service.py:1015` |
| `CampaignDetailController` | `class CampaignDetailController` `services/donation_service.py:105` | `RetrieveCampaignInformation()` `services/donation_service.py:107` and `GetCampaignDetails()` `services/donation_service.py:116` |
| `FundraisingCampaign` | `class FundraisingCampaign` `models/campaign.py:19` | `GetCampaignById()` `models/campaign.py:71`, `GetMatchingCampaigns()` `models/campaign.py:119`, and `GetFilteredCampaigns()` `models/campaign.py:163` |
| `UserAccount` | `class UserAccount` `models/user.py:12` | `GetUserAccount()` `models/user.py:55` |

## D4 View Campaign Images

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CampaignDetailPage` | `class CampaignDetailPage` `routers/donee.py:614` | `ViewCampaignImages()` `routers/donee.py:624` and `RenderCampaignCards()` `routers/donee.py:636` |
| `CampaignImageController` | `class CampaignImageController` `services/donation_service.py:121` | `RetrieveCampaignImages()` `services/donation_service.py:123` and `GetCampaignImages()` `services/donation_service.py:127` |
| `CampaignSummaryService` | `class CampaignSummaryService` `services/donation_service.py:973` | `GetPublishedCampaignSummaries()` `services/donation_service.py:975`, `SerializeCampaignSummaries()` `services/donation_service.py:1009`, and `BuildCampaignImageUrls()` `services/donation_service.py:1031` |
| `CampaignImage` | `class CampaignImage` `models/campaign.py:444` | `GetImageDetails()` `models/campaign.py:470` and `GetCampaignImages()` `models/campaign.py:479` |

## D5 Save Campaigns to Favourite List

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `FavouriteListPage` | `class FavouriteListPage` `routers/donee.py:643` | `SelectFavouriteReturnLocation()` `routers/donee.py:647`, `SaveCampaignToFavouriteList()` `routers/donee.py:661`, `DisplayFavouriteSaveResult()` `routers/donee.py:735`, and `RedirectAfterFavouriteChange()` `routers/donee.py:763` |
| `FavouriteController` | `class FavouriteController` `services/donation_service.py:131` | `SaveCampaignToFavouriteList()` `services/donation_service.py:133` and `AddCampaignToFavouriteList()` `services/donation_service.py:140` |
| `CampaignDetailController` | `class CampaignDetailController` `services/donation_service.py:105` | `RetrieveCampaignInformation()` `services/donation_service.py:107` |
| `FundraisingCampaign` | `class FundraisingCampaign` `models/campaign.py:19` | `GetCampaignById()` `models/campaign.py:71` |
| `FavouriteCampaign` | `class FavouriteCampaign` `models/donation.py:235` | `GetFavouriteRecord()` `models/donation.py:261`, `AddToFavourite()` `models/donation.py:249`, and `SaveFavouriteRecord()` `models/donation.py:257` |

## D6 Remove Campaigns from Favourite List

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `FavouriteListPage` | `class FavouriteListPage` `routers/donee.py:643` | `SelectFavouriteReturnLocation()` `routers/donee.py:647`, `RemoveCampaignFromFavouriteList()` `routers/donee.py:690`, `DisplayFavouriteRemovalResult()` `routers/donee.py:749`, and `RedirectAfterFavouriteChange()` `routers/donee.py:763` |
| `FavouriteController` | `class FavouriteController` `services/donation_service.py:131` | `RemoveCampaignFromFavouriteList()` `services/donation_service.py:153` |
| `FavouriteCampaign` | `class FavouriteCampaign` `models/donation.py:235` | `RemoveFromFavourite()` `models/donation.py:271`, `GetFavouriteRecord()` `models/donation.py:261`, and `DeleteFavouriteRecord()` `models/donation.py:277` |

## D7 View Favourite Campaigns

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `FavouriteListPage` | `class FavouriteListPage` `routers/donee.py:643` | `ViewFavouriteCampaigns()` `routers/donee.py:719` and `SerializeFavouriteCampaigns()` `routers/donee.py:723` |
| `FavouriteController` | `class FavouriteController` `services/donation_service.py:131` | `RetrieveFavouriteCampaigns()` `services/donation_service.py:163`, `GetFavouriteCampaignDetails()` `services/donation_service.py:167`, and `GetFavouriteCampaignIds()` `services/donation_service.py:176` |
| `FavouriteCampaign` | `class FavouriteCampaign` `models/donation.py:235` | `GetFavouriteCampaigns()` `models/donation.py:281` |
| `CampaignSummaryService` | `class CampaignSummaryService` `services/donation_service.py:973` | `SerializeCampaignSummary()` `services/donation_service.py:1003` |

## D8 View Donation History

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `DonationHistoryPage` | `class DonationHistoryPage` `routers/donee.py:784` | `SelectDonationFilters()` `routers/donee.py:788`, `RetrieveDonationRecords()` `routers/donee.py:800`, `ViewDonationHistory()` `routers/donee.py:832`, and `DisplayDonationHistory()` `routers/donee.py:898` |
| `DonationHistoryController` | `class DonationHistoryController` `services/donation_service.py:180` | `RetrieveDonationRecords()` `services/donation_service.py:182` and `GetDonationDetails()` `services/donation_service.py:196` |
| `DonationFilterController` | `class DonationFilterController` `services/donation_service.py:216` | `RetrieveFilteredDonationRecords()` `services/donation_service.py:246` |
| `DonationRecord` | `class DonationRecord` `models/donation.py:13` | `GetFilteredDonations()` `models/donation.py:92` |
| `DonationRecordSerializer` | `class DonationRecordSerializer` `services/donation_service.py:1043` | `SerializeDonationRecord()` `services/donation_service.py:1045` |
| `FundraisingCampaign` | `class FundraisingCampaign` `models/campaign.py:19` | `GetCampaignById()` `models/campaign.py:71` |
| `CampaignProgressController` | `class CampaignProgressController` `services/donation_service.py:260` | `GetCampaignProgress()` `services/donation_service.py:266` |
| `CampaignProgress` | `class CampaignProgress` `models/campaign.py:810` | `GetFundingStatusDetails()` `models/campaign.py:836` |

## D9 Filter Donations by Category

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `DonationHistoryPage` | `class DonationHistoryPage` `routers/donee.py:784` | `SelectDonationFilters()` `routers/donee.py:788`, `FilterDonationsByCategory()` `routers/donee.py:804`, `ViewDonationHistory()` `routers/donee.py:832`, and `DisplayDonationHistory()` `routers/donee.py:898` |
| `DonationFilterController` | `class DonationFilterController` `services/donation_service.py:216` | `FilterDonationsByCategory()` `services/donation_service.py:218` and `RetrieveFilteredDonationRecords()` `services/donation_service.py:246` |
| `DonationRecord` | `class DonationRecord` `models/donation.py:13` | `FilterByCategory()` `models/donation.py:64` and `GetFilteredDonations()` `models/donation.py:92` |
| `DonationRecordSerializer` | `class DonationRecordSerializer` `services/donation_service.py:1043` | `SerializeDonationRecord()` `services/donation_service.py:1045` |

## D10 Filter Donations by Date Period

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `DonationHistoryPage` | `class DonationHistoryPage` `routers/donee.py:784` | `SelectDonationFilters()` `routers/donee.py:788`, `FilterDonationsByDatePeriod()` `routers/donee.py:818`, `ViewDonationHistory()` `routers/donee.py:832`, and `DisplayDonationHistory()` `routers/donee.py:898` |
| `DonationFilterController` | `class DonationFilterController` `services/donation_service.py:216` | `FilterDonationsByDatePeriod()` `services/donation_service.py:232` and `RetrieveFilteredDonationRecords()` `services/donation_service.py:246` |
| `DonationRecord` | `class DonationRecord` `models/donation.py:13` | `FilterByDatePeriod()` `models/donation.py:78` and `GetFilteredDonations()` `models/donation.py:92` |
| `DonationRecordSerializer` | `class DonationRecordSerializer` `services/donation_service.py:1043` | `SerializeDonationRecord()` `services/donation_service.py:1045` |

## D11 View Campaign Progress

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CampaignDetailPage` | `class CampaignDetailPage` `routers/donee.py:614` | `ViewCampaignProgress()` `routers/donee.py:628` and `RetrieveCampaignProgressData()` `routers/donee.py:632` |
| `CampaignSummaryService` | `class CampaignSummaryService` `services/donation_service.py:973` | `BuildCampaignProgressPayload()` `services/donation_service.py:1037` |
| `CampaignProgressController` | `class CampaignProgressController` `services/donation_service.py:260` | `RetrieveCampaignProgressData()` `services/donation_service.py:262` and `GetCampaignProgress()` `services/donation_service.py:266` |
| `CampaignProgress` | `class CampaignProgress` `models/campaign.py:810` | `GetCampaignProgress()` `models/campaign.py:812` and `GetFundingStatusDetails()` `models/campaign.py:836` |
| `FundraisingCampaign` | `class FundraisingCampaign` `models/campaign.py:19` | `IsCompleted()` `models/campaign.py:245` |
