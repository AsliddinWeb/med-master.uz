from django import forms
from .models import Quiz, Question, Choice


class QuizCreateForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'passing_score', 'time_limit']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Test nomi'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Test haqida ma\'lumot',
                'rows': 3
            }),
            'passing_score': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'O\'tish balli (%)',
                'min': 0,
                'max': 100,
                'value': 70
            }),
            'time_limit': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Vaqt chegarasi (daqiqa)',
                'min': 1,
                'value': 30
            })
        }
        labels = {
            'title': 'Test nomi',
            'description': 'Test tavsifi',
            'passing_score': 'O\'tish balli (%)',
            'time_limit': 'Vaqt chegarasi (daqiqa)'
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError('Test nomi kamida 5 ta belgidan iborat bo\'lishi kerak!')
        return title

    def clean_passing_score(self):
        score = self.cleaned_data.get('passing_score')
        if score < 0 or score > 100:
            raise forms.ValidationError('O\'tish balli 0 dan 100 gacha bo\'lishi kerak!')
        return score

    def clean_time_limit(self):
        time_limit = self.cleaned_data.get('time_limit')
        if time_limit < 1:
            raise forms.ValidationError('Vaqt chegarasi kamida 1 daqiqa bo\'lishi kerak!')
        if time_limit > 180:  # 3 soat
            raise forms.ValidationError('Vaqt chegarasi 180 daqiqadan ko\'p bo\'lishi mumkin emas!')
        return time_limit


class QuestionCreateForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Savol matnini kiriting...',
                'rows': 3
            })
        }
        labels = {
            'text': 'Savol matni'
        }

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) < 10:
            raise forms.ValidationError('Savol matni kamida 10 ta belgidan iborat bo\'lishi kerak!')
        return text


class QuizAttemptForm(forms.Form):
    """Test yechish form (dinamik)"""

    def __init__(self, quiz, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Har bir savol uchun field yaratish
        for question in quiz.questions.all():
            choices = [(choice.id, choice.text) for choice in question.choices.all()]

            self.fields[f'question_{question.id}'] = forms.ChoiceField(
                label=question.text,
                choices=[('', 'Javobni tanlang')] + choices,
                required=True,
                widget=forms.RadioSelect(attrs={
                    'class': 'text-blue-600 focus:ring-blue-500'
                })
            )


class QuizFilterForm(forms.Form):
    """Test filtrlash form"""
    course = forms.ModelChoiceField(
        queryset=None,  # Dinamik set qilinadi
        required=False,
        empty_label='Barcha kurslar',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )

    status = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Barchasi'),
            ('passed', 'O\'tgan'),
            ('failed', 'O\'tmagan'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # User kurslari
        from apps.courses.models import Course
        self.fields['course'].queryset = Course.objects.filter(
            enrollment__student=user
        ).distinct()


class ChoiceForm(forms.ModelForm):
    """Javob varianti form"""

    class Meta:
        model = Choice
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Javob varianti'
            }),
            'is_correct': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            })
        }


# Formset for multiple choices
ChoiceFormSet = forms.modelformset_factory(
    Choice,
    form=ChoiceForm,
    extra=4,
    max_num=6,
    can_delete=True
)