from django.db import models
from django.core.validators import URLValidator


class SiteSettings(models.Model):
    # Asosiy ma'lumotlar
    site_name = models.CharField(max_length=100, default='Tibbiy Ta\'lim Platformasi')
    site_description = models.TextField(default='Professional tibbiy ta\'lim onlayn platformasi')
    site_keywords = models.TextField(help_text='SEO uchun kalit so\'zlar (vergul bilan ajrating)')
    site_logo = models.ImageField(upload_to='site/', blank=True)
    site_favicon = models.ImageField(upload_to='site/', blank=True)

    # Contact ma'lumotlari
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    # SEO sozlamalari
    google_analytics_id = models.CharField(max_length=50, blank=True)
    google_tag_manager_id = models.CharField(max_length=50, blank=True)
    meta_author = models.CharField(max_length=100, blank=True)

    # Tizim sozlamalari
    site_maintenance = models.BooleanField(default=False, help_text='Sayt texnik ishlar rejimida')
    registration_open = models.BooleanField(default=True, help_text='Ro\'yxatdan o\'tishga ruxsat')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sayt sozlamalari'
        verbose_name_plural = 'Sayt sozlamalari'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError('Faqat bitta sayt sozlamalari obyekti yaratish mumkin')
        super().save(*args, **kwargs)


class SocialNetworks(models.Model):
    # Ijtimoiy tarmoqlar
    facebook_url = models.URLField(blank=True, verbose_name='Facebook')
    instagram_url = models.URLField(blank=True, verbose_name='Instagram')
    telegram_url = models.URLField(blank=True, verbose_name='Telegram')
    youtube_url = models.URLField(blank=True, verbose_name='YouTube')
    linkedin_url = models.URLField(blank=True, verbose_name='LinkedIn')
    twitter_url = models.URLField(blank=True, verbose_name='Twitter')
    tiktok_url = models.URLField(blank=True, verbose_name='TikTok')

    # Qo'shimcha sozlamalar
    show_in_header = models.BooleanField(default=True, verbose_name='Header da ko\'rsatish')
    show_in_footer = models.BooleanField(default=True, verbose_name='Footer da ko\'rsatish')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ijtimoiy tarmoqlar'
        verbose_name_plural = 'Ijtimoiy tarmoqlar'

    def __str__(self):
        return 'Ijtimoiy tarmoqlar'

    def save(self, *args, **kwargs):
        if not self.pk and SocialNetworks.objects.exists():
            raise ValueError('Faqat bitta ijtimoiy tarmoqlar obyekti yaratish mumkin')
        super().save(*args, **kwargs)


class HeaderSettings(models.Model):
    # Header sozlamalari
    show_phone = models.BooleanField(default=True)
    show_email = models.BooleanField(default=True)
    show_search = models.BooleanField(default=True)
    show_language_switcher = models.BooleanField(default=False)

    # Header announcement
    announcement_text = models.CharField(max_length=200, blank=True, verbose_name='E\'lon matni')
    announcement_url = models.URLField(blank=True, verbose_name='E\'lon linki')
    announcement_active = models.BooleanField(default=False, verbose_name='E\'lonni ko\'rsatish')

    # Header style
    header_transparent = models.BooleanField(default=False, verbose_name='Shaffof header')
    header_sticky = models.BooleanField(default=True, verbose_name='Yapishqoq header')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Header sozlamalari'
        verbose_name_plural = 'Header sozlamalari'

    def __str__(self):
        return 'Header sozlamalari'

    def save(self, *args, **kwargs):
        if not self.pk and HeaderSettings.objects.exists():
            raise ValueError('Faqat bitta header sozlamalari obyekti yaratish mumkin')
        super().save(*args, **kwargs)


class FooterSettings(models.Model):
    # Footer asosiy ma'lumotlar
    footer_logo = models.ImageField(upload_to='footer/', blank=True)
    footer_description = models.TextField(blank=True, verbose_name='Footer tavsifi')
    copyright_text = models.CharField(
        max_length=200,
        default='© 2024 Tibbiy Ta\'lim Platformasi. Barcha huquqlar himoyalangan.',
        verbose_name='Copyright matni'
    )

    # Footer columns
    show_courses_column = models.BooleanField(default=True, verbose_name='Kurslar ustunini ko\'rsatish')
    show_company_column = models.BooleanField(default=True, verbose_name='Kompaniya ustunini ko\'rsatish')
    show_support_column = models.BooleanField(default=True, verbose_name='Yordam ustunini ko\'rsatish')
    show_contact_column = models.BooleanField(default=True, verbose_name='Aloqa ustunini ko\'rsatish')

    # Newsletter
    newsletter_title = models.CharField(max_length=100, default='Yangiliklardan xabardor bo\'ling', blank=True)
    newsletter_description = models.TextField(blank=True, verbose_name='Newsletter tavsifi')
    newsletter_active = models.BooleanField(default=True, verbose_name='Newsletter faol')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Footer sozlamalari'
        verbose_name_plural = 'Footer sozlamalari'

    def __str__(self):
        return 'Footer sozlamalari'

    def save(self, *args, **kwargs):
        if not self.pk and FooterSettings.objects.exists():
            raise ValueError('Faqat bitta footer sozlamalari obyekti yaratish mumkin')
        super().save(*args, **kwargs)


class NavbarMenu(models.Model):
    title = models.CharField(max_length=100, verbose_name='Sarlavha')
    url = models.CharField(max_length=200, help_text='URL yoki URL nomi', verbose_name='Havola')
    icon = models.CharField(max_length=50, blank=True, help_text='Font Awesome icon class', verbose_name='Ikonka')
    order = models.PositiveIntegerField(default=1, verbose_name='Tartib')
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Ota-element'
    )

    class Meta:
        ordering = ['order']
        verbose_name = 'Navbar menu'
        verbose_name_plural = 'Navbar menular'

    def __str__(self):
        if self.parent:
            return f"{self.parent.title} > {self.title}"
        return self.title


class FooterLink(models.Model):
    COLUMN_CHOICES = [
        ('courses', 'Kurslar'),
        ('company', 'Kompaniya'),
        ('support', 'Yordam'),
        ('contact', 'Aloqa'),
    ]

    title = models.CharField(max_length=100, verbose_name='Sarlavha')
    url = models.CharField(max_length=200, verbose_name='Havola')
    column = models.CharField(max_length=20, choices=COLUMN_CHOICES, default='company', verbose_name='Ustun')
    order = models.PositiveIntegerField(default=1, verbose_name='Tartib')
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    open_new_tab = models.BooleanField(default=False, verbose_name='Yangi oynada ochish')

    class Meta:
        ordering = ['column', 'order']
        verbose_name = 'Footer link'
        verbose_name_plural = 'Footer linklar'

    def __str__(self):
        return f"{self.title} ({self.get_column_display()})"


class SEOPage(models.Model):
    page_name = models.CharField(
        max_length=100,
        unique=True,
        help_text='Sahifa nomi (home, courses, lessons, etc.)',
        verbose_name='Sahifa nomi'
    )
    meta_title = models.CharField(max_length=60, blank=True, verbose_name='Meta sarlavha')
    meta_description = models.CharField(max_length=160, blank=True, verbose_name='Meta tavsif')
    meta_keywords = models.TextField(blank=True, verbose_name='Meta kalit so\'zlar')

    # Open Graph
    og_title = models.CharField(max_length=100, blank=True, help_text='Open Graph title', verbose_name='OG sarlavha')
    og_description = models.CharField(max_length=200, blank=True, verbose_name='OG tavsif')
    og_image = models.ImageField(upload_to='seo/', blank=True, verbose_name='OG rasm')

    # Twitter Card
    twitter_title = models.CharField(max_length=100, blank=True, verbose_name='Twitter sarlavha')
    twitter_description = models.CharField(max_length=200, blank=True, verbose_name='Twitter tavsif')
    twitter_image = models.ImageField(upload_to='seo/', blank=True, verbose_name='Twitter rasm')

    class Meta:
        verbose_name = 'SEO sahifa'
        verbose_name_plural = 'SEO sahifalar'

    def __str__(self):
        return self.page_name


class Testimonial(models.Model):
    name = models.CharField(max_length=100, verbose_name='Ism')
    position = models.CharField(max_length=100, blank=True, verbose_name='Lavozim')
    company = models.CharField(max_length=100, blank=True, verbose_name='Kompaniya')
    avatar = models.ImageField(upload_to='testimonials/', blank=True, verbose_name='Avatar')
    content = models.TextField(verbose_name='Sharh matni')
    rating = models.PositiveIntegerField(
        choices=[(i, f'{i} yulduz') for i in range(1, 6)],
        default=5,
        verbose_name='Baho'
    )
    is_featured = models.BooleanField(default=False, verbose_name='Asosiy sharhlar')
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']
        verbose_name = 'Sharh'
        verbose_name_plural = 'Sharhlar'

    def __str__(self):
        return f"{self.name} - {self.rating}⭐"


class Newsletter(models.Model):
    email = models.EmailField(unique=True, verbose_name='Email')
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Newsletter obunachi'
        verbose_name_plural = 'Newsletter obunachilar'

    def __str__(self):
        return self.email