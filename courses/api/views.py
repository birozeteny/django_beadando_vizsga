from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from courses.models import Instructor, Tag, Course, Enrollment
from .serializers import InstructorSerializer, TagSerializer, CourseSerializer, EnrollmentSerializer
from courses.permissions import IsEnrollmentOwner

class InstructorViewSet(viewsets.ModelViewSet):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('instructor').prefetch_related('tags')
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['instructor']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'published_year']

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.select_related('course', 'created_by')
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated, IsEnrollmentOwner]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)