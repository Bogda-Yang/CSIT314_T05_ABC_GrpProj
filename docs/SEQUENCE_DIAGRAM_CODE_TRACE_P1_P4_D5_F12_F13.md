# Sequence Diagram Code Trace: P1, P4, D5, F12, F13

This document maps the selected Sequence Diagram messages to the real code locations in the project. The purpose is to explain where each BCE sequence step appears in the implementation and to note where a diagram step is a route handler, UI action, return value, or inline logic rather than a separate method.

## P1 Create Category

### Code Trace

| Sequence step | Real code location | Notes |
|---|---|---|
| `create_category()` route entry | `routers/admin.py:102` | Real POST route for `/admin/categories/create`. |
| route calls `CategoryManagementPage.SubmitCategoryCreation()` | `routers/admin.py:108` | Transfers request handling to the Boundary class. |
| `AccessCategoryManagementPage()` | `routers/admin.py:652` | Opens the Admin Dashboard with the create-category modal. |
| `EnterCategoryDetails(name, description)` | `routers/admin.py:659` | Boundary method; calls validation before creation. |
| `SubmitCategoryCreation()` | `routers/admin.py:663` | Main Boundary method for P1. |
| `CategoryManagementPage.EnterCategoryDetails(...)` | `routers/admin.py:672` | Boundary-level validation call inside submit flow. |
| `CategoryController.CreateCategory(session, name, description)` | call: `routers/admin.py:673`; definition: `services/admin_service.py:321` | Boundary calls Controller to create the category. |
| `ValidateCategoryInformation(name, description)` | definition: `services/admin_service.py:301`; internal call: `services/admin_service.py:322` | Validates category name and description length, then returns cleaned values. |
| `Category.CreateCategory(clean_name, clean_description)` | definition: `models/admin.py:40`; call: `services/admin_service.py:323` | Entity creates the `Category` object. |
| `Category --> CategoryController : category` | `services/admin_service.py:323` | The created object is assigned to `category`. |
| `CategoryController.SaveCategory(session, category)` | definition: `services/admin_service.py:334`; call: `services/admin_service.py:324` | Controller wrapper for saving the category. |
| `Category.SaveCategory(session, category)` | definition: `models/admin.py:52`; call: `services/admin_service.py:335` | Entity method calls `session.add(category)`. |
| `saved` | `services/admin_service.py:326`, `services/admin_service.py:330` | `session.commit()` saves the row; `session.refresh(category)` refreshes it. |
| `creation success` | `services/admin_service.py:331` | Controller returns the created category. |
| `DisplayCreationResult()` success | call: `routers/admin.py:682`; definition: `routers/admin.py:685` | Boundary redirects back to dashboard with a success flash message. |
| `validation error` | `routers/admin.py:674` | `HTTPException` is caught by the Boundary submit method. |
| `DisplayCreationResult()` failure | `routers/admin.py:676` | Boundary redirects back with an error flash message. |
| duplicate category error | `services/admin_service.py:327` to `services/admin_service.py:329` | Database uniqueness conflict triggers rollback and returns HTTP 409. |

### Notes

- The Sequence Diagram flow is logically correct.
- The real code validates twice: first through `CategoryManagementPage.EnterCategoryDetails()` and again inside `CategoryController.CreateCategory()`.
- `create_category()` is a route handler, not a BCE class method. The BCE Boundary method is `CategoryManagementPage.SubmitCategoryCreation()`.

## P4 View All Categories

### Code Trace

| Sequence step | Real code location | Notes |
|---|---|---|
| `dashboard_page(category_q, category_status, category_id)` | `routers/admin.py:51` | Real GET route for the Admin Dashboard. |
| `category_q`, `category_status`, `category_id` parameters | `routers/admin.py:61` to `routers/admin.py:63` | Query parameters used by P4. |
| route calls `AdminDashboardPage.ViewUserAccounts(...)` | `routers/admin.py:71` | The dashboard method handles account, category, campaign-review, and report panels. |
| `AdminDashboardPage.ViewUserAccounts()` | `routers/admin.py:179` | Real dashboard page-loading method. |
| `CategoryManagementPage.AccessCategoryManagementPage()` | `routers/admin.py:652` | Exists, but only opens the create-category modal; it is not the real P4 list-loading method. |
| normalize category status | `services/admin_service.py:51`; used at `routers/admin.py:232` | Converts `"all"` to `None` and validates active/inactive status. |
| `CategoryManagementPage.ViewAllCategories(...)` | call: `routers/admin.py:234`; definition: `routers/admin.py:785` | Boundary method for loading the category list. |
| `CategoryController.GetCategoryList(session, search_keywords, status)` | call: `routers/admin.py:790`; definition: `services/admin_service.py:338` | Controller method for search, all-category loading, and status filtering. |
| `SearchCategories(session, search_keywords)` | definition: `services/admin_service.py:351`; call condition: `services/admin_service.py:342` | Used when search keywords exist. |
| `Category.SearchCategories(session, search_keywords)` | definition: `models/admin.py:77`; call: `services/admin_service.py:352` | Entity search query by name, description, or value. |
| `search results` | `models/admin.py:93` | Entity returns search results. |
| `Category.GetAllCategories(session)` | definition: `models/admin.py:72`; call: `services/admin_service.py:344` | Used when no search keyword is provided. |
| `all categories` | `models/admin.py:74` | Entity returns all category rows. |
| `filter categories by status in memory` | `services/admin_service.py:346` to `services/admin_service.py:347` | Inline list comprehension, not a separate method. |
| `category list` | `services/admin_service.py:348` | Controller returns the final list. |
| serialize category list | `routers/admin.py:239`; serializer: `services/admin_service.py:545` | Converts category objects into template payloads. |
| display categories | `routers/admin.py:391` | `serialized_categories` is passed to the template context. There is no separate `DisplayCategories()` method. |
| `category_id exists` | `routers/admin.py:241` | Optional detail flow begins when `category_id` is present. |
| `CategoryManagementPage.ViewCategoryDetails(session, category_id)` | call: `routers/admin.py:243`; definition: `routers/admin.py:805` | Boundary method for detail loading. |
| `CategoryController.GetCategoryDetails(session, category_id)` | definition: `services/admin_service.py:359`; call: `routers/admin.py:806` | Controller detail method. |
| `Category.GetCategoryById(session, category_id)` | definition: `models/admin.py:68`; call: `services/admin_service.py:360` | Entity lookup by category id. |
| `category record` | `models/admin.py:69` | Returns category object or `None`. |
| `Category.GetCategoryDetails(category)` | definition: `models/admin.py:56`; call: `services/admin_service.py:363` | Converts the category object into a detail dictionary. |
| `GetCategoryCampaignCount(session, category.value)` | definition: `services/admin_service.py:407`; call: `services/admin_service.py:364` | Counts campaigns using this category. |
| `category details` | `services/admin_service.py:365` | Controller returns category detail payload. |
| selected category passed to template | `routers/admin.py:392` | `selected_category_record` is included in template context. |

### Notes

- The real P4 entry is `dashboard_page()`, not `CategoryManagementPage.AccessCategoryManagementPage(category_q, category_status, category_id)`.
- `CategoryManagementPage.AccessCategoryManagementPage()` exists, but it is mainly for opening the create-category modal.
- The status filter is implemented inline in `CategoryController.GetCategoryList()`, not as a separate method call.
- There is no separate `DisplayCategories()` method; categories are serialized and placed into the dashboard template context.

## D5 Save Campaign to Favourite List

### Code Trace

| Sequence step | Real code location | Notes |
|---|---|---|
| `projects_page()` | `routers/donee.py:184` | `/projects` page entry. It calls `CampaignSearchPage.ViewCampaigns()`. |
| route calls `CampaignSearchPage.ViewCampaigns()` | `routers/donee.py:190` | The project list page is loaded before the favourite action. |
| `Select save to favourite option` | No separate backend method | This is a UI action: the user clicks the save/favourite button. |
| `save_campaign_to_favourite_list(campaign_id)` route | `routers/donee.py:337` | Real POST route for `/projects/{campaign_id}/favourites/save`. |
| route calls `FavouriteListPage.SaveCampaignToFavouriteList()` | `routers/donee.py:346` | Transfers the POST request to the Boundary class. |
| `FavouriteListPage.SaveCampaignToFavouriteList()` | `routers/donee.py:661` | Main Boundary method for D5. |
| `SelectFavouriteReturnLocation(category, q, sort)` | definition: `routers/donee.py:647`; call: `routers/donee.py:669` | Prepares return URL filters after the save action. |
| get authenticated Donee | `routers/donee.py:675` | Gets the current user and uses `user.id` as `donee_id`. |
| `FavouriteController.SaveCampaignToFavouriteList(donee_id, campaign_id)` | call: `routers/donee.py:678`; definition: `services/donation_service.py:133` | Boundary calls Controller to save favourite. |
| `CampaignDetailController.RetrieveCampaignInformation(campaign_id)` | definition: `services/donation_service.py:107`; call: `services/donation_service.py:136` | Verifies that the campaign exists and is published. |
| `FundraisingCampaign.GetCampaignById(campaign_id)` | definition: `models/campaign.py:71`; call: `services/donation_service.py:110` | Entity campaign lookup. |
| `published campaign record` | `services/donation_service.py:111` | Checks `campaign.status == "published"`. |
| return campaign to `FavouriteController` | `services/donation_service.py:113` | Returns the valid campaign object. |
| `AddCampaignToFavouriteList(donee_id, campaign_id)` | definition: `services/donation_service.py:140`; call: `services/donation_service.py:137` | Controller method for duplicate check and save. |
| `FavouriteCampaign.GetFavouriteRecord(donee_id, campaign_id)` | definition: `models/donation.py:261`; call: `services/donation_service.py:143` | Checks whether the favourite already exists. |
| `existing record or none` | `models/donation.py:268` | Entity returns existing record or `None`. |
| favourite already exists | `services/donation_service.py:144` to `services/donation_service.py:145` | Existing record is returned directly. |
| `FavouriteCampaign.AddToFavourite(donee_id, campaign_id)` | definition: `models/donation.py:249`; call: `services/donation_service.py:146` | Creates a new `FavouriteCampaign` object. |
| `favourite record` | `models/donation.py:250` | Returns the new object. |
| `FavouriteCampaign.SaveFavouriteRecord(record)` | definition: `models/donation.py:257`; call: `services/donation_service.py:147` | Entity adds the record to the session. |
| `save success` | `services/donation_service.py:148` to `services/donation_service.py:149` | `session.commit()` and `session.refresh(favourite_record)`. |
| return save success | `services/donation_service.py:150` | Controller returns the favourite record. |
| `DisplayFavouriteSaveResult()` | call: `routers/donee.py:680`; definition: `routers/donee.py:735` | Boundary sets a success flash message. |
| `RedirectAfterFavouriteChange()` | definition: `routers/donee.py:763`; call: `routers/donee.py:744` | Redirects back to projects, impact, or profile depending on `return_to`. |

### Notes

- `projects_page()` is a route handler, not a `FavouriteListPage` method.
- The favourite action really starts from `save_campaign_to_favourite_list()`.
- `Select save to favourite option` is a UI action, so it has no separate backend method.
- The duplicate favourite branch is handled by checking `existing_record` and returning it directly.

## F12 View Completed Campaigns

### Code Trace

| Sequence step | Real code location | Notes |
|---|---|---|
| `your_fundraisers_page()` | `routers/fundraiser.py:52` | `/your-fundraisers` route entry. |
| route calls `CampaignAnalysisPage.ViewFilteredCampaigns()` | `routers/fundraiser.py:58` | Real page method used by the route. |
| `CampaignHistoryPage.AccessCampaignHistoryPage()` | `routers/fundraiser.py:745` | Exists, but also forwards to `CampaignAnalysisPage.ViewFilteredCampaigns()`. |
| `CampaignHistoryPage.ViewCompletedCampaigns(...)` | call: `routers/fundraiser.py:839`; definition: `routers/fundraiser.py:754` | Boundary method that asks for completed campaigns. |
| `CampaignHistoryController.RetrieveCompletedCampaignList(session, owner_id, filters)` | call: `routers/fundraiser.py:760`; definition: `services/campaign_service.py:1147` | Controller method for the completed campaign list. |
| `CompletedCampaignRecord.GetCompletedCampaigns(session, owner_id, filters)` | definition: `models/campaign.py:768`; call: `services/campaign_service.py:1153` | Entity-like class for completed campaign retrieval. |
| `FundraisingCampaign.GetFilteredCampaigns(...)` | definition: `models/campaign.py:163`; call: `models/campaign.py:774` | Real filtering logic, called with `lifecycle="completed"`. |
| `lifecycle="completed"` | `models/campaign.py:778` | Restricts the result to completed campaigns. |
| `completed campaign list` | `models/campaign.py:781` | Returns the campaign list. |
| `CampaignDetailSerializer.SerializeCampaignDetail(completed_campaign)` | call: `routers/fundraiser.py:849`; definition: `services/campaign_service.py:563` | Serializes each completed campaign for template rendering. |
| `completed campaign detail payload` | `services/campaign_service.py:572` to `services/campaign_service.py:615` | Returns payload including title, status, progress, images, view count, and shortlist count. |
| `completed campaign data` | Controller return: `services/campaign_service.py:1153` to `services/campaign_service.py:1158`; Boundary receive: `routers/fundraiser.py:839` | Controller returns list; Boundary serializes it afterward. |

### Notes

- `your_fundraisers_page()` is a route handler, not a `CampaignHistoryPage` method.
- The route enters `CampaignAnalysisPage.ViewFilteredCampaigns()` first, then calls `CampaignHistoryPage.ViewCompletedCampaigns()`.
- The diagram name `serialize_campaign_detail(completed_campaign)` should be understood as the real class method `CampaignDetailSerializer.SerializeCampaignDetail(session, campaign)`.
- A lowercase wrapper `serialize_campaign_detail()` also exists at `services/campaign_service.py:618`, but F12 uses the class method directly.

## F13 Filter Campaigns Using Selectable Criteria

### Code Trace

| Sequence step | Real code location | Notes |
|---|---|---|
| `your_fundraisers_page(category, lifecycle, sort)` | `routers/fundraiser.py:52` | `/your-fundraisers` route receives filter query parameters. |
| route calls `CampaignAnalysisPage.ViewFilteredCampaigns(...)` | `routers/fundraiser.py:58` | Main Boundary entry for F13. |
| `Select filter criteria` | real method: `routers/fundraiser.py:782`; call: `routers/fundraiser.py:821` | Implemented as `CampaignAnalysisPage.SelectFilterCriteria(category, lifecycle, sort)`. |
| normalize category | `routers/fundraiser.py:787` to `routers/fundraiser.py:790` | Blank or `"all"` becomes `None`; otherwise category is normalized. |
| `normalize_fundraiser_lifecycle(lifecycle)` | definition: `services/campaign_service.py:1257`; call: `routers/fundraiser.py:791` | Invalid lifecycle returns `"all"`. |
| `normalize_fundraiser_campaign_sort(sort)` | definition: `services/campaign_service.py:1250`; call: `routers/fundraiser.py:792` | Invalid sort returns the default fundraiser sort. |
| `CampaignAnalysisPage.FilterCampaigns(...)` | definition: `routers/fundraiser.py:796`; call: `routers/fundraiser.py:832` | Boundary method that calls the Controller. |
| `RetrieveFilteredCampaignResults(session, owner_id, criteria)` | definition: `services/campaign_service.py:1199`; call: `routers/fundraiser.py:803` | Controller method for retrieving filtered campaigns. |
| `FundraisingCampaign.GetFilteredCampaigns(session, owner_id, criteria)` | definition: `models/campaign.py:163`; call: `services/campaign_service.py:1206` | Entity method for the actual filtering. |
| `GetCampaignsByOwner(session, owner_id)` | definition: `models/campaign.py:75`; call: `models/campaign.py:174` | Gets campaigns owned by the current Fund Raiser. |
| category filter | `models/campaign.py:175` to `models/campaign.py:176` | Filters campaigns by category if category is provided. |
| lifecycle filter | `models/campaign.py:186` to `models/campaign.py:191`; `MatchesLifecycle()` at `models/campaign.py:256` | Filters campaigns by lifecycle when lifecycle is not `"all"`. |
| sort filter | call: `models/campaign.py:192`; method: `models/campaign.py:262` | Sorts owner campaigns using `SortOwnerCampaigns()`. |
| `filtered campaign results` to Controller | `models/campaign.py:192` | Entity returns the filtered and sorted list. |
| `filtered campaign results` to Boundary | `services/campaign_service.py:1206` to `services/campaign_service.py:1211` | Controller returns Entity results. |
| `CampaignDetailSerializer.SerializeCampaignDetail(...)` | `routers/fundraiser.py:845` to `routers/fundraiser.py:848` | Serializes filtered campaigns for display. |
| `DisplayFilteredCampaigns()` | call: `routers/fundraiser.py:866`; definition: `routers/fundraiser.py:882` | Renders `your_fundraisers.html` with selected filters and campaign results. |
| `Clear filter controls` | No separate backend method | Implemented by requesting the page with default query values. |
| default clear-filter values | `routers/fundraiser.py:54` to `routers/fundraiser.py:56` | Defaults are `category=None`, `lifecycle="all"`, `sort="updated_desc"`. |
| unfiltered fundraiser campaigns | same flow through `ViewFilteredCampaigns()` | With default values, `GetFilteredCampaigns()` returns the owner's campaigns without category/lifecycle filtering. |

### Notes

- The F13 diagram is logically correct.
- `Select filter criteria` should be written as `SelectFilterCriteria(category, lifecycle, sort)` if the diagram needs exact method names.
- `Clear filter controls` is a front-end or URL-parameter behavior, not a separate BCE method.
- The back-end implementation of clearing filters is to rerun `ViewFilteredCampaigns(None, "all", "updated_desc")`.

## Recommended Diagram Adjustments

If the diagrams need to be strict about real method names, these replacements are safer:

| Current diagram wording | More code-accurate wording |
|---|---|
| `P4: AccessCategoryManagementPage(category_q, category_status, category_id)` | `dashboard_page(category_q, category_status, category_id)` or `ViewAllCategories(search_keywords, status)` |
| `P4: Display categories` | `serialize_category_summaries()` and template context `"categories"` |
| `D5: Select save to favourite option` | UI action that submits to `save_campaign_to_favourite_list(campaign_id)` |
| `F12: serialize_campaign_detail(completed_campaign)` | `CampaignDetailSerializer.SerializeCampaignDetail(session, campaign)` |
| `F13: Select filter criteria` | `SelectFilterCriteria(category, lifecycle, sort)` |
| `F13: Clear filter controls` | `ViewFilteredCampaigns(None, "all", "updated_desc")` |
