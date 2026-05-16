# Test Data Locations

This document lists where the hardcoded test data for the five test categories is stored.

All pure test data is centralized in `tests/test_data.py`. The other test files import data from that file and keep only test logic and assertions.

## Common Test Helpers

| Purpose | File | Lines |
|---|---|---|
| Shared fake session used instead of a real database | `tests/helpers.py` | 12-39 |
| Shared user builder | `tests/helpers.py` | 42-46 |
| Shared profile builder | `tests/helpers.py` | 49-60 |
| Shared campaign builder | `tests/helpers.py` | 63-86 |
| Shared campaign image builder and approval monkeypatch helper | `tests/helpers.py` | 89-122 |
| Shared donation record builder and hardcoded filter function | `tests/helpers.py` | 125-144 |
| Shared category builder | `tests/helpers.py` | 147-151 |
| Shared dummy request fixture | `tests/conftest.py` | 10-17 |

## 1. User Tests

| Data / Test Area | File | Lines |
|---|---|---|
| Shared valid password | `tests/test_data.py` | 1 |
| Registration test data: `REGISTER_CASES` | `tests/test_data.py` | 3-9 |
| Registration validation data: `REGISTRATION_VALIDATION_CASES` | `tests/test_data.py` | 11-20 |
| Login test data: `LOGIN_CASES` | `tests/test_data.py` | 22-27 |
| Login rejection data: `LOGIN_REJECTION_CASES` | `tests/test_data.py` | 29-34 |
| Registration test cases | `tests/test_user_auth.py` | 16-38 |
| Registration validation test cases | `tests/test_user_auth.py` | 41-54 |
| Login success test cases | `tests/test_user_auth.py` | 57-78 |
| Login failure test cases | `tests/test_user_auth.py` | 81-93 |

## 2. Fundraiser Tests

| Data / Test Area | File | Lines |
|---|---|---|
| Campaign submission data: `CAMPAIGN_SUBMISSION_CASES` | `tests/test_data.py` | 36-70 |
| Incomplete campaign submission data: `INCOMPLETE_CAMPAIGN_SUBMISSION_CASES` | `tests/test_data.py` | 72-79 |
| Workflow stage validation data: `WORKFLOW_STAGE_CASES` | `tests/test_data.py` | 81-87 |
| Valid campaign information data: `VALID_CAMPAIGN_INFORMATION_CASES` | `tests/test_data.py` | 89-94 |
| Invalid campaign category data: `INVALID_CAMPAIGN_CATEGORIES` | `tests/test_data.py` | 96 |
| Fundraiser validator data: `FUNDRAISER_VALIDATOR_CASES` | `tests/test_data.py` | 98-104 |
| Complete campaign submission test cases | `tests/test_fundraiser_submission.py` | 31-42 |
| Incomplete campaign rejection test cases | `tests/test_fundraiser_submission.py` | 45-53 |
| Workflow stage validation test cases | `tests/test_fundraiser_submission.py` | 56-65 |
| Campaign information validation test cases | `tests/test_fundraiser_submission.py` | 68-79 |
| Fundraiser validator test cases | `tests/test_fundraiser_submission.py` | 82-89 |

## 3. Admin Tests

| Data / Test Area | File | Lines |
|---|---|---|
| Admin approval data: `ADMIN_APPROVAL_CASES` | `tests/test_data.py` | 106-140 |
| Non-pending status data: `NON_PENDING_CAMPAIGN_STATUSES` | `tests/test_data.py` | 142 |
| Missing submission requirement data: `MISSING_SUBMISSION_REQUIREMENT_CASES` | `tests/test_data.py` | 144-150 |
| Approval status data: `APPROVAL_STATUS_CASES` | `tests/test_data.py` | 152 |
| Campaign status helper data: `STATUS_HELPER_INITIAL_STATUSES` | `tests/test_data.py` | 154 |
| Pending campaign validation test cases | `tests/test_admin_approval.py` | 17-25 |
| Non-pending campaign rejection test cases | `tests/test_admin_approval.py` | 28-36 |
| Approve campaign test cases | `tests/test_admin_approval.py` | 39-50 |
| Missing submission requirement test cases | `tests/test_admin_approval.py` | 53-60 |
| Approval status test cases | `tests/test_admin_approval.py` | 63-71 |
| Publish campaign test cases | `tests/test_admin_approval.py` | 74-83 |
| Campaign status helper test cases | `tests/test_admin_approval.py` | 86-94 |

## 4. Platform Manager Tests

| Data / Test Area | File | Lines |
|---|---|---|
| Valid category information data: `VALID_CATEGORY_INFORMATION_CASES` | `tests/test_data.py` | 156-162 |
| Invalid category information data: `INVALID_CATEGORY_INFORMATION_CASES` | `tests/test_data.py` | 164-170 |
| Valid category status data: `VALID_CATEGORY_STATUS_CASES` | `tests/test_data.py` | 172-177 |
| Invalid category status data: `INVALID_CATEGORY_STATUSES` | `tests/test_data.py` | 179 |
| Create category data: `CREATE_CATEGORY_CASES` | `tests/test_data.py` | 181-185 |
| Delete category usage data: `DELETE_CATEGORY_USAGE_CASES` | `tests/test_data.py` | 187-191 |
| Missing category id data: `MISSING_CATEGORY_IDS` | `tests/test_data.py` | 193 |
| Valid category information test cases | `tests/test_platform_category.py` | 19-23 |
| Invalid category information test cases | `tests/test_platform_category.py` | 26-30 |
| Category status validation test cases | `tests/test_platform_category.py` | 33-48 |
| Create category test cases | `tests/test_platform_category.py` | 51-60 |
| Delete category usage test cases | `tests/test_platform_category.py` | 63-82 |
| Missing category test cases | `tests/test_platform_category.py` | 85-92 |

## 5. Donee Tests

| Data / Test Area | File | Lines |
|---|---|---|
| Donation filter records: `DONATION_FILTER_RECORDS` | `tests/test_data.py` | 195-201 |
| Category filter data: `DONATION_CATEGORY_FILTER_CASES` | `tests/test_data.py` | 203-209 |
| Date period filter data: `DONATION_DATE_PERIOD_CASES` | `tests/test_data.py` | 211-217 |
| Combined category and date filter data: `DONATION_COMBINED_FILTER_CASES` | `tests/test_data.py` | 219-225 |
| Empty-result filter data: `DONATION_EMPTY_FILTER_CASES` | `tests/test_data.py` | 227-232 |
| Unknown date period data: `UNKNOWN_DATE_PERIOD_CASES` | `tests/test_data.py` | 234 |
| Category filter test cases | `tests/test_donee_donation_filters.py` | 25-33 |
| Date period filter test cases | `tests/test_donee_donation_filters.py` | 36-44 |
| Combined category and date filter test cases | `tests/test_donee_donation_filters.py` | 47-55 |
| Empty-result filter test cases | `tests/test_donee_donation_filters.py` | 58-66 |
| Unknown date period test cases | `tests/test_donee_donation_filters.py` | 69-77 |

## Current Test Count

The current test suite collects 116 pytest cases:

| Category | File | Collected Cases |
|---|---|---:|
| User | `tests/test_user_auth.py` | 21 |
| Fundraiser | `tests/test_fundraiser_submission.py` | 26 |
| Admin | `tests/test_admin_approval.py` | 23 |
| Platform Manager | `tests/test_platform_category.py` | 25 |
| Donee | `tests/test_donee_donation_filters.py` | 21 |
