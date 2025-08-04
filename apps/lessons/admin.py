from django.contrib import admin
from .models import Lesson, LessonProgress


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'duration_minutes', 'is_free', 'created_at')
    list_filter = ('is_free', 'created_at', 'course')
    search_fields = ('title', 'description', 'course__title')
    list_editable = ('order', 'is_free')
    ordering = ('course', 'order')

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('course', 'title', 'description')
        }),
        ('Kontent', {
            'fields': ('video_url', 'content')
        }),
        ('Sozlamalar', {
            'fields': ('order', 'duration_minutes', 'is_free')
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'teacher':
            return qs.filter(course__instructor=request.user)
        return qs


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'is_completed', 'watched_duration', 'completed_at')
    list_filter = ('is_completed', 'completed_at', 'lesson__course')
    search_fields = ('student__username', 'lesson__title', 'lesson__course__title')
    list_editable = ('is_completed',)
    ordering = ('-completed_at',)

    readonly_fields = ('completed_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'teacher':
            return qs.filter(lesson__course__instructor=request.user)
        elif request.user.role == 'student':
            return qs.filter(student=request.user)
        return qs