from django.db import models


class Faculty(models.Model):
    title = models.CharField('Название', max_length=40, unique=True)
    short_title = models.CharField('Краткое название', max_length=4, unique=True)

    class Meta:
        verbose_name = 'Факультеты'

    def __str__(self):
        return self.short_title


class Student(models.Model):
    faculty = models.ForeignKey(Faculty, verbose_name='Факультет', on_delete=models.PROTECT, db_index=True)
    course_n = models.PositiveSmallIntegerField(verbose_name='Курс', db_index=True)
    stream_n = models.PositiveSmallIntegerField(verbose_name='Поток', db_index=True)
    group_n = models.PositiveSmallIntegerField(verbose_name='Группа', db_index=True)
    position_in_group = models.PositiveSmallIntegerField(verbose_name='№ в группе')
    surname = models.CharField(verbose_name='Фамилия', max_length=40, blank=True)
    name = models.CharField(verbose_name='Имя', max_length=40, blank=True)
    f_name = models.CharField(verbose_name='Отчество', max_length=40, blank=True)
    is_foreigner = models.BooleanField(verbose_name='Иностранец')
    is_head = models.BooleanField(verbose_name='Староста')
    login = models.CharField(verbose_name='Логин', max_length=30, unique=True)
    password = models.CharField(verbose_name='Пароль', max_length=30)
    vk_id = models.BigIntegerField(verbose_name='ID Вконтакте', unique=True, null=True, blank=True)
    is_locked = models.BooleanField(verbose_name='Заблокирован Старостой', default=True)
    is_fired = models.BooleanField(verbose_name='Отчислен', default=False)
    is_head_assistant = models.BooleanField(verbose_name='Помощник старосты', default=False)
    can_add_lecture_url = models.CharField(verbose_name='Добавляет ссылки на лекции', max_length=20, default='', blank=True)
    get_lec_urls_automatically = models.BooleanField(verbose_name='Автоматически получать ссылки', default=False)
    is_head_of_head = models.BooleanField(verbose_name='Староста курса', default=False)

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'
        ordering = ['faculty', 'course_n', 'group_n', 'position_in_group']

    def __str__(self):
        head = " _Староста_"if self.is_head else ""
        return f'{self.surname} {self.name} {self.f_name}{head}'


class StudentsDoc(models.Model):
    student = models.ForeignKey(Student, verbose_name='Студент', on_delete=models.PROTECT)
    doc_type = models.CharField(verbose_name='Вид документа', max_length=50)
    doc_url = models.URLField(verbose_name='Ссылка на документ')

    class Meta:
        verbose_name = 'Документы студентов'

    # def __str__(self):
    #     return f'{self.doc_type} {self.student}'


class StudentsVaccine(models.Model):
    student = models.ForeignKey(Student, verbose_name='Студент', on_delete=models.PROTECT)
    vac_num = models.SmallIntegerField(verbose_name='№ вакцинации')
    vac_step = models.SmallIntegerField(verbose_name='Этап')
    vac_date = models.DateField(verbose_name='ДатаВакцинации')

    class Meta:
        verbose_name = 'Вакцинация студентов'

    # def __str__(self):
    #     vac_dt = self.vac_date.strftime('%d.%m %H:%Y')
    #     return f' {self.student} № {self.vac_num} {self.vac_step} этап {vac_dt}'


class Subject(models.Model):
    faculty = models.ForeignKey(Faculty, verbose_name='Факультет', db_index=True, on_delete=models.PROTECT)
    course_n = models.PositiveSmallIntegerField(verbose_name='Курс', db_index=True)
    half = models.PositiveSmallIntegerField(verbose_name='Семестр в году', db_index=True)
    full_title = models.CharField(verbose_name='Полное наименование', max_length=150)
    short_title = models.CharField(verbose_name='Краткое наименование', max_length=20)
    duration = models.PositiveSmallIntegerField(verbose_name='Длительность (количество пар)')
    hours_per_pair = models.PositiveSmallIntegerField(verbose_name='Длительность 1 пары')

    class Meta:
        verbose_name = 'Предметы'

    def __str__(self):
        return self.short_title


class LecturesSchedule(models.Model):
    faculty = models.ForeignKey(Faculty, verbose_name='Факультет', db_index=True, on_delete=models.PROTECT)
    course_n = models.PositiveSmallIntegerField(verbose_name='Курс', db_index=True)
    stream_n = models.PositiveSmallIntegerField(verbose_name='Поток', db_index=True)
    subject = models.ForeignKey(Subject, verbose_name='Курация', on_delete=models.PROTECT)
    lecture_datetime = models.DateTimeField(verbose_name='Дата и время')
    lecture_url = models.URLField(verbose_name='Ссылка', max_length=500)
    is_sent = models.BooleanField(verbose_name='Ссылка была разослана', default=False)
    stud_add_lec = models.ForeignKey(Student, verbose_name='Кто добавил лекцию', on_delete=models.SET_NULL, null=True,
                                     default=None)

    class Meta:
        verbose_name = 'Лекции'

    # def __str__(self):
    #     lec_dt = self.lecture_datetime.strftime('%d.%m %H:%Y')
    #     return f'{self.faculty} {self.course_n} курс {self.stream_n} поток {self.subject} в {lec_dt}'


class PairsSchedule(models.Model):
    faculty = models.ForeignKey(Faculty, verbose_name='Факультет', db_index=True, on_delete=models.PROTECT)
    course_n = models.PositiveSmallIntegerField(verbose_name='Курс', db_index=True)
    group_n = models.PositiveSmallIntegerField(verbose_name='Группа', db_index=True)
    pr_lk_datetime = models.DateTimeField(verbose_name='Дата и время')
    pair_n = models.PositiveSmallIntegerField(verbose_name='№ пары')
    is_practical = models.BooleanField(verbose_name='Практическое занятие (лк = нет)')
    subject = models.ForeignKey(Subject, verbose_name='Пара', on_delete=models.PROTECT)
    lecture = models.ForeignKey(LecturesSchedule, verbose_name='Лекция', null=True, on_delete=models.PROTECT, blank=True)
    is_reported = models.BooleanField(verbose_name='Рапорт отправлен')
    pr_lk_comment = models.URLField(verbose_name='Комментарий')

    class Meta:
        verbose_name = 'Расписание пар'

    # def __str__(self):
    #     pair_dt = self.pr_lk_datetime.strftime('%d.%m %H:%Y')
    #     is_pr = 'пр' if self.is_practical else 'лк'
    #     return f'{self.faculty} {self.course_n} курс {self.group_n} группа {pair_dt} {is_pr} {self.subject}'


class MissingPair(models.Model):
    pair = models.ForeignKey(PairsSchedule, verbose_name='Пара', db_index=True, on_delete=models.PROTECT)
    student = models.ForeignKey(Student, verbose_name='Студент', on_delete=models.PROTECT)
    # н - нб; с - без отработки; б - болел
    missing_reason = models.CharField(verbose_name='Причина отсутствия', max_length=1)
    is_debt = models.BooleanField(verbose_name='Отработано')
    work_out_datetime = models.DateTimeField(verbose_name='Дата отработки', null=True, blank=True)

    class Meta:
        verbose_name = 'Пропуски'


class ChangesAttendance(models.Model):
    pair = models.ForeignKey(PairsSchedule, verbose_name='Пара', db_index=True, on_delete=models.PROTECT)
    student = models.ForeignKey(Student, verbose_name='Студент', on_delete=models.PROTECT)
    # н - нб; с - без отработки; б - болел; + - был
    past_missing_reason = models.CharField(verbose_name='Причина до', max_length=1)
    new_missing_reason = models.CharField(verbose_name='Причина после', max_length=1)
    change_datetime = models.DateTimeField(verbose_name='Дата отработки')

    class Meta:
        verbose_name = 'Изменения рапортичек'
