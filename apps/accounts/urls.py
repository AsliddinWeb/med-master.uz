from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard va Profile
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/<int:user_id>/', views.public_profile_view, name='public_profile'),

    # Courses
    path('my-courses/', views.my_courses_view, name='my_courses'),

    # Password management
    path('change-password/', views.change_password_view, name='change_password'),
    path('password-reset/', views.password_reset_view, name='password_reset'),

    # Settings
    path('notifications/', views.notifications_view, name='notifications'),
    path('delete-account/', views.delete_account_view, name='delete_account'),

    # Teacher application
    path('become-teacher/', views.become_teacher_view, name='become_teacher'),
]