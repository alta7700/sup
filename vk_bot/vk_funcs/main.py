import re

from .work_with_users import *
from .load_reports import *
from .show_attendahce import *
from .work_outs import *
from .pr_lk_schedule import *
from .head_of_head_btns import *
from .badge import send_badge_if_exists


def convert_to_pars(pars: str):
    pars_list = pars.split('?')[1:]
    attrs = {}
    for p in pars_list:
        if p:
            pair = p.split('-')
            key = pair[0]
            try:
                value = int(pair[1])
            except ValueError:
                value = pair[1]
            attrs[key] = value
    return attrs


def message_from_user(message, recursive=False):
    user_id = message['from_id']
    msg = message['text']
    query = msg.split('\n')[0].lower().strip()
    user_info = get_user_by_vk_id(user_id)
    if user_info:
        user_info = dict(user_info)
        if query.startswith('рапорт'):
            if query == 'рапорт':
                if msg.count('\n') == 0:
                    if len(message['attachments']) == 0:
                        var_message(user_id, 'Чтобы получить шаблон, напиши:\nРапорт таблицей\nили\nРапорт сообщением')
                    elif len(message['attachments']) == 1:
                        attach = message['attachments'][0]
                        if attach['type'] == 'doc':
                            parse_report_excel_pattern(user_id, attach['doc'])
                        else:
                            var_message(user_id, 'Чтобы я обработал рапорт, отправь таблицу')
                    else:
                        var_message(user_id, 'Больше одного вложения вложения для меня слишком сложно')
                else:
                    parse_report_message(user_id, msg)
            elif query == 'рапорт изменить':
                parse_report_change_message(user_id, msg)
            elif query == 'рапорт таблицей':
                send_report_excel_pattern(user_id)
            elif query == 'рапорт сообщением':
                send_report_message_pattern(user_id)
            else:
                var_message(user_id, 'Чтобы получить шаблон, напиши:\nРапорт таблицей\nили\nРапорт сообщением')

        elif query.startswith('ссылка'):
            if query == 'ссылка добавить':
                parse_lecture_url_add_or_change_message(user_id, user_info, msg, add=True, recursive=recursive)
            elif query == 'ссылка изменить':
                parse_lecture_url_add_or_change_message(user_id, user_info, msg, add=False, recursive=recursive)

        elif query.startswith('бейдж'):
            send_badge_if_exists(user_id, user_info)

        elif query.startswith('stud-'):
            if user_info['login'] != msg.split('\n')[0].strip():
                r_msg = f'Ты уже авторизован(а) под другим логином:\n{user_info["login"]}'
            else:
                r_msg = f'{user_info["surname"]} {user_info["name"]}, ты уже авторизован(а)'
            if user_info['is_head'] or user_info['is_head_assistant']:
                kb = main_kb_head
            else:
                kb = main_kb_student
            var_message(user_id, r_msg, kb)

        elif query.startswith('список') and user_info['is_head_of_head']:
            if query == 'список курса':
                send_stud_list(user_info)
            elif re.match(r'^список \d+ поток', query):
                send_stud_list(user_info, stream_n=int(query.split()[1]))
            elif re.match(r'^список \d+ групп', query):
                send_stud_list(user_info, group_n=int(query.split()[1]))
            else:
                var_message(
                    user_id,
                    'Напиши что-то из этого:\n'
                    'Cписок курса\n'
                    'Список 1 потока'
                    'Список 1 группы'
                )

        elif query == 'выход':
            log_out(user_id)
        elif query == 'сменить пароль':
            change_user_passwd(user_id, msg)

        elif message.get('reply_message') or ((not message.get('fwd_messages') is None) and message['fwd_messages'] != []):
            if user_info['can_add_lecture_url']:
                if message.get('reply_message'):
                    if message['reply_message']['from_id'] != -VK_INT_GROUP_ID:
                        var_message(user_id, 'Это как')
                        return
                    lecture_pattern = message['reply_message']['text']
                    url = msg
                else:
                    if len(message['fwd_messages']) > 1:
                        var_message(user_id, 'Слишком много сообщений внутри, а я один\nДавай один на один')
                        return
                    else:
                        fwd = message['fwd_messages'][0]
                        if fwd['from_id'] != -VK_INT_GROUP_ID:
                            var_message(user_id, 'Это не моё сообщение, так не пойдет')
                            return
                        lecture_pattern = fwd['text']
                        url = msg
                if lecture_pattern.startswith('Ссылка ДОБАВИТЬ') or lecture_pattern.startswith('Ссылка ИЗМЕНИТЬ'):
                    if lecture_pattern.startswith('Ссылка ДОБАВИТЬ'):
                        lecture_pattern = lecture_pattern.strip().rstrip('}')
                        new_query = f'{lecture_pattern}{url}}}'
                    else:
                        lecture_pattern = '\n'.join(lecture_pattern.split('\n')[:4])
                        new_query = f'{lecture_pattern}\n{{{url}}}'
                    message['text'] = new_query
                    message['reply_message'] = {}
                    message['fwd_messages'] = []
                    message_from_user(message, recursive=True)
        elif query == '...':
            var_message(user_id, 'Хрюшка-повторюшка')
    else:
        if query.startswith('stud-'):
            log_in(user_id, msg)
        else:
            var_message(user_id, 'Для начала нужно авторизоваться', kb_params=before_login_kb)


def do_kb_act(user_id, payload: str, msg: str):
    if payload.startswith('{"button'):
        payload_list = payload[11:-2].split('_')
        if payload_list[0] == 'report':
            if payload_list[1] == 'category':
                var_message(user_id, '...', kb_params=category_reports_kb)
            elif payload_list[1] == 'send':
                if payload_list[2] == 'message':
                    send_report_message_pattern(user_id)
                elif payload_list[2] == 'excel':
                    send_report_excel_pattern(user_id)
            elif payload_list[1] == 'change':
                if len(payload_list) == 2:
                    var_message(user_id, '...', kb_params=change_report_kb)
                else:
                    is_pr = True if payload_list[2].split('-')[0] == 'practical' else False
                    if payload_list[2].count('-') == 0:
                        if is_pr:
                            show_subjects_to_change_report(user_id, '{{"button": "report_change_practical-{}"}}', is_pr)
                        else:
                            show_subjects_to_change_report(user_id, '{{"button": "report_change_lecture-{}"}}', is_pr)
                    else:
                        if payload_list[2].count('-') == 1:
                            show_subject_dates_to_change_report(user_id, payload, is_pr)
                        elif payload_list[2].count('-') == 2:
                            send_report_message_pattern_to_change_raport(user_id, payload)
            elif payload_list[1] == 'instructions':
                var_message(user_id, how_to_report_instruction + right_attandance_tags)

        elif payload_list[0] == 'attendance':
            stud_info = get_user_by_vk_id(user_id)
            if not stud_info:
                var_message(user_id, 'Ты не авторизован', kb_params=before_login_kb)
            elif payload_list[1] == 'category':
                if stud_info['is_head_of_head']:
                    return var_message(user_id, '...', kb_params={0: (attendance_complete, ), **attendance_pr_or_lk_kb})
                var_message(user_id, '...', kb_params=attendance_pr_or_lk_kb)
            elif payload_list[1] == 'show':
                if stud_info:
                    if payload_list[2] == 'all':
                        if stud_info['is_head'] or stud_info['is_head_assistant']:
                            show_all_group_reports(user_id, stud_info)
                        else:
                            var_message(user_id, 'Эта кнопка для старост, выбирай из тех, что пониже')
                    else:
                        is_practical = True if payload_list[2].split('-')[0] == 'practical' else False
                        if payload_list[2].count('-') == 0:
                            show_reported_subjects_to_show_attendance(user_id, stud_info, is_practical)
                        elif payload_list[2].count('-') == 1:
                            show_attendance_stud_choice_btn(user_id, stud_info, payload)
                        elif payload_list[2].count('-') == 2:
                            show_attendance(user_id, stud_info, payload, is_practical)
            elif payload_list[1] == 'complete':
                if not stud_info['is_head_of_head']:
                    return var_message(user_id, 'Откуда кнопка?')
                last_reports(stud_info)

        elif payload_list[0] == 'work' and payload_list[1] == 'out':
            if payload == '{"button":"work_out"}':
                var_message(user_id, '...', kb_params=work_out_kb)
            else:
                work_out_payload_parsing(user_id, payload)

        elif payload_list[0] == 'schedule':
            stud_info = get_user_by_vk_id(user_id)
            if not stud_info:
                var_message(user_id, 'Ты не авторизован', kb_params=before_login_kb)
                return

            if payload_list[1] == 'category':
                if stud_info['can_add_lecture_url']:
                    var_message(user_id, '...', kb_params=schedule_kb_add)
                else:
                    if stud_info['is_head'] or stud_info['is_head_assistant']:
                        kb = {0: (send_lecture, ), **schedule_kb}
                    else:
                        kb = schedule_kb
                    var_message(user_id, '...', kb_params=kb)
            elif payload_list[1] == 'lecture':
                if payload_list[2] == 'url':
                    if stud_info['can_add_lecture_url']:
                        if payload_list[3].startswith('add') or payload_list[3].startswith('change'):
                            lecture_url_add_or_change_payload_processing(user_id, stud_info, payload_list[3])
                    else:
                        var_message(user_id, 'Неть', kb_params=schedule_kb)
                elif payload_list[2] == 'get':
                    show_lectures_for_two_more_days(user_id, stud_info)
                elif payload_list[2] == 'attendance':
                    if stud_info['can_add_lecture_url']:
                        pars = convert_to_pars(payload_list[3])
                        show_stream_lecture_attendance(stud_info, **pars)
                elif payload_list[2] == 'send':
                    send_lecture_by_query(stud_info, **convert_to_pars(payload_list[3]))

            # elif payload_list[1] == 'pair':
            #     if payload_list[2] == 'comment':
            #         if len(payload_list) == 3:
            #             show_subject_to_add_pair_comment(user_id, stud_info)
            #         else:
            #             comment_pars = payload_list[3].split('-')
            #             if len(comment_pars) == 1:
            #                 show_dates_to_add_pair_comment()
            #             else:
            #                 send_comment_add_pattern()

            elif payload_list[1] == 'show':
                if payload_list[2].startswith('week'):
                    show_week_schedule(user_id, stud_info, payload_list[2])

        elif payload_list[0] == 'get':
            stud_info = get_user_by_vk_id(user_id)
            if stud_info:
                if stud_info['is_head'] or stud_info['is_head_assistant']:
                    if payload_list[1] == 'settings' and payload_list[2] == 'kb':
                        var_message(user_id, '...', kb_params=settings_kb_head)
                    elif payload_list[1] == 'gr' and payload_list[2] == 'passwd':
                        get_group_members_passwd(user_id, stud_info)
                else:
                    if payload_list[1] == 'settings' and payload_list[2] == 'kb':
                        var_message(user_id, '...', kb_params=settings_kb_student)
                    elif payload_list[1] == 'gr' and payload_list[2] == 'passwd':
                        var_message(user_id, 'Не покажу, ты не староста?', kb_params=main_kb_student)
            else:
                var_message(user_id, 'Ты не авторизован', kb_params=before_login_kb)

        elif payload_list[0] == 'cancel' and payload_list[1] == 'kb':
            stud_info = get_user_by_vk_id(user_id)
            if stud_info:
                if stud_info['is_head'] or stud_info['is_head_assistant']:
                    var_message(user_id, '...', kb_params=main_kb_head)
                else:
                    var_message(user_id, '...', kb_params=main_kb_student)
            else:
                var_message(user_id, 'Ты не авторизован', kb_params=before_login_kb)

        elif payload_list[0] == 'roles':
            if len(payload_list) == 1:
                var_message(user_id, '...', kb_params=roles_kb)
            elif payload_list[1] == 'unlock':
                if payload_list[2] == 'groupmate':
                    get_locked_groupmates_kb(user_id)
                elif payload_list[2] == 'one':
                    unlock_groupmate(user_id, msg)
                elif payload_list[2] == 'all':
                    unlock_groupmate(user_id, msg, unlock_all=True)
            elif payload_list[1] == 'lock':
                if payload_list[2] == 'groupmate':
                    get_unlocked_groupmates_kb(user_id)
                elif payload_list[2] == 'one':
                    lock_groupmate(user_id, msg)
                elif payload_list[2] == 'all':
                    lock_groupmate(user_id, msg, lock_all=True)
            elif payload_list[1] == 'assistant':
                if payload_list[2] == 'choose':
                    get_groupmates_to_choose_assistant(user_id)
                elif payload_list[2] == 'make':
                    make_assistant(user_id, msg)
                elif payload_list[2] == 'zero':
                    make_assistant(user_id, msg, zero_only=True)

        elif payload_list[0] == 'lectures':
            lectures_btn_payload_parse(user_id, payload_list)

        elif payload_list[0] == 'change' and payload_list[1] == 'passwd':
            var_message(user_id, change_user_passwd_instruction1)
            if get_user_by_vk_id(user_id, get_head_bool=True):
                var_message(user_id, change_user_passwd_instruction2, kb_params=main_kb_head)
            else:
                var_message(user_id, change_user_passwd_instruction2, kb_params=main_kb_student)

        elif payload_list[0] == 'log':
            if payload_list[1] == 'in':
                var_message(user_id, log_in_btn_instruction)
            elif payload_list[1] == 'out':
                log_out(user_id)
            elif payload_list[1].startswith('off'):
                switch_off_groupmate(user_id, payload_list[1])

    elif payload == '{"command":"start"}':
        var_message(user_id, 'Привет, для начала работы со мной тебе нужно авторизоваться', kb_params=before_login_kb)


def message_new(message):
    if message.get('payload'):
        do_kb_act(message['from_id'], message['payload'], message['text'])
    else:
        message_from_user(message)
