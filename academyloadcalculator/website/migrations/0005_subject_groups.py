# Generated by Django 4.2.5 on 2023-10-02 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_group_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='groups',
            field=models.ManyToManyField(to='website.group', verbose_name='groups'),
        ),
    ]
