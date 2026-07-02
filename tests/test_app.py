"""Backend API tests using the Arrange-Act-Assert (AAA) pattern."""

from urllib.parse import quote


def _encode_activity_name(activity_name: str) -> str:
    """Encode activity names for URL path safety."""
    return quote(activity_name, safe="")


def test_root_redirects_to_static_index(client):
    # Arrange
    endpoint = "/"

    # Act
    response = client.get(endpoint, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_structure(client):
    # Arrange
    endpoint = "/activities"

    # Act
    response = client.get(endpoint)
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert "participants" in payload["Chess Club"]


def test_signup_success_adds_participant(client):
    # Arrange
    activity_name = "Debate Club"
    email = "new.student@mergington.edu"
    endpoint = f"/activities/{_encode_activity_name(activity_name)}/signup"

    # Act
    signup_response = client.post(endpoint, params={"email": email})
    activities_response = client.get("/activities")

    # Assert
    assert signup_response.status_code == 200
    assert signup_response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert email in activities_response.json()[activity_name]["participants"]


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"
    endpoint = f"/activities/{_encode_activity_name(activity_name)}/signup"

    # Act
    response = client.post(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_returns_400_for_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    endpoint = f"/activities/{_encode_activity_name(activity_name)}/signup"

    # Act
    response = client.post(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_unregister_success_removes_participant(client):
    # Arrange
    activity_name = "Art Club"
    email = "lucas@mergington.edu"
    endpoint = f"/activities/{_encode_activity_name(activity_name)}/participants"

    # Act
    unregister_response = client.delete(endpoint, params={"email": email})
    activities_response = client.get("/activities")

    # Assert
    assert unregister_response.status_code == 200
    assert unregister_response.json() == {
        "message": f"Unregistered {email} from {activity_name}"
    }
    assert email not in activities_response.json()[activity_name]["participants"]


def test_unregister_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"
    endpoint = f"/activities/{_encode_activity_name(activity_name)}/participants"

    # Act
    response = client.delete(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_returns_404_for_missing_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "not_enrolled@mergington.edu"
    endpoint = f"/activities/{_encode_activity_name(activity_name)}/participants"

    # Act
    response = client.delete(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found in this activity"}
