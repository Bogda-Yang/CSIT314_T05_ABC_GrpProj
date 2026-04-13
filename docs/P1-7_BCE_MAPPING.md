# P1-7 BCE Mapping

This file documents the BCE scope for the platform-management range `P1-7`.

Current implementation note:

- No `P1-7` platform-management features are implemented in the current codebase.
- The classes and methods below are preserved from the BCE source so the mapping file exists for later implementation.

## Status Summary

| Range | Status | Notes |
|---|---|---|
| `P1-4` | Not implemented | Category management is not implemented |
| `P5-7` | Not implemented | Daily, weekly, and monthly reporting are not implemented |

## P1 Create Category

| BCE Class | Source Methods | Current File Mapping | Status |
|---|---|---|---|
| `CategoryManagementPage` | `AccessCategoryManagementPage()`, `EnterCategoryDetails()`, `SubmitCategoryCreation()`, `DisplayCreationResult()` | No category boundary page exists in the current project | Not implemented |
| `CategoryController` | `ValidateCategoryInformation()`, `CreateCategory()`, `SaveCategory()` | No controller implementation exists | Not implemented |
| `Category` | `CreateCategory()`, `SaveCategory()`, `GetCategoryDetails()` | No entity implementation exists | Not implemented |

## P2 Update Category

| BCE Class | Source Methods | Current File Mapping | Status |
|---|---|---|---|
| `CategoryManagementPage` | `AccessCategoryManagementPage()`, `SelectExistingCategory()`, `ViewCurrentCategoryDetails()`, `EditCategoryDetails()`, `SubmitCategoryUpdate()`, `DisplayUpdateResult()` | No category update boundary page exists | Not implemented |
| `CategoryController` | `GetCategoryDetails()`, `ValidateUpdatedInformation()`, `UpdateCategory()`, `SaveCategoryChanges()` | No controller implementation exists | Not implemented |
| `Category` | `GetCategoryById()`, `GetCategoryDetails()`, `UpdateCategory()`, `SaveCategoryChanges()` | No entity implementation exists | Not implemented |

## P3 Delete Category

| BCE Class | Source Methods | Current File Mapping | Status |
|---|---|---|---|
| `CategoryManagementPage` | `AccessCategoryManagementPage()`, `SelectCategory()`, `ReviewCategoryDetails()`, `ConfirmCategoryDeletion()`, `DisplayDeletionResult()` | No category delete boundary page exists | Not implemented |
| `CategoryController` | `GetCategoryDetails()`, `DeleteCategory()`, `RemoveCategory()` | No controller implementation exists | Not implemented |
| `Category` | `GetCategoryById()`, `GetCategoryDetails()`, `DeleteCategory()` | No entity implementation exists | Not implemented |

## P4 View All Categories

| BCE Class | Source Methods | Current File Mapping | Status |
|---|---|---|---|
| `CategoryManagementPage` | `AccessCategoryManagementPage()`, `ViewAllCategories()`, `SearchCategories()`, `FilterCategories()`, `ViewCategoryDetails()` | No category listing boundary page exists | Not implemented |
| `CategoryController` | `GetCategoryList()`, `SearchCategories()`, `FilterCategories()`, `GetCategoryDetails()` | No controller implementation exists | Not implemented |
| `Category` | `GetAllCategories()`, `SearchCategories()`, `FilterCategories()`, `GetCategoryById()` | No entity implementation exists | Not implemented |

## P5 Generate Daily Report

| BCE Class | Source Methods | Current File Mapping | Status |
|---|---|---|---|
| `ReportManagementPage` | `AccessReportManagementPage()`, `SelectDailyReportType()`, `GenerateDailyReport()`, `ViewDailyReport()`, `ExportDailyReport()` | No reporting boundary page exists | Not implemented |
| `ReportController` | `CollectDailyActivityData()`, `GenerateDailyReport()`, `GetDailyReport()`, `ExportReport()` | No reporting controller exists | Not implemented |
| `PlatformActivity` | `GetDailyActivityData()` | No entity implementation exists | Not implemented |
| `DailyReport` | `GenerateReport()`, `GetReport()`, `ExportReport()` | No entity implementation exists | Not implemented |

## P6 Generate Weekly Report

| BCE Class | Source Methods | Current File Mapping | Status |
|---|---|---|---|
| `ReportManagementPage` | `AccessReportManagementPage()`, `SelectWeeklyReportType()`, `GenerateWeeklyReport()`, `ViewWeeklyReport()`, `ExportWeeklyReport()` | No reporting boundary page exists | Not implemented |
| `ReportController` | `CollectWeeklyActivityData()`, `GenerateWeeklyReport()`, `GetWeeklyReport()`, `ExportReport()` | No reporting controller exists | Not implemented |
| `PlatformActivity` | `GetWeeklyActivityData()` | No entity implementation exists | Not implemented |
| `WeeklyReport` | `GenerateReport()`, `GetReport()`, `ExportReport()` | No entity implementation exists | Not implemented |

## P7 Generate Monthly Report

| BCE Class | Source Methods | Current File Mapping | Status |
|---|---|---|---|
| `ReportManagementPage` | `AccessReportManagementPage()`, `SelectMonthlyReportType()`, `GenerateMonthlyReport()`, `ViewMonthlyReport()`, `ExportMonthlyReport()` | No reporting boundary page exists | Not implemented |
| `ReportController` | `CollectMonthlyPerformanceData()`, `GenerateMonthlyReport()`, `GetMonthlyReport()`, `ExportReport()` | No reporting controller exists | Not implemented |
| `PlatformActivity` | `GetMonthlyPerformanceData()` | No entity implementation exists | Not implemented |
| `MonthlyReport` | `GenerateReport()`, `GetReport()`, `ExportReport()` | No entity implementation exists | Not implemented |
