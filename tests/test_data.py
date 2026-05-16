VALID_PASSWORD = "Password123"

REGISTER_CASES = [
    {"username": "New User", "email": "new.user@example.com", "password": VALID_PASSWORD, "code": "123456"},
    {"username": "Amy", "email": "amy@example.com", "password": "Amy12345", "code": "222222"},
    {"username": "Ben Tester", "email": "ben.tester@example.com", "password": "Ben12345", "code": "333333"},
    {"username": "Cara", "email": "cara@example.com", "password": "Cara1234", "code": "444444"},
    {"username": "Dan", "email": "dan@example.com", "password": "Dan12345", "code": "555555"},
]

REGISTRATION_VALIDATION_CASES = [
    ("A", "valid@example.com", VALID_PASSWORD, 400),
    ("x" * 51, "valid@example.com", VALID_PASSWORD, 400),
    ("Valid User", "not-an-email", VALID_PASSWORD, 400),
    ("Valid User", "valid@example.com", "short", 400),
    ("Valid User", "valid@example.com", "NoDigitsHere", 400),
    ("Valid User", "valid@example.com", "1234567", 400),
    (" Valid User ", "VALID@EXAMPLE.COM", VALID_PASSWORD, None),
    ("Another User", "another@example.com", "Good1234", None),
]

LOGIN_CASES = [
    {"username": "Login User", "email": "login.user@example.com", "password": VALID_PASSWORD},
    {"username": "Alice Login", "email": "alice.login@example.com", "password": "Alice123"},
    {"username": "Bob Login", "email": "bob.login@example.com", "password": "Bob12345"},
    {"username": "Cory Login", "email": "cory.login@example.com", "password": "Cory1234"},
]

LOGIN_REJECTION_CASES = [
    ("missing@example.com", VALID_PASSWORD, "active", 401),
    ("login.user@example.com", "Wrong123", "active", 401),
    ("login.user@example.com", VALID_PASSWORD, "inactive", 403),
    ("login.user@example.com", VALID_PASSWORD, "suspended", 403),
]

CAMPAIGN_SUBMISSION_CASES = [
    {
        "id": 101,
        "owner_id": 10,
        "title": "Education Support Campaign",
        "category": "education",
        "goal_amount": 5000,
        "description": "This campaign description is long enough for approval.",
        "deadline_days_from_now": 30,
        "workflow_stage": 5,
        "status": "draft",
    },
    {
        "id": 102,
        "owner_id": 11,
        "title": "Medical Recovery Campaign",
        "category": "medical",
        "goal_amount": 8000,
        "description": "This medical campaign description has enough detail for approval.",
        "deadline_days_from_now": 60,
        "workflow_stage": 5,
        "status": "draft",
    },
    {
        "id": 103,
        "owner_id": 12,
        "title": "Community Food Campaign",
        "category": "community",
        "goal_amount": 3000,
        "description": "This community campaign description is sufficiently detailed.",
        "deadline_days_from_now": 20,
        "workflow_stage": 5,
        "status": "draft",
    },
]

INCOMPLETE_CAMPAIGN_SUBMISSION_CASES = [
    ({"goal_amount": None}, True, "Set a fundraising goal before submission."),
    ({"goal_amount": 0}, True, "Set a fundraising goal before submission."),
    ({"description": "too short"}, True, "Campaign description must be at least 20 characters."),
    ({"deadline_days_from_now": None}, True, "Set a campaign deadline before submission."),
    ({"deadline_days_from_now": -1}, True, "Campaign deadline must be a future date."),
    ({}, False, "Upload at least one campaign image before submission."),
]

WORKFLOW_STAGE_CASES = [
    (5, 5, True),
    (6, 5, True),
    (4, 5, False),
    (0, 1, False),
    (3, 3, True),
]

VALID_CAMPAIGN_INFORMATION_CASES = [
    ("Valid Education Title", "education", "education"),
    ("  Trimmed Campaign  ", "medical", "medical"),
    ("Community Help", "other", "other"),
    ("Relief Campaign", "relief", "relief"),
]

INVALID_CAMPAIGN_CATEGORIES = ["unknown-category", "!", "x"]

FUNDRAISER_VALIDATOR_CASES = [
    ("goal", 1),
    ("goal", 5000),
    ("description", "This description is valid enough."),
    ("deadline", "2999-12-31"),
    ("campaign_information", ("Another Valid Title", "education")),
]

ADMIN_APPROVAL_CASES = [
    {
        "id": 201,
        "owner_id": 20,
        "title": "Pending Education Campaign",
        "category": "education",
        "goal_amount": 7500,
        "description": "This pending campaign has all required approval fields.",
        "deadline_days_from_now": 45,
        "workflow_stage": 5,
        "status": "pending",
    },
    {
        "id": 202,
        "owner_id": 21,
        "title": "Pending Medical Campaign",
        "category": "medical",
        "goal_amount": 9500,
        "description": "This pending medical campaign is ready for administrator approval.",
        "deadline_days_from_now": 90,
        "workflow_stage": 5,
        "status": "pending",
    },
    {
        "id": 203,
        "owner_id": 22,
        "title": "Pending Relief Campaign",
        "category": "relief",
        "goal_amount": 4000,
        "description": "This pending relief campaign contains complete required details.",
        "deadline_days_from_now": 15,
        "workflow_stage": 5,
        "status": "pending",
    },
]

NON_PENDING_CAMPAIGN_STATUSES = ["draft", "published", "rejected", "approved"]

MISSING_SUBMISSION_REQUIREMENT_CASES = [
    ({"goal_amount": None}, True),
    ({"description": "short"}, True),
    ({"deadline_days_from_now": None}, True),
    ({"deadline_days_from_now": -2}, True),
    ({}, False),
]

APPROVAL_STATUS_CASES = ["pending", "published", "rejected"]

STATUS_HELPER_INITIAL_STATUSES = ["pending", "approved"]

VALID_CATEGORY_INFORMATION_CASES = [
    ("Education", "Education campaigns", "Education"),
    (" Medical ", "Medical campaigns", "Medical"),
    ("Community", "", "Community"),
    ("Relief", "Short relief category", "Relief"),
    ("Culture", "Culture and arts", "Culture"),
]

INVALID_CATEGORY_INFORMATION_CASES = [
    ("A", "Too short name"),
    ("x" * 81, "Too long name"),
    ("Education", "x" * 301),
    ("", "Missing name"),
    (" ", "Blank name"),
]

VALID_CATEGORY_STATUS_CASES = [
    ("active", "active"),
    ("inactive", "inactive"),
    (" Active ", "active"),
    ("", "active"),
]

INVALID_CATEGORY_STATUSES = ["deleted", "pending", "unknown"]

CREATE_CATEGORY_CASES = [
    ("Education", "Education campaigns"),
    ("Medical", "Medical campaigns"),
    ("Community", ""),
]

DELETE_CATEGORY_USAGE_CASES = [
    (0, True),
    (1, False),
    (5, False),
]

MISSING_CATEGORY_IDS = [1, 99]

DONATION_FILTER_RECORDS = [
    {"id": 1, "user_id": 7, "campaign_id": 101, "amount": 100, "category": "education", "days_ago": 2},
    {"id": 2, "user_id": 7, "campaign_id": 202, "amount": 50, "category": "medical", "days_ago": 3},
    {"id": 3, "user_id": 7, "campaign_id": 101, "amount": 25, "category": "education", "days_ago": 40},
    {"id": 4, "user_id": 7, "campaign_id": 303, "amount": 70, "category": "community", "days_ago": 10},
    {"id": 5, "user_id": 8, "campaign_id": 404, "amount": 90, "category": "education", "days_ago": 1},
]

DONATION_CATEGORY_FILTER_CASES = [
    ("education", {1, 3}),
    ("medical", {2}),
    ("community", {4}),
    ("other", set()),
    (None, {1, 2, 3, 4}),
]

DONATION_DATE_PERIOD_CASES = [
    ("all", {1, 2, 3, 4}),
    ("7d", {1, 2}),
    ("30d", {1, 2, 4}),
    ("90d", {1, 2, 3, 4}),
    ("year", {1, 2, 3, 4}),
]

DONATION_COMBINED_FILTER_CASES = [
    ("education", "all", {1, 3}),
    ("education", "30d", {1}),
    ("medical", "30d", {2}),
    ("community", "7d", set()),
    ("community", "30d", {4}),
]

DONATION_EMPTY_FILTER_CASES = [
    (99, None, "all"),
    (99, "education", "all"),
    (7, "missing", "all"),
    (8, "medical", "all"),
]

UNKNOWN_DATE_PERIOD_CASES = ["", "unknown"]
