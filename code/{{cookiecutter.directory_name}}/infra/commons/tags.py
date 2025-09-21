import config as project_config

DEFAULT_TAGS = {
    "Environment": project_config.ENVIRONMENT,
    "Project": project_config.APP_NAME,
    "Owner": "{{ cookiecutter.project_name }}",
}