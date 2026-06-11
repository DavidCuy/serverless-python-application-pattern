import json
import logging
import hashlib
import pulumi
import pulumi_aws as aws
from providers.aws import config as project_config

from typing import Optional
from enum import Enum
from pathlib import Path
from typing import cast

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"

class IntegrationType(Enum):
    MOCK = "MOCK"

class AuthType(Enum):
    NONE = "NONE"

class HttpStatusCode(Enum):
    OK = "200"
    CREATED = "201"
    ACCEPTED = "202"
    NO_CONTENT = "204"
    BAD_REQUEST = "400"
    UNAUTHORIZED = "401"
    FORBIDDEN = "403"
    NOT_FOUND = "404"
    METHOD_NOT_ALLOWED = "405"
    UNPROCESSABLE_CONTENT = "422"

class ApiRestEndpoint:
    def __init__(self, method: pulumi.Output,
                 integration: pulumi.Output,
                 method_response: pulumi.Output,
                 integration_response: pulumi.Output):
        self.method = method
        self.integration = integration
        self.method_response = method_response
        self.integration_response = integration_response

class ApiGatewayStack(pulumi.ComponentResource):
    OPEN_API_SPEC = "openapi.json"

    def __init__(self, name: str,
                 tags: Optional[dict] = None,
                 opts: Optional[pulumi.ResourceOptions] = None):
        super().__init__("{{ cookiecutter.project_name }}:components:apiGatewayStack", name, {}, opts)

        self.name = name
        self.tags = tags or {}

        (openapi_body, openapi_sha) = self.build_openapi_file()

        self.rest_api = aws.apigateway.RestApi(f"{name}-api",
            name=f"{project_config.ENVIRONMENT}-{project_config.APP_NAME}-gateway",
            body=openapi_body,
            tags=self.tags
        )

        aws.ssm.Parameter(
            f"{name}-rest-api-id",
            name=f"/{project_config.ENVIRONMENT}/{project_config.APP_NAME}/apigateway/principal/id",
            type="String",
            value=self.rest_api.id,
            tags=self.tags,
            opts=pulumi.ResourceOptions(parent=self)
        )

        self.apig_deploy = aws.apigateway.Deployment(f"{name}-api-deployment",
            rest_api=self.rest_api.id,
            triggers={
                "openapi_sha": openapi_sha,
                "stack": pulumi.get_stack(),
            },
            opts=pulumi.ResourceOptions(parent=self.rest_api)
        )

        self.apig_log_group = aws.cloudwatch.LogGroup(f"{name}-api-log-group",
            name=self.rest_api.id.apply(lambda apiId: f"API-Gateway-Execution-Logs_{apiId}/{project_config.ENVIRONMENT}"),
            retention_in_days=14,
            tags=self.tags
        )

        self.apig_role = aws.iam.Role(
            f"{name}-apig-role",
            name=f"{project_config.ENVIRONMENT}-{project_config.APP_NAME}-apigw-invoke-lambda-role",
            assume_role_policy=aws.iam.get_policy_document(
                statements=[{
                    "effect": "Allow",
                    "actions": ["sts:AssumeRole"],
                    "principals": [{
                        "type": "Service",
                        "identifiers": ["apigateway.amazonaws.com"]
                    }]
                }]
            ).json,
            managed_policy_arns=[
                "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
            ],
            inline_policies=[
                {
                    "name": "allow-invoke-lambdas-by-project",
                    "policy": json.dumps({
                        "Version": "2012-10-17",
                        "Statement": [{
                            "Action": ["lambda:InvokeFunction"],
                            "Effect": "Allow",
                            "Resource": [f"arn:aws:lambda:{project_config.AWS_REGION}:{project_config.AWS_ACCOUNT_ID}:function:{project_config.ENVIRONMENT}-{project_config.APP_NAME}-*"]
                        }],
                    }),
                },
                {
                    "name": "allow-invoke-lambdas-by-environment",
                    "policy": json.dumps({
                        "Version": "2012-10-17",
                        "Statement": [{
                            "Action": ["lambda:InvokeFunction"],
                            "Effect": "Allow",
                            "Resource": [f"arn:aws:lambda:{project_config.AWS_REGION}:{project_config.AWS_ACCOUNT_ID}:function:{project_config.ENVIRONMENT}-{project_config.APP_NAME}-*"]
                        }],
                    }),
                },
                {
                    "name": "allow-write-logs-by-project",
                    "policy": json.dumps({
                        "Version": "2012-10-17",
                        "Statement": [{
                            "Action": [
                                "logs:CreateLogGroup", "logs:CreateLogStream",
                                "logs:DescribeLogGroups", "logs:DescribeLogStreams",
                                "logs:PutLogEvents", "logs:GetLogEvents", "logs:FilterLogEvents"
                            ],
                            "Effect": "Allow",
                            "Resource": [f"arn:aws:logs:{project_config.AWS_REGION}:{project_config.AWS_ACCOUNT_ID}:log-group:/aws/lambda/{project_config.ENVIRONMENT}-{project_config.APP_NAME}-*"]
                        }],
                    }),
                },
                {
                    "name": "allow-write-logs-by-environment",
                    "policy": json.dumps({
                        "Version": "2012-10-17",
                        "Statement": [{
                            "Action": [
                                "logs:CreateLogGroup", "logs:CreateLogStream",
                                "logs:DescribeLogGroups", "logs:DescribeLogStreams",
                                "logs:PutLogEvents", "logs:GetLogEvents", "logs:FilterLogEvents"
                            ],
                            "Effect": "Allow",
                            "Resource": [f"arn:aws:logs:{project_config.AWS_REGION}:{project_config.AWS_ACCOUNT_ID}:log-group:/aws/lambda/{project_config.ENVIRONMENT}-{project_config.APP_NAME}-*"]
                        }],
                    }),
                }
            ],
            path="/",
            tags=self.tags,
            opts=pulumi.ResourceOptions(parent=self)
        )

        self.apig_account = aws.apigateway.Account(f"{name}-api-account",
            cloudwatch_role_arn=self.apig_role.arn,
            opts=pulumi.ResourceOptions(parent=self)
        )

        access_logs_settings = aws.apigateway.StageAccessLogSettingsArgs(
            destination_arn=self.apig_log_group.arn,
            format=json.dumps({
                "requestId": "$context.requestId",
                "ip": "$context.identity.sourceIp",
                "caller": "$context.identity.caller",
                "user": "$context.identity.user",
                "requestTime": "$context.requestTime",
                "httpMethod": "$context.httpMethod",
                "resourcePath": "$context.resourcePath",
                "status": "$context.status",
                "protocol": "$context.protocol",
                "responseLength": "$context.responseLength"
            })
        )

        self.stage = aws.apigateway.Stage(f"{name}-api-stage",
            rest_api=self.rest_api.id,
            deployment=self.apig_deploy.id,
            stage_name=project_config.ENVIRONMENT,
            access_log_settings=access_logs_settings,
            tags=self.tags
        )

        self.api_usage_plan = aws.apigateway.UsagePlan(f"{name}-api-usage-plan",
            api_stages=[aws.apigateway.UsagePlanApiStageArgs(
                api_id=self.rest_api.id,
                stage=self.stage.stage_name
            )],
            description="Usage plan to protect the gateway",
            tags=self.tags
        )

        self.api_key = aws.apigateway.ApiKey(f"{name}-api-key",
            name=f"{name}-key",
            description="General api key for backend integration",
            enabled=True,
            tags=self.tags
        )

        aws.apigateway.UsagePlanKey(f"{name}-usage-plan-key",
            key_id=self.api_key.id,
            key_type="API_KEY",
            usage_plan_id=self.api_usage_plan.id
        )

        self.invoke_url = pulumi.Output.concat("https://", self.rest_api.id, ".execute-api.", aws.config.region, ".amazonaws.com/", project_config.ENVIRONMENT, "/")

        self.api_resource = aws.apigateway.Resource(f"{name}-api",
            rest_api=self.rest_api.id,
            parent_id=self.rest_api.root_resource_id,
            path_part="api"
        )

        self.register_outputs({
            "api_gateway_url": self.invoke_url,
            "api_id": self.rest_api.id,
            "api_log_group_name": self.apig_log_group.name,
            "api_stage_name": self.stage.stage_name,
            "api_resource_path": self.api_resource.id
        })

    def build_openapi_file(self) -> tuple[str, str]:
        raw_spec = (Path(__file__).parent / self.OPEN_API_SPEC).read_text(encoding="utf-8")
        spec = json.loads(raw_spec)
        spec['info']['title'] = f"{project_config.APP_NAME} API"
        openapi_body = json.dumps(spec)
        openapi_sha = hashlib.sha256(openapi_body.encode("utf-8")).hexdigest()
        return (openapi_body, openapi_sha)
