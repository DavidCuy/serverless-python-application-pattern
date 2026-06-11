import logging
import pulumi
import config as project_config
from commons import DEFAULT_TAGS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Environment: {project_config.ENVIRONMENT}")
logger.info(f"Project Name: {project_config.APP_NAME}")
logger.info(f"Default Tags: {DEFAULT_TAGS}")

logger.info("Starting creation...")

{% if cookiecutter.provider == 'aws' %}
from providers.aws.stack import deploy
deploy()
{% endif %}
