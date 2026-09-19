from rest_framework import serializers
from courses.models import Instructor, Tag, Course, Enrollment

class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    instructor = InstructorSerializer(read_only=True)
    instructor_id = serializers.PrimaryKeyRelatedField(
        queryset=Instructor.objects.all(), source='instructor', write_only=True
    )

    class Meta:
        model = Course
        fields = '__all__'

class CourseMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'slug']

class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseMiniSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source='course', write_only=True
    )
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Enrollment
        fields = '__all__'