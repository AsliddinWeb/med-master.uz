from django import template
from django.conf import settings
from apps.core.models import SiteSettings

register = template.Library()


@register.simple_tag
def site_name():
    """Sayt nomi"""
    try:
        site_settings = SiteSettings.objects.first()
        return site_settings.site_name if site_settings else 'Tibbiy Ta\'lim Platformasi'
    except:
        return 'Tibbiy Ta\'lim Platformasi'


@register.simple_tag
def site_logo():
    """Sayt logosi"""
    try:
        site_settings = SiteSettings.objects.first()
        if site_settings and site_settings.site_logo:
            return site_settings.site_logo.url
    except:
        pass
    return '/static/images/logo.png'  # Default logo


@register.filter
def truncate_words_custom(text, limit):
    """So'zlarni kesish"""
    words = text.split()
    if len(words) > limit:
        return ' '.join(words[:limit]) + '...'
    return text


@register.simple_tag
def current_year():
    """Joriy yil"""
    from datetime import datetime
    return datetime.now().year


@register.simple_tag(takes_context=True)
def active_link(context, url_name, css_class='text-blue-600'):
    """Aktiv link highlight"""
    request = context['request']
    from django.urls import reverse, NoReverseMatch

    try:
        url = reverse(url_name)
        if request.path == url:
            return css_class
    except NoReverseMatch:
        pass
    return ''


@register.inclusion_tag('core/components/social_links.html')
def social_links(show_labels=False):
    """Ijtimoiy tarmoq linklari"""
    from apps.core.models import SocialNetworks

    try:
        social = SocialNetworks.objects.first()
    except:
        social = None

    return {
        'social': social,
        'show_labels': show_labels,
    }


@register.simple_tag
def seo_title(page_title=None):
    """SEO title yaratish"""
    site_name = site_name()
    if page_title:
        return f"{page_title} | {site_name}"
    return site_name