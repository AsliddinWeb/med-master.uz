from django.contrib import admin
from .models import Course, Enrollment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'level', 'duration_weeks', 'price', 'is_active', 'created_at')
    list_filter = ('level', 'is_active', 'created_at', 'instructor')
    search_fields = ('title', 'description', 'instructor__first_name', 'instructor__last_name')
    list_editable = ('is_active', 'price')
    ordering = ('-created_at',)

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('title', 'description', 'instructor')
        }),
        ('Kurs tafsilotlari', {
            'fields': ('level', 'duration_weeks', 'price')
        }),
        ('Sozlamalar', {
            'fields': ('is_active',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'teacher':
            return qs.filter(instructor=request.user)
        return qs


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'progress', 'is_completed', 'enrolled_at')
    list_filter = ('is_completed', 'enrolled_at', 'course__level')
    search_fields = ('student__username', 'student__email', 'course__title')
    list_editable = ('progress', 'is_completed')
    ordering = ('-enrolled_at',)

    readonly_fields = ('enrolled_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'teacher':
            return qs.filter(course__instructor=request.user)
        elif request.user.role == 'student':
            return qs.filter(student=request.user)
        return qs