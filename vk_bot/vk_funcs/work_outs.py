from .config import *
from .all_buttons import *
from datetime import datetime


def work_out_payload_parsing(user_id, payload):
    payload_str = payload[11:-2]
    payload_lvl = payload_str.split('_')
    if len(payload_lvl) == 3:
        var_message(user_id, '...', kb_params=work_out_mark_kb if payload_lvl[2] == 'mark' else work_out_remark_kb)
    else:
        stud_info = get_user_by_vk_id(user_id)
        if not stud_info:
            var_message(user_id, 'Ты не авторизован', kb_params=before_login_kb)
            return
        if len(payload_lvl) == 4:
            mark = True if payload_lvl[2] == 'mark' else False
            if stud_info['is_locked']:
                var_message(user_id, 'Ты не можешь изменять отработки', kb_params=main_kb_student)
                return
            pr_or_lk_lvl = payload_lvl[3].split('-')
            is_practical = True if pr_or_lk_lvl[0] == 'practical' else False
            if len(pr_or_lk_lvl) == 1:
                if stud_info['is_head'] or stud_info['is_head_assistant']:
                    show_students_to_head_for_work_out(user_id, stud_info, mark, is_practical)
                else:
                    show_subjects_for_work_out(user_id, stud_info, mark, is_practical, stud_info['id'])
            else:
                stud_id = int(pr_or_lk_lvl[1])
                if len(pr_or_lk_lvl) == 2:
                    show_subjects_for_work_out(user_id, stud_info, mark, is_practical, stud_id)
                else:
                    subj_id = int(pr_or_lk_lvl[2])
                    if len(pr_or_lk_lvl) == 3:
                        show_subject_dates_for_work_out(user_id, stud_info, mark, is_practical, stud_id, subj_id)
                    elif len(pr_or_lk_lvl) == 4:
                        pair_date = datetime.strptime(pr_or_lk_lvl[3], '%Y.%m.%d %H:%M:%S')
                        mark_remark_work_out(user_id, stud_info, mark, is_practical, stud_id, subj_id, pair_date)


def show_students_to_head_for_work_out(user_id, head_info, mark, is_practical):
    faculty_id = head_info['faculty_id']
    course_n = head_info['course_n']
    group_n = head_info['group_n']

    cur.execute(
        '''SELECT
            mp_st.st_id AS student_id,
            mp_st.pos AS pos,
            mp_st.surname as surname,
            mp_st.name as name
        FROM reports_pairsschedule AS ps
            JOIN reports_subject AS s
            ON s.id = ps.subject_id
            JOIN (
                SELECT
                    mp.pair_id AS pair_id,
                    st.id AS st_id,
                    st.position_in_group AS pos,
                    st.surname AS surname,
                    st.name AS name
                FROM reports_missingpair AS mp
                    JOIN reports_student AS st
                    ON st.id = mp.student_id
                WHERE
                    mp.is_debt = %s AND
                    mp.missing_reason != %s AND
                    st.is_fired = %s) AS mp_st
            ON mp_st.pair_id = ps.id
        WHERE
            ps.faculty_id = %s AND
            ps.course_n = %s AND
            ps.group_n = %s AND
            ps.is_practical = %s
        GROUP BY
            mp_st.st_id,
            mp_st.pos,
            mp_st.surname,
            mp_st.name''',
        (mark, 'с', False, faculty_id, course_n, group_n, is_practical)
    )
    studs_info = cur.fetchall()
    if not studs_info:
        reply_msg = 'У тебя и твоих одногруппников нет {}отработанных {}'.format(
            'не' if mark else '', 'практических занятий' if is_practical else 'лекций')
        var_message(user_id, reply_msg, kb_params=main_kb_head)
        return
    num = 1
    studs_work_out_kb = {num: []}
    payload_button = '{{{{"button":"work_out_{}_{}-{{}}"}}}}'.format('mark' if mark else 'remark',
                                                                     'practical' if is_practical else 'lecture')
    max_btn_in_line = 3 if len(studs_info) > 16 else 2
    for stud in studs_info:
        studs_work_out_kb[num].append(
            (f'{stud["pos"]}. {stud["surname"]}', 'primary', payload_button.format(stud['student_id']))
        )
        if len(studs_work_out_kb[num]) == max_btn_in_line:
            num += 1
            studs_work_out_kb[num] = []
    studs_work_out_kb[num].append(cancel_btn)
    var_message(user_id, '...', studs_work_out_kb)


def show_subjects_for_work_out(user_id, stud_info, mark, is_practical, stud_id):
    faculty_id = stud_info['faculty_id']
    course_n = stud_info['course_n']
    group_n = stud_info['group_n']

    cur.execute(
        '''SELECT
            s.id AS subject_id,
            s.short_title AS subject
        FROM reports_pairsschedule AS ps
            JOIN reports_subject AS s
            ON s.id = ps.subject_id
            JOIN (
                SELECT
                    mp.pair_id AS pair_id,
                    st.id AS st_id,
                    st.position_in_group AS pos,
                    st.surname AS surname,
                    st.name AS name
                FROM reports_missingpair AS mp
                    JOIN reports_student AS st
                    ON st.id = mp.student_id
                WHERE
                    st.id = %s AND
                    mp.is_debt = %s AND
                    mp.missing_reason != %s) AS mp_st
            ON mp_st.pair_id = ps.id
        WHERE
            ps.faculty_id = %s AND
            ps.course_n = %s AND
            ps.group_n = %s AND
            ps.is_practical = %s
        GROUP BY
            s.id''',
        (stud_id, mark, 'с', faculty_id, course_n, group_n, is_practical)
    )
    subjects = cur.fetchall()
    if not subjects:
        if stud_info['id'] == stud_id:
            name = 'тебя'
        else:
            s = get_user_by_stud_id(stud_id)
            name = f'{s["surname"]} {s["name"]}'
        reply_msg = 'У {} нет {}отработанных {}'.format(name, 'не' if mark else '',
                                                        'практических занятий' if is_practical else 'лекций')
        if not (stud_info['is_head'] or stud_info['is_head_assistant']):
            var_message(user_id, reply_msg, main_kb_student)
        else:
            var_message(user_id, reply_msg, main_kb_student)
        return

    num = 1
    subj_work_out_kb = {num: []}
    payload_button = '{{{{"button":"work_out_{}_{}-{{}}-{{}}"}}}}'.format('mark' if mark else 'remark',
                                                                          'practical' if is_practical else 'lecture')
    max_btn_in_line = 3 if len(subjects) > 16 else 2
    for subj in subjects:
        subj_work_out_kb[num].append((subj['subject'], 'primary', payload_button.format(stud_id, subj['subject_id'])))
        if len(subj_work_out_kb[num]) == max_btn_in_line:
            num += 1
            subj_work_out_kb[num] = []
    if stud_info['is_head'] or stud_info['is_head_assistant']:
        back_btn = ['<-Назад', 'negative', '{{"button":"work_out_{}_{}"}}'.format(
            'mark' if mark else 'remark',
            'practical' if is_practical else 'lecture'
        )]
        subj_work_out_kb[num].append(back_btn)
    else:
        subj_work_out_kb[num].append(cancel_btn)
    var_message(user_id, '...', subj_work_out_kb)


def show_subject_dates_for_work_out(user_id, stud_info, mark, is_practical, stud_id, subj_id, r_msg='...'):
    faculty_id = stud_info['faculty_id']
    course_n = stud_info['course_n']
    group_n = stud_info['group_n']

    cur.execute(
        '''SELECT
            ps.pr_lk_datetime as pr_lk_datetime
        FROM reports_pairsschedule AS ps
            JOIN reports_subject AS s
            ON s.id = ps.subject_id
            JOIN (
                SELECT
                    mp.pair_id AS pair_id,
                    st.id AS st_id,
                    st.position_in_group AS pos,
                    st.surname AS surname,
                    st.name AS name
                FROM reports_missingpair AS mp
                    JOIN reports_student AS st
                    ON st.id = mp.student_id
                WHERE
                    st.id = %s AND
                    mp.is_debt = %s AND
                    mp.missing_reason != %s) AS mp_st
            ON mp_st.pair_id = ps.id
        WHERE
            ps.faculty_id = %s AND
            ps.course_n = %s AND
            ps.group_n = %s AND
            ps.is_practical = %s AND
            s.id = %s
        ORDER BY
            ps.pr_lk_datetime''',
        (stud_id, mark, 'с', faculty_id, course_n, group_n, is_practical, subj_id)
    )
    subj_dates = cur.fetchall()
    if not subj_dates:
        if stud_info['id'] == stud_id:
            name = 'тебя'
        else:
            s = get_user_by_stud_id(stud_id)
            name = f'{s["surname"]} {s["name"]}'
        subject_title = get_subject_by_id(subj_id)['short_title']
        reply_msg = 'У {} нет {}отработанных {} по {}'.format(
            name, 'не' if mark else '', 'практических занятий' if is_practical else 'лекций', subject_title)
        if not (stud_info['is_head'] or stud_info['is_head_assistant']):
            var_message(user_id, reply_msg, main_kb_student)
        else:
            var_message(user_id, reply_msg)
        return

    num = 1
    dates_work_out_kb = {num: []}
    payload_button = '{{{{"button":"work_out_{}_{}-{{}}-{{}}-{{}}"}}}}'.format(
        'mark' if mark else 'remark', 'practical' if is_practical else 'lecture')
    max_btn_in_line = 3 if len(subj_dates) > 16 else 2
    for subj_date in subj_dates:
        s_date = subj_date['pr_lk_datetime'].strftime('%d.%m %H:%M')
        s_date_p = subj_date['pr_lk_datetime'].strftime('%Y.%m.%d %H:%M:%S')
        dates_work_out_kb[num].append((s_date, 'primary', payload_button.format(stud_id, subj_id, s_date_p)))
        if len(dates_work_out_kb[num]) == max_btn_in_line:
            num += 1
            dates_work_out_kb[num] = []
    back_btn = ['<-Назад', 'negative', '{{{{"button":"work_out_{}_{}{{}}"}}}}'.format(
        'mark' if mark else 'remark',
        'practical' if is_practical else 'lecture'
    )]
    back_btn[2] = back_btn[2].format(f'-{stud_id}' if stud_info['is_head'] or stud_info['is_head_assistant'] else '')
    dates_work_out_kb[num].append(back_btn)
    var_message(user_id, r_msg, dates_work_out_kb)


def mark_remark_work_out(user_id, stud_info, mark, is_practical, stud_id, subj_id, pair_date):
    faculty_id = stud_info['faculty_id']
    course_n = stud_info['course_n']
    group_n = stud_info['group_n']

    cur.execute(
        '''SELECT
            ps.id AS pair_id,
            s.short_title AS subject,
            mp_st.surname AS surname,
            mp_st.name AS name
        FROM reports_pairsschedule AS ps
            JOIN reports_subject AS s
            ON s.id = ps.subject_id
            JOIN (
                SELECT
                    mp.pair_id AS pair_id,
                    st.id AS st_id,
                    st.position_in_group AS pos,
                    st.surname AS surname,
                    st.name AS name
                FROM reports_missingpair AS mp
                    JOIN reports_student AS st
                    ON st.id = mp.student_id
                WHERE
                    st.id = %s AND
                    mp.is_debt = %s AND
                    mp.missing_reason != %s) AS mp_st
            ON mp_st.pair_id = ps.id
        WHERE
            ps.faculty_id = %s AND
            ps.course_n = %s AND
            ps.group_n = %s AND
            ps.is_practical = %s AND
            s.id = %s AND
            ps.pr_lk_datetime = %s''',
        (stud_id, mark, 'с', faculty_id, course_n, group_n, is_practical, subj_id, pair_date)
    )
    pair = cur.fetchone()
    p_date_str = pair_date.strftime('%d.%m в %H:%M')
    if stud_info['id'] == stud_id:
        name = 'тебя'
    else:
        s = get_user_by_stud_id(stud_id)
        name = f'{s["surname"]} {s["name"]}'
    if not pair:
        subject_title = get_subject_by_id(subj_id)['short_title']
        reply_msg = 'За {} по {} {} у {} нет {}'.format(
            'практическое занятие' if is_practical else 'лекцию', subject_title, p_date_str, name,
            'задолженности' if mark else 'отмеченной отработки'
        )
        var_message(user_id, reply_msg)
        return
    cur.execute(
        'UPDATE reports_missingpair SET is_debt = %s, work_out_datetime = %s WHERE pair_id = %s AND student_id = %s',
        (not mark, datetime.now() if mark else None, pair['pair_id'], stud_id)
    )
    connection.commit()
    debt_msg = 'Отработка за {} по {} {} у {} {}'.format(
        'практическое занятие' if is_practical else 'лекцию', pair['subject'], p_date_str, name,
        "принята" if mark else "отменена")
    var_message(user_id, debt_msg)
    # show_subject_dates_for_work_out(user_id, stud_info, mark, is_practical, stud_id, subj_id, r_msg=debt_msg)
