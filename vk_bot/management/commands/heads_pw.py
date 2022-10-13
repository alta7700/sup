from pathlib import Path

from django.core.management import BaseCommand

from vk_bot.vk_funcs.filling_base.get_head_logins_and_passwords import generate


class Command(BaseCommand):

    def handle(self, *args, **options):
        courses = options.get('courses') or [1, 2, 3, 4, 5, 6]
        print(courses)
        folder = Path(__file__).parent / 'heads_pw'
        for course in courses:
            generate(course, folder)

    def add_arguments(self, parser):
        parser.add_argument(
            '--courses', nargs='*', type=int
        )
