import os

os.environ.setdefault("GITHUB_ACTIONS", "true")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("EMAIL_DELIVERY_MODE", "demo")

import pytest


class DummyRequest:
    def __init__(self):
        self.session = {}


@pytest.fixture()
def dummy_request():
    return DummyRequest()
