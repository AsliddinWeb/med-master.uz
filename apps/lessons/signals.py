from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import LessonProgress
from apps.courses.models import Enrollment


@receiver(post_save, sender=LessonProgress)
def update_course_progress_on_lesson_complete(sender, instance, **kwargs):
    """Dars tugallanganda course progress yangilash"""
    if instance.is_completed:
        try:
            enrollment = Enrollment.objects.get(
                student=instance.student,
                course=instance.lesson.course
            )

            # Course dagi barcha darslar
            total_lessons = instance.lesson.course.lessons.count()
            if total_lessons == 0:
                return

            # Tugallangan darslar
            completed_lessons = LessonProgress.objects.filter(
                student=instance.student,
                lesson__course=instance.lesson.course,
                is_completed=True
            ).count()

            # Progress hisoblash
            progress = round((completed_lessons / total_lessons) * 100)
            enrollment.progress = progress

            # 100% bo'lsa kursni tugallangan deb belgilash
            if progress >= 100:
                enrollment.is_completed = True

            enrollment.save()

        except Enrollment.DoesNotExist:
            pass


@receiver(post_delete, sender=LessonProgress)
def update_course_progress_on_lesson_delete(sender, instance, **kwargs):
    """Lesson progress o'chirilganda course progress yangilash"""
    try:
        enrollment = Enrollment.objects.get(
            student=instance.student,
            course=instance.lesson.course
        )

        total_lessons = instance.lesson.course.lessons.count()
        if total_lessons == 0:
            enrollment.progress = 0
            enrollment.is_completed = False
            enrollment.save()
            return

        completed_lessons = LessonProgress.objects.filter(
            student=instance.student,
            lesson__course=instance.lesson.course,
            is_completed=True
        ).count()

        progress = round((completed_lessons / total_lessons) * 100)
        enrollment.progress = progress
        enrollment.is_completed = (progress >= 100)
        enrollment.save()

    except Enrollment.DoesNotExist:
        pass