"""
Tests for the POST /activities/{activity_name}/signup endpoint.
Uses Arrange-Act-Assert (AAA) pattern.
"""

import pytest


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant_succeeds(self, client, reset_activities):
        """
        Arrange: Prepare a new email not yet registered
        Act: Send POST signup request
        Assert: Verify participant is added and response indicates success
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        initial_participants = client.get("/activities").json()[activity_name]["participants"]
        initial_count = len(initial_participants)

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}",
            json={}
        )

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        
        # Verify participant was added
        updated_activities = client.get("/activities").json()
        updated_participants = updated_activities[activity_name]["participants"]
        assert len(updated_participants) == initial_count + 1
        assert new_email in updated_participants

    def test_signup_duplicate_participant_rejected(self, client, reset_activities):
        """
        Arrange: Get existing participant from an activity
        Act: Attempt to sign up the same participant again
        Assert: Verify request is rejected with 400 status
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = client.get("/activities").json()[activity_name]["participants"][0]

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_email}",
            json={}
        )

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "already" in result["detail"].lower()

    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        Arrange: Prepare a non-existent activity name
        Act: Attempt to sign up for invalid activity
        Assert: Verify 404 response
        """
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        test_email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup?email={test_email}",
            json={}
        )

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result

    def test_signup_multiple_participants_to_same_activity(self, client, reset_activities):
        """
        Arrange: Prepare multiple new emails for same activity
        Act: Sign up each new participant sequentially
        Assert: Verify all participants are added successfully
        """
        # Arrange
        activity_name = "Gym Class"
        new_emails = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]

        # Act
        responses = []
        for email in new_emails:
            response = client.post(
                f"/activities/{activity_name}/signup?email={email}",
                json={}
            )
            responses.append(response)

        # Assert
        for response in responses:
            assert response.status_code == 200
        
        # Verify all were added
        final_participants = client.get("/activities").json()[activity_name]["participants"]
        for email in new_emails:
            assert email in final_participants

    def test_signup_different_activities_independent(self, client, reset_activities):
        """
        Arrange: Prepare same email for different activities
        Act: Sign up same email to two different activities
        Assert: Verify same email can be registered to multiple activities
        """
        # Arrange
        email = "versatile@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Gym Class"

        # Act
        response1 = client.post(
            f"/activities/{activity1}/signup?email={email}",
            json={}
        )
        response2 = client.post(
            f"/activities/{activity2}/signup?email={email}",
            json={}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities = client.get("/activities").json()
        assert email in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]
