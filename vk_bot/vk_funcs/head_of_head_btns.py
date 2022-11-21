from typing import Any
from itertools import groupby

from reports.models import Student
from .config import *
from .all_buttons import cancel_btn, main_kb_student
from datetime import datetime, timedelta


def kb_generator(buttons: list, max_btn_in_line: int, first_raw=None, last_raw=None):
    raw = 1
    kb = {raw: []}

    lines = 10 - (1 if first_raw else 0) - (1 if last_raw else 0)
    if len(buttons) > max_btn_in_line * lines:
        if max_btn_in_line > 4:
            return False, {1: cancel_btn}, 1
        return kb_generator(buttons, max_btn_in_line + 1, first_raw, last_raw)

    def add_raw():
        nonlocal raw, kb
        raw += 1
        kb[raw] = []

    if first_raw:
        kb[raw] = first_raw
        add_raw()
    for s in buttons:
        if len(kb[raw]) == max_btn_in_line:
            add_raw()
        kb[raw].append(s)
    if last_raw:
        add_raw()
        kb[raw] = last_raw
    return True, kb, raw


def get_stream_kb(stud_info, pattern, values=None):
    streams = [int(x) for x in stud_info['can_add_lecture_url'].split(',')]
    values = values or {}
    if len(streams) == 1:
        return 'stream', streams[0]
    else:
        kb = {}
        for s in streams:
            kb[s] = [(f'{s} поток', 'primary', payload_constructor(pattern, {**values, 'stream': s}))]
        kb[10] = (cancel_btn,)
        return 'kb', kb


def show_stream_lecture_attendance(stud_info, stream=None, subject=None, lecture=None, mode=None):
    faculty = stud_info['faculty_id']
    course_n = stud_info['course_n']
    pattern = 'schedule_lecture_attendance'
    if not stream:
        result = get_stream_kb(stud_info, pattern)
        if result[0] == 'stream':
            return show_stream_lecture_attendance(stud_info, stream=result[1])
        else:
            return var_message(stud_info['vk_id'], '...', result[1])
    elif not subject:
        end_dt = datetime.now()
        begin_dt = datetime.now() - timedelta(days=90)
        cur.execute(
            'SELECT '
            '   DISTINCT s.id AS id, '
            '   s.short_title AS title '
            'FROM reports_lecturesschedule AS ls '
            '   JOIN reports_subject AS s '
            '       ON s.id = ls.subject_id '
            'WHERE '
            '   ls.faculty_id = %s AND '
            '   ls.course_n = %s AND '
            '   ls.stream_n = %s AND '
            '   lecture_datetime BETWEEN %s AND %s '
            'ORDER BY '
            '   title',
            (faculty, course_n, stream, begin_dt, end_dt)
        )
        subjects = cur.fetchall()
        if subjects:
            num = 1
            kb = {num: []}
            max_btn_in_line = 2 if len(subjects) < 14 else 3
            for subj in subjects:
                values = {'stream': stream, 'subject': subj['id']}
                kb[num].append((subj['title'], 'primary', payload_constructor(pattern, values)))
                if len(kb[num]) == max_btn_in_line:
                    num += 1
                    kb[num] = []
            if kb[num]:
                num += 1
                kb[num] = []
            kb[num] = [('<- Назад', 'negative', f'{{"button":"{pattern}_"}}'), cancel_btn]
            var_message(stud_info['vk_id'], '...', kb_params=kb)
        else:
            var_message(stud_info['vk_id'], f'Лекций у {stream} потока ещё не было')

    elif not lecture:
        end_dt = datetime.now()
        begin_dt = datetime.now() - timedelta(days=90)
        cur.execute(
            'SELECT '
            '   id AS id, '
            '   lecture_datetime AS dt '
            'FROM reports_lecturesschedule '
            'WHERE '
            '   faculty_id = %s AND '
            '   course_n = %s AND '
            '   stream_n = %s AND '
            '   subject_id = %s AND '
            '   lecture_datetime BETWEEN %s AND %s '
            'ORDER BY '
            '   dt',
            (faculty, course_n, stream, subject, begin_dt, end_dt)
        )
        lectures = cur.fetchall()
        if lectures:
            num = 1
            kb = {num: []}
            max_btn_in_line = 2 if len(lectures) < 14 else 3
            for lec in lectures:
                values = {'stream': stream, 'subject': subject, 'lecture': lec['id']}
                kb[num].append((lec['dt'].strftime('%d.%m %H:%M'), 'primary', payload_constructor(pattern, values)))
                if len(kb[num]) == max_btn_in_line:
                    num += 1
                    kb[num] = []
            if kb[num]:
                num += 1
                kb[num] = []
            kb[num].append(('<- Назад', 'negative', payload_constructor(pattern, {'stream': stream})))
            kb[num].append(cancel_btn)
            var_message(stud_info['vk_id'], '...', kb_params=kb)
        else:
            var_message(stud_info['vk_id'],
                        f'Лекций у {stream} потока по {get_subject_by_id(subject)["short_title"]} ещё не было')

    elif not mode:
        cur.execute(
            'SELECT '
            '   ps.group_n AS group_n, '
            '   (SELECT vk_id FROM reports_student '
            '       WHERE '
            '           faculty_id = ps.faculty_id AND '
            '           course_n = ps.course_n AND '
            '           group_n = ps.group_n AND '
            '           is_head = %s) AS vk_id '
            'FROM reports_pairsschedule AS ps '
            'WHERE '
            '   ps.lecture_id = %s AND '
            '   ps.is_reported = %s '
            'ORDER BY '
            '   group_n',
            (True, lecture, False)
        )
        not_rep = cur.fetchall()
        if not_rep:
            heads = [f'[id{s["vk_id"]}|{s["group_n"]}гр]' for s in not_rep]
            reply_msg = f'Не отправили рапорты: {", ".join(heads)}'
        else:
            reply_msg = 'Все старосты отправили рапорты'
        values = {'stream': stream, 'subject': subject}
        kb = {
            1: [('н', 'primary', payload_constructor(pattern, {**values, 'lecture': lecture, 'mode': 1}))],
            2: [('+/н', 'primary', payload_constructor(pattern, {**values, 'lecture': lecture, 'mode': 2}))],
            3: [('+/н/б/с', 'primary', payload_constructor(pattern, {**values, 'lecture': lecture, 'mode': 3}))]
        }
        var_message(stud_info['vk_id'], reply_msg, kb_params=kb, kb_inline=True)

    else:
        cur.execute('SELECT l.lecture_datetime AS dt, s.short_title AS subj '
                    'FROM reports_lecturesschedule AS l JOIN reports_subject AS s ON s.id = l.subject_id '
                    'WHERE l.id = %s', (lecture,))
        lec_info = cur.fetchone()
        if mode == 1:
            cur.execute(
                'SELECT '
                '   ps.group_n AS group_n, '
                '   ps.is_reported AS is_reported, '
                '   st.surname AS surname, '
                '   st.name AS name, '
                '   st.f_name AS f_name, '
                '   mp.student_id AS stud_id, '
                '   mp.missing_reason AS reason '
                'FROM reports_pairsschedule AS ps '
                '   LEFT JOIN reports_missingpair AS mp '
                '       ON mp.pair_id = ps.id '
                '   LEFT JOIN (SELECT '
                '           id, '
                '           surname, '
                '           name, '
                '           f_name '
                '       FROM reports_student '
                '       WHERE '
                '           faculty_id = %s AND '
                '           course_n = %s AND '
                '           stream_n = %s AND '
                '           is_fired = %s '
                '       ORDER BY '
                '           surname, '
                '           name) AS st '
                '       ON st.id = mp.student_id '
                'WHERE '
                '   ps.lecture_id = %s '
                'ORDER BY '
                '   group_n',
                (faculty, course_n, stream, False, lecture)
            )
            pairs = cur.fetchall()
            if not pairs:
                var_message(stud_info['vk_id'], 'Что-то не так, странненько, скажи [id39398636|Саше]')
                return
            pairs_by_group = {}
            for pair in pairs:
                if not pairs_by_group.get(pair['group_n']):
                    pairs_by_group[pair['group_n']] = {'is_rep': pair['is_reported'], 'studs': {}}
                if pair['reason']:
                    if pair["surname"]:
                        stud_name = f'{pair["surname"]} {pair["name"][0] if pair["name"] else "" }' \
                                    f'{pair["f_name"][0] if pair["f_name"] else "" }'
                        pairs_by_group[pair['group_n']]['studs'][pair['stud_id']] = stud_name

            reply_msg = f'Лекция {lec_info["subj"]} в {lec_info["dt"].strftime("%d.%m %H:%M")}\nОтсутствующие\n\n'
            for group, group_info in pairs_by_group.items():
                reply_msg += f'{group} группа:\n'
                if group_info['is_rep']:
                    if group_info['studs']:
                        for i, (st_id, st_name) in enumerate(group_info['studs'].items()):
                            reply_msg += f'{i+1}) {st_name}\n'
                        reply_msg += '\n'
                    else:
                        reply_msg += 'Все присутствовали\n\n'
                else:
                    reply_msg += 'Рапорт ещё не отправлен\n\n'
        else:
            cur.execute(
                'SELECT '
                '   ps.group_n AS group_n, '
                '   ps.is_reported AS is_reported, '
                '   mp.student_id AS stud_id, '
                '   mp.missing_reason AS reason '
                'FROM reports_pairsschedule AS ps '
                '   LEFT JOIN reports_missingpair AS mp '
                '       ON mp.pair_id = ps.id '
                'WHERE '
                '   ps.lecture_id = %s '
                'ORDER BY '
                '   group_n',
                (lecture, )
            )
            pairs = cur.fetchall()
            if not pairs:
                var_message(stud_info['vk_id'], 'Что-то не так, странненько, скажи [id39398636|Саше]')
                return
            pairs_by_group = {}
            for pair in pairs:
                if not pairs_by_group.get(pair['group_n']):
                    pairs_by_group[pair['group_n']] = {'is_rep': pair['is_reported'], 'studs': {}}
                if pair['reason']:
                    pairs_by_group[pair['group_n']]['studs'][pair['stud_id']] = pair['reason']

            cur.execute(
                'SELECT group_n, id, surname, name, f_name FROM reports_student WHERE '
                '  faculty_id = %s AND course_n = %s and stream_n = %s and is_fired = %s '
                'ORDER BY group_n, surname, name, f_name',
                (faculty, course_n, stream, False)
            )
            students = cur.fetchall()
            studs_by_group = {}
            for stud in students:
                if not studs_by_group.get(stud['group_n']):
                    studs_by_group[stud['group_n']] = {}
                stud_name = f'{stud["surname"]} {stud["name"][0] if stud["name"] else ""}' \
                            f'{stud["f_name"][0] if stud["f_name"] else ""}'
                studs_by_group[stud['group_n']][stud['id']] = stud_name
            reply_msg = f'Лекция {lec_info["subj"]} в {lec_info["dt"].strftime("%d.%m %H:%M")}\n\n'
            for group, group_info in pairs_by_group.items():
                group_msg = f'{group} группа:\n'
                if group_info['is_rep']:
                    group_studs = group_info['studs']
                    for i, (st_id, st_name) in enumerate(studs_by_group[group].items()):
                        miss = group_studs.get(st_id)
                        if miss:
                            reason = 'н' if mode == 2 else miss
                        else:
                            reason = '+'
                        group_msg += f'{reason} - {i+1}) {st_name}\n'
                else:
                    group_msg += 'Рапорт ещё не отправлен\n\n'
                reply_msg += f'{group_msg}\n\n'
        for msg_part in seq_separator(reply_msg, 3500):
            var_message(stud_info['vk_id'], msg_part)


def send_lecture_by_query(stud_info, stream=None, lecture=None, group=None, mode=None):
    faculty = stud_info['faculty_id']
    course_n = stud_info['course_n']
    pattern = 'schedule_lecture_send'

    if not stream:
        if stud_info['can_add_lecture_url']:
            result, obj = get_stream_kb(stud_info, pattern)
            if result == 'stream':
                send_lecture_by_query(stud_info, stream=obj)
            elif result == 'kb':
                var_message(stud_info['vk_id'], text='...', kb_params=obj)
        elif stud_info['is_head'] or stud_info['is_head_assistant']:
            stream = stud_info['stream_n']
            group = stud_info['group_n']
            send_lecture_by_query(stud_info, stream=stream, group=group)
        else:
            var_message(stud_info['vk_id'], 'Незя', kb_params=main_kb_student)
    elif not lecture:
        begin_dt = datetime.combine(datetime.now().date(), datetime.min.time())
        end_dt = begin_dt + timedelta(days=2)
        cur.execute(
            'SELECT '
            '   l.id AS id, '
            '   l.lecture_datetime AS dt, '
            '   s.short_title AS subj '
            'FROM reports_lecturesschedule AS l '
            '   JOIN reports_subject AS s '
            '      ON s.id = l.subject_id '
            'WHERE '
            '   l.faculty_id = %s AND '
            '   l.course_n = %s AND '
            '   l.stream_n = %s AND '
            '   l.lecture_datetime BETWEEN %s AND %s '
            'ORDER BY '
            '   dt',
            (faculty, course_n, stream, begin_dt, end_dt)
        )
        lectures = cur.fetchall()
        count = len(lectures)
        if count == 0:
            var_message(stud_info['vk_id'], f'У {stream} потока лекций сегодня нет')
        elif count == 1:
            send_lecture_by_query(stud_info, stream=stream, lecture=lectures[0]['id'], group=group)
        else:
            buttons = []
            for lec in lectures:
                btn_title = lec["dt"].strftime("%d.%m {} %H:%M").format(lec["subj"])
                pl = payload_constructor(pattern, {'stream': stream, 'lecture': lec['id'], 'group': group})
                buttons.append((btn_title, 'primary', pl))
            last_raw = (('<-Назад', 'negative', payload_constructor(pattern, {})), cancel_btn)
            success, kb, raw = kb_generator(buttons, 1, last_raw=last_raw)
            if success:
                var_message(stud_info['vk_id'], '...', kb_params=kb)
            else:
                var_message(stud_info['vk_id'], 'Что-то не так')
    elif not group:
        cur.execute(
            'SELECT DISTINCT group_n AS group_n FROM reports_student WHERE '
            '   faculty_id = %s AND course_n = %s AND stream_n = %s ORDER BY group_n',
            (faculty, course_n, stream)
        )
        groups = [x['group_n'] for x in cur.fetchall()]
        buttons = []
        payload_values = {'stream': stream, 'lecture': lecture, 'group': 'all'}
        first_raw = ((f'Весь {stream} поток', 'positive', payload_constructor(pattern, {**payload_values})), )
        last_raw = (('<-Назад', 'negative', payload_constructor(pattern, {})), cancel_btn)
        for gr in groups:
            buttons.append((f'{gr}гр', 'primary', payload_constructor(pattern, {**payload_values, 'group': gr})))
        success, kb, raw = kb_generator(buttons, 3, first_raw=first_raw, last_raw=last_raw)
        if success:
            var_message(stud_info['vk_id'], '...', kb_params=kb)
        else:
            var_message(stud_info['vk_id'], 'Что-то не то', kb_params=kb)
    elif not mode:
        payload_values = {'stream': stream, 'lecture': lecture, 'group': group}
        kb = {
            1: (('Быстрее подключайтесь', 'secondary', payload_constructor(pattern, {**payload_values, 'mode': 1})),),
            2: (('Ссылка', 'secondary', payload_constructor(pattern, {**payload_values, 'mode': 2})),),
            3: (('Лекции не будет', 'secondary', payload_constructor(pattern, {**payload_values, 'mode': 3})), )
        }
        reply_msg = f'Выбери что отправить {f"{group} группе" if group != "all" else f"{stream} потоку"}'
        var_message(stud_info['vk_id'], reply_msg, kb_params=kb, kb_inline=True)
    else:
        cur.execute(
            'SELECT '
            '   l.lecture_datetime AS dt, '
            '   l.lecture_url as url, '
            '   s.short_title AS subj '
            'FROM reports_lecturesschedule AS l '
            '   JOIN reports_subject AS s '
            '      ON s.id = l.subject_id '
            'WHERE '
            '   l.id = %s ',
            (lecture,)
        )
        lecture = cur.fetchone()
        msg_pattern = f'по {lecture["subj"]} в {lecture["dt"].strftime("%H:%M")}'
        if mode == 1:
            reply_msg = f'Быстрее подключайся\nЛекция {msg_pattern}\n{lecture["url"]}'
        elif mode == 2:
            reply_msg = f'Лекция {msg_pattern}\n{lecture["url"]}'
        else:
            reply_msg = f'Сегодня не будет лекции {msg_pattern}'

        st_or_gr = ('stream_n = %s', stream) if group == 'all' else ('group_n = %s', group)
        cur.execute(
            'SELECT vk_id FROM reports_student WHERE '
            f'  faculty_id = %s AND course_n = %s AND {st_or_gr[0]} AND vk_id IS NOT NULL',
            (faculty, course_n, st_or_gr[1])
        )
        studs = [str(x['vk_id']) for x in cur.fetchall()]
        for user_set in seq_separator(studs, 99):
            var_message(user_ids=','.join(user_set), text=reply_msg)


def last_reports(stud_info):
    faculty_id = stud_info['faculty_id']
    course_n = stud_info['course_n']
    cur.execute(
        'SELECT * FROM reports_student WHERE faculty_id = %s AND course_n = %s AND is_head = %s '
        'ORDER BY group_n',
        (faculty_id, course_n, True)
    )
    heads = cur.fetchall()
    unauth_heads_msg = []
    last_report_msg = 'Последние рапортички (дата):'
    if heads:
        for h in heads:
            if h['vk_id'] is None:
                unauth_heads_msg.append(f'\n{h["group_n"]}гр - {h["surname"]} {h["name"]}')
            cur.execute(
                'SELECT max(pr_lk_datetime) AS dt FROM reports_pairsschedule '
                'WHERE faculty_id = %s AND course_n = %s AND group_n = %s AND is_reported = %s',
                (h['faculty_id'], h['course_n'], h['group_n'], True)
            )
            last_report = cur.fetchone()
            last_report_msg += f'\n{h["group_n"]}гр - {h["surname"]} - ' \
                               f'{last_report["dt"].strftime("%d.%m.%Y") if last_report["dt"] else "Нет ни одного"}'

    unauth_heads_msg = f'Неавторизованные старосты:{"".join(unauth_heads_msg)}\n\n' if unauth_heads_msg else ''
    var_message(stud_info['vk_id'], f'{unauth_heads_msg}{last_report_msg}')


def send_stud_list(hoh_info: dict[str, Any], stream_n: int = None, group_n: int = None):
    students = Student.objects.\
        filter(faculty_id=hoh_info['faculty_id'], is_fired=False)\
        .order_by('group_n', 'surname', 'name', 'f_name')
    if stream_n:
        students = students.filter(stream_n=stream_n)
    elif group_n:
        students = students.filter(group_n=group_n)
    if not students:
        return var_message(
            hoh_info['vk_id'],
            text=f'Не нашёл {f"{stream_n} поток" if stream_n else f"{group_n} группу"} :(',
        )
    text = ''
    grouped_studs = groupby(students, key=lambda s: s.group_n)
    for group, studs_list in grouped_studs:
        text += f'\n{group} группа\n'
        for stud in studs_list:
            text += f'{stud}\n'
        if len(text) > 3000:
            var_message(hoh_info['vk_id'], text=text)
            text = ''
    var_message(hoh_info['vk_id'], text=text)
