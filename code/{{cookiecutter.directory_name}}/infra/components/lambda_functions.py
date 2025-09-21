import pulumi
import config as project_config
from pulumi import ResourceOptions
from .lambdas import LambdasStack

class LambdaFunctionsStack(pulumi.ComponentResource):
    def __init__(self,
                 name: str,
                 lambda_execution_role_arn: pulumi.Output[str],
                 layers: list[pulumi.Output[str]],
                 sg_ids: list[str],
                 subnets_ids: list[str],
                 tags: dict,
                 opts: ResourceOptions = None
        ):
        super().__init__("{{ cookiecutter.project_name }}:components:lambdaFunctionsStack", name, {}, opts)

        self.name = name
        self.tags = tags or {}

        self.lambda_functions = LambdasStack(
            name=f"{name}-lambdaFunctions",
            lambda_execution_role_arn=lambda_execution_role_arn,
            layers=layers,
            sg_ids=sg_ids,
            subnets_ids=subnets_ids,
            tags=self.tags
        )
