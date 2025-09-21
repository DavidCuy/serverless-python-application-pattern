from core_utils.environment import env
from aws_lambda_powertools import Logger

from core_aws.secret_manager import get_secret
from core_utils.environment import env

LOGGER = Logger('layers.core_utils.email.config')
LOGGER.info("Email configuration")

def get_from_secrets():
    global SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

    if not (SMTP_HOST and SMTP_PORT and SMTP_USER and SMTP_PASSWORD):
        LOGGER.warning("Email configuration not found using environment variables, getting from secrets")
        email_config = get_secret('email-smtp-config', is_dict=True, use_prefix=True)

        SMTP_HOST = email_config.get('SMTP_HOST', None)
        SMTP_PORT = email_config.get('SMTP_PORT', None)
        SMTP_USER = email_config.get('SMTP_USER', None)
        SMTP_PASSWORD = email_config.get('SMTP_PASSWORD', None)

LOGGER.info("Loading from environment variables")
SMTP_HOST = env("SMTP_HOST", None)
SMTP_PORT = env("SMTP_PORT", None)
SMTP_USER = env("SMTP_USER", None)
SMTP_PASSWORD = env("SMTP_PASSWORD", None)

get_from_secrets()