import yadisk
import os
from datetime import datetime

ya = yadisk.YaDisk(token='AQAAAAA7GRcMAAesptPAjJG54kasszZQNrlbIQM')

backup_title = f'backup_{datetime.now().strftime("%d-%m-%Y--%H-%M-%S")}.sql'

reports_backup_path = f'/home/tascan7700/BACKUP/Reports/{backup_title}'
os.system(f'pg_dump -d Reports > {reports_backup_path}')
try:
    ya.upload(reports_backup_path, f'/ReportsBackup/{backup_title}')
except:
    pass

medoc_backup_path = f'/home/tascan7700/BACKUP/MEDoc/{backup_title}'
os.system(f'pg_dump -d MEDoc > {medoc_backup_path}')
ya.upload(medoc_backup_path, f'/MEDoc_BACKUP/{backup_title}')
