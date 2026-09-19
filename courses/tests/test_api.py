import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestStudentAPI:
    def test_course_list_pagination(self):
        client = APIClient()
        response = client.get("/api/courses/")
        assert response.status_code == 200
        assert "results" in response.json()
        assert "count" in response.json()

    def test_unauthenticated_cannot_create_enrollment(self):
        client = APIClient()
        response = client.post("/api/enrollments/", {
            "course_id": 1, 
            "student_name": "Test Diák", 
            "enrolled_at": "2026-09-19"
        })
        assert response.status_code == 401

    def test_search_course_by_title(self):
        client = APIClient()
        response = client.get("/api/courses/?search=valami")
        assert response.status_code == 200
        assert type(response.json()["results"]) == list