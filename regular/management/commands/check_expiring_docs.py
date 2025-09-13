import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from regular.models import RenewableDoc, UserProfile
from django.conf import settings
from django.core.mail import EmailMessage, get_connection


class Command(BaseCommand):
    help = "Verifica documentos que irão expirar em 30 dias e envia alerta por email (via MailerSend SMTP)"

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        target_date = today + timedelta(days=26)

        docs_to_notify = RenewableDoc.objects.filter(expiration_date=target_date, alert_sent=False)

        if not docs_to_notify.exists():
            self.stdout.write(self.style.SUCCESS("Nenhum documento precisa de alerta hoje."))
            return

        # Cria a conexão SMTP
        with get_connection(
            host=settings.MAILERSEND_SMTP_HOST,
            port=settings.MAILERSEND_SMTP_PORT,
            username=settings.MAILERSEND_SMTP_USERNAME,
            password=settings.MAILERSEND_SMTP_PASSWORD,
            use_tls=True,
        ) as connection:

            for doc in docs_to_notify:
                profiles_with_email = UserProfile.objects.filter(
                    company=doc.company,
                    user__email__isnull=False
                ).exclude(user__email__exact='').select_related('user')

                if not profiles_with_email.exists():
                    self.stdout.write(f"Nenhum usuário com email encontrado para a empresa {doc.company.name}")
                    continue

                recipient_list = [p.user.email for p in profiles_with_email]

                subject = f"[ALERTA] Documento prestes a expirar: {doc.doc_name}"
                html_content = (
                    f"<p>Olá, a Regular está aqui para te lembrar:</p>"
                    f"<p>O documento <strong>'{doc.doc_name}'</strong> da empresa <strong>{doc.company.name}</strong> "
                    f"irá expirar em <strong>{doc.expiration_date.strftime('%d/%m/%Y')}</strong>.</p>"
                    f"<p>Favor providenciar a renovação.</p>"
                    f"<p>Para conformidade sanitária, recomendamos a renovação antes do vencimento. Conte com o nosso apoio!</p>"
                    f"<p>Atenciosamente,</p>"
                    f"<p>Regular Consultoria</p>"
                )

                for recipient in recipient_list:
                    try:
                        email = EmailMessage(
                            subject=subject,
                            body=html_content,
                            from_email=settings.MAILERSEND_FROM_EMAIL,
                            to=[recipient],
                            connection=connection,
                        )
                        email.content_subtype = "html"
                        email.send()
                        self.stdout.write(self.style.SUCCESS(
                            f"✅ Email enviado para {recipient} sobre o doc '{doc.doc_name}'"
                        ))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(
                            f"❌ Erro ao enviar email para {recipient}: {str(e)}"
                        ))

                # Marca o documento como notificado (depois de tentar todos)
                doc.alert_sent = True
                doc.save(update_fields=["alert_sent"])
