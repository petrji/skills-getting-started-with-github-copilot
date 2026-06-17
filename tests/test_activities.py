"""
Tests for the GET /activities endpoint.
Uses Arrange-Act-Assert (AAA) pattern.
"""

import pytest


class TestGetActivities:
    """Test suite for GET /activities endpoint."""

    def test_get_all_activities_returns_success(self, client, reset_activities):
        """
        Arrange: Set up client and reset activity state
        Act: Send GET request to /activities
        Assert: Verify response status is 200 and contains all activities
        """
        # Arrange
        expected_activity_count = 3

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == expected_activity_count
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_activity_has_required_fields(self, client, reset_activities):
        """
        Arrange: Retrieve activities data
        Act: Fetch /activities endpoint
        Assert: Verify each activity contains required fields
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert required_fields.issubset(activity_data.keys()), \
                f"Activity {activity_name} missing required fields"

    def test_activity_participants_is_list(self, client, reset_activities):
        """
        Arrange: Set up test expectations
        Act: Get activities data
        Assert: Verify participants field is a list for all activities
        """
        # Arrange
        expected_type = list

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], expected_type), \
                f"Activity {activity_name} participants should be a list"
            assert isinstance(activity_data["max_participants"], int)

    def test_activity_participants_contains_emails(self, client, reset_activities):
        """
        Arrange: Set up test data
        Act: Fetch activities
        Assert: Verify participants list contains email addresses
        """
        # Arrange
        # No special setup needed

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                assert "@" in participant, \
                    f"Participant '{participant}' in {activity_name} should be an email"
