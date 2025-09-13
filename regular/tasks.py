# regular/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from mailersend import Email
from .models import RenewableDoc, UserProfile

@shared_task
def check_expiring_docs_task():
    today = timezone.now().date()
    target_date = today + timedelta(days=30)

    docs = RenewableDoc.objects.filter(expiration_date=target_date, alert_sent=False)

    if not docs.exists():
        return "Nenhum documento expira em 30 dias."

    mailer = Email(settings.MAILERSEND_API_KEY)


    for doc in docs:
        profiles = UserProfile.objects.filter(company=doc.company)
        recipients = [p.user.email for p in profiles if p.user.email]

        if not recipients:
            continue

        subject = f"[ALERTA] Documento prestes a expirar: {doc.doc_name}"
        message = (
            f"O documento '{doc.doc_name}' da empresa {doc.company.name} "
            f"irá expirar em {doc.expiration_date}. "
            f"Favor providenciar a renovação."
        )

        mail_body = {
            "from": {
                "email": settings.MAILERSEND_FROM_EMAIL,
                "name": "Sistema de Alertas"
            },
            "to": [{"email": email} for email in recipients],
            "subject": subject,
            "text": message,
        }

        mailer.send(mail_body)

        doc.alert_sent = True
        doc.save(update_fields=["alert_sent"])

    return "Emails enviados com sucesso!"
