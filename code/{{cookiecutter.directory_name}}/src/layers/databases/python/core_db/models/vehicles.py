from typing import Any, Dict, List
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..BaseModel import BaseModel

class Vehicle(BaseModel):
    """ Table kavak_list_vehicles Database view

    Args:
        BaseModel (ORMClass): Parent class

    Returns:
        Vehicle: Instance of model
    """
    __tablename__ = 'kavak_list_vehicles'
    __connection_config_name__ = 'avasaops'
    id = Column("id", Integer, primary_key=True)
    vin = Column("vin", String(128))
    brand = Column("brand", String(128))
    model = Column("model", String(128))
    year = Column("year", Integer)
    version = Column("version", String(128))
    sku = Column("sku", String(128))
    id_inventory = Column("id_inventory", String(128))
    km = Column("km", Integer)
    has_second_key = Column("has_second_key", Boolean)
    purchase_date = Column("purchase_date", DateTime(timezone=True))
    color = Column("color", String(128))
    estatus = Column("estatus", String(128))
    rental_agreement_id = Column("rental_agreement_id", Integer)
    region = Column("region", String(256))
    location = Column("location", String(128))
    vehicle_code = Column("vehicle_code", String(128))
    plate = Column ("plate", String(128))
    plate_state = Column ("plate_state", String(128))

    model_path_name = "vehicles"

    filter_columns = [
        "id",
        "vin",
        "brand",
        "model",
        "year",
        "version",
        "has_second_key",
        "color",
        "estatus",
        "rental_agreement_id",
        "location",
        "plate",
        "plate_state"
    ]
    relationship_names = []
    search_columns = [
        "vin",
        "brand",
        "model",
        "color",
        "region",
        "location"
    ]
    
    @classmethod
    def property_map(self) -> Dict:
        return {}
    
    @classmethod
    def display_members(cls_) -> List[str]:
        return [
            "id",
            "vin",
            "brand",
            "model",
            "year",
            "version",
            "sku",
            "id_inventory",
            "km",
            "has_second_key",
            "purchase_date",
            "color",
            "estatus",
            "rental_agreement_id",
            "region",
            "location",
            "plate_state"
        ]
    
    @classmethod
    def rules_for_store(cls_) -> Dict[str, List[Any]]:
        return {}