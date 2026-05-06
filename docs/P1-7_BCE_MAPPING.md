# P1-7 BCE Mapping

This version lists only real method/function definition lines.

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

| BCE Class | Method definitions |
|---|---|
| `CategoryManagementPage` | `AccessCategoryManagementPage()` is handled by `dashboard_page()` `routers/admin.py:51`; `EnterCategoryDetails()`, `SubmitCategoryCreation()`, and `DisplayCreationResult()` are handled by `create_category()` `routers/admin.py:323` |
| `CategoryController` | `ValidateCategoryInformation()` `services/admin_service.py:307`, `CreateCategory()` `services/admin_service.py:327`, `SaveCategory()` `services/admin_service.py:340` |
| `Category` | `CreateCategory()` `models/admin.py:40`, `SaveCategory()` `models/admin.py:52`, `GetCategoryDetails()` `models/admin.py:56` |

## P2 Update Category

| BCE Class | Method definitions |
|---|---|
| `CategoryManagementPage` | `AccessCategoryManagementPage()`, `SelectExistingCategory()`, `ViewCurrentCategoryDetails()`, and `EditCategoryDetails()` are handled by `dashboard_page()` `routers/admin.py:51`; `SubmitCategoryUpdate()` and `DisplayUpdateResult()` are handled by `update_category()` `routers/admin.py:351` |
| `CategoryController` | `GetCategoryDetails()` `services/admin_service.py:365`, `ValidateUpdatedInformation()` `services/admin_service.py:319`, `UpdateCategory()` `services/admin_service.py:374`, `SaveCategoryChanges()` `services/admin_service.py:394` |
| `Category` | `GetCategoryById()` `models/admin.py:68`, `GetCategoryDetails()` `models/admin.py:56`, `UpdateCategory()` `models/admin.py:104`, `SaveCategoryChanges()` `models/admin.py:111` |

## P3 Delete Category

| BCE Class | Method definitions |
|---|---|
| `CategoryManagementPage` | `AccessCategoryManagementPage()`, `SelectCategory()`, and `ReviewCategoryDetails()` are handled by `dashboard_page()` `routers/admin.py:51`; `ConfirmCategoryDeletion()` and `DisplayDeletionResult()` are handled by `delete_category()` `routers/admin.py:381` |
| `CategoryController` | `GetCategoryDetails()` `services/admin_service.py:365`, `DeleteCategory()` `services/admin_service.py:398`, `RemoveCategory()` `services/admin_service.py:409` |
| `Category` | `GetCategoryById()` `models/admin.py:68`, `GetCategoryDetails()` `models/admin.py:56`, `DeleteCategory()` `models/admin.py:115` |

## P4 View All Categories

| BCE Class | Method definitions |
|---|---|
| `CategoryManagementPage` | `AccessCategoryManagementPage()`, `ViewAllCategories()`, `SearchCategories()`, `FilterCategories()`, and `ViewCategoryDetails()` are handled by `dashboard_page()` `routers/admin.py:51` |
| `CategoryController` | `GetCategoryList()` `services/admin_service.py:344`, `SearchCategories()` `services/admin_service.py:357`, `FilterCategories()` `services/admin_service.py:361`, `GetCategoryDetails()` `services/admin_service.py:365` |
| `Category` | `GetAllCategories()` `models/admin.py:72`, `SearchCategories()` `models/admin.py:77`, `FilterCategories()` `models/admin.py:96`, `GetCategoryById()` `models/admin.py:68` |

## P5 Generate Daily Report

| BCE Class | Method definitions |
|---|---|
| `ReportManagementPage` | `AccessReportManagementPage()`, `SelectDailyReportType()`, `GenerateDailyReport()`, and `ViewDailyReport()` are handled by `dashboard_page()` `routers/admin.py:51`; `ExportDailyReport()` is handled by `export_report()` `routers/admin.py:405` |
| `ReportController` | `CollectDailyActivityData()` `services/admin_service.py:427`, `GenerateDailyReport()` `services/admin_service.py:447`, `GetDailyReport()` `services/admin_service.py:469`, `ExportReport()` `services/admin_service.py:500` |
| `PlatformActivity` | `GetDailyActivityData()` `models/admin.py:220` |
| `DailyReport` | `GenerateReport()` `models/admin.py:273`, `GetReport()` `models/admin.py:277`, `ExportReport()` `models/admin.py:281` |

## P6 Generate Weekly Report

| BCE Class | Method definitions |
|---|---|
| `ReportManagementPage` | `AccessReportManagementPage()`, `SelectWeeklyReportType()`, `GenerateWeeklyReport()`, and `ViewWeeklyReport()` are handled by `dashboard_page()` `routers/admin.py:51`; `ExportWeeklyReport()` is handled by `export_report()` `routers/admin.py:405` |
| `ReportController` | `CollectWeeklyActivityData()` `services/admin_service.py:431`, `GenerateWeeklyReport()` `services/admin_service.py:451`, `GetWeeklyReport()` `services/admin_service.py:473`, `ExportReport()` `services/admin_service.py:500` |
| `PlatformActivity` | `GetWeeklyActivityData()` `models/admin.py:229` |
| `WeeklyReport` | `GenerateReport()` `models/admin.py:287`, `GetReport()` `models/admin.py:291`, `ExportReport()` `models/admin.py:295` |

## P7 Generate Monthly Report

| BCE Class | Method definitions |
|---|---|
| `ReportManagementPage` | `AccessReportManagementPage()`, `SelectMonthlyReportType()`, `GenerateMonthlyReport()`, and `ViewMonthlyReport()` are handled by `dashboard_page()` `routers/admin.py:51`; `ExportMonthlyReport()` is handled by `export_report()` `routers/admin.py:405` |
| `ReportController` | `CollectMonthlyPerformanceData()` `services/admin_service.py:441`, `GenerateMonthlyReport()` `services/admin_service.py:463`, `GetMonthlyReport()` `services/admin_service.py:483`, `ExportReport()` `services/admin_service.py:500` |
| `PlatformActivity` | `GetMonthlyPerformanceData()` `models/admin.py:249` |
| `MonthlyReport` | `GenerateReport()` `models/admin.py:301`, `GetReport()` `models/admin.py:305`, `ExportReport()` `models/admin.py:309` |
