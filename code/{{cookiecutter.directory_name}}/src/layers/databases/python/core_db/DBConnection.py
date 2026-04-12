import json
import uuid
import decimal
import datetime
from functools import lru_cache
from sqlalchemy import create_engine

@lru_cache(maxsize=None)
def _get_mapper_relationship_names(cls):
    return frozenset(cls.__mapper__.relationships.keys())
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm.session import Session as ORMSession

from core_db.config import DBConfig, CONNECTIONS

CONNECTION_HANDLERS: dict[str, 'DBConnection'] = {}

class DBConnection:

    def __init__(self, config_name: str, secret_name: str = None, prefix: str = 'default', *_, **__) -> None:
        self.config_name = config_name
        self.secret_name = secret_name
        self.prefix = prefix
        
        self.config: DBConfig | None = None
        self.engine: Engine | None = None
        self.session: ORMSession | None = None

        if self.config_name not in CONNECTION_HANDLERS:
            CONNECTION_HANDLERS[self.config_name] = self

            if CONNECTION_HANDLERS[self.config_name].session:
                return self

        if not CONNECTION_HANDLERS[self.config_name].config:
            CONNECTION_HANDLERS[self.config_name].config = DBConfig.get_config(conn_name=config_name, secret_name=secret_name, prefix=prefix)

        if not CONNECTION_HANDLERS[self.config_name].engine:
            CONNECTION_HANDLERS[self.config_name].engine = create_engine(**CONNECTION_HANDLERS[self.config_name].config.get_engine_config())

        if not CONNECTION_HANDLERS[self.config_name].session:
            CONNECTION_HANDLERS[self.config_name].session = sessionmaker(CONNECTION_HANDLERS[self.config_name].engine)

    def get_engine(self) -> Engine:
        if not CONNECTION_HANDLERS[self.config_name].engine:
            CONNECTION_HANDLERS[self.config_name].engine = create_engine(**CONNECTION_HANDLERS[self.config_name].config.get_engine_config())
        return CONNECTION_HANDLERS[self.config_name].engine

    def get_session(self) -> ORMSession:
        if not CONNECTION_HANDLERS[self.config_name].session:
            CONNECTION_HANDLERS[self.config_name].session = sessionmaker(self.get_engine())
        return CONNECTION_HANDLERS[self.config_name].session(expire_on_commit=False)

for conn_name in CONNECTIONS.keys():
    DBConnection(**CONNECTIONS[conn_name])

class AlchemyEncoder(json.JSONEncoder):
    """ Based on: https://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json/41204271 """
    def default(self, obj):
        if issubclass(obj.__class__, DeclarativeBase):
            fields = {}
            prop_map_obj = obj.__class__.property_map()
            for field in [x for x in obj.attrs]:
                data = obj.__getattribute__(field)
                try:
                    if isinstance(data, uuid.UUID):
                        data = str(data)
                    elif isinstance(data, decimal.Decimal):
                        if data % 1 > 0:
                            data = float(data)
                        else:
                            data = int(data)
                    elif isinstance(data, (datetime.datetime, datetime.date, datetime.time)):
                        data = data.isoformat()
                    else:
                        json.dumps(data)
                    fields[prop_map_obj[field] if field in prop_map_obj else field] = data
                except TypeError:
                    fields[field] = None
            return fields
        return json.JSONEncoder.default(self, obj)


class AlchemyRelationEncoder(json.JSONEncoder):
    def __init__(self, *args, relationships=None, max_depth=2, _visited=None, **kwargs):
        self.relationships = relationships or []
        self.max_depth = max_depth
        self._visited = _visited if _visited is not None else set()
        super().__init__(*args, **kwargs)

    def _serialize_value(self, data, depth):
        if isinstance(data, uuid.UUID):
            return str(data)
        elif isinstance(data, decimal.Decimal):
            return float(data) if data % 1 > 0 else int(data)
        elif isinstance(data, (datetime.datetime, datetime.date, datetime.time)):
            return data.isoformat()
        elif isinstance(data, DeclarativeBase):
            return self._serialize_model(data, depth)
        elif isinstance(data, list):
            return [
                self._serialize_model(d, depth) if isinstance(d, DeclarativeBase) else d
                for d in data
            ]
        return data

    def _serialize_model(self, obj, depth):
        if id(obj) in self._visited or depth <= -1:
            return obj.id

        self._visited.add(id(obj))
        fields = {}
        prop_map_obj = obj.__class__.property_map()

        filters_model = _get_mapper_relationship_names(obj.__class__).intersection(self.relationships)
        attributes = list(obj.attrs) + list(filters_model)

        for field in attributes:
            data = getattr(obj, field, None)
            try:
                fields[prop_map_obj.get(field, field)] = self._serialize_value(data, depth - 1)
            except Exception:
                fields[field] = None
        return fields

    def default(self, obj):
        if isinstance(obj, DeclarativeBase):
            return self._serialize_model(obj, self.max_depth)
        return super().default(obj)

