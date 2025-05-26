# @file auth.py
import logging

from smtplib import SMTPException
from threading import Thread

from flask_mail import Message

from qhawariy import mail
# Configuracion para envio de email de confirmacion
logger = logging.getLogger(__name__)


def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except SMTPException:
            logger.exception("Ocurrio un problema al enviar el email")


def send_email(
        app,
        subject,
        sender,
        recipients,
        text_body,
        cc=None,
        bcc=None,
        html_body=None
):
    msg = Message(subject, sender=sender, recipients=recipients, cc=cc, bcc=bcc)
    msg.body = text_body
    if html_body:
        msg.html = html_body

    Thread(
        target=send_async_email,
        args=(app._get_current_object(), msg)
    ).start()
