import shutil
from pathlib import Path

PROVIDER = "{{ cookiecutter.provider }}"

AWS_ONLY_PATHS = [
    Path("src/libs/core/python/core_aws"),
    Path("infra/utils/aws"),
    Path("infra/components/apigateway.py"),
    Path("infra/components/lambda_role.py"),
    Path("infra/components/lambda_layers.py"),
    Path("infra/components/lambda_functions.py"),
]

INFRA_LESS_PROVIDERS = {"container-cloud"}

if PROVIDER != "aws":
    for path in AWS_ONLY_PATHS:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            print(f"[post-gen] Removed {path} (provider={PROVIDER})")

if PROVIDER in INFRA_LESS_PROVIDERS:
    infra_path = Path("infra")
    if infra_path.exists():
        shutil.rmtree(infra_path)
        print(f"[post-gen] Removed {infra_path} (provider={PROVIDER})")

    for infra_config in Path("src/functions").glob("*/infra_config.py"):
        infra_config.unlink()
        print(f"[post-gen] Removed {infra_config} (provider={PROVIDER})")
