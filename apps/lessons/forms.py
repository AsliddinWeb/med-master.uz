from django import forms
from .models import Lesson


class LessonCreateForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'video_url', 'content', 'duration_minutes', 'is_free']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Dars nomi'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Dars haqida qisqacha ma\'lumot',
                'rows': 3
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Video URL (YouTube, Vimeo)'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Dars matni va qo\'shimcha ma\'lumotlar',
                'rows': 8
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Davomiylik (daqiqa)',
                'min': 1
            }),
            'is_free': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            })
        }
        labels = {
            'title': 'Dars nomi',
            'description': 'Dars tavsifi',
            'video_url': 'Video URL',
            'content': 'Dars matni',
            'duration_minutes': 'Davomiylik (daqiqa)',
            'is_free': 'Bepul dars'
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError('Dars nomi kamida 5 ta belgidan iborat bo\'lishi kerak!')
        return title

    def clean_duration_minutes(self):
        duration = self.cleaned_data.get('duration_minutes')
        if duration < 1:
            raise forms.ValidationError('Davomiylik kamida 1 daqiqa bo\'lishi kerak!')
        if duration > 300:  # 5 soat
            raise forms.ValidationError('Davomiylik 300 daqiqadan ko\'p bo\'lishi mumkin emas!')
        return duration

    def clean_video_url(self):
        url = self.cleaned_data.get('video_url')
        if url:
            # YouTube va Vimeo URL tekshirish
            if not any(domain in url for domain in ['youtube.com', 'youtu.be', 'vimeo.com']):
                raise forms.ValidationError('Faqat YouTube yoki Vimeo havolalarini ishlatish mumkin!')
        return url


class LessonEditForm(LessonCreateForm):
    """Dars tahrirlash form"""

    class Meta(LessonCreateForm.Meta):
        fields = LessonCreateForm.Meta.fields + ['order']
        widgets = LessonCreateForm.Meta.widgets.copy()
        widgets['order'] = forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'min': 1
        })
        labels = LessonCreateForm.Meta.labels.copy()
        labels['order'] = 'Tartib raqami'


class LessonProgressForm(forms.Form):
    """Dars progress form"""
    watched_duration = forms.IntegerField(
        widget=forms.HiddenInput()
    )

    is_completed = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
        }),
        label='Darsni tugallangan deb belgilash'
    )


class LessonSearchForm(forms.Form):
    """Dars qidiruv form"""
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Dars nomida qidiring...'
        })
    )

    is_completed = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Barchasi'),
            ('true', 'Tugallangan'),
            ('false', 'Tugallanmagan'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )


class LessonFeedbackForm(forms.Form):
    """Dars haqida fikr-mulohaza"""
    rating = forms.ChoiceField(
        choices=[(i, f'{i} yulduz') for i in range(1, 6)],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        }),
        label='Baho'
    )

    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Dars haqidagi fikringiz...',
            'rows': 4
        }),
        label='Izoh'
    )