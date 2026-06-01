from abc import ABC, abstractmethod
from typing import cast, Self

from core_utils.environment import env, APP_NAME, ENVIRONMENT
from aws_lambda_powertools import Logger

LOGGER = Logger('layers.core.core_db.config')

CONNECTIONS: dict[str, str] = {
    'default': {
        'config_name': 'default',
        'secret_name': f'{ENVIRONMENT}-{APP_NAME}-{{ cookiecutter.db_secret_name }}',
        'driver': '{{ cookiecutter._dbDriver }}',
        'prefix': 'DEFAULT'
    }
}

CONNECTIONS_CONFIG = {}

CLOUD_PROVIDER = env('CLOUD_PROVIDER', 'aws')


class CredentialStrategy(ABC):
    @abstractmethod
    def load(self, db_config: 'DBConfig') -> None: ...


class AwsCredentialStrategy(CredentialStrategy):
    def load(self, db_config: 'DBConfig') -> None:
        from core_aws.secret_manager import get_secret
        LOGGER.info("Loading DB credentials from AWS Secrets Manager")
        prefix_lower = db_config.prefix.lower()
        credentials = get_secret(db_config.secret_name, is_dict=True, use_prefix=False)
        db_config.DATABASE_ENGINE   = credentials.get(f'{prefix_lower}-db-engine', 'mysql')
        db_config.DATABASE_DRIVER   = CONNECTIONS[db_config.conn_name]['driver']
        db_config.DATABASE_USERNAME = credentials.get(f'{prefix_lower}-db-username', 'root')
        db_config.DATABASE_PASSWORD = credentials.get(f'{prefix_lower}-db-password', 'root')
        db_config.DATABASE_HOST     = credentials.get(f'{prefix_lower}-db-host', 'localhost')
        db_config.DATABASE_PORT     = credentials.get(f'{prefix_lower}-db-port', '3306')
        db_config.DATABASE_NAME     = credentials.get(f'{prefix_lower}-db-name', 'test')
        db_config.DATABASE_CONNECTION_STRING = (
            f"{db_config.DATABASE_ENGINE}+{db_config.DATABASE_DRIVER}://"
            f"{db_config.DATABASE_USERNAME}:{db_config.DATABASE_PASSWORD}@"
            f"{db_config.DATABASE_HOST}:{db_config.DATABASE_PORT}/{db_config.DATABASE_NAME}"
        )


class EnvCredentialStrategy(CredentialStrategy):
    def load(self, db_config: 'DBConfig') -> None:
        LOGGER.info("Loading DB credentials from environment variables")
        prefix = db_config.prefix
        db_config.DATABASE_ENGINE   = env(f'{prefix}_DATABASE_ENGINE', 'mysql')
        db_config.DATABASE_DRIVER   = CONNECTIONS[db_config.conn_name]['driver']
        db_config.DATABASE_USERNAME = env(f'{prefix}_DATABASE_USERNAME', 'root')
        db_config.DATABASE_PASSWORD = env(f'{prefix}_DATABASE_PASSWORD', 'root')
        db_config.DATABASE_HOST     = env(f'{prefix}_DATABASE_HOST', 'localhost')
        db_config.DATABASE_PORT     = env(f'{prefix}_DATABASE_PORT', '3306')
        db_config.DATABASE_NAME     = env(f'{prefix}_DATABASE_NAME', 'test')
        db_config.DATABASE_CONNECTION_STRING = (
            f"{db_config.DATABASE_ENGINE}+{db_config.DATABASE_DRIVER}://"
            f"{db_config.DATABASE_USERNAME}:{db_config.DATABASE_PASSWORD}@"
            f"{db_config.DATABASE_HOST}:{db_config.DATABASE_PORT}/{db_config.DATABASE_NAME}"
        )


_STRATEGIES: dict[str, CredentialStrategy] = {
    'aws': AwsCredentialStrategy(),
    'env': EnvCredentialStrategy(),
}


def get_strategy(provider: str) -> CredentialStrategy:
    strategy = _STRATEGIES.get(provider)
    if strategy is None:
        raise NotImplementedError(
            f"Credential strategy not implemented for provider: '{provider}'. "
            f"Available: {sorted(_STRATEGIES.keys())}"
        )
    return strategy


class DBConfig:
    def __init__(self, connection_name: str, secret_name: str, prefix='default') -> Self:
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
    def get_config(cls, conn_name: str, secret_name: str = None, prefix: str = 'default') -> Self:
        if conn_name in CONNECTIONS_CONFIG:
            return cast(DBConfig, CONNECTIONS_CONFIG[conn_name])
        if secret_name:
            return cls(connection_name=conn_name, secret_name=secret_name, prefix=prefix)
        return None

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
