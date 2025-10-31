# from django.core.mail.backends.smtp import EmailBackend
# import ssl, certifi
#
# class BrevoEmailBackend(EmailBackend):
#     """
#     Corrige problema SSL no Windows + Python 3.14
#     ao enviar e-mails via Brevo (smtp-relay.brevo.com).
#     """
#     def open(self):
#         # Cria contexto seguro com CA do certifi
#         self.ssl_context = ssl.create_default_context(cafile=certifi.where())
#         return super().open()
import smtplib, ssl, certifi
from django.core.mail.backends.smtp import EmailBackend


class BrevoEmailBackend(EmailBackend):
    def open(self):
        # Cria o contexto SSL confiável (verifica certificado, mas ignora hostname)
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_REQUIRED

        # Garante compatibilidade com versões que não possuem self.local_hostname
        local_hostname = getattr(self, "local_hostname", None)
        connection_params = {"local_hostname": local_hostname} if local_hostname else {}

        if self.use_ssl:
            # Conexão direta SSL
            self.connection = self.connection_class(
                self.host, self.port, **connection_params
            )
        else:
            # Conexão TLS (STARTTLS)
            self.connection = self.connection_class(self.host, self.port)
            self.connection.ehlo()
            if self.use_tls:
                self.connection.starttls(context=self.ssl_context)
                self.connection.ehlo()

        # Login SMTP
        if self.username and self.password:
            self.connection.login(self.username, self.password)

        return self.connection
