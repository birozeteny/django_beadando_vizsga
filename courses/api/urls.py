from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InstructorViewSet, TagViewSet, CourseViewSet, EnrollmentViewSet

router = DefaultRouter()
router.register(r'instructors', InstructorViewSet)
router.register(r'tags', TagViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'enrollments', EnrollmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]