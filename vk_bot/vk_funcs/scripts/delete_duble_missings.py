from ..config import *


cur.execute(
    'SELECT pair_id, student_id, count(*), min(id) as min_id '
    'FROM reports_missingpair '
    'GROUP BY pair_id, student_id '
    'HAVING count(*) > 1'
)
min_ids = cur.fetchall()
if min_ids:
    min_ids = [x['min_id'] for x in min_ids]
    cur.execute('DELETE FROM reports_missingpair WHERE id = ANY(%s)', (min_ids, ))
    print('удалил')
else:
    print('нечего')
