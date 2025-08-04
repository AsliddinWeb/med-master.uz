from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Count

from apps.courses.models import Course
from apps.accounts.models import User
from apps.lessons.models import Lesson
from .models import Testimonial, Newsletter
from .forms import NewsletterForm, ContactForm


def home_view(request):
    """Bosh sahifa"""
    # Featured kurslar (eng mashhur 6 ta)
    featured_courses = Course.objects.filter(is_active=True).annotate(
        student_count=Count('enrollment')
    ).order_by('-student_count')[:6]

    # Featured testimonials
    testimonials = Testimonial.objects.filter(is_active=True, is_featured=True)[:6]

    # Statistika
    stats = {
        'total_courses': Course.objects.filter(is_active=True).count(),
        'total_students': User.objects.filter(role='student', is_active=True).count(),
        'total_teachers': User.objects.filter(role='teacher', is_active=True).count(),
        'total_lessons': Lesson.objects.count(),
    }

    # Newsletter form
    newsletter_form = NewsletterForm()

    context = {
        'featured_courses': featured_courses,
        'testimonials': testimonials,
        'stats': stats,
        'newsletter_form': newsletter_form,
        'page_title': 'Bosh sahifa',
    }

    return render(request, 'pages/home.html', context)


def about_view(request):
    """Biz haqimizda sahifasi"""
    # O'qituvchilar
    teachers = User.objects.filter(
        role='teacher',
        is_active=True
    ).select_related('profile')[:8]

    # Barcha testimonials
    testimonials = Testimonial.objects.filter(is_active=True)

    context = {
        'teachers': teachers,
        'testimonials': testimonials,
        'page_title': 'Biz haqimizda',
    }

    return render(request, 'pages/about.html', context)


def contact_view(request):
    """Aloqa sahifasi"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Contact form ma'lumotlarini saqlash (keyinroq model yaratamiz)
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Email yuborish (keyinroq)
            # send_contact_email(name, email, subject, message)

            messages.success(request, 'Xabaringiz muvaffaqiyatli yuborildi!')
            return redirect('core:contact')
    else:
        form = ContactForm()

    context = {
        'form': form,
        'page_title': 'Aloqa',
    }

    return render(request, 'pages/contact.html', context)


@require_http_methods(["POST"])
def newsletter_subscribe(request):
    """Newsletter obuna (AJAX)"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = NewsletterForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']

            # Newsletter obyektini yaratish yoki yangilash
            newsletter, created = Newsletter.objects.get_or_create(
                email=email,
                defaults={'is_active': True}
            )

            if created:
                return JsonResponse({
                    'success': True,
                    'message': 'Muvaffaqiyatli obuna bo\'ldingiz!'
                })
            else:
                if newsletter.is_active:
                    return JsonResponse({
                        'success': False,
                        'message': 'Siz allaqachon obuna bo\'lgansiz!'
                    })
                else:
                    newsletter.is_active = True
                    newsletter.save()
                    return JsonResponse({
                        'success': True,
                        'message': 'Obunangiz qayta faollashtirildi!'
                    })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Email manzil noto\'g\'ri!'
            })

    return JsonResponse({'success': False, 'message': 'Noto\'g\'ri so\'rov!'})


def search_view(request):
    """Qidiruv sahifasi"""
    query = request.GET.get('q', '').strip()
    results = []
    total_results = 0

    if query:
        # Kurslarda qidirish
        course_results = Course.objects.filter(
            title__icontains=query,
            is_active=True
        ).select_related('instructor')

        # Darslarda qidirish
        lesson_results = Lesson.objects.filter(
            title__icontains=query
        ).select_related('course')

        results = {
            'courses': course_results[:10],
            'lessons': lesson_results[:10],
        }

        total_results = course_results.count() + lesson_results.count()

    context = {
        'query': query,
        'results': results,
        'total_results': total_results,
        'page_title': f'Qidiruv: {query}' if query else 'Qidiruv',
    }

    return render(request, 'pages/search.html', context)


def privacy_policy_view(request):
    """Maxfiylik siyosati"""
    context = {
        'page_title': 'Maxfiylik siyosati',
    }
    return render(request, 'pages/privacy_policy.html', context)


def terms_of_service_view(request):
    """Foydalanish shartlari"""
    context = {
        'page_title': 'Foydalanish shartlari',
    }
    return render(request, 'pages/terms_of_service.html', context)


def faq_view(request):
    """Tez-tez so'raladigan savollar"""
    # FAQ ma'lumotlari (keyinroq model yaratamiz)
    faqs = [
        {
            'question': 'Kursga qanday yozilish mumkin?',
            'answer': 'Kurs sahifasidagi "Kursga yozilish" tugmasini bosing va to\'lovni amalga oshiring.'
        },
        {
            'question': 'Kursni tugatgandan keyin sertifikat berilazimi?',
            'answer': 'Ha, kursni muvaffaqiyatli tugatgandan keyin elektron sertifikat beriladi.'
        },
        # Boshqa savollar...
    ]

    context = {
        'faqs': faqs,
        'page_title': 'Tez-tez so\'raladigan savollar',
    }
    return render(request, 'pages/faq.html', context)


def maintenance_view(request):
    """Texnik ishlar sahifasi"""
    context = {
        'page_title': 'Texnik ishlar',
    }
    return render(request, 'pages/maintenance.html', context)


def handler404(request, exception):
    """404 xatolik sahifasi"""
    context = {
        'page_title': 'Sahifa topilmadi',
    }
    return render(request, 'pages/404.html', context, status=404)


def handler500(request):
    """500 xatolik sahifasi"""
    context = {
        'page_title': 'Server xatoligi',
    }
    return render(request, 'pages/500.html', context, status=500)