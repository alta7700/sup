from .config import *
from .all_buttons import *
from .instructions import *


def log_in(user_id, msg):
    msg = msg.split('\n')
    if len(msg) == 2:
        login = msg[0].strip().lower()
        password = msg[1].strip().replace('l', 'I')
        cur.execute(
            'SELECT * FROM reports_student WHERE login = %s AND password = %s',
            (login, password)
        )
        student = cur.fetchone()
        if student:
            if not student['vk_id'] is None:
                var_message(user_id, 'Кто-то уже авторизован под этим логином')
                return
            if not student['is_fired']:
                cur.execute(
                    'UPDATE reports_student SET vk_id = %s WHERE login = %s AND password = %s',
                    (user_id, login, password)
                )
                connection.commit()
                if student['is_head'] or student['is_head_assistant']:
                    kb = main_kb_head
                else:
                    kb = main_kb_student
                var_message(user_id, f'Привет, {student["surname"]} {student["name"]}, рад тебя видеть', kb)
                if student['is_head']:
                    get_group_members_passwd(user_id, student)
            else:
                var_message(user_id, 'Ты отчислен или что-то типа того (если нет, то попроси у старосты пароль,'
                                     'он точно подойдёт)', before_login_kb)
        else:
            var_message(user_id, 'Неправильный логин или пароль', before_login_kb)
    else:
        var_message(user_id, 'Нужно так:\n1 строка - логин\n 2 строка - пароль', before_login_kb)


def log_out(user_id):
    cur.execute('UPDATE reports_student SET vk_id = %s WHERE vk_id = %s', (None, user_id))
    connection.commit()
    var_message(user_id, 'До встречи', kb_params=before_login_kb)


def switch_off_groupmate(user_id, payload_pars):
    payload_pars = payload_pars.split('-')
    payload_pars_len = len(payload_pars)

    if payload_pars_len == 1:
        stud_info = get_user_by_vk_id(user_id)
        faculty_id = stud_info['faculty_id']
        course_n = stud_info['course_n']
        group_n = stud_info['group_n']
        cur.execute(
            '''SELECT id, position_in_group AS pos, surname FROM reports_student
            WHERE faculty_id = %s AND course_n = %s AND group_n = %s AND is_fired = %s AND is_head = %s
            ORDER BY position_in_group''',
            (faculty_id, course_n, group_n, False, False)
        )
        studs = cur.fetchall()
        num = 1
        studs_kb = {num: []}
        max_btn_in_line = 3 if len(studs) > 16 else 2
        for stud in studs:
            studs_kb[num].append(
                (f'{stud["pos"]}.{stud["surname"]}', 'primary', f'{{"button": "log_off-{stud["id"]}"}}')
            )
            if len(studs_kb[num]) == max_btn_in_line:
                num += 1
                studs_kb[num] = []
        studs_kb[num].append(cancel_btn)
        var_message(user_id, '...', kb_params=studs_kb)
    else:
        stud_id = int(payload_pars[1])
        cur.execute(
            '''SELECT name, surname, vk_id FROM reports_student WHERE id = %s''',
            (stud_id, )
        )
        s = cur.fetchone()
        if not s:
            var_message(user_id, 'Такого студента нет')
            return
        if s['vk_id'] is None:
            var_message(user_id, f'{s["name"]} {s["surname"]} не был авторизован')
        else:
            cur.execute('''UPDATE reports_student SET vk_id = %s WHERE id = %s''', (None, stud_id))
            var_message(user_id, f'{s["name"]} {s["surname"]} теперь не авторизован')


def get_locked_groupmates_kb(user_id):
    user_info = get_user_by_vk_id(user_id)
    if user_info:
        if user_info['is_head'] or user_info['is_head_assistant']:
            cur.execute(
                '''SELECT * FROM reports_student WHERE
                faculty_id = %s AND course_n = %s AND group_n = %s AND is_head = %s AND is_locked = %s AND is_fired = %s
                ORDER BY position_in_group''',
                (user_info['faculty_id'], user_info['course_n'], user_info['group_n'], False, True, False)
            )
            locked_groupmates = cur.fetchall()
            if locked_groupmates:
                num = 2
                locked_kb = {1: [('Разблокировать всех', 'positive', '{"button": "roles_unlock_all"}'), ], num: []}
                msx_btn_in_line = 3 if len(locked_groupmates) > 16 else 2
                for stud in locked_groupmates:
                    locked_kb[num].append(
                        (f'{stud["position_in_group"]}.{stud["surname"]}', 'primary', '{"button": "roles_unlock_one"}')
                    )
                    if len(locked_kb[num]) == msx_btn_in_line:
                        num += 1
                        locked_kb[num] = []
                locked_kb[num].append(cancel_btn)
                var_message(user_id, '...', kb_params=locked_kb)
            else:
                var_message(user_id, 'Все твои одногруппники разблокированы', kb_params=main_kb_head)
        else:
            var_message(user_id, 'Ты не староста, откуда кнопка😕', kb_params=main_kb_student)
    else:
        var_message(user_id, 'Ты не авторизован', kb_params=before_login_kb)


def get_unlocked_groupmates_kb(user_id):
    user_info = get_user_by_vk_id(user_id)
    if user_info:
        if user_info['is_head'] or user_info['is_head_assistant']:
            cur.execute(
                '''SELECT * FROM reports_student WHERE
                faculty_id = %s AND course_n = %s AND group_n = %s AND is_head = %s AND is_locked = %s AND is_fired = %s
                ORDER BY id''',
                (user_info['faculty_id'], user_info['course_n'], user_info['group_n'], False, False, False)
            )
            unlocked_groupmates = cur.fetchall()
            if unlocked_groupmates:
                num = 2
                unlocked_kb = {1: [('Заблокировать всех', 'negative', '{"button": "roles_lock_all"}'), ], num: []}
                max_btn_in_line = 3 if len(unlocked_groupmates) > 16 else 2
                for stud in unlocked_groupmates:
                    unlocked_kb[num].append(
                        (f'{stud["position_in_group"]}.{stud["surname"]}', 'primary', '{"button": "roles_lock_one"}')
                    )
                    if len(unlocked_kb[num]) == max_btn_in_line:
                        num += 1
                        unlocked_kb[num] = []
                unlocked_kb[num].append(cancel_btn)
                var_message(user_id, '...', kb_params=unlocked_kb)
            else:
                var_message(user_id, 'Все твои одногруппники заблокированы', kb_params=main_kb_head)
        else:
            var_message(user_id, 'Ты не староста, откуда кнопка😕', kb_params=main_kb_student)
    else:
        var_message(user_id, 'Ты не авторизован', kb_params=before_login_kb)


def get_groupmates_to_choose_assistant(user_id):
    head_info = get_user_by_vk_id(user_id)
    if head_info:
        if head_info['is_head']:
            cur.execute(
                '''SELECT * FROM reports_student WHERE
                faculty_id = %s AND course_n = %s AND group_n = %s AND is_head = %s AND is_locked = %s AND is_fired = %s
                ORDER BY id''',
                (head_info['faculty_id'], head_info['course_n'], head_info['group_n'], False, False, False)
            )
            unlocked_groupmates = cur.fetchall()
            if unlocked_groupmates:
                payload_btn = '{"button": "roles_assistant_make"}'
                num = 2
                assistants_kb = {1: [('Обнулить', 'negative', '{"button": "roles_assistant_zero"}'), ], num: []}
                head_assistant = None
                max_btn_in_line = 3 if len(unlocked_groupmates) > 16 else 2
                for stud in unlocked_groupmates:
                    btn_color = 'primary'
                    if stud["is_head_assistant"]:
                        head_assistant = f'{stud["name"]} {stud["surname"]}'
                        btn_color = 'positive'
                    assistants_kb[num].append(
                        (f'{stud["position_in_group"]}.{stud["surname"]}', btn_color, payload_btn)
                    )
                    if len(assistants_kb[num]) == max_btn_in_line:
                        num += 1
                        assistants_kb[num] = []
                assistants_kb[num].append(cancel_btn)
                if head_assistant:
                    var_message(user_id, f'Сейчас тебе помогает {head_assistant}', kb_params=assistants_kb)
                else:
                    var_message(user_id, 'Выбери себе помощника', kb_params=assistants_kb)
            else:
                var_message(user_id, 'Сначала разблокируй хоть кого-то', kb_params=main_kb_head)
        elif head_info['is_head_assistant']:
            var_message(user_id, 'Когда станешь старостой, тогда и будешь помощников выбирать', kb_params=main_kb_head)
        else:
            var_message(user_id, 'Ты не староста, откуда кнопка😕', kb_params=main_kb_student)
    else:
        var_message(user_id, 'Ты не авторизован', kb_params=before_login_kb)


def unlock_groupmate(user_id, msg, unlock_all=False):
    head_info = get_user_by_vk_id(user_id)
    if head_info:
        if head_info['is_head'] or head_info['is_head_assistant']:
            if unlock_all:
                cur.execute(
                    '''UPDATE reports_student SET is_locked = %s WHERE faculty_id = %s AND course_n = %s
                    AND group_n = %s AND is_head = %s AND is_locked = %s''',
                    (False, head_info['faculty_id'], head_info['course_n'], head_info['group_n'], False, True)
                )
                connection.commit()
                var_message(user_id, 'Все твои одногруппники разблокированы', kb_params=main_kb_head)
            else:
                pos = msg.split('.')[0]
                surname = msg.split('.')[1].strip()
                cur.execute(
                    '''SELECT * FROM reports_student WHERE faculty_id = %s AND course_n = %s
                    AND group_n = %s AND is_head = %s AND position_in_group = %s AND surname = %s''',
                    (head_info['faculty_id'], head_info['course_n'], head_info['group_n'],
                     False, pos, surname)
                )
                stud_info = cur.fetchone()
                if stud_info:
                    if stud_info['is_locked']:
                        cur.execute(
                            'UPDATE reports_student SET is_locked = %s WHERE id = %s',
                            (False, stud_info['id'])
                        )
                        connection.commit()
                        var_message(user_id, f'Пользователь {surname} {stud_info["name"]} разблокирован')
                    else:
                        var_message(user_id, f'Пользователь {surname} {stud_info["name"]} был разблокирован')
                    get_locked_groupmates_kb(user_id)
                else:
                    var_message(user_id, 'Что-то не так, почему-то такого студента нет😕\nНапиши [id39398636|Саше]')
        else:
            var_message(user_id, 'Ты не староста, откуда кнопка😕', kb_params=main_kb_student)
    else:
        var_message(user_id, 'Ты не авторизован', kb_params=before_login_kb)


def lock_groupmate(user_id, msg, lock_all=False):
    head_info = get_user_by_vk_id(user_id)
    if head_info:
        if head_info['is_head'] or head_info['is_head_assistant']:
            if lock_all:
                cur.execute(
                    '''UPDATE reports_student SET is_locked = %s WHERE faculty_id = %s AND course_n = %s
                    AND group_n = %s AND is_head = %s AND is_locked = %s''',
                    (True, head_info['faculty_id'], head_info['course_n'], head_info['group_n'], False, False)
                )
                connection.commit()
                var_message(user_id, 'Все твои одногруппники заблокированы', kb_params=main_kb_head)
            else:
                pos = msg.split('.')[0]
                surname = msg.split('.')[1].strip()
                cur.execute(
                    '''SELECT * FROM reports_student WHERE faculty_id = %s AND course_n = %s
                    AND group_n = %s AND is_head = %s AND position_in_group = %s AND surname = %s''',
                    (head_info['faculty_id'], head_info['course_n'], head_info['group_n'],
                     False, pos, surname)
                )
                stud_info = cur.fetchone()
                if stud_info:
                    if not stud_info['is_locked']:
                        cur.execute(
                            'UPDATE reports_student SET is_locked = %s, is_head_assistant = %s WHERE id = %s',
                            (True, False, stud_info['id'])
                        )
                        connection.commit()
                        var_message(user_id, f'{surname} {stud_info["name"]} теперь не может ничего изменять')
                    else:
                        var_message(user_id, f'{surname} {stud_info["name"]} и так заблокирован')
                else:
                    var_message(user_id, 'Что-то не так, почему-то такого студента нет😕\nНапиши [id39398636|Саше]')
                get_unlocked_groupmates_kb(user_id)
        else:
            var_message(user_id, 'Ты не староста, откуда кнопка😕', kb_params=main_kb_student)
    else:
        var_message(user_id, 'Ты не авторизован', kb_params=before_login_kb)


def make_assistant(user_id, msg, zero_only=False):
    head_info = get_user_by_vk_id(user_id)
    if head_info:
        if head_info['is_head']:
            cur.execute(
                '''UPDATE reports_student SET is_head_assistant = %s WHERE
                faculty_id = %s AND course_n = %s AND group_n = %s''',
                (False, head_info['faculty_id'], head_info['course_n'], head_info['group_n'])
            )
            connection.commit()
            if not zero_only:
                pos = msg.split('.')[0]
                surname = msg.split('.')[1].strip()
                cur.execute(
                    '''SELECT * FROM reports_student WHERE faculty_id = %s AND course_n = %s
                    AND group_n = %s AND is_head = %s AND position_in_group = %s AND surname = %s''',
                    (head_info['faculty_id'], head_info['course_n'], head_info['group_n'],
                     False, pos, surname)
                )
                stud_info = cur.fetchone()
                if stud_info:
                    if not stud_info['is_head_assistant']:
                        cur.execute(
                            'UPDATE reports_student SET is_head_assistant = %s WHERE id = %s',
                            (True, stud_info['id'])
                        )
                        connection.commit()
                        var_message(user_id, f'{stud_info["name"]} {surname} теперь твой помощник',
                                    kb_params=main_kb_head)
                    else:
                        var_message(user_id, f'{stud_info["name"]} {surname} и так был твоим помощником')
                else:
                    var_message(user_id, 'Что-то не так, почему-то такого студента нет😕\nНапиши [id39398636|Саше]',
                                kb_params=main_kb_head)
            else:
                var_message(user_id, f'Обнуление прошло успешно', kb_params=main_kb_head)
        elif head_info['is_head_assistant']:
            var_message(user_id, 'Откуда кнопка, признавайся хакер', kb_params=main_kb_head)
        else:
            var_message(user_id, 'Ты не староста, откуда кнопка😕', kb_params=main_kb_student)
    else:
        var_message(user_id, 'Ты не авторизован', kb_params=before_login_kb)


def change_user_passwd(user_id, msg):
    msg = [m.strip() for m in msg.split('\n')[1:]]
    login, old_password, new_password = None, None, None
    if len(msg) == 3:
        for m in msg:
            if m.startswith('Логин - {') and m.endswith('}'):
                login = m[9:-1]
            elif m.startswith('Старый пароль - {') and m.endswith('}'):
                old_password = m[17:-1]
            elif m.startswith('Новый пароль - {') and m.endswith('}'):
                new_password = m[16:-1]
        if login and old_password and new_password:
            cur.execute('SELECT * FROM reports_student WHERE vk_id = %s', (user_id, ))
            user_info = cur.fetchone()
            if user_info:
                kb = main_kb_head if user_info['is_head'] or user_info['is_head_assistant'] else main_kb_student
                if len(new_password) < 8:
                    var_message(user_id, 'Новый пароль слишком короткий (минимум 8 символов)', kb_params=kb)
                else:
                    if user_info['login'] == login and user_info['password'] == old_password:
                        cur.execute('UPDATE reports_student SET password = %s WHERE login = %s', (new_password, login))
                        var_message(user_id, 'Пароль успешно изменен', kb_params=kb)
                    else:
                        var_message(user_id, 'Неправильный логин или пароль', kb_params=kb)
            else:
                var_message(user_id, 'Ты же не авторизован, как ты вызвал эту команду', kb_params=before_login_kb)
        else:
            var_message(user_id, change_user_passwd_instruction1)
            if get_user_by_vk_id(user_id, get_head_bool=True):
                var_message(user_id, change_user_passwd_instruction2, kb_params=main_kb_head)
            else:
                var_message(user_id, change_user_passwd_instruction2, kb_params=main_kb_student)
    else:
        var_message(user_id, change_user_passwd_instruction1)
        if get_user_by_vk_id(user_id, get_head_bool=True):
            var_message(user_id, change_user_passwd_instruction2, kb_params=main_kb_head)
        else:
            var_message(user_id, change_user_passwd_instruction2, kb_params=main_kb_student)


def get_group_members_passwd(user_id, head_info):
    cur.execute(
        '''SELECT * FROM reports_student
        WHERE faculty_id = %s AND course_n = %s AND group_n = %s ORDER BY id''',
        (head_info['faculty_id'], head_info['course_n'], head_info['group_n'])
    )
    students_in_group = cur.fetchall()
    if students_in_group:
        password_list = []
        for stud in students_in_group:
            pos = stud["position_in_group"]
            fio = f'{stud["surname"]} {stud["name"]} {stud["f_name"]}'
            login_password = f'{stud["login"]}\n{stud["password"]}'
            password_list.append(f'{pos}) {fio}\n{login_password}\n')
        var_message(user_id, 'Пароли твоей группы:\n' + '\n'.join(password_list), kb_params=main_kb_head)
    else:
        var_message(user_id, 'Не могу найти твоих одногруппников\nОбратись к [id39398636|Саше]')


def lectures_btn_payload_parse(user_id, payload_list):
    stud_info = get_user_by_vk_id(user_id)
    if not stud_info:
        var_message(user_id, 'Похоже ты не авторизован', kb_params=before_login_kb)
        return
    if len(payload_list) == 1:
        num = 1
        lectures_settings_kb = {}
        if stud_info['is_head_of_head']:
            lectures_settings_kb[num] = (['Кто добавляет ссылки', 'primary', '{"button": "lectures_who-can"}'],)
            lectures_settings_kb[num+1] = (['+установщик ссылок', 'primary', '{"button": "lectures_who-add"}'], )
            lectures_settings_kb[num+2] = (['-установщик ссылок', 'primary', '{"button": "lectures_who-del"}'],)
            num += 3
        if stud_info['get_lec_urls_automatically']:
            lectures_settings_kb[num] = (['Не напоминать о лекциях', 'negative', '{"button": "lectures_auto-no"}'], )
        else:
            lectures_settings_kb[num] = (['Напоминать о лекциях', 'positive', '{"button": "lectures_auto-yes"}'], )
        lectures_settings_kb[num+1] = (cancel_btn, )
        var_message(user_id, '...', lectures_settings_kb)
    elif len(payload_list) == 2:
        p_pars = payload_list[1].split('-')
        if p_pars[0] == 'who':
            if stud_info['is_head_of_head']:
                if p_pars[1] == 'can':
                    who_can_add_lectures_url_can_show_list(user_id, stud_info)
                elif p_pars[1] == 'add':
                    payload_pars_len = len(p_pars)
                    if payload_pars_len == 2:
                        who_can_add_lectures_url_to_add_show_groups_ranges(user_id, stud_info)
                    elif payload_pars_len == 3:
                        if '|' in p_pars[2]:
                            who_can_add_lectures_url_to_add_show_groups(user_id, stud_info, p_pars[2])
                        else:
                            who_can_add_lectures_url_to_add_show_studs(user_id, stud_info, int(p_pars[2]))
                    elif payload_pars_len == 4:
                        who_can_add_lectures_url_to_add_stud(user_id, stud_info, int(p_pars[3]))
                    elif payload_pars_len == 5:
                        who_can_add_lectures_url_to_add_stream_in_stud(user_id, int(p_pars[3]), int(p_pars[4]))
                elif p_pars[1] == 'del':
                    payload_pars_len = len(p_pars)
                    if payload_pars_len == 2:
                        who_can_add_lectures_url_to_del_show_groups_ranges(user_id, stud_info)
                    elif payload_pars_len == 3:
                        if '|' in p_pars[2]:
                            who_can_add_lectures_url_to_del_show_groups(user_id, stud_info, p_pars[2])
                        else:
                            who_can_add_lectures_url_to_del_show_studs(user_id, stud_info, int(p_pars[2]))
                    elif payload_pars_len == 4:
                        who_can_add_lectures_url_to_del_stud(user_id, int(p_pars[3]))
                    elif payload_pars_len == 5:
                        who_can_add_lectures_url_to_del_stream_in_stud(user_id, int(p_pars[3]), int(p_pars[4]))
            else:
                var_message(user_id, 'Неть')
        elif p_pars[0] == 'auto':
            y_or_n = True if p_pars[1] == 'yes' else False
            set_get_lectures_url_automatically(user_id, stud_info, y_or_n)


def who_can_add_lectures_url_can_show_list(user_id, stud_info):
    faculty_id = stud_info['faculty_id']
    course_n = stud_info['course_n']

    cur.execute(
        '''SELECT * FROM reports_student
        WHERE faculty_id = %s AND course_n = %s AND can_add_lecture_url != %s''',
        (faculty_id, course_n, '')
    )
    studs = cur.fetchall()
    if not studs:
        var_message(user_id, 'Никто не может')
        return

    streams = {}
    for stud in studs:
        stud_streams = (int(x) for x in stud['can_add_lecture_url'].split(','))
        for s in stud_streams:
            if not streams.get(s):
                streams[s] = []
            streams[s].append(f'{stud["surname"]} {stud["name"]} - {stud["group_n"]} группа')

    reply_msg = ''
    for s, studs_list in streams.items():
        reply_msg += f'{s} поток:\n'
        for stud in studs_list:
            reply_msg += stud + '\n'
        reply_msg += '\n'
    var_message(user_id, reply_msg)


def who_can_add_lectures_url_to_add_show_groups_ranges(user_id, stud_info):
    faculty_id = stud_info['faculty_id']
    course_n = stud_info['course_n']

    cur.execute(
        'SELECT group_n FROM reports_student WHERE faculty_id = %s AND course_n = %s GROUP BY group_n ORDER BY group_n',
        (faculty_id, course_n)
    )
    groups = [dict(x)['group_n'] for x in cur.fetchall()]
    if len(groups) > 15:
        groups_div = {}
        for group_n in groups:
            group_div = group_n // 10
            if not groups_div.get(group_div):
                groups_div[group_div] = []
            groups_div[group_div].append(group_n)

        num = 1
        groups_ranges_kb = {num: []}
        max_btn_in_line = 3 if len(groups_div.values()) > 16 else 2
        for groups_n in groups_div.values():
            min_gr = min(groups_n)
            max_gr = max(groups_n)
            groups_ranges_kb[num].append(
                (f'{min_gr}-{max_gr} группы', 'primary', f'{{"button": "lectures_who-add-{min_gr}|{max_gr}"}}')
            )
            if len(groups_ranges_kb[num]) == max_btn_in_line:
                num += 1
                groups_ranges_kb[num] = []
        groups_ranges_kb[num].append(cancel_btn)
        var_message(user_id, '...', kb_params=groups_ranges_kb)
    else:
        who_can_add_lectures_url_to_add_show_groups(user_id, stud_info, groups_range=None, groups=groups)


def who_can_add_lectures_url_to_del_show_groups_ranges(user_id, stud_info):
    faculty_id = stud_info['faculty_id']
    course_n = stud_info['course_n']

    cur.execute(
        '''SELECT
            group_n
        FROM reports_student
        WHERE
            faculty_id = %s AND
            course_n = %s AND
            can_add_lecture_url != %s
        GROUP BY group_n
        ORDER BY group_n''',
        (faculty_id, course_n, '')
    )
    groups = [dict(x)['group_n'] for x in cur.fetchall()]
    if len(groups) > 15:
        groups_div = {}
        for group_n in groups:
            group_div = group_n // 10
            if not groups_div.get(group_div):
                groups_div[group_div] = []
            groups_div[group_div].append(group_n)

        num = 1
        groups_ranges_kb = {num: []}
        max_btn_in_line = 3 if len(groups_div.values()) > 16 else 2
        for groups_n in groups_div.values():
            min_gr = min(groups_n)
            max_gr = max(groups_n)
            groups_ranges_kb[num].append(
                (f'{min_gr}-{max_gr} группы', 'primary', f'{{"button": "lectures_who-del-{min_gr}|{max_gr}"}}')
            )
            if len(groups_ranges_kb[num]) == max_btn_in_line:
                num += 1
                groups_ranges_kb[num] = []
        groups_ranges_kb[num].append(cancel_btn)
        var_message(user_id, '...', kb_params=groups_ranges_kb)
    else:
        who_can_add_lectures_url_to_del_show_groups(user_id, stud_info, groups_range=None, groups=groups)


def who_can_add_lectures_url_to_add_show_groups(user_id, stud_info, groups_range=None, groups=None):
    if groups_range:
        min_gr = int(groups_range.split('|')[0])
        max_gr = int(groups_range.split('|')[1])

        faculty_id = stud_info['faculty_id']
        course_n = stud_info['course_n']

        cur.execute(
            '''SELECT group_n FROM reports_student
            WHERE faculty_id = %s AND course_n = %s AND group_n BETWEEN %s AND %s GROUP BY group_n ORDER BY group_n''',
            (faculty_id, course_n, min_gr, max_gr)
        )
        groups = [dict(x)['group_n'] for x in cur.fetchall()]

    num = 1
    groups_kb = {num: []}
    max_btn_in_line = 3 if len(groups) > 16 else 2
    for group_n in groups:
        groups_kb[num].append((f'{group_n} группа', 'primary', f'{{"button": "lectures_who-add-{group_n}"}}'))
        if len(groups_kb[num]) == max_btn_in_line:
            num += 1
            groups_kb[num] = []
    groups_kb[num].append(cancel_btn)
    var_message(user_id, '...', kb_params=groups_kb)


def who_can_add_lectures_url_to_del_show_groups(user_id, stud_info, groups_range=None, groups=None):
    if groups_range:
        min_gr = int(groups_range.split('|')[0])
        max_gr = int(groups_range.split('|')[1])

        faculty_id = stud_info['faculty_id']
        course_n = stud_info['course_n']

        cur.execute(
            '''SELECT group_n FROM reports_student
            WHERE
                faculty_id = %s AND
                course_n = %s AND
                group_n BETWEEN %s AND %s AND
                can_add_lecture_url != %s
            GROUP BY group_n
            ORDER BY group_n''',
            (faculty_id, course_n, min_gr, max_gr, '')
        )
        groups = [dict(x)['group_n'] for x in cur.fetchall()]

    num = 1
    groups_kb = {num: []}
    max_btn_in_line = 3 if len(groups) > 16 else 2
    for group_n in groups:
        groups_kb[num].append((f'{group_n} группа', 'primary', f'{{"button": "lectures_who-del-{group_n}"}}'))
        if len(groups_kb[num]) == max_btn_in_line:
            num += 1
            groups_kb[num] = []
    groups_kb[num].append(cancel_btn)
    var_message(user_id, '...', kb_params=groups_kb)


def who_can_add_lectures_url_to_add_show_studs(user_id, stud_info, group_n):
    faculty_id = stud_info['faculty_id']
    course_n = stud_info['course_n']

    cur.execute(
        '''SELECT
            id AS id,
            position_in_group AS pos,
            surname AS surname,
            is_head AS is_head,
            is_head_assistant AS is_head_assistant
        FROM reports_student
        WHERE
            faculty_id = %s AND
            course_n = %s AND
            group_n = %s AND
            is_fired = %s
        ORDER BY position_in_group''',
        (faculty_id, course_n, group_n, False)
    )
    studs = cur.fetchall()
    num = 1
    studs_kb = {num: []}
    max_btn_in_line = 3 if len(studs) > 16 else 2
    for stud in studs:
        name = f'{stud["pos"]}. {stud["surname"]}'
        name += '(ст)' if stud['is_head'] else ''
        name += '(пом)' if stud['is_head_assistant'] else ''
        studs_kb[num].append((name, 'primary', f'{{"button": "lectures_who-add-{group_n}-{stud["id"]}"}}'))
        if len(studs_kb[num]) == max_btn_in_line:
            num += 1
            studs_kb[num] = []
    studs_kb[num].append(cancel_btn)
    var_message(user_id, '...', kb_params=studs_kb)


def who_can_add_lectures_url_to_del_show_studs(user_id, stud_info, group_n):
    faculty_id = stud_info['faculty_id']
    course_n = stud_info['course_n']

    cur.execute(
        '''SELECT
            id AS id,
            position_in_group AS pos,
            surname AS surname,
            is_head AS is_head,
            is_head_assistant AS is_head_assistant
        FROM reports_student
        WHERE
            faculty_id = %s AND
            course_n = %s AND
            group_n = %s AND
            can_add_lecture_url != %s AND
            is_fired = %s
        ORDER BY position_in_group''',
        (faculty_id, course_n, group_n, '', False)
    )
    studs = cur.fetchall()
    num = 1
    studs_kb = {num: []}
    max_btn_in_line = 3 if len(studs) > 16 else 2
    for stud in studs:
        name = f'{stud["pos"]}. {stud["surname"]}'
        name += '(ст)' if stud['is_head'] else ''
        name += '(пом)' if stud['is_head_assistant'] else ''
        studs_kb[num].append((name, 'primary', f'{{"button": "lectures_who-del-{group_n}-{stud["id"]}"}}'))
        if len(studs_kb[num]) == max_btn_in_line:
            num += 1
            studs_kb[num] = []
    studs_kb[num].append(cancel_btn)
    var_message(user_id, '...', kb_params=studs_kb)


def who_can_add_lectures_url_to_add_stud(user_id, stud_info, stud_id):
    faculty_id = stud_info['faculty_id']
    course_n = stud_info['course_n']

    cur.execute('SELECT * FROM reports_student WHERE id = %s', (stud_id, ))
    stud = cur.fetchone()
    if not stud:
        var_message(user_id, 'Такого студента нет')
        return

    cur.execute(
        '''SELECT stream_n FROM reports_student
        WHERE faculty_id = %s AND course_n = %s GROUP BY stream_n ORDER BY stream_n''',
        (faculty_id, course_n)
    )
    streams = [dict(x)['stream_n'] for x in cur.fetchall()]

    if stud['can_add_lecture_url'] != '':
        streams_stud = [int(x) for x in stud['can_add_lecture_url'].split(',')]
        cant_add_s = []
        for s in streams:
            if s not in streams_stud:
                cant_add_s.append(s)
        streams_stud_str = [str(x) for x in streams_stud]
        reply_msg = f'{stud["name"]} {stud["surname"]} может добавлять лекции для потоков: {",".join(streams_stud_str)}'
        if not cant_add_s:
            var_message(user_id, reply_msg)
            return
    else:
        reply_msg = f'{stud["name"]} {stud["surname"]} пока не может добавлять лекции'
        cant_add_s = streams
    num = 1
    streams_kb = {num: []}
    max_btn_in_line = 3 if len(cant_add_s) > 16 else 2
    for s in cant_add_s:
        streams_kb[num].append(
            (f'{s} поток', 'primary', f'{{"button": "lectures_who-add-{stud["group_n"]}-{stud["id"]}-{s}"}}')
        )
        if len(streams_kb[num]) == max_btn_in_line:
            num += 1
            streams_kb[num] = []
    streams_kb[num].append(cancel_btn)
    var_message(user_id, reply_msg, kb_params=streams_kb)


def who_can_add_lectures_url_to_del_stud(user_id, stud_id):

    cur.execute('SELECT * FROM reports_student WHERE id = %s', (stud_id,))
    stud = cur.fetchone()
    if not stud:
        var_message(user_id, 'Такого студента нет')
        return

    if stud['can_add_lecture_url'] != '':
        streams_stud = [x for x in stud['can_add_lecture_url'].split(',')]
        reply_msg = f'{stud["name"]} {stud["surname"]} может добавлять лекции для потоков: {",".join(streams_stud)}'
    else:
        var_message(user_id, f'{stud["name"]} {stud["surname"]} и так не может добавлять лекции')
        return
    num = 1
    streams_kb = {num: []}
    max_btn_in_line = 3 if len(streams_stud) > 16 else 2
    for s in streams_stud:
        streams_kb[num].append(
            (f'{s} поток', 'primary', f'{{"button": "lectures_who-del-{stud["group_n"]}-{stud["id"]}-{s}"}}')
        )
        if len(streams_kb[num]) == max_btn_in_line:
            num += 1
            streams_kb[num] = []
    streams_kb[num].append(cancel_btn)
    var_message(user_id, reply_msg, kb_params=streams_kb)


def who_can_add_lectures_url_to_add_stream_in_stud(user_id, stud_id, str_to_add):
    cur.execute('SELECT * FROM reports_student WHERE id = %s', (stud_id,))
    stud = cur.fetchone()
    if not stud:
        var_message(user_id, 'Такого студента нет')
        return

    if stud['can_add_lecture_url'] != '':
        streams = [int(x) for x in stud['can_add_lecture_url'].split(',')]
        if str_to_add in streams:
            var_message(user_id, f'{stud["name"]} {stud["surname"]} и так мог добавлять ссылки для {str_to_add} потока')
            return
        streams.append(str_to_add)
        streams.sort()
        streams = ','.join([str(x) for x in streams])
    else:
        streams = str(str_to_add)
    cur.execute(
        '''UPDATE reports_student SET can_add_lecture_url = %s WHERE id = %s''',
        (streams, stud_id)
    )
    var_message(user_id,
                f'{stud["name"]} {stud["surname"]} теперь может добавлять ссылки на лекции для потоков: {streams}')


def who_can_add_lectures_url_to_del_stream_in_stud(user_id, stud_id, str_to_add):
    cur.execute('SELECT * FROM reports_student WHERE id = %s', (stud_id,))
    stud = cur.fetchone()
    if not stud:
        var_message(user_id, 'Такого студента нет')
        return

    if stud['can_add_lecture_url'] != '':
        streams = [int(x) for x in stud['can_add_lecture_url'].split(',')]
        if str_to_add not in streams:
            var_message(user_id,
                        f'{stud["name"]} {stud["surname"]} и не так мог добавлять ссылки для {str_to_add} потока')
            return
        streams.remove(str_to_add)
        streams.sort()
        streams = ','.join([str(x) for x in streams])
    else:
        var_message(user_id, f'{stud["name"]} {stud["surname"]} и так не может добавлять лекции')
        return
    cur.execute(
        '''UPDATE reports_student SET can_add_lecture_url = %s WHERE id = %s''',
        (streams, stud_id)
    )
    if streams:
        var_message(user_id,
                    f'{stud["name"]} {stud["surname"]} теперь может добавлять ссылки на лекции для потоков: {streams}')
    else:
        var_message(user_id, f'{stud["name"]} {stud["surname"]} теперь не может добавлять ссылки на лекции')


def set_get_lectures_url_automatically(user_id, stud_info, set_yes: bool):
    if stud_info['get_lec_urls_automatically'] == set_yes:
        var_message(user_id, f'Ты и так {"не " if not set_yes else ""}получал ссылки автоматически')
    else:
        cur.execute(
            '''UPDATE reports_student SET get_lec_urls_automatically = %s WHERE id = %s''',
            (set_yes, stud_info['id'])
        )
        var_message(user_id, f'Теперь ты {"не " if not set_yes else ""}получаешь ссылки автоматически',
                    main_kb_head if stud_info['is_head'] or stud_info['is_head_assistant'] else main_kb_student)
