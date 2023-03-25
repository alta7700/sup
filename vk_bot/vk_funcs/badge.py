from typing import Any

from ReportsDjango.settings import BASE_DIR
from .config import doc_sender, var_message

BADGES_DIR = BASE_DIR / 'badges'


def send_badge_if_exists(user_id: int, stud_info: dict[str, Any]) -> None:
    badge = BADGES_DIR / f'{stud_info["id"]}.png'
    if badge.exists():
        doc_sender(user_id, badge, text='Осталось найти зеленую бумагу')
    else:
        var_message(user_id, text='Напиши [id39398636|Саше], пусть добавит твой бейдж')
