import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app, follow_redirects=False)


class TestActivitiesAPI:
    """Test suite for the Activities API endpoints."""

    def test_root_redirect(self, client):
        """Test that GET / redirects to static index.html."""
        # Arrange - no special setup needed

        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"

    def test_get_activities(self, client):
        """Test that GET /activities returns all activities."""
        # Arrange - no special setup needed

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        # Check structure
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_signup_success(self, client):
        """Test successful signup for an activity."""
        # Arrange
        email = "test@example.com"
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]

        # Verify participant was added
        response2 = client.get("/activities")
        data = response2.json()
        assert email in data[activity]["participants"]

    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity returns 404."""
        # Arrange
        email = "test@example.com"
        activity = "NonExistent Activity"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Activity not found" in result["detail"]

    def test_signup_already_registered(self, client):
        """Test signup when already registered returns 400."""
        # Arrange
        email = "duplicate@example.com"
        activity = "Chess Club"
        # First signup
        client.post(f"/activities/{activity}/signup?email={email}")

        # Act - second signup
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "already registered" in result["detail"]

    def test_unregister_success(self, client):
        """Test successful unregister from an activity."""
        # Arrange
        email = "unregister@example.com"
        activity = "Programming Class"
        # First signup
        client.post(f"/activities/{activity}/signup?email={email}")

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]

        # Verify participant was removed
        response2 = client.get("/activities")
        data = response2.json()
        assert email not in data[activity]["participants"]

    def test_unregister_activity_not_found(self, client):
        """Test unregister from non-existent activity returns 404."""
        # Arrange
        email = "test@example.com"
        activity = "NonExistent Activity"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Activity not found" in result["detail"]

    def test_unregister_not_registered(self, client):
        """Test unregister when not registered returns 400."""
        # Arrange
        email = "notregistered@example.com"
        activity = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "not registered" in result["detail"]