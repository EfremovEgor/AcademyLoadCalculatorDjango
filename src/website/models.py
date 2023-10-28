from django.db import models


class Subject(models.Model):
    name = models.CharField(max_length=255)
    holding_type = models.CharField(
        max_length=255,
        choices=[
            ("Практическое занятие", "Практическое занятие"),
            ("Лабораторная работа", "Лабораторная работа"),
            ("Лекция", "Лекция"),
        ],
        null=True,
        blank=True,
    )
    course = models.PositiveIntegerField()
    semester = models.PositiveIntegerField()
    group_name = models.CharField(max_length=255)
    total_time_for_group = models.PositiveIntegerField()
    used = models.BooleanField()
    semester_duration = models.PositiveIntegerField()
    study_level = models.CharField(
        max_length=50,
        choices=[
            ("Бакалавриат", "Бакалавриат"),
            ("Магистратура", "Магистратура"),
            ("Специалитет", "Специалитет"),
            ("Аспирантура", "Аспирантура"),
        ],
    )
    subject_type = models.CharField(
        max_length=255,
    )
    department = models.CharField(
        max_length=255,
    )
    credit = models.PositiveIntegerField()
    cipher = models.CharField(
        max_length=255,
    )
    direction = models.CharField(
        max_length=255,
    )
    groups = models.ForeignKey(
        "Group", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"{self.name}, {self.study_level}, {self.course} Курс, {self.semester} Семестр, {self.holding_type}, {self.groups.name if self.groups.name is not None else 'Без группы'} "


class Group(models.Model):
    name = models.CharField(max_length=200)
    number_of_students = models.PositiveIntegerField()
    cipher = models.CharField(max_length=50)
    direction = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Position(models.Model):
    position_name = models.CharField(max_length=100)
    load = models.PositiveIntegerField()
    salary = models.FloatField()

    def __str__(self):
        return self.position_name


class AcademicTitle(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Degree(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Person(models.Model):
    full_name = models.CharField(max_length=200)
    birth_date = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=30)

    degree = models.ForeignKey(
        "Degree", on_delete=models.CASCADE, blank=True, null=True
    )
    academic_title = models.ForeignKey(
        "AcademicTitle", on_delete=models.CASCADE, blank=True, null=True
    )

    position = models.ForeignKey("Position", on_delete=models.CASCADE)
    rate = models.FloatField()
    subjects = models.ManyToManyField("Subject", verbose_name="subjects")

    def __str__(self):
        return self.full_name
