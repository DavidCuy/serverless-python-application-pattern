import os
from typing import Any
from dotenv import load_dotenv
from aws_lambda_powertools import Logger

LOGGER = Logger('layers.core.core_utils.environment')
load_dotenv()

def env(env_key: str, default_value: Any) -> Any:
    """ Parsea el valor de una variable de entorno a una variable utilizable para python

    Args:
        env_key (str): Nombre de la variable de entorno de
        default_value (Any): Valor por default de la variable de entorno

    Returns:
        Any: Valor designado de la variable de entorno o en su defecto la default
    """
    if env_key in os.environ:
        if os.environ[env_key].isdecimal():
            return int(os.environ[env_key])
        elif str(os.environ[env_key]).lower() == "true" or str(os.environ[env_key]).lower() == "true":
            return str(os.environ[env_key]).lower() == "true"
        else:
            return os.environ[env_key]
    else:
        return default_value

APP_NAME    = env("APP_NAME", "App")
APP_URL     = env("APP_URL", "http://localhost")
ENVIRONMENT = env("ENVIRONMENT", "dev")

LOGGER.info("All variables LOADED")

DAMAGE_ID_API_KEY = env("DAMAGE_ID_API_KEY", "")
DAMAGE_ID_ACCESS_KEY = env("DAMAGE_ID_ACCESS_KEY", "")
