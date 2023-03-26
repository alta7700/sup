from typing import Any

from ReportsDjango.settings import BASE_DIR
from .config import doc_sender, multi_doc_sender, var_message, cur

BADGES_DIR = BASE_DIR / 'badges'


def send_badge_if_exists(user_id: int, stud_info: dict[str, Any]) -> None:
    badge = BADGES_DIR / f'{stud_info["id"]}.png'
    if badge.exists():
        doc_sender(user_id, badge, text='Осталось найти зеленую бумагу', remove=False)
    else:
        var_message(user_id, text='Напиши [id39398636|Саше], пусть добавит твой бейдж')


def send_group_badges(user_id: int, head_info: dict[str, Any], surnames: list[str]) -> None:
    cur.execute('''
        SELECT id
        FROM reports_student
        WHERE
            faculty_id = %s AND
            course_n = %s AND
            group_n = %s AND
            lower(surname) = ANY(%s)
        ''', (
            head_info['faculty_id'],
            head_info['course_n'],
            head_info['group_n'],
            surnames
        )
    )
    badges = []
    for stud_info in cur.fetchall():
        badge = BADGES_DIR / f'{stud_info["id"]}.png'
        if badge.exists():
            badges.append(badge)
    if badges:
        multi_doc_sender(user_id, filenames=badges, text='Если чьих-то бейджей нет, напиши [id39398636|Саше]',
                         remove=False)
    else:
        var_message(user_id, text='Напиши [id39398636|Саше], что-то пошло не так')
