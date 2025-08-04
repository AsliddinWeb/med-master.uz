from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Count, Avg
from django.utils import timezone
import json

from .models import Quiz, Question, Choice, QuizAttempt
from .forms import QuizCreateForm, QuestionCreateForm, ChoiceFormSet, QuizAttemptForm
from apps.courses.models import Course, Enrollment
from apps.lessons.models import Lesson


def quiz_list_view(request, lesson_id):
    """Dars testlari ro'yxati"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course

    # Access tekshirish
    is_enrolled = False
    can_view = False

    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
        can_view = (
                is_enrolled or
                request.user == course.instructor or
                request.user.role == 'admin'
        )

    if not can_view:
        messages.error(request, 'Bu testlarni ko\'rish uchun kursga yozilishingiz kerak!')
        return redirect('courses:detail', course_id=course.id)

    quizzes = lesson.quizzes.all()

    # User attempts
    user_attempts = {}
    if request.user.is_authenticated and is_enrolled:
        attempts = QuizAttempt.objects.filter(
            student=request.user,
            quiz__lesson=lesson
        ).values('quiz_id', 'score', 'is_passed', 'completed_at')

        user_attempts = {
            attempt['quiz_id']: attempt for attempt in attempts
        }

    context = {
        'lesson': lesson,
        'course': course,
        'quizzes': quizzes,
        'user_attempts': user_attempts,
        'is_enrolled': is_enrolled,
        'page_title': f'{lesson.title} - Testlar',
    }

    return render(request, 'quizzes/quiz_list.html', context)


def quiz_detail_view(request, quiz_id):
    """Test tafsilotlari"""
    quiz = get_object_or_404(Quiz.objects.select_related('lesson__course'), id=quiz_id)
    course = quiz.lesson.course

    # Access tekshirish
    is_enrolled = False
    can_view = False

    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
        can_view = (
                is_enrolled or
                request.user == course.instructor or
                request.user.role == 'admin'
        )

    if not can_view:
        messages.error(request, 'Bu testni ko\'rish uchun kursga yozilishingiz kerak!')
        return redirect('courses:detail', course_id=course.id)

    # Questions count
    questions_count = quiz.questions.count()

    # User attempts
    user_attempts = []
    best_score = 0
    can_attempt = True

    if request.user.is_authenticated and is_enrolled:
        user_attempts = QuizAttempt.objects.filter(
            student=request.user,
            quiz=quiz
        ).order_by('-started_at')

        if user_attempts.exists():
            best_score = max(attempt.score for attempt in user_attempts)
            # 3 marta urinishdan keyin to'xtatish (ixtiyoriy)
            can_attempt = user_attempts.count() < 3

    context = {
        'quiz': quiz,
        'course': course,
        'questions_count': questions_count,
        'user_attempts': user_attempts,
        'best_score': best_score,
        'can_attempt': can_attempt,
        'is_enrolled': is_enrolled,
        'page_title': f'{quiz.title} - Test',
    }

    return render(request, 'quizzes/quiz_detail.html', context)


@login_required
def quiz_attempt_view(request, quiz_id):
    """Test yechish"""
    quiz = get_object_or_404(
        Quiz.objects.select_related('lesson__course').prefetch_related('questions__choices'),
        id=quiz_id
    )
    course = quiz.lesson.course

    # Enrollment tekshirish
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.error(request, 'Bu testni yechish uchun kursga yozilishingiz kerak!')
        return redirect('quizzes:detail', quiz_id=quiz.id)

    # Questions
    questions = quiz.questions.all().order_by('order')
    if not questions.exists():
        messages.error(request, 'Bu testda savollar mavjud emas!')
        return redirect('quizzes:detail', quiz_id=quiz.id)

    if request.method == 'POST':
        # Quiz attempt yaratish
        attempt = QuizAttempt.objects.create(
            student=request.user,
            quiz=quiz
        )

        correct_answers = 0
        total_questions = questions.count()

        # Javoblarni tekshirish
        for question in questions:
            selected_choice_id = request.POST.get(f'question_{question.id}')
            if selected_choice_id:
                try:
                    selected_choice = question.choices.get(id=selected_choice_id)
                    if selected_choice.is_correct:
                        correct_answers += 1
                except Choice.DoesNotExist:
                    pass

        # Score hisoblash
        score = round((correct_answers / total_questions) * 100) if total_questions > 0 else 0
        is_passed = score >= quiz.passing_score

        # Attempt yangilash
        attempt.score = score
        attempt.is_passed = is_passed
        attempt.completed_at = timezone.now()
        attempt.save()

        messages.success(request, f'Test tugallandi! Sizning natijangiz: {score}%')
        return redirect('quizzes:result', attempt_id=attempt.id)

    context = {
        'quiz': quiz,
        'questions': questions,
        'course': course,
        'page_title': f'{quiz.title} - Test yechish',
    }

    return render(request, 'quizzes/quiz_attempt.html', context)


@login_required
def quiz_result_view(request, attempt_id):
    """Test natijasi"""
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related('quiz__lesson__course', 'student'),
        id=attempt_id,
        student=request.user
    )

    quiz = attempt.quiz
    questions = quiz.questions.all().order_by('order')

    context = {
        'attempt': attempt,
        'quiz': quiz,
        'questions': questions,
        'page_title': f'{quiz.title} - Natija',
    }

    return render(request, 'quizzes/quiz_result.html', context)


@login_required
def quiz_create_view(request, lesson_id):
    """Test yaratish (O'qituvchi uchun)"""
    lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=request.user)

    if request.method == 'POST':
        form = QuizCreateForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.lesson = lesson
            quiz.save()

            messages.success(request, f'"{quiz.title}" testi yaratildi!')
            return redirect('quizzes:add_questions', quiz_id=quiz.id)
    else:
        form = QuizCreateForm()

    context = {
        'form': form,
        'lesson': lesson,
        'page_title': f'{lesson.title} - Yangi test',
    }

    return render(request, 'quizzes/quiz_create.html', context)


@login_required
def quiz_add_questions_view(request, quiz_id):
    """Test savollarini qo'shish"""
    quiz = get_object_or_404(Quiz, id=quiz_id, lesson__course__instructor=request.user)

    if request.method == 'POST':
        question_form = QuestionCreateForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz

            # Order avtomatik belgilash
            last_question = quiz.questions.order_by('-order').first()
            question.order = (last_question.order + 1) if last_question else 1

            question.save()

            # Javob variantlarini saqlash
            choices_data = json.loads(request.POST.get('choices_data', '[]'))
            for i, choice_data in enumerate(choices_data):
                if choice_data.get('text'):
                    Choice.objects.create(
                        question=question,
                        text=choice_data['text'],
                        is_correct=choice_data.get('is_correct', False)
                    )

            messages.success(request, 'Savol qo\'shildi!')
            return redirect('quizzes:add_questions', quiz_id=quiz.id)
    else:
        question_form = QuestionCreateForm()

    questions = quiz.questions.all().order_by('order')

    context = {
        'quiz': quiz,
        'question_form': question_form,
        'questions': questions,
        'page_title': f'{quiz.title} - Savollar qo\'shish',
    }

    return render(request, 'quizzes/quiz_add_questions.html', context)


@login_required
@require_http_methods(["POST"])
def question_delete_view(request, question_id):
    """Savolni o'chirish"""
    question = get_object_or_404(Question, id=question_id, quiz__lesson__course__instructor=request.user)

    question_text = question.text[:50]
    question.delete()

    messages.success(request, f'Savol o\'chirildi: {question_text}...')
    return redirect('quizzes:add_questions', quiz_id=question.quiz.id)


@login_required
def quiz_statistics_view(request, quiz_id):
    """Test statistikasi (O'qituvchi uchun)"""
    quiz = get_object_or_404(Quiz, id=quiz_id, lesson__course__instructor=request.user)

    attempts = QuizAttempt.objects.filter(quiz=quiz).select_related('student')

    # Statistics
    total_attempts = attempts.count()
    unique_students = attempts.values('student').distinct().count()
    passed_attempts = attempts.filter(is_passed=True).count()
    avg_score = attempts.aggregate(avg_score=Avg('score'))['avg_score'] or 0

    # Score distribution
    score_ranges = {
        '90-100': attempts.filter(score__gte=90).count(),
        '80-89': attempts.filter(score__gte=80, score__lt=90).count(),
        '70-79': attempts.filter(score__gte=70, score__lt=80).count(),
        '60-69': attempts.filter(score__gte=60, score__lt=70).count(),
        '0-59': attempts.filter(score__lt=60).count(),
    }

    # Recent attempts
    recent_attempts = attempts.order_by('-started_at')[:10]

    context = {
        'quiz': quiz,
        'total_attempts': total_attempts,
        'unique_students': unique_students,
        'passed_attempts': passed_attempts,
        'pass_rate': round((passed_attempts / total_attempts * 100), 1) if total_attempts > 0 else 0,
        'avg_score': round(avg_score, 1),
        'score_ranges': score_ranges,
        'recent_attempts': recent_attempts,
        'page_title': f'{quiz.title} - Statistika',
    }

    return render(request, 'quizzes/quiz_statistics.html', context)


@login_required
def my_quiz_results_view(request):
    """Mening test natijalarim"""
    attempts = QuizAttempt.objects.filter(
        student=request.user,
        completed_at__isnull=False
    ).select_related('quiz__lesson__course').order_by('-completed_at')

    # Filter
    course_id = request.GET.get('course')
    passed_only = request.GET.get('passed')

    if course_id:
        attempts = attempts.filter(quiz__lesson__course_id=course_id)

    if passed_only == 'true':
        attempts = attempts.filter(is_passed=True)
    elif passed_only == 'false':
        attempts = attempts.filter(is_passed=False)

    # Pagination
    paginator = Paginator(attempts, 20)
    page = request.GET.get('page')
    attempts_page = paginator.get_page(page)

    # Statistics
    stats = {
        'total_attempts': attempts.count(),
        'passed_attempts': attempts.filter(is_passed=True).count(),
        'avg_score': attempts.aggregate(avg_score=Avg('score'))['avg_score'] or 0,
    }

    # Available courses
    enrolled_courses = Course.objects.filter(
        enrollment__student=request.user
    ).distinct()

    context = {
        'attempts': attempts_page,
        'stats': stats,
        'enrolled_courses': enrolled_courses,
        'current_course': course_id,
        'passed_only': passed_only,
        'page_title': 'Mening test natijalarim',
    }

    return render(request, 'quizzes/my_results.html', context)


@login_required
@require_http_methods(["POST"])
def quiz_toggle_status_view(request, quiz_id):
    """Test holatini o'zgartirish"""
    quiz = get_object_or_404(Quiz, id=quiz_id, lesson__course__instructor=request.user)

    # Quiz modelda active field yo'q, lekin qo'shish mumkin
    # Hozircha faqat o'chirish
    return JsonResponse({'success': False, 'message': 'Funksiya hali tayyor emas'})


# API endpoints for AJAX
@login_required
@require_http_methods(["POST"])
def save_quiz_progress(request, quiz_id):
    """Test progressini saqlash (AJAX)"""
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Enrollment tekshirish
    if not Enrollment.objects.filter(student=request.user, course=quiz.lesson.course).exists():
        return JsonResponse({'success': False, 'message': 'Ruxsat yo\'q!'})

    try:
        # Progress ma'lumotlarini saqlash (session da)
        progress_data = json.loads(request.body)
        request.session[f'quiz_{quiz_id}_progress'] = progress_data

        return JsonResponse({'success': True})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Noto\'g\'ri ma\'lumot!'})