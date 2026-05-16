# Sequence Diagram 代码位置对照：P1、P4、D5、F12、F13

这份文档是 `SEQUENCE_DIAGRAM_CODE_TRACE_P1_P4_D5_F12_F13.md` 的中文对照版。原英文版保持不变。本文件用于说明五个选定 Sequence Diagram 中的每一步，在真实代码中分别对应哪个文件、哪一行，以及哪些步骤属于 route handler、UI 操作、返回值或代码块逻辑，而不是独立方法。

## P1 Create Category

### 代码位置对照表

| Sequence Diagram 步骤 | 真实代码位置 | 中文说明 |
|---|---|---|
| `create_category()` route entry | `routers/admin.py:102` | `/admin/categories/create` 的真实 POST route 入口。 |
| route calls `CategoryManagementPage.SubmitCategoryCreation()` | `routers/admin.py:108` | route handler 把请求交给 Boundary class 处理。 |
| `AccessCategoryManagementPage()` | `routers/admin.py:652` | 打开 Admin Dashboard，并显示 create-category modal。 |
| `EnterCategoryDetails(name, description)` | `routers/admin.py:659` | Boundary 方法，先调用 Controller 做 category 信息验证。 |
| `SubmitCategoryCreation()` | `routers/admin.py:663` | P1 创建 category 的主要 Boundary 提交流程。 |
| `CategoryManagementPage.EnterCategoryDetails(...)` | `routers/admin.py:672` | 在提交流程中先执行 Boundary 层验证。 |
| `CategoryController.CreateCategory(session, name, description)` | 调用：`routers/admin.py:673`；定义：`services/admin_service.py:321` | Boundary 调用 Controller 创建 category。 |
| `ValidateCategoryInformation(name, description)` | 定义：`services/admin_service.py:301`；内部调用：`services/admin_service.py:322` | 验证 category name 和 description 长度，并返回清理后的值。 |
| `Category.CreateCategory(clean_name, clean_description)` | 定义：`models/admin.py:40`；调用：`services/admin_service.py:323` | Entity 创建 `Category` object。 |
| `Category --> CategoryController : category` | `services/admin_service.py:323` | `Category.CreateCategory(...)` 返回的对象被赋值给 `category`。 |
| `CategoryController.SaveCategory(session, category)` | 定义：`services/admin_service.py:334`；调用：`services/admin_service.py:324` | Controller 层保存 category 的 wrapper 方法。 |
| `Category.SaveCategory(session, category)` | 定义：`models/admin.py:52`；调用：`services/admin_service.py:335` | Entity 方法执行 `session.add(category)`。 |
| `saved` | `services/admin_service.py:326`, `services/admin_service.py:330` | `session.commit()` 保存数据库记录，`session.refresh(category)` 刷新对象。 |
| `creation success` | `services/admin_service.py:331` | Controller 返回创建好的 category。 |
| `DisplayCreationResult()` success | 调用：`routers/admin.py:682`；定义：`routers/admin.py:685` | Boundary 返回 dashboard，并显示成功 flash message。 |
| `validation error` | `routers/admin.py:674` | Boundary 捕获 `HTTPException`。 |
| `DisplayCreationResult()` failure | `routers/admin.py:676` | Boundary 返回 dashboard，并显示错误 flash message。 |
| duplicate category error | `services/admin_service.py:327` 到 `services/admin_service.py:329` | 数据库唯一约束冲突时 rollback，并返回 HTTP 409。 |

### 注意点

- P1 的 Sequence Diagram 主流程是正确的。
- 真实代码里验证会执行两次：第一次是 `CategoryManagementPage.EnterCategoryDetails()`，第二次是在 `CategoryController.CreateCategory()` 内部。
- `create_category()` 是 route handler，不是 BCE class 方法；真正的 Boundary 方法是 `CategoryManagementPage.SubmitCategoryCreation()`。

## P4 View All Categories

### 代码位置对照表

| Sequence Diagram 步骤 | 真实代码位置 | 中文说明 |
|---|---|---|
| `dashboard_page(category_q, category_status, category_id)` | `routers/admin.py:51` | Admin Dashboard 的真实 GET route。 |
| `category_q`, `category_status`, `category_id` parameters | `routers/admin.py:61` 到 `routers/admin.py:63` | P4 使用的 query 参数。 |
| route calls `AdminDashboardPage.ViewUserAccounts(...)` | `routers/admin.py:71` | dashboard 方法同时处理 account、category、campaign review 和 report 面板。 |
| `AdminDashboardPage.ViewUserAccounts()` | `routers/admin.py:179` | 真实的 dashboard 页面加载方法。 |
| `CategoryManagementPage.AccessCategoryManagementPage()` | `routers/admin.py:652` | 这个方法存在，但主要用于打开 create-category modal，不是真正的 P4 list-loading 方法。 |
| normalize category status | `services/admin_service.py:51`；使用位置：`routers/admin.py:232` | 把 `"all"` 转成 `None`，并验证 active/inactive 状态。 |
| `CategoryManagementPage.ViewAllCategories(...)` | 调用：`routers/admin.py:234`；定义：`routers/admin.py:785` | Boundary 方法，用于加载 category list。 |
| `CategoryController.GetCategoryList(session, search_keywords, status)` | 调用：`routers/admin.py:790`；定义：`services/admin_service.py:338` | Controller 方法，负责搜索、加载全部 categories 和 status filter。 |
| `SearchCategories(session, search_keywords)` | 定义：`services/admin_service.py:351`；调用条件：`services/admin_service.py:342` | 当存在 search keyword 时调用。 |
| `Category.SearchCategories(session, search_keywords)` | 定义：`models/admin.py:77`；调用：`services/admin_service.py:352` | Entity 层按 name、description 或 value 搜索。 |
| `search results` | `models/admin.py:93` | Entity 返回搜索结果。 |
| `Category.GetAllCategories(session)` | 定义：`models/admin.py:72`；调用：`services/admin_service.py:344` | 没有搜索关键词时返回所有 categories。 |
| `all categories` | `models/admin.py:74` | Entity 返回全部 category rows。 |
| `filter categories by status in memory` | `services/admin_service.py:346` 到 `services/admin_service.py:347` | 这是 inline list comprehension，不是独立方法。 |
| `category list` | `services/admin_service.py:348` | Controller 返回最终 category list。 |
| serialize category list | `routers/admin.py:239`；serializer：`services/admin_service.py:545` | 把 category objects 转成 template payload。 |
| display categories | `routers/admin.py:391` | `serialized_categories` 被放入 template context；没有单独的 `DisplayCategories()` 方法。 |
| `category_id exists` | `routers/admin.py:241` | 当 URL 里有 `category_id` 时，进入详情流程。 |
| `CategoryManagementPage.ViewCategoryDetails(session, category_id)` | 调用：`routers/admin.py:243`；定义：`routers/admin.py:805` | Boundary 方法，用于加载 category details。 |
| `CategoryController.GetCategoryDetails(session, category_id)` | 定义：`services/admin_service.py:359`；调用：`routers/admin.py:806` | Controller 详情方法。 |
| `Category.GetCategoryById(session, category_id)` | 定义：`models/admin.py:68`；调用：`services/admin_service.py:360` | Entity 按 category id 查询。 |
| `category record` | `models/admin.py:69` | 返回 category object 或 `None`。 |
| `Category.GetCategoryDetails(category)` | 定义：`models/admin.py:56`；调用：`services/admin_service.py:363` | 把 category object 转成详情 dictionary。 |
| `GetCategoryCampaignCount(session, category.value)` | 定义：`services/admin_service.py:407`；调用：`services/admin_service.py:364` | 统计该 category 下关联的 campaign 数量。 |
| `category details` | `services/admin_service.py:365` | Controller 返回 category detail payload。 |
| selected category passed to template | `routers/admin.py:392` | `selected_category_record` 被传入 template context。 |

### 注意点

- P4 的真实入口是 `dashboard_page()`，不是 `CategoryManagementPage.AccessCategoryManagementPage(category_q, category_status, category_id)`。
- `CategoryManagementPage.AccessCategoryManagementPage()` 确实存在，但主要是打开 create-category modal。
- status filter 是在 `CategoryController.GetCategoryList()` 里面用代码块完成的，不是单独方法。
- 没有单独的 `DisplayCategories()` 方法；categories 是被序列化后放入 dashboard template context。

## D5 Save Campaign to Favourite List

### 代码位置对照表

| Sequence Diagram 步骤 | 真实代码位置 | 中文说明 |
|---|---|---|
| `projects_page()` | `routers/donee.py:184` | `/projects` 页面入口，实际调用 `CampaignSearchPage.ViewCampaigns()`。 |
| route calls `CampaignSearchPage.ViewCampaigns()` | `routers/donee.py:190` | 收藏操作发生前，先加载 project list 页面。 |
| `Select save to favourite option` | 没有单独后端方法 | 这是 UI 行为：用户点击 save/favourite 按钮。 |
| `save_campaign_to_favourite_list(campaign_id)` route | `routers/donee.py:337` | `/projects/{campaign_id}/favourites/save` 的真实 POST route。 |
| route calls `FavouriteListPage.SaveCampaignToFavouriteList()` | `routers/donee.py:346` | route handler 把 POST 请求交给 Boundary class。 |
| `FavouriteListPage.SaveCampaignToFavouriteList()` | `routers/donee.py:661` | D5 的主要 Boundary 方法。 |
| `SelectFavouriteReturnLocation(category, q, sort)` | 定义：`routers/donee.py:647`；调用：`routers/donee.py:669` | 保存后准备返回页面所需的筛选参数。 |
| get authenticated Donee | `routers/donee.py:675` | 获取当前登录用户，并用 `user.id` 作为 `donee_id`。 |
| `FavouriteController.SaveCampaignToFavouriteList(donee_id, campaign_id)` | 调用：`routers/donee.py:678`；定义：`services/donation_service.py:133` | Boundary 调用 Controller 保存 favourite。 |
| `CampaignDetailController.RetrieveCampaignInformation(campaign_id)` | 定义：`services/donation_service.py:107`；调用：`services/donation_service.py:136` | 验证 campaign 是否存在，并且是否为 published。 |
| `FundraisingCampaign.GetCampaignById(campaign_id)` | 定义：`models/campaign.py:71`；调用：`services/donation_service.py:110` | Entity 层查询 campaign。 |
| `published campaign record` | `services/donation_service.py:111` | 检查 `campaign.status == "published"`。 |
| return campaign to `FavouriteController` | `services/donation_service.py:113` | 返回通过验证的 campaign object。 |
| `AddCampaignToFavouriteList(donee_id, campaign_id)` | 定义：`services/donation_service.py:140`；调用：`services/donation_service.py:137` | Controller 内部继续处理 favourite record。 |
| `FavouriteCampaign.GetFavouriteRecord(donee_id, campaign_id)` | 定义：`models/donation.py:261`；调用：`services/donation_service.py:143` | 检查是否已经收藏过。 |
| `existing record or none` | `models/donation.py:268` | Entity 返回已有 record 或 `None`。 |
| favourite already exists | `services/donation_service.py:144` 到 `services/donation_service.py:145` | 如果已经存在，直接返回已有 record。 |
| `FavouriteCampaign.AddToFavourite(donee_id, campaign_id)` | 定义：`models/donation.py:249`；调用：`services/donation_service.py:146` | 创建新的 `FavouriteCampaign` object。 |
| `favourite record` | `models/donation.py:250` | 返回新创建的 favourite object。 |
| `FavouriteCampaign.SaveFavouriteRecord(record)` | 定义：`models/donation.py:257`；调用：`services/donation_service.py:147` | Entity 把 record 加入 session。 |
| `save success` | `services/donation_service.py:148` 到 `services/donation_service.py:149` | 执行 `session.commit()` 和 `session.refresh(favourite_record)`。 |
| return save success | `services/donation_service.py:150` | Controller 返回 favourite record。 |
| `DisplayFavouriteSaveResult()` | 调用：`routers/donee.py:680`；定义：`routers/donee.py:735` | Boundary 设置成功 flash message。 |
| `RedirectAfterFavouriteChange()` | 定义：`routers/donee.py:763`；调用：`routers/donee.py:744` | 根据 `return_to` redirect 回 projects、impact 或 profile。 |

### 注意点

- `projects_page()` 是 route handler，不是 `FavouriteListPage` 方法。
- D5 收藏流程真正开始于 `save_campaign_to_favourite_list()`。
- `Select save to favourite option` 是 UI 点击行为，没有单独后端方法。
- duplicate favourite 分支通过检查 `existing_record` 实现；如果已存在，就直接返回旧 record。

## F12 View Completed Campaigns

### 代码位置对照表

| Sequence Diagram 步骤 | 真实代码位置 | 中文说明 |
|---|---|---|
| `your_fundraisers_page()` | `routers/fundraiser.py:52` | `/your-fundraisers` route 入口。 |
| route calls `CampaignAnalysisPage.ViewFilteredCampaigns()` | `routers/fundraiser.py:58` | route 实际进入的页面方法。 |
| `CampaignHistoryPage.AccessCampaignHistoryPage()` | `routers/fundraiser.py:745` | 这个方法存在，但也是转到 `CampaignAnalysisPage.ViewFilteredCampaigns()`。 |
| `CampaignHistoryPage.ViewCompletedCampaigns(...)` | 调用：`routers/fundraiser.py:839`；定义：`routers/fundraiser.py:754` | Boundary 方法，用来请求 completed campaigns。 |
| `CampaignHistoryController.RetrieveCompletedCampaignList(session, owner_id, filters)` | 调用：`routers/fundraiser.py:760`；定义：`services/campaign_service.py:1147` | Controller 方法，取得 completed campaign list。 |
| `CompletedCampaignRecord.GetCompletedCampaigns(session, owner_id, filters)` | 定义：`models/campaign.py:768`；调用：`services/campaign_service.py:1153` | Entity-like class，用来取得 completed campaigns。 |
| `FundraisingCampaign.GetFilteredCampaigns(...)` | 定义：`models/campaign.py:163`；调用：`models/campaign.py:774` | 真实过滤逻辑，使用 `lifecycle="completed"`。 |
| `lifecycle="completed"` | `models/campaign.py:778` | 限制结果只包含 completed campaigns。 |
| `completed campaign list` | `models/campaign.py:781` | 返回 campaign list。 |
| `CampaignDetailSerializer.SerializeCampaignDetail(completed_campaign)` | 调用：`routers/fundraiser.py:849`；定义：`services/campaign_service.py:563` | 把每个 completed campaign 序列化成 template 需要的数据。 |
| `completed campaign detail payload` | `services/campaign_service.py:572` 到 `services/campaign_service.py:615` | 返回包含 title、status、progress、images、view count、shortlist count 等信息的 payload。 |
| `completed campaign data` | Controller 返回：`services/campaign_service.py:1153` 到 `services/campaign_service.py:1158`；Boundary 接收：`routers/fundraiser.py:839` | Controller 返回 list，Boundary 后续再序列化。 |

### 注意点

- `your_fundraisers_page()` 是 route handler，不是 `CampaignHistoryPage` 方法。
- route 先进入 `CampaignAnalysisPage.ViewFilteredCampaigns()`，然后内部再调用 `CampaignHistoryPage.ViewCompletedCampaigns()`。
- 图里的 `serialize_campaign_detail(completed_campaign)` 更准确应理解为 `CampaignDetailSerializer.SerializeCampaignDetail(session, campaign)`。
- lowercase wrapper `serialize_campaign_detail()` 也存在于 `services/campaign_service.py:618`，但 F12 页面实际使用的是 class method。

## F13 Filter Campaigns Using Selectable Criteria

### 代码位置对照表

| Sequence Diagram 步骤 | 真实代码位置 | 中文说明 |
|---|---|---|
| `your_fundraisers_page(category, lifecycle, sort)` | `routers/fundraiser.py:52` | `/your-fundraisers` route 接收 filter query 参数。 |
| route calls `CampaignAnalysisPage.ViewFilteredCampaigns(...)` | `routers/fundraiser.py:58` | F13 的主要 Boundary 入口。 |
| `Select filter criteria` | 真实方法：`routers/fundraiser.py:782`；调用：`routers/fundraiser.py:821` | 真实代码是 `CampaignAnalysisPage.SelectFilterCriteria(category, lifecycle, sort)`。 |
| normalize category | `routers/fundraiser.py:787` 到 `routers/fundraiser.py:790` | 空值或 `"all"` 会变成 `None`，否则会标准化 category。 |
| `normalize_fundraiser_lifecycle(lifecycle)` | 定义：`services/campaign_service.py:1257`；调用：`routers/fundraiser.py:791` | 不合法 lifecycle 会回到 `"all"`。 |
| `normalize_fundraiser_campaign_sort(sort)` | 定义：`services/campaign_service.py:1250`；调用：`routers/fundraiser.py:792` | 不合法 sort 会回到默认 fundraiser sort。 |
| `CampaignAnalysisPage.FilterCampaigns(...)` | 定义：`routers/fundraiser.py:796`；调用：`routers/fundraiser.py:832` | Boundary 方法，负责调用 Controller。 |
| `RetrieveFilteredCampaignResults(session, owner_id, criteria)` | 定义：`services/campaign_service.py:1199`；调用：`routers/fundraiser.py:803` | Controller 方法，用于取得 filtered campaigns。 |
| `FundraisingCampaign.GetFilteredCampaigns(session, owner_id, criteria)` | 定义：`models/campaign.py:163`；调用：`services/campaign_service.py:1206` | Entity 方法，执行真实 filtering。 |
| `GetCampaignsByOwner(session, owner_id)` | 定义：`models/campaign.py:75`；调用：`models/campaign.py:174` | 先取得当前 Fund Raiser 自己的 campaigns。 |
| category filter | `models/campaign.py:175` 到 `models/campaign.py:176` | 如果有 category，就按 category 筛选。 |
| lifecycle filter | `models/campaign.py:186` 到 `models/campaign.py:191`；`MatchesLifecycle()` 在 `models/campaign.py:256` | 如果 lifecycle 不是 `"all"`，就按 lifecycle 筛选。 |
| sort filter | 调用：`models/campaign.py:192`；方法：`models/campaign.py:262` | 用 `SortOwnerCampaigns()` 排序。 |
| `filtered campaign results` to Controller | `models/campaign.py:192` | Entity 返回过滤和排序后的 campaign list。 |
| `filtered campaign results` to Boundary | `services/campaign_service.py:1206` 到 `services/campaign_service.py:1211` | Controller 返回 Entity 结果。 |
| `CampaignDetailSerializer.SerializeCampaignDetail(...)` | `routers/fundraiser.py:845` 到 `routers/fundraiser.py:848` | 把 filtered campaigns 序列化成页面展示数据。 |
| `DisplayFilteredCampaigns()` | 调用：`routers/fundraiser.py:866`；定义：`routers/fundraiser.py:882` | 渲染 `your_fundraisers.html`，并传入当前 filters 和 campaign results。 |
| `Clear filter controls` | 没有单独后端方法 | 通过重新请求默认 query values 实现。 |
| default clear-filter values | `routers/fundraiser.py:54` 到 `routers/fundraiser.py:56` | 默认值是 `category=None`, `lifecycle="all"`, `sort="updated_desc"`。 |
| unfiltered fundraiser campaigns | 仍然走 `ViewFilteredCampaigns()` 同一流程 | 使用默认值时，`GetFilteredCampaigns()` 返回该 owner 的 campaigns，不按 category/lifecycle 进一步过滤。 |

### 注意点

- F13 的 Sequence Diagram 逻辑是正确的。
- `Select filter criteria` 如果要严格对应代码，建议写成 `SelectFilterCriteria(category, lifecycle, sort)`。
- `Clear filter controls` 是前端或 URL 参数行为，不是单独 BCE 方法。
- 后端清除筛选的实现方式是重新执行 `ViewFilteredCampaigns(None, "all", "updated_desc")`。

## 建议修改的 Sequence Diagram 表达

如果 Sequence Diagram 需要严格使用真实代码方法名，下面这些表达会更稳妥：

| 当前图中的写法 | 更贴近真实代码的写法 |
|---|---|
| `P4: AccessCategoryManagementPage(category_q, category_status, category_id)` | `dashboard_page(category_q, category_status, category_id)` 或 `ViewAllCategories(search_keywords, status)` |
| `P4: Display categories` | `serialize_category_summaries()` 和 template context `"categories"` |
| `D5: Select save to favourite option` | UI action that submits to `save_campaign_to_favourite_list(campaign_id)` |
| `F12: serialize_campaign_detail(completed_campaign)` | `CampaignDetailSerializer.SerializeCampaignDetail(session, campaign)` |
| `F13: Select filter criteria` | `SelectFilterCriteria(category, lifecycle, sort)` |
| `F13: Clear filter controls` | `ViewFilteredCampaigns(None, "all", "updated_desc")` |
