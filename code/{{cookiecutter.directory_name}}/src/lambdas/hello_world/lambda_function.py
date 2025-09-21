from aws_lambda_powertools import Logger
from core_http.utils import build_response

logger = Logger()


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    logger.info(event)
    return build_response(200, {"statusCode": 200, "body": "Success"})

