from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, Enum
from db.database import Base

class CorrFanParam(Base):
    __tablename__ = "iip_bit_corr_fan_param"

    id = Column(Integer, primary_key=True, index=True)
    fan_code = Column(String)
    fan_name = Column(String)
    param_code = Column(String)
    param_name = Column(String)