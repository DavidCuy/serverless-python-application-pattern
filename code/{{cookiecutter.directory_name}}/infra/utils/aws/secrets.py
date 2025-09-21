import logging
import pulumi
import pulumi_aws as aws
import boto3
import json
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def secret_version_exists(secret_id: str) -> pulumi.Output[bool]:
    """
    Checks if a specific version of a secret exists in AWS Secrets Manager.

    Args:
        secret_id (str): The identifier of the secret to check.

    Returns:
        bool: True if the secret version exists, False otherwise.

    Logs:
        Logs an error message if an exception occurs while attempting to retrieve the secret version.
    """
    try:
        logger.info(f"Verifying secret {secret_id}")
        aws.secretsmanager.get_secret_version(
            secret_id=secret_id
        )
        return True
    except Exception as e:
        logger.error(f"Error getting secret version: {e}")
        return False


def get_secret(secret_name:str, is_dict=False) -> str | dict:
    secret_client = boto3.client("secretsmanager")
    try:
        logger.info(f"Getting secret: {secret_name}")
        get_secret_value_response = secret_client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response["SecretString"]
    except (KeyError, ClientError) as e:
        logger.error("Error create client secretmanager")
        logger.error(f"Details: {str(e)}")
        raise e
    else:
        return secret if not is_dict else json.loads(str(secret))
