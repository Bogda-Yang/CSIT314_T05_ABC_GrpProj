import pytest

from models.donation import DonationRecord
from services.donation_service import DonationFilterController

from tests.helpers import FakeSession, filter_hardcoded_donations
from tests.test_data import (
    DONATION_CATEGORY_FILTER_CASES,
    DONATION_COMBINED_FILTER_CASES,
    DONATION_DATE_PERIOD_CASES,
    DONATION_EMPTY_FILTER_CASES,
    UNKNOWN_DATE_PERIOD_CASES,
)


@pytest.fixture(autouse=True)
def patch_donation_records(monkeypatch):
    monkeypatch.setattr(
        DonationRecord,
        "GetFilteredDonations",
        staticmethod(filter_hardcoded_donations),
    )


@pytest.mark.parametrize("category,expected_ids", DONATION_CATEGORY_FILTER_CASES)
def test_filter_donations_by_category(category, expected_ids):
    records = DonationFilterController.RetrieveFilteredDonationRecords(
        FakeSession(),
        7,
        category=category,
        date_period="all",
    )
    assert {record.id for record in records} == expected_ids


@pytest.mark.parametrize("date_period,expected_ids", DONATION_DATE_PERIOD_CASES)
def test_filter_donations_by_date_period(date_period, expected_ids):
    records = DonationFilterController.RetrieveFilteredDonationRecords(
        FakeSession(),
        7,
        category=None,
        date_period=date_period,
    )
    assert {record.id for record in records} == expected_ids


@pytest.mark.parametrize("category,date_period,expected_ids", DONATION_COMBINED_FILTER_CASES)
def test_filter_donations_by_category_and_date_period(category, date_period, expected_ids):
    records = DonationFilterController.RetrieveFilteredDonationRecords(
        FakeSession(),
        7,
        category=category,
        date_period=date_period,
    )
    assert {record.id for record in records} == expected_ids


@pytest.mark.parametrize("user_id,category,date_period", DONATION_EMPTY_FILTER_CASES)
def test_filter_donations_returns_empty_when_no_records_match(user_id, category, date_period):
    records = DonationFilterController.RetrieveFilteredDonationRecords(
        FakeSession(),
        user_id,
        category=category,
        date_period=date_period,
    )
    assert records == []


@pytest.mark.parametrize("date_period", UNKNOWN_DATE_PERIOD_CASES)
def test_unknown_date_period_behaves_like_all_time(date_period):
    records = DonationFilterController.RetrieveFilteredDonationRecords(
        FakeSession(),
        7,
        category=None,
        date_period=date_period,
    )
    assert {record.id for record in records} == {1, 2, 3, 4}
