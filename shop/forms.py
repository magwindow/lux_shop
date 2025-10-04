from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import *


class LoginForm(AuthenticationForm):
    """Аутентификация пользователя"""
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'placeholder': 'Имя пользователя'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                 'placeholder': 'Пароль'}))


class RegistrationForm(UserCreationForm):
    """Регистрация пользователя"""
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                  'placeholder': 'Пароль'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                  'placeholder': 'Подтвердите пароль'}))

    class Meta:
        model = User
        fields = ('username', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Почта'})
        }


class ReviewForm(forms.ModelForm):
    """Форма для отзыва"""

    class Meta:
        model = Review
        fields = ('text', 'grade')
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ваш отзыв...'}),
            'grade': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Ваша оценка'})
        }


class CustomerForm(forms.ModelForm):
    """Контактная информация"""
    class Meta:
        model = Customer
        fields = ('first_name', 'last_name', 'email', 'phone')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bruce'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wayne'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'batman@gmail.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+79521479654'})
        }


class ShippingForm(forms.ModelForm):
    """Адрес доставки"""
    class Meta:
        model = ShippingAddress
        fields = ('city', 'state', 'street')
        widgets = {
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Las Vegas'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nevada'}),
            'street': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'West Warm Springs'}),
        }
