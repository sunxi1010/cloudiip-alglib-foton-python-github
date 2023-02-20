from typing import List
from sqlalchemy.orm import Session
from exceptions.param_exceptions import ParamInfoInfoAlreadyExistError, ParamInfoNotFoundError
from models.corr_fan_param import CorrFanParam
from schemas.corr_fan_param import CreateAndUpdateParam


def get_all_params(session: Session) -> list[CorrFanParam]:
    return session.query(CorrFanParam).all()

def get_param_by_id(session: Session, _id: int) -> CorrFanParam:
    param = session.query(CorrFanParam).get(_id)

    if param is None:
        raise ParamInfoNotFoundError
    
    return param

def create_param():
    pass

def update_param():
    pass

def delete_param():
    pass
