from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Conference module removed."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Conference module has been disabled/removed."))
