import os
import sys
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(override=True)
from unittest import TestCase, TestLoader, TestSuite, TextTestRunner, mock
from uuid import uuid4


class MockContext:
    def __init__(self):
        self.function_name = "hello_world"
        self.memory_limit_in_mb = 50
        self.invoked_function_arn = "arn:aws:lambda:aws-region-1:123456789012:function:hello_world"
        self.aws_request_id = str(uuid4())


class TestHelloWorld(TestCase):

    def setUp(self) -> None:
        return super().setUp()

    def test_success(self, *_, **__):
        from lambda_function import lambda_handler
        event = {
            "version": "2.0",
            "routeKey": "$default",
            "rawPath": "/path/to/resource",
            "rawQueryString": "parameter1=value1&parameter1=value2&parameter2=value",
            "cookies": [
                "cookie1",
                "cookie2"
            ],
            "headers": {
                "Header1": "value1",
                "Header2": "value1,value2"
            },
            "queryStringParameters": None,
            "requestContext": {
                "accountId": "123456789012",
                "apiId": "api-id",
                "authentication": {
                "clientCert": {
                    "clientCertPem": "CERT_CONTENT",
                    "subjectDN": "www.example.com",
                    "issuerDN": "Example issuer",
                    "serialNumber": "a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1",
                    "validity": {
                    "notBefore": "May 28 12:30:02 2019 GMT",
                    "notAfter": "Aug  5 09:36:04 2021 GMT"
                    }
                }
                },
                "authorizer": {
                "jwt": {
                    "claims": {
                    "claim1": "value1",
                    "claim2": "value2"
                    },
                    "scopes": [
                    "scope1",
                    "scope2"
                    ]
                }
                },
                "domainName": "id.execute-api.us-east-1.amazonaws.com",
                "domainPrefix": "id",
                "http": {
                "method": "POST",
                "path": "/path/to/resource",
                "protocol": "HTTP/1.1",
                "sourceIp": "192.168.0.1/32",
                "userAgent": "agent"
                },
                "requestId": "id",
                "routeKey": "$default",
                "stage": "$default",
                "time": "12/Mar/2020:19:03:58 +0000",
                "timeEpoch": 1583348638390
            },
            "body": None,
            "pathParameters": {},
            "isBase64Encoded": False
        }
        output = lambda_handler(event, MockContext())
        logging.info(output)

test = TestHelloWorld()
test.setUp()
test_suite = TestLoader().loadTestsFromTestCase(TestHelloWorld)

runner = TextTestRunner()
runner.run(test_suite)

