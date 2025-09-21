from typing import cast, Self

from core_utils.environment import env, APP_NAME, ENVIRONMENT
from aws_lambda_powertools import Logger

LOGGER = Logger('layers.core.core_db.config')

CONNECTIONS: dict[str, str] = {
    
}

CONNECTIONS_CONFIG = {}

class DBConfig:
    def __init__(self, connection_name: str, secret_name:str, prefix = 'default') -> Self:
        LOGGER.info("Database configuration")
        self.conn_name = connection_name
        self.secret_name = secret_name
        self.prefix = prefix

        if self.conn_name not in CONNECTIONS_CONFIG:
            CONNECTIONS_CONFIG[self.conn_name] = self

        self.refresh()

    def refresh(self) -> None:
        self.DATABASE_DRIVER               = env(f"{self.prefix}_DATABASE_DRIVER", None)
        self.DATABASE_NAME                 = env(f"{self.prefix}_DATABASE_NAME", None)
        self.DATABASE_CONNECTION_STRING    = env(f"{self.prefix}_DATABASE_CONNECTION_STRING", None)
        self.DATABASE_DEBUG_MODE           = env(f"{self.prefix}_DATABASE_DEBUG_MODE", True)
        self.DATABASE_POOL_SIZE            = env(f"{self.prefix}_DATABASE_POOL_SIZE", 20)
        self.DATABASE_MAX_OVERFLOW         = env(f"{self.prefix}_DATABASE_MAX_OVERFLOW", 5)
        self.DATABASE_POOL_RECYCLE         = env(f"{self.prefix}_DATABASE_POOL_RECYCLE", 3600)
        self.DATABASE_POOL_PRE_PING        = env(f"{self.prefix}_DATABASE_POOL_PRE_PING", True)
        self.DATABASE_POOL_USE_LIFO        = env(f"{self.prefix}_DATABASE_POOL_USE_LIFO", True)
        
        if not self.DATABASE_CONNECTION_STRING:
            self.get_db_from_secrets()

    def get_db_from_secrets(self) -> None:
        if self.DATABASE_CONNECTION_STRING:
            return

        from core_aws.secret_manager import get_secret
        LOGGER.info("Loading from params and secrets")
        
        prefix_lower = self.prefix.lower()
        credentials = get_secret(self.secret_name, is_dict=True, use_prefix=False)
        self.DATABASE_ENGINE = credentials.get(f'{prefix_lower}-db-engine', 'mysql')
        self.DATABASE_DRIVER = "pymysql"
        self.DATABASE_USERNAME = credentials.get(f'{prefix_lower}-db-username', 'root')
        self.DATABASE_PASSWORD = credentials.get(f'{prefix_lower}-db-password', 'root')
        self.DATABASE_HOST = credentials.get(f'{prefix_lower}-db-host', 'localhost')
        self.DATABASE_PORT = credentials.get(f'{prefix_lower}-db-port', '3306')
        self.DATABASE_NAME = credentials.get(f'{prefix_lower}-db-name', 'test')

        self.DATABASE_CONNECTION_STRING = f"{self.DATABASE_ENGINE}+{self.DATABASE_DRIVER}://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

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
            'pool_use_lifo': self.DATABASE_POOL_USE_LIFO
    }
