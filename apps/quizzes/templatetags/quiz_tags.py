from django import template
from apps.quizzes.models import QuizAttempt

register = template.Library()


@register.filter
def user_quiz_attempt(user, quiz):
    """Foydalanuvchining quiz urinishi"""
    if not user.is_authenticated:
        return None

    try:
        return QuizAttempt.objects.filter(
            student=user,
            quiz=quiz,
            completed_at__isnull=False
        ).order_by('-started_at').first()
    except QuizAttempt.DoesNotExist:
        return None


@register.filter
def user_best_score(user, quiz):
    """Foydalanuvchining eng yaxshi natijasi"""
    if not user.is_authenticated:
        return 0

    attempts = QuizAttempt.objects.filter(
        student=user,
        quiz=quiz,
        completed_at__isnull=False
    )

    if attempts.exists():
        return max(attempt.score for attempt in attempts)
    return 0


@register.filter
def quiz_attempts_count(user, quiz):
    """Foydalanuvchi urinishlar soni"""
    if not user.is_authenticated:
        return 0

    return QuizAttempt.objects.filter(
        student=user,
        quiz=quiz,
        completed_at__isnull=False
    ).count()


@register.filter
def is_quiz_passed(user, quiz):
    """Test o'tilganmi?"""
    if not user.is_authenticated:
        return False

    return QuizAttempt.objects.filter(
        student=user,
        quiz=quiz,
        is_passed=True
    ).exists()


@register.simple_tag
def quiz_status_badge(user, quiz):
    """Test holati badge"""
    if not user.is_authenticated:
        return '<span class="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">Login qiling</span>'

    attempts = QuizAttempt.objects.filter(
        student=user,
        quiz=quiz,
        completed_at__isnull=False
    )

    if not attempts.exists():
        return '<span class="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">🎯 Yangi</span>'

    best_attempt = attempts.order_by('-score').first()

    if best_attempt.is_passed:
        return f'<span class="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">✓ O\'tgan ({best_attempt.score}%)</span>'
    else:
        return f'<span class="px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800">✗ O\'tmagan ({best_attempt.score}%)</span>'


@register.filter
def format_quiz_time(minutes):
    """Quiz vaqtini formatlash"""
    if minutes < 60:
        return f"{minutes} daqiqa"

    hours = minutes // 60
    mins = minutes % 60

    if mins == 0:
        return f"{hours} soat"
    return f"{hours} soat {mins} daqiqa"


@register.filter
def score_percentage_class(score):
    """Score bo'yicha CSS class"""
    if score >= 90:
        return 'text-green-600'
    elif score >= 70:
        return 'text-yellow-600'
    elif score >= 50:
        return 'text-orange-600'
    else:
        return 'text-red-600'


@register.inclusion_tag('quizzes/components/quiz_card.html')
def quiz_card(quiz, user=None):
    """Quiz kartasi"""
    return {
        'quiz': quiz,
        'user': user,
    }


@register.inclusion_tag('quizzes/components/attempt_result.html')
def attempt_result(attempt):
    """Attempt natijasi component"""
    return {
        'attempt': attempt,
    }


@register.simple_tag
def quiz_progress_bar(score, passing_score):
    """Quiz progress bar"""
    if score >= passing_score:
        color = 'bg-green-500'
    elif score >= passing_score * 0.8:
        color = 'bg-yellow-500'
    else:
        color = 'bg-red-500'

    return f'''
    <div class="w-full bg-gray-200 rounded-full h-2">
        <div class="{color} h-2 rounded-full transition-all duration-300" style="width: {score}%"></div>
    </div>
    <div class="flex justify-between text-xs text-gray-600 mt-1">
        <span>0%</span>
        <span class="text-gray-400">O\'tish: {passing_score}%</span>
        <span>100%</span>
    </div>
    '''