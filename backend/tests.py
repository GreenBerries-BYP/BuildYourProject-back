import os
import django
#teste

# Configura o Django (ajusta se o nome do projeto não for "config")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def testar_envio_email():
    subject = "Teste de envio de e-mail"
    message = "Se você recebeu este e-mail, o Django está configurado corretamente! 🚀"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ["mihcup@gmail.com"]  # coloque o email de destino

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        print(f"✅ E-mail enviado com sucesso para {recipient_list[0]}")
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")

if __name__ == "__main__":
    testar_envio_email()
