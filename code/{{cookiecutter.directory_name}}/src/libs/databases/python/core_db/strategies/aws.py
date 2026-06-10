from core_db.config import CredentialStrategy, CONNECTIONS
from core_utils.logging import Logger

LOGGER = Logger('layers.core.core_db.strategies.aws')


class AwsCredentialStrategy(CredentialStrategy):
    def load(self, db_config) -> None:
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
