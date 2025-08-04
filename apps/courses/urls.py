from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Kurslar ro'yxati va tafsilotlar
    path('', views.course_list_view, name='list'),
    path('<int:course_id>/', views.course_detail_view, name='detail'),
    path('level/<str:level>/', views.category_courses_view, name='category'),

    # Kursga yozilish
    path('enroll/<int:course_id>/', views.course_enroll_view, name='enroll'),

    # Foydalanuvchi kurslari
    path('my-courses/', views.my_courses_view, name='my_courses'),
    path('instructor/courses/', views.instructor_courses_view, name='instructor_courses'),

    # Kurs boshqaruvi (O'qituvchi uchun)
    path('create/', views.course_create_view, name='create'),
    path('edit/<int:course_id>/', views.course_edit_view, name='edit'),
    path('delete/<int:course_id>/', views.course_delete_view, name='delete'),
    path('toggle-status/<int:course_id>/', views.course_toggle_status_view, name='toggle_status'),
]