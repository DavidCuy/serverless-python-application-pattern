from typing import Dict, Type
from core_db.BaseModel import BaseModel
#from core_aws.ssm import get_parameter
import core_utils.environment as env
from core_utils.constants import HTTP_SCHEMA

#APP_HOST = get_parameter(f'/{env.ENVIRONMENT}/{env.APP_NAME}/back/domain', is_dict=False, default='localhost')
APP_HOST = "https://localhost"

class ResourceReference:

    def __init__(self, model: Type[BaseModel], prefix_model: str = "", sufix_model: str = "", action: str = "GET", prefix_host: str | None = None) -> None:
        full_host = f"{(prefix_host + '.') if prefix_host else ''}{APP_HOST}"
        self.Name = model.__name__
        self.Action = action
        self.Ref = f"{HTTP_SCHEMA}://{full_host}/{prefix_model}/{model.model_path_name}{sufix_model}" if prefix_model is True else f"{HTTP_SCHEMA}://{full_host}/{model.model_path_name}{sufix_model}"
    
    def to_dict(self) -> Dict:
        return {
            "Name": self.Name,
            "Action": self.Action,
            "Ref": self.Ref
        }