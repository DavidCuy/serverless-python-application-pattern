from typing import List, Type

import math
from core_db.BaseModel import BaseModel
from .resource_reference import ResourceReference

class PaginationResult:

    def __init__(self, data: List[BaseModel], offset: int = 1, limit: int = 50, total: int = 1, prefix_model: str = "", sufix_model: str = "", refType: Type = BaseModel, request_method='GET', prefix_host: str | None = None) -> None:
        if len(data) > 0:
            self.Data = data
            self.Links = {
                "current": ResourceReference(
                    type(data[0]),
                    prefix_model=prefix_model,
                    sufix_model=f"{'/' if sufix_model != '' else ''}{sufix_model}?page={offset}&per_page={limit}",
                    action=request_method,
                    prefix_host=prefix_host)
                    .to_dict()
            }
            self.Offset = offset
            self.Limit = limit
            self.Total = total
            
            self.Links["first"] = ResourceReference(
                refType,
                prefix_model=prefix_model,
                sufix_model=f"{'/' if sufix_model != '' else ''}{sufix_model}?page=1&per_page={limit}",
                action=request_method,
                prefix_host=prefix_host).to_dict()
            
            self.Links["last"] = ResourceReference(
                refType,
                prefix_model=prefix_model,
                sufix_model=f"{'/' if sufix_model != '' else ''}{sufix_model}?page={(math.ceil(total / limit))}&per_page={limit}",
                action=request_method,
                prefix_host=prefix_host).to_dict()

            if (self.Offset * self.Limit) < self.Total:
                self.Links["next"] = ResourceReference(
                    refType,
                    prefix_model=prefix_model,
                    sufix_model=f"{'/' if sufix_model != '' else ''}{sufix_model}?page={offset+1}&per_page={limit}",
                    action=request_method,
                    prefix_host=prefix_host).to_dict()
            if self.Offset > 1:
                self.Links["prev"] = ResourceReference(
                    refType,
                    prefix_model=prefix_model,
                    sufix_model=f"{'/' if sufix_model != '' else ''}{sufix_model}?page={offset-1}&per_page={limit}",
                    action=request_method,
                    prefix_host=prefix_host).to_dict()
        else:
            self.Data = []
            self.Links = None
            self.Offset = 0
            self.Limit = 0
            self.Total = 0
    
    def to_dict(self) -> dict:
        links = self.Links or {}  # Si self.Links es None, usa un dict vacío

        return {
            "data": self.Data,
            "first_page_url": links.get("first", {}).get("Ref", None),
            "last_page_url": links.get("last", {}).get("Ref", None),
            "next_page_url": links.get("next", {}).get("Ref", None),
            "prev_page_url": links.get("prev", {}).get("Ref", None),
            "current_page": self.Offset,
            "per_page": self.Limit,
            "total": self.Total
        }
    