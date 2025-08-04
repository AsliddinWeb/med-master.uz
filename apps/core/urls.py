from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Asosiy sahifalar
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('search/', views.search_view, name='search'),

    # Static sahifalar
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service_view, name='terms_of_service'),
    path('faq/', views.faq_view, name='faq'),

    # AJAX endpoints
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),

    # Texnik sahifalar
    path('maintenance/', views.maintenance_view, name='maintenance'),
]