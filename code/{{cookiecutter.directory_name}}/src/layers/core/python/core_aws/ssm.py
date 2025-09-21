# -*- coding: utf-8 -*-
import json

import boto3
from aws_lambda_powertools import Logger
from botocore import exceptions
from core_utils.environment import (
    ENVIRONMENT,
    APP_NAME
)

__all__ = ["get_parameter",
           "get_parameters_by_path"]

LOGGER = Logger('layers.core.core_aws.ssm')


def get_parameter(ssm_name, use_environ=False, default=None, is_dict=True, use_prefix=False):
    """
    Get a parameter from SSM service on aws.

    Parameters
    ----------
    is_dict : bool
    ssm_name : str
        The name of the parameter to get.
    use_environ : bool
        If True, the environment variable will be used to get the parameter.
    default : str
        The default value to return if the parameter is not found.

    Returns
    -------
    str
        The value of the parameter.

    Raises
    ------
    ValueError
        If the parameter is not found and no default value is provided.

    Examples
    --------
    >>> from core_aws.ssm import get_parameter
    >>> get_parameter("/my/parameter")

    """
    try:
        ssm = boto3.client("ssm")
    except Exception as details:
        LOGGER.error("Error create client ssm")
        LOGGER.error("Details: {}".format(details))
        raise exceptions.ClientError
    try:
        if use_environ:
            ssm_name = f"{ssm_name}-{ENVIRONMENT}"
        if use_prefix:
            ssm_name = f"/{ENVIRONMENT.lower()}/{APP_NAME.lower()}/{ssm_name}"
        LOGGER.info(f"Getting parameter: {ssm_name}")
        parameters = ssm.get_parameter(Name=ssm_name)["Parameter"]["Value"]
        LOGGER.info(parameters)
    except Exception as details:
        LOGGER.exception("Name parameter ref : " + ssm_name)
        LOGGER.exception(details)
        LOGGER.info(f"Default value: {default}")
        return default
    else:
        LOGGER.info(f"Value for {ssm_name}: {parameters}")
        if is_dict:
            parameters = json.loads(parameters)

        return parameters

def get_parameters_by_path(ssm_path, recursive=True, parameters_filters=[], with_decription=False, default=None):
    """
    Get a parameter from SSM service on aws.

    Parameters
    ----------
    ssm_path : str
        The name of the path to get a dict of parameters.
    recursive : bool
    parameters_filters: list
    with_decription: bool

    Returns
    -------
    dict
        The values of the parameter.

    Raises
    ------
    ValueError
        If the parameter is not found and no default value is provided.

    Examples
    --------
    >>> from core_aws.ssm import get_parameter
    >>> get_parameters_by_path("/my/parameter")

    """
    try:
        ssm = boto3.client("ssm")
    except Exception as details:
        LOGGER.error("Error create client ssm")
        LOGGER.error("Details: {}".format(details))
        raise exceptions.ClientError
    try:
        LOGGER.info(f"Getting parameter by path: {ssm_path}")
        parameters = ssm.get_parameters_by_path(Path=ssm_path, Recursive=recursive,
                                                ParameterFilters=parameters_filters,
                                                WithDecryption=with_decription)["Parameters"]
    except Exception as details:
        LOGGER.warning("Name parameter ref : " + ssm_path)
        LOGGER.warning(details)
        return default
    else:
        LOGGER.debug(f"Value for {ssm_path}: {parameters}")
        return parameters

def update_parameter(ssm_name, ssm_value, use_environ=False, use_prefix=False, value_type="String"):
    """
    Update a parameter from SSM service on aws.

    Parameters
    ----------
    ssm_name : str
        The name of the parameter to update.
    ssm_value : str
        The value of the parameter to update.
    use_environ : bool
        If True, the environment variable will be used to get the parameter.

    Returns
    -------
    bool
        True if the parameter was updated, False otherwise.

    Raises
    ------
    ValueError
        If the parameter is not found and no default value is provided.

    Examples
    --------
    >>> from core_aws.ssm import update_parameter
    >>> update_parameter("/my/parameter", "my_value")
    True
    """
    try:
        if use_environ:
            ssm_name = f"{ssm_name}-{ENVIRONMENT}"
        if use_prefix:
            ssm_name = f"/{ENVIRONMENT.lower()}/{APP_NAME.lower()}/{ssm_name}"
        ssm = boto3.client("ssm")
        LOGGER.info(f"Updating parameter: {ssm_name} with value: {ssm_value}")
        ssm.put_parameter(Name=ssm_name, Value=ssm_value, Type=value_type, Overwrite=True)
    except Exception as details:
        LOGGER.error("Error updating parameter: {}".format(ssm_name))
        LOGGER.error("Details: {}".format(details))
        return False
    LOGGER.info("Parameter updated: {}".format(ssm_name))
    return True