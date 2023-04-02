from collections import defaultdict
from typing import Any

from django import forms
from django.db import transaction
from django.core.exceptions import ValidationError
from django_json_widget.widgets import JSONEditorWidget

from reports.models import Student, Faculty
from .models import Table, TablePart


class FillTableForm(forms.Form):
    part_data: list[dict[str, Any]]

    def __init__(self, *args, instance: TablePart = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance
        for i, row in enumerate(instance.data):
            for field in instance.document.fields:
                self.fields[f'field_{i}_{field["alias"]}'] = get_field(field, row)

    def get_context(self):
        context = super().get_context()
        return context

    def save(self):
        data = self.instance.data
        for field_id, value in self.cleaned_data.items():
            _, index, alias = field_id.split('_')
            data[int(index)][alias] = value
        self.instance.save(update_fields=['data'])
        return self.instance


class CreateTableForm(forms.ModelForm):
    instance: Table
    course_n = forms.IntegerField(max_value=6, min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    faculty = forms.ModelChoiceField(queryset=Faculty.objects.all(), required=False)
    field_order = ('faculty', 'course_n', 'title', 'description', 'fields')

    class Meta:
        model = Table
        fields = ('title', 'description', 'fields', 'faculty', 'course_n')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'fields': JSONEditorWidget(attrs={'class': 'form-control'}, mode='tree', width='600px', height='200px')
        }

    def clean_fields(self) -> list[dict]:
        fields: list[dict] = self.cleaned_data.get('fields')
        result = []
        if isinstance(self.cleaned_data['fields'], list):
            for field in fields:
                if not isinstance(field, dict):
                    raise ValidationError('Нужен список словарей')
                for key in required_keys:
                    if key not in field:
                        raise ValidationError(f'Нужен список словарей с {", ".join(required_keys)}')
                try:
                    result.append(sanitize_field(field))
                except Exception as e:
                    raise ValidationError(str(e))
        else:
            raise ValidationError('Нужен список')
        return result

    def clean_course_n(self):
        user = self.instance.owner
        faculty = self.cleaned_data.get('faculty')
        course_n = self.cleaned_data['course_n']
        if not faculty:
            return course_n
        if not user.is_superuser:
            deansuser = user.deansuser
            if deansuser.courses and course_n not in deansuser.courses:
                raise ValidationError('Нет доступа к курсу')
        if not Student.objects.filter(faculty=faculty, course_n=course_n, is_fired=False).exists():
            raise ValidationError('Этого курса нет в базе')
        return course_n

    def clean_faculty(self):
        if self.instance.owner.is_superuser:
            faculty = self.cleaned_data.get('faculty')
        else:
            faculty = self.instance.owner.deansuser.faculty
        if not faculty:
            raise ValidationError('Не выбран Факультет')
        return faculty

    def save(self, commit=True):
        faculty = self.cleaned_data['faculty']
        course_n = self.cleaned_data['course_n']
        students = Student.objects.filter(faculty=faculty, course_n=course_n, is_fired=False)
        parts_by_group = defaultdict(list)
        for stud in students:
            stud_data = {
                FIO_FIELD['alias']: f'{stud.surname} {stud.name} {stud.f_name}'.strip(),
                **{f['alias']: f.get('default') for f in self.cleaned_data['fields']},
            }
            parts_by_group[stud.group_n].append(stud_data)

        with transaction.atomic():
            table = super().save(commit=commit)
            parts = [TablePart(document=table, data=p, group_n=group_n) for group_n, p in parts_by_group.items()]
            TablePart.objects.bulk_create(parts)
        return table


required_keys = ['name', 'alias']
allowed_keys = {
    'name': str,
    'description': str,
    'alias': str,
    'type': str,
    'kwargs': dict,
    'default': lambda x: x
}
fields_map = {
    'str': forms.CharField,
    'int': forms.IntegerField,
    'date': forms.DateField,
    'datetime': forms.DateTimeField,
    'bool': forms.BooleanField,
    'time': forms.TimeField,
}
FIO_FIELD = {'name': 'ФИО', 'alias': 'fio', 'type': 'str', 'kwargs': {}}


def sanitize_field(field: dict) -> dict:
    return {k: allowed_keys[k](v) for k, v in field.items() if k in allowed_keys}


def get_field(field, row) -> forms.Field:
    t = t if (t := field.get('type')) in fields_map else 'str'
    kwargs = {'initial': row.get(field['alias']), 'label': field['name'], 'required': False}
    kwargs = {**d_kwargs, **kwargs} if isinstance(d_kwargs := field.get('kwargs'), dict) else kwargs
    return fields_map[t](**kwargs)
