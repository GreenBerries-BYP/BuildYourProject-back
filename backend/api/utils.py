from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_project_invitation_email(email, project_name):
    """
    Sends an invitation email to a user for a specific project.
    """
    subject = f"You've been invited to collaborate on a project: {project_name}"
    message = (
        f"Hello,\n\n"
        f"You have been invited to collaborate on the project: '{project_name}'.\n\n"
        f"Please log in to the platform to view the project details and start collaborating.\n\n"
        f"Best regards,\n"
        f"The Project Management Team"
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    try:
        send_mail(subject, message, from_email, recipient_list)
        logger.info(f"Invitation email sent to {email} for project {project_name}")
        return True
    except Exception as e:
        logger.error(f"Error sending invitation email to {email} for project {project_name}: {e}")
        return False
