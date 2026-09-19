from django.contrib import admin
from .models import Instructor, Tag, Course, Enrollment

class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'price', 'is_published')
    search_fields = ('title', 'description')
    list_filter = ('is_published', 'instructor')
    filter_horizontal = ('tags',)
    inlines = [EnrollmentInline]

admin.site.register(Instructor)
admin.site.register(Tag)
admin.site.register(Enrollment)