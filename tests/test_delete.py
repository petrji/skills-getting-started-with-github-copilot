"""
Tests for the DELETE /activities/{activity_name}/participants/{email} endpoint.
Uses Arrange-Act-Assert (AAA) pattern.
"""

import pytest


class TestRemoveParticipant:
    """Test suite for DELETE /activities/{activity_name}/participants/{email} endpoint."""

    def test_delete_existing_participant_succeeds(self, client, reset_activities):
        """
        Arrange: Get existing participant from activity
        Act: Send DELETE request to remove participant
        Assert: Verify participant is removed and response indicates success
        """
        # Arrange
        activity_name = "Chess Club"
        activities_data = client.get("/activities").json()
        email_to_remove = activities_data[activity_name]["participants"][0]
        initial_count = len(activities_data[activity_name]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email_to_remove}"
        )

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        
        # Verify participant was removed
        updated_activities = client.get("/activities").json()
        updated_participants = updated_activities[activity_name]["participants"]
        assert len(updated_participants) == initial_count - 1
        assert email_to_remove not in updated_participants

    def test_delete_nonexistent_participant_returns_400(self, client, reset_activities):
        """
        Arrange: Prepare email not registered for activity
        Act: Attempt to delete non-existent participant
        Assert: Verify 400 response
        """
        # Arrange
        activity_name = "Chess Club"
        nonexistent_email = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{nonexistent_email}"
        )

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result

    def test_delete_from_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        Arrange: Prepare non-existent activity name and email
        Act: Attempt to delete from invalid activity
        Assert: Verify 404 response
        """
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants/{email}"
        )

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result

    def test_delete_last_participant_from_activity(self, client, reset_activities):
        """
        Arrange: Get an activity with one participant and remove them
        Act: Delete the only participant
        Assert: Verify participant removed, activity still exists with empty list
        """
        # Arrange
        # First sign up only one person to an activity
        activity_name = "Gym Class"
        single_email = "solo@mergington.edu"
        
        # Sign them up
        client.post(
            f"/activities/{activity_name}/signup?email={single_email}",
            json={}
        )
        
        # Get initial state
        activities_before = client.get("/activities").json()
        participants_before = activities_before[activity_name]["participants"]

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{single_email}"
        )

        # Assert
        assert response.status_code == 200
        
        # Verify activity still exists but participant removed
        activities_after = client.get("/activities").json()
        assert activity_name in activities_after
        assert single_email not in activities_after[activity_name]["participants"]

    def test_delete_multiple_participants_sequentially(self, client, reset_activities):
        """
        Arrange: Set up activity with multiple participants
        Act: Delete participants one at a time
        Assert: Verify each deletion works correctly
        """
        # Arrange
        activity_name = "Gym Class"
        new_emails = ["first@mergington.edu", "second@mergington.edu", "third@mergington.edu"]
        
        # Add participants
        for email in new_emails:
            client.post(
                f"/activities/{activity_name}/signup?email={email}",
                json={}
            )

        # Act & Assert
        for i, email_to_delete in enumerate(new_emails):
            response = client.delete(
                f"/activities/{activity_name}/participants/{email_to_delete}"
            )
            assert response.status_code == 200
            
            # Verify it's gone
            activities = client.get("/activities").json()
            assert email_to_delete not in activities[activity_name]["participants"]
            # Verify others remain
            for remaining_email in new_emails[i+1:]:
                assert remaining_email in activities[activity_name]["participants"]

    def test_delete_and_resign_same_participant(self, client, reset_activities):
        """
        Arrange: Sign up a participant, then delete them
        Act: Sign up the same person again after deletion
        Assert: Verify re-signup succeeds (no lingering state)
        """
        # Arrange
        activity_name = "Chess Club"
        email = "returner@mergington.edu"
        
        # Initial signup
        client.post(
            f"/activities/{activity_name}/signup?email={email}",
            json={}
        )
        activities_after_first_signup = client.get("/activities").json()
        initial_count = len(activities_after_first_signup[activity_name]["participants"])

        # Act - Delete
        delete_response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        assert delete_response.status_code == 200
        
        # Act - Re-signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            json={}
        )

        # Assert
        assert signup_response.status_code == 200
        final_activities = client.get("/activities").json()
        assert email in final_activities[activity_name]["participants"]
        assert len(final_activities[activity_name]["participants"]) == initial_count
