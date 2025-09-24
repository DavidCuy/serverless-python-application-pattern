import logging
import pulumi
import tempfile
import pulumi_aws as aws
import config as project_config

from typing import Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LambdaLayersStack(pulumi.ComponentResource):
    def __init__(self,
                 name: str,
                 tags: Optional[dict] = None,
                 opts: Optional[pulumi.ResourceOptions] = None):
        super().__init__("{{ cookiecutter.project_name }}:components:lambdaLayersStack", name, {}, opts)

        output_path = Path.cwd().joinpath("../tmp_build_layer")

        self.core_layer = aws.lambda_.LayerVersion(f"{name}-core-layer",
            layer_name=f"{project_config.ENVIRONMENT}-{project_config.APP_NAME}-core-layer",
            compatible_runtimes=[aws.lambda_.Runtime.PYTHON3D11],
            code=pulumi.FileArchive(str((output_path / "core").resolve())),
            description="Core layer for Lambda functions"
        )

        self.databases_layer = aws.lambda_.LayerVersion(f"{name}-databases-layer",
            layer_name=f"{project_config.ENVIRONMENT}-{project_config.APP_NAME}-databases-layer",
            compatible_runtimes=[aws.lambda_.Runtime.PYTHON3D11],
            code=pulumi.FileArchive(str((output_path / "databases").resolve())),
            description="Databases layer for Lambda functions"
        )