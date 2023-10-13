# Generated by Django 4.2.5 on 2023-10-02 10:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0002_subject_cipher_subject_direction"),
    ]

    operations = [
        migrations.RenameField(
            model_name="group",
            old_name="name",
            new_name="cipher",
        ),
        migrations.RenameField(
            model_name="group",
            old_name="students_amount",
            new_name="number_of_students",
        ),
        migrations.AddField(
            model_name="group",
            name="direction",
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
    ]
