from django.core.management.base import BaseCommand
from regular.tasks import check_expiring_docs_task

class Command(BaseCommand):
    help = "Verifica documentos a expirar e envia alerta por e-mail."

    def handle(self, *args, **kwargs):
        result = check_expiring_docs_task()
        self.stdout.write(self.style.SUCCESS(result))
