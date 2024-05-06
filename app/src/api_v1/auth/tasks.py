import smtplib
from email.message import EmailMessage

from ...config.settings import settings
from celery import shared_task


def get_message(username, email, verify_uuid):
    message = EmailMessage()
    message['Subject'] = 'Верификация аккаунта'
    message['From'] = settings.MAIL_FROM
    message['To'] = email

    message.set_content(
        '<p>'
        f"""
        Hello {username}
        You registered an account on {settings.DOMAIN_NAME}, 
        before being able to use your account 
        you need to verify that this is your email address by clicking here: http://127.0.0.1:8000/api/v1/verify/{verify_uuid}
        """
        '</p>',
        subtype='html'

    )
    return message


@shared_task(name="celery-verify-send-mail")
def send_verification_mail(username, email, verify_uuid):
    message = get_message(username, email, verify_uuid)
    with smtplib.SMTP_SSL(settings.MAIL_HOST, settings.MAIL_PORT) as server:
        server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        server.send_message(message)
