from django.core.management import BaseCommand

from vk_bot.vk_funcs.filling_base.fill import fill_by_files_in_dirs, truncate_db


class Command(BaseCommand):
    help = 'Fill db'

    params = ['subjects', 'students', 'schedules_e', 'schedules_j']

    def handle(self, *args, **options):
        if options.get('truncate'):
            truncate_db()
        if options.get('all'):
            options.update({par: True for par in self.params})
        fill_by_files_in_dirs(**options)

    def add_arguments(self, parser):
        parser.add_argument(
            '--all', action='store_true'
        )
        parser.add_argument(
            '--truncate', action='store_true'
        )
        parser.add_argument(
            '-f', '--folder_suffix', default=''
        )
        for par in self.params:
            parser.add_argument(
                '--' + par, action='store_true'
            )
