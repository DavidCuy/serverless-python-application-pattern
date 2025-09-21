import json
import pulumi
from pathlib import Path
import pulumi_aws as aws


parameters_cfg = pulumi.Config("parameters")
vpc_cfg = pulumi.Config("vpc")

# Load configuration values from Pulumi config
try:
    ENVIRONMENT = pulumi.Config("global").require("env")
    AWS_REGION = pulumi.Config("aws").require("region")
    AWS_ACCOUNT_ID = aws.get_caller_identity().account_id
except Exception as e:
    ENVIRONMENT = "dev"
    AWS_REGION = "us-east-2"
    AWS_ACCOUNT_ID = aws.get_caller_identity().account_id

APP_NAME = pulumi.Config("global").require("app-name")
ROOT_PROJECT = Path(__file__).parent.parent

def add_param_prefix(param_name: str) -> str:
    return f"/{ENVIRONMENT.lower()}/{APP_NAME.lower()}/{param_name}"

def add_secret_prefix(secret_name: str) -> str:
    return f"{ENVIRONMENT.lower()}-{APP_NAME.lower()}-{secret_name}"


PRIVATE_SUBNETS_AZ = json.loads(vpc_cfg.get("private_az") or '["us-east-1a", "us-east-1b", "us-east-1c"]')
PUBLIC_SUBNETS_AZ = json.loads(vpc_cfg.get("public_az") or '["us-east-1a", "us-east-1b", "us-east-1c"]')

VPC_CIDR_BLOCK = vpc_cfg.get("cidr") or "10.0.0.0/16"
VPC_PRIVATE_SUBNET_MASK = vpc_cfg.get_int("private_subnet_mask") or 24
VPC_PRIVATE_INITIAL_IP = vpc_cfg.get("private_init_ip") or "10.0.30.0"

VPC_PUBLIC_SUBNET_MASK = vpc_cfg.get_int("public_subnet_mask") or 24
VPC_PUBLIC_INITIAL_IP = vpc_cfg.get("public_init_ip") or "10.0.40.0"
