"""Integration tests for FastAPI endpoints."""

import pytest
from fastapi import status


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Verify that GET /activities returns all available activities."""
        response = client.get("/activities")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify structure - should be a dict
        assert isinstance(data, dict)
        
        # Verify we have activities (at least the default ones)
        assert len(data) > 0
        
        # Verify required fields in each activity
        for activity_name, activity_data in data.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_has_required_activities(self, client):
        """Verify that default activities are present."""
        response = client.get("/activities")
        data = response.json()
        
        required_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Debate Club",
            "Science Olympiad",
            "Theater Club",
            "Art Studio"
        ]
        
        for activity in required_activities:
            assert activity in data


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client):
        """Verify successful registration for an activity."""
        response = client.post(
            "/activities/Chess Club/signup?email=john@mergington.edu"
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "john@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_adds_participant(self, client):
        """Verify that signup actually adds the participant to the activity."""
        email = "alice@mergington.edu"
        activity = "Programming Class"
        
        # Sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        
        assert email in data[activity]["participants"]

    def test_signup_activity_not_found(self, client):
        """Verify that signup fails with 404 when activity doesn't exist."""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_duplicate_registration(self, client):
        """Verify that a student cannot sign up twice for the same activity."""
        email = "bob@mergington.edu"
        activity = "Gym Class"
        
        # First signup - should succeed
        response1 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response1.status_code == status.HTTP_200_OK
        
        # Second signup - should fail with 400
        response2 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        data = response2.json()
        assert "detail" in data
        assert "already" in data["detail"].lower() or "signed up" in data["detail"].lower()

    def test_signup_multiple_students_same_activity(self, client):
        """Verify that multiple different students can sign up for the same activity."""
        activity = "Basketball Team"
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        # Sign up all students
        for email in emails:
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == status.HTTP_200_OK
        
        # Verify all are registered
        response = client.get("/activities")
        data = response.json()
        participants = data[activity]["participants"]
        
        for email in emails:
            assert email in participants


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_successful(self, client):
        """Verify successful unregistration from an activity."""
        email = "carol@mergington.edu"
        activity = "Tennis Club"
        
        # First sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Then unregister
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]

    def test_unregister_removes_participant(self, client):
        """Verify that unregister actually removes the participant."""
        email = "david@mergington.edu"
        activity = "Debate Club"
        
        # Sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Verify participant is in list
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity]["participants"]
        
        # Unregister
        client.delete(f"/activities/{activity}/unregister?email={email}")
        
        # Verify participant was removed
        response = client.get("/activities")
        data = response.json()
        assert email not in data[activity]["participants"]

    def test_unregister_activity_not_found(self, client):
        """Verify that unregister fails with 404 when activity doesn't exist."""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=test@mergington.edu"
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data

    def test_unregister_student_not_registered(self, client):
        """Verify that unregister fails with 400 when student is not registered."""
        email = "notregistered@mergington.edu"
        activity = "Science Olympiad"
        
        # Try to unregister without being signed up
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data

    def test_unregister_only_removes_specific_participant(self, client):
        """Verify that unregister only removes the requested participant."""
        activity = "Theater Club"
        email1 = "emma@mergington.edu"
        email2 = "frank@mergington.edu"
        
        # Sign up both students
        client.post(f"/activities/{activity}/signup?email={email1}")
        client.post(f"/activities/{activity}/signup?email={email2}")
        
        # Unregister first student
        client.delete(f"/activities/{activity}/unregister?email={email1}")
        
        # Verify only second student remains
        response = client.get("/activities")
        data = response.json()
        participants = data[activity]["participants"]
        
        assert email1 not in participants
        assert email2 in participants


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """Verify that GET / redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert "location" in response.headers
        assert "static/index.html" in response.headers["location"]
