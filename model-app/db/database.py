# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import envconfig

DATABASE_IP = envconfig.Settings().database_ip
DATABASE_PORT = envconfig.Settings().database_port
DATABASE_USERNAME = envconfig.Settings().database_username
DATABASE_PASSWORD = envconfig.Settings().database_password
DATABASE_NAME = envconfig.Settings().database_name
DATABASE_URL = f"mysql+mysqldb://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_IP}:{DATABASE_PORT}/{DATABASE_NAME}"


db_engine = create_engine(DATABASE_URL, connect_args={'connect_timeout': 120})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

Base = declarative_base()

def get_db():
    """
    Function to generate db session
    :return: Session
    """
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()