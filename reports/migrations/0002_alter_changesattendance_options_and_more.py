# Generated by Django 4.0 on 2022-01-06 16:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='changesattendance',
            options={'verbose_name': 'Изменения рапортичек'},
        ),
        migrations.AlterModelOptions(
            name='faculty',
            options={'verbose_name': 'Факультеты'},
        ),
        migrations.AlterModelOptions(
            name='lecturesschedule',
            options={'verbose_name': 'Лекции'},
        ),
        migrations.AlterModelOptions(
            name='missingpair',
            options={'verbose_name': 'Пропуски'},
        ),
        migrations.AlterModelOptions(
            name='pairsschedule',
            options={'verbose_name': 'Расписание пар'},
        ),
        migrations.AlterModelOptions(
            name='student',
            options={'ordering': ['faculty', 'course_n', 'group_n', 'position_in_group'], 'verbose_name': 'Студент', 'verbose_name_plural': 'Студенты'},
        ),
        migrations.AlterModelOptions(
            name='studentsdoc',
            options={'verbose_name': 'Документы студентов'},
        ),
        migrations.AlterModelOptions(
            name='studentsvaccine',
            options={'verbose_name': 'Вакцинация студентов'},
        ),
        migrations.AlterModelOptions(
            name='subject',
            options={'verbose_name': 'Предметы'},
        ),
    ]
