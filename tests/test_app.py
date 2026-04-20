import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities_returns_all_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()

    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_signup_for_activity_adds_participant():
    email = "newstudent@mergington.edu"
    response = client.post(
        f"/activities/{quote('Chess Club')}/signup?email={quote(email)}"
    )

    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    assert email in activities["Chess Club"]["participants"]


def test_unregister_from_activity_removes_participant():
    email = "michael@mergington.edu"
    assert email in activities["Chess Club"]["participants"]

    response = client.delete(
        f"/activities/{quote('Chess Club')}/signup?email={quote(email)}"
    )

    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]
    assert email not in activities["Chess Club"]["participants"]


def test_signup_nonexistent_activity_returns_404():
    response = client.post(
        f"/activities/{quote('Nonexistent Activity')}/signup?email={quote('test@mergington.edu')}"
    )
    assert response.status_code == 404


def test_unregister_missing_participant_returns_404():
    response = client.delete(
        f"/activities/{quote('Gym Class')}/signup?email={quote('notregistered@mergington.edu')}"
    )
    assert response.status_code == 404
