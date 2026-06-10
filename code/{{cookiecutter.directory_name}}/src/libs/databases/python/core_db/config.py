from abc import ABC, abstractmethod
from typing import cast, Optional, Self

from core_utils.environment import env, APP_NAME, ENVIRONMENT
from core_utils.logging import Logger

LOGGER = Logger('layers.core.core_db.config')

CONNECTIONS: dict[str, dict] = {
    'default': {
        'config_name': 'default',
        'driver': '{{ cookiecutter._dbDriver }}',
        'prefix': 'DEFAULT',
        {% if cookiecutter.provider == 'aws' %}'secret_name': f'{ENVIRONMENT}-{APP_NAME}-{{ cookiecutter.db_secret_name }}',{% endif %}
    }
}

CONNECTIONS_CONFIG = {}

CLOUD_PROVIDER = env('CLOUD_PROVIDER', '{{ cookiecutter.provider }}')


class CredentialStrategy(ABC):
    @abstractmethod
    def load(self, db_config: 'DBConfig') -> None: ...


_strategy_cache: dict[str, CredentialStrategy] = {}


def get_strategy(provider: str) -> CredentialStrategy:
    if provider in _strategy_cache:
        return _strategy_cache[provider]

    if provider == 'aws':
        from core_db.strategies.aws import AwsCredentialStrategy
        _strategy_cache[provider] = AwsCredentialStrategy()
    elif provider in ('gcp', 'azure', 'cloudflare', 'container-cloud', 'env'):
        from core_db.strategies.env import EnvCredentialStrategy
        _strategy_cache[provider] = EnvCredentialStrategy()
    else:
        raise NotImplementedError(
            f"Credential strategy not implemented for provider: '{provider}'. "
            f"Available: aws, gcp, azure, cloudflare, container-cloud"
        )

    return _strategy_cache[provider]


class DBConfig:
    def __init__(self, connection_name: str, secret_name: Optional[str] = None, prefix='default') -> None:
        LOGGER.info("Database configuration")
        self.conn_name = connection_name
        self.secret_name = secret_name
        self.prefix = prefix

        if self.conn_name not in CONNECTIONS_CONFIG:
            CONNECTIONS_CONFIG[self.conn_name] = self

        self.refresh()

    def refresh(self) -> None:
        self.DATABASE_DRIVER            = env(f"{self.prefix}_DATABASE_DRIVER", None)
        self.DATABASE_NAME              = env(f"{self.prefix}_DATABASE_NAME", None)
        self.DATABASE_CONNECTION_STRING = env(f"{self.prefix}_DATABASE_CONNECTION_STRING", None)
        self.DATABASE_DEBUG_MODE        = env(f"{self.prefix}_DATABASE_DEBUG_MODE", True)
        self.DATABASE_POOL_SIZE         = env(f"{self.prefix}_DATABASE_POOL_SIZE", 20)
        self.DATABASE_MAX_OVERFLOW      = env(f"{self.prefix}_DATABASE_MAX_OVERFLOW", 5)
        self.DATABASE_POOL_RECYCLE      = env(f"{self.prefix}_DATABASE_POOL_RECYCLE", 3600)
        self.DATABASE_POOL_PRE_PING     = env(f"{self.prefix}_DATABASE_POOL_PRE_PING", True)
        self.DATABASE_POOL_USE_LIFO     = env(f"{self.prefix}_DATABASE_POOL_USE_LIFO", True)

        if not self.DATABASE_CONNECTION_STRING:
            get_strategy(CLOUD_PROVIDER).load(self)

    @classmethod
    def get_config(cls, conn_name: str, secret_name: Optional[str] = None, prefix: str = 'default') -> Self:
        if conn_name in CONNECTIONS_CONFIG:
            return cast(DBConfig, CONNECTIONS_CONFIG[conn_name])
        return cls(connection_name=conn_name, secret_name=secret_name, prefix=prefix)

    def get_engine_config(self) -> dict[str, str | int | bool]:
        return {
            'url': self.DATABASE_CONNECTION_STRING,
            'echo': self.DATABASE_DEBUG_MODE,
            'pool_size': self.DATABASE_POOL_SIZE,
            'max_overflow': self.DATABASE_MAX_OVERFLOW,
            'pool_recycle': self.DATABASE_POOL_RECYCLE,
            'pool_pre_ping': self.DATABASE_POOL_PRE_PING,
            'pool_use_lifo': self.DATABASE_POOL_USE_LIFO,
        }
