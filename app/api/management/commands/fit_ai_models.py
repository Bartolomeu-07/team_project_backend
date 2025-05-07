from django.core.management.base import BaseCommand

from api.utils import fit_ai_models


class Command(BaseCommand):
    help = "Fits AI models"

    def handle(self, *args, **options):
        fit_ai_models()
        self.stdout.write(self.style.SUCCESS("Models fitted successfully!"))