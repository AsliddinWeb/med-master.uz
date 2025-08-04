from django import template
from django.contrib.auth import get_user_model
from apps.courses.models import Enrollment
from apps.lessons.models import LessonProgress

register = template.Library()
User = get_user_model()


@register.simple_tag
def user_avatar(user, size='w-10 h-10'):
    """Foydalanuvchi avatari"""
    try:
        if user.profile and user.profile.avatar:
            return f'<img src="{user.profile.avatar.url}" alt="{user.get_full_name()}" class="{size} rounded-full object-cover border-2 border-gray-200">'
    except:
        pass

    # Default avatar - initials
    if user.first_name and user.last_name:
        initials = f"{user.first_name[0]}{user.last_name[0]}"
    else:
        initials = user.username[:2] if user.username else "?"

    colors = [
        'bg-blue-500', 'bg-green-500', 'bg-purple-500',
        'bg-pink-500', 'bg-indigo-500', 'bg-red-500'
    ]
    color = colors[hash(user.username) % len(colors)]

    return f'''
    <div class="{size} {color} rounded-full flex items-center justify-center text-white font-semibold">
        {initials.upper()}
    </div>
    '''


@register.filter
def user_role_badge(user):
    """Foydalanuvchi roli badge"""
    role_config = {
        'student': {'name': 'Talaba', 'class': 'bg-blue-100 text-blue-800'},
        'teacher': {'name': 'O\'qituvchi', 'class': 'bg-green-100 text-green-800'},
        'admin': {'name': 'Administrator', 'class': 'bg-purple-100 text-purple-800'},
    }

    config = role_config.get(user.role, {'name': user.role, 'class': 'bg-gray-100 text-gray-800'})

    return f'<span class="px-2 py-1 text-xs font-medium rounded-full {config["class"]}">{config["name"]}</span>'


@register.filter
def user_stats(user):
    """Foydalanuvchi statistikasi"""
    if user.role == 'student':
        return {
            'enrolled_courses': Enrollment.objects.filter(student=user).count(),
            'completed_courses': Enrollment.objects.filter(student=user, is_completed=True).count(),
            'completed_lessons': LessonProgress.objects.filter(student=user, is_completed=True).count(),
        }
    elif user.role == 'teacher':
        from apps.courses.models import Course
        return {
            'created_courses': Course.objects.filter(instructor=user).count(),
            'total_students': Enrollment.objects.filter(course__instructor=user).count(),
        }
    return {}


@register.simple_tag
def user_progress_summary(user):
    """Foydalanuvchi progress xulosasi"""
    if user.role != 'student':
        return None

    enrollments = Enrollment.objects.filter(student=user)
    if not enrollments.exists():
        return None

    total_progress = sum(e.progress for e in enrollments)
    avg_progress = total_progress / enrollments.count()

    return {
        'total_courses': enrollments.count(),
        'avg_progress': round(avg_progress, 1),
        'completed_courses': enrollments.filter(is_completed=True).count(),
    }


@register.inclusion_tag('accounts/components/user_card.html')
def user_card(user, show_stats=False):
    """Foydalanuvchi kartasi"""
    return {
        'user': user,
        'show_stats': show_stats,
    }


@register.filter
def user_full_name_or_username(user):
    """To'liq ism yoki username"""
    full_name = user.get_full_name()
    return full_name if full_name.strip() else user.username


@register.simple_tag
def user_online_status(user):
    """Foydalanuvchi online holati (keyinroq implement)"""
    # Hozircha barcha foydalanuvchilar offline
    return '<span class="w-3 h-3 bg-gray-400 rounded-full"></span>'


@register.filter
def user_join_date(user):
    """Ro'yxatdan o'tgan sana"""
    return user.date_joined.strftime('%B %Y')