from typing import Dict, Tuple, List

login_btn = ['Авторизация', 'positive', '{"button": "log_in"}']
##
before_login_kb = {1: (login_btn, )}


category_reports_btn = ['Рапорты', 'positive', '{"button": "report_category"}']
category_attendance_btn = ['Посещаемость', 'primary', '{"button": "attendance_category"}']
category_work_out_btn = ['Отработки', 'primary', '{"button": "work_out"}']
category_schedule_btn = ['Расписание', 'primary', '{"button": "schedule_category"}']
settings_btn = ['Настройки', 'secondary', '{"button": "get_settings_kb"}']
##
main_kb_head = {

    1: (category_reports_btn, ),
    2: (category_attendance_btn, category_work_out_btn),
    3: (category_schedule_btn,),
    4: (settings_btn, )
}
##
main_kb_student = {
    1: (category_attendance_btn, category_work_out_btn),
    2: (category_schedule_btn,),
    3: (settings_btn, )
}

roles_settings = ['Роли', 'primary', '{"button": "roles"}']
lectures_settings = ['Лекции', 'primary', '{"button": "lectures"}']
switch_off = ['Сбросить авторизацию', 'primary', '{"button": "log_off"}']
get_gr_passwd_btn = ['Пароли группы', 'primary', '{"button": "get_gr_passwd"}']
change_passwd_btn = ['Сменить пароль', 'primary', '{"button": "change_passwd"}']
cancel_btn = ['В начало', 'secondary', '{"button": "cancel_kb"}']
logout_btn = ['Выход', 'negative', '{"button": "log_out"}']
##
settings_kb_head = {
    1: (roles_settings, lectures_settings),
    2: (get_gr_passwd_btn, switch_off),
    3: (change_passwd_btn, ),
    4: (cancel_btn, logout_btn)
}
settings_kb_student = {
    1: (lectures_settings, ),
    2: (change_passwd_btn, ),
    3: (cancel_btn, logout_btn)
}


unlock_groupmate_btn = ['Разблокировать одногруппника', 'positive', '{"button": "roles_unlock_groupmate"}']
lock_groupmate_btn = ['Заблокировать одногруппника', 'negative', '{"button": "roles_lock_groupmate"}']
choose_assistant_btn = ['Выбрать помощника', 'primary', '{"button": "roles_assistant_choose"}']
##
roles_kb = {
    1: (unlock_groupmate_btn, ),
    2: (lock_groupmate_btn, ),
    3: (choose_assistant_btn, ),
    4: (cancel_btn, )
}


upload_report_excel = ['Рапорт excel', 'primary', '{"button": "report_send_excel"}']
upload_report_message = ['Рапорт сообщением', 'primary', '{"button": "report_send_message"}']
change_report = ['Изменить рапорт', 'primary', '{"button": "report_change"}']
report_instructions = ['Что делать?', 'primary', '{"button": "report_instructions"}']
##
category_reports_kb = {
    1: (upload_report_excel, upload_report_message),
    2: (change_report, report_instructions),
    3: (cancel_btn, )
}


change_report_pr = ['Практическое занятие', 'positive', '{"button": "report_change_practical"}']
change_report_lk = ['Лекция', 'primary', '{"button": "report_change_lecture"}']
##
change_report_kb = {
    1: (change_report_pr, ),
    2: (change_report_lk, ),
    3: (cancel_btn, )
}

attendance_complete = ['Последние рапорты', 'primary', '{"button": "attendance_complete"}']
all_reports_btn = ['Все рапортички', 'primary', '{"button": "attendance_show_all"}']
attendance_pr_btn = ['Практические занятия', 'positive', '{"button": "attendance_show_practical"}']
attendance_lk_btn = ['Лекции', 'primary', '{"button": "attendance_show_lecture"}']
##
attendance_pr_or_lk_kb = {
    1: (all_reports_btn, ),
    2: (attendance_pr_btn, ),
    3: (attendance_lk_btn, ),
    4: (cancel_btn, )
}


work_out_mark = ['Отметить отработку', 'positive', '{"button": "work_out_mark"}']
work_out_mark_practical = ['Практическое занятие', 'positive', '{"button": "work_out_mark_practical"}']
work_out_mark_lecture = ['Лекция', 'primary', '{"button": "work_out_mark_lecture"}']
work_out_remark = ['Отменить отметку', 'negative', '{"button": "work_out_remark"}']
work_out_remark_practical = ['Практическое занятие', 'positive', '{"button": "work_out_remark_practical"}']
work_out_remark_lecture = ['Лекция', 'primary', '{"button": "work_out_remark_lecture"}']
##
work_out_kb = {
    1: (work_out_mark, ),
    2: (work_out_remark, ),
    3: (cancel_btn, )
}
##
work_out_mark_kb = {
    1: (work_out_mark_practical, ),
    2: (work_out_mark_lecture, ),
    3: (cancel_btn, )
}
##
work_out_remark_kb = {
    1: (work_out_remark_practical, ),
    2: (work_out_remark_lecture, ),
    3: (cancel_btn, )
}


# add_pair_comment = ['Комментарий к паре', 'primary', '{"button": "schedule_pair_comment"}']
add_lecture_url = ['Добавить ссылку', 'positive', '{"button": "schedule_lecture_url_add"}']
change_lecture_url = ['Заменить ссылку', 'negative', '{"button": "schedule_lecture_url_change"}']
show_lecture_attendance = ['Посещаемость лекций', 'primary', '{"button": "schedule_lecture_attendance_"}']
send_lecture = ['Напомнить о лекции', 'primary', '{"button": "schedule_lecture_send_"}']
lectures_url_btn = ['Ссылки на лекции', 'primary', '{"button": "schedule_lecture_get"}']
show_schedule_btn = ['Расписание пар', 'primary', '{"button": "schedule_show_week"}']
##
schedule_kb_add = {
    # 1: (add_pair_comment, ),
    1: (add_lecture_url, ),
    2: (change_lecture_url, ),
    3: (show_lecture_attendance, ),
    4: (send_lecture, ),
    5: (lectures_url_btn, ),
    6: (show_schedule_btn, ),
    7: (cancel_btn, )
}
schedule_kb = {
    # 1: (add_pair_comment, ),
    2: (lectures_url_btn, ),
    3: (show_schedule_btn, ),
    4: (cancel_btn, )
}
show_schedule_kb = {
    1: (['Прошлая неделя', 'negative', '{"button": "schedule_show_week-last"}'], ),
    2: (['Эта неделя', 'primary', '{"button": "schedule_show_week-this"}'], ),
    3: (['Следующая неделя', 'positive', '{"button": "schedule_show_week-next"}'], ),
    4: (cancel_btn, )
}
