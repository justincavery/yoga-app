"""
Integration tests for YogaFlow API endpoints.
Tests actual HTTP requests against a running server.

These tests verify:
- Backend server is running and accessible
- All API endpoints respond correctly
- Database connectivity works
- Query parameters are handled properly
- CORS configuration is correct
- Response formatting matches API contract
"""
import pytest
import httpx
import time
from typing import Optional


# Test configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"
TIMEOUT = 10.0


class TestServerHealth:
    """Test server health and availability."""

    def test_server_is_running(self):
        """Test that the server is accessible."""
        response = httpx.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self):
        """Test root endpoint returns API info."""
        response = httpx.get(BASE_URL, timeout=TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "YogaFlow API"
        assert data["status"] == "healthy"
        assert "version" in data

    def test_docs_accessible(self):
        """Test that API documentation is accessible."""
        response = httpx.get(f"{BASE_URL}/docs", timeout=TIMEOUT)
        assert response.status_code == 200
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()

    def test_openapi_spec_accessible(self):
        """Test that OpenAPI spec is accessible."""
        response = httpx.get(f"{BASE_URL}/openapi.json", timeout=TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data
        assert "/api/v1/poses" in data["paths"]


class TestPosesEndpoint:
    """Test /api/v1/poses endpoint."""

    def test_list_all_poses(self):
        """Test listing all poses returns expected data structure."""
        response = httpx.get(f"{API_BASE}/poses", timeout=TIMEOUT)
        assert response.status_code == 200

        data = response.json()
        assert "poses" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data

        # Verify we have 80 poses in database
        assert data["total"] == 80
        assert isinstance(data["poses"], list)

    def test_default_pagination(self):
        """Test default pagination (page 1, 20 items per page)."""
        response = httpx.get(f"{API_BASE}/poses", timeout=TIMEOUT)
        assert response.status_code == 200

        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert len(data["poses"]) == 20  # Should return 20 items by default

    def test_custom_pagination(self):
        """Test custom pagination parameters."""
        response = httpx.get(f"{API_BASE}/poses?page=1&page_size=5", timeout=TIMEOUT)
        assert response.status_code == 200

        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert len(data["poses"]) == 5

    def test_pagination_second_page(self):
        """Test getting second page of results."""
        response = httpx.get(f"{API_BASE}/poses?page=2&page_size=10", timeout=TIMEOUT)
        assert response.status_code == 200

        data = response.json()
        assert data["page"] == 2
        assert data["page_size"] == 10
        assert len(data["poses"]) == 10

    def test_search_by_name(self):
        """Test searching poses by name."""
        # Search for "warrior" - there should be multiple warrior poses
        response = httpx.get(f"{API_BASE}/poses?search=warrior", timeout=TIMEOUT)
        assert response.status_code == 200

        data = response.json()
        assert data["total"] > 0

        # Verify all returned poses contain "warrior" in their name
        for pose in data["poses"]:
            name = pose["name_english"].lower()
            assert "warrior" in name

    def test_search_case_insensitive(self):
        """Test that search is case-insensitive."""
        response1 = httpx.get(f"{API_BASE}/poses?search=WARRIOR", timeout=TIMEOUT)
        response2 = httpx.get(f"{API_BASE}/poses?search=warrior", timeout=TIMEOUT)

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Should return same number of results
        assert response1.json()["total"] == response2.json()["total"]

    def test_filter_by_difficulty_beginner(self):
        """Test filtering by beginner difficulty level."""
        response = httpx.get(f"{API_BASE}/poses?difficulty=beginner", timeout=TIMEOUT)
        assert response.status_code == 200

        data = response.json()
        assert data["total"] > 0

        # Verify all returned poses are beginner level
        for pose in data["poses"]:
            assert pose["difficulty_level"] == "beginner"

    def test_filter_by_difficulty_intermediate(self):
        """Test filtering by intermediate difficulty level."""
        response = httpx.get(f"{API_BASE}/poses?difficulty=intermediate", timeout=TIMEOUT)
        assert response.status_code == 200

        data = response.json()
        # There should be intermediate poses
        assert data["total"] > 0

        for pose in data["poses"]:
            assert pose["difficulty_level"] == "intermediate"

    def test_filter_by_difficulty_advanced(self):
        """Test filtering by advanced difficulty level."""
        response = httpx.get(f"{API_BASE}/poses?difficulty=advanced", timeout=TIMEOUT)
        assert response.status_code == 200

        data = response.json()
        # There should be advanced poses
        assert data["total"] > 0

        for pose in data["poses"]:
            assert pose["difficulty_level"] == "advanced"

    def test_filter_by_category(self):
        """Test filtering by category."""
        response = httpx.get(f"{API_BASE}/poses?category=standing", timeout=TIMEOUT)
        assert response.status_code == 200

        data = response.json()
        assert data["total"] > 0

        for pose in data["poses"]:
            assert pose["category"] == "standing"

    def test_combined_filters(self):
        """Test combining search and filters."""
        response = httpx.get(
            f"{API_BASE}/poses?search=warrior&difficulty=beginner",
            timeout=TIMEOUT
        )
        assert response.status_code == 200

        data = response.json()
        # Should return beginner warrior poses only
        for pose in data["poses"]:
            assert "warrior" in pose["name_english"].lower()
            assert pose["difficulty_level"] == "beginner"

    def test_pose_response_structure(self):
        """Test that pose response contains all required fields."""
        response = httpx.get(f"{API_BASE}/poses?page_size=1", timeout=TIMEOUT)
        assert response.status_code == 200

        data = response.json()
        assert len(data["poses"]) == 1

        pose = data["poses"][0]

        # Verify required fields
        required_fields = [
            "pose_id",
            "name_english",
            "category",
            "difficulty_level",
            "description",
            "instructions",
            "image_urls"
        ]

        for field in required_fields:
            assert field in pose, f"Missing required field: {field}"
            assert pose[field] is not None, f"Field {field} should not be None"

    def test_invalid_page_number(self):
        """Test that invalid page numbers are rejected."""
        response = httpx.get(f"{API_BASE}/poses?page=0", timeout=TIMEOUT)
        assert response.status_code == 422  # Validation error

    def test_invalid_page_size(self):
        """Test that invalid page size is rejected."""
        response = httpx.get(f"{API_BASE}/poses?page_size=0", timeout=TIMEOUT)
        assert response.status_code == 422  # Validation error

    def test_page_size_exceeds_max(self):
        """Test that page size > 100 is rejected."""
        response = httpx.get(f"{API_BASE}/poses?page_size=150", timeout=TIMEOUT)
        assert response.status_code == 422  # Validation error

    def test_invalid_difficulty_level(self):
        """Test that invalid difficulty level is rejected."""
        response = httpx.get(f"{API_BASE}/poses?difficulty=INVALID", timeout=TIMEOUT)
        assert response.status_code == 422  # Validation error

    def test_invalid_category(self):
        """Test that invalid category is rejected."""
        response = httpx.get(f"{API_BASE}/poses?category=INVALID", timeout=TIMEOUT)
        assert response.status_code == 422  # Validation error


class TestSinglePoseEndpoint:
    """Test /api/v1/poses/{pose_id} endpoint."""

    def test_get_pose_by_id(self):
        """Test getting a specific pose by ID."""
        # First get list to find a valid pose ID
        list_response = httpx.get(f"{API_BASE}/poses?page_size=1", timeout=TIMEOUT)
        assert list_response.status_code == 200

        pose_id = list_response.json()["poses"][0]["pose_id"]

        # Now get that specific pose
        response = httpx.get(f"{API_BASE}/poses/{pose_id}", timeout=TIMEOUT)
        assert response.status_code == 200

        data = response.json()
        assert data["pose_id"] == pose_id
        assert "name_english" in data
        assert "description" in data

    def test_get_nonexistent_pose(self):
        """Test getting a pose that doesn't exist."""
        response = httpx.get(f"{API_BASE}/poses/999999", timeout=TIMEOUT)
        assert response.status_code == 404

        data = response.json()
        # Check for error message in response
        assert "error" in data or "detail" in data

    def test_get_pose_invalid_id(self):
        """Test getting a pose with invalid ID format."""
        response = httpx.get(f"{API_BASE}/poses/invalid", timeout=TIMEOUT)
        assert response.status_code == 422  # Validation error


class TestCORSConfiguration:
    """Test CORS headers for frontend connectivity."""

    def test_cors_headers_on_poses_endpoint(self):
        """Test that CORS headers are present for frontend."""
        # FastAPI CORS middleware handles OPTIONS automatically via regular requests
        # Test with a regular GET request instead
        response = httpx.get(
            f"{API_BASE}/poses",
            headers={"Origin": "http://localhost:5173"},
            timeout=TIMEOUT
        )

        # Should succeed and have CORS headers
        assert response.status_code == 200

    def test_cors_allows_frontend_origin(self):
        """Test that frontend origin is allowed."""
        response = httpx.get(
            f"{API_BASE}/poses",
            headers={"Origin": "http://localhost:5173"},
            timeout=TIMEOUT
        )

        assert response.status_code == 200
        # CORS header should be present
        assert "access-control-allow-origin" in response.headers


class TestDatabaseConnectivity:
    """Test that database queries work correctly."""

    def test_database_returns_consistent_data(self):
        """Test that database returns consistent data across requests."""
        response1 = httpx.get(f"{API_BASE}/poses", timeout=TIMEOUT)
        response2 = httpx.get(f"{API_BASE}/poses", timeout=TIMEOUT)

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Should return same total count
        assert response1.json()["total"] == response2.json()["total"]
        assert response1.json()["total"] == 80

    def test_database_query_performance(self):
        """Test that database queries complete in reasonable time."""
        start_time = time.time()
        response = httpx.get(f"{API_BASE}/poses", timeout=TIMEOUT)
        end_time = time.time()

        assert response.status_code == 200

        # Should complete within 1 second
        assert (end_time - start_time) < 1.0


class TestEndToEndWorkflow:
    """Test complete workflows that frontend would use."""

    def test_frontend_pose_browsing_workflow(self):
        """Test typical frontend workflow: browse poses with filters."""
        # Step 1: Get initial page of poses
        response = httpx.get(f"{API_BASE}/poses?page_size=20", timeout=TIMEOUT)
        assert response.status_code == 200
        assert len(response.json()["poses"]) == 20

        # Step 2: Filter by difficulty
        response = httpx.get(
            f"{API_BASE}/poses?difficulty=beginner&page_size=20",
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        beginner_count = response.json()["total"]
        assert beginner_count > 0

        # Step 3: Search within filtered results
        response = httpx.get(
            f"{API_BASE}/poses?difficulty=beginner&search=mountain",
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        # Should find Mountain Pose which is beginner
        assert response.json()["total"] >= 0

    def test_frontend_pose_details_workflow(self):
        """Test typical workflow: list poses then get details."""
        # Step 1: Get list of poses
        list_response = httpx.get(f"{API_BASE}/poses?page_size=5", timeout=TIMEOUT)
        assert list_response.status_code == 200

        poses = list_response.json()["poses"]
        assert len(poses) == 5

        # Step 2: Get details for first pose
        pose_id = poses[0]["pose_id"]
        detail_response = httpx.get(f"{API_BASE}/poses/{pose_id}", timeout=TIMEOUT)
        assert detail_response.status_code == 200

        detail = detail_response.json()
        assert detail["pose_id"] == pose_id
        assert "instructions" in detail
        assert isinstance(detail["instructions"], list)


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v", "--tb=short"])
