import json
import logging
import hashlib
import pulumi
import pulumi_aws as aws
import config as project_config

from typing import Optional
from enum import Enum
from pathlib import Path
from typing import cast

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HttpMethod (Enum):
    """
    Enum class representing HTTP methods.

    Attributes:
        GET (str): Represents the HTTP GET method, used to retrieve data from a server.
        POST (str): Represents the HTTP POST method, used to send data to a server to create a resource.
        PUT (str): Represents the HTTP PUT method, used to update or create a resource on a server.
        PATCH (str): Represents the HTTP PATCH method, used to apply partial modifications to a resource.
        DELETE (str): Represents the HTTP DELETE method, used to delete a resource from a server.
        OPTIONS (str): Represents the HTTP OPTIONS method, used to describe the communication options for the target resource.
    """
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"

class IntegrationType (Enum):
    """
    Enum class representing the types of integrations available for the API Gateway.

    Attributes:
        MOCK: Represents a mocked integration type, typically used for testing or development purposes.
    """
    MOCK = "MOCK"

class AuthType(Enum):
    """
    AuthType is an enumeration that defines the types of authentication
    supported by the API Gateway.

    Attributes:
        NONE: Represents no authentication required.
    """
    NONE = "NONE"

class HttpStatusCode(Enum):
    """
    Enum class representing HTTP status codes.
    Attributes:
        OK (str): HTTP status code for a successful request (200).
        CREATED (str): HTTP status code indicating that a resource has been successfully created (201).
        ACCEPTED (str): HTTP status code indicating that a request has been accepted for processing, but the processing is not complete (202).
        NO_CONTENT (str): HTTP status code indicating that the server successfully processed the request, but is not returning any content (204).
        BAD_REQUEST (str): HTTP status code indicating that the server could not understand the request due to invalid syntax (400).
        UNAUTHORIZED (str): HTTP status code indicating that authentication is required and has failed or has not been provided (401).
        FORBIDDEN (str): HTTP status code indicating that the server understands the request but refuses to authorize it (403).
        NOT_FOUND (str): HTTP status code indicating that the requested resource could not be found (404).
        METHOD_NOT_ALLOWED (str): HTTP status code indicating that the request method is not supported for the requested resource (405).
        UNPROCESSABLE_CONTENT (str): HTTP status code indicating that the server understands the content type of the request entity, but was unable to process the contained instructions (422).
    """
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
    """
    Represents a REST API endpoint in an API Gateway.

    Attributes:
        method (pulumi.Output): The HTTP method (e.g., GET, POST) associated with the API endpoint.
        integration (pulumi.Output): The integration configuration for the API endpoint, defining how the endpoint interacts with backend resources.
        method_response (pulumi.Output): The response configuration for the method, specifying the response status codes, headers, and models.
        integration_response (pulumi.Output): The response configuration for the integration, specifying how the backend responses are mapped to the method responses.
    """
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

        # Create a REST API gateway
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

        # Api Gateway deployment
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

        # Api Gateway Role for invoke functions and logging
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
                            "Action": [
                                "lambda:InvokeFunction"
                            ],
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
                            "Action": [
                                "lambda:InvokeFunction"
                            ],
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
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:DescribeLogGroups",
                                "logs:DescribeLogStreams",
                                "logs:PutLogEvents",
                                "logs:GetLogEvents",
                                "logs:FilterLogEvents"
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
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:DescribeLogGroups",
                                "logs:DescribeLogStreams",
                                "logs:PutLogEvents",
                                "logs:GetLogEvents",
                                "logs:FilterLogEvents"
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

        # API Gateway Account
        aws.apigateway.Account(f"{name}-api-account",
            cloudwatch_role_arn=self.apig_role.arn
        )

        # API Gateway Stage

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

        # Usage plan and api key
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

        # TODO: Implement custom domain names
        #root_domain_name = aws.apigateway.DomainName(f"{name}-root-domain-name",
        #    domain_name=aws.ssm.get_parameter(name=project_config.API_BACK_CUSTOM_DOMAIN_ROOT_SSM).value,
        #    endpoint_configuration=aws.apigateway.DomainNameEndpointConfigurationArgs(
        #        types="EDGE"
        #    ),
        #    security_policy="TLS_1_2",
        #    certificate_arn=aws.ssm.get_parameter(name=project_config.CERTIFICATE_APIG_SSM).value
        #)
        #
        #aws.apigateway.BasePathMapping(f"{name}-root-mapping",
        #    rest_api=self.rest_api.id,
        #    stage_name=self.stage.stage_name,
        #    domain_name=root_domain_name.domain_name
        #)
        #
        #wildcard_domain_name = aws.apigateway.DomainName(f"{name}-wildcard-domain-name",
        #    domain_name=aws.ssm.get_parameter(name=project_config.API_BACK_CUSTOM_DOMAIN_WILDCARD_SSM).value,
        #    endpoint_configuration=aws.apigateway.DomainNameEndpointConfigurationArgs(
        #        types="EDGE"
        #    ),
        #    security_policy="TLS_1_2",
        #    certificate_arn=aws.ssm.get_parameter(name=project_config.CERTIFICATE_APIG_SSM).value
        #)
        #
        #aws.apigateway.BasePathMapping(f"{name}-wildcard-mapping",
        #    rest_api=self.rest_api.id,
        #    stage_name=self.stage.stage_name,
        #    domain_name=wildcard_domain_name.domain_name
        #)

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
        # Read openApi file
        raw_spec = (Path(__file__).parent / self.OPEN_API_SPEC).read_text(encoding="utf-8")

        # Parse the OpenAPI specification
        spec = json.loads(raw_spec)
        logger.info(f"Loaded OpenAPI spec: {Path(__file__).parent / self.OPEN_API_SPEC}")

        # Modify the spec as needed
        spec['info']['title'] = f"{project_config.APP_NAME} API"

        # Serialize json
        openapi_body = json.dumps(spec)
        openapi_sha = hashlib.sha256(openapi_body.encode("utf-8")).hexdigest()

        return (openapi_body, openapi_sha)
