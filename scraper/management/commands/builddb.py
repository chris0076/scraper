from django.core.management.base import BaseCommand, CommandError
from scraper.databaser import load_course_data, load_class_data

class Command(BaseCommand):
    args = ''
    help = 'Loads all the class data into the database'

    def handle(self, *args, **options):
        load_course_data()
        load_class_data()