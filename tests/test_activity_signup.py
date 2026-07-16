import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = original


@pytest.fixture()
def client():
    return TestClient(app_module.app)


def test_duplicate_signup_is_rejected(client):
    first_response = client.post(
        "/activities/Chess Club/signup?email=test@example.com"
    )
    assert first_response.status_code == 200

    second_response = client.post(
        "/activities/Chess Club/signup?email=test@example.com"
    )
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_participant_removes_email(client):
    response = client.delete(
        "/activities/Chess Club/signup?email=michael@mergington.edu"
    )

    assert response.status_code == 200
    assert "michael@mergington.edu" not in app_module.activities["Chess Club"]["participants"]
