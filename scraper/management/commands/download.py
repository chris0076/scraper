from django.core.management.base import BaseCommand, CommandError
from scraper.scraper import run_all

class Command(BaseCommand):
    args = '<subject subject ...>'
    help = 'Download class data'

    def handle(self, *args, **options):
        run_all(args)