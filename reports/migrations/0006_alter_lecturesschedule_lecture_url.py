# Generated by Django 4.0 on 2022-02-14 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0005_lecturesschedule_stud_add_lec'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lecturesschedule',
            name='lecture_url',
            field=models.URLField(max_length=500, verbose_name='Ссылка'),
        ),
    ]
