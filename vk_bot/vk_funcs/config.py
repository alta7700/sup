import json
import zipfile
import openpyxl.utils.exceptions
import vk_api
import requests
import os
import psycopg2
from psycopg2.extras import DictCursor
from openpyxl import load_workbook
from ReportsDjango.settings import VK_GROUP_TK, VK_USER_TK, VK_INT_GROUP_ID, VK_APP_ID, VK_API_VERSION, VK_GROUP_OWNER_ID
from vk_api.keyboard import VkKeyboard
from ReportsDjango.settings import DATABASES


db_settings = {key.lower(): value for key, value in DATABASES['default'].items()}

db_settings = {
    'database': db_settings['name'],
    'user': db_settings['user'],
    'password': db_settings['password'],
    'host': db_settings['host'],
    'port': db_settings['port'],
}

connection = psycopg2.connect(**db_settings)

cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
connection.autocommit = True

gr_session = vk_api.VkApi(token=VK_GROUP_TK, app_id=VK_APP_ID, api_version=VK_API_VERSION)
user_session = vk_api.VkApi(token=VK_USER_TK, app_id=VK_APP_ID, api_version=VK_API_VERSION)


def payload_constructor(pattern: str, params: dict) -> str:
    params_str = '?'.join([f'{key}-{value}' for key, value in params.items() if value is not None])
    return f'{{"button":"{pattern}_?{params_str}"}}'


def seq_separator(sequence, size):
    return [sequence[offset:offset + size] for offset in range(0, len(sequence), size)]


def var_message(user_id=None, text=None, kb_params=None, kb_onetime=False, attach_list=None, user_ids=None,
                kb_inline=False):
    values = {
        'user_id': user_id,
        'random_id': 0
    }
    if user_ids:
        values = {
            'user_ids': user_ids,
            'random_id': 0
        }
    if text:
        values['message'] = text
    if kb_params:
        keyboard = VkKeyboard(one_time=kb_onetime, inline=kb_inline)
        if len(kb_params.values()) > 1:
            for i, line in enumerate(list(kb_params.values())):
                for btn in line:
                    if len(btn) == 2:
                        keyboard.add_button(btn[0], btn[1])
                    else:
                        keyboard.add_button(btn[0], btn[1], btn[2])
                if i + 1 != len(kb_params.values()):
                    keyboard.add_line()
        else:
            for btn in list(kb_params.values())[0]:
                if len(btn) == 2:
                    keyboard.add_button(btn[0], btn[1])
                else:
                    keyboard.add_button(btn[0], btn[1], btn[2])
        values['keyboard'] = keyboard.get_keyboard()
    if attach_list:
        values['attachment'] = ','.join(attach_list)
    gr_session.method("messages.send", values)


def is_needed_attach(message, needed_attach):
    if message.get('attachments'):
        for attach in message.get('attachments'):
            if attach.get('type') == needed_attach:
                return attach[needed_attach]
    return {}


def download_attach_xlsx(user_id, attach):
    doc = requests.get(attach['url'])
    with open(attach['title'], 'wb') as f:
        f.write(doc.content)

    try:
        book = load_workbook(attach['title'])
        book.close()
        return True
    except zipfile.BadZipfile:
        var_message(user_id, 'Файл EXCEL поврежден, рапорт не обработан')
        return False
    except openpyxl.utils.exceptions.InvalidFileException:
        var_message(user_id, 'Неправильное расширение файла, я обрабатываю только .xlsx')
        return False
    except KeyError:
        var_message(user_id, 'По-моему кто-то просто поменял .zip на .xlsx')
        return False
    except Exception:
        var_message(user_id, 'Расскажи [id39398636|Саше] что ты такого наделал(а)\nЭтого я не предвидел')
        return False


def get_user_by_vk_id(user_id, get_head_bool=False):
    cur.execute('SELECT * FROM reports_student WHERE vk_id = %s', (user_id, ))
    user_info = cur.fetchone()
    if get_head_bool:
        return user_info['is_head'] or user_info['is_head_assistant']
    else:
        return user_info


def get_user_by_stud_id(stud_id):
    cur.execute('SELECT * FROM reports_student WHERE id = %s', (stud_id, ))
    return cur.fetchone()


def get_faculty_by_id(faculty_id):
    cur.execute('SELECT * FROM reports_faculty WHERE id = %s', (faculty_id, ))
    return cur.fetchone()


def get_faculty_id_by_title(faculty_title):
    cur.execute('SELECT * FROM reports_faculty WHERE title = %s', (faculty_title,))
    faculty = cur.fetchone()
    return faculty['id']


def get_curation_id_by_title(faculty_id, course_n, half, subject):
    cur.execute(
        'SELECT * FROM reports_subjects WHERE faculty_id = %s AND course_n = %s AND half = %s AND short_title = %s',
        (faculty_id, course_n, half, subject)
    )
    cur_info = cur.fetchall()
    if cur_info:
        if len(cur_info) == 1:
            return cur_info[0]['id']
        else:
            return None
    else:
        return False


def get_subject_by_id(subject_id):
    cur.execute('SELECT * FROM reports_subject WHERE id = %s', (subject_id,))
    return cur.fetchone()


def get_subject_by_title(faculty_id, course_n, half, subject_title):
    cur.execute(
        'SELECT * FROM reports_subject WHERE faculty_id = %s AND course_n = %s AND half = %s AND short_title = %s',
        (faculty_id, course_n, half, subject_title)
    )
    return cur.fetchone()


def get_subject_by_pair(pair_info):
    if pair_info['is_practical']:
        cur.execute('SELECT * FROM reports_subject WHERE id = %s', (pair_info['subject_id'], ))
        return cur.fetchone()
    else:
        cur.execute(
            'SELECT * FROM reports_subject WHERE id = (SELECT subject_id FROM reports_lecturesschedule WHERE id = %s)',
            (pair_info['lecture_id'], )
        )
        return cur.fetchone()


def doc_sender(user_id: int, file_name, text=None, kb_params=None, kb_onetime=None, remove=True):

    upload_url = gr_session.method("docs.getMessagesUploadServer", {
        'peer_id': user_id
    }).get('upload_url')
    response = requests.post(upload_url, files={'file': open(file_name, 'rb')}).json()
    doc = gr_session.method('docs.save', {
        'file': response.get('file')
    }).get('doc')
    attach = 'doc{}_{}'.format(doc.get('owner_id'), doc.get('id'))

    var_message(user_id, text=text, kb_params=kb_params, kb_onetime=kb_onetime, attach_list=[attach, ])
    if remove:
        os.remove(file_name)


def open_file_with_address(address):
    if os.path.exists(address):
        return address
    address = address.split('/')
    if len(address) < 3:
        if len(address) == 2:
            if not os.path.isdir(address[0]):
                os.mkdir(address[0])
        address_str = '/'.join(address)
    else:
        file = address[-1]
        address_list = address[:-1]
        address_str = f'{address_list[0]}/{address_list[1]}' if address_list[0] == '..' else address_list[0]
        address_list = address_list[2:] if address_list[0] == '..' else address_list[1:]
        if not os.path.isdir(address_str):
            os.mkdir(address_str)
        for directory in address_list:
            address_str += '/' + directory
            if not os.path.isdir(address_str):
                os.mkdir(address_str)
        address_str += '/' + file
    with open(address_str, 'w', encoding='utf-8') as f:
        if address_str.endswith('.json'):
            json.dump({}, f, ensure_ascii=False, indent=4)
    return address_str

