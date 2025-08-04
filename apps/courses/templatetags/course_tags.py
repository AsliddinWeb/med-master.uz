from django import template
from django.db.models import Count, Avg
from apps.courses.models import Course, Enrollment
from apps.lessons.models import LessonProgress
from apps.quizzes.models import QuizAttempt

register = template.Library()


@register.filter
def course_progress(user, course):
    """Foydalanuvchining kursdagi progressi (0-100%)"""
    if not user.is_authenticated:
        return 0

    try:
        enrollment = Enrollment.objects.get(student=user, course=course)
        return enrollment.progress
    except Enrollment.DoesNotExist:
        return 0


@register.filter
def is_enrolled(user, course):
    """Foydalanuvchi kursga yozilganmi?"""
    if not user.is_authenticated:
        return False
    return Enrollment.objects.filter(student=user, course=course).exists()


@register.filter
def completed_lessons_count(user, course):
    """Tugallangan darslar soni"""
    if not user.is_authenticated:
        return 0

    return LessonProgress.objects.filter(
        student=user,
        lesson__course=course,
        is_completed=True
    ).count()


@register.filter
def total_lessons_count(course):
    """Kursdagi umumiy darslar soni"""
    return course.lessons.count()


@register.filter
def format_duration(minutes):
    """Daqiqalarni soat va daqiqaga aylantirish"""
    if not minutes:
        return "0 daqiqa"

    hours = minutes // 60
    mins = minutes % 60

    if hours > 0:
        if mins > 0:
            return f"{hours} soat {mins} daqiqa"
        return f"{hours} soat"
    return f"{mins} daqiqa"


@register.filter
def format_price(price):
    """Narxni formatlash"""
    if price == 0:
        return "Bepul"

    # Raqamni formatlash (1000000 -> 1,000,000)
    return f"{price:,.0f} UZS".replace(',', ' ')


@register.filter
def course_level_badge(level):
    """Kurs darajasi uchun badge"""
    level_classes = {
        'beginner': 'bg-green-100 text-green-800',
        'intermediate': 'bg-yellow-100 text-yellow-800',
        'advanced': 'bg-red-100 text-red-800',
    }

    level_names = dict(Course.LEVEL_CHOICES)
    level_name = level_names.get(level, level)
    css_class = level_classes.get(level, 'bg-gray-100 text-gray-800')

    return f'<span class="px-2 py-1 text-xs font-medium rounded-full {css_class}">{level_name}</span>'


@register.filter
def student_count(course):
    """Kursdagi talabalar soni"""
    return course.enrollment_set.count()


@register.filter
def average_rating(course):
    """Kurs o'rtacha reytingi (hozircha static)"""
    # Keyinroq rating system qo'shilganda to'ldiriladi
    return 4.5


@register.filter
def rating_stars(rating):
    """Ratingni yulduzcha ko'rinishida"""
    full_stars = int(rating)
    half_star = rating - full_stars >= 0.5
    empty_stars = 5 - full_stars - (1 if half_star else 0)

    stars_html = '★' * full_stars
    if half_star:
        stars_html += '☆'
    stars_html += '☆' * empty_stars

    return f'<span class="text-yellow-400">{stars_html}</span> <span class="text-gray-600">({rating})</span>'


@register.simple_tag
def course_card(course, user=None):
    """Kurs kartasi uchun ma'lumotlar"""
    data = {
        'course': course,
        'student_count': course.enrollment_set.count(),
        'lesson_count': course.lessons.count(),
        'is_enrolled': False,
        'progress': 0,
    }

    if user and user.is_authenticated:
        data['is_enrolled'] = Enrollment.objects.filter(student=user, course=course).exists()
        if data['is_enrolled']:
            try:
                enrollment = Enrollment.objects.get(student=user, course=course)
                data['progress'] = enrollment.progress
            except Enrollment.DoesNotExist:
                pass

    return data


@register.inclusion_tag('courses/components/course_card.html')
def render_course_card(course, user=None, show_progress=True):
    """Kurs kartasini render qilish"""
    return {
        'course': course,
        'user': user,
        'show_progress': show_progress,
        'student_count': course.enrollment_set.count(),
        'lesson_count': course.lessons.count(),
    }


@register.inclusion_tag('courses/components/progress_bar.html')
def progress_bar(progress, size='normal'):
    """Progress bar component"""
    return {
        'progress': progress,
        'size': size,
    }


@register.simple_tag
def course_url(course, action='detail'):
    """Kurs URL yaratish"""
    from django.urls import reverse

    url_mapping = {
        'detail': 'courses:detail',
        'enroll': 'courses:enroll',
        'edit': 'courses:edit',
        'delete': 'courses:delete',
    }

    url_name = url_mapping.get(action, 'courses:detail')
    return reverse(url_name, kwargs={'course_id': course.id})