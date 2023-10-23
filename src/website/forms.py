from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField


class DataFileForm(forms.Form):
    model = forms.ChoiceField(
        choices=[
            ("Предметы", "Предметы"),
            ("Должности", "Должности"),
            ("Группы", "Группы"),
        ],
        required=True,
        label="Модель",
    )
    file = forms.FileField(label="Прикрепите файл")


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    username = UsernameField(
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "type": "text",
                "autocomplete": "login",
            }
        ),
    )
    password = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg",
                "type": "password",
                "autocomplete": "password",
            }
        ),
    )
