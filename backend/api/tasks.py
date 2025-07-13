import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def send_project_invitation_email(self, recipient_email, project_name):
    """
    Envia um e-mail de convite de forma assíncrona com retentativas.
    """
    try:
        subject = "Você foi convidado para colaborar em um projeto!"
        message = (
            f"Olá!\n\n"
            f"Você foi convidado para colaborar no projeto '{project_name}'.\n\n"
            f"Se você ainda não tem uma conta em nossa plataforma, por favor, "
            f"registre-se usando este e-mail ({recipient_email}) para ter acesso ao projeto."
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[recipient_email],
            fail_silently=False
        )
        logger.info(f"E-mail de convite enviado com sucesso para {recipient_email} para o projeto {project_name}.")
    except Exception as e:
        logger.error(f"Falha ao enviar e-mail para {recipient_email}: {e}")
        raise