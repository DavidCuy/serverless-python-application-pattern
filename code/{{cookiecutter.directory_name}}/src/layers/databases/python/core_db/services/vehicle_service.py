from core_db.BaseService import BaseService
from core_db.models.vehicles import Vehicle


class VehicleService(BaseService):
    def __init__(self) -> None:
        super().__init__(Vehicle)