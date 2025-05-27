from django.core.management.base import BaseCommand

from api.utils import (fetch_and_create_countries,
                       fetch_and_create_competitions,
                       fetch_and_create_teams_and_venues)


class Command(BaseCommand):
    help = "Creates countries, competitions and team if doesn't exist"

    def handle(self, *args, **options):
        fetch_and_create_countries()
        fetch_and_create_competitions()
        fetch_and_create_teams_and_venues()
        self.stdout.write(self.style.SUCCESS("Data updated successfully!"))