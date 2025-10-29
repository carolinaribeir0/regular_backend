from django.core.mail.backends.smtp import EmailBackend
import ssl, certifi

class BrevoEmailBackend(EmailBackend):
    """
    Corrige problema SSL no Windows + Python 3.14
    ao enviar e-mails via Brevo (smtp-relay.brevo.com).
    """
    def open(self):
        # Cria contexto seguro com CA do certifi
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        return super().open()
