from django import forms
from .models import Faculty


class GroupReportForm(forms.Form):
    faculty = forms.ModelChoiceField(queryset=Faculty.objects.all(), label='Факультет')
    course_n = forms.ChoiceField(label='Курс', choices=[(x, x) for x in range(1, 7)])
    group_n = forms.IntegerField(min_value=1, max_value=1000, label='Группа')

    def __init__(self, data=None, faculty_id=None, courses_n=None, group_n=None, studs=None, subjects=None, pr_lk=None):
        super(GroupReportForm, self).__init__(data=data)
        if faculty_id:
            self.fields['faculty'].queryset = Faculty.objects.filter(id=faculty_id)
            self.fields['faculty'].initial = faculty_id
        if courses_n:
            self.fields['course_n'].choices = [(x, x) for x in courses_n]
        if group_n:
            self.fields['group_n'] = forms.IntegerField(min_value=group_n, max_value=group_n, label='Группа')
        if studs:
            self.fields['stud'] = forms.ModelChoiceField(queryset=studs, label='Студент')
        if subjects:
            self.fields['subj'] = forms.ModelChoiceField(queryset=subjects, label='Предмет')
        if pr_lk:
            self.fields['is_lec'] = forms.BooleanField(label='Лекции', required=False)


class BigReportForm(forms.Form):
    faculty = forms.ModelChoiceField(queryset=Faculty.objects.all(), label='Факультет')
    course_n = forms.ChoiceField(label='Курс', choices=[(x, x) for x in range(1, 7)])

    def __init__(self, data=None, faculty_id=None, courses_n=None, subjects=None, pr_lk=None,
                 all_subjects=False, fill_subjects=False):
        super(BigReportForm, self).__init__(data=data)
        if faculty_id:
            self.fields['faculty'].queryset = Faculty.objects.filter(id=faculty_id)
            self.fields['faculty'].initial = faculty_id
        if courses_n:
            self.fields['course_n'].choices = [(x, x) for x in courses_n]
        if all_subjects:
            self.fields['stream_n'] = forms.IntegerField(min_value=1, max_value=3, label='Поток', required=False)
            self.fields['group_n'] = forms.IntegerField(min_value=1, max_value=1000, label='Группа', required=False)
        if subjects:
            self.fields['stream_n'] = forms.IntegerField(min_value=1, max_value=3, label='Поток', required=False)
            self.fields['group_n'] = forms.IntegerField(min_value=1, max_value=1000, label='Группа', required=False)
            self.fields['subj'] = forms.ModelChoiceField(queryset=subjects, label='Предмет')
        if pr_lk:
            self.fields['is_lec'] = forms.BooleanField(label='Лекции', required=False)
        if fill_subjects:
            self.fields['fill_subjects'] = forms.BooleanField(label='Заполнить предметы', required=False)
