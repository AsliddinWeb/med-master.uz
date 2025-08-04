from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    # Test ro'yxati va tafsilotlar
    path('lesson/<int:lesson_id>/', views.quiz_list_view, name='list'),
    path('<int:quiz_id>/', views.quiz_detail_view, name='detail'),

    # Test yechish
    path('<int:quiz_id>/attempt/', views.quiz_attempt_view, name='attempt'),
    path('result/<int:attempt_id>/', views.quiz_result_view, name='result'),

    # Test yaratish (O'qituvchi uchun)
    path('lesson/<int:lesson_id>/create/', views.quiz_create_view, name='create'),
    path('<int:quiz_id>/add-questions/', views.quiz_add_questions_view, name='add_questions'),
    path('question/<int:question_id>/delete/', views.question_delete_view, name='delete_question'),

    # Statistika va boshqaruv
    path('<int:quiz_id>/statistics/', views.quiz_statistics_view, name='statistics'),
    path('<int:quiz_id>/toggle-status/', views.quiz_toggle_status_view, name='toggle_status'),

    # Foydalanuvchi natijalar
    path('my-results/', views.my_quiz_results_view, name='my_results'),

    # AJAX endpoints
    path('<int:quiz_id>/save-progress/', views.save_quiz_progress, name='save_progress'),
]