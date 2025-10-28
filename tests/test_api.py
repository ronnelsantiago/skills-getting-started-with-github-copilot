from fastapi.testclient import TestClient
from urllib.parse import quote

from src.app import app, activities


client = TestClient(app)


def test_get_activities_returns_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Should be a mapping and contain some known activities from the in-memory store
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_remove_participant_flow():
    activity = "Chess Club"
    test_email = "test_user@example.com"

    # Ensure test email is not present to start
    if test_email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(test_email)

    # Sign up the test email
    signup_path = f"/activities/{quote(activity)}/signup?email={quote(test_email)}"
    resp = client.post(signup_path)
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")

    # Verify participant is now present in the in-memory store
    assert test_email in activities[activity]["participants"]

    # Now remove the participant using DELETE
    delete_path = f"/activities/{quote(activity)}/participants?email={quote(test_email)}"
    resp = client.delete(delete_path)
    assert resp.status_code == 200
    body = resp.json()
    assert "Removed" in body.get("message", "")

    # Verify participant removed
    assert test_email not in activities[activity]["participants"]


def test_signup_nonexistent_activity_returns_404():
    activity = "Nonexistent Activity"
    test_email = "noone@example.com"
    signup_path = f"/activities/{quote(activity)}/signup?email={quote(test_email)}"
    resp = client.post(signup_path)
    assert resp.status_code == 404


def test_signup_duplicate_returns_400():
    activity = "Chess Club"
    test_email = "duplicate_user@example.com"

    # Ensure clean start
    if test_email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(test_email)

    # First signup should succeed
    resp = client.post(f"/activities/{quote(activity)}/signup?email={quote(test_email)}")
    assert resp.status_code == 200

    # Duplicate signup should fail with 400
    resp = client.post(f"/activities/{quote(activity)}/signup?email={quote(test_email)}")
    assert resp.status_code == 400

    # Cleanup
    client.delete(f"/activities/{quote(activity)}/participants?email={quote(test_email)}")


def test_remove_nonexistent_participant_returns_404():
    activity = "Chess Club"
    test_email = "not_in_list@example.com"

    # Ensure the participant is not in the list
    if test_email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(test_email)

    delete_path = f"/activities/{quote(activity)}/participants?email={quote(test_email)}"
    resp = client.delete(delete_path)
    assert resp.status_code == 404


def test_remove_from_nonexistent_activity_returns_404():
    activity = "NoSuchActivity"
    test_email = "someone@example.com"
    delete_path = f"/activities/{quote(activity)}/participants?email={quote(test_email)}"
    resp = client.delete(delete_path)
    assert resp.status_code == 404
