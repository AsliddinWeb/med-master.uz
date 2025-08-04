from .models import (
    SiteSettings, SocialNetworks, HeaderSettings,
    FooterSettings, NavbarMenu, FooterLink, SEOPage
)
from django.core.cache import cache
from django.conf import settings


def site_settings(request):
    """Global sayt sozlamalari"""
    # Cache dan olishga harakat qilish (performance uchun)
    site_config = cache.get('site_settings')

    if not site_config:
        try:
            site_config = SiteSettings.objects.first()
            # 1 soatga cache qilish
            cache.set('site_settings', site_config, 3600)
        except SiteSettings.DoesNotExist:
            site_config = None

    return {
        'site_settings': site_config,
        'DEBUG': settings.DEBUG,
    }


def social_networks(request):
    """Ijtimoiy tarmoqlar"""
    social_data = cache.get('social_networks')

    if not social_data:
        try:
            social_data = SocialNetworks.objects.first()
            cache.set('social_networks', social_data, 3600)
        except SocialNetworks.DoesNotExist:
            social_data = None

    return {
        'social_networks': social_data,
    }


def header_settings(request):
    """Header sozlamalari"""
    header_config = cache.get('header_settings')

    if not header_config:
        try:
            header_config = HeaderSettings.objects.first()
            cache.set('header_settings', header_config, 3600)
        except HeaderSettings.DoesNotExist:
            header_config = None

    return {
        'header_settings': header_config,
    }


def footer_settings(request):
    """Footer sozlamalari"""
    footer_config = cache.get('footer_settings')

    if not footer_config:
        try:
            footer_config = FooterSettings.objects.first()
            cache.set('footer_settings', footer_config, 3600)
        except FooterSettings.DoesNotExist:
            footer_config = None

    return {
        'footer_settings': footer_config,
    }


def navigation_menus(request):
    """Navigation menular"""
    nav_data = cache.get('navigation_menus')

    if not nav_data:
        # Navbar menu (parent elements faqat, children bilan)
        navbar_menu = NavbarMenu.objects.filter(
            is_active=True,
            parent=None
        ).prefetch_related(
            'children'
        ).order_by('order')

        # Footer linklar (ustunlar bo'yicha guruhlangan)
        footer_links_queryset = FooterLink.objects.filter(is_active=True).order_by('column', 'order')

        # Footer linklarni ustunlar bo'yicha guruhlash
        footer_links = {}
        for link in footer_links_queryset:
            if link.column not in footer_links:
                footer_links[link.column] = []
            footer_links[link.column].append(link)

        nav_data = {
            'navbar_menu': navbar_menu,
            'footer_links': footer_links,
        }

        cache.set('navigation_menus', nav_data, 3600)

    return nav_data


def seo_context(request):
    """SEO ma'lumotlari"""
    # URL dan sahifa nomini aniqlash
    path = request.path.strip('/')

    if not path:
        page_name = 'home'
    else:
        page_name = path.split('/')[0]

    # Cache key
    cache_key = f'seo_page_{page_name}'
    seo_data = cache.get(cache_key)

    if not seo_data:
        try:
            seo_page = SEOPage.objects.get(page_name=page_name)
        except SEOPage.DoesNotExist:
            # Default SEO ma'lumotlari
            site_config = SiteSettings.objects.first()
            seo_page = None

            # Default meta ma'lumotlar
            default_meta = {
                'title': site_config.site_name if site_config else 'Tibbiy Ta\'lim Platformasi',
                'description': site_config.site_description if site_config else 'Professional tibbiy ta\'lim',
                'keywords': site_config.site_keywords if site_config else 'tibbiyot, ta\'lim, kurs',
            }
        else:
            default_meta = None

        seo_data = {
            'seo_page': seo_page,
            'default_meta': default_meta,
            'current_page': page_name,
        }

        cache.set(cache_key, seo_data, 3600)

    return seo_data


def user_context(request):
    """Foydalanuvchi konteksti"""
    context = {
        'is_authenticated': request.user.is_authenticated,
    }

    if request.user.is_authenticated:
        context.update({
            'user_role': getattr(request.user, 'role', 'student'),
            'user_full_name': request.user.get_full_name() or request.user.username,
            'is_student': getattr(request.user, 'role', '') == 'student',
            'is_teacher': getattr(request.user, 'role', '') == 'teacher',
            'is_admin': getattr(request.user, 'role', '') == 'admin',
        })

    return context


def maintenance_mode(request):
    """Texnik ishlar rejimi"""
    site_config = SiteSettings.objects.first()

    return {
        'maintenance_mode': site_config.site_maintenance if site_config else False,
        'registration_open': site_config.registration_open if site_config else True,
    }


def breadcrumbs_context(request):
    """Breadcrumbs uchun kontekst"""
    path_parts = request.path.strip('/').split('/')
    breadcrumbs = []

    # Breadcrumbs yaratish
    current_path = ''
    for part in path_parts:
        if part:
            current_path += f'/{part}'
            breadcrumbs.append({
                'name': part.replace('-', ' ').replace('_', ' ').title(),
                'url': current_path
            })

    return {
        'breadcrumbs': breadcrumbs,
    }


def global_counters(request):
    """Global hisoblagichlar (statistika uchun)"""
    from apps.courses.models import Course
    from apps.accounts.models import User
    from apps.lessons.models import Lesson

    counters = cache.get('global_counters')

    if not counters:
        counters = {
            'total_courses': Course.objects.filter(is_active=True).count(),
            'total_students': User.objects.filter(role='student', is_active=True).count(),
            'total_teachers': User.objects.filter(role='teacher', is_active=True).count(),
            'total_lessons': Lesson.objects.count(),
        }

        # 30 daqiqaga cache
        cache.set('global_counters', counters, 1800)

    return {
        'counters': counters,
    }