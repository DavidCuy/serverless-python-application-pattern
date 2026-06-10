from core_db.config import CredentialStrategy, CONNECTIONS
from core_utils.environment import env
from core_utils.logging import Logger

LOGGER = Logger('layers.core.core_db.strategies.env')


class EnvCredentialStrategy(CredentialStrategy):
    def load(self, db_config) -> None:
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
