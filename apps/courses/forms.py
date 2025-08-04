from django import forms
from .models import Course
from apps.accounts.models import User


class CourseSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Kurs nomi yoki tavsifida qidiring...'
        })
    )

    level = forms.ChoiceField(
        required=False,
        choices=[('', 'Barcha darajalar')] + Course.LEVEL_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )

    instructor = forms.ModelChoiceField(
        required=False,
        queryset=User.objects.filter(role='teacher', is_active=True),
        empty_label='Barcha o\'qituvchilar',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )


class CourseCreateForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'level', 'duration_weeks', 'price']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Kurs nomi'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Kurs haqida batafsil ma\'lumot',
                'rows': 5
            }),
            'level': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'duration_weeks': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Kurs davomiyligi (hafta)',
                'min': 1
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Kurs narxi (UZS)',
                'min': 0,
                'step': 'any'
            })
        }
        labels = {
            'title': 'Kurs nomi',
            'description': 'Kurs tavsifi',
            'level': 'Daraja',
            'duration_weeks': 'Davomiylik (hafta)',
            'price': 'Narxi (UZS)'
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 10:
            raise forms.ValidationError('Kurs nomi kamida 10 ta belgidan iborat bo\'lishi kerak!')
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) < 50:
            raise forms.ValidationError('Kurs tavsifi kamida 50 ta belgidan iborat bo\'lishi kerak!')
        return description

    def clean_duration_weeks(self):
        duration = self.cleaned_data.get('duration_weeks')
        if duration < 1:
            raise forms.ValidationError('Kurs davomiyligi kamida 1 hafta bo\'lishi kerak!')
        if duration > 52:
            raise forms.ValidationError('Kurs davomiyligi 52 haftadan ko\'p bo\'lishi mumkin emas!')
        return duration


class CourseEditForm(CourseCreateForm):
    """Kurs tahrirlash form (create form bilan bir xil)"""

    class Meta(CourseCreateForm.Meta):
        fields = CourseCreateForm.Meta.fields + ['is_active']
        widgets = CourseCreateForm.Meta.widgets.copy()
        widgets['is_active'] = forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
        })
        labels = CourseCreateForm.Meta.labels.copy()
        labels['is_active'] = 'Kurs faol'


class CourseFilterForm(forms.Form):
    """Kurslarni filtrlash uchun"""
    SORT_CHOICES = [
        ('newest', 'Eng yangi'),
        ('popular', 'Mashhur'),
        ('alphabetical', 'Alfavit bo\'yicha'),
        ('price_low', 'Arzon narx'),
        ('price_high', 'Qimmat narx'),
    ]

    level = forms.ChoiceField(
        required=False,
        choices=[('', 'Barcha darajalar')] + Course.LEVEL_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select rounded-lg border-gray-300'
        })
    )

    sort_by = forms.ChoiceField(
        required=False,
        choices=SORT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select rounded-lg border-gray-300'
        })
    )

    price_min = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-input rounded-lg border-gray-300',
            'placeholder': 'Min narx'
        })
    )

    price_max = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-input rounded-lg border-gray-300',
            'placeholder': 'Max narx'
        })
    )