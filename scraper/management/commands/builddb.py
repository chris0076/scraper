from django.core.management.base import BaseCommand, CommandError
from scraper.databaser import load_course_data, load_class_data
from scraper.models import Class, Course, Location

class Command(BaseCommand):
    args = ''
    help = 'Loads all the class data into the database'

    def handle(self, *args, **options):
        # this is because of https://code.djangoproject.com/ticket/16426
        # sqlite does not allow deletes with more than 999 vars
        # this is only a problem because of the way django deletes rows if a
        # FK is involved
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("DELETE FROM scraper_class")
        cursor.execute("DELETE FROM scraper_course")
        cursor.execute("DELETE FROM scraper_location")
        load_course_data()
        load_class_data()