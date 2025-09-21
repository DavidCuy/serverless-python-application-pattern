import smtplib

from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import cast
from email.message import EmailMessage
from aws_lambda_powertools import Logger

from .config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD
)
from .templates import TEMPLATE_CONFIG

LOGGER = Logger('layers.core.core_aws.ssm')

class Attachments:
    """Class to represent email attachments.
    """
    def __init__(self, file_path: str, filename: str, mime_type: str):
        """Initialize an attachment.

        Args:
            file_path (str): The path to the file to attach.
            filename (str): The name of the file to attach.
            mime_type (str): The MIME type of the file to attach.
        """
        self.file_path = file_path
        self.filename = filename
        self.mime_type = mime_type

def send_template_email(email_to: list[str], template_name: str, template_params: dict[str, str]):
    """
    Send an email using a template.

    Args:
        email_to (list[str]): The recipient email addresses.
        template_name (str): The name of the template to use.
        template_params (dict[str, str]): The parameters to fill in the template.
    """
    template = cast(str, TEMPLATE_CONFIG[template_name].get('content'))
    template = template.format(**template_params)
    
    email_msg = EmailMessage()
    email_msg['From'] = SMTP_USER
    email_msg['To'] = ', '.join(email_to)
    email_msg['Subject'] = TEMPLATE_CONFIG[template_name].get('subject', 'No Subject')
    email_msg.add_alternative(template, subtype='html')
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp_server:
            smtp_server.starttls()
            smtp_server.login(SMTP_USER, SMTP_PASSWORD)
            smtp_server.send_message(email_msg)
            LOGGER.info('Correo enviado exitosamente.')
    except Exception as e:
        LOGGER.exception(f'Error al enviar el correo: {e}')

def send_email_with_attachment(email_to: list[str], template_name: str, template_params: dict[str, str], attachments: list[Attachments]):
    """
    Send an email with attachments using a template.

    Args:
        email_to (list[str]): The recipient email addresses.
        template_name (str): The name of the template to use.
        template_params (dict[str, str]): The parameters to fill in the template.
        attachments (list[Attachments]): The list of attachments to include in the email.
    """
    template = cast(str, TEMPLATE_CONFIG[template_name].get('content'))
    template = template.format(**template_params)
    
    email_msg = MIMEMultipart()
    email_msg['From'] = SMTP_USER
    email_msg['To'] = ', '.join(email_to)
    email_msg['Subject'] = TEMPLATE_CONFIG[template_name].get('subject', 'No Subject')
    email_msg.attach(MIMEText(template, 'html'))

    for f in attachments or []:
        file_name = f.filename or basename(f.file_path)
        with open(f.file_path, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=file_name
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % file_name
        email_msg.attach(part)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp_server:
            smtp_server.starttls()
            smtp_server.login(SMTP_USER, SMTP_PASSWORD)
            smtp_server.send_message(email_msg)
            LOGGER.info('Correo enviado exitosamente.')
    except Exception as e:
        LOGGER.exception(f'Error al enviar el correo: {e}')
