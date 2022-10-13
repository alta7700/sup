from django.db import models
from django.conf import settings
from reports.models import Faculty


class DeansUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    faculty = models.ForeignKey(Faculty, on_delete=models.PROTECT, verbose_name='Факультет', null=True, blank=True)
    courses_n = models.CharField(max_length=20, verbose_name='Курсы', null=True, blank=True)

    class Meta:
        verbose_name = 'Дополнение Декан'
        verbose_name_plural = 'Дополнения Деканы'
        ordering = ['faculty', 'courses_n']
