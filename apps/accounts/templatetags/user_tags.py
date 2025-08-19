# apps/accounts/templatetags/user_tags.py

from django import template
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.utils.html import format_html

register = template.Library()
User = get_user_model()

@register.simple_tag
def user_avatar(user, size='w-10 h-10'):
    """Foydalanuvchi avatari"""
    if not user:
        return ''
    
    try:
        # Check if user has profile with avatar
        if hasattr(user, 'profile') and user.profile and hasattr(user.profile, 'avatar') and user.profile.avatar:
            avatar_html = format_html(
                '<img src="{}" alt="{}" class="{} rounded-full object-cover border-2 border-gray-200">',
                user.profile.avatar.url,
                user.get_full_name() or user.username,
                size
            )
            return mark_safe(avatar_html)
    except Exception as e:
        pass

    # Default avatar with initials
    if user.first_name and user.last_name:
        initials = f"{user.first_name[0]}{user.last_name[0]}"
    elif user.first_name:
        initials = user.first_name[:2]
    elif hasattr(user, 'username'):
        initials = user.username[:2]
    else:
        initials = "?"

    # Color based on username hash
    colors = [
        'bg-blue-500', 'bg-green-500', 'bg-purple-500',
        'bg-pink-500', 'bg-indigo-500', 'bg-red-500'
    ]
    
    username = getattr(user, 'username', 'user')
    color = colors[hash(username) % len(colors)]

    avatar_html = format_html(
        '<div class="{} {} rounded-full flex items-center justify-center text-white font-semibold">{}</div>',
        size,
        color,
        initials.upper()
    )
    
    return mark_safe(avatar_html)

@register.simple_tag
def user_role_badge(user):
    """Foydalanuvchi roli badge"""
    if not user:
        return ''
        
    role_config = {
        'student': {'name': 'Talaba', 'class': 'bg-blue-100 text-blue-800'},
        'teacher': {'name': 'O\'qituvchi', 'class': 'bg-green-100 text-green-800'},
        'admin': {'name': 'Administrator', 'class': 'bg-purple-100 text-purple-800'},
    }

    user_role = getattr(user, 'role', 'student')
    config = role_config.get(user_role, {'name': user_role, 'class': 'bg-gray-100 text-gray-800'})

    badge_html = format_html(
        '<span class="px-2 py-1 text-xs font-medium rounded-full {}">{}</span>',
        config['class'],
        config['name']
    )
    
    return mark_safe(badge_html)

# Math filters qo'shing
@register.filter
def percentage(value, total):
    """Foizni hisoblash"""
    try:
        if float(total) == 0:
            return 0
        return round((float(value) / float(total)) * 100, 1)
    except:
        return 0

@register.filter
def mul(value, arg):
    """Ko'paytirish"""
    try:
        return float(value) * float(arg)
    except:
        return 0

@register.filter
def div(value, arg):
    """Bo'lish"""
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except:
        return 0