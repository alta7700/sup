import os
from datetime import datetime, timedelta

try:
    with open('last_query_time.txt', 'r') as lq:
        last_q = datetime.strptime(lq.read(), '%Y-%m-%d %H:%M:%S')
        if last_q < datetime.now() - timedelta(minutes=3):
            os.system('supervisorctl restart ReportsVKBot')
except FileNotFoundError:
    os.system('supervisorctl restart ReportsVKBot')
