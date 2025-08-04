from django.contrib import admin
from .models import Quiz, Question, Choice, QuizAttempt


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    max_num = 6


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'order', 'text_short')
    list_filter = ('quiz',)
    search_fields = ('text', 'quiz__title')
    ordering = ('quiz', 'order')
    inlines = [ChoiceInline]

    def text_short(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text

    text_short.short_description = 'Savol matni'


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'passing_score', 'time_limit')
    list_filter = ('passing_score', 'lesson__course')
    search_fields = ('title', 'description', 'lesson__title')
    ordering = ('lesson__course', 'lesson__order')
    inlines = [QuestionInline]

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('lesson', 'title', 'description')
        }),
        ('Sozlamalar', {
            'fields': ('passing_score', 'time_limit')
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'teacher':
            return qs.filter(lesson__course__instructor=request.user)
        return qs


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score', 'is_passed', 'started_at', 'completed_at')
    list_filter = ('is_passed', 'started_at', 'quiz__lesson__course')
    search_fields = ('student__username', 'quiz__title')
    ordering = ('-started_at',)

    readonly_fields = ('started_at', 'completed_at')

    fieldsets = (
        ('Test ma\'lumotlari', {
            'fields': ('student', 'quiz')
        }),
        ('Natijalar', {
            'fields': ('score', 'is_passed')
        }),
        ('Vaqt', {
            'fields': ('started_at', 'completed_at')
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'teacher':
            return qs.filter(quiz__lesson__course__instructor=request.user)
        elif request.user.role == 'student':
            return qs.filter(student=request.user)
        return qs