from django.contrib import admin
from .models import *


def str_to_list_int(int_s: str, splitter=','):
    try:
        return sorted([int(x) for x in int_s.split(splitter)])
    except ValueError:
        return None


class FacultyAdmin(admin.ModelAdmin):
    list_display_links = list_display = ('id', 'title', 'short_title')


class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'faculty', 'course_n', 'stream_n', 'group_n', 'surname', 'name', 'f_name', 'is_head')
    list_display_links = ('id', 'surname')
    list_filter = ('faculty__short_title', 'course_n', 'stream_n', 'is_head', 'is_foreigner', 'is_fired')
    search_fields = ('surname', 'name', 'f_name', '=group_n')

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(StudentAdmin, self).get_queryset(request)
        elif hasattr(request.user, 'deansuser'):
            fac = request.user.deansuser.faculty
            if fac:
                courses_n = request.user.deansuser.courses_n
                if courses_n:
                    c_list = str_to_list_int(courses_n, ',')
                    if c_list:
                        return super(StudentAdmin, self).get_queryset(request).filter(faculty=fac, course_n__in=c_list)
                    else:
                        return super(StudentAdmin, self).get_queryset(request).filter(id=1000000000)
                else:
                    return super(StudentAdmin, self).get_queryset(request).filter(faculty=fac)
            else:
                return super(StudentAdmin, self).get_queryset(request)
        else:
            return super(StudentAdmin, self).get_queryset(request).filter(id=1000000000)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        else:
            return tuple(['faculty', 'course_n', 'stream_n', 'group_n', 'position_in_group', 'login', 'password',
                         'is_locked', 'is_head_assistant', 'can_add_lecture_url', 'get_lec_urls_automatically'])

    def save_model(self, request, obj: Student, form, change):
        super(StudentAdmin, self).save_model(request, obj, form, change)
        on_update = []
        group_members = Student.objects \
            .filter(faculty_id=obj.faculty_id, course_n=obj.course_n, group_n=obj.group_n) \
            .order_by('is_fired', 'surname', 'name', 'f_name')
        for i, student in enumerate(group_members, start=1):
            if student.position_in_group != i:
                student.position_in_group = i
                on_update.append(student)
        if on_update:
            Student.objects.bulk_update(on_update, ['position_in_group'])


class SubjectAdmin(admin.ModelAdmin):
    list_display_links = list_display = ('id', 'faculty', 'course_n', 'short_title')
    ordering = ['faculty', 'course_n', 'short_title']
    list_filter = ('faculty', 'course_n')
    search_fields = ('=short_title', )


class PairsScheduleAdmin(admin.ModelAdmin):
    list_display_links = list_display = ('id', 'faculty', 'course_n', 'group_n', 'pr_lk_datetime', 'subject', 'is_reported')
    ordering = ['faculty', 'course_n', 'group_n', 'pr_lk_datetime', 'subject']
    list_filter = ('faculty', 'course_n', 'is_reported', 'is_practical')
    search_fields = ('=group_n', '=subject__short_title')


class LecturesScheduleAdmin(admin.ModelAdmin):
    list_display_links = list_display = ('id', 'faculty', 'course_n', 'stream_n', 'lecture_datetime', 'subject')
    ordering = ['faculty', 'course_n', 'stream_n', 'lecture_datetime', 'subject']
    list_filter = ('faculty', 'course_n', 'stream_n')
    search_fields = ('=subject__short_title', )


admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(PairsSchedule, PairsScheduleAdmin)
admin.site.register(LecturesSchedule, LecturesScheduleAdmin)
