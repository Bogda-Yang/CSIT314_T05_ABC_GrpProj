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
| `CampaignSearchPage` | `projects_page()` `routers/donee.py:165` |
| `CampaignSearchController` | `SearchFundraisingCampaigns()` `services/donation_service.py:30`, `RetrieveMatchingCampaigns()` `services/donation_service.py:44` |
| `FundraisingCampaign` | `SearchCampaigns()` `models/campaign.py:97`, `GetMatchingCampaigns()` `models/campaign.py:111` |

## D2 Filter Campaigns Using Selectable Criteria

| BCE Class | Method definitions |
|---|---|
| `CampaignSearchPage` | `projects_page()` `routers/donee.py:165` |
| `CampaignFilterController` | `FilterCampaigns()` `services/donation_service.py:60`, `RetrieveFilteredCampaigns()` `services/donation_service.py:74` |
| `FundraisingCampaign` | `FilterCampaigns()` `models/campaign.py:134`, `GetFilteredCampaigns()` `models/campaign.py:148` |

## D3 View Campaign Details

| BCE Class | Method definitions |
|---|---|
| `CampaignDetailPage` | `projects_page()` `routers/donee.py:165` |
| `CampaignDetailController` | `RetrieveCampaignInformation()` `services/donation_service.py:90`, `GetCampaignDetails()` `services/donation_service.py:99` |
| `FundraisingCampaign` | `GetCampaignById()` `models/campaign.py:71`, `GetCampaignDetails()` `models/campaign.py:67` |

## D4 View Campaign Images

| BCE Class | Method definitions |
|---|---|
| `CampaignDetailPage` | `projects_page()` `routers/donee.py:165` |
| `CampaignImageController` | `RetrieveCampaignImages()` `services/donation_service.py:106`, `GetCampaignImages()` `services/donation_service.py:110` |
| `CampaignImage` | `GetCampaignImages()` `models/campaign.py:429`, `GetImageRecord()` `models/campaign.py:442` |

## D5 Save Campaigns to Favourite List

| BCE Class | Method definitions |
|---|---|
| `FavouriteListPage` | `projects_page()` `routers/donee.py:165`, `save_campaign_to_favourite_list()` `routers/donee.py:428` |
| `FavouriteController` | `SaveCampaignToFavouriteList()` `services/donation_service.py:116`, `AddCampaignToFavouriteList()` `services/donation_service.py:123` |
| `FavouriteCampaign` | `AddToFavourite()` `models/donation.py:249`, `SaveFavouriteRecord()` `models/donation.py:257` |

## D6 Remove Campaigns from Favourite List

| BCE Class | Method definitions |
|---|---|
| `FavouriteListPage` | `your_impact_page()` `routers/donee.py:263`, `remove_campaign_from_favourite_list()` `routers/donee.py:466` |
| `FavouriteController` | `RemoveCampaignFromFavouriteList()` `services/donation_service.py:136` |
| `FavouriteCampaign` | `RemoveFromFavourite()` `models/donation.py:271`, `DeleteFavouriteRecord()` `models/donation.py:277` |

## D7 View Favourite Campaigns

| BCE Class | Method definitions |
|---|---|
| `FavouriteListPage` | `your_impact_page()` `routers/donee.py:263`, `projects_page()` `routers/donee.py:165` |
| `FavouriteController` | `RetrieveFavouriteCampaigns()` `services/donation_service.py:146`, `GetFavouriteCampaignDetails()` `services/donation_service.py:150` |
| `FavouriteCampaign` | `GetFavouriteCampaigns()` `models/donation.py:281`, `GetFavouriteCampaignById()` `models/donation.py:297` |

## D8 View Donation History

| BCE Class | Method definitions |
|---|---|
| `DonationHistoryPage` | `your_impact_page()` `routers/donee.py:263` |
| `DonationHistoryController` | `RetrieveDonationRecords()` `services/donation_service.py:165`, `GetDonationDetails()` `services/donation_service.py:179` |
| `DonationRecord` | `GetDonationRecords()` `models/donation.py:45`, `GetDonationById()` `models/donation.py:54` |

## D9 Filter Donations by Category

| BCE Class | Method definitions |
|---|---|
| `DonationHistoryPage` | `your_impact_page()` `routers/donee.py:263` |
| `DonationFilterController` | `FilterDonationsByCategory()` `services/donation_service.py:201`, `RetrieveFilteredDonationRecords()` `services/donation_service.py:229` |
| `DonationRecord` | `FilterByCategory()` `models/donation.py:64`, `GetFilteredDonations()` `models/donation.py:92` |

## D10 Filter Donations by Date Period

| BCE Class | Method definitions |
|---|---|
| `DonationHistoryPage` | `your_impact_page()` `routers/donee.py:263` |
| `DonationFilterController` | `FilterDonationsByDatePeriod()` `services/donation_service.py:215`, `RetrieveFilteredDonationRecords()` `services/donation_service.py:229` |
| `DonationRecord` | `FilterByDatePeriod()` `models/donation.py:78`, `GetFilteredDonations()` `models/donation.py:92` |

## D11 View Campaign Progress

| BCE Class | Method definitions |
|---|---|
| `CampaignDetailPage` | `projects_page()` `routers/donee.py:165`, `support_campaign()` `routers/donee.py:369` |
| `CampaignProgressController` | `RetrieveCampaignProgressData()` `services/donation_service.py:245`, `GetCampaignProgress()` `services/donation_service.py:249` |
| `CampaignProgress` | `GetCampaignProgress()` `models/campaign.py:762`, `GetFundingStatusDetails()` `models/campaign.py:786` |
