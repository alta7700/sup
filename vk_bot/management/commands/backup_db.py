from pathlib import Path

import yadisk
import os
from datetime import datetime
from django.core.management import BaseCommand
from yadisk.exceptions import PathExistsError

from ReportsDjango import settings
from vk_bot.vk_funcs.config import doc_sender


class Command(BaseCommand):
    help = 'Backup db'

    def handle(self, *args, **options):

        db_name = settings.DATABASES["default"]["NAME"]
        backup_filename = f'{datetime.now().strftime("%d-%m-%Y--%H-%M-%S")}.sql'
        backup_file = (Path(__file__).parent / 'backups' / backup_filename).as_posix()
        os.system(f'pg_dump -d {db_name} > {backup_file}')

        try:
            ya = yadisk.YaDisk(token=settings.YADISK_TOKEN)
            ya.upload(backup_file, f'/{db_name}Backup/{backup_filename}')
        except PathExistsError:  # library bag, filename is datetime with seconds< its uploads twice
            pass
        except Exception as e:
            doc_sender(settings.VK_GROUP_OWNER_ID, backup_file, 'Я не смог сделать бэкап', remove=False)
            raise e
