from django.urls import path
from . import views

app_name = 'lessons'

urlpatterns = [
    # Darslar ro'yxati va tafsilotlar
    path('course/<int:course_id>/', views.lesson_list_view, name='list'),
    path('course/<int:course_id>/lesson/<int:lesson_id>/', views.lesson_detail_view, name='detail'),

    # Dars progress
    path('lesson/<int:lesson_id>/complete/', views.mark_lesson_complete, name='complete'),
    path('lesson/<int:lesson_id>/progress/', views.update_lesson_progress, name='update_progress'),

    # Dars boshqaruvi (O'qituvchi uchun)
    path('course/<int:course_id>/create/', views.lesson_create_view, name='create'),
    path('course/<int:course_id>/lesson/<int:lesson_id>/edit/', views.lesson_edit_view, name='edit'),
    path('course/<int:course_id>/lesson/<int:lesson_id>/delete/', views.lesson_delete_view, name='delete'),
    path('course/<int:course_id>/reorder/', views.lesson_reorder_view, name='reorder'),

    # Qo'shimcha
    path('lesson/<int:lesson_id>/notes/', views.lesson_notes_view, name='notes'),
]