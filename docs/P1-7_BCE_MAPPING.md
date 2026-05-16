# P1-7 BCE Mapping

This version maps each BCE class and method to the real implementation definition lines.

Scope:

- `P1 Create Category`
- `P2 Update Category`
- `P3 Delete Category`
- `P4 View All Categories`
- `P5 Generate Daily Report`
- `P6 Generate Weekly Report`
- `P7 Generate Monthly Report`

Implementation note:

- Platform manager functions are implemented inside the administrator dashboard because the project treats the platform manager role as the admin account.

## P1 Create Category

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CategoryManagementPage` | `class CategoryManagementPage` `routers/admin.py:648` | `AccessCategoryManagementPage()` `routers/admin.py:652`, `EnterCategoryDetails()` `routers/admin.py:659`, `SubmitCategoryCreation()` `routers/admin.py:663`, and `DisplayCreationResult()` `routers/admin.py:685` |
| `CategoryController` | `class CategoryController` `services/admin_service.py:299` | `ValidateCategoryInformation()` `services/admin_service.py:301`, `CreateCategory()` `services/admin_service.py:321`, and `SaveCategory()` `services/admin_service.py:334` |
| `Category` | `class Category` `models/admin.py:20` | `CreateCategory()` `models/admin.py:40` and `SaveCategory()` `models/admin.py:52` |

## P2 Update Category

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CategoryManagementPage` | `class CategoryManagementPage` `routers/admin.py:648` | `AccessCategoryManagementPage()` `routers/admin.py:652`, `SelectExistingCategory()` `routers/admin.py:698`, `ViewCurrentCategoryDetails()` `routers/admin.py:702`, `EditCategoryDetails()` `routers/admin.py:706`, `SubmitCategoryUpdate()` `routers/admin.py:710`, and `DisplayUpdateResult()` `routers/admin.py:734` |
| `CategoryController` | `class CategoryController` `services/admin_service.py:299` | `GetCategoryDetails()` `services/admin_service.py:359`, `GetCategoryCampaignCount()` `services/admin_service.py:407`, `ValidateUpdatedInformation()` `services/admin_service.py:313`, `ValidateCategoryInformation()` `services/admin_service.py:301`, `UpdateCategory()` `services/admin_service.py:368`, and `SaveCategoryChanges()` `services/admin_service.py:388` |
| `Category` | `class Category` `models/admin.py:20` | `GetCategoryById()` `models/admin.py:68`, `GetCategoryDetails()` `models/admin.py:56`, `UpdateCategory()` `models/admin.py:104`, and `SaveCategoryChanges()` `models/admin.py:111` |

## P3 Delete Category

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CategoryManagementPage` | `class CategoryManagementPage` `routers/admin.py:648` | `AccessCategoryManagementPage()` `routers/admin.py:652`, `SelectCategory()` `routers/admin.py:747`, `ReviewCategoryDetails()` `routers/admin.py:751`, `ConfirmCategoryDeletion()` `routers/admin.py:755`, and `DisplayDeletionResult()` `routers/admin.py:772` |
| `CategoryController` | `class CategoryController` `services/admin_service.py:299` | `GetCategoryDetails()` `services/admin_service.py:359`, `DeleteCategory()` `services/admin_service.py:392`, `GetCategoryCampaignCount()` `services/admin_service.py:407`, and `RemoveCategory()` `services/admin_service.py:403` |
| `Category` | `class Category` `models/admin.py:20` | `GetCategoryById()` `models/admin.py:68`, `GetCategoryDetails()` `models/admin.py:56`, and `DeleteCategory()` `models/admin.py:115` |

## P4 View All Categories

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `CategoryManagementPage` | `class CategoryManagementPage` `routers/admin.py:648` | `AccessCategoryManagementPage()` `routers/admin.py:652`, `ViewAllCategories()` `routers/admin.py:785`, `SearchCategories()` `routers/admin.py:797`, `FilterCategories()` `routers/admin.py:801`, and `ViewCategoryDetails()` `routers/admin.py:805` |
| `CategoryController` | `class CategoryController` `services/admin_service.py:299` | `GetCategoryList()` `services/admin_service.py:338`, `SearchCategories()` `services/admin_service.py:351`, `FilterCategories()` `services/admin_service.py:355`, `GetCategoryDetails()` `services/admin_service.py:359`, and `GetCategoryCampaignCount()` `services/admin_service.py:407` |
| `Category` | `class Category` `models/admin.py:20` | `GetAllCategories()` `models/admin.py:72`, `SearchCategories()` `models/admin.py:77`, `FilterCategories()` `models/admin.py:96`, `GetCategoryById()` `models/admin.py:68`, and `GetCategoryDetails()` `models/admin.py:56` |

## P5 Generate Daily Report

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `ReportManagementPage` | `class ReportManagementPage` `routers/admin.py:809` | `AccessReportManagementPage()` `routers/admin.py:813`, `SelectDailyReportType()` `routers/admin.py:823`, `GenerateDailyReport()` `routers/admin.py:835`, `ViewDailyReport()` `routers/admin.py:849`, and `ExportDailyReport()` `routers/admin.py:863` |
| `ReportController` | `class ReportController` `services/admin_service.py:419` | `GetReport()` `services/admin_service.py:483`, `CollectDailyActivityData()` `services/admin_service.py:421`, `GenerateDailyReport()` `services/admin_service.py:441`, `GetDailyReport()` `services/admin_service.py:463`, and `ExportReport()` `services/admin_service.py:494` |
| `PlatformActivity` | `class PlatformActivity` `models/admin.py:140` | `GetDailyActivityData()` `models/admin.py:318` |
| `DailyReport` | `class DailyReport` `models/admin.py:401` | `GenerateReport()` `models/admin.py:403`, `GetReport()` `models/admin.py:407`, and `ExportReport()` `models/admin.py:411` |

## P6 Generate Weekly Report

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `ReportManagementPage` | `class ReportManagementPage` `routers/admin.py:809` | `AccessReportManagementPage()` `routers/admin.py:813`, `SelectWeeklyReportType()` `routers/admin.py:827`, `GenerateWeeklyReport()` `routers/admin.py:839`, `ViewWeeklyReport()` `routers/admin.py:853`, and `ExportWeeklyReport()` `routers/admin.py:874` |
| `ReportController` | `class ReportController` `services/admin_service.py:419` | `GetReport()` `services/admin_service.py:483`, `CollectWeeklyActivityData()` `services/admin_service.py:425`, `GenerateWeeklyReport()` `services/admin_service.py:445`, `GetWeeklyReport()` `services/admin_service.py:467`, and `ExportReport()` `services/admin_service.py:494` |
| `PlatformActivity` | `class PlatformActivity` `models/admin.py:140` | `GetWeeklyActivityData()` `models/admin.py:327` |
| `WeeklyReport` | `class WeeklyReport` `models/admin.py:415` | `GenerateReport()` `models/admin.py:417`, `GetReport()` `models/admin.py:421`, and `ExportReport()` `models/admin.py:425` |

## P7 Generate Monthly Report

| BCE Class | Class definition | Method definitions |
|---|---|---|
| `ReportManagementPage` | `class ReportManagementPage` `routers/admin.py:809` | `AccessReportManagementPage()` `routers/admin.py:813`, `SelectMonthlyReportType()` `routers/admin.py:831`, `GenerateMonthlyReport()` `routers/admin.py:845`, `ViewMonthlyReport()` `routers/admin.py:859`, and `ExportMonthlyReport()` `routers/admin.py:889` |
| `ReportController` | `class ReportController` `services/admin_service.py:419` | `GetReport()` `services/admin_service.py:483`, `CollectMonthlyPerformanceData()` `services/admin_service.py:435`, `GenerateMonthlyReport()` `services/admin_service.py:457`, `GetMonthlyReport()` `services/admin_service.py:477`, and `ExportReport()` `services/admin_service.py:494` |
| `PlatformActivity` | `class PlatformActivity` `models/admin.py:140` | `GetMonthlyPerformanceData()` `models/admin.py:351` |
| `MonthlyReport` | `class MonthlyReport` `models/admin.py:429` | `GenerateReport()` `models/admin.py:431`, `GetReport()` `models/admin.py:435`, and `ExportReport()` `models/admin.py:439` |
