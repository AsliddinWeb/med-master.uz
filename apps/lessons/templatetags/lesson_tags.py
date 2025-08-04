from django import template
from apps.lessons.models import LessonProgress

register = template.Library()


@register.filter
def lesson_progress(user, lesson):
    """Dars progressi"""
    if not user.is_authenticated:
        return None

    try:
        return LessonProgress.objects.get(student=user, lesson=lesson)
    except LessonProgress.DoesNotExist:
        return None


@register.filter
def is_lesson_completed(user, lesson):
    """Dars tugallanganmi?"""
    if not user.is_authenticated:
        return False

    try:
        progress = LessonProgress.objects.get(student=user, lesson=lesson)
        return progress.is_completed
    except LessonProgress.DoesNotExist:
        return False


@register.filter
def lesson_watched_percentage(user, lesson):
    """Darsning necha foizi ko'rilgan"""
    if not user.is_authenticated or lesson.duration_minutes == 0:
        return 0

    try:
        progress = LessonProgress.objects.get(student=user, lesson=lesson)
        watched_minutes = progress.watched_duration / 60  # seconds to minutes
        percentage = (watched_minutes / lesson.duration_minutes) * 100
        return min(100, round(percentage, 1))
    except LessonProgress.DoesNotExist:
        return 0


@register.filter
def format_video_url(url):
    """Video URL ni embed formatga o'tkazish"""
    if not url:
        return ''

    # YouTube
    if 'youtube.com/watch?v=' in url:
        video_id = url.split('watch?v=')[1].split('&')[0]
        return f'https://www.youtube.com/embed/{video_id}'
    elif 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[1].split('?')[0]
        return f'https://www.youtube.com/embed/{video_id}'

    # Vimeo
    elif 'vimeo.com/' in url:
        video_id = url.split('vimeo.com/')[1].split('?')[0]
        return f'https://player.vimeo.com/video/{video_id}'

    return url


@register.simple_tag
def lesson_status_badge(user, lesson):
    """Dars holati badge"""
    if not user.is_authenticated:
        return '<span class="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">Ko\'rish uchun login qiling</span>'

    try:
        progress = LessonProgress.objects.get(student=user, lesson=lesson)
        if progress.is_completed:
            return '<span class="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">✓ Tugallangan</span>'
        elif progress.watched_duration > 0:
            return '<span class="px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800">📺 Ko\'rilmoqda</span>'
    except LessonProgress.DoesNotExist:
        pass

    return '<span class="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">🎯 Yangi</span>'


@register.inclusion_tag('lessons/components/lesson_card.html')
def lesson_card(lesson, user=None, show_progress=True):
    """Dars kartasi"""
    return {
        'lesson': lesson,
        'user': user,
        'show_progress': show_progress,
    }


@register.inclusion_tag('lessons/components/video_player.html')
def video_player(lesson, user=None):
    """Video player component"""
    return {
        'lesson': lesson,
        'user': user,
        'embed_url': format_video_url(lesson.video_url),
    }


@register.simple_tag
def next_lesson_url(lesson):
    """Keyingi dars URL"""
    from django.urls import reverse

    next_lesson = lesson.course.lessons.filter(
        order__gt=lesson.order
    ).order_by('order').first()

    if next_lesson:
        return reverse('lessons:detail', kwargs={
            'course_id': lesson.course.id,
            'lesson_id': next_lesson.id
        })
    return None


@register.simple_tag
def prev_lesson_url(lesson):
    """Oldingi dars URL"""
    from django.urls import reverse

    prev_lesson = lesson.course.lessons.filter(
        order__lt=lesson.order
    ).order_by('-order').first()

    if prev_lesson:
        return reverse('lessons:detail', kwargs={
            'course_id': lesson.course.id,
            'lesson_id': prev_lesson.id
        })
    return None