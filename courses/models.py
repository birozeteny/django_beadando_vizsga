from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Instructor(models.Model):
    name = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    birth_year = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.IntegerField()
    published_year = models.IntegerField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name='courses')
    tags = models.ManyToManyField(Tag, related_name='courses', blank=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    student_name = models.CharField(max_length=150)
    enrolled_at = models.DateField()
    progress = models.IntegerField(default=0)
    completed_at = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')

    class Meta:
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.student_name} – {self.course.title}"