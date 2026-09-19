"""
Beadandó vizsga – Online tanfolyam REST API automatikus tesztjei.

NE MÓDOSÍTSD ezt a fájlt!
"""

from datetime import date
from pathlib import Path

import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

ROOT = Path(__file__).resolve().parent
User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="anna", password="titok123")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="bela", password="titok123")


@pytest.fixture
def sample(db, user):
    from courses.models import Course, Enrollment, Instructor, Tag

    instructor = Instructor.objects.create(
        name="Teszt Oktató",
        bio="Bio",
        birth_year=1985,
    )
    tag = Tag.objects.create(name="Django", description="Django")
    tag2 = Tag.objects.create(name="REST", description="REST")
    course = Course.objects.create(
        title="Django alapok",
        slug="django-alapok",
        description="Bevezető Django kurzus",
        price=10000,
        published_year=2026,
        is_published=True,
        instructor=instructor,
    )
    course.tags.add(tag, tag2)
    enrollment = Enrollment.objects.create(
        course=course,
        student_name="Kiss Éva",
        enrolled_at=date(2026, 8, 1),
        progress=25,
        created_by=user,
    )
    return {
        "user": user,
        "instructor": instructor,
        "tag": tag,
        "tag2": tag2,
        "course": course,
        "enrollment": enrollment,
    }


# ---------------------------------------------------------------------------
# A – Projekt + DRF setup (6 pt)
# ---------------------------------------------------------------------------


class TestProjektSetup:
    def test_manage_py(self):
        assert (ROOT / "manage.py").is_file()

    def test_requirements(self):
        content = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
        assert "django" in content
        assert "djangorestframework" in content
        assert "simplejwt" in content or "djangorestframework-simplejwt" in content
        assert "django-filter" in content or "django_filter" in content
        assert "psycopg2" in content

    def test_api_package(self):
        assert (ROOT / "courses" / "api" / "serializers.py").is_file()
        assert (ROOT / "courses" / "api" / "views.py").is_file()
        assert (ROOT / "courses" / "api" / "urls.py").is_file()

    def test_rest_framework_installed(self):
        from django.conf import settings

        assert "rest_framework" in settings.INSTALLED_APPS
        assert "courses" in settings.INSTALLED_APPS

    def test_dual_db_support(self):
        content = (ROOT / "config" / "settings.py").read_text(encoding="utf-8")
        assert "USE_POSTGRES" in content
        assert "postgresql" in content.lower()


# ---------------------------------------------------------------------------
# B – Modellek (12 pt)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestModellek:
    def test_model_classes_exist(self):
        from courses.models import Course, Enrollment, Instructor, Tag

        assert Instructor is not None
        assert Tag is not None
        assert Course is not None
        assert Enrollment is not None

    def test_instructor_fields(self):
        from courses.models import Instructor

        field_names = {f.name for f in Instructor._meta.get_fields()}
        assert {"name", "bio", "birth_year"}.issubset(field_names)

    def test_tag_unique_name(self):
        from courses.models import Tag

        field = Tag._meta.get_field("name")
        assert field.unique is True

    def test_course_relations(self):
        from courses.models import Course

        instructor_field = Course._meta.get_field("instructor")
        assert instructor_field.is_relation
        assert instructor_field.many_to_one
        tags_field = Course._meta.get_field("tags")
        assert tags_field.many_to_many
        field_names = {f.name for f in Course._meta.get_fields()}
        assert {
            "title",
            "slug",
            "description",
            "price",
            "published_year",
            "is_published",
        }.issubset(field_names)
        assert Course._meta.get_field("slug").unique is True

    def test_enrollment_created_by(self, sample):
        from courses.models import Enrollment

        field = Enrollment._meta.get_field("created_by")
        assert field.is_relation
        assert sample["enrollment"].created_by.username == "anna"
        assert sample["enrollment"].progress == 25

    def test_create_roundtrip(self, sample):
        from courses.models import Course

        assert Course.objects.filter(slug="django-alapok").exists()
        assert sample["course"].instructor.name == "Teszt Oktató"
        assert sample["course"].tags.count() == 2


# ---------------------------------------------------------------------------
# C – Admin (6 pt)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAdmin:
    def test_models_registered(self):
        from courses.models import Course, Enrollment, Instructor, Tag

        for model in (Instructor, Tag, Course, Enrollment):
            assert model in admin.site._registry

    def test_course_admin_config(self):
        from courses.models import Course

        model_admin = admin.site._registry[Course]
        assert "title" in model_admin.list_display
        assert "instructor" in model_admin.list_display
        assert model_admin.search_fields
        assert model_admin.list_filter
        assert model_admin.filter_horizontal
        assert model_admin.inlines

    def test_enrollment_inline_on_course(self):
        from courses.models import Course, Enrollment

        model_admin = admin.site._registry[Course]
        inline_models = [inline.model for inline in model_admin.inlines]
        assert Enrollment in inline_models


# ---------------------------------------------------------------------------
# D – Serializers (10 pt)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestSerializers:
    def test_course_nested_instructor_read(self, sample):
        from courses.api.serializers import CourseSerializer

        data = CourseSerializer(sample["course"]).data
        assert isinstance(data["instructor"], dict)
        assert data["instructor"]["name"] == "Teszt Oktató"

    def test_course_write_by_instructor_id(self, sample):
        from courses.api.serializers import CourseSerializer

        serializer = CourseSerializer(
            data={
                "title": "Új kurzus",
                "slug": "uj-kurzus",
                "description": "",
                "price": 5000,
                "published_year": 2026,
                "is_published": True,
                "instructor_id": sample["instructor"].pk,
                "tags": [sample["tag"].pk],
            }
        )
        assert serializer.is_valid(), serializer.errors
        course = serializer.save()
        assert course.instructor_id == sample["instructor"].pk
        assert list(course.tags.values_list("id", flat=True)) == [sample["tag"].pk]

    def test_enrollment_mini_course(self, sample):
        from courses.api.serializers import EnrollmentSerializer

        data = EnrollmentSerializer(sample["enrollment"]).data
        assert isinstance(data["course"], dict)
        assert data["course"]["title"] == "Django alapok"
        assert "slug" in data["course"]
        assert data["created_by"] == "anna"

    def test_invalid_course_returns_errors(self):
        from courses.api.serializers import CourseSerializer

        serializer = CourseSerializer(data={"title": "Hiányos"})
        assert serializer.is_valid() is False


# ---------------------------------------------------------------------------
# E – ViewSet CRUD (16 pt)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestViewSetCrud:
    def test_list_courses(self, api_client, sample):
        response = api_client.get("/api/courses/")
        assert response.status_code == 200

    def test_retrieve_course(self, api_client, sample):
        response = api_client.get(f"/api/courses/{sample['course'].pk}/")
        assert response.status_code == 200
        assert response.json()["slug"] == "django-alapok"

    def test_create_course_authenticated(self, api_client, sample, user):
        api_client.force_authenticate(user=user)
        response = api_client.post(
            "/api/courses/",
            {
                "title": "JWT kurzus",
                "slug": "jwt-kurzus",
                "description": "Auth",
                "price": 20000,
                "published_year": 2026,
                "is_published": True,
                "instructor_id": sample["instructor"].pk,
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["title"] == "JWT kurzus"

    def test_delete_course(self, api_client, sample, user):
        api_client.force_authenticate(user=user)
        response = api_client.delete(f"/api/courses/{sample['course'].pk}/")
        assert response.status_code == 204

    def test_instructors_tags_endpoints(self, api_client, sample):
        assert api_client.get("/api/instructors/").status_code == 200
        assert api_client.get("/api/tags/").status_code == 200
        assert (
            api_client.get(f"/api/instructors/{sample['instructor'].pk}/").status_code
            == 200
        )

    def test_missing_course_404(self, api_client, sample):
        response = api_client.get("/api/courses/99999/")
        assert response.status_code == 404

    def test_patch_course(self, api_client, sample, user):
        api_client.force_authenticate(user=user)
        response = api_client.patch(
            f"/api/courses/{sample['course'].pk}/",
            {"price": 15000},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["price"] == 15000


# ---------------------------------------------------------------------------
# F – Queryset optimalizálás (4 pt)
# ---------------------------------------------------------------------------


def _prefetch_lookups(queryset):
    return getattr(queryset, "_prefetch_related_lookups", ())


class TestQuerysetOpt:
    def test_course_queryset_uses_select_related(self):
        from courses.api.views import CourseViewSet

        qs = CourseViewSet.queryset
        assert "instructor" in qs.query.select_related

    def test_course_queryset_prefetch_tags(self):
        from courses.api.views import CourseViewSet

        lookups = [str(x).lower() for x in _prefetch_lookups(CourseViewSet.queryset)]
        assert any("tag" in x for x in lookups)

    def test_enrollment_select_related(self):
        from courses.api.views import EnrollmentViewSet

        related = EnrollmentViewSet.queryset.query.select_related
        assert "course" in related
        assert "created_by" in related


# ---------------------------------------------------------------------------
# G – JWT (10 pt)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestJwt:
    def test_token_obtain(self, api_client, user):
        response = api_client.post(
            "/api/token/",
            {"username": "anna", "password": "titok123"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert "access" in data
        assert "refresh" in data

    def test_token_refresh(self, api_client, user):
        obtain = api_client.post(
            "/api/token/",
            {"username": "anna", "password": "titok123"},
            format="json",
        )
        refresh = obtain.json()["refresh"]
        response = api_client.post(
            "/api/token/refresh/",
            {"refresh": refresh},
            format="json",
        )
        assert response.status_code == 200
        assert "access" in response.json()

    def test_bearer_access_enrollment(self, api_client, sample, user):
        obtain = api_client.post(
            "/api/token/",
            {"username": "anna", "password": "titok123"},
            format="json",
        )
        token = obtain.json()["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = api_client.get("/api/enrollments/")
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# H – Permissions (12 pt)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPermissions:
    def test_enrollment_list_requires_auth(self, api_client, sample):
        response = api_client.get("/api/enrollments/")
        assert response.status_code in (401, 403)

    def test_enrollment_create_sets_owner(self, api_client, sample, user):
        api_client.force_authenticate(user=user)
        response = api_client.post(
            "/api/enrollments/",
            {
                "course_id": sample["course"].pk,
                "student_name": "Új Diák",
                "enrolled_at": "2026-08-10",
                "progress": 0,
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["created_by"] == "anna"

    def test_owner_can_patch(self, api_client, sample, user):
        api_client.force_authenticate(user=user)
        response = api_client.patch(
            f"/api/enrollments/{sample['enrollment'].pk}/",
            {"progress": 80},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["progress"] == 80

    def test_non_owner_cannot_delete(self, api_client, sample, other_user):
        api_client.force_authenticate(user=other_user)
        response = api_client.delete(f"/api/enrollments/{sample['enrollment'].pk}/")
        assert response.status_code == 403

    def test_anonymous_can_read_courses(self, api_client, sample):
        response = api_client.get("/api/courses/")
        assert response.status_code == 200

    def test_anonymous_cannot_create_course(self, api_client, sample):
        response = api_client.post(
            "/api/courses/",
            {
                "title": "X",
                "slug": "x",
                "price": 1,
                "instructor_id": sample["instructor"].pk,
            },
            format="json",
        )
        assert response.status_code in (401, 403)


# ---------------------------------------------------------------------------
# I – Pagination + filter (10 pt)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPaginationFilter:
    def test_pagination_keys(self, api_client, sample):
        response = api_client.get("/api/courses/")
        data = response.json()
        assert "count" in data
        assert "results" in data
        assert "next" in data
        assert "previous" in data

    def test_page_size_five(self, api_client, sample):
        from courses.models import Course

        for i in range(6):
            Course.objects.create(
                title=f"Kurzus {i}",
                slug=f"kurzus-{i}",
                price=1000 + i,
                instructor=sample["instructor"],
            )
        response = api_client.get("/api/courses/")
        data = response.json()
        assert len(data["results"]) == 5
        assert data["count"] >= 7

    def test_search(self, api_client, sample):
        from courses.models import Course

        Course.objects.create(
            title="PostgreSQL alapok",
            slug="postgresql-alapok",
            price=3000,
            instructor=sample["instructor"],
        )
        response = api_client.get("/api/courses/?search=Django")
        titles = [r["title"] for r in response.json()["results"]]
        assert any("Django" in t for t in titles)
        assert all("PostgreSQL" not in t for t in titles)

    def test_filter_instructor(self, api_client, sample):
        from courses.models import Course, Instructor

        other = Instructor.objects.create(name="Másik Oktató")
        Course.objects.create(
            title="Másik kurzus",
            slug="masik-kurzus",
            price=1000,
            instructor=other,
        )
        response = api_client.get(
            f"/api/courses/?instructor={sample['instructor'].pk}"
        )
        results = response.json()["results"]
        assert results
        assert all(r["instructor"]["id"] == sample["instructor"].pk for r in results)

    def test_ordering(self, api_client, sample):
        from courses.models import Course

        Course.objects.create(
            title="AAA olcso",
            slug="aaa-olcso",
            price=100,
            instructor=sample["instructor"],
        )
        response = api_client.get("/api/courses/?ordering=price")
        prices = [r["price"] for r in response.json()["results"]]
        assert prices == sorted(prices)


# ---------------------------------------------------------------------------
# J – Seed (4 pt)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestSeed:
    def test_seed_creates_minimum_data(self):
        from django.core.management import call_command

        from courses.models import Course, Enrollment, Instructor, Tag

        call_command("seed_courses")
        assert Instructor.objects.count() >= 3
        assert Tag.objects.count() >= 2
        assert Course.objects.count() >= 3
        assert Enrollment.objects.count() >= 2

    def test_seed_idempotent(self):
        from django.core.management import call_command

        from courses.models import Course

        call_command("seed_courses")
        count = Course.objects.count()
        call_command("seed_courses")
        assert Course.objects.count() == count


# ---------------------------------------------------------------------------
# K – Diák tesztek (6 pt)
# ---------------------------------------------------------------------------


class TestDiakTesztek:
    def test_file_exists(self):
        assert (ROOT / "courses" / "tests" / "test_api.py").is_file()

    def test_at_least_three_tests_defined(self):
        content = (ROOT / "courses" / "tests" / "test_api.py").read_text(
            encoding="utf-8"
        )
        count = sum(
            1
            for line in content.splitlines()
            if line.lstrip().startswith("def test_")
        )
        assert count >= 3, f"Legalább 3 test_* függvény kell, most: {count}"

    def test_student_tests_pass(self):
        import subprocess
        import sys

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "courses/tests/test_api.py",
                "-q",
                "--tb=line",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr


# ---------------------------------------------------------------------------
# L – README + docs (4 pt)
# ---------------------------------------------------------------------------


class TestDocs:
    def test_readme_has_install_and_token(self):
        raw = (ROOT / "README.md").read_text(encoding="utf-8")
        content = raw.lower()
        assert "TODO: Töltsd ki ezt a README-t" not in raw
        assert "## README teendő" not in raw
        assert "pip" in content or "venv" in content
        assert "migrate" in content
        assert "seed_courses" in content
        assert "token" in content or "jwt" in content
        assert "search" in content or "filter" in content
        assert "enrollment" in content

    def test_er_diagram(self):
        raw = (ROOT / "docs" / "er_diagram.md").read_text(encoding="utf-8")
        lower = raw.lower()
        assert "todo: rajzold" not in lower
        assert "instructor" in lower
        assert "course" in lower
        assert "enrollment" in lower
        assert "||--" in raw or "foreign" in lower or "fk" in lower

    def test_api_tesztek_doc(self):
        raw = (ROOT / "docs" / "api_tesztek.md").read_text(encoding="utf-8")
        content = raw.lower()
        assert "todo: dokumentálj" not in content
        assert "token" in content or "jwt" in content
        assert "curl" in content or "postman" in content or "authorization" in content
        assert "api/" in content
