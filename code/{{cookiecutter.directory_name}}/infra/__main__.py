import logging
import pulumi
import config as project_config
import components
from commons import DEFAULT_TAGS
from utils.aws.ssm import get_parameter


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


logger.info(f"Environment: {project_config.ENVIRONMENT}")
logger.info(f"Project Name: {project_config.APP_NAME}")
logger.info(f"Default Tags: {DEFAULT_TAGS}")

logger.info("Starting creation...")

sg_params = get_parameter(f"/{project_config.ENVIRONMENT.lower()}/{project_config.APP_NAME}/lambda/security/group", is_dict=False)
subnet_ids_params = get_parameter(f"/{project_config.ENVIRONMENT.lower()}/{project_config.APP_NAME}/vpc/private/subnets", is_dict=False)

lambda_roles_stack = components.LambdaRoleStack(
    name=f"{project_config.ENVIRONMENT}-{project_config.APP_NAME}-lambdaRolesStack",
    tags=DEFAULT_TAGS
)

lambda_layers_stack = components.LambdaLayersStack(
    name=f"{project_config.ENVIRONMENT}-{project_config.APP_NAME}-lambdaLayersStack",
    tags=DEFAULT_TAGS
)

lambdas_stack = components.LambdaFunctionsStack(
    name=f"{project_config.ENVIRONMENT}-{project_config.APP_NAME}-lambdaFunctionsStack",
    lambda_execution_role_arn=lambda_roles_stack.lambda_execution_role.arn,
    layers=[
        lambda_layers_stack.core_layer.arn
    ],
    sg_ids=[sg_params],
    subnets_ids=str(subnet_ids_params).split(","),
    tags=DEFAULT_TAGS
)

api_gateway_stack = components.ApiGatewayStack(
    name=f"{project_config.ENVIRONMENT}-{project_config.APP_NAME}-apiGatewayStack",
    tags=DEFAULT_TAGS
)


pulumi.export("lambda_role_default_name", lambda_roles_stack.lambda_execution_role.name)
pulumi.export("lambda_role_default_arn", lambda_roles_stack.lambda_execution_role.arn)

pulumi.export("lambda_layer_arn", lambda_layers_stack.core_layer.layer_arn)
pulumi.export("lambda_layer_name", lambda_layers_stack.core_layer.layer_name)

pulumi.export("api_gateway_id", api_gateway_stack.rest_api.id)
pulumi.export("api_gateway_invoke_url", api_gateway_stack.invoke_url)
pulumi.export("api_gateway_execution_role_arn", api_gateway_stack.apig_role.arn)