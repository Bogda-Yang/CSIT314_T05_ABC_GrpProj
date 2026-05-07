# D1-11 BCE Mapping

This version lists only real method/function definition lines.

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

| BCE Class | Method definitions |
|---|---|
| `CampaignSearchPage` | `projects_page()` `routers/donee.py:186` |
| `CampaignSearchController` | `SearchFundraisingCampaigns()` `services/donation_service.py:31`, `RetrieveMatchingCampaigns()` `services/donation_service.py:49` |
| `FundraisingCampaign` | `SearchCampaigns()` `models/campaign.py:101`, `GetMatchingCampaigns()` `models/campaign.py:119` |

## D2 Filter Campaigns Using Selectable Criteria

| BCE Class | Method definitions |
|---|---|
| `CampaignSearchPage` | `projects_page()` `routers/donee.py:186` |
| `CampaignFilterController` | `FilterCampaigns()` `services/donation_service.py:69`, `RetrieveFilteredCampaigns()` `services/donation_service.py:87` |
| `FundraisingCampaign` | `FilterCampaigns()` `models/campaign.py:145`, `GetFilteredCampaigns()` `models/campaign.py:163` |

## D3 View Campaign Details

| BCE Class | Method definitions |
|---|---|
| `CampaignDetailPage` | `projects_page()` `routers/donee.py:186` |
| `CampaignDetailController` | `RetrieveCampaignInformation()` `services/donation_service.py:107`, `GetCampaignDetails()` `services/donation_service.py:116` |
| `FundraisingCampaign` | `GetCampaignById()` `models/campaign.py:71`, `GetCampaignDetails()` `models/campaign.py:67` |

## D4 View Campaign Images

| BCE Class | Method definitions |
|---|---|
| `CampaignDetailPage` | `projects_page()` `routers/donee.py:186` |
| `CampaignImageController` | `RetrieveCampaignImages()` `services/donation_service.py:123`, `GetCampaignImages()` `services/donation_service.py:127` |
| `CampaignImage` | `GetCampaignImages()` `models/campaign.py:479`, `GetImageRecord()` `models/campaign.py:492` |

## D5 Save Campaigns to Favourite List

| BCE Class | Method definitions |
|---|---|
| `FavouriteListPage` | `projects_page()` `routers/donee.py:186`, `save_campaign_to_favourite_list()` `routers/donee.py:506` |
| `FavouriteController` | `SaveCampaignToFavouriteList()` `services/donation_service.py:133`, `AddCampaignToFavouriteList()` `services/donation_service.py:140` |
| `FavouriteCampaign` | `AddToFavourite()` `models/donation.py:249`, `SaveFavouriteRecord()` `models/donation.py:257` |

## D6 Remove Campaigns from Favourite List

| BCE Class | Method definitions |
|---|---|
| `FavouriteListPage` | `your_impact_page()` `routers/donee.py:341`, `remove_campaign_from_favourite_list()` `routers/donee.py:544` |
| `FavouriteController` | `RemoveCampaignFromFavouriteList()` `services/donation_service.py:153` |
| `FavouriteCampaign` | `RemoveFromFavourite()` `models/donation.py:271`, `DeleteFavouriteRecord()` `models/donation.py:277` |

## D7 View Favourite Campaigns

| BCE Class | Method definitions |
|---|---|
| `FavouriteListPage` | `your_impact_page()` `routers/donee.py:341`, `projects_page()` `routers/donee.py:186` |
| `FavouriteController` | `RetrieveFavouriteCampaigns()` `services/donation_service.py:163`, `GetFavouriteCampaignDetails()` `services/donation_service.py:167` |
| `FavouriteCampaign` | `GetFavouriteCampaigns()` `models/donation.py:281`, `GetFavouriteCampaignById()` `models/donation.py:297` |

## D8 View Donation History

| BCE Class | Method definitions |
|---|---|
| `DonationHistoryPage` | `your_impact_page()` `routers/donee.py:341` |
| `DonationHistoryController` | `RetrieveDonationRecords()` `services/donation_service.py:182`, `GetDonationDetails()` `services/donation_service.py:196` |
| `DonationRecord` | `GetDonationRecords()` `models/donation.py:45`, `GetDonationById()` `models/donation.py:54` |

## D9 Filter Donations by Category

| BCE Class | Method definitions |
|---|---|
| `DonationHistoryPage` | `your_impact_page()` `routers/donee.py:341` |
| `DonationFilterController` | `FilterDonationsByCategory()` `services/donation_service.py:218`, `RetrieveFilteredDonationRecords()` `services/donation_service.py:246` |
| `DonationRecord` | `FilterByCategory()` `models/donation.py:64`, `GetFilteredDonations()` `models/donation.py:92` |

## D10 Filter Donations by Date Period

| BCE Class | Method definitions |
|---|---|
| `DonationHistoryPage` | `your_impact_page()` `routers/donee.py:341` |
| `DonationFilterController` | `FilterDonationsByDatePeriod()` `services/donation_service.py:232`, `RetrieveFilteredDonationRecords()` `services/donation_service.py:246` |
| `DonationRecord` | `FilterByDatePeriod()` `models/donation.py:78`, `GetFilteredDonations()` `models/donation.py:92` |

## D11 View Campaign Progress

| BCE Class | Method definitions |
|---|---|
| `CampaignDetailPage` | `projects_page()` `routers/donee.py:186`, `support_campaign()` `routers/donee.py:447` |
| `CampaignProgressController` | `RetrieveCampaignProgressData()` `services/donation_service.py:262`, `GetCampaignProgress()` `services/donation_service.py:266` |
| `CampaignProgress` | `GetCampaignProgress()` `models/campaign.py:812`, `GetFundingStatusDetails()` `models/campaign.py:836` |
