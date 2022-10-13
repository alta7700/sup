from django.shortcuts import render, redirect, HttpResponse
from .forms import *
from .make_reports import *
from openpyxl.writer.excel import save_virtual_workbook
from transliterate import translit

report_types = [
    {'url': 'all_subj_hours_report', 'title': 'Все предметы с учетом часов'},
    {'url': 'all_subj_report', 'title': 'Все предметы'},
    {'url': 'subj_report', 'title': '1 предмет'},
    {'url': 'stud_report', 'title': '1 студент - Все предметы'},
    {'url': 'stud_subj_report', 'title': '1 студент - 1 предмет'}
]


def str_to_list_int(int_s: str, splitter=','):
    try:
        return sorted([int(x) for x in int_s.split(splitter)])
    except ValueError:
        return None


def index1(request):
    user = request.user
    faculty, courses_n = None, None
    if not user.is_authenticated:
        return redirect('admin_panel/login/')
    if not user.is_superuser:
        if hasattr(user, 'deansuser'):
            if user.deansuser.faculty:
                faculty = user.deansuser.faculty.title.title()
                if user.deansuser.courses_n:
                    courses_n = str_to_list_int(user.deansuser.courses_n)
                    if courses_n:
                        courses_n = ', '.join(str(x) for x in courses_n)

        else:
            return HttpResponse('Недостаточно прав')
    # if faculty_id:
    #     if courses_n:
    #         all_studs = Student.objects.filter(faculty_id=faculty_id, course_n__in=courses_n)
    #     else:
    #         all_studs = Student.objects.filter(faculty_id=faculty_id)
    # else:
    #     all_studs = Student.objects.all()
    # all_studs.order_by('faculty_id', 'course_n', 'group_n', 'position_in_group').select_related()
    # studs_by_groups = {}
    # for x in all_studs:
    #     if not studs_by_groups.get(x.faculty.short_title):
    #         studs_by_groups[x.faculty.short_title] = {}
    #     if not studs_by_groups[x.faculty.short_title].get(x.course_n):
    #         studs_by_groups[x.faculty.short_title][x.course_n] = {}
    #     if not studs_by_groups[x.faculty.short_title][x.course_n].get(x.group_n):
    #         studs_by_groups[x.faculty.short_title][x.course_n][x.group_n] = []
    #     studs_by_groups[x.faculty.short_title][x.course_n][x.group_n].append(
    #         f'{x.position_in_group}. {x.surname} {x.name} {"_______" if x.is_head else ""}'
    #     )

    return render(request, 'reports/index1.html', {'f': faculty, 'c': courses_n, 'report_types': report_types})


def stud_subj_report(request):
    user = request.user
    faculty, courses_n, group_n, result = None, None, None, None
    if not user.is_authenticated:
        return redirect('admin_panel/login/')
    if not user.is_superuser:
        if hasattr(user, 'deansuser'):
            if user.deansuser.faculty:
                faculty = user.deansuser.faculty.id
                if user.deansuser.courses_n:
                    courses_n = str_to_list_int(user.deansuser.courses_n)
        else:
            return HttpResponse('Недостаточно прав')
    choose_btn = True
    if request.method == 'POST':
        post = request.POST
        form = GroupReportForm(post)
        if form.is_valid():
            if post.get('act'):
                act = post['act']
                faculty_id = int(post['faculty'])
                if faculty and faculty_id != faculty:
                    return HttpResponse('Не нужно изменять форму')
                course_n = int(post['course_n'])
                if courses_n and course_n not in courses_n:
                    return HttpResponse('Не нужно изменять форму')
                group_n = int(post['group_n'])
                if act == 'choose_stud_and_subj':
                    studs = Student.objects.filter(faculty__id=faculty_id, course_n=course_n, group_n=group_n)
                    subjects = Subject.objects.filter(faculty__id=faculty_id, course_n=course_n)
                    form = GroupReportForm(post, faculty_id, [course_n], group_n, studs, subjects, pr_lk=True)
                    choose_btn = False
                elif act == 'make_report':
                    stud = int(post['stud'])
                    subj = int(post['subj'])
                    studs = Student.objects.filter(faculty__id=faculty_id, course_n=course_n, group_n=group_n,
                                                   is_fired=False)
                    subjects = Subject.objects.filter(faculty__id=faculty_id, course_n=course_n)
                    is_pr = False if post.get('is_lec') else True
                    result = show_attendance_group(faculty_id, course_n, group_n, stud, subj, is_pr)
                    form = GroupReportForm(post, faculty_id, [course_n], group_n, studs, subjects, pr_lk=True)
                    choose_btn = False
                elif act == 'change_group':
                    form = GroupReportForm(faculty_id=faculty, courses_n=courses_n)
            else:
                form = GroupReportForm(faculty_id=faculty, courses_n=courses_n)
        else:
            form = GroupReportForm(faculty_id=faculty, courses_n=courses_n)
    else:
        form = GroupReportForm(faculty_id=faculty, courses_n=courses_n)
    return render(request, 'reports/stud_subj_report.html', {'form': form, 'choose_btn': choose_btn, 'result': result})


def stud_report(request):
    user = request.user
    faculty, courses_n, group_n, e_msg = None, None, None, None
    if not user.is_authenticated:
        return redirect('admin_panel/login/')
    if not user.is_superuser:
        if hasattr(user, 'deansuser'):
            if user.deansuser.faculty:
                faculty = user.deansuser.faculty.id
                if user.deansuser.courses_n:
                    courses_n = str_to_list_int(user.deansuser.courses_n)
        else:
            return HttpResponse('Недостаточно прав')
    choose_btn = True
    if request.method == 'POST':
        post = request.POST
        form = GroupReportForm(post)
        if form.is_valid():
            if post.get('act'):
                act = post['act']
                faculty_id = int(post['faculty'])
                if faculty and faculty_id != faculty:
                    return HttpResponse('Не нужно изменять форму')
                course_n = int(post['course_n'])
                if courses_n and course_n not in courses_n:
                    return HttpResponse('Не нужно изменять форму')
                group_n = int(post['group_n'])
                if act == 'choose_stud':
                    studs = Student.objects.filter(faculty__id=faculty_id, course_n=course_n, group_n=group_n)
                    form = GroupReportForm(post, faculty_id, [course_n], group_n, studs, pr_lk=True)
                    choose_btn = False
                elif act == 'make_report':
                    stud = int(post['stud'])
                    is_pr = False if post.get('is_lec') else True
                    studs = Student.objects.filter(faculty__id=faculty_id, course_n=course_n, group_n=group_n)
                    result = show_attendance_group(faculty_id, course_n, group_n, stud_id=stud, is_pr=is_pr)
                    if result.get('workbook'):
                        wb = result['workbook']
                        response = HttpResponse(content=save_virtual_workbook(wb), content_type='application/ms-excel')
                        filename = translit(result["filename"].replace(' ', '_').replace(',', '_'), 'ru', True)
                        response['Content-Disposition'] = f'attachment; filename={filename}.xlsx'
                        return response
                    else:
                        e_msg = result['e_msg']
                    form = GroupReportForm(post, faculty_id, [course_n], group_n, studs, pr_lk=True)
                    choose_btn = False
                elif act == 'change_group':
                    form = GroupReportForm(faculty_id=faculty, courses_n=courses_n)
            else:
                form = GroupReportForm(faculty_id=faculty, courses_n=courses_n)
        else:
            form = GroupReportForm(faculty_id=faculty, courses_n=courses_n)
    else:
        form = GroupReportForm(faculty_id=faculty, courses_n=courses_n)
    return render(request, 'reports/stud_report.html', {'form': form, 'choose_btn': choose_btn, 'e_msg': e_msg})


def subj_report(request):
    user = request.user
    faculty, courses_n, group_n, e_msg = None, None, None, None
    buttons = {'choose_btn': True, 'can_change': False}
    if not user.is_authenticated:
        return redirect('admin_panel/login/')
    if not user.is_superuser:
        if hasattr(user, 'deansuser'):
            if user.deansuser.faculty:
                faculty = user.deansuser.faculty.id
                if user.deansuser.courses_n:
                    courses_n = str_to_list_int(user.deansuser.courses_n)
        else:
            return HttpResponse('Недостаточно прав')

    if request.method == 'POST':
        post = request.POST
        form = BigReportForm(post)
        if form.is_valid():
            if post.get('act'):
                act = post['act']
                faculty_id = int(post['faculty'])
                if faculty and faculty_id != faculty:
                    return HttpResponse('Не нужно изменять форму')
                course_n = int(post['course_n'])
                if courses_n and (course_n not in courses_n):
                    return HttpResponse('Не нужно изменять форму')
                if act == 'choose_subj':
                    subjects = Subject.objects.filter(faculty=faculty_id, course_n=course_n)
                    form = BigReportForm(post, faculty_id, [course_n], subjects, pr_lk=True)
                    buttons = {'choose_btn': False, 'can_change': True}
                elif act == 'make_report':
                    stream_n = int(post['stream_n']) if post.get('stream_n') else None
                    group_n = int(post['group_n']) if post.get('group_n') else None
                    subj_id = int(post['subj'])
                    is_pr = False if post.get('is_lec') else True
                    if group_n:
                        result = show_attendance_group(faculty_id, course_n, group_n, 'all', subj_id, is_pr)
                    else:
                        result = show_attendance_course(faculty_id, course_n, stream_n, subj_id, is_pr)
                    if result.get('workbook'):
                        wb = result['workbook']
                        response = HttpResponse(save_virtual_workbook(wb), content_type='application/ms-excel')
                        filename = translit(result["filename"].replace(' ', '_').replace(',', '_'), 'ru', True)
                        response['Content-Disposition'] = f'attachment; filename={filename}.xlsx'
                        return response
                    else:
                        req_data = {'faculty': faculty_id, 'course_n': course_n, 'group_n': group_n,
                                    'subj': subj_id}
                        subjects = Subject.objects.filter(faculty=faculty_id, course_n=course_n)
                        form = BigReportForm(req_data, faculty_id, courses_n, subjects, True)
                        if faculty_id and courses_n and len(courses_n) == 1:
                            buttons['choose_btn'] = False
                        e_msg = result['e_msg']
                elif act == 'change_course':
                    form = BigReportForm(faculty_id=faculty, courses_n=courses_n)
            else:
                form = BigReportForm(faculty_id=faculty, courses_n=courses_n)
        else:
            form = BigReportForm(faculty_id=faculty, courses_n=courses_n)
    else:
        if faculty and courses_n and len(courses_n) == 1:
            subjects = Subject.objects.filter(faculty=faculty, course_n=courses_n[0])
            form = BigReportForm(faculty_id=faculty, courses_n=courses_n, subjects=subjects, pr_lk=True)
            buttons['choose_btn'] = False
        else:
            form = BigReportForm(faculty_id=faculty, courses_n=courses_n)
    return render(request, 'reports/subj_report.html', {'form': form, 'buttons': buttons, 'e_msg': e_msg})


def all_subj_report(request):
    user = request.user
    faculty, courses_n, group_n, e_msg = None, None, None, None
    if not user.is_authenticated:
        return redirect('admin_panel/login/')
    if not user.is_superuser:
        if hasattr(user, 'deansuser'):
            if user.deansuser.faculty:
                faculty = user.deansuser.faculty.id
                if user.deansuser.courses_n:
                    courses_n = str_to_list_int(user.deansuser.courses_n)
        else:
            return HttpResponse('Недостаточно прав')

    if request.method == 'POST':
        post = request.POST
        form = BigReportForm(post)
        if form.is_valid():
            if post.get('act'):
                act = post['act']
                faculty_id = int(post['faculty'])
                if faculty and faculty_id != faculty:
                    return HttpResponse('Не нужно изменять форму')
                course_n = int(post['course_n'])
                if courses_n and course_n not in courses_n:
                    return HttpResponse('Не нужно изменять форму')
                if act == 'make_report':
                    stream_n = int(post['stream_n']) if post.get('stream_n') else None
                    group_n = int(post['group_n']) if post.get('group_n') else None
                    is_pr = False if post.get('is_lec') else True
                    if group_n:
                        result = show_attendance_group(faculty_id, course_n, group_n, 'all', 'all', is_pr)
                    else:
                        result = show_attendance_course(faculty_id, course_n, stream_n, 'all', is_pr)
                    if result.get('workbook'):
                        wb = result['workbook']
                        response = HttpResponse(save_virtual_workbook(wb), content_type='application/ms-excel')
                        filename = translit(result["filename"].replace(' ', '_').replace(',', '_'), 'ru', True)
                        response['Content-Disposition'] = f'attachment; filename={filename}.xlsx'
                        return response
                    else:
                        req_data = {'faculty': faculty_id, 'course_n': course_n,
                                    'stream_n': stream_n, 'group_n': group_n, 'is_lec': not is_pr}
                        form = BigReportForm(req_data, faculty_id, courses_n, all_subjects=True, pr_lk=True)
                        e_msg = result['e_msg']
            else:
                form = BigReportForm(faculty_id=faculty, courses_n=courses_n, all_subjects=True, pr_lk=True)
        else:
            form = BigReportForm(faculty_id=faculty, courses_n=courses_n, all_subjects=True, pr_lk=True)
    else:
        form = BigReportForm(faculty_id=faculty, courses_n=courses_n, all_subjects=True, pr_lk=True)
    return render(request, 'reports/all_subj_report.html', {'form': form, 'e_msg': e_msg})


def all_subj_hours_report(request):
    user = request.user
    faculty, courses_n, group_n, e_msg = None, None, None, None
    if not user.is_authenticated:
        return redirect('admin_panel/login/')
    if not user.is_superuser:
        if hasattr(user, 'deansuser'):
            if user.deansuser.faculty:
                faculty = user.deansuser.faculty.id
                if user.deansuser.courses_n:
                    courses_n = str_to_list_int(user.deansuser.courses_n)
        else:
            return HttpResponse('Недостаточно прав')

    if request.method == 'POST':
        post = request.POST
        form = BigReportForm(post)
        if form.is_valid():
            if post.get('act'):
                act = post['act']
                faculty_id = int(post['faculty'])
                if faculty and faculty_id != faculty:
                    return HttpResponse('Не нужно изменять форму')
                course_n = int(post['course_n'])
                if courses_n and course_n not in courses_n:
                    return HttpResponse('Не нужно изменять форму')
                if act == 'make_report':
                    stream_n = int(post['stream_n']) if post.get('stream_n') else None
                    group_n = int(post['group_n']) if post.get('group_n') else None
                    fill_subjects = True if post.get('fill_subjects') else False
                    result = show_attendance_hours_course(faculty_id, course_n, stream_n, group_n, fill_subjects)
                    if result.get('workbook'):
                        wb = result['workbook']
                        response = HttpResponse(save_virtual_workbook(wb), content_type='application/ms-excel')
                        filename = translit(result["filename"].replace(' ', '_').replace(',', '_'), 'ru', True)
                        response['Content-Disposition'] = f'attachment; filename={filename}.xlsx'
                        return response
                    else:
                        req_data = {'faculty': faculty_id, 'course_n': course_n,
                                    'stream_n': stream_n, 'group_n': group_n}
                        form = BigReportForm(req_data, faculty_id, courses_n, all_subjects=True, fill_subjects=True)
                        e_msg = result['e_msg']
            else:
                form = BigReportForm(faculty_id=faculty, courses_n=courses_n, all_subjects=True, fill_subjects=True)
        else:
            form = BigReportForm(faculty_id=faculty, courses_n=courses_n, all_subjects=True, fill_subjects=True)
    else:
        form = BigReportForm(faculty_id=faculty, courses_n=courses_n, all_subjects=True, fill_subjects=True)
    return render(request, 'reports/all_subj_hours_report.html', {'form': form, 'e_msg': e_msg})
