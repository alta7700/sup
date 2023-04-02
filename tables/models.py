from uuid import UUID, uuid4

from django.conf import settings
from django.db import models

from reports.models import Faculty


class Table(models.Model):

    id: int
    owner = models.ForeignKey(verbose_name='Владелец', to=settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                              related_name='tables')
    title = models.CharField(verbose_name='Название', max_length=40)
    description = models.TextField(verbose_name='Описание')
    fields = models.JSONField(verbose_name='Поля')
    editable = models.BooleanField(verbose_name='Возможно редактирование', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    faculty = models.ForeignKey(verbose_name='Факультет', to=Faculty, on_delete=models.RESTRICT)
    course_n = models.SmallIntegerField(verbose_name='Курс')

    class Meta:
        verbose_name = 'Таблица'
        verbose_name_plural = 'Таблицы'
        ordering = ('created_at', )


class TablePart(models.Model):
    id: UUID = models.UUIDField(primary_key=True, default=uuid4)
    document = models.ForeignKey(verbose_name='Таблица', to=Table, on_delete=models.CASCADE, related_name='parts')
    data = models.JSONField(verbose_name='Данные')
    group_n: int = models.SmallIntegerField(verbose_name='Группа')

    class Meta:
        verbose_name = 'Часть таблицы'
        verbose_name_plural = 'Части таблиц'
        ordering = ('group_n', )

