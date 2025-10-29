from datetime import timedelta
from django.core.mail import send_mail
from django.utils import timezone
from regular.models import RenewableDoc, UserProfile
from django.conf import settings

def check_expiring_docs_task():
    """
    Verifica documentos com data de expiração <= 30 dias e envia alertas por e-mail.
    """
    today = timezone.now().date()
    target_date = today + timedelta(days=30)

    docs = RenewableDoc.objects.filter(
        expiration_date__lte=target_date,  # <= 30 dias
        alert_sent=False
    )

    if not docs.exists():
        return "Nenhum documento expira em 30 dias."

    for doc in docs:
        company = doc.company
        user_profiles = UserProfile.objects.filter(company=company)
        for profile in user_profiles:
            user_email=profile.user.email
            if user_email:
                send_mail(
                    subject=f"⚠️ Documento '{doc.doc_name}' expira em breve",
                    message=(
                        f"Olá, {company.name} \n\n A Regula On está aqui para te lembrar: \n\n O documento '{doc.doc_name}' "
                        f"expira em {doc.expiration_date.strftime('%d/%m/%Y')}.\n"
                        f"Por favor, providencie a renovação.\n\n Para conformidade sanitária, recomendamos a renovação antes do vencimento. Conte com o nosso apoio!\n\n"
                        f"Atenciosamente,\nRegula On"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user_email],
                    fail_silently=False,
                )

        doc.alert_sent = True
        doc.save()

    return f"{docs.count()} alertas de expiração enviados com sucesso."

