import time
from ..config import *


cur.execute(
    'SELECT * FROM reports_student WHERE is_head_of_head = %s AND vk_id IS NOT %s AND is_fired = %s '
    'ORDER BY faculty_id, course_n, group_n',
    (True, None, False)
)
course_heads = cur.fetchall()

if course_heads:
    for hoh in course_heads:
        faculty_id = hoh['faculty_id']
        course_n = hoh['course_n']
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
                last_report_msg += f'\n{h["group_n"]}гр - {h["surname"]} - '\
                                   f'{last_report["dt"].strftime("%d.%m.%Y") if last_report["dt"] else "Нет ни одного"}'

        unauth_heads_msg = f'Неавторизованные старосты:{"".join(unauth_heads_msg)}\n\n' if unauth_heads_msg else ''
        var_message(hoh['vk_id'], f'{unauth_heads_msg}{last_report_msg}')
        print(f'Отправил старосте {faculty_id}ф {course_n}к')
        time.sleep(0.4)

# cur.execute('SELECT * FROM reports_student WHERE is_head = %s AND vk_id IS NOT %s', (True, None))
# heads = cur.fetchall()
# if heads:
#     for h in heads:
#         cur.execute(
#             'SELECT * FROM reports_student '
#             'WHERE faculty_id = %s AND course_n = %s AND group_n = %s AND vk_id IS %s AND is_fired = %s'
#             'ORDER BY surname, name',
#             (h['faculty_id'], h['course_n'], h['group_n'], None, False)
#         )
#         unauth_studs = cur.fetchall()
#         if unauth_studs:
#             unauth_studs_msg = 'В твоей группе не авторизовались:'
#             for stud in unauth_studs:
#                 unauth_studs_msg += f'\n{stud["surname"]} {stud["name"]}'
#             var_message(h['vk_id'], unauth_studs_msg)
#             print(f'Отправил старосте {h["faculty_id"]}ф {h["course_n"]}к {h["group_n"]}гр')
#             time.sleep(0.4)
