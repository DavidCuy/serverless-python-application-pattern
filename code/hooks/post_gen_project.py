import shutil
from pathlib import Path

PROVIDER = "{{ cookiecutter.provider }}"

AWS_ONLY_PATHS = [
    Path("src/libs/core/python/core_aws"),
    Path("infra/providers/aws"),
]

INFRA_LESS_PROVIDERS = {"container-cloud"}

CONTAINER_ONLY_PATHS = [
    Path("ansible"),
]

if PROVIDER != "aws":
    for path in AWS_ONLY_PATHS:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            print(f"[post-gen] Removed {path} (provider={PROVIDER})")

    for infra_config in Path("src/functions").glob("*/infra_config.py"):
        infra_config.unlink()
        print(f"[post-gen] Removed {infra_config} (provider={PROVIDER})")

    test_file = Path("src/functions/hello_world/test_function.py")
    if test_file.exists():
        test_file.unlink()
        print(f"[post-gen] Removed {test_file} (provider={PROVIDER})")

# Remove template dirs for non-selected providers
templates_path = Path(".spa/templates")
if templates_path.exists():
    for provider_dir in templates_path.iterdir():
        if provider_dir.is_dir() and provider_dir.name != PROVIDER:
            shutil.rmtree(provider_dir)
            print(f"[post-gen] Removed {provider_dir} (provider={PROVIDER})")

if PROVIDER in INFRA_LESS_PROVIDERS:
    infra_path = Path("infra")
    if infra_path.exists():
        shutil.rmtree(infra_path)
        print(f"[post-gen] Removed {infra_path} (provider={PROVIDER})")

if PROVIDER != "container-cloud":
    for path in CONTAINER_ONLY_PATHS:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            print(f"[post-gen] Removed {path} (provider={PROVIDER})")
