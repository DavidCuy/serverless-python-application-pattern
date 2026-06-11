import pulumi
from pathlib import Path

try:
    ENVIRONMENT = pulumi.Config("global").require("env")
except Exception:
    ENVIRONMENT = "dev"

APP_NAME = pulumi.Config("global").require("app-name")
ROOT_PROJECT = Path(__file__).parent.parent

parameters_cfg = pulumi.Config("parameters")
vpc_cfg = pulumi.Config("vpc")

{% if cookiecutter.provider == 'aws' %}
import pulumi_aws as aws

try:
    AWS_REGION = pulumi.Config("aws").require("region")
except Exception:
    AWS_REGION = "us-east-1"

AWS_ACCOUNT_ID = aws.get_caller_identity().account_id
{% endif %}

def add_param_prefix(param_name: str) -> str:
    return f"/{ENVIRONMENT.lower()}/{APP_NAME.lower()}/{param_name}"

def add_secret_prefix(secret_name: str) -> str:
    return f"{ENVIRONMENT.lower()}-{APP_NAME.lower()}-{secret_name}"
