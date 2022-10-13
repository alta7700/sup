from datetime import datetime, time
from ..config import *


COURSE = 3
STREAM = 1
WEEKDAY = {'Понедельник': 1, 'Вторник': 2, 'Среда': 3, 'Четверг': 4, 'Пятница': 5, 'Суббота': 6}
NEW_LEC_TIME = time(hour=12, minute=0)

cur.execute(
    '''SELECT 
        l.id AS id,
        l.course_n AS course_n,
        l.stream_n AS stream_n,
        l.lecture_datetime AS lec_dt,
        s.short_title AS subj,
        l.lecture_url AS url,
        st.surname AS surname
    FROM reports_lecturesschedule AS l
        JOIN reports_subject AS s
            ON s.id=l.subject_id
        LEFT JOIN reports_student AS st
            ON st.id=l.stud_add_lec_id
    WHERE
        l.course_n = %s AND
        l.stream_n = %s AND
        extract(isodow from l.lecture_datetime) = %s
    ORDER BY
        lecture_datetime''',
    (COURSE, STREAM, WEEKDAY['Среда'])
)
lectures = cur.fetchall()
if lectures:
    for lec in lectures:
        new_lec_dt = lec['lec_dt'].replace(hour=NEW_LEC_TIME.hour, minute=NEW_LEC_TIME.minute)
        cur.execute('UPDATE reports_lecturesschedule SET lecture_datetime = %s WHERE id = %s', (new_lec_dt, lec['id']))
        cur.execute(
            'UPDATE reports_pairsschedule SET pr_lk_datetime = %s WHERE lecture_id = %s',
            (new_lec_dt, lec['id'])
        )
else:
    print('Таких лекций нет')
