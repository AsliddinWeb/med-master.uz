from django.contrib import admin
from .models import (
    SiteSettings, SocialNetworks, HeaderSettings, FooterSettings,
    NavbarMenu, FooterLink, SEOPage, Testimonial, Newsletter
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'site_maintenance', 'registration_open', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('site_name', 'site_description', 'site_keywords')
        }),
        ('Logo va Favicon', {
            'fields': ('site_logo', 'site_favicon')
        }),
        ('Aloqa ma\'lumotlari', {
            'fields': ('phone', 'email', 'address')
        }),
        ('SEO sozlamalari', {
            'fields': ('google_analytics_id', 'google_tag_manager_id', 'meta_author')
        }),
        ('Tizim sozlamalari', {
            'fields': ('site_maintenance', 'registration_open')
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SocialNetworks)
class SocialNetworksAdmin(admin.ModelAdmin):
    list_display = ('show_in_header', 'show_in_footer', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Ijtimoiy tarmoq havolalari', {
            'fields': (
                'facebook_url', 'instagram_url', 'telegram_url',
                'youtube_url', 'linkedin_url', 'twitter_url', 'tiktok_url'
            )
        }),
        ('Ko\'rsatish sozlamalari', {
            'fields': ('show_in_header', 'show_in_footer')
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return not SocialNetworks.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HeaderSettings)
class HeaderSettingsAdmin(admin.ModelAdmin):
    list_display = ('show_phone', 'show_email', 'announcement_active', 'header_sticky', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Ko\'rsatish sozlamalari', {
            'fields': ('show_phone', 'show_email', 'show_search', 'show_language_switcher')
        }),
        ('E\'lon sozlamalari', {
            'fields': ('announcement_text', 'announcement_url', 'announcement_active')
        }),
        ('Header stil sozlamalari', {
            'fields': ('header_transparent', 'header_sticky')
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return not HeaderSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(FooterSettings)
class FooterSettingsAdmin(admin.ModelAdmin):
    list_display = ('newsletter_active', 'show_courses_column', 'show_company_column', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Footer asosiy ma\'lumotlar', {
            'fields': ('footer_logo', 'footer_description', 'copyright_text')
        }),
        ('Ustunlar sozlamalari', {
            'fields': (
                'show_courses_column', 'show_company_column',
                'show_support_column', 'show_contact_column'
            )
        }),
        ('Newsletter sozlamalari', {
            'fields': ('newsletter_title', 'newsletter_description', 'newsletter_active')
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return not FooterSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(NavbarMenu)
class NavbarMenuAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'parent', 'order', 'is_active')
    list_filter = ('is_active', 'parent')
    search_fields = ('title', 'url')
    list_editable = ('order', 'is_active')
    ordering = ('parent__order', 'parent__title', 'order')

    fieldsets = (
        ('Menu ma\'lumotlari', {
            'fields': ('title', 'url', 'icon', 'parent')
        }),
        ('Sozlamalar', {
            'fields': ('order', 'is_active')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')


@admin.register(FooterLink)
class FooterLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'column', 'order', 'is_active', 'open_new_tab')
    list_filter = ('column', 'is_active', 'open_new_tab')
    search_fields = ('title', 'url')
    list_editable = ('order', 'is_active')
    ordering = ('column', 'order')

    fieldsets = (
        ('Link ma\'lumotlari', {
            'fields': ('title', 'url', 'column')
        }),
        ('Sozlamalar', {
            'fields': ('order', 'is_active', 'open_new_tab')
        }),
    )


@admin.register(SEOPage)
class SEOPageAdmin(admin.ModelAdmin):
    list_display = ('page_name', 'meta_title', 'og_title', 'twitter_title')
    search_fields = ('page_name', 'meta_title', 'meta_description')

    fieldsets = (
        ('Sahifa', {
            'fields': ('page_name',)
        }),
        ('Meta taglar', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords')
        }),
        ('Open Graph', {
            'fields': ('og_title', 'og_description', 'og_image'),
            'classes': ('collapse',)
        }),
        ('Twitter Card', {
            'fields': ('twitter_title', 'twitter_description', 'twitter_image'),
            'classes': ('collapse',)
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Page name uchun yordam matni
        if 'page_name' in form.base_fields:
            form.base_fields['page_name'].help_text = (
                'Masalan: home, courses, lessons, about, contact va hokazo'
            )
        return form


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'company', 'rating', 'is_featured', 'is_active', 'created_at')
    list_filter = ('rating', 'is_featured', 'is_active', 'created_at')
    search_fields = ('name', 'position', 'company', 'content')
    list_editable = ('is_featured', 'is_active')
    ordering = ('-is_featured', '-created_at')

    fieldsets = (
        ('Shaxsiy ma\'lumotlar', {
            'fields': ('name', 'position', 'company', 'avatar')
        }),
        ('Sharh ma\'lumotlari', {
            'fields': ('content', 'rating')
        }),
        ('Sozlamalar', {
            'fields': ('is_featured', 'is_active')
        }),
    )

    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-is_featured', '-created_at')


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
    list_editable = ('is_active',)
    ordering = ('-subscribed_at',)
    readonly_fields = ('subscribed_at',)

    fieldsets = (
        ('Obunachi ma\'lumotlari', {
            'fields': ('email', 'is_active')
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('subscribed_at',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Newsletter orqali qo'shilishi kerak, admin orqali emas
        return False


# Custom admin site sozlamalari
admin.site.site_header = 'Tibbiy Ta\'lim Platformasi'
admin.site.site_title = 'Admin Panel'
admin.site.index_title = 'Boshqaruv Paneli'


# Admin guruhini yaratish
class CoreAdminGroup:
    """Core sozlamalar uchun admin grup"""
    pass


# Admin interface ni yaxshilash uchun
class CoreAdminMixin:
    """Core admin uchun umumiy mixin"""

    def save_model(self, request, obj, form, change):
        if not change:  # Yangi obyekt yaratilganda
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    class Media:
        css = {
            'all': ('admin/css/core_admin.css',)
        }
        js = ('admin/js/core_admin.js',)