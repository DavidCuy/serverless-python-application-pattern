import csv
from datetime import datetime, timezone
from http import HTTPStatus
import io
import json
from typing import cast
from .enums.http_status_code import HTTPStatusCode

from .exceptions.api_exception import APIException
from .validators.request_validator import RequestValidator

from .interfaces.pagination_result import PaginationResult
from .utils import build_response, get_paginate_params, get_filter_params, get_relationship_params, get_search_method_param, get_search_params, get_body, get_headers_request, get_path_parameters

from core_db.BaseModel import BaseModel
from core_db.BaseService import BaseService
from core_db.DBConnection import AlchemyEncoder, AlchemyRelationEncoder, DBConnection
from aws_lambda_powertools import Logger

LOGGER = Logger('layers.core.core_http.base_controller')

def index(service: BaseService, request: dict):
    session = DBConnection(**service.get_connection_params()).get_session()
    (page, per_page) = get_paginate_params(request)
    relationship_retrieve = get_relationship_params(request)
    filter_query = get_filter_params(request)
    filter_keys = filter_query.keys()
    prefix_host = request.get('headers', {}).get('er-company-request', None)
    params = request.get("queryStringParameters") or {}
    order_by = params.get("order_by")
    order_dir = params.get("order_dir", "asc")

    
    encoder = AlchemyEncoder if 'relationships' not in relationship_retrieve else AlchemyRelationEncoder
    search_query = get_search_params(request)
    search_keys = service.get_search_columns()
    search_columns = list(set(search_keys).intersection(search_query.keys()))
    filters_search = []
    for skey in search_columns:
        filters_search.append({
            'column': getattr(cast(BaseService, service).model, skey),
            'value': search_query[skey]
        })
    
    search_method = 'AND'
    if len(filters_search) > 0:
        search_method = get_search_method_param(request)
    
    model_filter_keys = cast(BaseService, service).get_filter_columns()
    filters_model = set(model_filter_keys).intersection(filter_keys)
    
    filters = []
    for f in filters_model:
        filters.append({f: filter_query[f]})
    
    if cast(BaseService, service).has_soft_delete():
        filters.append({
            cast(BaseModel, cast(BaseService, service).model).SOFT_DELETE_COLUMN: None
        })
    
    try:
        query, elements = cast(BaseService, service).multiple_filters(session, filters, True, page, per_page, search_filters=filters_search, search_method=search_method,order_by=order_by,order_dir=order_dir)
        total_elements = cast(BaseService, service).count_with_query(query)
        
        body = PaginationResult(elements, page, per_page, total_elements, refType=cast(BaseService, service).model, prefix_host=prefix_host).to_dict()
        body['data'] = list(map(lambda d: dict(
                **cast(BaseModel, d).to_dict(jsonEncoder=encoder, encoder_extras=relationship_retrieve)
            ), body['data'])
        )

        status_code = HTTPStatusCode.OK.value
    except APIException as e:
        LOGGER.exception("APIException occurred")
        body = e.to_dict()
        status_code = e.status_code
    except Exception as e:
        LOGGER.exception("Cannot make the request")
        body = dict(message=str(e))
        status_code = HTTPStatusCode.UNPROCESABLE_ENTITY.value
    finally:
        session.close()
    
    return build_response(status_code, body, jsonEncoder=encoder, encoder_extras=relationship_retrieve)

def find(service: BaseService, request: dict):
    path_params = get_path_parameters(request)
    id = path_params.get('id', None)
    session = DBConnection(**service.get_connection_params()).get_session()
    relationship_retrieve = get_relationship_params(request)
    encoder = AlchemyEncoder if 'relationships' not in relationship_retrieve else AlchemyRelationEncoder
    try:
        element = cast(BaseService, service).get_one(session, id)
        body = element.to_dict(jsonEncoder=encoder, encoder_extras=relationship_retrieve)
        status_code = HTTPStatusCode.OK.value
    except APIException as e:
        LOGGER.exception("APIException occurred")
        body = e.to_dict()
        status_code = e.status_code
    except Exception as e:
        LOGGER.exception("Cannot make the request")
        body = dict(message="Cannot make the request")
        status_code = HTTPStatusCode.UNPROCESABLE_ENTITY.value
    finally:
        session.close()
    return build_response(status_code, body, jsonEncoder=AlchemyEncoder)

def store(service: BaseService, request: dict, context = None):
    session = DBConnection(**service.get_connection_params()).get_session()
    
    RequestValidator(cast(BaseService, service).get_rules_for_store()).validate(request)
    input_params = get_body(request)
    
    try:
        body = cast(BaseService, service).insert_register(session, input_params)
        response = json.dumps(body, cls=AlchemyEncoder)
        status_code = HTTPStatusCode.OK.value
    except APIException as e:
        LOGGER.exception("APIException occurred")
        response = json.dumps(e.to_dict())
        status_code = e.status_code
    except Exception:
        LOGGER.exception("No se pudo realizar la consulta")
        body = dict(message="No se pudo realizar la consulta")
        response = json.dumps(body)
        status_code=HTTPStatusCode.UNPROCESABLE_ENTITY.value
    finally:
        session.close()
    
    return build_response(status_code, response, is_body_str=True)

def update(service: BaseService, request: dict, context = None):
    path_params = get_path_parameters(request)
    id = path_params.get('id', None)
    session = DBConnection(**service.get_connection_params()).get_session()

    input_params = get_body(request)
    try:
        body = cast(BaseService, service).update_register(session, id, input_params)
        response = json.dumps(body, cls=AlchemyEncoder)
        status_code = HTTPStatusCode.OK.value
    except APIException as e:
        LOGGER.exception("APIException occurred")
        response = json.dumps(e.to_dict())
        status_code = e.status_code
    except Exception as e:
        LOGGER.exception("Cannot make the request")
        body = dict(message="Cannot make the request")
        response = json.dumps(body)
        status_code = HTTPStatusCode.UNPROCESABLE_ENTITY.value
    finally:
        session.close()
    return build_response(status_code, response, is_body_str=True)

def delete(service: BaseService, request: dict, context = None):
    path_params = get_path_parameters(request)
    id = path_params.get('id', None)
    session = DBConnection(**service.get_connection_params()).get_session()
    body = None  

    try:
        element = cast(BaseService, service).soft_delete_register(session, id) if cast(BaseService, service).has_soft_delete() else cast(BaseService, service).delete_register(session, id)
        status_code = HTTPStatusCode.OK.value
        body = {'id': id}
    except APIException as e:
        LOGGER.exception("APIException occurred")
        body = e.to_dict()
        status_code = e.status_code
    except Exception as e:
        LOGGER.exception("Cannot make the request")
        body = dict(message="Cannot make the request")
        status_code = HTTPStatusCode.UNPROCESABLE_ENTITY.value
    finally:
        session.close()
    return build_response(status_code, body, jsonEncoder=AlchemyEncoder)

def get_filtered_elements(service: BaseService, request: dict):
    session = DBConnection(**service.get_connection_params()).get_session()
    (page, per_page) = get_paginate_params(request)
    relationship_retrieve = get_relationship_params(request)
    filter_query = get_filter_params(request)
    filter_keys = filter_query.keys()

    encoder = AlchemyEncoder if 'relationships' not in relationship_retrieve else AlchemyRelationEncoder
    search_query = get_search_params(request)
    search_keys = service.get_search_columns()
    search_columns = list(set(search_keys).intersection(search_query.keys()))

    filters_search = []
    for skey in search_columns:
        filters_search.append({
            'column': getattr(cast(BaseService, service).model, skey),
            'value': search_query[skey]
        })

    search_method = 'AND'
    if len(filters_search) > 0:
        search_method = get_search_method_param(request)

    model_filter_keys = cast(BaseService, service).get_filter_columns()
    filters_model = set(model_filter_keys).intersection(filter_keys)

    filters = []
    for f in filters_model:
        filters.append({f: filter_query[f]})

    if cast(BaseService, service).has_soft_delete():
        filters.append({
            cast(BaseModel, cast(BaseService, service).model).SOFT_DELETE_COLUMN: None
        })

    query, elements = cast(BaseService, service).multiple_filters(
        session,
        filters,
        True,
        page,
        per_page,
        search_filters=filters_search,
        search_method=search_method
    )

    return  elements, encoder, relationship_retrieve

def get_field_value(obj, field_info):
    if "relation" in field_info and getattr(obj, field_info["relation"], None):
        related_obj = getattr(obj, field_info["relation"])
        return getattr(related_obj, field_info["attr"], None)
    else:
        return getattr(obj, field_info.get("field", None), None)

def exportToCSV(service: BaseService, request: dict, column_aliases):
    try:

        elements, encoder, relationship_retrieve = get_filtered_elements(service,request)

        data = list(map(lambda d: dict(
                **cast(BaseModel, d).to_dict(jsonEncoder=encoder, encoder_extras=relationship_retrieve)
            ), elements)
        )

        if not data:
            return {
                "statusCode": HTTPStatus.BAD_REQUEST,
                "body": json.dumps({"message": "No data provided"})
            }

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[info["alias"] for info in column_aliases.values()])
        writer.writeheader()

        for item in elements:
            row = {}
            for field, info in column_aliases.items():
                if "field" not in info:
                    info["field"] = field
                row[info["alias"]] = get_field_value(item, info)
            writer.writerow(row)
        csv_content=output.getvalue()
        output.close()

        print(csv_content)

        file_date = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        filename = f"export_{file_date}.csv"

        response= {
            "statusCode": HTTPStatus.OK,
            "headers": {
                "Content-Type": "text/csv",
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Allow-Origin": "*"
            },
            "body": csv_content
        }
        print("Response headers:", response["headers"])
        return response
    except Exception as e:
        return {
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "body": json.dumps({"error": str(e)})
        }