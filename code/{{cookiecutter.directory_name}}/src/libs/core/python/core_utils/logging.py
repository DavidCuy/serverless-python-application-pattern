import json
import logging
import os
import datetime
from abc import ABC, abstractmethod
from typing import Any

from dotenv import load_dotenv
load_dotenv()

_cold_start = True


class _PowertoolsFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        global _cold_start
        now = datetime.datetime.now(datetime.timezone.utc)
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S,') + f'{now.microsecond // 1000:03d}+0000'

        entry = {
            'level': record.levelname,
            'location': f'{record.funcName}:{record.lineno}',
            'message': record.getMessage(),
            'timestamp': timestamp,
            'service': record.name,
            'cold_start': _cold_start,
            'function_name': os.getenv('APP_NAME', 'unknown'),
            'function_request_id': os.getenv('_X_AMZN_TRACE_ID', ''),
        }

        if record.exc_info:
            entry['exception'] = self.formatException(record.exc_info)

        _cold_start = False
        return json.dumps(entry)


class _DefaultLogger:
    """JSON logger matching aws_lambda_powertools.Logger public API."""

    def __init__(self, service: str):
        self._service = service
        self._logger = logging.getLogger(service)
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(_PowertoolsFormatter())
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.DEBUG)
            self._logger.propagate = False

    def debug(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, stacklevel=2, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, stacklevel=2, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, stacklevel=2, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, stacklevel=2, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self._logger.exception(msg, *args, stacklevel=2, **kwargs)

    def inject_function_context(self, func=None, *, log_event: bool = False, clear_state: bool = False):
        """No-op decorator for provider-agnostic function context injection."""
        if func is None:
            def decorator(f):
                return f
            return decorator
        return func


class LoggingStrategy(ABC):
    @abstractmethod
    def get_logger(self, service: str) -> Any: ...


class AwsLoggingStrategy(LoggingStrategy):
    def get_logger(self, service: str) -> Any:
        from aws_lambda_powertools import Logger as PowertoolsLogger
        logger = PowertoolsLogger(service=service)
        logger.inject_function_context = logger.inject_lambda_context
        return logger


class DefaultLoggingStrategy(LoggingStrategy):
    def get_logger(self, service: str) -> _DefaultLogger:
        return _DefaultLogger(service=service)


_STRATEGIES: dict[str, LoggingStrategy] = {
    'aws': AwsLoggingStrategy(),
}

_DEFAULT_STRATEGY = DefaultLoggingStrategy()


def Logger(service: str = None) -> Any:
    """Factory matching aws_lambda_powertools.Logger(service) API."""
    cloud_provider = os.getenv('CLOUD_PROVIDER', '')
    resolved = service or os.getenv('POWERTOOLS_SERVICE_NAME') or os.getenv('APP_NAME', 'service')
    strategy = _STRATEGIES.get(cloud_provider, _DEFAULT_STRATEGY)
    return strategy.get_logger(resolved)
