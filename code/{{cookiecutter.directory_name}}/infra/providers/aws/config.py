from config import ENVIRONMENT, APP_NAME, ROOT_PROJECT, add_param_prefix, add_secret_prefix
import pulumi
import pulumi_aws as aws

try:
    AWS_REGION = pulumi.Config("aws").require("region")
except Exception:
    AWS_REGION = "us-east-1"

AWS_ACCOUNT_ID = aws.get_caller_identity().account_id
