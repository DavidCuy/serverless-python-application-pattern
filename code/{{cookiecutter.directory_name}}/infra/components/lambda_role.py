import logging
import json
import pulumi
import pulumi_aws as aws
import config as project_config

from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LambdaRoleStack(pulumi.ComponentResource):
    def __init__(self,
                 name: str,
                 tags: Optional[dict] = None,
                 opts: Optional[pulumi.ResourceOptions] = None):
        super().__init__("{{ cookiecutter.project_name }}:components:lambdaRoleStack", name, {}, opts)

        # Create a execution role for the lambda function
        self.lambda_execution_role = aws.iam.Role(
            f"{name}-lambda-execution-role",
            name=f"{project_config.ENVIRONMENT}-{project_config.APP_NAME}-lambda-execution-role",
            assume_role_policy=aws.iam.get_policy_document(
                statements=[{
                    "effect": "Allow",
                    "actions": ["sts:AssumeRole"],
                    "principals": [{
                        "type": "Service",
                        "identifiers": ["lambda.amazonaws.com"]
                    }]
                }]
            ).json,
            inline_policies=[
                {
                    "name": "lambda-log-policies",
                    "policy": json.dumps({ 
                        "Version": "2012-10-17",
                        "Statement": [{
                            "Action": [
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents"
                            ],
                            "Effect": "Allow",
                            "Resource": ["arn:aws:logs:*:*:*"],
                        }],
                    }),
                }, {
                    "name": "lambda-parameters-secrets-policy",
                    "policy": json.dumps({ 
                        "Version": "2012-10-17",
                        "Statement": [{
                            "Action": [
                                "secretsmanager:GetResourcePolicy",
                                "secretsmanager:GetSecretValue",
                                "secretsmanager:DescribeSecret",
                                "secretsmanager:ListSecretVersionIds",
                                "ssm:GetParameters",
                                "ssm:GetParameter"
                            ],
                            "Effect": "Allow",
                            "Resource": ["*"],
                        }],
                    }),
                }, {
                    "name": "lambda-networking-policy",
                    "policy": json.dumps({ 
                        "Version": "2012-10-17",
                        "Statement": [{
                            "Action": [
                                "ec2:DescribeNetworkInterfaces",
                                "ec2:CreateNetworkInterface",
                                "ec2:DeleteNetworkInterface",
                                "ec2:DescribeInstances",
                                "ec2:AttachNetworkInterface"
                            ],
                            "Effect": "Allow",
                            "Resource": ["*"],
                        }],
                    }),
                }
            ],
            managed_policy_arns=[
                "arn:aws:iam::aws:policy/AWSLambdaExecute"
            ],
            path="/",
            tags=tags,
            opts=pulumi.ResourceOptions(parent=self)
        )

        self.register_outputs({
            "lambda_role_name": self.lambda_execution_role.name,
            "lambda_role_arn": self.lambda_execution_role.arn
        })
