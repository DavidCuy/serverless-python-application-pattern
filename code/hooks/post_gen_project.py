import shutil
from pathlib import Path

PROVIDER = "{{ cookiecutter.provider }}"

AWS_ONLY_PATHS = [
    Path("src/layers/core/python/core_aws"),
    # TODO: Path("infra/utils/aws"),
    # TODO: Path("infra/components"),  # Pulumi-AWS infra — pendiente multicloud
]

INFRA_LESS_PROVIDERS = {"container-cloud"}

if PROVIDER != "aws":
    for path in AWS_ONLY_PATHS:
        if path.exists():
            shutil.rmtree(path)
            print(f"[post-gen] Removed {path} (provider={PROVIDER})")

if PROVIDER in INFRA_LESS_PROVIDERS:
    infra_path = Path("infra")
    if infra_path.exists():
        shutil.rmtree(infra_path)
        print(f"[post-gen] Removed {infra_path} (provider={PROVIDER})")

    for infra_config in Path("src/functions").glob("*/infra_config.py"):
        infra_config.unlink()
        print(f"[post-gen] Removed {infra_config} (provider={PROVIDER})")
