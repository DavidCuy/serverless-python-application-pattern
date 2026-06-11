import pulumi
from pathlib import Path

try:
    ENVIRONMENT = pulumi.Config("global").require("env")
except Exception:
    ENVIRONMENT = "dev"

APP_NAME = pulumi.Config("global").require("app-name")
ROOT_PROJECT = Path(__file__).parent.parent

def add_param_prefix(param_name: str) -> str:
    return f"/{ENVIRONMENT.lower()}/{APP_NAME.lower()}/{param_name}"

def add_secret_prefix(secret_name: str) -> str:
    return f"{ENVIRONMENT.lower()}-{APP_NAME.lower()}-{secret_name}"
