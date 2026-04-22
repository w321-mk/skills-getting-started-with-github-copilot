"""
Test suite for Mergington High School API

Tests cover all endpoints with the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the API call
- Assert: Verify the response
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from src.app import activities as app_activities
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for all skill levels",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in friendly matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["alex@mergington.edu", "sarah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in plays and musicals throughout the school year",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["isabella@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["ryan@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Wednesdays, 4:00 PM - 5:00 PM",
            "max_participants": 22,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        }
    }
    # Clear and restore activities
    app_activities.clear()
    for key, value in original_activities.items():
        app_activities[key] = value.copy()
        app_activities[key]["participants"] = value["participants"].copy()
    
    yield
    
    # Teardown: reset again
    app_activities.clear()
    for key, value in original_activities.items():
        app_activities[key] = value.copy()
        app_activities[key]["participants"] = value["participants"].copy()


class TestRootEndpoint:
    """Tests for the GET / endpoint"""
    
    def test_root_redirects_to_index(self, client):
        """
        Arrange: Set up the test client
        Act: Make a GET request to the root endpoint
        Assert: Verify the response is a redirect to /static/index.html
        """
        # Arrange
        expected_redirect_url = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect_url


class TestGetActivitiesEndpoint:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """
        Arrange: Set up expected activities in the database
        Act: Send GET request to /activities
        Assert: Verify all activities are returned with correct structure
        """
        # Arrange
        expected_activity_names = {
            "Chess Club", "Programming Class", "Gym Class", 
            "Basketball Team", "Tennis Club", "Drama Club",
            "Art Studio", "Debate Team", "Science Club"
        }
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert set(activities.keys()) == expected_activity_names
        
        # Verify structure of each activity
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_returns_correct_activity_details(self, client, reset_activities):
        """
        Arrange: Know the expected details for a specific activity
        Act: Fetch all activities and check a specific one
        Assert: Verify the activity details match expected values
        """
        # Arrange
        activity_name = "Chess Club"
        expected_description = "Learn strategies and compete in chess tournaments"
        expected_schedule = "Fridays, 3:30 PM - 5:00 PM"
        expected_max_participants = 12
        expected_initial_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities[activity_name]
        
        # Assert
        assert chess_club["description"] == expected_description
        assert chess_club["schedule"] == expected_schedule
        assert chess_club["max_participants"] == expected_max_participants
        assert chess_club["participants"] == expected_initial_participants


class TestSignupForActivityEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_activity_successful(self, client, reset_activities):
        """
        Arrange: Select an activity with available spots and a new email
        Act: Send POST request to signup endpoint with valid data
        Assert: Verify the student is added and success message is returned
        """
        # Arrange
        activity_name = "Programming Class"
        new_student_email = "new_student@mergington.edu"
        expected_message = f"Signed up {new_student_email} for {activity_name}"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_student_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == expected_message
        
        # Verify student was actually added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert new_student_email in activities[activity_name]["participants"]
    
    def test_signup_for_activity_not_found(self, client):
        """
        Arrange: Reference a non-existent activity
        Act: Send POST request with invalid activity name
        Assert: Verify 404 error with appropriate message
        """
        # Arrange
        non_existent_activity = "Nonexistent Activity"
        student_email = "student@mergington.edu"
        expected_status_code = 404
        expected_detail = "Activity not found"
        
        # Act
        response = client.post(
            f"/activities/{non_existent_activity}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == expected_status_code
        assert response.json()["detail"] == expected_detail
    
    def test_signup_already_signed_up(self, client, reset_activities):
        """
        Arrange: Identify a student already signed up for an activity
        Act: Attempt to sign up that student again
        Assert: Verify 400 error indicating student is already signed up
        """
        # Arrange
        activity_name = "Tennis Club"
        existing_student_email = "alex@mergington.edu"  # Already signed up
        expected_status_code = 400
        expected_detail = "Student already signed up for this activity"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_student_email}
        )
        
        # Assert
        assert response.status_code == expected_status_code
        assert response.json()["detail"] == expected_detail
    
    def test_signup_activity_is_full(self, client, reset_activities):
        """
        Arrange: Create an activity at max capacity and prepare a new student
        Act: Attempt to sign up new student to full activity
        Assert: Verify 400 error indicating activity is full
        """
        # Arrange
        from src.app import activities as app_activities
        activity_name = "Tennis Club"
        new_student_email = "overflowing_student@mergington.edu"
        
        # Fill up Tennis Club (max is 10, currently has 2)
        activity = app_activities[activity_name]
        for i in range(activity["max_participants"] - len(activity["participants"])):
            activity["participants"].append(f"temp_student_{i}@mergington.edu")
        
        assert len(activity["participants"]) == activity["max_participants"]
        
        expected_status_code = 400
        expected_detail = "Activity is full"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_student_email}
        )
        
        # Assert
        assert response.status_code == expected_status_code
        assert response.json()["detail"] == expected_detail
    
    def test_signup_multiple_students_same_activity(self, client, reset_activities):
        """
        Arrange: Prepare multiple new students to enroll in the same activity
        Act: Sign up each student sequentially
        Assert: Verify all students are successfully added to the activity
        """
        # Arrange
        activity_name = "Gym Class"
        new_students = [
            "student1@test.edu",
            "student2@test.edu",
            "student3@test.edu"
        ]
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]
        initial_count = len(initial_participants)
        
        # Act
        for student_email in new_students:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": student_email}
            )
            assert response.status_code == 200
        
        # Assert
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity_name]["participants"]
        
        assert len(final_participants) == initial_count + len(new_students)
        for student_email in new_students:
            assert student_email in final_participants
    
    def test_signup_different_students_different_activities(self, client, reset_activities):
        """
        Arrange: Prepare multiple students enrolling in different activities
        Act: Sign up each student to different activities
        Assert: Verify each student is in their respective activity
        """
        # Arrange
        enrollments = {
            "Chess Club": "chess_enthusiast@test.edu",
            "Drama Club": "drama_lover@test.edu",
            "Science Club": "science_nerd@test.edu"
        }
        
        # Act
        for activity_name, student_email in enrollments.items():
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": student_email}
            )
            assert response.status_code == 200
        
        # Assert
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        for activity_name, student_email in enrollments.items():
            assert student_email in activities[activity_name]["participants"]
    
    def test_signup_case_sensitive_activity_name(self, client):
        """
        Arrange: Reference activity with different case than stored
        Act: Send POST request with incorrect case
        Assert: Verify request fails with 404 (case-sensitive matching)
        """
        # Arrange
        incorrect_case_activity = "chess club"  # lowercase instead of "Chess Club"
        student_email = "case_test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{incorrect_case_activity}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestUnregisterFromActivityEndpoint:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_from_activity_successful(self, client, reset_activities):
        """
        Arrange: Select an activity and an existing participant
        Act: Send DELETE request to unregister endpoint
        Assert: Verify the student is removed and success message is returned
        """
        # Arrange
        activity_name = "Chess Club"
        student_email = "michael@mergington.edu"  # Already signed up
        expected_message = f"Unregistered {student_email} from {activity_name}"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == expected_message
        
        # Verify student was actually removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert student_email not in activities[activity_name]["participants"]
    
    def test_unregister_activity_not_found(self, client):
        """
        Arrange: Reference a non-existent activity
        Act: Send DELETE request with invalid activity name
        Assert: Verify 404 error with appropriate message
        """
        # Arrange
        non_existent_activity = "Nonexistent Activity"
        student_email = "student@mergington.edu"
        expected_status_code = 404
        expected_detail = "Activity not found"
        
        # Act
        response = client.delete(
            f"/activities/{non_existent_activity}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == expected_status_code
        assert response.json()["detail"] == expected_detail
    
    def test_unregister_student_not_signed_up(self, client, reset_activities):
        """
        Arrange: Select an activity and a student not signed up for it
        Act: Attempt to unregister the student
        Assert: Verify 400 error indicating student is not signed up
        """
        # Arrange
        activity_name = "Programming Class"
        not_signed_up_email = "not_signed_up@mergington.edu"
        expected_status_code = 400
        expected_detail = "Student is not signed up for this activity"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": not_signed_up_email}
        )
        
        # Assert
        assert response.status_code == expected_status_code
        assert response.json()["detail"] == expected_detail
    
    def test_unregister_multiple_students(self, client, reset_activities):
        """
        Arrange: Select an activity with multiple participants
        Act: Unregister several students sequentially
        Assert: Verify all students are successfully removed
        """
        # Arrange
        activity_name = "Programming Class"
        students_to_remove = ["emma@mergington.edu", "sophia@mergington.edu"]
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]
        initial_count = len(initial_participants)
        
        # Act
        for student_email in students_to_remove:
            response = client.delete(
                f"/activities/{activity_name}/unregister",
                params={"email": student_email}
            )
            assert response.status_code == 200
        
        # Assert
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity_name]["participants"]
        
        assert len(final_participants) == initial_count - len(students_to_remove)
        for student_email in students_to_remove:
            assert student_email not in final_participants
    
    def test_unregister_case_sensitive_activity_name(self, client):
        """
        Arrange: Reference activity with different case than stored
        Act: Send DELETE request with incorrect case
        Assert: Verify request fails with 404 (case-sensitive matching)
        """
        # Arrange
        incorrect_case_activity = "programming class"  # lowercase instead of "Programming Class"
        student_email = "emma@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{incorrect_case_activity}/unregister",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
