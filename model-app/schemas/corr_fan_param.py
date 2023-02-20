from pydantic import BaseModel
from typing import Optional, List

class CreateAndUpdateParam(BaseModel):
    fan_code: str
    fan_name: str
    param_code: str
    param_name: str

class Param(CreateAndUpdateParam):
    id: int

    class Config:
        orm_mode = True

class ParamListInfo(BaseModel):
    limit: int
    offset: int
    data: List[Param]