import pytest
from fastapi import HTTPException

from models.admin import Category
from services.admin_service import CategoryController

from tests.helpers import FakeSession, make_category
from tests.test_data import (
    CREATE_CATEGORY_CASES,
    DELETE_CATEGORY_USAGE_CASES,
    INVALID_CATEGORY_INFORMATION_CASES,
    INVALID_CATEGORY_STATUSES,
    MISSING_CATEGORY_IDS,
    VALID_CATEGORY_INFORMATION_CASES,
    VALID_CATEGORY_STATUS_CASES,
)


@pytest.mark.parametrize("name,description,expected_name", VALID_CATEGORY_INFORMATION_CASES)
def test_validate_category_information_accepts_valid_data(name, description, expected_name):
    clean_name, clean_description = CategoryController.ValidateCategoryInformation(name, description)
    assert clean_name == expected_name
    assert clean_description == description.strip()


@pytest.mark.parametrize("name,description", INVALID_CATEGORY_INFORMATION_CASES)
def test_validate_category_information_rejects_invalid_data(name, description):
    with pytest.raises(HTTPException) as error:
        CategoryController.ValidateCategoryInformation(name, description)
    assert error.value.status_code == 400


@pytest.mark.parametrize("status,expected_status", VALID_CATEGORY_STATUS_CASES)
def test_validate_updated_information_accepts_status(status, expected_status):
    clean_name, _clean_description, clean_status = CategoryController.ValidateUpdatedInformation(
        "Education",
        "Education campaigns",
        status,
    )
    assert clean_name == "Education"
    assert clean_status == expected_status


@pytest.mark.parametrize("status", INVALID_CATEGORY_STATUSES)
def test_validate_updated_information_rejects_invalid_status(status):
    with pytest.raises(HTTPException) as error:
        CategoryController.ValidateUpdatedInformation("Education", "", status)
    assert error.value.status_code == 400


@pytest.mark.parametrize("name,description", CREATE_CATEGORY_CASES)
def test_create_category_uses_hardcoded_data(name, description):
    session = FakeSession()

    category = CategoryController.CreateCategory(session, name, description)

    assert category.name == name
    assert category.description == description
    assert category in session.added
    assert session.commits == 1


@pytest.mark.parametrize("campaign_count,should_delete", DELETE_CATEGORY_USAGE_CASES)
def test_delete_category_respects_campaign_usage(monkeypatch, campaign_count, should_delete):
    session = FakeSession()
    category = make_category()
    monkeypatch.setattr(Category, "GetCategoryById", staticmethod(lambda _session, _category_id: category))
    monkeypatch.setattr(
        CategoryController,
        "GetCategoryCampaignCount",
        staticmethod(lambda _session, _category_value: campaign_count),
    )

    if should_delete:
        CategoryController.DeleteCategory(session, category.id)
        assert category in session.deleted
        assert session.commits == 1
        return

    with pytest.raises(HTTPException) as error:
        CategoryController.DeleteCategory(session, category.id)
    assert error.value.status_code == 400


@pytest.mark.parametrize("category_id", MISSING_CATEGORY_IDS)
def test_delete_category_rejects_missing_category(monkeypatch, category_id):
    session = FakeSession()
    monkeypatch.setattr(Category, "GetCategoryById", staticmethod(lambda _session, _category_id: None))

    with pytest.raises(HTTPException) as error:
        CategoryController.DeleteCategory(session, category_id)
    assert error.value.status_code == 404
