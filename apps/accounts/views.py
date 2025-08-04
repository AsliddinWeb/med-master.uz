from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Count, Q, Avg

from .models import User, Profile
from .forms import (
    UserRegistrationForm, UserLoginForm, ProfileUpdateForm,
    PasswordChangeForm, PasswordResetForm, TeacherApplicationForm
)
from apps.courses.models import Course, Enrollment
from apps.lessons.models import LessonProgress
from apps.quizzes.models import QuizAttempt


def register_view(request):
    """Ro'yxatdan o'tish"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Profile yaratish
            Profile.objects.create(user=user)

            # Auto login
            login(request, user)

            messages.success(request, f'Xush kelibsiz, {user.first_name}! Hisobingiz yaratildi.')
            return redirect('accounts:dashboard')
    else:
        form = UserRegistrationForm()

    context = {
        'form': form,
        'page_title': 'Ro\'yxatdan o\'tish',
    }

    return render(request, 'accounts/register.html', context)


def login_view(request):
    """Tizimga kirish"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)

                # Next URL ni tekshirish
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)

                messages.success(request, f'Xush kelibsiz, {user.first_name}!')
                return redirect('accounts:dashboard')
            else:
                messages.error(request, 'Email yoki parol noto\'g\'ri!')
    else:
        form = UserLoginForm()

    context = {
        'form': form,
        'page_title': 'Tizimga kirish',
    }

    return render(request, 'accounts/login.html', context)


@login_required
def logout_view(request):
    """Tizimdan chiqish"""
    logout(request)
    messages.success(request, 'Tizimdan muvaffaqiyatli chiqdingiz!')
    return redirect('core:home')


@login_required
def dashboard_view(request):
    """Shaxsiy kabinet"""
    user = request.user

    # Statistika
    if user.role == 'student':
        # Talaba statistikasi
        enrollments = Enrollment.objects.filter(student=user)
        completed_lessons = LessonProgress.objects.filter(
            student=user,
            is_completed=True
        ).count()

        quiz_attempts = QuizAttempt.objects.filter(student=user)
        avg_score = quiz_attempts.aggregate(
            avg_score=Avg('score')
        )['avg_score'] or 0

        stats = {
            'total_courses': enrollments.count(),
            'active_courses': enrollments.filter(is_completed=False).count(),
            'completed_courses': enrollments.filter(is_completed=True).count(),
            'completed_lessons': completed_lessons,
            'quiz_attempts': quiz_attempts.count(),
            'average_score': round(avg_score, 1),
        }

        # So'nggi faoliyat
        recent_enrollments = enrollments.select_related('course')[:5]
        recent_quiz_attempts = quiz_attempts.select_related('quiz__lesson__course')[:5]

        context = {
            'stats': stats,
            'recent_enrollments': recent_enrollments,
            'recent_quiz_attempts': recent_quiz_attempts,
        }

    elif user.role == 'teacher':
        # O'qituvchi statistikasi
        my_courses = Course.objects.filter(instructor=user)
        total_students = Enrollment.objects.filter(
            course__instructor=user
        ).count()

        stats = {
            'total_courses': my_courses.count(),
            'active_courses': my_courses.filter(is_active=True).count(),
            'total_students': total_students,
            'total_lessons': sum(course.lessons.count() for course in my_courses),
        }

        # So'nggi enrollmentlar
        recent_enrollments = Enrollment.objects.filter(
            course__instructor=user
        ).select_related('student', 'course')[:10]

        context = {
            'stats': stats,
            'my_courses': my_courses[:5],
            'recent_enrollments': recent_enrollments,
        }

    else:
        # Admin statistikasi
        stats = {
            'total_users': User.objects.count(),
            'total_students': User.objects.filter(role='student').count(),
            'total_teachers': User.objects.filter(role='teacher').count(),
            'total_courses': Course.objects.count(),
        }

        context = {
            'stats': stats,
        }

    context.update({
        'page_title': 'Shaxsiy kabinet',
        'user_role': user.role,
    })

    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_view(request):
    """Profil ko'rish"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    context = {
        'profile': profile,
        'page_title': 'Mening profilim',
    }

    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit_view(request):
    """Profilni tahrirlash"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()

            # Profile ma'lumotlarini yangilash
            profile.bio = form.cleaned_data.get('bio', '')
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
            profile.save()

            messages.success(request, 'Profil muvaffaqiyatli yangilandi!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user, initial={
            'bio': profile.bio,
        })

    context = {
        'form': form,
        'profile': profile,
        'page_title': 'Profilni tahrirlash',
    }

    return render(request, 'accounts/profile_edit.html', context)


@login_required
def my_courses_view(request):
    """Mening kurslarim"""
    user = request.user

    if user.role == 'student':
        # Talaba kurslari
        enrollments = Enrollment.objects.filter(
            student=user
        ).select_related('course', 'course__instructor').order_by('-enrolled_at')

        # Pagination
        paginator = Paginator(enrollments, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'enrollments': page_obj,
            'page_title': 'Mening kurslarim',
        }

    elif user.role == 'teacher':
        # O'qituvchi kurslari
        courses = Course.objects.filter(
            instructor=user
        ).annotate(
            student_count=Count('enrollment')
        ).order_by('-created_at')

        # Pagination
        paginator = Paginator(courses, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'courses': page_obj,
            'page_title': 'Mening kurslarim',
        }

    return render(request, 'accounts/my_courses.html', context)


@login_required
def change_password_view(request):
    """Parolni o'zgartirish"""
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Parol muvaffaqiyatli o\'zgartirildi!')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(user=request.user)

    context = {
        'form': form,
        'page_title': 'Parolni o\'zgartirish',
    }

    return render(request, 'accounts/change_password.html', context)


def password_reset_view(request):
    """Parolni tiklash"""
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Email yuborish logic (keyinroq)
            messages.success(request, 'Parolni tiklash havolasi emailingizga yuborildi!')
            return redirect('accounts:login')
    else:
        form = PasswordResetForm()

    context = {
        'form': form,
        'page_title': 'Parolni tiklash',
    }

    return render(request, 'accounts/password_reset.html', context)


def public_profile_view(request, user_id):
    """Ommaviy profil ko'rish"""
    user = get_object_or_404(User, id=user_id, is_active=True)

    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = None

    # O'qituvchi bo'lsa, kurslarini ko'rsatish
    courses = None
    if user.role == 'teacher':
        courses = Course.objects.filter(
            instructor=user,
            is_active=True
        ).annotate(
            student_count=Count('enrollment')
        )[:6]

    context = {
        'profile_user': user,
        'profile': profile,
        'courses': courses,
        'page_title': f'{user.get_full_name()} - Profil',
    }

    return render(request, 'accounts/public_profile.html', context)


@login_required
@require_http_methods(["POST"])
def delete_account_view(request):
    """Hisobni o'chirish"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        user = request.user

        # Faqat o'zini o'chirishi mumkin
        user.is_active = False
        user.save()

        logout(request)

        return JsonResponse({
            'success': True,
            'message': 'Hisobingiz o\'chirildi!'
        })

    return JsonResponse({'success': False})


@login_required
def notifications_view(request):
    """Bildirishnomalar (keyinroq to'liq implement qilamiz)"""
    # Hozircha bo'sh
    notifications = []

    context = {
        'notifications': notifications,
        'page_title': 'Bildirishnomalar',
    }

    return render(request, 'accounts/notifications.html', context)


@login_required
def become_teacher_view(request):
    """O'qituvchi bo'lish uchun ariza"""
    if request.user.role == 'teacher':
        messages.info(request, 'Siz allaqachon o\'qituvchisiz!')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = TeacherApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            # Teacher application yaratish (keyinroq model yaratamiz)
            messages.success(request, 'Arizangiz qabul qilindi! Tez orada javob beramiz.')
            return redirect('accounts:dashboard')
    else:
        form = TeacherApplicationForm()

    context = {
        'form': form,
        'page_title': 'O\'qituvchi bo\'lish',
    }

    return render(request, 'accounts/become_teacher.html', context)