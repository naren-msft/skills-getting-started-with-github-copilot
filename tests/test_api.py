"""
Tests for the main API endpoints of the Mergington High School Activities system.
"""

def test_root_redirect(client):
    """Test that the root endpoint redirects to the static index.html."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test getting all activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    
    # Check structure of activity data
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_for_activity_success(client):
    """Test successful signup for an activity."""
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity in data["message"]
    
    # Verify the participant was added
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email in activities_data[activity]["participants"]


def test_signup_for_nonexistent_activity(client):
    """Test signup for an activity that doesn't exist."""
    email = "student@mergington.edu"
    activity = "Nonexistent Club"
    
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 404
    
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_signup_duplicate_participant(client):
    """Test that a student cannot sign up twice for the same activity."""
    email = "michael@mergington.edu"  # Already signed up for Chess Club
    activity = "Chess Club"
    
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    
    data = response.json()
    assert data["detail"] == "Student already signed up"


def test_remove_participant_success(client):
    """Test successful removal of a participant from an activity."""
    email = "michael@mergington.edu"  # Already signed up for Chess Club
    activity = "Chess Club"
    
    response = client.delete(f"/activities/{activity}/remove?email={email}")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity in data["message"]
    
    # Verify the participant was removed
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email not in activities_data[activity]["participants"]


def test_remove_participant_from_nonexistent_activity(client):
    """Test removal from an activity that doesn't exist."""
    email = "student@mergington.edu"
    activity = "Nonexistent Club"
    
    response = client.delete(f"/activities/{activity}/remove?email={email}")
    assert response.status_code == 404
    
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_remove_nonexistent_participant(client):
    """Test removal of a participant who isn't signed up."""
    email = "notsignedup@mergington.edu"
    activity = "Chess Club"
    
    response = client.delete(f"/activities/{activity}/remove?email={email}")
    assert response.status_code == 400
    
    data = response.json()
    assert data["detail"] == "Student is not signed up for this activity"


def test_signup_and_remove_workflow(client):
    """Test the complete workflow of signing up and then removing a participant."""
    email = "workflow@mergington.edu"
    activity = "Programming Class"
    
    # Initial state - check participant count
    initial_response = client.get("/activities")
    initial_data = initial_response.json()
    initial_count = len(initial_data[activity]["participants"])
    
    # Sign up
    signup_response = client.post(f"/activities/{activity}/signup?email={email}")
    assert signup_response.status_code == 200
    
    # Verify signup
    after_signup_response = client.get("/activities")
    after_signup_data = after_signup_response.json()
    assert len(after_signup_data[activity]["participants"]) == initial_count + 1
    assert email in after_signup_data[activity]["participants"]
    
    # Remove participant
    remove_response = client.delete(f"/activities/{activity}/remove?email={email}")
    assert remove_response.status_code == 200
    
    # Verify removal
    after_removal_response = client.get("/activities")
    after_removal_data = after_removal_response.json()
    assert len(after_removal_data[activity]["participants"]) == initial_count
    assert email not in after_removal_data[activity]["participants"]


def test_url_encoding_in_activity_names(client):
    """Test that activity names with special characters are handled properly."""
    # Add an activity with special characters for testing
    from app import activities
    activities["Art & Crafts Club"] = {
        "description": "Creative arts and crafts",
        "schedule": "Wednesdays, 3:00 PM - 4:00 PM",
        "max_participants": 15,
        "participants": []
    }
    
    email = "artist@mergington.edu"
    activity = "Art & Crafts Club"
    
    # Test signup with URL encoding
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    
    # Test removal with URL encoding
    response = client.delete(f"/activities/{activity}/remove?email={email}")
    assert response.status_code == 200