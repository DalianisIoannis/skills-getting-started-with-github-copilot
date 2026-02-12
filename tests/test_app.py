"""Tests for the Mergington High School Activities API"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Create test client
client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]
    activities["Programming Class"]["participants"] = ["emma@mergington.edu", "sophia@mergington.edu"]
    activities["Gym Class"]["participants"] = ["john@mergington.edu", "olivia@mergington.edu"]
    activities["Basketball Team"]["participants"] = ["alex@mergington.edu"]
    activities["Tennis Club"]["participants"] = ["sarah@mergington.edu"]
    activities["Art Studio"]["participants"] = ["isabella@mergington.edu", "lucas@mergington.edu"]
    activities["Drama Club"]["participants"] = ["noah@mergington.edu"]
    activities["Debate Team"]["participants"] = ["ava@mergington.edu", "ethan@mergington.edu"]
    activities["Science Club"]["participants"] = ["mia@mergington.edu"]
    yield
    # Reset after test
    activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]
    activities["Programming Class"]["participants"] = ["emma@mergington.edu", "sophia@mergington.edu"]
    activities["Gym Class"]["participants"] = ["john@mergington.edu", "olivia@mergington.edu"]
    activities["Basketball Team"]["participants"] = ["alex@mergington.edu"]
    activities["Tennis Club"]["participants"] = ["sarah@mergington.edu"]
    activities["Art Studio"]["participants"] = ["isabella@mergington.edu", "lucas@mergington.edu"]
    activities["Drama Club"]["participants"] = ["noah@mergington.edu"]
    activities["Debate Team"]["participants"] = ["ava@mergington.edu", "ethan@mergington.edu"]
    activities["Science Club"]["participants"] = ["mia@mergington.edu"]


class TestApiEndpoints:
    """Test API endpoints"""

    def test_get_activities(self):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_contains_required_fields(self):
        """Test that activities have required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_signup_for_activity_success(self, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_for_activity_duplicate(self, reset_activities):
        """Test that duplicate signups are rejected"""
        # First signup should succeed
        response1 = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response1.status_code == 200

        # Second signup with same email should fail
        response2 = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_for_nonexistent_activity(self):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_from_activity_success(self, reset_activities):
        """Test successful unregister from an activity"""
        # First, get the initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])

        # Unregister
        response = client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

        # Verify participant was removed
        response = client.get("/activities")
        new_count = len(response.json()["Chess Club"]["participants"])
        assert new_count == initial_count - 1
        assert "michael@mergington.edu" not in response.json()["Chess Club"]["participants"]

    def test_unregister_from_nonexistent_activity(self):
        """Test unregister from non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404

    def test_unregister_not_signed_up_participant(self, reset_activities):
        """Test unregister for participant not signed up"""
        response = client.post(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_root_redirect(self):
        """Test root path redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestActivityCapacity:
    """Test activity capacity constraints"""

    def test_activity_max_participants_field(self):
        """Test that activities have max_participants field"""
        response = client.get("/activities")
        data = response.json()
        for activity_name, activity_data in data.items():
            assert "max_participants" in activity_data
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0

    def test_activity_participants_list(self):
        """Test that participants list is present in each activity"""
        response = client.get("/activities")
        data = response.json()
        for activity_name, activity_data in data.items():
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
