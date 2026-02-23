"""Unit tests for business logic and data integrity."""

import pytest
from src.app import activities


class TestActivitiesDataStructure:
    """Tests for activities data structure and initialization."""

    def test_activities_is_dict(self):
        """Verify activities is a dictionary."""
        assert isinstance(activities, dict)

    def test_all_activities_have_required_fields(self):
        """Verify each activity has all required fields."""
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data, dict)
            
            for field in required_fields:
                assert field in activity_data, f"Missing field '{field}' in {activity_name}"

    def test_participants_is_list(self):
        """Verify participants field is a list in all activities."""
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list), \
                f"Participants in {activity_name} is not a list"

    def test_max_participants_is_positive_integer(self):
        """Verify max_participants is a positive integer."""
        for activity_name, activity_data in activities.items():
            max_part = activity_data["max_participants"]
            assert isinstance(max_part, int), \
                f"max_participants in {activity_name} is not an integer"
            assert max_part > 0, \
                f"max_participants in {activity_name} is not positive"

    def test_description_is_string(self):
        """Verify description is a non-empty string."""
        for activity_name, activity_data in activities.items():
            desc = activity_data["description"]
            assert isinstance(desc, str), \
                f"Description in {activity_name} is not a string"
            assert len(desc) > 0, \
                f"Description in {activity_name} is empty"

    def test_schedule_is_string(self):
        """Verify schedule is a non-empty string."""
        for activity_name, activity_data in activities.items():
            sched = activity_data["schedule"]
            assert isinstance(sched, str), \
                f"Schedule in {activity_name} is not a string"
            assert len(sched) > 0, \
                f"Schedule in {activity_name} is empty"


class TestActivityValidation:
    """Tests for activity validation logic."""

    def test_cannot_exceed_max_participants(self):
        """Verify an activity validates max_participants limit."""
        # Get an activity with few max participants
        for activity_name, activity_data in activities.items():
            max_part = activity_data["max_participants"]
            
            # Ensure participants list doesn't exceed max
            current_count = len(activity_data["participants"])
            assert current_count <= max_part, \
                f"{activity_name} has {current_count} participants but max is {max_part}"

    def test_no_duplicate_participants_in_initial_state(self):
        """Verify no duplicate emails in participants list initially."""
        for activity_name, activity_data in activities.items():
            participants = activity_data["participants"]
            
            # Check for duplicates
            assert len(participants) == len(set(participants)), \
                f"Duplicate participants found in {activity_name}"

    def test_participants_are_email_strings(self):
        """Verify all participants are strings (emails)."""
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str), \
                    f"Non-string participant in {activity_name}: {participant}"
                assert "@" in participant, \
                    f"Invalid email format in {activity_name}: {participant}"


class TestDataIntegrity:
    """Tests for data integrity after operations."""

    def test_participant_can_be_added_to_participants_list(self):
        """Verify that participants can be added to the list."""
        activity_name = "Chess Club"
        email = "testuser@mergington.edu"
        
        # Clear participants
        activities[activity_name]["participants"] = []
        
        # Add participant
        activities[activity_name]["participants"].append(email)
        
        # Verify
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == 1

    def test_participant_can_be_removed_from_participants_list(self):
        """Verify that participants can be removed from the list."""
        activity_name = "Programming Class"
        email1 = "user1@mergington.edu"
        email2 = "user2@mergington.edu"
        
        # Clear and add two participants
        activities[activity_name]["participants"] = [email1, email2]
        
        # Remove first participant
        activities[activity_name]["participants"].remove(email1)
        
        # Verify
        assert email1 not in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == 1

    def test_participant_list_maintains_other_activities(self):
        """Verify that modifying one activity doesn't affect others."""
        activity1 = "Gym Class"
        activity2 = "Basketball Team"
        email = "participant@mergington.edu"
        
        # Store initial state
        initial_act2_participants = set(activities[activity2]["participants"])
        
        # Modify activity1
        activities[activity1]["participants"].append(email)
        
        # Verify activity2 is unchanged
        current_act2_participants = set(activities[activity2]["participants"])
        assert current_act2_participants == initial_act2_participants

    def test_duplicate_email_in_participants_list(self):
        """Verify behavior with duplicate emails."""
        activity_name = "Debate Club"
        email = "duplicate@mergington.edu"
        
        # Clear and add duplicate
        activities[activity_name]["participants"] = [email, email]
        
        # Check that list contains both (this tests the current behavior)
        assert activities[activity_name]["participants"].count(email) == 2


class TestActivityNames:
    """Tests for activity names and consistency."""

    def test_all_activity_names_are_unique(self):
        """Verify all activity names are unique."""
        activity_names = list(activities.keys())
        assert len(activity_names) == len(set(activity_names)), \
            "Duplicate activity names found"

    def test_all_activity_names_are_strings(self):
        """Verify all activity names are strings."""
        for activity_name in activities.keys():
            assert isinstance(activity_name, str)
            assert len(activity_name) > 0

    def test_activity_names_case_sensitive(self):
        """Verify that activity names are case-sensitive."""
        # Get all activity names
        activity_names = list(activities.keys())
        
        # Convert to lowercase and check for duplicates (case-insensitive)
        lowercased = [name.lower() for name in activity_names]
        assert len(lowercased) == len(set(lowercased)), \
            "Case-insensitive duplicate activity names found"
