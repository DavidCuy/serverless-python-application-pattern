import boto3
import json
from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError
from core_utils.environment import ENVIRONMENT, APP_NAME

LOGGER = Logger('layers.core.core_aws.secret_manager')
SECRET_CLIENT = boto3.client("secretsmanager")

def get_secret(secret_name:str, is_dict=False, use_prefix = False) -> str | dict:
    if use_prefix:
        secret_name = f"{ENVIRONMENT}-{APP_NAME}-{secret_name}"
    try:
        LOGGER.info(f"Getting secret: {secret_name}")
        get_secret_value_response = SECRET_CLIENT.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response["SecretString"]
    except (KeyError, ClientError) as e:
        LOGGER.error("Error create client secretmanager")
        LOGGER.error(f"Details: {str(e)}")
        raise e
    else:
        return secret if not is_dict else json.loads(str(secret))
