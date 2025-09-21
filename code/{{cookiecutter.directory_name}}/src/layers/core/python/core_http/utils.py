import json
import decimal
import datetime
from json.encoder import JSONEncoder
from typing import Tuple

class CustomJSONDecoder(json.JSONEncoder):
    """ Clase que ayuda con el manejo de JSON de un blob Storage de Azure
    """
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        if isinstance(o, bytes):
            return o.decode()
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        return super(CustomJSONDecoder, self).default(o)

def get_body(event: str | dict) -> dict:
    """
    Get event body if lambda has proxy lambda integration in api_local gateway.
    Parameters
    ----------
    event : dict

    Returns
    -------
    dict
        dictionary with body information.

    Examples
    --------
    >>> from core_api.utils import get_body
    >>> get_body({"body": {"a": 1}})

    """
    if isinstance(event, str):
        event = json.loads(event)
    body = event.get("body")
    if isinstance(body, str):
        return json.loads(body)
    return body


def get_status_code(response: dict):
    """
    Get a status code from the lambda response if you use the decorator LambdaResponseWebDefault.
    Parameters
    ----------
    response : dict
        lambda response in api format.

    Returns
    -------
    int
        Status code returned.

    Examples
    --------
    >>> from core_api.utils import get_status_code
    >>> get_status_code({"statusCode": 200})

    """
    status_code = response.get("statusCode")
    return status_code


def get_query_parameters(event: str | dict):
    """
    Get event query parameters if lambda has proxy lambda integration in api_local gateway.
    Parameters
    ----------
    event : dict

    Returns
    -------
    dict
        dictionary with query parameters if exists.

    Examples
    --------
    >>> from core_api.utils import get_query_parameters
    >>> get_query_parameters({"queryStringParameters": {"a": 1}})

    """
    if isinstance(event, str):
        events = json.loads(event)
        return events.get("queryStringParameters") or {}
    return event.get("queryStringParameters") or {}


def get_path_parameters(event: str | dict):
    """
    Get event path parameters if lambda has proxy lambda integration in api_local gateway.
    Parameters
    ----------
    event : dict

    Returns
    -------
    dict
        dictionary with path parameters if exists.

    Examples
    --------
    >>> from core_api.utils import get_path_parameters
    >>> get_path_parameters({"pathParameters": {"a": 1}})

    """
    if isinstance(event, str):
        events = json.loads(event)
        return events.get("pathParameters") or {}
    return event.get("pathParameters") or {}


def get_headers_request(event: str | dict):
    """
    Get event query parameters if lambda has proxy lambda integration in api_local gateway.
    Parameters
    ----------
    event : dict

    Returns
    -------
    dict
        dictionary with query parameters if exists.

    Examples
    --------
    >>> from core_api.utils import get_headers_request
    >>> get_headers_request({"headers": {"a": 1}})

    """
    if isinstance(event, str):
        events = json.loads(event)
        return events.get("headers") or {}
    return event.get("headers") or {}


def build_response(status: int, body: dict, application_type: str = 'application/json', is_base_64: bool = False, jsonEncoder: JSONEncoder = CustomJSONDecoder, circular: bool = True, is_body_str: bool = False, encoder_extras: dict = {}) -> dict:
    """ Devuelve el formato que acepta azure para una respuesta de HTTP

    Args:
        status (int): Codido http
        body (dict): Contenido del json de respuesta
        application_type (str, optional): Tipo de respuesta. Defaults to 'application/json'.
        jsonEncoder (JSONEncoder, optional): Codificacion el JSON de salida. Defaults to CustomJSONDecoder.
        circular (bool, optional): Inidica si la codificacion la hara por cada parametro del JSON. Defaults to True.

    Returns:
        func.HttpResponse: Respuesta HTTP aceptada por Azure
    """
    return {
        "isBase64Encoded": is_base_64,
        "statusCode": status,
        "body": body if is_body_str else json.dumps(body, cls=jsonEncoder, check_circular=circular, **encoder_extras),
        "headers": {
            "content-type": application_type,
            "Access-Control-Allow-Origin": "*"
        }
    }

def serialize_json(data: dict, jsonEncoder: JSONEncoder = CustomJSONDecoder, circular: bool = True) -> str:
    """ Devuelve una cadena en formato JSON de un objeto

    Args:
        data (dict): Contenido del json de respuesta
        jsonEncoder (JSONEncoder, optional): Codificacion el JSON de salida. Defaults to CustomJSONDecoder.
        circular (bool, optional): Inidica si la codificacion la hara por cada parametro del JSON. Defaults to True.

    Returns:
        str: Cadena con formato JSON del contenido
    """
    return json.dumps(data, cls=jsonEncoder, check_circular=circular)

def get_paginate_params(req: str | dict) -> Tuple[bool, int, int]:
    """ Devuelve los parametros de paginacion de una peticion http

    Args:
        req (func.HttpRequest): Peticion http

    Returns:
        Tuple[bool, int, int]: Parametros de paginacion (Paginado, num de pagina, elementos por pagina)
    """
    query_params = get_query_parameters(req)
    page = query_params.get('page')
    if page is not None:
        page = int(page)
    else:
        page = 1

    per_page = query_params.get('per_page')
    if per_page is not None:
        per_page = int(per_page)
    else:
        per_page = 50
    
    return (page, per_page)

def get_filter_params(req: str | dict) -> dict:
    """ Obtiene filtros de query

    Args:
        req (dict): Peticion http

    Returns:
        dict: Filtros formados como par valor
    """
    query_params = get_query_parameters(req)
    
    ret_dict = {}
    for key in query_params.keys():
        if key == 'page' or key == 'per_page' or key == 'relationships':
            pass
        else:
            ret_dict.update({key: query_params[key]})
    
    return ret_dict

def get_relationship_params(req: str | dict) -> dict:
    """ Obtiene filtros de query

    Args:
        req (dict): Peticion http

    Returns:
        dict: Filtros formados como par valor
    """
    query_params = get_query_parameters(req)
    
    ret_dict = {}
    if 'relationships' in query_params.keys():
        ret_dict.update(
            dict(
                relationships=str(query_params.get('relationships', '')).split(',')
            )
        )
    
    return ret_dict
 
def get_search_params(req: str | dict) -> dict:
    """ Obtiene filtros de query

    Args:
        req (dict): Peticion http

    Returns:
        dict: Filtros formados como par valor
    """
    query_params = get_query_parameters(req)
    
    ret_dict = {}
    for k in query_params.keys():
        if str(k).startswith('search_') and str(k):
            v = query_params[k]
            key = k.replace("search_", "", 1)
            if str(v).isdigit():
                ret_dict[key] = v  # sin '%'
            else:
                ret_dict[key] = f"%{v}%"
    
    return ret_dict
 
def get_search_method_param(req: str | dict) -> str:
    """ Obtiene el metodo de filtrado de query

    Args:
        req (dict): Peticion http

    Returns:
        str: Metodo de filtraddo
    """
    query_params = get_query_parameters(req)
    if not query_params:
        return 'AND'
    if 'searchmethod' not in query_params:
        return 'AND'
    
    method = str(query_params['searchmethod']).upper()
    return 'AND' if method not in ['AND', 'OR'] else method
