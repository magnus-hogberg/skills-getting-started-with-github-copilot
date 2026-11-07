from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


TEST_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 2,
        "participants": ["alex@mergington.edu"],
    },
    "Drama Club": {
        "description": "Explore acting and stage performance",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 10,
        "participants": [],
    },
}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(app_module, "activities", deepcopy(TEST_ACTIVITIES))
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_all_activity_details(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == TEST_ACTIVITIES


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Drama Club/signup",
        params={"email": "sam@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up sam@mergington.edu for Drama Club"}
    assert "sam@mergington.edu" in client.get("/activities").json()["Drama Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "alex@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "sam@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client):
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "alex@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Removed alex@mergington.edu from Chess Club"}
    assert "alex@mergington.edu" not in client.get("/activities").json()["Chess Club"]["participants"]


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Club/signup",
        params={"email": "sam@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_rejects_unregistered_participant(client):
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "sam@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
