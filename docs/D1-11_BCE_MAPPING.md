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
| `CampaignSearchPage` | `projects_page()` `routers/donee.py:98` |
| `CampaignSearchController` | `SearchFundraisingCampaigns()` `services/donation_service.py:26`, `RetrieveMatchingCampaigns()` `services/donation_service.py:40` |
| `FundraisingCampaign` | `SearchCampaigns()` `models/campaign.py:93`, `GetMatchingCampaigns()` `models/campaign.py:107` |

## D2 Filter Campaigns Using Selectable Criteria

| BCE Class | Method definitions |
|---|---|
| `CampaignSearchPage` | `projects_page()` `routers/donee.py:98` |
| `CampaignFilterController` | `FilterCampaigns()` `services/donation_service.py:56`, `RetrieveFilteredCampaigns()` `services/donation_service.py:70` |
| `FundraisingCampaign` | `FilterCampaigns()` `models/campaign.py:130`, `GetFilteredCampaigns()` `models/campaign.py:144` |

## D3 View Campaign Details

| BCE Class | Method definitions |
|---|---|
| `CampaignDetailPage` | `projects_page()` `routers/donee.py:98` |
| `CampaignDetailController` | `RetrieveCampaignInformation()` `services/donation_service.py:86`, `GetCampaignDetails()` `services/donation_service.py:95` |
| `FundraisingCampaign` | `GetCampaignById()` `models/campaign.py:70`, `GetCampaignDetails()` `models/campaign.py:66` |

## D4 View Campaign Images

| BCE Class | Method definitions |
|---|---|
| `CampaignDetailPage` | `projects_page()` `routers/donee.py:98` |
| `CampaignImageController` | `RetrieveCampaignImages()` `services/donation_service.py:102`, `GetCampaignImages()` `services/donation_service.py:106` |
| `CampaignImage` | `GetCampaignImages()` `models/campaign.py:413`, `GetImageRecord()` `models/campaign.py:426` |

## D5 Save Campaigns to Favourite List

| BCE Class | Method definitions |
|---|---|
| `FavouriteListPage` | `projects_page()` `routers/donee.py:98`, `save_campaign_to_favourite_list()` `routers/donee.py:326` |
| `FavouriteController` | `SaveCampaignToFavouriteList()` `services/donation_service.py:112`, `AddCampaignToFavouriteList()` `services/donation_service.py:119` |
| `FavouriteCampaign` | `AddToFavourite()` `models/donation.py:172`, `SaveFavouriteRecord()` `models/donation.py:180` |

## D6 Remove Campaigns from Favourite List

| BCE Class | Method definitions |
|---|---|
| `FavouriteListPage` | `your_impact_page()` `routers/donee.py:162`, `remove_campaign_from_favourite_list()` `routers/donee.py:364` |
| `FavouriteController` | `RemoveCampaignFromFavouriteList()` `services/donation_service.py:132` |
| `FavouriteCampaign` | `RemoveFromFavourite()` `models/donation.py:194`, `DeleteFavouriteRecord()` `models/donation.py:200` |

## D7 View Favourite Campaigns

| BCE Class | Method definitions |
|---|---|
| `FavouriteListPage` | `your_impact_page()` `routers/donee.py:162`, `projects_page()` `routers/donee.py:98` |
| `FavouriteController` | `RetrieveFavouriteCampaigns()` `services/donation_service.py:142`, `GetFavouriteCampaignDetails()` `services/donation_service.py:146` |
| `FavouriteCampaign` | `GetFavouriteCampaigns()` `models/donation.py:204`, `GetFavouriteCampaignById()` `models/donation.py:220` |

## D8 View Donation History

| BCE Class | Method definitions |
|---|---|
| `DonationHistoryPage` | `your_impact_page()` `routers/donee.py:162` |
| `DonationHistoryController` | `RetrieveDonationRecords()` `services/donation_service.py:161`, `GetDonationDetails()` `services/donation_service.py:175` |
| `DonationRecord` | `GetDonationRecords()` `models/donation.py:43`, `GetDonationById()` `models/donation.py:52` |

## D9 Filter Donations by Category

| BCE Class | Method definitions |
|---|---|
| `DonationHistoryPage` | `your_impact_page()` `routers/donee.py:162` |
| `DonationFilterController` | `FilterDonationsByCategory()` `services/donation_service.py:197`, `RetrieveFilteredDonationRecords()` `services/donation_service.py:225` |
| `DonationRecord` | `FilterByCategory()` `models/donation.py:62`, `GetFilteredDonations()` `models/donation.py:90` |

## D10 Filter Donations by Date Period

| BCE Class | Method definitions |
|---|---|
| `DonationHistoryPage` | `your_impact_page()` `routers/donee.py:162` |
| `DonationFilterController` | `FilterDonationsByDatePeriod()` `services/donation_service.py:211`, `RetrieveFilteredDonationRecords()` `services/donation_service.py:225` |
| `DonationRecord` | `FilterByDatePeriod()` `models/donation.py:76`, `GetFilteredDonations()` `models/donation.py:90` |

## D11 View Campaign Progress

| BCE Class | Method definitions |
|---|---|
| `CampaignDetailPage` | `projects_page()` `routers/donee.py:98`, `support_campaign()` `routers/donee.py:267` |
| `CampaignProgressController` | `RetrieveCampaignProgressData()` `services/donation_service.py:241`, `GetCampaignProgress()` `services/donation_service.py:245` |
| `CampaignProgress` | `GetCampaignProgress()` `models/campaign.py:735`, `GetFundingStatusDetails()` `models/campaign.py:759` |
