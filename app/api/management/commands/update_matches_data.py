from django.core.management.base import BaseCommand

from api.utils import create_or_update_match_data


class Command(BaseCommand):
    help = "Creates countries, competitions and team if doesn't exist"

    def handle(self, *args, **options):
        create_or_update_match_data()
        self.stdout.write(self.style.SUCCESS("Data updated successfully!"))