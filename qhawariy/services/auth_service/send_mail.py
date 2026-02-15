# @file auth.py
import logging

from smtplib import SMTPException
from threading import Thread
from typing import Optional, Union

from flask import Flask
from flask_mail import Message

from qhawariy import mail
# Configuracion para envio de email de confirmacion
logger = logging.getLogger(__name__)


def send_async_email(app: Flask, msg: Message) -> None:
    """Envia email de forma asincronica dentro del contexto de la app"""
    with app.app_context():
        try:
            mail.send(msg)
        except SMTPException:
            logger.exception("Ocurrio un problema al enviar el email")


def send_email(
    subject: str,
    sender: str,
    recipients: Optional[list[Union[str, tuple[str, str]]]] = None,
    text_body: Optional[str] = None,
    html_body: Optional[str] = None,
    cc: Optional[list[Union[str, tuple[str, str]]]] = None,
    bcc: Optional[list[Union[str, tuple[str, str]]]] = None,
    app: Flask | None = None
) -> None:
    """ Construye y envia un email en un hilo separado"""
    msg = Message(subject, sender=sender, recipients=recipients, cc=cc, bcc=bcc)
    if text_body:
        msg.body = text_body
    if html_body:
        msg.html = html_body

    # current_app es un LocalProxy, por eso usamos _get_current_object()
    app_qh = app._get_current_object()  # type: ignore
    Thread(
        target=send_async_email,
        args=(app_qh, msg)  # type: ignore
    ).start()
