# D1-11 BCE Mapping

This file documents the BCE scope for the donor and donee interaction range `D1-11`.

Current implementation note:

- No `D1-11` donor-side campaign browsing, favourite list, or donation-history features are implemented in the current codebase.
- The classes and methods below are preserved from the BCE source so the mapping file exists for later implementation.

## Status Summary

| Range | Status | Notes |
|---|---|---|
| `D1-4` | Not implemented | Campaign search, filtering, detail, and image browsing are not implemented |
| `D5-7` | Not implemented | Favourite list features are not implemented |
| `D8-10` | Not implemented | Donation history and donation filters are not implemented |
| `D11` | Not implemented | Campaign progress view is not implemented as a donor-facing feature |

## D1 Search Fundraising Campaigns

| BCE Class | Source Methods | Current File Mapping | Status |
|---|---|---|---|
| `CampaignSearchPage` | `AccessCampaignSearchPage()`, `EnterSearchKeywords()`, `SubmitSearchRequest()`, `DisplaySearchResults()`, `ClearSearchInput()` | No campaign search page exists | Not implemented |
| `CampaignSearchController` | `SearchFundraisingCampaigns()`, `RetrieveMatchingCampaigns()` | No controller implementation exists | Not implemented |
| `FundraisingCampaign` | `SearchCampaigns()`, `GetMatchingCampaigns()` | No donor-side search entity behavior is implemented | Not implemented |

## D2 Filter Campaigns Using Selectable Criteria

| BCE Class | Source Methods | Current File Mapping | Status |
|---|---|---|---|
| `CampaignSearchPage` | `AccessCampaignSearchPage()`, `SelectFilterCriteria()`, `ApplyFilters()`, `DisplayFilteredResults()`, `ClearFilters()` | No campaign filter boundary page exists | Not implemented |
| `CampaignFilterController` | `FilterCampaigns()`, `RetrieveFilteredCampaigns()` | No controller implementation exists | Not implemented |
| `FundraisingCampaign` | `FilterCampaigns()`, `GetFilteredCampaigns()` | No donor-side filter entity behavior is implemented | Not implemented |

## D3 View Campaign Details

| BCE Class | Source Methods | Current File Mapping | Status |
|---|---|---|---|
| `CampaignDetailPage` | `AccessCampaignDetailPage()`, `SelectCampaign()`, `DisplayCampaignDetails()`, `ViewAdditionalInformation()` | No campaign detail page exists | Not implemented |
| `CampaignDetailController` | `RetrieveCampaignInformation()`, `GetCampaignDetails()` | No controller implementation exists | Not implemented |
| `FundraisingCampaign` | `GetCampaignById()`, `GetCampaignDetails()` | No donor-facing detail route exists | Not implemented |

## D4 View Campaign Images

| BCE Class | Source Methods | Current File Mapping | Status |
|---|---|---|---|
| `CampaignDetailPage` | `AccessCampaignDetailPage()`, `ViewCampaignImages()`, `DisplayCampaignImages()`, `ViewEnlargedImage()` | No campaign image gallery page exists | Not implemented |
| `CampaignImageController` | `RetrieveCampaignImages()`, `GetCampaignImages()` | No donor-side controller implementation exists | Not implemented |
| `CampaignImage` | `GetCampaignImages()`, `GetImageById()` | No donor-facing image retrieval flow exists | Not implemented |

## D5 Save Campaigns to Favourite List

| BCE Class | Source Methods | Current File Mapping | Status |
|---|---|---|---|
| `FavouriteListPage` | `AccessCampaignDetailPage()`, `SelectSaveToFavouriteOption()`, `DisplaySaveResult()` | No favourite list boundary page exists | Not implemented |
| `FavouriteController` | `SaveCampaignToFavouriteList()`, `AddCampaignToFavouriteList()` | No controller implementation exists | Not implemented |
| `FavouriteCampaign` | `AddToFavourite()`, `SaveFavouriteRecord()` | No entity implementation exists | Not implemented |

## D6 Remove Campaigns from Favourite List

| BCE Class | Source Methods | Current File Mapping | Status |
|---|---|---|---|
| `FavouriteListPage` | `AccessFavouriteListPage()`, `SelectSavedCampaign()`, `RemoveCampaignFromFavouriteList()`, `DisplayRemovalResult()`, `CancelRemoval()` | No favourite removal boundary page exists | Not implemented |
| `FavouriteController` | `RemoveCampaignFromFavouriteList()` | No controller implementation exists | Not implemented |
| `FavouriteCampaign` | `RemoveFromFavourite()`, `DeleteFavouriteRecord()` | No entity implementation exists | Not implemented |

## D7 View Favourite Campaigns

| BCE Class | Source Methods | Current File Mapping | Status |
|---|---|---|---|
| `FavouriteListPage` | `AccessFavouriteListPage()`, `ViewFavouriteCampaigns()`, `DisplayFavouriteCampaigns()`, `ViewFavouriteCampaignDetails()` | No favourite list view page exists | Not implemented |
| `FavouriteController` | `RetrieveFavouriteCampaigns()`, `GetFavouriteCampaignDetails()` | No controller implementation exists | Not implemented |
| `FavouriteCampaign` | `GetFavouriteCampaigns()`, `GetFavouriteCampaignById()` | No entity implementation exists | Not implemented |

## D8 View Donation History

| BCE Class | Source Methods | Current File Mapping | Status |
|---|---|---|---|
| `DonationHistoryPage` | `AccessDonationHistoryPage()`, `ViewDonationHistory()`, `DisplayDonationHistory()`, `ViewDonationDetails()` | No donation history page exists | Not implemented |
| `DonationHistoryController` | `RetrieveDonationRecords()`, `GetDonationDetails()` | No controller implementation exists | Not implemented |
| `DonationRecord` | `GetDonationRecords()`, `GetDonationById()` | No entity implementation exists | Not implemented |

## D9 Filter Donations by Category

| BCE Class | Source Methods | Current File Mapping | Status |
|---|---|---|---|
| `DonationHistoryPage` | `AccessDonationHistoryPage()`, `SelectDonationCategory()`, `ApplyCategoryFilter()`, `DisplayFilteredDonations()`, `ClearCategoryFilter()` | No donation category filter page exists | Not implemented |
| `DonationFilterController` | `FilterDonationsByCategory()`, `RetrieveFilteredDonationRecords()` | No controller implementation exists | Not implemented |
| `DonationRecord` | `FilterByCategory()`, `GetFilteredDonations()` | No entity implementation exists | Not implemented |

## D10 Filter Donations by Date Period

| BCE Class | Source Methods | Current File Mapping | Status |
|---|---|---|---|
| `DonationHistoryPage` | `AccessDonationHistoryPage()`, `SelectDatePeriod()`, `ApplyDateFilter()`, `DisplayFilteredDonations()`, `ClearDateFilter()` | No donation date filter page exists | Not implemented |
| `DonationFilterController` | `FilterDonationsByDatePeriod()`, `RetrieveFilteredDonationRecords()` | No controller implementation exists | Not implemented |
| `DonationRecord` | `FilterByDatePeriod()`, `GetFilteredDonations()` | No entity implementation exists | Not implemented |

## D11 View Campaign Progress

| BCE Class | Source Methods | Current File Mapping | Status |
|---|---|---|---|
| `CampaignDetailPage` | `AccessCampaignDetailPage()`, `ViewCampaignProgress()`, `DisplayCampaignProgress()`, `ViewFundingStatusDetails()` | No donor-facing campaign progress page exists | Not implemented |
| `CampaignProgressController` | `RetrieveCampaignProgressData()`, `GetCampaignProgress()` | No controller implementation exists | Not implemented |
| `CampaignProgress` | `GetCampaignProgress()`, `GetFundingStatusDetails()` | No entity implementation exists | Not implemented |
