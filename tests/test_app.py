import copy
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    activities.clear()
    activities.update(copy.deepcopy(original))
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


@pytest.fixture()
def client():
    return TestClient(app)


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_catalog(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["max_participants"] == 12
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]


def test_signup_for_activity_adds_participant(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up newstudent@mergington.edu for Chess Club"
    }
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_for_unknown_activity_returns_404(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
