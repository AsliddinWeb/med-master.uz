from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils import timezone

from .models import Lesson, LessonProgress
from .forms import LessonCreateForm, LessonEditForm, LessonProgressForm
from apps.courses.models import Course, Enrollment
from apps.quizzes.models import Quiz


def lesson_list_view(request, course_id):
    """Kurs darslari ro'yxati"""
    course = get_object_or_404(Course, id=course_id, is_active=True)

    # Enrollment tekshirish
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()

    # Faqat enrolled yoki o'qituvchi ko'rishi mumkin
    can_view = (
            request.user.is_authenticated and
            (is_enrolled or request.user == course.instructor or request.user.role == 'admin')
    )

    lessons = course.lessons.all().order_by('order')

    # Free lessons barchaga ko'rsatish
    if not can_view:
        lessons = lessons.filter(is_free=True)

    # Progress ma'lumotlari
    lesson_progress = {}
    if request.user.is_authenticated and is_enrolled:
        progress_data = LessonProgress.objects.filter(
            student=request.user,
            lesson__course=course
        ).values('lesson_id', 'is_completed', 'watched_duration')

        lesson_progress = {p['lesson_id']: p for p in progress_data}

    context = {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled,
        'can_view': can_view,
        'lesson_progress': lesson_progress,
        'page_title': f'{course.title} - Darslar',
    }

    return render(request, 'lessons/lesson_list.html', context)


def lesson_detail_view(request, course_id, lesson_id):
    """Dars tafsilotlari"""
    course = get_object_or_404(Course, id=course_id, is_active=True)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    # Access tekshirish
    can_view = False
    is_enrolled = False

    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
        can_view = (
                is_enrolled or
                request.user == course.instructor or
                request.user.role == 'admin'
        )

    # Free lesson bo'lsa barchaga ko'rsatish
    if lesson.is_free:
        can_view = True

    if not can_view:
        messages.error(request, 'Bu darsni ko\'rish uchun kursga yozilishingiz kerak!')
        return redirect('courses:detail', course_id=course.id)

    # Progress ma'lumotlari
    lesson_progress = None
    if request.user.is_authenticated and is_enrolled:
        lesson_progress, created = LessonProgress.objects.get_or_create(
            student=request.user,
            lesson=lesson,
            defaults={'watched_duration': 0}
        )

    # Quizlar
    quizzes = lesson.quizzes.all()

    # Oldingi va keyingi darslar
    prev_lesson = course.lessons.filter(order__lt=lesson.order).order_by('-order').first()
    next_lesson = course.lessons.filter(order__gt=lesson.order).order_by('order').first()

    context = {
        'course': course,
        'lesson': lesson,
        'lesson_progress': lesson_progress,
        'quizzes': quizzes,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'is_enrolled': is_enrolled,
        'page_title': f'{lesson.title} - {course.title}',
    }

    return render(request, 'lessons/lesson_detail.html', context)


@login_required
@require_http_methods(["POST"])
def mark_lesson_complete(request, lesson_id):
    """Darsni tugallangan deb belgilash"""
    lesson = get_object_or_404(Lesson, id=lesson_id)

    # Enrollment tekshirish
    if not Enrollment.objects.filter(student=request.user, course=lesson.course).exists():
        return JsonResponse({'success': False, 'message': 'Kursga yozilmagan!'})

    # Progress yaratish yoki yangilash
    progress, created = LessonProgress.objects.get_or_create(
        student=request.user,
        lesson=lesson,
        defaults={
            'is_completed': True,
            'completed_at': timezone.now(),
            'watched_duration': lesson.duration_minutes * 60  # seconds
        }
    )

    if not progress.is_completed:
        progress.is_completed = True
        progress.completed_at = timezone.now()
        progress.save()

        # Course progress yangilash
        update_course_progress(request.user, lesson.course)

        return JsonResponse({
            'success': True,
            'message': 'Dars tugallandi!',
            'is_completed': True
        })

    return JsonResponse({
        'success': True,
        'message': 'Dars allaqachon tugallangan',
        'is_completed': True
    })


@login_required
@require_http_methods(["POST"])
def update_lesson_progress(request, lesson_id):
    """Dars progress yangilash (video watching)"""
    lesson = get_object_or_404(Lesson, id=lesson_id)

    # Enrollment tekshirish
    if not Enrollment.objects.filter(student=request.user, course=lesson.course).exists():
        return JsonResponse({'success': False, 'message': 'Kursga yozilmagan!'})

    try:
        watched_duration = int(request.POST.get('watched_duration', 0))

        progress, created = LessonProgress.objects.get_or_create(
            student=request.user,
            lesson=lesson,
            defaults={'watched_duration': watched_duration}
        )

        progress.watched_duration = max(progress.watched_duration, watched_duration)

        # 80% ko'rgan bo'lsa tugallangan deb hisoblash
        if watched_duration >= (lesson.duration_minutes * 60 * 0.8):
            if not progress.is_completed:
                progress.is_completed = True
                progress.completed_at = timezone.now()
                update_course_progress(request.user, lesson.course)

        progress.save()

        return JsonResponse({
            'success': True,
            'watched_duration': progress.watched_duration,
            'is_completed': progress.is_completed
        })

    except ValueError:
        return JsonResponse({'success': False, 'message': 'Noto\'g\'ri ma\'lumot!'})


@login_required
def lesson_create_view(request, course_id):
    """Dars yaratish (O'qituvchi uchun)"""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    if request.method == 'POST':
        form = LessonCreateForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course

            # Order avtomatik belgilash
            last_lesson = course.lessons.order_by('-order').first()
            lesson.order = (last_lesson.order + 1) if last_lesson else 1

            lesson.save()

            messages.success(request, f'"{lesson.title}" darsi muvaffaqiyatli yaratildi!')
            return redirect('lessons:detail', course_id=course.id, lesson_id=lesson.id)
    else:
        form = LessonCreateForm()

    context = {
        'form': form,
        'course': course,
        'page_title': f'{course.title} - Yangi dars',
    }

    return render(request, 'lessons/lesson_create.html', context)


@login_required
def lesson_edit_view(request, course_id, lesson_id):
    """Dars tahrirlash"""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    if request.method == 'POST':
        form = LessonEditForm(request.POST, instance=lesson)
        if form.is_valid():
            lesson = form.save()
            messages.success(request, f'"{lesson.title}" darsi yangilandi!')
            return redirect('lessons:detail', course_id=course.id, lesson_id=lesson.id)
    else:
        form = LessonEditForm(instance=lesson)

    context = {
        'form': form,
        'course': course,
        'lesson': lesson,
        'page_title': f'{lesson.title} - Tahrirlash',
    }

    return render(request, 'lessons/lesson_edit.html', context)


@login_required
@require_http_methods(["POST"])
def lesson_delete_view(request, course_id, lesson_id):
    """Dars o'chirish"""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    lesson_title = lesson.title
    lesson.delete()

    messages.success(request, f'"{lesson_title}" darsi o\'chirildi!')
    return redirect('lessons:list', course_id=course.id)


@login_required
@require_http_methods(["POST"])
def lesson_reorder_view(request, course_id):
    """Darslar tartibini o'zgartirish"""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    try:
        lesson_orders = request.POST.getlist('lesson_order')

        for i, lesson_id in enumerate(lesson_orders, 1):
            Lesson.objects.filter(id=lesson_id, course=course).update(order=i)

        return JsonResponse({'success': True, 'message': 'Tartib o\'zgartirildi!'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


def lesson_notes_view(request, lesson_id):
    """Dars izohlar (keyinroq implement)"""
    lesson = get_object_or_404(Lesson, id=lesson_id)

    context = {
        'lesson': lesson,
        'notes': [],  # Keyinroq Notes model yaratiladi
        'page_title': f'{lesson.title} - Izohlar',
    }

    return render(request, 'lessons/lesson_notes.html', context)


# Helper function
def update_course_progress(user, course):
    """Course progress yangilash"""
    try:
        enrollment = Enrollment.objects.get(student=user, course=course)

        total_lessons = course.lessons.count()
        if total_lessons == 0:
            return

        completed_lessons = LessonProgress.objects.filter(
            student=user,
            lesson__course=course,
            is_completed=True
        ).count()

        progress = round((completed_lessons / total_lessons) * 100)
        enrollment.progress = progress

        # 100% bo'lsa kursni tugallangan deb belgilash
        if progress >= 100:
            enrollment.is_completed = True

        enrollment.save()

    except Enrollment.DoesNotExist:
        pass