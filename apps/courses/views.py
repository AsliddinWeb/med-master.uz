from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Count, Q, Avg
from django.urls import reverse

from .models import Course, Enrollment
from .forms import CourseSearchForm, CourseCreateForm, CourseEditForm
from apps.accounts.models import User
from apps.lessons.models import Lesson


def course_list_view(request):
    """Kurslar ro'yxati"""
    courses = Course.objects.filter(is_active=True).select_related('instructor').annotate(
        student_count=Count('enrollment'),
        lesson_count=Count('lessons')
    )

    # Search va Filter
    form = CourseSearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data.get('query')
        level = form.cleaned_data.get('level')
        instructor = form.cleaned_data.get('instructor')

        if query:
            courses = courses.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )

        if level:
            courses = courses.filter(level=level)

        if instructor:
            courses = courses.filter(instructor=instructor)

    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'popular':
        courses = courses.order_by('-student_count')
    elif sort_by == 'alphabetical':
        courses = courses.order_by('title')
    else:  # newest
        courses = courses.order_by('-created_at')

    # Pagination
    paginator = Paginator(courses, 12)
    page = request.GET.get('page')
    courses_page = paginator.get_page(page)

    # Statistics
    stats = {
        'total_courses': Course.objects.filter(is_active=True).count(),
        'total_instructors': User.objects.filter(role='teacher', is_active=True).count(),
        'levels': Course.LEVEL_CHOICES,
    }

    context = {
        'courses': courses_page,
        'form': form,
        'stats': stats,
        'current_sort': sort_by,
        'page_title': 'Barcha kurslar',
    }

    return render(request, 'courses/course_list.html', context)


def course_detail_view(request, course_id):
    """Kurs tafsilotlari"""
    course = get_object_or_404(
        Course.objects.select_related('instructor').prefetch_related('lessons'),
        id=course_id,
        is_active=True
    )

    # Enrollment tekshirish
    is_enrolled = False
    enrollment = None
    if request.user.is_authenticated:
        try:
            enrollment = Enrollment.objects.get(student=request.user, course=course)
            is_enrolled = True
        except Enrollment.DoesNotExist:
            pass

    # Darslar
    lessons = course.lessons.all().order_by('order')

    # Statistika
    total_students = course.enrollment_set.count()
    total_lessons = lessons.count()
    total_duration = sum(lesson.duration_minutes for lesson in lessons)

    # O'qituvchining boshqa kurslari
    instructor_other_courses = Course.objects.filter(
        instructor=course.instructor,
        is_active=True
    ).exclude(id=course.id)[:3]

    context = {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'total_students': total_students,
        'total_lessons': total_lessons,
        'total_duration': total_duration,
        'instructor_other_courses': instructor_other_courses,
        'page_title': course.title,
    }

    return render(request, 'courses/course_detail.html', context)


@login_required
@require_http_methods(["POST"])
def course_enroll_view(request, course_id):
    """Kursga yozilish"""
    course = get_object_or_404(Course, id=course_id, is_active=True)

    # Faqat talabalar yozilishi mumkin
    if request.user.role != 'student':
        messages.error(request, 'Faqat talabalar kursga yozilishi mumkin!')
        return redirect('courses:detail', course_id=course.id)

    # Allaqachon yozilganligini tekshirish
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.warning(request, 'Siz allaqachon bu kursga yozilgansiz!')
        return redirect('courses:detail', course_id=course.id)

    # Enrollment yaratish
    enrollment = Enrollment.objects.create(
        student=request.user,
        course=course
    )

    messages.success(request, f'"{course.title}" kursiga muvaffaqiyatli yozildingiz!')
    return redirect('courses:detail', course_id=course.id)


@login_required
def my_courses_view(request):
    """Mening kurslarim"""
    if request.user.role == 'student':
        # Talaba kurslari
        enrollments = Enrollment.objects.filter(
            student=request.user
        ).select_related('course', 'course__instructor').order_by('-enrolled_at')

        # Status bo'yicha filter
        status = request.GET.get('status', 'all')
        if status == 'active':
            enrollments = enrollments.filter(is_completed=False)
        elif status == 'completed':
            enrollments = enrollments.filter(is_completed=True)

        # Pagination
        paginator = Paginator(enrollments, 12)
        page = request.GET.get('page')
        enrollments_page = paginator.get_page(page)

        context = {
            'enrollments': enrollments_page,
            'current_status': status,
            'page_title': 'Mening kurslarim',
        }

        return render(request, 'courses/my_courses_student.html', context)

    elif request.user.role == 'teacher':
        # O'qituvchi kurslari
        return redirect('courses:instructor_courses')

    else:
        messages.error(request, 'Sizda kurslar mavjud emas!')
        return redirect('accounts:dashboard')


@login_required
def instructor_courses_view(request):
    """O'qituvchi kurslari"""
    if request.user.role != 'teacher':
        messages.error(request, 'Faqat o\'qituvchilar uchun!')
        return redirect('accounts:dashboard')

    # O'qituvchi kurslari
    courses = Course.objects.filter(
        instructor=request.user
    ).annotate(
        student_count=Count('enrollment'),
        lesson_count=Count('lessons')
    ).order_by('-created_at')

    # Status filter
    status = request.GET.get('status', 'all')
    if status == 'active':
        courses = courses.filter(is_active=True)
    elif status == 'inactive':
        courses = courses.filter(is_active=False)

    # Pagination
    paginator = Paginator(courses, 12)
    page = request.GET.get('page')
    courses_page = paginator.get_page(page)

    # Statistics
    stats = {
        'total_courses': courses.count(),
        'active_courses': courses.filter(is_active=True).count(),
        'total_students': Enrollment.objects.filter(course__instructor=request.user).count(),
    }

    context = {
        'courses': courses_page,
        'stats': stats,
        'current_status': status,
        'page_title': 'Mening kurslarim',
    }

    return render(request, 'courses/instructor_courses.html', context)


@login_required
def course_create_view(request):
    """Kurs yaratish"""
    if request.user.role != 'teacher':
        messages.error(request, 'Faqat o\'qituvchilar kurs yaratishi mumkin!')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = CourseCreateForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()

            messages.success(request, f'"{course.title}" kursi muvaffaqiyatli yaratildi!')
            return redirect('courses:detail', course_id=course.id)
    else:
        form = CourseCreateForm()

    context = {
        'form': form,
        'page_title': 'Yangi kurs yaratish',
    }

    return render(request, 'courses/course_create.html', context)


@login_required
def course_edit_view(request, course_id):
    """Kurs tahrirlash"""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    if request.method == 'POST':
        form = CourseEditForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'"{course.title}" kursi muvaffaqiyatli yangilandi!')
            return redirect('courses:detail', course_id=course.id)
    else:
        form = CourseEditForm(instance=course)

    context = {
        'form': form,
        'course': course,
        'page_title': f'{course.title} - Tahrirlash',
    }

    return render(request, 'courses/course_edit.html', context)


@login_required
@require_http_methods(["POST"])
def course_delete_view(request, course_id):
    """Kurs o'chirish"""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    # Soft delete - is_active = False
    course.is_active = False
    course.save()

    messages.success(request, f'"{course.title}" kursi o\'chirildi!')
    return redirect('courses:instructor_courses')


@login_required
@require_http_methods(["POST"])
def course_toggle_status_view(request, course_id):
    """Kurs holatini o'zgartirish (active/inactive)"""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    course.is_active = not course.is_active
    course.save()

    status = 'faollashtirildi' if course.is_active else 'to\'xtatildi'
    messages.success(request, f'"{course.title}" kursi {status}!')

    return redirect('courses:instructor_courses')


def category_courses_view(request, level):
    """Daraja bo'yicha kurslar"""
    level_choices = dict(Course.LEVEL_CHOICES)
    if level not in level_choices:
        messages.error(request, 'Noto\'g\'ri daraja!')
        return redirect('courses:list')

    courses = Course.objects.filter(
        is_active=True,
        level=level
    ).select_related('instructor').annotate(
        student_count=Count('enrollment')
    ).order_by('-created_at')

    # Pagination
    paginator = Paginator(courses, 12)
    page = request.GET.get('page')
    courses_page = paginator.get_page(page)

    context = {
        'courses': courses_page,
        'level': level,
        'level_display': level_choices[level],
        'page_title': f'{level_choices[level]} darajadagi kurslar',
    }

    return render(request, 'courses/category_courses.html', context)