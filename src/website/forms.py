from django import forms
from dynamic_forms import DynamicField, DynamicFormMixin

from .models import Position, Subject


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


class EmployeeForm(DynamicFormMixin, forms.Form):
    full_name = forms.CharField(label="ФИО")
    birth_date = forms.DateField(label="День рождения")
    phone_number = forms.CharField(label="Телефон")
    degree = forms.CharField(label="Ученая степень")
    academic_title = forms.CharField(label="Ученое звание")
    position = forms.ModelChoiceField(queryset=Position.objects.all())
    rate = forms.FloatField(min_value=0, max_value=2, label="Ставка")
    study_level = forms.ChoiceField(
        choices=[
            ("Бакалавриат", "Бакалавриат"),
            ("Магистратура", "Магистратура"),
            ("Специалитет", "Специалитет"),
            ("Аспирантура", "Аспирантура"),
        ]
    )

    # subject_name = forms.ChoiceField(
    #     choices=[
    # (subject.name, subject.name)
    # for subject in Subject.objects.filter(study_level=)
    #     ]
    # )
    def subject_name_choices(form):
        study_level = form["study_level"].value()
        data = Subject.objects.filter(study_level=study_level).all()
        return sorted(
            list(
                set(
                    [
                        (
                            subject.name,
                            subject.name,
                        )
                        for subject in data
                    ]
                )
            ),
            key=lambda x: x[0],
        )

    subject_name = DynamicField(
        forms.ChoiceField,
        choices=subject_name_choices,
    )

    def subject_direction_cipher_choices(form):
        study_level = form["study_level"].value()
        name = form["subject_name"].value()
        data = Subject.objects.filter(study_level=study_level, name=name).all()
        print(form.data)
        return sorted(
            list(
                set(
                    [
                        (
                            subject.direction + ", " + subject.cipher,
                            subject.direction + ", " + subject.cipher,
                        )
                        for subject in data
                    ]
                )
            ),
            key=lambda x: x[0],
        )

    subject_direction_cipher = DynamicField(
        forms.ChoiceField,
        choices=subject_direction_cipher_choices,
    )
